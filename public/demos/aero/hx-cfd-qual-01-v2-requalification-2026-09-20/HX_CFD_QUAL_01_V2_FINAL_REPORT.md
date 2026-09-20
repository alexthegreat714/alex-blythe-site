# HX-CFD-QUAL-01 clean V2 requalification — 2026-09-20

Owner: Alex Blythe · Report date: 2026-09-20

Final disposition: **FAILED_NUMERICAL_GATES**.

This report covers fresh coarse, medium, and fine runs under the frozen V2 Core + two-fluid solid CHT profile case contract. Historical R1–R8 evidence was not grandfathered and HX-CFD was withheld from calibration.

## Frozen acceptance basis

- Acceptance criteria SHA-256: `4de11c7bc0ecbddb7f7bf9de9cf908943bc19a089f38876115494b88a54f104f`.
- Endpoint: 800 s; Δt=1 s; nOuterCorrectors=2; 20% direct outer-telemetry tail.
- Frozen thresholds were not changed: outer normalized RMS/q95 ≤0.01, 200 s monitor window, 0.01 K temperature stability, 1% duty/energy/interface limits, 1e-6 mass balance, and 1.000% mesh-independence criterion.

## Execution summary

| Grid | Solver completion | Telemetry records | Flow nonlinear | Thermal nonlinear | Field/monitor | Energy/interface |
|---|---|---:|---|---|---|---|
| coarse | PASS | 8000 | FAIL | FAIL | NOT_ESTABLISHED / NOT_ESTABLISHED | NOT_ESTABLISHED / NOT_ESTABLISHED |
| medium | PASS | 8000 | FAIL | FAIL | NOT_ESTABLISHED / NOT_ESTABLISHED | NOT_ESTABLISHED / NOT_ESTABLISHED |
| fine | PASS | 8000 | FAIL | FAIL | NOT_ESTABLISHED / NOT_ESTABLISHED | NOT_ESTABLISHED / NOT_ESTABLISHED |

## Late pressure-solver context

The direct outer-update tail is small on all three grids, but this does not waive the other gates. The last 160 s of the logs provide the following pressure-solve context:

| Grid | Shell initial mean/max | Shell final mean/max | Tube initial mean/max | Tube final mean/max |
|---|---:|---:|---:|---:|
| coarse | 0.000252771 / 0.000372951 | 1.68733e-06 / 2.7489e-06 | 0.00252343 / 0.00307542 | 1.69368e-05 / 2.98255e-05 |
| medium | 0.000336109 / 0.000512358 | 1.85254e-06 / 3.49872e-06 | 0.0025251 / 0.00312723 | 1.86252e-05 / 2.98513e-05 |
| fine | 0.000583545 / 0.000769496 | 2.7075e-06 / 4.75217e-06 | 0.00243582 / 0.00310964 | 1.5209e-05 / 2.8117e-05 |

## Interpretation

Direct outer-loop telemetry was captured, but qualification requires every per-grid evidence layer. The retained clean case package does not contain deterministic solid-storage/energy-closure and interface-flux telemetry or a local inlet-manifold stationarity probe; those gates therefore remain NOT_ESTABLISHED rather than being inferred from conservation or global fields. Mesh comparison is not allowed until all three grids satisfy the per-grid gates.

The result is consequently **FAILED_NUMERICAL_GATES** under the frozen contract. This is a fresh V2 disposition; it does not rewrite the historical R1–R8 result (including the historical 1.303% > 1.000% mesh failure). HX-03 remains FROZEN_AND_BLOCKED.

## Evidence custody

Source immutability recorded: `True`. Raw logs, direct telemetry, monitors, selected 600/700/800 s fields, and the predeclared criteria remain under `Aero/reports/hx_cfd_qual_01_v2_requalification_20260919/`.

Recommended next step: retain this failed clean requalification as evidence and version one targeted instrumentation/contract repair for the missing local-manifold and energy/interface observables before any further qualification attempt. Do not unlock HX-03.
