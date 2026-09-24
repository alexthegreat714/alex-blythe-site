---
title: "Aero source releases: Rev 2.0, 2.1 and 2.2"
summary: "Public downloads of the reviewed baseline record, auditable Routing Lab and Engineering Validity Gate. Rev 2.3 Physics-AI is the next development branch."
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
| 2.3 | Controlled Physics-AI witnesses. **Development branch, not a completed pretrained-inference release.** | No stable release yet |

**For the latest published modules, download Rev 2.2.** These are source module
packages, not complete one-click installations of the private Aero application.
The application shell, personal integrations, solver installations and model
weights are excluded. Public availability is not evidence of engineering qualification.

## Pull and verify

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

Rev 2.0 contains no test suite. Rev 2.1 and 2.2 tests use controlled synthetic
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

**Rev 2.3** begins a separate supporting-witness capability: optional neural
physics models with applicability checks, checkpoint provenance and explicit
limits on authority. A surrogate will not grade its own work, replace a required
solver run or turn agreement into validation.

## Version boundaries

These are Aero **source revisions**, not the public presentation's revision
numbers, the V2/V2.1 convergence contracts, or the benchmark report's release
number. The running private application retains authentication and its existing
release until a new runtime revision is deliberately tested and deployed.

Aero is a personal project. Public release grants no employer-data ingestion
authority or employer endorsement. Upstream models and frameworks retain their
own licenses; no model weights are redistributed here.
