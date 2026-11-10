// A head's form by deformers on Anny's head (beside the wrap onto a designed form, src/head/wrap.js): each a change
// of the rest of the head only (all of it, fading down the neck: src/head/frame.js omega), with a strength, on any
// body of Anny's mesh, combined in the order an author lists them; on the rest (frames kept or turned) or as a pose
// layer (its rest change weighed in) like any deformer (src/deform.js). Sizes in head units (the cranium's radius 1) of
// a head drawn as Anny's own (src/head/frame.js: HEAD_SIZE).
//   face     Anny's own face settings: her 129 local changes of the head and face (data/anny/face.json, made by
//            tools/face_targets.py) — {changes: {name: value (−1.5..1.5)}}, each at its own sign's move, scaled to this
//            head's size against moood's woman's (on whom they were made)
//   headOf   a head of another age (or of any other body of the same mesh): this head goes over to that body's head,
//            laid in this one's place and scaled to its size — {body: "<id>@<hash>", size (its size here, 1: as tall as
//            this head)}; the head's joints (its end, the jaw, the eyes) go with it
//   points   the face by points: landmarks found on the head's own surface (eyes and their corners, brows, the nose's
//            root and tip, the mouth and its corners, the chin, the jaw's angles, cheeks, ears, forehead, top, back)
//            moved by [dx, dy, dz] each — one smooth warp through them (biharmonic), the neck held; `mirror`: a left
//            landmark's move is the right one's too, x mirrored, unless the right one has its own
//   cage     a lattice round the head (Bézier, its points moved): the whole head changed in one gesture
//   warps    smooth warps: pushes (a point and its surroundings moved, falling off over r) and scales by height (the
//            head wider or deeper about its middle, over a band of heights)
import { register } from '../deform.js';
import { headFrame, headShares, annyScale } from './frame.js';
import { lerp, biharmonic } from '../math.js';
import { num, flag, vec } from '../schema.js';

const v3 = vec(3, -5, 5);
export const LANDMARKS = ['eyeL', 'eyeR', 'eyeInL', 'eyeInR', 'eyeOutL', 'eyeOutR', 'browL', 'browR', 'noseRoot', 'noseTip', 'mouth', 'mouthL', 'mouthR', 'chin', 'chinFront',
  'jawL', 'jawR', 'cheekL', 'cheekR', 'earL', 'earR', 'forehead', 'top', 'back'];

// —— Anny's own face settings ——
register({
  kind: 'face', of: 'skin',
  params: { changes: { type: 'map', values: num(-1.5, 1.5) } },
  defaults: {},
  prepare: async (p, E, body) => {
    if (body.topology !== 'anny-moood') throw new Error(`face: Anny's face changes are on moood's mesh (anny-moood), not ${body.topology}`);
    return E.faceTargets();
  },
  rest(p, R, { data, body }) {
    const P = Float32Array.from(body.mesh.positions), u = annyScale(body.rig);
    for (const [name, v] of Object.entries(p.changes)) {
      const c = data.changes[name]; if (!c) throw new Error(`face: Anny has no face change "${name}" (data/anny/face.json)`);
      const k = Math.abs(v) * p.strength * u * data.unit, D = v >= 0 ? c.p : c.n, I = c.i;
      for (let m = 0; m < I.length; m++) for (let q = 0; q < 3; q++) P[I[m] * 3 + q] += k * D[m * 3 + q];
    }
    return { positions: P };
  },
});

