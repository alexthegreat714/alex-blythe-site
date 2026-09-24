# Rev 2.3 development follow-up: evidence workflows

September 24, 2026. This is an additive source patch to the immutable public
Rev 2.3 archive, not a replacement of that archive or a live-app deployment.
The original 2.3-dev.1 request is **PARTIALLY_COMPLETED / BLOCKED_HUMAN_ACTION**
for full Transolver execution. The software additions below are implemented and
tested; no claim of completed multi-model validation is made.

## Reuse and implementation

Reuse the existing Engineering Contract, validity gate, source custody, registry,
approval policy, CampaignController, worker lease, event chain and solver adapters.
No second scheduler, neural dependency in the core process, automatic download,
CFD execution, training pipeline or new physical acceptance criterion.

Added modules:

- `physics_ai/benchmark.py`: explicit reference/checkpoint identity, matching
  sample IDs/order/components/units/quadrature, component MAE/RMS/max/relative-L2,
  correlation and weighted integral comparison. Zero-reference metrics remain
  uninformative, not fabricated. Separate conservation checks can fail a prediction
  with low field error. Results and frozen specifications are retained with hashes.
- `physics_ai/screening.py`: deterministic, review-only ranking by a declared
  quantity/direction. All candidates, excluded records, uncertainty and reasons
  remain present. No geometry change, automatic rejection or qualification.
- `physics_ai/experiment.py`: evaluates a frozen optional experiment against an
  applicable, traceable surrogate witness. It can defer only that optional
  experiment; it cannot eliminate a physical hypothesis or waive a required run.
- `tests/test_physics_ai_workflows.py`: synthetic protocol/regression cases.

Extended `physics_ai/__main__.py`, `physics_ai/comparison.py`,
`engineering_validity/contracts.py`, `engineering_validity/controller.py` and the
extension-point manifest. An empty evidence comparison now returns NOT_ESTABLISHED,
not agreement. Campaign reads independently verify the retained witness summary.

## Benchmark operation

```text
python -m Aero.physics_ai benchmark-freeze --evidence-root <directory> --spec <spec.json>
python -m Aero.physics_ai benchmark-evaluate --evidence-root <directory> --contract-path <relative-contract.json> --prediction-path <relative-prediction.json>
```

The specification names dataset/revision, reference path/hash/origin, geometry,
weight units, component metric limits, balance limits and evaluation design.
`PROSPECTIVE` means limits must be independently established before prediction;
the operator remains responsible for that chronology. Re-scoring retained output
uses `RETROSPECTIVE_DESCRIPTIVE`, for which new acceptance limits are prohibited.
Prediction records bind to the specification hash and geometry and carry the
checkpoint hash. Field records explicitly list IDs, components, units, values and
positive quadrature weights. No interpolation or topology correspondence is guessed.

PASS_BENCHMARK_ONLY is not engineering validation. This harness is dataset-neutral;
PDEBench and RealPDEBench dataset ingestion/reproduction remain NOT_IMPLEMENTED.
Synthetic protocol tests are not either benchmark's scientific results.

## Optional campaign integration

An optional `physics_ai_policy` in a **new, frozen Engineering Contract** names
allowed models and optional experiments. Each experiment fixes its ID, hypothesis,
quantity, units, expected interval, contradiction margin and one authorized numerical
mutation path. Its `required` value must be false. It cannot share a required-check
ID or authorize Class C physical changes. Existing frozen contracts are unchanged.

1. Attach the witness through `CampaignController.attach_physics_ai`.
2. Record competing hypotheses using the existing diagnosis interface.
3. Call `consider_physics_ai(campaign_id, witness_sha256, experiment_id)`.
4. The current model hash, exact quantity/units, applicability, authority, provenance
   and frozen margin determine whether that optional proposal is deferred.
5. The existing bounded loop reselects proposals before dispatch and stops when no
   eligible proposal remains. Required/unlabelled conventional runs remain eligible.

The hypothesis annotation is `CONTRADICTED_BY_SURROGATE_NOT_ELIMINATED`.
Unknown/OOD/research-only/test-double evidence cannot cause deferral. Uncertainty
and source dependence remain recorded, not converted into invented confidence.
This is an optional library/controller hook, not an automatically enabled HTTP
endpoint or autonomous model-discovery daemon. Real campaign savings are unproven.

## Actual model evidence and outstanding work

The existing DoMINO DrivAer reference was executed twice, including the Aero adapter.
Its pressure/shear outputs repeat exactly; sensitivity gradients do not. The retained
independent integration comparison gives Cd 1.104%, Cs 25.587% and Cl 539.453%
relative discrepancies. These are retained discrepancies, not validation success.
The new harness also scores these retained scalar coefficients descriptively;
it does not claim native-field mapping, held-out testing or new inference.

DoMINO is IMPLEMENTED_NOT_FULLY_VALIDATED. PhysicsNeMo execution is tested only for
the pinned reference runtime. Transolver remains ADAPTER_STUB_ONLY /
BLOCKED_HUMAN_ACTION: the upstream MIT code and public checkpoint listing exist,
but separately hosted weight/data usage terms, exact checkpoint identity and
matching preprocessing/reference configuration are not established. No new weight
or data download or deserialization has been performed under presumed permission.

PFEM remains INVESTIGATED, not a production dependency. Learned OOD, calibrated
uncertainty, arbitrary-geometry inference, autonomous geometry optimization and
training remain NOT_IMPLEMENTED or NOT_ESTABLISHED. No unsupported future-model
registry entries were fabricated. Qualified-dataset schema remains interface only.

## Safety, tests and custody

Regression tests cover exact field alignment, nonfinite values, zero denominators,
separate conservation failure, missing evidence, altered hashes, research authority,
optional versus mandatory runs, physical-mutation blocking and witness-summary
tampering. Tests use protocol doubles; they do not demonstrate neural prediction
quality or actual CFD savings. Exact results are in TEST_RECORD.json.

Code, tests, reports and an allowlisted patch archive are retained on D:. Original
model/runtime/audit packages and public 2.0–2.3 archives are not overwritten.
No checkpoint, licensed geometry, credentials, private corpus or employer data is
in the public addendum. The live private application has not been restarted.

Next action: provide an approved Transolver checkpoint plus matching reference data
and their usage terms. Then pin hashes and preprocessing, execute the supported
reference in isolation, retain discrepancies and ingest the witness. Until that
happens, the full original multi-model milestone must not be called complete.

## Verified upstream access references

- [Transolver++ pinned code and checkpoint links](https://github.com/thuml/Transolver_plus/tree/d5a23bc734a0ebac56384cf72049a26af9673452)
- [PDEBench](https://github.com/pdebench/PDEBench)
- [RealPDEBench](https://github.com/AI4Science-WestlakeU/RealPDEBench)
