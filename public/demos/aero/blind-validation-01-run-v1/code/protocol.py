"""Custodian-side blind challenge ledger. No model or solver is launched here.

The state machine enforces chronology and byte commitments. It cannot certify
that an operator/model has never learned a public dataset. See README.md.
"""
import argparse, base64, csv, hashlib, io, json, math, os, re, subprocess
from datetime import datetime, timezone
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encode(v):return (json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def finite(v):return type(v) in (int,float) and math.isfinite(v)
def check_key_location(directory,keypath):
    directory=Path(directory).resolve();keypath=Path(keypath).resolve()
    if keypath.is_relative_to(directory):raise ValueError('Key must be outside challenge tree')
    probe=directory
    while not probe.exists():probe=probe.parent
    try:repo=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=probe,text=True,stderr=subprocess.DEVNULL).strip()).resolve()
    except subprocess.CalledProcessError:repo=None
    if repo and keypath.is_relative_to(repo):raise ValueError('Key must be outside the repository')
def complete(v):
    if v is None or v=='' or v==[] or v=={}:return False
    if isinstance(v,dict):return all(complete(x) for x in v.values())
    if isinstance(v,list):return all(complete(x) for x in v)
    return not isinstance(v,float) or math.isfinite(v)

FIELDS=['benchmark_id','source_citation','source_version','input_sha256','sealed_reference_sha256','quantities','stations','geometry_source','dimensional_assumptions','flow_conditions','solver','governing_equations','turbulence_model','wall_treatment','boundary_conditions','initial_conditions','mesh_strategy','mesh_levels','refinement_strategy','yplus_criterion','convergence_criteria','conservation_criteria','residual_criteria','comparison_metrics','acceptance_thresholds','experimental_uncertainty','allowable_preprocessing','prohibited_tuning','failure_conditions','repository_commit','environment_versions','date_time']

def validate_criteria(c):
    if c.get('status')!='READY_TO_FREEZE':raise ValueError('Draft criteria cannot be frozen')
    for k in FIELDS:
        if k not in c or not complete(c[k]):raise ValueError('Missing/incomplete preregistration field: '+k)
    if len(c['mesh_levels'])<3:raise ValueError('Three mesh levels required by this framework')
    if c['comparison_metrics']!=['rmse','max_absolute_error']:raise ValueError('Unsupported comparison metrics')
    if set(c['quantities'])!=set(c['acceptance_thresholds']):raise ValueError('Quantity/threshold mismatch')
    for q,t in c['acceptance_thresholds'].items():
        if set(t)!=set(c['comparison_metrics']) or any(not finite(v) or v<=0 for v in t.values()):raise ValueError('Invalid threshold '+q)
    if c['experimental_uncertainty']['gate_policy']!='descriptive_only_no_threshold_widening':raise ValueError('Unsupported uncertainty policy')
    if len(c['stations'])!=len(set(c['stations'])):raise ValueError('Duplicate station')

def parse_reference(raw):
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))));out={}
    if not rows or set(rows[0])!={'quantity','station','value','uncertainty'}:raise ValueError('Reference CSV schema')
    for r in rows:
        k=(r['quantity'],r['station']);v=float(r['value']);u=None if r['uncertainty']=='' else float(r['uncertainty'])
        if k in out or not math.isfinite(v) or (u is not None and (not math.isfinite(u) or u<0)):raise ValueError('Invalid/duplicate measurement')
        out[k]=(v,u)
    return out

def compare(prediction,reference,criteria):
    expected={(q,s) for q in criteria['quantities'] for s in criteria['stations']}
    ref=parse_reference(reference);pred={}
    for r in prediction['values']:
        k=(r['quantity'],r['station'])
        if k in pred or not finite(r['value']):raise ValueError('Invalid/duplicate prediction')
        pred[k]=r['value']
    if set(pred)!=expected or set(ref)!=expected:raise ValueError('Coverage failure: no omitted points, hidden regions or interpolation')
    metrics={};point_errors=[]
    for q in criteria['quantities']:
        errors=[];overlap=[]
        for s in criteria['stations']:
            key=(q,s);value,u=ref[key];e=pred[key]-value;errors.append(e)
            point_errors.append({'quantity':q,'station':s,'prediction':pred[key],'reference':value,'signed_error':e,'absolute_error':abs(e),'relative_error':None if value==0 else abs(e/value),'uncertainty':u,'uncertainty_overlap':None if u is None else abs(e)<=u})
            if u is not None:overlap.append(abs(e)<=u)
        rmse=math.sqrt(sum(e*e for e in errors)/len(errors));maximum=max(map(abs,errors));t=criteria['acceptance_thresholds'][q]
        metrics[q]={'rmse':rmse,'max_absolute_error':maximum,'pass':rmse<=t['rmse'] and maximum<=t['max_absolute_error'],'uncertainty_overlap_count':sum(overlap) if overlap else None,'uncertainty_known_points':len(overlap)}
    passes=[x['pass'] for x in metrics.values()]
    comparison_status='PASS' if all(passes) else 'FAIL' if not any(passes) else 'MIXED'
    numeric=prediction['numerical_status']
    return {'schema':'aero.blind.comparison.v1','experimental_comparison':comparison_status,'status':comparison_status if numeric=='PASS' else 'FAIL','numerical_status':numeric,'metrics':metrics,'all_points':point_errors,'scope':'Specific benchmark only. No universal validation or design readiness.'}

