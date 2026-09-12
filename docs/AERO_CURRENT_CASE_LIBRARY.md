# Aero Current case library

The top-right **Saved cases** control in `/software/aero/current/` contains browser-local working copies plus versioned public example seeds. Opening a seed creates a copy under **My cases**; edits, confirmations, and chat persist in `aero.current.caseLibrary.v1`. Existing `aero.current.workspace.v1` records are migrated on first load. Users can create folders, rename/move/delete saved copies, and start a new case without erasing earlier ones. There is no account sync or VM access in this public page.

Seeds are defined in `src/data/aero-case-library.ts`. A seed must declare its primary source, exact scope, and one of two honest states:

- `setup`: cited study plan only; no Aero mesh/solver/result is implied. The NASA TMR NACA 0012 and AIAA DPW-6 CRM entries currently have this state.
- `recorded`: a local solver run has retained artifacts, linked in `evidence`. Current entries are the new OpenFOAM pitzDaily run and two earlier Aero nozzle examples. Recorded completion is distinct from engineering validation.

For a recorded seed, the browser compares the current requirement/equation inputs with the loaded baseline. Changing them marks linked results **historical; rerun required**. The previous artifacts remain accessible, but the page never represents them as outputs of an edited case. The browser cannot start a CFD job; that remains on the authenticated execution route. The public NACA and AIAA presets are not end-to-end runs until real geometry, mesh, solver, and verification artifacts have been produced and reviewed.

The pitzDaily evidence package is `public/demos/aero/textbook-pitzdaily/`; its full local field directories are in `Aero/reports/aero_current_pitzdaily_20260912/`. The public package contains `blockMesh`, `checkMesh`, and `simpleFoam` logs with SHA-256 hashes. `scripts/test-aero-case-library.mjs` verifies the artifact hashes and the browser behavior.
