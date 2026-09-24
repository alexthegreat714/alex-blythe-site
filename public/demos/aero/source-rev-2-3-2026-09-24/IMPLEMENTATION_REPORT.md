# Aero Rev 2.3 — controlled Physics-AI reference adapter

September 24, 2026. Source-module release, **not a promotion of the live private
application**. The model remains **RESEARCH_ONLY / NOT_ESTABLISHED** for engineering
validation. Successful inference is not a qualification decision.

## Discovery, reuse and implementation

Reuse the Engineering Contract digest, analytical baseline, eight-domain validity
gate, CampaignController, event chain, solver adapters and approval policy. No
parallel scheduler, simulation framework, approval service or training pipeline.

The optional `Aero.physics_ai` package provides a registry, conservative metadata
applicability, checkpoint inspection, retained prediction records, pairwise
discrepancy analysis and supporting-gate annotations. CampaignController's
`attach_physics_ai` verifies witness custody without changing campaign state,
proposals, hypotheses or solver authorization. Reads recheck artifact hashes.

Flow: contract → applicability/capability → explicit isolated reference adapter →
retained PHYSICS_AI_RESULT → supporting evidence → existing engineering review.
Agreement never votes, averages or overrides required engineering gates.

## Components

| Component | Status and boundary |
| --- | --- |
| Registry, applicability, checkpoint custody | IMPLEMENTED_AND_TESTED; metadata envelope, not learned OOD |
| Provenance, balance check, comparison, gate attachment | IMPLEMENTED_AND_TESTED; synthetic regressions plus actual reference witness ingestion |
| PhysicsNeMo isolated execution | IMPLEMENTED_AND_TESTED for the pinned Linux/RTX 3090 reference environment only |
| DoMINO adapter | IMPLEMENTED_NOT_FULLY_VALIDATED; pinned DrivAerML run 1 only |
| Actual pretrained reference inference | Executed twice; 753,234 surface cells; finite outputs |
| Transolver | ADAPTER_STUB_ONLY; checkpoint/license/preprocessing selection unresolved |
| PDEBench / RealPDEBench | INVESTIGATED; benchmark execution NOT_IMPLEMENTED |
| PFEM / FEM warm start | INVESTIGATED; execution NOT_IMPLEMENTED |
| Arbitrary-geometry inference, autonomous screening | NOT_IMPLEMENTED |
| Learned OOD, calibrated uncertainty | NOT_ESTABLISHED |
| Native CFD-to-STL field correspondence | NOT_ESTABLISHED; different topology |
| Autonomous hypothesis elimination / saved CFD runs | NOT_IMPLEMENTED; no claimed savings |
| Training | NOT_IMPLEMENTED; not authorized |

## Added and modified code

Added: `physics_ai/domino.py`, `domino_worker.py`, `reference_evidence.py`,
`tests/test_domino_adapter.py`. Existing foundation files remain part of the release:
registry, catalog, evidence, comparison, integration, service, dataset schema and
software tests. Extended service/CLI for explicit reference execution; updated
catalog with verified OpenFOAM training lineage and honest reference status.
Existing Engineering Validity Gate decisions and mutation approvals are unchanged.

## Runtime and dependency isolation

The main Python process imports no Torch, CUDA, PhysicsNeMo or PyVista. Missing
dependencies return structured results. The worker uses an existing Docker image
and a separately provisioned read-only virtual-environment volume. No automatic
pull, package install, checkpoint download or shared-service restart.

Tested: Python 3.11.16, PhysicsNeMo 2.2.0, Torch 2.10.0+cu130, CUDA 13.0,
PyVista 0.47.0, RTX 3090. Worker cap: 2.5 GiB host RAM, no swap, four CPUs,
1,800-second internal deadline / 1,860-second supervisor timeout. PyTorch peak
allocation was 3,127,602,176 bytes; this is not total GPU memory or a minimum VRAM
specification. Dependencies/runtime/caches and research evidence reside on the
operator-approved D: storage. The conventional Aero environment is unchanged.

Container network is disabled, root filesystem is read-only, capabilities are
dropped, no-new-privileges is set, inputs/venv are read-only and each output
directory is unique. Timeout stops only the new worker. Failed logs and containers
are retained. Container isolation is not a guarantee that arbitrary checkpoints
are safe: the worker configuration and pinned upstream sources are trusted local
operator inputs, never an unauthenticated upload API.

## Using the optional adapter

`python -m Aero.physics_ai list` is read-only and does not load a neural package.

After an operator has independently accepted applicable licenses and provisioned
the pinned bundle/runtime, use:

```text
python -m Aero.physics_ai reference --worker-config worker.json --acknowledge-research --evidence-root D:/AeroRuntime/physics_ai
```

