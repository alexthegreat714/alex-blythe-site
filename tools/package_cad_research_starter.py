"""Package public upstream snapshots as inert research assets; never run them."""
import hashlib
import json
from pathlib import Path
import zipfile

SITE = Path(__file__).resolve().parents[1]
SOURCE = Path('D:/AeroRuntime/cad_translation_research_20260924')
OUT = SITE / 'public/demos/aero/future-work/cad-design-intent-v0.1'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    receipts = json.loads((SOURCE / 'UPSTREAM_RECEIPTS.json').read_text())
    entries = []
    licenses = {}
    for item in receipts['repositories']:
        path = SOURCE / item['file']
        data = path.read_bytes()
        assert len(data) == item['bytes'] and digest(data) == item['sha256']
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            matches = [n for n in archive.namelist() if len(n.split('/')) == 2 and n.split('/')[-1].upper() in ('LICENSE', 'LICENSE.MD', 'LICENSE.TXT')]
            assert matches, f"Missing top-level license: {item['repo']}"
            text = archive.read(matches[0])
            licenses[item['repo'].split('/')[-1] + '-LICENSE.txt'] = text
            item['retained_license_path'] = matches[0]
            item['license_sha256'] = digest(text)
        entries.append(item)
    (OUT / 'UPSTREAM_RECEIPTS.json').write_text(json.dumps(receipts, indent=2) + '\n', encoding='utf8')
    notices = ('# Third-party source snapshots\n\nUnmodified upstream source ZIPs for research. '
               'Original licenses/notices remain inside every archive. Separate copies of top-level '
               'licenses are supplied for convenience. No dependency installation or upstream code '
               'execution was performed. No warranty or CAD compatibility claim is made. '
               'Review per-file and dependency terms before use; presence in this bundle is not '
               'organizational approval. Source ZIPs are not full git clones and do not include '
               'external dependencies or submodule contents.\n')
    (OUT / 'THIRD_PARTY_NOTICES.md').write_text(notices, encoding='utf8')
    with zipfile.ZipFile(OUT / 'CAD_TRANSLATION_RESEARCH_STARTER.zip', 'w', zipfile.ZIP_DEFLATED) as bundle:
        for item in entries:
            bundle.write(SOURCE / item['file'], 'upstream/' + item['file'])
        for name, data in licenses.items():
            bundle.writestr('licenses/' + name, data)
        for name in ['IMPLEMENTATION_BRIEF.md', 'UPSTREAM_RECEIPTS.json', 'THIRD_PARTY_NOTICES.md']:
            bundle.write(OUT / name, name)
        bundle.write(SITE / 'src/content/research/aero-cad-design-intent-translator.md', 'PROJECT_RESEARCH.md')
    manifest = {'algorithm': 'SHA-256', 'files': [
        {'path': p.name, 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())}
        for p in sorted(OUT.iterdir()) if p.is_file() and not p.name.startswith('.') and p.name not in ('SHA256_MANIFEST.json', 'VERIFICATION.json')
    ]}
    (OUT / 'SHA256_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf8')
    missing = sum(not (OUT / e['path']).is_file() for e in manifest['files'])
    mismatch = sum(digest((OUT / e['path']).read_bytes()) != e['sha256'] for e in manifest['files'] if (OUT / e['path']).is_file())
    with zipfile.ZipFile(OUT / 'CAD_TRANSLATION_RESEARCH_STARTER.zip') as bundle:
        assert bundle.testzip() is None
        for item in entries:
            assert digest(bundle.read('upstream/' + item['file'])) == item['sha256']
    verification = {'checked': len(manifest['files']), 'missing': missing, 'mismatch': mismatch,
        'upstream_archives_checked': len(entries), 'archive_crc': 'PASS',
        'upstream_code_executed': False, 'cad_conversion_tested': False,
        'manifest_sha256': digest((OUT / 'SHA256_MANIFEST.json').read_bytes()),
        'scope': 'Payload hashes and ZIP integrity only; manifest and verification are excluded from recursive self-hashing.'}
    (OUT / 'VERIFICATION.json').write_text(json.dumps(verification, indent=2) + '\n', encoding='utf8')
    assert missing == mismatch == 0
    print(json.dumps(verification))

if __name__ == '__main__':
    main()
