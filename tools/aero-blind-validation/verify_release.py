"""Verify an actual Challenge 01 release and every file inside its case archives.

No reference access is necessary for the archive-only mode. Verification checks
identity and coverage, not physical validity. No files are extracted from ZIPs.
"""
import argparse,json,zipfile,hashlib
from pathlib import Path,PurePosixPath
from protocol import Challenge,sha

def safe_relative(name):
    p=PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
        raise ValueError('Unsafe artifact path '+name)
    return p

def archive(path,expected_case=None):
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP member')
        for name in names:safe_relative(name)
        manifest=json.loads(z.read('archive-manifest.json'))
        if expected_case and manifest['case']!=expected_case:raise ValueError('Archive case mismatch')
        rows=manifest['files']
        if len(rows)!=len({r['path'] for r in rows}):raise ValueError('Duplicate manifest entry')
        if set(names)!={r['path'] for r in rows}|{'archive-manifest.json'}:raise ValueError('ZIP inventory mismatch')
        total=0
        for row in rows:
            data=z.read(row['path'])
            if len(data)!=row['size'] or sha(data)!=row['sha256']:raise ValueError('Archive hash mismatch: '+row['path'])
            total+=len(data)
        return {'case':manifest['case'],'files':len(rows),'bytes':total}

def verify(root,archive_only=False):
    root=Path(root).resolve();ch=Challenge(root);ch.intact()
    index=ch.load('evidence/run-index.json');criteria=ch.load('preregistration.json')
    expected={s+'-'+m['name'] for s in criteria['stations'] for m in criteria['mesh_levels']}
    if {row['case'] for row in index['cases']}!=expected or len(index['cases'])!=len(expected):raise ValueError('Case inventory incomplete')
    checked=[]
    for row in index['cases']:
        p=root/str(safe_relative(row['path']))
        if p.stat().st_size!=row['size'] or sha(p.read_bytes())!=row['sha256']:raise ValueError('Case ZIP hash mismatch '+row['case'])
        checked.append(archive(p,row['case']))
    count=sum(r['files'] for r in checked)
    if count!=index['files_retained']:raise ValueError('Retained file count mismatch')
    if not archive_only:
        ch.require('COMPARED_ANCHORED')
        manifest=ch.load('manifest.json')
        rows=manifest['files'];listed={r['path'] for r in rows}
        if len(rows)!=len(listed):raise ValueError('Duplicate release manifest entry')
        actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        exclusions={'manifest.json','reproduction.zip','publication.json','current-status.json'}
        if actual-exclusions!=listed:raise ValueError('Release inventory mismatch: '+str((actual-exclusions)^listed))
        for row in rows:
            p=root/str(safe_relative(row['path']))
            if p.stat().st_size!=row['size'] or sha(p.read_bytes())!=row['sha256']:raise ValueError('Release file mismatch '+row['path'])
        with zipfile.ZipFile(root/'reproduction.zip') as z:
            desired={r['path'] for r in rows if not r['path'].startswith('evidence/cases/')}|{'manifest.json'}
            if set(z.namelist())!=desired:raise ValueError('Reproduction package inventory mismatch')
            for name in desired:
                if sha(z.read(name))!=sha((root/name).read_bytes()):raise ValueError('Reproduction bytes differ '+name)
    return {'status':'PASS','stage':ch.state()['stage'],'case_archives':len(checked),'retained_case_files':count,'uncompressed_case_bytes':sum(r['bytes'] for r in checked),'identity_is_not_validity':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('--archive-only',action='store_true');a=p.parse_args()
    print(json.dumps(verify(a.package,a.archive_only),indent=2))
