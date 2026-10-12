# Aero first-principles heat-exchanger notebook — Rev 1.0

October 12, 2026. Public synthetic educational example, not employer work.

The public page is `/software/aero/first-principles/`. It provides rendered LaTeX,
expandable equation source, deterministic browser recalculation, and retained
small finite-element verification. This does not publish the private LaTeX app.

## Reproduce

With Python 3 and NumPy installed, download `verify.py` and `inputs.json` into
one directory. Run `python verify.py`. The script runs nine tests and generates
`results.json`, `pressure-convergence.csv`, and `pressure-convergence.svg`.
The recorded NumPy version is 2.3.5. No GPU, model, credential, network call,
private service, or conventional solver is required.

Compile `proof.tex` using an existing LaTeX runtime. The published `proof.pdf`
was compiled with bundled Tectonic. The LaTeX document's source equations are
independent of the model smoke-test output. Those failed outputs remain failed.

## Model scope

Pressure-only: straight long closed-end isotropic tube, generalized axial strain,
linear radial finite elements, 3-point Gauss quadrature. Analytical reference is
the independently derived Lamé solution with closed-end axial force balance.

Thermal-only: uniform axial tube/bar, traction-free transverse surfaces, either
one end axially free or both ends axially fixed. Constant uniform temperature.
The free/fully axial restrained cases are distinct. No triaxial-restraint claim.

These are three separate cases, not a combined load qualification. There is no
material certification, buckling, plasticity, fatigue, creep, weld, tube-sheet
contact or CFD-mapped temperature assessment. No HX historical result is changed.

## Evidence meanings

- ASSUMED: all synthetic geometry, material and load inputs.
- CALCULATED: analytical values and small FE outputs; nine executable checks.
- OBSERVED: separately retained October 12 local model runtime smoke test.
- NOT_ESTABLISHED: physical validation, real hardware safety, private-page
  end-to-end 3090 execution, and real exchanger qualification.

The runtime receipt is a sanitized summary, not a raw private-corpus export.
Model execution succeeded while arithmetic failed. The published worksheet
therefore uses deterministic calculations rather than trusting model reasoning.

## Custody

`manifest.json` hashes the public assets. `verification.json` records actual
missing/mismatch counts. Hashes establish integrity against recorded values,
not physics correctness or an external trusted timestamp.

This is notebook Rev 1.0, not a new operational Aero software revision.
