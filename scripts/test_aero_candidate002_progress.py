import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import hashlib

spec = importlib.util.spec_from_file_location('projection', Path(__file__).with_name('aero-candidate002-progress.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    contract = {'schema': 'aero.fea.candidate002.validation_execution.v1', 'expected_new_outputs': 864,
                'phases': [p[0] for p in m.SPECS], 'phase_specs': {p[0]: {'cases': p[4]} for p in m.SPECS},
                'candidate_receipt': {'adapter_sha256': m.ADAPTER}}
    terminal = {'owned_processes_zero': True, 'owned_gpu_contexts_zero': True,
                'state': {'Running': False}, 'logs_closed': True,
                'error': 'RuntimeError: Windows priority lease/heartbeat unavailable'}
    value = {'snapshot_at': 1000, 'state': {'state': 'FAILED_OR_BLOCKED', 'expected_new_outputs': 864,
              'training': False, 'promotion': 'NOT_AUTHORIZED'}, 'terminal': {'ended_at': 999,
              'owned_containers_running': [], 'error': terminal['error']}, 'supervisor': {'alive': False},
              'running_containers': [], 'phases': [{'name': 'init_probe', 'gate': {'breaches': []},
              'init_probe_complete': {'state': 'COMPLETED_MODEL_FREE_DIAGNOSTIC', 'predictions': 0},
              'terminal': terminal}, {'name': 'heldout_base_r0', 'progress': {
              'phase': 'heldout_base_r0', 'saved': 36, 'total': 48, 'last_id': 'PRIVATE_CASE'},
              'gate': {'breaches': ['PRIVATE_SECRET']}, 'terminal': terminal}]}
    training = {'state': 'completed', 'steps': 858, 'adapter_sha256': m.ADAPTER}
    release = {'ok': True, 'released': True, 'owner': 'AeroFEA-candidate002-GX10-validation',
               'run_id': 'aerofea-candidate002-validation-20261020-run002'}
    controller = {'ended_at': 1001, 'process_handle_waited': True, 'redirect_handles_closed': True}
    return [value, contract, training, release, controller, True, 1002]


class ProjectionTests(unittest.TestCase):
    def test_terminal_counts_privacy_and_closure(self):
        args = fixture()
        args[0]['host'] = 'PRIVATE_HOST'
        s = m.project(*args)
        self.assertEqual((s['saved_outputs'], s['percent'], s['training_steps']), (36, 4.2, 858))
        self.assertEqual(s['state'], 'INCOMPLETE_STOPPED')
        self.assertEqual(s['gate_breach_count'], 1)
        self.assertTrue(all(s['closure'].values()))
        self.assertEqual(s['phases'][1]['saved'], 0)
        self.assertEqual(s['phases'][1]['state'], 'not_started')
        self.assertNotIn('PRIVATE', json.dumps(s))
        self.assertNotIn(m.ADAPTER, json.dumps(s))

    def test_missing_corrupt_progress_is_unknown(self):
        for mutation in ['absent', 'bool', 'negative', 'overflow', 'duplicate', 'foreign', 'missing_count']:
            args = fixture()
            row = args[0]['phases'][1]
            if mutation == 'absent': args[0] = None
            elif mutation == 'bool': row['progress']['saved'] = True
            elif mutation == 'negative': row['progress']['saved'] = -1
            elif mutation == 'overflow': row['progress']['saved'] = 49
            elif mutation == 'duplicate': args[0]['phases'].append(copy.deepcopy(row))
            elif mutation == 'foreign': row['name'] = 'foreign'
            elif mutation == 'missing_count': del row['progress']['saved']
            s = m.project(*args)
            self.assertEqual(s['state'], 'UNKNOWN', mutation)
            self.assertIsNone(s['saved_outputs'], mutation)
            self.assertIsNone(s['percent'], mutation)

    def test_live_or_stale_process_never_claimed_active(self):
        for now in [1002, 99999]:
            args = fixture()
            args[0]['supervisor']['alive'] = True
            args[-1] = now
            self.assertEqual(m.project(*args)['state'], 'UNKNOWN')

    def test_no_promotion_or_efficacy_from_complete_collection(self):
        args = fixture()
        args[0]['state']['state'] = 'VALIDATION_COMPLETED_OFFLINE_SCORING_PENDING'
        original = args[0]['phases'][1]
        args[0]['phases'] = [args[0]['phases'][0]]
        for name, _, _, _, count in m.SPECS:
            row = copy.deepcopy(original)
            row['name'] = row['progress']['phase'] = name
            row['progress']['saved'] = row['progress']['total'] = count
            args[0]['phases'].append(row)
        s = m.project(*args)
        self.assertEqual(s['saved_outputs'], 864)
        self.assertTrue(s['collection_complete'])
        self.assertEqual(s['evaluation_status'], 'NOT_ESTABLISHED')
        self.assertEqual(s['promotion_status'], 'NOT_AUTHORIZED')

    def test_training_hash_and_exact_release_required(self):
        args = fixture()
        args[2]['adapter_sha256'] = 'different'
        args[3]['run_id'] = 'another-run'
        args[5] = False
        s = m.project(*args)
        self.assertIsNone(s['training_steps'])
        self.assertFalse(s['closure']['reservation_released'])
        self.assertFalse(s['closure']['custody_verified'])

    def test_custody_hash_size_containment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'evidence').write_bytes(b'proof')
            manifest = {'schema': 'aero.artifact_custody.v2', 'artifacts': [{
                'path': 'evidence', 'bytes': 5, 'sha256': hashlib.sha256(b'proof').hexdigest()}]}
            def save(): (root / 'CUSTODY_FINAL_MANIFEST_V2.json').write_text(json.dumps(manifest))
            save()
            self.assertTrue(m.custody_verified(root))
            (root / 'evidence').write_bytes(b'other')
            self.assertFalse(m.custody_verified(root))
            manifest['artifacts'][0]['path'] = '../outside'
            save()
            self.assertFalse(m.custody_verified(root))


if __name__ == '__main__':
    unittest.main()