// —— a head of another age ——
register({
  kind: 'headOf', of: 'skin',
  params: { body: { type: 'string', pattern: /^[A-Za-z0-9_.-]+@[0-9a-f]{12,64}$/ }, size: num(0.2, 3) },
  defaults: { size: 1 },
  prepare: (p, E) => E.body(p.body),
  rest(p, R, { data: other, body }) {
    if (other.topology !== body.topology) throw new Error(`headOf: ${other.id} is on ${other.topology}, not ${body.topology}`);
    const A = headFrame(body.rig), B = headFrame(other.rig), { omega } = headShares(body.mesh, body.rig.skeleton), k = p.strength, s = p.size;
    const there = (x, y, z) => { const l = B.toL(x, y, z); return A.toW(l[0] * s, l[1] * s, l[2] * s); };
    const P = Float32Array.from(body.mesh.positions), Q = other.mesh.positions;
    for (let i = 0; i < body.mesh.N; i++) { const w = k * omega[i]; if (!w) continue; const t = there(Q[i * 3], Q[i * 3 + 1], Q[i * 3 + 2]); for (let c = 0; c < 3; c++) P[i * 3 + c] = lerp(P[i * 3 + c], t[c], w); }
    const J = Float64Array.from(body.rig.joints), sk = body.rig.skeleton;
    for (const n of ['HeadEnd', 'Jaw', 'LeftEye', 'RightEye']) { const j = sk.index[n], t = there(other.rig.joints[j * 3], other.rig.joints[j * 3 + 1], other.rig.joints[j * 3 + 2]); for (let c = 0; c < 3; c++) J[j * 3 + c] = lerp(J[j * 3 + c], t[c], k); }
    return { positions: P, joints: J };
  },
});

