"""Deterministic input-only extraction. Missing samples stay missing, never zero."""
import json, math, re
from pathlib import Path
from case_driver import CHORD,SPEED

def array(text, key='internalField'):
    m=re.search(r'\b'+re.escape(key)+r'\s+nonuniform\s+List<(scalar|vector)>\s+(\d+)\s*\((.*?)\)\s*;',text,re.S)
    if m:
        raw=m[3]
        values=[list(map(float,q.split())) for q in re.findall(r'\(([^)]+)\)',raw)] if m[1]=='vector' else list(map(float,raw.split()))
        if len(values)!=int(m[2]):raise ValueError('Field length mismatch')
        return values
    m=re.search(r'\b'+re.escape(key)+r'\s+uniform\s+([^;]+);',text)
    if m:
        val=m[1].strip()
        return [list(map(float,val.strip('()').split()))] if val.startswith('(') else [float(val)]
    raise ValueError('Missing field '+key)

def patch_values(text,name):
    m=re.search(r'\b'+re.escape(name)+r'\s*\{(.*?)\}',text,re.S)
    if not m:raise ValueError('Missing patch '+name)
    return array(m[1],'value')

def mean_interval(rows, column, start, end):
    if len(rows)<2 or rows[0][0]>start+1e-10 or rows[-1][0]<end-1e-8: return None
    integral=0.;span=0.
    for a,b in zip(rows,rows[1:]):
        lo=max(a[0],start);hi=min(b[0],end)
        if hi<=lo:continue
        dt=b[0]-a[0]
        if dt<=0:raise ValueError('Non-increasing coefficient times')
        va=a[column]+(b[column]-a[column])*(lo-a[0])/dt
        vb=a[column]+(b[column]-a[column])*(hi-a[0])/dt
        integral+=(va+vb)/2*(hi-lo);span+=hi-lo
    return integral/span if abs(span-(end-start))<1e-7 else None

