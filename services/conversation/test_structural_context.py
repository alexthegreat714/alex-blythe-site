import json
import unittest
from unittest.mock import patch
import server

class Response:
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,*args):return json.dumps({'message':{'content':json.dumps({'reply':'Review the support assumptions before choosing a structural model.','requirements':{},'equation_ids':['ideal_gas']})}}).encode()

class StructuralContextTests(unittest.TestCase):
    def test_structural_context_preserves_math_and_no_execution(self):
        with patch.object(server.urllib.request,'urlopen',return_value=Response()) as call:
            result=server.infer([{'role':'user','content':'Explain the bracket supports'}],{},structural=True)
        payload=json.loads(call.call_args.args[0].data)
        instructions=' '.join(m['content'] for m in payload['messages'] if m['role']=='system')
        self.assertIn('STRUCTURAL / FEA',instructions)
        self.assertIn('planning-only',instructions)
        self.assertEqual(result['equations'],[])
        self.assertNotIn('tools',payload)

if __name__=='__main__':unittest.main()
