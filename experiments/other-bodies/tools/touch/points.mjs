// The points touched, on the touched person's body at rest (its own rest space; carried by a joint), for other bodies.
//   node tools/touch/points.mjs
// К2's two points on the woman's right shoulder are shoulder.mjs's shoulderSurface pushed 2 cm out along the ray
// (found by search: the touch at share 1.1, angle 0.45 — 1.9 mm from К2's point; the slide at share 1.4, angle 0.2 —
// exact). The same two settings give the points on another body's shoulder. A point on the upper arm (for one too
// short to reach the shoulder): where a ray from the upper arm's axis, `share` of the way from the shoulder joint to
// the elbow, going out and back at `angle` (0: straight out to the side; π/2: straight back), leaves the skin, 2 cm out.
import { createEngine } from '../../../../engine/src/engine.js';
import { read } from '../../../../engine/check/node-read.mjs';
import { getV, normalize, sub, cross } from '../../../../engine/src/math.js';
import { shoulderSurface } from './shoulder.mjs';
const E = await createEngine({ read });
const r4 = p => p.map(v => +v.toFixed(4));
const out2 = (r, d = 0.02) => r4(r.point.map((v, i) => v + d * r.dir[i]));

export async function armSurface(id, side = 'Right', share = 0.3, angle = 1.0) {
  const b = await E.body(id), sk = b.skeleton;
  const s = getV(b.joints, sk.index[side + 'Arm']), e = getV(b.joints, sk.index[side + 'ForeArm']);
  const m = s.map((v, i) => v + (e[i] - v) * share);
  const axis = normalize(sub(e, s)), sx = side === 'Right' ? -1 : 1;
  // out: away from the body, square to the arm; back: −z
  const outw = normalize(cross(cross(axis, [sx, 0, 0]), axis).map(v => -v));
  const d = normalize(outw.map((v, i) => v * Math.cos(angle) + [0, 0, -1][i] * Math.sin(angle)));
  let best = -1, bt = -Infinity;
  for (let i = 0; i < b.N; i++) {
    const v = [b.positions[i * 3] - m[0], b.positions[i * 3 + 1] - m[1], b.positions[i * 3 + 2] - m[2]];
    const t = v[0] * d[0] + v[1] * d[1] + v[2] * d[2];
    if (t <= 0 || t > 0.15) continue;
    const off = Math.hypot(v[0] - t * d[0], v[1] - t * d[1], v[2] - t * d[2]);
    if (off < 0.012 && t > bt) { bt = t; best = i; }
  }
  return { point: [b.positions[best * 3], b.positions[best * 3 + 1], b.positions[best * 3 + 2]], dir: d, depth: bt, joint: side + 'Arm' };
}

if (process.argv[1].endsWith('points.mjs')) {
  for (const id of ['moood-woman', 'anny-C-pear']) {
    console.log(id, 'touch (RightShoulder)', out2(await shoulderSurface(id, 'Right', 1.1, 0.45)), 'slide (RightShoulder)', out2(await shoulderSurface(id, 'Right', 1.4, 0.2)));
  }
  for (const [sh, a] of [[0.3, 1.0], [0.35, 1.2], [0.25, 0.9]]) console.log('moood-woman upper arm', sh, a, '(RightArm)', out2(await armSurface('moood-woman', 'Right', sh, a)));
}
