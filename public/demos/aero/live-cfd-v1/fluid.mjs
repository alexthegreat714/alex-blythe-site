// D2Q9 two-relaxation-time lattice Boltzmann: density and momentum evolve.
// Lattice units dx=dt=1, cs^2=1/3, nu=(tau-1/2)/3.
export const CX=[0,1,0,-1,0,1,-1,-1,1];
export const CY=[0,0,1,0,-1,1,1,-1,-1];
export const OPP=[0,3,4,1,2,7,8,5,6];
export const W=[4/9,1/9,1/9,1/9,1/9,1/36,1/36,1/36,1/36];
export const CASE=Object.freeze({nx:192,ny:80,side:12,x0:42,y0:34,u:.065,re:80,tau:.52925,loopSteps:12000});
export function createFluid(options={}){
  const p={...CASE,...options},n=p.nx*p.ny;
  if(!Number.isInteger(p.nx)||!Number.isInteger(p.ny)||p.nx<8||p.ny<8||!(p.tau>.5)||p.u<0||p.u>.12)throw Error('Invalid lattice configuration.');
  const f=new Float32Array(n*9),post=new Float32Array(n*9),next=new Float32Array(n*9),solid=new Uint8Array(n),source=new Int32Array(n*9);
  const rho=new Float32Array(n),ux=new Float32Array(n),uy=new Float32Array(n);
  for(let y=0;y<p.ny;y++)for(let x=0;x<p.nx;x++){
    const k=y*p.nx+x;
    solid[k]=!p.periodic&&p.obstacle!==false&&x>=p.x0&&x<p.x0+p.side&&y>=p.y0&&y<p.y0+p.side?1:0;
  }
  for(let y=0;y<p.ny;y++)for(let x=0;x<p.nx;x++){
    const k=y*p.nx+x;let vx=p.u,vy=0;
    if(p.taylorGreen){const a=2*Math.PI*x/p.nx,b=2*Math.PI*y/p.ny;vx=-p.u*Math.cos(a)*Math.sin(b);vy=p.u*Math.sin(a)*Math.cos(b);}
    else if(!p.periodic)vy=p.u*.05*Math.exp(-(((x-p.x0-p.side-8)/18)**2)-(((y-p.ny/2)/15)**2));
    if(solid[k])vx=vy=0;
    const density=p.taylorGreen?1-.75*p.u*p.u*(Math.cos(4*Math.PI*x/p.nx)+Math.cos(4*Math.PI*y/p.ny)):1;
    for(let q=0;q<9;q++){
      const eu=CX[q]*vx+CY[q]*vy;f[q*n+k]=W[q]*density*(1+3*eu+4.5*eu*eu-1.5*(vx*vx+vy*vy));
      let sx=x-CX[q],sy=(y-CY[q]+p.ny)%p.ny;
      if(p.periodic)sx=(sx+p.nx)%p.nx;
      source[q*n+k]=sx<0||sx>=p.nx?-2:solid[sy*p.nx+sx]?-1:sy*p.nx+sx;
    }
  }
  const s={p,n,f,post,next,solid,source,rho,ux,uy,steps:0};macroscopic(s);return s;
}
export function macroscopic(s){
  const {n,f,rho,ux,uy,solid}=s;
  for(let k=0;k<n;k++){
    if(solid[k]){rho[k]=1;ux[k]=uy[k]=0;continue;}
    const a=f[k],b=f[n+k],c=f[2*n+k],d=f[3*n+k],e=f[4*n+k],g=f[5*n+k],h=f[6*n+k],i=f[7*n+k],j=f[8*n+k];
    const r=a+b+c+d+e+g+h+i+j;
    rho[k]=r;ux[k]=(b+g+j-d-h-i)/r;uy[k]=(c+g+h-e-i-j)/r;
  }
}
export function advance(s,count=1){
  const {p,n,post,source,solid}=s,omega=1/p.tau,omegaOdd=1/(.5+(3/16)/(p.tau-.5));
  for(let tick=0;tick<count;tick++){
    const f=s.f,next=s.next;
    for(let k=0;k<n;k++){
      if(solid[k])continue;
      const a=f[k],b=f[n+k],c=f[2*n+k],d=f[3*n+k],e=f[4*n+k],g=f[5*n+k],h=f[6*n+k],i=f[7*n+k],j=f[8*n+k];
      const r=a+b+c+d+e+g+h+i+j,vx=(b+g+j-d-h-i)/r,vy=(c+g+h-e-i-j)/r,vv=vx*vx+vy*vy;
      for(let q=0;q<9;q++){const eu=CX[q]*vx+CY[q]*vy,at=q*n+k,op=f[OPP[q]*n+k],wr=W[q]*r;post[at]=f[at]-omega*((f[at]+op)/2-wr*(1+4.5*eu*eu-1.5*vv))-omegaOdd*((f[at]-op)/2-3*wr*eu);}
    }
    for(let q=0;q<9;q++){
      const at=q*n,opp=OPP[q]*n;
      for(let k=0;k<n;k++)if(!solid[k]){const from=source[at+k];next[at+k]=from>=0?post[at+from]:from===-1?post[opp+k]:0;}
    }
    if(!p.periodic)for(let y=0;y<p.ny;y++){
      // Zou/He velocity inlet (left), density/pressure outlet (right).
      let k=y*p.nx;
      let r=(next[k]+next[2*n+k]+next[4*n+k]+2*(next[3*n+k]+next[6*n+k]+next[7*n+k]))/(1-p.u);
      next[n+k]=next[3*n+k]+2/3*r*p.u;
      next[5*n+k]=next[7*n+k]+.5*(next[4*n+k]-next[2*n+k])+r*p.u/6;
      next[8*n+k]=next[6*n+k]+.5*(next[2*n+k]-next[4*n+k])+r*p.u/6;
      k+=p.nx-1;r=1;
      const vx=-1+(next[k]+next[2*n+k]+next[4*n+k]+2*(next[n+k]+next[5*n+k]+next[8*n+k]))/r;
      next[3*n+k]=next[n+k]-2/3*r*vx;
      next[6*n+k]=next[8*n+k]+.5*(next[4*n+k]-next[2*n+k])-r*vx/6;
      next[7*n+k]=next[5*n+k]+.5*(next[2*n+k]-next[4*n+k])-r*vx/6;
    }
    s.f=next;s.next=f;s.steps++;
  }
}
export function snapshot(s){
  macroscopic(s);const {p,n,rho,ux,uy,solid}=s;
  let maxSpeed=0,minDensity=Infinity,maxDensity=-Infinity,sum=0,maxVorticity=0;
  const vorticity=new Float32Array(n);
  for(let y=0;y<p.ny;y++)for(let x=0;x<p.nx;x++){
    const k=y*p.nx+x;if(solid[k])continue;
    const speed=Math.hypot(ux[k],uy[k]);maxSpeed=Math.max(maxSpeed,speed);minDensity=Math.min(minDensity,rho[k]);maxDensity=Math.max(maxDensity,rho[k]);sum+=rho[k];
    const l=x? k-1:k,r=x<p.nx-1?k+1:k,t=((y-1+p.ny)%p.ny)*p.nx+x,b=((y+1)%p.ny)*p.nx+x;
    vorticity[k]=(uy[r]-uy[l])/2-(ux[b]-ux[t])/2;maxVorticity=Math.max(maxVorticity,Math.abs(vorticity[k]));
  }
  if(!Number.isFinite(maxSpeed)||minDensity<.8||maxDensity>1.2||maxSpeed>.3)throw Error('Flow solver left its numerical stability limits. Restart the example.');
  return {nx:p.nx,ny:p.ny,steps:s.steps,convectiveTime:s.steps*p.u/p.side,ux:ux.slice(),uy:uy.slice(),rho:rho.slice(),vorticity,solid:solid.slice(),metrics:{maxSpeed,maxMach:maxSpeed*Math.sqrt(3),minDensity,maxDensity,totalDensity:sum,maxVorticity}};
}
