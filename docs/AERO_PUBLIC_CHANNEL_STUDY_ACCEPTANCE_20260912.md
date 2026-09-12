# Aero website Rev 1.2 — public live channel study

Date: 12 September 2026. Scope: a supported preliminary pressure-loss workflow,
not arbitrary public CAD/CFD execution or physical-device validation.

## What changed

1. A fixed parallel-plate study supports editable inputs, independent numerical
   execution and an actual gap-selection decision.
2. The public workspace has a downloadable study brief, rendered equations,
   rotatable geometry, distinct structured mesh display, solver progress,
   computed pressure/velocity fields and a report at the end.
3. A network-free Linux worker runs nine OpenFOAM solves after an explicit Start
   click. The broker accepts bounded numbers only; no VM access is granted.
4. Evidence labels separate analytical estimates, planned/generated mesh,
   computed fields, numerical checks and omitted physical effects.
5. The worked comparison selects a channel gap rather than merely presenting a
   converged field. The retained report and full cases support reproduction.
6. Landing-page positioning now offers **Run a worked example**, **Build your
   study**, and **Private evaluation**, with deliverables and a real result.

## Numerical acceptance

Three real studies passed all numerical checks, totaling 27 OpenFOAM solves.

| Study | L mm | Nominal gap mm | Q mL/s | Budget Pa | Duration | Outcome |
|---|---:|---:|---:|---:|---:|---|
| Default | 200 | 2 | 20 | 70 | 15.81 s | 2 mm selected |
| Minimum inputs | 100 | 1 | 1 | 1 | 15.47 s | None meets budget |
| Maximum inputs | 500 | 3 | 40 | 1000 | 33.95 s | 2.25 mm selected |

The minimum-input test deliberately exercises “numerically correct but no
acceptable candidate,” not an invented successful recommendation.

Default comparison:

| Gap mm | Analytical Pa | CFD Pa | Budget margin including numerical allowance |
|---|---:|---:|---:|
| 1.5 | 142.64889 | 142.37082 | −72.64889 Pa |
| 2.0 | 60.18000 | 60.06269 | +9.82000 Pa |
| 2.5 | 30.81216 | 30.75210 | +39.18784 Pa |

Every study ZIP contained 182 hashed artifacts; all hashes matched. Criteria,
pressure definition, physical assumptions and provenance are in the report.

- [Worked report](../public/demos/aero/channel-study-v1/report.html)
- [All min/default/max receipts](../public/demos/aero/channel-study-v1/acceptance.json)
- [Machine-readable worked result](../public/demos/aero/channel-study-v1/result.json)
- [Full cases, fields and logs](../public/demos/aero/channel-study-v1/evidence.zip)

## Browser and model acceptance

Headless Chrome (no native desktop takeover) exercised staged static assets with
real public HTTPS model and solver endpoints. Run
`28099ed97bf3ef7c46fc4928e1be70b5b85d452856a050df` completed all nine solves in
15.61 seconds and selected 2 mm. Passed:

- Input confirmation, brief download, KaTeX math, distinct geometry/mesh stages.
- Explicit Start, actual progress, reload during the run resumes the same ID.
- Computed field switching, report download and embedded proof rendering.
- Result and conversation persistence; changing inputs invalidates current proof
  and retains a historical report link rather than presenting stale results.
- 1440 px, 900 px and 390 px layouts without horizontal page overflow.
- Existing generic workspace regression suite (dark/light, saved state,
  malformed model output, failed requests, unconfirmed fields, HTML/TeX guards).
- No uncaught browser JavaScript exceptions.

The initial live model explanation was **wrong** about gap scaling and exposed
an internal formula identifier. This was not accepted as a successful teaching
test. The server now supplies the independently calculated brief to inference,
normalizes internal identifiers and withholds the observed inverse-trend
contradictions. A real retest correctly explained inverse-cubic gap scaling.
Chat receives completed evidence from the server, not a browser-supplied result.
It cannot change the controls or authorize a solve. The narrow contradiction
guard does not establish general model correctness.

## Automated and operational checks

- 18 conversation tests: trust boundaries, reviewed formulas, result context,
  observed contradiction regression, first-turn quantities and quotas.
- 8 study tests: input bounds/injection, exact reference scaling, discrete inlet
  flux, idempotency, IP/global/queue limits, offline refusal, injected timeout
  cleanup and interrupted-run recovery preserving queued/completed jobs.
- Solver sequence has fixed commands, time/memory/CPU/storage caps; no network.
- Status distinguishes queued/running/complete/failed/offline/stalled. Evidence
  expiry or integrity failure cannot be relabelled a completed fresh result.
- Private authentication and VM routes remain separate. No Fluent, Windows app,
  private image or GB10 dependency was added to the study worker.

The retained three-study report records the worker source at execution time.
Subsequent recovery/UI hardening does not rewrite that historical provenance.
The final published browser smoke receipt is recorded separately below after
deployment, so staged testing is not confused with testing published assets.

## Published-site changed-input proof

GitHub Pages deployment `34715909837` completed successfully for application
commit `732e779`. With **no staged-asset interception**, headless Chrome loaded
the public website and used its real model and solver services. Flow was changed
to **25 mL/s** and budget to **40 Pa**. Run
`c285c4d248f1f2f8dc00ae43e01fae051e29f2c0f136250a` passed all nine solves in
**16.12 seconds** on the final self-contained Linux runtime.

| Gap mm | Fresh CFD pressure drop Pa | Budget outcome |
|---|---:|---|
| 1.5 | 177.96353 | Exceeds |
| 2.0 | 75.07837 | Exceeds |
| 2.5 | 38.44013 | Meets; selected |

The selected gap changed from 2 mm to **2.5 mm**, and nominal pressure rose by
the expected factor 1.25. The model correctly explained inverse-cubic gap
scaling before the run and the new 2.5 mm decision afterward. Refresh recovery,
field switching, proof rendering, downloads, changed-input invalidation and
responsive layouts all passed again, with no JavaScript exceptions.

- [Published browser receipt](../public/demos/aero/channel-study-v1/public-browser-acceptance.json)
- [Changed-input proof report](../public/demos/aero/channel-study-v1/changed-inputs-report.html)
- [Changed-input fields and metrics](../public/demos/aero/channel-study-v1/changed-inputs-result.json)
- [Changed-input evidence archive](../public/demos/aero/channel-study-v1/changed-inputs-evidence.zip)
- [Public rejection and isolation checks](../public/demos/aero/channel-study-v1/isolation-acceptance.json)

All 182 changed-input archive hashes matched; the downloaded result/report
matched the archived copies. Five private/arbitrary public routes returned 404,
two malformed numerical requests returned 400, and a disallowed origin returned
403. Container inspection confirmed the configured isolation and resource caps.
Explicit browser failure fixtures (not real solver results) passed quota-message
preservation, idempotent retry, offline red bars, input locking, expiry failure
and new UUID after a terminal failure.

After acceptance, only the six known maintainer test IDs were removed from quota
bookkeeping. Their evidence was preserved, public limits were unchanged, and no
visitor run was touched. This leaves capacity available for the owner's first use.

## Supported claim

**Aero provides a live, reproducible preliminary parallel-plate sizing study with
an analytical reference and numerical quality checks.** This checks a defined
mathematical model. It does not verify a manufactured channel, include sidewall
or fitting losses, certify flight hardware, or demonstrate arbitrary CAD import.
Expansion should add another explicitly bounded and validated problem class,
not remove these distinctions.

For deployment, capacity, recovery and test commands see
[the study runbook](../services/study/README.md).
