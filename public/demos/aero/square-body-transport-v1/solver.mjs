// Steady scalar transport. No velocity or pressure equations are solved here.
export const defaults = Object.freeze({L:3,H:2,u:1,rho:1,gamma:0.1,inlet:1,solid:0,x0:0.8,y0:0.75,side:0.5,enabled:1});
export const presets = {
  baseline:{...defaults}, faster:{...defaults,u:2},
  diffusion:{...defaults,u:0}, uniform:{...defaults,enabled:0},
};
export function validate(p) {
  if(Object.keys(defaults).some(k=>typeof p[k]!=='number'||!Number.isFinite(p[k]))) throw new Error('Enter a finite number in every input.');
  if(p.L<=0||p.H<=0||p.rho<=0||p.gamma<=0||p.u<0) throw new Error('Dimensions, density and diffusion must be positive. Velocity must be zero or positive.');
  if(p.x0<=0||p.y0<=0||p.side<=0||p.x0+p.side>=p.L||p.y0+p.side>=p.H) throw new Error('Keep the square strictly inside the domain.');
  if(![0,1].includes(p.enabled)) throw new Error('Square enabled must be 0 or 1.');
}
export function createProblem(parameters=defaults,nx=61,ny=41) {
  const p={...parameters};validate(p);
  if(!Number.isInteger(nx)||!Number.isInteger(ny)||nx<3||ny<3||nx>241||ny>161) throw new Error('Grid dimensions are outside the supported range.');
  const dx=p.L/(nx-1),dy=p.H/(ny-1),Dx=p.gamma*dy/dx,Dy=p.gamma*dx/dy,F=p.rho*p.u*dy;
  const c={dx,dy,Dx,Dy,F,W:Dx+Math.max(F,0),E:Dx+Math.max(-F,0),N:Dy,S:Dy,P:2*Dx+2*Dy+Math.abs(F),Pe:Math.abs(F)/Dx};
  const values=new Float64Array(nx*ny),mask=new Uint8Array(nx*ny);
  for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){
    const x=i*dx,y=p.H-j*dy,k=j*nx+i;
    mask[k]=p.enabled&&x>=p.x0-1e-9&&x<=p.x0+p.side+1e-9&&y>=p.y0-1e-9&&y<=p.y0+p.side+1e-9?1:0;
    values[k]=mask[k]?p.solid:p.inlet;
  }
  return {p,nx,ny,c,values,mask,iterations:0,change:Infinity};
}
function target(s,i,j,k) {
  const {p,nx,ny,c,values:a,mask}=s;
  if(mask[k])return p.solid;
  if(i===0)return p.inlet;
  if(i===nx-1)return a[k-1];
  if(j===0)return a[k+nx];
  if(j===ny-1)return a[k-nx];
  return (c.W*a[k-1]+c.E*a[k+1]+c.N*a[k-nx]+c.S*a[k+nx])/c.P;
}
export function sweep(s,count=100,tolerance=1e-12) {
  for(let n=0;n<count;n++){
    let change=0;
    for(let j=0;j<s.ny;j++)for(let i=0;i<s.nx;i++){
      const k=j*s.nx+i,v=target(s,i,j,k);change=Math.max(change,Math.abs(v-s.values[k]));s.values[k]=v;
    }
    s.iterations++;s.change=change;
    if(!Number.isFinite(change))throw new Error('The calculation became non-finite. Check the inputs.');
    if(change<tolerance)return true;
  }
  return false;
}
export function measure(s) {
  let residual=0,min=Infinity,max=-Infinity,symmetry=0;
  for(let j=0;j<s.ny;j++)for(let i=0;i<s.nx;i++){
    const k=j*s.nx+i,v=s.values[k];residual=Math.max(residual,Math.abs(v-target(s,i,j,k)));
    min=Math.min(min,v);max=Math.max(max,v);symmetry=Math.max(symmetry,Math.abs(v-s.values[(s.ny-1-j)*s.nx+i]));
  }
  return {residual,min,max,symmetry,outletCenter:s.values[Math.floor(s.ny/2)*s.nx+s.nx-1]};
}
export function solve(parameters=defaults) {
  const s=createProblem(parameters);let converged=false;
  while(s.iterations<60000&&!converged)converged=sweep(s,100);
  if(!converged)throw new Error('Iteration limit reached. The result has not converged.');
  return {...s,metrics:measure(s)};
}
