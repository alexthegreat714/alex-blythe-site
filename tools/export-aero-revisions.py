"""Explicit source-only release allowlist. Never walk the private runtime tree."""
from pathlib import Path
import hashlib
import io
import json
import re
import zipfile
import argparse

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parents[1]
DEST = SITE / 'public/demos/aero/source-revisions-2026-09-24'
BASELINE = 'Aero/revisions/private_2_0_before_anyjev_20260923'
ROUTING = ['Aero/private/routing_lab/' + x for x in
    ['__init__.py', 'service.py', 'worker.py', 'benchmark.py', 'contract.json', 'examples.json', 'README.md']]
CONTROL = ['Aero/engineering_validity/' + x for x in
    ['__init__.py', 'contracts.py', 'gate.py', 'controller.py', 'adapters.py', 'http.py']]
DEPENDENCIES = ['Aero/__init__.py', 'Aero/engineering_toolkit/__init__.py',
    'Aero/engineering_toolkit/kernel.py', 'Aero/cfd/evidence.py',
    'Aero/core/approval_policy.py', 'Aero/core/measurement_contract.py',
    'Aero/public_stack/engineering_readiness.py', 'Aero/openfoam_pipeline.py',
    'Aero/fea/bounded/controller.py', 'Aero/fea/bounded/contracts.py', 'Aero/fea/bounded/evidence.py']
COMMON = ['Aero/config/deployment_profiles.json', BASELINE+'/config/deployment_profiles.json',
    'Aero/templates/routing_lab.html', 'Aero/tests/test_private_routing_lab.py']
DOCS = ['Aero/docs/ENGINEERING_VALIDITY_GATE.md', 'Aero/docs/ENGINEERING_VALIDITY_GATE_PLAN.md']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def json_bytes(obj):
    return (json.dumps(obj, indent=2, sort_keys=True)+'\n').encode()

def reviewed(path):
    original = (ROOT/path).read_bytes()
    text = original.decode('utf-8-sig').replace('\r\n', '\n')
    # Published derivatives remove personal edge routes. Runtime originals remain intact.
    text = text.replace('https://aegis.alex-blythe.com', 'https://your-aero-host.example')
    text = re.sub(r'C:[/\\]Users[/\\]blyth[/\\]Desktop[/\\]Engineering', '<ENGINEERING_ROOT>', text)
    text = text.replace('C:\\Users\\blyth', '<USER_HOME>')
    for pattern in [r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY', r'gh[pousr]_[A-Za-z0-9]{30,}',
                    r'sk-[A-Za-z0-9_-]{30,}', r'192\.168\.\d+\.\d+', r'10\.0\.\d+\.\d+',
                    r'C:[/\\]Users[/\\]blyth', r'aegis\.alex-blythe\.com']:
        if re.search(pattern, text):
            raise ValueError('Publication review required: '+path+' matches '+pattern)
    return text.encode(), sha(original)

README = '''# Aero public source releases — September 24, 2026

Owner-authorized source publication, not an unauthenticated running service.
No conversations, private corpus, credentials, model weights, runtime databases,
employer data or historical CFD run directories are included.

## Contents and limitations

2.0 is a PARTIAL_BASELINE_REFERENCE: the historical profile configuration and
revision history, not a complete runnable application. The original scoped
snapshot did not constitute a full installation. The private application shell
and personal service integrations are deliberately excluded.

2.1 is the auditable AnyJev Routing Lab module: source, pinned generic contract,
examples, page and software tests. Weights and isolated inference dependencies
must be separately installed. The standalone benchmark script can download its
pinned model when explicitly invoked; it is NOT run by the tests.

2.2 is the cumulative Routing Lab + Engineering Validity Gate source module pack,
including dependency-light first-principles calculations and worker integration
source. It is NOT a complete configured OpenFOAM/CalculiX installation or an
employer-approved engineering tool. No solver campaign is launched by tests.

Publication transformations: normalize text to LF; replace the owner's edge
origin with your-aero-host.example. Original hashes and release hashes are in
SOURCE_MANIFEST.json. Existing lab-only access and approval checks remain.
Do not expose these control routes publicly without authentication.

## Verify and test a downloaded archive

Extract into a new directory. Inspect SOURCE_MANIFEST.json before use.
Use an isolated Python 3.12 environment; install requirements-test.txt, then:

    python -m pytest Aero/tests -q

Tests use synthetic cases and test doubles. Passing them is software evidence,
not neural-model validation, CFD/FEA validation, or hardware qualification.
Framework/model dependencies remain governed by their upstream licenses. No
new license or employer authorization is implied by public source availability.

The current live private app remains authenticated. Public site presentation
revisions, solver convergence-contract versions and source revisions are distinct.
'''

