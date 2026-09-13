# Aero Verification Bench — Rev 1.0

Recorded 13 September 2026. Numerical verification and controlled negative tests,
not experimental validation, autonomous LLM diagnosis, or design-release evidence.

## Contents and disposition

- Five new OpenFOAM Foundation 10 laminar-pipe runs at the declared Re=200.
  Coarse/medium/fine pass the 2% pressure-reference allowance. Two radial cells
  miss by 13.96%; doubled deck viscosity misses the original reference by 99.61%.
- Two new low-Mach nozzle SST wall-treatment diagnostics: both NOT_ESTABLISHED
  and both fail the nominated y+ area screen. Neither reaches the built-in stop.
  The direct low-Re active fields have small residuals; only its essentially zero
  transverse component retains a large normalized residual. The wall-function run
  has significant active-field residuals. These are different numerical outcomes.
  This is not the older wall-refinement-v6 nozzle and does not revalidate it.
- Two synthetic STEP reimports. The connected manifold passes topology only;
  adding a detached sliver causes rejection before mesh/solve. No automatic repair.
- Five retained CalculiX solves from 12 September: pressure tube coarse/medium/fine,
  ported tube fine, thermal-gradient fine. Original receipts preserve their states.
  These are archived prior solves, not new runs or newly established validation.

The published PDF documents equations, measurements, acceptance criteria,
conservation, wall diagnostics, limitations and the protocol revision history.
The front page links the bench through See the evidence.

## Verify the permanent archive

Extract `reproducibility.zip` to a new directory. From that directory:

```sh
python source/audit.py .
python -m unittest discover -s source -p test_audit.py
```

The first command checks every file listed in manifest.json. It detects changed,
missing, and escaped paths. SHA-256 establishes identity, not scientific validity
or authenticity by itself. Verify the ZIP hash against the site's public manifest
as well. The archive includes original per-case input manifests and original
CalculiX manifests. The accompanying public summary records image content IDs.
Those IDs identify local executed images; they are not public registry pull URLs.

Curated versioned assets have no application-level 48-hour expiration. This does
not change the retention of separately submitted visitor jobs or guarantee hosting
availability forever. Preserve the download independently when citing a result.

## Rerun an archived OpenFOAM deck

Use Linux with OpenFOAM **Foundation 10** configured in the shell. Copy, do not
overwrite, the retained case. Example (choose a new scratch path):

```sh
mkdir -p scratch/pipe-fine
cp -R openfoam/pipe-fine/0 openfoam/pipe-fine/constant openfoam/pipe-fine/system scratch/pipe-fine/
cp openfoam/pipe-fine/wall-geometry.json scratch/pipe-fine/
blockMesh -case scratch/pipe-fine > scratch/pipe-fine/log.blockMesh 2>&1
checkMesh -case scratch/pipe-fine > scratch/pipe-fine/log.checkMesh 2>&1
simpleFoam -case scratch/pipe-fine > scratch/pipe-fine/log.simpleFoam 2>&1
```

The archived final fields are not copied into scratch. Compare the new logs,
pressure-gradient reference, residuals and flux CSVs rather than assuming identical
bytes across platforms. `source/runtime.py` contains the exact executed generator,
extractor, and initial runtime gate. Its CLI expects read-only `/source` and writable
`/output` mounts, Python+NumPy and the OpenFOAM executables on PATH:

```sh
python3 /source/runtime.py pipe --out /output
python3 /source/runtime.py nozzle --out /output
```

Use an EMPTY output directory for a new run: existing result.json files are resumed.
For diagnosis/extraction of a scratch case, `runtime.extract` is importable; pressure
sampling and postProcessing parsing are shown in that source. `source/audit.py`
adds a stricter publication check requiring all four pressure/velocity residual
components. It independently agreed with all five recorded final pipe outcomes.

For the STEP fixture, `python /source/geometry.py` requires CadQuery 2.7.0 /
OCP 7.8.1.1 and writes to `/output`. Geometry units are mm, OpenFOAM units are m.
This fixture is generated, exported and reimported; it is not customer geometry.

## Rerun a retained CalculiX deck

Use CalculiX 2.20. From the extracted archive:

```sh
mkdir -p scratch/tube-fine
cp calculix/tube/fine/job.inp scratch/tube-fine/
cd scratch/tube-fine
ccx job > solver.log 2>&1
```

The complete job.inp contains the mesh, material, loads and constraints. Gmsh
4.15.2 and CadQuery 2.7.0 produced the retained geometry/mesh, but are not needed
to solve that already-written deck. Source geometry and meshes remain available.
Read the receipt and result for each case's accepted quantities and failed gates.

## Protocol transparency

Initial diagnostics are retained in `initial-diagnostics/`. The v1.0 gate rejected
pipe cases because the nearly zero out-of-plane velocity had an ill-conditioned
normalized residual. Before the final rerun, criteria v1.1 added an explicit
negligible-velocity test (max component / bulk <=1e-10). Pressure is never exempt.
This was a disclosed post-diagnostic correction, not a blinded preregistration.
Built-in convergence flags are retained separately; the pipe runs reached their
fixed stop. The original diagnostic criteria file is not reconstructed: original
outcomes and the revision note document the change, not a fabricated v1.0 hash.

Earlier setup defects (collapsed wedge faces, missing meshWave wall-distance
scheme) were repaired before the reported final seven CFD runs. Initial setup
failures remain in local diagnostic folders; only the pre-final summary results
are included in this curated archive. They are not counted as successful runs.

Pipe pressure is a fitted interior pressure gradient times full length; it is not
an entrance-loss measurement. The reference is the Poiseuille equation in OpenStax,
University Physics Vol. 1, section 14.7:
https://openstax.org/books/university-physics-volume-1/pages/14-7-viscosity-and-turbulence

Nozzle y+ uses OpenFOAM's exported wall field. Different wall treatments can use
different effective wall-scaling evaluations; the comparison is a suitability
diagnostic, not an independent wall-shear validation. Nominal areas come from the
generated wedge geometry; direct low-Re omega uses approximate first-cell height.
The selected 95% area screens are requirements for this bench, not universal laws.

## Maintainer publication

Within the Engineering tree, `python Aero/verification/publish.py` verifies inputs,
re-evaluates gates, generates plots, assembles the archive and writes paper.tex.
It requires the original local run folders (not included as that directory layout
in the extracted public bundle). Compile paper.tex, render and visually inspect
every PDF page, then `python Aero/verification/publish.py --finalize`. Do not modify
Rev 1.0 results in place when doing new physics: create a new revision and preserve
old URLs. No solver or private service is started by the public evidence page.
