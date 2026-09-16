# Aero Heat Exchanger Blind Benchmark Program — v1

**Current program state (2026-09-16): the executable synthetic evidence release
is complete, but publication validation is incomplete. HX-B01 has two preserved,
hash-frozen plan-only STOPs
plus a separately identified Seo-channel analytical comparison. That scoped
slice deliberately failed its revealed correlation screen by 30.86%; it did
not run CFD/FEA and does not establish pointwise experimental validation. The
approved HX-S01 source-informed synthetic replacement remains a numerical FAIL;
HX-B02 through HX-B04 remain source/scoreability gated. HX-B05 received a
separate anonymized, result-withheld Luna feasibility packet after custodian
disclosure and stopped before preregistration. HX-D01 remains open and must not
begin until the preceding study dispositions are complete and frozen. A separate
synthetic companion suite now exercises the remaining B02–B05/D01 capability
intents without claiming source truth.
HX-S01 is not blind and does not replace or pass HX-B01.**

### Latest HX-S01 diagnostic update — 16 September 2026

The original three-grid baseline remains a numerical FAIL. A separately
identified coarse-grid tolerance diagnostic reached iteration 1,600 with
residual, mass, and energy checks inside their limits, but the full-window
pressure-drop/heat-duty stability gate failed: cold-side pressure drop changed
1.81–4.42% and each duty changed about 0.79–0.89% per 25 iterations, versus a
0.5% limit. Medium/fine were not run under this diagnostic. LTOL-002 is kept
with its normal solver end and an unevaluable monitor gate because `purgeWrite`
discarded two required checkpoints; LTOL-003 repeated the window while
retaining all outputs. See `HX-S01_synthetic_replacement/diagnostics/` for the
plan, receipts, solver log, five postprocessing records, result, and hashes.

## Purpose and scientific boundary

The program tests whether Aero can reconstruct engineering methods, choose
fidelity, calculate first-order quantities, construct fit-for-purpose geometry,
run CFD/FEA when warranted, preserve numerical failures, and compare frozen
predictions with a publication only after a timestamped reveal gate. A synthetic
transfer study is not an experimental benchmark. A successful solver exit is not
validation. A withheld answer does not turn an under-specified reconstruction
into a reproducible one.

The supplied task text ends at the heading for **§22 Blind Freeze**. This v1
implements the requirements visible through that heading. No unstated later
sections have been inferred.

## Sequence

1. Verify source identity, lawful access, benchmark suitability, and input/result
   partition.
2. Give Luna only the allowlisted, anonymized pre-run packet. The first call is
   planning/feasibility only; it cannot run solvers or access publication results.
3. Freeze the complete engineering plan and its assumptions before any target
   calculation. Freeze analytical predictions before CFD/FEA. Freeze final
   numerical predictions, evidence, and disposition before opening the sealed
   comparison package.
4. Require packet lexical audit, human boundary review, source custodian
   attestation, hash verification, and an external timestamp before reveal.
5. Reveal through a separate comparison step; retain every original artifact.
   Any tuning is a new POST-REVEAL run with a different run ID.

The repository tool `Aero/tools/hx_blind_program_guard.py` checks the exact
visible-file allowlist, scans configured forbidden literals, hashes the packet,
and freezes/verifies the Luna plan. Its `solver-gate` command fails closed while
study applicability, comparison targets, numerical gates, acceptance bands,
source eligibility, or independent packet review remain open. That command is
a program preflight only; it does not dispatch a solver or replace Aero's own
case-level authorization controls. The utility is deliberately described as a
lexical/hash check: it does not prove semantic non-leakage, filesystem
isolation, immutable storage, or trusted time. The existing
`Aero/tools/freeze_pche_evidence.py` remains the final prediction-bundle freezer.

## Study registry

