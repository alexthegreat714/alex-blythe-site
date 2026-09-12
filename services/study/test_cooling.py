import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import api
import cooling as c

class CoolingTests(unittest.TestCase):
    def test_reference_decision_and_energy(self):
        r=c.calculate(c.DEFAULTS)
        self.assertEqual(r['selected_layout'],'B');self.assertTrue(r['checks_passed'])
        self.assertAlmostEqual(r['bulk_rise_k'],100/(997*1e-6*4180))
        self.assertGreater(r['layouts'][0]['guard_pressure_pa'],2000)
        self.assertGreater(r['layouts'][2]['guard_wall_c'],72)
    def test_independent_pressure_reference(self):
        v=c.calculate(c.DEFAULTS)['layouts'][1]
        self.assertAlmostEqual(v['pressure_pa'],.00089*.5*(.5e-6)*8/(math.pi*.001**4))
    def test_radial_refinement(self):
        values=[c.radial_verification(n) for n in (16,32,64,128)]
        for a,b in zip(values,values[1:]):self.assertLess(b['relative_error_pct'],a['relative_error_pct']/3)
        self.assertLess(values[-1]['relative_error_pct'],.002)
    def test_rejects_missing_nan_bool_commands(self):
        for data in ({},{**c.DEFAULTS,'length_mm':None},{**c.DEFAULTS,'heat_w':float('nan')},{**c.DEFAULTS,'flow_ml_s':True},{**c.DEFAULTS,'command':'run'}):
            with self.assertRaises(ValueError):c.validate(data)
    def test_no_feasible_is_not_a_recommendation(self):
        r=c.calculate({**c.DEFAULTS,'wall_limit_c':40});self.assertIsNone(r['selected_layout'])
        r=c.calculate({**c.DEFAULTS,'available_width_mm':4});self.assertIsNone(r['selected_layout'])
    def test_flow_trade_is_not_free_cooling(self):
        a=c.calculate(c.DEFAULTS)['layouts'][1];b=c.calculate({**c.DEFAULTS,'flow_ml_s':2})['layouts'][1]
        self.assertAlmostEqual(b['pressure_pa'],2*a['pressure_pa']);self.assertLess(b['wall_c'],a['wall_c'])
    def test_kind_is_bound_to_idempotency_key(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(api,'DATA',Path(directory)),patch.object(api,'worker_ready',return_value=True):
            key='a'*36;job=api.enqueue('192.0.2.21',key,c.DEFAULTS,'cooling')
            self.assertTrue((Path(directory)/job/'kind.json').exists())
            self.assertEqual(job,api.enqueue('192.0.2.21',key,c.DEFAULTS,'cooling'))
            with self.assertRaises(ValueError):api.enqueue('192.0.2.21',key,api.DEFAULTS)

if __name__=='__main__':unittest.main()
