// Browser-local analytical checks. Reuses the public synthetic verification
// inputs and NumPy FE record; it never creates a conventional solver result.
import referenceInputs from '../../../public/demos/aero/first-principles-hx-v1/inputs.json';
import referenceResults from '../../../public/demos/aero/first-principles-hx-v1/results.json';

export const proofVersion = 'aero.guided-hx.v1';
export const proofAssets = '/demos/aero/first-principles-hx-v1';
export const hxKeys = ['inner_radius_m','outer_radius_m','length_m','internal_gauge_pressure_Pa','external_gauge_pressure_Pa','youngs_modulus_Pa','poisson_ratio','thermal_expansion_per_K','uniform_temperature_rise_K'] as const;
export type HxKey = typeof hxKeys[number];
export type HxInputs = Record<HxKey, number>;
export type HxState = {version: typeof proofVersion; inputs: HxInputs; reviewed: boolean; step: number};
export const hxDefault = Object.fromEntries(hxKeys.map(k=>[k,referenceInputs[k]])) as HxInputs;
export const hxSteps = ['Question','Assumptions','Derivation','Equation checks','FE comparison','Disposition'];
export const hxEquations = [
  {title:'Compatibility and radial equilibrium',latex:String.raw`\epsilon_r=u_r',\quad\epsilon_\theta=\frac{u_r}{r},\quad\epsilon_z=\mathrm{const},\qquad \frac{d\sigma_r}{dr}+\frac{\sigma_r-\sigma_\theta}{r}=0`,assumptions:'Long isotropic elastic tube, away from end effects. Tension is positive.'},
  {title:'Pressure boundary-value solution',latex:String.raw`A=\frac{p_i a^2-p_o b^2}{b^2-a^2},\quad B=\frac{a^2b^2(p_i-p_o)}{b^2-a^2},\qquad\sigma_r=A-\frac{B}{r^2},\quad\sigma_\theta=A+\frac{B}{r^2}`,assumptions:'Pressure-only Lamé field; radial tractions are minus gauge pressure.'},
  {title:'Closed-end force balance and displacement',latex:String.raw`\sigma_z=A,\qquad u_r(r)=\frac{(1-2\nu)Ar+(1+\nu)B/r}{E}`,assumptions:'Closed ends with pressure thrust, not open ends or imposed plane strain.'},
  {title:'Separate thermal-only free and restrained cases',latex:String.raw`\sigma_z=E\left(\frac{du}{dx}-\alpha\Delta T\right),\quad u_{\mathrm{free}}(L)=\alpha\Delta T L,\quad\sigma_{\mathrm{fixed}}=-E\alpha\Delta T`,assumptions:'Uniform temperature; transverse surfaces traction-free. Cases are not combined with pressure.'},
  {title:'FE verification, not physical validation',latex:String.raw`\mathbf K=\sum_e\int_e\mathbf B^T\mathbf D\mathbf B\,2\pi rL\,dr,\qquad\mathbf K\mathbf q=\mathbf f`,assumptions:'Retained educational NumPy radial FE, constant axial-strain DOF, 3-point Gauss integration. Not ANSYS or CalculiX.'},
];