| Study | Target | Current disposition |
|---|---|---|
| HX-B01 | Open experimental straight-channel PCHE study; bibliographic identity held in custodian registry | Two original plan-only STOPs are preserved. Scoped Seo-channel analytical comparison is complete and FAILs the revealed correlation screen; pointwise experiment, CFD, and FEA remain unestablished. [Scoped evidence](HX-B01/runs/seo_channel_analytical_01/COMPARISON_REPORT.md). |
| HX-S01 | Source-informed synthetic counterflow PCHE reconstruction | Complete as a separate synthetic study. Frozen 250-iteration three-grid result is NUMERICAL FAIL; all three same-settings diagnostics reached 1,000 and still missed the residual gate. No experimental score, PCHE FEA, or design-readiness claim. [Local report](../HX-S01_synthetic_replacement/REPORT.md). |
| HX-B02 | Laboratory PCHE CFD → thermal/structural analysis | Not eligible for FEA-accuracy scoring until lawful full text and an independent structural truth/measurement are located. |
| HX-B03 | 3-D zigzag PCHE fidelity/thermal-structural study | Conditional; article is paywalled and the available author manuscript must be version-matched and audited before packetization. |
| HX-B04 | PCHE structural and geometry sensitivity study | Candidate requires lawful full text and enough pre-result geometry/material/loading to reproduce. |
| HX-B05 | High-temperature lattice-HX architecture/material trade | An anonymized, runtime-reference-withheld Luna plan-only review completed and froze a `STOP` before preregistration. The packet passed lexical review; custodian result exposure is disclosed. No selection, solver run, or score. See `HX-B05/custodian/LUNA_PREPLAN_REVIEW.md`. |
| HX-D01 | New, generic synthetic design-transfer study | Explicitly blocked until HX-B01–B05 have finished and been frozen. |

The separately identified `synthetic_companion_suite_v1/` adds executable,
source-informed synthetic companions for the coupled contract, fidelity,
sensitivity, architecture/material and design-transfer intents. It does not
override the publication-order gate or convert any synthetic output into
validation.

The authoritative details, DOI links, licensing/access checks, and per-study
gates are in `program_registry.json`; that custodian file is not part of the
Luna-visible packet.

## Frozen common rubric

`common_rubric_v1.json` defines the 0/1/2 scoring semantics for the 20 requested
categories. Applicability and target-specific numerical thresholds must be
declared in each benchmark's preregistration after source audit but before any
target solve. `NOT_APPLICABLE` is not a zero. A missing result target is not a
license to invent one.

## HX-B01 current gate

The initial packet contained problem inputs, measurement definitions, declared
uncertainties, and explicit unknowns, but not article identity or results. A
fresh GPT-5.6 Luna invocation returned a complete 22-section plan and
recommended **STOP before CFD/FEA** for a pointwise validation claim. A second,
separately versioned thermal-only packet attempted a narrower mean-duty question.
Luna again completed all 22 sections and recommended **STOP before
preregistration**: outlet measurement/mixing-plane correspondence, profile and
flow-distribution bounds, area mapping, external/edge losses, and uncertainty
coverage remain unresolved. It analytically reconstructed provisional flow
rates and a loose energy ceiling, but explicitly did not produce a defensible
heat-duty prediction interval. That second plan is preserved at
`HX-B01/runs/scoped_thermal_T01/frozen/luna_scoped_feasibility_T01_v2_20260915T182742Z/`;
its plan SHA-256 is
`72aea54a3f3d3cdda9b53a2d243873ecb8dfec5e2a17cecb48a3487bff961fca` and its
packet SHA-256 is
`19523e41ef083c9d72481f90d75fa783b0f697540cef54eafdc28fd819ddef28`. The
run-specific gate returned `DENIED`; no solver was dispatched and no target
was revealed.

After this stop, a custodian-only source screen identified an ASME 2024
high-pressure-water airfoil-fin PCHE paper as a **conditional lead**, not an
approved replacement. It reports a dimensioned NACA0025 fin arrangement and
core-level instrumentation that may resolve some current packet gaps, but the
reviewed author-hosted PDF carries ASME copyright, permission handling is not
established, and exact input-point selection plus core-to-measurement
comparability still require review. The detailed gate list is in
`HX-B01/custodian/source_replacement_review_20260915.json`. No paper copy was
added to a public area and no new Luna packet was issued.

The source article presents its experimental outcomes graphically rather than
providing a verified machine-readable raw-data file in the reviewed source
record. Any later reference digitization needs a separate, hashed extraction
record, independent point/axis checks, and a digitization uncertainty estimate.
If an exact experimental point and matching quantity cannot be established, the
accuracy gate remains `NOT_EVALUATED`.

## Existing Samarmad run

