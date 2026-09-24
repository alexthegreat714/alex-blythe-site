---
title: "Aero source releases: Rev 2.0 through 2.3"
summary: "Public source downloads: Routing Lab, Engineering Validity Gate and Rev 2.3's controlled Physics-AI reference adapter—with measured results and explicit limitations."
date: 2026-09-24
author: Alex Blythe
tags: [Aero, Software, Engineering, Provenance]
readingTime: 4 min
draft: false
relatedSoftware: [Aero]
type: Technical note
---

The previously private revision modules are now available as public downloads.
This publishes source and documentation—not access to the running private service,
private engineering corpus, conversations, machine credentials or employer data.

## Download a revision

| Revision | What it contains | Download |
| --- | --- | --- |
| 2.0 | Historical deployment-profile and boundary reference. **Partial snapshot, not a complete installable application.** | [Rev 2.0 baseline record](/demos/aero/source-revisions-2026-09-24/aero-rev-2.0.zip) |
| 2.1 | AnyJev Routing Lab source, generic examples, frozen routing contract, page and tests. Alternatives, scores, chosen route and observable selection reasons are auditable. | [Rev 2.1 module](/demos/aero/source-revisions-2026-09-24/aero-rev-2.1.zip) |
| 2.2 | Cumulative Routing Lab and Engineering Validity Gate modules, deterministic checks, engineering contracts, hypotheses, approval controls and synthetic regression tests. | [Rev 2.2 cumulative source](/demos/aero/source-revisions-2026-09-24/aero-rev-2.2.zip) |
| 2.3 | Cumulative modules plus controlled Physics-AI witnesses, isolated DoMINO reference adapter, provenance, applicability checks and tests. **Research-only model; not validated engineering inference.** | [Rev 2.3 cumulative source](/demos/aero/source-rev-2-3-2026-09-24/aero-rev-2.3.zip) |

**Latest source: [Rev 2.3 workflow addendum](/demos/aero/physics-ai-workflow-addendum-2026-09-24/aero-rev-2.3-workflow-addendum.zip)**
(cumulative; preserves the original Rev 2.3 archive). These are source module
packages, not complete one-click installations of the private Aero application.
The application shell, personal integrations, solver installations and model
weights are excluded. Public availability is not evidence of engineering qualification.

## Pull and verify

**Rev 2.3:** [Release and archive hash](/demos/aero/source-rev-2-3-2026-09-24/release.json) ·
[SHA-256 manifest](/demos/aero/source-rev-2-3-2026-09-24/SHA256_MANIFEST.json) ·
[Verification](/demos/aero/source-rev-2-3-2026-09-24/VERIFICATION.json) ·
[Implementation report](/demos/aero/source-rev-2-3-2026-09-24/IMPLEMENTATION_REPORT.md) ·
[Reference results](/demos/aero/source-rev-2-3-2026-09-24/REFERENCE_REPORT.json).

Historical Rev 2.0–2.2 archives and their original manifests remain unchanged:

[Release index and archive hashes](/demos/aero/source-revisions-2026-09-24/releases.json) ·
[SHA-256 manifest](/demos/aero/source-revisions-2026-09-24/SHA256_MANIFEST.json) ·
[Verification record](/demos/aero/source-revisions-2026-09-24/VERIFICATION.json) ·
[README](/demos/aero/source-revisions-2026-09-24/README.md)

Download the desired ZIP without a login, verify its SHA-256, and extract into a
new directory. Each archive includes an interior source manifest with original
and published file hashes. Personal edge URLs are replaced with an example
origin; text line endings are normalized. Runtime source is left unchanged.

In an isolated Python 3.12 environment:

```text
python -m pip install -r requirements-test.txt
python -m pytest Aero/tests -q
```

Rev 2.0 contains no test suite. Rev 2.1–2.3 software tests use controlled synthetic
evidence and model/solver test doubles. Model inference requires its separately
configured environment and checkpoint. Conventional CFD/FEA execution requires
its existing worker integration. Do not mistake passing software tests for
validation of a physical model or a real engineering result.

Release verification: **16 extracted-archive tests passed for Rev 2.1; 54 for
Rev 2.2; seven publication/custody checks passed.** The initial attempt used a
Python environment without Flask and failed collection; the successful runs used
the existing Aero Python environment. [Test record](/demos/aero/source-revisions-2026-09-24/TEST_RECORD.json).

## What changed, and why

**Rev 2.0** separated the personal local Aero agent from the corpus-free portable
deployment. The original historical snapshot was scoped, not a full runtime backup.

**Rev 2.1** made model-selected workflow choices inspectable. It retains what the
choices were, the model's scores, the selected route and the observable decision
rule. It does not claim to expose hidden model reasoning. Its small-model pilot
does not authorize autonomous physical changes or engineering acceptance.

