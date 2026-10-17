"""Publish an allowlisted progress snapshot, never source logs or predictions.

Read-only toward the diagnostic. No SSH, GPU, model calls, scheduler operations
or service changes. Public updates are separate from execution and scoring.
"""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'public/demos/aero/fea-diagnostic-progress/status.json'
ARMS = ('base_native', 'base_source_copy', 'candidate_native', 'candidate_source_copy')
LABELS = ('Stock · original prompt', 'Stock · source-copy prompt',
          'AeroFEA · original prompt', 'AeroFEA · source-copy prompt')


def number(value):
    return value if type(value) in (int,float) and math.isfinite(value) else None


def project(value, now):
    snapshot = number(value.get('snapshot_at'))
    fresh = snapshot is not None and -5 <= now-snapshot <= 90
    state = value.get('state',{}).get('state','UNKNOWN')
    phases = value.get('phases',[])
    if not isinstance(phases,list):
        raise ValueError('Invalid phase list')
    rows = {}
    for row in phases:
        name = row.get('name')
        if name not in ('init_probe',*ARMS) or name in rows:
            raise ValueError('Unexpected or duplicate phase')
        rows[name] = row
    cells = []
    breaches = 0
    active = None
    last_change = None
    for arm,label in zip(ARMS,LABELS):
        row = rows.get(arm,{})
        progress = row.get('progress') or {}
        saved = progress.get('saved',0)
        if type(saved) is not int or not 0 <= saved <= 48:
            raise ValueError('Invalid saved-output count')
        gate = row.get('gate') or {}
        violations = gate.get('breaches') or []
        if not isinstance(violations,list):
            raise ValueError('Invalid gate breach list')
        breaches += len(violations)
        terminal = row.get('terminal') or {}
        complete = row.get('evaluation_complete') or {}
        loaded = row.get('model_loaded') is True
        changed = number(progress.get('time'))
        if changed is not None:
            last_change = max(last_change or changed,changed)
        failed = bool(terminal.get('error')) or bool(terminal.get('state',{}).get('OOMKilled'))
        if complete.get('state') == 'COMPLETED' and complete.get('records') == 48:
            phase_state = 'outputs_saved' if saved == 48 else 'count_mismatch'
        elif failed or violations:
            phase_state = 'stopped'
        elif row and not terminal:
            phase_state = 'running' if loaded else 'loading_model'
            active = arm
        elif row:
            phase_state = 'stopped'
        else:
            phase_state = 'queued'
        cells.append({'id':arm,'label':label,'saved':saved,'total':48,'state':phase_state})
    init = rows.get('init_probe',{})
    breaches += len((init.get('gate') or {}).get('breaches') or [])
    total = sum(c['saved'] for c in cells)
    terminal = bool(value.get('terminal'))
    complete = state == 'DEVELOPMENT_DIAGNOSTIC_COMPLETED_OFFLINE_SCORING_PENDING' and total == 192
    if complete:
        disposition = 'OUTPUTS_SAVED_SCORING_PENDING'
    elif terminal or state == 'FAILED_OR_BLOCKED' or breaches:
        disposition = 'INCOMPLETE_STOPPED'
    elif not fresh:
        disposition = 'OBSERVATION_STALE'
    elif active:
        disposition = 'MODEL_LOADING' if next(c for c in cells if c['id']==active)['state']=='loading_model' else 'RUNNING'
    elif state == 'DEVELOPMENT_DIAGNOSTIC_RUNNING':
        disposition = 'STARTUP_CHECK'
    else:
        disposition = 'NOT_ESTABLISHED'
    useful_change_recent = last_change is not None and 0 <= now-last_change <= 240
    return {'schema':'aero.public.fea.progress.v1',
        'published_at':datetime.fromtimestamp(now,timezone.utc).isoformat(),
        'observed_at':datetime.fromtimestamp(snapshot,timezone.utc).isoformat() if snapshot is not None else None,
        'run_label':'Source-copy development diagnostic · 17 October 2026',
        'state':disposition,'saved_outputs':total,'total_outputs':192,
        'percent':round(100*total/192,1),'active_phase':active,'phases':cells,
        'gate_breach_count':breaches,'startup_passed':bool(init.get('init_probe_complete')),
        'recent_output_change_at':datetime.fromtimestamp(last_change,timezone.utc).isoformat() if last_change is not None else None,
        'activity_at_observation': 'recent_output_progress' if fresh and useful_change_recent and not terminal else
            'model_loading' if disposition=='MODEL_LOADING' else 'worker_running_no_recent_output' if disposition=='RUNNING' else 'not_active',
        'snapshot_source_fresh':fresh,'collection_complete':complete,
        'evaluation_status':'NOT_ESTABLISHED','promotion_status':'NOT_AUTHORIZED',
        'training_status':'PRIOR_14B_CANDIDATE_TRAINED_858_STEPS_NOT_RETRAINING',
        'expected_public_update_minutes':15,
        'limitations':['192 is the output-collection target, not a model-quality score.',
            '48 synthetic development cases, four model/prompt cells, one repeat per cell.',
            'Prompt or guard gains are not learned improvements.',
            'No fresh heldout confirmation, broad FEA/CFD superiority, physical validation or promotion is established.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--run',required=True,type=Path,help='Private local run directory; never included in published JSON')
    args = parser.parse_args()
    snapshot = json.loads((args.run/'remote_progress.json').read_text(encoding='utf-8'))
    result = project(snapshot,time.time())
    if args.write:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        temporary = OUT.with_suffix('.tmp')
        temporary.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        temporary.replace(OUT)
    print(json.dumps({'state':result['state'],'saved':result['saved_outputs'],'total':192,
                      'written':args.write,'privacy':'ALLOWLIST_ONLY_NO_LOGS_PROMPTS_RESPONSES_HOSTS_OR_PIDS'}))


if __name__=='__main__':
    main()
