# Aero Transolver checkpoint-conventions audit

Date: 2026-09-24

## Decision

**CHECKPOINT_TRAINING_PREPROCESSING_NOT_ESTABLISHED.** Retain this model as **RESEARCH_ONLY**. The existing inference executed, but its accuracy cannot yet be attributed cleanly to model generalization versus a training/inference convention mismatch. No further inference, parameter sweep, retraining, CFD, gate change, or public release was performed in this audit.

The current Aero preprocessing follows the pinned modern PhysicsNeMo surface datapipe and coordinate configuration. That is not proof that this exact checkpoint was trained with those conventions. No input or output was tuned against the retained reference error.

## Evidence identity

- Checkpoint: NVIDIA `transolver_drivaerml`, surface `Transolver.0.501.mdlus`.
- Hugging Face revision: `96477aeb86d24c26ccf0797bca1b3851268017d0`.
- Checkpoint SHA-256: `eb98f399a050a8f8a24919335c61642e4a835bd4044f7e21abec231aa31fd82c`.
- Checkpoint creator metadata: PhysicsNeMo `1.3.0`; actual retained inference: PhysicsNeMo `2.2.0`.
- Modern source commit: `a078229716ce39d9d9273b23d54b073d3adb925e`.
- Public v1.3.0 tag: `14e0874847ffb56b35abf7708a1665e71605999c`. This tag is a comparison source, **not an established training commit**.
- Prior execution contract SHA-256: `620799e83fc6b04c0402441f57af3f94c93caaa5c32d12835ef1a5a580ce9720`.
- Prior package: `../transolver_reference_20260924`, manifest `e178fae452f72dadf5a0c1b4d9468cfbceb7dd4fb959f19217e7a0f963150f09`.

## Source-supported comparison

| Convention | Public v1.3 example | Modern source / retained Aero execution | Checkpoint-specific conclusion |
|---|---|---|---|
| Architecture | Training YAML: 8 layers, MLP ratio 4, 128 slices, TransformerEngine enabled | Checkpoint: 20 layers, MLP ratio 2, 512 slices, TransformerEngine disabled; Aero loads those saved arguments | Saved arguments establish architecture; generic example is not the exact recipe |
| Card architecture | Model card describes 8 layers | Checkpoint contains 20; modern CFD wrapper defaults to 20, while modern generic YAML still says 8 | Documentation discrepancy; no averaging or guesswork |
| Training source | Creator metadata says 1.3.0 | Checkpoint has `plus:false`; public v1.3 constructor lacks that argument | Version label alone does not identify exact training code |
| Translation | Training preprocessing uses area-weighted STL triangle centers | Modern datapipe uses arithmetic mean of STL triangle centers; Aero supplies full STL centers | Material convention difference; training linkage unresolved |
| Coordinate scaling | Legacy preprocessing subtracts origin without anisotropic scaling | Modern example and Aero divide by `[12, 4.5, 3.25]` | Modern agreement established; checkpoint training convention unresolved |
| Legacy inference origin | VTP inference uses area-weighted VTP cell centers | Legacy training uses STL centers | Even the legacy example is not a self-consistent exact reproduction recipe |
| Sampling | Legacy training default 300,000, random sampling | Modern example default 200,000; Aero uses frozen 200,000 native IDs in one context | Aero does not reproduce exact training or full-mesh inference context |
| Fluid features | Density and velocity | Same feature concepts; Aero uses 1.205 kg/m³ and 38.889 m/s | Velocity matches retained pressure/Cp relation, but checkpoint feature convention remains unresolved |
| Published inference defaults | 1.205 kg/m³ and 30 m/s | Modern CFD wrapper also defaults to 30 m/s, with 2,048-point blocks | A default is not evidence to replace the actual reference speed; block/context parity not claimed |
| Output scaling | Mean/std reversal and multiplication by density times velocity squared | Aero uses the checkpoint's `global_stats.json`, then density times velocity squared | Inference convention supported; exact native-to-training target conversion not established |
| Split | Card describes 436 training files and 48 test samples | Published tree/config do not identify run 1's membership | Held-out status NOT_ESTABLISHED |

