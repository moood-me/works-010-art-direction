// The skeleton: SOMA's joints (no fingers) set by the sprite's sizes, and Kimodo's motions carried onto them — the
// way of experiments/indie and Р21/Р22 (core.js), without three.js: only the joints' turns and places are needed.
// A turn is a quaternion [x, y, z, w]; a place is [x, y, z] in the sprite's pixels (y up, z to the viewer).
export const PARENT = {
  Hips: null, Spine1: 'Hips', Spine2: 'Spine1', Chest: 'Spine2', Neck1: 'Chest', Neck2: 'Neck1', Head: 'Neck2', HeadEnd: 'Head', Jaw: 'Head', LeftEye: 'Head', RightEye: 'Head',
  LeftShoulder: 'Chest', LeftArm: 'LeftShoulder', LeftForeArm: 'LeftArm', LeftHand: 'LeftForeArm',
  RightShoulder: 'Chest', RightArm: 'RightShoulder', RightForeArm: 'RightArm', RightHand: 'RightForeArm',
  LeftLeg: 'Hips', LeftShin: 'LeftLeg', LeftFoot: 'LeftShin', LeftToeBase: 'LeftFoot', LeftToeEnd: 'LeftToeBase',
  RightLeg: 'Hips', RightShin: 'RightLeg', RightFoot: 'RightShin', RightToeBase: 'RightFoot', RightToeEnd: 'RightToeBase',
};
export const BONES = Object.keys(PARENT);
const CHAIN = { LeftLeg: 'LeftShin', LeftShin: 'LeftFoot', LeftFoot: 'LeftToeBase', RightLeg: 'RightShin', RightShin: 'RightFoot', RightFoot: 'RightToeBase',
  LeftShoulder: 'LeftArm', LeftArm: 'LeftForeArm', LeftForeArm: 'LeftHand', LeftHand: 'LeftHandMiddle1', RightShoulder: 'RightArm', RightArm: 'RightForeArm', RightForeArm: 'RightHand', RightHand: 'RightHandMiddle1' };
const ARMS = ['Arm', 'ForeArm', 'Hand'];

export const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
export const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
export const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
export const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
export const norm = a => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
export const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const Q0 = [0, 0, 0, 1];
export const qmul = (a, b) => [
  a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1],
  a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
  a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3],
  a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]];
export const qinv = q => [-q[0], -q[1], -q[2], q[3]];
export function qrot(q, v) {
  const [x, y, z, w] = q, tx = 2 * (y * v[2] - z * v[1]), ty = 2 * (z * v[0] - x * v[2]), tz = 2 * (x * v[1] - y * v[0]);
  return [v[0] + w * tx + y * tz - z * ty, v[1] + w * ty + z * tx - x * tz, v[2] + w * tz + x * ty - y * tx];
}
export const qaxis = (ax, a) => { const s = Math.sin(a / 2), n = norm(ax); return [n[0] * s, n[1] * s, n[2] * s, Math.cos(a / 2)]; };
export function qbetween(a, b) { // the shortest turn that takes direction a to direction b
  a = norm(a); b = norm(b);
  const d = dot(a, b);
  if (d < -0.999999) { const o = Math.abs(a[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0]; return qaxis(cross(a, o), Math.PI); }
  const c = cross(a, b), q = [c[0], c[1], c[2], 1 + d], l = Math.hypot(...q);
  return q.map(x => x / l);
}
export function qslerp(a, b, t) {
  let d = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3];
  if (d < 0) { b = b.map(x => -x); d = -d; }
  if (d > 0.9995) { const q = a.map((x, i) => x + (b[i] - x) * t), l = Math.hypot(...q); return q.map(x => x / l); }
  const th = Math.acos(d), s = Math.sin(th), wa = Math.sin((1 - t) * th) / s, wb = Math.sin(t * th) / s;
  return a.map((x, i) => x * wa + b[i] * wb);
}
export const qmat = q => { // rows of the 3×3 matrix
  const [x, y, z, w] = q;
  return [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w),
    2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w),
    2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)];
};
// a turn rounded to whole steps of `step` radians about its own axis (a part that must keep its pixels steady);
// below three quarters of a step it is no turn at all, so that a small sway doesn't click the part aside
export function qsnap(q, step) {
  if (q[3] < 0) q = q.map(x => -x);
  const s = Math.hypot(q[0], q[1], q[2]), a = 2 * Math.atan2(s, q[3]), b = a < 0.75 * step ? 0 : Math.max(1, Math.round(a / step)) * step;
  if (b === 0 || s < 1e-9) return Q0;
  return qaxis([q[0], q[1], q[2]], b);
}

