import katex from 'katex';

export type ChannelInputs={length_mm:number;gap_mm:number;flow_ml_s:number;budget_pa:number};
export type ChannelState={inputs:ChannelInputs;reviewed:boolean;runId?:string;status?:any;result?:any;history?:{id:string;inputs:ChannelInputs}[];requestId?:string};
const defaults:ChannelInputs={length_mm:200,gap_mm:2,flow_ml_s:20,budget_pa:70};
const ranges={length_mm:[100,500],gap_mm:[1,3],flow_ml_s:[1,40],budget_pa:[1,1000]};
const reference='https://farside.ph.utexas.edu/teaching/336L/Fluidhtml/node134.html';
export const channelEquations=[
  {title:'Fully developed parallel-plate pressure drop',latex:'\\Delta p=\\frac{12\\mu LQ}{Wh^3}',assumptions:'Steady incompressible laminar flow; no-slip parallel plates; no entrance or sidewall loss.'},
  {title:'Mean velocity and Reynolds number',latex:'\\bar U=\\frac{Q}{Wh},\\qquad Re_{2h}=\\frac{2\\rho\\bar U h}{\\mu}',assumptions:'Constant water properties; W = 100 mm is a reference width.'}
];
export function channelFields(p:ChannelInputs){return {
  goal:'Choose the smallest of three parallel-plate channel gaps meeting a pressure-drop budget.',
  geometry:`Length ${p.length_mm} mm; nominal gap ${p.gap_mm} mm; gaps at 75%, 100% and 125% of nominal; reference width 100 mm. Structured 2D channel slice.`,
  fluid:'Water, nominal 20 °C; density 998.2 kg/m³; dynamic viscosity 0.001003 Pa·s. Constant properties, incompressible, laminar.',
  conditions:`Volume flow ${p.flow_ml_s} mL/s. Fully developed parabolic inlet, zero gauge outlet pressure, no-slip plates, spanwise empty boundaries. No heat transfer or sidewall/entrance losses.`,
  success:`Pressure drop plus numerical allowance ≤ ${p.budget_pa} Pa; reference error <2%; medium/fine change <1%; flux imbalance <0.1%; profile error <2%; residuals ≤1e-7.`,
  reference:'Analytical plane Poiseuille solution: '+reference
};}
function variants(p:ChannelInputs){return [.75,1,1.25].map(f=>{const h=p.gap_mm*f/1000;return {gap_mm:h*1000,pa:12*.001003*(p.length_mm/1000)*(p.flow_ml_s*1e-6)/(.1*h**3),re:998.2*2*p.flow_ml_s*1e-6/(.1*.001003)};});}
function download(name:string,content:string,type='text/plain'){const link=document.createElement('a');link.href=URL.createObjectURL(new Blob([content],{type}));link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);}
function table(headers:string[],rows:string[][]){const table=document.createElement('table');const head=table.createTHead().insertRow();headers.forEach(value=>{const th=document.createElement('th');th.textContent=value;head.append(th);});const body=table.createTBody();rows.forEach(values=>{const row=body.insertRow();values.forEach(v=>row.insertCell().textContent=v);});return table;}
const fmt=(n:number)=>Number.isFinite(n)?n.toPrecision(4):'—';

