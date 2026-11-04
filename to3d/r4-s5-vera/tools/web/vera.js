// Вера (style С5, «инди») in 3D: the indie constructor's simple forms on SOMA's joints, built from the very numbers
// the drawing was made of (styles/s5-indie/tools/cast.py: stacks of elliptic rings, tubes, spheres), coloured with
// the drawing's paints, the face signs projected from the drawing itself, a flat two-tone look with a warm outline,
// moved by Kimodo's motions (experiments/indie/motions, retargeted as experiments/indie does).
// window.A.set({...}) sets what is shown; window.A.render() draws. See shots.mjs.
import * as THREE from 'three';
import { lerp, clamp, smooth, smin, smax, ellipsoid, oell, cone, add, sub, mul, surfaceNets, sph, ell, rbox, inter, capsule, horn } from './forms.js';

// ———————————— the drawing's units → metres ————————————
// the drawing: units, y down, the ground at y = 0, she is 464 units tall. Here: metres, y up, 1 unit = 2.5 mm (1.16 m)
const S = 1 / 400;
const P = (X, Y, Z = 0) => [X * S, -Y * S, Z * S];
const HEAD_Y = -352;                       // the head's centre in the drawing (cast.vera: translate(0,-352))

// ———————————— the drawing's paints (cast.vera, geo.py) ————————————
const C = {
  hair: '#3c2f3b', coat: '#2f5b5f', neck: '#7a4560', trous: '#3a3940', shoe: '#26232a', skin: '#f7d7bf', skinSh: '#efbfa6',
  line: '#4a3036', folder: '#e9dcc0', tick: '#d36b5a', pencil: '#e9b949', eraser: '#e58a8a', ring: '#cfd6dc', button: '#1f3c3f', shine: '#ffffff',
};
const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255);
const mixc = (a, b, t) => a.map((x, i) => x + (b[i] - x) * t);
const shadeOf = h => mixc(hex(h), hex('#2a1f3d'), 0.28);   // geo.shade_of: darker, toward violet

// ———————————— a stack of elliptic rings (the drawing's volume) as a distance ————————————
const cr = (a, b, c, d, t) => 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t * t * t);
function ringTable(rings, out = 0) {
  let R = rings.map(r => [r[0], r[1], r[2], r[3] || 0, r[4] || 0]);
  if (out) { R = R.map(r => [r[0], r[1] ? r[1] + out : 0, r[2] ? r[2] + out : 0, r[3], r[4]]); R[0][0] -= out; }
  // smooth through the rings as the drawing's outline does (Catmull-Rom), then a dense table along y
  const D = [];
  for (let i = 0; i < R.length - 1; i++) {
    const p0 = R[Math.max(i - 1, 0)], p1 = R[i], p2 = R[i + 1], p3 = R[Math.min(i + 2, R.length - 1)];
    for (let j = 0; j < 16; j++) D.push(p1.map((_, k) => cr(p0[k], p1[k], p2[k], p3[k], j / 16)));
  }
  D.push(R[R.length - 1].slice());
  for (let i = 1; i < D.length; i++) D[i][0] = Math.max(D[i][0], D[i - 1][0] + 1e-4);
  for (const d of D) { d[1] = Math.max(d[1], 0); d[2] = Math.max(d[2], 0); }
  const y0 = D[0][0], y1 = D[D.length - 1][0], N = 400, T = new Float32Array(N * 4);
  let j = 0;
  for (let i = 0; i < N; i++) {
    const y = y0 + (y1 - y0) * i / (N - 1);
    while (j < D.length - 2 && D[j + 1][0] < y) j++;
    const a = D[j], b = D[j + 1], t = clamp((y - a[0]) / (b[0] - a[0]), 0, 1);
    for (let k = 0; k < 4; k++) T[i * 4 + k] = lerp(a[k + 1], b[k + 1], t);
  }
  const at = y => { const f = clamp((y - y0) / (y1 - y0), 0, 1) * (N - 1), i = Math.min(Math.floor(f), N - 2), t = f - i; return [0, 1, 2, 3].map(k => lerp(T[i * 4 + k], T[i * 4 + 4 + k], t)); };
  return { y0, y1, at };
}
// o: where the stack's own (0,0,0) is, in drawing units
function rings(rs, { out = 0, o = [0, 0, 0] } = {}) {
  const tb = ringTable(rs, out), dy = (tb.y1 - tb.y0) / 399;
  return (x, y, z) => {
    const X = x / S - o[0], Y = -y / S - o[1], Z = z / S - o[2];
    const Yc = clamp(Y, tb.y0, tb.y1), [w, d, cx, cz] = tb.at(Yc);
    const px = X - cx, pz = Z - cz, W = Math.max(w, 0.3), Dd = Math.max(d, 0.3);
    const k0 = Math.hypot(px / W, pz / Dd), k1 = Math.hypot(px / (W * W), pz / (Dd * Dd));
    let dh = k1 < 1e-9 ? -Math.min(W, Dd) : k0 * (k0 - 1) / k1;
    if (Y < tb.y0 || Y > tb.y1) return Math.hypot(Math.max(dh, 0), Y - Yc) * S;
    // a slanted wall: the level distance is longer than the true one
    const a = tb.at(Yc - 2 * dy), b = tb.at(Yc + 2 * dy), sl = Math.max(Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1])) / (4 * dy);
    return dh / Math.hypot(1, sl) * S;
  };
}
// a point on a ring stack at angle phi (0 = front, + toward +X) and height y, pushed out by `out` (geo.surf)
function surf(tb, phi, y, out = 0, o = [0, 0, 0]) {
  const [w, d, cx, cz] = tb.at(y);
  return [o[0] + cx + (w + out) * Math.sin(phi), o[1] + y, o[2] + cz + (d + out) * Math.cos(phi)];
}

