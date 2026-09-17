# HX-CFD-QUAL-01 v7 pressure / velocity diagnostic

This report is a read-only analysis of retained solver telemetry and latest-time VTK snapshots. The frozen v7 package was not modified.

## Finding

The evidence supports `FIELD_SPECIFIC_CONVERGENCE_FAILURE`. `p_rgh` remains high in both fluid regions, while Ux and h are comparatively small and the outlet temperature monitors drift rather than alternate. The unchanged continuation does not close the pressure residual gate.

## Pressure controls inspected

- Outlet `p_rgh` is `fixedValue 0` in each fluid region, providing a pressure reference; inlet, walls, and fluid-solid interfaces use `fixedFluxPressure`.
- Outlet velocity is `pressureInletOutletVelocity`, so backflow is permitted by the boundary condition. The retained shell/tube outlet snapshots show zero reverse-flow cells, so backflow is not demonstrated as the cause.
- Case-level PIMPLE uses one outer corrector. Fluid-region pressure uses GAMG (`tolerance 1e-7`, `relTol 0.01`) with `p_rgh` relaxation 0.7; U equation relaxation is 0.3.
- Retained phi/continuity telemetry is present, but non-zero continuity values mean flux consistency is observed rather than qualified closed.

## Where transverse residual contributions originate

The VTK field audit places the largest transverse-speed q95 in the first 50 mm from each respective inlet, then shows decay through the exchanger core. This is an inlet/manifold development signature. It is not evidence of a distributed transverse failure or resolved recirculation throughout the core. See `v7_transverse_velocity_localization.png` and the VTK snapshots in the visualization package.

## Solid telemetry repair

The old function object requested `residuals(region = solid, h)`, but `system/solid/fvSolution` and the solver log show `e`. That mismatch explains the header-only solid residual file. `repair_openfoam_solid_telemetry.py` now detects the solved field and emits a patched-copy plan. A bounded patched-copy probe recorded numeric `e` residuals for 11 time levels (800–811 s) without modifying v7.

## Steady-model suitability

`NOT_ESTABLISHED`. The run is not numerically converged, but this does not prove intrinsic unsteadiness. A transient comparison would be a separate, explicitly identified study after pressure/flux controls are remediated.

## Disposition

This diagnostic clarifies the failure and repairs future observability. It does not convert the v7 result into a passing qualification case and does not establish design readiness.

Artifacts: `PRESSURE_VELOCITY_DIAGNOSTIC.json`, `v7_transverse_velocity_localization.png`, `solid_telemetry/`, and the ParaView visualization package.
