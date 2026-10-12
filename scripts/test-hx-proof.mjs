import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
const root = new URL('../public/demos/aero/first-principles-hx-v1/', import.meta.url);
const read = (name) => fs.readFileSync(new URL(name, root));
const result = JSON.parse(read('results.json'));
assert.equal(result.tests.run, 9);
assert.equal(result.tests.failures, 0);
assert.equal(result.tests.errors, 0);
assert.equal(result.physical_validation, 'NOT_ESTABLISHED');
assert.equal(result.production_solver_used, false);
assert.equal(result.GPU_required, false);
assert.ok(Math.abs(result.analytical_inner.hoop_Pa/1e6-21.047619047619)<1e-8);
assert.ok(result.pressure_fe.at(-1).gauss_stress_relative_L2_error<0.001);
const receipt = JSON.parse(read('runtime-verification.json'));
assert.equal(receipt.desktop_model.calculation, 'FAIL');
assert.equal(receipt.private_page.page_3090_execution, 'NOT_ESTABLISHED');
assert.equal(receipt.public_notebook.private_backend_exposed, false);
assert.equal(read('proof.pdf').subarray(0, 5).toString(), '%PDF-');
const manifest = JSON.parse(read('manifest.json'));
for (const entry of manifest.files) {
  const data = read(entry.path);
  assert.equal(data.length, entry.bytes);
  assert.equal(crypto.createHash('sha256').update(data).digest('hex'), entry.sha256);
  const built = fs.readFileSync(new URL(`../dist/demos/aero/first-principles-hx-v1/${entry.path}`, import.meta.url));
  assert.equal(crypto.createHash('sha256').update(built).digest('hex'), entry.sha256);
}
for (const name of ['README.md', 'proof.tex', 'inputs.json', 'runtime-verification.json', 'results.json', 'verify.py']) {
  assert.doesNotMatch(read(name).toString(), /AEGIS_LOCAL_TOKEN|127\.0\.0\.1|C:\\Users\\|D:\\Aero\\|29[,.]?201|GPU-17b679/);
}
const html = fs.readFileSync(new URL('../dist/software/aero/first-principles/index.html', import.meta.url), 'utf8');
assert.ok((html.match(/class="katex"/g)||[]).length>=10);
assert.match(html, /First principles before FEA/);
assert.match(html, /sources\.zip/);
assert.match(html, /Hardware safety: NOT_ESTABLISHED/);
assert.doesNotMatch(html, /katex-error|http:\/\/127\.0\.0\.1/);
assert.match(fs.readFileSync(new URL('../dist/software/aero/index.html', import.meta.url),'utf8'), /\/software\/aero\/first-principles\//);
const archive = fs.readFileSync(new URL('../public/research/road-to-type-2-working-draft-2024-11-23.md', import.meta.url), 'utf8');
const count = (text) => [...text.replace(/\r\n/g, '\n').matchAll(/^# (\d+)\.  (You|ChatGPT)\n([\s\S]*?)(?=\n---\n# \d+\.  |(?![\s\S]))/gm)].length;
assert.equal(count(archive), 160);
assert.equal(count(archive.replace(/\r?\n/g, '\r\n')), 160);
assert.equal(count(archive.replace(/\r\n/g, '\n')), 160);
console.log(`PASS: nine calculated tests, ${manifest.files.length} artifact hashes, public scope/privacy checks, equation rendering, Aero discovery link, archive LF/CRLF parity.`);
