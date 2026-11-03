// A pose of a rig: each joint's turn from its rest, in the world (Q, J×4 — what skinning applies), and its place now
// (P, J×3); floor — how high the lowest point should be now (the floor step sets the meshes on it), shift — how much
// the floor step moved everything up (0 until it runs). A pose belongs to whoever made it: the engine writes only into
// the pose it is given (src/figure.js keeps two of its own for its step and says so).
import { qMul, qConj, getQ, setQ, qRot } from './math.js';

export class Pose {
  constructor(J) { this.J = J; this.Q = new Float64Array(J * 4); this.P = new Float64Array(J * 3); this.floor = 0; this.shift = 0; this.identity(); }
  identity() { this.Q.fill(0); for (let j = 0; j < this.J; j++) this.Q[j * 4 + 3] = 1; return this; }
  copy(o) { this.Q.set(o.Q); this.P.set(o.P); this.floor = o.floor; this.shift = o.shift; return this; }
  clone() { return new Pose(this.J).copy(this); }
  // the rig at rest, as it stands
  static rest(rig, out = new Pose(rig.J)) { out.identity(); out.P.set(rig.joints); out.floor = rig.floor; out.shift = 0; return out; }
}

// the joints' places from the pelvis down the rig's own bones
export function build(pose, rig, hip) {
  const sk = rig.skeleton, R = rig.joints, Q = pose.Q, P = pose.P, v = [0, 0, 0], q = [0, 0, 0, 0], d = [0, 0, 0];
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
