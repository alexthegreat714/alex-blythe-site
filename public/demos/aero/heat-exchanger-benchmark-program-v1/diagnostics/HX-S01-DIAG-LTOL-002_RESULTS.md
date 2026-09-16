# HX-S01-DIAG-LTOL-002 — incomplete stability-window evidence

**Run disposition: SOLVER COMPLETED NORMALLY; FULL-WINDOW STABILITY GATE NOT
EVALUABLE.** The solver reached 1600 and wrote an `End` marker with exit code
0. This is not a failed solver process, but it is also not a stationarity
pass.

The frozen plan required postprocessing at iterations 1500, 1525, 1550, 1575,
and 1600. The copied case inherited `purgeWrite 3`, so only `0`, `1100`,
`1550`, `1575`, and `1600` remained after completion. The required 1500 and
1525 checkpoints were deleted before their fields could be exported. The full
five-point comparison therefore cannot be calculated from this run.

The output-capture defect was corrected in the separate LTOL-003 repeat by
setting only `purgeWrite 0` in its copied control dictionary. LTOL-002 is
preserved, not overwritten, and its incomplete evidence is reported as such.

The exact copied-case solver log is retained at
[`HX-S01-DIAG-LTOL-002_solver.log`](HX-S01-DIAG-LTOL-002_solver.log),
SHA-256 `30F5BBD78C18735C2FEC1FF9D8A40952ABB0F908124F6FEFC453166A83771EFE`.
The setup receipt documents the retained time directories, normal end, and
the `purgeWrite` reason. See
[`HX-S01-DIAG-LTOL-002_PLAN.md`](HX-S01-DIAG-LTOL-002_PLAN.md) and the
complete-window repeat result in
[`HX-S01-DIAG-LTOL-003_RESULTS.md`](HX-S01-DIAG-LTOL-003_RESULTS.md).
