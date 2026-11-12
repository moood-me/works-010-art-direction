// a point on a body's trunk at rest: where a ray from a joint (raised by dy) going a given way leaves the trunk's skin
// (only vertices the trunk's joints carry), and that point pushed out along the ray
//   node tools/trunkpoint.mjs <body> <joint> <dy> <dx,dy,dz direction> <out metres>
import { createEngine } from '../../../engine/src/engine.js';
import { read } from '../../../engine/check/node-read.mjs';
import { getV } from '../../../engine/src/math.js';
const [id, joint, dy, dirs, out] = process.argv.slice(2);
const E = await createEngine({ read });
const b = await E.body(id), sk = b.skeleton, o = getV(b.joints, sk.index[joint]); o[1] += +dy;
let d = dirs.split(',').map(Number); const l = Math.hypot(...d); d = d.map(v => v / l);
const trunk = new Set(['Hips', 'Spine1', 'Spine2', 'Chest', 'Neck1', 'LeftShoulder', 'RightShoulder'].map(n => sk.index[n]));
let best = -1, bt = 0;
for (let i = 0; i < b.N; i++) {
  if (!trunk.has(b.skin.joints[i * 4]) || b.skin.weights[i * 4] < 0.5) continue;
  const v = [b.positions[i * 3] - o[0], b.positions[i * 3 + 1] - o[1], b.positions[i * 3 + 2] - o[2]], t = v[0] * d[0] + v[1] * d[1] + v[2] * d[2];
  const off = Math.hypot(v[0] - t * d[0], v[1] - t * d[1], v[2] - t * d[2]);
  if (t > 0 && off < 0.015 && t > bt) { bt = t; best = i; }
}
const p = [b.positions[best * 3], b.positions[best * 3 + 1], b.positions[best * 3 + 2]];
console.log(JSON.stringify({ skin: p.map(v => +v.toFixed(4)), out: p.map((v, k) => +(v + d[k] * +out).toFixed(4)) }));
