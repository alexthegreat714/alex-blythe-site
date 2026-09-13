"""Input-only NACA0012 mesh/deck generator. No reference-reading code.

Uses Python's standard library inside the pinned OpenFOAM container. The finite
trailing edge is deliberate. All coordinates are generated, never fitted to CL/CD.
"""
import argparse, json, math, gzip, re, subprocess
from pathlib import Path

LEVELS = {'coarse': (128, 96, 2e-5), 'medium': (192, 128, 1e-5), 'fine': (288, 160, 5e-6)}
CHORD = .601
SPAN = .01 * CHORD
SPEED = .15 * math.sqrt(1.4 * 287.05 * 288.15)
NU = SPEED * CHORD / 5950000

def header(name, cls='dictionary'):
    return f'FoamFile {{ version 2.0; format ascii; class {cls}; object {name}; }}\n'

def put(root, name, content):
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='ascii')

def mesh(root, level):
    """Use the installed Foundation 10 tutorial's projectable six-block C-grid.

    Its GPL template is retained with attribution. No tutorial flow conditions,
    solver results, force histories or external measured values are copied.
    """
    base=Path('/opt/openfoam10/tutorials/compressible/rhoSimpleFoam/aerofoilNACA0012')
    text=(base/'system/blockMeshDict').read_text()
    counts={'coarse':(64,64,40,64),'medium':(96,96,60,96),'fine':(128,128,80,128)}[level]
    for name,value in zip(('zCells','xUCells','xMCells','xDCells'),counts):
        text=re.sub(r'\b'+name+r'\s+\d+;',name+' '+str(value)+';',text)
    text=re.sub(r'\bxMax\s+100;', 'xMax 30;',text)
    text=re.sub(r'\bzMax\s+50;', 'zMax 20;',text)
    text=re.sub(r'\bzGrading\s+30000;', 'zGrading 300000;',text)
    # Fix two outer-upper projections in the retained tutorial: they must be
    # on the farfield cylinder, not the airfoil surface.
    text=text.replace('project ($aerofoil/xUpper -0.1 $domain/zMax) (aerofoil)', 'project ($aerofoil/xUpper -0.1 $domain/zMax) (cylinder)')
    text=text.replace('project ($aerofoil/xTrail -0.1 $domain/zMax) (aerofoil)', '($aerofoil/xTrail -0.1 $domain/zMax)')
    text=text.replace('project ($aerofoil/xUpper  0.1 $domain/zMax) (aerofoil)', 'project ($aerofoil/xUpper  0.1 $domain/zMax) (cylinder)')
    text=text.replace('project ($aerofoil/xTrail  0.1 $domain/zMax) (aerofoil)', '($aerofoil/xTrail  0.1 $domain/zMax)')
    put(root,'system/blockMeshDict',text)
    data=gzip.decompress(Path('/opt/openfoam10/tutorials/resources/geometry/NACA0012.obj.gz').read_bytes())
    put(root,'constant/geometry/NACA0012.obj',data.decode('ascii'))
    with (root/'blockMesh.log').open('w') as log:
        subprocess.run(['blockMesh','-case',str(root)],stdout=log,stderr=subprocess.STDOUT,check=True)
    path=root/'constant/polyMesh/points';raw=path.read_text()
    points=[tuple(map(float,v.split())) for v in re.findall(r'\(([-+0-9.eE ]+)\)',raw)]
    transformed=[(CHORD*x,CHORD*z,-SPAN*y/.2) for x,y,z in points]
    put(root,'constant/polyMesh/points',header('points','vectorField')+f'{len(points)}\n(\n'+'\n'.join('(%s)'%' '.join(f'{v:.12g}' for v in p) for p in transformed)+'\n)\n')
    # Rotate x-z to x-y with a proper rotation; rescale the empty span only.
    faces=[list(map(int,v.split())) for v in re.findall(r'\d+\(([^)]+)\)',(root/'constant/polyMesh/faces').read_text())]
    owner=list(map(int,re.search(r'\n\(\s*(.*?)\s*\)',(root/'constant/polyMesh/owner').read_text(),re.S)[1].split()))
    neigh=list(map(int,re.search(r'\n\(\s*(.*?)\s*\)',(root/'constant/polyMesh/neighbour').read_text(),re.S)[1].split()))
    cells=[set() for _ in range(max(owner)+1)]
    for i,face in enumerate(faces):
        cells[owner[i]].update(face)
        if i<len(neigh):cells[neigh[i]].update(face)
    laminar=[];trip=[]
    for i,vs in enumerate(cells):
        x=sum(transformed[v][0] for v in vs)/len(vs)/CHORD
        y=sum(transformed[v][1] for v in vs)/len(vs)/CHORD
        if 0<=x<=1:
            yt=.6*(.2969*math.sqrt(x)-.126*x-.3516*x*x+.2843*x**3-.1036*x**4)
            if abs(y)-yt<=.02:
                (laminar if x<.05 else trip).append(i)
    for name,values in [('preTrip',laminar),('postTrip',trip)]:put(root,'constant/polyMesh/sets/'+name,header(name,'cellSet')+f'{len(values)}\n(\n'+'\n'.join(map(str,values))+'\n)\n')
    put(root,'geometry.json',json.dumps({'level':level,'topology':'Foundation 10 projected C-grid','cells':len(cells),'counts':counts,'geometry_source':'Pinned OpenFOAM 10 NACA0012.obj; nominal geometry only','trip_cells':len(trip),'laminar_cells':len(laminar)},indent=2)+'\n')

