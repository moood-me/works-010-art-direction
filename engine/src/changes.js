// Changes of a body's rest — the same changes src/layers.js applies as pose layers (on every frame), applied once to
// the rest instead. Each says what its joint frames do, explicitly:
//   frames: 'keep'  design — the frames (the retargeting reference) stay; what the change put into the rest rides along
//                   in every motion (a line of action, a limb bent in an arc, a hunch)
//   frames: 'turn'  anatomy — the frames turn with their bones; the rest is a different stance of the same skeleton and
//                   a motion moves it as Kimodo moved SOMA (the change shows at rest only)
//   turnAtRest(body, {joint, axis, degrees, frames})   a joint (and all under it) turned about an axis of its own frame
//   morphAtRest(body, {mesh?, name, weight})            a morph baked into the rest (joints and frames as they were)
//   withRest(body, {positions, joints, frames})         any deformer's result: frames 'keep' or 'turn' (turnFrames)
//   turnFrames(rig, mesh, joints, positions)            frames turned as the bones and the skin turned: a joint with one
//      child by the smallest turn of its bone; others by the best rotation of the skin they carry (as
//      tools/bodies_anny.py does for Т8's bodies)
import { Skinner } from './skin.js';
import { morphed } from './mesh.js';
import { Pose, build, hipOf, turnUnder } from './pose.js';
import { qMul, qRot, qAxisAngle, qBetween, qNorm, getQ, setQ } from './math.js';

const FRAMES = ['keep', 'turn'];
const need = f => { if (!FRAMES.includes(f)) throw new Error(`a rest change says what its frames do: 'keep' (design) or 'turn' (anatomy), not ${JSON.stringify(f)}`); };

export function turnAtRest(body, { joint, axis, degrees, frames }) {
  need(frames);
  const rig = body.rig, sk = rig.skeleton, j = sk.index[joint];
  if (j == null) throw new Error(`turn: no joint ${joint}`);
  const r = qAxisAngle(qRot(getQ(rig.frames, j), axis), degrees * Math.PI / 180);
  const pose = Pose.rest(rig);
  turnUnder(pose, sk, j, r);
  build(pose, rig, hipOf(pose, sk));
  const positions = new Float32Array(body.mesh.positions.length);
  new Skinner(body.mesh, rig, { method: 'cor' }).skin(pose, positions);
  copyUnused(body.mesh, positions);
  let F = rig.frames;
  if (frames === 'turn') { F = Float64Array.from(F); for (const k of sk.under(j)) setQ(F, k, qNorm(qMul(r, getQ(F, k)))); }
  return body.withRest({ positions, joints: pose.P, frames: F });
}

export function morphAtRest(body, { mesh = 'body', name, weight }) {
  if (mesh !== 'body') throw new Error(`morphAtRest: only the body's own morphs are baked here (not "${mesh}")`);
  return body.withRest({ positions: morphed(body.mesh, { [name]: weight }) });
}

export function withRest(body, { positions, joints, frames }) {
  need(frames);
  const F = frames === 'turn' ? turnFrames(body.rig, body.mesh, joints ?? body.rig.joints, positions ?? body.mesh.positions) : body.rig.frames;
  return body.withRest({ positions, joints, frames: F });
}

// vertices no triangle uses are not skinned: they keep their rest
function copyUnused(mesh, out) { for (let i = 0; i < mesh.N; i++) if (!mesh.isUsed[i]) for (let c = 0; c < 3; c++) out[i * 3 + c] = mesh.positions[i * 3 + c]; }

