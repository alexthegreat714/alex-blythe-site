# Challenge 01: input freeze v1

This is an actual input freeze, not a completed CFD benchmark or frozen acceptance criterion.

The input package selects NASA TM-4074 Table XIII, first subtable: NACA 0012,
Mach 0.15, chord Reynolds number 5.95 million, localized No. 180 grit transition
strips. All 18 operating points are retained, including both near-zero points.
The 36 measured CL/CD observations are encrypted in `reference.enc`.

`input.json` is the only document permitted in the fresh planning review.
`custody.json` explains source rights, transcription checks and role limitations.
`reference-metadata.json` contains SHA-256 commitments, not measurement values.
`state.json` records when these exact bytes were frozen.

The original source PDF, plaintext extraction and encryption key are retained
outside the website repository with restricted local account permissions. No
plaintext measurements or key belong in this download before prediction freeze.

Source selection/curation were not blind. Runtime reference withholding applies
to the separate predictor, not to the custodian. One exposed custodian performed
image/transcription review and a printed-ratio consistency check; this is not dual
independent human review. Model pretraining familiarity cannot be excluded.

Input unknowns are explicit. Exact measured coordinates, trailing-edge convention,
test-series temperature, turbulence level and trip-height equivalence are not
invented. Input freeze preserves those facts; it does not declare them sufficient
for a validated numerical model. Solver criteria and assumptions require a
separate input-only review and public preregistration before production solving.

NASA source: https://ntrs.nasa.gov/citations/19880019495

Original PDF SHA-256:
`8e466706cbdf54b3c778ea2b089c4f52d87686bf7f6b1bd10d224b42c2d06902`
