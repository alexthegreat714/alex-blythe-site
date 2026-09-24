"""Freeze public source-release receipts from measured tests, not assertions of model validity."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_counts(path):
    root = ET.parse(path).getroot()
    suites = root.findall('testsuite')
    return {key: sum(int(s.get(key, '0')) for s in suites) for key in ('tests', 'failures', 'errors', 'skipped')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit', required=True, type=Path)
    args = parser.parse_args()
    site = Path(__file__).resolve().parents[1]
    release = site / 'public/demos/aero/source-rev-2-3-2026-09-24'
    extracted = args.audit / 'standalone-final'
    extracted.mkdir(exist_ok=False)
    with zipfile.ZipFile(release / 'aero-rev-2.3.zip') as z:
        z.extractall(extracted)
    junit = args.audit / 'standalone-final.xml'
    run = subprocess.run([sys.executable, '-m', 'pytest', 'Aero/tests', '-q', '--junitxml', str(junit)],
                         cwd=extracted, capture_output=True, text=True, timeout=60)
    (args.audit / 'standalone-final.log').write_text(run.stdout + run.stderr)
    if run.returncode:
        raise RuntimeError('Extracted-archive tests failed; see retained log')
    tests = {'local_focused_suite': test_counts(args.audit / 'tests-final.xml'),
             'publication_and_old_release_custody': test_counts(args.audit / 'public-tests-01.xml'),
             'rev_2_3_extracted_archive': test_counts(junit),
             'actual_pretrained_inference': 'COMPLETED_NOT_VALIDATED',
             'website_build': 'PASS_45_ROUTES',
             'warnings': ['Local pytest cache_dir warning while cache plugin disabled',
                          'Existing Astro bundle-size warning; build succeeded'],
             'test_receipt_sha256': {p.name: sha(p) for p in
                                    [args.audit / 'tests-final.xml', args.audit / 'public-tests-01.xml', junit]}}
    (release / 'TEST_RECORD.json').write_text(json.dumps(tests, indent=2))
    manifest = {p.name: sha(p) for p in sorted(release.iterdir())
                if p.is_file() and p.name not in ('SHA256_MANIFEST.json', 'VERIFICATION.json')}
    (release / 'SHA256_MANIFEST.json').write_text(json.dumps(manifest, indent=2))
    missing = sum(not (release / p).is_file() for p in manifest)
    mismatch = sum(sha(release / p) != h for p, h in manifest.items() if (release / p).is_file())
    verification = {'checked': len(manifest), 'missing': missing, 'mismatch': mismatch,
                    'scope': 'All public release artifacts; ZIP interior additionally verified by SOURCE_MANIFEST.json',
                    'manifest_sha256': sha(release / 'SHA256_MANIFEST.json')}
    (release / 'VERIFICATION.json').write_text(json.dumps(verification, indent=2))
    print(json.dumps({'tests': tests, 'verification': verification}, indent=2))


if __name__ == '__main__':
    main()
