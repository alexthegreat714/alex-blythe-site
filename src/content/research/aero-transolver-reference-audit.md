---
title: "Aero Physics-AI: a successful Transolver run is not validation"
summary: "A real pretrained inference, a dimensional check, and a checkpoint-provenance audit. What executed, what disagreed, and why Aero keeps the result research-only."
date: 2026-09-24
author: Alex Blythe
tags: [Aero, Physics-AI, CFD, Provenance]
readingTime: 6 min
draft: false
relatedSoftware: [Aero]
type: Technical note
---

**September 24, 2026 · Rev 2.3 Transolver addendum**

The NVIDIA Transolver adapter now runs a real pretrained automotive reference
case. That closes an execution gap, not an engineering-validation gap. The
prediction disagrees substantially with the retained reference, and the exact
checkpoint training/preprocessing recipe remains unestablished.

**Disposition: RESEARCH_ONLY. No engineering gate was relaxed.**

[Download cumulative source](/demos/aero/transolver-addendum-2026-09-24/aero-rev-2.3-transolver-addendum.zip) ·
[All Aero source revisions](/software/notes/aero-source-revisions/) ·
[Full conventions audit](/demos/aero/transolver-addendum-2026-09-24/CONVENTIONS_AUDIT_REPORT.md)

## Why we did this

Aero's Physics-AI layer treats a neural model as another witness, not as the
judge. The Engineering Validity Gate must distinguish a model that loads, a
model that applies to the problem, and a model independently validated for that
problem. These are different achievements.

The earlier DoMINO demonstration already showed why this matters: a close drag
coefficient did not erase large side-force and lift discrepancies. Transolver
adds a second executable adapter, not a second vote that makes CFD correct.
Both models' OpenFOAM training lineage limits their independence from OpenFOAM.

## What actually ran

The pinned NVIDIA **original Transolver** surface checkpoint—not THUML
Transolver++ or Transolver-3—ran through the existing isolated PhysicsNeMo worker.
The case was DrivAerML run 1, with **200,000 native boundary cells** sampled from
8,828,095 polygons using a frozen seed and preserved cell IDs. Reference output
fields were not supplied to the neural model.

| Measurement | Retained result | Interpretation |
| --- | ---: | --- |
| Model parameters | 9,763,236 | Saved architecture, strictly loaded |
| Selected native cells | 200,000 | Exact sample correspondence, not full-mesh inference |
| Forward/inference phase | 2.404 s | One execution, includes output unscaling |
| Complete adapter invocation | 73.958 s | Includes preparation/startup; not a repeated benchmark |
| Peak PyTorch allocated GPU memory | 10.727 GB | Decimal GB; not total GPU consumption or minimum VRAM |
| Extracted cumulative-source tests | 125 passed | Software tests, not physical validation |
| Audit source/metadata checks | 10 passed | Provenance consistency checks, not accuracy tests |

Environment: RTX 3090, PhysicsNeMo 2.2.0, PyTorch 2.10.0+cu130. Execution used a
network-disabled, bounded worker with read-only inputs. No conventional CFD,
training, production-service restart, or heat-exchanger calibration was performed.
Repeatability of this Transolver run has **not** been measured.

## Compare like units before discussing accuracy

The native pressure/Cp relationship supports a kinematic-pressure interpretation.
Comparing the model's pascals directly against that raw field would mix units.
The retained dimensional audit converts the reference using the already-declared
density; it does not alter the prediction or fit a pressure offset.

| Quantity | Relative L2 discrepancy | Qualification |
| --- | ---: | --- |
| Pressure | 56.2% | Reference conversion supported by retained Cp identity |
| Wall shear | 82.8% | Conditional on standard incompressible OpenFOAM shear units; explicit native dimensional metadata missing |

These are **descriptive discrepancies**, not scores against invented acceptance
limits. They do not establish the cause of the disagreement. Neither full-surface
force validity nor conservation can be established from this sample-only run.

