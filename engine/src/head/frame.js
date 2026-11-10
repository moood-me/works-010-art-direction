// The head of a body: its units and what of the skin is head. Everything of heads (src/head/, the face deformers) is
// measured in head units — the cranium's radius 1, its centre a little above the Head joint (Г1's heads,
// experiments/heads-anime): x the person's left, y up, z forward, as the body's axes at rest.
//   headFrame(rig, size) → {O, R, toL(x,y,z), toW(x,y,z)}   size: how big the head is drawn against Anny's own (Г1: hs)
//   annyScale(rig)        the head's lengths against moood's woman's (Anny's own lengths scaled by it)
//   headShares(mesh, sk) → {head, jaw, neck, omega}   each vertex's weight on the head's joints, the jaw's, the neck's;
//                          omega: how much of it a change of the head moves — all of the head, fading down the neck
import { neighboursOf } from '../mesh.js';
import { smoothField } from '../regions.js';
import { clamp } from '../math.js';

export const HEAD_JOINTS = ['Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'];

// how big a head is drawn when nothing says (Г1's heads: Anny's own head)
export const HEAD_SIZE = 1.1;
// a head's lengths against moood's woman's, on whose head Anny's own lengths were found (how near a point must be to a
// landmark, how wide her eye is): the Head joint to HeadEnd, against hers (0.151 m)
export const annyScale = rig => { const sk = rig.skeleton, J = rig.joints; return (J[sk.index.HeadEnd * 3 + 1] - J[sk.index.Head * 3 + 1]) / 0.151; };

export function headFrame(rig, size = HEAD_SIZE) {
  const sk = rig.skeleton, J = rig.joints, H = sk.index.Head;
  const R = 0.088 * size * annyScale(rig);
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
