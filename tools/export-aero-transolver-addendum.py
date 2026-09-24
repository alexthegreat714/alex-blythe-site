"""Publish an allowlisted, tested derivative; preserve all prior releases and runs."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

SITE = Path(__file__).resolve().parents[1]
DEST = SITE / 'public/demos/aero/transolver-addendum-2026-09-24'
FILES = ['Aero/physics_ai/' + n for n in ('__init__.py','__main__.py','catalog.json',
    'registry.py','service.py','reference_evidence.py','transolver.py','transolver_worker.py')]
FILES += ['Aero/tests/test_transolver_adapter.py','Aero/docs/PHYSICS_AI_TRANSOLVER_REFERENCE.md']

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def write(p,obj):
    p.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf8')

def counts(p):
    suites=ET.parse(p).getroot().findall('testsuite')
    return {k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}

def main():
    ap=argparse.ArgumentParser()
    for n in ['source','reference','audit','evidence']:ap.add_argument('--'+n,type=Path,required=True)
    args=ap.parse_args()
    if DEST.exists():raise RuntimeError('Immutable public package already exists')
    args.evidence.mkdir(exist_ok=False,parents=True)
    spec=importlib.util.spec_from_file_location('prior',SITE/'tools/export-aero-revisions.py')
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior);prior.ROOT=args.source
    custody={}
    for folder in ['source-revisions-2026-09-24','source-rev-2-3-2026-09-24','physics-ai-workflow-addendum-2026-09-24']:
        root=SITE/'public/demos/aero'/folder
        m=json.loads((root/'SHA256_MANIFEST.json').read_text())
        assert all(sha(root/p)==h for p,h in m.items())
        custody[folder]={'checked':len(m),'missing':0,'mismatch':0,'manifest_sha256':sha(root/'SHA256_MANIFEST.json')}
    # Verify, never edit, both canonical retained-evidence packages.
    for name,root,base in [('reference',args.reference,args.reference.parent),('audit',args.audit,args.audit)]:
        m=json.loads((root/'SHA256_MANIFEST.json').read_text())
        assert all(sha(base/r['path'])==r['sha256'] for r in m['files'])
        custody[name]={'checked':len(m['files']),'missing':0,'mismatch':0,'manifest_sha256':sha(root/'SHA256_MANIFEST.json')}
    old=SITE/'public/demos/aero/physics-ai-workflow-addendum-2026-09-24/aero-rev-2.3-workflow-addendum.zip'
    with zipfile.ZipFile(old) as z:
        payload={p:z.read(p) for p in z.namelist() if p!='SOURCE_MANIFEST.json'}
        records={r['path']:r for r in json.loads(z.read('SOURCE_MANIFEST.json'))['files']}
    for p in FILES:
        data,original=prior.reviewed(p)
        if p.endswith('PHYSICS_AI_TRANSOLVER_REFERENCE.md'):
            text=data.decode().replace('Canonical local evidence: `D:/AeroRuntime/physics_ai/transolver_reference_20260924`.','Canonical execution and audit evidence are retained outside this source archive.')
            text=text.replace('This adapter has **not** been deployed to the running private\nservice or added to the immutable public Rev 2.3 downloads.','This adapter is now included in the public Transolver addendum. It has **not**\nbeen deployed to the running private service; earlier Rev 2.3 downloads remain unchanged.')
            data=text.encode()
        payload[p]=data
        records[p]={'path':p,'source_sha256':original,'release_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
    payload['README.md']=b'''# Aero Rev 2.3 Transolver addendum - 2026-09-24

Cumulative workflow-addendum source plus the NVIDIA Transolver reference adapter.
Read Aero/docs/PHYSICS_AI_TRANSOLVER_REFERENCE.md first. Earlier documents inside
the cumulative archive describe their historical milestones; this README and the
new guide describe the current addendum. The NVIDIA adapter executed, but exact
checkpoint training/preprocessing and engineering accuracy remain NOT_ESTABLISHED.
The separate THUML Transolver++ model remains pending. Models are RESEARCH_ONLY.

Extract into a NEW directory, use an isolated Python 3.12 environment, install
requirements-test.txt, and run: python -m pytest Aero/tests -q
Discovery: python -m Aero.physics_ai list

No model weights, reference geometry, private corpus, credentials, raw runs or
employer data are included. Inference needs separately licensed/provisioned inputs
and an explicit research acknowledgement. Tests neither download models nor run
CFD. This is a source-module release, not a complete Aero service installation.
No private deployment, qualification change or neural-model validation is implied.
'''
    payload['SOURCE_MANIFEST.json']=prior.json_bytes({'revision':'2.3-transolver-addendum-20260924',
        'base_archive_sha256':sha(old),'files':list(records.values()),
        'generated_files':{p:hashlib.sha256(d).hexdigest() for p,d in payload.items() if not p.startswith('Aero/')},
        'runtime_deployed':False,'model_validation':'NOT_ESTABLISHED'})
    out=args.evidence/'release';out.mkdir()
    archive=out/'aero-rev-2.3-transolver-addendum.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p,data in sorted(payload.items()):
            assert not re.search(r'C:[/\\]Users[/\\]blyth|192\.168\.\d+\.\d+|-----BEGIN .*PRIVATE KEY',data.decode())
            info=zipfile.ZipInfo(p,(2026,9,24,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
    extracted=args.evidence/'standalone'
    with zipfile.ZipFile(archive) as z:z.extractall(extracted)
    junit=args.evidence/'standalone.xml'
    run=subprocess.run([sys.executable,'-B','-m','pytest','Aero/tests','-q','-p','no:cacheprovider',
        '--basetemp',str(args.evidence/'test-tmp'),'--junitxml',str(junit)],cwd=extracted,capture_output=True,text=True,timeout=120)
    (args.evidence/'standalone.log').write_text(run.stdout+run.stderr,encoding='utf8')
    if run.returncode:raise RuntimeError('Extracted source tests failed; failure retained')
    worker=json.loads((args.reference/'executions/transolver-18195596b356/EXECUTION_RESULT.json').read_text())
    audit=json.loads((args.audit/'FINAL_RESULTS.json').read_text())
    public={'date':'2026-09-24','model_id':'nvidia-transolver-drivaerml-surface-1.0',
        'state':'REFERENCE_INFERENCE_COMPLETED_NOT_VALIDATED','authority':'RESEARCH_ONLY',
        'applicability':'NOT_ESTABLISHED','held_out_status':'NOT_ESTABLISHED','engineering_validation':'NOT_ESTABLISHED',
        'sample_count':worker['sample_count'],'hardware':worker['hardware'],
        'software_versions':worker['software_versions'],'forward_seconds':worker['inference_seconds'],
        'adapter_wall_seconds':73.958,'adapter_wall_precision':'Rounded retained observation, not repeated benchmark',
        'gpu_peak_allocated_bytes':worker['gpu_peak_allocated_bytes'],
        'parameters':worker['parameters'],'model_arguments':worker['model_arguments'],
        'checkpoint_sha256':audit['checkpoint_sha256'],
        'units_and_discrepancies':json.loads((args.reference/'UNIT_AUDIT.json').read_text()),
        'checkpoint_conventions_state':audit['state'],'conventions_findings':audit['findings'],
        'repeatability':'NOT_MEASURED','source_independence':'LOW_RELATIVE_TO_OPENFOAM',
        'full_mesh_inference':False,'conservation':'NOT_ESTABLISHED_SAMPLE_ONLY',
        'new_inference_during_publication':False,'runtime_deployed':False,'qualification_override':False}
    write(out/'REFERENCE_AND_AUDIT_RESULTS.json',public)
    report=(args.audit/'FINAL_REPORT.md').read_text(encoding='utf8')
    report=report.replace('The separately retained modern CFD wrapper and its hash are indexed in `RETAINED_SOURCE_INDEX.json`.','The [pinned modern CFD wrapper](https://github.com/NVIDIA/physicsnemo-cfd/blob/0612ec4ed54484a47bfa134eda7b3b012a607624/physicsnemo/cfd/evaluation/models/wrappers/transolver/wrapper.py) is retained in the local audit.')
    report=report.replace('This report is stored on D: and is not a new website revision.','This is a public derivative of the immutable local audit, released with the Transolver addendum. It is not a private-runtime promotion.')
    report=report.replace('using the narrowly scoped questions in `UPSTREAM_INQUIRY_DRAFT.md`. The inquiry is prepared but **not sent**.','using the narrowly scoped public checkpoint-recipe inquiry. Submission status is recorded separately in `INQUIRY_STATUS.json`; the original local audit remains unchanged.')
    (out/'CONVENTIONS_AUDIT_REPORT.md').write_text(report,encoding='utf8')
    (out/'IMPLEMENTATION_REPORT.md').write_bytes(payload['Aero/docs/PHYSICS_AI_TRANSOLVER_REFERENCE.md'])
    write(out/'SOURCE_CUSTODY.json',custody)
    write(out/'TEST_RECORD.json',{'extracted_archive':counts(junit),'receipt_sha256':sha(junit),
        'retained_execution_suite':counts(args.reference/'tests-02.xml'),
        'audit_static_checks':json.loads((args.audit/'AUDIT_CHECKS.json').read_text()),
        'meaning':'Software and static-source checks; not neural accuracy validation'})
    write(out/'release.json',{'revision':'2.3-transolver-addendum-20260924','file':archive.name,
        'sha256':sha(archive),'bytes':archive.stat().st_size,'runtime_deployed':False,
        'model_validation':'NOT_ESTABLISHED','base_archive_sha256':sha(old)})
    # Status is a separate publication record, not an edit to the frozen audit.
    shutil.copyfile(args.evidence.parent/'INQUIRY_STATUS.json',out/'INQUIRY_STATUS.json')
    shutil.copyfile(args.evidence.parent/'INQUIRY.md',out/'INQUIRY.md')
    manifest={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()}
    write(out/'SHA256_MANIFEST.json',manifest)
    assert all(sha(out/p)==h for p,h in manifest.items())
    write(out/'VERIFICATION.json',{'checked':len(manifest),'missing':0,'mismatch':0,
        'manifest_sha256':sha(out/'SHA256_MANIFEST.json'),'scope':'All public payloads; manifest and verification envelopes excluded from self-hashing'})
    shutil.copytree(out,DEST)
    print(json.dumps({'tests':counts(junit),'public_files_checked':len(manifest),'archive_sha256':sha(archive)}))

if __name__=='__main__':main()
