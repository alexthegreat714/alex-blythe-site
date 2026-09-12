"""Serial, network-free OpenFOAM study executor. Run only in the bounded container."""
import json
import math
import os
import re
import shutil
import subprocess
import threading
import time
import zipfile
from pathlib import Path
from core import RHO, MU, WIDTH, GRIDS, REVISION, DEFAULTS, atomic_json, brief, digest, materialize, validate, report_html

DATA = Path(os.getenv("AERO_STUDY_DATA", "/data"))
WORK = Path("/work")
NUMBER = r"[-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?"


def field_values(path, vectors=False):
    source = path.read_text()
    match = re.search(r"internalField\s+nonuniform\s+List<\w+>\s+(\d+)\s*\((.*?)\)\s*;", source, re.S)
    if not match:
        raise RuntimeError("Missing solved nonuniform field")
    if vectors:
        values = [list(map(float, re.findall(NUMBER, vector))) for vector in re.findall(r"\(([^()]+)\)", match[2])]
    else:
        values = list(map(float, re.findall(NUMBER, match[2])))
    if len(values) != int(match[1]) or not all(math.isfinite(v) for row in values for v in (row if vectors else [row])):
        raise RuntimeError("Invalid solved field")
    return values


def patch_flux(path, name):
    source = path.read_text()
    block = re.search(r"\b" + name + r"\s*\{([^{}]+)\}", source, re.S)
    if not block:
        raise RuntimeError("Missing boundary flux")
    match = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)\s*;", block[1], re.S)
    if not match:
        raise RuntimeError("Missing computed boundary flux values")
    return sum(map(float, re.findall(NUMBER, match[2])))


def command(executable, root, deadline):
    with (root / ("log." + executable)).open("w") as log:
        remaining = min(70, deadline - time.monotonic())
        if remaining <= 0:
            raise TimeoutError("Study runtime limit reached")
        child = subprocess.Popen([executable, "-case", str(root)], stdout=log, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        try:
            code = child.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, 9)
            child.wait()
            raise TimeoutError(f"{executable} exceeded the time limit")
    if code:
        raise RuntimeError(f"{executable} failed; see the retained run log")
    if (root / ("log." + executable)).stat().st_size > 6 * 1024 ** 2:
        raise RuntimeError("Solver log size limit")


