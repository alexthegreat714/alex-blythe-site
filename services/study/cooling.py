"""Bounded water/circular-passage screening. Analytical, never a thermal CFD claim."""
import math
from core import digest

REVISION='forced-convection-screening-v1'
DEFAULTS={'heat_w':100,'flow_ml_s':1,'inlet_c':25,'wall_limit_c':72,'pressure_budget_pa':2000,'length_mm':500,'available_width_mm':12}
BOUNDS={'heat_w':(10,150),'flow_ml_s':(.5,2),'inlet_c':(15,35),'wall_limit_c':(40,85),'pressure_budget_pa':(100,10000),'length_mm':(300,800),'available_width_mm':(4,30)}
PROPERTIES={'rho':997,'cp':4180,'mu':.00089,'k':.607,'Nu':48/11}
LAYOUTS=[('A',4,1),('B',2,2),('C',1,4)]
SOURCES=[{'title':'NPTEL: internal forced convection, uniform wall heat flux and entrance lengths','url':'https://archive.nptel.ac.in/content/storage2/courses/112108149/pdf/M6/M6TeacherSlides.pdf'},
 {'title':'Fitzpatrick: Poiseuille flow','url':'https://farside.ph.utexas.edu/teaching/336L/Fluidhtml/node136.html'},
 {'title':'NIST Chemistry WebBook: fluid property reference service','url':'https://webbook.nist.gov/chemistry/fluid/'}]
LIMITS='Analytical, constant-property, single-phase water screening. Equal flow and heat split in straight circular passages; uniform heat flux around the whole wetted perimeter. Temperature means wetted inner wall, not an external component. No CAD import, solid conduction, contact resistance, manifold/entry/bend losses, experimental validation or thermal CFD. Pressure is straight-passage friction only. Safety factors are explicit scenarios, not confidence intervals.'

def validate(data):
    if not isinstance(data,dict) or set(data)!=set(BOUNDS):raise ValueError('All seven supported numeric inputs are required')
    if any(isinstance(data[k],bool) or not isinstance(data[k],(int,float)) or not math.isfinite(data[k]) or not lo<=data[k]<=hi for k,(lo,hi) in BOUNDS.items()):raise ValueError('Cooling input outside its supported range')
    return {k:float(data[k]) for k in BOUNDS}

def radial_verification(cells):
    # Conservative radial energy integration, wall T=0; weighted bulk temperature.
    # Dimensionless PDE: (s t')'/s=4(1-s^2). No use of Nu in this computation.
    ds=1/cells;s=[(i+.5)*ds for i in range(cells)]
    t=[0.0]*cells;t[-1]=-ds/2
    for i in range(cells-2,-1,-1):
        face=(i+1)*ds;t[i]=t[i+1]-(2*face-face**3)*ds
    weights=[2*(1-x*x)*x*ds for x in s]
    bulk=sum(a*b for a,b in zip(t,weights))/sum(weights)
    return {'radial_cells':cells,'nu':-2/bulk,'relative_error_pct':abs((-2/bulk)/(48/11)-1)*100}

def calculate(data,run_id='preview'):
    p=validate(data);rho,cp,mu,k,nu=(PROPERTIES[x] for x in ('rho','cp','mu','k','Nu'))
    flow=p['flow_ml_s']*1e-6;length=p['length_mm']/1000;heat=p['heat_w'];mdot=rho*flow
    rise=heat/(mdot*cp);out=p['inlet_c']+rise;out_guard=p['inlet_c']+rise*1.1/.9
    results=[]
    for name,count,diameter in LAYOUTS:
        d=diameter/1000;area=count*math.pi*d*length;velocity=flow/(count*math.pi*d*d/4)
        re=rho*velocity*d/mu;pr=cp*mu/k;h=nu*k/d;film=heat/(h*area)
        dp=128*mu*length*flow/(count*math.pi*d**4)
        dp_cross=(64/re)*(length/d)*rho*velocity**2/2
        guard_dp=dp*1.2*1.1/.98**4
        wall=out+film;guard_wall=out_guard+film*1.1/.8
        span=count*diameter+(count-1)*1.0 # One millimetre minimum ligament; no outer casing.
        thermal_entry=.05*re*pr*d;hydro_entry=.05*re*d
        gates={'laminar':re*1.1/(.8*.98)<1800,'outlet_developed':thermal_entry*1.1/.8<=length,
               'fits_width':span<=p['available_width_mm'],'single_phase_screen':guard_wall<90,
               'wall_budget':guard_wall<=p['wall_limit_c'],'friction_budget':guard_dp<=p['pressure_budget_pa']}
        results.append({'id':name,'channels':count,'diameter_mm':diameter,'span_mm':span,'re':re,'h_w_m2k':h,'area_m2':area,
           'bulk_outlet_c':out,'wall_c':wall,'guard_wall_c':guard_wall,'pressure_pa':dp,'guard_pressure_pa':guard_dp,
           'pump_w':dp*flow,'thermal_margin_k':p['wall_limit_c']-guard_wall,'pressure_margin_pa':p['pressure_budget_pa']-guard_dp,
           'thermal_entry_mm':thermal_entry*1000,'hydro_entry_mm':hydro_entry*1000,'gates':gates,'passes':all(gates.values()),
           'pressure_crosscheck_relative':abs(dp_cross/dp-1),
           'profile':{'x_mm':[length*1000*i/50 for i in range(51)],'bulk_c':[p['inlet_c']+rise*i/50 for i in range(51)],
                      'wall_c':[p['inlet_c']+rise*i/50+film for i in range(51)]}})
    passed=[v for v in results if v['passes']];chosen=min(passed,key=lambda v:v['pump_w']) if passed else None
    radial=[radial_verification(n) for n in (16,32,64,128)]
    energy_error=abs(mdot*cp*(out-p['inlet_c'])/heat-1)
    return {'id':run_id,'revision':REVISION,'source':'ANALYTICAL_SCREENING','inputs':p,'properties':PROPERTIES,'layouts':results,
       'selected_layout':chosen['id'] if chosen else None,'decision':f"Layout {chosen['id']} ({chosen['channels']} x {chosen['diameter_mm']} mm) has the lowest straight-passage pumping power among candidates passing the stated screening gates." if chosen else 'No layout passes all screening gates. Revise requirements or use higher-fidelity analysis; do not select a layout from this screen.',
       'bulk_rise_k':rise,'radial_verification':radial,'energy_relative_error':energy_error,'checks_passed':energy_error<1e-12 and radial[-1]['relative_error_pct']<.05 and all(v['pressure_crosscheck_relative']<1e-12 for v in results),
       'limits':LIMITS,'sources':SOURCES,'provenance':{'calculator_sha256':digest(__file__)},
       'guard_scenario':{'heat_multiplier':1.1,'thermal_flow_multiplier':.9,'h_multiplier':.8,'pressure_flow_multiplier':1.1,'viscosity_multiplier':1.2,'diameter_multiplier':.98}}
