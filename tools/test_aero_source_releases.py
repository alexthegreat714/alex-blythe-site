"""Verify public custody and execute tests outside the Engineering repository."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
import pytest

SITE = Path(__file__).resolve().parents[1]
RELEASE = SITE/'public/demos/aero/source-revisions-2026-09-24'

def test_public_archive_custody():
    manifest = json.loads((RELEASE/'SHA256_MANIFEST.json').read_text())
    for path,expected in manifest.items():
        assert hashlib.sha256((RELEASE/path).read_bytes()).hexdigest()==expected

@pytest.mark.parametrize('revision',['2.0','2.1','2.2'])
def test_archive_allowlist_and_internal_hashes(revision):
    with zipfile.ZipFile(RELEASE/f'aero-rev-{revision}.zip') as z:
        assert all(not any(part in {'.env','__pycache__','pipeline','conversations'} for part in Path(n).parts) for n in z.namelist())
        assert not any(n.endswith(('.sqlite3','.db','.pt','.safetensors')) for n in z.namelist())
        m=json.loads(z.read('SOURCE_MANIFEST.json'))
        for row in m['files']:
            assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['release_sha256']
        for path,expected in m['generated_files'].items():
            assert hashlib.sha256(z.read(path)).hexdigest()==expected

@pytest.mark.parametrize('revision',['2.1','2.2'])
def test_extracted_archive_standalone_software_suite(tmp_path,revision):
    with zipfile.ZipFile(RELEASE/f'aero-rev-{revision}.zip') as z:
        z.extractall(tmp_path)
    env=dict(os.environ)
    env.pop('PYTHONPATH',None)
    result=subprocess.run([sys.executable,'-m','pytest','Aero/tests','-q'],cwd=tmp_path,
        env=env,text=True,capture_output=True,timeout=60)
    assert result.returncode==0, result.stdout+'\n'+result.stderr

def test_public_page_labels_scope_and_navigation():
    article=(SITE/'src/content/research/aero-source-revisions.md').read_text(encoding='utf8')
    assert 'Partial snapshot' in article and 'not complete one-click' in article
    assert 'Rev 2.3 cumulative source' in article and 'RESEARCH_ONLY' in article
    assert '/software/notes/aero-source-revisions/' in (SITE/'src/pages/software/[slug].astro').read_text(encoding='utf8')

def test_export_cannot_rewrite_a_published_revision(tmp_path,monkeypatch):
    spec=importlib.util.spec_from_file_location('export_revisions',SITE/'tools/export-aero-revisions.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    destination=tmp_path/'release';destination.mkdir()
    monkeypatch.setattr(module,'ROOT',tmp_path);monkeypatch.setattr(module,'DEST',destination)
    source=tmp_path/'example.py';source.write_text('original = True\n')
    module.archive('test',['example.py'])
    before=(destination/'aero-rev-test.zip').read_bytes()
    source.write_text('original = False\n')
    with pytest.raises(RuntimeError,match='Frozen release would change'):
        module.archive('test',['example.py'])
    assert (destination/'aero-rev-test.zip').read_bytes()==before