def extract(root, data, variant, grid, nx, ny):
    log = (root / "log.simpleFoam").read_text()
    mesh = (root / "log.checkMesh").read_text()
    times = [p for p in root.iterdir() if p.is_dir() and p.name.isdigit() and int(p.name) > 0]
    if not times or not re.search(r"\bEnd\s*$", log.strip()):
        raise RuntimeError("No terminal solver fields")
    final = max(times, key=lambda p: int(p.name))
    pressure = field_values(final / "p")
    velocity = field_values(final / "U", True)
    if len(pressure) != nx * ny or len(velocity) != nx * ny:
        raise RuntimeError("Solved field count differs from the structured mesh")
    length = data["length_mm"] / 1000
    # blockMesh's single block uses i (x) fastest, followed by j (y).
    xs = [(i + .5) * length / nx for i in range(nx)]
    axial_p = [sum(pressure[j * nx + i] for j in range(ny)) / ny * RHO for i in range(nx)]
    indices = list(range(nx // 4, 3 * nx // 4))
    mean_x = sum(xs[i] for i in indices) / len(indices)
    mean_p = sum(axial_p[i] for i in indices) / len(indices)
    slope = sum((xs[i] - mean_x) * (axial_p[i] - mean_p) for i in indices) / sum((xs[i] - mean_x) ** 2 for i in indices)
    dp = -slope * length
    profile = [sum(velocity[j * nx + i][0] for i in indices) / len(indices) for j in range(ny)]
    target = [6 * variant["mean_velocity_m_s"] * ((j + .5) / ny) * (1 - (j + .5) / ny) for j in range(ny)]
    profile_error = math.sqrt(sum((a - b) ** 2 for a, b in zip(profile, target)) / sum(v * v for v in target)) * 100
    flux_in, flux_out = patch_flux(final / "phi", "inlet"), patch_flux(final / "phi", "outlet")
    imbalance = abs(flux_in + flux_out) / max(abs(flux_in), 1e-20) * 100
    residuals = {}
    history = []
    iteration = 0
    for line in log.splitlines():
        current = re.match(r"Time = (\d+)", line)
        if current:
            iteration = int(current[1])
        match = re.search(r"Solving for (Ux|Uy|Uz|p), Initial residual = (" + NUMBER + ")", line)
        if match:
            residuals[match[1]] = float(match[2])
            if iteration % 10 == 0:
                history.append({"iteration": iteration, "field": match[1], "residual": float(match[2])})
    values = [dp, profile_error, imbalance, *residuals.values()]
    if not all(math.isfinite(v) for v in values) or dp <= 0:
        raise RuntimeError("Nonphysical or nonfinite solved metrics")
    reference_error = abs(dp / variant["analytical_pa"] - 1) * 100
    gates = {"mesh": "Mesh OK." in mesh, "solver": "solution converged" in log.lower(),
             "residuals": set(residuals) >= {"p", "Ux", "Uy"} and max(residuals.values()) <= 1e-7,
             "conservation": imbalance < .1, "analytical_reference": reference_error < 2,
             "velocity_profile": profile_error < 2}
    return {"grid": grid, "nx": nx, "ny": ny, "cells": nx * ny,
            "iterations": int(final.name), "pressure_drop_pa": dp,
            "reference_error_pct": reference_error, "mass_imbalance_pct": imbalance,
            "profile_error_pct": profile_error, "residuals": residuals, "history": history[-240:], "gates": gates,
            "pressure_definition": "Interior axial pressure gradient fitted over x/L=0.25..0.75 and multiplied by total length; p converted from m2/s2 to Pa using density.",
            "field": {"x_m": xs, "axial_pressure_pa": axial_p,
                      "y_fraction": [(j + .5) / ny for j in range(ny)], "velocity_m_s": profile,
                      "pressure_pa": [v * RHO for v in pressure], "speed_m_s": [math.sqrt(sum(c*c for c in v)) for v in velocity]}}


def execute(job):
    root = WORK / job.name
    deadline = time.monotonic() + 300
    inputs = validate(json.loads((job / "input.json").read_text()))
    record = brief(inputs)
    started = time.time()
    completed = 0
    def status(state, message, **extra):
        atomic_json(job / "status.json", {"id": job.name, "state": state, "message": message,
                    "completed": completed, "total": 9, "progress": round(completed / 9 * 100),
                    "started_at": started, "updated_at": time.time(), **extra})
    status("running", "Preparing three geometry variants and mesh families")
    try:
        outcomes = []
        for variant_number, variant in enumerate(record["variants"]):
            levels = []
            for grid, nx, ny in GRIDS:
                case = root / f"gap-{variant_number + 1}" / grid
                materialize(case, inputs, variant["gap_mm"], nx, ny)
                status("running", f"Gap {variant['gap_mm']:.3g} mm: generating {grid} mesh", phase="mesh")
                command("blockMesh", case, deadline)
                command("checkMesh", case, deadline)
                if "Mesh OK." not in (case / "log.checkMesh").read_text():
                    raise RuntimeError("Mesh quality check did not pass")
                status("running", f"Gap {variant['gap_mm']:.3g} mm: solving {grid} grid", phase="solve")
                command("simpleFoam", case, deadline)
                levels.append(extract(case, inputs, variant, grid, nx, ny))
                completed += 1
                status("running", f"{completed}/9 solves complete; checking reference and conservation", phase="verify")
            medium, fine = levels[-2:]
            difference = abs(fine["pressure_drop_pa"] - medium["pressure_drop_pa"])
            allowance = max(difference, abs(fine["pressure_drop_pa"] - variant["analytical_pa"]))
            checked = all(all(level["gates"].values()) for level in levels) and difference / fine["pressure_drop_pa"] < .01
            outcomes.append({**variant, "levels": levels, "pressure_drop_pa": fine["pressure_drop_pa"],
                "mesh_change_pct": difference / fine["pressure_drop_pa"] * 100,
                "numerical_allowance_pa": allowance, "margin_pa": inputs["budget_pa"] - fine["pressure_drop_pa"] - allowance,
                "checks_passed": checked, "meets_budget": checked and fine["pressure_drop_pa"] + allowance <= inputs["budget_pa"]})
        candidates = [v for v in outcomes if v["meets_budget"]]
        all_passed = all(v["checks_passed"] for v in outcomes)
        selected = min(candidates, key=lambda v: v["gap_mm"]) if candidates and all_passed else None
        result = {"id": job.name, "revision": REVISION, "source": "LIVE_OPENFOAM", "brief": record, "variants": outcomes,
                  "completed_at": time.time(), "elapsed_seconds": round(time.time()-started, 2),
                  "checks_passed": all_passed, "selected_gap_mm": selected["gap_mm"] if selected else None,
                  "decision": (f"{selected['gap_mm']:.3g} mm is the smallest tested gap meeting the {inputs['budget_pa']:.3g} Pa budget within the stated parallel-plate model."
                               if selected else "No tested gap meets the budget with all checks passed. Review the results or change the study inputs."),
                  "provenance": {"solver": "OpenFOAM Foundation 10 / simpleFoam", "grids_per_variant": 3,
                                 "worker_source_sha256": digest(__file__), "case_generator_sha256": digest(Path(__file__).with_name("core.py"))},
                  "interpretation": "The analytical comparison verifies this idealized flow calculation. Sidewalls, entrance effects, fittings, temperature variation and manufacturing tolerance require separate assessment for a physical channel."}
        atomic_json(job / "result.json", result)
        (job / "report.html").write_text(report_html(result), encoding="utf-8")
        status('running','Nine solves complete; generating figures and compiling the LaTeX paper',phase='report')
        paper_root=root/'paper'
        with (root/'log.paper').open('w') as log:
            child=subprocess.Popen(['python3',str(Path(__file__).with_name('paper.py')),str(job/'result.json'),str(paper_root)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:
                if child.wait(timeout=90):raise RuntimeError('PDF paper generation failed; see the retained report log')
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,9);child.wait();raise TimeoutError('PDF paper exceeded its 90-second limit')
        shutil.copyfile(paper_root/'paper.pdf',job/'paper.pdf')
        manifest = {}
        with zipfile.ZipFile(job / "evidence.zip", "w", zipfile.ZIP_DEFLATED) as bundle:
            total = 0
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    total += path.stat().st_size
                    if total > 48 * 1024 ** 2:
                        raise RuntimeError("Evidence size limit reached")
                    name = "cases/" + path.relative_to(root).as_posix()
                    manifest[name] = digest(path)
                    bundle.write(path, name)
            manifest["result.json"] = digest(job / "result.json")
            bundle.write(job / "result.json", "result.json")
            manifest["report.html"] = digest(job / "report.html")
            bundle.write(job / "report.html", "report.html")
            manifest['paper.pdf']=digest(job/'paper.pdf')
            bundle.write(job/'paper.pdf','paper.pdf')
            bundle.writestr("sha256.json", json.dumps(manifest, indent=2))
        status("complete", result["decision"], checks_passed=all_passed, evidence_sha256=digest(job / "evidence.zip"), result_sha256=digest(job / "result.json"), report_sha256=digest(job / "report.html"), paper_sha256=digest(job/'paper.pdf'))
    except Exception as exc:
        # Fixed commands and validated numerical inputs only; logs retained in a bounded ZIP for diagnosis.
        with zipfile.ZipFile(job / "failure.zip", "w", zipfile.ZIP_DEFLATED) as bundle:
            for path in root.rglob("log.*"):
                if path.stat().st_size < 6 * 1024 ** 2:
                    bundle.write(path, path.relative_to(root).as_posix())
        status("failed", str(exc)[:200])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def recover_interrupted():
    for path in WORK.iterdir():
        if path.is_dir() and re.fullmatch(r"[a-f0-9]{48}", path.name):
            shutil.rmtree(path)
    for job in DATA.iterdir():
        if job.is_dir() and (job / "status.json").exists():
            state = json.loads((job / "status.json").read_text())
            if state["state"] == "running":
                atomic_json(job / "status.json", {**state, "state": "failed", "message": "Worker restarted; submit a fresh run.", "updated_at": time.time()})


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    recover_interrupted()
    def heartbeat():
        while True:
            atomic_json(DATA / "worker.json", {"ready": shutil.which("simpleFoam") is not None, "time": time.time(), "revision": REVISION})
            time.sleep(3)
    threading.Thread(target=heartbeat, daemon=True).start()
    while True:
        for job in sorted(DATA.iterdir(), key=lambda p: p.stat().st_mtime):
            if not job.is_dir() or not re.fullmatch(r"[a-f0-9]{48}", job.name) or not (job / "status.json").exists():
                continue
            state = json.loads((job / "status.json").read_text())
            if state["state"] == "queued":
                if (job/'kind.json').exists():
                    from cooling_worker import execute_cooling
                    execute_cooling(job,WORK)
                else:execute(job)
            elif state["state"] in ("complete", "failed") and time.time() - state["updated_at"] > 48*3600:
                shutil.rmtree(job)
        time.sleep(1)


if __name__ == "__main__":
    main()
