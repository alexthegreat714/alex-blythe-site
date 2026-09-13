"""Input-only numerical readiness review in a disposable networkless Ollama.

Mounts ONLY the named public model cache's models subdirectory read-only. No
reference, input source tree, chat history or output directory is mounted. The
fresh prompt is passed to a new CLI process through stdin. Not a solver run.
"""
import argparse,hashlib,json,subprocess,time,uuid
from datetime import datetime,timezone
from pathlib import Path

IMAGE='sha256:684d8674b4315fa18f4f0e973a118ec2652ed96f67563277839985175858e0ba'
VOLUME='alex-blythe-site_aero-public-models'
MODEL='gemma3:12b'
POLICY='''You are Aero's fresh input-only numerical planning reviewer. You receive no previous conversation and no experimental measurements. You have no tools, browsing, RAG, filesystem documents or source paper. Do not infer or quote expected lift/drag values, published outcomes, or memorized benchmark answers. Use only the INPUT below plus generic engineering methods.
This is a READINESS REVIEW, not an authorized solve or frozen preregistration. Review all operating points, preserve the complete series, and distinguish missing facts from proposed assumptions. Do not silently replace a fixed transition strip with fully turbulent flow. Do not claim a model is valid across separated/unsteady conditions without evidence. Do not assign numerical acceptance thresholds based on anticipated answers.
Return a concise structured review: (1) HOLD or READY TO DRAFT (neither authorizes solving); (2) unresolved inputs/modeling equivalences; (3) proposed solver/mesh/time treatment with rationale; (4) pre-answer numerical verification gates that need quantified criteria; (5) what must be decided before preregistration. Explicitly state when the provided source does not establish a fact. Keep the review below 1000 words.
INPUT:
'''
def cmd(*a):return subprocess.check_output(list(a),text=True,stderr=subprocess.PIPE).strip()
def review(input_file,out):
    input_file=Path(input_file);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    raw=input_file.read_bytes();prompt=POLICY+raw.decode('utf8');cid=None
    (out/'prompt.txt').write_text(prompt,encoding='utf8',newline='\n')
    receipt={'schema':'aero.blind.fresh-review.v1','kind':'INPUT_ONLY_READINESS_REVIEW_NOT_PREDICTION','started_at':datetime.now(timezone.utc).isoformat(),'model':MODEL,'image':IMAGE,'input_sha256':hashlib.sha256(raw).hexdigest(),'source_context_inherited':False,'rag':False,'tools':False,'experimental_values_supplied':False,'production_solver_runs':0}
    try:
        cid=cmd('docker','create','--name','aero-ch01-review-'+uuid.uuid4().hex[:10],
            '--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges',
            '--user','10001:10001','--gpus','all','--cpus','2','--memory','6g','--memory-swap','6g','--pids-limit','256',
            '--tmpfs','/tmp:rw,nosuid,size=1073741824','--tmpfs','/home/reviewer:rw,nosuid,uid=10001,gid=10001,size=16777216',
            '--mount',f'type=volume,src={VOLUME},dst=/models,volume-subpath=models,readonly',
            '-e','HOME=/home/reviewer','-e','OLLAMA_MODELS=/models','-e','OLLAMA_HOST=127.0.0.1:11434',
            '-e','OLLAMA_KEEP_ALIVE=0','-e','OLLAMA_NUM_PARALLEL=1',IMAGE,'serve')
        c=json.loads(cmd('docker','inspect',cid))[0];h=c['HostConfig']
        assert h['NetworkMode']=='none' and h['ReadonlyRootfs'] and c['Config']['User']=='10001:10001'
        assert len(c['Mounts'])==1 and c['Mounts'][0]['Destination']=='/models' and c['Mounts'][0]['RW'] is False
        assert h['Mounts'][0]['VolumeOptions']['Subpath']=='models'
        receipt['container_id']=cid;receipt['isolation']={'network_mode':h['NetworkMode'],'read_only_root':h['ReadonlyRootfs'],'user':c['Config']['User'],'cap_drop':h['CapDrop'],'security_opt':h['SecurityOpt'],'mount_targets':['/models'],'read_only_model_subpath':'models','host_filesystem_mounts':0,'ephemeral_home':True,'memory_bytes':h['Memory'],'gpu_requested':True}
        cmd('docker','start',cid)
        for _ in range(30):
            p=subprocess.run(['docker','exec',cid,'ollama','list'],capture_output=True,text=True)
            if p.returncode==0:break
            time.sleep(1)
        else:raise RuntimeError('Isolated Ollama did not become ready')
        receipt['model_manifest_sha256']=cmd('docker','exec',cid,'sha256sum','/models/manifests/registry.ollama.ai/library/gemma3/12b').split()[0]
        p=subprocess.run(['docker','exec','-i',cid,'ollama','run',MODEL],input=prompt,text=True,encoding='utf8',capture_output=True,timeout=240)
        (out/'review.txt').write_text(p.stdout,encoding='utf8',newline='\n')
        (out/'inference.stderr.txt').write_text(p.stderr,encoding='utf8',newline='\n')
        if p.returncode or not p.stdout.strip():raise RuntimeError('Isolated review failed; inspect private run logs')
        receipt['status']='COMPLETED_REVIEW_ONLY'
    except Exception as e:receipt['status']='FAILED';receipt['error']=str(e);raise
    finally:
        if cid:
            logs=subprocess.run(['docker','logs',cid],capture_output=True,text=True,encoding='utf8')
            (out/'server.log').write_text(logs.stdout+'\n'+logs.stderr,encoding='utf8',newline='\n')
            subprocess.run(['docker','rm','-f',cid],capture_output=True,timeout=15)
        receipt['finished_at']=datetime.now(timezone.utc).isoformat();receipt['artifacts']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8',newline='\n')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();r=review(a.input,a.output);print(json.dumps({'status':r['status'],'model':r['model'],'production_solver_runs':0}))
