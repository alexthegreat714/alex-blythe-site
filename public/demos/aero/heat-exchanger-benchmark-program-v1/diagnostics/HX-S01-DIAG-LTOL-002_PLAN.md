# HX-S01-DIAG-LTOL-002 — extended stationarity check

**Created:** 2026-09-16 02:10 UTC  
**Class:** post-baseline, non-blind continuation  
**Parent:** HX-S01-DIAG-LTOL-001, which passed its residual/conservation checks
but failed the 25-iteration monitor-stability check  
**Scope:** coarse grid only; continue the corrected `relTol 0`, `tolerance 1e-8`
case from iteration 1,100 to a hard cap of 1,600

## Question

After algebraic linear solves are tightened, do the coarse-grid pressure-drop
and heat-duty monitors settle without changing geometry, mesh, physics,
boundary conditions, schemes, relaxation, or linear-solver settings?

This is a follow-on diagnostic after the original failed results were seen.
It is not blind, is not a replacement baseline, and cannot establish
publication validation.

## Frozen procedure

1. Copy the corrected LTOL-001 case's `0`, `1100`, `constant`, and `system`
   into a new run directory. Do not modify LTOL-001 or the original
   publication-run cases.
2. Preserve all LTOL-001 solver settings and inputs; change only copied
   `controlDict` `endTime` from `1100` to `1600`.
3. Run OpenFOAM Foundation v10 `chtMultiRegionFoam` from the copied 1,100
   checkpoint. Retain the full log, dictionaries, mesh checks, VTK patch
   fields, and mass/energy postprocessing at 1,500, 1,525, 1,550, 1,575,
   and 1,600.
4. Measure every adjacent 25-iteration change over the final 100 iterations
   for hot/cold pressure drop and hot/cold heat duty. Use the same symmetric
   relative-change definition as LTOL-001.

## Predeclared stop criteria

LTOL-002 is **coarse-grid stable enough to consider a three-grid follow-up**
only if all conditions hold:

- the solver reaches 1,600 with a normal `End` and no fatal error;
- maximum final equation-solver residual at 1,600 is `<= 1e-6`;
- independently integrated mass imbalance is `<= 0.5%` and hot/cold energy
  imbalance is `<= 5%` at 1,600;
- for each of the four engineering monitors, **every** adjacent 25-iteration
  symmetric change from 1,500 through 1,600 is `<= 0.5%`.

If any condition fails, stop at coarse and report the failure. Do not scale the
solver settings to medium/fine and do not relax the criteria. Passing only
authorizes a separately identified three-grid run; it does not establish grid
independence or experimental accuracy.

## Interpretation boundary

This check asks whether a solver configuration on one reconstructed synthetic
grid reaches a stationary operating point. It cannot validate the source
paper's correlations, the reconstructed geometry, the material assumptions,
or any design. The original baseline, both earlier same-settings diagnostics,
and LTOL-001 remain preserved regardless of outcome.
