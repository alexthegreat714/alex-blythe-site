import type { Provenance } from './case';

export type AnalysisStepId =
  | 'scope'
  | 'area'
  | 'density'
  | 'velocity'
  | 'mach'
  | 'dynamic-pressure'
  | 'limits';

export interface AnalysisStep {
  id: AnalysisStepId;
  index: string;
  title: string;
  latex: string;
  mathml: string;
  explanation: string;
  resultKey?: keyof FirstOrderValues;
  resultLabel?: string;
  units?: string;
  source: Provenance;
}

export interface FirstOrderInputs {
  massFlowKgS: number;
  referencePressurePa: number;
  referenceTemperatureK: number;
  gasConstantJkgK: number;
  heatCapacityRatio: number;
  inletRadiusM: number;
}

export interface FirstOrderValues {
  areaM2: number;
  densityKgM3: number;
  velocityMS: number;
  speedOfSoundMS: number;
  mach: number;
  dynamicPressurePa: number;
}

export const firstOrderInputs: FirstOrderInputs = {
  massFlowKgS: 0.010,
  referencePressurePa: 101325,
  referenceTemperatureK: 300,
  gasConstantJkgK: 287,
  heatCapacityRatio: 1.4,
  inletRadiusM: 0.020,
};

export function calculateFirstOrder(inputs: FirstOrderInputs): FirstOrderValues {
  const areaM2 = Math.PI * inputs.inletRadiusM ** 2;
  const densityKgM3 = inputs.referencePressurePa
    / (inputs.gasConstantJkgK * inputs.referenceTemperatureK);
  const velocityMS = inputs.massFlowKgS / (densityKgM3 * areaM2);
  const speedOfSoundMS = Math.sqrt(
    inputs.heatCapacityRatio * inputs.gasConstantJkgK * inputs.referenceTemperatureK,
  );
  const mach = velocityMS / speedOfSoundMS;
  const dynamicPressurePa = 0.5 * densityKgM3 * velocityMS ** 2;
  return { areaM2, densityKgM3, velocityMS, speedOfSoundMS, mach, dynamicPressurePa };
}

export const firstOrderValues = calculateFirstOrder(firstOrderInputs);

const math = (label: string, body: string) =>
  `<math display="block" xmlns="http://www.w3.org/1998/Math/MathML" aria-label="${label}">${body}</math>`;

