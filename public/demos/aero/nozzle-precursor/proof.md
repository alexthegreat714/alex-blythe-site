# Compressible nozzle precursor — Aero run proof

**Disposition:** Solver completed; numerical status `NOT_ESTABLISHED`. This is a bounded teaching run, not validated nozzle performance.

## Setup

- Planar converging-diverging nozzle, 0.3 m long, one cell through a 0.012 m span.
- Perfect-gas air, laminar, adiabatic walls; OpenFOAM `rhoSimpleFoam`.
- 0.01 kg/s prescribed inlet mass flow at 300 K; 101325 Pa outlet.
- Four-block, 864-cell mesh.

## Recorded gates

- Run completion: **PASS**; finalization artifacts were written.
- Mesh quality: **PASS** in the retained result; no negative-volume condition.
- Residual convergence: **PASS**; worst final residual below `1e-4`.
- Mass conservation: **PASS**; reported net mass imbalance 0%.
- Energy conservation: **NOT EVALUATED**; the solver evidence contains no energy-balance report. This blocks numerical acceptance.
- Independent validation: **NOT EVALUATED**; no experimental or equivalent reference is attached.

## Evidence

- [Case inputs](case.json)
- [Mesh study](mesh-study.json)
- [Engineering result and all gates](engineering-result.json)
- [Recorded result view](images/result.svg)

Changing geometry, boundary conditions, material properties, or solver settings invalidates applicability of this recorded result. A new run and energy/validation review are required.
