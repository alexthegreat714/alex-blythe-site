"""Synthetic archive-integrity tests; no Challenge 01 measurements are used."""
import tempfile,unittest,zipfile,json
from pathlib import Path
from protocol import sha,encode
from verify_release import safe_relative,archive

class ReleaseTests(unittest.TestCase):
    def test_unsafe_paths(self):
        for name in ('../key','/root/file','C:/private','x\\file','foo/../bar',''):
            with self.assertRaises(ValueError):safe_relative(name)
    def test_nested_path(self):self.assertEqual(str(safe_relative('case/system/controlDict')),'case/system/controlDict')
    def test_archive_integrity(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.zip';data=b'SYNTHETIC UNIT FIXTURE ONLY'
            manifest={'case':'synthetic','files':[{'path':'case/field','size':len(data),'sha256':sha(data)}]}
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('case/field',data);z.writestr('archive-manifest.json',encode(manifest))
            self.assertEqual(archive(p,'synthetic')['files'],1)
            with self.assertRaises(ValueError):archive(p,'wrong-label')
    def test_changed_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.zip'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('field',b'altered');z.writestr('archive-manifest.json',encode({'case':'synthetic','files':[{'path':'field','size':7,'sha256':sha(b'correct')}]}))
            with self.assertRaises(ValueError):archive(p)
    def test_unlisted_files_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.zip'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('extra',b'unit test');z.writestr('archive-manifest.json',encode({'case':'synthetic','files':[]}))
            with self.assertRaises(ValueError):archive(p)
    def test_duplicate_files_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.zip'
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                with zipfile.ZipFile(p,'w') as z:
                    z.writestr('duplicate',b'a');z.writestr('duplicate',b'b')
            with self.assertRaises(ValueError):archive(p)

if __name__=='__main__':unittest.main()
