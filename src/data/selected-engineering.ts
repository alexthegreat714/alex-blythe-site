// Reading paths only. Numerical results and gate states remain in the retained records.
export const selectedEngineering = [
  {
    title: 'Aero Verification Bench',
    href: '/software/aero/verification/',
    discipline: 'CFD / analytical references',
    summary: 'I compared three pipe-grid cases against analytical pressure loss and retained intentional negative controls. Failed nozzle qualification and rejected CAD remain visible alongside the reference checks. Downloadable cases and evidence make the acceptance and rejection decisions reproducible.',
  },
  {
    title: 'Heat Exchanger Benchmark Program',
    href: '/software/aero/evidence/benchmarks/heat-exchanger-benchmark-program-v1/',
    discipline: 'Coupled thermal / fluid studies',
    summary: 'I organized analytical screening, reconstructed geometry, coupled CFD, and structural-transfer contracts around declared acceptance gates. The transfer study retains parametric geometry and unexecuted tolerance/FEA gates, not completed CAD or structural qualification. HX-S01 numerical failure and the analytical mismatch remain visible; engineering disposition is separate from solver completion.',
  },
  {
    title: 'Channel Pressure-Budget Study',
    href: '/software/aero/evidence/#channel-study',
    discipline: 'Requirements / bounded design decision',
    summary: 'I screened three channel gaps analytically, then compared nine CFD cases across three meshes per design against a 40 Pa pressure budget at 25 mL/s. The 2.5 mm gap was the smallest tested option meeting the budget with the declared numerical allowance. The record traces the requirement, decision criteria, and bounded disposition.',
  },
] as const;
