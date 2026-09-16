# Aero heat-exchanger benchmark program — evidence and disposition

**Program report v1.3 · 16 September 2026 UTC**  
**Overall status: EVIDENCE RELEASE COMPLETE / VALIDATION INCOMPLETE.** This report consolidates what was actually executed, what stopped before execution, and what remains unscoreable. It is not a claim that the planned HX-B01–B05 and HX-D01 studies all ran.

## Executive disposition

**Evidence update v1.1 — 16 September 2026 UTC:** a separately labeled,
post-baseline coarse-grid solver-tolerance investigation has now reached its
predeclared stop. LTOL-003 passed the residual and conservation gates but
failed the full-window monitor-stability limit; no medium/fine follow-up was
run. The original 250-iteration three-grid numerical FAIL remains unchanged.
LTOL-002 is documented as a normal solver end with its stationarity window
unevaluable because output purging removed two required checkpoints.

**Evidence update v1.2 — 16 September 2026 UTC:** HX-B01 now has a separately
identified, source-grounded analytical slice (`HX-B01-SC-ANALYTICAL-01`). It
uses only the Seo et al. straight-microchannel geometry and operating inputs,
freezes a first-principles channel-friction prediction before revealing the
source correlation, and preserves the two earlier Luna feasibility STOPs.
The comparison is a deliberate **FAIL** (30.86% underprediction against the
revealed fitted correlation). It is not a pointwise experimental validation:
the source figure does not provide a verified machine-readable point, and this
slice does not run CFD or FEA.

**Evidence update v1.3 — 16 September 2026 UTC:** the still-ineligible
publication candidates B02–B05 and the ordered transfer study now have a
separate synthetic companion release. Five deterministic companions exercise
coupled transfer/structural-contract handling, fidelity escalation, a declared
81-case sensitivity sweep, architecture/material trade reasoning, and a new
two-stage design-transfer requirement. They use real public references only for
methodology context; all numeric inputs and outputs are marked synthetic. This
closes the executable synthetic capability slice without claiming publication
validation or PCHE-specific CFD/FEA truth.

The program has produced one executed, source-informed synthetic PCHE CFD study, HX-S01. Its 250-iteration three-grid baseline is a **NUMERICAL FAIL** under the criteria frozen before the run. Same-settings continuations to iteration 1,000 are diagnostic only; they still fail the residual limit and retain roughly 28% fine-to-medium pressure-drop differences. Experimental agreement, PCHE-specific structural performance, and design readiness are **NOT EVALUATED / NOT ESTABLISHED**.

The publication-blind HX-B01 candidate was stopped twice at its input/feasibility gate; those plans remain hash-verifiable and immutable. The new analytical slice is a separately disclosed release and does not retroactively turn the earlier stops into a pointwise benchmark. HX-B05 also produced a fresh anonymized, result-withheld plan-only review; Luna stopped before preregistration because decision-critical requirements, properties, and geometry were missing. HX-B02–B04 remain source/reproducibility gated. HX-D01 has not started because the planned predecessor-study sequence is not closed.

The accurate takeaway is therefore mixed: Aero's source-aware custody, first-principles, CHT, numerical-gate, and evidence-preservation path has been exercised on a difficult synthetic reconstruction, and the gates rejected it. This does **not** demonstrate a validated heat exchanger or a fully autonomous model-piloted workflow.

## Program register

