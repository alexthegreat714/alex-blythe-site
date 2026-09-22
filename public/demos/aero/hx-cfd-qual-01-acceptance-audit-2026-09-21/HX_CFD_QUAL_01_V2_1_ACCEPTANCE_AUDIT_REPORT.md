# HX-CFD-QUAL-01 V2.1 Acceptance-Path Correction Audit

Date: 2026-09-21  
Owner: Alex Blythe  
Scope: retained-evidence audit; no CFD execution

## Disposition

The historical V2.1 qualification remains `FAILED_NUMERICAL_GATES_UNCHANGED`. Mesh independence remains `NOT_EVALUATED`. This report corrects the acceptance/evidence path and does not rescore the clean three-grid run.

## Corrections made

The acceptance finalizer contained an invalid field-stationarity predicate: it tested that normalized field change was greater than zero rather than testing the frozen upper limit. The predicate now requires a non-empty set of finite normalized RMS updates, each `<= 0.001`.

The continuation analyzer also incorrectly stated that monitor rows after 800 s were missing. The retained `surfaceFieldValue` histories contain rows through 1000 s. The corrected analyzer reports those rows directly.

## Retained monitor evidence

The 800–1000 s outlet-temperature spans are:

- shell: `0.002803965 K`;
- tube: `0.001039865 K`.

These are supporting continuation evidence, not a qualification pass. Full energy closure and integrated interface heat-rate evidence remain unresolved in this branch.

## Spatial and field-custody limitation

The declared `x <= 0.05 m` tube mask contains `98.646%` of the exported tube cells (`391,955` of `397,335`). It is therefore not a defensible inlet-manifold-local measurement. The field comparison is also positional/truncated rather than proven by explicit cell identity or topology correspondence.

## Property-reference limitation

Retained endpoint `p/p_rgh` ranges include negative values while the declared property-pressure interval begins at 0 Pa. The corrected disposition is `NOT_ESTABLISHED_PRESSURE_REFERENCE`, not a supporting property-validity pass.

## Artifact integrity

The continuation source-immutability result is `True`. The regenerated continuation manifest and verification files are parseable; verification reports `219` checked, `0` missing, and `0` mismatches.

## Final status

`DIAGNOSTIC_CORRECTION_COMPLETE`  
`HX-CFD-QUAL-01 = FAILED_NUMERICAL_GATES`  
`MESH_INDEPENDENCE = NOT_EVALUATED`  
`HX-03 = FROZEN_AND_BLOCKED`  
`HX-04 = STAGE_B_BLOCKED`

No new CFD was run. The next clean qualification must use the corrected predicate, an independently defined geometry-backed local region, explicit field correspondence, resolved pressure-reference semantics, and complete energy/interface evidence.
