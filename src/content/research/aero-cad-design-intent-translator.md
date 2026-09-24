---
title: "Aero future work: editable CAD translation"
summary: "A research starter for native Creo-to-NX feature reconstruction: pinned open-source repositories, known gaps, edit-behavior tests, and a bounded implementation brief."
date: 2026-09-24
author: Alex Blythe
tags: [Aero, CAD, Future work, Open source]
readingTime: 8 min
draft: false
relatedSoftware: [Aero]
type: Architecture
---

**Future work · Research starter v0.1 · September 24, 2026**

Page update: **staged implementation roadmap added September 24, 2026**.
The original v0.1 source download remains unchanged; the expanded roadmap below
is the current planning supplement.

Status: **RESEARCH_ONLY / NOT_IMPLEMENTED**. This is not a new operational Aero
revision or a demonstrated Creo-to-NX converter. Only public-source research is
included. No employer models, workflows, code, credentials, or licenses are used.

[Download the project and pinned repositories](/demos/aero/future-work/cad-design-intent-v0.1/CAD_TRANSLATION_RESEARCH_STARTER.zip) ·
[Implementation brief](/demos/aero/future-work/cad-design-intent-v0.1/IMPLEMENTATION_BRIEF.md) ·
[Repository identities](/demos/aero/future-work/cad-design-intent-v0.1/UPSTREAM_RECEIPTS.json) ·
[SHA-256 manifest](/demos/aero/future-work/cad-design-intent-v0.1/SHA256_MANIFEST.json) ·
[Package verification](/demos/aero/future-work/cad-design-intent-v0.1/VERIFICATION.json)

## The project we actually want

Transfer **editable engineering relationships**, not merely matching solids.
The proposed first direction is native Creo to native NX for single parts.
STEP remains a reference geometry channel, not a feature-history substitute.
The desired result preserves supported sketches, dimensions, expressions,
dependencies, and native edit behavior. Equivalent destination operations may
use a different feature sequence; identical tree appearance is not the goal.

The success test is changing predeclared dimensions in both CAD systems and
checking that the models regenerate with equivalent geometry and relationships.
Passing a bounded edit suite is evidence for that scope, not proof of arbitrary
future-edit equivalence or recovery of undocumented human design intent.

## Sources saved for later

The download contains untouched source ZIPs pinned to the commits below, their
upstream license files, a source receipt, and a starting implementation brief.
They were downloaded and their archive integrity checked, **not installed or
executed**. Repository descriptions are leads to evaluate, not Aero test results.
These snapshots omit Git history, submodule contents, and any external assets
not contained in upstream's source ZIPs.

