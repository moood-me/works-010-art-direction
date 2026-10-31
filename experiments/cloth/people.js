// Anny's bodies as moood bakes them (experiments/data), and a Kimodo motion played on them: each moment the body's
// skin, its normals and the joints' matrices (to carry what is skinned to the body: shoes, hair, the garments' targets).
// THREE is passed in (the page takes it from jsDelivr, the tests from npm); `bytes(name)` gives a data file's bytes.
import { turns } from '../../gallery/player-core.js';

const reader = (buf, at = 0) => (Kind, n) => { const a = new Kind(buf.slice(at, at + n * Kind.BYTES_PER_ELEMENT)); at += n * Kind.BYTES_PER_ELEMENT; return a; };
export const parseBase = buf => {
  const take = reader(buf), [N, T] = take(Uint32Array, 2), tris = take(Uint16Array, T * 3), joint = take(Uint8Array, N * 4), weight = take(Uint8Array, N * 4);
  return { N, tris, joint, weight };
};
export const parseGarment = buf => {
  const take = reader(buf), [V, T] = take(Uint32Array, 4);
  return { V, refs: take(Uint16Array, V * 3), bary: take(Float32Array, V * 3), offset: Float32Array.from(take(Int16Array, V * 3), v => v / 10000), measure: take(Uint16Array, 6), span: take(Float32Array, 3),
    joint: take(Uint8Array, V * 4), weight: take(Uint8Array, V * 4), loose: take(Uint8Array, V), hangs: take(Uint16Array, V), far: take(Uint16Array, V), beneath: take(Uint16Array, V), tris: take(Uint16Array, T * 3) };
};
// a MakeHuman garment on a body: each point on its three body points, the offset scaled by the body's measures
export function fitted(g, pos) {
  const s = [0, 1, 2].map(k => Math.abs(pos[g.measure[k * 2] * 3 + k] - pos[g.measure[k * 2 + 1] * 3 + k]) / g.span[k]);
  const out = new Float32Array(g.V * 3);
  for (let i = 0; i < g.V; i++) for (let c = 0; c < 3; c++) {
    let v = g.offset[i * 3 + c] * s[c];
    for (let k = 0; k < 3; k++) v += g.bary[i * 3 + k] * pos[g.refs[i * 3 + k] * 3 + c];
    out[i * 3 + c] = v;
  }
  return out;
}

export function normalsOf(pos, tris, out = new Float32Array(pos.length)) {
  out.fill(0);
  for (let t = 0; t < tris.length; t += 3) {
    const a = tris[t] * 3, b = tris[t + 1] * 3, c = tris[t + 2] * 3;
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2];
    const vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    for (const i of [a, b, c]) { out[i] += nx; out[i + 1] += ny; out[i + 2] += nz; }
  }
  for (let i = 0; i < out.length; i += 3) { const l = Math.hypot(out[i], out[i + 1], out[i + 2]) || 1; out[i] /= l; out[i + 1] /= l; out[i + 2] /= l; }
  return out;
}

export function skeletonOf(joints) {
  const JI = Object.fromEntries(joints.map((n, i) => [n, i]));
  return joints.map(n => {
    if (n === 'Hips') return -1;
    const chain = { Spine1: 'Hips', Spine2: 'Spine1', Chest: 'Spine2', Neck1: 'Chest', Neck2: 'Neck1', Head: 'Neck2', HeadEnd: 'Head', Jaw: 'Head', LeftEye: 'Head', RightEye: 'Head' };
    if (chain[n]) return JI[chain[n]];
    const s = n.startsWith('Left') ? 'Left' : 'Right', r = n.slice(s.length);
    const limb = { Shoulder: 'Chest', Arm: s + 'Shoulder', ForeArm: s + 'Arm', Hand: s + 'ForeArm', Leg: 'Hips', Shin: s + 'Leg', Foot: s + 'Shin', ToeBase: s + 'Foot', ToeEnd: s + 'ToeBase' };
    if (limb[r]) return JI[limb[r]];
    const m = r.match(/^Hand(Thumb|Index|Middle|Ring|Pinky)(\d|End)$/);
    if (m) { if (m[2] === '1') return JI[s + 'Hand']; const k = m[2] === 'End' ? (m[1] === 'Thumb' ? 3 : 4) : +m[2] - 1; return JI[s + 'Hand' + m[1] + k]; }
    return JI.Hips;
  });
}