[Measured results and dimensional limitations](/demos/aero/transolver-addendum-2026-09-24/REFERENCE_AND_AUDIT_RESULTS.json)

## The provenance audit found a real documentation gap

The next step was source inspection, not trying input variants until an error
looked smaller. The audit found:

1. **Architecture disagreement:** the model card describes eight layers; the
   checkpoint stores twenty. The adapter uses the saved checkpoint arguments.
2. **Version ambiguity:** checkpoint metadata says PhysicsNeMo 1.3.0, but its
   `plus:false` argument is absent from the public v1.3.0 constructor. That
   version label alone does not identify the training commit.
3. **Changed geometry preprocessing:** legacy training uses an area-weighted STL
   origin without the newer anisotropic scaling. The modern datapipe uses an
   arithmetic STL-center mean, with scaling enabled by the example configuration.
4. **Unresolved checkpoint linkage:** the current Aero path follows the pinned
   modern formulas, but the inspected release does not establish which exact
   training recipe or split produced these weights. Run 1's held-out status is unknown.

Sources: [NVIDIA checkpoint/card](https://huggingface.co/nvidia/transolver_drivaerml/tree/96477aeb86d24c26ccf0797bca1b3851268017d0),
[legacy preprocessing](https://github.com/NVIDIA/physicsnemo/blob/14e0874847ffb56b35abf7708a1665e71605999c/examples/cfd/external_aerodynamics/transolver/preprocess.py),
[modern datapipe](https://github.com/NVIDIA/physicsnemo/blob/a078229716ce39d9d9273b23d54b073d3adb925e/physicsnemo/datapipes/cae/transolver_datapipe.py).

These differences are **compatibility hypotheses**, not proof of a defective
checkpoint or the cause of the error. Strict weight loading is not cross-version
numerical equivalence. A wrapper's 30 m/s default is not a reason to replace the
frozen reference's approximately 38.889 m/s input merely to improve agreement.

### New primary-source check: run 1 is in a later benchmark list

The checkpoint's public training recipe remains **NOT_ESTABLISHED**, but a
separate NVIDIA DrivAerML benchmark split now provides one artifact-level fact.
At [physicsnemo-cfd commit 0612ec4](https://github.com/NVIDIA/physicsnemo-cfd/tree/0612ec4ed54484a47bfa134eda7b3b012a607624/workflows/benchmarking/drivaer_ml_files),
the README proposes a 90/10 split over 484 usable cases. Its [train.csv](https://github.com/NVIDIA/physicsnemo-cfd/blob/0612ec4ed54484a47bfa134eda7b3b012a607624/workflows/benchmarking/drivaer_ml_files/train.csv)
lists 436 runs and contains `1,510.20091805275615`; its [validation.csv](https://github.com/NVIDIA/physicsnemo-cfd/blob/0612ec4ed54484a47bfa134eda7b3b012a607624/workflows/benchmarking/drivaer_ml_files/validation.csv)
lists 48 runs and excludes run 1.

That does **not** identify the split used to train these weights. Git history
dates the checkpoint upload to April 29, 2026 and the model card to April 30;
the benchmark split files first appear in a May 6 commit. The matching 436/48
counts cannot establish checkpoint linkage. The card itself gives no run IDs.
Therefore run 1's training or held-out status for this checkpoint remains
**NOT_ESTABLISHED**.

The checkpoint revision is the full 40-character
`96477aeb86d24c26ccf0797bca1b3851268017d0`. Earlier retained URL text omitted
the `f` after `cc` and Hugging Face rejects that 39-character text. The full
revision's published LFS digest matches the retained checkpoint; earlier frozen
receipts and packages were left unchanged.

A bounded range check of the companion `checkpoint.0.501.pt` inspected its ZIP
index and serialized opcode metadata without downloading the full file or
deserializing the pickle. The inspected stream exposes optimizer/scheduler
state and an epoch field, but no source commit or run-list identifiers.

The maintainer reply in [discussion #1157](https://github.com/NVIDIA/physicsnemo/discussions/1157)
points to [arXiv:2507.10747v1](https://arxiv.org/html/2507.10747v1), whose
evaluation lists DoMINO, X-MeshGraphNet and FIGConvNet. That paper provides
benchmark context, not direct evidence of this Transolver checkpoint's recipe.

[Download the bounded findings report](/demos/aero/transolver-website-followup-2026-09-24/FINDINGS_UPDATE.md) ·
[Evidence matrix](/demos/aero/transolver-website-followup-2026-09-24/EVIDENCE_MATRIX.json) ·
[Source index and hashes](/demos/aero/transolver-website-followup-2026-09-24/SOURCE_INDEX.json) ·
[Custody summary](/demos/aero/transolver-website-followup-2026-09-24/CUSTODY_SUMMARY.json)

## What is released

This is an additive, cumulative **Rev 2.3 source-module package**. It includes
the Transolver adapter, isolated worker, registry/service integration, tests and
implementation guide on top of the previous workflow addendum. The existing
release ZIPs remain byte-for-byte unchanged.

No model weights, licensed geometry, raw reference fields, private corpus,
credentials, conversations or employer information are redistributed. This is
not a complete one-click private Aero installation or a promotion of the live
private service. Upstream terms still govern separately obtained models/data.

[Implementation guide](/demos/aero/transolver-addendum-2026-09-24/IMPLEMENTATION_REPORT.md) ·
[Release and archive hash](/demos/aero/transolver-addendum-2026-09-24/release.json) ·
[Test record](/demos/aero/transolver-addendum-2026-09-24/TEST_RECORD.json) ·
[SHA-256 manifest](/demos/aero/transolver-addendum-2026-09-24/SHA256_MANIFEST.json) ·
[Verification](/demos/aero/transolver-addendum-2026-09-24/VERIFICATION.json) ·
[Earlier-evidence custody](/demos/aero/transolver-addendum-2026-09-24/SOURCE_CUSTODY.json)

The local audit rechecked **91 retained execution artifacts and 36 audit
artifacts**, with zero missing or mismatched entries. The public derivative has
its own manifest. Software tests and custody checks establish reproducibility
boundaries, not engineering truth.

## On-site follow-up: recover the recipe, not tune the answer

**Website publication only. No GitHub issue or external inquiry will be submitted.**
The report, results, source download and open research questions are published
here. No GitHub sign-in or outside submission is required. Earlier downloadable
inquiry records are historical snapshots; the owner's website-only direction
supersedes those submission instructions without changing the frozen evidence.

The checkpoint-recipe questions are now Aero's on-site research checklist:

1. **Exact training identity:** establish the training source commit, resolved
   model/data/training configuration, and compatible inference runtime.
2. **Architecture:** resolve the saved twenty-layer model versus the card's
   eight-layer description.
3. **Geometry preprocessing:** establish the origin formula and whether
   `[12, 4.5, 3.25]` coordinate scaling was used for these weights.
4. **Physical units and operating inputs:** establish native-to-training pressure
   and wall-shear conversion, sign conventions, pressure reference, density,
   and the meaning of the velocity input.
5. **Normalization:** establish the generation recipe for `global_stats.json`,
   ideally with checksum-linked reference inputs and expected outputs.
6. **Inference context:** establish normal orientation, point-context size,
   sampling/chunking, precision and deterministic-execution settings.
7. **Dataset split:** establish exact training/validation/test run IDs and
   whether native run 1 is held out.

[Download the research checklist](/demos/aero/transolver-website-followup-2026-09-24/CHECKPOINT_RECIPE_CHECKLIST.md) ·
[Current website-only status](/demos/aero/transolver-website-followup-2026-09-24/CURRENT_STATUS.json)

Once the recipe is independently established, freeze a new reproduction contract
before another inference. Until then: keep the anomalous prediction, preserve
uncertainty, and do not let a neural result satisfy a required engineering gate.

**Aero should become harder to fool, not easier to impress.**
