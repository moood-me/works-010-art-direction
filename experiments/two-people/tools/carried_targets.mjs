// For the carried one's own constraints: a point on the carrier (a joint and a point at rest) at scene frames T, in
// the carried one's Kimodo space — undoing the attachment (the rigid move of the carrier's hands since `from`), the
// carried one's placement and size, and the `startsAt` of the motion being ordered (x, z; that motion goes on `after`
// the carried one's earlier one).
//   node tools/carried_targets.mjs <scene> <carrier joint> <x,y,z> <frames,comma> <startsAt x,z>
import { createEngine } from '../../../engine/src/engine.js';
import { read } from '../../../engine/check/node-read.mjs';
import { loadScene, jointAt } from '../scene.js';
import { SCENES } from '../scenes.js';
import { qRot, qConj, qMul, qAxisAngle, sub } from '../../../engine/src/math.js';
const [id, joint, pt, frames, sa] = process.argv.slice(2);
const def = SCENES.find(s => s.id === id), E = await createEngine({ read });
const S = await loadScene(E, new URL('../', import.meta.url), def, read);
const W = S.by[def.carry.who], C = S.by[def.carry.by], p = pt.split(',').map(Number), [sx, sz] = sa.split(',').map(Number);
const F0 = S.carryFrame(def.carry.from), k = W.fig.retarget.k, fl = W.body.measures.floor;
const place = W.place, sF = E.skeleton.floor;
const out = [];
for (const T of frames.split(',').map(Number)) {
  const F = S.carryFrame(T);
  const pose = C.fig.posed(C.clip, Math.max(0, Math.min(C.clip.frames - 1, T - C.start)));
  const w = jointAt(pose, C.body, C.body.skeleton.index[joint], p);
  // undo the rigid move: x = R0 Rᵀ (w − o) + o0
  const r = qMul(F0.q, qConj(F.q)), u = qRot(r, sub(w, F.o)), x = [u[0] + F0.o[0], u[1] + F0.o[1], u[2] + F0.o[2]];
  // undo the placement (turn about y and move), then the size
  const l = qRot(qAxisAngle([0, 1, 0], -place.heading), [x[0] - place.position[0], x[1], x[2] - place.position[2]]);
  out.push({ T, kimodo: [l[0] / k - sx, (l[1] - fl) / k + sF, l[2] / k - sz].map(v => +v.toFixed(4)) });
}
console.log(JSON.stringify(out));
