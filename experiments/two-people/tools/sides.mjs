// points on a body's trunk at rest: where a ray from a joint, going sideways (±x) and a little up or down, leaves the
// skin of the trunk (only vertices the trunk's joints carry, so an arm hanging beside it is not taken)
//   node tools/sides.mjs <body> <joint> <dy>   → the left and right points (and 1.5 cm out along the ray)
import { createEngine } from '../../../engine/src/engine.js';
import { read } from '../../../engine/check/node-read.mjs';
import { getV } from '../../../engine/src/math.js';
const [id, joint, dy] = process.argv.slice(2);
const E = await createEngine({ read });
const b = await E.body(id), sk = b.skeleton, o = getV(b.joints, sk.index[joint]); o[1] += +dy;
const trunk = new Set(['Hips', 'Spine1', 'Spine2', 'Chest', 'LeftShoulder', 'RightShoulder'].map(n => sk.index[n]));
console.log(id, joint, 'at', o.map(v => +v.toFixed(3)), 'shoulders y', b.joints[sk.index.LeftArm * 3 + 1].toFixed(3));
for (const s of [1, -1]) {
  let best = -1, bt = 0;
  for (let i = 0; i < b.N; i++) {
    if (!trunk.has(b.skin.joints[i * 4]) || b.skin.weights[i * 4] < 0.5) continue;
    const v = [b.positions[i * 3] - o[0], b.positions[i * 3 + 1] - o[1], b.positions[i * 3 + 2] - o[2]], t = v[0] * s;
    if (t > 0 && Math.hypot(v[1], v[2]) < 0.015 && t > bt) { bt = t; best = i; }
  }
  const p = [b.positions[best * 3], b.positions[best * 3 + 1], b.positions[best * 3 + 2]];
  console.log(s > 0 ? 'left ' : 'right', p.map(v => +v.toFixed(4)), 'out 1.5 cm', [p[0] + s * 0.015, p[1], p[2]].map(v => +v.toFixed(4)));
}
