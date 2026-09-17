# HX-CFD-QUAL-01 — remediation v7

**Status: `FAILED_NUMERICAL_GATES`**

Remediation v7 is a separate, immutable revision. The original package and the HX-03 Rev A pre-CHT freeze were not overwritten.

## What changed

The same three-region shell/tube/solid physics was rerun on a clean high-resolution structured triplet. Each region passed `checkMesh`; fields were initialized through recorded `mapFields` interpolation from the retained v5 fine result; the cases were run with `deltaT = 1` to 800 s. The mesh-independence threshold remained **1%**.

| Level | Total cells | Heat duty (W) | Shell outlet (K) | Tube outlet (K) |
| --- | ---: | ---: | ---: | ---: |
| coarse_structured_v7 | 184,320 | 29,373.197 | 459.3282 | 440.5080 |
| medium_structured_v7 | 360,000 | 29,668.528 | 457.9589 | 441.9207 |
| fine_structured_v7 | 622,080 | 29,787.545 | 457.5076 | 442.4882 |

## Gate result

The mesh-independence gate now **passes**: the maximum adjacent-grid change is **0.9954%**, just below the frozen 1% limit. Mesh quality, run completion, hot/cold mass conservation, energy closure, region/interface checks and measurement-plane extraction also pass.

The qualification still stops at two numerical gates:

- `RESIDUAL_CONVERGENCE = NOT_ESTABLISHED` — the retained initial-residual window on the fine grid is 0.04778247, above the 1e-3 criterion.
- `MONITOR_STABILITY = NOT_ESTABLISHED` — the last-window outlet-temperature drift is 0.0608 K on the shell and 0.0644 K on the tube, above the 0.01 K criterion.

Those results are not converted into a pass by changing definitions after the run. A previous pseudo-time experiment and a partial fine-grid continuation are retained locally as rejected controls; neither is part of this public status. No experimental comparison, generic CHT qualification claim, or HX-03 Stage B authorization follows from v7.

## Next predeclared action

Run a separately identified solver-control/convergence investigation or a predeclared steady-state formulation. Preserve v5 and v7, evaluate the same gates, and only resume HX-03 Stage B if residual and monitor stability are actually established.