// ———————————— Вера's forms: cast.vera's numbers ————————————
const HEAD = [[-72, 0, 0, 0, -3], [-66, 30, 32, 0, -3], [-50, 52, 54, 0, -3], [-24, 59, 60, 0, -2], [4, 59, 58, 0, 2],
  [26, 55, 52, 0, 5], [44, 44, 41, 0, 9], [58, 27, 27, 0, 12], [66, 11, 13, 0, 13], [68, 0, 0, 0, 13]];
const BUN = [[-112, 0, 0, 0, -18], [-106, 22, 22, 0, -20], [-92, 30, 30, 0, -22], [-76, 27, 27, 0, -22], [-68, 0, 0, 0, -22]];
const HAIRLINE = [[-2.6, 40], [-2.0, 20], [-1.75, 0], [-1.55, -6], [-1.35, 0], [-1.12, -8], [-0.85, -22], [-0.5, -32], [-0.15, -36],
  [0.2, -42], [0.38, -50], [0.5, -44], [0.8, -34], [1.1, -18], [1.35, -2], [1.55, -6], [1.75, 0], [2.0, 20], [2.6, 40]];
const NECK = [[-296, 0, 0, 0, 2], [-292, 22, 22, 0, 2], [-280, 26, 25, 0, 2], [-266, 28, 26, 0, 2], [-262, 0, 0, 0, 2]];
const COAT = [[-272, 0, 0], [-268, 34, 26], [-258, 48, 34], [-230, 50, 36], [-180, 48, 36], [-140, 52, 38], [-90, 60, 42], [-62, 64, 44], [-58, 0, 0]];
const shoe = X => [[-16, 0, 0, X, 4], [-14, 10, 11, X, 4], [-6, 11, 18, X, 7], [0, 10, 19, X, 9], [1, 0, 0, X, 9]];
const HO = [0, HEAD_Y, 0];                 // the head's own origin
const headT = ringTable(HEAD);

// the hairline: keys (phi, y) on the head, closed around it (cast.vera's `hl`), smoothed as the drawing smooths it
function hairlineAt() {
  const K = HAIRLINE, ext = [...K.map(([p, y]) => [p - 2 * Math.PI, y]), ...K, ...K.map(([p, y]) => [p + 2 * Math.PI, y])];
  const D = [];
  for (let i = 1; i < ext.length - 2; i++) for (let j = 0; j < 8; j++) D.push([0, 1].map(k => cr(ext[i - 1][k], ext[i][k], ext[i + 1][k], ext[i + 2][k], j / 8)));
  D.sort((a, b) => a[0] - b[0]);
  return phi => { let i = 0; while (i < D.length - 2 && D[i + 1][0] < phi) i++; const a = D[i], b = D[i + 1]; return lerp(a[1], b[1], clamp((phi - a[0]) / (b[0] - a[0]), 0, 1)); };
}
const hairY = hairlineAt();
const HL_N = 720, HL = new Float32Array(HL_N + 1);
for (let i = 0; i <= HL_N; i++) HL[i] = hairY(-Math.PI + 2 * Math.PI * i / HL_N);
const hairlineY = phi => { const f = (phi + Math.PI) / (2 * Math.PI) * HL_N, i = clamp(Math.floor(f), 0, HL_N - 1); return lerp(HL[i], HL[i + 1], f - i); };