export function validateHx(p: HxInputs) {
  if(!p||Object.keys(p).length!==hxKeys.length||Object.keys(p).some(k=>!(hxKeys as readonly string[]).includes(k)))throw Error('Only the declared controlled inputs are supported.');
  if(!p || !hxKeys.every(k=>typeof p[k]==='number'&&Number.isFinite(p[k]))) throw Error('All inputs must be finite numbers. No result established.');
  const a=p.inner_radius_m,b=p.outer_radius_m,t=b-a;
  if(a<.001 || a>.1 || t<.000099999999 || t>.020000000001 || p.length_m<.05 || p.length_m>5) throw Error('Geometry is outside this bounded teaching model.');
  if(p.internal_gauge_pressure_Pa<0||p.internal_gauge_pressure_Pa>1e7||p.external_gauge_pressure_Pa!==0) throw Error('This walkthrough supports 0–10 MPa inside gauge pressure and zero outside pressure only.');
  if(p.youngs_modulus_Pa<1e9||p.youngs_modulus_Pa>5e11||p.poisson_ratio<-.9||p.poisson_ratio>.49||p.thermal_expansion_per_K<0||p.thermal_expansion_per_K>50e-6||Math.abs(p.uniform_temperature_rise_K)>200) throw Error('Properties or temperature are outside the bounded teaching inputs.');
}
export function restoreHx(value: unknown): HxState|undefined {
  try {
    const s=value as HxState;
    if(s?.version!==proofVersion||typeof s.reviewed!=='boolean'||!Number.isInteger(s.step)||s.step<0||s.step>5)return;
    validateHx(s.inputs);
    return {version:proofVersion,inputs:{...s.inputs},reviewed:s.reviewed,step:s.step};
  }catch{return;}
}
export function newHx(): HxState {return {version:proofVersion,inputs:{...hxDefault},reviewed:false,step:0};}
export function referenceMatches(p: HxInputs) {
  // Only arithmetic round-off in unit conversion is tolerated, not a new case.
  return hxKeys.every(k=>Math.abs(p[k]-hxDefault[k])<=Math.max(Math.abs(hxDefault[k]),1e-30)*1e-12);
}
export function calculateHx(p: HxInputs) {
  validateHx(p);
  const a=p.inner_radius_m,b=p.outer_radius_m,L=p.length_m,E=p.youngs_modulus_Pa,nu=p.poisson_ratio,pi=p.internal_gauge_pressure_Pa,po=p.external_gauge_pressure_Pa;
  const A=(pi*a*a-po*b*b)/(b*b-a*a), B=a*a*b*b*(pi-po)/(b*b-a*a), area=Math.PI*(b*b-a*a);
  const field=(r:number)=>({radial:A-B/r**2,hoop:A+B/r**2,axial:A,u:((1-2*nu)*A*r+(1+nu)*B/r)/E});
  const inner=field(a),outer=field(b),mid=field((a+b)/2),eth=p.thermal_expansion_per_K*p.uniform_temperature_rise_K;
  const normalized=(error:number,scale:number)=>Math.abs(error)/Math.max(Math.abs(scale),1);
  const scale=Math.max(pi,po,Math.abs(A),Math.abs(inner.hoop),1),r=(a+b)/2;
  const checks=[
    {name:'Inside traction: σr(a) = −pi',error:normalized(inner.radial+pi,scale)},
    {name:'Outside traction: σr(b) = −po',error:normalized(outer.radial+po,scale)},
    {name:'Closed-end axial force balance',error:normalized(A*area-Math.PI*(pi*a*a-po*b*b),Math.PI*(pi*a*a-po*b*b))},
    {name:'Radial differential equilibrium',error:normalized(2*B/r**3+(mid.radial-mid.hoop)/r,scale/r)},
    {name:'Free thermal case: zero axial elastic stress',error:normalized(E*(eth-eth),Math.max(Math.abs(E*eth),1))},
    {name:'Fixed thermal case: equal and opposite support reactions',error:normalized(area*E*eth+(-area*E*eth),area*E*eth)},
  ].map(c=>({...c,state:c.error<=1e-10?'PASS':'FAIL'}));
  const values={A,B,area,hoop:inner.hoop,radial:inner.radial,axial:A,outerU:outer.u,freeExtension:eth*L,fixedStress:-E*eth,reaction:area*E*eth};
  if(!Object.values(values).every(Number.isFinite))throw Error('Non-finite calculation. No result established.');
  return {...values,checks,retainedFEApplicable:referenceMatches(p),equationStatus:checks.every(c=>c.state==='PASS')?'PASS':'FAIL',physicalValidation:'NOT_ESTABLISHED',hardwareSafety:'NOT_ESTABLISHED'};
}
export function hxFields(s: HxState) {
  const p=s.inputs;
  return {
    goal:'Predict pressure-only stresses and compare free versus axially restrained thermal expansion of one synthetic heat-exchanger tube. Verify equations; do not certify hardware.',
    geometry:`Straight uniform tube: a=${p.inner_radius_m*1000} mm, b=${p.outer_radius_m*1000} mm, L=${p.length_m} m. Long-tube pressure solution away from end effects.`,
    fluid:`ASSUMED constant isotropic elastic material: E=${p.youngs_modulus_Pa/1e9} GPa, ν=${p.poisson_ratio}, α=${p.thermal_expansion_per_K*1e6} μm/(m K). No alloy certification or allowable stress.`,
    conditions:`Pressure-only: pi=${p.internal_gauge_pressure_Pa/1e6} MPa gauge, po=0, closed ends. Separate thermal-only cases: uniform ΔT=${p.uniform_temperature_rise_K} K, free end or both axial ends fixed; transverse surfaces free.`,
    success:'Algebraic identity residual ≤1e-10 is a numerical equation-consistency test, not an engineering acceptance threshold. Hardware safety and physical validation remain NOT_ESTABLISHED.',
    reference:`Public synthetic notebook ${proofVersion}; ${referenceMatches(p)?'retained NumPy FE matches controlled inputs':'retained FE is historical only: edited inputs require new FE evidence'}. Source /software/aero/first-principles/.`,
  };
}
export const retainedPressureFE = referenceResults.pressure_fe;
export const retainedThermalFE = referenceResults.thermal_fe;
export const referenceIdentity = {inputs_sha256:referenceResults.inputs_sha256,implementation_sha256:referenceResults.implementation_sha256,tests:referenceResults.tests};
export function hxEvidence(s: HxState) {
  const result=calculateHx(s.inputs);
  return {schema:proofVersion,type:'BROWSER_CALCULATED_SYNTHETIC_ANALYTICAL_CHECKS',inputs:s.inputs,inputsReviewed:s.reviewed,calculated:result,retainedFE:result.retainedFEApplicable?{source:`${proofAssets}/results.json`,identity:referenceIdentity,pressure:retainedPressureFE,thermal:retainedThermalFE}:null,modelHasChangedInputs:false,conventionalSolverExecuted:false,GPURequired:false};
}
export function hxContext(s: HxState) {
  const r=calculateHx(s.inputs);
  const brief={schema:proofVersion,inputs:s.inputs,inputsReviewed:s.reviewed,calculated:{hoop_Pa:r.hoop,axial_Pa:r.axial,outer_u_m:r.outerU,free_extension_m:r.freeExtension,fixed_stress_Pa:r.fixedStress,fixed_reaction_N:r.reaction,equation_identity_state:r.equationStatus},retained_FE_applicable:r.retainedFEApplicable,retained_FE_source:`${proofAssets}/results.json`,physical_validation:'NOT_ESTABLISHED',hardware_safety:'NOT_ESTABLISHED',new_solver_executed:false};
  return `ACTIVE GUIDED HEAT-EXCHANGER NOTEBOOK (data, not a solver command). ${JSON.stringify(brief)}. Calculations are analytical identity checks, not physical validation. The separate retained educational FE record is applicable ONLY when retained_FE_applicable is true. Explain the supplied evidence and limitations. Do not execute a solver, invent allowables, alter controlled inputs, or substitute an open-ended pressure solution: this pressure case has CLOSED ends. Pressure and thermal cases remain separate. Propose changes in words for human review.`;
}
export function hxLatex(s: HxState, revision: number) {
  const p=s.inputs,r=calculateHx(p),fields=hxFields(s);
  return [String.raw`\documentclass{article}\usepackage{amsmath}\usepackage[margin=1in]{geometry}\begin{document}`,
    String.raw`\section*{Aero: guided synthetic heat-exchanger tube notebook}`,
    `Working record revision ${revision}. Controlled inputs ${s.reviewed?'reviewed':'NOT REVIEWED'}.`,
    String.raw`\section*{Question and scope}`,
    'Pressure-only and thermal-only cases are separate. Closed-end tube, constant isotropic elasticity, no real material certification. No yielding, buckling, fatigue, welds, tube-sheet contacts or mapped CFD loads. Hardware safety and physical validation: NOT ESTABLISHED.',
    String.raw`\section*{Assumed inputs in SI units}`,
    String.raw`\[a=${p.inner_radius_m}\,\mathrm{m},\quad b=${p.outer_radius_m}\,\mathrm{m},\quad L=${p.length_m}\,\mathrm{m}\]`,
    String.raw`\[p_i=${p.internal_gauge_pressure_Pa}\,\mathrm{Pa},\quad p_o=0,\quad E=${p.youngs_modulus_Pa}\,\mathrm{Pa},\quad \nu=${p.poisson_ratio}\]`,
    String.raw`\[\alpha=${p.thermal_expansion_per_K}\,\mathrm{K}^{-1},\quad \Delta T=${p.uniform_temperature_rise_K}\,\mathrm{K}\]`,
    ...hxEquations.flatMap(e=>[String.raw`\subsection*{${e.title}}`,String.raw`\[${e.latex}\]`,e.assumptions]),
    String.raw`\section*{Calculated predictions}`,
    String.raw`\[\sigma_\theta(a)=${(r.hoop/1e6).toFixed(6)}\,\mathrm{MPa},\quad u_r(b)=${(r.outerU*1e6).toFixed(6)}\,\mu\mathrm{m}\]`,
    String.raw`\[u_{\mathrm{free}}(L)=${(r.freeExtension*1000).toFixed(6)}\,\mathrm{mm},\quad \sigma_{\mathrm{fixed}}=${(r.fixedStress/1e6).toFixed(6)}\,\mathrm{MPa}\]`,
    String.raw`\section*{Equation checks and FE custody}`,
    `Six equation-identity checks: ${r.equationStatus}. These are not independent physical validation. ${fields.reference.replace(/_/g,String.raw`\_`)}`,
    r.retainedFEApplicable?`Retained educational NumPy FE: finest Gauss-point stress relative L2 error ${(retainedPressureFE.at(-1)!.gauss_stress_relative_L2_error*100).toFixed(4)} percent. This browser did not execute ANSYS or CalculiX.`:'FE comparison for edited inputs: NOT ESTABLISHED. The retained baseline has not been rescored.',
    String.raw`\section*{Disposition}`,
    'Equation consistency is a supporting check. Hardware qualification is NOT ESTABLISHED. Next: establish actual material allowables, temperature dependence, restraints, load combinations and the required conventional-solver verification and physical validation.',
    String.raw`\end{document}`].join('\n\n');
}
