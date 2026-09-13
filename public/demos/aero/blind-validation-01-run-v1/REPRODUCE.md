# Challenge 01 — reproduction guide

This is a nominal NACA 0012, steady-RANS experiment, not an as-built airfoil
certification or an independently blinded model-development exercise.
The setup supervisor was source-exposed. Solver execution was reference-withheld.
The public event ledger records which phases have actually occurred.

## Software and inputs

- Docker with Linux containers, local Python 3.8 or newer, and enough storage.
- Pinned image: `openfoam/openfoam10-paraview56@sha256:5992a995c1eacc16246de4cba583b5645cde7e4e8c480db83158dddbe07b36f6`.
- `code/case_driver.py` and `code/execute_case.py` must match the hashes in
  `preregistration.json`. The production snapshots must not be edited.
- All 18 operating points are listed in `input.json`. The production sweep uses
  three grid levels and 2,000 SIMPLE iterations per case.

Pull and inspect the pinned image before reproducing:

```sh
docker pull openfoam/openfoam10-paraview56@sha256:5992a995c1eacc16246de4cba583b5645cde7e4e8c480db83158dddbe07b36f6
docker image inspect openfoam/openfoam10-paraview56@sha256:5992a995c1eacc16246de4cba583b5645cde7e4e8c480db83158dddbe07b36f6
```

## Reproduce one independent case

From the unpacked reproduction directory:

```sh
python code/execute_case.py NEW_OUTPUT --level fine --angle -3.99 --duration 2000 --timeout 7200
python code/analyze_case.py NEW_OUTPUT
```

`NEW_OUTPUT` must not already exist. Use a different output directory for every
attempt. The executor limits the case to two CPUs, 4 GB of memory, no network,
non-root execution, and two narrow file mounts. It does not use an LLM, API token,
personal VM, Windows application, GB10, or RAG. Docker itself is a prerequisite;
this script does not install or alter the host's container service.

In this steady solver, `duration=2000` denotes SIMPLE iterations, **not seconds**.
The first launch can take longer if Docker must pull the image. The image download
occurs outside the isolated solver container; the case remains network-disabled.
The original archived run is not overwritten or extended by this command.

The executor returns a process receipt. A zero exit code does not constitute
numerical or physical acceptance. Inspect `analysis.json`, raw `solver.log`,
`mesh.log`, the force history and the retained fields. Reproduction can show
floating-point differences across hardware or OpenFOAM builds; the image digest,
input hashes and original results remain the comparison baseline.

## Reproduce the full parameter matrix

Use the angle list in `input.json` and all three `mesh_levels` in preregistration.
Create fresh outputs for every station/grid combination. The original
`run_sweep.py` also implements this matrix, but deliberately refuses to restart
an already completed or revealed protocol package. Do not falsify its ledger or
erase the published history to make a rerun look like the original experiment.
Independent repetitions should have their own identifiers and manifests.

## Permanent evidence downloads

After prediction freeze, `evidence/run-index.json` lists every complete case ZIP,
its byte size and SHA-256 hash. Paths are relative to this directory:

`https://alex-blythe.com/demos/aero/blind-validation-01-run-v1/`

Each case ZIP contains its own `archive-manifest.json`, mesh, generated deck,
initial/final fields, raw logs, force history, runtime receipt and extraction
results. The master `reproduction.zip` contains code, the report, comparison and
manifests; the case ZIPs are separate to avoid duplicating hundreds of megabytes.
These are versioned public assets, not temporary download links.

`python code/verify_release.py PATH_TO_COMPLETE_RELEASE` checks the release and
all ZIP members without extracting them. Install `cryptography` for the protocol
library used by that verifier. Report regeneration additionally requires
`matplotlib` and a LaTeX compiler. The production solver itself needs neither.

## Source rights and interpretation

Source: C. L. Ladson, NASA TM-4074 (1988), NTRS 19880019495, Table XIII first
subtable: <https://ntrs.nasa.gov/citations/19880019495>.
The reference transcription is published only after the prediction commitment;
the full source PDF and decryption key are not redistributed. Source version and
PDF hash are recorded in `input.json` and preregistration.

The nominal surface and mesh template derive from OpenFOAM Foundation 10.
The accompanying `evidence/OPENFOAM-COPYING.txt` retains its GPL license.
Hashes prove byte identity, not scientific validity. Failed numerical gates and
experimental disagreements are part of the retained record, not defects to hide.