class Challenge:
    def __init__(self,path):self.root=Path(path).resolve()
    def load(self,name):return json.loads((self.root/name).read_text())
    def save(self,name,v):
        p=self.root/name
        if p.exists():raise ValueError('Immutable artifact already exists: '+name)
        p.write_bytes(v if isinstance(v,bytes) else encode(v))
    def state(self):return self.load('state.json')
    def event(self,stage,**extra):
        s=self.state() if (self.root/'state.json').exists() else {'schema':'aero.blind.state.v1','events':[]}
        s['stage']=stage;s['events'].append({'stage':stage,'time':now(),**extra})
        temp=self.root/'state.pending';temp.write_bytes(encode(s));os.replace(temp,self.root/'state.json')
    def require(self,stage):
        if self.state()['stage']!=stage:raise ValueError('Expected stage '+stage)
    def intact(self):
        for e in self.state()['events']:
            for name,h in e.get('files',{}).items():
                p=(self.root/name).resolve()
                if not p.is_relative_to(self.root) or not p.is_file() or sha(p.read_bytes())!=h:raise ValueError('Frozen artifact changed: '+name)
    def hashes(self,names):return {n:sha((self.root/n).read_bytes()) for n in names}
    def seal(self,inputs,reference,key,custody):
        if self.root.exists() and any(self.root.iterdir()):raise ValueError('Use a new empty challenge directory')
        allowed={'benchmark_id','source_citation','source_version','geometry','flow_conditions','facility','quantities','stations','permitted_uncertainty'}
        if set(inputs)!=allowed or not complete(inputs):raise ValueError('Input package must use reviewed allowlisted fields')
        if custody.get('reviewed_no_answer_material') is not True or not custody.get('custodian_id'):raise ValueError('Custodian review required')
        parse_reference(reference)
        if len(key)!=32:raise ValueError('AES-256 key required')
        self.root.mkdir(parents=True,exist_ok=True)
        nonce=os.urandom(12);cipher=AESGCM(key).encrypt(nonce,reference,inputs['benchmark_id'].encode())
        self.save('input.json',inputs);self.save('reference.enc',nonce+cipher);self.save('custody.json',custody)
        self.save('reference-metadata.json',{'algorithm':'AES-256-GCM','plaintext_sha256':sha(reference),'ciphertext_sha256':sha(nonce+cipher),'license_clearance':custody.get('license_clearance','UNRESOLVED')})
        self.event('INPUT_FROZEN',files=self.hashes(['input.json','reference.enc','custody.json','reference-metadata.json']))
    def freeze_criteria(self,c):
        self.require('INPUT_FROZEN');self.intact();validate_criteria(c)
        if c['input_sha256']!=sha((self.root/'input.json').read_bytes()) or c['sealed_reference_sha256']!=sha((self.root/'reference.enc').read_bytes()):raise ValueError('Package hash mismatch')
        i=self.load('input.json')
        if c['benchmark_id']!=i['benchmark_id'] or c['quantities']!=i['quantities'] or c['stations']!=i['stations']:raise ValueError('Permitted input mismatch')
        self.save('preregistration.json',c);self.event('CRITERIA_FROZEN',files=self.hashes(['preregistration.json']))
    def anchor(self,commit):
        stage=self.state()['stage']
        if stage not in ['CRITERIA_FROZEN','PREDICTION_FROZEN','COMPARED']:raise ValueError('No anchorable checkpoint')
        if not re.fullmatch('[0-9a-f]{40}',commit):raise ValueError('Full Git commit required')
        self.intact()
        repo=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=self.root,text=True).strip()).resolve()
        # Explicit remote verification, not a caller-supplied timestamp string.
        subprocess.check_call(['git','fetch','origin','main'],cwd=repo,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=repo,text=True).split()[0]
        subprocess.check_call(['git','merge-base','--is-ancestor',commit,remote],cwd=repo)
        files={k:v for e in self.state()['events'] for k,v in e.get('files',{}).items()}
        for n,h in files.items():
            rel=(self.root/n).relative_to(repo).as_posix();blob=subprocess.check_output(['git','show',commit+':'+rel],cwd=repo)
            if sha(blob)!=h:raise ValueError('Commit does not contain frozen bytes: '+n)
        self.event(stage+'_ANCHORED',commit=commit,remote_head=remote,files={})
    def start(self,receipt):
        self.require('CRITERIA_FROZEN_ANCHORED');self.intact()
        for k in ['fresh_predictor_context','reference_not_mounted','network_disabled','rag_disabled','key_not_available']:
            if receipt.get(k) is not True:raise ValueError('Isolation attestation missing '+k)
        if not receipt.get('predictor_id') or not receipt.get('supervisor_id'):raise ValueError('Named roles required')
        self.save('isolation.json',receipt);self.event('SOLVE',files=self.hashes(['isolation.json']))
    def freeze_prediction(self,p):
        self.require('SOLVE');self.intact();c=self.load('preregistration.json')
        if p.get('numerical_status') not in ['PASS','FAIL','NOT_ESTABLISHED']:raise ValueError('Numerical status required')
        if not p.get('engineering_disposition') or not p.get('evidence_manifest'):raise ValueError('Retained evidence manifest and disposition required')
        expected={(q,s) for q in c['quantities'] for s in c['stations']};actual=[]
        for row in p['values']:
            if not finite(row.get('value')):raise ValueError('Non-finite prediction')
            actual.append((row['quantity'],row['station']))
        if set(actual)!=expected or len(actual)!=len(expected):raise ValueError('Incomplete or duplicate frozen curve')
        evidence=p['evidence_manifest']
        for role in ['requirements','first_principles','geometry','topology','mesh','mesh_diagnostics','deck','runtime','solver_log','residuals','conservation','wall_diagnostics','grid_study','extracted_values']:
            row=evidence.get(role,{})
            f=(self.root/row.get('path','')).resolve()
            if not f.is_relative_to(self.root) or not f.is_file() or sha(f.read_bytes())!=row.get('sha256'):raise ValueError('Missing/bad retained evidence '+role)
        self.save('blind_prediction.json',p)
        self.save('blind_prediction.md',('# Frozen prediction\n\n'+p['engineering_disposition']+'\n\nNumerical status: '+p['numerical_status']+'\n\n'+json.dumps(p['values'],indent=2)+'\n').encode())
        files=self.hashes(['blind_prediction.json','blind_prediction.md']);files.update({r['path']:r['sha256'] for r in evidence.values()})
        self.event('PREDICTION_FROZEN',files=files)
    def unseal(self,key):
        self.require('PREDICTION_FROZEN_ANCHORED');self.intact();m=self.load('reference-metadata.json')
        if m['license_clearance']!='REDISTRIBUTION_APPROVED':raise ValueError('Reference redistribution not cleared; do not reveal into a public tree')
        blob=(self.root/'reference.enc').read_bytes();raw=AESGCM(key).decrypt(blob[:12],blob[12:],self.load('input.json')['benchmark_id'].encode())
        if sha(raw)!=m['plaintext_sha256']:raise ValueError('Reference commitment mismatch')
        parse_reference(raw);self.save('reference.csv',raw);self.event('REFERENCE_UNSEALED',files=self.hashes(['reference.csv']))
    def comparison(self):
        self.require('REFERENCE_UNSEALED');self.intact()
        result=compare(self.load('blind_prediction.json'),(self.root/'reference.csv').read_bytes(),self.load('preregistration.json'))
        self.save('comparison.json',result);self.event('COMPARED',files=self.hashes(['comparison.json']));return result

def main():
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('action',choices=['status','seal','criteria','anchor','start','prediction','unseal','compare']);p.add_argument('--json',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--custody',type=Path);p.add_argument('--key-file',type=Path);p.add_argument('--commit');a=p.parse_args();run=Challenge(a.directory)
    key=None
    if a.key_file:
        keypath=a.key_file.resolve()
        check_key_location(a.directory,keypath)
        key=keypath.read_bytes()
    payload=json.loads(a.json.read_text()) if a.json else None
    if a.action=='seal':run.seal(payload,a.reference.read_bytes(),key,json.loads(a.custody.read_text()))
    elif a.action=='criteria':run.freeze_criteria(payload)
    elif a.action=='anchor':run.anchor(a.commit)
    elif a.action=='start':run.start(payload)
    elif a.action=='prediction':run.freeze_prediction(payload)
    elif a.action=='unseal':run.unseal(key)
    elif a.action=='compare':run.comparison()
    # Print stage only: never key bytes or sealed measurements.
    print(json.dumps({'stage':run.state()['stage'],'events':len(run.state()['events'])}))
if __name__=='__main__':main()
