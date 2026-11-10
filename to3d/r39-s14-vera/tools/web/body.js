// С14 in 3D — body parts shared by the characters (styles/s14-paper/tools/body.py carried into space):
// SOMA's joints placed by the drawing's sizes, limbs as stiff strips with a brad in the joint, a hand cut from one
// piece with finger snips, a shoe, trunk shells (coat, dress) with pieces glued on them, the ground.
import { ell, curve, patch, loft, tube, slab, ringAt, through, mix, merge, U, V, corner } from './paper.js';

export const BRASS = '#c9a24c';

// SOMA's 77 joints at the drawing's sizes (metres). The bones keep SOMA's rest directions in the arms (so its frames
// carry Kimodo's turns as they are); legs straight down.
export function proportion(sk, P) {
  const R = sk.rest, out = new Float64Array(sk.J * 3), I = n => sk.index[n], rest = n => [R[I(n) * 3], R[I(n) * 3 + 1], R[I(n) * 3 + 2]];
  const set = (n, p) => out.set(p, I(n) * 3), get = n => [out[I(n) * 3], out[I(n) * 3 + 1], out[I(n) * 3 + 2]];
  set('Hips', [0, P.hip, 0]);
  const y0 = rest('Hips')[1], y1 = rest('Neck1')[1];
  for (const n of ['Spine1', 'Spine2', 'Chest']) set(n, [0, P.hip + (rest(n)[1] - y0) / (y1 - y0) * (P.neck - P.hip), 0]);
  set('Neck1', [0, P.neck, 0]); set('Neck2', [0, (P.neck + P.head) / 2, 0]); set('Head', [0, P.head, 0]); set('HeadEnd', [0, P.top, 0]);
  set('Jaw', [0, P.head + .005, .03]);
  for (const [S, s] of [['Left', 1], ['Right', -1]]) {
    set(S + 'Eye', [s * .03, P.head + .06, .07]);
    set(S + 'Shoulder', [s * .015, P.shoulder + .02, 0]);
    set(S + 'Arm', [s * P.shoulderX, P.shoulder, 0]);
    const m = v => [s * v[0], v[1], v[2]];
    const up = V.norm(V.sub(rest('LeftForeArm'), rest('LeftArm'))), fo = V.norm(V.sub(rest('LeftHand'), rest('LeftForeArm')));
    set(S + 'ForeArm', V.add(get(S + 'Arm'), m(V.mul(up, P.upper))));
    set(S + 'Hand', V.add(get(S + 'ForeArm'), m(V.mul(fo, P.fore))));
    for (let j = 0; j < sk.J; j++) if (sk.names[j].startsWith(S + 'Hand') && sk.names[j] !== S + 'Hand') set(sk.names[j], V.add(get(S + 'Hand'), m(V.mul(V.sub(rest('Left' + sk.names[j].slice(S.length)), rest('LeftHand')), P.hand ?? .8))));
    set(S + 'Leg', [s * P.legX, P.leg, 0]); set(S + 'Shin', [s * (P.kneeX ?? P.legX), P.knee, .004]); set(S + 'Foot', [s * (P.footX ?? P.legX), P.ankle, -.012]);
    set(S + 'ToeBase', [s * (P.footX ?? P.legX), .02, -.012 + (P.foot ?? .1) * .75]); set(S + 'ToeEnd', [s * (P.footX ?? P.legX), .008, -.012 + (P.foot ?? .1) * 1.15]);
  }
  return out;
}

// a limb: one stiff strip per bone, overlapping at the joints (round ends); brads go in separately
export function limbPiece(fig, joint, child, ra, rb, o) {
  const a = fig.R(joint), b = o.to || fig.R(child);
  return fig.piece({ name: joint, joint, geo: tube(o.from || a, b, ra * U, rb * U, { flat: o.flat ?? .8, n: 16 }), color: o.color, kind: o.kind || 'card', v: o.v });
}
export function brad(fig, joint, r = 3.4, out = .03) {
  fig.bill({ joint, at: fig.R(joint), r: r * U, out, discs: [{ k: 1, color: BRASS }, { k: .35, color: '#f3e2a6', dx: -.3, dy: .3 }] });
}

