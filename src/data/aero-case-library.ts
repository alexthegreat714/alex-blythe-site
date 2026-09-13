import { verificationCaseSeeds } from './aero-verification-cases';
import { challengeCaseSeeds } from './aero-challenge-cases';
// Public, versioned teaching cases. A source reference is not a local CFD result.
// Only entries with recordedEvidence have retained local solver evidence.
export type AeroSeed = {
  id: string;
  folder: 'NACA studies' | 'AIAA studies' | 'Textbook & verified runs' | 'Structural studies';
  discipline?: 'FEA';
  surfaceUrl?: string;
  title: string;
  summary: string;
  sourceLabel: string;
  sourceUrl: string;
  status: 'setup' | 'recorded';
  fields: Partial<Record<'goal' | 'geometry' | 'fluid' | 'conditions' | 'success' | 'reference', string>>;
  equations: {title: string; latex: string; assumptions: string}[];
  build: {geometry: string; mesh: string; solve: string; results: string};
  evidence?: {label: string; url: string; secondary?: {label: string; url: string}[]};
  proofUrl?: string;
  recordedGates?: {mesh?: 'warning'; solve?: 'warning'};
};

export const aeroCaseSeeds: AeroSeed[] = [
  ...challengeCaseSeeds,
  ...verificationCaseSeeds,
  {
    id:'naca-0012-openfoam-tutorial-20260912',folder:'NACA studies',title:'NACA 0012 · OpenFOAM tutorial run',
    summary:'Actual 16,200-cell rhoSimpleFoam teaching run at 0° and 250 m/s. Solver converged in 1,581 iterations; mesh aspect-ratio check warned. Not NASA validation.',
    sourceLabel:'OpenFOAM Foundation v10 aerofoilNACA0012 tutorial',
    sourceUrl:'https://github.com/OpenFOAM/OpenFOAM-10/tree/master/tutorials/compressible/rhoSimpleFoam/aerofoilNACA0012',status:'recorded',
    fields:{
      goal:'Inspect a complete local NACA 0012 airfoil tutorial from geometry and mesh through solver convergence and lift/drag histories.',
      geometry:'OpenFOAM Foundation v10 NACA0012.obj tutorial airfoil; unit chord and one-cell spanwise 2D mesh.',
      fluid:'Perfect-gas air; steady compressible rhoSimpleFoam with k-omega SST RANS.',
      conditions:'Tutorial setup: 250 m/s freestream, 0° angle of attack, inlet temperature 298 K, outlet pressure 100 kPa.',
      success:'Inspect checkMesh warning, solver completion, final fields and force-coefficient history; do not call it NASA or AIAA validation.',
      reference:'OpenFOAM Foundation v10 aerofoilNACA0012 tutorial; locally executed 12 September 2026.'
    },
    equations:[{title:'Force coefficient',latex:'C_L=\\frac{L}{\\tfrac12\\rho_\\infty U_\\infty^2 A_{ref}},\\quad C_D=\\frac{D}{\\tfrac12\\rho_\\infty U_\\infty^2 A_{ref}}',assumptions:'The tutorial uses its own reference density and area; the published coefficients inherit those definitions.'}],
    build:{geometry:'Copied the installed OpenFOAM Foundation v10 NACA 0012 tutorial geometry.',mesh:'Ran blockMesh, transformPoints, extrudeMesh and checkMesh. 16,200 cells; 710 high-aspect cells caused one failed mesh check.',solve:'rhoSimpleFoam converged in 1,581 SIMPLE iterations. Final field directory and forceCoeffs data exist.',results:'Embedded proof shows CL≈0, CD≈0.00791, force history, source, hashes and all validation caveats.'},
    evidence:{label:'Proof document',url:'/demos/aero/naca0012-openfoam-tutorial/proof.html',secondary:[{label:'Machine-readable proof',url:'/demos/aero/naca0012-openfoam-tutorial/proof.json'},{label:'Mesh log',url:'/demos/aero/naca0012-openfoam-tutorial/log.checkMesh'},{label:'Solver log',url:'/demos/aero/naca0012-openfoam-tutorial/log.rhoSimpleFoam'}]},
    proofUrl:'/demos/aero/naca0012-openfoam-tutorial/proof.html',recordedGates:{mesh:'warning'}
  },
  {
    id: 'naca-0012-tmr', folder: 'NACA studies', title: 'NACA 0012 · NASA TMR validation',
    summary: 'Reference-backed airfoil validation setup. No Aero/OpenFOAM run is recorded for this case yet.',
    sourceLabel: 'NASA Turbulence Modeling Resource · NACA 0012',
    sourceUrl: 'https://turbmodels.larc.nasa.gov/naca0012numerics_val_sa_withpv.html', status: 'setup',
    fields: {
      goal: 'Reproduce and compare lift, drag, surface pressure, and skin friction for the NACA 0012 validation case.',
      geometry: 'NACA 0012 airfoil, unit chord. Obtain the official geometry and grid family before running; do not substitute a generic airfoil.',
      fluid: 'Air; compressible RANS with Spalart–Allmaras for a like-for-like NASA TMR comparison.',
      conditions: 'Reference condition: Mach 0.15, chord Reynolds number 6,000,000, angle of attack 10°. Farfield point-vortex treatment must match the selected reference series.',
      success: 'Compare CL, CD, Cp(x), Cf(x), residual/force history, and grid-refinement trend; document geometry and boundary-condition equivalence.',
      reference: 'NASA TMR NACA 0012 numerical-analysis results at M = 0.15, Re_c = 6 million, alpha = 10°.'
    },
    equations: [
      {title:'Chord Reynolds number',latex:'Re_c=\\frac{\\rho_\\infty U_\\infty c}{\\mu_\\infty}',assumptions:'Use the same reference properties and chord as the NASA case.'},
      {title:'Lift and drag coefficients',latex:'C_L=\\frac{L}{\\tfrac12\\rho_\\infty U_\\infty^2 c},\\qquad C_D=\\frac{D}{\\tfrac12\\rho_\\infty U_\\infty^2 c}',assumptions:'Two-dimensional force per unit span; compare like reference definitions.'}
    ],
    build: {
      geometry:'Acquire and verify the published NACA 0012 coordinates and unit-chord convention. This preset does not include a mesh file.',
      mesh:'Build a farfield airfoil grid family with wall resolution and documented growth/refinement; check cell quality and domain sensitivity.',
      solve:'Configure compressible RANS/SA, M 0.15, Re_c 6e6, alpha 10°, and the same farfield treatment as the selected NASA data series. No local execution is attached.',
      results:'Plot CL/CD, Cp, Cf, force histories, conservation, and grid convergence against NASA TMR. No Aero result exists yet.'
    }
  },
  {
    id:'aiaa-dpw6-case1-precursor-20260912',folder:'AIAA studies',title:'AIAA DPW-6 Case 1 · NACA 0012 precursor',
    summary:'Actual OpenFOAM run nominally matching Case 1 Mach/Re/AoA, converged in 1,045 iterations. Tutorial mesh and SST model differ from the official grid/reference: not a workshop submission.',
    sourceLabel:'AIAA DPW-6 requested test cases',sourceUrl:'https://aiaa-dpw.larc.nasa.gov/Workshop6/DPW6_Test_Cases_2015-10-21.pdf',status:'recorded',
    fields:{
      goal:'Explore the DPW-6 Case 1 flow-condition setup, an actual precursor solve, and the gaps to a defensible workshop verification result.',
      geometry:'NACA 0012 unit-chord geometry from the OpenFOAM Foundation v10 tutorial, not the official NASA grid family.',
      fluid:'Perfect-gas air; compressible steady rhoSimpleFoam with k-omega SST RANS. NASA reference-model comparison requires separate turbulence-model alignment.',
      conditions:'Nominal targets: Mach 0.15, chord Reynolds number 6,000,000, 10° angle of attack; T∞ 300 K, U∞ 52.1596945 m/s, p∞ 180684.56 Pa, dynamic viscosity 1.82e-5 Pa·s. The proof reports the slight actual gas-constant difference.',
      success:'Inspect force and residual histories, then replace the tutorial mesh with an accepted 500-chord grid family, resolve mesh warnings and compare Cp/Cf before validation.',
      reference:'AIAA DPW-6 Case 1 requested conditions and NASA TMR NACA 0012 numerical-analysis grids; current solve is a precursor only.'
    },
    equations:[{title:'Target Mach and Reynolds number',latex:'M=\\frac{U_\\infty}{\\sqrt{\\gamma RT_\\infty}}\\approx0.15,\\quad Re_c=\\frac{\\rho_\\infty U_\\infty c}{\\mu_\\infty}\\approx6\\times10^6',assumptions:'Perfect-gas air at 300 K, 1 m chord and the stated viscosity; exact derived values are in the proof.'}],
    build:{geometry:'Reused the actual NACA 0012 tutorial surface. The official NASA Family I source grid was also imported separately, but the attempted solve on that grid failed and is not used here.',mesh:'16,200-cell tutorial mesh. checkMesh reports 710 high-aspect cells; domain is roughly 50-100 chords rather than the specified 500.',solve:'Set Mach/Re/AoA physical inputs, then ran rhoSimpleFoam. SIMPLE converged in 1,045 iterations, with retained final fields and force coefficients.',results:'Embedded proof reports CL≈1.09034 and CD≈0.013379 with force history, failed-grid logs and explicit gates. This is not a like-for-like NASA/AIAA validated result.'},
    evidence:{label:'Proof document',url:'/demos/aero/aiaa-dpw6-case1-precursor/proof.html',secondary:[{label:'Machine-readable proof',url:'/demos/aero/aiaa-dpw6-case1-precursor/proof.json'},{label:'Mesh log',url:'/demos/aero/aiaa-dpw6-case1-precursor/log.checkMesh'},{label:'Solver log',url:'/demos/aero/aiaa-dpw6-case1-precursor/log.rhoSimpleFoam'}]},
    proofUrl:'/demos/aero/aiaa-dpw6-case1-precursor/proof.html',recordedGates:{mesh:'warning'}
  },
  {
    id: 'aiaa-dpw6-crm', folder: 'AIAA studies', title: 'AIAA DPW-6 · CRM drag study',
    summary: 'Workshop-aligned CRM wing-body / nacelle-pylon study plan. Geometry, grids, and a local solver run are not yet attached.',
    sourceLabel: 'NASA-hosted AIAA DPW-6 case forms', sourceUrl: 'https://aiaa-dpw.larc.nasa.gov/Workshop6/forms/DataForm.html', status: 'setup',
    fields: {
      goal: 'Compare the CRM wing-body and wing-body-nacelle-pylon configurations for the DPW-6 Case 2 drag-increment and grid-convergence study.',
      geometry: 'Common Research Model wing-body (Case 2A) and wing-body-nacelle-pylon (Case 2B). Obtain the official geometry and grid family; neither is bundled here.',
      fluid: 'Compressible external aerodynamics; select and document a workshop-compatible turbulence model and physical properties.',
      conditions: 'Use the exact DPW-6 Case 2 condition, reference definitions, and grid family from the official workshop package; not prefilled without a matching imported package.',
      success: 'Report grid metrics, total/component forces and moments, sectional cuts, and the 2B–2A drag increment using the workshop definitions.',
      reference: 'DPW-6 Case 2 data-submittal forms and gridding guidance; external workshop results are comparison data, not Aero results.'
    },
    equations: [{title:'Drag increment',latex:'\\Delta C_D=C_{D,\\mathrm{WBNP}}-C_{D,\\mathrm{WB}}',assumptions:'Both configurations must use the same reference area, flow condition, and compatible grid family.'}],
    build: {
      geometry:'Import and inspect the official CRM wing-body and nacelle-pylon configurations. Confirm units, surfaces, and reference area.',
      mesh:'Prepare matched grid families and record grid metrics for both configurations. No mesh is bundled in this browser preset.',
      solve:'Select a workshop-compatible compressible RANS solver and turbulence model, then run both configurations at the official condition. Not run in Aero yet.',
      results:'Compute force/moment and sectional metrics for each grid and the drag increment; compare to workshop submissions. No local CFD output is attached.'
    }
  },
  {
    id: 'textbook-pitzdaily-20260912', folder: 'Textbook & verified runs', title: 'Backward-facing step · pitzDaily',
    summary: 'Fresh OpenFOAM Foundation v10 tutorial run: 12,225-cell mesh checked; simpleFoam converged in 287 iterations. Teaching case, not design validation.',
    sourceLabel: 'OpenFOAM Foundation · pitzDaily tutorial', sourceUrl: 'https://openfoam.org/download/10-source/', status: 'recorded',
    fields: {
      goal: 'Inspect a steady backward-facing-step flow setup, mesh check, RANS solve, and convergence evidence.',
      geometry: 'OpenFOAM Foundation pitzDaily backward-facing-step tutorial geometry; two-dimensional domain, spanwise empty patch.',
      fluid: 'Incompressible Newtonian fluid, k-epsilon RANS; kinematic viscosity 1e-5 m²/s.',
      conditions: 'Uniform inlet velocity (10, 0, 0) m/s; no-slip upper/lower walls; tutorial outlet condition.',
      success: 'The tutorial mesh passes checkMesh and simpleFoam reports convergence. This is a solver demonstration, not comparison to experiment.',
      reference: 'OpenFOAM Foundation pitzDaily tutorial; local run on 12 Sep 2026.'
    },
    equations: [{title:'Reynolds number',latex:'Re=\\frac{UL}{\\nu}',assumptions:'Choose and document a characteristic step height L before interpreting the flow regime.'}],
    build: {
      geometry:'Copied the unmodified OpenFOAM Foundation v10 pitzDaily tutorial into an isolated container run directory.',
      mesh:'Ran blockMesh with the tutorial resource dictionary, then checkMesh. 12,225 hexahedra, 5 boundary patches, mesh OK.',
      solve:'Ran simpleFoam (steady incompressible k-epsilon RANS). SIMPLE solution converged in 287 iterations; the final field time directory was written.',
      results:'Solver logs and field outputs were retained locally. Public evidence includes the mesh check and terminal solver log; no independent experimental validation or field render is claimed.'
    },
    evidence: {label:'Proof document',url:'/demos/aero/textbook-pitzdaily/proof.html',secondary:[{label:'Machine-readable proof',url:'/demos/aero/textbook-pitzdaily/proof.json'},{label:'Mesh check log',url:'/demos/aero/textbook-pitzdaily/log.checkMesh'},{label:'Solver log',url:'/demos/aero/textbook-pitzdaily/log.simpleFoam'}]},
    proofUrl:'/demos/aero/textbook-pitzdaily/proof.html'
  },
  {
    id: 'textbook-nozzle-wall-v6', folder: 'Textbook & verified runs', title: 'Nozzle · wall-refinement proof',
    summary: 'Recorded rhoSimpleFoam nozzle run with CAD/mesh manifests and numerical gates. Not a flight-design validation.',
    sourceLabel: 'Aero public engineering evidence',sourceUrl:'/demos/aero/wall-refinement-v6/engineering-result.json',status:'recorded',
    fields: {
      goal:'Inspect the end-to-end wall-refined axisymmetric nozzle CFD workflow and its numerical/evidence gates.',
      geometry:'Parametric axisymmetric converging-diverging nozzle wedge generated with CadQuery/OpenCascade; retained STEP/STL/mesh hashes.',
      fluid:'Compressible steady flow solved with OpenFOAM rhoSimpleFoam.',
      conditions:'Use the exact retained boundary conditions in the linked engineering result; do not infer unreported design conditions.',
      success:'Check geometry/mesh manifests, residual and conservation gates, and compare with an independent reference before design use.',
      reference:'Aero retained CFD evidence; independent physical validation remains not established.'
    },
    equations:[{title:'Mass conservation',latex:'\\dot m_{\\mathrm{in}}-\\dot m_{\\mathrm{out}}\\approx 0',assumptions:'Numerical conservation alone does not validate the physical model.'}],
    build:{geometry:'CadQuery/OpenCascade generated an axisymmetric nozzle wedge with dimension and topology checks.',mesh:'Gmsh generated a wall-refined mesh; the linked manifest records 25,596 nodes and 12,600 volume elements.',solve:'rhoSimpleFoam completed the retained production proof run. See numerical gates in the linked result.',results:'Open the retained engineering-result JSON and demo visualization. The independent-validation gate remains open.'},
    evidence:{label:'Proof document',url:'/software/aero/report/',secondary:[{label:'Engineering result',url:'/demos/aero/wall-refinement-v6/engineering-result.json'},{label:'Explore visual proof',url:'/software/aero/demo/'}]},
    proofUrl:'/software/aero/report/'
  },
  {
    id: 'textbook-nozzle-precursor',folder:'Textbook & verified runs',title:'Nozzle · compressible precursor',
    summary:'Recorded 864-cell rhoSimpleFoam teaching run and mesh study. Energy-conservation gate remains unresolved.',
    sourceLabel:'Aero public precursor case',sourceUrl:'/demos/aero/nozzle-precursor/case.json',status:'recorded',
    fields:{goal:'Explore a bounded compressible-nozzle teaching run from geometry to solver evidence.',geometry:'Planar 2D converging-diverging passage; 0.3 m long, one cell through a 0.012 m span.',fluid:'Perfect-gas air, laminar, adiabatic walls; OpenFOAM rhoSimpleFoam.',conditions:'Mass-flow inlet 0.01 kg/s at 300 K; fixed outlet static pressure 101325 Pa.',success:'Review solver and mesh evidence while recognizing the unresolved energy-conservation and validation gates.',reference:'No independent geometry/experiment reference is attached.'},
    equations:[{title:'Continuity',latex:'\\dot m=\\rho U A',assumptions:'A prescribed mass-flow inlet does not demonstrate choking.'}],
    build:{geometry:'Parametric planar nozzle with documented axial stations and half-heights.',mesh:'Four-block, 864-cell structured precursor mesh; separate three-grid study is retained.',solve:'rhoSimpleFoam executed and wrote final artifacts; the numerical disposition is NOT_ESTABLISHED because the energy gate blocks.',results:'Explore telemetry, mesh study, gate list, and the engineering result. Do not treat completion as validated physics.'},
    evidence:{label:'Proof document',url:'/demos/aero/nozzle-precursor/proof.html',secondary:[{label:'Case & settings',url:'/demos/aero/nozzle-precursor/case.json'},{label:'Mesh study',url:'/demos/aero/nozzle-precursor/mesh-study.json'},{label:'Solver evidence',url:'/demos/aero/nozzle-precursor/engineering-result.json'},{label:'Result view',url:'/demos/aero/nozzle-precursor/images/result.svg'}]},
    proofUrl:'/demos/aero/nozzle-precursor/proof.html',recordedGates:{solve:'warning'}
  }
];
