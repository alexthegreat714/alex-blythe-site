import {createProblem,sweep,measure} from './solver.mjs';
self.onmessage=({data})=>{
  try{
    const s=createProblem(data.parameters);
    function advance(){
      try{
        const converged=sweep(s,100);
        if(converged){
          const metrics=measure(s);
          self.postMessage({type:'complete',p:s.p,nx:s.nx,ny:s.ny,c:s.c,iterations:s.iterations,metrics,values:s.values,mask:s.mask},[s.values.buffer,s.mask.buffer]);
        }else if(s.iterations>=60000)self.postMessage({type:'error',message:'Iteration limit reached. No converged result is available for these inputs.'});
        else{self.postMessage({type:'progress',iterations:s.iterations,change:s.change});setTimeout(advance,0);}
      }catch(e){self.postMessage({type:'error',message:e.message});}
    }
    advance();
  }catch(e){self.postMessage({type:'error',message:e.message});}
};