`worker.json` is local-only configuration containing `bundle`, `output_root`,
`docker`, `runtime_volume`, `image`, `workflow_commit`, `download_plan_sha256` and
`contract_sha256`. Image and workflow identities are pinned in `domino.py`.
`bundle` must contain the previously verified DOWNLOAD_PLAN.json, reference
execution contract, successful install/smoke receipts, checkpoints, upstream code
and DrivAerML run-1 assets. The adapter verifies required artifacts before launch
and inside the worker. It rejects other geometry identities, unsupported outputs,
changed inputs and missing research acknowledgement. It never silently uses this
automotive model on a heat exchanger.

The optional evidence root must contain both bundle and outputs. Reference
ingestion uses existing build/verify/retain APIs. Its contract is explicitly a
reference-execution contract, not a fabricated engineering acceptance contract.
Actual campaign attachment still requires the real campaign's contract/controller.

Checkpoint and runtime preparation are deliberately manual/approval-controlled;
this archive is not a one-click 5 GB downloader. No weights or licensed reference
geometry are redistributed. Runtime identity and package lock are separate from
Aero's dependency-light software-test requirements.

## Reference results and discrepancy audit

Original upstream reference worker: **127.353 s**. Integrated adapter worker:
**119.478 s**. These are single wall-time observations including setup, not a
performance benchmark or demonstrated speedup.

| Coefficient | Prediction | Published reference | Relative discrepancy |
| --- | ---: | ---: | ---: |
| Drag Cd | 0.306863 | 0.303512 | 1.10% |
| Side Cs | 0.035471 | 0.047668 | 25.59% |
| Lift Cl | 0.433089 | 0.067728 | 539.45% |

Pressure, wall shear, coordinates and integrated force are exactly equal between
the two executions. Geometry sensitivity is **not** bitwise equal: maximum
absolute difference 0.0007534027099609375 in upstream sensitivity units. Strict
deterministic algorithms were not enabled; no universal reproducibility claim.

Independent float64 pressure/shear integration reproduces the force within
0.0000842 N. The STL's net area vector is near zero; removing the mean pressure
would change lift only about 0.00000349 N, not explain the discrepancy. Changing
between the two published reference-area conventions does not remove it.

The pinned design-sensitivities workflow and PhysicsNeMo v2.2 datapipe differ in
COM-offset preprocessing. This is a **compatibility hypothesis**, not a proven
bug or license to tune until the reference matches. Checkpoint config uses
min-max scaling and disables parameter encoding. No fitted offset, sign flip,
normalization correction or threshold was applied. Native CFD reference has
8,828,095 polygons; it cannot be compared elementwise to the 753,234-cell STL.
Field error and held-out validation remain NOT_ESTABLISHED.

## Authority, evidence independence and human judgment

Missing applicability metadata remains NOT_ESTABLISHED, even within the named
automotive family. A known geometry mismatch is OUT_OF_DISTRIBUTION. Both remain
RESEARCH_ONLY. OpenFOAM-trained surrogate evidence against OpenFOAM has LOW
independence, not two independent validations. Uncertainty is not invented.

Humans must approve model access/licenses and any physical model/requirement
changes. Engineering interpretation, training-path compatibility, native-field
mapping, benchmark fidelity and any domain validation remain unresolved work.
No HX case, CFD/FEA run, acceptance criterion or historical disposition changed.

## Verification

Run the dependency-light suite in an isolated Python 3.12 environment:

```text
python -m pytest Aero/tests/test_domino_adapter.py Aero/tests/test_physics_ai.py Aero/tests/test_engineering_validity.py Aero/tests/test_private_routing_lab.py -q
```

Boundary tests exercise missing dependencies, wrong reference identity, required
acknowledgement, hash mismatch, network/memory isolation arguments, failure
retention, timeout handling and incomplete-result rejection. These are test
doubles; the actual pretrained invocation has a separate execution/audit receipt.
Exact final suite counts appear in the release TEST_RECORD.json.

## Pinned upstream sources

- [DoMINO model card](https://huggingface.co/nvidia/domino_drivaerml/tree/35b1bf1edafdaa2600d16182825890cd51c07427)
- [Design-sensitivities workflow](https://github.com/NVIDIA/physicsnemo-cfd/tree/0612ec4ed54484a47bfa134eda7b3b012a607624/workflows/domino_design_sensitivities)
- [PhysicsNeMo v2.2 datapipe](https://github.com/NVIDIA/physicsnemo/blob/a078229716ce39d9d9273b23d54b073d3adb925e/physicsnemo/datapipes/cae/domino_datapipe.py)
- [DrivAerML dataset and OpenFOAM provenance](https://huggingface.co/datasets/neashton/drivaerml/tree/5d448b209bf654503c64ce7261c34fa125f46392)

Recommended next scientific step: independently establish the checkpoint's exact
training/preprocessing contract and native-reference mapping before any claim of
engineering field accuracy. Rev 2.3 ships a controlled witness, not a CFD judge.
