"""Create a versioned report/reproduction manifest after anchored comparison.

Large case ZIPs are kept as permanent separate downloads; the small reproduction
ZIP contains the code, report and a hashed index of every full case archive.
"""
import argparse,json,zipfile,shutil
from pathlib import Path
from protocol import Challenge,sha,encode

def package(root):
    ch=Challenge(root);ch.require('COMPARED_ANCHORED');ch.intact();root=ch.root
    if not (root/'report/paper.pdf').is_file():raise ValueError('Compile and visually verify the actual report first')
    if (root/'manifest.json').exists() or (root/'reproduction.zip').exists():raise ValueError('Existing immutable release; do not overwrite')
    for name in ('freeze_sweep.py','experiment_report.py','render_result.py','package_release.py','verify_release.py'):
        shutil.copyfile(Path(__file__).with_name(name),root/'code'/name)
    # Do not replace the preregistered execution snapshots with later tooling.
    for name,h in ch.load('preregistration.json')['execution_code'].items():
        if sha((root/'code'/name).read_bytes())!=h:raise ValueError('Frozen execution code changed')
    rows=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(root).as_posix()
        if rel in ('current-status.json','publication.json'):continue
        if p.suffix in ('.key','.env') or p.name=='reference-original.pdf':raise ValueError('Forbidden private/source artifact')
        stage='POST_COMPARISON' if rel.startswith('report/') or rel in ('comparison.json','reference.csv') else 'PREDICTION' if rel.startswith('evidence/') or rel.startswith('blind_prediction.') else 'PROTOCOL'
        role='case_archive' if rel.startswith('evidence/cases/') else 'technical_report' if rel=='report/paper.pdf' else 'source_code' if rel.startswith('code/') else 'figure' if rel.startswith('report/') and p.suffix in ('.png','.pdf') else 'provenance_or_data'
        rows.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p.read_bytes()),'role':role,'generation_stage':stage,'classification':'attributed_reference_transcription' if rel=='reference.csv' else 'generated_or_retained'})
    manifest={'schema':'aero.challenge.release-manifest.v1','version':'run-v1','files':rows,'file_count':len(rows),'excluded_dynamic_metadata':['current-status.json','publication.json'],'excluded_self_and_bundle':['manifest.json','reproduction.zip'],'archive_policy':'Permanent public case ZIPs are listed and hashed separately. reproduction.zip contains all other listed files plus this manifest.','identity_is_not_scientific_validity':True}
    (root/'manifest.json').write_bytes(encode(manifest))
    with zipfile.ZipFile(root/'reproduction.zip','x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for row in rows:
            if not row['path'].startswith('evidence/cases/'):z.write(root/row['path'],row['path'])
        z.write(root/'manifest.json','manifest.json')
    from verify_release import verify
    print(json.dumps(verify(root),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);a=p.parse_args();package(a.package)
