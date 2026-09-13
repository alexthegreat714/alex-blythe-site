"""Package all attempts and freeze predictions without reading the reference.

This implements only the declared arithmetic and archive provenance; it does
not change the preregistered model, averaging window or numerical thresholds.
"""
import argparse,json,hashlib,zipfile,subprocess,re
from pathlib import Path
from protocol import Challenge,sha,encode

def freeze(root,out):
    ch=Challenge(root);ch.require('SOLVE');ch.intact();root=ch.root;out=Path(out)
    progress=json.loads((out/'progress.json').read_text())
    if progress['completed']!=54 or progress['running']:raise ValueError('Sweep is not finished')
    c=ch.load('preregistration.json');inputs=ch.load('input.json')
    expected={station+'-'+level for station in inputs['stations'] for level in ('coarse','medium','fine')}
    if set(progress['results'])!=expected:raise ValueError('All registered station/grid attempts are required')
    results={key:json.loads((out/key/'analysis.json').read_text()) for key in expected}
    if any(not r.get('complete_prediction') for r in results.values()):
        raise ValueError('Incomplete case curves: do not invent missing values or unseal reference')
    for key,r in results.items():
        station,level=key.rsplit('-',1)
        if r.get('station')!=station or r.get('level')!=level:raise ValueError('Mislabelled case '+key)
        if r.get('angle_deg')!=inputs['flow_conditions']['angle_of_attack_degrees'][station]:raise ValueError('Operating point mismatch '+key)
        receipt=json.loads((out/key/'receipt.json').read_text())
        if receipt['driver_sha256']!=c['execution_code']['case_driver.py']:raise ValueError('Generator changed '+key)
        if receipt['image']!=c['solver']['image']:raise ValueError('Solver image changed '+key)
    dest=root/'evidence';dest.mkdir(exist_ok=False);archives=dest/'cases';archives.mkdir()
    allfiles=[];index=[];geometries=[];meshes=[];grids=[]
    residuals=[];conservation=[];walls=[];runtimes=[]
    for station in inputs['stations']:
        series=[]
        for level in ('coarse','medium','fine'):
            key=station+'-'+level;directory=out/key;result=results[key]
            archive=archives/(key+'.zip')
            inside=[]
            with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
                for p in sorted(directory.rglob('*')):
                    if not p.is_file():continue
                    if p.name in ['reference.csv','challenge01.key','.env']:raise ValueError('Forbidden artifact')
                    rel=p.relative_to(directory).as_posix()
                    data=p.read_bytes();h=sha(data)
                    z.writestr(rel,data)
                    inside.append({'path':rel,'size':len(data),'sha256':h})
                z.writestr('archive-manifest.json',encode({'case':key,'files':inside}))
            if archive.stat().st_size>95*1024*1024:raise ValueError('Bundle exceeds public file limit')
            row={'case':key,'path':archive.relative_to(root).as_posix(),'sha256':sha(archive.read_bytes()),'size':archive.stat().st_size,'file_count':len(inside),'station':station,'level':level,'numerical_status':result['status']}
            index.append(row);allfiles.extend({'case':key,**r} for r in inside)
            geo=json.loads((directory/'case/geometry.json').read_text());geometries.append({'case':key,**geo})
            mesh_log=(directory/'mesh.log').read_text()
            failed=re.search(r'Failed (\d+) mesh checks',mesh_log)
            aspect=re.search(r'Max aspect ratio: ([0-9.eE+-]+)',mesh_log)
            meshes.append({'case':key,'raw_checkMesh':mesh_log,'failed_check_count':int(failed[1]) if failed else 0,'max_aspect_ratio':float(aspect[1]) if aspect else None,'mesh_generator_archive':row['path']})
            residuals.append({'case':key,'initial':result['initial_residuals_final_iteration'],'final':result['linear_residuals_final'],'gates':{k:v for k,v in result['gates'].items() if 'residual' in k}})
            conservation.append({'case':key,'flux_imbalance_fraction':result['boundary_flux_imbalance_fraction'],'solver_continuity_final':result['continuity_final'],'gates':{k:v for k,v in result['gates'].items() if k in ['boundary_conservation','continuity']}})
            walls.append({'case':key,'yplus':json.loads((directory/'yplus-wall.json').read_text()),'p95':result['yplus_p95'],'max':result['yplus_max'],'gate':result['gates']['wall_yplus']})
            runtimes.append({'case':key,**json.loads((directory/'receipt.json').read_text())})
            series.append(result)
        med,fine=series[1:]
        delta={q:abs(fine['mean_iterations_1500_2000'][q]-med['mean_iterations_1500_2000'][q]) for q in ['CL','CD']}
        grids.append({'station':station,'angle_deg':fine['angle_deg'],'levels':series,'medium_fine_absolute_change':delta,'pass':delta['CL']<=.02 and delta['CD']<=.002})
    requirements={'inputs':'../input.json','preregistration':'../preregistration.json','prediction':'Nominal two-dimensional steady-RANS CL/CD polar; all18 operating points retained.','exposure':'Source-exposed supervisor; execution reference-withheld, not fully blinded setup.'}
    first={'speed_m_s':.15*(1.4*287.05*288.15)**.5,'chord_m':.601,'nu_m2_s':.15*(1.4*287.05*288.15)**.5*.601/5950000,'normalization':'CL/CD from forces divided by 0.5*rhoInf*U^2*chord*empty_span; rhoInf=1 for kinematic pressure. No pressure or lift target used.'}
    files={'requirements.json':requirements,'first-principles.json':first,'geometry.json':geometries,'mesh-diagnostics.json':meshes,'residuals.json':residuals,'conservation.json':conservation,'wall-diagnostics.json':walls,'grid-study.json':grids,'runtimes.json':runtimes,'extracted-values.json':results,'run-index.json':{'cases':index,'files_retained':len(allfiles),'compressed_bytes':sum(r['size'] for r in index)},'file-manifest.json':allfiles}
    applicable=lambda r:{k:v for k,v in r['gates'].items() if k!='wall_yplus' or r['level']=='fine'}
    files['numerical-summary.json']={
        'case_count':len(results),'cases_passing_applicable_individual_gates':sum(all(applicable(r).values()) for r in results.values()),
        'failed_case_counts_by_gate':{gate:sum(not applicable(r).get(gate,True) for r in results.values()) for gate in sorted({k for r in results.values() for k in applicable(r)})},
        'wall_gate_applicability':'Fine grid only; coarse/medium wall values remain diagnostics.',
        'mesh_cases_with_failed_checkMesh_checks':sum(m['failed_check_count']>0 for m in meshes),
        'mesh_policy':'Aspect-ratio/determinant check failures retained under the declared thin-grid policy. Not presented as a clean mesh-quality PASS.',
        'grid_pairs_passing':sum(g['pass'] for g in grids),'grid_pairs_total':len(grids),
        'transition_model_iteration_warning_count':sum((out/key/'solver.log').read_text().count('Number of lambda iterations exceeds maxLambdaIter') for key in results)
    }
    for name,data in files.items():(dest/name).write_bytes(encode(data))
    # GPL license accompanies the copied Foundation geometry/template in bundles.
    license_data=subprocess.check_output(['docker','run','--rm','--network','none','--read-only','--entrypoint','/bin/cat',c['solver']['image'],'/opt/openfoam10/COPYING'])
    (dest/'OPENFOAM-COPYING.txt').write_bytes(license_data)
    mapping={'requirements':'requirements.json','first_principles':'first-principles.json','geometry':'geometry.json','topology':'mesh-diagnostics.json','mesh':'run-index.json','mesh_diagnostics':'mesh-diagnostics.json','deck':'run-index.json','runtime':'runtimes.json','solver_log':'run-index.json','residuals':'residuals.json','conservation':'conservation.json','wall_diagnostics':'wall-diagnostics.json','grid_study':'grid-study.json','extracted_values':'extracted-values.json'}
    evidence={role:{'path':'evidence/'+name,'sha256':sha((dest/name).read_bytes())} for role,name in mapping.items()}
    for row in index:evidence['case_'+row['case']]={'path':row['path'],'sha256':row['sha256']}
    evidence['internal_file_manifest']={'path':'evidence/file-manifest.json','sha256':sha((dest/'file-manifest.json').read_bytes())}
    evidence['openfoam_license']={'path':'evidence/OPENFOAM-COPYING.txt','sha256':sha(license_data)}
    evidence['numerical_summary']={'path':'evidence/numerical-summary.json','sha256':sha((dest/'numerical-summary.json').read_bytes())}
    values=[{'station':s,'quantity':q,'value':results[s+'-fine']['mean_iterations_1500_2000'][q]} for s in inputs['stations'] for q in ['CL','CD']]
    # The wall requirement is fine-grid only. Other numerical gates apply to
    # every retained level, as the predeclared full-grid comparison requires.
    numerical=all(all(v for k,v in r['gates'].items() if k!='wall_yplus' or r['level']=='fine') for r in results.values()) and all(g['pass'] for g in grids)
    pred={'values':values,'numerical_status':'PASS' if numerical else 'FAIL','engineering_disposition':'Complete nominal steady-RANS prediction retained. '+('All declared numerical gates pass.' if numerical else 'Numerical acceptance failed; no design-ready or validated prediction is claimed, irrespective of later coefficient agreement.')+' Setup supervisor was source-exposed; solver execution was reference-withheld. No physical-time average, exact grit equivalence, or universal validation is claimed.','evidence_manifest':evidence}
    ch.freeze_prediction(pred)
    print(json.dumps({'stage':ch.state()['stage'],'numerical_status':pred['numerical_status'],'bundles':len(index),'bytes':sum(r['size'] for r in index)}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('output',type=Path);a=p.parse_args();freeze(a.package,a.output)
