# HX-S01-DIAG-LTOL-003 — retained-checkpoint stationarity result

**Disposition: STOP AT COARSE — preregistered monitor-stability gate failed.**  
**Run class:** post-baseline, non-blind, source-informed synthetic diagnostic.  
**Solver:** OpenFOAM Foundation v10 `chtMultiRegionFoam`; normal exit at
iteration 1600 (`End`, exit code 0).

## Why this repeat was necessary

LTOL-002 reached 1600 normally, but its inherited `purgeWrite 3` removed the
1500 and 1525 solution checkpoints before the complete 1500–1600 monitor window
could be postprocessed. Therefore the stability criterion for LTOL-002 is
**NOT EVALUABLE**, not PASS and not a solver-run failure. LTOL-003 repeats the
1100–1600 coarse continuation from the LTOL-001 checkpoint with the same mesh,
physics, boundary conditions, schemes, relaxation, linear-solver settings and
monitor definitions. Only the runtime horizon and `purgeWrite 0` output
retention setting differ; the latter retains checkpoints and does not alter
the equations.

## Frozen gates and outcome

| Gate at iteration 1600 | Observed | Threshold | Result |
|---|---:|---:|---|
| Normal solver end | `End`, exit code 0 | Normal end at 1600 | PASS |
| Maximum final equation residual | `5.8496e-9` | `<= 1e-6` | PASS |
| Maximum stream inlet/outlet mass imbalance | `0.06674%` | `<= 0.5%` | PASS |
| Hot/cold energy imbalance | `2.1811%` | `<= 5%` | PASS |
| Every adjacent 25-step monitor change, 1500–1600 | Several monitors exceed `0.5%` | `<= 0.5%` | **FAIL** |

The postprocessed state values are:

| Iteration | Hot Δp (Pa) | Cold Δp (Pa) | Hot duty (W) | Cold duty (W) |
|---:|---:|---:|---:|---:|
| 1500 | 1318.6291 | 1282.7005 | 25.6547 | 26.2422 |
| 1525 | 1318.6291 | 1306.3679 | 25.8838 | 26.4760 |
| 1550 | 1318.6291 | 1264.7514 | 26.1094 | 26.7031 |
| 1575 | 1318.6291 | 1323.2905 | 26.3303 | 26.9238 |
| 1600 | 1318.6291 | 1272.7335 | 26.5462 | 27.1381 |

Each value below is the symmetric relative change between adjacent samples.
All four intervals are required to be at most 0.5% for each monitor.

| Interval | Hot Δp | Cold Δp | Hot duty | Cold duty |
|---|---:|---:|---:|---:|
| 1500–1525 | 0.000% | **1.812%** | **0.885%** | **0.883%** |
| 1525–1550 | 0.000% | **3.186%** | **0.864%** | **0.850%** |
| 1550–1575 | 0.000% | **4.424%** | **0.839%** | **0.820%** |
| 1575–1600 | 0.000% | **3.821%** | **0.813%** | **0.790%** |

The hot-side pressure-drop monitor is unchanged in these samples, while the
cold-side pressure drop oscillates materially and both reported duties continue
to rise. Residual and conservation passes do not override those unstable
engineering monitors. No single root cause is established here.

## Decision and limits

LTOL-003 fails the preregistered coarse-grid stability gate. Per the plan, stop
here; do **not** scale these settings to medium/fine and do not relax the
threshold. The original 250-iteration three-grid baseline remains a numerical
FAIL and is unchanged. These diagnostics are not blind predictions, not
experimental comparisons, and not evidence of PCHE validation, structural
performance, design readiness, or local-model autonomy.

The complete machine-readable results and artifact hashes are in
[`HX-S01-DIAG-LTOL-003_RESULT.json`](HX-S01-DIAG-LTOL-003_RESULT.json). The
pre-run plan and preparation receipt are next to this file. The runtime case,
including every retained time directory and VTK patch export, remains at
`D:\AeroRuntime\foamagent\cases\samarmad_publication_v1\diagnostics\HX-S01-DIAG-LTOL-003\coarse_netgen`.
