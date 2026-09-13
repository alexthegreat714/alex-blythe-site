import unittest
from analyze_case import array,patch_values,mean_interval

class ExtractionTests(unittest.TestCase):
    def test_scalar(self):self.assertEqual(array('internalField nonuniform List<scalar> 3 (1 2 3);'),[1,2,3])
    def test_vector(self):self.assertEqual(array('internalField nonuniform List<vector> 2 ((1 2 3)(4 5 6));'),[[1,2,3],[4,5,6]])
    def test_bad_count(self):
        with self.assertRaises(ValueError):array('internalField nonuniform List<scalar> 3 (1 2);')
    def test_uniform(self):self.assertEqual(array('internalField uniform 3;'),[3])
    def test_patch(self):self.assertEqual(patch_values('wall { type calculated; value nonuniform List<scalar> 2 (1 2); }','wall'),[1,2])
    def test_no_missing_zero(self):self.assertIsNone(mean_interval([[0,1],[1,2]],1,0,2))
    def test_trapezoid(self):self.assertAlmostEqual(mean_interval([[0,0],[1,1],[2,2]],1,.5,1.5),1)
    def test_unequal_spacing(self):self.assertAlmostEqual(mean_interval([[0,0],[.2,.2],[2,2]],1,0,2),1)
    def test_missing_patch(self):
        with self.assertRaises(ValueError):patch_values('wall { type zeroGradient; }','wall')
if __name__=='__main__':unittest.main()
