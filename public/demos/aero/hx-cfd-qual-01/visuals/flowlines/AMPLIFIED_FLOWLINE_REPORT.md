# HX-CFD-QUAL-01 amplified flow-line diagnostic

This is a second visualization of the unchanged retained v7 OpenFOAM velocity
fields. It exists to make small temporal changes visible without presenting a
per-frame auto-scaled color map as a physical result.

## Method

- Streamlines are generated independently for the shell and tube regions at
  `t = 0, 200, 400, 600, 800 s`.
- At each streamline point, the retained `t=0` velocity field is sampled as a
  fixed reference.
- The displayed scalar is
  `delta_speed_pct = 100 * (|U(t)| - |U(0)|) / |U(0)|`.
- The color bar is fixed at `-10%` to `+10%` for every frame. Values outside that
  display range are clipped for color only; the VTP files retain the derived
  scalar values.
- The geometry and solver fields are not modified by this post-processing.

## Interpretation boundary

This is an amplified diagnostic view, not a new CFD result and not a claim that
the flow path changed by the color scale. The honest velocity-colored recording
and the original OpenFOAM/ParaView artifacts remain available beside it. The
qualification residual, monitor-stability, and physical-validation gates are
unchanged.

The collection `hx_cfd_qual_01_v7_flowlines_amplified.pvd` can be opened in
ParaView to inspect the time-indexed derived streamline objects and the
`delta_speed_pct` point field directly.

The browser recording `hx_cfd_qual_01_v7_flowlines_amplified_interpolated.mp4`
contains 25 frames over five seconds. It smoothly interpolates the rendered
colors between the five retained snapshots so the progression is visible at
normal playback speed. Those in-between frames are a presentation aid, not
additional solver time steps; the discrete VTP/PVD snapshots remain the
authoritative post-processing record.