| Study | Current disposition | What the evidence supports |
|---|---|---|
| HX-B01 — experimental straight-channel PCHE | `SCOPED ANALYTICAL COMPARISON COMPLETE / POINTWISE EXPERIMENT NOT ESTABLISHED` | Two plan-only Luna STOPs are preserved. A new Seo-channel analytical slice froze f and channel ΔP before revealing the fitted correlation; it failed by 30.86% and ran no CFD/FEA. |
| HX-S01 — source-informed synthetic PCHE | `NUMERICAL FAIL / EXPERIMENT NOT SCORED` | First-principles screen, reconstructed periodic geometry, three-grid OpenFOAM CHT, balances, and retained 1,000-iteration diagnostics. The numerical gates fail; no experimental truth or structural result is claimed. |
| HX-B02 — laboratory PCHE CFD-to-FEA candidate | `SOURCE_AND_STRUCTURAL_TRUTH_GATE_OPEN` | No eligible run. Lawful full-text/input access and an independent structural truth target were not established. Author FEA output alone would not score physical accuracy. |
| HX-B03 — 3D zigzag PCHE fidelity candidate | `ACCESS_AND_VERSION_GATE_OPEN` | Publisher record identifies a 3D CFD→FEA study and reports 2D/3D differences, but a lawful, version-matched full methods/input source and independent structural target were not established. No run. |
| HX-B04 — high-temperature PCHE sensitivity candidate | `FULL_TEXT_AND_REPRODUCIBILITY_GATE_OPEN` | Publisher metadata/abstract are discoverable; reproducible complete inputs and independent structural truth were not established. No run. A repository search hit was a review citing this paper, not the paper itself. |
| HX-B05 — high-temperature lattice architecture/material trade | `STOP_BEFORE_PREREGISTRATION / NOT SCORED` | Fresh anonymized Luna feasibility plan completed and hash-froze a STOP. No architecture/material ranking or solver run. Custodian exposure of result-bearing publication content is disclosed; this is not a fully human-blind experiment. |
| HX-D01 — new design-transfer study | `NOT STARTED / ORDER GATE OPEN` | Deliberately not started while HX-B01–B05 dispositions remain open. It must retain a broad-requirements stage and a controlled fidelity-escalation stage. |
| METHOD-AIAA-01 | `METHODOLOGY REFERENCE ONLY` | Process grounding only; not a hidden-answer truth benchmark or scored run. |
| Synthetic companion suite | `COMPLETE / VALIDATION INCOMPLETE` | Five separately identified deterministic companions cover the currently ineligible B02–B05 and D01 capability intents. They preserve source gates and do not substitute for publication truth. |

The older `pche_samarmad_publication_run_v1` remains a separate incomplete rehearsal. It is not silently reclassified as HX-B01 or as a successful validation result.

## HX-B01: preserved blind feasibility stops

The first input-only Luna plan (run `HX-B01-LUNA-PREPLAN-20260915T172952Z`) and its separately versioned thermal-only follow-up (`HX-B01-SC-THERMAL-01-LUNA-PREPLAN-V2-20260915T1826Z`) are retained. Both returned a direct STOP before a numerical run. The follow-up is especially clear that it cannot define a defensible heat-duty prediction interval from the supplied inputs.

The run guard reverified both frozen-plan hashes during this report pass:

- Initial plan: `152d573ec41a83662edef5db71c74829074bf6ca99ddc4cc8b04fa0312155690`
- Scoped thermal plan: `72aea54a3f3d3cdda9b53a2d243873ecb8dfec5e2a17cecb48a3487bff961fca`

The STOP is not a CFD failure. The cases were never submitted. The missing items include verified channel/profile geometry, configuration-specific flow and area mapping, pressure-tap/port correspondence, a target-point procedure, and an uncertainty-aware extraction route for figure-only results. No results were revealed to those Luna invocations. However, local hashes are not a trusted timestamp or immutable archive, and CLI sandboxing is not proof of system-wide isolation.

## HX-B01: scoped Seo analytical comparison

To exercise a valid part of HX-B01 without overwriting the earlier STOPs, the
program added run `HX-B01-SC-ANALYTICAL-01`. This is a source-grounded,
analytical-only comparison against Seo et al. (2015), whose open-access paper
defines a straight PCHE microchannel geometry and a fitted friction-factor
correlation. The implementing agent had access to the public article during
construction; that exposure is disclosed, so this is not claimed as a fully
human-custodian blind experiment.

The visible packet contained the geometry envelope, channel dimensions,
hydraulic-area definitions, water-property reference, and a single matched
operating point (`Re = 300`). It excluded the fitted correlation, experimental
points, result figures, reported errors, and conclusions until the prediction
was frozen. The deterministic script reads only that packet and reproduces the
frozen values; it does not need the publication to run.

