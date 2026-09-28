---
title: "Aero future work: local engineering pilot"
summary: "A reference roadmap for a teens-sized GX10 engineering pilot: Luna prepares traceable data and bounded implementations, a lead reasoning model designs and reviews, and deterministic gates retain authority."
date: 2026-09-28
author: Alex Blythe
tags: [Aero, Future work, Engineering agents, Fine-tuning]
readingTime: 8 min
draft: false
relatedSoftware: [Aero]
type: Architecture
---

**Future work · Planning reference v0.1 · September 28, 2026**

Status: **PROPOSED / NOT_IMPLEMENTED_AS_DESCRIBED**. This page freezes a reference
direction, not a trained-model release or an engineering qualification. Publishing
it does not launch training, simulations, autonomous campaigns, or deployment.
The proposed model's benefit remains **NOT_ESTABLISHED** until measured.

[Purpose](#the-goal-to-return-to) · [Work breakdown](#work-breakdown-and-ownership) ·
[First milestone](#first-bounded-milestone) · [Drift checklist](#return-here-if-the-project-drifts)

## The goal to return to

Develop a roughly **12–14B-parameter local engineering pilot on the GX10**, working
with a larger reasoning model to perform CFD, FEA, and related engineering tasks.
The size is a target band, not a selected checkpoint or verified training-memory
claim. Base-model choice, licensing, tool-use support, and hardware/runtime fit
must be established before training.

The local pilot should select tools, prepare structured requests, inspect supplied
evidence, track hypotheses, propose bounded experiments, and recognize when it
needs help. It must not replace conventional solvers, independently certify its
own results, or bypass Aero's existing engineering-validity and approval gates.

**Success means correct, authorized engineering decisions in useful time—not
merely more generated text, more simulations, or a model that sounds technical.**

## Two different divisions of responsibility

During development, **Luna is the preparation and implementation worker**, and
the **lead reasoning model is the designer and reviewer**. Luna is not the local
model being trained. At runtime, the trained local pilot would work with a larger
reasoning model through explicit escalation rules.

| Runtime component | Intended responsibility |
| --- | --- |
| Local teens-sized pilot | Routine tool selection, structured requests, evidence tracking, bounded next-action proposals, and escalation |
| Larger reasoning model | Difficult diagnosis, competing hypotheses, workflow design, and independent critique of consequential proposals |
| Deterministic engineering tools and gates | Physics calculations, CFD/FEA execution, evidence checks, numerical/physical validity, mutation authority, and acceptance prerequisites |
| RAG knowledge library | Traceable engineering references, applicability limits, and approved case context |
| Human engineer | Physical-problem changes, consequential approvals, and deployment authority |

An additional model opinion is not experimental validation. Escalation must carry
the evidence, uncertainties, source references, and proposed action—not just the
small model's preferred conclusion.

## Separate knowledge from decision training

Build two connected resources instead of turning every paper into fine-tuning text.

| Resource | Purpose | Example |
| --- | --- | --- |
| Engineering knowledge library: RAG | Retrieve equations, facts, assumptions, valid ranges, and citations | A heat-transfer correlation with its source page, units, geometry assumptions, and applicability range |
| Engineering decision dataset: fine-tuning | Teach evidence use, tool selection, controlled action, and escalation | Given a converged CFD run with missing energy closure, request the missing calculation instead of accepting the result |

Papers and articles can support both. Their conclusions remain bounded by their
assumptions. Source preparation must record provenance and permitted use; public
availability alone is not permission to redistribute or train on a document.
Do not import employer data into personal Aero or this public site.

Synthetic examples remain labeled **SYNTHETIC**. Mocked tool outputs remain
**MOCKED**, never observed solver results. Unknown facts, missing units, ambiguous
equations, and unsupported conclusions must be flagged rather than filled in.

## Work breakdown and ownership

| Part | Luna's bounded work | Lead model's responsibility | Exit artifact |
| --- | --- | --- | --- |
| A. Existing-work inventory | Catalog datasets, scripts, configurations, failures, and tool interfaces | Decide what to reuse, extend, or retire | Reuse map and gap list |
| B. Source preparation | Extract approved sources into evidence cards with page references, units, assumptions, and limitations | Approve sources; resolve ambiguous physics and conflicting claims | Traceable RAG evidence cards |
| C. Curriculum design | Organize proposed examples against a fixed taxonomy and report coverage gaps | Define skills, authority boundaries, expected behavior, and escalation rules | Frozen curriculum specification |
| D. Synthetic production | Generate bounded variations from approved templates and evidence cards | Design scenarios; approve labels and decision logic | Candidate training records |
| E. Tool-use sequences | Format actual or explicitly mocked requests/results into consistent sequences | Define tool choice, prerequisites, stop conditions, and next actions | Reviewed multi-step examples |
| F. Dataset quality control | Run schema, citation, duplicate, repetition, and coverage checks | Audit engineering correctness and approve the dataset freeze | Manifest, review decisions, and rejection log |
| G. Training preparation | Prepare approved configs, check paths/dependencies, collect logs, and summarize measured resource usage | Select base model, recipe, budget, and stop conditions | Reproducible training configuration |
| H. Evaluation | Execute frozen tests and collect complete outputs without changing answer keys | Interpret failures; compare against the untuned baseline; decide promotion | Held-out evaluation report |
| I. Integration | Implement bounded adapters, documentation, and tests against an approved specification | Design small/large-model handoff and preserve existing gates | Controlled pilot integration |

Luna can draft code and tests. A task belongs in that lane when it is clearly
specified and independently checkable—not merely because it is tedious.
Uncertain engineering interpretation goes back to the lead reviewer.

## The decision curriculum

The initial task families are:

- **Tool selection:** analytical calculation, CFD, FEA, or additional evidence.
- **Evidence extraction:** observed, calculated, inferred, assumed, and missing information.
- **Numerical diagnosis:** mesh, stationarity, conservation, solver health, and field custody.
- **Physics diagnosis:** disagreements without assuming either the simulation or analytical estimate is automatically correct.
- **Experiment selection:** small discriminating tests instead of automatic global refinement.
- **Mutation authority:** numerical adjustments versus changes to geometry, properties, loads, boundary conditions, or requirements.
- **Escalation:** recognize when the larger model or a human engineer is required.
- **Acceptance:** accept only when the required evidence exists and passes its independent checks.

### Example: evidence changes the decision

Create a matched scenario family with similar apparent CFD results but different
evidence completeness:

1. Solver finished; conservation evidence is missing.
2. Conservation passes; mesh independence is missing.
3. Numerical gates pass; the physical prediction differs substantially from the baseline.
4. Complete independent evidence supports acceptance within a declared scope.
5. Evidence conflicts and requires escalation.

The correct decision must change with the evidence, not the phrasing. Include
valid acceptance cases as well as rejection and insufficient-evidence cases;
teaching the model to reject everything is not successful engineering behavior.

## Candidate production is not dataset approval

Every Luna work order should specify approved inputs/source IDs, the output
schema, allowed transformations, prohibited assumptions, deterministic checks,
escalation conditions, and a bounded batch size.

**Luna produces → scripts check → lead reviewer audits → accepted records are frozen.**

Suggested record fields include a case/family ID, source/page references,
evidence type, input assumptions and units, visible tool results, expected action,
concise evidence-linked rationale, alternatives and escalation conditions,
mutation authority, calculation/check receipts, review status, and split ID.

Numerical answers should come from executable calculations or verified retained
results wherever possible. Language-model agreement is not a substitute for
mathematical verification. Failed, ambiguous, and rejected records remain in a
separate audit trail; they do not silently enter training as correct examples.

Split training, development, and held-out evaluation by source and scenario family
**before generating variants**. Keep near-duplicates, paraphrases, and matched
variants within the same split. The production worker must not use hidden test
answers to create training examples. If a held-out case guides remediation, it is
no longer fresh confirmation evidence; retain an untouched final test set.

## Training and promotion authority

The lead model owns base-model selection, the training design, difficult case
labels, predeclared evaluation criteria, and promotion recommendations. The human
engineer retains authority over physical-problem changes and deployment.

Prior rejected fine-tunes remain rejected and preserved. Do not repeat an
unsuccessful recipe unchanged, or recycle its outputs as ground truth. Reuse
existing Aero training, evidence, RAG, verification, and approval infrastructure
where suitable rather than creating a parallel framework.

The proposed comparison is the same base model **untuned versus tuned**, with the
same tools, evidence, retrieval, and execution settings. Separately evaluate the
benefit and cost of larger-model assistance. Do not attribute orchestration gains
to fine-tuning, or compare different checkpoints and call that adapter efficacy.

Measure correct decisions, false acceptance, missed valid acceptance, evidence
fidelity, unauthorized-action attempts, tool correctness, escalation quality,
unnecessary solver runs, task completion time, and resource usage. Freeze scoring
and critical-failure rules before examining results. The student must not be its
own sole judge. Average score cannot excuse a critical acceptance or authority
failure.

## First bounded milestone

The next milestone is a **reviewed pilot dataset and untuned baseline**, not an
immediate training launch:

1. Lead model defines the decision schema, curriculum, and held-out evaluation design.
2. Luna inventories reusable Aero material and prepares approved source cards.
3. Lead model authors a small set of canonical CFD/FEA decision examples.
4. Luna expands approved training families into approximately **100–200 candidate records**.
5. Deterministic checks and lead review audit every pilot record, including acceptance, rejection, and escalation cases.
6. Baseline the untuned teens-sized model, then decide whether to freeze a bounded training experiment.

The count is a proposed pilot scope, not evidence that this amount of training
data is sufficient. Increase volume only when coverage and measured failures
justify it. A larger dataset is not automatically a better dataset.

Possible Luna preparation lanes are source extraction, scenario formatting,
and data/test hygiene. They can operate independently after their schemas and
authority are fixed. No worker may silently change labels, thresholds, or the
engineering contract to complete a batch.

## Return here if the project drifts

Before adding a model, dataset, benchmark, feature, or simulation, answer:

- Does this help the local pilot make a correct, authorized engineering decision?
- Is it knowledge retrieval, decision training, tool execution, or evaluation?
- Can an existing Aero component handle it?
- Is the evidence traceable, applicable, and labeled honestly?
- Who verifies the result independently?
- What bounded exit criterion makes the work complete?
- Are we preserving the original problem, acceptance criteria, and human authority?

Avoid spending the effort on paper accumulation, impressive demos, unrelated
hardware comparisons, or synthetic-data volume without a measured connection to
the engineering-pilot goal. A useful negative experiment is worth retaining.

## Ownership and revision discipline

**Luna prepares and implements. The lead model designs and adjudicates. Code
verifies. The human engineer controls consequential authority.**

This is a public planning reference only. It contains no private toolkit,
training corpus, employer information, credentials, or machine access details.
Revise this roadmap explicitly when the objective changes; do not silently move
the goalposts. It does not authorize any blocked engineering case or weaken
existing qualification gates.

Revision history: **v0.1 — September 28, 2026:** original engineering-pilot goal,
work ownership, data separation, review gates, and first bounded milestone recorded.
This is the roadmap version, not a new operational Aero software revision.

[Back to Aero future work](/software/notes/aero-future-work/) · [Aero home](/software/aero/)
