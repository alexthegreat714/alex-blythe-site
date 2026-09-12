import {mountPressureViewer, type PressureSurface} from './pressure-viewer';
import {mountCadViewer} from './cad-viewer';

export async function mountStructuralGeometry(host:HTMLElement,url:string):Promise<()=>void>{
  const response=await fetch(url,{credentials:'omit'});if(!response.ok)throw Error('CAD artifact unavailable');
  const payload=await response.arrayBuffer();if(!host.isConnected)return ()=>{};
  host.style.cssText='height:350px;width:100%;border:1px solid #304853;border-radius:8px;overflow:hidden';
  const viewer=mountCadViewer(host,payload);return ()=>viewer.dispose();
}

// Uses exactly the existing scientific viewport and verified solver projection.
export async function mountStructuralViewer(host:HTMLElement,url:string,meshOnly=false):Promise<()=>void>{
  const response=await fetch(url,{credentials:'omit'});
  if(!response.ok)throw Error('Recorded structural field unavailable');
  const surface:PressureSurface=await response.json();
  if(!host.isConnected)return ()=>{};
  host.replaceChildren();
  const toolbar=document.createElement('div');toolbar.style.cssText='display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:12px 0;font-size:14px';
  const field=document.createElement('select');field.setAttribute('aria-label','Structural result field');
  Object.keys(surface.fields||{DISPLACEMENT:{}}).forEach(key=>field.add(new Option(key.replaceAll('_',' '),key)));
  const scale=document.createElement('input');scale.type='range';scale.min='0';scale.max='100';scale.value='0';scale.setAttribute('aria-label','Deformation scale');
  const scaleLabel=document.createElement('label');scaleLabel.textContent='Deformation ×0';scaleLabel.append(scale);
  const legend=document.createElement('output');
  const mesh=document.createElement('button');mesh.textContent='Mesh overlay';mesh.setAttribute('aria-pressed',String(meshOnly));
  toolbar.append(field,scaleLabel,mesh,legend);
  if(meshOnly){field.hidden=true;scaleLabel.hidden=true;legend.hidden=true;}
  const canvas=document.createElement('div');canvas.style.cssText='height:350px;width:100%;border:1px solid #304853;border-radius:8px;overflow:hidden';
  host.append(toolbar,canvas);
  const viewer=mountPressureViewer(canvas,surface,{meshOnly});
  const update=()=>{const range=viewer.setField(field.value);legend.textContent=`${range.low.toPrecision(4)} – ${range.high.toPrecision(4)} ${range.units}`;};
  update();field.addEventListener('change',update);
  scale.addEventListener('input',()=>{viewer.setDeformationScale(Number(scale.value));scaleLabel.firstChild!.textContent=`Deformation ×${scale.value} `;});
  let visible=meshOnly;mesh.addEventListener('click',()=>{visible=!visible;viewer.setMeshVisible(visible);mesh.setAttribute('aria-pressed',String(visible));});
  return ()=>viewer.dispose();
}
