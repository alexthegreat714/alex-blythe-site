# HARCC S4 Part II — fresh Sol investigator comparison

**Result:** GPT-5.6 Sol at low reasoning produced a strong, independently frozen diagnosis from the original v5 evidence packet. No CFD solver was run. The comparison concerns investigator behavior, not physical validation and not general model superiority.

## Controlled information boundary

The Sol task received only the same frozen 140-file v5 packet, investigator prompt, and deterministic criteria used for the earlier Luna diagnosis. It did not receive Luna's response, the v6-v8 experiments, the Part II conclusions, or website material. The evidence packet re-hashed after the run to its original SHA-256, `c3802f63...8761ed`.

The valid response is preserved verbatim in `sol_initial_diagnosis.md` with SHA-256 `7f333f42...45eb1a2`. The run used GPT-5.6 Sol with low reasoning, completed in approximately 362 seconds, and reported 406,442 input tokens (331,392 cached), 6,709 output tokens, and 1,034 reasoning-output tokens. Cost telemetry was not recorded.

Several transport attempts were excluded before scoring: one higher-effort launch was stopped before producing an answer after the user selected low reasoning; one literal prompt interpretation refused because the evidence had not been transported into context; and read-only command-policy attempts could not open the staged files. None produced a scored diagnosis. The valid run used a fresh ephemeral context with read-only instructions and an OS-read-only staged input tree; post-run hashes and file counts were verified.

## What Sol concluded

Sol correctly separated a normal `End` marker from residual convergence. It identified continuing thermal evolution as the leading immediate explanation, followed by single-outer-corrector coupling, the wall-treatment/source-method mismatch, and remaining property-table margin. It recommended one unchanged continuation from the preserved v5 checkpoint for exactly 200 iterations, with frozen monitors and distinct predictions, before changing solver controls.

That proposal is diagnostically useful in light of the later record: Luna's pressure-iteration-cap experiment showed the cap was real but not the material coupled-residual fix, and the corrected two-outer-corrector experiment gave mixed improvement. Sol did not see those results. No Sol-selected experiment was authorized or executed here.

## Paired rubric

The frozen nine-dimension rubric scores initial diagnosis quality from 0 to 2 per dimension.

| Dimension | Luna | Sol |
|---|---:|---:|
| Case-specific evidence | 2 | 1 |
| Competing hypotheses | 2 | 2 |
| Unknown preservation | 2 | 1 |
| Experiment isolation | 2 | 2 |
| Frozen prediction | 2 | 2 |
| Numerical/physical distinction | 2 | 2 |
| Reference-method use | 2 | 2 |
| No gate manipulation | 2 | 2 |
| Stop discipline | 1 | 2 |
| **Total** | **17/18** | **16/18** |

Sol lost one point because it did not reconcile the retained v5 machine-observation versus raw-log temperature discrepancy, and another because it labeled retained inlet/outlet mass-flow observations unestablished rather than distinguishing the observed values from the missing frozen acceptance tolerance. Luna lost one point because its initial recommended pair was described as short without an exact frozen iteration count.

## Interpretation

Both investigators were evidence-disciplined and refused to turn a completed solver run into a claim of convergence or validation. Luna was slightly more complete about packet-level inconsistencies. Sol imposed the cleaner fixed stop and selected the more conservative unchanged diagnostic. Their different first choices are useful: the harness can accept more than one defensible hypothesis while requiring case evidence, isolated tests, frozen predictions, immutable gates, and explicit stop rules.

This is one paired case. It does not prove that either model is generally better, and it adds no physical credibility to the underlying HARCC CFD result.
