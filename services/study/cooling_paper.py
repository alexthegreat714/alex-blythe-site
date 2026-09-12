"""Reproducible figures and source-owned LaTeX for the cooling screen."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from cooling import calculate
from paper import compile_paper,tex

def prepare(result,destination,screenshots=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator,ScalarFormatter,NullLocator
    import numpy as np
    out=Path(destination);out.mkdir(parents=True,exist_ok=True)
    p=result['inputs'];vs=result['layouts'];colors=['#bc7146','#167f96','#796ca9']
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def save(fig,name):
        fig.savefig(out/(name+'.pdf'),bbox_inches='tight');fig.savefig(out/(name+'.png'),dpi=170,bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,3.6),constrained_layout=True)
    for v,c in zip(vs,colors):
        ax.plot([v['pressure_pa'],v['guard_pressure_pa']],[v['wall_c'],v['guard_wall_c']],'-',color=c)
        ax.scatter(v['pressure_pa'],v['wall_c'],color=c,marker='o',label=f"{v['id']}: {v['channels']} x {v['diameter_mm']} mm")
        ax.scatter(v['guard_pressure_pa'],v['guard_wall_c'],color=c,marker='s');ax.annotate(v['id'],(v['guard_pressure_pa'],v['guard_wall_c']),xytext=(7,4),textcoords='offset points')
    ax.axhline(p['wall_limit_c'],color='#a73737',linestyle='--',label='Wall limit');ax.axvline(p['pressure_budget_pa'],color='#777',linestyle='--',label='Friction budget')
    ax.set(xscale='log',xlabel='Straight-passage pressure loss (Pa)',ylabel='Outlet inner-wall temperature (C)');ax.legend(fontsize=9,ncol=2);save(fig,'trade')
    fig,axes=plt.subplots(2,1,figsize=(7,5.2),constrained_layout=True)
    for v,c in zip(vs,colors):
        axes[0].plot(v['profile']['x_mm'],v['profile']['wall_c'],color=c,label='Wall '+v['id'])
        for i in range(v['channels']):
            d=v['diameter_mm'];circle=plt.Circle((i*(d+1)+d/2,ord(v['id'])-65),d/10,color=c,fill=False,lw=2);axes[1].add_patch(circle)
        axes[1].text(8,ord(v['id'])-65,f"{v['id']}: {v['channels']} channels, diameter {d:g} mm; span {v['span_mm']:g} mm",va='center',fontsize=9)
    axes[0].plot(vs[0]['profile']['x_mm'],vs[0]['profile']['bulk_c'],'--',color='#333',label='Bulk coolant (all)');axes[0].axhline(p['wall_limit_c'],ls=':',color='#a73737');axes[0].set(xlabel='Heated length (mm)',ylabel='Temperature (C)');axes[0].legend(ncol=2,fontsize=9)
    axes[1].set(xlim=(-.5,23),ylim=(-.8,2.8),aspect='equal');axes[1].axis('off');axes[1].set_title('Layout identifiers / schematic only, not a manufactured CAD drawing',fontsize=10);save(fig,'profiles')
    fig,(ax,bx)=plt.subplots(1,2,figsize=(7,3),constrained_layout=True)
    rv=result['radial_verification'];ax.plot([v['radial_cells'] for v in rv],[v['nu'] for v in rv],'o-',color='#167f96');ax.axhline(48/11,ls='--',color='#777');ax.set(xlabel='Radial control volumes',ylabel='Computed Nusselt number')
    bx.loglog([v['radial_cells'] for v in rv],[v['relative_error_pct'] for v in rv],'o-',color='#167f96');bx.set(xlabel='Radial control volumes',ylabel='Relative error (%)');bx.xaxis.set_major_locator(FixedLocator([16,32,64,128]));bx.xaxis.set_major_formatter(ScalarFormatter());bx.xaxis.set_minor_locator(NullLocator());save(fig,'verification')
    fig,(ax,bx)=plt.subplots(1,2,figsize=(7,3),constrained_layout=True)
    flows=np.linspace(.5,2,31)
    for i,c in enumerate(colors):
        samples=[calculate({**p,'flow_ml_s':float(q)})['layouts'][i] for q in flows]
        ax.plot(flows,[v['guard_wall_c'] for v in samples],color=c,label=vs[i]['id']);bx.plot(flows,[v['guard_pressure_pa'] for v in samples],color=c)
    ax.axhline(p['wall_limit_c'],ls='--',color='#777');bx.axhline(p['pressure_budget_pa'],ls='--',color='#777');ax.set(xlabel='Total flow (mL/s)',ylabel='Guard inner-wall temperature (C)');bx.set(xlabel='Total flow (mL/s)',ylabel='Guard friction loss (Pa)');ax.legend();save(fig,'sensitivity')
    rows='\n'.join(f"{v['id']} & {v['wall_c']:.2f} & {v['guard_wall_c']:.2f} & {v['pressure_pa']:.1f} & {v['guard_pressure_pa']:.1f} & {'PASS' if v['passes'] else 'FAIL'} \\\\" for v in vs)
    gate_rows='\n'.join(f"{v['id']} & {v['re']:.1f} & {v['h_w_m2k']:.1f} & {v['thermal_entry_mm']:.1f} & {v['thermal_margin_k']:.2f} & {v['pressure_margin_pa']:.1f} \\\\" for v in vs)
    radial_rows='\n'.join(f"{v['radial_cells']} & {v['nu']:.7f} & {v['relative_error_pct']:.5f} \\\\" for v in rv)
    appendix='';image_hashes={}
    if screenshots:
        receipt=json.loads((Path(screenshots)/'acceptance.json').read_text())
        if receipt['id']!=result['id']:raise ValueError('Browser screenshots must match this run')
        for i,(name,caption) in enumerate([('01-requirements.png','Reviewed requirements and missing-input guidance.'),('03-layouts.png','Interactive parametric circular-passage layouts; no imported or verified manufacturing CAD.'),('05-results.png','Completed analytical comparison and paper download.')]):
            target=out/f'workspace-{i}.png';shutil.copyfile(Path(screenshots)/name,target);image_hashes[target.name]=hashlib.sha256(target.read_bytes()).hexdigest()
            appendix+=r'\clearpage\section*{Browser evidence '+str(i+1)+r'} Actual browser capture from the same run. Interface evidence is distinct from numerical verification.\begin{center}\includegraphics[width=\textwidth,height=.75\textheight,keepaspectratio]{'+target.name+r'}\end{center}'+tex(caption)+'\n'
    source=r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=22mm]{geometry}\usepackage[T1]{fontenc}
\usepackage{lmodern,amsmath,graphicx,booktabs,xcolor,hyperref}
\definecolor{aeroblue}{HTML}{147E96}\hypersetup{colorlinks=true,urlcolor=aeroblue,linkcolor=aeroblue}
\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}
\newcommand{\fig}[2]{\begin{center}\includegraphics[width=\textwidth]{#1}\end{center}\small\textit{#2}\normalsize\par}
\begin{document}
{\small\color{aeroblue} AERO / ENGINEERING TECHNICAL NOTE 02 / REVISION 1.0}
\begin{center}\LARGE\bfseries Forced-convection channel sizing:\\a thermal--hydraulic screening decision\end{center}
\begin{center}Aero engineering pipeline\\Analytical verification study; not a peer-reviewed publication\end{center}
\begin{abstract}
Three circular-passage layouts are compared using an energy balance, laminar
friction and a fully developed uniform-heat-flux relation. The design question
is which tested layout meets an inner-wall temperature limit and a straight-channel
pressure budget with explicit adverse scenarios. %%DECISION%% The result is a
conditional preliminary screen, not a thermal CFD result or hardware certification.
\end{abstract}
\section{Requirements and problem definition}
\begin{center}\begin{tabular}{lr}\toprule Quantity & Value\\\midrule
Total heat into coolant & %%HEAT%% W\\
Total volume flow & %%FLOW%% mL/s\\
Coolant inlet temperature & %%INLET%% $^\circ$C\\
Wetted inner-wall limit & %%WALL%% $^\circ$C\\
Straight-passage pressure budget & %%PRESSURE%% Pa\\
Heated length & %%LENGTH%% mm\\
Available channel-array width & %%WIDTH%% mm\\\bottomrule\end{tabular}\end{center}
The interface asks for missing heated length or available width before the
user can authorize a report. A calculation is invalidated when an input changes.
The report preserves the exact inputs, formulas and result identity.

The fixed candidates are A: four 1 mm passages; B: two 2 mm passages; C: one 4 mm
passage. They have equal total wetted perimeter, but different velocity, heat
transfer coefficient and resistance. A 1 mm ligament separates adjacent passages;
the required spans are 7, 5 and 4 mm, excluding outer casing. These are geometric
options, not a tolerance-checked or manufactured part.

\textbf{Property assumptions.} Constant water properties are specified as
$\rho=997$ kg/m$^3$, $c_p=4180$ J/(kg K), $\mu=0.00089$ Pa s,
$k=0.607$ W/(m K), representative near 25 $^\circ$C. They are fixed benchmark
inputs, not temperature-updated property data. Use a property service such as
NIST [3] before application to other conditions.
\clearpage\section{Model and governing relations}
For $N$ equally fed circular passages of diameter $D$ and heated length $L$:
\begin{align}
\dot m&=\rho\dot V,&\quad T_{b,o}&=T_{b,i}+\frac{Q}{\dot m c_p},\\
U&=\frac{4\dot V}{N\pi D^2},&Re_D&=\frac{\rho U D}{\mu},\\
Nu_D&=\frac{hD}{k}=\frac{48}{11}\simeq4.364,& A_w&=N\pi DL,\\
T_{w,o}&=T_{b,o}+\frac{Q}{h A_w},& \Delta p&=\frac{128\mu L\dot V}{N\pi D^4},\\
P_{hyd}&=\Delta p\dot V,& f_D&=\frac{64}{Re_D}.
\end{align}
The heat-transfer relation assumes constant axial and circumferential heat flux,
fully developed laminar convection [1]. Friction is independently cross-checked
with $f_D(L/D)\rho U^2/2$ [2]. $P_{hyd}$ is fluid power, not electrical pump power.
Equal heat and flow sharing are imposed; a real manifold must establish them.

The inner-wall estimate increases monotonically along the heated length. Fully
developed $Nu$ is used as an asymptotic film-resistance screen, not as a resolved
entrance-region temperature field. We require the outlet to exceed the estimated
thermal entry length $L_t\simeq0.05 Re_D Pr D$, with
$Pr=c_p\mu/k$. The corresponding hydrodynamic estimate is $0.05Re_DD$.
Even when the outlet passes this check, entry pressure losses are omitted.

\subsection{Adverse scenarios and selection rule}
The thermal scenario uses 10\% more heat, 10\% less total flow and 20\% lower $h$:
\[
T_{w,g}=T_{b,i}+\frac{1.1Q}{0.9\dot m c_p}+\frac{1.1Q}{0.8hA_w}.
\]
The separate pressure scenario uses 20\% higher viscosity, 10\% higher flow and
2\% smaller diameter: $\Delta p_g=\Delta p(1.2)(1.1)/(0.98)^4$.
These are adverse scenarios, not simultaneous observations or statistical bounds.
They do not cover omitted physics or all water-property variation.

Each layout must fit the width, remain below an adverse $Re=1800$, have
$1.1L_t/0.8\le L$, remain below the 90 $^\circ$C single-phase screening ceiling,
and meet both guard budgets. The ceiling is not a boiling model; pressure,
orientation and mixed convection require review. The selected layout minimizes
nominal fluid pumping power among the passing candidates only. No global
optimum or external solid-wall temperature is established.
\clearpage\section{Thermal--hydraulic decision}
\textbf{%%DECISION%%}
\fig{trade.pdf}{Figure 1. Nominal circles and adverse-scenario squares. The region below both budget lines is feasible only if the other gates also pass. Pressure and thermal guard points combine separate scenarios.}
\begin{center}\small\begin{tabular}{lrrrrl}\toprule Layout & Wall C & Guard C & Friction Pa & Guard Pa & Gates\\\midrule
%%ROWS%%
\bottomrule\end{tabular}\end{center}
The nominal bulk-fluid rise is %%RISE%% K for every layout because total heat,
total mass flow and heat capacity are unchanged. Channel count changes film
resistance, not this energy balance. A lower pressure loss alone is therefore
not enough to choose a cooling layout.
\clearpage\section{Temperature development and geometry}
\fig{profiles.pdf}{Figure 2. Analytical bulk and asymptotic inner-wall profiles and layout identifiers. These are computed one-dimensional estimates, not CFD contours, mesh images or experimental measurements.}
\begin{center}\small\begin{tabular}{lrrrrr}\toprule Layout & Re & $h$ W/m$^2$K & $L_t$ mm & Guard K margin & Guard Pa margin\\\midrule
%%GATES%%
\bottomrule\end{tabular}\end{center}
Positive budget margins alone do not override regime or packaging gates. Failed
gates remain visible in the evidence JSON, including the no-feasible-layout case.
\clearpage\section{Verification, not physical validation}
An independent radial finite-volume energy integration checks the Nusselt
coefficient. With $s=r/R$ and $t=k(T-T_w)/(q''R)$:
\[
\frac1s\frac{d}{ds}\left(s\frac{dt}{ds}\right)=4(1-s^2),\quad
t'(0)=0,\quad t'(1)=1,\quad t(1)=0.
\]
Face-integrated fluxes and midpoint velocity-weighted bulk temperatures yield
$Nu=-2/t_b$. The analytic solution is $t=s^2-s^4/4-3/4$ and $t_b=-11/24$.
This verification does not call the production $Nu$ constant to compute its answer.
\fig{verification.pdf}{Figure 3. Radial energy discretization approaching $48/11$. This is not an OpenFOAM grid-convergence study.}
\begin{center}\begin{tabular}{rrr}\toprule Radial cells & Computed Nu & Error \%\\\midrule
%%RADIAL%%
\bottomrule\end{tabular}\end{center}
The energy-balance relative closure error is %%ENERGY%%. The two algebraically
equivalent pressure formulations agree to floating-point precision. These checks
detect implementation mistakes; they do not provide independent experimental
validation of the assumptions or empirical entrance-length criterion.
\clearpage\section{Sensitivity and next fidelity level}
\fig{sensitivity.pdf}{Figure 4. Separate adverse thermal and pressure scenarios versus total flow. Curves outside regime, width or entry-length gates must not be interpreted as valid designs.}
Increasing flow lowers the bulk-fluid rise but raises friction loss. A real
follow-on should import manufactured geometry, include manifolds, review flow
sharing and property variation, and use conjugate heat-transfer CFD for solid
conduction, local hot spots, contact resistance and the heated footprint. It
needs a thermal mesh study, energy and mass conservation, and a matched thermal
reference or measurement before design readiness is claimed. No thermal CFD was
performed in this study.

\textbf{Run identity:} \nolinkurl{%%ID%%}\\
\textbf{Calculator source SHA-256:}\par\nolinkurl{%%HASH%%}\par
The hashed evidence bundle retains inputs, all gate results, verification
records, calculator source, this PDF, LaTeX source and figures. Live runs are
retained for 48 hours; download the bundle to keep it.
\begin{thebibliography}{9}\small
\bibitem{nptel} NPTEL, Internal forced convection, uniform-flux circular tubes and entrance regions.\newline\url{https://archive.nptel.ac.in/content/storage2/courses/112108149/pdf/M6/M6TeacherSlides.pdf}
\bibitem{poiseuille} R. Fitzpatrick, Poiseuille Flow.\newline\url{https://farside.ph.utexas.edu/teaching/336L/Fluidhtml/node136.html}
\bibitem{nist} NIST, Chemistry WebBook, Thermophysical Properties of Fluid Systems.\newline\url{https://webbook.nist.gov/chemistry/fluid/}
\end{thebibliography}
%%APPENDIX%%
\end{document}
'''
    vals={'HEAT':p['heat_w'],'FLOW':p['flow_ml_s'],'INLET':p['inlet_c'],'WALL':p['wall_limit_c'],'PRESSURE':p['pressure_budget_pa'],'LENGTH':p['length_mm'],'WIDTH':p['available_width_mm'],'DECISION':tex(result['decision']),'ROWS':rows,'GATES':gate_rows,'RADIAL':radial_rows,'RISE':f"{result['bulk_rise_k']:.3f}",'ENERGY':f"{result['energy_relative_error']:.2g}",'ID':result['id'],'HASH':result['provenance']['calculator_sha256'],'APPENDIX':appendix}
    for key,value in vals.items():source=source.replace('%%'+key+'%%',str(value))
    (out/'paper.tex').write_text(source,encoding='utf-8');(out/'result.json').write_text(json.dumps(result,allow_nan=False),encoding='utf-8');(out/'figures.json').write_text(json.dumps({'run_id':result['id'],'source':'analytical_correlations_and_radial_energy_verification','screenshot_sha256':image_hashes},indent=2))
    return out

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('result');parser.add_argument('output');parser.add_argument('--screenshots');parser.add_argument('--prepare-only',action='store_true');a=parser.parse_args()
    folder=prepare(json.loads(Path(a.result).read_text()),a.output,a.screenshots)
    if not a.prepare_only:compile_paper(folder)
    print(folder)