// —— the face by points ——
// the landmarks of a head: vertex indices, found on the stored body it was made from (body.origin: Anny's own surface
// there), so whatever changed the head since — a wrap, other deformers — they are the same points of the skin. The
// points deformer moves LANDMARKS; the wrap also takes the eyes' tops and bottoms
const MARKS = new WeakMap();
export function landmarksOf(changed) {
  const body = changed.origin ?? changed;
  if (MARKS.has(body.mesh.positions)) return MARKS.get(body.mesh.positions);
  const m = body.mesh, P = m.positions, N = m.N, used = m.isUsed, sk = body.rig.skeleton, J = body.rig.joints, { head, jaw: jawW } = headShares(m, sk);
  const jt = n => { const j = sk.index[n]; return [J[j * 3], J[j * 3 + 1], J[j * 3 + 2]]; }, u = annyScale(body.rig);
  const X = i => P[i * 3], Y = i => P[i * 3 + 1], Z = i => P[i * 3 + 2];
  const best = (ok, score, what) => { let b = -1, s = -Infinity; for (let i = 0; i < N; i++) if (used[i] && head[i] > 0.5 && ok(i)) { const v = score(i); if (v > s) { s = v; b = i; } } if (b < 0) throw new Error(`points: no ${what} found on this head`); return b; };
  const front = (x, y, r = 0.006 * u) => best(i => Math.abs(X(i) - x) < r && Math.abs(Y(i) - y) < r, Z);
  const eye = jt('LeftEye'), jaw = jt('Jaw');
  const tip = best(i => Math.abs(X(i)) < 0.004 * u && Y(i) < eye[1] && Y(i) > jaw[1] - 0.02 * u, Z);
  // the mouth: where the lips part — the upper lip's lowest point on the midline (the last the jaw doesn't carry), in front
  const mouth = best(i => Math.abs(X(i)) < 0.004 * u && jawW[i] < 0.5 && Y(i) < Y(tip) - 0.005 * u && Z(i) > Z(tip) - 0.03 * u, i => -Y(i), 'mouth');
  const L = {
    eyeL: front(eye[0], eye[1]), eyeInL: front(eye[0] - 0.014 * u, eye[1]), eyeOutL: front(eye[0] + 0.016 * u, eye[1]), browL: front(eye[0], eye[1] + 0.022 * u),
    eyeUpL: front(eye[0], eye[1] + 0.006 * u), eyeDownL: front(eye[0], eye[1] - 0.006 * u),
    noseRoot: front(0, eye[1], 0.004 * u), noseTip: tip, mouth,
    // the mouth's corner: where the lips' parting (the jaw's weight half) ends
    mouthL: best(i => X(i) > 0 && jawW[i] > 0.25 && jawW[i] < 0.75 && Math.abs(Y(i) - Y(mouth)) < 0.012 * u && Z(i) > Z(tip) - 0.035 * u, X, 'mouth corner'),
    chin: best(i => Math.abs(X(i)) < 0.004 * u && Z(i) > jaw[2] + 0.035 * u, i => -Y(i)), chinFront: front(0, Y(mouth) - 0.03 * u, 0.005 * u),
    jawL: best(i => X(i) > 0 && Math.abs(Y(i) - (Y(mouth) - 0.02 * u)) < 0.006 * u && Z(i) < Z(tip) - 0.06 * u, X),
    cheekL: front(eye[0] + 0.01 * u, eye[1] - 0.03 * u), earL: best(i => X(i) > 0 && Y(i) < eye[1] + 0.01 * u, X),
    forehead: front(0, eye[1] + 0.05 * u, 0.005 * u), top: best(() => true, Y),
    back: best(i => Math.abs(Y(i) - eye[1]) < 0.006 * u && Math.abs(X(i)) < 0.01 * u, i => -Z(i)),
  };
  // the right side: the mirror of the left
  const mir = i => { let b = -1, d = Infinity; for (let j = 0; j < N; j++) { if (!used[j]) continue; const e = Math.hypot(X(j) + X(i), Y(j) - Y(i), Z(j) - Z(i)); if (e < d) { d = e; b = j; } } return b; };
  for (const n of ['eye', 'eyeIn', 'eyeOut', 'eyeUp', 'eyeDown', 'brow', 'mouth', 'jaw', 'cheek', 'ear']) L[n + 'R'] = mir(L[n + 'L']);
  MARKS.set(body.mesh.positions, L);
  return L;
}
register({
  kind: 'points', of: 'skin',
  params: { moves: { type: 'map', keys: LANDMARKS, values: v3 }, mirror: flag },
  defaults: { mirror: true },
  rest(p, R, { body }) {
    const F = headFrame(body.rig), L = landmarksOf(body), P = body.mesh.positions, { omega } = headShares(body.mesh, body.rig.skeleton), k = p.strength;
    const moves = { ...p.moves };
    if (p.mirror) for (const [n, d] of Object.entries(p.moves)) if (n.endsWith('L') && !(n.slice(0, -1) + 'R' in p.moves)) moves[n.slice(0, -1) + 'R'] = [-d[0], d[1], d[2]];
    // (two landmarks on one vertex — a head drawn so small that they meet — move it by their mean)
    const byVertex = new Map();
    for (const n of LANDMARKS) { const i = L[n], d = moves[n] ?? [0, 0, 0], o = byVertex.get(i) ?? { d: [0, 0, 0], n: 0 }; for (let c = 0; c < 3; c++) o.d[c] += d[c]; o.n++; byVertex.set(i, o); }
    const src = [], dst = [];
    for (const [i, { d, n }] of byVertex) { const at = [P[i * 3], P[i * 3 + 1], P[i * 3 + 2]]; src.push(at); dst.push(at.map((v, c) => v + d[c] / n * k * F.R)); }
    for (let i = 0; i < body.mesh.N; i += 37) if (body.mesh.isUsed[i] && omega[i] < 0.02 && Math.hypot(P[i * 3] - F.O[0], P[i * 3 + 1] - F.O[1], P[i * 3 + 2] - F.O[2]) < 4 * F.R) { const at = [P[i * 3], P[i * 3 + 1], P[i * 3 + 2]]; src.push(at); dst.push(at); }
    return { positions: warped(body, omega, biharmonic(src, dst)) };
  },
});
const warped = (body, omega, move) => {
  const P = Float32Array.from(body.mesh.positions), d = [0, 0, 0];
  for (const i of body.mesh.used) { const w = omega[i]; if (w < 1e-3) continue; move(P[i * 3], P[i * 3 + 1], P[i * 3 + 2], d); for (let c = 0; c < 3; c++) P[i * 3 + c] += w * d[c]; }
  return P;
};