| Quantity | Frozen first-principles prediction | Revealed source-correlation comparison |
|---|---:|---:|
| Hydraulic diameter reconciliation | 0.1963% difference from source value | **PASS** (predeclared ≤1% screen) |
| Fanning friction factor at Re 300 | 0.0533333 | 0.0771347 |
| Channel pressure drop | 2,810.20 Pa | 4,064.32 Pa (same channel-only definition) |
| Relative error | — | **−30.86%** (underprediction) |

The source reports its fitted correlation as valid over `Re = 100–850` and an
approximately ±8% experiment/correlation envelope. The frozen analytical
screen therefore **FAILS** that disclosed correlation comparison. This is a
useful negative result, not a validation success: the article does not provide
a verified machine-readable point and its reported apparatus pressure drop
includes inlet/outlet-port effects that are not represented in this channel-only
comparison. Pointwise experimental validation is consequently **NOT
ESTABLISHED**. No OpenFOAM or CalculiX run was authorized for this scoped slice.

The immutable run packet, freeze record, source reveal, comparison report,
reproducibility script, and per-file SHA-256 manifest are retained under
[`HX-B01 scoped analytical evidence`](HX-B01/runs/seo_channel_analytical_01/).

## Synthetic companion suite: executable coverage for the remaining intents

Because the publication candidates B02–B05 remain blocked by lawful-input,
version, or independent-truth gates, the program adds five new run IDs rather
than inventing source data or relabeling generic evidence. The suite is
`synthetic_companion_suite_v1/` and its top-level manifest covers every file.
Real public papers supply methodology families only; no paper result, author
ranking, or conclusion was supplied to the calculations.

| Companion | Executed scope | Disposition |
|---|---|---|
| `HX-S02-COUPLED-SURROGATE-01` | Counterflow energy balance, synthetic pressure/temperature field, and transfer-contract expectations; prior generic CalculiX run cited but not relabeled as PCHE FEA | **COMPLETE SYNTHETIC CONTRACT / PCHE CFD–FEA NOT ESTABLISHED** |
| `HX-S03-FIDELITY-01` | 1-D, 2-D, and 3-D reduced-order levels; pressure loss, wall-temperature spread, and local-stress changes drive a predeclared escalation decision | **COMPLETE SYNTHETIC FIDELITY DECISION** |
| `HX-S04-SENSITIVITY-01` | 81-case diameter/thickness/fillet/thermal-gradient sweep with pressure, thermal, combined-stress and margin screens | **COMPLETE SYNTHETIC SENSITIVITY SWEEP** |
| `HX-S05-ARCH-01` | Three architecture families × three material families with frozen duty, pressure-loss, temperature and margin criteria | **COMPLETE SYNTHETIC ARCHITECTURE/MATERIAL TRADE** |
| `HX-D01-TRANSFER-01` | New generic requirement; Stage A keeps CFD out of the first screen, Stage B tightens local limits and escalates to a planned 3-D CFD/FEA/tolerance path | **COMPLETE SYNTHETIC DESIGN TRANSFER / NO SOLVER CLAIM** |

These companions prove orchestration, preservation of alternatives, and
fidelity/stop decisions under declared assumptions. They do **not** establish
experimental accuracy, PCHE-specific solver accuracy, structural qualification,
or design readiness. The suite report and machine-readable summary are at
[`synthetic companion evidence`](synthetic_companion_suite_v1/).

## HX-S01: the executed synthetic replacement

### Why this replacement is synthetic

Samarmad and Jaffal (2023) supplies real PCHE configuration context, while Seo et al. (2015) provides related straight-microchannel methodology and NIST water correlations support the declared property range. The reconstructed solver condition did not have a verified, matched pointwise experimental target. The source also has a 290 K/293 K cold-inlet discrepancy and does not supply independent structural truth. Missing values were recorded as engineering assumptions; no measurements were invented or treated as a validation target.

HX-S01 is therefore **source-informed, synthetic, not blind, and not experimental validation**. It uses a periodic hot/cold/solid channel-pair reconstruction, not author CAD. The analysis is Codex-supervised and human-orchestrated; it does not score local-agent autonomy.

### Frozen first-principles screen

For a straight, fully developed semicircular duct (an analytical screen, not the corrugated geometry), the retained calculation gives:

