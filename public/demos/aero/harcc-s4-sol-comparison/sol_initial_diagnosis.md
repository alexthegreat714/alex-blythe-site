## OBSERVED FAILURE

The v5 run completed to its declared end label, `Time = 5000s`, and emitted the solver marker `End`. It did **not** satisfy the frozen residual criteria.

At time 5000:

| Field | Initial residual | Frozen threshold | Status |
|---|---:|---:|---|
| Ux | 9.23×10⁻⁵ | 1×10⁻⁵ | FAIL |
| Uy | 1.07×10⁻⁴ | 1×10⁻⁵ | FAIL |
| Uz | 1.15×10⁻⁴ | 1×10⁻⁵ | FAIL |
| h | 6.73×10⁻⁵ | 1×10⁻⁵ | FAIL |
| e | 1.82×10⁻⁴ | 1×10⁻⁶ | FAIL |
| p_rgh | 3.87×10⁻⁵ | 1×10⁻⁴ | PASS |
| k | 4.80×10⁻⁵ | 1×10⁻⁴ | PASS |
| omega | 3.77×10⁻⁶ | 1×10⁻⁴ | PASS |

These are equation initial residuals, not the much smaller final linear-solver residuals.

Run completion and numerical convergence are therefore separate:

- Solver end marker: observed.
- Process exit result: not retained or otherwise verified.
- Residual convergence: FAIL.
- Design readiness: NOT_ESTABLISHED.

## IMPORTANT EVIDENCE

- `attempts/v5/solver_v5.log`, time 5000:
  - Solid `e` initial residual: `0.00018234749`.
  - `Ux`, `Uy`, `Uz`: `9.2288626e-05`, `0.00010684136`, `0.00011485148`.
  - `h`: `6.7264055e-05`.
  - `p_rgh`: `3.8669461e-05`.
  - `omega`: `3.7717048e-06`.
  - `k`: `4.7960261e-05`.
  - Solid temperature range: 360.34–538.77 K.
  - Fluid temperature range: 139.8–505.07 K.
  - End marker: `End`.
- `v5_case/system/fluid/fvSolution`, `residualControl`:
  - `p_rgh 1e-4`, `U 1e-5`, `h 1e-5`, `k 1e-4`, `omega 1e-4`.
  - One outer corrector; two pressure correctors.
- `v5_case/system/solid/fvSolution`, `residualControl`:
  - `e 1e-6`.
- `v5_case/system/controlDict`:
  - Steady calculation represented by `deltaT 1`, `adjustTimeStep no`, `endTime 5000`.
  - Only retained function-object diagnostic is `yPlus`.
- `v5_case/postProcessing/fluid/yPlus/1260/yPlus.dat`, time 5000:
  - Minimum 36.22, maximum 289.78, average 100.62.
- `attempts/v4/solver_v4.log`:
  - Fatal termination at label 1277 because `Hs` temperature coordinate reached 400.036 K outside the former 120–400 K table.
- `attempts/v5/methane_HEOS_property_table.csv`:
  - Retained table spans pressures 5–12 MPa and temperatures 120–600 K.
- `v5_case/0/fluid/U`:
  - Prescribed inlet mass flow `0.0113 kg/s`.
- `v5_case/0/fluid/T`:
  - Prescribed inlet temperature `139.8 K`.
- `v5_case/constant/fluid/pRef`:
  - Reference pressure `7.86 MPa`.
- `v5_case/constant/fluid/momentumTransport`:
  - RAS `kOmegaSST`.
- `v5_case/constant/solid/physicalProperties`:
  - Solid conductivity `350 W/(m K)`.
- Retained mesh headers:
  - Fluid: 11,520 cells.
  - Solid: 58,880 cells.
  - Combined: 70,400 cells.

## KNOWN FACTS

1. The prescribed inlet mass flow, inlet temperature, outlet/reference pressure, SST model, and solid conductivity correspond to source-method inputs.
2. v5 avoided the earlier 400 K property-table limit by using a table extending to 600 K.
3. Thermal fields were still changing substantially:
   - Solid maximum temperature: 431.18 K at 1261, 461.59 K at 2000, 492.13 K at 3000, 516.96 K at 4000, 538.77 K at 5000.
   - Fluid maximum temperature: 399.12, 428.79, 458.84, 483.42, and 505.07 K at the same labels.
