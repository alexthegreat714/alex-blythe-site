# HX-CFD-QUAL-01 V2.1: completed acceptance repair and failure triage (R2)

Alex Blythe | September 21, 2026 | Retained evidence only; no new CFD

## Disposition

The evaluator repair and retained-evidence investigation are complete. **The CFD problem is not resolved or qualified.** Historical V2/V2.1 results remain failed, mesh comparison remains NOT_EVALUATED, and HX-03/HX-04 remain blocked. This report supersedes the interpretation in the first September 21 correction audit, not its historical files.

## What was supposed to be done — and what is now done

| Work | Completed evidence |
|---|---|
| Acceptance evaluator | Fail-closed required-field/monitor/gate evaluation, explicit equivalent-settled-state prerequisite and actual mesh observables; 40 behavior tests pass. |
| Retained mass/monitor audit | All grids, 600–800 s; continuation, 800–1000 s; native phi cross-checks and separate instantaneous/mean metrics. |
| Spatial evidence | 36 exact point/connectivity/type comparisons; no index truncation; predefined inlet-oriented masks and cellwise flux-defect localization. |
| Energy/interface recovery | Native sum(phi*h), model-based solid storage, two-sided conductive heat rates and matched interface temperatures. |
| Output repair | Discover native h/e from properties, generate writeObjects include, verify 900/1000 custody, require property-symlink dereferencing. |
| Custody/public record | New R2 package, fresh before/after source hashes, genuine missing/mismatch verification, dated report and current website navigation. |

## Coarse cold mass: a real retained imbalance, with a precision caveat

Native face sums independently establish these values against the unchanged 1e-6 limit:

| Time | Inlet kg/s | Outlet kg/s | Normalized imbalance | Comparison |
|---|---:|---:|---:|---|
| 600 | -0.05 | 0.0500000795989 | 1.5919749e-06 | FAIL |
| 700 | -0.05 | 0.0500000415984 | 8.3196797e-07 | PASS |
| 800 | -0.05 | 0.0500000335644 | 6.712874e-07 | PASS |

The historical 600–800 s printed-monitor mean is 1.03809416e-06. Its excess above the limit is small relative to printed-flux rounding; only three exact native checkpoints are retained. This does not erase the historical FAIL. The 600 s native failure rules out an extraction-only explanation.
At 800 s, 80.89% of the integrated absolute cell flux defect lies in the geometry-defined inlet 50 mm region. Cellwise signed sums agree with boundary sums to floating-point roundoff. This localizes a numerical imbalance; it does not prove a pressure-control cause or physical unsteadiness.

## Fine monitors improve, but mass averaging hides alternating errors

Original shell/tube temperature spans: 0.0109 / 0.0131 K, both above 0.01 K. Continuation spans over the complete 800–1000 s window: 0.002803965 / 0.001039865 K. Duty and pressure-drop ranges are also below their frozen 1% comparison limits. This supports thermal-monitor settling only.
The continuation cold mass ratio of signed means is 2.29483623e-07, while the maximum instantaneous imbalance is 3.7172728e-06. At 1000 s, the native imbalance is 1.45404114e-07 kg/s. The signed error alternates. The frozen contract omitted temporal aggregation; this audit reports both definitions and does not choose the favorable one.

## Global/local stationarity: recovered, not silently passed

| Interval | Tube U global normalized RMS | Inlet-oriented local RMS |
|---|---:|---:|
| 800-900 s | 0.001344837 | 0.001620536 |
| 900-1000 s | 0.000761637 | 0.000900963 |
| 800-1000 s | 0.001853264 | 0.002146532 |

The full 200 s tube U change exceeds 0.001; the smaller last-100-s change cannot replace that window. Original 600–800 s tube U changes are 0.002053 (coarse), 0.002343 (medium), and 0.007226 (fine), also above that comparison level. These are sparse endpoint differences, not proof of every intervening timestep.
The historical x≤0.05 m mask included approximately 98.65% of exported tube cells. The new exploratory masks follow the real z-axis and inlet identity: shell z≥0.1199952 m; tube z≤0.049999999 m. They were declared before their difference metrics were calculated and cannot retroactively replace the historical mask. Exported-cell RMS and native volume-weighted RMS are labeled separately.

## Energy: the evidence was available

