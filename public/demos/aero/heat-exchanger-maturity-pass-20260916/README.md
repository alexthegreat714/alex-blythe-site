# Aero heat-exchanger program — maturity pass

This is the public companion to the current Aero heat-exchanger maturity pass. It preserves the evidence story rather than presenting three attractive but unqualified CFD examples:

1. **HX-01 / HX-S01 — failure discipline.** A real two-stream counterflow PCHE CHT run is retained as a numerical failure. Conservation passed, but residual, stationarity, mesh-independence, and PCHE-specific field-transfer gates did not.
2. **HX-02 — external physical truth.** Aero has selected an open-access, two-stream industrial plate-and-shell water experiment as a new blind thermal-hydraulic benchmark. The visible packet is available; experimental result data remain withheld until a future prediction package is frozen.
3. **HX-03 — engineering transfer.** A new generic high-temperature/high-pressure gas recuperator is specified. Its first-order screen is complete; a controlled requirement change is reserved to justify 3-D CHT/FEA only if the new limits make those tools decision-relevant.

Current status: **HX-02 packet ready, solver not run; HX-03 Stage A screen ready; no physical validation or design-readiness claim.**

The source candidate for HX-02 is Kim et al., “Single-Phase Heat Transfer Characteristics of Water in an Industrial Plate and Shell Heat Exchanger under High-Temperature Conditions,” *Energies* 14(20), 6688 (2021), DOI 10.3390/en14206688. See the [publisher page](https://www.mdpi.com/1996-1073/14/20/6688) for the source publication.

* [HX-02 visible pre-run packet](HX-02_PSHE_BLIND/VISIBLE_PRE_RUN_PACKET.md)
* [HX-02 blind plan](HX-02_PSHE_BLIND/BLIND_PLAN.md)
* [HX-03 transfer capstone](HX-03_TRANSFER_CAPSTONE/README.md)
* [HX-03 Stage A/B fidelity decision](HX-03_TRANSFER_CAPSTONE/FIDELITY_DECISION.md)
