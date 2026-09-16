# HX-S01-DIAG-LTOL-003 — checkpoint-retention repeat

**Created:** 2026-09-16 UTC  
**Class:** post-baseline, non-blind evidence-capture repeat  
**Parent:** LTOL-002 reached iteration 1600 normally, but `purgeWrite 3`
discarded checkpoints 1500 and 1525 before the preregistered final-100-step
stationarity window could be evaluated.  
**Scope:** coarse grid only; repeat the 1100→1600 continuation with every
25-step solution checkpoint retained.

## Question

With the LTOL-001 tighter linear-solver settings unchanged, do all four
engineering monitors meet the frozen stationarity threshold at every adjacent
25-step interval from iteration 1500 through 1600?

## Frozen procedure

1. Create an isolated run from the corrected LTOL-001 checkpoint at 1100,
   including only `0`, `1100`, `constant`, and `system`.
2. Preserve the mesh, geometry, physics, properties, boundary conditions,
   schemes, relaxation, solver tolerances, function objects, and all other
   settings. In the copied `controlDict`, change only `endTime` to 1600 and
   `purgeWrite` to 0. `purgeWrite 0` is solely to retain all time directories;
   it does not change the equations or numerical method.
3. Verify the copied case begins from latest time 1100; compare solver and
   region dictionaries against LTOL-001; run `checkMesh` separately for
   hotFluid, coldFluid, and solidPlate.
4. Run OpenFOAM Foundation v10 `chtMultiRegionFoam` to 1600. Retain every
   25-step checkpoint and the complete solver log.
5. Independently postprocess hot/cold pressure drop and heat duty at
   1500, 1525, 1550, 1575, and 1600 using the same script and symmetric
   relative-change definition as LTOL-001/002.

## Predeclared stop criteria

LTOL-003 is **coarse-grid stable enough to consider a separate three-grid
follow-up** only if all conditions hold:

- normal solver exit at 1600 with `End` and no fatal error;
- maximum final equation-solver residual at 1600 `<= 1e-6`;
- independently integrated mass imbalance `<= 0.5%` and energy imbalance
  `<= 5%` at 1600;
- for hot/cold pressure drop and hot/cold heat duty, every adjacent
  25-step symmetric relative change from 1500 through 1600 is `<= 0.5%`.

If any condition fails, stop at coarse. Do not scale the settings to
medium/fine and do not relax the criteria. A pass only authorizes a separately
identified three-grid follow-up; it does not establish grid independence,
publication validation, or design readiness.

## Interpretation boundary

This repeat corrects a checkpoint-retention shortfall discovered after
LTOL-002; it is not a new blind prediction or a replacement for the frozen
baseline. LTOL-002 remains preserved and will be reported as a normal solver
completion with an unevaluable full-window stability gate. All earlier runs
remain unchanged.
