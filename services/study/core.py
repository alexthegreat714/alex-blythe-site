"""Fixed public channel study. No prompts, paths, code or commands in its input."""
import hashlib
import html
import json
import math
from pathlib import Path

REVISION = "channel-pressure-loss-v1"
RHO = 998.2
MU = 0.001003
WIDTH = 0.1
REFERENCE = "https://farside.ph.utexas.edu/teaching/336L/Fluidhtml/node134.html"
GRIDS = (("coarse", 32, 16), ("medium", 48, 24), ("fine", 64, 32))
DEFAULTS = {"length_mm": 200, "gap_mm": 2, "flow_ml_s": 20, "budget_pa": 70}
BOUNDS = {"length_mm": (100, 500), "gap_mm": (1, 3), "flow_ml_s": (1, 40), "budget_pa": (1, 1000)}


def validate(data):
    if not isinstance(data, dict) or set(data) != set(BOUNDS):
        raise ValueError("Supply only length_mm, gap_mm, flow_ml_s and budget_pa.")
    for key, (low, high) in BOUNDS.items():
        value = data[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f"{key} must be a finite number between {low} and {high}.")
    return {key: float(data[key]) for key in BOUNDS}


def brief(data):
    values = validate(data)
    length, flow = values["length_mm"] / 1000, values["flow_ml_s"] * 1e-6
    variants = []
    for factor in (0.75, 1, 1.25):
        gap = values["gap_mm"] / 1000 * factor
        speed = flow / (WIDTH * gap)
        dp = 12 * MU * length * flow / (WIDTH * gap ** 3)
        variants.append({"gap_mm": gap * 1000, "mean_velocity_m_s": speed,
                         "reynolds": RHO * speed * 2 * gap / MU, "analytical_pa": dp,
                         "analytical_margin_pa": values["budget_pa"] - dp})
    return {"revision": REVISION, "inputs": values, "variants": variants,
            "fluid": {"name": "Water, nominal 20 C", "rho_kg_m3": RHO, "mu_pa_s": MU},
            "width_mm": WIDTH * 1000, "reference_url": REFERENCE,
            "goal": "Choose the smallest of three channel gaps that meets the pressure-drop budget.",
            "scope": "Steady, incompressible, fully developed laminar flow between parallel plates. 2D flow; 100 mm reference width converts flow per width to total flow.",
            "assumptions": ["Constant water properties; no heat transfer.", "Parabolic inlet; no-slip stationary plates; zero gauge outlet pressure.",
                            "Spanwise empty boundaries omit sidewall drag. Bends, fittings, entrance losses and roughness are excluded."],
            "checks": {"reference_error_pct_max": 2, "medium_fine_change_pct_max": 1,
                       "mass_imbalance_pct_max": 0.1, "velocity_profile_error_pct_max": 2,
                       "residual_max": 1e-7},
            "decision_rule": "Recommend the smallest tested gap only if all numerical checks pass and its pressure drop plus the larger of analytical discrepancy or medium/fine difference stays below budget. This is a numerical allowance, not a total physical uncertainty bound."}


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, allow_nan=False), encoding="utf-8")
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def foam(name, body, cls="dictionary"):
    return f"FoamFile {{ version 2.0; format ascii; class {cls}; object {name}; }}\n{body}\n"


