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

## How the smaller-model trial was prepared

The previous internal-flow v2 test used `qwen2.5-coder:14b` as both proposal
author and shadow observer. Its accepted proposal needed one allowed
correction; the resulting OpenFOAM run completed and its terminal observer
passed strict checks. Earlier 7B trials exposed missing proposal criteria and
evidence-key alias use. The next controlled variable is model size: the same
public pitzDaily seed and the same two-attempt model-only contract are retained,
while Aero's local planner **and** observer are changed to `qwen2.5:1.5b`.
The compact model was already installed; no model was fine-tuned or downloaded
for this trial. The human/Codex operator model is separate from Aero's local
model and may be switched without changing the latter.

Before changing the configured model, the prior 14B watch was complete and no
OpenFOAM run was active. The Aero web process and durable observer were then
reloaded with the 1.5B setting, preserving the existing case/evidence volume.
A read-only preflight confirmed matching configuration, a ready observer,
zero active runs, and no new trial receipt. A fresh contract and receipt path
were reserved; earlier records cannot be overwritten. A passive terminal
notification monitor is armed. It reports completion, proposal/solver failure,
stall, or timeout but **cannot start the proposal or solver**. As of this
report, the 1.5B model has not been asked to propose the case.

Why 1.5B? It is a deliberate stress test of a much smaller local controller:
can typed constraints and independent solver checks compensate for less model
capacity on a narrow, already-reviewed task? Parameter count alone does not
predict speed, reliability, or quality, so no performance score is forecast.
This is a workflow-efficiency question, not a claim that 1.5B knows CFD.

The main expected failure is a malformed or incomplete proposal, even after
one corrective response. If that happens, the model-only arm stops with no
caller-written fallback and no solver run. If the proposal passes, OpenFOAM
may complete the known seed, but the compact observer must still correctly
identify solver state, numerical evidence, open validation gates, and a safe
next action without evidence-key aliases or invented budgets. A completed
solver cannot make the design ready while independent reference, model
fidelity, and mesh independence remain open. A separate reviewed-seed
observer-only test could later isolate observation ability after proposal
failure, but it would not turn that failure into a model-authored pass.

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
| Internal flow v1 | qwen2.5-coder:14b | Model proposal rejected | No | OpenFOAM proposal included an inappropriate cross-backend `fea_case` field. |
| Internal flow v2 | qwen2.5-coder:14b | Bounded workflow passed after allowed correction | Yes | OpenFOAM completed; manifest verified; numerical gate passed; strict observer passed with zero aliases/errors. Independent review scored this narrow workflow 89/100, with deductions for the earlier schema miss and limited generality. Design readiness remained no. |
| Internal flow 1.5B v1 | qwen2.5:1.5b | **Prepared, not run** | No | Fresh receipt and two-attempt, model-only contract are ready. No result or score is claimed. |

The airfoil v7 score is its predeclared *workflow* rubric; 89/100 is a later
reviewer's judgment of the internal-flow handoff, not the same instrument.
Neither number is an accuracy percentage or physical-validation score.

The earlier 7B internal-flow reliability check reached a numerically passing
OpenFOAM result, but strict observer grading failed because two assessments
used gate IDs as evidence-key aliases. The separate reviewed-seed nozzle arm
passed strict observation; because its proposal was caller-reviewed, it does
not prove a model-authored proposal. These are diagnostic context, not extra
rows in the versioned chronology above.

## What the completed runs establish

Airfoil v7 and internal-flow v2 demonstrate guarded, operator-approved
model-to-OpenFOAM handoff on two public templates. The solver completed, the
evidence manifests verified, and the terminal observers did not confuse
numerical pass with design readiness. The internal-flow v2 terminal state was
`solver=completed`, `numerical=pass`, `design_ready=no`, with blocking gates
`validation_reference`, `model_fidelity_for_declared_use`, and
`mesh_independence`. Its terminal notification was delivered.

They do **not** show a model independently designing an unfamiliar case, a
multi-grid validation study, or agreement with independent measurements. The
next 1.5B run tests whether a much smaller local model can clear the same
proposal and observation gates. A proposal failure is a legitimate result and
must not be converted to a pass through a caller-written fallback.

## Audit trail and update policy

The source contracts and receipts remain in the private Aero workspace. This
public report is a curated snapshot; raw protected proposal attempts and local
tokens are not published. At this snapshot, the SHA-256 digest of the airfoil
v7 receipt was
`d495cb460c5965e2864de0263fb98b6e3e3b653bbf802621bce9b04d9c9a5c9f`;
the internal-flow v2 receipt was
`536e22b61ef9fd25c25bf1f96ea697fdb13bdac433bf2f22760fb97fd77be20f`.
Hashes identify those local records, not scientific validity.

The pending 1.5B entry will be revised only after its receipt and passive
terminal watch are inspected. Failures, retries, solver status, strict observer
grade, and open engineering gates will be reported even if the trial does not
complete.