4. Solid-energy residual decreased from 3.26×10⁻⁴ at 1261 to 1.82×10⁻⁴ at 5000, but remained approximately 182 times its threshold.
5. Enthalpy residual decreased only from 8.43×10⁻⁵ to 6.73×10⁻⁵ and remained about 6.7 times its threshold.
6. Velocity residuals improved greatly, especially Uy, but all components remained above threshold at 5000.
7. The final y+ distribution is nowhere near the source’s approximate y+≈1 target.

## UNKNOWN/UNVERIFIED ITEMS

- Actual process exit code.
- Global energy balance: NOT_ESTABLISHED.
- Measured inlet/outlet mass flows and mismatch: NOT_ESTABLISHED. A prescribed inlet value and continuity residuals are not an inlet/outlet balance.
- Monitor stability: no declared acceptance threshold and no retained engineering monitor histories beyond solver quantities and y+.
- Mesh-quality report: NOT_EVALUATED.
- Mesh independence: NOT_ESTABLISHED; only one v5 grid is available.
- Exact first-cell height and wall-normal refinement distribution.
- Suitability of the wall functions for the observed y+ distribution: NOT_ESTABLISHED because no frozen suitability criterion exists.
- Roughness implementation in the v5 case.
- Eligible experimental result comparison: NOT_EVALUATED.
- Measured outlet temperature, inlet pressure, pressure drop, or wall-temperature data.
- Whether the reconstructed geometry accurately represents the manufactured lower-corner radius, electrodeposition, 90-degree inlet turn, and half-channel source model.
- Validation and model fidelity. Neither follows from solver completion or residual convergence.

## REFERENCE-METHODOLOGY OBSERVATIONS

The methodology extract reports:

- Structured hexahedral meshes refined toward walls.
- An approximate y+ target of 1.
- SST-family turbulence modeling.
- A half-channel symmetry model with a 90-degree inlet turn.
- Measured mass flow and inlet temperature, with measured outlet static pressure.
- Real-gas property tables.
- Polished-wall equivalent sand roughness of approximately 1.1 μm.
- Copper-alloy conductivity of 350 W/(m·K).
- Calorimetric and inverse-method heat-flux alternatives.

The source methodology does not supply an eligible validation target in this evidence packet. Its setup values cannot establish agreement with experiment.

## RANKED CASE-SPECIFIC HYPOTHESES

### 1. The v5 run stopped during a slow, continuing thermal transient in iteration space

**Support**

- Solid and fluid maximum temperatures rose monotonically through the retained checkpoints, including increases of about 21.9 K and 21.6 K respectively between 4000 and 5000.
- Solid `e` and fluid `h` residuals declined slowly but remained above threshold.
- No thermal plateau is evident at 5000.
- Velocity residuals changed as the evolving density and temperature fields continued to alter the flow.

**Contradiction**

- Some fields already meet their thresholds.
- Slow residual reduction alone does not prove eventual convergence; a residual floor or non-steady solution remains possible.

**Missing evidence**

- Heat-rate, outlet-temperature, pressure-drop, and wall-temperature monitor histories.
- A predeclared trend/plateau criterion.

**Discriminating test**

Restart from the preserved v5 state with **all physical and numerical settings unchanged** and run a fixed 200 additional iterations solely as a diagnostic. This is not permission to redefine `endTime` as an acceptance criterion.

Freeze before execution:

- Record `e`, `h`, all U components, maximum solid/fluid temperature, outlet bulk temperature, and inlet/outlet mass flow every 20 iterations.
- Compare the 4800–5000 and 5000–5200 slopes.
- Do not alter thresholds.

**Prediction if correct**

Temperatures and outlet quantities will retain a consistent directional slope, while `e` and `h` continue systematic decay rather than fluctuating around stationary levels.

**Prediction if wrong**

Thermal quantities will plateau or oscillate without meaningful drift, while failed residuals remain at approximately fixed levels.

### 2. One outer fluid-solid coupling corrector is producing a segregated-coupling residual floor

**Support**

- `system/fvSolution` declares only one outer corrector.
- Thermal coupling is strong: the final fluid and solid maxima exceed 500 K while the inlet is 139.8 K.
- Individual linear equations reach small final residuals, yet their next-iteration initial residuals remain above the global criteria. That pattern is consistent with inter-equation or inter-region coupling error dominating individual linear-solver error.
- Pressure repeatedly reaches its `maxIter 100` on the first correction near the end, although its initial residual passes the frozen global threshold.

**Contradiction**

- Residuals and temperatures still exhibit secular trends, which may be explained entirely by Hypothesis 1.
- No controlled outer-corrector comparison exists.

**Missing evidence**

