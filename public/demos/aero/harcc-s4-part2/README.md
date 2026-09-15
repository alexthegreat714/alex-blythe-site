# HARCC S4 Part II: bounded CFD failure investigation

**Study date:** 2026-09-15

**Investigator:** GPT-5.6 Luna

**Solver:** OpenFOAM Foundation 10, `chtMultiRegionFoam`

**Disposition:** the diagnostic branch is complete; CFD numerical credibility was **not established**.

This is a follow-up to the HARCC S4 methane-cooling case's frozen v5 run. It asks whether bounded changes to linear-solver and PIMPLE controls explain the residual failure. It is not a heat-exchanger validation study and does not compare a completed prediction with matched experimental truth.

## Result in one sentence

Increasing the pressure-solver iteration limit removed a real inner-solver cap but did not materially improve the coupled target residuals. A corrected two-outer-corrector continuation improved enthalpy and solid-energy residuals while worsening the final velocity residual; every target residual gate still failed, so the predeclared stop rule ended solver-control tuning without a v9 run.

## What was tested

The v5 case ended normally at pseudo-iteration 5000 on a 70,400-cell reconstructed single-pitch segment. The three target residual gates failed:

| Field | v5 final residual | Frozen limit | Result |
|---|---:|---:|---|
| Velocity `U` | 1.1485e-4 | 1e-5 | FAIL |
| Fluid enthalpy `h` | 6.7264e-5 | 1e-5 | FAIL |
| Solid internal-energy residual `e` | 1.8235e-4 | 1e-6 | FAIL |

The `p_rgh`, `k` and `omega` residuals met their listed limits. Those passes do not override the three failed target gates. The recorded inlet and outlet mass flows were nearly equal, but no mass-imbalance tolerance had been frozen, so the report does not label mass conservation PASS.

### v6: pressure linear-solver cap

Two independent branches continued from the same frozen iteration-5000 state to 5200. The treatment changed the regional `p_rgh` linear-solver `maxIter` from 100 to 300. The control hit 100 iterations in 190 of 400 pressure solves; the treatment hit its cap in none and reached as many as 106 iterations. Its mean final pressure linear residual over the last 20 steps was lower, but the coupled `U`, `h` and solid-`e` histories were essentially coincident. The residual gates remained failed. The pressure cap was a real inner-solver limit, but this test did not support it as the material cause of the coupled residual failure.

### v7: invalid implementation, retained and excluded

The intended two-outer-corrector treatment was written to a region-local dictionary rather than the global algorithm dictionary read by `chtMultiRegionFoam`. Both runtime logs therefore reported one outer corrector. This pair is **invalid for hypothesis inference**; its near-identical outcomes are not evidence for or against the intended change. The configuration mistake was identified before v8, corrected, and guarded by pre-run and runtime checks.

### v8: corrected global outer-corrector comparison

The valid paired continuation started both branches from the same v5 checkpoint and ran 200 additional pseudo-iterations. Runtime logs confirmed one global outer corrector in control and two in treatment. The branch-specific change was the global `nOuterCorrectors` value; mesh, checkpoint, physical settings, thresholds and regional solver dictionary were held constant.

| Residual at iteration 5200 | Control: 1 outer | Treatment: 2 outer | Treatment change | Gate in both |
|---|---:|---:|---:|---|
| `U` | 1.0618507e-4 | 1.0755145e-4 | +1.2868% (worse) | FAIL |
| `h` | 6.6143406e-5 | 6.5061837e-5 | -1.6352% | FAIL |
| Solid `e` | 1.7854397e-4 | 1.7479682e-4 | -2.0987% | FAIL |
| `p_rgh` | 1.1285021e-5 | 1.1034152e-5 | -2.2230% | PASS |
| `k` | 4.7785213e-5 | 9.5224623e-5 | +99.28% | PASS |
| `omega` | 3.7509783e-6 | 7.4665358e-6 | +99.06% | PASS |

The treatment doubled pressure solves (400 to 800) and took 116.4 seconds versus 69.0 seconds. Although `h` and `e` ended lower, `U` ended higher; therefore the frozen requirement for consistent improvement across all three target fields was not met. This is partial hypothesis support, not a recovery or an accuracy improvement.

The last-saved pressure drop was 73.727 kPa for control and 75.302 kPa for treatment; mean outlet temperature was 202.739 K and 203.477 K, respectively. These are differences between short restart continuations, not validated predictions.

## Engineering disposition

The investigation stopped at v8. It did not identify one unique root cause. Residual convergence remains **FAIL**. Energy closure, qualified mass conservation, mesh independence, wall-treatment suitability, agreement with a matched experiment, physical validation and design readiness remain **NOT ESTABLISHED**.

The run uses a reconstructed segment rather than complete as-built hardware or native author CAD. Interface `y+` ranged approximately 36 to 290 (mean 101), while the source methods describe a near-wall target around 1. This discrepancy merits a separate, predeclared wall-treatment study; it does not by itself explain the residual failure. The prose description of applied heat input also conflicts with the retained facewise thermal boundary field and remains unresolved.

## How blind was the investigation?

The initial diagnosis used a fresh, read-only GPT-5.6 Luna context. It received the frozen v5 evidence, the same initial investigation prompt and unchanged criteria; the publication's reported results and the retrospective Part-I report were withheld. The model had no solver or shell authority. It could see genuine v5 evidence such as `y+` and a methods-only source extract. This is **reference-withheld initial diagnosis**, not a hermetic or fully blind benchmark.

The v6, v7 and v8 reviews continued in the same Luna context and saw earlier hypotheses and outcomes. Their interpretations are sequential, not independent blind replications. The exact implementation-review prompt for v7 was not captured contemporaneously and was not reconstructed after the fact.

A separate GPT-5.6 Sol protocol was prepared but **not run**. Its purpose is an optional independent model-behavior check: Sol would receive only the original frozen v5 packet, prompt and criteria, without Luna's hypotheses or Part-II outcomes. That protocol adds no CFD evidence and is not part of this result.

## Public artifacts and reproduction boundary

The two byte-preserved v8 OpenFOAM logs are downloadable here:

- [One outer corrector: control solver log](v8-control-solver.log)
- [Two outer correctors: treatment solver log](v8-two-outer-correctors-solver.log)
- [Compact machine-readable results and artifact hashes](summary.json)

The log SHA-256 values are recorded in `summary.json`. Hashes establish artifact identity; they do not establish scientific validity. The large mesh and full field/checkpoint database are retained in the local research archive but are **not mirrored in this public release**, so the links here are not a complete turnkey rerun package. No full-text paper, figures or experimental tables are reproduced; the source is identified by [DOI 10.2322/tastj.19.96](https://doi.org/10.2322/tastj.19.96).

The original case and result remain a numerical failure. No post-run threshold changes, physical validation claims, or design-release claims are made.
