// What a deformer reads off a body (src/deform.js): its parts along their bones, each vertex's share of them, the
// limbs, the head, the hands and feet, its landmarks by height — and the small tools on a mesh they share
// (smoothing a field over the surface, Taubin's smoothing, normals).
//
//   regionsOf(mesh, rig) → {
//     segs        the body's parts along their bones: torso (Hips→Neck1), neck, head, and per side clav, arm, fore,
//                 hand, thigh, shin, foot — {id, kind, side (1 left, −1 right, 0), a, b (joints), parent, members}
//     frames      each part's frame at this rest: {a (its root joint's place), e (along the bone), u, w (across), L}
//     jseg        each joint's part
//     seg, sw     each vertex's two strongest parts and their shares (from the skin's weights, sharpened)
//     limb        each vertex's share of the five limbs — 0 body, 1 left arm, 2 right arm, 3 left leg, 4 right leg —
//                 smoothed over the surface so a change of a limb fades into the body (N×5)
//     jlimb       each joint's limb
//     head, fingers, ends   each vertex's share of the head, the fingers, the hands and feet (smoothed)
//     levels      landmarks by height (metres): floor, ankle, knee, crotch, hips, waist, chest, armpit, shoulders,
//                 neck, head, top
//     height      top − floor
//   }
// What depends only on the skin's weights and triangles (shares, limbs) is kept per topology; what depends on the rest
// (frames, levels) per rest.
import { neighboursOf } from './mesh.js';

export const LIMBS = ['body', 'armLeft', 'armRight', 'legLeft', 'legRight'];

export function segmentsOf(sk) {
  const J = n => { const j = sk.index[n]; if (j == null) throw new Error(`no joint ${n}`); return j; };
  const segs = [
    { id: 'torso', kind: 'torso', side: 0, a: J('Hips'), b: J('Neck1'), parent: null, members: ['Hips', 'Spine1', 'Spine2', 'Chest'] },
    { id: 'neck', kind: 'neck', side: 0, a: J('Neck1'), b: J('Head'), parent: 'torso', members: ['Neck1', 'Neck2'] },
    { id: 'head', kind: 'head', side: 0, a: J('Head'), b: J('HeadEnd'), parent: 'neck', members: ['Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'] },
  ];
  for (const [s, side] of [['Left', 1], ['Right', -1]]) {
    segs.push({ id: 'clav' + s, kind: 'clav', side, a: J(s + 'Shoulder'), b: J(s + 'Arm'), parent: 'torso', members: [s + 'Shoulder'] });
    segs.push({ id: 'arm' + s, kind: 'arm', side, a: J(s + 'Arm'), b: J(s + 'ForeArm'), parent: 'clav' + s, members: [s + 'Arm'] });
    segs.push({ id: 'fore' + s, kind: 'fore', side, a: J(s + 'ForeArm'), b: J(s + 'Hand'), parent: 'arm' + s, members: [s + 'ForeArm'] });
    segs.push({ id: 'hand' + s, kind: 'hand', side, a: J(s + 'Hand'), b: J(s + 'HandMiddleEnd'), parent: 'fore' + s, members: sk.names.filter(n => n.startsWith(s + 'Hand')) });
    segs.push({ id: 'thigh' + s, kind: 'thigh', side, a: J(s + 'Leg'), b: J(s + 'Shin'), parent: 'torso', members: [s + 'Leg'] });
    segs.push({ id: 'shin' + s, kind: 'shin', side, a: J(s + 'Shin'), b: J(s + 'Foot'), parent: 'thigh' + s, members: [s + 'Shin'] });
    segs.push({ id: 'foot' + s, kind: 'foot', side, a: J(s + 'Foot'), b: J(s + 'ToeEnd'), parent: 'shin' + s, members: [s + 'Foot', s + 'ToeBase', s + 'ToeEnd'] });
  }
  segs.forEach((s, i) => { s.index = i; s.members = s.members.map(J); });
  const index = Object.fromEntries(segs.map((s, i) => [s.id, i]));
  for (const s of segs) s.parentIndex = s.parent ? index[s.parent] : -1;
  const jseg = new Int32Array(sk.J);
  segs.forEach((s, i) => s.members.forEach(j => { jseg[j] = i; }));
  return { segs, index, jseg };
}
const limbOfSeg = s => s.kind === 'arm' || s.kind === 'fore' || s.kind === 'hand' ? (s.side > 0 ? 1 : 2) : s.kind === 'thigh' || s.kind === 'shin' || s.kind === 'foot' ? (s.side > 0 ? 3 : 4) : 0;

