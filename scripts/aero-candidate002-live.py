"""Allowlisted public projection of independently collected, private observation.

No network, process control, scoring or raw text copying. The private bridge owns
identity checks. Do not call this with an unverified observer or publish its input.
"""
from datetime import datetime, timezone
import math
import sys

if sys.flags.optimize:
    raise RuntimeError('Optimization is not admitted for public projection')

SPECS = [(f'{dataset}_{arm}_r{repeat}', dataset, arm, repeat, count)
         for dataset, repeats, count in [('heldout', 2, 48), ('named', 1, 240), ('historical', 2, 48)]
         for repeat in range(repeats) for arm in ['base', 'candidate002']]
STATES = {'RUNNING', 'INITIALIZING', 'CHECKING', 'FINALIZING',
          'INCOMPLETE_STOPPED', 'COLLECTED_REVIEW_PENDING', 'UNKNOWN'}
CLOSURE = ('controller_exited', 'owned_workers_cleared', 'logs_closed',
           'reservation_released', 'custody_verified')


def stamp(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        return None
    try:
        return datetime.fromtimestamp(value, timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def project(evidence, now):
    """Fail closed; all strings in output are fixed here, never source text."""
    out = dict(schema='aero.public.candidate002.validation.v2', published_at=stamp(now),
               observed_at=None, candidate='candidate002 · 14B',
               run_label='Validation attempt 4 · 20 October 2026', state='UNKNOWN',
               saved_outputs=None, total_outputs=864, percent=None,
               collection_complete=False, last_phase=None, gate_breach_count=None,
               stop_reason='NOT_ESTABLISHED', training_steps=None, training_total_steps=858,
               evaluation_status='NOT_ESTABLISHED', promotion_status='NOT_AUTHORIZED',
               publication_mode='IDENTITY_VERIFIED_PERIODIC_SNAPSHOT',
               refresh_interval_seconds=900, stale_after_seconds=1200,
               closure={key: False for key in CLOSURE},
               phases=[dict(id=name, label=f'{dataset.title()} · {"Base" if arm == "base" else "Candidate002"} · repeat {repeat+1}',
                            saved=None, total=count, state='unknown')
                       for name, dataset, arm, repeat, count in SPECS])
    if not isinstance(evidence, dict):
        return out
    if evidence.get('training_verified') is True:
        out['training_steps'] = 858
    try:
        assert evidence['identity_verified'] is True
        observed = evidence['observed_at']
        assert stamp(observed) and -5 <= now - observed <= 60
        state = evidence['state']
        assert state in STATES - {'UNKNOWN'}
        rows = evidence['phases']
        assert isinstance(rows, list) and len(rows) == 10
        cells = []
        for template, row in zip(out['phases'], rows):
            assert row['id'] == template['id']
            saved, phase_state = row['saved'], row['state']
            assert phase_state in {'unknown', 'not_started', 'initializing', 'running', 'stopped', 'outputs_saved'}
            assert saved is None or type(saved) is int and 0 <= saved <= template['total']
            assert phase_state != 'not_started' or saved == 0
            assert phase_state != 'outputs_saved' or saved == template['total']
            cells.append({**template, 'saved': saved, 'state': phase_state})
        last = evidence['last_phase']
        assert last is None or last in {r['id'] for r in cells}
        breaches = evidence['gate_breach_count']
        assert type(breaches) is int and breaches >= 0
        known = all(r['saved'] is not None for r in cells)
        total = sum(r['saved'] for r in cells) if known else None
        complete = state == 'COLLECTED_REVIEW_PENDING'
        assert not complete or total == 864
        closure = {key: evidence.get('closure', {}).get(key) is True for key in CLOSURE}
        # Active execution cannot be simultaneously finalized.
        if state in {'RUNNING', 'INITIALIZING', 'CHECKING', 'FINALIZING'}:
            assert not any(closure.values())
        out.update(state=state, observed_at=stamp(observed), phases=cells,
                   saved_outputs=total, percent=((total * 1000 + 432) // 864) / 10 if known else None,
                   last_phase=last, gate_breach_count=breaches, closure=closure,
                   collection_complete=complete,
                   stop_reason='INCOMPLETE_REASON_NOT_ESTABLISHED' if state == 'INCOMPLETE_STOPPED' else 'NONE')
    except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
        pass
    return out