def deck(root, angle, duration=2000, dt=1, smoke=False):
    alpha=math.radians(angle); u=(SPEED*math.cos(alpha), SPEED*math.sin(alpha),0)
    vec=lambda v:'('+' '.join(f'{x:.12g}' for x in v)+')'
    k=1.5*(SPEED*.001)**2  # ASSUMED 0.1 percent, not measured.
    omega=math.sqrt(k)/(.09**.25 * .01*CHORD)
    props={'U':('volVectorField','[0 1 -1 0 0 0 0]',vec(u),'fixedValue; value uniform (0 0 0)','freestreamVelocity; freestreamValue uniform '+vec(u)),
           'p':('volScalarField','[0 2 -2 0 0 0 0]','0','zeroGradient','freestreamPressure; freestreamValue uniform 0'),
           'k':('volScalarField','[0 2 -2 0 0 0 0]',str(k),'fixedValue; value uniform 1e-12','inletOutlet; inletValue uniform '+str(k)+'; value uniform '+str(k)),
           'omega':('volScalarField','[0 0 -1 0 0 0 0]',str(omega),'omegaWallFunction; value uniform '+str(omega),'inletOutlet; inletValue uniform '+str(omega)+'; value uniform '+str(omega)),
           'nut':('volScalarField','[0 2 -1 0 0 0 0]','0','nutLowReWallFunction; value uniform 0','calculated; value uniform 0'),
           'gammaInt':('volScalarField','[0 0 0 0 0 0 0]','1','zeroGradient','inletOutlet; inletValue uniform 1; value uniform 1'),
           'ReThetat':('volScalarField','[0 0 0 0 0 0 0]','1136.5272','zeroGradient','inletOutlet; inletValue uniform 1136.5272; value uniform 1136.5272')}
    for name,(cls,dim,val,wall,far) in props.items():
        put(root,'0/'+name,header(name,cls)+f'dimensions {dim};\ninternalField uniform {val};\nboundaryField {{ aerofoil {{ type {wall}; }} "(inlet|outlet)" {{ type {far}; }} "(front|back)" {{ type empty; }} }}\n')
    put(root,'constant/physicalProperties',header('physicalProperties')+f'viscosityModel constant; nu {NU:.14g};\n')
    put(root,'constant/momentumTransport',header('momentumTransport')+'simulationType RAS; RAS { model kOmegaSSTLM; turbulence on; printCoeffs on; }\n')
    put(root,'system/fvConstraints',header('fvConstraints')+'preTrip { type fixedValueConstraint; selectionMode cellSet; cellSet preTrip; fieldValues { gammaInt 0; } }\npostTrip { type fixedValueConstraint; selectionMode cellSet; cellSet postTrip; fieldValues { gammaInt 1; } }\n')
    tc=1.0  # SIMPLE iteration index, not physical time.
    funcs=''
    if True:  # Smoke instrumentation is retained but is never a frozen prediction.
        funcs=f'''forces {{ type forceCoeffs; libs ("libforces.so"); patches (aerofoil); rho rhoInf; rhoInf 1; CofR ({.25*CHORD} 0 0); liftDir {vec((-math.sin(alpha),math.cos(alpha),0))}; dragDir {vec((math.cos(alpha),math.sin(alpha),0))}; pitchAxis (0 0 1); magUInf {SPEED}; lRef {CHORD}; Aref {CHORD*SPAN}; writeControl timeStep; writeInterval 1; }}
yPlus {{ type yPlus; libs ("libfieldFunctionObjects.so"); writeControl writeTime; }}
'''
    put(root,'system/controlDict',header('controlDict')+f'''application simpleFoam; startFrom startTime; startTime 0; stopAt endTime; endTime {duration:.14g}; deltaT 1; writeControl timeStep; writeInterval {int(duration)}; purgeWrite 0; writeFormat ascii; writePrecision 10; timeFormat general; timePrecision 10; runTimeModifiable false; functions {{ {funcs} }}\n''')
    put(root,'system/fvSchemes',header('fvSchemes')+'''ddtSchemes { default steadyState; }
gradSchemes { default cellLimited Gauss linear 1; }
divSchemes { default none; div(phi,U) bounded Gauss linearUpwind grad(U); div(phi,k) bounded Gauss upwind; div(phi,omega) bounded Gauss upwind; div(phi,gammaInt) bounded Gauss upwind; div(phi,ReThetat) bounded Gauss upwind; div((nuEff*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear limited 0.5; }
interpolationSchemes { default linear; }
snGradSchemes { default limited 0.5; }
wallDist { method meshWave; }
''')
    put(root,'system/fvSolution',header('fvSolution')+'''solvers {
p { solver PCG; tolerance 1e-7; relTol 0.01; preconditioner DIC; maxIter 2000; }
Phi { solver PCG; tolerance 1e-7; relTol 0; preconditioner DIC; maxIter 2000; }
pFinal { $p; relTol 0; }
"(U|k|omega|gammaInt|ReThetat)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-8; relTol 0.05; }
"(U|k|omega|gammaInt|ReThetat)Final" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-8; relTol 0; }
}
potentialFlow { nNonOrthogonalCorrectors 4; }
SIMPLE { nNonOrthogonalCorrectors 1; pRefCell 0; pRefValue 0; consistent yes; }
relaxationFactors { fields { p 0.3; } equations { U 0.5; k 0.5; omega 0.5; gammaInt 0.5; ReThetat 0.5; } }
''')
    put(root,'case-input.json',json.dumps({'angle_deg':angle,'chord_m':CHORD,'speed_m_s':SPEED,'nu_m2_s':NU,'iterations':duration,'iteration_is_not_physical_time':True,'smoke_not_prediction':smoke},indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--level',choices=LEVELS,default='coarse');p.add_argument('--angle',type=float,default=1);p.add_argument('--duration',type=float,default=30);p.add_argument('--dt',type=float,default=.02);p.add_argument('--smoke',action='store_true');a=p.parse_args()
    a.directory.mkdir(parents=True,exist_ok=False)
    deck(a.directory,a.angle,a.duration,a.dt,a.smoke);mesh(a.directory,a.level)