// —— a cage on the head ——
const BOX = { min: [-1.3, -1.75, -1.35], max: [1.3, 1.45, 1.55] };
register({
  kind: 'cage', of: 'skin',
  params: { n: { type: 'array', min: 3, max: 3, items: { type: 'integer', min: 2, max: 6 } }, box: { type: 'object', props: { min: v3, max: v3 }, required: ['min', 'max'] },
    moves: { type: 'array', items: { type: 'object', required: ['at', 'by'], props: { at: { type: 'array', min: 3, max: 3, items: { type: 'integer', min: 0, max: 5 } }, by: v3 } } }, mirror: flag },
  defaults: { n: [3, 3, 3], box: BOX, moves: [], mirror: true },
  rest(p, R, { body }) {
    const F = headFrame(body.rig), { omega } = headShares(body.mesh, body.rig.skeleton), [nx, ny, nz] = p.n, k = p.strength;
    const D = new Float64Array(nx * ny * nz * 3), at = (i, j, l) => ((l * ny + j) * nx + i) * 3;
    for (const m of p.moves) {
      if (m.at.some((v, c) => v >= p.n[c])) throw new Error(`cage: a point ${JSON.stringify(m.at)} outside its ${p.n.join('×')} lattice`);
      const put = (i, sx) => { const o = at(i, m.at[1], m.at[2]); D[o] += sx * m.by[0]; D[o + 1] += m.by[1]; D[o + 2] += m.by[2]; };
      put(m.at[0], 1); if (p.mirror && m.at[0] !== nx - 1 - m.at[0]) put(nx - 1 - m.at[0], -1);
    }
    const bern = (n, t) => { const out = []; for (let i = 0; i < n; i++) out.push(binom(n - 1, i) * t ** i * (1 - t) ** (n - 1 - i)); return out; };
    const B = p.box;
    return { positions: warped(body, omega, (x, y, z, d) => {
      const l = F.toL(x, y, z), t = l.map((v, c) => (v - B.min[c]) / (B.max[c] - B.min[c]));
      d[0] = d[1] = d[2] = 0; if (t.some(v => v < 0 || v > 1)) return;
      const bx = bern(nx, t[0]), by = bern(ny, t[1]), bz = bern(nz, t[2]);
      for (let c = 0; c < nz; c++) for (let b = 0; b < ny; b++) for (let a = 0; a < nx; a++) { const w = bx[a] * by[b] * bz[c] * k * F.R, o = at(a, b, c); d[0] += w * D[o]; d[1] += w * D[o + 1]; d[2] += w * D[o + 2]; }
    }) };
  },
});
const binom = (n, k) => { let r = 1; for (let i = 1; i <= k; i++) r = r * (n - k + i) / i; return r; };

// —— smooth warps ——
const WARP = { type: 'union', key: 'kind', cases: {
  push: { type: 'object', required: ['kind', 'at', 'r', 'by'], props: { kind: { const: 'push' }, at: v3, r: num(0.01, 3), by: v3, mirror: flag } },
  scale: { type: 'object', required: ['kind', 'y', 'r'], props: { kind: { const: 'scale' }, y: num(-3, 3), r: num(0.01, 3), x: num(0.2, 3), z: num(0.2, 3) } } } };
register({
  kind: 'warps', of: 'skin',
  params: { warps: { type: 'array', min: 1, items: WARP } },
  defaults: {},
  rest(p, R, { body }) {
    const F = headFrame(body.rig), { omega } = headShares(body.mesh, body.rig.skeleton), k = p.strength;
    return { positions: warped(body, omega, (x, y, z, d) => {
      const l = F.toL(x, y, z); d[0] = d[1] = d[2] = 0;
      for (const w of p.warps) {
        if (w.kind === 'push') for (const s of w.mirror && w.at[0] ? [1, -1] : [1]) { const f = Math.exp(-((l[0] - s * w.at[0]) ** 2 + (l[1] - w.at[1]) ** 2 + (l[2] - w.at[2]) ** 2) / (w.r * w.r)) * k * F.R; d[0] += s * w.by[0] * f; d[1] += w.by[1] * f; d[2] += w.by[2] * f; }
        else { const f = Math.exp(-(((l[1] - w.y) / w.r) ** 2)) * k; d[0] += l[0] * ((w.x ?? 1) - 1) * f * F.R; d[2] += l[2] * ((w.z ?? 1) - 1) * f * F.R; }
      }
    }) };
  },
});
