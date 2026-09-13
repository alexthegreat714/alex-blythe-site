"""Index committed, frozen evidence without changing any original artifact."""
import hashlib, io, json, subprocess, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='public/demos/aero/'
seen={}
def raw(path):
    data=subprocess.check_output(['git','show','HEAD:'+BASE+path],cwd=ROOT)
    seen['/demos/aero/'+path]={'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),'classification':'retained','stage':'evidence-index'}
    return data
def read(path):return json.loads(raw(path))
def verify(path,files):
    return [name for name,h in files.items() if hashlib.sha256(raw(path+'/'+name)).hexdigest()!=h]
def main():
    v=read('verification-bench-v1/summary.json');vm=read('verification-bench-v1/manifest.json')
    issues=verify('verification-bench-v1',vm['files'])
    if issues:raise ValueError('Frozen verification integrity failure '+str(issues))
    channel=read('channel-study-v1/changed-inputs-result.json');thermal=read('cooling-study-v1/result.json')
    paperinfo={}
    for family in ['channel-study-v1','cooling-study-v1']:
        m=read(family+'/research-paper-manifest.json')
        if verify(family,{'research-paper.pdf':m['paper_sha256'],'research-paper-sources.zip':m['source_bundle_sha256']}):raise ValueError('Paper integrity '+family)
        with zipfile.ZipFile(io.BytesIO(raw(family+'/research-paper-sources.zip'))) as z:
            hashes=json.loads(z.read('sha256.json'))
            if len(hashes)!=m['hashed_artifacts']:raise ValueError('Paper artifact count '+family)
            for name,h in hashes.items():
                if hashlib.sha256(z.read(name)).hexdigest()!=h:raise ValueError('Paper archive integrity '+family+'/'+name)
        paperinfo[family]=m
    families=['bracket','tube','tube3d','port','thermal-free','thermal-fixed','thermal-gradient'];fea=[];fea_issues=[]
    for name in families:
        r=read('fea-v1/'+name+'/result.json');m=read('fea-v1/'+name+'/manifest.json');e=r['evidence']
        bad=verify('fea-v1/'+name,m['artifacts']);fea_issues.extend(name+'/'+f for f in bad)
        fea.append({'case':name,'solves':len(r['levels']),'numerical':e['numerical_acceptability'],'requirements':e['requirement_satisfaction'],'design':e['design_readiness'],'url':'/demos/aero/fea-v1/'+name+'/result.json','manifest':'/demos/aero/fea-v1/'+name+'/manifest.json'})
    if sum(x['solves'] for x in fea)!=21:raise ValueError('Structural count changed; review copy')
    data={'schema':'aero.evidence.index.v1','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'verification':v,'channel':{'conditions':channel['brief']['inputs'],'solves':sum(len(x['levels']) for x in channel['variants']),'selected_gap_mm':channel['selected_gap_mm'],'checks_passed':channel['checks_passed'],'variants':[ {k:x[k] for k in ['gap_mm','pressure_drop_pa','mesh_change_pct','checks_passed','meets_budget']} for x in channel['variants']],'paper_artifacts':paperinfo['channel-study-v1']['hashed_artifacts']},'thermal':{'inputs':thermal['inputs'],'selected_layout':thermal['selected_layout'],'energy_relative_error':thermal['energy_relative_error'],'radial_final_error_pct':thermal['radial_verification'][-1]['relative_error_pct'],'layouts':len(thermal['layouts']),'paper_artifacts':paperinfo['cooling-study-v1']['hashed_artifacts']},'structural':{'solves':sum(x['solves'] for x in fea),'cases':fea,'manifest_mismatches':fea_issues},'artifacts':seen}
    out=ROOT/'public/demos/aero/evidence-index-v1';out.mkdir(exist_ok=True)
    (out/'index.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'sources_audited':len(seen),'structural_solves':data['structural']['solves'],'structural_manifest_mismatches':fea_issues}))
if __name__=='__main__':main()
