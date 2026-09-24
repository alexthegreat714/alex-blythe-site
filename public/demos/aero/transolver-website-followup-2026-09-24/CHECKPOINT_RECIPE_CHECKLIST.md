# Aero Transolver checkpoint-recipe research checklist

September 24, 2026. Public website follow-up; not an external inquiry.

The owner requested website publication only. No GitHub issue or external inquiry
will be submitted. No login is needed. This direction supersedes the earlier
submission instructions; frozen execution evidence and release archives remain
unchanged.

## Open evidence requirements

1. Establish the exact training source commit, resolved model/data/training
   configuration, and supported inference runtime.
2. Resolve the checkpoint's twenty-layer architecture versus the model card's
   eight-layer description.
3. Establish the geometry origin formula and whether coordinate scaling by
   `[12, 4.5, 3.25]` applies to these weights.
4. Establish native DrivAerML-to-training pressure/shear units, signs, pressure
   reference, density and velocity-feature conventions.
5. Establish the normalization-generation recipe and checksum-linked reference
   inputs/outputs for `global_stats.json`.
6. Establish normal orientation, point-context size, sampling/chunking, precision
   and deterministic-execution settings.
7. Establish train/validation/test run IDs and run 1's held-out status. A
   separate NVIDIA benchmark split at commit
   `0612ec4ed54484a47bfa134eda7b3b012a607624` puts run 1 in `train.csv` and not
   `validation.csv`; its 436/48 rows match model-card counts, but the split files
   were first committed May 6, 2026, after the checkpoint upload on April 29.
   No source links that later benchmark split to the checkpoint, so the weights'
   run 1 membership stays **NOT_ESTABLISHED**.

The full 40-character checkpoint revision is
`96477aeb86d24c26ccf0797bca1b3851268017d0`. Earlier source-link text omitted
one `f`; the corrected revision's LFS SHA-256 matches the retained file. Frozen
receipts and prior archives were not changed.

See [the dated findings update](FINDINGS_UPDATE.md),
[structured evidence matrix](EVIDENCE_MATRIX.json),
[source index and hashes](SOURCE_INDEX.json), and
[custody summary](CUSTODY_SUMMARY.json).

## Acceptance boundary

These are unresolved questions, not an instruction to fit preprocessing against
the lowest observed error. Keep the model RESEARCH_ONLY. Once a recipe is
independently established, freeze a new reproduction contract before inference.
Publication does not validate the model or authorize another simulation campaign.

The complete report, measurements, audit and source download are at:
https://alex-blythe.com/software/notes/aero-transolver-reference-audit/
