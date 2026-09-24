"""New immutable cumulative source release; never rebuild the 2.0–2.2 archives."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import re
import zipfile

SITE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prior_export', SITE / 'tools/export-aero-revisions.py')
prior = importlib.util.module_from_spec(spec); spec.loader.exec_module(prior)
DEST = SITE / 'public/demos/aero/source-rev-2-3-2026-09-24'
FILES = ['Aero/physics_ai/' + x for x in (
    '__init__.py', '__main__.py', 'catalog.json', 'registry.py', 'service.py',
    'evidence.py', 'comparison.py', 'integration.py', 'domino.py', 'domino_worker.py',
    'reference_evidence.py', 'dataset.schema.json')]
FILES += ['Aero/engineering_validity/controller.py', 'Aero/tests/test_physics_ai.py',
          'Aero/tests/test_domino_adapter.py', 'Aero/docs/PHYSICS_AI_REV_2_3_PLAN.md',
          'Aero/docs/PHYSICS_AI_REV_2_3_IMPLEMENTATION.md']
README = '''# Aero source Rev 2.3 — September 24, 2026

Cumulative 2.2 modules plus optional controlled Physics-AI witness infrastructure
and a tested pinned DoMINO reference adapter. NOT a complete private app install.
The private live service remains separately authenticated and is not upgraded by
downloading this archive. No weights, private corpus, credentials, conversations,
employer data or raw CFD cases are included.

Read Aero/docs/PHYSICS_AI_REV_2_3_IMPLEMENTATION.md first. The reference inference
completed, but lift disagreed substantially with the published reference. Model
authority is RESEARCH_ONLY, applicability/physical validation NOT_ESTABLISHED.
Transolver remains a stub. Other benchmark/model integrations remain explicit
future work. No training or autonomous geometry optimization is implemented.

Extract into a new directory. In an isolated Python 3.12 environment:

    python -m pip install -r requirements-test.txt
    python -m pytest Aero/tests -q
    python -m Aero.physics_ai list

These tests do not download neural weights or launch CFD. Actual reference
inference requires the separately licensed/provisioned Linux CUDA environment,
an operator-owned worker configuration, and explicit research acknowledgement.
See the implementation guide. The package lock is reference-environment evidence,
not dependencies to install in the main Aero process. Source availability grants
no employer authorization and does not change upstream model/software licenses.

The base 2.2 ZIP is reused byte-for-byte internally except explicitly updated
files in SOURCE_MANIFEST.json. The historical ZIP itself is never changed.
Published text is LF-normalized and personal origins are replaced by examples.
'''


def immutable(path, data):
    if path.exists() and path.read_bytes() != data:
        raise RuntimeError('Frozen release would change: ' + path.name)
    if not path.exists():
        path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, required=True)
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    old = prior.DEST / 'aero-rev-2.2.zip'
    old_expected = json.loads((prior.DEST / 'SHA256_MANIFEST.json').read_text())[old.name]
    assert prior.sha(old.read_bytes()) == old_expected
    with zipfile.ZipFile(old) as z:
        payload = {p: z.read(p) for p in z.namelist() if p != 'SOURCE_MANIFEST.json'}
        old_manifest = json.loads(z.read('SOURCE_MANIFEST.json'))
    records = {r['path']: r for r in old_manifest['files']}
    for path in FILES:
        data, original = prior.reviewed(path)
        payload[path] = data
        records[path] = {'path': path, 'source_sha256': original, 'release_sha256': prior.sha(data), 'bytes': len(data)}
    payload['README.md'] = README.encode()
    payload['SOURCE_MANIFEST.json'] = prior.json_bytes({
        'revision': '2.3', 'scope': 'SOURCE_MODULE_RELEASE_RESEARCH_ADAPTER',
        'base_archive_sha256': old_expected, 'files': list(records.values()),
        'generated_files': {p: prior.sha(d) for p, d in payload.items() if not p.startswith('Aero/')},
        'private_runtime_published': False, 'physical_validation': 'NOT_ESTABLISHED'})
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for path, data in sorted(payload.items()):
            info = zipfile.ZipInfo(path, (2026, 9, 24, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    immutable(DEST / 'aero-rev-2.3.zip', archive.getvalue())
    # Explicit public, non-sensitive subset of the reference experiment.
    execution = json.loads((args.audit / 'ADAPTER_RESULT.json').read_text())
    run = Path(execution['artifact_directory'])
    worker = json.loads((run / 'EXECUTION_RESULT.json').read_text())
    audit = json.loads((args.audit / 'REFERENCE_AUDIT.json').read_text())
    ingestion = json.loads((args.audit / 'INGESTION_SUMMARY.json').read_text())
    report = {'revision': '2.3', 'date': '2026-09-24', 'adapter_status': execution['status'],
        'hardware': worker['hardware'], 'software_versions': worker['software_versions'],
        'worker_wall_seconds': worker['wall_seconds'], 'peak_torch_allocated_bytes': worker['peak_torch_allocated_bytes'],
        'audit': audit, 'witness_verification': ingestion['verification'],
        'source_audit': json.loads((args.audit / 'SOURCE_AUDIT.json').read_text()),
        'original_runtime_source_immutability': json.loads((args.audit / 'SOURCE_VERIFICATION.json').read_text()),
        'pretrained_scientific_validation': 'NOT_ESTABLISHED', 'live_private_runtime_changed': False}
    # Remove only the generated command comment containing personal host paths.
    lock = '\n'.join(line for line in (args.runtime / 'pylock.toml').read_text().splitlines()
                     if not (line.startswith('#') and ('C:/Users/' in line or 'D:/AeroRuntime/' in line))) + '\n'
    for name, data in {'REFERENCE_REPORT.json': prior.json_bytes(report), 'README.md': README.encode(),
                       'IMPLEMENTATION_REPORT.md': payload['Aero/docs/PHYSICS_AI_REV_2_3_IMPLEMENTATION.md'],
                       'REFERENCE_RUNTIME_LOCK.toml': lock.encode(),
                       'RUNTIME_BUNDLE_MANIFEST.json': (args.runtime / 'DOWNLOAD_PLAN.json').read_bytes()}.items():
        text = data.decode('utf8')
        for pattern in (r'C:[/\\]Users', r'192\.168\.\d+\.\d+', r'-----BEGIN .*PRIVATE KEY', r'gh[pousr]_[A-Za-z0-9]{30,}'):
            if re.search(pattern, text):
                raise ValueError('Public evidence privacy review: ' + name)
        immutable(DEST / name, data)
    release = {'revision': '2.3', 'file': 'aero-rev-2.3.zip', 'sha256': prior.sha(archive.getvalue()),
               'bytes': len(archive.getvalue()), 'scope': 'SOURCE_MODULE_RELEASE_RESEARCH_ADAPTER',
               'runtime_deployed': False, 'engineering_validation': 'NOT_ESTABLISHED'}
    immutable(DEST / 'release.json', prior.json_bytes(release))
    print(json.dumps(release, indent=2))


if __name__ == '__main__':
    main()
