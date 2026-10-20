# Candidate002 public tracker

`/software/aero/progress/` now uses the separate candidate002 aggregate snapshot.
The 17 October diagnostic JSON remains unchanged and historical.

Generate a terminal snapshot locally with:

```
python scripts/aero-candidate002-progress.py --run <private-validation-run> --training-run <private-training-run> --write
```

Review the public JSON, run the projection and browser tests, build, and publish
only the intended website changes through the existing main/GitHub Pages workflow.
No private input directories may be copied into the public tree. The exporter
independently checks custody hashes, but does not infer current machine health.

There is no unattended publisher for this stopped validation attempt. Browser
polling checks published JSON; it does not observe the private machine or restart
work. Nonterminal input deliberately exports UNKNOWN: a future live tracker must
first verify supervisor birth ticks and worker/container ownership, not just PIDs.
Do not point the old diagnostic publisher at this page or relabel its snapshot.

Training completion and response collection do not establish efficacy or promotion.
Do not publish raw errors, case IDs, prompts, predictions, host/process identities,
credentials, paths, or unreviewed claims. A future scored report needs a separately
reviewed schema and evidence; changing a completion label is insufficient.
