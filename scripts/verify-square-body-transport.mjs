import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {Worker} from 'node:worker_threads';
import {solve,presets,createProblem} from '../public/demos/aero/square-body-transport-v1/solver.mjs';
const dir=new URL('../public/demos/aero/square-body-transport-v1/',import.meta.url);
const reference=JSON.parse(await fs.readFile(new URL('workbook-reference.json',dir),'utf8'));
const results={};
for(const [name,p] of Object.entries(presets)){
  const s=solve(p);let difference=0;
  for(let j=0;j<s.ny;j++)for(let i=0;i<s.nx;i++)difference=Math.max(difference,Math.abs(s.values[j*s.nx+i]-reference[name].values[j][i]));
  assert.ok(difference<1e-10,`${name}: reference difference ${difference}`);
  assert.ok(s.metrics.residual<1e-10,`${name}: residual`);
  if(name==='uniform')assert.ok(s.values.every(v=>Math.abs(v-1)<1e-10),'Uniform exact control');
  results[name]={iterations:s.iterations,...s.metrics,max_difference_from_workbook_reference:difference};
}
for(const patch of [{gamma:0},{u:-1},{x0:3},{L:NaN},{enabled:2}])assert.throws(()=>createProblem({...presets.baseline,...patch}));
const workerFile=new URL('worker.mjs',dir).href;
const workerHarness=`const {parentPort}=require('node:worker_threads');global.self={postMessage:(data,transfer)=>parentPort.postMessage(data,transfer)};import(${JSON.stringify(workerFile)}).then(()=>parentPort.on('message',data=>self.onmessage({data})));`;
async function runWorker(p){
  const worker=new Worker(workerHarness,{eval:true});
  try{return await new Promise((resolve,reject)=>{
    const timeout=setTimeout(()=>reject(Error('Worker timeout')),30000);
    worker.on('error',e=>{clearTimeout(timeout);reject(e);});
    worker.on('message',data=>{if(data.type==='complete'||data.type==='error'){clearTimeout(timeout);resolve(data);}});
    worker.postMessage({parameters:p});
  });}finally{await worker.terminate();}
}
const message=await runWorker(presets.baseline);assert.equal(message.type,'complete');assert.equal(message.values.length,2501);assert.ok(message.metrics.residual<1e-10);
assert.equal((await runWorker({...presets.baseline,gamma:0})).type,'error');
await fs.writeFile(new URL('browser-solver-checks.json',dir),JSON.stringify({engine:process.version,cases:results,invalid_input_checks:5,worker_message_checks:2,all_passed:true,browser_ui_checked:false},null,2));
console.log(JSON.stringify(results,null,2));