**Rev 2.2** added an engineering investigator's control loop. A frozen contract and
pre-run analytical baseline challenge numerical results; numerical and physical
validity stay separate. Discrepancies produce competing hypotheses and bounded
experiments. Physical changes still require approval. Missing evidence cannot
be inferred into existence, and earlier failed qualifications remain failed.

**Rev 2.3** adds an optional supporting-witness capability: neural physics models
with applicability checks, checkpoint provenance, isolated execution and explicit
limits on authority. A surrogate cannot grade its own work, replace a required
solver run or turn agreement into validation. The existing private application
remains **Rev 2.2-local**; this publication does not expose or restart it.

## Rev 2.3: what actually ran

The pinned DoMINO automotive surface checkpoint ran on a 753,234-cell DrivAerML
reference geometry through PhysicsNeMo in an isolated Linux/CUDA worker on an RTX
3090. The adapter invocation took **119.478 seconds**, including setup; this is a
single reference execution, not a hardware benchmark. Inputs and runtime remain
on the approved D: storage, outside Aero's main Python environment.

| Reference coefficient | Prediction | Reference | Relative discrepancy |
| --- | ---: | ---: | ---: |
| Drag Cd | 0.306863 | 0.303512 | 1.10% |
| Side Cs | 0.035471 | 0.047668 | 25.59% |
| Lift Cl | 0.433089 | 0.067728 | 539.45% |

Pressure, shear and force exactly reproduced the first reference execution.
Sensitivity gradients did not: maximum absolute difference was 0.0007534 in the
upstream sensitivity units. No strict-determinism claim is made.

Independent force integration agreed within 0.0000842 N. A constant pressure-offset
check did not explain the lift discrepancy. Two upstream preprocessing paths use
different COM-offset scaling; that is an unresolved compatibility hypothesis,
not a proven cause. Native CFD/STL field correspondence is not established.

The correct outcome is **REFERENCE_INFERENCE_COMPLETED_NOT_VALIDATED**.
Applicability remains **NOT_ESTABLISHED**, authority **RESEARCH_ONLY**, and
shared OpenFOAM training lineage means **LOW** independence from OpenFOAM.
No neural result can satisfy a required engineering qualification gate.

The software tests and actual model execution are separate evidence. See the
[Rev 2.3 test record](/demos/aero/source-rev-2-3-2026-09-24/TEST_RECORD.json).
Transolver remains a stub; PDEBench/RealPDEBench execution, PFEM warm starts,
autonomous surrogate screening and training are not implemented. This is a
bounded source release, not a claim that every planned Physics-AI feature is done.

## Version boundaries

### September 24 workflow addendum

The development follow-up adds identity-aligned field benchmarking, review-only
candidate ranking and an optional-experiment hook in the existing campaign loop.
A frozen contract can allow a traceable, applicable surrogate witness to defer a
specifically optional numerical experiment. It cannot eliminate a physical
hypothesis, waive a required solver run or override an engineering gate.

**113 local tests and 110 extracted-package tests pass.** These test software
contracts, not neural accuracy or demonstrated CFD savings. The new harness also
scores retained DoMINO coefficients descriptively, with no post-hoc acceptance
limits. Native-field correspondence and model validation remain unestablished.

[Implementation and limitations](/demos/aero/physics-ai-workflow-addendum-2026-09-24/IMPLEMENTATION_REPORT.md) ·
[Test evidence](/demos/aero/physics-ai-workflow-addendum-2026-09-24/TEST_RECORD.json) ·
[Retained-model comparison](/demos/aero/physics-ai-workflow-addendum-2026-09-24/RETAINED_MODEL_EVALUATION.json) ·
[Archive identity](/demos/aero/physics-ai-workflow-addendum-2026-09-24/release.json) ·
[SHA-256 manifest](/demos/aero/physics-ai-workflow-addendum-2026-09-24/SHA256_MANIFEST.json) ·
[Verification](/demos/aero/physics-ai-workflow-addendum-2026-09-24/VERIFICATION.json).

**The original multi-model milestone is not fully complete.** Transolver remains
blocked pending approved weights, matching reference data and verified usage terms.
PDEBench/RealPDEBench dataset reproduction and PFEM execution are still future work.
No private service was restarted, no additional model downloaded and no CFD run
launched. This addendum does not silently promote the private application or
rewrite any historical release.

These are Aero **source revisions**, not the public presentation's revision
numbers, the V2/V2.1 convergence contracts, or the benchmark report's release
number. The running private application retains authentication and its existing
release until a new runtime revision is deliberately tested and deployed.

Aero is a personal project. Public release grants no employer-data ingestion
authority or employer endorsement. Upstream models and frameworks retain their
own licenses; no model weights are redistributed here.
