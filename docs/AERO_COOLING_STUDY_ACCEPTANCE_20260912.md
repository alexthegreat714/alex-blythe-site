# Aero capability study 02 — forced-convection screening

Website revision 1.3; paper revision 1.0. Completed 12 September 2026.

## Discoverability and deliverables

The Aero landing page now has a top-of-page **Read the capability papers** anchor
and two side-by-side **Capability papers** cards. Each has an actual result-chart
preview, PDF, editable study link and LaTeX/evidence download. The original flow
paper remains unchanged. The cooling screen is linked from the main workspace.

- Landing: `/software/aero/#capability-papers`
- Cooling workspace: `/software/aero/cooling/`
- Nine-page paper: `/demos/aero/cooling-study-v1/research-paper.pdf`
- Sources: `/demos/aero/cooling-study-v1/research-paper-sources.zip`
- Result and package manifests are alongside the paper.

This is a research-style technical report, not a peer-reviewed publication. The
first capability uses real OpenFOAM; the second is explicitly analytical, with
thermal CFD reserved for a higher-fidelity follow-on.

## Worked decision

Run `1212c96216c4f6eda0468997a14fc7d146ed39cf1a0aeb53`.
Water, 100 W, total flow 1 mL/s, inlet 25 C, heated length 500 mm,
available array width 12 mm, inner-wall limit 72 C, friction budget 2,000 Pa.

| Layout | Nominal wall C | Guard wall C | Guard friction Pa | Disposition |
| --- | ---: | ---: | ---: | --- |
| A: 4 x 1 mm | 55.00 | 62.59 | 6,486.79 | Pressure budget fails |
| B: 2 x 2 mm | 61.01 | 70.85 | 810.85 | All screening gates pass |
| C: 1 x 4 mm | 73.03 | 87.38 | 101.36 | Wall and outlet-development gates fail |

B minimizes nominal straight-passage fluid pumping power among passing
candidates. The energy balance gives a 23.995 K coolant rise. Adverse scenarios
are declared deterministic factors, not confidence bounds. No global optimum,
outer-solid temperature, boiling margin or hardware validation is established.

## Proof and tests

- Real public browser-to-queue-to-isolated-worker execution; no numerical responses mocked.
- Automatic six-page PDF compiled before completion; 21 automatic bundle hashes checked.
- Four radial energy resolutions: 16, 32, 64, 128 cells. Nu errors decrease from
  0.12392% to 0.00194% relative to 48/11. This is NOT a thermal CFD mesh study.
- Energy closure and independent Poiseuille/Darcy calculation checks pass.
- Seven cooling tests plus ten original study tests pass; 21 gateway tests pass.
- Real model asked for missing heated length and available width; no assumed
  dimensions entered the numerical controls. The initial response mixed in the
  separate parallel-plate workflow. Typed cooling-route context was added and
  retested. Width was clarified as a packaging envelope, not flow area.
- Browser refresh resumed the same job. Editing an input invalidated current
  proof. Desktop, 900 px and 390 px checks passed without page errors.
- Final nine-page worked paper adds three actual screenshots of this retained
  run (requirements, 3D passage view, comparison). Every page was rendered and
  visually inspected after correcting crowded logarithmic tick labels.
- The 41-artifact final bundle preserves the original automatic report under
  `original-report/` plus the appendix paper and regenerating Python source.

The initial receipt is `.qa/cooling/initial-browser/acceptance.json`. Subsequent
model/UI checks resumed that existing run, rather than spending another public
compute slot; final screenshots are in `.qa/cooling/browser/`. This does not
claim additional thermal/CFD executions or general model correctness.

## Architecture and safety

The existing broker accepts seven bounded numeric inputs at
`POST /study/cooling/runs`; `POST /study/cooling/brief` is a read-only calculation.
Both study types share persistent visitor/global budgets, a serial queue and
48-hour retention. Request IDs bind type and inputs. Cooling jobs never call
OpenFOAM. The worker remains network-free, non-root, read-only outside bounded
scratch/storage, and subject to existing resource limits. PDF compilation has
a 90-second job limit and disabled shell escape.

Sources and governing assumptions are cited in the paper. The local pre-existing
rectangular turbulent cooling helper was inspected but not substituted: this
public example intentionally uses a separate circular laminar contract.

To regenerate the screenshot edition, run `services/study/cooling_paper.py` on
the retained result with its matching browser receipt, compile `paper.tex`,
visually inspect every page, then run `scripts/package-aero-paper.py` against
the original evidence ZIP. Exact result identity and every original hash are
checked before packaging.
