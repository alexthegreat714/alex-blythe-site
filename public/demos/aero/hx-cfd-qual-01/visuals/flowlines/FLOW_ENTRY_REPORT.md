# HX-CFD-QUAL-01 v7 flow-entry presentation

This recording answers a visual question: show the flow starting from an empty view, then entering the exchanger until the retained flow field is visible. It is derived from the unchanged retained v7 OpenFOAM result and does not rerun or alter the solver case.

## Method

- Source: shell and tube streamlines generated from the retained `t = 800 s` velocity fields.
- Geometry: translucent shell and tube solver surfaces from the same retained case.
- Reveal: 75 frames at 15 frames per second over 5 seconds. Each frame clips the streamline geometry at an axial plane that advances smoothly from the inlet toward the outlet, avoiding coarse visible jumps between volume increments. The visible streamlines carry the retained temperature field on the fixed 435-600 K turbo scale.
- Inlet convention: shell and tube inlets are shown at the left side of the rendered model.
- Outputs: `hx_cfd_qual_01_v7_flow_entry.mp4`, `hx_cfd_qual_01_flow_entry.gif`, and `hx_cfd_qual_01_v7_flow_entry_800.png`.

## Interpretation boundary

The first frame is intentionally empty and the final frame is the retained t=800 s field. Intermediate frames are a presentation aid that progressively reveals an already-solved field; they are not additional OpenFOAM time steps, not a zero-initialized transient, and not evidence of solver convergence. The actual retained time sequence remains the separate 0/200/400/600/800 s flow-line recording and ParaView collection.