Foundation 10 surfaceFieldValue average with weightField phi is sum(phi*h)/sum(phi), not an unweighted average. The retained monitors therefore support boundary enthalpy rates. Independent native face integration at 900/1000 s checks that interpretation.
For 800–1000 s, mean outward hot/cold enthalpy rates are -8921.452971 / 8922.107475 W. Solid storage is 0.028960 W. The declared solid-storage closure is 0.683464 W, or 0.007660% of duty, below the unchanged 1% comparison limit.
Solid energy difference is recoverable from native T with the exact constant-Cv model and verified identical meshes. Missing native h/e files at 800 s remain missing; none were fabricated. Fluid storage reconstructed from T is separately labeled thermodynamic-model evidence: retained h/T/p differ by at most about 7.4e-8 K in equivalent temperature. The 900–1000 s native solved-energy storage calculation is also retained. Boundary rates use 10 s trapezoidal sampling. This is not a claim that all mechanical-energy terms or historical custody gates passed.

## Interfaces: heat balance is observable; temperature tolerance is unspecified

| 1000 s interface | Fluid outward W | Solid outward W | Relative heat imbalance | Maximum T jump K |
|---|---:|---:|---:|---:|
| shell | 8922.182002 | -8922.141374 | 4.5536156e-06 | 0.02239145 |
| tube | -8921.246473 | 8922.085304 | 9.40172966e-05 | 0.02145357 |

Heat rates use retained mixed-boundary coefficients and native OpenFOAM geometry, q_out=−kappa*snGrad(T)*area. Face matching is bijective with maximum centroid discrepancy below 1.4e-16 m. The geometry kernel is also tested on an analytic unit cube. Both integrated heat imbalances are below 1%. Interface temperatures are not identical; the historical contract gave no numerical temperature-continuity tolerance. No convenient tolerance was invented after inspecting those jumps.

## Property and output-contract repairs

The actual fluid model solves sensible enthalpy h; solid solves internal energy e. The telemetry label e refers to thermo.he() for fluids. The new adapter derives native names from properties instead of assuming e everywhere. It generates an observation-only writeObjects include; it was not applied to a case. Required native fields at 900 and 1000 s are present.
The omitted tube property file is a Linux symlink to shell properties; the recovered target hash matches. The native copy contract now requires dereferencing and hashing targets. Original missing fields are not relabeled as retained.
With zero gravity, p and p_rgh coincide here. The outlet reference is zero and internal values include negatives. rhoConst contributes p/rho to enthalpy; pressure is not simply irrelevant. No independently declared absolute-pressure datum or physical property-validity coverage was recovered. PROPERTY_VALIDITY remains NOT_ESTABLISHED; no invented atmospheric offset.

## Integrity and reproducibility

518 local source artifacts were hashed before and after R2 and remain identical. Frozen Core/profile/binary identities match their declared hashes. Runtime mesh copies and native flux identities were checked before/after. The historical continuation SHA256SUMS.json has one pre-existing mismatch, CUSTODY_COPY_RECORD.json; later manifests match. This is disclosed, not repaired by overwriting history.
The R2 SHA-256 manifest covers generated analysis, recovered geometry, source references, report, tests and code. Its companion verification is computed by reopening files. The public download manifest covers only the published subset; raw solver fields remain in the local canonical packages.
Reproduction: run the versioned audit prepare → analyze → recover → report → seal workflow in a NEW revision directory. Existing prepare fails if its output directory exists. Historical in-place audit/analyzer entrypoints now reject execution. The evaluator requires an explicit new output plus verified contract/evidence hashes. No solver is launched by these audit tools.

## Exactly what remains — and the next branch

This completes the requested implementation repair, not a numerical remediation or a new qualification. Before one targeted cold-side continuity experiment, resolve and independently freeze the acceptance-contract details listed in NEXT_ACCEPTANCE_CONTRACT_REPAIR_DRAFT.json: mass temporal aggregation, absolute pressure/property coverage, interface temperature tolerance, correct inlet mask and field-history cadence. Do not immediately run another three-grid campaign or another thermal-only fine continuation.
No numerical parameter change is selected by this audit. The surviving numerical concern is cold-side flux/velocity settling, not missing interface observability. Historical FAILED_NUMERICAL_GATES remains; mesh NOT_EVALUATED; HX-03 FROZEN_AND_BLOCKED; HX-04 STAGE_B_BLOCKED.
