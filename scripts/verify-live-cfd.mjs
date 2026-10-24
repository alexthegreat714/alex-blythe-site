import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {CASE,CX,CY,W,createFluid,advance,snapshot} from '../public/demos/aero/live-cfd-v1/fluid.mjs';
const out=new URL('../public/demos/aero/live-cfd-v1/',import.meta.url);
assert.ok(Math.abs(W.reduce((a,b)=>a+b)-1)<1e-14);
for(const velocities of [CX,CY])assert.ok(Math.abs(W.reduce((a,w,q)=>a+w*velocities[q],0))<1e-14);
const uniform=createFluid({nx:32,ny:24,periodic:true,u:.025,tau:.7});advance(uniform,1000);const uniformResult=snapshot(uniform);
let uniformError=0;for(let k=0;k<uniform.n;k++)uniformError=Math.max(uniformError,Math.abs(uniformResult.ux[k]-.025),Math.abs(uniformResult.uy[k]));assert.ok(uniformError<1e-6);
const analytical=[];
for(const nx of [32,64]){
  const u=1.28/nx,tau=.7,ticks=nx*nx/16,s=createFluid({nx,ny:nx,u,tau,periodic:true,taylorGreen:true});
  advance(s,ticks);const r=snapshot(s),nu=(tau-.5)/3,decay=Math.exp(-2*nu*(2*Math.PI/nx)**2*ticks);let error=0,norm=0,mass=0;
  for(let y=0;y<nx;y++)for(let x=0;x<nx;x++){const k=y*nx+x,a=2*Math.PI*x/nx,b=2*Math.PI*y/nx,vx=-u*Math.cos(a)*Math.sin(b)*decay,vy=u*Math.sin(a)*Math.cos(b)*decay;error+=(r.ux[k]-vx)**2+(r.uy[k]-vy)**2;norm+=vx*vx+vy*vy;mass+=r.rho[k];}
  const relativeL2=Math.sqrt(error/norm),meanDensityError=Math.abs(mass/(nx*nx)-1);assert.ok(relativeL2<.02);assert.ok(meanDensityError<1e-5);analytical.push({nx,u,tau,ticks,relativeL2,meanDensityError});
}
assert.ok(analytical[1].relativeL2<analytical[0].relativeL2*.8);
const s=createFluid(),probes=[];let minDensity=Infinity,maxDensity=0,maxMach=0,checkpoint;
for(let i=0;i<48;i++){
  advance(s,500);const r=snapshot(s);minDensity=Math.min(minDensity,r.metrics.minDensity);maxDensity=Math.max(maxDensity,r.metrics.maxDensity);maxMach=Math.max(maxMach,r.metrics.maxMach);
  probes.push({step:s.steps,uy:r.uy[40*CASE.nx+95]});
  for(let k=0;k<s.n;k++)if(s.solid[k])assert.equal(r.ux[k]+r.uy[k],0);
  for(let y=0;y<CASE.ny;y++){assert.ok(Math.abs(r.ux[y*CASE.nx]-CASE.u)<1e-6);assert.ok(Math.abs(r.rho[y*CASE.nx+CASE.nx-1]-1)<1e-6);}
  if(s.steps===12000){checkpoint=Buffer.from(s.f.buffer.slice(0));fs.writeFileSync(new URL('wake.bin',out),checkpoint);fs.writeFileSync(new URL('../qa/square-body-transport/wake-snapshot.json',import.meta.url),JSON.stringify(r));}
}
let signChanges=0;for(let i=1;i<probes.length;i++)if(probes[i].uy*probes[i-1].uy<0)signChanges++;
assert.ok(signChanges>=4,'Wake must evolve and alternate');assert.ok(maxMach<.25);
const restarted=createFluid();restarted.f.set(new Float32Array(checkpoint.buffer,checkpoint.byteOffset,checkpoint.length/4));restarted.steps=12000;
advance(restarted,24);const first=snapshot(restarted);const twice=createFluid();twice.f.set(new Float32Array(checkpoint.buffer,checkpoint.byteOffset,checkpoint.length/4));twice.steps=12000;advance(twice,24);assert.deepEqual(first.ux,snapshot(twice).ux);
const checks={generated_at:new Date().toISOString(),method:'D2Q9 TRT lattice Boltzmann',case:CASE,uniform_max_velocity_error:uniformError,taylor_green:analytical,wake:{steps:24000,minDensity,maxDensity,maxMach,probe_sign_changes:signChanges,probes},checkpoint:{steps:12000,bytes:checkpoint.length,sha256:crypto.createHash('sha256').update(checkpoint).digest('hex'),deterministic_restart:true},all_passed:true,experimental_validation:false,grid_independence_demonstrated:false};
fs.writeFileSync(new URL('checks.json',out),JSON.stringify(checks,null,2));console.log(JSON.stringify({...checks,wake:{...checks.wake,probes:undefined}},null,2));
