import type { AeroSeed } from './aero-case-library';
import snapshot from '../../public/demos/aero/blind-validation-01-run-v1/current-status.json';

const page='/software/aero/evidence/benchmarks/blind-validation-01/';
const assets='/demos/aero/blind-validation-01-run-v1/';
// No case or hidden measurements enter the library until comparison occurred.
// Edited browser inputs invalidate the attached original evidence as usual.
export const challengeCaseSeeds: AeroSeed[] = snapshot.has_comparison && snapshot.has_paper ? [{
  id:'external-challenge01-run-v1',folder:'NACA studies',
  title:`External Benchmark · Challenge 01 · ${snapshot.result}`,
  summary:`Frozen NACA 0012 production case: 18 angles × three meshes. Overall ${snapshot.result}. Reference withheld from solver execution; supervisory setup was not fully blinded.`,
  sourceLabel:'NASA TM-4074 · Table XIII, first subtable',
  sourceUrl:'https://ntrs.nasa.gov/citations/19880019495',status:'recorded',
  fields:{
    goal:'Audit the complete frozen lift/drag polar against the independent experiment, retaining numerical failures and every operating point.',
    geometry:'Nominal NACA 0012, chord 0.601 m; projected C-grid and one 0.00601 m empty span cell. Exact as-built coordinates were not available.',
    fluid:'Air, low-Mach incompressible steady RANS; kOmegaSSTLM transition model. Mach 0.15 and chord Reynolds number 5.95 million. Temperature 288.15 K and inlet turbulence intensity 0.1% are assumptions.',
    conditions:'18 angles from -3.99° to 19.27°. Prescribed intermittency near the surface approximates transition at x/c=0.05; it does not resolve the experimental grit strip or its drag.',
    success:'Frozen bounds: CL RMSE <=0.10 and max error <=0.20; CD RMSE <=0.005 and max error <=0.010. Numerical, conservation, stationarity, grid and fine-wall y+ gates must separately pass.',
    reference:'NASA TM-4074 (Ladson, 1988), Table XIII first subtable. All 36 CL/CD measurements were revealed only after prediction commitment. Source-exposed supervisory setup is disclosed.'
  },
  equations:[{title:'Force coefficients and Reynolds number',latex:'C_L=\\frac{L}{\\tfrac12\\rho U_\\infty^2 cb},\\quad C_D=\\frac{D}{\\tfrac12\\rho U_\\infty^2 cb},\\quad \\nu=\\frac{U_\\infty c}{Re_c}',assumptions:'Nominal two-dimensional steady RANS; kinematic-pressure coefficient normalization. SIMPLE iteration averages are not physical-time averages.'}],
  build:{
    geometry:'Retained nominal airfoil surface, projected mesh generator and dimensional transform; no exact as-built reconstruction is claimed.',
    mesh:'Three frozen refinement levels at every angle. Actual meshes, raw quality warnings, final wall y+ values and per-file hashes are downloadable.',
    solve:'54 independent simpleFoam attempts, 2,000 SIMPLE iterations each under a two-hour case timeout. Inspect the actual receipts and failed gates; completion is not convergence.',
    results:`Original result: ${snapshot.result}. The embedded report retains the entire polar, all errors and numerical evidence. Changing these fields does not recompute or replace that frozen experiment.`
  },
  evidence:{label:'Full experiment and chronology',url:page,secondary:[{label:'Technical paper',url:assets+'report/paper.pdf'},{label:'Reproduction package',url:assets+'reproduction.zip'},{label:'Every case archive',url:assets+'evidence/run-index.json'}]},
  proofUrl:page,recordedGates:{mesh:'warning',...(snapshot.result==='PASS'?{}:{solve:'warning' as const})}
}] : [];
