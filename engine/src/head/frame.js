// The head of a body: its units and what of the skin is head. Everything of heads (src/head/, the face deformers) is
// measured in head units — the cranium's radius 1, its centre a little above the Head joint (Г1's heads,
// experiments/heads-anime): x the person's left, y up, z forward, as the body's axes at rest.
//   headFrame(body, size) → {O, R, toL(x,y,z), toW(x,y,z)}   size: how big the head is drawn against Anny's own (Г1: hs)
//   headShares(mesh, sk) → {head, jaw, neck, omega}   each vertex's weight on the head's joints, the jaw's, the neck's;
//                          omega: how much of it a change of the head moves — all of the head, fading down the neck
import { neighboursOf } from '../mesh.js';
import { smoothField } from '../regions.js';
import { clamp } from '../math.js';

export const HEAD_JOINTS = ['Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'];

export function headFrame(rig, size = 1.1) {
  const sk = rig.skeleton, J = rig.joints, H = sk.index.Head, E = sk.index.HeadEnd;
  const R = 0.088 * size * (J[E * 3 + 1] - J[H * 3 + 1]) / 0.151;
  const O = [J[H * 3], J[H * 3 + 1] + 0.62 * R, J[H * 3 + 2] - 0.03 * R];
  return { O, R, size, toL: (x, y, z) => [(x - O[0]) / R, (y - O[1]) / R, (z - O[2]) / R], toW: (x, y, z) => [O[0] + x * R, O[1] + y * R, O[2] + z * R] };
}

const SHARES = new WeakMap();
export function headShares(mesh, sk) {
  if (SHARES.has(mesh.skin.joints)) return SHARES.get(mesh.skin.joints);
  const N = mesh.N, K = mesh.skin.K, SJ = mesh.skin.joints, SW = mesh.skin.weights;
  const isHead = new Uint8Array(sk.J); for (const n of HEAD_JOINTS) isHead[sk.index[n]] = 1;
  const head = new Float32Array(N), jaw = new Float32Array(N), neck = new Float32Array(N);
  for (let i = 0; i < N; i++) for (let k = 0; k < K; k++) {
    const w = SW[i * K + k]; if (!w) continue; const j = SJ[i * K + k];
    if (isHead[j]) head[i] += w;
    if (j === sk.index.Jaw) jaw[i] += w;
    if (j === sk.index.Neck1 || j === sk.index.Neck2) neck[i] += w;
  }
  const omega = smoothField(Float32Array.from(head, w => clamp(w * 1.25, 0, 1)), 1, neighboursOf(mesh), 8);
  const out = { head, jaw, neck, omega };
  SHARES.set(mesh.skin.joints, out);
  return out;
}
