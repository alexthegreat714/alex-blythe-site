/** Structured Engineering Notebook for the bounded nozzle precursor.
 * First-order values use case inputs only; they never read CFD output.
 */
import type { EquationBlock, FirstOrderAnalysis, NotebookSection } from './case';

const MDOT = 0.010;
const P_REF = 101325;
const T_REF = 300;
const R_AIR = 287;
const GAMMA = 1.4;
const AREA = Math.PI * 0.02 ** 2;
const RHO_REF = P_REF / (R_AIR * T_REF);
const V_REF = MDOT / (RHO_REF * AREA);
const A_REF = Math.sqrt(GAMMA * R_AIR * T_REF);
const M_REF = V_REF / A_REF;
const Q_REF = 0.5 * RHO_REF * V_REF ** 2;

const CONTINUITY: EquationBlock = {
  title: 'Steady mass continuity', latex: String.raw`\dot{m} = \rho A V`,
  symbols: [
    { symbol: 'ṁ', meaning: 'mass-flow rate', units: 'kg/s' },
    { symbol: 'ρ', meaning: 'density', units: 'kg/m³' },
    { symbol: 'A', meaning: 'flow area', units: 'm²' },
    { symbol: 'V', meaning: 'area-mean normal velocity', units: 'm/s' },
  ],
  meaning: 'Sets an independent inlet velocity scale from case inputs before OpenFOAM is run.',
  source: 'ANALYTICAL',
};

const IDEAL_GAS: EquationBlock = {
  title: 'Ideal-gas reference density', latex: String.raw`\rho = \frac{p}{R T}`,
  symbols: [
    { symbol: 'p', meaning: 'absolute reference pressure', units: 'Pa' },
    { symbol: 'R', meaning: 'specific gas constant for air', units: 'J/(kg K)' },
    { symbol: 'T', meaning: 'absolute reference temperature', units: 'K' },
  ],
  meaning: 'Provides a reference density for low-speed screening, not a solved density field.',
  source: 'ANALYTICAL',
};

const MACH: EquationBlock = {
  title: 'Reference Mach number', latex: String.raw`M = \frac{V}{\sqrt{\gamma R T}}`,
  symbols: [
    { symbol: 'M', meaning: 'Mach number' },
    { symbol: 'γ', meaning: 'heat-capacity ratio' },
    { symbol: 'V', meaning: 'reference mean velocity', units: 'm/s' },
  ],
  meaning: 'Screens the expected inlet regime independently of the numerical solution.',
  source: 'ANALYTICAL',
};

const DIFFERENTIAL_CONTINUITY: EquationBlock = {
  title: 'Conservation of mass',
  latex: String.raw`\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0`,
  symbols: [
    { symbol: '∂ρ/∂t', meaning: 'density accumulation; zero in the selected steady model' },
    { symbol: '∇·(ρu)', meaning: 'net mass flux from a control volume' },
  ],
  meaning: 'The evidence harness checks the solver patch-flux balance against this requirement.',
  source: 'ANALYTICAL',
};

