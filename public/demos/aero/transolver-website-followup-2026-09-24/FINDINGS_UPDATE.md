# Transolver checkpoint provenance: primary-source update

September 24, 2026 · Website publication only

## What the public record establishes

The pinned NVIDIA DrivAerML benchmark split lists native run 1 in `train.csv`
and not in `validation.csv`. The training file has 436 rows; the validation file
has 48. The README describes a proposed 90/10 split over 484 usable cases.

That split is **not linked to the Transolver checkpoint**. Hugging Face history
dates the checkpoint upload to April 29, 2026 and the model-card addition to
April 30. The benchmark files first appear in a May 6, 2026 source commit. The
model card's matching 436/48 counts do not establish that its weights used these
later lists, and it supplies no run IDs. The checkpoint's run 1 training or
held-out status remains **NOT_ESTABLISHED**.

The full Hugging Face revision is
`96477aeb86d24c26ccf0797bca1b3851268017d0`. Earlier retained URL text missed an
`f` after `cc` and was an invalid 39-character revision. The full revision's
checkpoint LFS digest matches the retained checkpoint. Earlier frozen receipts
and archives were not edited.

The pinned model card says eight layers; the retained checkpoint arguments say
twenty. A bounded range read of the companion `checkpoint.0.501.pt` inspected
its ZIP index and `data.pkl` opcode metadata without downloading the full file
or deserializing it. That metadata includes optimizer/scheduler state and an
epoch field. No explicit source-revision or run-list terms appeared among the
decoded string operands; that bounded check does not rule out values encoded in
another form or metadata stored elsewhere.

The maintainer response in [discussion #1157](https://github.com/NVIDIA/physicsnemo/discussions/1157)
points to [arXiv:2507.10747v1](https://arxiv.org/html/2507.10747v1), which
evaluates DoMINO, X-MeshGraphNet and FIGConvNet. It provides benchmark context,
not the recipe for this Transolver checkpoint.

## Status

| Finding | Status |
| --- | --- |
| Retained checkpoint matches the full Hugging Face revision's LFS digest | **CONFIRMED** |
| Run 1 appears in the pinned NVIDIA benchmark `train.csv` | **CONFIRMED** |
| Run 1 is absent from that benchmark's `validation.csv` | **CONFIRMED** |
| The 436/48 benchmark lists produced this checkpoint | **NOT_ESTABLISHED** |
| Run 1 was used to train or held out from this checkpoint | **NOT_ESTABLISHED** |
| Exact training source commit, resolved recipe, preprocessing, target units and normalization inputs | **NOT_ESTABLISHED** |

See the [structured evidence matrix](EVIDENCE_MATRIX.json),
[source URLs and SHA-256 index](SOURCE_INDEX.json),
[custody summary](CUSTODY_SUMMARY.json), and [current website-only status](CURRENT_STATUS.json).
The [existing full report](https://alex-blythe.com/software/notes/aero-transolver-reference-audit/)
retains the execution measurements and dimensional limitations.

## Boundary and next action

The model remains **RESEARCH_ONLY**. This follow-up changed no inference,
training, CFD, production service, acceptance gate, or HX use. No NVIDIA contact,
issue, pull request, forum post, email, or other outside submission was made.

Change the recipe status only if a public checkpoint-linked training manifest
or exact versioned artifact binds the run IDs, resolved preprocessing/training
configuration and normalization inputs to this checkpoint's SHA-256. Until then,
do not infer held-out status or start another inference.
