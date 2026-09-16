# CEP-01 Revision 1.5 qualification report

Run: `2026-09-16T12:58:24.410638Z`

## Disposition

**Infrastructure qualification is complete for the fixture harness; model qualification remains OPEN.**
No CFD/FEA solver was run and no model was granted an engineering-authority verdict.

The program is split into six claims rather than a universal `MODEL PASSED AERO` label. The full-context comparator was constructed locally and never sent to a model.

## Retained case mix

| Case | Retained disposition | Source |
|---|---|---|
| `channel-pass` | BOUNDED_PASS | /software/aero/evidence/ |
| `structural-pass` | NUMERICAL_PASS | /software/aero/evidence/ |
| `structural-not-established` | NOT_ESTABLISHED | /software/aero/evidence/ |
| `structural-fail` | REQUIREMENT_FAIL | /software/aero/evidence/ |
| `harcc-failure` | NUMERICAL_FAIL | /software/aero/evidence/benchmarks/harcc-s4-part2/ |
| `cad-rejection` | REJECTED | /software/aero/evidence/ |
| `coupled-evidence` | MIXED | /software/aero/evidence/ |

The mix includes a passing analytical/CFD screen, structural PASS, structural NOT_ESTABLISHED, structural FAIL, HARCC numerical FAIL, CAD rejection, and a mixed coupled-evidence case.

## Track results

| Track | Claim | Fixture status | Cases | Model calls |
|---|---|---|---:|---:|
| `CEP-R` REPORTING | Model-written report prose is checked against immutable deterministic facts. | **INFRASTRUCTURE_PASS_MODEL_QUALIFICATION_OPEN** | 7 | 0 |
| `CEP-S` STATUS / TELEMETRY NARRATION | Status narration preserves authoritative run state and does not invent progress. | **INFRASTRUCTURE_PASS_MODEL_QUALIFICATION_OPEN** | 7 | 0 |
| `CEP-E` ENGINEERING EXPLANATION | Routine explanations can request bounded evidence and retain open gates. | **INFRASTRUCTURE_PASS_MODEL_QUALIFICATION_OPEN** | 7 | 0 |
| `CEP-C` CONTEXT COMPRESSION | Progressive context reduces payload size without changing decision-grade meaning. | **INFRASTRUCTURE_PASS_MODEL_QUALIFICATION_OPEN** | 7 | 0 |
| `CEP-RTR` ROUTING / ESCALATION | Tasks route by capability, consequence, and evidence rather than model name. | **INFRASTRUCTURE_PASS_MODEL_QUALIFICATION_OPEN** | 7 | 0 |
| `CEP-INV` INVESTIGATION ROUTING | Failed-analysis questions receive bounded evidence and an explicit escalation contract. | **INFRASTRUCTURE_PASS_MODEL_QUALIFICATION_OPEN** | 7 | 0 |

Each track has its own acceptance criteria in the machine-readable record. A fixture PASS means the contract behaved as intended; it is not evidence that a local model is reliable on that task.

## Full versus progressive context

- Comparisons: **42**
- Mean estimated reduction: **93.82%**
- Range: **92.98–94.54%**
- Equivalence rule: disposition, numerical gates, requirement states, open validation gates, critical evidence, unknowns, fidelity recommendation where applicable, and stop discipline must remain materially equivalent.
- Prose need not be identical. A changed engineering disposition is retained as a failure; it is never tuned away.

## Routing and authority contract

- Deterministic arithmetic, gate evaluation, provenance, hashes, and report tables remain authoritative.
- Capability routing selects an advisory provider by capability, consequence, privacy, context budget, and measured performance—not by a hard-coded model name.
- Level 1 decision summaries are the default; Level 2 evidence is typed/allowlisted; Level 3 artifacts remain references unless direct inspection is required.
- HIGH/CRITICAL questions retain escalation or human review. A local narrator may not invent solver progress.

## What remains before qualification

1. Attach held-out cases and repeated runs for each track.
2. Run actual configured local profiles where appropriate and record provider token/latency telemetry.
3. Apply the deterministic report fact verifier to every generated narrative.
4. Preserve every disagreement and route change; do not collapse results into a single score.

## Artifact policy

This report contains only public retained-result metadata and contract fixtures. It contains no private corpus, employer data, raw solver logs, or hidden benchmark answers.
