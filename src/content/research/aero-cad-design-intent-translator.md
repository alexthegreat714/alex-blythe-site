---
title: "Aero future work: editable CAD translation"
summary: "A research starter for native Creo-to-NX feature reconstruction: pinned open-source repositories, known gaps, edit-behavior tests, and a bounded implementation brief."
date: 2026-09-24
author: Alex Blythe
tags: [Aero, CAD, Future work, Open source]
readingTime: 5 min
draft: false
relatedSoftware: [Aero]
type: Architecture
---

**Future work · Research starter v0.1 · September 24, 2026**

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

## The first bounded experiment

1. Inventory approved CAD versions, API access, licenses, and existing adapters.
2. Audit the pinned libraries and run their relevant tests in an approved sandbox.
3. Create a synthetic fully constrained sketch, extrusion, and dependent hole
   pattern; freeze expected relationships and admissible edits before translation.
4. Extract the source relationships, reconstruct native destination features,
   and keep all intermediate representations and mapping decisions.
5. Change thickness, hole diameter, and pattern spacing separately. Compare both
   regenerated models, then save, close, reopen, and regenerate the destination.
6. Deliberately exercise unsupported constraints, ambiguous references, units,
   and corrupted inputs. Require honest failures rather than flattened success.

No assemblies, drawings, PLM writes, production migration, or autonomous geometry
redesign in the first milestone. Expand only after explicit evidence supports it.

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
