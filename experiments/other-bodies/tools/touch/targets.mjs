// where a point on one person is, frame by frame, in the scene — and the same point in another person's Kimodo space
// (what their motion is ordered with); PLACE=x,z,heading places the first.  node tools/targets.mjs <character> <chain ids,comma> <joint> <x,y,z at rest> <frames,comma> [B: x0,z0,heading,k]
import { createEngine } from '../../../../engine/src/engine.js';
import { read } from '../../../../engine/check/node-read.mjs';
import { loadScene, jointAt } from '../../scene.js';
const [character, chain, joint, pt, frames, other] = process.argv.slice(2);
const E = await createEngine({ read });
const base = new URL('../../', import.meta.url);
// other bodies: `body:<body id>` for a body that has no character file (engine/characters)
const who = character.startsWith('body:') ? { format: 'engine/character', version: 1, id: 'x', body: character.slice(5) } : character;
const S = await loadScene(E, base, { frames: 1000, people: [{ id: 'A', character: who, chain: chain.split(','), start: 0, place: (([x, z, h]) => ({ position: [x, 0, z], heading: h }))((process.env.PLACE || '0,0,0').split(',').map(Number)) }] }, read);
const A = S.by.A, p = pt.split(',').map(Number), j = A.body.skeleton.index[joint];
const sF = E.skeleton.floor;
const out = []; let q0 = null;
import { getQ, qMul, qConj, qRot } from '../../../../engine/src/math.js';
for (const f of frames.split(',').map(Number)) {
  S.at(f);
  const w = jointAt(A.fig.pose, A.body, j, p);
  const q = getQ(A.fig.pose.Q, j); q0 ??= q;
  // how far the joint turned about the vertical since the first frame asked (radians): its forward axis's heading
  const d = qRot(qMul(q, qConj(q0)), [0, 0, 1]);
  const row = { f, world: w.map(v => +v.toFixed(4)), turn: +Math.atan2(d[0], d[2]).toFixed(3) };
  if (other) {
    const [x0, z0, h, k] = other.split(',').map(Number), c = Math.cos(-h), s = Math.sin(-h);
    const dx = w[0] - x0, dz = w[2] - z0;
    row.kimodo = [(c * dx + s * dz) / k, w[1] / k + sF, (-s * dx + c * dz) / k].map(v => +v.toFixed(4));
  }
  out.push(row);
}
console.log(JSON.stringify(out));
