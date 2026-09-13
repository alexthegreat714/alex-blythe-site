"""Disposable isolated case execution; each attempt has a fresh retained folder."""
import argparse, hashlib, json, subprocess, time, uuid
from datetime import datetime, timezone
from pathlib import Path
IMAGE='sha256:5992a995c1eacc16246de4cba583b5645cde7e4e8c480db83158dddbe07b36f6'
def now(): return datetime.now(timezone.utc).isoformat()
def execute(out, level, angle, duration, dt, smoke=False, timeout=3600):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    driver=Path(__file__).with_name('case_driver.py').resolve()
    receipt={'started_at':now(),'image':IMAGE,'kind':'SMOKE_NOT_PREDICTION' if smoke else 'PRODUCTION','level':level,'angle':angle,'driver_sha256':hashlib.sha256(driver.read_bytes()).hexdigest()}
    shell='source /opt/openfoam10/etc/bashrc; unset FOAM_SIGFPE; set -e; python3 /driver.py /work/case --level '+level+' --angle '+str(angle)+' --duration '+str(duration)+' --dt '+str(dt)+(' --smoke' if smoke else '')+'; cd /work/case; checkMesh -allTopology -allGeometry > ../mesh.log 2>&1; if grep -Eq "negative volume|incorrectly oriented|non-orthogonality errors|negative cell volumes" ../mesh.log; then exit 43; fi; potentialFoam > ../initialization.log 2>&1; simpleFoam > ../solver.log 2>&1'
    args=['docker','create','--name','aero-ch01-case-'+uuid.uuid4().hex[:10],'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user','10001:10001','--cpus','2','--memory','4g','--memory-swap','4g','--pids-limit','128','--tmpfs','/tmp:rw,nosuid,size=268435456','--mount',f'type=bind,src={driver},dst=/driver.py,readonly','--mount',f'type=bind,src={out},dst=/work','--workdir','/work','--entrypoint','/bin/bash',IMAGE,'-c',shell]
    cid=None
    try:
        cid=subprocess.check_output(args,text=True).strip()
        info=json.loads(subprocess.check_output(['docker','inspect',cid]))[0]
        h=info['HostConfig'];ms=info['Mounts']
        assert h['NetworkMode']=='none' and h['ReadonlyRootfs'] and not h['Privileged']
        assert info['Config']['User']=='10001:10001' and 'ALL' in h['CapDrop']
        assert {m['Destination']:m['RW'] for m in ms}=={'/driver.py':False,'/work':True}
        receipt['enforcement']={'network':'none','rag':False,'fresh_output':True,'reference_mounted':False,'key_mounted':False,'mounts':[{'target':m['Destination'],'rw':m['RW']} for m in ms],'user':info['Config']['User'],'read_only_root':True,'cap_drop':h['CapDrop'],'image_id':info['Image']}
        receipt['container_id']=cid
        (out/'receipt-start.json').write_text(json.dumps(receipt,indent=2)+'\n')
        subprocess.run(['docker','start',cid],check=True,capture_output=True)
        start=time.monotonic()
        while True:
            state=json.loads(subprocess.check_output(['docker','inspect',cid]))[0]['State']
            if not state['Running']:break
            if time.monotonic()-start>timeout:
                receipt['timeout']=True
                subprocess.run(['docker','stop','-t','5',cid],capture_output=True)
                break
            time.sleep(2)
        receipt['state']=json.loads(subprocess.check_output(['docker','inspect',cid]))[0]['State']
        receipt['status']='EXECUTED' if receipt['state']['ExitCode']==0 and not receipt.get('timeout') else 'EXECUTION_FAILED'
        logs=subprocess.run(['docker','logs',cid],capture_output=True)
        (out/'container.log').write_bytes(logs.stdout+logs.stderr)
    finally:
        if cid:subprocess.run(['docker','rm','-f',cid],capture_output=True)
        receipt['finished_at']=now()
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--level',default='coarse');p.add_argument('--angle',type=float,default=1);p.add_argument('--duration',type=float,default=.04);p.add_argument('--dt',type=float,default=.02);p.add_argument('--smoke',action='store_true');p.add_argument('--timeout',type=float,default=3600);a=p.parse_args()
    print(json.dumps(execute(a.output,a.level,a.angle,a.duration,a.dt,a.smoke,a.timeout),indent=2))
