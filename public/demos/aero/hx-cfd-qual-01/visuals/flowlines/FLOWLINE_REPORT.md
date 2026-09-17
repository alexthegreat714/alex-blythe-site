# HX-CFD-QUAL-01 v7 flow-line visualization

This package is a post-processing visualization of the retained, unchanged HX-CFD-QUAL-01 v7 OpenFOAM case. It does not alter the frozen solver case and does not change the qualification disposition.

## Source and method

- Fields: shell and tube velocity `U` fields exported at 0, 200, 400, 600, and 800 s.
- Seeds: bounded planes near each fluid inlet.
- Derived object: PyVista/VTK streamlines for the shell and tube regions.
- Geometry: translucent surfaces extracted from the retained shell and tube solver meshes.

## Outputs

- `hx_cfd_qual_01_v7_flowlines.pvd`: time-indexed ParaView collection.
- `shell_flowlines_*.vtp`, `tube_flowlines_*.vtp`: streamline geometry at each retained time.
- `hx_cfd_qual_01_v7_flowlines_*.png`: rendered frames.
- `hx_cfd_qual_01_v7_flowlines.mp4` and `hx_cfd_qual_01_flowlines.gif`: five-frame recording of the actual field-derived flow lines.
- `FLOWLINE_MANIFEST.json` and `FLOWLINE_SHA256SUMS.*`: provenance and integrity records.

The animation is a genuine time sequence from one unchanged solver case, not a montage of different meshes or runs. It is visualization evidence only: residual convergence and monitor-stability gates remain open in the qualification record.
