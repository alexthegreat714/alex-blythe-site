import hashlib
import json
from pathlib import Path
import re
import zipfile

SITE=Path(__file__).resolve().parents[1]
RELEASE=SITE/'public/demos/aero/transolver-addendum-2026-09-24'

def test_public_payload_custody():
    m=json.loads((RELEASE/'SHA256_MANIFEST.json').read_text())
    for name,h in m.items():
        assert hashlib.sha256((RELEASE/name).read_bytes()).hexdigest()==h
    v=json.loads((RELEASE/'VERIFICATION.json').read_text())
    assert v['checked']==len(m) and v['missing']==v['mismatch']==0

def test_source_archive_and_boundary():
    with zipfile.ZipFile(RELEASE/'aero-rev-2.3-transolver-addendum.zip') as z:
        m=json.loads(z.read('SOURCE_MANIFEST.json'))
        assert m['runtime_deployed'] is False
        for row in m['files']:
            assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['release_sha256']
        for name,h in m['generated_files'].items():
            assert hashlib.sha256(z.read(name)).hexdigest()==h
        for name in z.namelist():
            assert not name.endswith(('.pt','.pth','.mdlus','.npz','.stl','.vtp','.env'))
            assert not re.search(r'C:[/\\]Users[/\\]blyth|192\.168\.\d+\.\d+|-----BEGIN .*PRIVATE KEY',z.read(name).decode())
        assert 'Aero/physics_ai/transolver_worker.py' in z.namelist()
        assert 'Aero/physics_ai/experiment.py' in z.namelist()

def test_no_execution_to_validation_promotion():
    r=json.loads((RELEASE/'REFERENCE_AND_AUDIT_RESULTS.json').read_text())
    assert r['authority']=='RESEARCH_ONLY'
    assert r['engineering_validation']==r['held_out_status']=='NOT_ESTABLISHED'
    assert r['qualification_override'] is False
    assert r['repeatability']=='NOT_MEASURED'
    assert r['units_and_discrepancies']['dimensional_comparison']['pressure']['relative_L2']>0.5
    assert r['checkpoint_conventions_state']=='CHECKPOINT_TRAINING_PREPROCESSING_NOT_ESTABLISHED'

def test_report_downloads_and_measured_tests():
    page=(SITE/'src/content/research/aero-transolver-reference-audit.md').read_text()
    for link in re.findall(r'\]\((/demos/aero/[^)]+)\)',page):
        assert (SITE/'public'/link.lstrip('/')).is_file()
    r=json.loads((RELEASE/'TEST_RECORD.json').read_text())
    assert r['extracted_archive']['tests']==125
    assert r['extracted_archive']['failures']==r['extracted_archive']['errors']==0
    assert r['audit_static_checks']['passed']==10
    assert 'Transolver execution &amp; audit' in (SITE/'src/pages/software/[slug].astro').read_text(encoding='utf8')

def test_old_archives_unchanged():
    for directory in ['source-revisions-2026-09-24','source-rev-2-3-2026-09-24','physics-ai-workflow-addendum-2026-09-24']:
        root=SITE/'public/demos/aero'/directory
        for name,h in json.loads((root/'SHA256_MANIFEST.json').read_text()).items():
            assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h

def test_public_text_has_no_local_machine_identifiers():
    for p in RELEASE.iterdir():
        if p.suffix in ('.md','.json'):
            assert not re.search(r'C:[/\\]Users|192\.168\.\d+\.\d+|-----BEGIN .*PRIVATE KEY|AEGIS_LOCAL_TOKEN',p.read_text())