export const sections: NotebookSection[] = [
  { id: 'problem', index: '01', title: 'Problem', body: [
    'Evaluate steady compressible air flow through the approved converging-diverging nozzle and determine whether pressure drop is stable across the predeclared wall-resolved mesh family.',
  ] },
  { id: 'requirements-knowns', index: '02', title: 'Requirements / knowns', body: [
    'Use the fixed rhoSimpleFoam chain, deterministic case template, and every predeclared required gate.',
  ], values: [
    { label: 'Commanded mass flow', value: MDOT.toFixed(3), units: 'kg/s', source: 'USER_INPUT' },
    { label: 'Reference pressure', value: String(P_REF), units: 'Pa', source: 'CASE_CONFIGURATION' },
    { label: 'Reference temperature', value: String(T_REF), units: 'K', source: 'CASE_CONFIGURATION' },
    { label: 'Unknown fields', value: 'p, U, T, rho', source: 'CASE_CONFIGURATION' },
  ] },
  { id: 'assumptions', index: '03', title: 'Assumptions', body: [
    'Steady, compressible perfect-gas air; one-degree axisymmetric wedge; k-omega SST turbulence model; adiabatic no-slip wall; fixed reviewed inlet turbulence quantities.',
  ] },
  { id: 'physics', index: '04', title: 'Governing physics', equations: [DIFFERENTIAL_CONTINUITY, IDEAL_GAS, CONTINUITY, MACH] },
  { id: 'first-order', index: '05', title: 'First-order analysis', body: [
    `Reference density ${RHO_REF.toFixed(4)} kg/m³, inlet velocity ${V_REF.toFixed(3)} m/s, Mach ${M_REF.toFixed(4)}, and dynamic-pressure scale ${Q_REF.toFixed(1)} Pa.`,
    'These are ANALYTICAL screening values computed before solving. Independent pressure drop is NOT YET ESTABLISHED because the inputs do not justify a fully-developed loss model.',
  ] },
  { id: 'geometry', index: '06', title: 'Geometry', body: [
    'PARAMETRIC GENERATED - deterministic nozzle with 20 mm inlet radius, 8 mm throat radius, 24 mm exit radius, 45 mm converging length, and 110 mm diverging length. This is not unrestricted text-to-CAD.',
  ] },
  { id: 'boundary-conditions', index: '07', title: 'Boundary conditions', values: [
    { label: 'Inlet U', value: 'flowRateInletVelocity / one-degree mass fraction', source: 'CASE_CONFIGURATION' },
    { label: 'Outlet p', value: '101325', units: 'Pa', source: 'CASE_CONFIGURATION' },
    { label: 'Inlet T', value: '300', units: 'K', source: 'CASE_CONFIGURATION' },
    { label: 'Walls', value: 'no-slip / adiabatic', source: 'CASE_CONFIGURATION' },
  ] },
  { id: 'model-fidelity', index: '08', title: 'Fidelity / model selection', body: [
    'Steady compressible k-omega SST model. Numerical acceptability and mesh independence passed, while external validation, wall-resolution suitability, and fitness for a design decision remain NOT YET ESTABLISHED.',
  ] },
  { id: 'numerical-method', index: '09', title: 'Numerical method', values: [
    { label: 'Solver', value: 'OpenFOAM rhoSimpleFoam', source: 'CASE_CONFIGURATION' },
    { label: 'Mesher', value: 'CadQuery + Gmsh transfinite wedge, 12,600 cells at Level 4', source: 'CASE_CONFIGURATION' },
    { label: 'Execution', value: 'isolated fixed worker chain', source: 'CASE_CONFIGURATION' },
  ] },
  { id: 'acceptance', index: '10', title: 'Predeclared acceptance criteria', body: [
    'Before execution: completion artifacts; mesh quality; residual ≤ 1×10⁻⁴; mass imbalance ≤ 1%; energy imbalance ≤ 2%; outlet-flow variation ≤ 1% over 20 samples.',
    'Readiness additionally requires a validation reference, substantiated fidelity claims, and at least two eligible mesh levels agreeing within 2%. Missing required evidence blocks establishment.',
  ] },
  { id: 'execution', index: '11', title: 'Execution', body: [
    'The retained Level 4 run completed 4,200 outer iterations through the isolated worker. Process exit alone was not treated as engineering success; all required numerical evidence was finalized afterward.',
  ] },
  { id: 'evidence', index: '12', title: 'Evidence', body: [
    'The Aero/cfd/evidence.py contract is authoritative. Residual, conservation, and monitor charts use parsed OpenFOAM telemetry only.',
  ] },
  { id: 'interpretation', index: '13', title: 'Interpretation', body: [
    'Numerical acceptability is PASS and the predeclared 2% pressure-drop mesh-independence gate is PASS. Overall design readiness remains NOT ESTABLISHED because validation and intended-use fidelity are not established.',
  ] },
];

export const firstOrder: FirstOrderAnalysis = {
  title: 'Independent inlet regime screening',
  inputs: [
    { label: 'Commanded mass flow', value: MDOT.toFixed(3), units: 'kg/s', source: 'USER_INPUT' },
    { label: 'Reference state', value: `${P_REF} Pa / ${T_REF} K`, source: 'CASE_CONFIGURATION' },
    { label: 'Inlet area', value: AREA.toExponential(3), units: 'm²', source: 'CASE_CONFIGURATION' },
  ],
  equation: CONTINUITY,
  estimate: { label: 'Reference inlet velocity', value: V_REF.toFixed(3), units: 'm/s' },
  expectedTrend: 'Increasing mass flow raises reference velocity and Mach linearly and the dynamic-pressure scale approximately quadratically.',
  numericalResult: null,
  comparison: null,
};

export function mathml(block: EquationBlock): string {
  const table: Record<string, string> = {
    [String.raw`\dot{m} = \rho A V`]: '<mrow><mover><mi>m</mi><mo>˙</mo></mover><mo>=</mo><mi>ρ</mi><mi>A</mi><mi>V</mi></mrow>',
    [String.raw`\rho = \frac{p}{R T}`]: '<mrow><mi>ρ</mi><mo>=</mo><mfrac><mi>p</mi><mrow><mi>R</mi><mi>T</mi></mrow></mfrac></mrow>',
    [String.raw`M = \frac{V}{\sqrt{\gamma R T}}`]: '<mrow><mi>M</mi><mo>=</mo><mfrac><mi>V</mi><msqrt><mi>γ</mi><mi>R</mi><mi>T</mi></msqrt></mfrac></mrow>',
    [String.raw`\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0`]: '<mrow><mfrac><mrow><mo>∂</mo><mi>ρ</mi></mrow><mrow><mo>∂</mo><mi>t</mi></mrow></mfrac><mo>+</mo><mo>∇</mo><mo>·</mo><mo>(</mo><mi>ρ</mi><mi mathvariant="bold">u</mi><mo>)</mo><mo>=</mo><mn>0</mn></mrow>',
  };
  const body = table[block.latex];
  if (!body) return `<code>${block.latex}</code>`;
  return `<math display="block" xmlns="http://www.w3.org/1998/Math/MathML" aria-label="${block.title}">${body}</math>`;
}
