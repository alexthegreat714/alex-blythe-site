# HX-CFD-QUAL-01 ParaView visualization package

This package contains derived, ParaView-compatible field snapshots for the retained HX-CFD-QUAL-01 runs and an animated plot of the retained outlet-temperature monitors. The frozen v7 solver package is unchanged.

## Open the fields

1. Download and extract the case bundle (`*_vtk.zip`).
2. Open the matching `*.pvd` file in ParaView.
3. The collection contains separate `shell`, `tube`, and `solid` datasets at the latest exported time. Select `T`, `U`, or `p_rgh` in the coloring menu; use **Glyph** on `U` for velocity vectors and **Clip/Slice** to inspect the manifolds and exchanger core.

Bundles:

- `v5_fine_vtk.zip` — original fine run, latest field time 800 s.
- `v6_fine_vtk.zip` — refined fine run, latest field time 1600 s.
- `v7_fine_vtk.zip` — retained remediation run, latest field time 800 s.
- `continuation_v1_fine_vtk.zip` — unchanged bounded continuation, latest exported field time 800 s (monitor telemetry reached 810 s).
- `solver_control_v1_coarse_vtk.zip` — isolated `nOuterCorrectors=2` control run, latest field time 100 s.

The VTK files are latest-time snapshots exported with `foamToVTK`; they are not a time-resolved 3-D animation. The `hx_cfd_qual_01_outlet_monitors.mp4` file is an inline, browser-playable recording of the retained shell/tube outlet-temperature histories across the five runs, with `hx_cfd_qual_01_outlet_monitors.gif` as a fallback. It is useful for comparing drift, but it is not a substitute for transient field data. For interactive 3-D fields, open one of the `.pvd` collections in ParaView.

## Time-indexed CFD flow lines

The `flowlines/` package is the visual that should be used when a flow-field view is needed. It was generated from the unchanged retained v7 case after exporting shell and tube `U` fields at 0, 200, 400, 600, and 800 seconds. `hx_cfd_qual_01_v7_flowlines.pvd` opens the streamline geometry as a time collection in ParaView; the accompanying MP4/GIF is a rendered five-frame recording of those actual solver fields. This is a post-processing visualization, not a new solver run and not a claim that the open residual/monitor gates passed.

The package has its own `flowlines/FLOWLINE_SHA256SUMS.txt` and JSON manifest so the rendered frames and streamline geometry can be checked independently of the broader visualization bundle.

### Amplified diagnostic view

The same package now includes `flowlines/hx_cfd_qual_01_v7_flowlines_amplified.pvd` and a browser-playable amplified recording. Its point scalar is the speed change relative to the fixed `t=0` field, with a fixed `-10%` to `+10%` color scale across every frame. This makes small changes easier to see without per-frame auto-normalization. The color range is a display choice only; the underlying velocity fields, geometry, and qualification disposition are unchanged. The method and integrity records are in `flowlines/AMPLIFIED_FLOWLINE_REPORT.md` and `flowlines/FLOWLINE_SHA256SUMS.txt`.

The source package retains `hx_cfd_qual_01_v7_flowlines_amplified_interpolated.mp4` as a diagnostic artifact, but the page now uses one combined browser recording instead of separate video players.

### Flow-entry presentation

`flowlines/hx_cfd_qual_01_v7_flow_entry.mp4` is a separate five-second teaching view. It starts with no visible streamlines and reveals the retained `t=800 s` shell/tube paths from the left-side inlets toward the outlets. The first and last frames are intentionally empty/final states; intermediate frames are an axial geometry reveal of the already-solved field. It is not a zero-initialized transient, not a new solver result, and not a qualification gate. The exact interpretation and file names are retained in `flowlines/FLOW_ENTRY_REPORT.md` and `flowlines/FLOWLINE_MANIFEST.json`.

### Combined browser recording

The page uses `flowlines/hx_cfd_qual_01_v7_flow_story.mp4` as its single video. It combines the flow-entry reveal, the retained 0/200/400/600/800 s streamline sequence, and a final retained-temperature segment colored with a fixed 435–600 K scale. The stronger thermal contrast is a display choice only; the source `T` field, geometry, and solver evidence are unchanged. Segment definitions and the interpretation boundary are retained in `flowlines/FLOW_STORY_REPORT.md`.

## What the visuals show

- `v7_residual_decomposition.png` shows equation/region residual tails. `p_rgh` is visibly dominant in both fluid regions; `Uy`/`Uz` are intermediate and `Ux`/`h` are lower.
- `v7_transverse_velocity_localization.png` shows the 95th-percentile transverse speed concentrated in the first 50 mm from each inlet and decaying through the core.

These plots support the diagnostic classification `FIELD_SPECIFIC_CONVERGENCE_FAILURE`. They do not establish physical validation or design readiness. Outlet backflow was not detected in the retained snapshots, although the configured outlet velocity boundary condition permits reverse flow.

The solid residual observability repair is documented in `solid_telemetry/` and demonstrated by the patched-copy probe in `solid_telemetry_probe/`: the solid equation is `e`, so future function-object telemetry must request `e` rather than `h`.
