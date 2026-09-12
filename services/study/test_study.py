import json
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
import core
import api
import worker
import paper


class StudyTests(unittest.TestCase):
    def test_paper_escapes_tex_controls(self):
        self.assertEqual(paper.tex('A&B_1%'),r'A\&B\_1\%')
        self.assertNotIn(r'\input{',paper.tex(r'\input{/secret}'))

    def test_pdf_failure_is_not_a_completed_study(self):
        import subprocess
        with tempfile.TemporaryDirectory() as temporary,patch('paper.subprocess.run',side_effect=subprocess.TimeoutExpired('pdflatex',35)):
            with self.assertRaises(subprocess.TimeoutExpired):paper.compile_paper(temporary)
        with tempfile.TemporaryDirectory() as temporary,patch('paper.subprocess.run') as run:
            run.return_value.returncode=1
            with self.assertRaises(RuntimeError):paper.compile_paper(temporary)
            self.assertIn('-no-shell-escape',run.call_args.args[0])
    def test_command_failure_is_terminal_and_scratch_is_removed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);data=root/'data';work=root/'work';data.mkdir();work.mkdir()
            job=data/('a'*48);job.mkdir();core.atomic_json(job/'input.json',core.DEFAULTS)
            with patch.object(worker,'WORK',work),patch.object(worker,'command',side_effect=TimeoutError('Injected timeout test')):
                worker.execute(job)
            status=json.loads((job/'status.json').read_text())
            self.assertEqual(status['state'],'failed');self.assertEqual(status['completed'],0)
            self.assertFalse((work/job.name).exists());self.assertTrue((job/'failure.zip').exists())
            self.assertFalse((job/'result.json').exists())

    def test_restart_marks_interrupted_failed_but_preserves_queue_and_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);data=root/'data';work=root/'work';data.mkdir();work.mkdir()
            for name,state in [('a','running'),('b','queued'),('c','complete')]:
                job=data/(name*48);job.mkdir();core.atomic_json(job/'status.json',{'state':state,'updated_at':1})
            (work/('a'*48)).mkdir();(work/'unrelated').mkdir()
            with patch.object(worker,'DATA',data),patch.object(worker,'WORK',work):worker.recover_interrupted()
            self.assertEqual(json.loads((data/('a'*48)/'status.json').read_text())['state'],'failed')
            self.assertEqual(json.loads((data/('b'*48)/'status.json').read_text())['state'],'queued')
            self.assertEqual(json.loads((data/('c'*48)/'status.json').read_text())['state'],'complete')
            self.assertFalse((work/('a'*48)).exists());self.assertTrue((work/'unrelated').exists())

    def test_queue_limit_and_global_budget(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(api,'DATA',Path(temporary)),patch.object(api,'worker_ready',return_value=True):
            ids=[api.enqueue(f'192.0.2.{i}',str(uuid.uuid4()),core.DEFAULTS) for i in range(1,4)]
            with self.assertRaises(OverflowError):api.enqueue('192.0.2.4',str(uuid.uuid4()),core.DEFAULTS)
            for job in ids:core.atomic_json(Path(temporary)/job/'status.json',{'state':'complete'})
            for i in range(4,7):api.enqueue(f'192.0.2.{i}',str(uuid.uuid4()),core.DEFAULTS)
            with self.assertRaises(OverflowError):api.enqueue('192.0.2.7',str(uuid.uuid4()),core.DEFAULTS)
    def test_reference_and_cubic_gap_scaling(self):
        result = core.brief(core.DEFAULTS)
        self.assertAlmostEqual(result['variants'][1]['analytical_pa'], 60.18)
        self.assertAlmostEqual(result['variants'][0]['analytical_pa'] / result['variants'][1]['analytical_pa'], 1/.75**3)
        self.assertLess(max(v['reynolds'] for v in core.brief({**core.DEFAULTS,'flow_ml_s':40})['variants']), 800)

    def test_reject_unbounded_and_nonnumeric_or_extra_inputs(self):
        for value in (True, None, '2; curl example.com', float('nan'), float('inf'), 0, 4):
            with self.subTest(value=value), self.assertRaises(ValueError):
                core.validate({**core.DEFAULTS, 'gap_mm': value})
        with self.assertRaises(ValueError):
            core.validate({**core.DEFAULTS, 'command':'whoami'})

    def test_idempotency_and_persistent_quota(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(api,'DATA',Path(temporary)), patch.object(api,'worker_ready',return_value=True):
            key = str(uuid.uuid4())
            one=api.enqueue('192.0.2.1',key,core.DEFAULTS)
            self.assertEqual(one,api.enqueue('192.0.2.1',key,core.DEFAULTS))
            with self.assertRaises(ValueError):
                api.enqueue('192.0.2.1',key,{**core.DEFAULTS,'gap_mm':3})
            api.enqueue('192.0.2.1',str(uuid.uuid4()),core.DEFAULTS)
            with self.assertRaises(OverflowError):
                api.enqueue('192.0.2.1',str(uuid.uuid4()),core.DEFAULTS)
            self.assertTrue((Path(temporary)/'quota.sqlite').exists())

    def test_offline_worker_does_not_accept_job(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(api,'DATA',Path(temporary)), patch.object(api,'worker_ready',return_value=False):
            with self.assertRaises(ConnectionError):
                api.enqueue('192.0.2.1',str(uuid.uuid4()),core.DEFAULTS)
            self.assertFalse(any(p.is_dir() for p in Path(temporary).iterdir()))

    def test_inlet_midpoint_flux_is_normalized(self):
        import re
        with tempfile.TemporaryDirectory() as temporary:
            files=core.materialize(temporary,core.DEFAULTS,2,32,16)
            match=re.search(r'List<vector> 16 \( (.*?) \);',files['0/U'],re.S)
            speeds=[float(v) for v in re.findall(r'\(([^ ]+) 0 0\)',match[1])]
            self.assertAlmostEqual(sum(speeds)/16,.1,places=10)
            self.assertNotIn('codedFixedValue',files['0/U'])

if __name__=='__main__':
    unittest.main()