def archive(revision, paths, extra=None):
    records = []
    payload = {'README.md': README.encode(),
               'requirements-test.txt': b'Flask>=3,<4\njsonschema>=4,<5\npytest>=8,<9\n'}
    for path in sorted(set(paths)):
        data, source_hash = reviewed(path)
        payload[path] = data
        records.append({'path': path, 'source_sha256': source_hash,
                        'release_sha256': sha(data), 'bytes': len(data)})
    payload.update(extra or {})
    payload['SOURCE_MANIFEST.json'] = json_bytes({'revision': revision,
        'scope': 'PARTIAL_BASELINE_REFERENCE' if revision=='2.0' else 'SOURCE_MODULE_RELEASE',
        'files': records, 'generated_files': {p:sha(d) for p,d in payload.items() if not p.startswith('Aero/')},
        'private_runtime_published': False})
    path = DEST / ('aero-rev-'+revision+'.zip')
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, (2026,9,24,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info,data)
    data = buffer.getvalue()
    if path.exists() and path.read_bytes()!=data:
        raise RuntimeError('Frozen release would change; create a new version instead: '+path.name)
    path.write_bytes(data)
    return {'revision': revision, 'file': path.name, 'sha256': sha(path.read_bytes()),
            'bytes': path.stat().st_size, 'entries': len(payload)}

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    baseline = [BASELINE+'/config/deployment_profiles.json', BASELINE+'/REVISION.md']
    releases = [archive('2.0', baseline),
        archive('2.1', ['Aero/__init__.py']+ROUTING+COMMON),
        archive('2.2', DEPENDENCIES+ROUTING+COMMON+CONTROL+DOCS+['Aero/tests/test_engineering_validity.py'])]
    (DEST/'README.md').write_bytes(README.encode())
    (DEST/'releases.json').write_bytes(json_bytes({'date':'2026-09-24','releases':releases,
        'rev_2_3':'IN_DEVELOPMENT_NOT_A_RELEASE', 'live_private_authentication':'UNCHANGED',
        'excluded':['private app shell','personal runtime/service configuration','private corpus',
                    'credentials','conversation logs','runtime databases','model weights','raw CFD cases']}))
    manifest = {p.name:sha(p.read_bytes()) for p in sorted(DEST.iterdir())
                if p.name not in {'SHA256_MANIFEST.json','VERIFICATION.json'}}
    (DEST/'SHA256_MANIFEST.json').write_bytes(json_bytes(manifest))
    missing = sum(not (DEST/p).is_file() for p in manifest)
    mismatch = sum(sha((DEST/p).read_bytes()) != h for p,h in manifest.items() if (DEST/p).is_file())
    verification = {'checked':len(manifest),'missing':missing,'mismatch':mismatch,
                    'scope':'Every release ZIP plus public index and README; archive interiors have source manifests'}
    (DEST/'VERIFICATION.json').write_bytes(json_bytes(verification))
    print(json.dumps({'releases':releases,'verification':verification},indent=2))

if __name__=='__main__':
    main()
