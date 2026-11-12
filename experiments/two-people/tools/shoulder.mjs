// a point on top of a body's shoulder (at rest): the skin's highest point above the line from the collarbone's root
// to the shoulder joint, at a share of the way; and the skin's normal there
import { createEngine } from '../../../engine/src/engine.js';
import { read } from '../../../engine/check/node-read.mjs';
import { getV } from '../../../engine/src/math.js';
const E = await createEngine({ read });
export async function shoulderTop(id, side = 'Right', share = 0.6) {
  const b = await E.body(id), sk = b.skeleton;
  const c = getV(b.joints, sk.index[side + 'Shoulder']), a = getV(b.joints, sk.index[side + 'Arm']);
  const m = c.map((v, i) => v + (a[i] - v) * share);
  let best = -1, by = -Infinity;
  for (let i = 0; i < b.N; i++) {
    const x = b.positions[i * 3], y = b.positions[i * 3 + 1], z = b.positions[i * 3 + 2];
    if (Math.hypot(x - m[0], z - m[2]) < 0.02 && y > by && y < m[1] + 0.2) { by = y; best = i; }
  }
  return { body: b, joint: side + 'Shoulder', point: [b.positions[best * 3], by, b.positions[best * 3 + 2]], m };
}
// node tools/shoulder.mjs top <body> [side]  |  node tools/shoulder.mjs surface <body> <side> <share> <angle> <out metres>
// (surface: the skin's point, and that point pushed `out` along the RAY — not along the skin's normal)
if (process.argv[2] === 'top') { const r = await shoulderTop(process.argv[3], process.argv[4] || 'Right'); console.log(r.point.map(v => +v.toFixed(4)), 'joint line', r.m.map(v => +v.toFixed(4))); }
if (process.argv[2] === 'surface') {
  const [, , , id, side, share, angle, out] = process.argv;
  const r = await shoulderSurface(id, side, +share, +angle);
  console.log(JSON.stringify({ skin: r.point.map(v => +v.toFixed(4)), out: r.point.map((v, i) => +(v + r.dir[i] * +out).toFixed(4)) }));
}
// the skin's point where a ray from inside the shoulder (on the collarbone's line, at a share of the way out) leaves
// the body, going up and back at an angle (0: straight up; π/2: straight back)
export async function shoulderSurface(id, side = 'Right', share = 0.85, angle = Math.PI / 4) {
  const b = await E.body(id), sk = b.skeleton;
  const c = getV(b.joints, sk.index[side + 'Shoulder']), a = getV(b.joints, sk.index[side + 'Arm']);
  const m = c.map((v, i) => v + (a[i] - v) * share), d = [0, Math.cos(angle), -Math.sin(angle)];
  let best = -1, bt = -Infinity;
  for (let i = 0; i < b.N; i++) {
    const v = [b.positions[i * 3] - m[0], b.positions[i * 3 + 1] - m[1], b.positions[i * 3 + 2] - m[2]];
    const t = v[0] * d[0] + v[1] * d[1] + v[2] * d[2];
    if (t <= 0 || t > 0.2) continue;
    const off = Math.hypot(v[0] - t * d[0], v[1] - t * d[1], v[2] - t * d[2]);
    if (off < 0.012 && t > bt) { bt = t; best = i; }
  }
  return { point: [b.positions[best * 3], b.positions[best * 3 + 1], b.positions[best * 3 + 2]], dir: d, depth: bt };
}
