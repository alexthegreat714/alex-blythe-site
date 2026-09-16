# HX-S02 synthetic coupled companion

This is a synthetic capability companion for the blocked Che/PCHE structural
candidate.  It uses a declared PCHE-shaped parametric surrogate, a deterministic
counterflow energy balance, and a four-point synthetic pressure/temperature
field.  No publication result or author CAD was used.

## Outcome

- Effectiveness: `0.808138`; analytical duty: `6222.660 W`.
- The synthetic field has complete declared coverage and zero integral error by
  construction; this exercises the transfer contract, not physical CFD truth.
- Prior generic evidence shows a real three-level CalculiX run and conservative
  transfer checks, but this companion does **not** claim PCHE-specific FEA.
- Experimental validation and design readiness remain **NOT ESTABLISHED**.

Inputs, frozen prediction, machine result and hashes are retained beside this
report.  Any future PCHE solver run gets a new run ID.