def report_html(result):
    """Portable engineering deliverable, generated solely from completed solver output."""
    esc = html.escape
    record = result["brief"]
    rows = "".join(f"<tr><td>{v['gap_mm']:.3g}</td><td>{v['analytical_pa']:.4g}</td><td>{v['pressure_drop_pa']:.4g}</td><td>{v['numerical_allowance_pa']:.3g}</td><td>{v['margin_pa']:.4g}</td><td>{'Meets' if v['meets_budget'] else 'Review / exceeds'}</td></tr>" for v in result["variants"])
    grids = "".join(f"<tr><td>{v['gap_mm']:.3g}</td><td>{g['grid']}</td><td>{g['cells']}</td><td>{g['iterations']}</td><td>{g['pressure_drop_pa']:.5g}</td><td>{g['reference_error_pct']:.3g}%</td><td>{g['mass_imbalance_pct']:.3g}%</td><td>{esc(', '.join(k for k, passed in g['gates'].items() if not passed) or 'All passed')}</td></tr>" for v in result["variants"] for g in v["levels"])
    requirements = "".join(f"<li>{esc(key)}: <b>{value:g}</b></li>" for key, value in record["inputs"].items())
    assumptions = "".join(f"<li>{esc(s)}</li>" for s in record["assumptions"])
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Aero | Channel study report</title>
<style>body{{font:15px/1.65 system-ui,sans-serif;background:#112029;color:#e0edef;max-width:1080px;margin:auto;padding:30px}}h1,h2{{line-height:1.2}}h2{{margin-top:32px;font-size:21px}}small{{color:#9fb9c1}}.decision{{border-left:4px solid #56c9b9;padding:14px 22px;background:#1b353f}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{text-align:left;border-bottom:1px solid #39505a;padding:9px}}.scroll{{overflow:auto}}a{{color:#8edce0}}code{{overflow-wrap:anywhere}}@media print{{body{{background:white;color:black;padding:0}}.decision{{background:#edf5f5}}small{{color:#555}}a{{color:#174858}}h2{{break-after:avoid}}tr{{break-inside:avoid}}}}</style>
<small>AERO / PRELIMINARY CHANNEL STUDY / {esc(result['revision'])}</small><h1>Which channel gap meets the pressure-drop budget?</h1>
<div class="decision"><strong>{esc(result['decision'])}</strong><p>Fresh OpenFOAM execution: 9 solves in {result['elapsed_seconds']:.1f} seconds. Numerical checks: {'passed' if result['checks_passed'] else 'review required'}.</p></div>
<h2>Requirements and model</h2><ul>{requirements}</ul><p>{esc(record['scope'])}</p><p>Fixed water properties: density {RHO} kg/m³; dynamic viscosity {MU} Pa·s.</p><ul>{assumptions}</ul>
<h2>First-principles comparison</h2><p>For this fully developed parallel-plate model, Q = W h Ū and Δp = 12 μ L Q / (W h³). The Reynolds number uses hydraulic diameter 2h. The model omits sidewall and entrance losses.</p>
<p>Reference: <a href="{REFERENCE}">Richard Fitzpatrick, Flow Between Parallel Plates, University of Texas at Austin</a>. This is an analytical solution comparison, not comparison to a measured device.</p>
<h2>Gap decision</h2><div class="scroll"><table><thead><tr><th>Gap mm</th><th>Analytical Pa</th><th>OpenFOAM Pa</th><th>Allowance Pa</th><th>Budget margin Pa</th><th>Decision</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>{esc(record['decision_rule'])}</p><p>{esc(result['interpretation'])}</p>
<h2>Mesh and solver evidence</h2><div class="scroll"><table><thead><tr><th>Gap mm</th><th>Grid</th><th>Cells</th><th>Iterations</th><th>Δp Pa</th><th>Reference error</th><th>Mass imbalance</th><th>Checks</th></tr></thead><tbody>{grids}</tbody></table></div>
<p>Pass thresholds: reference error &lt;2%; medium/fine pressure change &lt;1%; flux imbalance &lt;0.1%; velocity-profile L2 error &lt;2%; final initial residuals ≤10⁻⁷; solver reports convergence; mesh passes checkMesh.</p>
<p>Pressure is fitted over the middle half of the channel and extrapolated to its length. Incompressible OpenFOAM pressure is multiplied by density to obtain Pa. Values are extracted from final p, U and phi fields. Residual histories, exact dictionaries, generated meshes and final fields are in the evidence ZIP.</p>
<h2>Reproducibility</h2><p>Solver: {esc(result['provenance']['solver'])}. Study ID: <code>{esc(result['id'])}</code>.</p><p>Worker SHA-256: <code>{result['provenance']['worker_source_sha256']}</code><br>Case generator SHA-256: <code>{result['provenance']['case_generator_sha256']}</code>.</p>
<p>The ZIP contains this report, result.json and sha256.json covering its case files. Download the report and evidence within 48 hours; use your browser's Print / Save as PDF for a PDF copy.</p></html>"""


def materialize(root, data, gap_mm, nx, ny):
    """Only validated scalars are substituted into source-owned OpenFOAM dictionaries."""
    data = validate(data)
    root = Path(root)
    for folder in ("0", "constant", "system"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    length, gap = data["length_mm"] / 1000, gap_mm / 1000
    speed = data["flow_ml_s"] * 1e-6 / (WIDTH * gap)
    # Midpoint face values normalized to the specified finite-volume flux.
    weights = [6 * ((j + .5) / ny) * (1 - (j + .5) / ny) for j in range(ny)]
    norm = sum(weights) / ny
    inlet = "\n".join(f"({speed * value / norm:.12g} 0 0)" for value in weights)
    files = {
        "system/blockMeshDict": foam("blockMeshDict", f"""
convertToMeters 1;
vertices ((0 0 0) ({length} 0 0) ({length} {gap} 0) (0 {gap} 0)
          (0 0 0.001) ({length} 0 0.001) ({length} {gap} 0.001) (0 {gap} 0.001));
blocks (hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) simpleGrading (1 1 1));
edges ();
boundary (
 inlet {{type patch; faces ((0 4 7 3));}}
 outlet {{type patch; faces ((1 2 6 5));}}
 walls {{type wall; faces ((0 1 5 4) (3 7 6 2));}}
 frontAndBack {{type empty; faces ((0 3 2 1) (4 5 6 7));}}
);
mergePatchPairs ();
"""),
        "constant/physicalProperties": foam("physicalProperties", f"viscosityModel constant;\nnu {MU / RHO:.15g};"),
        "constant/momentumTransport": foam("momentumTransport", "simulationType laminar;"),
        "0/U": foam("U", f"""dimensions [0 1 -1 0 0 0 0];
internalField uniform ({speed} 0 0);
boundaryField {{
 inlet {{type fixedValue; value nonuniform List<vector> {ny} ( {inlet} );}}
 outlet {{type zeroGradient;}}
 walls {{type noSlip;}}
 frontAndBack {{type empty;}}
}}""", "volVectorField"),
        "0/p": foam("p", """dimensions [0 2 -2 0 0 0 0];
internalField uniform 0;
boundaryField {
 inlet {type zeroGradient;}
 outlet {type fixedValue; value uniform 0;}
 walls {type zeroGradient;}
 frontAndBack {type empty;}
}""", "volScalarField"),
        "system/controlDict": foam("controlDict", """application simpleFoam;
startFrom startTime; startTime 0; stopAt endTime; endTime 1200; deltaT 1;
writeControl timeStep; writeInterval 1200; purgeWrite 1; writeFormat ascii;
writePrecision 12; writeCompression off; timeFormat general; timePrecision 8;
runTimeModifiable false;
"""),
        "system/fvSchemes": foam("fvSchemes", """
ddtSchemes {default steadyState;}
gradSchemes {default Gauss linear;}
divSchemes {default none; div(phi,U) bounded Gauss linearUpwind grad(U); div((nuEff*dev2(T(grad(U))))) Gauss linear;}
laplacianSchemes {default Gauss linear corrected;}
interpolationSchemes {default linear;}
snGradSchemes {default corrected;}
"""),
        "system/fvSolution": foam("fvSolution", """
solvers {
 p {solver GAMG; smoother GaussSeidel; tolerance 1e-10; relTol 0.01;}
 U {solver smoothSolver; smoother symGaussSeidel; tolerance 1e-10; relTol 0.01;}
}
SIMPLE {nNonOrthogonalCorrectors 0; residualControl {p 1e-8; U 1e-8;}}
relaxationFactors {fields {p 0.3;} equations {U 0.7;}}
"""),
    }
    for name, content in files.items():
        (root / name).write_text(content, encoding="utf-8")
    return files
