import katex from 'katex';
import {calculateHx,newHx,restoreHx,hxEvidence,hxSteps,type HxState} from './hx-proof';

export function setupHxWalkthrough(root: HTMLElement, changed:(state:HxState,kind:'inputs'|'review'|'step')=>void, ask:(question:string)=>void) {
  const $=<T extends HTMLElement=HTMLElement>(s:string)=>root.querySelector<T>(s)!;
  const form=$<HTMLFormElement>('[data-hx-inputs]');
  let state=newHx(),draftInvalid=false;
  const writeInputs=()=>{
    const p=state.inputs,values={pressure:p.internal_gauge_pressure_Pa/1e6,radius:p.inner_radius_m*1000,thickness:(p.outer_radius_m-p.inner_radius_m)*1000,length:p.length_m,modulus:p.youngs_modulus_Pa/1e9,poisson:p.poisson_ratio,alpha:p.thermal_expansion_per_K*1e6,temperature:p.uniform_temperature_rise_K};
    Object.entries(values).forEach(([name,value])=>{(form.elements.namedItem(name) as HTMLInputElement).value=String(Number(value.toPrecision(12)));});
  };
  const render=()=>{
    const r=calculateHx(state.inputs),step=state.step;
    $('[data-hx-hoop]').textContent=`${(r.hoop/1e6).toFixed(3)} MPa`;
    $('[data-hx-extension]').textContent=`${(r.freeExtension*1e3).toFixed(3)} mm`;
    $('[data-hx-stress]').textContent=`${(r.fixedStress/1e6).toFixed(3)} MPa`;
    root.querySelectorAll<HTMLElement>('[data-hx-step]').forEach(el=>el.hidden=Number(el.dataset.hxStep)!==step);
    $('[data-hx-position]').textContent=`Step ${step+1} of 6`;
    $<HTMLButtonElement>('[data-hx-back]').disabled=step===0;
    $<HTMLButtonElement>('[data-hx-next]').disabled=step===5;
    $('[data-hx-next]').textContent=step===5?'Walkthrough complete':`Next: ${hxSteps[step+1]} →`;
    $('[data-hx-status]').textContent=draftInvalid?'Unapplied or invalid draft. Predictions and export still describe the last applied inputs.':`${state.reviewed?'Synthetic assumptions reviewed':'Assumed inputs · not yet reviewed'}. ${r.retainedFEApplicable?'Retained FE matches the reference inputs.':'Inputs changed: active FE comparison NOT_ESTABLISHED.'}`;
    $('[data-hx-review]').textContent=state.reviewed?'Synthetic assumptions reviewed ✓':'Review these synthetic assumptions';
    $('[data-hx-substitution]').replaceChildren();
    const math=document.createElement('div');
    katex.render(String.raw`\sigma_\theta(a)=${(r.hoop/1e6).toFixed(3)}\,\mathrm{MPa},\quad u_r(b)=${(r.outerU*1e6).toFixed(3)}\,\mu\mathrm{m}`,math,{displayMode:true,throwOnError:true,trust:false});
    const note=document.createElement('p');note.textContent=`Substitution uses the applied inputs, not model-generated values. A = ${(r.A/1e6).toFixed(6)} MPa; B = ${r.B.toFixed(6)} Pa·m²; axial stress = ${(r.axial/1e6).toFixed(6)} MPa; fixed-end reaction magnitude = ${(Math.abs(r.reaction)/1e3).toFixed(3)} kN.`;
    $('[data-hx-substitution]').append(math,note);
    $('[data-hx-checks]').replaceChildren();
    r.checks.forEach(c=>{const tr=document.createElement('tr');[c.name,c.error.toExponential(2),c.state].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.append(td);});$('[data-hx-checks]').append(tr);});
    $('[data-hx-fe-current]').hidden=!r.retainedFEApplicable;
    $('[data-hx-fe-state]').textContent=r.retainedFEApplicable?'APPLICABLE RETAINED VERIFICATION · exact synthetic input match. Nine Python tests passed; 64-element pressure stress L₂ error 0.0834%. No new FE run occurred in this browser.':'NOT_ESTABLISHED FOR ACTIVE INPUTS · reference inputs no longer match. The historical record stays preserved, but its errors and PASS cannot qualify your edited case. Reproduce a new FE record before comparison.';
    $('[data-hx-equation-state]').textContent=r.equationStatus;
    $('[data-hx-comparison-state]').textContent=r.retainedFEApplicable?'APPLICABLE RETAINED VERIFICATION':'NOT_ESTABLISHED';
    $('[data-hx-review-state]').textContent=state.reviewed?'SYNTHETIC ASSUMPTIONS REVIEWED':'NOT REVIEWED';
  };
  const readDraft=()=>{
    if(!form.checkValidity())throw Error('Review the bounded numeric inputs. Last applied results are unchanged.');
    const v=(name:string)=>Number((form.elements.namedItem(name) as HTMLInputElement).value);
    const p={inner_radius_m:v('radius')/1e3,outer_radius_m:(v('radius')+v('thickness'))/1e3,length_m:v('length'),internal_gauge_pressure_Pa:v('pressure')*1e6,external_gauge_pressure_Pa:0,youngs_modulus_Pa:v('modulus')*1e9,poisson_ratio:v('poisson'),thermal_expansion_per_K:v('alpha')*1e-6,uniform_temperature_rise_K:v('temperature')};
    calculateHx(p);return p;
  };
  form.addEventListener('input',()=>{draftInvalid=true;render();});
  form.addEventListener('submit',e=>{e.preventDefault();try{state={...state,inputs:readDraft(),reviewed:false};draftInvalid=false;render();changed(structuredClone(state),'inputs');}catch(error){draftInvalid=true;render();$('[data-hx-status]').textContent=error instanceof Error?error.message:'Invalid draft. Last applied results unchanged.';}});
  $('[data-hx-review]').addEventListener('click',()=>{
    try {const p=readDraft();if(JSON.stringify(p)!==JSON.stringify(state.inputs)&&draftInvalid)throw Error('Apply the draft before reviewing it.');state.reviewed=true;draftInvalid=false;render();changed(structuredClone(state),'review');}
    catch(error){$('[data-hx-status]').textContent=error instanceof Error?error.message:'Apply valid inputs first.';}
  });
  const show=(step:number)=>{state.step=Math.max(0,Math.min(5,step));render();changed(structuredClone(state),'step');};
  $('[data-hx-back]').addEventListener('click',()=>show(state.step-1));
  $('[data-hx-next]').addEventListener('click',()=>show(state.step+1));
  root.querySelectorAll<HTMLButtonElement>('[data-hx-ask]').forEach(b=>b.addEventListener('click',()=>ask(b.dataset.hxAsk!)));
  $('[data-hx-export]').addEventListener('click',()=>{
    const url=URL.createObjectURL(new Blob([JSON.stringify(hxEvidence(state),null,2)+'\n'],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='aero-guided-hx-evidence.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  render();
  return {state:()=>structuredClone(state),load:(value?:HxState)=>{state=restoreHx(value)||newHx();draftInvalid=false;writeInputs();render();},show:(step:number)=>{state.step=step;render();},draftPending:()=>draftInvalid};
}
