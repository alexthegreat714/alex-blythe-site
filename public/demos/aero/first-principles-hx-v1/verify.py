"""Reproduce this public educational example: python verify.py.

Requires Python 3 and NumPy. No model, GPU, CFD, private service or network access.
The small FE implementations verify idealized equations, not real hardware.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parent
INPUTS = json.loads((ROOT / "inputs.json").read_text(encoding="utf-8"))


def validate(p):
    a, b = p["inner_radius_m"], p["outer_radius_m"]
    if not (0 < a < b and p["length_m"] > 0 and p["youngs_modulus_Pa"] > 0):
        raise ValueError("Positive geometry and modulus required")
    if not (-1 < p["poisson_ratio"] < 0.5):
        raise ValueError("Stable isotropic elasticity required")


def lame(p, r):
    validate(p)
    a, b = p["inner_radius_m"], p["outer_radius_m"]
    pi, po = p["internal_gauge_pressure_Pa"], p["external_gauge_pressure_Pa"]
    E, nu = p["youngs_modulus_Pa"], p["poisson_ratio"]
    A = (pi*a*a-po*b*b)/(b*b-a*a)
    B = a*a*b*b*(pi-po)/(b*b-a*a)
    sr, st, sz = A-B/r**2, A+B/r**2, A
    vm = math.sqrt(((st-sr)**2+(sr-sz)**2+(sz-st)**2)/2)
    u = ((1-2*nu)*A*r+(1+nu)*B/r)/E
    return {"A_Pa": A, "B_Pa_m2": B, "radial_Pa": sr,
            "hoop_Pa": st, "axial_Pa": sz, "von_mises_Pa": vm,
            "radial_displacement_m": u}


def pressure_fe(p, n):
    """Linear radial FE + one constant axial-strain DOF (closed ends).

    3-point Gauss integration, full 3D isotropic constitutive matrix;
    radial/hoop/axial strains, no shear. End force enters virtual work.
    """
    validate(p)
    a, b, L = p["inner_radius_m"], p["outer_radius_m"], p["length_m"]
    E, nu = p["youngs_modulus_Pa"], p["poisson_ratio"]
    lam, mu = E*nu/((1+nu)*(1-2*nu)), E/(2*(1+nu))
    D = np.full((3, 3), lam) + np.eye(3)*2*mu
    r = np.linspace(a, b, n+1)
    K, f = np.zeros((n+2, n+2)), np.zeros(n+2)
    xis, weights = np.polynomial.legendre.leggauss(3)
    samples = []
    for i in range(n):
        h = r[i+1]-r[i]
        ids = [i, i+1, n+1]
        for xi, weight in zip(xis, weights):
            N = np.array([(1-xi)/2, (1+xi)/2])
            rg = float(N @ r[i:i+2])
            B = np.array([[-1/h, 1/h, 0], [N[0]/rg, N[1]/rg, 0], [0, 0, 1]])
            dv = 2*math.pi*rg*L*h/2*weight
            K[np.ix_(ids, ids)] += B.T @ D @ B * dv
            samples.append((ids, rg, B, dv))
    pi, po = p["internal_gauge_pressure_Pa"], p["external_gauge_pressure_Pa"]
    f[0], f[n] = 2*math.pi*a*L*pi, -2*math.pi*b*L*po
    f[-1] = math.pi*(pi*a*a-po*b*b)*L
    q = np.linalg.solve(K, f)
    err, ref = 0.0, 0.0
    for ids, rg, B, dv in samples:
        actual = D @ B @ q[ids]
        exact = lame(p, rg)
        target = np.array([exact["radial_Pa"], exact["hoop_Pa"], exact["axial_Pa"]])
        err += float((actual-target) @ (actual-target))*dv
        ref += float(target @ target)*dv
    uexact = lame(p, b)["radial_displacement_m"]
    # Convert the axial generalized-work equation (N*m) to force (N) before
    # forming a norm alongside the radial-force equations. Do not mix units.
    imbalance = K @ q-f
    force_residual = np.linalg.norm(np.r_[imbalance[:-1], imbalance[-1]/L])
    force_scale = np.linalg.norm(np.r_[f[:-1], f[-1]/L])
    residual = force_residual/max(force_scale, 1.0)
    return {"elements": n, "outer_u_m": float(q[n]), "axial_strain": float(q[-1]),
            "outer_u_relative_error": abs(float(q[n])-uexact)/max(abs(uexact), 1e-30),
            "gauss_stress_relative_L2_error": math.sqrt(err/ref) if ref else 0.0,
            "normalized_equilibrium_residual": float(residual)}


def thermal_fe(p, n, restrained):
    """Uniform 1D thermal bar with real assembled element thermal loads."""
    E, L = p["youngs_modulus_Pa"], p["length_m"]
    area = math.pi*(p["outer_radius_m"]**2-p["inner_radius_m"]**2)
    eth = p["thermal_expansion_per_K"]*p["uniform_temperature_rise_K"]
    K, f = np.zeros((n+1, n+1)), np.zeros(n+1)
    h = L/n
    for i in range(n):
        ids = [i, i+1]
        K[np.ix_(ids, ids)] += E*area/h*np.array([[1, -1], [-1, 1]])
        f[ids] += E*area*eth*np.array([-1, 1])
    fixed = {0, n} if restrained else {0}
    free = [i for i in range(n+1) if i not in fixed]
    u = np.zeros(n+1)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], f[free])
    stress = E*(np.diff(u)/h-eth)
    reactions = K @ u-f
    exact_u, exact_s = (0.0, -E*eth) if restrained else (eth*L, 0.0)
    residual = np.linalg.norm(reactions[free])/max(np.linalg.norm(f), 1.0)
    return {"elements": n, "restrained": restrained, "end_u_m": float(u[-1]),
            "mean_stress_Pa": float(np.mean(stress)),
            "max_stress_error_Pa": float(np.max(np.abs(stress-exact_s))),
            "end_u_error_m": abs(float(u[-1])-exact_u),
            "left_reaction_N": float(reactions[0]), "right_reaction_N": float(reactions[-1]),
            "normalized_equilibrium_residual": float(residual)}


class EquationTests(unittest.TestCase):
    def test_inner_and_outer_traction(self):
        p = INPUTS
        self.assertAlmostEqual(lame(p, p["inner_radius_m"])["radial_Pa"], -p["internal_gauge_pressure_Pa"], places=7)
        self.assertAlmostEqual(lame(p, p["outer_radius_m"])["radial_Pa"], -p["external_gauge_pressure_Pa"], places=7)

    def test_closed_end_force_balance(self):
        p = INPUTS
        area = math.pi*(p["outer_radius_m"]**2-p["inner_radius_m"]**2)
        self.assertAlmostEqual(lame(p, p["inner_radius_m"])["axial_Pa"]*area,
                               math.pi*p["internal_gauge_pressure_Pa"]*p["inner_radius_m"]**2, places=8)

    def test_radial_differential_equilibrium(self):
        p, r = INPUTS, 0.0105
        v = lame(p, r)
        derivative = 2*v["B_Pa_m2"]/r**3
        self.assertLess(abs(derivative+(v["radial_Pa"]-v["hoop_Pa"])/r), 1e-5)

    def test_zero_pressure_zero_response(self):
        p = dict(INPUTS, internal_gauge_pressure_Pa=0.0, external_gauge_pressure_Pa=0.0)
        self.assertEqual(lame(p, p["inner_radius_m"])["von_mises_Pa"], 0)
        self.assertEqual(pressure_fe(p, 4)["outer_u_m"], 0)

    def test_pressure_fe_refines_towards_reference(self):
        rows = [pressure_fe(INPUTS, n) for n in INPUTS["radial_meshes"]]
        self.assertTrue(all(b["gauss_stress_relative_L2_error"] < a["gauss_stress_relative_L2_error"] for a, b in zip(rows, rows[1:])))
        lim = INPUTS["verification_limits"]
        self.assertLess(rows[-1]["outer_u_relative_error"], lim["finest_outer_displacement_relative_error"])
        self.assertLess(rows[-1]["gauss_stress_relative_L2_error"], lim["finest_gauss_stress_relative_L2_error"])
        self.assertTrue(all(row["normalized_equilibrium_residual"] < lim["normalized_equilibrium_residual"] for row in rows))

    def test_free_thermal_bar(self):
        p = INPUTS
        for n in p["thermal_meshes"]:
            row = thermal_fe(p, n, False)
            self.assertLess(row["end_u_error_m"], 1e-12)
            stress_scale = max(p["youngs_modulus_Pa"]*abs(p["thermal_expansion_per_K"]*p["uniform_temperature_rise_K"]), 1.0)
            self.assertLess(row["max_stress_error_Pa"], stress_scale*p["verification_limits"]["thermal_relative_error"])

    def test_fixed_thermal_bar_reactions(self):
        p = INPUTS
        for n in p["thermal_meshes"]:
            row = thermal_fe(p, n, True)
            self.assertLess(row["end_u_error_m"], 1e-12)
            stress_scale = max(p["youngs_modulus_Pa"]*abs(p["thermal_expansion_per_K"]*p["uniform_temperature_rise_K"]), 1.0)
            self.assertLess(row["max_stress_error_Pa"], stress_scale*p["verification_limits"]["thermal_relative_error"])
            self.assertAlmostEqual(row["left_reaction_N"]+row["right_reaction_N"], 0, places=8)

    def test_units_and_known_values(self):
        p = INPUTS
        self.assertAlmostEqual(p["thermal_expansion_per_K"]*p["uniform_temperature_rise_K"]*p["length_m"]*1000, 1.28)
        self.assertAlmostEqual(p["youngs_modulus_Pa"]*p["thermal_expansion_per_K"]*p["uniform_temperature_rise_K"]/1e6, 243.2)
        self.assertAlmostEqual(lame(p, p["inner_radius_m"])["hoop_Pa"]/1e6, 21.047619047619, places=8)

    def test_invalid_geometry_rejected(self):
        with self.assertRaises(ValueError):
            lame(dict(INPUTS, outer_radius_m=0.009), 0.01)


def chart(rows):
    points = [(75+500*math.log2(row["elements"]/4)/4,
               280-210*math.log10(0.1/row["gauss_stress_relative_L2_error"])/3) for row in rows]
    line = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    circles = "".join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="#6cddd4"/>' for x, y in points)
    labels = "".join(f'<text x="{x:.2f}" y="318" text-anchor="middle">{row["elements"]}</text>' for (x,y), row in zip(points,rows))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="680" height="375" viewBox="0 0 680 375" role="img" aria-labelledby="title desc">
<title id="title">Computed pressure FE stress error under refinement</title><desc id="desc">Volume-weighted Gauss-point stress error against the independent Lame solution. Actual computed errors, not a solver screenshot.</desc>
<rect width="680" height="375" rx="14" fill="#142127"/><g fill="#c6d6db" font-family="sans-serif" font-size="14">
<text x="32" y="34" font-size="20" fill="#edf6f8">Pressure FE verification · actual computed error</text>
<text x="32" y="58">Relative stress L2 error · logarithmic vertical axis</text>
<path d="M75 90V295H585" fill="none" stroke="#57717d"/>
<text x="28" y="286">10%</text><text x="28" y="216">1%</text><text x="21" y="146">0.1%</text><text x="12" y="76">0.01%</text>
<polyline points="{line}" fill="none" stroke="#6cddd4" stroke-width="3"/>{circles}{labels}
<text x="330" y="350" text-anchor="middle">Radial elements (uniform refinement)</text></g></svg>'''


def main():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EquationTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    p = INPUTS
    pressure = [pressure_fe(p, n) for n in p["radial_meshes"]]
    thermal = [thermal_fe(p, n, fixed) for fixed in [False, True] for n in p["thermal_meshes"]]
    record = {"schema": "aero.public.first_principles_hx.v1", "date": "2026-10-12",
              "case_id": p["case_id"], "type": "CALCULATED_SYNTHETIC_VERIFICATION",
              "inputs_sha256": hashlib.sha256((ROOT/"inputs.json").read_bytes()).hexdigest(),
              "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "numpy_version": np.__version__, "tests": {"run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors)},
              "analytical_inner": lame(p, p["inner_radius_m"]), "analytical_outer": lame(p, p["outer_radius_m"]),
              "pressure_fe": pressure, "thermal_fe": thermal,
              "proof_scope": "Equation consistency and idealized FE discretization verification only",
              "physical_validation": "NOT_ESTABLISHED", "hardware_design_qualification": "NOT_ESTABLISHED",
              "production_solver_used": False, "GPU_required": False}
    (ROOT/"results.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    with (ROOT/"pressure-convergence.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(pressure[0]))
        writer.writeheader()
        writer.writerows(pressure)
    (ROOT/"pressure-convergence.svg").write_text(chart(pressure), encoding="utf-8")
    print(json.dumps({"tests": record["tests"], "finest_pressure": pressure[-1], "thermal": thermal[-1]}, indent=2))


if __name__ == "__main__":
    main()
