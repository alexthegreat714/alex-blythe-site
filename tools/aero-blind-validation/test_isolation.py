"""Fast configuration-regression tests; real Docker proof is retained separately."""
import copy,json,tempfile,unittest
from pathlib import Path
from isolation import inspect_solver

class IsolationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();p=Path(self.tmp.name);self.input=p/'input.json';self.input.write_text('{}');self.out=p/'out';self.out.mkdir()
        self.c={'Config':{'User':'10001:10001'},'HostConfig':{'NetworkMode':'none','ReadonlyRootfs':True,'CapDrop':['ALL'],'SecurityOpt':['no-new-privileges'],'Privileged':False,'DeviceRequests':None,'PidsLimit':128,'Memory':2*1024**3,'NanoCpus':2*10**9},'Mounts':[{'Destination':'/input/input.json','Type':'bind','RW':False},{'Destination':'/work','Type':'bind','RW':True}]}
    def tearDown(self):self.tmp.cleanup()
    def test_approved_layout(self):self.assertEqual(inspect_solver(self.c,self.input,self.out)['network_mode'],'none')
    def test_extra_reference_mount_rejected(self):
        self.c['Mounts'].append({'Destination':'/reference','Type':'bind','RW':False})
        with self.assertRaises(AssertionError):inspect_solver(self.c,self.input,self.out)
    def test_writable_input_rejected(self):
        self.c['Mounts'][0]['RW']=True
        with self.assertRaises(AssertionError):inspect_solver(self.c,self.input,self.out)
    def test_external_network_rejected(self):
        self.c['HostConfig']['NetworkMode']='bridge'
        with self.assertRaises(AssertionError):inspect_solver(self.c,self.input,self.out)
    def test_reused_outputs_rejected(self):
        (self.out/'old.txt').write_text('prior context')
        with self.assertRaises(AssertionError):inspect_solver(self.c,self.input,self.out)
    def test_privileged_rejected(self):
        self.c['HostConfig']['Privileged']=True
        with self.assertRaises(AssertionError):inspect_solver(self.c,self.input,self.out)
if __name__=='__main__':unittest.main()
