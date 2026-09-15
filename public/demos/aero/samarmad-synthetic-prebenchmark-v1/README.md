# Samarmad-derived PCHE synthetic prebenchmark

**Aero benchmark register entry:** `PCHE-SAMARMAD-SYNTHETIC-01`  
**Evidence revision:** v5  
**Completed:** 2026-09-14  
**Disposition:** runnable orchestration gates complete; paper-specific execution and publication validation are open.

This is a **synthetic prebenchmark**, not a claim that Aero has reproduced the
publication. The model-facing packet contains a source-derived geometry and
operating envelope, with pointwise values and missing material properties
explicitly marked as synthetic estimates. The prediction bundle was frozen and
hash-verified before the synthetic truth was generated. The publication's
measurements were not supplied to the model.

## What this public record demonstrates

- source/input and synthetic-estimate separation;
- frozen criteria and prediction-bundle hash verification;
- a curved-interface pressure and heat-rate transfer proof;
- a generic OpenFOAM conjugate-heat-transfer acceptance run;
- a generic three-level CalculiX thermal-structural acceptance run; and
- retained, machine-readable gate evidence.

The Samarmad-specific corrugated OpenFOAM case, PCHE curved CFD-to-FEA
mapping, geometry-specific CalculiX case, and comparison to the paper's
experimental measurements are **not run or established** in this revision.
The generic acceptance runs prove the surrounding pipeline contracts, not the
physical accuracy of a PCHE prediction.

## Source and custody boundary

Ahmed Oleiwi Samarmad and Hayder Mohammad Jaffal, “Performance evaluation of a
printed circuit heat exchanger with a novel two-way corrugated channel,” 2023,
DOI [10.1016/j.rineng.2023.101303](https://doi.org/10.1016/j.rineng.2023.101303).

The source record is linked for attribution only. No publication measurements,
full text, or adapted source material are redistributed here. See
`source_custody.json` for the current rights and eligibility state.

## Reproduce / inspect

- [Gate manifest](gate_manifest.json)
- [Frozen criteria](criteria.json)
- [Model-facing input packet](input_packet.json)
- [Prediction/run manifest](run_manifest.json)
- [Verification receipt](verification.json)
- [Source-custody record](source_custody.json)
- [OpenFOAM CHT acceptance](cht_openfoam_acceptance.json)
- [OpenFOAM study acceptance](openfoam_acceptance.json)
- [CalculiX acceptance](fea_acceptance.json)
- [Curved-transfer proof](curved-transfer/curved_transfer_shakedown.json)
- [Curved-transfer artifact manifest](curved-transfer/manifest.json)

Hashes establish byte identity and ordering; they do not establish scientific
validity, experimental agreement, design readiness, or certification.
