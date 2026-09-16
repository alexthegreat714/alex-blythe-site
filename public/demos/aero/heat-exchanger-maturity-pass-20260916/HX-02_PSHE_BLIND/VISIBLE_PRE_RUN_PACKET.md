# HX-02 visible pre-run packet

This packet contains only problem inputs an independent analyst may receive before a blind prediction freeze. It contains no measured results, fitted correlations, result plots, reported errors, author ranking, or conclusions.

## Problem

Predict pressure loss and heat-transfer response for a single-phase, counter-current industrial plate-and-shell heat exchanger with water on both sides at 90–110 °C.

## Geometry and conditions

* Circular corrugated plate cassette inside a shell; hot water flows downward on the plate side and cold water upward on the shell side.
* Plate diameter 0.86 m; port diameter 0.145 m; port-to-port length 0.65 m; chevron angle 45°; plate thickness 0.0008 m; corrugation pitch 0.012 m; corrugation depth 0.003 m; hydraulic diameter 0.005 m; enlargement factor 1.170; four plates; effective area 2.619 m².
* Hot volumetric flow range 1.0–5.0 m³/h (2.2–5.0 m³/h for heat-transfer runs); cold range 1.5–4.7 m³/h.
* Heat-flux range 1.5–4.0 kW/m²; five-minute steady acquisition definition.
* Pre-run equations: Q̇ = ṁ cp ΔT; q″ = Q̇/A; counter-current LMTD; U = Q̇/(A·LMTD); Reynolds, Nusselt, and friction-factor definitions.

The analyst must declare property source, one operating point, port/manifold idealization, corrugation reconstruction, boundary conditions, mesh levels, convergence and conservation gates, and comparison quantities before execution.

The candidate is thermal-hydraulic only. No independent structural truth package is available, so FEA is not scored for this benchmark.