// a part's frame from two places: e along the bone, w the forward (or up, for a bone along z) across it, u = e × w
export function frameOf(a, b) {
  const e = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], L = Math.hypot(...e) || 1e-9;
  e[0] /= L; e[1] /= L; e[2] /= L;
  const ref = Math.abs(e[2]) > 0.7 ? [0, 1, 0] : [0, 0, 1], d = ref[0] * e[0] + ref[1] * e[1] + ref[2] * e[2];
  const w = norm([ref[0] - d * e[0], ref[1] - d * e[1], ref[2] - d * e[2]]);
  const u = norm([e[1] * w[2] - e[2] * w[1], e[2] * w[0] - e[0] * w[2], e[0] * w[1] - e[1] * w[0]]);
  return { a: [a[0], a[1], a[2]], e, u, w, L };
}
const norm = v => { const l = Math.hypot(v[0], v[1], v[2]) || 1; return [v[0] / l, v[1] / l, v[2] / l]; };
// a point in a part's frame: [along (a share of the bone), across u, across w]
export function local(f, x, y, z) {
  const dx = x - f.a[0], dy = y - f.a[1], dz = z - f.a[2], al = dx * f.e[0] + dy * f.e[1] + dz * f.e[2];
  const rx = dx - f.e[0] * al, ry = dy - f.e[1] * al, rz = dz - f.e[2] * al;
  return [al / f.L, rx * f.u[0] + ry * f.u[1] + rz * f.u[2], rx * f.w[0] + ry * f.w[1] + rz * f.w[2]];
}

// —— what depends on the skin only (kept per topology) ——
const SHARES = new WeakMap();
function sharesOf(mesh, sk) {
  if (SHARES.has(mesh.skin.joints)) return SHARES.get(mesh.skin.joints);
  const { segs, jseg } = segmentsOf(sk), N = mesh.N, K = mesh.skin.K, SJ = mesh.skin.joints, SW = mesh.skin.weights;
  const seg = new Int32Array(N * 2), sw = new Float32Array(N * 2), acc = new Float64Array(segs.length);
  const limb = new Float32Array(N * 5), head = new Float32Array(N), fingers = new Float32Array(N), ends = new Float32Array(N);
  const HEAD = new Set(['Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'].map(n => sk.index[n]));
  for (let i = 0; i < N; i++) {
    acc.fill(0);
    for (let k = 0; k < K; k++) {
      const w = SW[i * K + k]; if (!w) continue; const j = SJ[i * K + k], s = segs[jseg[j]];
      acc[jseg[j]] += w; limb[i * 5 + limbOfSeg(s)] += w;
      if (HEAD.has(j)) head[i] += w;
      if (sk.part[j] === 'finger') fingers[i] += w;
      if (s.kind === 'hand' || s.kind === 'foot') ends[i] += w;
    }
    let s1 = -1, s2 = -1;
    for (let s = 0; s < acc.length; s++) { if (s1 < 0 || acc[s] > acc[s1]) { s2 = s1; s1 = s; } else if (s2 < 0 || acc[s] > acc[s2]) s2 = s; }
    let w1 = acc[s1] ** 1.6, w2 = s2 >= 0 ? acc[s2] ** 1.6 : 0; const t = w1 + w2 || 1; w1 /= t; w2 /= t;
    seg[i * 2] = s1; seg[i * 2 + 1] = s2 < 0 ? s1 : s2; sw[i * 2] = w1; sw[i * 2 + 1] = w2;
  }
  const nb = neighboursOf(mesh);
  smoothField(limb, 5, nb, 6);
  const out = { seg, sw, limb, head: smoothField(head, 1, nb, 4), fingers, ends: smoothField(Float32Array.from(ends, v => sst(Math.min(1, v * 1.3))), 1, nb, 10) };
  SHARES.set(mesh.skin.joints, out);
  return out;
}

// —— what depends on the rest too (kept per rest) ——
const REGIONS = new WeakMap();
export function regionsOf(mesh, rig) {
  let byJ = REGIONS.get(mesh.positions); if (!byJ) REGIONS.set(mesh.positions, byJ = new WeakMap());
  if (byJ.has(rig.joints)) return byJ.get(rig.joints);
  const sk = rig.skeleton, { segs, index, jseg } = segmentsOf(sk), J = rig.joints, P = mesh.positions;
  const at = j => [J[j * 3], J[j * 3 + 1], J[j * 3 + 2]];
  const frames = segs.map(s => frameOf(at(s.a), at(s.b)));
  const jlimb = Int8Array.from(jseg, s => limbOfSeg(segs[s]));
  const r = { skeleton: sk, segs, index, jseg, jlimb, frames, ...sharesOf(mesh, sk), mesh, rig, nb: neighboursOf(mesh) };
  // landmarks by height
  let lo = Infinity, hi = -Infinity;
  for (const i of mesh.used) { const y = P[i * 3 + 1]; if (y < lo) lo = y; if (y > hi) hi = y; }
  const y = n => J[sk.index[n] * 3 + 1], both = n => (y('Left' + n) + y('Right' + n)) / 2;
  const shoulders = both('Arm'), hips = y('Hips'), crotch = both('Leg');
  // the waist: where the torso is narrowest between the hips and the chest (its half-width by height, arms left out)
  const narrow = { y: (y('Spine1') + y('Spine2')) / 2, w: Infinity };
  const B = 40, y0 = hips, y1 = y('Chest'), wid = new Float64Array(B);
  for (const i of mesh.used) {
    const v = P[i * 3 + 1]; if (v < y0 || v > y1 || r.limb[i * 5] < 0.9) continue;
    const b = Math.min(B - 1, Math.floor((v - y0) / (y1 - y0) * B)); wid[b] = Math.max(wid[b], Math.abs(P[i * 3] - J[0]));
  }
  for (let b = 2; b < B - 2; b++) if (wid[b] > 0 && wid[b] < narrow.w) narrow.w = wid[b], narrow.y = y0 + (b + 0.5) / B * (y1 - y0);
  const chest = y('Chest') + 0.45 * (shoulders - y('Chest'));
  r.levels = { floor: lo, ankle: both('Foot'), knee: both('Shin'), crotch, hips, waist: narrow.y, chest, armpit: y('Chest') + 0.75 * (shoulders - y('Chest')), shoulders, neck: y('Neck1'), head: y('Head'), top: hi };
  r.height = hi - lo;
  byJ.set(rig.joints, r);
  return r;
}
// a height given as a landmark's name or as a share of the height from the floor
export function levelOf(r, at) {
  if (typeof at === 'number') return r.levels.floor + at * r.height;
  if (!(at in r.levels)) throw new Error(`no landmark "${at}" (${Object.keys(r.levels).join(', ')})`);
  return r.levels[at];
}

