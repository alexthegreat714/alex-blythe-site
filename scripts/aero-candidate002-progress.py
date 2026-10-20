"""Export a privacy-safe, terminal candidate002 validation snapshot.

Read-only toward private runs. Does not launch/resume work or claim live execution.
Future active-run tracking needs a separate identity-verified observer; this exporter
deliberately reports UNKNOWN for nonterminal input. Never reuse the old diagnostic.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public/demos/aero/fea-candidate002-validation/status.json'
SPECS = [(f'{dataset}_{arm}_r{repeat}', dataset, arm, repeat, count)
         for dataset, repeats, count in [('heldout', 2, 48), ('named', 1, 240), ('historical', 2, 48)]
         for repeat in range(repeats) for arm in ['base', 'candidate002']]
ADAPTER = '04633ede671d3e6da309926d0ec5881b7288377ede77b1888f5d8c290ab385d9'


def read(path):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return None


def stamp(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        return None
    try:
        return datetime.fromtimestamp(value, timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def custody_verified(run):
    """Independently check every manifest size/hash; no public artifact names."""
    try:
        manifest = read(run / 'CUSTODY_FINAL_MANIFEST_V2.json')
        artifacts = manifest['artifacts']
        if manifest['schema'] != 'aero.artifact_custody.v2' or not artifacts:
            return False
        seen = set()
        root = run.resolve()
        for item in artifacts:
            path = (root / item['path']).resolve()
            if not path.is_relative_to(root) or path in seen or not path.is_file():
                return False
            seen.add(path)
            if path.stat().st_size != item['bytes']:
                return False
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            if digest.hexdigest() != item['sha256']:
                return False
        return True
    except (OSError, TypeError, KeyError, ValueError):
        return False


def project(value, contract, training, release, controller, custody, now):
    result = {
        'schema': 'aero.public.candidate002.validation.v1',
        'published_at': stamp(now), 'observed_at': None,
        'candidate': 'candidate002 · 14B', 'run_label': 'Validation attempt 2 · 20 October 2026',
        'state': 'UNKNOWN', 'saved_outputs': None, 'total_outputs': 864, 'percent': None,
        'collection_complete': False, 'last_phase': None, 'gate_breach_count': None,
        'stop_reason': 'NOT_ESTABLISHED', 'training_steps': None, 'training_total_steps': 858,
        'evaluation_status': 'NOT_ESTABLISHED', 'promotion_status': 'NOT_AUTHORIZED',
        'publication_mode': 'TERMINAL_SNAPSHOT_NOT_LIVE_TELEMETRY',
        'closure': {'controller_exited': False, 'owned_workers_cleared': False,
                    'logs_closed': False, 'reservation_released': False, 'custody_verified': False},
        'phases': [{'id': name, 'label': f'{dataset.title()} · {"Base" if arm == "base" else "Candidate002"} · repeat {repeat+1}',
                    'saved': None, 'total': count, 'state': 'unknown'}
                   for name, dataset, arm, repeat, count in SPECS],
    }
    if (isinstance(training, dict) and training.get('state') == 'completed' and training.get('steps') == 858
            and training.get('adapter_sha256') == ADAPTER):
        # Contract admission binds the completed training receipt to this adapter.
        if (isinstance(contract, dict) and isinstance(contract.get('candidate_receipt'), dict)
                and contract['candidate_receipt'].get('adapter_sha256') == ADAPTER):
            result['training_steps'] = 858
    try:
        expected = {name: count for name, _, _, _, count in SPECS}
        assert isinstance(value, dict) and isinstance(contract, dict)
        assert contract['schema'] == 'aero.fea.candidate002.validation_execution.v1'
        assert contract['expected_new_outputs'] == value['state']['expected_new_outputs'] == 864
        assert set(contract['phases']) == set(expected) and len(contract['phases']) == 10
        assert all(contract['phase_specs'][name]['cases'] == count for name, count in expected.items())
        assert value['state']['training'] is False and value['state']['promotion'] == 'NOT_AUTHORIZED'
        assert stamp(value['snapshot_at']) is not None
        rows = {}
        for row in value['phases']:
            name = row['name']
            assert name in ('init_probe', *expected) and name not in rows
            rows[name] = row
        # A completed model-free probe establishes that absent later phases were
        # not started. A missing phase list alone is not evidence of zero outputs.
        assert rows['init_probe']['init_probe_complete']['state'] == 'COMPLETED_MODEL_FREE_DIAGNOSTIC'
        assert rows['init_probe']['init_probe_complete']['predictions'] == 0
        breaches = len(rows['init_probe']['gate']['breaches'])
        cells = []
        last = None
        for cell in result['phases']:
            row = rows.get(cell['id'])
            if row is None:
                cells.append({**cell, 'saved': 0, 'state': 'not_started'})
                continue
            progress = row['progress']
            saved = progress['saved']
            assert type(saved) is int and 0 <= saved <= cell['total']
            assert progress['total'] == cell['total'] and progress['phase'] == cell['id']
            violations = row['gate']['breaches']
            assert isinstance(violations, list)
            breaches += len(violations)
            last = cell['id']
            cells.append({**cell, 'saved': saved, 'state': 'outputs_saved' if saved == cell['total'] else 'stopped'})
        terminal = value['terminal']
        assert isinstance(terminal, dict) and terminal
        assert value['supervisor']['alive'] is False and value['running_containers'] == []
        assert terminal['owned_containers_running'] == []
        assert value['state']['state'] in ('FAILED_OR_BLOCKED', 'VALIDATION_COMPLETED_OFFLINE_SCORING_PENDING')
        total = sum(cell['saved'] for cell in cells)
        complete = total == 864 and value['state']['state'] == 'VALIDATION_COMPLETED_OFFLINE_SCORING_PENDING'
        result.update(observed_at=stamp(value['snapshot_at']), phases=cells, last_phase=last,
                      saved_outputs=total, percent=round(total / 864 * 100, 1), gate_breach_count=breaches,
                      collection_complete=complete, state='COLLECTED_REVIEW_PENDING' if complete else 'INCOMPLETE_STOPPED')
        errors = [terminal.get('error', '')] + [row.get('terminal', {}).get('error', '') for row in rows.values()]
        result['stop_reason'] = ('HEARTBEAT_AUTHORITY_UNAVAILABLE' if any(
            isinstance(e, str) and 'Windows priority lease/heartbeat unavailable' in e for e in errors)
            else 'NONE' if complete else 'EXECUTION_GATE_STOP')
        ended = controller.get('ended_at') if isinstance(controller, dict) else None
        controller_ok = (stamp(ended) is not None and ended >= terminal['ended_at'] and
                         controller.get('process_handle_waited') is True and controller.get('redirect_handles_closed') is True)
        phase_terminals = [row.get('terminal', {}) for row in rows.values()]
        workers = all(t.get('owned_processes_zero') is True and t.get('owned_gpu_contexts_zero') is True
                      and t.get('state', {}).get('Running') is False for t in phase_terminals)
        logs = all(t.get('logs_closed') is True for t in phase_terminals)
        released = (isinstance(release, dict) and release.get('ok') is True and release.get('released') is True
                    and release.get('owner') == 'AeroFEA-candidate002-GX10-validation'
                    and release.get('run_id') == 'aerofea-candidate002-validation-20261020-run002')
        result['closure'] = {'controller_exited': controller_ok, 'owned_workers_cleared': workers,
                             'logs_closed': logs, 'reservation_released': released,
                             'custody_verified': custody is True and controller_ok and workers and logs}
    except (AssertionError, KeyError, TypeError, ValueError):
        # No partial or fabricated zero from malformed/missing source input.
        pass
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--training-run', type=Path, required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = project(read(args.run / 'remote_progress.json'), read(args.run / 'EXECUTION_CONTRACT.json'),
                     read(args.training_run / 'remote_artifacts/train_0/training_complete.json'),
                     read(args.run / 'priority_release.json'), read(args.run / 'controller_exit_receipt.json'),
                     custody_verified(args.run), time.time())
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({'state': result['state'], 'saved': result['saved_outputs'], 'total': 864,
                      'closure': result['closure'], 'written': args.write}))


if __name__ == '__main__':
    main()