export function setupChannelStudy(host:HTMLElement,endpoint:string,onChange:(state:ChannelState,writeRecord:boolean)=>void,onProgress:(percent:number[],labels:string[],tones:string[])=>void){
  const $=<T extends HTMLElement=HTMLElement>(s:string)=>host.querySelector<T>(s)!;
  let state:ChannelState={inputs:{...defaults},reviewed:false};
  let currentStage=0,online=false,active=false,requestBusy=false,generation=0,disposeView:(()=>void)|undefined;
  let timer:ReturnType<typeof setTimeout>|undefined;
  const base=endpoint.replace(/\/$/,'');
  const notice=(message:string)=>$('[data-study-notice]').textContent=message;
  const valid=()=>Object.entries(ranges).every(([key,[lo,hi]])=>{const n=state.inputs[key as keyof ChannelInputs];return Number.isFinite(n)&&n>=lo&&n<=hi;});
  const working=()=>requestBusy||['queued','running'].includes(state.status?.state);
  const save=(writeRecord=false)=>onChange(structuredClone(state),writeRecord);
  async function api(path:string,body?:unknown){const r=await fetch(base+'/study'+path,{method:body?'POST':'GET',credentials:'omit',cache:'no-store',signal:AbortSignal.timeout(10000),...(body?{headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{})});const data=await r.json();if(!r.ok)throw Object.assign(Error(data.error||'Study service unavailable'),{status:r.status});return data;}
  async function health(){try{const result=await api('/health');online=result.ready===true;}catch{online=false;}if(!host.isConnected)return;const el=$('[data-solver-state]');el.textContent=online?'● Solver online':'● Solver offline';el.dataset.online=String(online);$<HTMLButtonElement>('[data-study-run]').disabled=!online||!state.reviewed||working()||Boolean(state.result);}
  function progress(){if(!active)return;const complete=state.status?.state==='complete',failed=state.status?.state==='failed'||state.status?.worker_offline||state.status?.stalled,inProgress=working();const validCount=Object.entries(ranges).filter(([key,[lo,hi]])=>{const n=state.inputs[key as keyof ChannelInputs];return Number.isFinite(n)&&n>=lo&&n<=hi;}).length;
    const prep=state.reviewed?100:Math.round(validCount/4*75);
    onProgress([prep,prep,prep,complete?100:prep,complete?100:inProgress?state.status?.progress||0:prep,complete?100:0],
      [state.reviewed?'Inputs reviewed':'Review inputs','Analytical reference','Parametric channel',complete?'Meshes checked':'Three grids planned',complete?'Solver completed':failed?'Run failed':inProgress?`${state.status?.completed||0}/9 solved`:'Ready when reviewed',complete?(state.result?.checks_passed?'Report ready':'Review checks'):'Awaiting fields'],
      Array.from({length:6},(_,i)=>failed&&i>=3?'red':complete?(state.result?.checks_passed?'green':i>=4?'red':'green'):inProgress?(i<3?'green':i<5?'yellow':'blue'):'blue'));
  }
  async function viewport(){disposeView?.();disposeView=undefined;const ticket=++generation;if(!active||![2,3,5].includes(currentStage))return;
    const index=Number($<HTMLSelectElement>('[data-study-variant]').value)||0,v=variants(state.inputs)[index];if(!v||!valid())return;
    const fine=state.result?.variants?.[index]?.levels?.at(-1),field=$<HTMLSelectElement>('[data-study-field]').value;
    const caption=$('[data-study-viewport-caption]');
    if(currentStage===5&&!fine){$('[data-study-viewport]').textContent='A solved field will appear here after the run.';caption.textContent='No computed field exists for these inputs yet.';return;}
    try {const {channelView}=await import('./channel-view');if(ticket!==generation||!active)return;disposeView=channelView($('[data-study-viewport]'),state.inputs.length_mm/1000,v.gap_mm/1000,fine?.nx||64,fine?.ny||32,currentStage,fine?.field?.[field]);
      caption.textContent=currentStage===5?`Computed ${field==='speed_m_s'?'velocity (m/s)':'pressure (Pa)'} · ${fine.cells.toLocaleString()} cells · blue ${fmt(Math.min(...fine.field[field]))} → red ${fmt(Math.max(...fine.field[field]))}. Gap and slice depth ×20.`:currentStage===3?`${fine?'Generated':'Planned'} fine grid: 64 × 32 × 1. ${fine?'checkMesh passed.':'Mesh generation happens on Start.'} Gap and slice depth ×20.`:'Parametric fluid volume, not a manufactured part. Drag to rotate; scroll to zoom. Gap and solver slice depth ×20.';
    }catch{$('[data-study-viewport]').textContent='3D rendering unavailable in this browser. Dimensions and mesh evidence remain in the report.';}
  }
  function render(){
    $('[data-study-heading]').textContent=['Choose the channel gap.','Set expectations before solving.','Inspect the flow domain.','Review the mesh family.','Run and verify the study.','Decide from the evidence.'][currentStage];
    const explanations=['Compare three gaps against your pressure-drop budget. Edit the inputs or discuss the assumptions with Aero.','The h³ relation predicts how the gap affects pressure loss. OpenFOAM will calculate the same physical model independently.','The same parametric channel is used for each mesh and solver run.','Three resolutions test numerical sensitivity for every candidate gap.','Start a new computation from your reviewed inputs. Progress comes from the solver worker.','Compare the candidates, inspect computed fields and download the engineering report.'];
    $('[data-study-explanation]').textContent=explanations[currentStage];
    host.querySelectorAll<HTMLElement>('[data-study-part]').forEach(el=>el.hidden=!el.dataset.studyPart!.split(',').includes(String(currentStage)));
    for(const input of host.querySelectorAll<HTMLInputElement>('[data-study-input]')){input.value=String(state.inputs[input.dataset.studyInput as keyof ChannelInputs]);input.disabled=working();}
    $<HTMLInputElement>('[data-study-confirm]').checked=state.reviewed;$<HTMLInputElement>('[data-study-confirm]').disabled=working();
    $<HTMLButtonElement>('[data-study-run]').disabled=!state.reviewed||!online||working()||Boolean(state.result);
    $('[data-study-run]').textContent=state.result?'Study complete — view Results':state.status?.state==='failed'?'Start a fresh study':'Start nine OpenFOAM solves';
    $('[data-study-run-title]').textContent=state.result?'Calculation complete':working()?'Calculation in progress':'Ready for a fresh calculation';
    $<HTMLButtonElement>('[data-study-prepare]').disabled=!state.reviewed||!valid();
    $<HTMLButtonElement>('[data-study-brief]').disabled=!valid();
    const vs=valid()?variants(state.inputs):[];const selector=$<HTMLSelectElement>('[data-study-variant]'),choice=selector.value;selector.replaceChildren();vs.forEach((v,i)=>{const option=document.createElement('option');option.value=String(i);option.textContent=`${fmt(v.gap_mm)} mm`;selector.append(option);});selector.value=choice||'1';
    $('[data-study-field-label]').hidden=currentStage!==5;
    $('[data-study-estimates]').replaceChildren(table(['Gap (mm)','Analytical Δp (Pa)','Re (2h)'],vs.map(v=>[fmt(v.gap_mm),fmt(v.pa),fmt(v.re)])));
    $('[data-study-math]').replaceChildren();for(const eq of channelEquations){const el=document.createElement('div');el.className='equation';katex.render(eq.latex,el,{displayMode:true,trust:false});$('[data-study-math]').append(el);}
    const job=$('[data-study-job]');job.hidden=!state.status;job.dataset.state=state.status?.state||'';
    if(state.status){$('[data-study-job-label]').textContent=state.status.worker_offline?'Worker unavailable':state.status.state;$('[data-study-count]').textContent=`${state.status.completed||0} / 9`;$<HTMLProgressElement>('[data-study-progress]').value=state.status.completed||0;$('[data-study-job-message]').textContent=state.status.message;}
    $('[data-study-downloads]').hidden=!state.result;
    const history=$('[data-study-history]');history.replaceChildren();history.hidden=!state.history?.length;
    if(state.history?.length){const summary=document.createElement('summary');summary.textContent='Previous runs · historical inputs';history.append(summary);for(const previous of state.history){const link=document.createElement('a');link.href=base+'/study/runs/'+previous.id+'/report';link.target='_blank';link.rel='noopener noreferrer';link.textContent=`${previous.inputs.length_mm} mm length · ${previous.inputs.gap_mm} mm nominal gap · ${previous.inputs.flow_ml_s} mL/s · ${previous.inputs.budget_pa} Pa budget`;const p=document.createElement('p');p.append(link);history.append(p);}const note=document.createElement('p');note.textContent='Historical reports do not apply to changed inputs. Server copies expire after 48 hours; download evidence to keep it.';history.append(note);}
    if(state.result){const r=state.result;$('[data-study-decision]').textContent=r.decision;
      $('[data-study-comparison]').replaceChildren(table(['Gap mm','CFD Pa','Reference Pa','Margin Pa','Decision'],r.variants.map((v:any)=>[fmt(v.gap_mm),fmt(v.pressure_drop_pa),fmt(v.analytical_pa),fmt(v.margin_pa),v.meets_budget?'Meets budget':'Review / exceeds'])));
      const checks=$('[data-study-checks]');checks.replaceChildren();const all=(k:string)=>r.variants.every((v:any)=>v.levels.every((g:any)=>g.gates[k]));
      for(const [label,passed] of [['Solver completed',all('solver')],['Mesh sensitivity <1%',r.variants.every((v:any)=>v.mesh_change_pct<1)],['Reference error <2%',all('analytical_reference')],['Mass conserved',all('conservation')]]){const span=document.createElement('span');span.textContent=`${passed?'✓':'!'} ${label}`;span.dataset.pass=String(passed);checks.append(span);}
      $('[data-study-interpretation]').textContent=r.interpretation+' Margin subtracts a numerical allowance; it does not include omitted physical effects.';
      $<HTMLAnchorElement>('[data-study-evidence]').href=base+'/study/runs/'+state.runId+'/evidence';
      const paper=$<HTMLAnchorElement>('[data-study-paper]');paper.hidden=!state.status?.paper_sha256;paper.href=base+'/study/runs/'+state.runId+'/paper';
    }else{$('[data-study-decision]').textContent='No solver result for these inputs yet.';$('[data-study-comparison]').replaceChildren();$('[data-study-checks]').replaceChildren();$('[data-study-interpretation]').textContent='';$<HTMLIFrameElement>('[data-study-proof]').removeAttribute('src');$('[data-study-proof]').hidden=true;}
    $<HTMLButtonElement>('[data-study-back]').disabled=currentStage===0;$<HTMLButtonElement>('[data-study-next]').disabled=currentStage===5;
    $('[data-study-next]').textContent=['Review math →','Inspect geometry →','Review mesh →','Prepare run →','Inspect results →','Complete'][currentStage];
    progress();void viewport();
  }
  function goto(index:number){document.querySelector<HTMLButtonElement>(`[data-stage="${index}"]`)?.click();}
  function invalidate(){if(state.runId&&state.result){state.history=[{id:state.runId,inputs:{...state.result.brief.inputs}},...(state.history||[])].slice(0,5);}state.result=undefined;state.status=undefined;state.runId=undefined;state.requestId=undefined;state.reviewed=false;notice('Inputs changed. Review them before running a fresh study.');}
  host.querySelectorAll<HTMLInputElement>('[data-study-input]').forEach(input=>input.addEventListener('change',()=>{if(working())return;invalidate();state.inputs[input.dataset.studyInput as keyof ChannelInputs]=Number(input.value);save(true);render();}));
  $<HTMLInputElement>('[data-study-confirm]').addEventListener('change',()=>{state.reviewed=$<HTMLInputElement>('[data-study-confirm]').checked&&valid();save(true);render();});
  $('[data-study-prepare]').addEventListener('click',()=>{if(!state.reviewed||!valid())return;save(true);notice('Study brief and equations are ready. Review each stage, then Start at Solve.');goto(1);});
  $('[data-study-brief]').addEventListener('click',()=>{if(!valid())return;const fields=channelFields(state.inputs);const rows=variants(state.inputs).map(v=>`| ${fmt(v.gap_mm)} | ${fmt(v.pa)} | ${fmt(v.re)} |`).join('\n');download('aero-channel-study-brief.md',`# Aero channel study brief\n\n${Object.entries(fields).map(([k,v])=>`## ${k}\n\n${v}`).join('\n\n')}\n\n## Analytical screening\n\n| Gap mm | Pressure drop Pa | Reynolds |\n|---|---|---|\n${rows}\n\nInputs ${state.reviewed?'reviewed':'not yet reviewed'}. These are analytical estimates; no solver completion is implied.\n\n## Planned evidence\n\nNine OpenFOAM solves; mesh/refinement, convergence, conservation and analytical-reference checks; selected gap and numerical margin; downloadable report and hashed case files.`,'text/markdown');});
  $('[data-study-back]').addEventListener('click',()=>goto(currentStage-1));$('[data-study-next]').addEventListener('click',()=>goto(currentStage+1));
  $('[data-study-variant]').addEventListener('change',()=>void viewport());$('[data-study-field]').addEventListener('change',()=>void viewport());
  async function poll(){const id=state.runId;if(!id)return;try{const status=await api('/runs/'+id);if(id!==state.runId)return;state.status=status;if(status.state==='complete'){const result=await api('/runs/'+id+'/result');if(id!==state.runId)return;state.result=result;notice('Fresh result ready. Open Results to inspect the decision and proof.');}save();render();if(!['complete','failed'].includes(status.state))timer=setTimeout(()=>void poll(),2500);}catch(error){if(id!==state.runId)return;const failure=error as Error&{status?:number};if([404,409].includes(failure.status||0)){state.status={...state.status,state:'failed',message:failure.message};save();render();notice('The result is unavailable. Review the inputs and Start a fresh study.');return;}notice(failure.message+' Your run link is saved; reconnecting.');timer=setTimeout(()=>void poll(),10000);}}
  $('[data-study-run]').addEventListener('click',async()=>{if(!state.reviewed||!valid()||working()||state.result)return;if(state.status?.state==='failed')state.requestId=undefined;requestBusy=true;state.requestId ||= crypto.randomUUID();save();render();notice('Submitting the reviewed study…');const requestId=state.requestId;try{const result=await api('/runs',{request_id:requestId,inputs:state.inputs});if(state.requestId!==requestId)return;state.runId=result.id;state.status={state:'queued',completed:0,message:'Queued for OpenFOAM'};save();notice('Run submitted. You can keep discussing the case while the solver works.');void poll();}catch(error){notice((error as Error).message);}finally{requestBusy=false;render();}});
  $('[data-study-report]').addEventListener('click',async()=>{if(!state.runId)return;try{const response=await fetch(base+'/study/runs/'+state.runId+'/report');if(!response.ok)throw Error('Report unavailable or expired');download('aero-channel-study-report.html',await response.text(),'text/html');}catch(error){notice((error as Error).message);}});
  $('[data-study-inspect]').addEventListener('click',()=>{if(!state.runId)return;const frame=$<HTMLIFrameElement>('[data-study-proof]');frame.src=base+'/study/runs/'+state.runId+'/report';frame.hidden=false;frame.scrollIntoView({behavior:'smooth',block:'start'});});
  setInterval(()=>{if(!document.hidden)void health();},45000);void health();
  return {
    load(value?:ChannelState){if(timer)clearTimeout(timer);state=value?structuredClone(value):{inputs:{...defaults},reviewed:false};requestBusy=false;notice('');render();if(state.runId&&!state.result&&state.status?.state!=='failed')void poll();},
    show(index:number){active=true;host.hidden=false;currentStage=index;render();},
    hide(){active=false;host.hidden=true;generation++;disposeView?.();disposeView=undefined;},
    state:()=>structuredClone(state),refresh:()=>progress()
  };
}
