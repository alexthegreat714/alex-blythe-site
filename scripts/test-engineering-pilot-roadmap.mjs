import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

const route = '/software/notes/aero-engineering-pilot-roadmap/';
const read = (p) => readFileSync(resolve(p), 'utf8');
const source = read('src/content/research/aero-engineering-pilot-roadmap.md');
const page = read(`dist${route}index.html`);
for (const phrase of ['NOT_IMPLEMENTED_AS_DESCRIBED', 'NOT_ESTABLISHED', 'SYNTHETIC', 'MOCKED', 'First bounded milestone', 'Return here if the project drifts', 'Luna', 'GX10', '100–200']) {
  assert.ok(source.includes(phrase), `Missing planning safeguard/content: ${phrase}`);
  assert.ok(page.includes(phrase), `Missing built content: ${phrase}`);
}
assert.ok(!/(?:127\.0\.0\.1|host\.docker\.internal|[CD]:[\\/]|AEGIS_LOCAL_TOKEN)/i.test(source), 'Private route/path/token marker');
for (const p of ['dist/software/aero/index.html', 'dist/software/notes/aero-future-work/index.html']) {
  assert.ok(read(p).includes(`href="${route}"`), `Missing navigation: ${p}`);
}
for (const match of source.matchAll(/\]\((\/[^)#]+)(?:#[^)]*)?\)/g)) {
  assert.ok(existsSync(resolve('dist', `.${match[1]}`, 'index.html')), `Missing linked route: ${match[1]}`);
}
for (const anchor of ['the-goal-to-return-to', 'work-breakdown-and-ownership', 'first-bounded-milestone', 'return-here-if-the-project-drifts']) {
  assert.ok(page.includes(`id="${anchor}"`), `Missing jump target: ${anchor}`);
}
console.log('PASS: roadmap content, status boundaries, public-data markers, entry links, linked routes, and section anchors.');