// the skeleton: SOMA's joints (no fingers), placed on the drawing (units)
const PARENT = {
  Hips: null, Spine1: 'Hips', Spine2: 'Spine1', Chest: 'Spine2', Neck1: 'Chest', Neck2: 'Neck1', Head: 'Neck2', HeadEnd: 'Head', Jaw: 'Head', LeftEye: 'Head', RightEye: 'Head',
  LeftShoulder: 'Chest', LeftArm: 'LeftShoulder', LeftForeArm: 'LeftArm', LeftHand: 'LeftForeArm',
  RightShoulder: 'Chest', RightArm: 'RightShoulder', RightForeArm: 'RightArm', RightHand: 'RightForeArm',
  LeftLeg: 'Hips', LeftShin: 'LeftLeg', LeftFoot: 'LeftShin', LeftToeBase: 'LeftFoot', LeftToeEnd: 'LeftToeBase',
  RightLeg: 'Hips', RightShin: 'RightLeg', RightFoot: 'RightShin', RightToeBase: 'RightFoot', RightToeEnd: 'RightToeBase',
};
const JU = {
  Hips: [0, -105, 0], Spine1: [0, -157, 0], Spine2: [0, -210, 0], Chest: [0, -258, 0], Neck1: [0, -270, 1], Neck2: [0, -280, 2], Head: [0, -290, 2],
  HeadEnd: [0, -424, -3], Jaw: [0, -310, 30], LeftEye: [24, -344, 55], RightEye: [-24, -344, 55],
};
// the arms as drawn: shoulder, elbow, hand — holding the folder at the chest (this is their rest). The drawing lays
// the sleeves over the coat, though by its numbers they would sit inside it; here the shoulder and elbow are moved a
// few units out so that the sleeves lie on the coat as drawn
for (const [s, k] of [['Left', 1], ['Right', -1]]) {
  JU[s + 'Shoulder'] = [k * 14, -262, 0]; JU[s + 'Arm'] = [k * 45, -258, 4]; JU[s + 'ForeArm'] = [k * 55, -212, 22]; JU[s + 'Hand'] = [k * 18, -186, 50];
  JU[s + 'Leg'] = [k * 15, -105, 0]; JU[s + 'Shin'] = [k * 15, -58, 2]; JU[s + 'Foot'] = [k * 15, -14, 0]; JU[s + 'ToeBase'] = [k * 15, -5, 14]; JU[s + 'ToeEnd'] = [k * 15, -3, 27];
}
const J = Object.fromEntries(Object.entries(JU).map(([b, p]) => [b, P(...p)]));
const BONES = Object.keys(PARENT), BI = Object.fromEntries(BONES.map((b, i) => [b, i]));

// weights along a vertical chain of bones (the coat, the turtleneck): each point between the two nearest joints by height
const chain = names => (x, y) => {
  const hs = names.map(n => J[n][1]);
  if (y <= hs[0]) return { [names[0]]: 1 };
  for (let i = 0; i < names.length - 1; i++) if (y <= hs[i + 1]) { const t = smooth((y - hs[i]) / (hs[i + 1] - hs[i])); return { [names[i]]: 1 - t, [names[i + 1]]: t }; }
  return { [names[names.length - 1]]: 1 };
};
const coatW = chain(['Hips', 'Spine1', 'Spine2', 'Chest']), neckW = chain(['Chest', 'Neck1', 'Neck2']);

