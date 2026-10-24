"""Curate only the public scalar-transport release, never the Engineering tree."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'public'/'demos'/'aero'/'square-body-transport-v1'
shutil.copyfile(OUT/'paper-sources'/'main.pdf',OUT/'paper.pdf')
shutil.copyfile(Path(__file__).with_name('verify_accuracy.py'),OUT/'verify_accuracy.py')
versions=json.loads((OUT/'accuracy-results.json').read_text())['versions']
(OUT/'requirements.txt').write_text('\n'.join(f'{p}=={versions[p]}' for p in ['numpy','scipy','matplotlib'])+'\n')
(OUT/'README.md').write_text('''# Square-body scalar transport, version 1.0

Public page: https://alex-blythe.com/software/aero/square-body-transport/

This is steady scalar convection-diffusion in a prescribed horizontal velocity
field. The square holds scalar values. Velocity, pressure, drag and vortex
shedding are not solved. No experimental validation or design release is claimed.

## Use

Open Square_Body_Transport.xlsx in desktop Excel. Change amber inputs on Model.
Use iterative calculation with 10,000 iterations and maximum change 1E-10.
Press F9 if needed. The workbook contains no macros or external workbook links.

Read paper.pdf for the governing equations, numerical accuracy and examples.
The complete LaTeX source and figures are in paper-sources.zip.

The browser solver is solver.mjs and its worker is worker.mjs. Run them from
the public page or an HTTP server; module workers do not run from file URLs.
The browser worker message protocol was checked in a Node harness. This is
not cross-browser UI validation.

## Reproduce the independent numerical checks

Extract reproducibility.zip into a new directory, then run:

    python -m pip install -r requirements.txt
    python verify_accuracy.py --output .

This reconstructs the sparse LU, analytical and mesh-refinement checks and
figures. It reads the supplied workbook-reference.json and Excel summary.
It does not rerun Excel. Recorded desktop Excel checks are identified in
excel-verification.json. browser-solver-checks.json records JavaScript and
worker-harness checks. accuracy-results.json states the measured numerical
results; its passing checks do not establish physical accuracy.

Boundary values: inlet scalar 1, square scalar 0, zero-gradient outlet and
top/bottom. Domain 3 m by 2 m; square side 0.5 m, corner (0.8 m,0.75 m).
Domain and square dimensions are reconstruction assumptions. Visible
screenshot inputs rho=1, u=1, Gamma=0.1 and spacing=0.05 are reproduced.
Teaching inspiration: https://www.instagram.com/cfdbyhand/ . This is an
independently authored reconstruction, not the original workbook.

The CSV files contain x_m,y_m,phi,clamped_square. All figures use original
computed fields, not copied social-media images. manifest.json contains
SHA-256 hashes for public release files. Package hashes are in
download-checksums.json. Hashes establish identity, not scientific validity.
''')

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def archive(destination,files):
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for source,name in files:
            info=zipfile.ZipInfo(name,(2026,10,24,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,source.read_bytes())

sources=sorted(p for p in (OUT/'paper-sources').rglob('*') if p.is_file() and p.suffix in {'.tex','.png'})
archive(OUT/'paper-sources.zip',[(p,p.relative_to(OUT/'paper-sources').as_posix()) for p in sources])
names=['Square_Body_Transport.xlsx','paper.pdf','solver.mjs','worker.mjs','verify_accuracy.py','requirements.txt','README.md',
       'accuracy-results.json','excel-verification.json','browser-solver-checks.json','workbook-reference.json',
       'baseline.csv','faster.csv','diffusion.csv','uniform.csv','examples.png']
files=[OUT/n for n in names]+sources
for file in files:
    if not file.is_file():raise RuntimeError(f'Missing public artifact: {file.name}')
    if file.suffix in {'.json','.py','.mjs','.tex','.md','.txt'}:
        content=file.read_text(encoding='utf-8')
        for forbidden in ['C:\\Users\\','C:/Users/','host.docker.internal','AEGIS_LOCAL_TOKEN']:
            if forbidden in content:raise RuntimeError(f'Private path or token label in public artifact: {file.name}')
manifest={'release':'square-body-transport-v1','date':'2026-10-24','files':{p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':digest(p)} for p in files}}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
archive(OUT/'reproducibility.zip',[(p,p.relative_to(OUT).as_posix()) for p in files]+[(OUT/'manifest.json','manifest.json')])
(OUT/'download-checksums.json').write_text(json.dumps({n:{'bytes':(OUT/n).stat().st_size,'sha256':digest(OUT/n)} for n in ['paper-sources.zip','reproducibility.zip']},indent=2))
print(json.dumps({'files':len(files),'paper_bytes':(OUT/'paper.pdf').stat().st_size,'workbook_sha256':digest(OUT/'Square_Body_Transport.xlsx'),'packages':json.loads((OUT/'download-checksums.json').read_text())},indent=2))