Sources: [checkpoint model card](https://huggingface.co/nvidia/transolver_drivaerml/blob/96477aeb86d24c26ccf0797bca1b3851268017d0/README.md), [legacy training configuration](https://github.com/NVIDIA/physicsnemo/blob/14e0874847ffb56b35abf7708a1665e71605999c/examples/cfd/external_aerodynamics/transolver/conf/train_surface.yaml), [legacy preprocessing](https://github.com/NVIDIA/physicsnemo/blob/14e0874847ffb56b35abf7708a1665e71605999c/examples/cfd/external_aerodynamics/transolver/preprocess.py), [legacy VTP inference](https://github.com/NVIDIA/physicsnemo/blob/14e0874847ffb56b35abf7708a1665e71605999c/examples/cfd/external_aerodynamics/transolver/inference_on_vtp.py), [legacy model constructor](https://github.com/NVIDIA/physicsnemo/blob/14e0874847ffb56b35abf7708a1665e71605999c/physicsnemo/models/transolver/transolver.py), [modern datapipe](https://github.com/NVIDIA/physicsnemo/blob/a078229716ce39d9d9273b23d54b073d3adb925e/physicsnemo/datapipes/cae/transolver_datapipe.py), [modern coordinate configuration](https://github.com/NVIDIA/physicsnemo/blob/a078229716ce39d9d9273b23d54b073d3adb925e/examples/cfd/external_aerodynamics/transformer_models/src/conf/data/core.yaml). The [pinned modern CFD wrapper](https://github.com/NVIDIA/physicsnemo-cfd/blob/0612ec4ed54484a47bfa134eda7b3b012a607624/physicsnemo/cfd/evaluation/models/wrappers/transolver/wrapper.py) is retained in the local audit.

## Dimensional accounting: retain the correction, do not fit the result

The earlier dimensional audit remains unchanged. Native pressure and Cp satisfy `Cp = 2*p_native/U²` with relative L2 discrepancy `3.5757e-8` at the frozen velocity. This supports treating native pressure as kinematic and converting the reference with the fixed density. It does not establish the training target pipeline.

The retained pressure relative L2 discrepancy after that dimensional conversion is **0.5620**. The shear discrepancy is **0.8277**, conditional on standard incompressible OpenFOAM wall-shear units; explicit native shear dimensional metadata remains missing. Neither has a predeclared acceptance threshold. Raw mixed-unit comparisons are not physical accuracy scores.

No pressure offset, sign, density, velocity, coordinate transform, normalization factor, or sampling context was fitted in this audit. No reported discrepancy was recomputed to improve it. Sample-only inference cannot establish integrated force or conservation validity.

## What this establishes—and what it does not

Established: checkpoint identity; saved architecture; strict state loading in the retained execution; modern source formula correspondence; a real difference between legacy and modern conventions; retained evidence custody.

Not established: exact training commit and resolved configuration; native-to-training field units; exact geometry normalization used for these weights; training point-context distribution; held-out membership of run 1; equivalence between creator/runtime versions; cause of the observed error; repeatability; engineering validation.

The card's optimizer/epoch description also differs from the generic legacy YAML. This reinforces that an example configuration is not a checkpoint training record. We do not infer which source generated the published normalization statistics merely because a normalization script exists.

## Tests and custody

`audit.py` runs deterministic static-source/metadata checks, records relevant source hashes and line references, re-verifies every prior manifest entry, and hashes this audit package. These are audit consistency checks—not neural accuracy tests. `AUDIT_CHECKS.json` and `FINAL_VERIFICATION.json` hold the actual counts. The manifest covers authored files and downloaded/copied sources; the manifest and final verification envelope are explicitly excluded from self-hashing. The verification envelope records the manifest hash.

Original execution evidence, model, runtime, and qualification states are unchanged. This is a public derivative of the immutable local audit, released with the Transolver addendum. It is not a private-runtime promotion.

## One next action

Obtain the checkpoint-specific training/inference recipe from NVIDIA, using the narrowly scoped public checkpoint-recipe inquiry. Submission status is recorded separately in `INQUIRY_STATUS.json`; the original local audit remains unchanged. Once a verified recipe is available, freeze a new reference-reproduction contract before another inference. Do not run a convention sweep and choose the lowest error as a substitute for provenance.
