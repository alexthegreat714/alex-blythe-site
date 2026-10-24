type Frame={nx:number;ny:number;steps:number;convectiveTime:number;loop:number;ux:Float32Array;uy:Float32Array;rho:Float32Array;vorticity:Float32Array;solid:Uint8Array;metrics:{maxMach:number;minDensity:number;maxDensity:number}};
export function startLiveCFD(){
  const canvases=[...document.querySelectorAll<HTMLCanvasElement>('[data-cfd-canvas]')];
  const controls=[...document.querySelectorAll<HTMLButtonElement>('[data-cfd-toggle]')];
  const statuses=[...document.querySelectorAll<HTMLElement>('[data-cfd-status]')];
  const preference=matchMedia('(prefers-reduced-motion: reduce)');
  let enabled=!preference.matches,pending=false,restartRequested=false,frame:Frame|null=null,worker:Worker|null=null,timer=0,failed=false;
  const visible=new Set<Element>();
  const pixels=document.createElement('canvas');pixels.width=192;pixels.height=80;
  const pixelContext=pixels.getContext('2d')!,image=pixelContext.createImageData(192,80);
  const mode=document.querySelector<HTMLSelectElement>('#cfd-display')!;
  const info=document.querySelector<HTMLElement>('#cfd-time')!;
  const download=document.querySelector<HTMLButtonElement>('#cfd-csv')!;
  function active(){return enabled&&visible.size>0&&!document.hidden&&!failed;}
  function sync(){
    for(const button of controls){button.hidden=false;button.textContent=enabled?'Pause simulation':'Play simulation';button.setAttribute('aria-pressed',String(enabled));}
    for(const canvas of canvases)canvas.dataset.cfdState=failed?'error':!frame?'loading':active()?'running':'paused';
    for(const status of statuses)status.textContent=failed?'The CFD calculation could not continue. Reload to retry.':!frame?'Loading the computed flow state…':`${active()?'LIVE · solving':'PAUSED'} · Re = 80 · ${frame.steps.toLocaleString()} time steps · loop ${frame.loop}`;
    clearTimeout(timer);if(active()&&frame&&!pending)timer=window.setTimeout(step,16);
  }
  function step(){if(!active()||pending||!worker)return;pending=true;worker.postMessage({type:'step'});}
  function render(){
    if(!frame)return;
    const f=frame,view=mode.value;
    for(let k=0;k<f.nx*f.ny;k++){
      let rgb:number[];
      if(f.solid[k])rgb=[235,255,244];
      else if(view==='speed'){
        const t=Math.min(1,Math.hypot(f.ux[k],f.uy[k])/.065/1.7),stops=[[7,22,37],[36,110,174],[66,216,184],[255,225,117]],z=t*3,a=Math.min(2,Math.floor(z)),v=z-a;
        rgb=stops[a].map((c,i)=>c+(stops[a+1][i]-c)*v);
      }else{
        const v=view==='pressure'?2*(f.rho[k]-1)/(3*.065*.065)/4:f.vorticity[k]*12/.065/1.8,t=Math.pow(Math.min(1,Math.abs(v)),.55),low=[8,25,40],high=v<0?[60,204,235]:[255,119,72];
        rgb=low.map((c,i)=>c+(high[i]-c)*t);
      }
      image.data[k*4]=rgb[0];image.data[k*4+1]=rgb[1];image.data[k*4+2]=rgb[2];image.data[k*4+3]=255;
    }
    pixelContext.putImageData(image,0,0);
    for(const canvas of canvases){
      if(!visible.has(canvas)&&canvas.dataset.cfdReady==='true')continue;
      const c=canvas.getContext('2d')!;c.imageSmoothingEnabled=true;c.drawImage(pixels,0,0,canvas.width,canvas.height);canvas.hidden=false;canvas.dataset.cfdReady='true';canvas.dataset.cfdStep=String(f.steps);canvas.dataset.cfdLoop=String(f.loop);
      canvas.closest('[data-cfd-render]')?.querySelector<HTMLImageElement>('img')?.setAttribute('hidden','');
    }
    info.textContent=`tU/D = ${f.convectiveTime.toFixed(2)} · max Mach ${f.metrics.maxMach.toFixed(3)} · density ${f.metrics.minDensity.toFixed(4)}–${f.metrics.maxDensity.toFixed(4)}`;
    document.querySelector('#cfd-legend')!.textContent=view==='speed'?'Speed / inlet speed · 0 → 1.7':view==='pressure'?'Pressure coefficient · blue negative / orange positive':'Vorticity × D/U · blue negative / orange positive';
    download.disabled=false;
  }
  function init(){
    try{
      worker=new Worker('/demos/aero/live-cfd-v1/worker.mjs',{type:'module'});pending=true;
      worker.onmessage=({data})=>{pending=false;if(data.type==='error'){failed=true;sync();return;}frame=data;render();if(restartRequested){restartRequested=false;pending=true;worker!.postMessage({type:'restart'});}sync();};
      worker.onerror=()=>{pending=false;failed=true;sync();};worker.postMessage({type:'init'});
    }catch{failed=true;sync();}
  }
  const renders=[...document.querySelectorAll<HTMLElement>('[data-cfd-render]')];
  const visibility=new IntersectionObserver(entries=>{for(const entry of entries){const canvas=entry.target.querySelector('canvas')!;if(entry.isIntersecting)visible.add(canvas);else visible.delete(canvas);}if(frame)render();sync();});
  renders.forEach(render=>visibility.observe(render));
  controls.forEach(button=>button.addEventListener('click',()=>{enabled=!enabled;sync();}));
  document.querySelector('#cfd-restart')!.addEventListener('click',()=>{if(!worker)return;if(pending){restartRequested=true;return;}pending=true;worker.postMessage({type:'restart'});});
  mode.addEventListener('change',render);
  preference.addEventListener('change',()=>{enabled=!preference.matches;sync();});document.addEventListener('visibilitychange',sync);
  download.addEventListener('click',()=>{
    if(!frame)return;const f=frame,rows=['x_lattice,y_lattice,u_lattice,v_lattice,density,pressure_excess,vorticity,solid'];
    for(let y=0;y<f.ny;y++)for(let x=0;x<f.nx;x++){const k=y*f.nx+x;rows.push([x,y,f.ux[k],f.uy[k],f.rho[k],(f.rho[k]-1)/3,f.vorticity[k],f.solid[k]].join(','));}
    const url=URL.createObjectURL(new Blob([rows.join('\n')],{type:'text/csv'})),a=document.createElement('a');a.href=url;a.download=`live-cfd-step-${f.steps}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  window.addEventListener('pagehide',()=>{clearTimeout(timer);worker?.terminate();worker=null;});
  window.addEventListener('pageshow',event=>{if(event.persisted){frame=null;pending=false;failed=false;init();sync();}});
  sync();init();
}
