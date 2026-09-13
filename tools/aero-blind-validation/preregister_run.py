"""Create a new immutable production package from the previously frozen inputs.

Does not read the key, source paper or measurements. Does not launch a solver.
"""
import hashlib,json,shutil,subprocess
from pathlib import Path
from protocol import Challenge, now, sha
from execute_case import IMAGE

def prepare(repo):
    repo=Path(repo).resolve();root=repo/'public/demos/aero/blind-validation-01-run-v1'
    if root.exists():raise ValueError('Run package already exists')
    source=repo/'public/demos/aero/blind-validation-01-input-v1'
    root.mkdir()
    for n in ['input.json','reference.enc','reference-metadata.json','custody.json','state.json']:
        shutil.copyfile(source/n,root/n)
    inputs=json.loads((root/'input.json').read_text())
    code=root/'code';code.mkdir()
    for n in ['case_driver.py','execute_case.py','analyze_case.py','run_sweep.py','protocol.py']:
        shutil.copyfile(Path(__file__).parent/n,code/n)
    commits=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    criteria={
      'status':'READY_TO_FREEZE','benchmark_id':inputs['benchmark_id'],
      'source_citation':inputs['source_citation'],'source_version':inputs['source_version'],
      'input_sha256':sha((root/'input.json').read_bytes()),'sealed_reference_sha256':sha((root/'reference.enc').read_bytes()),
      'quantities':inputs['quantities'],'stations':inputs['stations'],
      'geometry_source':{'nominal':'Pinned OpenFOAM Foundation 10 NACA0012.obj.gz, copied without any tutorial solution or flow conditions','as_built':'UNKNOWN; nominal approximation only','mesh':'Six-block projected C-grid from Foundation 10 tutorial, with two upper-farfield projection corrections and documented counts/scales','license':'OpenFOAM GPL-3.0-or-later geometry and template; retain original provenance'},
      'dimensional_assumptions':{'chord_m':.601,'empty_span_m':.00601,'temperature_K_assumed':288.15,'gas_constant_J_kg_K':287.05,'heat_capacity_ratio':1.4,'speed_relation':'0.15*sqrt(1.4*287.05*288.15)','nu_relation':'U*0.601/5950000','density':'Force coefficients use rhoInf=1 with kinematic pressure; density cancels. No claim of atmospheric tunnel density.','geometry_transform':'(x,y,z) in nominal template maps to (0.601*x,0.601*z,-0.00601*y/0.2) metres'},
      'flow_conditions':inputs['flow_conditions'],
      'solver':{'name':'OpenFOAM Foundation 10 simpleFoam','image':IMAGE,'threads_per_case':1,'container_cpus':2,'case_memory_GB':4,'case_wall_timeout_seconds':7200,'concurrent_cases':3},
      'governing_equations':'Two-dimensional incompressible steady Reynolds-averaged Navier-Stokes. Low-Mach approximation at M=0.15; compressibility is not resolved or corrected post hoc. A bounded steady-model test, not a claim that the complete angle series is physically steady. Oscillating/nonstationary cases fail numerical acceptance.',
      'turbulence_model':'kOmegaSSTLM, unmodified Foundation 10 coefficients. Proposed transition surrogate, not a resolved No.180 grit model.',
      'wall_treatment':{'U':'no-slip','k':'fixed 1e-12','omega':'omegaWallFunction','nut':'nutLowReWallFunction','trip_surrogate':'gammaInt fixed to 0 for x/c<0.05 and 1 for x/c>=0.05 in a geometric near-surface band of thickness 0.02c. Cells selected against nominal thickness; constraints audited. This approximates prescribed transition, not physical roughness or strip-width drag.','gamma_caveat':'Does not establish trip equivalence, transition sensitivity or as-built fidelity.'},
      'boundary_conditions':{'outer':'freestreamVelocity/freestreamPressure at inlet+outlet; inletOutlet k,omega,gammaInt,ReThetat; empty front/back; corrected-free-air comparison, no second wind-tunnel correction','turbulence_intensity_assumed':.001,'length_scale_over_c_assumed':.01,'ReThetat_inlet':1136.5272,'gammaInt_inlet':1,'unknown_turbulence':'0.1 percent is a declared nominal assumption, NOT a measurement.'},
      'initial_conditions':'Uniform free-stream U, p=0, gammaInt=1, ReThetat=1136.5272; k=1.5*(0.001*U)^2, omega=sqrt(k)/(0.09^0.25*0.01c), followed by potentialFoam velocity/flux initialization. Initialize independently for each angle/grid; no warm-start from other stations. Do not write uppercase Phi on the case-insensitive host filesystem.',
      'mesh_strategy':'Projected six-block C-grid; upstream semicylinder radius20c, downstream30c; one empty span cell; near-wall grading300000; downstream grading400; no answer-based adaptation.',
      'mesh_levels':[{'name':'coarse','normal':64,'upstream':64,'surface_aft':40,'wake':64},{'name':'medium','normal':96,'upstream':96,'surface_aft':60,'wake':96},{'name':'fine','normal':128,'upstream':128,'surface_aft':80,'wake':128}],
      'refinement_strategy':'Retain all three independently generated grids at every station. Fine-grid mean over SIMPLE iterations1500..2000 is the prediction, explicitly not a physical time average. Medium/fine CL difference <=0.02 and CD difference <=0.002 at every station. Report coarse values too. No extrapolated GCI or uncertainty claim.',
      'yplus_criterion':{'fine_wall_percentile95_max':2,'fine_wall_absolute_max':5,'policy':'Both required for numerical PASS; retain per-face data/histograms and all-grid summaries, including failures.'},
      'convergence_criteria':{'iterations':2000,'stationarity':'Means over iterations1000..1500 versus1500..2000 differ by <=0.01 CL and <=0.001 CD. Additionally last500-iteration CL range <=0.02 and CD range <=0.002, so cancelling oscillations cannot pass by means alone.','physical_time_accuracy':'No physical time integration. A stable RANS fixed point does not establish flow is physically steady. Potential unsteady/stall behavior remains a modeling limitation; a transient follow-up is separate, not silent tuning.','solver_completion':'Full2000 iterations, finite output and end marker required; no cropped curve accepted as completion.'},
      'conservation_criteria':{'max_absolute_final_global_continuity':1e-6,'max_final_local_continuity':1e-5,'final_boundary_flux_imbalance_fraction_max':.001,'definition':'abs(sum boundary phi)/sum(abs(boundary phi)); phi in m3/s, density cancels; integrate each patch; not solver residual renamed as mass balance.'},
      'residual_criteria':{'last_iteration_final_linear_residual_max':1e-6,'last_iteration_initial_residual_max':1e-4,'fields':['p','Ux','Uy','k','omega','gammaInt','ReThetat'],'finite_all_fields_required':True,'linear_solution':'PCG/DIC pressure with 2000 linear-iteration cap and tolerance1e-7, relTol0.01. Smooth symGaussSeidel other fields. Both initial and final residual requirements must pass.'},
      'comparison_metrics':['rmse','max_absolute_error'],
      'acceptance_thresholds':{'CL':{'rmse':.1,'max_absolute_error':.2},'CD':{'rmse':.005,'max_absolute_error':.01}},
      'threshold_rationale':'Pre-answer engineering utility bounds for this first bounded workflow test, not experimental confidence intervals or a certified design tolerance. No target coefficients or measured scatter used to derive them.',
      'experimental_uncertainty':{'source':'Per-point uncertainty absent in permitted source inputs; unknown remains unknown','gate_policy':'descriptive_only_no_threshold_widening'},
      'allowable_preprocessing':'Pinned nominal geometry/mesh generation and input dimensional conversion only. Short implementation smoke tests at 1 degree (not a registered station) precede this freeze and remain labelled diagnostic. No tuning from experimental coefficients.',
      'prohibited_tuning':'No physical model, criteria, station, mesh-level or averaging-window changes after this freeze. A bug correction requires a visible version and invalidates affected runs. Do not remove difficult or failed operating points.',
      'failure_conditions':'Failed numerical/experimental gates imply FAIL. Missing/incomplete/nonfinite predictions imply INCOMPLETE and no reference reveal under the existing protocol. Timeout is not convergence. Invalid topology/negative-volume geometry aborts before solve. High aspect ratio/determinant warnings remain visible; numerical PASS still requires physical and numerical gates.',
      'runtime_numerics':'FOAM_SIGFPE unset because unmodified LM Fthetat contains the exp(-(y/delta)^4) limiting expression at zero vorticity. This permits IEEE infinity intermediates, NOT nonfinite stored fields: every retained numeric field and coefficient must pass a finite-value check. No alternate closure or changed coefficient is permitted.',
      'repository_commit':commits,'environment_versions':{'OpenFOAM':'Foundation10','Python_in_container':'3.8 standard library','Docker_image':IMAGE},'date_time':now(),
      'execution_code':{p.name:sha(p.read_bytes()) for p in code.iterdir()}
    }
    Challenge(root).freeze_criteria(criteria)
    (root/'README.md').write_text('# Challenge 01 production attempt v1\n\nInput-only numerical specification. Criteria must be publicly anchored before any production case is launched. Reference remains encrypted until a complete prediction is publicly frozen.\n')
    print(json.dumps({'stage':Challenge(root).state()['stage'],'path':str(root),'preregistration_sha256':sha((root/'preregistration.json').read_bytes())}))
if __name__=='__main__':prepare(Path(__file__).resolve().parents[2])
