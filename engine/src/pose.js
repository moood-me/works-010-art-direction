// A pose of a rig: each joint's turn from its rest, in the world (Q, J×4 — what skinning applies), and its place now
// (P, J×3); floor — how high the lowest point should be now (the floor step sets the meshes on it), shift — how much
// the floor step moved everything up (0 until it runs). A pose belongs to whoever made it: the engine writes only into
// the pose it is given (src/figure.js keeps two of its own for its step and says so).
import { qMul, qConj, qRot, qBetween, getQ, setQ, getV, add, sub, scale, dot, len, normalize, clamp } from './math.js';

export class Pose {
  constructor(J) { this.J = J; this.Q = new Float64Array(J * 4); this.P = new Float64Array(J * 3); this.floor = 0; this.shift = 0; this.identity(); }
  identity() { this.Q.fill(0); for (let j = 0; j < this.J; j++) this.Q[j * 4 + 3] = 1; return this; }
  copy(o) { this.Q.set(o.Q); this.P.set(o.P); this.floor = o.floor; this.shift = o.shift; return this; }
  clone() { return new Pose(this.J).copy(this); }
  // the rig at rest, as it stands
  static rest(rig, out = new Pose(rig.J)) { out.identity(); out.P.set(rig.joints); out.floor = rig.floor; out.shift = 0; return out; }
}

// the joints' places from the pelvis down the rig's own bones (rest: the rest places this frame — the rig's, or as
// the pose layers that change the rest make them, src/figure.js)
export function build(pose, rig, hip, rest = rig.joints) {
  const sk = rig.skeleton, R = rest, Q = pose.Q, P = pose.P, v = [0, 0, 0], q = [0, 0, 0, 0], d = [0, 0, 0];
  for (let j = 0; j < sk.J; j++) {
    const p = sk.parent[j];
    if (p < 0) { P[j * 3] = hip[0]; P[j * 3 + 1] = hip[1]; P[j * 3 + 2] = hip[2]; continue; }
    q[0] = Q[p * 4]; q[1] = Q[p * 4 + 1]; q[2] = Q[p * 4 + 2]; q[3] = Q[p * 4 + 3];
    d[0] = R[j * 3] - R[p * 3]; d[1] = R[j * 3 + 1] - R[p * 3 + 1]; d[2] = R[j * 3 + 2] - R[p * 3 + 2];
    qRot(q, d, v);
    P[j * 3] = P[p * 3] + v[0]; P[j * 3 + 1] = P[p * 3 + 1] + v[1]; P[j * 3 + 2] = P[p * 3 + 2] + v[2];
  }
}
export const hipOf = (pose, sk) => { const H = sk.index.Hips; return [pose.P[H * 3], pose.P[H * 3 + 1], pose.P[H * 3 + 2]]; };

// a joint's turn against its parent's (both from rest), and back
export const localOf = (pose, sk, j) => { const p = sk.parent[j]; return p < 0 ? getQ(pose.Q, j) : qMul(qConj(getQ(pose.Q, p)), getQ(pose.Q, j)); };
// set joint j's local turn, carrying everything under it along
export function setLocal(pose, sk, j, L) {
  const p = sk.parent[j], now = getQ(pose.Q, j), want = p < 0 ? L : qMul(getQ(pose.Q, p), L);
  turnUnder(pose, sk, j, qMul(want, qConj(now)));
}
// turn joint j and all under it by r (in the world)
export function turnUnder(pose, sk, j, r) { for (const k of sk.under(j)) setQ(pose.Q, k, qMul(r, getQ(pose.Q, k))); }

// the legs put back on their feet: each foot where it is in `before` (its place and its turn in the world), the knee
// bending in the plane it bends in now — two bones on this frame's rest lengths (ctx.rest), so no bone is stretched.
// Where a hip turned away from its foot farther than the leg reaches, the pelvis goes down as far as that leg needs
// (only down: where it goes over the ground stays Kimodo's). For a layer that turns the pelvis (src/deform.js): the
// feet stay where the motion put them.
export function keepFeet(pose, ctx, before) {
  const sk = ctx.rig.skeleton, rest = ctx.rest, legs = ['Left', 'Right'].map(s => ['Leg', 'Shin', 'Foot'].map(n => sk.index[s + n]));
  let drop = 0;
  for (const [a, b, c] of legs) {
    const reach = len(sub(getV(rest, b), getV(rest, a))) + len(sub(getV(rest, c), getV(rest, b)));
    const d = sub(getV(pose.P, a), getV(before.P, c)), h2 = d[0] * d[0] + d[2] * d[2];
    if (d[0] * d[0] + d[1] * d[1] + d[2] * d[2] > reach * reach && h2 < reach * reach) drop = Math.max(drop, d[1] - Math.sqrt(reach * reach - h2));
  }
  if (drop > 0) { ctx.hip[1] -= drop; ctx.build(); }
  for (const s of ['Left', 'Right']) {
    const a = sk.index[s + 'Leg'], b = sk.index[s + 'Shin'], c = sk.index[s + 'Foot'];
    const A = getV(pose.P, a), B = getV(pose.P, b), C = getV(pose.P, c);
    if (len(sub(C, getV(before.P, c))) < 1e-9) continue;   // this foot is where it was
    const la = len(sub(getV(rest, b), getV(rest, a))), lb = len(sub(getV(rest, c), getV(rest, b)));
    const AT = sub(getV(before.P, c), A), dir = normalize(AT), d = clamp(len(AT), Math.abs(la - lb) + 1e-9, la + lb - 1e-9);
    let pole = sub(B, A); pole = sub(pole, scale(dir, dot(pole, dir)));
    pole = len(pole) > 1e-7 ? normalize(pole) : normalize(qRot(getQ(pose.Q, b), [0, 0, 1]));
    const ca = (la * la + d * d - lb * lb) / (2 * la * d), sa = Math.sqrt(Math.max(0, 1 - ca * ca));
    const K = add(A, add(scale(dir, la * ca), scale(pole, la * sa))), T = add(A, scale(dir, d));
    const r1 = qBetween(normalize(sub(B, A)), normalize(sub(K, A)));
    turnUnder(pose, sk, a, r1);
    const C1 = add(K, qRot(r1, sub(C, B)));
    turnUnder(pose, sk, b, qBetween(normalize(sub(C1, K)), normalize(sub(T, K))));
    for (const k of sk.under(c)) setQ(pose.Q, k, getQ(before.Q, k));
  }
  ctx.build();
}
