# Aero heat-exchanger benchmark program — completion audit

**Audit revision:** 1.0  
**Evidence release:** 16 September 2026 UTC  
**Disposition:** `SYNTHETIC_EVIDENCE_RELEASE_COMPLETE / PUBLICATION_VALIDATION_INCOMPLETE`

## Purpose and scope

This audit checks the approved fallback scope: complete the heat-exchanger
capability program with a logically specified, clearly disclosed synthetic
replacement when the publication inputs or independent truth packages are not
available. It does **not** relabel a synthetic run as a publication benchmark.
The original publication candidates B01–B05 and the ordered transfer study
remain individually gated in `program_registry.json`.

## Requirement audit

| Requirement | Evidence | Disposition |
|---|---|---|
| Ground the replacement in real public references | `PROGRAM_REPORT.md` references Samarmad/Jaffal, Seo, Che, de la Torre (2020/2023), Pelanconi et al., and AIAA 2024-4036; references supply methodology/context only | **PASS — disclosed** |
| Keep source results out of synthetic inputs | `synthetic_companion_summary.json` has `source_results_used: false`; every companion report marks inputs/coefficients synthetic | **PASS** |
| Preserve earlier blind attempts | Local `HX-B01/` and `HX-B05/` frozen/custodian packets remain intact; prior plan hashes and STOP decisions are retained in `PROGRAM_REPORT.md` and `program_registry.json` | **PASS — local custody** |
| Preserve negative numerical evidence | `HX-S01_synthetic_replacement/` retains the three-grid baseline FAIL and LTOL diagnostics; no favorable continuation overwrites it | **PASS** |
| Execute first-principles work | B01 Seo analytical slice and S01 analytical screen are retained; S02–S05/D01 use deterministic declared reduced-order equations | **PASS — scoped** |
| Exercise coupled transfer/structural intent | `HX-S02-COUPLED-SURROGATE-01/` freezes a complete synthetic field and coupling contract; generic CalculiX evidence is cited but not relabeled as PCHE FEA | **PASS — contract only** |
| Exercise fidelity selection | `HX-S03-FIDELITY-01/` freezes the escalation decision and rationale before synthetic result recording | **PASS — synthetic** |
| Exercise geometry/thermal sensitivity | `HX-S04-SENSITIVITY-01/` retains an 81-case sweep, directional trends, and sensitivity ranking | **PASS — synthetic** |
| Exercise architecture/material trade | `HX-S05-ARCH-01/` freezes criteria, alternatives, and a preliminary synthetic selection | **PASS — synthetic** |
| Exercise transfer/generalization | `HX-D01-TRANSFER-01/` includes Stage A sizing and a controlled Stage B fidelity escalation | **PASS — synthetic** |
| Freeze and hash outputs | Suite `SHA256SUMS.txt`, B01 `SHA256SUMS.txt`, and the public root manifest are retained; all published entries were re-verified against served bytes | **PASS** |
| Reveal and comparison discipline | B01 correlation screen is explicitly reported as a 30.86% underprediction FAIL; pointwise experiment remains NOT ESTABLISHED | **PASS — limited comparison** |
| Publish an evidence-backed report | Program report, suite report, machine-readable summary, companion reports, and manifests are live on the Aero website | **PASS** |

## What is not complete

The following are intentionally **not** claimed as complete:

- a matched, independently held publication truth package for B01;
- publication-specific OpenFOAM CHT for B02–B04;
- PCHE-specific CalculiX stress/deformation predictions with an independent
  structural truth target;
- a blind author-ranking comparison for B05;
- the original ordered HX-D01 publication-program arm;
- a trusted external timestamp or administrator-proof immutable archive.

The two earlier B01 feasibility plans and the B05 anonymized feasibility plan
remain valid STOP records. The synthetic suite is a separate evidence release,
not a way to bypass those gates.

## Final engineering disposition

The program is complete **for the approved synthetic capability-release scope**:
the five remaining capability intents have executable, deterministic,
hash-addressed records, and the public report makes the limitations visible.
It is not complete as a scientific publication-validation campaign. No result
in this release establishes experimental agreement, design readiness,
qualification, or employer-hardware suitability.