// a part: [group, bone | [bone, bone] | weights(x,y,z), distance, paint, shade paint?]
function vera() {
  const parts = [];
  const add_ = (g, b, f, c, sh) => parts.push([g, b, f, c, sh]);
  // head: the drawing's ring stack; a small nose that shows in profile (cast.small_nose)
  add_('head', 'Head', rings(HEAD, { o: HO }), C.skin, C.skinSh);
  add_('head', 'Head', ell(P(0, HEAD_Y + 24, 57.5), [4.2 * S, 5 * S, 5 * S]), C.skin, C.skinSh);
  // ears with a small earring, on the head's sides (cast.vera: phi ±1.6, y 6, a bit inside the skin)
  for (const k of [-1, 1]) {
    const e = surf(headT, k * 1.6, 6, 0.5, HO);
    add_('ears', 'Head', oell(P(...e), [k * 1, 0, 0.03], [0, 1, 0], 3.2 * S, 11 * S, 8.5 * S), C.skin, C.skinSh);
    add_('ring', 'Head', sph(P(e[0] + k * 1, e[1] + 11, e[2]), 2.6 * S), C.ring);
  }
  // hair: the head grown by 4 units, kept above the hairline; the bun behind the crown joins it
  const cap = rings(HEAD, { out: 4, o: HO });
  const above = (x, y, z) => {
    const X = x / S, Y = -y / S - HEAD_Y, Z = z / S, [w, d, cx, cz] = headT.at(clamp(Y, headT.y0, headT.y1));
    const phi = Math.atan2((X - cx) / Math.max(w, 1), (Z - cz) / Math.max(d, 1));
    return (Y - hairlineY(phi)) * S;
  };
  add_('hair', 'Head', inter(cap, above, 1.2 * S), C.hair);
  add_('hair', 'Head', rings(BUN, { o: HO }), C.hair);
  // the pencil through the bun (cast.vera: from (-40,-104,-10) to (40,-84,-34), a pink end)
  add_('pencil', 'Head', capsule(P(-40, HEAD_Y - 104, -10), P(38, HEAD_Y - 84.5, -33.4), 2.6 * S), C.pencil);
  add_('eraser', 'Head', sph(P(40, HEAD_Y - 84, -34), 3.1 * S), C.eraser);
  // glasses: two soft rectangles (30 × 22, corners 6) before the eyes, following the face's turn; a bridge; arms to the ears
  const eyes = [-1, 1].map(k => surf(headT, k * 0.42, 8, 0, HO));
  const surfZ = (X, Y) => { const [w, d, cx, cz] = headT.at(Y - HEAD_Y); return cz + d * Math.sqrt(Math.max(0, 1 - ((X - cx) / w) ** 2)); };
  const lens = [];
  for (const [i, k] of [[0, -1], [1, 1]]) {
    const e = eyes[i], xi = e[0] - k * 15, xo = e[0] + k * 15, zi = surfZ(xi, e[1]) + 4.5, zo = surfZ(xo, e[1]) + 6.5;
    const c = [e[0], e[1], (zi + zo) / 2], u = [xo - xi, 0, zo - zi], L = Math.hypot(u[0], u[2]); u[0] /= L; u[2] /= L;
    const n = [-u[2] * k, 0, u[0] * k];      // the lens's forward
    const hw = L / 2, hh = 11, r = 6, t = 1.05;
    lens.push({ c, u, n, hw, k, xo, zo, xi, zi });
    add_('glasses', 'Head', (x, y, z) => {
      const q = [x / S - c[0], -y / S - c[1], z / S - c[2]];
      const a = q[0] * u[0] + q[2] * u[2], b = q[1], m = q[0] * n[0] + q[2] * n[2];
      const dx = Math.abs(a) - hw + r, dy = Math.abs(b) - hh + r;
      const d2 = Math.hypot(Math.max(dx, 0), Math.max(dy, 0)) + Math.min(Math.max(dx, dy), 0) - r;
      return (Math.hypot(d2, m) - t) * S;
    }, C.line);
    // a small white glint on the glass (cast.vera: from (x - w/2, y - 7), 0.45 w long, rising 2)
    const g0 = [c[0] - hw * 0.5, c[1] - 7, 0], g1 = [c[0] - hw * 0.05, c[1] - 9, 0];
    for (const g of [g0, g1]) { const a = g[0] - c[0]; g[2] = c[2] + a * u[2] / u[0]; }
    add_('shine', 'Head', capsule(P(...g0), P(...g1), 0.75 * S), C.shine, C.shine);
  }
  const [l0, l1] = lens;
  // the bridge: from lens to lens over the nose, a little higher (Q through the middle, 4 up)
  add_('glasses', 'Head', horn(P(l0.c[0] + l0.hw * l0.u[0] * 1, l0.c[1] - 3, l0.c[2] + l0.hw * l0.u[2]), P(0, l0.c[1] - 7.5, surfZ(0, l0.c[1]) + 6), P(l1.c[0] - l1.hw * l1.u[0], l1.c[1] - 3, l1.c[2] - l1.hw * l1.u[2]), 1.05 * S, 1.05 * S, 8), C.line);
  // the arms: from each lens's outer edge back to the ear, a little off the head
  for (const l of lens) {
    const a = [l.xo, l.c[1] - 5, l.zo], ear = surf(headT, l.k * 1.5, 2, 1.5, HO), mid = surf(headT, l.k * 1.05, 0, 7, HO);
    add_('glasses', 'Head', horn(P(...a), P(...mid), P(...ear), 1.05 * S, 1.05 * S, 10), C.line);
  }
  // the turtleneck and the long coat
  add_('neck', neckW, rings(NECK), C.neck);
  const coat = rings(COAT), coatT = ringTable(COAT);
  add_('coat', coatW, coat, C.coat);
  // the coat's front edge: a line down the coat (phi .12 at the collar to .16 at the hem), and three buttons
  for (let i = 0; i < 10; i++) {
    const t0 = i / 10, t1 = (i + 1) / 10, y0 = lerp(-262, -64, t0), y1 = lerp(-262, -64, t1);
    add_('coatline', coatW, capsule(P(...surf(coatT, lerp(0.12, 0.16, t0), y0, 0.3)), P(...surf(coatT, lerp(0.12, 0.16, t1), y1, 0.3)), 1.05 * S), C.line);
  }
  for (const yb of [-236, -204, -172]) add_('buttons', coatW, sph(P(...surf(coatT, 0.26, yb, 0.6)), 3.4 * S), C.button);
  // arms: tubes 17 wide from shoulder past the elbow to the hand, round hands (cast.vera)
  for (const s of ['Left', 'Right']) {
    // (while she holds the folder, the arms, hands and folder are weighted along the body like the coat, so the
    // folder stays on the coat when the spine bends; the arm bones are there for motions that free the arms)
    add_('arms', coatW, capsule(J[s + 'Arm'], J[s + 'ForeArm'], 8.5 * S), C.coat);
    add_('arms', coatW, capsule(J[s + 'ForeArm'], J[s + 'Hand'], 8.5 * S), C.coat);
    add_('hands', coatW, sph(add(J[s + 'Hand'], P(0, 0, 2)), 9.5 * S), C.skin, C.skinSh);
    // legs: trouser tubes 17 wide (the thigh hidden in the coat); shoes from the drawing's rings
    add_('legs', [s + 'Leg', s + 'Shin'], capsule(J[s + 'Leg'], J[s + 'Foot'], 8.5 * S), C.trous);
    add_('shoes', s + 'Foot', rings(shoe(J[s + 'Foot'][0] / S)), C.shoe);
  }
  // the folder held to the chest, with a red bookmark out of its top
  add_('folder', coatW, rbox(P(-2, -185, 44), [32 * S, 37 * S, 2.6 * S], 1.2 * S, -0.06), C.folder);
  add_('tick', coatW, capsule(P(-2, -219, 45.5), P(5, -229, 45.5), 1.15 * S), C.tick);
  return parts;
}