// body.hand's outline: the wrist at (0, 0), fingers along +y (units)
export function handOutline(spread = 0, thumb = 1) {
  const ky = 13, cx = [-7.5, -2.5, 2.5, 7.5], hw = 2.7; let ln = [14, 18, 17, 13]; if (thumb < 0) ln = ln.reverse();
  const pts = [[-6.5, -3, 1], [-10.5, 7]];
  for (let i = 0; i < 4; i++) {
    const a = (i - 1.5) * spread * Math.PI / 180, dx = Math.sin(a), dy = Math.cos(a), nx = dy, ny = -dx, bx = cx[i], tx = bx + dx * ln[i], ty = ky + dy * ln[i];
    if (i > 0) pts.push([(cx[i - 1] + bx) / 2, ky + Math.min(ln[i - 1], ln[i]) * (spread < 6 ? .45 : .05), 1]);
    pts.push([bx - nx * hw + dx * ln[i] * .7, ky - ny * hw + dy * ln[i] * .7], [tx - nx * hw * .6, ty - ny * hw * .6 - .5 * dy], [tx, ty + .8], [tx + nx * hw * .6, ty + ny * hw * .6 - .5 * dy], [bx + nx * hw + dx * ln[i] * .7, ky + ny * hw + dy * ln[i] * .7]);
  }
  pts.push([10.5, 7], [6.5, -3, 1]);
  const t = thumb, th = [[t * 6, 1], [t * 13, 6], [t * 18, 15], [t * 16.5, 20], [t * 12.5, 19], [t * 8, 12]];
  return { palm: pts, thumb: thumb ? (t > 0 ? th : th.reverse()) : null };
}
// a hand of paper on the Hand joint: flat, in the plane of the arm and the picture (it faces us when the arm hangs)
export function hand(fig, S, { skin, s = .95, spread = 3, thumb = 1, fist = false }) {
  const w = fig.R(S + 'Hand'), d = V.norm(V.sub(w, fig.R(S + 'ForeArm'))), e = V.norm(V.cross(d, [0, 0, 1])), n = V.cross(e, d);
  const place = (x, y, t) => V.add(w, V.add(V.add(V.mul(e, x * s * U), V.mul(d, (y + 1) * s * U)), V.mul(n, t)));
  const o = handOutline(spread, thumb);
  if (fist) { o.palm = [[-7, -3, 1], [-10, 6], [-10, 15], [-5, 19], [0, 17.5, 1], [5, 19], [10, 15], [10, 6], [7, -3, 1]]; o.thumb = [[-11, 6], [-3, 5], [2, 8], [-2, 12], [-11, 11]]; }
  (fig.handN ??= {})[S] = n; (fig.handE ??= {})[S] = e;
  if (o.thumb) fig.piece({ name: S + 'Thumb', joint: S + 'Hand', geo: slab(o.thumb, (x, y, t) => place(x, y, t + (fist ? .003 : -.0025)), { thick: .002 }), color: mix(skin, '#c0705c', .10), kind: 'card' });
  fig.piece({ name: S + 'Palm', joint: S + 'Hand', geo: slab(o.palm, place, { thick: .003, maxEdge: 12 }), color: skin, kind: 'card' });
}
// turn the hand about its fingers so that its face looks along `to` as far as it can
export function faceHand(fig, pose, S, to) {
  const sk = fig.sk, j = sk.index[S + 'Hand'], q = [pose.Q[j * 4], pose.Q[j * 4 + 1], pose.Q[j * 4 + 2], pose.Q[j * 4 + 3]];
  const rot = (v) => { const [x, y, z, w] = q, t = [2 * (y * v[2] - z * v[1]), 2 * (z * v[0] - x * v[2]), 2 * (x * v[1] - y * v[0])]; return [v[0] + w * t[0] + y * t[2] - z * t[1], v[1] + w * t[1] + z * t[0] - x * t[2], v[2] + w * t[2] + x * t[1] - y * t[0]]; };
  const d0 = V.norm(V.sub(fig.R(S + 'Hand'), fig.R(S + 'ForeArm'))), ax = V.norm(rot(d0)), n = rot(fig.handN[S]);
  const proj = v => V.norm(V.sub(v, V.mul(ax, v[0] * ax[0] + v[1] * ax[1] + v[2] * ax[2])));
  const a = proj(n), b = proj(to), c = V.cross(a, b), ang = Math.atan2(c[0] * ax[0] + c[1] * ax[1] + c[2] * ax[2], a[0] * b[0] + a[1] * b[1] + a[2] * b[2]);
  fig.turn(pose, S + 'Hand', ax, ang * 180 / Math.PI);
}

