"""Publish source preparation only. Never copies a run folder, key or reference."""
import hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/aero-blind-validation';OUT=ROOT/'public/demos/aero/blind-validation-01-preparation-v1'
def digest(b):return hashlib.sha256(b).hexdigest()
def write(name,data):(OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    OUT.mkdir(exist_ok=True)
    names=['README.md','selection.json','preregistration.draft.json','protocol.py','test_protocol.py','render_result.py','protocol-paper.tex']
    for name in ['README.md','selection.json','preregistration.draft.json']:shutil.copyfile(SRC/name,OUT/name)
    pdf=ROOT/'output/pdf/blind-validation-01/protocol-paper.pdf'
    if not pdf.exists():raise ValueError('Protocol paper must be compiled and inspected')
    shutil.copyfile(pdf,OUT/'protocol-paper.pdf')
    with zipfile.ZipFile(OUT/'preparation-sources.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n in names:z.write(SRC/n,n)
        z.write(pdf,'protocol-paper.pdf')
        hashes={n:digest((SRC/n).read_bytes()) for n in names};hashes['protocol-paper.pdf']=digest(pdf.read_bytes())
        z.writestr('manifest.json',json.dumps({'scope':'Preparation source release only; not a production run','files':hashes},indent=2))
    status={'schema':'aero.blind.public.status.v1','challenge':'Aero Blind Validation Challenge 01','status':'NOT_EVALUATED','release':'Preparation 0.1','scientific_result':None,'production_runs':0,'source_selection':'CANDIDATE_SELECTED_INPUT_CURATION_REQUIRED','phases':[{'label':label,'status':'NOT_OCCURRED'} for label in ['Input frozen','Criteria frozen','Solve','Prediction frozen','Reference unsealed','Automated comparison']],'scientific_hashes':{'input_package':None,'sealed_reference':None,'preregistration':None,'blind_prediction':None},'scientific_commits':{'preregistration':None,'prediction_freeze':None,'unseal_comparison':None},'tests':{'kind':'synthetic software tests, not scientific evidence','passed':13},'blockers':json.loads((SRC/'selection.json').read_text())['open_items'],'claim':'No completed blind run or external validation result exists. The planning task was exposed; it cannot act as the blind predictor.'}
    write('status.json',status)
    rows=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!='manifest.json':rows.append({'path':p.name,'size':p.stat().st_size,'sha256':digest(p.read_bytes()),'role':'protocol-report' if p.suffix=='.pdf' else 'preparation-artifact','generation_stage':'PREPARATION_ONLY','classification':'generated; no experimental source redistributed'})
    write('manifest.json',{'schema':'aero.artifacts.v1','scope':'These release hashes are not scientific preregistration or prediction hashes','files':rows})
    print(json.dumps({'artifacts':len(rows),'zip_files':len(hashes),'status':'NOT_EVALUATED'}))
if __name__=='__main__':main()
