# NACA 0012 · OpenFOAM tutorial run

**Disposition:** Recorded teaching run · not NASA validation

## Actual run

- Executed: 2026-09-12 in an isolated Linux/OpenFOAM Foundation v10 container.
- Source: [OpenFOAM Foundation v10 aerofoilNACA0012 tutorial](https://github.com/OpenFOAM/OpenFOAM-10/tree/master/tutorials/compressible/rhoSimpleFoam/aerofoilNACA0012)
- NACA 0012 tutorial geometry and mesh
- rhoSimpleFoam; compressible steady k-ω SST RANS
- 250 m/s inlet speed; 0° angle of attack
- Tutorial air properties and boundary conditions

## Observed evidence

- 16,200 cells
- 1,581 SIMPLE iterations
- Mesh check: warning
- CL = 0.000003
- CD = 0.007910
- last-50 CL spread = 18.8947%
- Final field directory exists in the local retained run.

## Gates

- Solver Completion: pass
- Mesh Quality: warning
- Grid Independence: not established
- Independent Validation: not established
- Design Release: blocked

## Limitations and next validation work

- checkMesh reports one failed check: 710 high-aspect-ratio cells (maximum 42,738). No negative-volume or non-orthogonality failure was reported.
- This is not the NASA TMR or AIAA DPW-6 Mach/Reynolds/angle-of-attack condition.
- No grid-independence study, experimental comparison, or Cp/Cf comparison was performed.
- Solver convergence proves numerical completion, not physical validity or design readiness.

## Evidence SHA-256

- `log.checkMesh`: `1a0ded7ba949dc31104a99a51fcd12abe7c15ce8489ff934ed334f698480c51e`
- `log.rhoSimpleFoam`: `9de88027ca4d78c260389c434734876d45618577c76d516150d80663ad8c9997`
- `forceCoeffs.dat`: `62c8c0f5fcc13ad56bf0b480db10916110335364ee723c8517c4cdaa0607db93`
- `force-history.svg`: `ec3e66ed00730cc733d1ea5fc44d90ddc13bb05e62db19a434b5ef6b6a1d7326`

The published logs are copies of the retained local files. Changed requirements, geometry, mesh, turbulence model, or boundary conditions require a new run and proof revision.
