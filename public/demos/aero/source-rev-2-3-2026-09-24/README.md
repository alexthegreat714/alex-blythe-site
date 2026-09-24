# Aero source Rev 2.3 — September 24, 2026

Cumulative 2.2 modules plus optional controlled Physics-AI witness infrastructure
and a tested pinned DoMINO reference adapter. NOT a complete private app install.
The private live service remains separately authenticated and is not upgraded by
downloading this archive. No weights, private corpus, credentials, conversations,
employer data or raw CFD cases are included.

Read Aero/docs/PHYSICS_AI_REV_2_3_IMPLEMENTATION.md first. The reference inference
completed, but lift disagreed substantially with the published reference. Model
authority is RESEARCH_ONLY, applicability/physical validation NOT_ESTABLISHED.
Transolver remains a stub. Other benchmark/model integrations remain explicit
future work. No training or autonomous geometry optimization is implemented.

Extract into a new directory. In an isolated Python 3.12 environment:

    python -m pip install -r requirements-test.txt
    python -m pytest Aero/tests -q
    python -m Aero.physics_ai list

These tests do not download neural weights or launch CFD. Actual reference
inference requires the separately licensed/provisioned Linux CUDA environment,
an operator-owned worker configuration, and explicit research acknowledgement.
See the implementation guide. The package lock is reference-environment evidence,
not dependencies to install in the main Aero process. Source availability grants
no employer authorization and does not change upstream model/software licenses.

The base 2.2 ZIP is reused byte-for-byte internally except explicitly updated
files in SOURCE_MANIFEST.json. The historical ZIP itself is never changed.
Published text is LF-normalized and personal origins are replaced by examples.
