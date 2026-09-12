# Aero automatic LaTeX paper — PDF revision 1.0

Verified 12 September 2026. The bounded public channel study now requires a
compiled paper before declaring its job complete. This is a numerical technical
report, not a peer-reviewed paper or physical-device validation certificate.

## Delivered artifacts

- Permanent eight-page worked paper: `/demos/aero/channel-study-v1/research-paper.pdf`.
- Source/evidence bundle: `/demos/aero/channel-study-v1/research-paper-sources.zip`.
- Manifest: `/demos/aero/channel-study-v1/research-paper-manifest.json`.
- Each new completed job: `/study/runs/<capability-id>/paper`, linked in Results.
- Each new evidence ZIP includes `paper.pdf`, `cases/paper/paper.tex`, vector/PNG
  figures, source result JSON, original solver files/logs and SHA-256 manifest.

The permanent paper is tied to the previously completed, model-assisted public
browser run `c285c4d248f1f2f8dc00ae43e01fae051e29f2c0f136250a`. Its three real
browser screenshots show requirements, planned mesh, and computed results. Its
bundle has 200 hashed artifacts. The original solver evidence is preserved;
the new package adds the paper and its sources. It contains no invented UI images.

Routine jobs produce five numerical pages automatically. They do not capture a
visitor's screen. Those pages contain source-owned equations, a decision chart,
three-grid pressure/error comparison, residual history, actual computed fields,
velocity-profile verification, all-nine-run gate table and reproducibility
hashes. Screenshots can be appended by the maintainer only when the browser
receipt's run ID matches the result exactly.

## Fresh end-to-end acceptance

Run: `7d1fe0ecc6a6501bbfdc4ae0af9546f83b1531dc14cef5af`.

Inputs: 200 mm length, 2 mm nominal gap, 25 mL/s, 40 Pa budget.

- Real public OpenFOAM endpoint; staged browser assets on the website origin.
- Nine solves completed in 31.53 seconds, excluding paper generation.
- All numerical checks passed; smallest passing tested gap: 2.5 mm.
- PDF compiled inside the actual network-free, non-root worker with its existing
  768 MiB memory / 2 CPU limits. No changes to private VM access or inference.
- Browser Results PDF link returned HTTP 200, application/pdf, valid PDF signature.
- Five pages parsed and every page visually inspected after Poppler rendering.
- All 201 evidence artifact hashes verified; PDF and ZIP hashes match API status.
- API PDF SHA-256: `dd3193e5b9b122b8cac923a79d7b6056ddff5903dad9cb6433366d9ac7f5f65f`.
- Refresh resumed the same job; editing reviewed inputs invalidated current proof.
- Browser checks passed at desktop, 900 px and 390 px; no page errors.
- Ten study unit tests passed, including TeX escaping and compile timeout/failure.
- All eight pages of the permanent worked paper were also rendered and inspected.

Local detailed receipt: `.qa/channel-study/pdf-browser/acceptance.json`, with
matching `status.json`, downloaded PDF/ZIP and screenshots. The model was not
called again in this PDF-only regression run; the earlier model evidence remains
in the worked example. Live job URLs expire after 48 hours; permanent published
paper and source bundle do not.

## Failure behavior and reproduction

The worker remains running during figure/PDF generation. It allows 90 seconds
for the fixed paper process and 35 seconds per pdflatex pass, with shell escape
disabled. Failure produces a failed job and diagnostic logs, not a completed job
with a missing PDF. Only trusted template code and validated numerical results
enter this pipeline; there is no arbitrary public LaTeX execution endpoint.

Regenerate a worked paper from matching result/receipt files:

```sh
python services/study/paper.py result.json output/pdf/channel-study --screenshots matching-browser-receipt-folder --prepare-only
# Compile paper.tex with the documented LaTeX runtime; inspect every rendered page.
python scripts/package-aero-paper.py output/pdf/channel-study original-evidence.zip public/demos/aero/channel-study-v1
```

The packager verifies every original solver-artifact hash and exact result
identity before adding the paper. `scripts/test-aero-study.mjs` now verifies the
PDF endpoint and accepts `AERO_STUDY_OUTPUT` to preserve earlier browser receipts.