| Project | Pinned commit | Listed license | Intended use and boundary |
| --- | --- | --- | --- |
| [Morphe](https://github.com/CodeReclaimers/morphe/tree/b1868427f35a13779c8fd3d5be50684c7675a688) | `b1868427f35a1` | MIT | CAD-independent 2D sketch/constraint schema and adapters. No listed Creo/NX adapter. Candidate for the sketch layer, not a full part translator. |
| [SketchBridge](https://github.com/CodeReclaimers/sketch_bridge/tree/4aff4209ce7ff706b3c33eaff2785bb0761b0708) | `4aff4209ce7ff` | MIT | Transfer UI built on Morphe. Optional reference for user workflow, not a second required engine. |
| [SimpleCADAPI / CADIR](https://github.com/PhySpace/SimpleCADAPI/tree/aead7f84817ff6320512aad8f6b85cad590f23df) | `aead7f84817ff` | Apache-2.0 | Replayable modeling graphs, expressions, and editable reconstruction. Candidate architecture; Creo/NX support and extraction from arbitrary existing models are not established. |
| [InventorLoader](https://github.com/jmplonka/InventorLoader/tree/e94bdf5e29052a0dc7ce6fdf755e956ae507caec) | `e94bdf5e29052` | GPL-2.0 | Feature-based Inventor-to-FreeCAD reconstruction to study. Not a bidirectional exporter or Creo/NX adapter. |
| [Creopyson](https://github.com/Zepmanbc/creopyson/tree/2e45d232bcafee4af1cc4b728536d5cdde39049a) | `2e45d232bcaf` | MIT | Python automation through CREOSON/JLink; useful for parameters and dimensions. Complete feature extraction is not established. Creo and its applicable licenses remain necessary. |

Licenses and dependencies require the receiving organization's normal review.
The bundle is not an assertion that all projects can be combined without further
review. Original notices remain intact; no upstream source has been modified.

## Findings that must not get lost

- Morphe's SolidWorks adapter includes dimensional operations that move or
  recreate geometry. That does not establish a persistent driving dimension.
  [Inspected adapter source](https://github.com/CodeReclaimers/morphe/blob/b1868427f35a13779c8fd3d5be50684c7675a688/morphe/adapters/solidworks/adapter.py).
- InventorLoader documents replacing unsupported parameter expressions with
  nominal values. Its behavior is useful to study but unacceptable as an
  undisclosed full-fidelity translation.
  [Documented limitations](https://github.com/jmplonka/InventorLoader/tree/e94bdf5e29052a0dc7ce6fdf755e956ae507caec#limitations).
- CadQuery is useful for geometry operations and synthetic fixtures, but its
  import/export documentation explicitly does not promise parametric interchange.
  It is not included as another mandatory framework.
  [CadQuery exchange documentation](https://github.com/CadQuery/cadquery/blob/master/doc/importexport.rst).
- Public Creo documentation describes supported feature-element extraction;
  NX Open provides native automation. Exact version, coverage, SDK access, and
  license requirements must be discovered in the implementation environment.
  [Creo feature inquiry](https://support.ptc.com/help/creo_toolkit/protoolkit_pma/r13/chinese_tw/creo_toolkit/Feature_Inquiry_1.html),
  [NX Open](https://training.plm.automation.siemens.com/ilt/iltdescription.cfm?pID=TR-OPENAPI____NX___12.0___6200).

## Proposed architecture

Source-native extraction → typed design representation → deterministic mapping
→ destination-native reconstruction → independent geometry and edit tests
→ scoped translation disposition.

The representation needs explicit units, coordinate frames, sketch constraints,
parameter expressions, datums, feature dependencies, source identifiers,
suppression states, and reference-selection intent. Observed relationships and
inferred relationships must remain distinct. Do not assume Morphe and CADIR fit
together without adaptation; evaluate them before choosing a dependency boundary.

AI may propose unsupported mappings or diagnose failures. Native CAD regeneration
and independent tests determine acceptance. Ambiguous references require review;
nearest-face matching alone is insufficient when several faces are plausible.

## The intended finished experience

Select a source Creo part and an NX target version. Before reconstruction, the
tool reports supported features, known gaps, and required review. It creates a
native editable destination model, runs independent tests, and presents the
result alongside preserved relationships, unresolved features, and manual work
still required. The user can open the destination model and change supported
driving dimensions, not merely inspect an imported solid.

This is a target experience, not a capability of the current research bundle.

## Implementation roadmap and exit criteria

The goal is to turn selected upstream projects into components of one translator,
not stitch five applications together. Each stage has an evidence requirement
before the scope grows. No stage below has been executed.

### Step 0 — Establish the approved execution boundary

Inventory exact Creo/NX versions, licensed APIs, SDKs, approved runtimes, existing
adapters, and evidence/review infrastructure. Review the pinned libraries and
their dependencies, then run relevant upstream tests in an approved sandbox.
Keep all implementation and organizational data within that environment.

**Exit evidence:** a capability and license inventory, recorded test outcomes,
and an explicit choice of components to reuse, extend, or reject. Missing API
access or approval is a blocker, not a reason to bypass controls.

### Step 1 — Prove we can read engineering relationships

Start with a small synthetic Creo part. Extract its sketch entities, constraints,
driving dimensions, expressions, datums, feature dependencies, and references.
Produce a human-readable account before creating anything in NX: for example,
“this hole stays centered because of these relationships,” rather than “the hole
happens to be centered at the current coordinates.” Preserve source identifiers
and distinguish explicit relationships from inferred intent.

**Exit evidence:** the extraction agrees with the deliberately authored synthetic
model and identifies missing or unsupported information. A screenshot or current
shape alone cannot establish this.

### Step 2 — Define the common design representation

Evaluate Morphe for sketch interchange and SimpleCADAPI/CADIR for modeling graphs
and expressions. Reuse only what passes the required tests; do not force either
library to express unsupported semantics. Specify a typed, versioned intermediate
format with explicit units, coordinate frames, dependencies, source provenance,
constraints, expressions, and reference-selection intent.

**Exit evidence:** the representation can serialize and recover the declared
relationships without silent loss. Invalid units, dangling references, unsupported
expressions, and unknown feature types receive deterministic diagnostics. It is
neither a STEP file nor an unstructured AI description.

### Step 3 — Translate one small part end to end

Implement source extraction and destination reconstruction for a constrained
sketch, extrusion, and simple hole. The NX result must contain native editable
features and persistent driving dimensions. Freeze expected relationships,
comparison tolerances, and admissible dimensional edits before reviewing results.
Change dimensions independently in both CAD systems and compare regeneration.
Save, close, reopen, and regenerate the destination model.

**Exit evidence:** baseline geometry and the declared edit suite pass, with the
underlying constraints and expressions preserved. A single imported body or
nominal-value substitution must not count as a feature-preserving translation.

### Step 4 — Preserve references and dependent behavior

Add a datum-positioned hole, a face-attached pocket, and an expression-driven
pattern. Exercise changes that split, remove, or reshape referenced entities.
Determine whether the destination remains attached to the intended engineering
reference. Do not accept matching entity numbers or nearest-face selection as
proof when multiple candidates are plausible.

**Exit evidence:** supported reference changes regenerate consistently; ambiguous
or unsupported cases stop or enter review. For later simulation use, protect
semantic selections such as inlets, interfaces, loaded surfaces, and contacts
through a separate downstream selection-validity check.

### Step 5 — Expand one feature family at a time

Add revolutions, patterns, and mirrors, then consider more difficult operations.
Each addition needs a mapping specification, positive and negative fixtures,
admissible edit tests, and an explicit support boundary. Keep synthetic variants
held out from mapping development so the translator is not merely reproducing
its demonstrations. Retain failures rather than deleting difficult cases.

**Exit evidence:** per-family test results, known failure modes, and a scoped
support matrix. Passing finite edits does not establish arbitrary-edit equivalence.
Do not expand simply to increase the count of advertised feature names.

### Step 6 — Make the translator practical to use

After the core proof, add batch processing, resumable jobs, side-by-side inspection,
per-feature mapping explanations, and a human-review queue. Preserve originals
and write destination artifacts separately. Assemblies and associated drawings
are separate later milestones, not assumed consequences of part translation.

**Exit evidence:** users can identify supported results, inspect failures, resume
interrupted work without corrupting evidence, and distinguish verified models
from incomplete reconstructions. No production migration or PLM writes are
authorized by this research roadmap.

### Proposed policy for unsupported features

Allow an explicitly marked partial model for inspection, but never label it a
successful full translation. Stop dependent reconstruction where missing
semantics would make subsequent results misleading. Geometry-only fallback must
be separately approved and remain `GEOMETRY_ONLY`. Whether partial output is
enabled by default is an open product decision to freeze in the implementation
contract—not a decision already made by this page.

### AI's role throughout

AI can help implement adapters, propose alternate mappings, and diagnose failed
tests. Deterministic mappings handle established cases. Independent native
regeneration and relationship/edit tests determine acceptance. More generated
code cannot substitute for API coverage, reference integrity, or verified behavior.

## Fit with the Aero methodology

Reuse approved contract, artifact custody, independent-gate, and review patterns
where present. A translator must not grade its own success from a screenshot.
Report geometry agreement, constraint preservation, expression preservation,
reference integrity, regeneration, and tested edit behavior separately.

Engineering selections need special protection: inlets, walls, interfaces, loads,
and contact surfaces must not silently attach to the wrong entity after transfer.
Simulation setup validity is separate from CAD translation validity, and neither
establishes physical validation of a future analysis.

Suggested dispositions: `VERIFIED_WITHIN_DECLARED_SCOPE`, `PARTIAL_RECONSTRUCTION`,
`GEOMETRY_ONLY`, `UNSUPPORTED`, `FAILED`, and `NOT_ESTABLISHED`.

## Next action

Take the downloadable brief into the approved implementation environment and
perform discovery plus a library acceptance audit. Do not begin with arbitrary
production parts or assume the saved code is qualified. This public starter does
not authorize employer-data ingestion into personal Aero or outward sync.

[Back to Aero future work](/software/notes/aero-future-work/) · [Aero home](/software/aero/)
