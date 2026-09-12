// Public, versioned teaching cases. A source reference is not a local CFD result.
// Only entries with recordedEvidence have retained local solver evidence.
export type AeroSeed = {
  id: string;
  folder: 'NACA studies' | 'AIAA studies' | 'Textbook & verified runs';
  title: string;
  summary: string;
  sourceLabel: string;
  sourceUrl: string;
  status: 'setup' | 'recorded';
  fields: Partial<Record<'goal' | 'geometry' | 'fluid' | 'conditions' | 'success' | 'reference', string>>;
  equations: {title: string; latex: string; assumptions: string}[];
  build: {geometry: string; mesh: string; solve: string; results: string};
  evidence?: {label: string; url: string; secondary?: {label: string; url: string}[]};
};

export const aeroCaseSeeds: AeroSeed[] = [
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
    sourceLabel: 'OpenFOAM Foundation · pitzDaily tutorial', sourceUrl: 'https://openfoam.org/download/8-source/', status: 'recorded',
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
    evidence: {label:'Run summary & hashes',url:'/demos/aero/textbook-pitzdaily/evidence.json',secondary:[{label:'Mesh check log',url:'/demos/aero/textbook-pitzdaily/log.checkMesh'},{label:'Solver log',url:'/demos/aero/textbook-pitzdaily/log.simpleFoam'}]}
  },
  {
    id: 'textbook-nozzle-wall-v6', folder: 'Textbook & verified runs', title: 'Nozzle · wall-refinement proof',
    summary: 'Recorded rhoSimpleFoam nozzle run with CAD/mesh manifests and numerical gates. Not a flight-design validation.',
    sourceLabel: 'Aero public engineering evidence',sourceUrl:'/demos/aero/wall-refinement-v6/engineering-result.json',status:'recorded',
    fields: {
      goal:'Inspect the end-to-end wall-resolved axisymmetric nozzle CFD workflow and its numerical/evidence gates.',
      geometry:'Parametric axisymmetric converging-diverging nozzle wedge generated with CadQuery/OpenCascade; retained STEP/STL/mesh hashes.',
      fluid:'Compressible steady flow solved with OpenFOAM rhoSimpleFoam.',
      conditions:'Use the exact retained boundary conditions in the linked engineering result; do not infer unreported design conditions.',
      success:'Check geometry/mesh manifests, residual and conservation gates, and compare with an independent reference before design use.',
      reference:'Aero retained CFD evidence; independent physical validation remains not established.'
    },
    equations:[{title:'Mass conservation',latex:'\\dot m_{\\mathrm{in}}-\\dot m_{\\mathrm{out}}\\approx 0',assumptions:'Numerical conservation alone does not validate the physical model.'}],
    build:{geometry:'CadQuery/OpenCascade generated an axisymmetric nozzle wedge with dimension and topology checks.',mesh:'Gmsh generated a wall-resolved mesh; the linked manifest records 25,596 nodes and 12,600 volume elements.',solve:'rhoSimpleFoam completed the retained production proof run. See numerical gates in the linked result.',results:'Open the retained engineering-result JSON and demo visualization. The independent-validation gate remains open.'},
    evidence:{label:'Engineering result',url:'/demos/aero/wall-refinement-v6/engineering-result.json',secondary:[{label:'Explore visual proof',url:'/software/aero/demo/'}]}
  },
  {
    id: 'textbook-nozzle-precursor',folder:'Textbook & verified runs',title:'Nozzle · compressible precursor',
    summary:'Recorded 864-cell rhoSimpleFoam teaching run and mesh study. Energy-conservation gate remains unresolved.',
    sourceLabel:'Aero public precursor case',sourceUrl:'/demos/aero/nozzle-precursor/case.json',status:'recorded',
    fields:{goal:'Explore a bounded compressible-nozzle teaching run from geometry to solver evidence.',geometry:'Planar 2D converging-diverging passage; 0.3 m long, one cell through a 0.012 m span.',fluid:'Perfect-gas air, laminar, adiabatic walls; OpenFOAM rhoSimpleFoam.',conditions:'Mass-flow inlet 0.01 kg/s at 300 K; fixed outlet static pressure 101325 Pa.',success:'Review solver and mesh evidence while recognizing the unresolved energy-conservation and validation gates.',reference:'No independent geometry/experiment reference is attached.'},
    equations:[{title:'Continuity',latex:'\\dot m=\\rho U A',assumptions:'A prescribed mass-flow inlet does not demonstrate choking.'}],
    build:{geometry:'Parametric planar nozzle with documented axial stations and half-heights.',mesh:'Four-block, 864-cell structured precursor mesh; separate three-grid study is retained.',solve:'rhoSimpleFoam executed and wrote final artifacts; the numerical disposition is NOT_ESTABLISHED because the energy gate blocks.',results:'Explore telemetry, mesh study, gate list, and the engineering result. Do not treat completion as validated physics.'},
    evidence:{label:'Case & settings',url:'/demos/aero/nozzle-precursor/case.json',secondary:[{label:'Mesh study',url:'/demos/aero/nozzle-precursor/mesh-study.json'},{label:'Solver evidence',url:'/demos/aero/nozzle-precursor/engineering-result.json'},{label:'Result view',url:'/demos/aero/nozzle-precursor/images/result.svg'}]}
  }
];
