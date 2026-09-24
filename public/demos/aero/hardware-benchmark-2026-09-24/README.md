# Aero public local-inference benchmark — September 24, 2026

Public release 1.0. Measurements September 23–24, 2026.

This is a deliberately selected aggregate export, not the complete private archive.
No private toolkit, machine access details, raw filesystem paths or credentials are included.
System IDs 3090 and spark are generic retained labels. spark means the tested GX10/GB10 node.

Primary suite: cache-neutral (deterministic unique prompt prefixes; n=5 per completed group).
Historical suite: warm-cache (repeated identical prompts; cache reuse affects prefill).
Both preserve actual measured values. Missing values remain null/blank, not zero.
Same Gemma 3 12B Q4_K_M checkpoint in the primary suite; Ollama 0.32.5 versus 0.20.4.
Runtime differences prevent a silicon-only or memory-bandwidth causal interpretation.
One warm-up precedes measured repetitions; medians are the primary reported statistic.
Agent loops contain four sequential model calls and mocked deterministic tools.
No CFD/FEA execution or production end-to-end engineering decision was measured.

Charts are rendered from the public primary-suite aggregates. Device power is not whole-system wall power.
GPU-memory and host/unified-memory counters are not interchangeable or isolated model memory.
Model labels and selected statistical fields are preserved; all other source keys are excluded.
The export script is versioned with the public website source.
REPORT.md records methodology, incomplete capacity tests and limitations.
SHA256_MANIFEST.json hashes the public data/report/chart subset, excluding itself and verification.
VERIFICATION.json records a separate reopening and digest check; it is not self-hashed.
