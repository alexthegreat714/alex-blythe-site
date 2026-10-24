# Square-body scalar transport, version 1.0

Public page: https://alex-blythe.com/software/aero/square-body-transport/

This is steady scalar convection-diffusion in a prescribed horizontal velocity
field. The square holds scalar values. Velocity, pressure, drag and vortex
shedding are not solved. No experimental validation or design release is claimed.

## Use

Open Square_Body_Transport.xlsx in desktop Excel. Change amber inputs on Model.
Use iterative calculation with 10,000 iterations and maximum change 1E-10.
Press F9 if needed. The workbook contains no macros or external workbook links.

Read paper.pdf for the governing equations, numerical accuracy and examples.
The complete LaTeX source and figures are in paper-sources.zip.

The browser solver is solver.mjs and its worker is worker.mjs. Run them from
the public page or an HTTP server; module workers do not run from file URLs.
The browser worker message protocol was checked in a Node harness. This is
not cross-browser UI validation.

## Reproduce the independent numerical checks

Extract reproducibility.zip into a new directory, then run:

    python -m pip install -r requirements.txt
    python verify_accuracy.py --output .

This reconstructs the sparse LU, analytical and mesh-refinement checks and
figures. It reads the supplied workbook-reference.json and Excel summary.
It does not rerun Excel. Recorded desktop Excel checks are identified in
excel-verification.json. browser-solver-checks.json records JavaScript and
worker-harness checks. accuracy-results.json states the measured numerical
results; its passing checks do not establish physical accuracy.

Boundary values: inlet scalar 1, square scalar 0, zero-gradient outlet and
top/bottom. Domain 3 m by 2 m; square side 0.5 m, corner (0.8 m,0.75 m).
Domain and square dimensions are reconstruction assumptions. Visible
screenshot inputs rho=1, u=1, Gamma=0.1 and spacing=0.05 are reproduced.
Teaching inspiration: https://www.instagram.com/cfdbyhand/ . This is an
independently authored reconstruction, not the original workbook.

The CSV files contain x_m,y_m,phi,clamped_square. All figures use original
computed fields, not copied social-media images. manifest.json contains
SHA-256 hashes for public release files. Package hashes are in
download-checksums.json. Hashes establish identity, not scientific validity.
