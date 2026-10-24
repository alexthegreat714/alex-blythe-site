"""Independently assemble and solve the scalar equations, then measure error.

Usage: python verify_accuracy.py --output ../../public/demos/aero/square-body-transport-v1
Dependencies: numpy, scipy, matplotlib. No network or private service is used.
"""
import argparse
import csv
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import scipy
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import spsolve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

DEFAULT = dict(L=3., H=2., u=1., rho=1., gamma=.1, inlet=1., solid=0., x0=.8, y0=.75, side=.5, enabled=1)
CASES = dict(baseline=DEFAULT, faster={**DEFAULT,'u':2.}, diffusion={**DEFAULT,'u':0.}, uniform={**DEFAULT,'enabled':0})

def solve(p, nx=61, ny=41):
    dx=p['L']/(nx-1); dy=p['H']/(ny-1)
    x=np.linspace(0,p['L'],nx); y=np.linspace(p['H'],0,ny)
    X,Y=np.meshgrid(x,y)
    mask=(p['enabled']==1)&(X>=p['x0']-1e-9)&(X<=p['x0']+p['side']+1e-9)&(Y>=p['y0']-1e-9)&(Y<=p['y0']+p['side']+1e-9)
    Dx=p['gamma']*dy/dx; Dy=p['gamma']*dx/dy; F=p['rho']*p['u']*dy
    W=Dx+max(F,0); E=Dx+max(-F,0); P=W+E+2*Dy
    rows=[];cols=[];data=[];b=np.zeros(nx*ny)
    for j in range(ny):
        for i in range(nx):
            k=j*nx+i
            if mask[j,i] or i==0:
                neighbors=[(k,1.)];b[k]=p['solid'] if mask[j,i] else p['inlet']
            elif i==nx-1: neighbors=[(k,1.),(k-1,-1.)]
            elif j==0: neighbors=[(k,1.),(k+nx,-1.)]
            elif j==ny-1: neighbors=[(k,1.),(k-nx,-1.)]
            else: neighbors=[(k,P),(k-1,-W),(k+1,-E),(k-nx,-Dy),(k+nx,-Dy)]
            for c,v in neighbors: rows.append(k);cols.append(c);data.append(v)
    A=coo_matrix((data,(rows,cols)),shape=(nx*ny,nx*ny)).tocsr()
    values=spsolve(A,b).reshape(ny,nx)
    residual=float(np.max(np.abs(A@values.ravel()-b)/A.diagonal()))
    return values,mask,dict(nx=nx,ny=ny,dx=dx,dy=dy,normalized_residual=residual,
                           outlet_center=float(values[ny//2,-1]),downstream_center=float(values[ny//2,round(2./dx)]),
                           min=float(values.min()),max=float(values.max()))

def analytical():
    records=[];profiles=[];previous=None
    for nx in [21,41,81,161]:
        h=1/(nx-1);gamma=.1;u=1.;rho=1.;W=gamma/h+rho*u;E=gamma/h;P=W+E
        n=nx-2;A=diags([-W*np.ones(n-1),P*np.ones(n),-E*np.ones(n-1)],[-1,0,1],format='csr')
        b=np.zeros(n);b[-1]=E
        values=np.r_[0.,spsolve(A,b),1.];x=np.linspace(0,1,nx)
        exact=np.expm1(10*x)/np.expm1(10)
        error=float(np.max(np.abs(values-exact)))
        records.append(dict(nodes=nx,dx=h,max_abs_error=error,observed_order=None if previous is None else float(np.log2(previous/error))))
        profiles.append((x,values,exact))
        previous=error
    return records,profiles

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True);figures=out/'paper-sources'/'figures';figures.mkdir(parents=True,exist_ok=True)
    reference=json.loads((out/'workbook-reference.json').read_text())
    excel=json.loads((out/'excel-verification.json').read_text())
    summary=dict(generated_at=datetime.now(timezone.utc).isoformat(),versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),model='steady prescribed-velocity scalar convection-diffusion',cases={},mesh=[],analytical=[],all_passed=True)
    fields={}
    for name,p in CASES.items():
        values,mask,m=solve(p);fields[name]=(values,mask)
        js=np.array(reference[name]['values'])
        m['max_difference_from_workbook_reference']=float(np.max(np.abs(values-js)))
        m['parameters']=p
        m['passed']=m['normalized_residual']<1e-10 and m['max_difference_from_workbook_reference']<1e-7 and m['min']>=-1e-10 and m['max']<=1+1e-10
        summary['cases'][name]=m;summary['all_passed'] &= m['passed']
        with (out/f'{name}.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['x_m','y_m','phi','clamped_square'])
            for j in range(41):
                for i in range(61):w.writerow([i*.05,2-j*.05,float(values[j,i]),int(mask[j,i])])
    previous=None
    for nx,ny in [(61,41),(121,81),(241,161)]:
        values,mask,m=solve(DEFAULT,nx,ny)
        m['max_difference_on_common_fluid_nodes']=None if previous is None else float(np.max(np.abs(previous[0][~previous[1]]-values[::2,::2][~previous[1]])))
        summary['mesh'].append(m);previous=(values,mask)
    summary['analytical'],profiles=analytical()
    summary['analytical_passed']=all(.85<r['observed_order']<1.1 for r in summary['analytical'][1:])
    summary['all_passed'] &= summary['analytical_passed'] and excel['all_passed']
    summary['excel']=excel
    summary['leading_artificial_diffusion']=dict(formula='rho*u*dx/2',baseline_gamma_numerical=.025,ratio_to_physical_gamma=.25,interpretation='leading truncation-error coefficient, not a percentage solution error')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
    fig,axes=plt.subplots(2,2,figsize=(10.4,7.2),layout='constrained')
    titles={'baseline':'Baseline: u = 1 m/s','faster':'Stronger transport: u = 2 m/s','diffusion':'Pure diffusion: u = 0','uniform':'Control: square disabled'}
    for ax,(name,p) in zip(axes.flat,CASES.items()):
        values,mask=fields[name];z=np.ma.array(values,mask=mask)
        im=ax.imshow(z,extent=[-.025,3.025,-.025,2.025],origin='upper',cmap='RdBu_r',vmin=0,vmax=1,interpolation='nearest')
        if p['enabled']:ax.add_patch(Rectangle((p['x0']-.025,p['y0']-.025),p['side']+.05,p['side']+.05,facecolor='white',edgecolor='#283E4A',lw=1))
        ax.set(xlim=(0,3),ylim=(0,2),xlabel='x (m)',ylabel='y (m)',title=titles[name]);ax.set_aspect('equal')
    fig.colorbar(im,ax=axes,shrink=.8,label='Scalar phi (dimensionless)');fig.savefig(figures/'examples.png');fig.savefig(out/'examples.png');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10.4,3.7),layout='constrained')
    x=np.linspace(0,1,500);axes[0].plot(x,np.expm1(10*x)/np.expm1(10),color='#1F3647',label='Exact')
    for (xx,v,_),r in zip(profiles,summary['analytical']):axes[0].plot(xx,v,'--',lw=1,label=f"{r['nodes']} nodes")
    axes[0].set(xlabel='x / L',ylabel='phi',title='1D Dirichlet verification (Pe = 10)');axes[0].legend(fontsize=8)
    hs=[r['dx'] for r in summary['analytical']];errors=[r['max_abs_error'] for r in summary['analytical']]
    axes[1].loglog(hs,errors,'o-',color='#C45932',label='Measured maximum error');axes[1].loglog(hs,np.array(hs)*errors[-1]/hs[-1],':',color='#657072',label='First-order guide')
    axes[1].set(xlabel='Grid spacing',ylabel='Maximum absolute scalar error',title='Error decreases with refinement');axes[1].legend(fontsize=8)
    fig.savefig(figures/'analytical.png');plt.close(fig)
    tables=[]
    def table(name,header,rows,columns):
        content='\\begin{tabular}{'+columns+'}\n\\toprule\n'+header+' \\\\\n\\midrule\n'+'\n'.join(' & '.join(row)+' \\\\' for row in rows)+'\n\\bottomrule\n\\end{tabular}\n'
        (out/'paper-sources'/name).write_text(content)
    table('analytic-table.tex','Nodes & $h$ & $\\|e\\|_\\infty$ & Observed order',[[str(r['nodes']),f"{r['dx']:.5f}",f"{r['max_abs_error']:.5f}",'--' if r['observed_order'] is None else f"{r['observed_order']:.3f}"] for r in summary['analytical']],'rrrr')
    table('mesh-table.tex','Grid & $h_x$ (m) & $\\phi(2,1)$ & $\\phi(3,1)$ & Common-node change',[[f"{r['nx']} $\\times$ {r['ny']}",f"{r['dx']:.4f}",f"{r['downstream_center']:.6f}",f"{r['outlet_center']:.6f}",'--' if r['max_difference_on_common_fluid_nodes'] is None else f"{r['max_difference_on_common_fluid_nodes']:.5f}"] for r in summary['mesh']],'lrrrr')
    table('direct-table.tex','Case & $\\|\\phi_{LU}-\\phi_{GS}\\|_\\infty$ & LU residual',[[name,f"{m['max_difference_from_workbook_reference']:.2e}",f"{m['normalized_residual']:.2e}"] for name,m in summary['cases'].items()],'lrr')
    table('excel-table.tex','Case & Excel vs. GS maximum difference & Excel residual',[[r['case'],f"{r['max_abs_difference_from_independent_solver']:.2e}",f"{r['native_max_normalized_residual']:.2e}"] for r in excel['checks'][:4]],'lrr')
    (out/'accuracy-results.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k not in ['excel','versions']},indent=2))
    if not summary['all_passed']:raise SystemExit('A numerical verification check failed')

if __name__=='__main__':main()
