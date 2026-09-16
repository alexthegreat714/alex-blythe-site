# HX-02 final visible pre-run packet

**Status:** `INPUT_RECONSTRUCTION_REVIEW_ONLY`

This packet contains only information an independent analyst may see before a blind prediction. It contains no experimental result values, result plots, reported agreement, preferred design, or conclusion text. It is not authorization to run CFD.

## Engineering question

Assess thermal-hydraulic behavior of a two-stream water plate-and-shell heat exchanger using the reported dimensions and operating envelope, while preserving uncertainty and measurement-plane definitions.

## Visible geometry and operation

- circular plate-and-shell / chevron channel configuration;
- D = 0.86 m; port diameter = 0.145 m; port length = 0.65 m;
- chevron angle = 45 deg; plate thickness = 0.0008 m; pitch = 0.012 m; channel depth = 0.003 m;
- reported hydraulic diameter = 0.005 m; enlargement factor = 1.170; four plates; reported effective area = 2.619 m2;
- hot water on the plate side and cold water on the shell side;
- average test temperatures 90, 100 and 110 degC;
- hot-side volume-flow envelope 1.0-5.0 m3/h and cold-side envelope 1.5-4.7 m3/h;
- heat-flux envelope 1.5-4.0 kW/m2; steady acquisition stated as five minutes.

## Permitted analytical framing

The analyst may use energy balance, counter-current LMTD, effectiveness/NTU, Reynolds number, hydraulic diameter, friction/pressure-loss relations and appropriate Nusselt correlations, with property sources declared before use. Every value must be labeled ANALYTICAL until a valid numerical run is authorized.

## Inputs still required before scored reproduction

1. Dimensioned 3-D header/manifold and port transition topology.
2. Dimensioned pressure-tap stations and a matched pressure-drop record.
3. Exact bulk-temperature probe/mixing definition and matched thermal records.
4. Plate/shell material identity and temperature-dependent properties for CHT.
5. A custodian decision on whether printed area and hydraulic diameter are authoritative source values.

Until those items are reconciled, geometry, CFD, FEA, blind prediction, reveal and validation remain NOT AUTHORIZED. A missing input is not permission to guess.