- Hydraulic diameter: `1.52754 mm`
- Reynolds number: `519.12`
- Straight-duct frictional pressure drop: `576.20 Pa` per channel
- Idealized counterflow heat-duty screening band: `27.46–30.90 W` per channel pair

This band is not a statistical uncertainty interval or a CFD acceptance target. It omits corrugation, headers, collectors, entrances, and measurement-plane correspondence.

### OpenFOAM baseline and frozen gates

OpenFOAM Foundation v10 `chtMultiRegionFoam` ran a three-region conjugate heat-transfer reconstruction on three distinct meshes. The frozen gates were: maximum final equation residual `≤1e-6`; mass imbalance `≤0.5%`; energy imbalance `≤5%`; medium-to-fine changes in pressure drop, duty, and outlet temperature `≤5%`; and all-region `checkMesh` pass.

| Grid | Cells | Max final residual | Mass imbalance | Energy imbalance | Hot / cold pressure drop | Outcome |
|---|---:|---:|---:|---:|---:|---|
| Coarse | 494,670 | `2.1375e-4` | 0.0669% | 3.671% | 1,319.4 / 1,340.9 Pa | **FAIL** residual |
| Medium | 1,003,677 | `5.7688e-6` | 0.0896% | 2.492% | 1,393.7 / 1,407.9 Pa | **FAIL** residual |
| Fine | 2,770,939 | `6.6989e-6` | 0.0624% | 1.496% | 1,800.9 / 1,808.9 Pa | **FAIL** residual |

All mass and energy balances satisfy their limits. All three residuals miss the frozen limit, and the medium-to-fine pressure-drop changes are 22.61% hot-side and 22.17% cold-side, exceeding the 5% grid-sensitivity gate. A normal OpenFOAM `End` marker means the process ended; it does not make these runs numerically converged.

### Same-settings continuations

Continuations were retained as diagnostics and do not change the frozen 250-iteration baseline. At iteration 1,000 all three grids still fail residual convergence. The fine endpoint has maximum final residual `1.9805244e-6`, mass imbalance `0.06253%`, energy imbalance `2.1226%`, hot/cold pressure drops `1794.72 / 1802.36 Pa`, and hot/cold duties `20.097 / 20.533 W`. Fine-to-medium pressure-drop differences remain `28.7% / 28.1%`. Duty values are closer across grids, but this does not cure the residual or pressure-drop failures.

The original case manifest contains an unsupported statement that all meshes fail a frozen mesh-quality criterion. The report preserves that manifest and follows the actual frozen criteria plus retained per-region `checkMesh` logs, which pass. A medium-grid hot-fluid log has one local 70.103° face diagnostic, retained for review. This discrepancy does not change the overall numerical FAIL.

### HX-S01 disposition

| Claim | State |
|---|---|
| Source-informed synthetic setup and assumptions | Established and documented |
| First-principles screening calculation | Completed, limited scope |
| Three-grid OpenFOAM CHT execution | Completed; numerical gates **FAIL** |
| Experimental comparison | **NOT EVALUATED** |
| PCHE-specific CalculiX / structural prediction | **NOT EVALUATED** |
| Model fidelity / design readiness | **NOT ESTABLISHED** |
| Local conversational-agent autonomy | **NOT EVALUATED** |

