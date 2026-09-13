# Aero Blind Validation Challenge framework — preparation release 0.1

**This is not a completed blind benchmark.** No production input package,
preregistration, solve, prediction freeze, reference unseal or comparison exists.
The public status must remain NOT EVALUATED until those events really occur.

## Role separation and the limit of the software

1. A **custodian** can access source papers, experimental values and the seal key.
   They select an entire matched series, document source version/rights and curate
   input-only geometry, operating conditions and station locations. They must not
   supply answer curves, expected coefficients, conclusions or successful CFD
   choices to the predictor. A schema is not semantic proof of clean curation.
2. A **fresh predictor** receives only input.json and the committed preregistration,
   plus approved tools. No shared chat, RAG, browsing, source paper, reference mount,
   seal key, or reusable contaminated case memory. A supervisor records actual
   process/container identity, mounts, network restrictions and tool versions.
3. A **comparison operator** gains the key only after a publicly anchored prediction
   and evidence manifest exist. The comparator preserves every registered point.

This planning task saw answer-bearing search snippets. Its exposure is recorded
in selection.json. Do not use its conversation as predictor context. A famous
benchmark may also occur in model pretraining; “blind” here can only mean verified
runtime reference withholding, not a proof of total prior ignorance.

AES-256-GCM protects the sealed bytes, not the honesty of a custodian. Git receipts
check file contents against a commit reachable on origin/main, fetched at the time
of anchoring. They are auditable history, not a trusted timestamp service or an
immutable ledger against repository administrators. Independent archiving/signing
can strengthen this. The state machine does not itself launch/secure a container
or attest model memory. start records reviewed isolation attestations; it is not a
substitute for actual supervisor evidence. Integration with a restricted Aero
predictor/solver executor remains an explicit production prerequisite.

## Implemented stages

`INPUT_FROZEN -> CRITERIA_FROZEN -> CRITERIA_FROZEN_ANCHORED -> SOLVE ->
PREDICTION_FROZEN -> PREDICTION_FROZEN_ANCHORED -> REFERENCE_UNSEALED ->
COMPARED -> COMPARED_ANCHORED`

- Input top-level fields are allowlisted. All must be populated and reviewed.
- Reference CSV is encrypted; plaintext is not written during seal.
- Both plaintext commitment and ciphertext hash are retained in metadata.
- Missing/null draft fields prevent criteria freeze. Three mesh levels required.
- Start requires a verified preregistration commit and isolation attestations.
- Prediction requires all registered quantities/stations and fourteen hashed
  evidence roles. Missing points, non-finite values and duplicate points reject.
- Unseal requires a verified prediction commit, unchanged artifacts, correct key,
  and explicit reference-redistribution clearance before writing plaintext.
- No incomplete coverage, hidden curve regions, post-unseal interpolation, or
  uncertainty-based threshold widening. Absolute RMSE and max error decide each
  registered quantity. Relative error is undefined at zero; uncertainty overlap
  is descriptive and missing uncertainty remains unknown.
- PASS/FAIL/MIXED are supported. Failed/unknown numerical status forces overall
  FAIL even when the experimental comparison happens to pass.
- Corrections must use a new directory/version, not overwrite frozen artifacts.

## Commands (custodian environment only)

Python 3.10+ and cryptography required; report renderer additionally uses NumPy,
Matplotlib and a LaTeX compiler. Use existing versions and record them before a
production freeze. A seal key is 32 random bytes, generated and stored by the
custodian outside the repository and predictor mounts. Never pass key contents
through chat, command arguments, stdout or Git.

```sh
python protocol.py RUN seal --json reviewed-input.json --reference reference.csv --custody custody.json --key-file /custodian-vault/challenge01.key
python protocol.py RUN criteria --json complete-preregistration.json
# Commit input/ciphertext/custody/preregistration bytes and push the scoped files.
python protocol.py RUN anchor --commit FULL_PREREGISTRATION_COMMIT_SHA
python protocol.py RUN start --json reviewed-isolation-receipt.json
# Supervisor now runs the restricted predictor/solver using only permitted inputs.
python protocol.py RUN prediction --json complete-prediction.json
# Commit prediction and its retained evidence, then push.
python protocol.py RUN anchor --commit FULL_PREDICTION_COMMIT_SHA
python protocol.py RUN unseal --key-file /custodian-vault/challenge01.key
python protocol.py RUN compare
# Commit reference reveal and comparison; preserve original PASS/FAIL/MIXED.
python protocol.py RUN anchor --commit FULL_COMPARISON_COMMIT_SHA
python render_result.py RUN
```

Anchor checks origin/main and all previously frozen file bytes, not a supplied
timestamp alone. Run directories must be inside the appropriate repository.
Keep the key and original unreviewed source material outside all public paths.
If redistribution is disallowed, do not unseal into a public directory: revise the
publication workflow to publish permitted metrics/citations and retain protected
reference access separately. This release fails closed rather than choosing a
license policy for the operator.

Reference CSV columns: `quantity,station,value,uncertainty`. Station IDs must match
the predeclared input list exactly. A blank uncertainty means unknown, not zero.
Prediction JSON has `values` (quantity/station/value rows), `numerical_status`,
`engineering_disposition`, and `evidence_manifest` mapping each required role to
relative path + SHA-256. The required roles are listed in protocol.py.

## Acceptance criteria are NOT frozen

preregistration.draft.json is deliberately incomplete. Null fields and its DRAFT
status are blockers, not implied approvals or hard-coded fallback criteria.
Proposed solver/model choices remain subject to a clean input-only regime review.
CL/CD full matched polar series is the candidate comparison, not a promise of Cp
availability. No exact Mach/Re/AoA, threshold, source-file version or package hash
is invented. Hashing this source release does not preregister a scientific case.

## Tests and publishing

`python -m unittest discover -s . -p test_protocol.py -v`

Tests use conspicuously synthetic fixtures only. They exercise sequencing,
tamper rejection, encryption and all result statuses; they are not benchmark
measurements. The public preparation bundle contains code, template, source
selection, exposure log and protocol paper—not experimental source content.

The result renderer consumes only an anchored comparison and makes full-series
overlay/error plots and a status-dependent LaTeX report. It cannot manufacture a
missing scientific run. Compile and visually review before publication. Keep the
original frozen result even when post-unseal analysis motivates Challenge 01B.
