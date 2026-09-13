"""Publish an actual, timestamped run snapshot; no invented results."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'public/demos/aero/blind-validation-01-run-v1'
def main():
    state=json.loads((RUN/'state.json').read_text());events=state['events']
    progress=json.loads((ROOT/'output/challenge01/production-v1/progress.json').read_text())
    labels=[('INPUT_FROZEN','Input frozen'),('CRITERIA_FROZEN','Criteria frozen'),('SOLVE','Solve'),('PREDICTION_FROZEN','Prediction frozen'),('REFERENCE_UNSEALED','Reference unsealed'),('COMPARED','Comparison')]
    phases=[]
    for stage,label in labels:
        ev=next((e for e in events if e['stage']==stage),None)
        flag='COMPLETE' if ev else 'NOT OCCURRED'
        if stage=='SOLVE' and ev and not (RUN/'blind_prediction.json').exists():flag='RUNNING' if progress['completed']<progress['total'] else 'RUNS FINISHED'
        phases.append({'label':label,'status':flag,'time':ev['time'] if ev else None})
    comp=json.loads((RUN/'comparison.json').read_text()) if (RUN/'comparison.json').exists() else None
    obj={'schema':'aero.challenge.status.v3','updated_at':datetime.now(timezone.utc).isoformat(),'stage':state['stage'],'result':comp['status'] if comp else 'NOT EVALUATED','total':progress['total'],'completed':progress['completed'],'complete_predictions':progress['successful_execution'],'running':progress['running'],'phases':phases,'hashes':{name:hashlib.sha256((RUN/name).read_bytes()).hexdigest() for name in ['input.json','reference.enc','preregistration.json','blind_prediction.json','comparison.json'] if (RUN/name).exists()},'commits':{e['stage']:e['commit'] for e in events if e.get('commit')},'has_paper':(RUN/'report/paper.pdf').exists(),'has_prediction':(RUN/'blind_prediction.json').exists(),'has_comparison':bool(comp),'has_bundle_index':(RUN/'evidence/run-index.json').exists(),'blinding_scope':'Reference withheld from deterministic solver execution; source-exposed supervisor designed the setup. Not double-blind or pretraining-blind.'}
    obj['numerical_status']=comp['numerical_status'] if comp else 'NOT EVALUATED'
    obj['experimental_comparison']=comp['experimental_comparison'] if comp else 'NOT EVALUATED'
    obj['metrics']=comp['metrics'] if comp else {}
    obj['has_reproduction']=(RUN/'reproduction.zip').is_file()
    obj['has_manifest']=(RUN/'manifest.json').is_file()
    (RUN/'current-status.json').write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:obj[k] for k in ('stage','result','completed','total')}))
if __name__=='__main__':main()
