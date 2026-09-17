# Solid residual telemetry repair

Detected solid solver field: `e`.

The original function-object include requests the fluid enthalpy field `h` for the solid region. The solid solver declaration and log use `e`; this explains the header-only `residuals(region=solid,h)` file without implying that the solid equation was not solved.

Log-backed rows extracted: **500**.

A patched-copy plan is retained in `SOLID_TELEMETRY_PATCH.json`. The frozen source case was not modified. Future CHT cases should request the detected solid field (normally `e`) and retain the resulting residual series alongside fluid residuals.

This repairs observability for subsequent experiments; it does not retroactively make the v7 numerical gates pass.
