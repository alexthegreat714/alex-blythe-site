import type {AeroSeed} from './aero-case-library';
const studies=[
  ['bracket','3D bracket / lug','A perforated cantilever bracket under a distributed 100 N tip load.','BRACKET'],
  ['tube','Pressure tube · axisymmetric','An open-ended, rotationally symmetric tube under 1 MPa bore pressure.','TUBE'],
  ['tube3d','Pressure tube · 3D comparison','The same tube solved as a full 3D solid; compare against the axisymmetric baseline.','TUBE'],
  ['port','Side-port tube · 3D escalation','A radial side port invalidates axisymmetry. Bore pressure only; cut-port faces unpressurized.','TUBE'],
  ['thermal-free','Thermal bar · free expansion','A uniform 50 K temperature increase; minimal symmetry-plane restraints allow expansion.','THERMAL_BAR'],
  ['thermal-fixed','Thermal bar · axial restraint','The same 50 K increase with both axial ends restrained.','THERMAL_BAR'],
  ['thermal-gradient','Thermal bar · prescribed gradient','An axial 50–80 K temperature increase with both ends restrained. Not a CFD-mapped field.','THERMAL_BAR'],
];
export const structuralSeeds:AeroSeed[]=studies.map(([id,title,summary,template])=>({
  id:`fea-${id}-20260912`,folder:'Structural studies',discipline:'FEA',title,summary,
  sourceLabel:'CalculiX structural verification · 12 September 2026',sourceUrl:'/demos/aero/fea-v1/README.html',status:'recorded',
  fields:{goal:summary,geometry:template==='BRACKET'?'Parametric perforated cantilever: L=100 mm, width=20 mm, height=10 mm, hole radius=2 mm at x=80 mm.':template==='TUBE'?'Parametric tube: bore radius=10 mm, thickness=2 mm, length=80 mm. Side-port variant adds a 3 mm radial cut.':'Parametric bar: L=100 mm, width=height=10 mm.',
    fluid:'Linear elastic assumed alloy: E=70 GPa, ν=0.3, α=23 µm/(m·K), yield=200 MPa. Constant properties; no material certification.',
    conditions:summary,success:'Preliminary stress limit 100 MPa; displacement limit 2 mm; yield factor of safety ≥1.5. Separate numerical checks; no design-release claim.',
    reference:template==='TUBE'?'Lamé open-ended tube; no port or local support effects.':template==='BRACKET'?'Euler–Bernoulli gross-section estimate; hole and clamp stress excluded.':'Independent thermal strain αΔT and axial constrained stress EαΔT; not back-calculated from FEA.'},
  equations:template==='TUBE'?[{title:'Lamé bore stress',latex:'\\sigma_\\theta(a)=p\\frac{a^2+b^2}{b^2-a^2},\\quad\\sigma_r(a)=-p,\\quad\\sigma_z=0',assumptions:'Open ends, isotropic elasticity, rotational symmetry, no port.'}]:template==='BRACKET'?[{title:'Gross-section bending',latex:'I=\\frac{bh^3}{12},\\quad\\delta=\\frac{FL^3}{3EI},\\quad\\sigma=\\frac{FLh}{2I}',assumptions:'Slender constant-section beam, ignoring the hole and clamp singularity.'}]:[{title:'Thermal expansion',latex:'\\varepsilon_{th}=\\alpha\\Delta T,\\quad u=\\alpha\\Delta T L,\\quad |\\sigma_{restrained}|=E\\alpha\\Delta T',assumptions:'Last relation is uniaxial axial restraint, not fully triaxial constraint.'}],
  build:{geometry:'Fixed CadQuery/OpenCascade template. Retained STEP/STL and geometry fingerprint; not arbitrary generative CAD.',mesh:'Three independently generated Gmsh meshes. Actual mesh overlay below; quality measured before ccx.',solve:'Linear CalculiX solve in a non-root, networkless, resource-limited worker. Retained results are not a new job.',results:'Measured fields, mesh sensitivity and requirement checks. Missing pressure equilibrium remains NOT_EVALUATED. Read the case evidence.'},
  surfaceUrl:`/demos/aero/fea-v1/${id}/surface.json`,
  evidence:{label:'Structural evidence',url:`/demos/aero/fea-v1/${id}/result.json`,secondary:[{label:'Approved case inputs',url:`/demos/aero/fea-v1/${id}/case.json`},{label:'Evidence manifest',url:`/demos/aero/fea-v1/${id}/manifest.json`}]},
  recordedGates:{solve:'warning'}
}));
