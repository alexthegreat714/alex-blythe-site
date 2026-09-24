import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'public/demos/aero/hardware-benchmark-2026-09-24'
SLUG = 'rtx-3090-vs-gb10-aero-inference-benchmark'
spec = importlib.util.spec_from_file_location('exporter', ROOT/'tools/export-hardware-benchmark.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)

class PublicationTests(unittest.TestCase):
    def test_manifest_matches(self):
        manifest = json.loads((BASE/'SHA256_MANIFEST.json').read_text())['files']
        self.assertEqual(len(manifest), 13)
        for name, digest in manifest.items():
            self.assertEqual(hashlib.sha256((BASE/name).read_bytes()).hexdigest(), digest, name)

    def test_private_paths_rejected(self):
        for value in ['C:/Users/private', 'D:\\private', 'http://127.0.0.1:1234', 'gx10-a448']:
            with self.assertRaises(ValueError): exporter.safe(value)
        self.assertEqual(exporter.safe('http://www.w3.org/2000/svg'), 'http://www.w3.org/2000/svg')

    def test_selected_fields_only(self):
        for suite, count in [('cache-neutral',20),('warm-cache',49)]:
            rows=json.loads((BASE/f'{suite}-results.json').read_text())['rows']
            self.assertEqual(len(rows),count)
            for row in rows:
                self.assertEqual(row['n'],5)
                self.assertTrue(set(row)<=exporter.ALLOWED)
                self.assertIn(row['system_id'], ('3090','spark'))

    def test_headline_numbers(self):
        rows=json.loads((BASE/'cache-neutral-results.json').read_text())['rows']
        expected={'3090':15.25,'spark':27.93}
        for system, seconds in expected.items():
            row=next(x for x in rows if x['system_id']==system and x['workload']=='agent_loop')
            self.assertAlmostEqual(row['wall_seconds_median'],seconds,places=2)

    def test_built_page_links_and_charts(self):
        html=(ROOT/f'dist/software/notes/{SLUG}/index.html').read_text(encoding='utf-8')
        images=re.findall(r'<img[^>]+src="([^"]+)"',html)
        self.assertEqual(len(images),7)
        for path in re.findall(r'(?:href|src)="(/demos/aero/hardware-benchmark-2026-09-24/[^"#]+)"',html):
            self.assertTrue((ROOT/'dist'/path.lstrip('/')).exists(),path)
        for page in ['software/aero','software/aero/evidence','software/aero/evidence/benchmarks','software']:
            self.assertIn(SLUG,(ROOT/f'dist/{page}/index.html').read_text(encoding='utf-8'))

    def test_export_is_static_and_sanitized(self):
        for file in BASE.rglob('*'):
            if file.is_file(): exporter.safe(file.read_text(encoding='utf-8'))
        for file in (BASE/'charts').glob('*.svg'):
            self.assertFalse(re.search(r'<script|foreignObject',file.read_text(),re.I))

    def test_chart_claim_and_mobile_inspection(self):
        chart=(BASE/'charts/task_wall_time.svg').read_text()
        self.assertIn('Model response and mocked-loop time',chart)
        self.assertNotIn('end-to-end',chart)
        for value in ['5.125','7.436','15.250','27.932','15.440','30.596','33.882','70.298']:
            self.assertIn(value,chart)
        report=(ROOT/f'src/content/research/{SLUG}.md').read_text(encoding='utf-8')
        self.assertEqual(report.count('class="benchmark-chart" tabindex="0"'),7)

if __name__=='__main__': unittest.main()