// a shoe on the Foot joint: body.shoe's (or body.boot's) side outline swept across the foot's width. L, h, w in units;
// sole: its colour (a thicker slab under the upper); lace: a colour — three small strips over the instep
export function shoe(fig, S, { L = 40, h = 20, w = 17, color, sole = null, toeOut = 8, boot = false, lace = null }) {
  const f = fig.R(S + 'Foot'), s = S === 'Left' ? 1 : -1, a = s * toeOut * Math.PI / 180, heel = -L * .30;
  const top = boot ? through([[0, 1], [.36, 1], [.47, .55], [.9, .44], [1, .16]]) : through([[0, .9], [.28, 1], [.62, .62], [.95, .5], [1, .14]]);
  const wid = through([[0, .72], [.3, 1], [.7, 1], [1, .62]]);
  const at = (x, y, z) => { const X = x * Math.cos(a) + z * Math.sin(a), Z = -x * Math.sin(a) + z * Math.cos(a); return [f[0] + X * U, y * U, f[2] + Z * U]; };
  const mk = (y0, ht, grow) => {
    const rings = [];
    for (let i = 0; i <= 14; i++) {
      const t = i / 14, z = heel + L * t + (grow > 1 ? (t - .5) * 4 : 0), hw = w / 2 * wid(t) * grow, hh = ht ?? h * top(t);
      rings.push(Array.from({ length: 14 }, (_, k) => { const u = 2 * Math.PI * k / 14, c = Math.cos(u), sn = Math.sin(u); return at(hw * Math.sign(c) * Math.abs(c) ** .7, y0 + (sn > 0 ? hh * sn ** (boot ? .5 : .8) : 0), z); }));
    }
    return loft(rings, { cap0: true, cap1: true });
  };
  const sh = sole ? h * (boot ? .13 : .16) : 0;
  if (sole) fig.piece({ name: S + 'Sole', joint: S + 'Foot', geo: mk(0, sh, 1.1), color: sole, kind: 'card' });
  fig.piece({ name: S + 'Shoe', joint: S + 'Foot', geo: mk(sh * .9, null, 1), color, kind: 'card' });
  if (lace) for (let i = 0; i < 3; i++) {
    const t = .50 + i * .1, z = heel + L * t, y = sh * .9 + h * top(t) + 1.6, hw = w / 2 * wid(t) * .8;
    fig.piece({ name: S + 'Lace' + i, joint: S + 'Foot', geo: slab([[-hw, -1.5, 1], [hw, -1.5, 1], [hw, 1.5, 1], [-hw, 1.5, 1]], (x, v, tt) => { const p = at(x, y - Math.abs(x) * .25 - (v - 1) * .3, z + v); return [p[0], p[1] + tt, p[2]]; }, { thick: .001 }), color: lace, kind: 'flat' });
  }
}

