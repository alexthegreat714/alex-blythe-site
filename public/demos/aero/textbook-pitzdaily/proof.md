# Backward-facing step · pitzDaily tutorial run

**Disposition:** Recorded teaching run · not experimental validation

## Actual run

- Executed: 2026-09-12 in an isolated Linux/OpenFOAM Foundation v10 container.
- Source: [OpenFOAM Foundation v10 pitzDaily tutorial](https://openfoam.org/download/10-source/)
- OpenFOAM Foundation v10 pitzDaily backward-facing-step mesh
- simpleFoam; incompressible steady k-ε RANS
- Uniform inlet velocity 10 m/s; kinematic viscosity 10⁻⁵ m²/s
- Tutorial boundary conditions

## Observed evidence

- 12,225 cells
- 287 SIMPLE iterations
- Mesh check: pass
- Final field directory exists in the local retained run.

## Gates

- Solver Completion: pass
- Mesh Quality: pass
- Grid Independence: not established
- Independent Validation: not established
- Design Release: blocked

## Limitations and next validation work

- Mesh and solver completion are documented, but no mesh-independence study was performed.
- No independent experimental validation or design-use claim is made.
- The full OpenFOAM field directories are retained locally, not published to the public browser.

## Evidence SHA-256

- `log.checkMesh`: `d65d9f3e8f5fcf97055296b2795ee5b73aab0b5f267e725f96b3ac23407603df`
- `log.simpleFoam`: `711d11169eec7f81948ac1d2c6facf4b2634c2bfd263adc77edb936fbbcba90e`

The published logs are copies of the retained local files. Changed requirements, geometry, mesh, turbulence model, or boundary conditions require a new run and proof revision.