// J: joint → place at rest. The motion (tools/motions/<id>.json, made by conv.py): D — each joint's turn against
// SOMA's rest, every frame; SOMA's rest joints; the pelvis's path; the feet's height.
export function prepare(M, J) {
  M.C = {};
  for (const [b, c] of Object.entries(CHAIN)) {
    const ours = /Hand$/.test(b) ? sub(J[b], J[PARENT[b]]) : sub(J[c], J[b]);
    M.C[b] = qbetween(ours, sub(M.rest[c], M.rest[b]));
  }
  let lean = 0;
  for (let f = 0; f < M.n; f++) { const fw = qrot(M.D.Chest.slice(f * 4, f * 4 + 4), [0, 0, 1]); lean += Math.asin(clamp(fw[1], -1, 1)); }
  M.lean = lean / M.n;
  return M;
}
const dq = (M, b, f) => {
  const d = M.D[b], i = Math.floor(f), j = Math.min(i + 1, M.n - 1);
  return qslerp(d.slice(i * 4, i * 4 + 4), d.slice(j * 4, j * 4 + 4), f - i);
};
const at3 = (M, f, k) => { const i = Math.floor(f), j = Math.min(i + 1, M.n - 1); return lerp(M.hips[i * 3 + k], M.hips[j * 3 + k], f - i); };
const at1 = (a, f, n) => { f = clamp(f, 0, n - 1); const i = Math.floor(f), j = Math.min(i + 1, n - 1); return lerp(a[i], a[j], f - i); };
const UPPER = new Set(BONES.filter(b => { for (let p = b; p; p = PARENT[p]) if (p === 'Spine1') return true; return false; }));

export function place(J, W, hips) { // joints' places from their turns
  const P = {};
  for (const b of BONES) { const p = PARENT[b]; P[b] = p ? add(P[p], qrot(W[p], sub(J[b], J[p]))) : hips.slice(); }
  return P;
}
// A pose at a (fractional) frame of a motion. o: travel (the pelvis's path kept), armOut (how far off the body the
// upper arm keeps, sine), head: {c: centre in the Head joint's rest place, r} for arms to keep out of the big head,
// upright (part of the clip's average stoop taken out), sole: points [joint, place at rest] that touch the ground,
// arms: false — the arms keep their rest places on the chest (a held pose is laid on top by `hold`)
export function pose(M, f, J, o = {}) {
  const W = {};
  for (const b of BONES) {
    const p = PARENT[b];
    if (M.D[b] && (o.arms !== false || !/Shoulder|Arm|Hand/.test(b))) { W[b] = dq(M, b, f); if (M.C[b]) W[b] = qmul(W[b], M.C[b]); }
    else W[b] = p ? W[p] : Q0;
  }
  if (o.upright && M.lean) {
    const fix = qaxis(qrot(W.Hips, [1, 0, 0]), -o.upright * M.lean);
    for (const b of UPPER) W[b] = qmul(fix, W[b]);
  }
  if (o.arms !== false) for (const [s, k] of [['Left', 1], ['Right', -1]]) {
    const side = qrot(W.Chest, [k, 0, 0]);
    const d2 = qrot(dq(M, s + 'Arm', f), norm(sub(M.rest[s + 'ForeArm'], M.rest[s + 'Arm'])));
    const out = dot(d2, side), need = o.armOut ?? 0.3;
    if (out < need) { const fix = qaxis(cross(d2, side), Math.asin(need) - Math.asin(Math.max(-1, out))); for (const a of ARMS) W[s + a] = qmul(fix, W[s + a]); }
    if (o.head) for (let it = 0; it < 14; it++) {
      const P = place(J, W, [0, 0, 0]), hc = add(P.Head, qrot(W.Head, sub(o.head.c, J.Head)));
      const tip = add(P[s + 'Hand'], qrot(W[s + 'Hand'], sub(J[s + 'Hand'], J[s + 'ForeArm'])));
      if (![P[s + 'Hand'], P[s + 'ForeArm'], tip].some(p => Math.hypot(...sub(p, hc)) < o.head.r)) break;
      const fix = qaxis(qrot(W.Chest, [0, 0, 1]), k * -0.12);
      for (const a of ARMS) W[s + a] = qmul(fix, W[s + a]);
    }
  }
  if (o.hold) o.hold(W);
  const kr = J.Hips[1] / M.hipY, t = o.travel;
  const hips = [t ? (at3(M, f, 0) - M.hips[0]) * kr : 0, at3(M, f, 1) * kr, t ? (at3(M, f, 2) - M.hips[2]) * kr : 0];
  let P = place(J, W, hips);
  if (o.sole) {
    let low = 1e9;
    for (const [b, r] of o.sole) low = Math.min(low, P[b][1] + qrot(W[b], sub(r, J[b]))[1]);
    hips[1] += at1(M.foot, f, M.n) * kr - low;
    P = place(J, W, hips);
  }
  return { W, P };
}
export function rest(J, hold) { const W = {}; for (const b of BONES) W[b] = Q0; if (hold) hold(W); return { W, P: place(J, W, J.Hips.slice()) }; }
