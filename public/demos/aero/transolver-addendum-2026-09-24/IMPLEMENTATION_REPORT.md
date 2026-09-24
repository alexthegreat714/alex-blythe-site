# NVIDIA Transolver reference adapter — September 24, 2026

Status: `IMPLEMENTED_NOT_FULLY_VALIDATED`. Optional personal research capability;
not a conventional solver replacement or a qualified engineering surrogate.

## What actually executed

- Pinned NVIDIA DrivAerML surface checkpoint, 39,188,235 bytes; SHA-256
  `eb98f399a050a8f8a24919335c61642e4a835bd4044f7e21abec231aa31fd82c`.
- 200,000 deterministically selected native boundary cells from retained run 1.
- Original PhysicsNeMo Transolver and data pipe; no rewritten neural architecture.
- Strict state-dictionary load; checkpoint contains 20 layers and 9,763,236 parameters,
  despite the model card's eight-layer description.
- Existing isolated PhysicsNeMo 2.2.0/PyTorch 2.10.0+cu130 worker on RTX 3090.
- Forward pass 2.404 s; complete adapter 73.958 s; peak allocated GPU memory 10.727 GB.
- Native cell IDs and coordinates retained with prediction. No full-surface integral
  or conservation claim. Exact repeatability has not been measured.

The executable demonstrator uses `PhysicsAI(..., reference_worker=config).predict`
with model ID `nvidia-transolver-drivaerml-surface-1.0`, the fixed run-1 case identity,
both surface outputs, and explicit research acknowledgement. Preflight verifies
contract, approval, checkpoint, preprocessing, source/reference hashes and resource
scope. It never downloads, installs, pulls an image or restarts another service.
Missing resources, unsupported cases, timeout, OOM and missing output fail closed.

## Accuracy and provenance are not inferred from execution

Raw VTP pressure is consistent with kinematic pressure: its Cp relation agrees to
relative L2 `3.58e-8`. Comparing pascals directly to that raw field is invalid.
A separate retrospective dimensional audit preserves the raw comparison and multiplies
the reference by the already-declared density; it does not change predictions or fit
an offset. Pressure relative L2 discrepancy remains **56.2%**. Shear discrepancy is
**82.8%**, conditional on the standard incompressible OpenFOAM shear-field units.
These are descriptive discrepancies, not scores against a new acceptance threshold.

Remaining limitations include checkpoint training/preprocessing compatibility, exact
held-out split membership, training ranges and cross-version numerical equivalence.
The checkpoint was saved with PhysicsNeMo 1.3.0. The reference uses the retained
38.889 m/s operating input; NVIDIA's wrapper defaults to 30 m/s. No input is tuned
to make this result look better.

Evidence ingestion uses existing `build_result`, `retain_result`, `verify_result`
and `annotate_gate`. Applicability stays `NOT_ESTABLISHED`, authority `RESEARCH_ONLY`,
independence `LOW` relative to OpenFOAM, and gate disposition `INCONCLUSIVE`.
Heat-exchanger geometry is explicitly out of distribution. No active campaign is
attached or qualified by this demonstration.

## Custody and deployment

Canonical execution and audit evidence are retained outside this source archive.
The existing DoMINO reference is mounted read-only. Checkpoint/runtime/cache/output
are on D:. Failed archive-inspection/cache probes are documented, not hidden.
No production runtime installation, new CFD, training, HX change or employer-data
ingestion occurred. This adapter is now included in the public Transolver addendum. It has **not**
been deployed to the running private service; earlier Rev 2.3 downloads remain unchanged.

The original THUML Transolver++ entry remains a distinct pending model; it was not
silently repointed. The NVIDIA model uses NVIDIA Open Model Agreement; framework
code is Apache-2.0 and retained DrivAerML reference data is CC-BY-SA-4.0. Do not
bundle weights or geometry into Aero's public source release.

Next bounded investigation: establish the checkpoint's original preprocessing and
operating-input convention independently, then predeclare any new comparison.
Do not fit normalization, signs, velocity or offsets to the current error.

Sources: [NVIDIA model](https://huggingface.co/nvidia/transolver_drivaerml),
[pinned NVIDIA wrapper](https://github.com/NVIDIA/physicsnemo-cfd/blob/0612ec4ed54484a47bfa134eda7b3b012a607624/physicsnemo/cfd/evaluation/models/wrappers/transolver/wrapper.py),
[OpenFOAM kinematic pressure](https://doc.openfoam.com/2312/tools/processing/solvers/algorithm-kinematic-pressure/),
[OpenFOAM shear field](https://api.openfoam.com/2212/wallShearStress_8H.html).