// each vertex's share of the five limbs, for any skinned mesh off the same skeleton (clothes, a head): from its own
// skin, smoothed over its own surface; for a rigid mesh, its joint's limb
export function limbsOfMesh(mesh, sk) {
  if (mesh.kind === 'skinned') return sharesOf(mesh, sk).limb;
  const { segs, jseg } = segmentsOf(sk), out = new Float32Array(mesh.N * 5);
  const l = mesh.kind === 'rigid' ? limbOfSeg(segs[jseg[mesh.joint]]) : 0;
  for (let i = 0; i < mesh.N; i++) out[i * 5 + l] = 1;
  return out;
}

// —— small tools on a mesh ——
export const sst = t => t <= 0 ? 0 : t >= 1 ? 1 : t * t * (3 - 2 * t);
export const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
export const lerp = (a, b, t) => a + (b - a) * t;

// a field of C values per vertex smoothed over the surface: each step half its own, half its neighbours' mean
export function smoothField(f, C, nb, iters, only = null) {
  const N = nb.start.length - 1, t = new Float32Array(f.length);
  for (let it = 0; it < iters; it++) {
    for (let i = 0; i < N; i++) {
      const a = nb.start[i], b = nb.start[i + 1];
      if (a === b || (only && !only[i])) { for (let c = 0; c < C; c++) t[i * C + c] = f[i * C + c]; continue; }
      for (let c = 0; c < C; c++) { let s = 0; for (let q = a; q < b; q++) s += f[nb.list[q] * C + c]; t[i * C + c] = 0.5 * f[i * C + c] + 0.5 * s / (b - a); }
    }
    f.set(t);
  }
  return f;
}
// Taubin's smoothing (λ|μ): small forms go, the volume stays. amount(i, it) in 0..1
export function taubin(pos, nb, amount, iters, mu = -0.53) {
  const p = Float32Array.from(pos), tmp = new Float32Array(p.length), N = nb.start.length - 1;
  for (let it = 0; it < iters; it++) for (const lam of [0.5, mu]) {
    if (!lam) continue;
    for (let i = 0; i < N; i++) {
      const a = nb.start[i], b = nb.start[i + 1], w = a === b ? 0 : amount(i, it);
      if (w <= 0) { tmp[i * 3] = p[i * 3]; tmp[i * 3 + 1] = p[i * 3 + 1]; tmp[i * 3 + 2] = p[i * 3 + 2]; continue; }
      let x = 0, y = 0, z = 0; for (let q = a; q < b; q++) { const j = nb.list[q]; x += p[j * 3]; y += p[j * 3 + 1]; z += p[j * 3 + 2]; }
      const n = b - a, k = lam * Math.min(w, 1) / n;
      tmp[i * 3] = p[i * 3] + (x - p[i * 3] * n) * k; tmp[i * 3 + 1] = p[i * 3 + 1] + (y - p[i * 3 + 1] * n) * k; tmp[i * 3 + 2] = p[i * 3 + 2] + (z - p[i * 3 + 2] * n) * k;
    }
    p.set(tmp);
  }
  return p;
}
// vertex normals (area-weighted) of any positions on the mesh's triangles
export function normalsAt(pos, tris) {
  const n = new Float32Array(pos.length);
  for (let t = 0; t < tris.length; t += 3) {
    const a = tris[t] * 3, b = tris[t + 1] * 3, c = tris[t + 2] * 3;
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2], vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    for (const k of [a, b, c]) { n[k] += nx; n[k + 1] += ny; n[k + 2] += nz; }
  }
  for (let i = 0; i < n.length; i += 3) { const l = Math.hypot(n[i], n[i + 1], n[i + 2]) || 1; n[i] /= l; n[i + 1] /= l; n[i + 2] /= l; }
  return n;
}
