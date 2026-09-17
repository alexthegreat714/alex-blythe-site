# HX-CFD-QUAL-01 — original qualification run

**Status: `FAILED_NUMERICAL_GATES`**

This is the original retained three-level OpenFOAM `chtMultiRegionFoam` fixture. It is a counterflow shell/tube/solid case with separate shell, tube and solid regions. The run completed and the regional mesh checks, hot/cold mass balances and energy accounting passed.

The qualification did not pass because the predeclared mesh-independence gate failed. The largest adjacent-grid change was **13.094%**, against the frozen **1%** limit. The fine run also retained `MONITOR_STABILITY = NOT_ESTABLISHED`. The original package therefore did not authorize HX-03 Stage B.

| Level | Total cells | Heat duty (W) | Shell outlet (K) | Tube outlet (K) |
| --- | ---: | ---: | ---: | ---: |
| coarse_structured_v5 | 2,880 | 24,160.473 | 484.4264 | 415.5727 |
| medium_structured_v5 | 23,040 | 27,799.448 | 467.0136 | 432.9799 |
| fine_structured_v5 | 77,760 | 29,073.163 | 460.7601 | 439.0728 |

The retained source record is explicit: this fixture uses constant/linear reference properties, does not establish a verified CAD-to-solver identity, and does not constitute experimental validation or design readiness.

The local canonical package is `Aero/reports/hx_cfd_qual_01`. The public copy is a status summary; the local package remains the evidence authority.
