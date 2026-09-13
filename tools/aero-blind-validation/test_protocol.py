"""Synthetic unit fixtures only: never represent a scientific Challenge 01 run."""
import copy,json,tempfile,unittest,subprocess
from pathlib import Path
from protocol import Challenge,FIELDS,sha,compare,validate_criteria,check_key_location

REF=b'quantity,station,value,uncertainty\nCL,a,1,0.1\nCL,b,2,0.1\nCD,a,0.1,\nCD,b,0.2,\n'
INPUT={'benchmark_id':'SYNTHETIC_TEST_ONLY','source_citation':'synthetic','source_version':'test','geometry':'test','flow_conditions':{'test':1},'facility':'none','quantities':['CL','CD'],'stations':['a','b'],'permitted_uncertainty':'unknown'}
KEY=b'k'*32
def criteria(run):
    c={k:'synthetic-test-only' for k in FIELDS};c.update(status='READY_TO_FREEZE',benchmark_id=INPUT['benchmark_id'],input_sha256=sha((run.root/'input.json').read_bytes()),sealed_reference_sha256=sha((run.root/'reference.enc').read_bytes()),quantities=['CL','CD'],stations=['a','b'],mesh_levels=['a','b','c'],comparison_metrics=['rmse','max_absolute_error'],acceptance_thresholds={q:{'rmse':.05,'max_absolute_error':.1} for q in ['CL','CD']},experimental_uncertainty={'gate_policy':'descriptive_only_no_threshold_widening'})
    return c
def prediction():return {'values':[{'quantity':q,'station':s,'value':v} for q,s,v in [('CL','a',1),('CL','b',2),('CD','a',.1),('CD','b',.2)]],'numerical_status':'PASS','engineering_disposition':'SYNTHETIC TEST ONLY'}

class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.run=Challenge(Path(self.tmp.name)/'run')
        self.run.seal(INPUT,REF,KEY,{'custodian_id':'unit-test','reviewed_no_answer_material':True,'license_clearance':'REDISTRIBUTION_APPROVED'})
    def tearDown(self):self.tmp.cleanup()
    def test_seal_hides_answer(self):
        self.assertNotIn(REF,(self.run.root/'reference.enc').read_bytes());self.assertFalse((self.run.root/'reference.csv').exists())
    def test_early_unseal_rejected(self):
        with self.assertRaises(ValueError):self.run.unseal(KEY)
    def test_unanchored_start_rejected(self):
        self.run.freeze_criteria(criteria(self.run))
        with self.assertRaises(ValueError):self.run.start({})
    def test_input_tamper(self):
        (self.run.root/'input.json').write_text('{}')
        with self.assertRaises(ValueError):self.run.freeze_criteria(criteria(self.run))
    def test_draft_rejected(self):
        c=criteria(self.run);c['status']='DRAFT'
        with self.assertRaises(ValueError):self.run.freeze_criteria(c)
    def test_null_criterion(self):
        c=criteria(self.run);c['flow_conditions']=None
        with self.assertRaises(ValueError):validate_criteria(c)
    def test_negative_nan_threshold(self):
        for v in [-1,float('nan'),True]:
            c=criteria(self.run);c['acceptance_thresholds']['CL']['rmse']=v
            with self.assertRaises(ValueError):validate_criteria(c)
    def test_all_outcomes(self):
        c=criteria(self.run);p=prediction();self.assertEqual(compare(p,REF,c)['status'],'PASS')
        p['values'][0]['value']=5;self.assertEqual(compare(p,REF,c)['status'],'MIXED')
        p['values'][2]['value']=5;self.assertEqual(compare(p,REF,c)['status'],'FAIL')
    def test_missing_point(self):
        p=prediction();p['values'].pop()
        with self.assertRaises(ValueError):compare(p,REF,criteria(self.run))
    def test_duplicate_point(self):
        p=prediction();p['values'].append(p['values'][0])
        with self.assertRaises(ValueError):compare(p,REF,criteria(self.run))
    def test_numerical_failure_not_rescued(self):
        p=prediction();p['numerical_status']='FAIL';r=compare(p,REF,criteria(self.run));self.assertEqual(r['experimental_comparison'],'PASS');self.assertEqual(r['status'],'FAIL')
    def test_unknown_uncertainty(self):
        r=compare(prediction(),REF,criteria(self.run));self.assertIsNone(r['all_points'][-1]['uncertainty_overlap'])
    def test_full_git_anchored_sequence(self):
        # Local temporary bare remote tests Git mechanics, not a public timestamp.
        repo=Path(self.tmp.name);remote=repo/'remote.git'
        def git(*args):return subprocess.check_output(['git',*args],cwd=repo,stderr=subprocess.DEVNULL,text=True).strip()
        git('init','--bare',str(remote));git('init','-b','main');git('config','user.name','Synthetic Test');git('config','user.email','test@example.invalid');git('config','core.autocrlf','false');git('remote','add','origin',str(remote))
        with self.assertRaises(ValueError):check_key_location(repo/'not-yet-created',repo/'secret.key')
        self.run.freeze_criteria(criteria(self.run))
        def commit(message):
            git('add','run');git('commit','-m',message);git('push','origin','main');return git('rev-parse','HEAD')
        self.run.anchor(commit('synthetic preregistration'))
        self.run.start({'predictor_id':'test','supervisor_id':'test',**dict.fromkeys(['fresh_predictor_context','reference_not_mounted','network_disabled','rag_disabled','key_not_available'],True)})
        p=prediction();(self.run.root/'test-evidence.txt').write_text('SYNTHETIC ONLY')
        roles=['requirements','first_principles','geometry','topology','mesh','mesh_diagnostics','deck','runtime','solver_log','residuals','conservation','wall_diagnostics','grid_study','extracted_values']
        p['evidence_manifest']={r:{'path':'test-evidence.txt','sha256':sha((self.run.root/'test-evidence.txt').read_bytes())} for r in roles}
        self.run.freeze_prediction(p)
        with self.assertRaises(ValueError):self.run.unseal(KEY)
        self.run.anchor(commit('synthetic prediction'))
        with self.assertRaises(Exception):self.run.unseal(b'x'*32)
        self.run.unseal(KEY);self.assertEqual(self.run.comparison()['status'],'PASS');self.run.anchor(commit('synthetic reveal'))
        self.assertEqual(self.run.state()['stage'],'COMPARED_ANCHORED')
        from render_result import render
        output=render(self.run.root)
        self.assertTrue((output/'paper.tex').is_file());self.assertTrue((output/'comparison-0.pdf').is_file())

if __name__=='__main__':unittest.main()
