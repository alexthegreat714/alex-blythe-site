"""CPU-only lifecycle/privacy tests. No model or service calls."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('projection',Path(__file__).with_name('aero-fea-progress.py'))
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)


class ProjectionTests(unittest.TestCase):
    def source(self):
        return {'snapshot_at':1000,'state':{'state':'DEVELOPMENT_DIAGNOSTIC_RUNNING'},
            'phases':[{'name':'base_native','model_loaded':True,'progress':{'saved':5,'time':998,
            'last_id':'PRIVATE_CASE'},'gate':{'breaches':[],'container_pids':[123456]},'terminal':{}}],
            'private_path':'PRIVATE_LOCAL_PATH','host':'PRIVATE_HOST','answers':['PRIVATE_RESPONSE']}

    def test_projection_is_allowlist_no_private_strings(self):
        s=P.project(self.source(),1001)
        encoded=json.dumps(s)
        for text in ('PRIVATE_CASE','123456','PRIVATE_LOCAL_PATH','PRIVATE_HOST','PRIVATE_RESPONSE'):
            self.assertNotIn(text,encoded)
        self.assertEqual(s['saved_outputs'],5)
        self.assertEqual(s['activity_at_observation'],'recent_output_progress')

    def test_stale_observation_never_claims_active(self):
        s=P.project(self.source(),1200)
        self.assertEqual(s['state'],'OBSERVATION_STALE')
        self.assertFalse(s['snapshot_source_fresh'])
        self.assertEqual(s['activity_at_observation'],'not_active')

    def test_no_output_change_is_distinguished_from_running_worker(self):
        source=self.source();source['phases'][0]['progress']['time']=600
        self.assertEqual(P.project(source,1001)['activity_at_observation'],'worker_running_no_recent_output')

    def test_loading_does_not_add_outputs(self):
        source=self.source();source['phases'][0]['model_loaded']=False;source['phases'][0]['progress']={}
        s=P.project(source,1001)
        self.assertEqual(s['state'],'MODEL_LOADING')
        self.assertEqual(s['saved_outputs'],0)

    def test_stopped_output_retained_and_raw_error_not_published(self):
        source=self.source();source['terminal']={'state':'FAILED_OR_BLOCKED'}
        source['phases'][0]['gate']['breaches']=['PRIVATE_ERROR']
        s=P.project(source,1001)
        self.assertEqual(s['state'],'INCOMPLETE_STOPPED')
        self.assertEqual(s['saved_outputs'],5)
        self.assertEqual(s['gate_breach_count'],1)
        self.assertNotIn('PRIVATE_ERROR',json.dumps(s))

    def test_full_collection_is_not_quality_or_promotion(self):
        source={'snapshot_at':1000,'state':{'state':'DEVELOPMENT_DIAGNOSTIC_COMPLETED_OFFLINE_SCORING_PENDING'},
            'terminal':{'state':'COMPLETE'},'phases':[{'name':a,'progress':{'saved':48},
            'evaluation_complete':{'state':'COMPLETED','records':48}} for a in P.ARMS]}
        s=P.project(source,1001)
        self.assertEqual(s['percent'],100)
        self.assertTrue(s['collection_complete'])
        self.assertEqual(s['promotion_status'],'NOT_AUTHORIZED')
        self.assertEqual(s['evaluation_status'],'NOT_ESTABLISHED')

    def test_bad_counts_duplicates_and_foreign_phases_rejected(self):
        for bad in (True,49,-1,3.5):
            source=self.source();source['phases'][0]['progress']['saved']=bad
            with self.assertRaises(ValueError):P.project(source,1001)
        source=self.source();source['phases'].append(copy.deepcopy(source['phases'][0]))
        with self.assertRaises(ValueError):P.project(source,1001)
        source=self.source();source['phases'][0]['name']='private_other_run'
        with self.assertRaises(ValueError):P.project(source,1001)


if __name__=='__main__':unittest.main(verbosity=2)