// ———————————— building: one mesh per group, skinned to its bones (the constructor's buildParts, with weights by
// height for long things, a shade paint per part, and the face's projection on the head) ————————————
const GRID = { glasses: 0.0011, shine: 0.0009, coatline: 0.0012, buttons: 0.0015, tick: 0.0012, pencil: 0.0015, eraser: 0.0015, ring: 0.0012, ears: 0.002 };
const BLEND = { hair: 2.0 * S, arms: 1.5 * S, head: 3 * S };
// the face texture covers this square of the head's own drawing coordinates (face_tex.py)
const FX0 = -76, FY0 = -84, FW = 152, FH = 160;
function build(parts) {
  const groups = {};
  for (const p of parts) (groups[p[0]] ??= []).push(p);
  const out = [];
  for (const [g, ps] of Object.entries(groups)) {
    const k = BLEND[g] ?? 0.6 * S;
    const sdf = (x, y, z) => { let d = 1e9; for (const p of ps) { const v = p[2](x, y, z); d = d === 1e9 ? v : smin(d, v, k); } return d; };
    const lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9], st = 0.012;
    for (let x = -0.3; x <= 0.3; x += st) for (let y = -0.02; y <= 1.25; y += st) for (let z = -0.2; z <= 0.25; z += st)
      if (sdf(x, y, z) < st) { lo[0] = Math.min(lo[0], x); lo[1] = Math.min(lo[1], y); lo[2] = Math.min(lo[2], z); hi[0] = Math.max(hi[0], x); hi[1] = Math.max(hi[1], y); hi[2] = Math.max(hi[2], z); }
    if (lo[0] > hi[0]) continue;
    const m = surfaceNets(sdf, lo.map(v => v - 2 * st), hi.map(v => v + 2 * st), GRID[g] ?? 0.0035);
    const nv = m.pos.length / 3;
    const si = new Uint16Array(nv * 4), sw = new Float32Array(nv * 4), col = new Float32Array(nv * 3), shd = new Float32Array(nv * 3);
    const cols = ps.map(p => hex(p[3])), shs = ps.map(p => p[4] ? hex(p[4]) : shadeOf(p[3]));
    const acc = new Float32Array(BONES.length);
    for (let v = 0; v < nv; v++) {
      const x = m.pos[v * 3], y = m.pos[v * 3 + 1], z = m.pos[v * 3 + 2];
      const ds = ps.map(p => p[2](x, y, z)), dmin = Math.min(...ds);
      acc.fill(0);
      ps.forEach((p, i) => {
        const w = Math.exp(-Math.max(ds[i] - dmin, 0) / 0.012);
        if (typeof p[1] === 'function') { for (const [b, t] of Object.entries(p[1](x, y, z))) acc[BI[b]] += w * t; }
        else if (Array.isArray(p[1])) {
          const [b0, b1] = p[1], a = J[b0], j = J[b1], e = J[b1.replace('Shin', 'Foot').replace('ForeArm', 'Hand')];
          const L = Math.hypot(...sub(e, a)), t = ((x - a[0]) * (e[0] - a[0]) + (y - a[1]) * (e[1] - a[1]) + (z - a[2]) * (e[2] - a[2])) / (L * L);
          const tj = Math.hypot(...sub(j, a)) / L, f = smooth(clamp((t - tj) / 0.24 + 0.5, 0, 1));
          acc[BI[b0]] += w * (1 - f); acc[BI[b1]] += w * f;
        } else acc[BI[p[1]]] += w;
      });
      const order = [...acc.keys()].sort((a, b) => acc[b] - acc[a]).slice(0, 4);
      let s = 0; for (const b of order) s += acc[b];
      order.forEach((b, i) => { si[v * 4 + i] = b; sw[v * 4 + i] = acc[b] / s; });
      const c = [0, 0, 0], h = [0, 0, 0]; let ws = 0;
      ps.forEach((p, i) => { const w = Math.exp(-Math.max(ds[i] - dmin, 0) / 0.0015); for (let q = 0; q < 3; q++) { c[q] += cols[i][q] * w; h[q] += shs[i][q] * w; } ws += w; });
      for (let q = 0; q < 3; q++) { col[v * 3 + q] = c[q] / ws; shd[v * 3 + q] = h[q] / ws; }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(m.pos, 3));
    geo.setAttribute('normal', new THREE.BufferAttribute(m.nor, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    geo.setAttribute('shade', new THREE.BufferAttribute(shd, 3));
    geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(si, 4));
    geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));
    // the face: a straight projection from the front, in the head's own drawing coordinates
    const uv = new Float32Array(nv * 2), fm = new Float32Array(nv);
    if (g === 'head') for (let v = 0; v < nv; v++) {
      const X = m.pos[v * 3] / S, Y = -m.pos[v * 3 + 1] / S - HEAD_Y, nz = m.nor[v * 3 + 2];
      uv[v * 2] = (X - FX0) / FW; uv[v * 2 + 1] = 1 - (Y - FY0) / FH; fm[v] = smooth(clamp((nz - 0.05) / 0.2, 0, 1));
    }
    geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
    geo.setAttribute('fmask', new THREE.BufferAttribute(fm, 1));
    geo.setIndex(nv > 65535 ? new THREE.Uint32BufferAttribute(m.idx, 1) : new THREE.Uint16BufferAttribute(m.idx, 1));
    out.push({ g, geo });
  }
  return out;
}

