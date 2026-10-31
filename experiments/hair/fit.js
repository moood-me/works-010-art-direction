// The designed hair onto a body's head, and the body as the hair meets it.
// The hairstyles are designed round a neutral head (`CRANIUM` in hair.js); a body's own skull is fitted with an
// ellipsoid (its points above the brows), and the hair is carried over by `warp`: whatever lies on the designed skull
// lands on the body's skull, and whatever lies off it keeps its distance and its direction from it.
// The body as the hair meets it: its head (the fitted skull and a face) moves with the Head joint; the neck, the
// shoulders, the back and chest, the arms and hands are capsules fitted to the skin, each end carried by a joint.
import { CRANIUM } from './hair.js';

const HEADJ = ['Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'];
// each skin point's weight on a set of joints
function weightOn(body, names) {
  const set = new Set(names.map(n => body.names.indexOf(n))), out = new Float32Array(body.N);
  for (let i = 0; i < body.N; i++) { let w = 0; for (let k = 0; k < 4; k++) if (set.has(body.joint[i * 4 + k])) w += body.weight[i * 4 + k] / 255; out[i] = w; }
  return out;
}
// an axis-aligned ellipsoid (centre on x = 0) through points, by shrinking steps on each parameter
function fitEllipsoid(P, x0) {
  const err = q => { let e = 0; for (let i = 0; i < P.length; i += 3) { const k = Math.hypot(P[i] / q[2], (P[i + 1] - q[0]) / q[3], (P[i + 2] - q[1]) / q[4]); e += (k - 1) ** 2; } return e; };
  let q = x0.slice(), e = err(q), st = 0.01;
  for (let it = 0; it < 400 && st > 1e-5; it++) {
    let better = false;
    for (let j = 0; j < 5; j++) for (const s of [1, -1]) { const t = q.slice(); t[j] += s * st; const et = err(t); if (et < e) { e = et; q = t; better = true; } }
    if (!better) st *= 0.5;
  }
  return { c: [0, q[0], q[1]], r: [q[2], q[3], q[4]] };
}
export function fitHead(body, eyes) {
  const w = weightOn(body, HEADJ), ey = (eyes[0][1] + eyes[1][1]) / 2, ez = (eyes[0][2] + eyes[1][2]) / 2;
  const top = [], face = [];
  for (let i = 0; i < body.N; i++) {
    if (w[i] < 0.5) continue;
    const x = body.rest[i * 3], y = body.rest[i * 3 + 1], z = body.rest[i * 3 + 2];
    if (y > ey + 0.03) top.push(x, y, z);
    else if (y < ey + 0.01 && Math.abs(x) < 0.06 && z > ez - 0.09) face.push(x, y, z);
  }
  // the designed head's skull from its eyes, to start from
  const c0 = CRANIUM.c, r0 = CRANIUM.r;
  const skull = fitEllipsoid(top, [ey + 0.014 + c0[1], ez - 0.075 + c0[2], ...r0]);
  const fc = fitEllipsoid(face, [ey - 0.045, ez - 0.06, 0.06, 0.07, 0.07]);
  return { skull, face: fc, eyeY: ey, eyeZ: ez };
}
// the designed hair's points onto the body's head
export function warp(fit) {
  const c = CRANIUM.c, r = CRANIUM.r, C = fit.skull.c, R = fit.skull.r;
  return (x, y, z, out = [0, 0, 0]) => {
    const qx = (x - c[0]) / r[0], qy = (y - c[1]) / r[1], qz = (z - c[2]) / r[2], k = Math.hypot(qx, qy, qz) || 1;
    // the point on the designed skull in its direction goes to the body's skull; the rest keeps its offset
    out[0] = x + (C[0] - c[0]) + (R[0] - r[0]) * qx / k;
    out[1] = y + (C[1] - c[1]) + (R[1] - r[1]) * qy / k;
    out[2] = z + (C[2] - c[2]) + (R[2] - r[2]) * qz / k;
    return out;
  };
}

