# Aero Revision 1.5 — consolidation and qualification report

**Status:** public surface realigned; CEP-01 infrastructure qualification fixture complete; model qualification remains open.

## Purpose

Revision 1.5 consolidates Aero's demonstrated scope as **engineering analysis orchestration**. Aero carries a declared question through requirements, first-principles checks, geometry, CFD or structural analysis where justified, evidence evaluation, and a reviewable engineering disposition. The numerical tools and retained evidence—not a language model—remain authoritative.

This revision adds no new engineering discipline, numerical solver, optimization framework, or UQ framework.

## Public identity changes

- Software index and Aero overview now describe engineering analysis orchestration rather than CFD-only orchestration.
- The primary path is **Try Aero → See the evidence → Technical details**.
- The evidence hub retains separate categories for verification/analytical benchmarking, numerical adequacy, negative controls/rejection, external validation, reproducibility, model behavior, and infrastructure/efficiency qualification.
- Failure and unknown states remain visible, including HARCC and Samarmad numerical failures, CalculiX `NOT_ESTABLISHED`, CAD rejection, Blind Validation Challenge failure, and open CEP-01 model qualification.

## CEP-01 Revision 1.5

The qualification program is split into six claims rather than a universal model score:

| Track | Claim |
|---|---|
| CEP-R | Report prose is checked against immutable deterministic facts. |
| CEP-S | Telemetry narration preserves authoritative state and does not invent progress. |
| CEP-E | Explanations use typed evidence and preserve unknowns. |
| CEP-C | Progressive context is smaller while decision-grade meaning remains equivalent. |
| CEP-RTR | Routing uses capability, consequence, privacy, and evidence—not model names. |
| CEP-INV | Failed-analysis questions receive bounded evidence and explicit escalation. |

The fixture harness compares full and progressive context across seven retained public evidence states (42 comparisons total). The full comparator is synthetic measurement scaffolding and was never sent to a model or solver. It records a **93.82% mean estimated serialization reduction** (range 92.98–94.54%). Provider-dependent token, latency, MCP-consumption, and model-quality fields are explicitly `NOT_RUN` in this fixture run.

## Authority and equivalence

Deterministic code owns arithmetic, units, hashes, gate evaluation, margins, provenance, report tables, and plot data. Level 1 decision summaries are the default model context; typed Level 2 evidence is requested explicitly; Level 3 artifacts remain references unless direct inspection is necessary. `HIGH` and `CRITICAL` work remains advisory or escalated to human review.

Full versus progressive context is considered equivalent only when disposition, numerical and requirement gate states, open validation gates, critical evidence, unknowns, fidelity recommendation where applicable, and stop discipline remain materially equivalent. Prose need not match. A changed disposition is retained as a failure, not tuned away.

## Remaining qualification work

Actual local-model qualification requires held-out, repeated provider runs for each track with deterministic claim verification. No model is currently certified as a reliable Aero engineering reasoner, and no CEP-01 result changes CFD/FEA validation or design-readiness states.

## Machine-readable record

- [CEP-01 Revision 1.5 qualification summary](../cep-01/qualification-v2/qualification-summary.json)
- [Qualification artifact manifest](../cep-01/qualification-v2/artifact-manifest.json)
- [Benchmark register](/software/aero/evidence/benchmarks/)
