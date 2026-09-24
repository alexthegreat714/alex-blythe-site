import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

RELEASE = Path(__file__).resolve().parents[1] / 'public/demos/aero/source-rev-2-3-2026-09-24'


def test_archive_integrity_and_exclusions():
    meta = json.loads((RELEASE / 'release.json').read_text())
    path = RELEASE / meta['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == meta['sha256']
    with zipfile.ZipFile(path) as z:
        manifest = json.loads(z.read('SOURCE_MANIFEST.json'))
        assert manifest['revision'] == '2.3' and not manifest['private_runtime_published']
        for row in manifest['files']:
            data = z.read(row['path'])
            assert hashlib.sha256(data).hexdigest() == row['release_sha256']
            text = data.decode('utf8')
            assert not re.search(r'C:[/\\]Users[/\\]blyth|192\.168\.\d+\.\d+|-----BEGIN .*PRIVATE KEY', text)
        for path, sha in manifest['generated_files'].items():
            assert hashlib.sha256(z.read(path)).hexdigest() == sha
        assert all(not name.endswith(('.pt', '.mdlus', '.pkl', '.stl', '.vtp', '.db', '.sqlite3')) for name in z.namelist())
        assert not any(part in ('.env', 'conversations', '__pycache__', 'engineering_environment_intake') for n in z.namelist() for part in Path(n).parts)


def test_extracted_archive_is_standalone(tmp_path):
    with zipfile.ZipFile(RELEASE / 'aero-rev-2.3.zip') as z:
        z.extractall(tmp_path)
    result = subprocess.run([sys.executable, '-m', 'pytest', 'Aero/tests', '-q'], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


def test_public_reference_does_not_claim_validation():
    report = json.loads((RELEASE / 'REFERENCE_REPORT.json').read_text())
    assert report['pretrained_scientific_validation'] == 'NOT_ESTABLISHED'
    assert report['witness_verification']['can_satisfy_qualification_gate'] is False
    assert report['audit']['coefficient_comparisons']['Cl']['relative_error'] > 5
    assert report['original_runtime_source_immutability']['source_unchanged'] is True