// ———————————— the look: the drawing's flat paint and one shade, light from the upper left (held to the view, as a
// drawing's is), a warm outline around each big form ————————————
const VS = `
#include <common>
#include <skinning_pars_vertex>
attribute vec3 shade; attribute float fmask;
varying vec3 vN; varying vec3 vC; varying vec3 vS; varying vec2 vUv; varying float vM;
void main() {
  #include <skinbase_vertex>
  #include <beginnormal_vertex>
  #include <skinnormal_vertex>
  #include <defaultnormal_vertex>
  #include <begin_vertex>
  #include <skinning_vertex>
  #include <project_vertex>
  vN = normalize(transformedNormal); vC = color; vS = shade; vUv = uv; vM = fmask;
}`;
const FS = `
uniform vec3 uL; uniform float uThr; uniform sampler2D uFace; uniform float uUseFace; uniform float uMode;
varying vec3 vN; varying vec3 vC; varying vec3 vS; varying vec2 vUv; varying float vM;
void main() {
  vec3 n = normalize(vN); if (!gl_FrontFacing) n = -n;
  float l = dot(n, normalize(uL));
  vec3 c;
  if (uMode > 0.5) { c = vec3(0.86, 0.82, 0.77) * (0.55 + 0.45 * max(l, 0.0)) + vec3(0.06); }
  else {
    float e = fwidth(l) * 1.2;
    c = mix(vS, vC, smoothstep(uThr - e, uThr + e, l));
    if (uUseFace > 0.5 && vM > 0.0) { vec4 f = texture2D(uFace, vUv); c = mix(c, f.rgb, f.a * vM); }
  }
  gl_FragColor = vec4(c, 1.0);
}`;
const LVS = `
#include <common>
#include <skinning_pars_vertex>
uniform float uW;
void main() {
  #include <skinbase_vertex>
  #include <beginnormal_vertex>
  #include <skinnormal_vertex>
  #include <begin_vertex>
  #include <skinning_vertex>
  transformed += normalize(objectNormal) * uW;
  #include <project_vertex>
}`;
const LFS = `uniform vec3 uCol; void main() { gl_FragColor = vec4(uCol, 1.0); }`;
const LIGHT = new THREE.Vector3(-0.42, 0.3, 0.86);
function bodyMat(face) {
  return new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, vertexColors: true, extensions: { derivatives: true },
    uniforms: { uL: { value: LIGHT }, uThr: { value: 0.28 }, uFace: { value: face || null }, uUseFace: { value: face ? 1 : 0 }, uMode: { value: 0 } } });
}
const LINE_MAT = new THREE.ShaderMaterial({ vertexShader: LVS, fragmentShader: LFS, side: THREE.BackSide, uniforms: { uW: { value: 2.1 * S }, uCol: { value: new THREE.Color().setRGB(...hex(C.line)) } } });
const NO_LINE = new Set(['glasses', 'shine', 'coatline', 'buttons', 'tick', 'ring']);

