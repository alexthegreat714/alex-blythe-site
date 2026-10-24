import {CASE,createFluid,advance,snapshot} from './fluid.mjs';
let state,seed,loop=1;
self.onmessage=async({data})=>{
  try{
    if(data.type==='init'){
      const response=await fetch(new URL('./wake.bin',import.meta.url));if(!response.ok)throw Error('The initial CFD state could not be loaded.');
      const bytes=await response.arrayBuffer();if(bytes.byteLength!==CASE.nx*CASE.ny*9*4)throw Error('Invalid CFD checkpoint.');
      seed=new Float32Array(bytes);state=createFluid();state.f.set(seed);state.steps=12000;loop=1;
    }else if(!state)throw Error('The CFD solver has not initialized.');
    else if(data.type==='restart'){state.f.set(seed);state.steps=12000;loop=1;}
    else if(data.type==='step'){
      advance(state,24);
      if(state.steps>=12000+CASE.loopSteps){state.f.set(seed);state.steps=12000;loop++;}
    }
    const frame=snapshot(state);self.postMessage({type:'frame',...frame,loop},[frame.ux.buffer,frame.uy.buffer,frame.rho.buffer,frame.vorticity.buffer,frame.solid.buffer]);
  }catch(error){self.postMessage({type:'error',message:error.message});}
};
