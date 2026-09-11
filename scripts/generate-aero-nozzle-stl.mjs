import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

const output = resolve('public/demos/aero/shared/nozzle-cutaway.stl');
const axialSegments = 72;
const angularSegments = 96;
const thetaStart = Math.PI / 6;
const thetaEnd = Math.PI * 2 - Math.PI / 6;
const wall = 0.004;

const smoothstep = (t) => t * t * (3 - 2 * t);
const radiusAt = (x) => {
  if (x <= 0) return 0.020 + (0.008 - 0.020) * smoothstep((x + 0.045) / 0.045);
  return 0.008 + (0.024 - 0.008) * smoothstep(x / 0.110);
};
const xAt = (i) => i <= axialSegments / 2
  ? -0.045 + (i / (axialSegments / 2)) * 0.045
  : ((i - axialSegments / 2) / (axialSegments / 2)) * 0.110;
const point = (x, r, theta) => [x, r * Math.sin(theta), r * Math.cos(theta)];
const triangles = [];
const add = (a, b, c) => triangles.push([a, b, c]);

for (let i = 0; i < axialSegments; i += 1) {
  const x0 = xAt(i), x1 = xAt(i + 1);
  const inner0 = radiusAt(x0), inner1 = radiusAt(x1);
  const outer0 = inner0 + wall, outer1 = inner1 + wall;
  for (let j = 0; j < angularSegments; j += 1) {
    const t0 = thetaStart + (j / angularSegments) * (thetaEnd - thetaStart);
    const t1 = thetaStart + ((j + 1) / angularSegments) * (thetaEnd - thetaStart);
    const oi0 = point(x0, outer0, t0), oi1 = point(x1, outer1, t0);
    const oj0 = point(x0, outer0, t1), oj1 = point(x1, outer1, t1);
    add(oi0, oi1, oj1); add(oi0, oj1, oj0);
    const ii0 = point(x0, inner0, t0), ii1 = point(x1, inner1, t0);
    const ij0 = point(x0, inner0, t1), ij1 = point(x1, inner1, t1);
    add(ii0, ij1, ii1); add(ii0, ij0, ij1);
  }
}

for (const [x, flip] of [[-0.045, false], [0.110, true]]) {
  const inner = radiusAt(x), outer = inner + wall;
  for (let j = 0; j < angularSegments; j += 1) {
    const t0 = thetaStart + (j / angularSegments) * (thetaEnd - thetaStart);
    const t1 = thetaStart + ((j + 1) / angularSegments) * (thetaEnd - thetaStart);
    const a = point(x, inner, t0), b = point(x, outer, t0), c = point(x, outer, t1), d = point(x, inner, t1);
    if (flip) { add(a, c, b); add(a, d, c); } else { add(a, b, c); add(a, c, d); }
  }
}

for (const [theta, flip] of [[thetaStart, true], [thetaEnd, false]]) {
  for (let i = 0; i < axialSegments; i += 1) {
    const x0 = xAt(i), x1 = xAt(i + 1);
    const a = point(x0, radiusAt(x0), theta);
    const b = point(x0, radiusAt(x0) + wall, theta);
    const c = point(x1, radiusAt(x1) + wall, theta);
    const d = point(x1, radiusAt(x1), theta);
    if (flip) { add(a, c, b); add(a, d, c); } else { add(a, b, c); add(a, c, d); }
  }
}

const normal = (a, b, c) => {
  const u = b.map((v, i) => v - a[i]);
  const v = c.map((n, i) => n - a[i]);
  const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
  const length = Math.hypot(...n) || 1;
  return n.map((value) => value / length);
};
const binary = Buffer.alloc(84 + triangles.length * 50);
binary.write('Aero nozzle cutaway / metres / parametric generated', 0, 'ascii');
binary.writeUInt32LE(triangles.length, 80);
triangles.forEach((triangle, triangleIndex) => {
  let offset = 84 + triangleIndex * 50;
  const n = normal(...triangle);
  [...n, ...triangle.flat()].forEach((value) => {
    binary.writeFloatLE(value, offset);
    offset += 4;
  });
  binary.writeUInt16LE(0, offset);
});
mkdirSync(dirname(output), { recursive: true });
writeFileSync(output, binary);
console.log(JSON.stringify({ output, triangles: triangles.length }));