// ———————————— the scene ————————————
const cv = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;   // paints go to the screen as written
const scene = new THREE.Scene();
const BG = '#ece5d9';
scene.background = new THREE.Color().setRGB(...hex(BG));
const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 50), persp = new THREE.PerspectiveCamera(22, 1, 0.05, 60);
let camera = ortho;
// a soft round shadow on the floor (the drawing's ground ellipse)
const shadowMat = new THREE.MeshBasicMaterial({ color: new THREE.Color().setRGB(...hex('#2a1f3d')), transparent: true, opacity: 0.13, depthWrite: false });
const loader = new THREE.TextureLoader();
const FACES = {};
const face = ex => FACES[ex] ??= new Promise(r => loader.load(`../tex/face-${ex}.png`, t => { t.colorSpace = THREE.NoColorSpace; t.anisotropy = 4; r(t); }));
const MESHES = build(vera());

function instance(tex) {
  const bones = {}, root = new THREE.Group();
  for (const b of BONES) { bones[b] = new THREE.Bone(); bones[b].name = b; }
  for (const b of BONES) { const p = PARENT[b], pp = p ? J[p] : [0, 0, 0]; bones[b].position.set(...sub(J[b], pp)); if (p) bones[p].add(bones[b]); else root.add(bones[b]); }
  const skel = new THREE.Skeleton(BONES.map(b => bones[b]));
  root.updateMatrixWorld(true); skel.calculateInverses();
  const meshes = [], outlines = [], mats = [];
  for (const { g, geo } of MESHES) {
    const mat = bodyMat(g === 'head' ? tex : null); mats.push(mat);
    const m = new THREE.SkinnedMesh(geo, mat); m.frustumCulled = false; m.bind(skel); m.userData.g = g; root.add(m); meshes.push(m);
    if (!NO_LINE.has(g)) { const o = new THREE.SkinnedMesh(geo, LINE_MAT); o.frustumCulled = false; o.bind(skel); root.add(o); outlines.push(o); }
  }
  const shadow = new THREE.Mesh(new THREE.CircleGeometry(1, 48), shadowMat); shadow.rotation.x = -Math.PI / 2; shadow.scale.set(56 * S, 40 * S, 1); shadow.position.y = 0.001; shadow.renderOrder = -1;
  scene.add(shadow);
  return { root, bones, meshes, outlines, mats, shadow };
}

// ———————————— Kimodo's motions (experiments/indie's retargeting): each SOMA joint turns as in the motion, a fixed
// turn first brings our bone to SOMA's rest direction; the pelvis goes as high and as far as our legs make it; the
// feet are put back on the floor. The arms keep the folder at the chest: they stay as drawn and go with the chest ————————————
const MOTION = {};
const motion = name => MOTION[name] ??= fetch(`../../../../experiments/indie/motions/${name}.json`).then(r => r.json());
const LEGCHAIN = { LeftLeg: 'LeftShin', LeftShin: 'LeftFoot', LeftFoot: 'LeftToeBase', RightLeg: 'RightShin', RightShin: 'RightFoot', RightFoot: 'RightToeBase' };
const HELD = /Shoulder|Arm|Hand/;
let CT = null;
function restTurns(M) {
  return CT ??= Object.fromEntries(Object.entries(LEGCHAIN).map(([b, c]) => [b, new THREE.Quaternion().setFromUnitVectors(
    new THREE.Vector3(...sub(J[c], J[b])).normalize(), new THREE.Vector3(...sub(M.rest[c], M.rest[b])).normalize())]));
}
const _v = new THREE.Vector3();
function poseFromMotion(I, M, f, travel) {
  const CTs = restTurns(M), W = {};
  for (const b of BONES) {
    const p = PARENT[b];
    let w;
    if (M.D[b] && !HELD.test(b)) { const o = f * 4, d = M.D[b]; w = new THREE.Quaternion(d[o], d[o + 1], d[o + 2], d[o + 3]); if (CTs[b]) w.multiply(CTs[b]); }
    else w = p ? W[p].clone() : new THREE.Quaternion();
    W[b] = w;
  }
  for (const b of BONES) { const p = PARENT[b]; I.bones[b].quaternion.copy(p ? W[p].clone().invert().multiply(W[b]) : W[b]); }
  const kr = J.Hips[1] / M.hipY;
  I.bones.Hips.position.set(travel ? (M.hips[f * 3] - M.hips[0]) * kr : 0, M.hips[f * 3 + 1] * kr, travel ? (M.hips[f * 3 + 2] - M.hips[2]) * kr : 0);
  I.root.updateMatrixWorld(true);
  let low = 1e9;
  for (const m of I.meshes) {
    if (m.userData.g !== 'shoes' && m.userData.g !== 'legs') continue;
    const pos = m.geometry.attributes.position;
    for (let i = 0; i < pos.count; i += 5) { _v.fromBufferAttribute(pos, i); m.applyBoneTransform(i, _v); _v.applyMatrix4(m.matrixWorld); if (_v.y < low) low = _v.y; }
  }
  I.bones.Hips.position.y += M.foot[f] * kr - (low - I.root.position.y) + 0.5 * S;
  I.root.updateMatrixWorld(true);
}
// the head's tilt on each expression of the sheet (cast.vera: rotate(tilt), clockwise in the drawing)
const TILT = { neutral: 2, joy: 4, surprise: -2, sad: 6, anger: -2 };

