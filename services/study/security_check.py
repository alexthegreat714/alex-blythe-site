"""Read-only isolation checks plus rejected requests; never creates a study."""
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

BASE='https://aero-chat.alex-blythe.com'
def response(path,body=None,origin='https://alex-blythe.com'):
    request=urllib.request.Request(BASE+path,json.dumps(body).encode() if body else None,{'Content-Type':'application/json','Origin':origin,'User-Agent':'Mozilla/5.0 AeroAcceptance/1.2'})
    try:
        with urllib.request.urlopen(request,timeout=15) as result:return result.status,result.read().decode()
    except urllib.error.HTTPError as error:return error.code,error.read().decode()

proof=[]
for path in ['/api/tags','/vm/console','/ops/privileged/gx10/recover','/study/runs/not-an-id','/study/anything']:
    code,_=response(path);assert code in (403,404),(path,code);proof.append({'path':path,'status':code})
for body,origin,expected in [({'length_mm':200,'gap_mm':'1; id','flow_ml_s':20,'budget_pa':70},'https://alex-blythe.com',400),({'length_mm':200,'gap_mm':2,'flow_ml_s':20,'budget_pa':70,'command':'id'},'https://alex-blythe.com',400),({'length_mm':200,'gap_mm':2,'flow_ml_s':20,'budget_pa':70},'https://invalid.example',403)]:
    code,detail=response('/study/brief',body,origin);assert code==expected,(code,detail[:200]);proof.append({'rejected_body':body,'origin':origin,'status':code})
for name in ['alex-blythe-site-study-api-1','alex-blythe-site-study-worker-1']:
    data=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
    host=data['HostConfig'];assert host['ReadonlyRootfs'];assert data['Config']['User']=='10001:10001'
    assert all(mount['Type']!='bind' for mount in data['Mounts'])
    assert not host.get('PortBindings');assert 'ALL' in host['CapDrop']
    if name.endswith('worker-1'):
        assert host['NetworkMode']=='none';assert host['Memory']==768*1024**2;assert host['NanoCpus']==2000000000
    proof.append({'container':name,'image':data['Image'],'readonly_root':host['ReadonlyRootfs'],'user':data['Config']['User'],'network':host['NetworkMode'],'memory_bytes':host['Memory'],'cpu_nanos':host['NanoCpus'],'pid_limit':host['PidsLimit'],'cap_drop':host['CapDrop'],'mount_types':[mount['Type'] for mount in data['Mounts']]})
out=Path('.qa/channel-study');out.mkdir(parents=True,exist_ok=True);(out/'security.json').write_text(json.dumps(proof,indent=2))
print('PASS: five private/arbitrary routes unavailable, three invalid requests rejected, API/worker isolation inspected.')
