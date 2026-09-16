# CEP-01 — Context efficiency, model routing, and portability

**Run:** 2026-09-16 00:13:36 UTC
**Disposition:** Infrastructure pass implemented; the model result is a one-sample demonstration, not a qualification.
**Scope:** Compact engineering context, capability-based model routing, local report drafting, deterministic claim verification, scoped tool discovery, and portability contracts. No CFD or FEA solver was run.

## Question

Can Aero give a model only the bounded evidence needed for its assigned task, route cognitive work by declared capability rather than fixed model names, and reject report prose that contradicts deterministic engineering records?

## What changed

CEP-01 adds an optional, model-independent layer around Aero's existing engineering and evidence systems:

- A typed context manifest summarizes the active question, stage, consequence, gates, assumptions, evidence IDs, and available expansions.
- A context broker exposes bounded, allowlisted requests for deeper evidence. Models receive decision summaries by default; detailed evidence is opt-in and raw artifacts remain references.
- Tool outputs use decision-summary, engineering-evidence, and raw-artifact levels.
- A capability router considers task, consequence, ambiguity, novelty, privacy, context, latency, cost class, and measured profile capability. Routing is configurable; engineering behavior does not require a named model.
- Deterministic calculations and evidence gates remain authoritative. A report verifier checks claims about values, units, gates, readiness, and causal statements before prose is accepted.
- Local status narration, rate limiting, context measurement, task-scoped MCP discovery, escalation packets, bounded retries, and portability contracts are available as opt-in components.
- Existing planner/MCP paths are integrated incrementally; CEP-01 does not silently replace every model call or globally re-plumb RAG/GraphRAG.

## Local report-drafting check

The run used one fabricated verifier fixture with declared pass, fail, and not-evaluated states. It was deliberately not a physical engineering case. All three model calls were local; there were zero remote model calls, and the full-context comparator was constructed locally and never sent to a model.

| Local profile | Result | Reported input tokens | Unsupported-claim checks | Latency |
|---|---|---:|---|---:|
| `gemma3:4b` | Draft rejected | 242 | One unsupported causal claim | 6.67 s |
| `qwen2.5:14b-instruct` | Draft rejected | 230 | Wrong gate state and unsupported causal claim | 14.92 s |
| `qwen2.5:72b-instruct` | Verified on this sample | 230 | None detected; all checked facts and required gate coverage passed | 148.66 s |

The compact context estimator reported 195 tokens against a hypothetical 51,542-token full-context estimate (99.62% estimated reduction). The local inference service reported 230–242 actual prompt tokens after provider framing, corresponding to approximately 99.53–99.55% fewer tokens than the hypothetical comparator. Token estimates are approximate and provider tokenization varies.

## Interpretation

For this single report-drafting sample, the deterministic verifier correctly blocked the two smaller-profile drafts and accepted the 72B profile's claims. The router therefore selected the configured profile that passed this one sample. This is a provisional routing observation—not evidence that 72B is generally better, that it is the smallest reliable option, or that it can reason through CFD/FEA work.

The targeted regression suite passed **55 tests** across context contracts, routing, reporting, status narration, portability, MCP, FEA, and the engineering toolkit. These are software tests, not solver validation.

## Limits and next work

- Repeat the report check over held-out cases and multiple runs before qualifying any model profile.
- Benchmark status narration, extraction, RAG synthesis, explanations, fidelity selection, and failure investigation as separate task classes.
- Integrate bounded knowledge retrieval and migrate live chat paths behind explicit configuration.
- Measure real provider costs where applicable; energy and local hardware depreciation were not measured.
- Map future environment adapters only after their approved models and tools are known.

This public report contains no private knowledge corpus, employer data, or physical simulation result. The benchmark is about context and report verification only.

## Public artifacts

- [Machine-readable summary](./benchmark-summary.json)
- [SHA-256 checksums](./SHA256SUMS.txt)