// capsules round the body's bones, fitted to the skin at rest: {a, b} ends with their joints, radius r
export function bodyCapsules(body) {
  const J = n => body.J[body.names.indexOf(n)], ji = n => body.names.indexOf(n);
  const caps = [];
  const dist = (p, a, b) => { const bx = b[0] - a[0], by = b[1] - a[1], bz = b[2] - a[2], qx = p[0] - a[0], qy = p[1] - a[1], qz = p[2] - a[2]; const L = bx * bx + by * by + bz * bz; const t = (qx * bx + qy * by + qz * bz) / L; return [Math.hypot(qx - bx * t, qy - by * t, qz - bz * t), t]; };
  const pts = names => { const w = weightOn(body, names), out = []; for (let i = 0; i < body.N; i++) if (w[i] > 0.6) out.push([body.rest[i * 3], body.rest[i * 3 + 1], body.rest[i * 3 + 2]]); return out; };
  const radius = (P, a, b, q = 0.5) => { const d = P.map(p => dist(p, a, b)).filter(([, t]) => t > 0.15 && t < 0.85).map(([d]) => d).sort((x, y) => x - y); return d.length ? d[Math.floor(d.length * q)] : 0.03; };
  const v = p => [p.x, p.y, p.z];
  // the neck
  { const a = v(J('Neck1')), b = v(J('Head')); caps.push({ a, b, ja: ji('Neck1'), jb: ji('Head'), r: radius(pts(['Neck1', 'Neck2']), a, b), name: 'neck' }); }
  // the trunk: in slices, each a pair of capsules side by side (the trunk is wide and flat), joined up the body
  const trunk = pts(['Hips', 'Spine1', 'Spine2', 'Chest', 'LeftShoulder', 'RightShoulder', 'Neck1']);
  const slice = (y0, h) => {
    let zmin = 1e9, zmax = -1e9, xmax = 0;
    for (const p of trunk) if (Math.abs(p[1] - y0) < h) { if (Math.abs(p[0]) < 0.05) { zmin = Math.min(zmin, p[2]); zmax = Math.max(zmax, p[2]); } xmax = Math.max(xmax, Math.abs(p[0])); }
    const r = (zmax - zmin) / 2;
    return { y: y0, z: (zmin + zmax) / 2, r, x: Math.max(0.005, xmax - r) };
  };
  const yS = J('LeftShoulder').y, levels = [['Spine1', J('Spine1').y], ['Spine2', J('Spine2').y], ['Chest', J('Chest').y], ['Chest', yS - 0.035]];
  const S = levels.map(([n, y]) => ({ ...slice(y, 0.02), j: ji(n) }));
  for (let k = 0; k < S.length - 1; k++) for (const s of [-1, 1]) {
    const A = S[k], B = S[k + 1];
    caps.push({ a: [s * A.x, A.y, A.z], b: [s * B.x, B.y, B.z], ja: A.j, jb: B.j, r: Math.min(A.r, B.r), name: 'trunk' });
  }
  // the shoulders, the arms, the hands
  for (const side of ['Left', 'Right']) {
    const s = side === 'Left' ? 1 : -1, top = S[S.length - 1];
    const sh = v(J(side + 'Arm')), a0 = [s * top.x * 0.5, top.y + 0.01, top.z];
    caps.push({ a: a0, b: sh, ja: ji('Chest'), jb: ji(side + 'Arm'), r: radius(pts([side + 'Shoulder']), a0, sh, 0.55), name: 'shoulder' });
    const el = v(J(side + 'ForeArm')), wr = v(J(side + 'Hand')), fi = v(J(side + 'HandMiddle1'));
    caps.push({ a: sh, b: el, ja: ji(side + 'Arm'), jb: ji(side + 'ForeArm'), r: radius(pts([side + 'Arm']), sh, el), name: 'arm' });
    caps.push({ a: el, b: wr, ja: ji(side + 'ForeArm'), jb: ji(side + 'Hand'), r: radius(pts([side + 'ForeArm']), el, wr), name: 'forearm' });
    const tip = fi.map((q, j) => q + (fi[j] - wr[j]) * 0.6);
    caps.push({ a: wr, b: tip, ja: ji(side + 'Hand'), jb: ji(side + 'Hand'), r: 0.028, name: 'hand' });
  }
  return caps;
}