export const analysisSteps: AnalysisStep[] = [
  {
    id: 'scope', index: '00', title: 'Scope and authority', latex: String.raw`\text{case inputs} \rightarrow \text{analytical expectations} \neq \text{solver output}`,
    mathml: math('Analytical authority chain', '<mrow><mtext>case inputs</mtext><mo>→</mo><mtext>analytical expectations</mtext><mo>≠</mo><mtext>solver output</mtext></mrow>'),
    explanation: 'Every value below is established before solving from the declared reference state and inlet geometry. It is a screening calculation, not validation and not a reconstruction of CFD output.',
    source: 'ANALYTICAL',
  },
  {
    id: 'area', index: '01', title: 'Inlet reference area', latex: String.raw`A_i = \pi r_i^2`,
    mathml: math('Inlet reference area', '<mrow><msub><mi>A</mi><mi>i</mi></msub><mo>=</mo><mi>π</mi><msubsup><mi>r</mi><mi>i</mi><mn>2</mn></msubsup></mrow>'),
    explanation: 'The deterministic nozzle definition supplies the 20 mm inlet radius. The full circular area is used for this independent reference-scale calculation.',
    resultKey: 'areaM2', resultLabel: 'Area', units: 'm²', source: 'ANALYTICAL',
  },
  {
    id: 'density', index: '02', title: 'Reference density', latex: String.raw`\rho_{ref} = \frac{p_{ref}}{R T_{ref}}`,
    mathml: math('Ideal gas reference density', '<mrow><msub><mi>ρ</mi><mi>ref</mi></msub><mo>=</mo><mfrac><msub><mi>p</mi><mi>ref</mi></msub><mrow><mi>R</mi><msub><mi>T</mi><mi>ref</mi></msub></mrow></mfrac></mrow>'),
    explanation: 'Perfect-gas air at the declared reference pressure and temperature provides a pre-solve density scale. This is not the solved density field.',
    resultKey: 'densityKgM3', resultLabel: 'Reference density', units: 'kg/m³', source: 'ANALYTICAL',
  },
  {
    id: 'velocity', index: '03', title: 'Continuity velocity scale', latex: String.raw`V_i = \frac{\dot{m}}{\rho_{ref} A_i}`,
    mathml: math('Continuity velocity scale', '<mrow><msub><mi>V</mi><mi>i</mi></msub><mo>=</mo><mfrac><mover><mi>m</mi><mo>˙</mo></mover><mrow><msub><mi>ρ</mi><mi>ref</mi></msub><msub><mi>A</mi><mi>i</mi></msub></mrow></mfrac></mrow>'),
    explanation: 'Steady mass continuity converts the commanded mass flow into an inlet mean-velocity scale using only case inputs.',
    resultKey: 'velocityMS', resultLabel: 'Reference velocity', units: 'm/s', source: 'ANALYTICAL',
  },
  {
    id: 'mach', index: '04', title: 'Compressibility screen', latex: String.raw`a_{ref}=\sqrt{\gamma R T_{ref}},\qquad M_i=\frac{V_i}{a_{ref}}`,
    mathml: math('Reference speed of sound and Mach number', '<mrow><msub><mi>a</mi><mi>ref</mi></msub><mo>=</mo><msqrt><mi>γ</mi><mi>R</mi><msub><mi>T</mi><mi>ref</mi></msub></msqrt><mo>,</mo><mspace width="1em"/><msub><mi>M</mi><mi>i</mi></msub><mo>=</mo><mfrac><msub><mi>V</mi><mi>i</mi></msub><msub><mi>a</mi><mi>ref</mi></msub></mfrac></mrow>'),
    explanation: 'The reference Mach number screens the inlet regime before choosing and running the numerical model.',
    resultKey: 'mach', resultLabel: 'Reference Mach number', source: 'ANALYTICAL',
  },
  {
    id: 'dynamic-pressure', index: '05', title: 'Dynamic-pressure scale', latex: String.raw`q_i = \frac{1}{2}\rho_{ref}V_i^2`,
    mathml: math('Dynamic pressure scale', '<mrow><msub><mi>q</mi><mi>i</mi></msub><mo>=</mo><mfrac><mn>1</mn><mn>2</mn></mfrac><msub><mi>ρ</mi><mi>ref</mi></msub><msubsup><mi>V</mi><mi>i</mi><mn>2</mn></msubsup></mrow>'),
    explanation: 'This establishes an order-of-magnitude pressure scale and the expected quadratic response to mass flow. It is not a nozzle pressure-drop prediction.',
    resultKey: 'dynamicPressurePa', resultLabel: 'Dynamic-pressure scale', units: 'Pa', source: 'ANALYTICAL',
  },
  {
    id: 'limits', index: '06', title: 'What is not established', latex: String.raw`\Delta p_{analytical}=\text{NOT YET ESTABLISHED}`,
    mathml: math('Analytical pressure drop is not yet established', '<mrow><msub><mi>Δp</mi><mi>analytical</mi></msub><mo>=</mo><mtext>NOT YET ESTABLISHED</mtext></mrow>'),
    explanation: 'The available inputs do not justify an independent loss model for this converging-diverging turbulent nozzle. Aero therefore does not fabricate an analytical pressure drop or reuse the CFD result as its own prediction.',
    source: 'ANALYTICAL',
  },
];

export const latexDocument = String.raw`% Aero pre-solve first-order screening
% Authority: CASE INPUTS -> ANALYTICAL; no CFD output is used.
\begin{aligned}
A_i &= \pi r_i^2 \\
\rho_{ref} &= \frac{p_{ref}}{R T_{ref}} \\
V_i &= \frac{\dot{m}}{\rho_{ref} A_i} \\
a_{ref} &= \sqrt{\gamma R T_{ref}} \\
M_i &= \frac{V_i}{a_{ref}} \\
q_i &= \frac{1}{2}\rho_{ref}V_i^2 \\
\Delta p_{analytical} &= \text{NOT YET ESTABLISHED}
\end{aligned}`;