// a trunk shell from sections [[height (units), half-width, front, back], …] (top first or bottom first — any order)
export function shell(sections, { n = 40, p = .8, rows = 26 } = {}) {
  const S = sections.slice().sort((a, b) => a[0] - b[0]), hw = through(S.map(s => [s[0], s[1]])), zf = through(S.map(s => [s[0], s[2]])), zb = through(S.map(s => [s[0], s[3]]));
  const h0 = S[0][0], h1 = S[S.length - 1][0];
  const sh = { h0, h1, hw, zf, zb };
  // the front (or the back) surface under a point of the front view; out: units above the surface
  sh.z = (x, h, back = false) => { const w = hw(h), c = Math.min(1, Math.abs(x) / w) ** (1 / p), s = Math.sqrt(Math.max(0, 1 - c * c)) ** p, zc = (zf(h) + zb(h)) / 2, d = (zf(h) - zb(h)) / 2; return zc + (back ? -1 : 1) * d * s; };
  sh.mesh = (o = {}) => {
    const rings = [];
    for (let i = 0; i <= rows; i++) { const h = h1 + (h0 - h1) * i / rows; rings.push(ringAt(h * U, hw(h) * U, zf(h) * U, zb(h) * U, n, p)); }
    return loft(rings, { cap0: o.capTop ?? true, cap1: o.capBottom ?? false });
  };
  // an outline of the front view glued on the shell's front, `out` units above it
  sh.on = (pts, out = .5, o = {}) => patch(pts, (x, y) => [x * U, -y * U, (sh.z(x, -y) + out) * U], { maxEdge: o.maxEdge ?? 9, dense: o.dense, holes: o.holes });
  return sh;
}

// the ground: a torn piece of paper lying under the figure (white core showing along the tear) and scraps on it
export function ground(look, { color, path = false, seed = 5 }) {
  let s = seed; const r = () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
  const out = [], core = [];
  const pt = (x, z, nx, nz) => { const j = (r() - .5) * .03 + (r() < .15 ? (r() - .5) * .05 : 0), k = .012 + r() * .016; out.push([x + nx * j, z + nz * j]); core.push([x + nx * (j + k), z + nz * (j + k)]); };
  if (!path) for (let i = 0; i < 160; i++) { const a = 2 * Math.PI * i / 160; pt(.78 * Math.cos(a), .1 + .62 * Math.sin(a), Math.cos(a), Math.sin(a)); }
  else {
    const W = 1.5, Z0 = -5, N = 420;
    for (let i = 0; i <= N; i++) pt(W, Z0 + i * .05, 1, 0);
    for (let i = 1; i < 40; i++) pt(W - i * 2 * W / 40, Z0 + N * .05, 0, 1);
    for (let i = N; i >= 0; i--) pt(-W, Z0 + i * .05, -1, 0);
    for (let i = 1; i < 40; i++) pt(-W + i * 2 * W / 40, Z0, 0, -1);
  }
  const lay = (poly, y) => patch(poly, (x, z) => [x, y, z], { dense: true, maxEdge: 9 });
  const pieces = [look.add({ geo: lay(core, -.002), color: '#f7f2e7', kind: 'ground' }), look.add({ geo: lay(out, 0), color, kind: 'ground', paint: false })];
  // scraps: small bits of paper lying about (they show the way walked)
  const n = path ? 90 : 9;
  for (let i = 0; i < n; i++) {
    const x = (r() - .5) * (path ? 2.6 : 1.3), z = path ? -3 + r() * 18 : -.35 + r() * .95, rr = .012 + r() * .022, a = r() * 360;
    if (Math.hypot(x, z) < .28) continue;
    pieces.push(look.add({ geo: patch(ell(x, z, rr, rr * (.5 + r() * .5), a, 5 + Math.floor(r() * 3)).map(q => r() < .5 ? corner(q) : q), (u, v) => [u, .0015, v], { maxEdge: 9 }), color: mix(color, r() < .5 ? '#fff6e6' : '#2b1b2c', .12 + r() * .16), kind: 'flat' }));
  }
  return pieces;
}