let BASE = null;
export async function person(THREE, bytes, meta, who) {
  BASE ??= parseBase(await bytes('base'));
  const N = BASE.N, pb = await bytes(who), take = reader(pb), rest = Float32Array.from(take(Int16Array, N * 3), v => v / 10000);
  const F = (pb.byteLength - N * 6 - 77 * 48) / 6; take(Int16Array, F * 3);
  const inv = take(Float32Array, 77 * 12), J = [];
  for (let j = 0; j < 77; j++) { const a = inv.subarray(j * 12, j * 12 + 12); J.push(new THREE.Vector3().setFromMatrixPosition(new THREE.Matrix4().set(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11], 0, 0, 0, 1).invert())); }
  let floor = Infinity, top = -Infinity; for (let i = 1; i < rest.length; i += 3) { floor = Math.min(floor, rest[i]); top = Math.max(top, rest[i]); }
  return { who, N, tris: BASE.tris, joint: BASE.joint, weight: BASE.weight, rest, nrm: normalsOf(rest, BASE.tris), J, names: meta.joints, parent: skeletonOf(meta.joints), floor, height: top - floor };
}

// Where a body is at a moment of a motion. A motion M is the converted Kimodo file (motions/*.json): turns D, the
// pelvis's place `hips`, SOMA's lowest point `low`. `at(M, f, s)`: frame f (fractional), mixed with the rest pose by s
// (0 rest, 1 the motion); `skin(state)` the skin. The pelvis goes along the floor as SOMA's did (scaled by leg length),
// and the body is lifted or lowered so its lowest point is as high as SOMA's lowest point.
export class Pose {
  constructor(THREE, body) {
    this.THREE = THREE; this.b = body; this.root = body.names.indexOf('Hips');
    this.memo = new Map();
  }
  // whether joint j is the arm of that side or below it
  arm(side, j) {
    this.arms ??= {};
    const set = this.arms[side] ??= (() => { const b = this.b, top = b.names.indexOf(side + 'Arm'), out = new Set([top]);
      for (let k = 0; k < b.names.length; k++) { let p = k; while (p >= 0 && p !== top) p = b.parent[p]; if (p === top) out.add(k); } return out; })();
    return set.has(j);
  }
  turnsAt(M, f) {
    let m = this.memo.get(M); if (!m) this.memo.set(M, m = { memo: {}, cache: new Map() });
    let W = m.cache.get(f); if (!W) { W = turns(this.THREE, M, f, this.b.names, this.b.parent, this.b.J, m.memo); m.cache.set(f, W); }
    return W;
  }
  // the joints' turns and the pelvis's place
  at(M, f, s = 1, carry = [0, 0]) {
    const { THREE, b } = this, n = b.names.length, Q = THREE.Quaternion;
    if (!M || s <= 0) return { W: Array.from({ length: n }, () => new Q()), hips: b.J[this.root].clone(), low: b.floor };
    const f0 = Math.max(0, Math.min(M.n - 1, Math.floor(f))), f1 = Math.min(M.n - 1, f0 + 1), u = Math.max(0, Math.min(1, f - f0));
    const A = this.turnsAt(M, f0), B = this.turnsAt(M, f1), k = b.J[this.root].y / M.hipY;
    const W = A.map((q, j) => { const w = q.clone().slerp(B[j], u); return s < 1 ? new Q().slerp(w, s) : w; });
    // the arms a little off the body: SOMA's arms swing close by its hips, and these bodies are wider there — without
    // it the hands go into the hips and thighs (and press the clothes into them)
    const fwd = new THREE.Vector3(0, 0, 1).applyQuaternion(W[b.names.indexOf('Chest')]);
    for (const [side, a] of [['Left', 0.12], ['Right', -0.12]]) {
      const R = new Q().setFromAxisAngle(fwd, a * s);
      for (let j = 0; j < n; j++) if (this.arm(side, j)) W[j].premultiply(R);
    }
    const h = i => M.hips[f0 * 3 + i] * (1 - u) + M.hips[f1 * 3 + i] * u;
    const r = b.J[this.root];
    const hips = new THREE.Vector3(r.x + (h(0) - M.hips[0] + carry[0]) * k, h(1) * k, r.z + (h(2) - M.hips[2] + carry[1]) * k);
    hips.lerp(r, 1 - s);
    // SOMA's skin goes a little into the floor where it lies (as Kimodo's bodies do): never lower than the floor
    const low = b.floor + Math.max(0, (M.low[f0] * (1 - u) + M.low[f1] * u) * k) * s;
    return { W, hips, low };
  }
  // joint matrices (column-major, as THREE's elements) and the skin, the body set on the floor
  skin(st, outPos, outNrm) {
    const { THREE, b } = this, n = b.names.length, P = new Array(n), E = new Array(n);
    for (let j = 0; j < n; j++) {
      const p = b.parent[j];
      P[j] = p < 0 ? st.hips.clone() : P[p].clone().add(b.J[j].clone().sub(b.J[p]).applyQuaternion(st.W[p]));
    }
    for (let j = 0; j < n; j++) E[j] = new THREE.Matrix4().makeTranslation(P[j].x, P[j].y, P[j].z).multiply(new THREE.Matrix4().makeRotationFromQuaternion(st.W[j])).multiply(new THREE.Matrix4().makeTranslation(-b.J[j].x, -b.J[j].y, -b.J[j].z)).elements;
    const pos = outPos || new Float32Array(b.N * 3), nrm = outNrm || new Float32Array(b.N * 3);
    skinInto(b.rest, b.nrm, b.joint, b.weight, 255, E, pos, nrm);
    let low = Infinity, at = 0; for (let i = 1; i < pos.length; i += 3) if (pos[i] < low) { low = pos[i]; at = (i - 1) / 3; }
    // on anything but the feet of one upright (lying, rolling, sitting — lying, the heels may be lowest) the body is kept a
    // cloth's thickness above the floor, so the clothes it lies on have room; the lift comes and goes over a few frames
    const g = b.names[b.joint[at * 4]], want = /Foot|Toe/.test(g) && st.hips.y - b.floor > b.height * 0.3 ? 0 : 0.009;
    this.lift = (this.lift ?? 0) + Math.max(-0.0015, Math.min(0.0015, want - (this.lift ?? 0)));
    const shift = st.low + this.lift - low;
    for (let i = 1; i < pos.length; i += 3) pos[i] += shift;
    for (const e of E) { e[13] += shift; }
    return { pos, nrm, E };
  }
}

