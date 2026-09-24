"""Allowlisted cumulative addendum; never mutate a prior source release or model run."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

SITE=Path(__file__).resolve().parents[1]
ROOT=SITE.parents[1]
DEST=SITE/'public/demos/aero/physics-ai-workflow-addendum-2026-09-24'
SPEC=importlib.util.spec_from_file_location('prior',SITE/'tools/export-aero-revisions.py')
prior=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(prior)
FILES=['Aero/physics_ai/'+p for p in ['__main__.py','benchmark.py','screening.py','experiment.py','comparison.py']]
FILES+=['Aero/engineering_validity/contracts.py','Aero/engineering_validity/controller.py',
        'Aero/tests/test_physics_ai_workflows.py','Aero/docs/PHYSICS_AI_WORKFLOW_ADDENDUM.md']

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def write(path,obj):
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf8')

def counts(path):
    suites=ET.parse(path).getroot().findall('testsuite')
    return {k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}

def verify(root,rows):
    return {'checked':len(rows),'missing':sum(not(root/r['path']).is_file() for r in rows),
        'mismatch':sum(sha(root/r['path'])!=r['sha256'] for r in rows if(root/r['path']).is_file())}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True)
    ap.add_argument('--audit',type=Path,required=True);ap.add_argument('--runtime',type=Path,required=True)
    args=ap.parse_args();out=args.evidence/'release';out.mkdir(exist_ok=False)
    sys.path.insert(0,str(ROOT))
    from Aero.physics_ai.benchmark import freeze_benchmark,evaluate_benchmark
    # Preserve and verify prior canonical datasets, including failed/anomalous output.
    custody={}
    for name,base in [('original_runtime',args.runtime),('reference_audit',args.audit)]:
        custody[name]=verify(base,json.loads((base/'SHA256_MANIFEST.json').read_text())['files'])
    for name,base in [('source_2_0_to_2_2',prior.DEST),('source_2_3',SITE/'public/demos/aero/source-rev-2-3-2026-09-24')]:
        old=json.loads((base/'SHA256_MANIFEST.json').read_text())
        custody[name]=verify(base,[{'path':p,'sha256':h} for p,h in old.items()])
    if any(r['missing'] or r['mismatch'] for r in custody.values()):raise RuntimeError('Prior custody failed')
    write(out/'SOURCE_CUSTODY.json',custody)
    # Actual retained model output; no new inference, fitted limits or field-mapping claim.
    audit=args.audit/'REFERENCE_AUDIT.json'
    source=json.loads(audit.read_text());terms=source['coefficient_comparisons']
    names=['Cd','Cs','Cl'];base={'ids':['DrivAerML-run-1'],'components':names,'units':'1','weights':[1.]}
    ref={**base,'values':[[terms[n]['reference'] for n in names]]}
    write(out/'reference-coefficients.json',ref)
    specification={'benchmark_id':'retained-domino-coefficients','dataset':'DrivAerML',
        'dataset_revision':'5d448b209bf654503c64ce7261c34fa125f46392','reference_origin':'OpenFOAM-derived published reference',
        'reference_path':'reference-coefficients.json','reference_sha256':sha(out/'reference-coefficients.json'),
        'geometry_identity':'411e6651284a26fc94924106b833fd79febc6deba63922c929dd8acfc99720d2',
        'weight_units':'1','limits':[],'balance_limits':{},'evaluation_design':'RETROSPECTIVE_DESCRIPTIVE'}
    contract=freeze_benchmark(out,specification)
    pred={'benchmark_contract_sha256':json.loads(contract.read_text())['sha256'],
        'geometry_identity':specification['geometry_identity'],
        'model_identity':{'model_id':'nvidia-domino-drivaerml','checkpoint_sha256':'ad45e9477a7c0336c07a039ba70db7ddc9a2254d4ff94104d9c297ae7d7b662b',
                          'retained_audit_sha256':sha(audit),'source_independence':'LOW','authority':'RESEARCH_ONLY'},
        'field':{**base,'values':[[terms[n]['prediction'] for n in names]]},'balances':{}}
    write(out/'prediction-coefficients.json',pred)
    evaluated=evaluate_benchmark(out,contract.name,'prediction-coefficients.json')
    write(out/'RETAINED_MODEL_EVALUATION.json',evaluated)
    old=SITE/'public/demos/aero/source-rev-2-3-2026-09-24/aero-rev-2.3.zip'
    with zipfile.ZipFile(old) as z:
        payload={n:z.read(n) for n in z.namelist() if n!='SOURCE_MANIFEST.json'}
        records={r['path']:r for r in json.loads(z.read('SOURCE_MANIFEST.json'))['files']}
    for p in FILES:
        data,original=prior.reviewed(p);payload[p]=data
        records[p]={'path':p,'source_sha256':original,'release_sha256':prior.sha(data),'bytes':len(data)}
    payload['README.md']=b'''# Aero Rev 2.3 workflow addendum - 2026-09-24

Cumulative public 2.3 source plus benchmark, review-only screening and bounded
optional-experiment control. Extract into a NEW directory; do not replace an active
installation. Read Aero/docs/PHYSICS_AI_WORKFLOW_ADDENDUM.md first.

This is not a completed multi-model milestone or a deployed private app.
Transolver reference execution is BLOCKED_HUMAN_ACTION; DoMINO is research-only.
No weights, licensed geometry, private corpus or machine credentials are included.
No required engineering gate is relaxed. No solver run or training is launched.

Use an isolated Python 3.12 environment, install requirements-test.txt, then run:
python -m pytest Aero/tests -q
python -m Aero.physics_ai list

Synthetic protocol tests do not validate physics or demonstrate real CFD savings.
'''
    payload['SOURCE_MANIFEST.json']=prior.json_bytes({'revision':'2.3-workflow-addendum-20260924',
        'base_archive_sha256':sha(old),'files':list(records.values()),
        'generated_files':{p:prior.sha(d) for p,d in payload.items() if not p.startswith('Aero/')},
        'full_multi_model_milestone':'BLOCKED_HUMAN_ACTION','runtime_deployed':False})
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w',zipfile.ZIP_DEFLATED) as z:
        for p,b in sorted(payload.items()):
            info=zipfile.ZipInfo(p,(2026,9,24,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    archive=out/'aero-rev-2.3-workflow-addendum.zip';archive.write_bytes(data.getvalue())
    (out/'IMPLEMENTATION_REPORT.md').write_bytes(payload['Aero/docs/PHYSICS_AI_WORKFLOW_ADDENDUM.md'])
    extracted=args.evidence/'standalone';extracted.mkdir(exist_ok=False)
    with zipfile.ZipFile(archive) as z:z.extractall(extracted)
    junit=args.evidence/'standalone.xml'
    run=subprocess.run([sys.executable,'-m','pytest','Aero/tests','-q','-p','no:cacheprovider',
        '--basetemp',str(args.evidence/'standalone-tests'),'--junitxml',str(junit)],
        cwd=extracted,capture_output=True,text=True,timeout=60)
    (args.evidence/'standalone.log').write_text(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError('Extracted archive failed tests; retained log')
    write(out/'TEST_RECORD.json',{'local_suite':counts(args.evidence/'tests-03.xml'),
        'extracted_archive':counts(junit),'local_receipt_sha256':sha(args.evidence/'tests-03.xml'),
        'extracted_receipt_sha256':sha(junit),'new_model_inference':False,
        'warning':'Local disabled cache plugin emits known cache_dir warning',
        'prior_failed_test':'tests-02.xml retained locally: 1 assertion failure,107 passed; witness rejection happened earlier in event chain'})
    write(out/'release.json',{'revision':'2.3-workflow-addendum-20260924','file':archive.name,
        'sha256':sha(archive),'bytes':archive.stat().st_size,'runtime_deployed':False,
        'full_multi_model_milestone':'BLOCKED_HUMAN_ACTION','model_validation':'NOT_ESTABLISHED'})
    manifest={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()}
    write(out/'SHA256_MANIFEST.json',manifest)
    checked=verify(out,[{'path':p,'sha256':h} for p,h in manifest.items()])
    checked['manifest_sha256']=sha(out/'SHA256_MANIFEST.json');write(out/'VERIFICATION.json',checked)
    if checked['missing'] or checked['mismatch']:raise RuntimeError('New custody failed')
    if DEST.exists():raise RuntimeError('Addendum already published; do not overwrite')
    shutil.copytree(out,DEST)
    print(json.dumps({'tests':counts(junit),'verification':checked,'prior_custody':custody,'archive_sha256':sha(archive)},indent=2))

if __name__=='__main__':main()
