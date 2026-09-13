"""Generate the actual post-comparison paper, figures and reproduction index.

Refuses to render an unrevealed or unanchored experiment. No fallback values.
"""
import argparse,json,math,re,zipfile
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from protocol import Challenge,sha,encode
from render_result import tex

def save(fig,out,name):
    fig.savefig(out/(name+'.pdf'),bbox_inches='tight')
    fig.savefig(out/(name+'.png'),dpi=170,bbox_inches='tight');plt.close(fig)

def make(root):
    ch=Challenge(root);ch.require('COMPARED_ANCHORED');ch.intact();root=ch.root
    r=ch.load('comparison.json');pred=ch.load('blind_prediction.json');c=ch.load('preregistration.json');inputs=ch.load('input.json')
    out=root/'report';out.mkdir(exist_ok=False)
    results=json.loads((root/'evidence/extracted-values.json').read_text());grids=json.loads((root/'evidence/grid-study.json').read_text());walls=json.loads((root/'evidence/wall-diagnostics.json').read_text())
    stations=inputs['stations'];angles=[inputs['flow_conditions']['angle_of_attack_degrees'][s] for s in stations]
    numerical=ch.load('evidence/numerical-summary.json')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,'figure.constrained_layout.use':True})
    colors={'coarse':'#b0bec5','medium':'#478d9f','fine':'#173e51'}
    fig,axs=plt.subplots(2,2,figsize=(10,7))
    for i,q in enumerate(['CL','CD']):
        rows=[x for x in r['all_points'] if x['quantity']==q]
        for level in ['coarse','medium','fine']:
            axs[i,0].plot(angles,[results[s+'-'+level]['mean_iterations_1500_2000'][q] for s in stations],'.-',color=colors[level],label=level+' RANS')
        axs[i,0].plot(angles,[v['reference'] for v in rows],'s',mfc='none',color='#b64a3a',label='NASA experiment')
        axs[i,0].set(ylabel=q,xlabel='Angle of attack (degrees)')
        axs[i,1].bar(angles,[v['signed_error'] for v in rows],width=.45,color='#478d9f')
        bound=c['acceptance_thresholds'][q]['max_absolute_error']
        axs[i,1].axhline(bound,color='#b64a3a',ls='--');axs[i,1].axhline(-bound,color='#b64a3a',ls='--')
        axs[i,1].set(ylabel='Fine minus experiment, '+q,xlabel='Angle of attack (degrees)')
    axs[0,0].legend(fontsize=8);fig.suptitle('All 18 operating points; no post-reveal adjustment')
    save(fig,out,'comparison')
    fig,axs=plt.subplots(1,2,figsize=(10,3.7))
    for level in colors:
        vals=[v for row in walls if row['case'].endswith('-'+level) for v in row['yplus']]
        axs[0].hist(vals,bins=45,histtype='step',label=level,color=colors[level])
    axs[0].set(xlabel='Final wall y+',ylabel='Wall-face samples (all angles)');axs[0].legend()
    for name,key in [('95th percentile','yplus_p95'),('Maximum','yplus_max')]:axs[1].plot(angles,[results[s+'-fine'][key] for s in stations],'.-',label=name)
    axs[1].axhline(2,color='#b64a3a',ls='--',label='p95 limit');axs[1].axhline(5,color='#b64a3a',ls=':',label='max limit')
    axs[1].set(xlabel='Angle of attack (degrees)',ylabel='Fine-grid y+');axs[1].legend(fontsize=8)
    save(fig,out,'wall-diagnostics')
    fig,axs=plt.subplots(2,2,figsize=(10,7))
    cmap=plt.get_cmap('viridis')
    norm=matplotlib.colors.Normalize(vmin=min(angles),vmax=max(angles))
    for i,s in enumerate(stations):
        with zipfile.ZipFile(root/'evidence/cases'/(s+'-fine.zip')) as z:
            log=z.read('solver.log').decode('utf8',errors='replace')
            force=z.read('case/postProcessing/forces/0/forceCoeffs.dat').decode('utf8')
        rows=[list(map(float,l.split())) for l in force.splitlines() if l.strip() and not l.startswith('#')]
        axs[0,0].plot([v[0] for v in rows],[v[3] for v in rows],color=cmap(norm(angles[i])),lw=.6)
        history=[];its=[]
        for block in log.split('\nTime = ')[1:]:
            m=re.match(r'([0-9.eE+-]+)',block)
            ps=re.findall(r'Solving for p, Initial residual = ([^,]+)',block)
            if m and ps:its.append(float(m[1]));history.append(max(float(ps[-1]),1e-18))
        axs[0,1].semilogy(its,history,color=cmap(norm(angles[i])),lw=.6)
    fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm,cmap=cmap),ax=list(axs[0]),label='Angle of attack (degrees)',shrink=.8)
    axs[0,0].set(xlabel='SIMPLE iteration (not seconds)',ylabel='CL, all fine-grid histories')
    axs[0,1].axhline(1e-4,color='#b64a3a',ls='--');axs[0,1].set(xlabel='SIMPLE iteration',ylabel='Pressure initial residual, final correction')
    for level in colors:
        vals=[max(results[s+'-'+level]['boundary_flux_imbalance_fraction'],1e-18) for s in stations]
        axs[1,0].semilogy(angles,vals,'.-',label=level,color=colors[level])
    axs[1,0].axhline(.001,color='#b64a3a',ls='--');axs[1,0].set(xlabel='Angle (degrees)',ylabel='Final boundary flux imbalance');axs[1,0].legend()
    axs[1,1].plot(angles,[g['medium_fine_absolute_change']['CL'] for g in grids],'.-',label='|delta CL|')
    axs[1,1].plot(angles,[g['medium_fine_absolute_change']['CD'] for g in grids],'.-',label='|delta CD|')
    axs[1,1].axhline(.02,color='#b64a3a',ls='--');axs[1,1].axhline(.002,color='#b64a3a',ls=':');axs[1,1].set(xlabel='Angle (degrees)',ylabel='Medium-to-fine change');axs[1,1].legend()
    save(fig,out,'numerical-evidence')
    # Actual mesh edges, not an illustrative airfoil graphic.
    fig,axs=plt.subplots(1,3,figsize=(10,3.5))
    for ax,level in zip(axs,['coarse','medium','fine']):
        with zipfile.ZipFile(root/'evidence/cases'/('p01-'+level+'.zip')) as z:
            raw=z.read('case/constant/polyMesh/points').decode();ff=z.read('case/constant/polyMesh/faces').decode()
        pts=[tuple(map(float,v.split())) for v in re.findall(r'\(([-+0-9.eE ]+)\)',raw)]
        faces=[list(map(int,v.split())) for v in re.findall(r'\d+\(([^)]+)\)',ff)]
        seg=[]
        for face in faces:
            if not all(abs(pts[v][2]-pts[face[0]][2])<1e-10 for v in face):continue
            if pts[face[0]][2]<0:continue
            for a,b in zip(face,face[1:]+face[:1]):
                p,q=pts[a],pts[b]
                if -.1<=p[0]/.601<=1.2 and abs(p[1]/.601)<.25:seg.append([(p[0]/.601,p[1]/.601),(q[0]/.601,q[1]/.601)])
        ax.add_collection(LineCollection(seg,linewidths=.15,color=colors[level]));ax.set(xlim=(-.1,1.2),ylim=(-.2,.2),xlabel='x/c',title=level);ax.set_aspect('equal')
    axs[0].set_ylabel('y/c');save(fig,out,'mesh')
    # Nine deliberately structured report pages; each holds actual evidence.
    lines=[r'\documentclass[10pt]{article}',r'\usepackage[margin=0.78in]{geometry}',r'\usepackage{graphicx,booktabs,longtable,amsmath,hyperref,xcolor}',r'\hypersetup{colorlinks=true,urlcolor=blue}',r'\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}',r'\begin{document}',r'\title{Aero Challenge 01\\A Reference-Withheld NACA 0012 Prediction Experiment}',r'\author{Alex Blythe / Aero engineering record}\date{September 2026}\maketitle',r'\begin{abstract}']
    lines.append(tex('A nominal two-dimensional steady-RANS prediction was preregistered, executed on three grids at each of 18 angles, and frozen before the experimental reference was revealed. The numerical disposition is '+r['numerical_status']+'; experimental coefficient comparison is '+r['experimental_comparison']+'; overall status is '+r['status']+'. This result is preserved without post-reveal tuning.'))
    lines.extend([r'\end{abstract}',r'\section{Decision and scope}',tex(pred['engineering_disposition']),r'\section{What was actually tested}',tex('NASA TM-4074 Table XIII, first subtable: NACA0012, Mach0.15, Reynolds number5.95 million, fixed transition strips at5 percent chord. The complete18-point CL/CD polar is retained. This is not a Cp-field comparison, an as-built reconstruction or a certified design calculation.'),r'\section{Independence limitation}',tex('The solver containers had no reference or decryption key. However, the source-exposed supervisor authored the numerical setup. This is runtime reference withholding, not double-blind source selection or independently blinded supervisory design. A fresh input-only model review does not remove that limitation.'),r'\section{Top-level results}',r'\begin{tabular}{lrrl}\toprule Quantity & RMSE & Maximum absolute error & Gate\\\midrule'])
    # Add numerical failures and utility bounds before the results table.
    lines.insert(len(lines)-1,tex(f"{numerical['cases_passing_applicable_individual_gates']} of {numerical['case_count']} cases passed their applicable individual numerical gates; {numerical['grid_pairs_passing']} of {numerical['grid_pairs_total']} medium/fine comparisons passed. {numerical['mesh_cases_with_failed_checkMesh_checks']} meshes retained failed checkMesh checks under the declared thin-grid policy, not clean mesh-quality passes."))
    lines.insert(len(lines)-1,tex('Frozen experimental bounds: CL RMSE <=0.10 and maximum absolute error <=0.20; CD RMSE <=0.005 and maximum absolute error <=0.010. These are declared utility bounds, not experimental confidence intervals.'))
    for q,m in r['metrics'].items():lines.append(f"{q} & {m['rmse']:.6f} & {m['max_absolute_error']:.6f} & {'PASS' if m['pass'] else 'FAIL'}\\\\")
    lines += [r'\bottomrule\end{tabular}',r'\clearpage\section{Source reconstruction and chronology}',tex(inputs['source_citation']),tex('The permitted package records the geometry description, every operating point, facility conditions and unknowns. Measured coefficients were transcribed and sealed by a source-exposed custodian. Per-point uncertainty is not supplied; no invented confidence interval or post-hoc tolerance widening is used.'),r'\begin{longtable}{p{.31\linewidth}p{.62\linewidth}}\toprule Event & UTC timestamp\\\midrule']
    for e in ch.state()['events']:lines.append(tex(e['stage'])+' & '+tex(e['time'])+r'\\')
    lines += [r'\bottomrule\end{longtable}',r'\subsection{Custody and execution separation}',tex('The original source PDF and plaintext reference were held outside the website repository. AES-256-GCM ciphertext and input hashes were public before prediction. Each solver container was non-root, network-disabled and capability-dropped, with a read-only generator and a fresh output bind. No RAG or model inference occurred during solving.'),r'\subsection{No retroactive tuning}',tex('Model choices, mesh counts, averaging windows and acceptance thresholds were fixed in the preregistration commit. All run attempts were retained. Reproduction and report-generation code performs declared arithmetic; it does not choose a more favorable angle subset.'),r'\clearpage\section{Numerical model and geometry}',tex(c['governing_equations']),tex(c['wall_treatment']['trip_surrogate']),tex('Inlet turbulence intensity0.1 percent and length scale0.01c are assumptions, not tunnel measurements. The nominal chord is0.601m. Velocity is0.15 sqrt(1.4 R T) at an assumed288.15K; kinematic viscosity is Uc/Re, preserving chord Reynolds number. Coefficients use kinematic pressure normalization; no atmospheric-density claim is made.'),r'\begin{equation} C_L=\frac{L}{\tfrac12\rho U_\infty^2 c b},\qquad C_D=\frac{D}{\tfrac12\rho U_\infty^2 c b},\qquad \nu=\frac{U_\infty c}{Re_c}.\end{equation}',r'\includegraphics[width=\linewidth]{mesh.pdf}',tex('Actual retained mesh edges from the three p01 cases. The nominal surface comes from the pinned Foundation10 geometry asset. Template and geometry provenance are retained with GPL licensing. Thin-cell/aspect-ratio warnings are not erased; checkMesh logs accompany every case.'),r'\clearpage\section{Wall treatment and numerical gates}',r'\includegraphics[width=\linewidth]{wall-diagnostics.pdf}',tex('The fine-grid95th-percentile y+ limit is2 and its maximum limit is5. A passing y+ check alone does not establish transition equivalence, turbulence-model adequacy or physical validation. The imposed intermittency band is not a geometrically resolved grit strip.'),r'\subsection{Acceptance policy}',tex('Each case must finish2000 SIMPLE iterations with finite fields and verified trip constraints. Initial residuals at the final iteration must be at most1e-4 and final linear residuals at most1e-6 for the declared fields. Boundary-flux imbalance must be at most0.001; the separate solver-continuity limits remain in preregistration.'),tex('Means over iterations1000--1500 and1500--2000 must differ by at most0.01 CL and0.001 CD. Last500-iteration ranges must be at most0.02 CL and0.002 CD. Medium-to-fine differences must be at most0.02 CL and0.002 CD. Iteration means are not physical-time averages.'),r'\clearpage\section{Convergence, conservation and grid sensitivity}',r'\includegraphics[width=\linewidth]{numerical-evidence.pdf}',tex('Every fine-grid force and pressure-residual history is shown. Boundary flux is independently summed over retained patch fluxes and normalized by total absolute boundary flux; it is not a residual relabeled as conservation. Numerical warnings and failed gates are retained even if the coefficient comparison happens to agree.'),r'\clearpage\section{Frozen prediction versus experiment}',r'\includegraphics[width=\linewidth]{comparison.pdf}',tex('All points are shown on their registered angles. Dashed error bounds are the preregistered maximum-absolute-error limits. Experimental uncertainty bars are absent because pointwise uncertainty is not supplied. The fine grid supplies the frozen prediction; no grid extrapolation is substituted after reveal.'),r'\clearpage\section{Complete coefficient errors}',r'\begin{longtable}{rrrrrrr}\toprule $\alpha$ & $C_L$ pred. & $C_L$ exp. & Error & $C_D$ pred. & $C_D$ exp. & Error\\\midrule']
    lookup={(v['quantity'],v['station']):v for v in r['all_points']}
    for s,a in zip(stations,angles):
        l,d=lookup['CL',s],lookup['CD',s]
        lines.append(' & '.join(f'{v:.5f}' for v in [a,l['prediction'],l['reference'],l['signed_error'],d['prediction'],d['reference'],d['signed_error']])+r'\\')
    lines += [r'\bottomrule\end{longtable}',r'\subsection{Experimental and numerical outcomes are separate}',tex('Numerical status: '+r['numerical_status']+'. Experimental comparison: '+r['experimental_comparison']+'. Overall status: '+r['status']+'. A failed numerical gate prevents an overall PASS regardless of coefficient agreement. This report does not infer a unique physical cause of error from coefficient mismatch alone.'),r'\clearpage\section{Limitations and reproduction}',tex('The study assumes a nominal two-dimensional geometry, low-Mach incompressibility, an assumed inlet turbulence state and a prescribed-transition surrogate. The source does not establish exact as-built coordinates, grit height, series temperature or pointwise coefficient uncertainty. A steady RANS fixed point cannot establish physical steadiness near stall. No transient averaging, spanwise instability resolution or physical grit drag is claimed.'),tex('During pre-registration development, rejected O-grid and C-grid attempts exposed mesh-quality and runtime issues. A case-insensitive Phi/phi filename collision was repaired by not exporting the uppercase potential field. The unmodified transition model uses limiting expressions with zero-vorticity denominators: floating-point trapping was disabled, but stored fields and coefficients were required to be finite. These decisions are recorded before production, not hidden post-reveal repairs.'),r'\subsection{Reproduce a case}',r'\begin{verbatim}python code/execute_case.py NEW_OUTPUT --level fine',r'  --angle -3.99 --duration 2000 --timeout 7200',r'\end{verbatim}',tex('Use the pinned public OpenFOAM10 image recorded in preregistration. Every case archive includes generated geometry, mesh, initial/final fields, constraints, decks, logs, coefficient history, extraction results and its own file-hash manifest. Archive hashes are committed with the prediction. Running the code requires Docker and local Python; no model token or private VM access is required.'),r'\subsection{References}',r'\begin{enumerate}',r'\item C. L. Ladson. NASA TM-4074 (1988). \url{https://ntrs.nasa.gov/citations/19880019495}.',r'\item OpenFOAM Foundation, Version10 source and user guide. \url{https://doc.cfd.direct/openfoam/user-guide-v10/}.',r'\item R. B. Langtry and F. R. Menter (2009), Correlation-based transition modeling for unstructured parallelized CFD codes, AIAA Journal47(12),2894--2906. Model implementation: Foundation10 kOmegaSSTLM.',r'\end{enumerate}',r'\clearpage\section{Commitments and artifact identity}']
    for name in ['input.json','reference.enc','preregistration.json','blind_prediction.json','comparison.json']:
        lines += [r'\paragraph{'+tex(name)+'}',r'{\small\ttfamily\detokenize{'+sha((root/name).read_bytes())+r'}}']
    for e in ch.state()['events']:
        if e.get('commit'):lines += [r'\paragraph{'+tex(e['stage'])+'}',r'\url{https://github.com/alexthegreat714/alex-blythe-site/commit/'+e['commit']+'}']
    lines += [tex('Hashes establish identity, not scientific validity or an immutable timestamp against repository administrators. The original frozen prediction and its failures remain preserved. Any later tuning must be published as a separately versioned follow-up.'),r'\end{document}']
    (out/'paper.tex').write_text('\n'.join(lines)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'report_source':str(out/'paper.tex'),'result':r['status']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);a=p.parse_args();make(a.package)
