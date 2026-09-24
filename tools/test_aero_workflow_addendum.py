import hashlib
import json
from pathlib import Path
import re
import zipfile

SITE=Path(__file__).resolve().parents[1]
RELEASE=SITE/'public/demos/aero/physics-ai-workflow-addendum-2026-09-24'

def test_artifact_custody():
    manifest=json.loads((RELEASE/'SHA256_MANIFEST.json').read_text())
    assert len(manifest)==10
    for name,expected in manifest.items():
        assert hashlib.sha256((RELEASE/name).read_bytes()).hexdigest()==expected
    check=json.loads((RELEASE/'VERIFICATION.json').read_text())
    assert check['missing']==check['mismatch']==0

def test_cumulative_archive_and_public_boundaries():
    with zipfile.ZipFile(RELEASE/'aero-rev-2.3-workflow-addendum.zip') as z:
        manifest=json.loads(z.read('SOURCE_MANIFEST.json'))
        assert manifest['runtime_deployed'] is False
        for record in manifest['files']:
            data=z.read(record['path'])
            assert hashlib.sha256(data).hexdigest()==record['release_sha256']
        for name in z.namelist():
            assert not name.endswith(('.pt','.pth','.mdlus','.npz','.stl','.env'))
            assert not any(p in name.lower() for p in ('private/knowledge','private/corpus','conversation','credentials'))
            assert not re.search(r'C:[/\\]Users[/\\]blyth|192\.168\.\d+\.\d+|-----BEGIN .*PRIVATE KEY',z.read(name).decode())
        assert 'Aero/physics_ai/benchmark.py' in z.namelist()
        assert 'Aero/physics_ai/experiment.py' in z.namelist()

def test_retained_scoring_never_claims_validation():
    r=json.loads((RELEASE/'RETAINED_MODEL_EVALUATION.json').read_text())
    assert r['evaluation_design']=='RETROSPECTIVE_DESCRIPTIVE'
    assert r['checks']==[] and r['balances']=={}
    assert r['engineering_validation']==r['status']=='NOT_ESTABLISHED'
    assert r['metrics']['components']['Cl']['relative_l2_error']>5
    assert r['qualification_override'] is False

def test_report_links_and_tests_are_real():
    page=(SITE/'src/content/research/aero-source-revisions.md').read_text()
    assert 'multi-model milestone is not fully complete' in page
    for link in re.findall(r'\]\((/demos/aero/physics-ai-workflow-addendum[^)]+)\)',page):
        assert (SITE/'public'/link.lstrip('/')).is_file()
    r=json.loads((RELEASE/'TEST_RECORD.json').read_text())
    assert r['local_suite']['tests']==113 and r['extracted_archive']['tests']==110
    assert r['local_suite']['failures']==r['extracted_archive']['failures']==0
