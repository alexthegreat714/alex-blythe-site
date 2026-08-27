---
title: Separating Intent, Execution, and Verification
summary: Why bounded agent workflows should define authority before acting, preserve execution evidence, and make acceptance a separate decision.
date: 2026-07-30
author: Alex Blythe
tags: [Agents, Verification, Architecture]
readingTime: 7 min
draft: false
relatedSoftware: [ForgeClaw]
type: Architecture
---

An automation run can finish every command it was given and still fail its actual task.

A browser may navigate successfully but land on the wrong account. A test command may exit cleanly while skipping the relevant suite. A desktop action may click a button without proving that the expected state appeared. These are not unusual edge cases. They are what happens when execution success is allowed to stand in for task success.

ForgeClaw is organized around a stricter model: define the intent, perform bounded execution, and verify the resulting state. Each phase has a different job, and none should quietly inherit the authority of the others.

## Intent defines the envelope

Intent is more than a natural-language objective. A useful request also identifies the operating surface, the expected result, the permitted tools, and the conditions that require a stop.

ForgeClaw records an execution surface for each session. Its documented surfaces include a controlled VM guest, an explicitly enabled native desktop, a non-mutating `contract_only` mode, and an unknown state that is blocked. Native desktop control is elevated risk and disabled unless it is deliberately enabled.

The controller also carries constraints such as approved windows, approved URL origins, and an allowlist for terminal commands. Before an action runs, the policy checker evaluates whether that action is permitted in the current phase and surface.

This creates a practical boundary around the objective:

- What result is being requested?
- Where may the work happen?
- Which actions are permitted?
- What evidence will count?
- Which condition requires review or termination?

Anything outside that envelope is a new decision. It is not implied permission.

This matters because a capable executor will often discover additional actions that might help. Without an explicit boundary, “helpful” expansion can become accidental authority.

## Execution produces a record, not a verdict

ForgeClaw’s controller separates perception, planning, action, and verification into explicit lifecycle steps. The action phase executes one bounded action after policy checks pass.

That design makes the executor responsible for doing work and reporting what happened. It does not make the executor the final judge of whether the objective was achieved.

The distinction is small in code and large in practice.

An action record can show that a click was issued, a command completed, or a browser operation returned successfully. Those facts are evidence about execution. They do not prove that the intended state exists afterward.

A useful execution record should answer:

- What surface was active?
- What was observed before acting?
- Which action was proposed?
- Which policy checks applied?
- Did the action mechanism report success?
- What artifacts were written?
- Was recovery attempted?

ForgeClaw persists lifecycle artifacts and exposes their paths through session status. Its public documentation also defines concrete failure classes such as `target_not_visible`, `surface_unknown`, `operator_approval_missing`, `credential_prompt_detected`, and `human_review_required`.

Those failure labels are part of the result. A run that stops honestly has produced better evidence than one that reports success without proving the outcome.

## Verification decides whether the claim is supported

Verification compares observed evidence with expected state.

In the ForgeClaw controller, the verification phase evaluates a predicate against the expected and observed state, writes a verification artifact, and returns a pass or fail verdict. A failed check is recorded as “Expected state was not proven.”

The browser and workflow verification helpers support structured criteria such as:

- URL or page-title checks
- Required text
- Field values
- Button state
- Row or modal presence
- Artifact existence
- Completed downloads
- Combined `all_of` and `any_of` conditions

This is deliberately different from asking whether the action call returned without an exception.

A successful action says, “The executor completed its operation.”

A successful verification says, “The available evidence satisfies the declared acceptance criteria.”

Those statements can agree, but the architecture should not assume that they always will.

## Separation does not require three services

“Separate” describes authority and data flow before it describes deployment topology.

The current ForgeClaw lifecycle is coordinated by one controller. It does not claim that intent, execution, and verification already run as three isolated services or security principals. The important property is that the phases remain explicit: the action result is recorded, the expected state is preserved, and verification can reject an apparently successful action.

That separation can later be strengthened with a different process, model, machine, or human reviewer. But a separate service is not enough by itself. If the verifier merely repeats the executor’s conclusion, the authority is still collapsed.

A stronger test is whether:

1. The executor can be replaced without redefining success.
2. Verification can reject a successful tool return.
3. An operator can inspect why a result passed or failed.
4. Missing evidence prevents promotion.
5. New scope requires a new authorization decision.

If those properties are absent, adding another model does not create meaningful independence.

## A no-mutation example

ForgeClaw includes a public `contract_only` lifecycle demo. It never sends mouse, keyboard, browser, or desktop input.

The demo starts a session with the goal of proving the lifecycle without mutating a user interface. It records an observed state, plans a short wait action, declares an expected state, and supplies a verification predicate. After the bounded action, the controller verifies the observed state and writes the verdict with the other session artifacts.

For the moving proof on the Precision Arts Lab homepage, the action completed successfully while the acceptance check remained `not_ready`. ForgeClaw rejected the result and preserved the expected state, observed state, predicate, and diff in a public evidence record.

The example is intentionally simple. It demonstrates something narrow and useful: execution and acceptance remain separate even when the action itself is trivial.

The same pattern becomes more important when the surface is a browser or desktop:

1. Declare the objective and operating boundary.
2. Observe the current state.
3. Plan one permitted action.
4. Execute and capture evidence.
5. Observe the resulting state.
6. Verify against the original criteria.
7. Continue, stop, recover, or request human review.

At no point does “the tool call succeeded” automatically become “the task is complete.”

## Failure should preserve the boundary

A bounded system must be able to stop without quietly weakening its rules.

ForgeClaw fails closed when it cannot prove the execution surface. It blocks native control unless the required enablement and approval are present. Its documented failure classes distinguish missing targets, unavailable surfaces, timeouts, credential prompts, risky actions, and operator-review states.

This does not make the system perfectly safe. OCR can misread text. Visual targeting can be wrong. A verifier can be given weak criteria. Native desktop automation remains elevated risk.

The architecture instead makes those limitations visible at the point where they matter. Uncertainty becomes a reason to collect more evidence, fail verification, or escalate—not a reason to silently broaden authority.

## The practical rule

Intent authorizes. Execution attempts. Verification promotes.

Keeping those jobs distinct produces a system that is easier to inspect and harder to fool with its own partial success. It also creates better failure packages: the operator can see the requested outcome, the permitted surface, the attempted action, the observed state, and the exact check that did not pass.

That is the useful promise of bounded execution. Not that every run succeeds, but that success means more than “nothing raised an error,” and failure leaves enough evidence for the next decision.

## Repository references

- [ForgeClaw overview and safety model](https://github.com/PrecisionArtsLab/ForgeClaw#readme)
- [Execution-surface contract](https://github.com/PrecisionArtsLab/ForgeClaw/blob/main/src/forgeclaw/surface.py)
- [Lifecycle controller](https://github.com/PrecisionArtsLab/ForgeClaw/blob/main/src/forgeclaw/controller.py)
- [Structured verification helpers](https://github.com/PrecisionArtsLab/ForgeClaw/blob/main/src/forgeclaw/verification.py)
- [Contract-only lifecycle demo](https://github.com/PrecisionArtsLab/ForgeClaw/blob/main/examples/forgeclaw/contract_only_lifecycle_demo.py)
- [Public verification-failure evidence](/evidence/forgeclaw-verification-failure.json)