// linear blend skinning of points (and normals) by up to four joints each
export function skinInto(rest, rn, joint, weight, wscale, E, pos, nrm) {
  const n = rest.length / 3;
  for (let i = 0; i < n; i++) {
    const x = rest[i * 3], y = rest[i * 3 + 1], z = rest[i * 3 + 2];
    let X = 0, Y = 0, Z = 0, nx = 0, ny = 0, nz = 0, ws = 0;
    const ax = rn ? rn[i * 3] : 0, ay = rn ? rn[i * 3 + 1] : 0, az = rn ? rn[i * 3 + 2] : 0;
    for (let k = 0; k < 4; k++) {
      const w = weight[i * 4 + k] / wscale; if (!w) continue; const e = E[joint[i * 4 + k]];
      X += w * (e[0] * x + e[4] * y + e[8] * z + e[12]); Y += w * (e[1] * x + e[5] * y + e[9] * z + e[13]); Z += w * (e[2] * x + e[6] * y + e[10] * z + e[14]);
      if (rn) { nx += w * (e[0] * ax + e[4] * ay + e[8] * az); ny += w * (e[1] * ax + e[5] * ay + e[9] * az); nz += w * (e[2] * ax + e[6] * ay + e[10] * az); }
      ws += w;
    }
    if (ws < 1e-6) { X = x; Y = y; Z = z; ws = 1; }
    pos[i * 3] = X / ws; pos[i * 3 + 1] = Y / ws; pos[i * 3 + 2] = Z / ws;
    if (rn && nrm) { const l = Math.hypot(nx, ny, nz) || 1; nrm[i * 3] = nx / l; nrm[i * 3 + 1] = ny / l; nrm[i * 3 + 2] = nz / l; }
  }
}
