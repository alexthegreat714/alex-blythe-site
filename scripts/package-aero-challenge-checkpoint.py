"""Publish reviewed milestone artifacts only; never the custody tree or seal key."""
import hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'public/demos/aero/blind-validation-01-input-v1'
OUT=ROOT/'public/demos/aero/blind-validation-01-checkpoint-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    if OUT.exists():raise ValueError('Immutable checkpoint already exists')
    OUT.mkdir()
    sources={
        'solver-isolation.json':'output/challenge01/solver-isolation-v1/receipt.json',
        'solver-probe.log':'output/challenge01/solver-isolation-v1/probe.log',
        'solver-help.txt':'output/challenge01/solver-isolation-v1/work/rhoSimpleFoam-help.txt',
        'fresh-review.json':'output/challenge01/fresh-review-v1/receipt.json',
        'fresh-review.raw.txt':'output/challenge01/fresh-review-v1/review.txt',
        'input-only-prompt.txt':'output/challenge01/fresh-review-v1/prompt.txt',
        'README.md':'tools/aero-blind-validation/CHECKPOINT_01.md'
    }
    for dest,src in sources.items():shutil.copyfile(ROOT/src,OUT/dest)
    state=json.loads((INPUT/'state.json').read_text());event=state['events'][0]
    assert state['stage']=='INPUT_FROZEN'
    for name,h in event['files'].items():assert sha(INPUT/name)==h
    assert json.loads((OUT/'solver-isolation.json').read_text())['status']=='PASS'
    assert json.loads((OUT/'fresh-review.json').read_text())['status']=='COMPLETED_REVIEW_ONLY'
    status={'schema':'aero.blind.public.status.v2','challenge':'Aero Blind Validation Challenge 01','status':'NOT_EVALUATED','current_stage':'INPUT_FROZEN','readiness':'HOLD_NUMERICAL_SPECIFICATION','production_runs':0,'scientific_result':None,'source_selection':'TABLE_XIII_FIRST_SERIES_FROZEN','operating_points':18,'sealed_observations':36,'phases':[{'label':label,'status':'FROZEN' if i==0 else 'NOT_OCCURRED','time':event['time'] if i==0 else None} for i,label in enumerate(['Input frozen','Criteria frozen','Solve','Prediction frozen','Reference unsealed','Automated comparison'])],'scientific_hashes':{'input_package':sha(INPUT/'input.json'),'sealed_reference':sha(INPUT/'reference.enc'),'preregistration':None,'blind_prediction':None},'scientific_commits':{'preregistration':None,'prediction_freeze':None,'unseal_comparison':None},'tests':{'passed':19,'kind':'software tests; not experimental validation'},'blockers':['Choose and justify nominal NACA geometry / trailing-edge convention without claiming exact as-built coordinates','Define dimensional fluid properties consistent with Mach 0.15 and Re=5.95e6; disclose assumed temperature','Implement and verify the localized transition-trip approximation and treatment of unknown inlet turbulence','Resolve steady versus unsteady treatment across all 18 operating points; do not delete difficult points','Predeclare three mesh levels, numerical gates, comparison thresholds and uncertainty policy before solving','Freeze and publicly anchor the full numerical specification and audited execution driver'], 'claim':'Input and reference are sealed; inference and solver readiness isolation tested. No scientific result or production solve exists.'}
    write(OUT/'status.json',status)
    input_names=['input.json','reference.enc','reference-metadata.json','custody.json','state.json','README.md']
    write(INPUT/'manifest.json',{'stage':'INPUT_FROZEN','files':[{'path':n,'size':(INPUT/n).stat().st_size,'sha256':sha(INPUT/n),'role':'ciphertext' if n=='reference.enc' else 'input-or-custody-record'} for n in input_names]})
    with zipfile.ZipFile(OUT/'checkpoint-sources.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n in ['protocol.py','test_protocol.py','isolation.py','fresh_review.py','test_isolation.py','CHECKPOINT_01.md']:z.write(ROOT/'tools/aero-blind-validation'/n,'tools/'+n)
        for n in input_names+['manifest.json']:z.write(INPUT/n,'input/'+n)
        for p in sorted(OUT.iterdir()):
            if p.is_file() and p.suffix!='.zip':z.write(p,'checkpoint/'+p.name)
    write(OUT/'manifest.json',{'schema':'aero.artifacts.v1','stage':'INPUT_FROZEN_NOT_SOLVED','files':[{'path':p.name,'size':p.stat().st_size,'sha256':sha(p),'classification':'generated-or-reviewed-input-only','role':'milestone-evidence'} for p in sorted(OUT.iterdir()) if p.is_file()]})
    print(json.dumps({'stage':status['current_stage'],'operating_points':18,'sealed_observations':36,'production_runs':0}))
if __name__=='__main__':main()