`Aero/reports/pche_samarmad_publication_run_v1/` is retained as a prior
publication-targeted rehearsal, not imported as evidence for this program. Its
own disposition is `INCOMPLETE`: numerical CFD gates failed and experimental
comparison was unscored because the operating point could not be matched; it
does not provide a structural truth target. It is not counted as HX-B01 or any
blind scored success.

## HX-S01 synthetic replacement

After the HX-B01 feasibility stops, the owner approved a logically bounded,
source-informed synthetic replacement rather than fabricated experimental
truth. Samarmad and Jaffal (2023) and supporting open references ground the PCHE
configuration, terminology, and nominal water-property choices. Assumed or
ambiguous inputs remain explicitly labeled; publication result values are not
used as HX-S01 targets. The study includes a first-principles screening
calculation, an independently reconstructed periodic hot/cold/solid geometry,
three OpenFOAM CHT grids, conservation checks, and retained numerical failures.

At the predeclared 250 pseudo-iteration horizon, the residual gate failed on
all three grids and medium-to-fine pressure-drop changes exceeded the 5%
threshold. All three same-settings diagnostics reached iteration 1,000 but
still failed the residual gate; their heat-duty snapshots rose about 196–203%
from iteration 250. The fine case resumed from its archived iteration-275
field without changing its mesh, physics, or numerical settings. At iteration
1,000, fine-to-medium pressure drop still differed by 28.7% hot-side and 28.1%
cold-side. These extensions do not alter the frozen baseline. HX-S01 is not an
experimental validation, a blind study, or a test of autonomous local-model
piloting. Full assumptions, results, hashes, and scope boundaries are in the
linked report and evidence manifest.

## Honest limitations

- A fresh Luna process and isolated working directory reduce conversational
  carryover, but the Codex CLI's read-only sandbox and instruction policy are
  not represented as cryptographic information-flow isolation.
- The model may have pretrained familiarity with public literature. The program
  can withhold runtime references; it cannot prove the model has never seen the
  paper during training.
- A local SHA-256 manifest proves file identity from that point onward only if
  the manifest itself is trusted. It is not an external timestamp or immutable
  storage. Those remain release gates.
- No HX-B01 prediction, CFD/FEA run, publication reveal, or score is claimed by
  this initialization report.

## First executed gate

The raw Luna plan is retained at
`HX-B01/custodian/luna_pre_run_plan_raw.md`; the plan-only freeze is at
`HX-B01/frozen/luna_feasibility_plan_20260915T172952Z/`. Its SHA-256 is
`152d573ec41a83662edef5db71c74829074bf6ca99ddc4cc8b04fa0312155690`, verified
by the guard. The packet hash is
`f8c4239964edaac6559e8f4e62b17c649a032efe6d5601f49082cf630cc721a0`. Both are
local hashes only; neither has a trusted external timestamp. The separate
invocation and decision record is `HX-B01/LUNA_PREPLAN_REVIEW.md`.

Before a revised B01 plan can be frozen, the custodian must decide whether to
provide a profile/dimensioned drawing extraction, configuration-specific
flow/area mapping, pressure-tap/port definition, and matched target-point
procedure. Any revised packet gets a new version and a separate Luna run; the
first stop decision remains unchanged.

## Blinding/custody disclosure

During source discovery, public search results exposed portions of the paper's
abstract/conclusion and outcome-related language to the implementing agent.
That material was not copied into Luna's two-file packet, the runtime directory,
the CLI prompt, or Luna's response; the invocation event stream showed no
model-initiated search/tool call. Nevertheless, the implementing agent cannot be
treated as answer-blind. The supported claim is **runtime-reference withholding
for Luna**, subject to the documented sandbox and pretraining limitations—not
a fully answer-blind human-custodian experiment. The disclosure is also recorded
in `INFORMATION_BOUNDARY_REPORT.md` and `information_boundary.json`.

## Current HX-B01 authorization

`HX-B01/preregistration_status.json` records the open applicability and
acceptance-band gates. No first-principles prediction, CAD/mesh, CFD, FEA,
numerical pass/fail, accuracy score, or reveal is authorized for HX-B01 until a
new versioned packet closes those gates and receives a new Luna plan freeze.
This restriction does not apply to the separately scoped HX-S01 synthetic
study. The original HX-B01 stop plans remain preserved.
