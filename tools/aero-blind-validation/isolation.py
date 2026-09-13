"""Restricted, disposable solver readiness probe. Does NOT submit a CFD case.

The only bind-mounted file is an input-only package. No reference/key, repository,
Docker socket, corpus or previous outputs are exposed. Containers are inspected
before starting and removed by their captured ID, never by a wildcard.
"""
import argparse,hashlib,json,subprocess,uuid
from datetime import datetime,timezone
from pathlib import Path

IMAGE='sha256:9d9c9387b6693d4cb4d0963c0e3b7256af22ed320a34cbae7869cf0c497b35f0'
def now():return datetime.now(timezone.utc).isoformat()
def command(*args,**kw):return subprocess.check_output(list(args),text=True,stderr=subprocess.PIPE,**kw).strip()

def inspect_solver(c,input_file,out):
    h=c['HostConfig'];mounts=c['Mounts'];targets={m['Destination']:m for m in mounts}
    assert h['NetworkMode']=='none' and h['ReadonlyRootfs'] is True
    assert c['Config']['User']=='10001:10001'
    assert 'ALL' in h['CapDrop'] and any('no-new-privileges' in s for s in h['SecurityOpt'])
    assert not h.get('Privileged') and not h.get('DeviceRequests')
    assert set(targets)=={'/input/input.json','/work'}
    assert targets['/input/input.json']['RW'] is False and targets['/work']['RW'] is True
    # Docker Desktop rewrites host source spelling; command construction records
    # exact source paths privately, while the public receipt exposes target+hash.
    assert targets['/input/input.json']['Type']=='bind' and targets['/work']['Type']=='bind'
    assert Path(input_file).is_file() and not any(Path(out).iterdir())
    return {'network_mode':h['NetworkMode'],'read_only_root':h['ReadonlyRootfs'],
            'user':c['Config']['User'],'cap_drop':h['CapDrop'],'security_opt':h['SecurityOpt'],
            'privileged':h['Privileged'],'gpu_access':False,'pids_limit':h['PidsLimit'],
            'memory_bytes':h['Memory'],'nano_cpus':h['NanoCpus'],
            'mounts':[{'target':m['Destination'],'read_only':not m['RW'],'type':m['Type']} for m in mounts],
            'input_sha256':hashlib.sha256(Path(input_file).read_bytes()).hexdigest()}

PROBE=r'''set -eu
test "$(id -u)" = 10001
test -r /input/input.json
test ! -e /var/run/docker.sock
test ! -e /custody
test ! -e /reference.csv
test ! -e /reference.enc
test ! -e /challenge01.key
if touch /root-write-probe 2>/dev/null; then exit 41; fi
if timeout 3 bash -c 'echo > /dev/tcp/1.1.1.1/443' 2>/dev/null; then exit 42; fi
command -v rhoSimpleFoam
command -v blockMesh
command -v checkMesh
rhoSimpleFoam -help > /work/rhoSimpleFoam-help.txt 2>&1
sha256sum /input/input.json
printf 'ISOLATION_PROBE_PASS\n'
'''

def probe(input_file,out,image=IMAGE):
    input_file=Path(input_file).resolve();out=Path(out).resolve()
    data=json.loads(input_file.read_text(encoding='utf8'))
    if data.get('benchmark_id')!='aero-blind-validation-01':raise ValueError('Wrong input package')
    if any(k in data for k in ['values','reference','prediction','expected_CL','expected_CD']):raise ValueError('Not an input-only document')
    if out.exists():raise ValueError('Use a fresh empty probe directory')
    out.mkdir(parents=True);work=out/'work';work.mkdir()
    cid=None;receipt={'schema':'aero.blind.solver-isolation.v1','kind':'READINESS_PROBE_NOT_CFD','started_at':now(),'image':image,'production_solver_runs':0}
    try:
        cid=command('docker','create','--name','aero-ch01-probe-'+uuid.uuid4().hex[:10],
            '--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges',
            '--user','10001:10001','--cpus','2','--memory','2g','--memory-swap','2g','--pids-limit','128',
            '--tmpfs','/tmp:rw,noexec,nosuid,size=67108864',
            '--mount',f'type=bind,src={input_file},dst=/input/input.json,readonly',
            '--mount',f'type=bind,src={work},dst=/work',
            '--workdir','/work','--entrypoint','/bin/bash',image,'-c',PROBE)
        container=json.loads(command('docker','inspect',cid))[0]
        receipt['container_id']=cid;receipt['enforcement']=inspect_solver(container,input_file,work)
        run=subprocess.run(['docker','start','-a',cid],capture_output=True,text=True,timeout=45)
        (out/'probe.log').write_text(run.stdout+'\n'+run.stderr,encoding='utf8',newline='\n')
        state=json.loads(command('docker','inspect',cid))[0]['State']
        receipt['exit_code']=state['ExitCode'];receipt['oom_killed']=state['OOMKilled']
        if run.returncode or state['ExitCode'] or 'ISOLATION_PROBE_PASS' not in run.stdout:raise RuntimeError('Sandbox probe failed; inspect retained log')
        receipt['status']='PASS'
        receipt['demonstrates']=['read-only input-only bind','non-root process','read-only rootfs','no capabilities','no external TCP connection','no repository or reference mounts','OpenFOAM executable starts']
        receipt['does_not_demonstrate']=['a valid mesh','production case execution','model inference isolation','numerical convergence','physical validation']
    except Exception as e:
        receipt['status']='FAIL';receipt['error']=str(e);raise
    finally:
        if cid:subprocess.run(['docker','rm','-f',cid],capture_output=True,timeout=15)
        receipt['finished_at']=now();receipt['artifacts']={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8',newline='\n')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    r=probe(a.input,a.output);print(json.dumps({'status':r['status'],'kind':r['kind'],'production_solver_runs':0}))
