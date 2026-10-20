import importlib.util
import json
from pathlib import Path
import unittest
import subprocess

spec = importlib.util.spec_from_file_location('live', Path(__file__).with_name('aero-candidate002-live.py'))
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


def fixture():
    return dict(identity_verified=True, observed_at=1_800_000_000, training_verified=True,
                state='RUNNING', last_phase=live.SPECS[0][0], gate_breach_count=0,
                phases=[dict(id=s[0], saved=24 if i == 0 else 0,
                             state='running' if i == 0 else 'not_started')
                        for i,s in enumerate(live.SPECS)])


class Projection(unittest.TestCase):
    def test_running_and_separate_training(self):
        p=live.project(fixture(),1_800_000_002)
        self.assertEqual((p['state'],p['saved_outputs'],p['percent']),('RUNNING',24,2.8))
        self.assertEqual(p['training_steps'],858)
        self.assertFalse(any(p['closure'].values()))

    def test_initialization_unknown_not_zero(self):
        f=fixture();f['state']='INITIALIZING'
        f['phases'][0].update(saved=None,state='initializing')
        p=live.project(f,1_800_000_002)
        self.assertEqual(p['state'],'INITIALIZING')
        self.assertIsNone(p['saved_outputs']);self.assertIsNone(p['percent'])
        self.assertEqual(p['phases'][1]['saved'],0)

    def test_absent_identity_stale_future_and_corrupt_fail_closed(self):
        for key,value in [('identity_verified',False),('observed_at',1_799_999_900),
                          ('observed_at',1_800_000_100),('gate_breach_count',True),
                          ('state','PROMOTED'),('phases',[])]:
            f=fixture();f[key]=value;p=live.project(f,1_800_000_002)
            self.assertEqual(p['state'],'UNKNOWN')
            self.assertIsNone(p['saved_outputs'])
            self.assertTrue(all(c['saved'] is None for c in p['phases']))

    def test_completion_not_quality_or_custody(self):
        f=fixture();f['state']='COLLECTED_REVIEW_PENDING'
        for p,s in zip(f['phases'],live.SPECS):p.update(saved=s[4],state='outputs_saved')
        p=live.project(f,1_800_000_002)
        self.assertEqual(p['saved_outputs'],864)
        self.assertTrue(p['collection_complete'])
        self.assertEqual(p['evaluation_status'],'NOT_ESTABLISHED')
        self.assertEqual(p['promotion_status'],'NOT_AUTHORIZED')
        self.assertFalse(any(p['closure'].values()))

    def test_active_cannot_claim_finalization(self):
        f=fixture();f['closure']={'custody_verified':True}
        self.assertEqual(live.project(f,1_800_000_002)['state'],'UNKNOWN')

    def test_private_canaries_cannot_be_serialized(self):
        f=fixture();canary='PRIVATE_PROMPT_HOST_PID_PATH_TOKEN_RESPONSE_CASE_ERROR'
        f.update(secret=canary,error=canary,hostname=canary)
        f['phases'][0].update(label=canary,response=canary,last_id=canary)
        p=live.project(f,1_800_000_002)
        self.assertNotIn(canary,json.dumps(p))

    def test_all_865_counts_agree_with_javascript_rounding(self):
        expected=json.loads(subprocess.check_output(['C:/Program Files/nodejs/node.exe','-e',
            'process.stdout.write(JSON.stringify(Array.from({length:865},(_,n)=>Math.round(n/864*1000)/10)))'],text=True))
        for n in range(865):
            f=fixture();left=n
            for row,s in zip(f['phases'],live.SPECS):
                saved=min(left,s[4]);left-=saved
                row.update(saved=saved,state='outputs_saved' if saved==s[4] else 'running')
            self.assertEqual(live.project(f,1_800_000_002)['percent'],expected[n],n)


if __name__=='__main__':unittest.main()
