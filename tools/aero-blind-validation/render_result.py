"""Render only a real, anchored comparison; no fallback benchmark values."""
import argparse,json,zipfile
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from protocol import Challenge,sha,encode

def tex(s):
    table={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(table.get(c,c) for c in str(s))
def render(root):
    run=Challenge(root);run.require('COMPARED_ANCHORED');run.intact();r=run.load('comparison.json');c=run.load('preregistration.json');out=run.root/'report';out.mkdir(exist_ok=False)
    plots=[]
    for i,q in enumerate(c['quantities']):
        rows=[x for x in r['all_points'] if x['quantity']==q];x=list(range(len(rows)));fig,axes=plt.subplots(2,1,figsize=(9,6),layout='constrained')
        axes[0].plot(x,[v['prediction'] for v in rows],'o-',label='Frozen prediction');axes[0].plot(x,[v['reference'] for v in rows],'s--',label='Experiment')
        axes[0].legend();axes[0].set_ylabel(q);axes[0].set_title(q+' / '+r['status']);axes[1].bar(x,[v['signed_error'] for v in rows]);axes[1].set_ylabel('Signed error');axes[1].set_xticks(x,[v['station'] for v in rows],rotation=60);axes[1].set_xlabel('Every preregistered station (no omissions)')
        name=f'comparison-{i}.pdf';fig.savefig(out/name,bbox_inches='tight');plt.close(fig);plots.append(name)
    state=run.state();lines=[r'\documentclass[10pt]{article}',r'\usepackage[margin=0.85in]{geometry}',r'\usepackage{graphicx,hyperref,longtable}',r'\begin{document}',r'\title{Aero external benchmark: '+tex(c['benchmark_id'])+r'}\author{Aero / engineering record}\date{}\maketitle',r'\section{Abstract and disposition}',tex('Frozen comparison result: '+r['status']+'. Specific tested configuration only; not universal validation or design readiness.'),r'\section{Source and permitted information}',tex(c['source_citation']),tex(c['source_version']),r'\section{Chronology}']
    for e in state['events']:lines.append(r'\paragraph{'+tex(e['stage'])+'} '+tex(e['time'])+' '+tex(e.get('commit','')))
    for title,keys in [('Numerical model',['governing_equations','flow_conditions','turbulence_model','wall_treatment']),('Geometry and mesh',['geometry_source','dimensional_assumptions','mesh_strategy','mesh_levels','refinement_strategy']),('Solver and acceptance',['solver','boundary_conditions','initial_conditions','convergence_criteria','conservation_criteria','residual_criteria','yplus_criterion','acceptance_thresholds']),('Uncertainty and permitted processing',['experimental_uncertainty','allowable_preprocessing','prohibited_tuning'])]:
        lines.append(r'\section{'+title+'}')
        for key in keys:lines.append(r'\paragraph{'+tex(key)+'} '+tex(json.dumps(c[key])))
    lines.extend([r'\clearpage\section{Prediction and experimental comparison}',tex(json.dumps(r['metrics']))])
    for name in plots:lines.append(r'\begin{center}\includegraphics[width=\linewidth]{'+name+r'}\end{center}')
    lines.extend([r'\section{Limitations and conclusions}',tex('Numerical status: '+r['numerical_status']+'. Outcome: '+r['status']+'. No post-unseal tuning is part of this frozen result. Diagnosis must be separately labeled. Unknown experimental uncertainty was not treated as zero.'),r'\section{Reproduction}',tex('The versioned package retains criteria, inputs, sealed-reference metadata, prediction, revealed measurements, complete point errors, software evidence and Git chronology. Hashes establish identity, not scientific validity.'),r'\end{document}'])
    (out/'paper.tex').write_text('\n'.join(lines)+'\n',encoding='utf8',newline='\n')
    manifest={'files':[{'path':p.relative_to(run.root).as_posix(),'size':p.stat().st_size,'sha256':sha(p.read_bytes()),'role':'report' if out in p.parents else 'retained-evidence','stage':'post-comparison','classification':'generated' if out in p.parents else 'source-or-solver-evidence'} for p in run.root.rglob('*') if p.is_file()]}
    (out/'manifest.json').write_bytes(encode(manifest));return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();print(render(a.directory))
