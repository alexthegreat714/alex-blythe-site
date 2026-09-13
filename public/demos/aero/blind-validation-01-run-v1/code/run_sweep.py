"""Run every frozen station and grid, without access to a reference or key."""
import argparse,concurrent.futures,hashlib,json,os,shutil,time
from pathlib import Path
from execute_case import execute
from analyze_case import analyze
from protocol import Challenge,sha,now

def sweep(root,out):
    root=Path(root).resolve();out=Path(out).resolve()
    ch=Challenge(root);ch.intact();criteria=ch.load('preregistration.json')
    if ch.state()['stage'] not in ['CRITERIA_FROZEN_ANCHORED','SOLVE']:raise ValueError('Publicly anchor criteria before starting')
    for name,h in criteria['execution_code'].items():
        if sha(Path(__file__).with_name(name).read_bytes())!=h:raise ValueError('Execution code differs from preregistration: '+name)
    if ch.state()['stage']=='CRITERIA_FROZEN_ANCHORED':
        ch.start({'predictor_id':'isolated-deterministic-OpenFOAM10-'+criteria['execution_code']['case_driver.py'][:12],'supervisor_id':'local-Aero-input-only-orchestrator','fresh_predictor_context':True,'reference_not_mounted':True,'network_disabled':True,'rag_disabled':True,'key_not_available':True,'isolation_method':'Each Docker case receives only the frozen generator script and a new empty per-case output bind. Source/reference/key and repository are not mounted. No LLM is called during solving.'})
    out.mkdir(parents=True,exist_ok=True)
    inputs=ch.load('input.json');jobs=[(s,m['name']) for s in inputs['stations'] for m in criteria['mesh_levels']]
    results={};running=[]
    def status():
        v={'updated_at':now(),'total':len(jobs),'completed':len(results),'running':list(running),'status':'RUNNING' if len(results)<len(jobs) else 'RUNS_FINISHED','successful_execution':sum(r.get('complete_prediction',False) for r in results.values()),'reference_revealed':False,'results':results}
        p=out/'progress.pending';p.write_text(json.dumps(v,indent=2)+'\n');os.replace(p,out/'progress.json')
    def one(s,level):
        d=out/(s+'-'+level)
        if d.exists():
            if (d/'analysis.json').exists():return json.loads((d/'analysis.json').read_text())
            raise ValueError('Existing unfinished attempt: preserve and explicitly investigate '+str(d))
        angle=inputs['flow_conditions']['angle_of_attack_degrees'][s]
        receipt=execute(d,level,angle,2000,1,False,criteria['solver']['case_wall_timeout_seconds'])
        try:r=analyze(d,s)
        except Exception as e:
            r={'station':s,'level':level,'complete_prediction':False,'status':'EXECUTION_OR_EXTRACTION_FAILED','error':str(e)}
            (d/'analysis.json').write_text(json.dumps(r,indent=2)+'\n')
        return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        pending={};remaining=iter(jobs)
        for _ in range(3):
            s,l=next(remaining);key=s+'-'+l;running.append(key);pending[pool.submit(one,s,l)]=key
        status()
        while pending:
            done,_=concurrent.futures.wait(pending,timeout=10,return_when=concurrent.futures.FIRST_COMPLETED)
            for f in done:
                key=pending.pop(f);running.remove(key)
                try:results[key]=f.result()
                except Exception as e:results[key]={'status':'FAILED','error':str(e),'complete_prediction':False}
                print(json.dumps({'done':len(results),'total':len(jobs),'case':key,'status':results[key]['status']}),flush=True)
                try:s,l=next(remaining)
                except StopIteration:continue
                key=s+'-'+l;running.append(key);pending[pool.submit(one,s,l)]=key
            status()
    return results
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('output',type=Path);a=p.parse_args();sweep(a.package,a.output)
