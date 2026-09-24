# Aero public source releases — September 24, 2026

Owner-authorized source publication, not an unauthenticated running service.
No conversations, private corpus, credentials, model weights, runtime databases,
employer data or historical CFD run directories are included.

## Contents and limitations

2.0 is a PARTIAL_BASELINE_REFERENCE: the historical profile configuration and
revision history, not a complete runnable application. The original scoped
snapshot did not constitute a full installation. The private application shell
and personal service integrations are deliberately excluded.

2.1 is the auditable AnyJev Routing Lab module: source, pinned generic contract,
examples, page and software tests. Weights and isolated inference dependencies
must be separately installed. The standalone benchmark script can download its
pinned model when explicitly invoked; it is NOT run by the tests.

2.2 is the cumulative Routing Lab + Engineering Validity Gate source module pack,
including dependency-light first-principles calculations and worker integration
source. It is NOT a complete configured OpenFOAM/CalculiX installation or an
employer-approved engineering tool. No solver campaign is launched by tests.

Publication transformations: normalize text to LF; replace the owner's edge
origin with your-aero-host.example. Original hashes and release hashes are in
SOURCE_MANIFEST.json. Existing lab-only access and approval checks remain.
Do not expose these control routes publicly without authentication.

## Verify and test a downloaded archive

Extract into a new directory. Inspect SOURCE_MANIFEST.json before use.
Use an isolated Python 3.12 environment; install requirements-test.txt, then:

    python -m pytest Aero/tests -q

Tests use synthetic cases and test doubles. Passing them is software evidence,
not neural-model validation, CFD/FEA validation, or hardware qualification.
Framework/model dependencies remain governed by their upstream licenses. No
new license or employer authorization is implied by public source availability.

The current live private app remains authenticated. Public site presentation
revisions, solver convergence-contract versions and source revisions are distinct.
