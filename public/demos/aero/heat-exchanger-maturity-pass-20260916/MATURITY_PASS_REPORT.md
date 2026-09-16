# Heat-exchanger maturity pass — public report

## Result

The current Aero program is deliberately presented as:

**HX-01 failure discipline → HX-02 external physical truth → HX-03 engineering transfer**

HX-01 is the retained two-stream PCHE CHT study. It is a real OpenFOAM run whose conservation checks passed but whose residual, stationarity, mesh-independence, and PCHE-specific field-transfer gates did not. It remains a numerical FAIL.

HX-02 is a new blind benchmark candidate based on an open-access industrial plate-and-shell water experiment. The public packet contains the geometry, operating ranges, measurement definitions, and equations needed before a run. Experimental result values, result figures, fitted correlations, and conclusions remain withheld until a future prediction package is frozen. Structural FEA is not scored because the source does not provide independent structural truth.

HX-03 is a new synthetic, employer-independent high-temperature/high-pressure gas-recuperator transfer case. Its Stage A first-principles screen passes the declared duty and pressure-drop budgets under declared screening assumptions. Stage B adds outlet-uniformity, local-wall-temperature, and compact-manifold requirements so fidelity escalation can be justified by the engineering question rather than by solver availability.

## Current gates

| Gate | Status |
|---|---|
| HX-01 retained failure | Complete; numerical FAIL |
| HX-02 source and input packet | Candidate verified; lexical leakage audit passed; human boundary review required |
| HX-02 CFD/experimental reveal | Not run / not authorized |
| HX-03 Stage A sizing | Complete screening artifact |
| HX-03 Stage B CFD/FEA | Not run; inputs and fidelity decision remain open |
| Physical validation | Not established |
| Design readiness | Not established |

This page is evidence navigation, not a claim of employer hardware suitability, qualification, or design authority.

