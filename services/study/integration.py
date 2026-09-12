"""Real min/default/max studies through the running broker. Records hashes and gates."""
import hashlib
import io
import json
import subprocess
import time
import uuid
import zipfile
from pathlib import Path

OUT=Path('.qa/channel-study')
OUT.mkdir(parents=True,exist_ok=True)

def request(path,body=None,ip='192.0.2.2'):
    program="import urllib.request; r=urllib.request.Request('http://127.0.0.1:5323"+path+"',data="+(repr(json.dumps(body).encode()) if body else "None")+",headers={'Content-Type':'application/json','Origin':'https://alex-blythe.com','X-Aero-Client-IP':"+repr(ip)+"}); print(urllib.request.urlopen(r,timeout=12).read().decode())"
    return json.loads(subprocess.check_output(['docker','exec','alex-blythe-site-study-api-1','python','-c',program],text=True))

cases=[('default',{'length_mm':200,'gap_mm':2,'flow_ml_s':20,'budget_pa':70}),
       ('minimum',{'length_mm':100,'gap_mm':1,'flow_ml_s':1,'budget_pa':1}),
       ('maximum',{'length_mm':500,'gap_mm':3,'flow_ml_s':40,'budget_pa':1000})]
receipts=[]
for i,(label,inputs) in enumerate(cases):
    key=str(uuid.uuid4())
    run=request('/study/runs',{'request_id':key,'inputs':inputs},f'192.0.2.{i+2}')
    assert run==request('/study/runs',{'request_id':key,'inputs':inputs},f'192.0.2.{i+2}')
    print(label,run['id'],flush=True)
    receipts.append({'label':label,'inputs':inputs,'id':run['id']})
for receipt in receipts:
    for _ in range(180):
        status=request('/study/runs/'+receipt['id'])
        if status['state'] in ('complete','failed'):break
        time.sleep(2)
    receipt['status']=status
    if status['state']!='complete':
        raise AssertionError(status)
    result=request('/study/runs/'+receipt['id']+'/result')
    assert result['checks_passed'],json.dumps([[g['gates'] for g in v['levels']] for v in result['variants']])
    receipt['elapsed_seconds']=result['elapsed_seconds']
    receipt['selected_gap_mm']=result['selected_gap_mm']
    receipt['variants']=[{k:v[k] for k in ('gap_mm','pressure_drop_pa','analytical_pa','mesh_change_pct','checks_passed','margin_pa')} for v in result['variants']]
    artifact=OUT/(receipt['label']+'.zip')
    subprocess.run(['docker','cp',f"alex-blythe-site-study-api-1:/data/{receipt['id']}/evidence.zip",str(artifact)],check=True,capture_output=True)
    assert hashlib.sha256(artifact.read_bytes()).hexdigest()==status['evidence_sha256']
    with zipfile.ZipFile(artifact) as bundle:
        hashes=json.loads(bundle.read('sha256.json'))
        assert all(hashlib.sha256(bundle.read(name)).hexdigest()==sha for name,sha in hashes.items())
        assert 'report.html' in hashes
        (OUT/(receipt['label']+'-report.html')).write_bytes(bundle.read('report.html'))
        (OUT/(receipt['label']+'-result.json')).write_bytes(bundle.read('result.json'))
        receipt['verified_artifacts']=len(hashes)
    print(receipt['label'],'PASS',receipt['elapsed_seconds'],'seconds',flush=True)
(OUT/'integration.json').write_text(json.dumps(receipts,indent=2))
