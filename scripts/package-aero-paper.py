"""Maintainer-only: package a compiled, visually reviewed paper with its run evidence."""
import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('paper_folder',type=Path)
parser.add_argument('solver_evidence',type=Path)
parser.add_argument('destination',type=Path)
args=parser.parse_args()
digest=lambda data:hashlib.sha256(data).hexdigest()
paper_result=json.loads((args.paper_folder/'result.json').read_text())
with zipfile.ZipFile(args.solver_evidence) as original:
    result=json.loads(original.read('result.json'))
    assert result['id']==paper_result['id'],'Paper and solver evidence must be the same run'
    assert result==paper_result,'Paper inputs and numerical evidence must match exactly'
    old_manifest=json.loads(original.read('sha256.json'))
    for name,expected in old_manifest.items():
        assert digest(original.read(name))==expected,f'Source evidence mismatch: {name}'
    args.destination.mkdir(parents=True,exist_ok=True)
    manifest={}
    with zipfile.ZipFile(args.destination/'research-paper-sources.zip','w',zipfile.ZIP_DEFLATED) as target:
        def add(name,data):
            assert name not in manifest,f'Duplicate artifact: {name}'
            manifest[name]=digest(data);target.writestr(name,data)
        for name in old_manifest:
            # Preserve automatic papers when adding a reviewed screenshot appendix.
            target_name='original-report/'+name if name=='paper.pdf' or name.startswith('cases/paper/') else name
            add(target_name,original.read(name))
        for file in sorted(args.paper_folder.iterdir()):
            if file.is_file() and file.suffix in {'.tex','.pdf','.png','.json','.py'} and not file.name.startswith('page-'):
                add('cases/paper/'+file.name,file.read_bytes())
        add('paper.pdf',(args.paper_folder/'paper.pdf').read_bytes())
        target.writestr('sha256.json',json.dumps(manifest,indent=2))
    shutil.copyfile(args.paper_folder/'paper.pdf',args.destination/'research-paper.pdf')
    receipt={'run_id':result['id'],'paper_sha256':digest((args.paper_folder/'paper.pdf').read_bytes()),'source_bundle_sha256':digest((args.destination/'research-paper-sources.zip').read_bytes()),'hashed_artifacts':len(manifest),'screenshots':json.loads((args.paper_folder/'figures.json').read_text())['screenshot_sha256']}
    (args.destination/'research-paper-manifest.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))