The detailed study report, input definition, conservation plot, machine records, and evidence manifests are available from the [HX-S01 evidence page](https://alex-blythe.com/software/aero/evidence/benchmarks/heat-exchanger-program-v1/).

## HX-S01: post-baseline stationarity diagnostics

These are non-blind synthetic diagnostics and do not replace the frozen
baseline. LTOL-001 tightened copied-case linear solves on the coarse grid;
although residual and balance checks passed, cold pressure drop and both duty
monitors changed more than the frozen 0.5% stability limit over its final
25-step interval. LTOL-002 extended the same coarse case to 1,600 and ended
normally, but `purgeWrite 3` removed iterations 1,500 and 1,525 before the full
five-point window could be postprocessed. That gate is **NOT EVALUABLE** for
LTOL-002, not a PASS or solver crash.

LTOL-003 repeated the 1,100–1,600 coarse continuation with the same numerical
settings and changed only the copied run horizon and `purgeWrite 0` checkpoint
retention. At 1,600, maximum final equation residual was `5.8496e-9`, mass
imbalance `0.06674%`, and energy imbalance `2.1811%`; all three passed their
frozen limits. The full-window stability gate failed: cold-side pressure-drop
changes were `1.812–4.424%`, while hot/cold duty changes were `0.790–0.885%`
per adjacent 25-step interval, all above the `0.5%` limit. The hot pressure
drop stayed unchanged in the sampled window. No root cause is asserted. The
predeclared action was to stop at coarse, so medium/fine were not run.

The detailed records, postprocessing JSON, region mesh logs, solver log, and
hashes are retained in
[`HX-S01 diagnostic evidence`](HX-S01_synthetic_replacement/diagnostics/HX-S01-DIAG-LTOL-003_RESULTS.md).
These results remain synthetic and non-blind; they do not establish
experimental accuracy, grid independence, structural performance, or design
readiness.

## HX-B05: architecture/material feasibility stop

The fresh packet used anonymized duty inputs and candidate architecture/material families from Pelanconi et al. (2021); it did not expose the source title, DOI, result-bearing abstract, rankings, or outcomes to the Luna invocation. The packet contained only the two allowlisted files and passed the lexical audit. The verified visible-packet SHA-256 is `8477398fd71c8a4e0eb8a3b87c12f1ea1b4545a82282caddbff35c5961a87a72`.

GPT-5.6 Luna completed the requested 22-section plan and froze **STOP before preregistration**. It calculated only the packet-supported cold-stream temperature rises of 550 K and 500 K, and declined to invent duty or rank materials without temperature/composition-dependent properties. Missing requirements included pressure-drop limits, envelope/mass/cost, service life/degradation, material allowables and chemistry, detailed geometry/manifolds, manufacturing limits, performance data, and owner-approved trade weights. The plan hash reverified as `57e32aeff9889606dc1e44f4259e7414f6ca7898b3dfb0f498e383b028a89e1d`.

Custody disclosure: the implementing agent had seen result-bearing public publisher content before this fresh invocation. The packet and runtime reference were withheld from Luna, but the study is not a fully human-custodian blind experiment and pretraining exposure cannot be ruled out. No ranking, CFD, FEA, score, or external timestamp resulted.

## Source and reproducibility audit

- **HX-B02 / Che et al. (2021):** the candidate's publisher record is known, but lawful full text and a reproducible input/data package were not established here. The paper's structural calculation would not itself be an independent experimental truth target.
- **HX-B03 / de la Torre et al. (2023):** the Elsevier record describes a 3D zigzag-PCHE CFD→FEA study and reports a 2D/3D difference. The publisher page remains purchase/access controlled; no version-matched complete input package or independent structural measurement was established. It is not scoreable as an independent validation case on this evidence.
- **HX-B04 / de la Torre et al. (2020):** the publisher record/abstract is discoverable, but a complete lawful methods/input source and independent structural truth are not established. A public Technical University of Denmark repository PDF encountered in this audit is a high-temperature-heat-exchanger review that lists B04 in its references; it is **not** a deposited copy of B04. That false lead is not counted as source access.
- **HX-B05 / Pelanconi et al. (2021):** an open article is suitable for architecture/material methodology, but the present input packet was insufficient for a defensible independent ranking. Its role is not experimental validation.
- **AIAA methodology reference:** used as process grounding only, not as an outcome benchmark.

No article results were used to tune HX-S01. The B01 and B05 Luna packets excluded outcome material. The fact that the implementing agent saw public, result-bearing abstracts during source research is disclosed; accordingly, the program does not claim perfect human blinding.

## Reproducibility, custody, and limitations

The complete local HX-S01 report and evidence manifest are retained under `HX-S01_synthetic_replacement/`. The public HX-S01 artifact manifest has been published separately. B01 and B05 frozen plans remain in their original versioned directories. No prior attempt is overwritten.

Local SHA-256 verifies content identity against a manifest, not scientific correctness, trusted time, or write-once storage. No external timestamp is established for the blind plans. Solver success or a normal process end is not a physical validation. None of the studies establish design release, qualification, Blue Origin/other employer hardware applicability, or autonomous local-model competence.

## Remaining validation work before full program closure

1. Upgrade HX-B01 only if a custodian-verified dataset or stronger lawful experimental source makes a pointwise target possible. The scoped analytical comparison is complete as an evidence slice, but it does not close the experiment, CFD, or FEA gates. Any new blind packet gets a new run ID; the old STOPs and this scoped FAIL remain immutable.
2. Either close HX-B02–B04 as ineligible with source evidence, or obtain lawful/version-matched inputs and an independent structural truth source. Do not use author FEA values alone as experimental truth.
3. For HX-B05, supply the missing owner requirements and verified property/geometry data, then create a new pre-result packet and plan freeze. Keep the prior STOP and custody disclosure.
4. The synthetic D01 transfer companion is complete and intentionally does not consume the publication order gate. Do not start a publication-informed or solver-backed D01 benchmark until the HX-B01–B05 dispositions required by the original program order are explicitly closed and frozen.
5. If continuing HX-S01 numerics, use a separately identified diagnostic/repair run with predeclared settings and gates. Never revise its frozen baseline or describe post-hoc tuning as blind validation.

Until those items are resolved, the honest status remains **VALIDATION INCOMPLETE**. This report is the program's evidence-backed status and executed-study record, not a certificate that the entire six-question program has passed.

## References

1. Samarmad, A. O., and Jaffal, H. M. (2023). “Performance evaluation of a printed circuit heat exchanger with a novel two-way corrugated channel.” *Results in Engineering*, 19, 101303. [DOI: 10.1016/j.rineng.2023.101303](https://doi.org/10.1016/j.rineng.2023.101303).
2. Seo, J.-W. et al. (2015). “Heat Transfer and Pressure Drop Characteristics in Straight Microchannel of Printed Circuit Heat Exchangers.” *Entropy*, 17(5), 3438–3457. [Publisher article](https://www.mdpi.com/1099-4300/17/5/3438).
3. Hruby, J. et al. (2009). “Reference Correlations for Thermophysical Properties of Liquid Water at 0.1 MPa.” *Journal of Physical and Chemical Reference Data*, 38(1). [NIST publication record](https://www.nist.gov/publications/reference-correlations-thermophysical-properties-liquid-water-01-mpa).
4. Che, S. et al. (2021). “Structural Integrity Assessment of a Unit Cell in a Laboratory-Scale Printed Circuit Heat Exchanger for Molten Salt Reactors With Supercritical CO2 Power Cycle.” ASME PVP2021-60735. [DOI: 10.1115/PVP2021-60735](https://doi.org/10.1115/PVP2021-60735).
5. de la Torre, R., François, J.-L., and Lin, C.-X. (2023). “Design analysis of a printed circuit heat exchanger for HTGR using a 3D finite elements model.” *Nuclear Engineering and Design*, 407, 112270. [DOI: 10.1016/j.nucengdes.2023.112270](https://doi.org/10.1016/j.nucengdes.2023.112270).
6. de la Torre, R., François, J.-L., and Lin, C.-X. (2020). “Assessment of the design effects on the structural performance of the Printed Circuit Heat Exchanger under very high temperature condition.” *Nuclear Engineering and Design*, 365, 110713. [DOI: 10.1016/j.nucengdes.2020.110713](https://doi.org/10.1016/j.nucengdes.2020.110713).
7. Pelanconi, M. et al. (2021). “Application of Ceramic Lattice Structures to Design Compact, High Temperature Heat Exchangers: Material and Architecture Selection.” *Materials*, 14(12), 3225. [Publisher article](https://www.mdpi.com/1996-1944/14/12/3225).
8. El-Soueidan et al. (2024). “The Coupling of a Preliminary Design Method with CFD Analysis for the Design of Heat Exchangers in Aviation.” AIAA SciTech Forum, AIAA 2024-4036. [DOI: 10.2514/6.2024-4036](https://doi.org/10.2514/6.2024-4036).
