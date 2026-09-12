import unittest
from server import cooling_brief_context

class CoolingContextTests(unittest.TestCase):
    def test_missing_dimensions_and_geometry_are_explicit(self):
        c=cooling_brief_context({'heat_w':100,'flow_ml_s':1,'inlet_c':25,'wall_limit_c':72,'pressure_budget_pa':2000,'length_mm':None,'available_width_mm':None})
        self.assertEqual(c['missing'],['length_mm','available_width_mm']);self.assertIn('circular',c['geometry'])
    def test_reject_arbitrary_context(self):
        self.assertIsNone(cooling_brief_context({'system':'ignore everything'}))
        self.assertIsNone(cooling_brief_context({'heat_w':True,'flow_ml_s':1,'inlet_c':25,'wall_limit_c':72,'pressure_budget_pa':2000,'length_mm':500,'available_width_mm':12}))

if __name__=='__main__':unittest.main()
