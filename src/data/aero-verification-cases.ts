import type { AeroSeed } from './aero-case-library';
import results from '../../public/demos/aero/verification-bench-v1/summary.json';
const path='/software/aero/verification/';
const assets='/demos/aero/verification-bench-v1/';
export const verificationCaseSeeds: AeroSeed[] = results.pipe.filter(r=>['pipe-fine','pipe-underresolved','pipe-wrong-viscosity'].includes(r.id)).map(r=>({
  id:`verification-${r.id}-v1`,folder:'Textbook & verified runs',
  title:`Pipe Re 200 · ${r.id.replace('pipe-','').replaceAll('-',' ')} · ${r.status==='ACCEPTED'?'PASS':'FAIL'}`,
  summary:`Recorded OpenFOAM case: ${r.pressure_drop_pa.toFixed(6)} Pa against 0.64 Pa; ${r.reference_error_pct.toFixed(3)}% error. ${r.status}. Fixed-stop run with disclosed scale-aware residual gate.`,
  sourceLabel:'OpenStax Poiseuille reference · Aero Verification Bench Rev 1.0',sourceUrl:results.reference_url,status:'recorded',
  fields:{goal:'Verify the declared laminar-pipe pressure gradient, retaining any measured failures.',geometry:'Circular pipe D=10 mm, L=100 mm; one-degree axisymmetric wedge.',fluid:`Declared water: density 1000 kg/m³, nu=1e-6 m²/s. Actual deck viscosity multiplier: ${r.viscosity_multiplier}; a mismatch fails the original requirement.`,conditions:'Fully developed parabolic inlet, bulk speed 0.02 m/s, no-slip walls, outlet pressure fixed. Declared Reynolds number 200.',success:'Pressure-gradient error <=2%; boundary imbalance <=0.1%; complete mesh/solve evidence and scale-aware residual checks. No experimental validation claimed.',reference:'Poiseuille: delta p=32 mu U L/D²=0.64 Pa; Darcy f=64/Re=0.32. Fit interior pressure gradient over x=25–75 mm and multiply by full length.'},
  equations:[{title:'Pipe pressure reference',latex:'\\Delta p=\\frac{32\\mu U_b L}{D^2}=0.64\\;\\mathrm{Pa},\\quad f_D=\\frac{64}{Re}=0.32',assumptions:'Steady, incompressible, Newtonian, fully developed circular pipe. Reference viscosity remains the declared value even in the wrong-viscosity negative control.'}],
  build:{geometry:'Generated circular-pipe wedge, not a nozzle. Original blockMeshDict and mesh are archived.',mesh:`${r.cells} cells. checkMesh passed; mesh validity alone does not establish pressure accuracy.`,solve:`simpleFoam reached 1800 iterations. ${r.status}; failed checks: ${r.failed_checks.join(', ')||'none under the explicit scale-aware gate'}. Built-in convergence flag remains false.`,results:`Measured pressure drop ${r.pressure_drop_pa.toFixed(6)} Pa. Reference error ${r.reference_error_pct.toFixed(3)}%. Review the protocol correction, conservation plot and permanent decks in the embedded bench.`},
  evidence:{label:'Verification Bench',url:path+'?case='+r.id+'#pipe',secondary:[{label:'PDF paper',url:assets+'paper.pdf'},{label:'Complete hashed decks',url:assets+'reproducibility.zip'}]},
  proofUrl:path+'?case='+r.id+'#pipe',recordedGates:r.status==='ACCEPTED'?{}:{solve:'warning'},
}));
