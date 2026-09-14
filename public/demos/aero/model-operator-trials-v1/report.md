# Aero local-model operator trials — public benchmark report v1

Snapshot: 2026-09-14. This report concerns a model's ability to propose a
bounded CFD case and read solver evidence through Aero's guarded workflow. It
does **not** benchmark aerodynamic accuracy, establish physical validation, or
grant design authority. All cases used reviewed public OpenFOAM seeds; no
employer data was used. The typed harness, human/operator approval, OpenFOAM,
and evidence gates remained authoritative.

## Method

- The model proposes a structured case. The harness rejects wrong backends,
  unsupported fields, missing requirements, redundant questions, and
  unsupported measurements. Rejected answers remain failures, not solver runs.
- An accepted proposal is fingerprinted and frozen. A separate exact-case
  approval starts OpenFOAM only after the shadow observer is active.
- The observer reads backend state and evidence. It is graded separately from
  numerical completion. A completed solver can be numerically adequate while
  independent validation, mesh independence, and model fidelity remain open.
- Airfoil v1-v7 are **iterative harness/model revisions**, not seven independent
  random samples. Internal-flow v1-v2 reuse one reviewed pitzDaily seed. These
  results cannot estimate a general autonomous success rate.

## The 7B internal-flow run: who did what

`qwen2.5:7b` authored the accepted OpenFOAM internal-flow proposal; its
receipt records `proposal_source=model`. The same local model supplied shadow
assessments. OpenFOAM completed, the manifest verified, and the numerical gate
passed. The terminal observer read the backend's solver/numerical/design state
correctly, but two assessments used gate IDs as evidence-key aliases, so its
strict observer result was **fail**. Design readiness remained **no**.

This run was operator-assisted. Earlier 7B proposals failed semantic review;
the reusable proposal example was clarified before the accepted attempt. A
Codex operator invoked the separate prepare, review, freeze, start, and status
steps. The typed harness enforced the case schema, the approval boundary, and
the backend evidence checks. The run receipt does not identify which Codex
model operated those steps, so it does not establish whether Luna specifically
was involved. It also does not establish a fully unattended local-agent run.

## Retained chronology

| Trial | Local model | Outcome | Solver started? | Specific finding |
| --- | --- | --- | --- | --- |
| Airfoil v1 | qwen2.5:7b | Proposal review failed | No | Conservation and wall-treatment requirements missing. |
| Airfoil v2 | qwen2.5:7b | Proposal review failed | No | Independent reference, mesh independence, and model-fidelity requirements missing. |
| Airfoil v3 | qwen2.5:7b | Proposal review failed | No | Lift, drag, mesh-independence, and model-fidelity requirements missing. |
| Airfoil v4 | qwen2.5:7b | Model proposal rejected | No | Invalid assumptions schema (HTTP 422). |
| Airfoil v5 | qwen2.5-coder:14b | Proposal review failed | No | Unresolved setup questions for the reviewed seed. |
| Airfoil v6 | qwen2.5-coder:14b | Freeze rejected | No | Requested wall-y-plus measurement was unsupported by this template. No solver case was launched. |
| Airfoil v7 | qwen2.5-coder:14b | Bounded workflow passed | Yes | Accepted model proposal; OpenFOAM completed; manifest verified; strict observer passed with zero aliases/errors; recorded rubric 100/100. Design readiness remained no. |
| Internal flow 7B | qwen2.5:7b | Solver completed; strict observer failed | Yes | Model-authored proposal; verified manifest and numerical pass; two evidence-key aliases. Operator-assisted setup and start. |
| Internal flow v1 | qwen2.5-coder:14b | Model proposal rejected | No | OpenFOAM proposal included an inappropriate cross-backend `fea_case` field. |
| Internal flow v2 | qwen2.5-coder:14b | Bounded workflow passed after allowed correction | Yes | OpenFOAM completed; manifest verified; numerical gate passed; strict observer passed with zero aliases/errors. Independent review scored this narrow workflow 89/100, with deductions for the earlier schema miss and limited generality. Design readiness remained no. |

The airfoil v7 score is its predeclared *workflow* rubric; 89/100 is a later
reviewer's judgment of the internal-flow handoff, not the same instrument.
Neither number is an accuracy percentage or physical-validation score.

The separate 7B reviewed-seed nozzle arm passed strict observation; because
its proposal was caller-reviewed, it does not prove a model-authored proposal.

## What the completed runs establish

Airfoil v7 and internal-flow v2 demonstrate guarded, operator-approved
model-to-OpenFOAM handoff on two public templates. The solver completed, the
evidence manifests verified, and the terminal observers did not confuse
numerical pass with design readiness. The internal-flow v2 terminal state was
`solver=completed`, `numerical=pass`, `design_ready=no`, with blocking gates
`validation_reference`, `model_fidelity_for_declared_use`, and
`mesh_independence`. Its terminal notification was delivered.

They do **not** show a model independently designing an unfamiliar case, a
multi-grid validation study, or agreement with independent measurements.

## Audit trail and update policy

The source contracts and receipts remain in the private Aero workspace. This
public report is a curated snapshot; raw protected proposal attempts and local
tokens are not published. At this snapshot, the SHA-256 digest of the airfoil
v7 receipt was
`d495cb460c5965e2864de0263fb98b6e3e3b653bbf802621bce9b04d9c9a5c9f`;
the internal-flow v2 receipt was
`536e22b61ef9fd25c25bf1f96ea697fdb13bdac433bf2f22760fb97fd77be20f`.
Hashes identify those local records, not scientific validity.

The 7B run's local receipt is
`Aero/reports/shadow_handoff_model_only_final_20260914.json` and the reliability
review is `Aero/reports/aero_handoff_reliability_20260914.md`. Its operator
identity is not included in the receipt; do not infer a specific Codex model
from a later handoff document.
