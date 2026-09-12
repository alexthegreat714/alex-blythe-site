# Aero website Rev 1.1

Public presentation release. This does not change the solver, training adapter,
private VM routes, or the scientific status of the retained case.

## Delivered

- One compact product headline; the illustrated film remains above the three
  workspace entry cards. Graphite/cyan accents, concise benefits, example links
  and a mailto pilot-discussion call to action.
- Interactive full-revolution nozzle illustration with a 6–12 mm throat-radius
  control. Constant-density continuity estimates update immediately. A changed
  radius disables recorded mesh/pressure until reset; it never launches CFD.
- A recorded mesh view sourced from the actual pressure-surface export rather
  than CAD tessellation. The one-degree wedge and boundary triangulation are
  labelled; this is not a full-annulus or full volume-topology viewer.
- Landing table, numerical/readiness gates and printable sample report derive
  from wall-refinement-v6/engineering-result.json. The old first-cut-proof
  summary remains archived, but no longer supplies the current proof link.
- Technical background, limitations and detailed evidence remain accessible
  behind disclosures. Other software project pages retain their open layout.
- Example deep links select their scenario. The two nozzle walkthroughs are
  explicitly two interpretations of one retained study; cooling is analytical.
- Public chat is explicitly labelled scripted. Unconfirmed requirement text
  no longer earns a false 100% preparation score.

## Not delivered / next boundary

Public live model chat is **not connected**. Inspection found the existing
workbench service explicitly local-only, guarded by strict local authentication.
The static site must not expose that token or proxy arbitrary private-agent
actions. A separately deployed, bounded public conversation endpoint needs a
chosen inference budget/model, abuse protection/rate limits, origin policy,
request limits and data-retention rules. It must carry no VM, solver or shell
authority. The public Current card states this limitation.

The existing film is retained as Film Rev 1.3 and explicitly labelled an
illustration, not a new live solve. Website revision and film revision are
independent. A new close-up cinematic recording and new independently solved
example cases are still future work.

## Verification

`pnpm run build`

`PLAYWRIGHT_MODULE=<installed playwright or playwright-core path> node scripts/test-aero-rev11.mjs`

The browser test checks video/card ordering, disclosure defaults, slider math,
stale-result blocking/reset, recorded mesh/pressure, table/source alignment,
sample report, example routing, scripted-chat disclosure, mobile overflow,
reduced motion, artifact SHA-256 checksums and browser JavaScript exceptions.
Screenshots are local QA artifacts in `.qa/rev11/`.

Public URLs: `/software/aero/`, `/software/aero/demo/`,
`/software/aero/report/`. Private authentication is unchanged.