// ———————————— what is shown ————————————
let placed = [], overlay = null;
const state = { view: 'style' };
async function set(o) {
  if (o.size) { renderer.setSize(o.size[0], o.size[1], false); cv.style.width = o.size[0] + 'px'; cv.style.height = o.size[1] + 'px'; }
  if (o.view) state.view = o.view;
  if (o.figures) {
    for (const I of placed) { scene.remove(I.root); scene.remove(I.shadow); }
    placed = [];
    for (const F of o.figures) {
      const ex = F.ex || 'neutral', I = instance(await face(ex));
      I.root.position.set((F.x || 0) * S, 0, (F.z || 0) * S); I.root.rotation.y = (F.yaw || 0) * Math.PI / 180;
      scene.add(I.root);
      if (F.motion) poseFromMotion(I, await motion(F.motion), F.f || 0, F.travel);
      const tilt = F.tilt ?? TILT[ex];
      I.bones.Head.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), -tilt * Math.PI / 180));
      I.root.updateMatrixWorld(true);
      I.bones.Hips.getWorldPosition(_v); I.shadow.position.x = _v.x; I.shadow.position.z = _v.z;
      I.shadow.visible = F.shadow !== false;
      placed.push(I);
    }
  }
  if (o.cam) {
    const c = o.cam;
    if (c.vb) {   // a drawing's viewBox [x, y, w, h] (units, y down), seen straight from the front
      const [x, y, w, h] = c.vb; camera = ortho;
      Object.assign(ortho, { left: x * S, right: (x + w) * S, top: -y * S, bottom: -(y + h) * S });
      ortho.position.set(0, 0, 10); ortho.lookAt(0, 0, 0); ortho.updateProjectionMatrix();
    } else {
      camera = persp; persp.fov = c.fov || 22; persp.aspect = cv.width / cv.height; persp.position.set(...c.pos); persp.lookAt(...c.at); persp.updateProjectionMatrix();
    }
  }
  // line: the outline's width in drawing units (the drawing: 2.4 on a figure, 2.0 on the expression sheet, 1.35 on the portrait)
  if (o.line) LINE_MAT.uniforms.uW.value = o.line * S;
  for (const I of placed) {
    for (const m of I.meshes) m.visible = state.view !== 'skel';
    I.shadow.visible = I.shadow.visible && state.view !== 'skel';
    for (const m of I.mats) m.uniforms.uMode.value = state.view === 'clay' ? 1 : 0;
    for (const m of I.mats) if (m.uniforms.uFace.value) m.uniforms.uUseFace.value = state.view === 'style' || state.view === 'bones' ? 1 : 0;
    for (const o2 of I.outlines) o2.visible = state.view !== 'clay' && state.view !== 'skel';
    for (const m of I.meshes) m.material.transparent = false;
  }
  bonesView(state.view === 'bones' || state.view === 'skel');
}
// the skeleton drawn over the figure
function bonesView(on) {
  if (overlay) { scene.remove(overlay); overlay = null; }
  if (!on) return;
  overlay = new THREE.Group();
  const p = [], d = [], a = new THREE.Vector3(), b = new THREE.Vector3();
  for (const I of placed) for (const bn of BONES) {
    I.bones[bn].getWorldPosition(a); d.push(a.x, a.y, a.z);
    const pb = PARENT[bn]; if (pb) { I.bones[pb].getWorldPosition(b); p.push(b.x, b.y, b.z, a.x, a.y, a.z); }
  }
  const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(p, 3));
  const ln = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: '#c8413b', depthTest: false, transparent: true }));
  const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.Float32BufferAttribute(d, 3));
  const pt = new THREE.Points(pg, new THREE.PointsMaterial({ color: '#c8413b', size: 7, sizeAttenuation: false, depthTest: false, transparent: true }));
  ln.renderOrder = pt.renderOrder = 10;
  overlay.add(ln, pt); scene.add(overlay);
}
function render() { renderer.render(scene, camera); }
window.A = { set, render, S, J };
window.__ready = true;
