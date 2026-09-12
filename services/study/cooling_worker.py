"""Serial fixed-template cooling report job; shares the existing bounded queue."""
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile
from core import atomic_json,digest
from cooling import calculate

def execute_cooling(job,work):
    root=work/job.name;root.mkdir(exist_ok=True)
    def status(state,message,completed=0,**extra):atomic_json(job/'status.json',{'id':job.name,'kind':'cooling','state':state,'message':message,'completed':completed,'total':3,'updated_at':time.time(),**extra})
    try:
        status('running','Computing three analytical layouts and verification checks')
        result=calculate(json.loads((job/'input.json').read_text()),job.name)
        atomic_json(job/'result.json',result)
        status('running','Three layouts calculated; compiling charts and LaTeX paper',3)
        with (root/'log.paper').open('w') as log:
            child=subprocess.Popen(['python3',str(Path(__file__).with_name('cooling_paper.py')),str(job/'result.json'),str(root/'paper')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:
                if child.wait(timeout=90):raise RuntimeError('Cooling PDF failed; diagnostic log retained')
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,9);child.wait();raise TimeoutError('Cooling PDF exceeded 90 seconds')
        shutil.copyfile(root/'paper'/'paper.pdf',job/'paper.pdf')
        for name in ('cooling.py','cooling_paper.py'):shutil.copyfile(Path(__file__).with_name(name),root/name)
        rows=''.join('<tr>'+''.join('<td>'+html.escape(str(v[k]))+'</td>' for k in ('id','guard_wall_c','guard_pressure_pa','passes'))+'</tr>' for v in result['layouts'])
        (job/'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Aero cooling study</title><h1>Forced-convection cooling-channel screening</h1><p>'+html.escape(result['decision'])+'</p><table><tr><th>Layout</th><th>Guard wall C</th><th>Guard pressure Pa</th><th>Passes</th></tr>'+rows+'</table><p>'+html.escape(result['limits'])+'</p><p>Download the LaTeX PDF in Results for charts, derivation and verification.</p></html>',encoding='utf-8')
        manifest={}
        with zipfile.ZipFile(job/'evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
            paths=[(p,'cases/'+p.relative_to(root).as_posix()) for p in root.rglob('*') if p.is_file()]+[(job/n,n) for n in ('paper.pdf','result.json','report.html')]
            if sum(p.stat().st_size for p,_ in paths)>48*1024**2:raise RuntimeError('Evidence size limit')
            for p,name in paths:manifest[name]=digest(p);z.write(p,name)
            z.writestr('sha256.json',json.dumps(manifest,indent=2))
        status('complete',result['decision'],3,checks_passed=result['checks_passed'],**{k+'_sha256':digest(job/n) for k,n in [('paper','paper.pdf'),('result','result.json'),('report','report.html'),('evidence','evidence.zip')]})
    except Exception as exc:
        with zipfile.ZipFile(job/'failure.zip','w',zipfile.ZIP_DEFLATED) as z:
            for p in root.rglob('*.log'):z.write(p,p.relative_to(root))
            if (root/'log.paper').exists():z.write(root/'log.paper','log.paper')
        status('failed',str(exc)[:200])
    finally:shutil.rmtree(root,ignore_errors=True)