export function turnFrames(rig, mesh, joints, positions) {
  const sk = rig.skeleton, J0 = rig.joints, F0 = rig.frames, out = new Float64Array(F0.length);
  const K = mesh.skin.K, SJ = mesh.skin.joints, SW = mesh.skin.weights, P0 = mesh.positions;
  const v = (A, j) => [A[j * 3], A[j * 3 + 1], A[j * 3 + 2]];
  for (let j = 0; j < sk.J; j++) {
    const ks = sk.children[j].filter(k => Math.hypot(J0[k * 3] - J0[j * 3], J0[k * 3 + 1] - J0[j * 3 + 1], J0[k * 3 + 2] - J0[j * 3 + 2]) > 1e-4);
    const f0 = getQ(F0, j);
    if (ks.length === 1) {
      const k = ks[0], a = sub3(v(J0, k), v(J0, j)), b = sub3(v(joints, k), v(joints, j));
      setQ(out, j, qNorm(qMul(qBetween(unit(a), unit(b)), f0)));
      continue;
    }
    // the skin it carries (weight > 0.05), its best rotation (Horn's: the top eigenvector of a 4×4)
    const S = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]; let n = 0;
    for (let i = 0; i < mesh.N; i++) {
      if (!mesh.isUsed[i]) continue;
      let w = 0; for (let k = 0; k < K; k++) if (SJ[i * K + k] === j) w += SW[i * K + k];
      if (w <= 0.05) continue; n++;
      const x = [P0[i * 3] - J0[j * 3], P0[i * 3 + 1] - J0[j * 3 + 1], P0[i * 3 + 2] - J0[j * 3 + 2]];
      const y = [positions[i * 3] - joints[j * 3], positions[i * 3 + 1] - joints[j * 3 + 1], positions[i * 3 + 2] - joints[j * 3 + 2]];
      for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) S[a][b] += w * x[a] * y[b];
    }
    if (n < 4) {   // too little skin of its own: it turns as its parent did
      const p = sk.parent[j];
      if (p < 0) { setQ(out, j, f0); continue; }
      const turnP = qMul(getQ(out, p), conj4(getQ(F0, p)));
      setQ(out, j, qNorm(qMul(turnP, f0)));
      continue;
    }
    setQ(out, j, qNorm(qMul(bestRotation(S), f0)));
  }
  return out;
}
const sub3 = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const unit = a => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const conj4 = q => [-q[0], -q[1], -q[2], q[3]];

// the rotation (a quaternion x y z w) best carrying points x onto y, from S = Σ w x yᵀ (Horn 1987)
export function bestRotation(S) {
  const [[xx, xy, xz], [yx, yy, yz], [zx, zy, zz]] = S;
  const N = [
    [xx + yy + zz, yz - zy, zx - xz, xy - yx],
    [yz - zy, xx - yy - zz, xy + yx, zx + xz],
    [zx - xz, xy + yx, -xx + yy - zz, yz + zy],
    [xy - yx, zx + xz, yz + zy, -xx - yy + zz]];
  const { values, vectors } = jacobi4(N);
  let best = 0; for (let i = 1; i < 4; i++) if (values[i] > values[best]) best = i;
  const [w, x, y, z] = vectors.map(r => r[best]);
  return qNorm([x, y, z, w]);
}
// eigenvalues and eigenvectors (columns) of a symmetric 4×4 by Jacobi's rotations
function jacobi4(A) {
  const a = A.map(r => r.slice()), V = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
  for (let sweep = 0; sweep < 50; sweep++) {
    let off = 0; for (let p = 0; p < 4; p++) for (let q = p + 1; q < 4; q++) off += a[p][q] ** 2;
    if (off < 1e-30) break;
    for (let p = 0; p < 4; p++) for (let q = p + 1; q < 4; q++) {
      if (Math.abs(a[p][q]) < 1e-300) continue;
      const th = (a[q][q] - a[p][p]) / (2 * a[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1));
      const c = 1 / Math.sqrt(t * t + 1), s = t * c;
      for (let k = 0; k < 4; k++) { const akp = a[k][p], akq = a[k][q]; a[k][p] = c * akp - s * akq; a[k][q] = s * akp + c * akq; }
      for (let k = 0; k < 4; k++) { const apk = a[p][k], aqk = a[q][k]; a[p][k] = c * apk - s * aqk; a[q][k] = s * apk + c * aqk; }
      for (let k = 0; k < 4; k++) { const vkp = V[k][p], vkq = V[k][q]; V[k][p] = c * vkp - s * vkq; V[k][q] = s * vkp + c * vkq; }
    }
  }
  return { values: [0, 1, 2, 3].map(i => a[i][i]), vectors: V };
}
