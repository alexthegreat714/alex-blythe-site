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

The old terminal-only projector and attempt-2 JSON are preserved as history.
Current attempt 4 uses `aero-candidate002-live.py`, a separate allowlist projector.
Its private bridge is outside this public repository and verifies the frozen
contract, supervisor birth/argv/owner, worker/container identity and actual argv,
local actor births, fresh admitted authority heartbeat and worker gate, GPU
ownership and newline-complete output counts. It never parses response text.
Model initialization without an output journal means unknown, not zero. Earlier
attempts and the model-free probe do not contribute to current saved outputs.

An owner-requested local heartbeat observes and publishes only this aggregate
JSON every 15 minutes while the desktop observer is available. GitHub Pages
deployment adds delay. Browser polling checks published JSON every 30 seconds;
it does not observe the private machine, call a model or restart work. Active
observations become stale after 20 minutes, even if no refresh succeeds. Failed
identity observation exports UNKNOWN; failed browser fetch preserves the prior
counts while explicitly withholding a current-execution claim. JavaScript-free
rendering is explicitly a build-time snapshot, not current telemetry.

The private publisher refuses unrelated staged/dirty files, wrong repo/branch,
advanced remote history and concurrent publication. It never force-pushes.
Deployment must be verified separately from a successful Git push. Terminal
counts do not set closure flags: process/log closure, GPU clearance, Ollama health,
exact reservation release and independent artifact custody verification remain
required before a separately reviewed finalization publication and watcher removal.
Do not point the old diagnostic publisher at this page or relabel its snapshot.

Training completion and response collection do not establish efficacy or promotion.
Do not publish raw errors, case IDs, prompts, predictions, host/process identities,
credentials, paths, or unreviewed claims. A future scored report needs a separately
reviewed schema and evidence; changing a completion label is insufficient.
