# Aero public channel study — v1

This is an anonymous, bounded **live OpenFOAM calculation**, separate from the
conversation model and from Aero's private VM. The public product is preliminary
channel sizing: choose the smallest of three gaps meeting a pressure-drop budget,
with a reviewable brief, analytical comparison, computed fields and evidence.

## Use it

Open `/software/aero/current/?study=channel`. Review four inputs and the model
assumptions, Prepare the study, inspect Math / CAD / Mesh, then press Start at
Solve. Results contains the decision, computed fields, **Read proof**, a portable
HTML report (print to PDF), and the full hashed OpenFOAM evidence ZIP.

Each new study now automatically compiles a research-style **LaTeX PDF paper**
before its state becomes complete. Results offers **PDF paper** and **Evidence +
LaTeX**. The paper includes an abstract, defined inputs/assumptions, equations,
design comparison, mesh/refinement and residual plots, solved-field snapshots,
velocity-profile comparison, per-grid gate table and reproducibility hashes.
Charts are generated from solver data, not model output. The ZIP retains the
`.tex`, vector/PNG figures, compile log and PDF. Compilation runs with shell
escape disabled and a timeout; failure produces a failed run, not a missing PDF
hidden behind a completed status. Allow extra time after the ninth solve for
figure generation and compilation. The standalone worked paper additionally
includes real browser screenshots matched to its exact run ID; those are
maintainer acceptance captures, not screenshots of future visitors' browsers.

Chat can explain the checked study brief and a server-fetched completed result.
It cannot submit jobs or change the four solver inputs. Model document proposals
are separate from those controls. Editing a completed study invalidates its
current result and preserves the old report under Previous runs. Refresh resumes
the same job; a repeated submission UUID does not consume another run.

## Fixed physical model

- Water at nominal 20 °C: density 998.2 kg/m³, dynamic viscosity 0.001003 Pa·s.
- Steady incompressible laminar flow between no-slip parallel plates, parabolic
  inlet, zero outlet gauge pressure. Spanwise empty boundaries; 1 mm solver slice.
- Reference width W=100 mm converts total volume flow to flow per width. This
  is **not** a finite rectangular duct with sidewall drag. No entry, bend,
  fitting, roughness, heat-transfer, cavitation or compressibility model.
- L=100–500 mm, nominal full gap h=1–3 mm, volume flow Q=1–40 mL/s,
  pressure budget=1–1000 Pa. Tested gaps: 0.75h, h, 1.25h.
- Reference: Δp=12μLQ/(Wh³), U=Q/(Wh), Re=2ρUh/μ. The supplied flow bound keeps
  Re below 800. The fully developed inlet is assumed; no entrance-length claim.
- Source: [Fitzpatrick, Flow Between Parallel Plates](https://farside.ph.utexas.edu/teaching/336L/Fluidhtml/node134.html).
- Each gap has 512 / 1152 / 2048 cells. `blockMesh`, `checkMesh`, `simpleFoam`.
- Pressure is the fitted interior gradient over x/L=0.25–0.75 multiplied by L,
  not the first-to-last-cell difference. OpenFOAM kinematic pressure is multiplied
  by density. Velocity and flux are read from final U and phi, not model text.

Every grid must pass mesh quality, solver convergence, final initial residuals
≤1e-7, flux imbalance <0.1%, pressure-reference error <2%, velocity-profile L2
error <2%. Each gap must have medium/fine pressure change <1%. Only if all checks
pass is the smallest budget-compliant gap selected. Numerical allowance is the
larger of analytical discrepancy or medium/fine difference; it is **not** a total
physical uncertainty bound or a manufacturing tolerance assessment.

## Deploy or recover

From the website repository, on a Docker host:

```sh
docker compose -f compose.aero-public-chat.yaml -f compose.aero-study.yaml up -d --build
docker compose -f compose.aero-public-chat.yaml -f compose.aero-study.yaml exec -T ollama ollama pull gemma3:12b
```

No model download is needed if already installed. The OpenFOAM runtime is copied
from a digest-pinned third-party development image during build. It needs no
private Aero image, Windows application, Fluent, WVM or GB10 endpoint. Only the
three required solver executables and runtime libraries enter the worker image.
Ollama GPU use is optional deployment infrastructure, not a solver dependency.

The existing public tunnel points to loopback Caddy port 5322; do not open that
port to the network or expose either container directly. Configure
`PUBLIC_AERO_CHAT_URL=https://aero-chat.alex-blythe.com` at static-site build time.
Origins are explicit. The edge replaces client identity with Cloudflare's
connecting address. CORS is not authentication and does not prevent bots.

```sh
curl https://aero-chat.alex-blythe.com/study/health
docker compose -f compose.aero-public-chat.yaml -f compose.aero-study.yaml ps
```

If the worker is unavailable, briefs remain editable and Start is disabled.
No progress for 90 seconds becomes a visible stalled state; a single command is
limited to 70 seconds and the solve sequence to 300 seconds. Before restarting,
inspect active run status. A restart marks interrupted jobs failed rather than
silently calling them complete; queued jobs resume and completed evidence stays.
Use only this study-worker service for recovery, not the private Aegis VM or
global Docker restart. On an interrupted run, review inputs and Start a fresh
study. Finished runs cannot silently replay themselves through the Start button.

## Capacity and security

- 2 studies per client IP / hour, 6 globally / hour, persisted in SQLite.
- One worker; at most 3 queued/running jobs; at most 24 retained studies.
- Evidence expires after 48 hours. Download to keep it. The published worked
  example is separately retained under `public/demos/aero/channel-study-v1`.
- Request accepts precisely four bounded numbers plus a UUID: 2 KB body cap.
  No prompt, path, URL, upload, executable, dictionary or command is accepted.
- Random 192-bit run capabilities: anyone with the complete link can read that
  run until expiry. Do not submit confidential data to this anonymous endpoint.
- API has no Docker socket, host mount, model or private agent tools.
- Worker: non-root, no network, read-only root, no capabilities, no-new-privileges,
  2 CPUs, 768 MiB RAM, 64 PIDs, 512 MiB scratch tmpfs, bounded output files.
- Evidence cap: 48 MiB uncompressed case files per study; logs bounded. Temporary
  case directories are removed after success/failure. Data uses a dedicated
  volume, not private files. Result/report/ZIP hashes are checked before serving.
- Public access still depends on this host, Docker and its tunnel being online;
  there is no uptime SLA or unlimited anonymous capacity promise.

## Reproduce tests

```sh
python -m unittest discover -s services/study -p test_study.py -v
python -m unittest discover -s services/conversation -p test_server.py -v
python services/study/integration.py
```

The integration runner submits three real jobs using reserved documentation IPs
inside the broker container; it does not reset or bypass the global quota. It
retains min/default/max receipts and verifies every archive hash under `.qa/`.
Expect it to consume three of six hourly run slots.

For the public browser test, set `AERO_STUDY_RUN=1`, optionally
`AERO_STUDY_CHAT=1`, then run `node scripts/test-aero-study.mjs`. This consumes a
real public run and, when requested, two real model calls. Optional
`AERO_PREVIEW_ORIGIN=http://127.0.0.1:4322` serves staged static assets on the
website origin while still calling the real public APIs; the receipt records
that distinction. Without this option it tests the published website.

The model remains fallible. One live QA answer inverted the gap trend; the
checked brief, source-owned formulas, and a narrow contradiction gate were added.
A subsequent real model call correctly explained inverse-cubic scaling. These
checks are not a general engineering reasoning certification.