def analyze(out, station=None):
    out=Path(out);case=out/'case';log=(out/'solver.log').read_text(errors='replace') if (out/'solver.log').exists() else ''
    config=json.loads((case/'case-input.json').read_text())
    files=list((case/'postProcessing/forces').glob('*/forceCoeffs.dat'))
    rows=[]
    for p in files:
        for line in p.read_text().splitlines():
            if line.strip() and not line.startswith('#'):
                row=list(map(float,line.split()))
                if not all(math.isfinite(x) for x in row):raise ValueError('Nonfinite coefficient')
                rows.append(row)
    rows.sort()
    means={q:mean_interval(rows,col,1500,2000) for q,col in [('CL',3),('CD',2)]}
    earlier={q:mean_interval(rows,col,1000,1500) for q,col in [('CL',3),('CD',2)]}
    complete=bool(rows) and rows[-1][0]>=2000 and '\nEnd\n' in log
    fields=sorted([p for p in case.iterdir() if p.is_dir() and re.fullmatch(r'[0-9.eE+-]+',p.name)],key=lambda p:float(p.name))
    finite=True;yplus=[];flux=None;trip_check=False
    errors=[]
    latest=fields[-1] if fields else None
    if latest:
        try:
            for field in ('U','p','k','omega','gammaInt','ReThetat','nut'):
                field_text=(latest/field).read_text()
                if re.search(r'(?<![A-Za-z])(nan|[-+]?inf)(?![A-Za-z])',field_text,re.I):finite=False
                values=array(field_text)
                nums=[n for v in values for n in (v if isinstance(v,list) else [v])]
                finite=finite and all(math.isfinite(v) for v in nums)
            yplus=patch_values((latest/'yPlus').read_text(),'aerofoil')
            raw=(latest/'phi').read_text()
            fluxes=patch_values(raw,'inlet')+patch_values(raw,'outlet')+patch_values(raw,'aerofoil')
            flux=abs(sum(fluxes))/sum(map(abs,fluxes)) if sum(map(abs,fluxes))>0 else None
            gamma=array((latest/'gammaInt').read_text())
            checks=[]
            for name,target in [('preTrip',0),('postTrip',1)]:
                s=(case/'constant/polyMesh/sets'/name).read_text()
                indices=list(map(int,re.search(r'\n\(\s*(.*?)\s*\)',s,re.S)[1].split()))
                checks.append(bool(indices) and all(abs(gamma[i if len(gamma)>1 else 0]-target)<1e-9 for i in indices))
            trip_check=all(checks)
        except (ValueError,IndexError,OSError) as e:errors.append(str(e));finite=False
    last_time=log.rsplit('\nTime =',1)[-1]
    residuals={};initials={}
    for field,initial,final in re.findall(r'Solving for (\w+), Initial residual = ([^,]+), Final residual = ([^,]+)',last_time):
        residuals[field]=float(final)
        initials[field]=float(initial)
    cont=re.findall(r'time step continuity errors : sum local = ([^,]+), global = ([^,]+), cumulative = ([\deE.+-]+)',last_time)
    continuity=list(map(float,cont[-1])) if cont else None
    yplus=sorted(yplus)
    y95=yplus[min(len(yplus)-1,math.ceil(.95*len(yplus))-1)] if yplus else None
    gates={
        'duration_complete':complete,
        'finite_fields':finite and bool(latest) and float(latest.name)>0,
        'trip_constraints':trip_check,
        'stationary_CL':means['CL'] is not None and earlier['CL'] is not None and abs(means['CL']-earlier['CL'])<=.01,
        'stationary_CD':means['CD'] is not None and earlier['CD'] is not None and abs(means['CD']-earlier['CD'])<=.001,
        'linear_residuals':all(k in residuals and math.isfinite(residuals[k]) and residuals[k]<=1e-6 for k in ('p','Ux','Uy','k','omega','gammaInt','ReThetat')),
        'initial_residuals':all(k in initials and math.isfinite(initials[k]) and initials[k]<=1e-4 for k in ('p','Ux','Uy','k','omega','gammaInt','ReThetat')),
        'continuity':continuity is not None and all(math.isfinite(x) for x in continuity) and abs(continuity[1])<=1e-6 and continuity[0]<=1e-5,
        'boundary_conservation':flux is not None and flux<=.001,
        'wall_yplus':y95 is not None and y95<=2 and max(yplus)<=5
    }
    tail=[r for r in rows if 1500<=r[0]<=2000]
    ranges={q:max(r[col] for r in tail)-min(r[col] for r in tail) if tail else None for q,col in [('CL',3),('CD',2)]}
    gates['nonoscillating_CL']=complete and ranges['CL'] is not None and ranges['CL']<=.02
    gates['nonoscillating_CD']=complete and ranges['CD'] is not None and ranges['CD']<=.002
    result={'station':station,'angle_deg':config['angle_deg'],'level':json.loads((case/'geometry.json').read_text())['level'],'complete_prediction':all(v is not None for v in means.values()),'mean_iterations_1500_2000':means,'mean_iterations_1000_1500':earlier,'last_iteration':rows[-1][0] if rows else None,'iteration_is_not_physical_time':True,'linear_residuals_final':residuals,'continuity_final':continuity,'boundary_flux_imbalance_fraction':flux,'yplus_p95':y95,'yplus_max':max(yplus) if yplus else None,'gates':gates,'status':'PASS' if all(gates.values()) else 'FAIL','extraction_errors':errors}
    result['initial_residuals_final_iteration']=initials;result['coefficient_range_last500']=ranges
    (out/'analysis.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (out/'yplus-wall.json').write_text(json.dumps(yplus,allow_nan=False)+'\n')
    return result

if __name__=='__main__':
    import sys
    print(json.dumps(analyze(Path(sys.argv[1])),indent=2))
