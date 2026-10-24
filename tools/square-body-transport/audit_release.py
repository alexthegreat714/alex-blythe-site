"""Audit the new static page and its release only, without browsing automation."""
import hashlib
import json
import zipfile
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlparse
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/'dist'
BASE=DIST/'demos'/'aero'/'square-body-transport-v1'
PAGE=DIST/'software'/'aero'/'square-body-transport'/'index.html'
class Page(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.inputs=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for k in ['href','src']:
            if a.get(k,'').startswith('/'):self.links.append(a[k])
        if tag=='input' and a.get('type')=='number':self.inputs.append(a)
p=Page();p.feed(PAGE.read_text(encoding='utf-8'))
assert len(p.ids)==len(set(p.ids)),'Duplicate page IDs'
for link in p.links:
    target=DIST/unquote(urlparse(link).path).lstrip('/')
    assert target.is_file() or (target/'index.html').is_file(),link
for a in p.inputs:
    value=Decimal(a['value'])
    if 'min' in a:assert value>=Decimal(a['min']),a['name']
    if 'max' in a:assert value<=Decimal(a['max']),a['name']
    if a.get('step','1')!='any':
        step=Decimal(a.get('step','1'));start=Decimal(a.get('min','0'))
        assert (value-start)%step==0,a['name']
manifest=json.loads((BASE/'manifest.json').read_text())
for name,m in manifest['files'].items():
    content=(BASE/name).read_bytes();assert len(content)==m['bytes'];assert hashlib.sha256(content).hexdigest()==m['sha256'],name
with zipfile.ZipFile(BASE/'reproducibility.zip') as archive:
    assert archive.testzip() is None
    for name,m in manifest['files'].items():assert hashlib.sha256(archive.read(name)).hexdigest()==m['sha256'],name
with zipfile.ZipFile(BASE/'paper-sources.zip') as archive:
    assert archive.testzip() is None
    assert 'main.tex' in archive.namelist() and 'figures/examples.png' in archive.namelist()
pdf=PdfReader(BASE/'paper.pdf');assert len(pdf.pages)==5
assert all(len(page.extract_text())>900 for page in pdf.pages),'Orphan PDF page'
for name in ['accuracy-results.json','excel-verification.json','browser-solver-checks.json']:
    assert json.loads((BASE/name).read_text())['all_passed'],name
assert b'/software/aero/square-body-transport/' in (DIST/'software'/'aero'/'index.html').read_bytes()
assert b'/software/aero/square-body-transport/' in (DIST/'sitemap.xml').read_bytes()
print(json.dumps({'local_links':len(p.links),'valid_default_numeric_inputs':len(p.inputs),'hashed_files':len(manifest['files']),'pdf_pages':len(pdf.pages),'all_passed':True,'browser_ui_checked':False},indent=2))