- Interface heat imbalance by iteration.
- Outer-corrector residual histories.

**Discriminating test**

Only after the unchanged continuation test, compare two preserved-state branches over the same fixed 100 iterations: control with one outer corrector versus treatment with two. Change no other setting.

**Prediction if correct**

Two outer correctors will cause a prompt, repeatable reduction in `e`, `h`, and U initial residuals per iteration and reduce fluid-solid interface imbalance relative to the control.

**Prediction if wrong**

Both branches will show comparable physical-monitor slopes and residual decay when normalized by work; the added corrector will mainly increase cost.

### 3. The wall mesh and wall treatment are inconsistent with the source-method near-wall approach

**Support**

- Final interface y+ is 36–290, average about 101.
- The source method reports wall-refined structured grids targeting approximately y+=1.
- The case uses `omegaWallFunction` and `kqRWallFunction`, whereas the source-method comparison requires resolving or otherwise consistently treating the near-wall region.
- Heat transfer is central to this conjugate problem, making near-wall treatment potentially influential.

**Contradiction**

- High y+ does not by itself cause residual nonconvergence.
- No frozen wall-resolution acceptance criterion exists.
- The current wall functions may be numerically intended for a wall-modeled regime, although suitability is unverified.

**Missing evidence**

- First-cell spacing, growth ratio, roughness boundary condition, mesh-quality report, and a wall-normal refinement comparison.

**Discriminating test**

Perform one predeclared wall-normal refinement study that targets approximately y+=1 while keeping geometry, boundary conditions, properties, turbulence family, and convergence thresholds unchanged. This must be treated as a separate grid, not as a repair that validates the baseline.

**Prediction if correct**

The refined grid will produce y+ near the source target and materially alter wall heat transfer, wall/fluid temperatures, or pressure drop beyond the predeclared comparison tolerance.

**Prediction if wrong**

The refined grid will change y+ substantially but leave the engineering observables within the predeclared comparison tolerance.

### 4. The expanded property table removed a crash condition but may only postpone another range failure

**Support**

- v4 failed immediately after the fluid reached 400.036 K, just outside its property-table temperature range.
- v5 reached a fluid maximum of 505.07 K and a solid maximum of 538.77 K while still heating.
- The v5 methane table ends at 600 K.

**Contradiction**

- Fluid temperature remained roughly 95 K below the retained table maximum at 5000.
- No v5 out-of-range error occurred.
- Solid temperature is not itself the methane-table lookup coordinate.

**Missing evidence**

- Predicted terminal fluid temperature and local pressure-temperature trajectory.
- Independent verification of table accuracy throughout 5–12 MPa and 120–600 K.

**Discriminating test**

Before any longer production run, predeclare a range-margin diagnostic: continue the unchanged case for the fixed 200-iteration test and track maximum fluid temperature and its slope against the 600 K boundary.

**Prediction if correct**

Maximum fluid temperature will continue rising at a rate indicating loss of adequate table margin before a steady state is reached.

**Prediction if wrong**

The temperature slope will decay with substantial margin remaining below 600 K.

## RECOMMENDED FIRST EXPERIMENT

Run the **unchanged 200-iteration continuation from the preserved v5 state**, with frozen monitor outputs and predictions as specified under Hypothesis 1.

This has the highest information value because it:

- Changes no model, boundary condition, material property, mesh, relaxation factor, or acceptance threshold.
- Directly distinguishes unfinished secular thermal evolution from a stationary residual floor.
- Establishes whether a subsequent outer-corrector experiment is justified.
- Quantifies property-table margin without changing the table.
- Preserves v5 as a failed baseline.
- Is substantially smaller than a mesh-refinement study.

Stop after the fixed 200 iterations. Do not continue merely because a residual appears close to passing. Interpret the result against the frozen slope predictions; retain the run regardless of outcome.

## CONFIDENCE AND UNCERTAINTY

- **High confidence:** v5 completed its declared iteration range but failed the frozen residual criteria.
- **High confidence:** the retained thermal fields had not reached an evident stationary plateau by 5000.
- **High confidence:** wall resolution differs strongly from the source’s approximate y+≈1 method.
- **Moderate confidence:** incomplete thermal settling is the dominant immediate explanation.
- **Low-to-moderate confidence:** one outer corrector is independently limiting convergence; a controlled comparison is required.
- **Low confidence:** the evidence supports any validation, design-readiness, or physical-accuracy conclusion.

The evidence supports a ranked diagnosis and a controlled first experiment, but it does not yet support a unique root cause.