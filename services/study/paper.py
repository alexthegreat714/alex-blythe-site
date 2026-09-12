"""Source-owned LaTeX paper and numerical figures, never model-generated TeX."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def tex(value):
    replacements={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(replacements.get(c,c) for c in str(value))


def prepare(result, destination, screenshots=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    output=Path(destination);output.mkdir(parents=True,exist_ok=True)
    variants=result['variants'];p=result['brief']['inputs'];colors=['#b66738','#147e96','#34794b']
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#23323c','text.color':'#23323c','savefig.facecolor':'white'})
    def save(fig,name):
        fig.savefig(output/(name+'.pdf'),bbox_inches='tight');fig.savefig(output/(name+'.png'),dpi=170,bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,3.4),layout='constrained');x=np.arange(3)
    ax.bar(x-.17,[v['pressure_drop_pa'] for v in variants],.34,label='OpenFOAM fine grid',color='#147e96')
    ax.bar(x+.17,[v['analytical_pa'] for v in variants],.34,label='Analytical reference',color='#abc7cc')
    ax.axhline(p['budget_pa'],color='#b14d31',linestyle='--',label=f"Budget: {p['budget_pa']:g} Pa")
    ax.set(xticks=x,xticklabels=[f"{v['gap_mm']:g}" for v in variants],xlabel='Full channel gap (mm)',ylabel='Pressure drop (Pa)');ax.legend(fontsize=9);save(fig,'decision')
    fig,(ax,bx)=plt.subplots(1,2,figsize=(7,3),layout='constrained')
    for v,c in zip(variants,colors):
        cells=[g['cells'] for g in v['levels']];dp=[g['pressure_drop_pa'] for g in v['levels']]
        ax.plot(cells,dp,'o-',color=c,label=f"{v['gap_mm']:g} mm");ax.axhline(v['analytical_pa'],color=c,linestyle=':',alpha=.6)
        bx.plot(cells,[g['reference_error_pct'] for g in v['levels']],'o-',color=c)
    ax.set(xlabel='Cells',ylabel='Pressure drop (Pa)');ax.legend(fontsize=9)
    bx.axhline(2,color='#b14d31',linestyle='--');bx.set(xlabel='Cells',ylabel='Reference error (%)');save(fig,'refinement')
    fine=variants[1]['levels'][-1]
    fig,ax=plt.subplots(figsize=(7,2.8),layout='constrained')
    for field in ['p','Ux','Uy']:
        records=[h for h in fine['history'] if h['field']==field]
        if records:ax.semilogy([h['iteration'] for h in records],[max(h['residual'],1e-18) for h in records],label=field)
    ax.axhline(1e-7,color='#b14d31',linestyle='--',label='Acceptance limit');ax.set(xlabel='Solver iteration',ylabel='Initial residual');ax.legend(ncol=4,fontsize=9);save(fig,'residuals')
    fig,axes=plt.subplots(3,1,figsize=(7,4.6),layout='constrained')
    nx,ny=fine['nx'],fine['ny'];length=p['length_mm'];gap=variants[1]['gap_mm']
    for xline in np.linspace(0,length,nx+1):axes[0].plot([xline,xline],[0,gap],color='#147e96',lw=.35)
    for yline in np.linspace(0,gap,ny+1):axes[0].plot([0,length],[yline,yline],color='#147e96',lw=.35)
    axes[0].set_title(f'Nominal-gap structured mesh: {nx} x {ny} x 1',fontsize=10)
    for ax,key,label in zip(axes[1:],['speed_m_s','pressure_pa'],['Computed speed (m/s)','Computed pressure (Pa)']):
        values=np.array(fine['field'][key]).reshape(ny,nx)
        im=ax.imshow(values,origin='lower',extent=[0,length,0,gap],aspect='auto',cmap='viridis');fig.colorbar(im,ax=ax,pad=.025,label=label)
    for ax in axes:ax.set(xlabel='Axial position (mm)',ylabel='Gap (mm)')
    save(fig,'fields')
    fig,ax=plt.subplots(figsize=(7,2.4),layout='constrained');eta=np.array(fine['field']['y_fraction']);u=variants[1]['mean_velocity_m_s']
    ax.plot(eta,fine['field']['velocity_m_s'],'o',markersize=3,label='Solved interior average');ax.plot(eta,6*u*eta*(1-eta),'-',label='Analytical parabola');ax.set(xlabel='Normalized gap position y/h',ylabel='Axial velocity (m/s)');ax.legend(fontsize=9);save(fig,'profile')
    rows='\n'.join(f"{v['gap_mm']:.3g} & {v['pressure_drop_pa']:.4f} & {v['analytical_pa']:.4f} & {v['numerical_allowance_pa']:.4f} & {v['margin_pa']:.4f} \\\\" for v in variants)
    gates='\n'.join(f"{v['gap_mm']:.3g} & {g['grid']} & {g['cells']} & {g['reference_error_pct']:.3f} & {g['mass_imbalance_pct']:.3g} & {g['profile_error_pct']:.3f} & {'PASS' if all(g['gates'].values()) else 'REVIEW'} \\\\" for v in variants for g in v['levels'])
    maxchange=max(v['mesh_change_pct'] for v in variants)
    screenshot_pages='';image_hashes={}
    if screenshots:
        # Maintainer CLI only. No public upload or screenshot path is accepted.
        receipt=json.loads((Path(screenshots)/'acceptance.json').read_text())
        if receipt['id']!=result['id']:raise ValueError('Screenshots must belong to this exact run')
        for i,(name,caption) in enumerate([('01-requirements.png','Browser requirements and reviewed numerical controls before execution.'),('04-mesh.png','Browser mesh stage: planned mesh family before the explicit Start action.'),('06-result.png','Browser result stage: computed velocity field and completed nine-solve run.')]):
            source=Path(screenshots)/name;target=output/f'workspace-{i}.png';shutil.copyfile(source,target)
            image_hashes[target.name]=hashlib.sha256(target.read_bytes()).hexdigest()
            screenshot_pages+=r'\clearpage\section*{Appendix: browser evidence '+str(i+1)+r'}'+ '\n'+r'\noindent Actual headless-browser capture for the study ID in this paper. This image demonstrates interface state; numerical evidence is in the charts, fields and hashed solver files.'+'\n'+r'\begin{center}\includegraphics[width=\textwidth,height=.72\textheight,keepaspectratio]{'+target.name+r'}\end{center}\noindent\textit{'+caption+'}\n'
    document=r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=22mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,amsmath,graphicx,booktabs,xcolor,hyperref}
\definecolor{aeroblue}{HTML}{147E96}
\hypersetup{colorlinks=true,urlcolor=aeroblue,linkcolor=aeroblue,pdftitle={Aero channel pressure-loss study}}
\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}
\newcommand{\fig}[2]{\begin{center}\includegraphics[width=\textwidth]{#1}\end{center}\small\textit{#2}\normalsize\par}
\begin{document}
{\small\color{aeroblue} AERO / COMPUTATIONAL ENGINEERING TECHNICAL NOTE / PDF REV 1.0}
\begin{center}\LARGE\bfseries Evidence-backed preliminary sizing\\of a parallel-plate channel\end{center}
\begin{center}\normalsize Aero automated study pipeline\\Numerical verification report; not a peer-reviewed publication\end{center}
\begin{abstract}
Three channel gaps are compared against a prescribed pressure-drop budget using
nine steady OpenFOAM calculations and a closed-form reference. The workflow
retains numerical inputs, mesh and solver diagnostics, computed fields and
reproducibility hashes. %%DECISION%% The comparison tests the stated idealized
flow model; it does not establish the performance of a manufactured device.
\end{abstract}
\section{Problem definition and scope}
\begin{center}\begin{tabular}{lr}\toprule Parameter & Value \\\midrule
Length & %%L%% mm \\ Nominal full gap & %%H%% mm \\
Reference width & 100 mm \\ Volume flow & %%Q%% mL/s \\
Pressure-drop budget & %%B%% Pa \\ Density & 998.2 kg/m$^3$ \\
Dynamic viscosity & 0.001003 Pa\,s \\\bottomrule\end{tabular}\end{center}
Water properties represent nominal $20\,^{\circ}\mathrm{C}$. The calculation is
two-dimensional, incompressible, steady and laminar. No-slip plates, a fully
developed parabolic inlet, zero outlet gauge pressure and spanwise empty
boundaries define the problem. The 100 mm width converts flow per unit width to
total flow; a 1 mm computational slice does not resolve sidewall drag.
\section{Governing reference and numerical method}
For plane Poiseuille flow~\cite{fitzpatrick}, with full gap $h$:
\begin{align}
\bar U&=\frac{Q}{Wh}, & Re_{2h}&=\frac{2\rho\bar U h}{\mu},\\
\Delta p&=\frac{12\mu LQ}{Wh^3}, &u(y)&=6\bar U\frac{y}{h}\left(1-\frac{y}{h}\right).
\end{align}
At fixed flow and properties, doubling the gap reduces pressure loss by a
factor of eight. Each candidate uses 512, 1,152 and 2,048 cells. OpenFOAM
Foundation 10, \texttt{simpleFoam}, computes the steady solution. Pressure is
fitted over $x/L=0.25$--$0.75$, multiplied by channel length, and converted from
kinematic pressure to Pa using density. This avoids interpreting cell-center
endpoints as the entire physical length.
\clearpage\section{Design comparison and decision}
\textbf{%%DECISION%%}
\fig{decision.pdf}{Figure 1. Actual fine-grid OpenFOAM pressure drop versus the analytical reference and the user-specified budget.}
\begin{center}\small\begin{tabular}{rrrrr}\toprule
Gap mm & CFD Pa & Reference Pa & Allowance Pa & Margin Pa \\\midrule
%%ROWS%%
\bottomrule\end{tabular}\end{center}
The numerical allowance is the larger of the medium--fine difference and the
fine-grid discrepancy from the analytical solution. Margin is budget minus
computed pressure drop minus this allowance. This allowance is not a statistical
confidence interval or a bound on omitted physical effects. A candidate is
recommended only when all numerical checks pass.
\section{Decision limitations}
The compared gaps are 75\%, 100\% and 125\% of nominal; this is not a continuous
optimum. Sidewall drag, entry losses, roughness, fittings, temperature variation,
manufacturing tolerances and unsteady effects require additional models or
measurements. Numerical agreement with the analytical solution is distinct from
experimental validation. The result supports preliminary sizing within scope.
\clearpage\section{Mesh sensitivity and iterative convergence}
\fig{refinement.pdf}{Figure 2. Pressure drop and analytical error across the three mesh resolutions. Dotted lines show analytical pressure; the dashed error threshold is 2 percent.}
The largest medium--fine pressure change across the three gaps is %%CHANGE%%\%.
This checks grid sensitivity but is not a formal grid-convergence-index analysis.
\fig{residuals.pdf}{Figure 3. Actual initial-residual history for the nominal-gap fine-grid run, sampled every ten iterations. Final acceptance also uses the last reported residuals, not only these plotted samples.}
\clearpage\section{Mesh and computed-field snapshots}
\fig{fields.pdf}{Figure 4. Nominal-gap mesh and actual solved cell fields. The vertical axis is visually expanded; labeled coordinates retain physical units. These are generated field snapshots, not photographs or invented contours.}
\fig{profile.pdf}{Figure 5. Solved axial velocity averaged over the middle half of the channel against the fully developed analytical parabola.}
\clearpage\section{Verification gates and reproducibility}
\begin{center}\scriptsize\begin{tabular}{rlrrrrl}\toprule
Gap & Grid & Cells & $p$ error \% & Flux error \% & $u$ error \% & Checks \\\midrule
%%GATES%%
\bottomrule\end{tabular}\end{center}
Each grid must pass \texttt{checkMesh}, reported solver convergence, final
initial residuals $\leq10^{-7}$, flux imbalance $<0.1\%$, pressure-reference
error $<2\%$ and velocity-profile relative $L_2$ error $<2\%$. Each gap also
requires medium--fine pressure change $<1\%$. All-checks disposition:
\textbf{%%PASS%%}. Nine-solve compute time: %%TIME%% seconds, excluding paper generation.

\textbf{Run identity.} \url{%%ID%%}

\textbf{Worker source SHA-256.}\par \url{%%WORKER%%}

\textbf{Case-generator source SHA-256.}\par \url{%%CORE%%}

\textbf{Result JSON SHA-256.}\par \url{%%RESULT%%}

The evidence ZIP contains the exact OpenFOAM dictionaries, generated meshes,
final $p$, $U$ and $\phi$ fields, logs, result JSON, this PDF and its LaTeX/figure
sources. Its SHA-256 manifest checks artifact identity, not scientific validity.
Raw source values, not language-model prose, generate this document.
Download the live report and evidence within 48 hours to retain a copy.
\begin{thebibliography}{9}
\bibitem{fitzpatrick} R. Fitzpatrick, \textit{Flow Between Parallel Plates},
University of Texas at Austin, Fluid Mechanics lecture notes.
\url{https://farside.ph.utexas.edu/teaching/336L/Fluidhtml/node134.html}.
\end{thebibliography}
%%SCREENSHOTS%%
\end{document}
'''
    result_bytes=json.dumps(result,allow_nan=False).encode()
    values={'L':f"{p['length_mm']:g}",'H':f"{p['gap_mm']:g}",'Q':f"{p['flow_ml_s']:g}",'B':f"{p['budget_pa']:g}",'DECISION':tex(result['decision']),'ROWS':rows,'GATES':gates,'CHANGE':f'{maxchange:.4f}','PASS':'PASS' if result['checks_passed'] else 'REVIEW REQUIRED','TIME':str(result['elapsed_seconds']),'ID':result['id'],'WORKER':result['provenance']['worker_source_sha256'],'CORE':result['provenance']['case_generator_sha256'],'RESULT':hashlib.sha256(result_bytes).hexdigest(),'SCREENSHOTS':screenshot_pages}
    for key,value in values.items():document=document.replace('%%'+key+'%%',value)
    (output/'paper.tex').write_text(document,encoding='utf-8')
    (output/'result.json').write_bytes(result_bytes)
    (output/'figures.json').write_text(json.dumps({'source':'solver_result_fields_and_diagnostics','run_id':result['id'],'screenshot_sha256':image_hashes},indent=2))
    return output


def compile_paper(output):
    output=Path(output)
    env={**os.environ,'openin_any':'p','openout_any':'p'}
    for _ in range(2):
        run=subprocess.run(['pdflatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','paper.tex'],cwd=output,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=35)
        if run.returncode:raise RuntimeError('LaTeX paper compilation failed; inspect paper.log')
    pdf=output/'paper.pdf'
    if not pdf.exists() or not pdf.read_bytes().startswith(b'%PDF-'):raise RuntimeError('LaTeX did not produce a valid PDF')
    return pdf


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('result');parser.add_argument('output');parser.add_argument('--screenshots');parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    folder=prepare(json.loads(Path(args.result).read_text()),args.output,args.screenshots)
    if not args.prepare_only:compile_paper(folder)
    print(folder)
