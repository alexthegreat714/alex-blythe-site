# Future task: editable CAD translation research prototype

Research starter v0.1 — 2026-09-24 — NOT_IMPLEMENTED

This is a proposed task, not authorization to run in a personal environment.
Implementation, employer code, models, and results must remain inside the
organization's approved environment. Do not send data to personal Aero, public
repositories, cloud CAD services, telemetry services, or unapproved AI endpoints.

## Objective

Build a bounded native Creo-to-NX single-part translator that preserves supported
design relationships and demonstrates native edit behavior. Do not substitute
STEP transfer for the requested feature reconstruction. Use STEP only as an
independent geometry reference where helpful.

## Discovery before implementation

Read local instructions. Inventory exact CAD versions, licensed APIs, SDKs,
runtime requirements, approved dependencies, existing CAD adapters, evidence
custody, approval systems, tests, and source-control policies. Do not assume
personal Aero is present or authorized. Reuse equivalent approved components.
Document unavailable APIs as blockers; do not bypass license controls.

Review these pinned upstream source snapshots and licenses before executing:
Morphe, SketchBridge, SimpleCADAPI/CADIR, InventorLoader, and Creopyson.
Use UPSTREAM_RECEIPTS.json for exact commits and archive hashes. Run a bounded
acceptance evaluation before selecting a base to fork. Do not blindly merge all
five projects or add unnecessary frameworks. InventorLoader is GPL-2.0 and needs
normal organizational license review. Dependencies have their own terms.

Known concerns: Morphe's SolidWorks dimensional operations can reposition
geometry rather than create driving dimensions. InventorLoader can replace
unsupported expressions with nominal values. Neither behavior may silently count
as design-intent preservation. CADIR reconstruction does not itself establish
extraction of arbitrary existing Creo histories. Creopyson's full feature
extraction coverage is not established.

## Freeze the translation contract

Record direction, versions, units, coordinate systems, tolerance definitions,
supported features and expressions, expected relationships, permitted equivalent
feature decompositions, validation cases, admissible edits, and stop conditions.
Choose tolerances before reviewing results. Never alter original source parts.

First milestone: synthetic single-part sketches with explicit geometric and
dimensional constraints, extrusion, simple holes and linear patterns. Exclude
assemblies, drawings, complex blends, external references, PLM writes, and
production migration. Unsupported cases must stop or remain explicitly partial.

## Proposed components

1. Read-only source-native extraction adapter.
2. Typed, versioned intermediate representation for features, sketches,
   constraints, expressions, datums, dependencies, units, reference intent,
   suppression state, and source provenance.
3. Deterministic feature-mapping registry with an explicit capability matrix.
4. Destination-native reconstruction adapter and regeneration diagnostics.
5. Independent geometry, relationships, and edit-behavior evaluator.
6. Auditable mapping decisions, errors, unsupported features, and review queue.

Do not assume source and target tree shapes must match exactly. Test supported
semantic equivalence. Preserve observed, inferred, proposed, and unestablished
relationships separately. Never invent undocumented design intent. Treat source
expressions as data, not arbitrary executable code.

AI may suggest mappings or diagnose discrepancies; it cannot certify itself.
Ambiguous face/edge references require explicit handling. Similar geometry or
matching numeric entity IDs alone does not establish reference equivalence.

## Required proof

Use a synthetic constrained bracket and independent held-out synthetic variants.
Freeze ground truth and tests before conversion. Evaluate:

- Native destination features, not one imported body labeled a feature tree.
- Geometry deviation, volume, units, orientation, and solid integrity.
- Sketch constraints and degrees of freedom; matching DOF alone is insufficient.
- Parameter-expression and parent-child relationship preservation.
- Separate controlled edits to thickness, hole diameter, and pattern spacing.
- Correct downstream regeneration and reference selection after each edit.
- Save/close/reopen/regenerate behavior.
- Negative tests for missing constraints, unit errors, nominalized expressions,
  unsupported features, ambiguous references, and corrupted inputs.
- Deterministic reproduction with tool/runtime/version and artifact identities.

Do not claim equivalence for arbitrary edits from a finite test suite. Define the
tested edit envelope. Record source and destination failures independently.
Do not silently heal geometry, flatten features, change dimensions, or suppress
failures to obtain PASS. Geometry-only fallback requires explicit approval and
must remain GEOMETRY_ONLY, not full-fidelity translation.

## Engineering-control integration

Reuse approved contract, provenance, hypothesis, mutation-authority and validity
gates. Protect semantic engineering selections (inlet, wall, load, contact,
interface). Require a separate downstream simulation-selection check before any
future CFD/FEA use. A successful CAD translation does not qualify a simulation.

## Deliverables and stop logic

Produce discovery report, dependency/license inventory, capability matrix,
translation contract, intermediate schema, adapter implementations, test corpus,
raw test results, per-feature mapping trace, limitations, and hashed artifacts.
Use VERIFIED_WITHIN_DECLARED_SCOPE, PARTIAL_RECONSTRUCTION, GEOMETRY_ONLY,
UNSUPPORTED, FAILED, or NOT_ESTABLISHED as appropriate. Do not fabricate pass
rates, expected coverage, development cost, or schedule.

Stop for absent licensed APIs, missing environment approval, unresolved license
obligations, unsafe dependencies, or inability to establish required semantics.
Do not automatically expand to real employer hardware or upload any artifacts.

## Next milestone decision

Only after the first synthetic source-to-native-target proof and edit suite pass,
propose one bounded expansion. Prioritize engineering usefulness and failure
coverage over number of supported feature names. Keep original failures.
