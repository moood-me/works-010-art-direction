import { lock, clump, ell, torus, scalpMass, scalp, CRANIUM } from './hair.js';
const hash = x => { const v = Math.sin(x * 12.9898) * 43758.5453; return v - Math.floor(v); };
// smaller locks breaking off a clump's end: one on alternate sides, a second on some, each its own length
const autoKids = (i, seed = 0, o = {}) => [{ side: i % 2 ? 1 : -1, at: 0.45 + 0.15 * hash(i + seed), w: (o.kw ?? 0.34) + 0.12 * hash(i * 3.1 + seed), len: 0.9 + 0.3 * hash(i * 7.3 + seed), spread: 0.8 },
  ...(hash(i * 5.7 + seed) > 0.5 ? [{ side: i % 2 ? -1 : 1, at: 0.6, w: (o.kw ?? 0.34) * 0.75, len: 0.8 + 0.25 * hash(i * 9.1 + seed), spread: 0.6 }] : [])];
const D = Math.PI / 180;
const add = (a, b, f = 1) => a.map((v, i) => v + b[i] * f);
// a point beside the head at azimuth th, height y, distance r from the head's vertical axis
// a lock by azimuths/heights/radii lists: [az, y, r] beside the head, the first point on the scalp at [az, elev]
// path points: [az, elev] or [az, elev, lift] on the scalp (elevation in degrees, so always > 1), or [az, y, r] beside it
const onScalp = q => Math.abs(q[1]) > 1;
const L = (root, path, o = {}) => clump({ pts: [scalp(root[0] * D, root[1] * D, -0.006), ...path.map(q => onScalp(q) ? scalp(q[0] * D, q[1] * D, q[2] ?? o.lift ?? 0.012) : ring(...q))], ...o });
const ring = (th, y, r) => [CRANIUM.c[0] + Math.sin(th * D) * r, y, CRANIUM.c[2] + Math.cos(th * D) * r];

// a fall of locks around the head: each from the scalp near the crown, over the skull, down to its end
function fall(o) {
  const out = [];
  for (let i = 0; i < o.n; i++) {
    const a = o.n === 1 ? o.from : o.from + (o.to - o.from) * i / (o.n - 1);
    const j = o.jit ? Math.sin(i * 12.9898 + (o.seed || 0)) * o.jit : 0;
    const lay = (o.layer || 0) * (i % 2 ? 1 : -1);             // alternate locks sit a little out and in: grooves
    const endY = (typeof o.endY === 'function' ? o.endY(a) : o.endY) + j * 0.01;
    const rootPh = typeof o.rootPh === 'function' ? o.rootPh(a) : o.rootPh;
    const sw = o.sweep || 0, ra = o.rootAz !== undefined ? o.rootAz + (a - o.rootAz) * (o.fan ?? 0.35) : a;
    const pts = [scalp(ra * D, rootPh * D, -0.006), scalp((ra + a) / 2 * D, (rootPh * 0.55 + 12) * D, (o.lift ?? 0.01) + lay)];
    const midY = o.midY ?? 0.0;
    pts.push(ring(a + sw * 0.5, midY, (o.midR ?? 0.104) + lay));
    if (endY < midY - 0.03) pts.push(ring(a + sw * 0.8, (midY + endY) / 2, (o.lowR ?? o.midR ?? 0.104) + lay + (o.flare || 0) * 0.5));
    pts.push(ring(a + sw + (o.tipTurn || 0), endY, (o.endR ?? 0.1) + lay + (o.flare || 0) + (o.tipOut || 0)));
    out.push(clump({ pts, kids: o.kids === false ? [] : autoKids(i, o.seed || 0, o), w: o.w, flat: o.flat ?? 0.6, tip: o.tip ?? 0.3, sharp: o.sharp, color: o.color, vert: o.vert, twist: o.twist, k: o.k, wave: o.wave && { ...o.wave, ph: (o.wave.ph || 0) + i * (o.wave.step ?? 1.9) } }));
  }
  return out;
}


// a fringe: a few clumps from the front of the crown over the forehead; each tip its own length and turn,
// tips tucking in towards the face; widths overlap so they read as one sheet notched only at the tips
function fringe(o) {
  return o.clumps.map(([a, y, w, turn = 0]) => L([a * 0.35 + (o.part || 0), o.rootEl ?? 78], [[a * 0.7 + (o.part || 0) * 0.4, 56, o.lift ?? 0.014], [a + turn * 0.4, 0.045, o.r ?? 0.1], [a + turn, y, (o.r ?? 0.1) - 0.006]],
    { w: [w * 0.7, w, w, w * 0.9], flat: o.flat ?? 0.42, tip: o.tip ?? 0.4, sharp: o.sharp ?? 0.85, color: o.color, k: o.k }));
}
// a braid: lens clumps along the braid's line, each crossing from one side at an angle (a chevron), overlapping
function braid(pts, o) {
  const out = [], n = o.n || 12, P = [];
  for (let i = 0; i <= n; i++) { const u = i / n * (pts.length - 1), k = Math.min(Math.floor(u), pts.length - 2), t = u - k; P.push(pts[k].map((v, j) => v + (pts[k + 1][j] - v) * t)); }
  for (let i = 0; i < n; i++) {
    const a = P[i], b = P[i + 1], T = b.map((v, j) => v - a[j]), tl = Math.hypot(...T), Tn = T.map(v => v / tl);
    const s = i % 2 ? 1 : -1, w = o.w0 + (o.w1 - o.w0) * i / n;
    const side = [Tn[2], 0, -Tn[0]].map(v => v / (Math.hypot(Tn[2], Tn[0]) || 1));
    const c = a.map((v, j) => v + T[j] * 0.5 + side[j] * s * w * 0.35);
    const u = Tn.map((v, j) => v * 0.75 - side[j] * s * 0.66);
    out.push(ell({ c, r: [w * 1.25, w * 0.62, w * 0.5], u, v: [0, 0, 1], k: o.k ?? 0.009 }));
  }
  return out;
}
// a curly clump: a big lock whose surface is twisted into spiral ridges
const curls = (root, path, o) => L(root, path, { ...o, curly: { amp: o.amp ?? 0.22, f: o.f ?? 7, turn: o.turn ?? 3 }, lens: 0.1 });

export const STYLES = {};

// ==== gwen: a blonde bob, a deep side part, a long swept fringe over one eye, the other side short
STYLES.gwen = { skin: 0xf1cdb4, parts: [{ color: 0xead08f, k: 0.007, items: [
  scalpMass({ thick: 0.007, puff: 0.012, back: 0.006, k: 0.007 }),
  fall({ n: 8, from: 84, to: 276, rootAz: 180, fan: 0.75, rootPh: 74, midY: 0.0, midR: 0.104, lowR: 0.1, endY: a => -0.066 - 0.01 * Math.cos(a * D), endR: 0.095, tipOut: 0.01, jit: 1.0, layer: 0.003, w: [0.032, 0.036, 0.034], flat: 0.42, tip: 0.18, sharp: 0.6 }),
  L([-30, 72], [[2, 52, 0.016], [32, 28, 0.014], [56, -0.022, 0.104], [64, -0.064, 0.098]], { w: [0.022, 0.034, 0.034, 0.026, 0.018], flat: 0.45, tip: 0.35, sharp: 0.9 }),
  L([-20, 74], [[0, 60, 0.02], [20, 38, 0.018], [38, 0.004, 0.104], [46, -0.03, 0.1]], { w: [0.018, 0.026, 0.026, 0.018], flat: 0.5, tip: 0.4, sharp: 0.9 }),
  L([-40, 68], [[-46, 42, 0.014], [-56, 0.004, 0.104], [-60, -0.04, 0.1], [-58, -0.064, 0.096]], { w: [0.02, 0.028, 0.028, 0.02], flat: 0.5, tip: 0.35, sharp: 1 }),
] }] };

// ==== gogo: a dark short bob, choppy, the fringe in a few big pieces, a purple streak
STYLES.gogo = { skin: 0xf0c7a8, parts: [{ color: 0x241d28, k: 0.007, items: [
  scalpMass({ thick: 0.007, puff: 0.012, back: 0.006, k: 0.007 }),
  fall({ n: 8, from: 80, to: 280, rootAz: 180, fan: 0.75, rootPh: 74, midY: 0.0, midR: 0.104, lowR: 0.102, endY: a => -0.048 - 0.01 * Math.cos(a * D), endR: 0.1, tipOut: 0.016, jit: 1.6, layer: 0.003, w: [0.032, 0.036, 0.034], flat: 0.42, tip: 0.2, sharp: 0.7 }),
  ...fringe({ clumps: [[-46, 0.0, 0.03, -8], [-20, 0.016, 0.034, 4], [8, 0.006, 0.034, 6], [36, 0.02, 0.03, 10]] }),
  L([40, 74], [[54, 50, 0.016], [66, 0.03, 0.104], [72, -0.03, 0.104]], { w: [0.012, 0.018, 0.018, 0.012], flat: 0.45, tip: 0.4, color: 0x8a3fc0 }),
] }] };

// ==== jack: messy white, short, flopping forward and to the side in soft tufts
STYLES.jack = { skin: 0xf2d6c4, head: { male: 1 }, parts: [{ color: 0xe8e5de, k: 0.009, items: [
  scalpMass({ thick: 0.012, puff: 0.02, back: 0.006, ear: 0.02, behind: -0.03, nape: -0.06, k: 0.009 }),
  // tufts pushed up off the forehead and out to the sides, tips pointing up, forward and out — tousled, not a crown
  ...[[-62, 0.05, 0.026, -14, 0.0], [-40, 0.1, 0.03, -10, 0.01], [-16, 0.12, 0.032, -2, 0.02], [8, 0.125, 0.032, 6, 0.018], [32, 0.11, 0.03, 14, 0.01], [54, 0.08, 0.028, 18, 0.0], [72, 0.03, 0.024, 20, -0.01]].map(([a, y, w, t, f], i) =>
    L([a * 0.6, 64], [[a * 0.8, 70, 0.026], [a + t * 0.4, y, 0.08 + f], [a + t, y + 0.012 - (i % 2) * 0.02, 0.112 + f]], { w: [w, w * 1.25, w * 1.2, w * 0.8], flat: 0.6, tip: 0.5, sharp: 1.0, lens: 0.3 })),
  // a few strands falling onto the forehead
  L([-6, 60], [[-8, 40, 0.02], [-14, 0.045, 0.104], [-22, 0.018, 0.102]], { w: [0.014, 0.02, 0.018, 0.012], flat: 0.5, tip: 0.5 }),
  L([10, 60], [[12, 40, 0.02], [18, 0.045, 0.104], [24, 0.024, 0.104]], { w: [0.012, 0.018, 0.016, 0.01], flat: 0.5, tip: 0.5 }),
  fall({ n: 8, from: 100, to: 260, rootAz: 180, fan: 0.6, rootPh: 74, midY: 0.03, midR: 0.108, endY: a => -0.03 - 0.03 * Math.abs(Math.cos(a * D)), endR: 0.094, tipOut: 0.0, jit: 2.2, layer: 0.005, w: [0.032, 0.036, 0.032], flat: 0.45, tip: 0.25, sharp: 0.7 }),
] }] };

// ==== marco: a brown boy's cut, a big rounded fringe swept to one side
STYLES.marco = { skin: 0xf0c8a6, head: { male: 1 }, parts: [{ color: 0x3e2618, k: 0.008, items: [
  scalpMass({ thick: 0.01, puff: 0.016, back: 0.008, ear: 0.02, behind: -0.035, nape: -0.06, k: 0.008 }),
  ...fringe({ part: -30, clumps: [[-36, 0.03, 0.034, 16], [-8, 0.032, 0.036, 22], [20, 0.036, 0.034, 26], [46, 0.03, 0.03, 26]], tip: 0.35, lift: 0.02 }),
  fall({ n: 8, from: 92, to: 268, rootAz: 180, fan: 0.6, rootPh: 74, midY: 0.025, midR: 0.106, endY: a => -0.035 - 0.02 * Math.abs(Math.cos(a * D)), endR: 0.092, jit: 1, layer: 0.003, w: [0.032, 0.036, 0.032], flat: 0.45, tip: 0.22, sharp: 0.65 }),
] }] };

// ==== ginger: a big swept quiff rising from the forehead, over and back to one side
STYLES.ginger = { skin: 0xf3c9a5, head: { male: 1 }, parts: [{ color: 0xc8632b, k: 0.014, items: [
  scalpMass({ thick: 0.01, puff: 0.014, back: 0.006, ear: 0.02, behind: -0.035, nape: -0.06, k: 0.014 }),
  // the quiff's body: a big volume over the forehead, leaning to his left
  ell({ c: [0.012, 0.115, 0.03], r: [0.075, 0.042, 0.06], u: [0.97, 0.24, 0], v: [-0.24, 0.97, 0] }),
  // its locks: rising off the forehead, sweeping over and back to the side, the front one curling down
  ...[[-30, 0.0, 0.036], [-8, 0.012, 0.04], [14, 0.012, 0.038], [34, 0.0, 0.032]].map(([a, dy, w]) =>
    L([a, 44], [[a + 4, 58, 0.03], [a + 16, 0.15 + dy, 0.074], [a + 46, 0.15 + dy, 0.1], [a + 74, 0.11 + dy * 0.5, 0.112], [a + 88, 0.07, 0.11]], { w: [w * 0.7, w, w * 1.1, w, w * 0.8, w * 0.5], flat: 0.45, tip: 0.35, sharp: 0.9, lens: 0.4 })),
  L([-40, 50], [[-34, 0.12, 0.06], [-20, 0.13, 0.1], [-12, 0.09, 0.115], [-22, 0.05, 0.112]], { w: [0.02, 0.03, 0.03, 0.022, 0.012], flat: 0.5, tip: 0.4 }),
  fall({ n: 8, from: 96, to: 264, rootAz: 180, fan: 0.6, rootPh: 70, midY: 0.025, midR: 0.106, endY: -0.045, endR: 0.092, jit: 1, layer: 0.003, w: [0.032, 0.036, 0.032], flat: 0.45, tip: 0.22, sharp: 0.65 }),
] }] };

// ==== ariel: long flowing red, high volume at the crown, a big swoop on one side, waves to the waist
STYLES.ariel = { skin: 0xf6dccd, dist: 1.9, ty: -0.13, parts: [{ color: 0xd2321e, k: 0.012, items: [
  scalpMass({ thick: 0.014, puff: 0.032, back: 0.012, lift: 0.008, k: 0.012 }),
  // the swoop: a big lock lifting from a side part, over the forehead, down past the face in a long S
  L([-26, 74], [[4, 64, 0.04], [34, 38, 0.034], [58, -0.01, 0.12], [66, -0.1, 0.12], [56, -0.2, 0.15], [46, -0.3, 0.16], [56, -0.4, 0.15]], { w: [0.03, 0.048, 0.052, 0.05, 0.046, 0.04, 0.032, 0.016], flat: 0.42, tip: 0.25, sharp: 0.8 }),
  L([-30, 74], [[-44, 52, 0.03], [-58, 0.02, 0.118], [-64, -0.09, 0.12], [-52, -0.2, 0.15], [-42, -0.3, 0.16], [-52, -0.38, 0.15]], { w: [0.028, 0.042, 0.046, 0.042, 0.038, 0.03, 0.014], flat: 0.42, tip: 0.25, sharp: 0.8 }),
  fall({ n: 7, from: 104, to: 256, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.12, lowR: 0.15, endY: a => -0.42 - 0.03 * Math.sin(a * 3 * D), endR: 0.14, flare: 0.02, jit: 2, layer: 0.006, w: [0.04, 0.05, 0.046, 0.026], flat: 0.4, tip: 0.3, sharp: 0.8, wave: { amp: 0.012, f: 1.1, step: 0.35 } }),
] }] };

// ==== doll: violet, voluminous, a big swooping fringe over one brow, locks to the shoulders flicking out
STYLES.doll = { skin: 0xf2c9a8, dist: 1.5, ty: -0.08, parts: [{ color: 0x6b2fd6, k: 0.01, items: [
  scalpMass({ thick: 0.012, puff: 0.03, back: 0.01, lift: 0.006, k: 0.01 }),
  L([-4, 84], [[18, 66, 0.03], [42, 38, 0.024], [62, 0.004, 0.118], [72, -0.05, 0.116]], { w: [0.03, 0.044, 0.046, 0.036, 0.024], flat: 0.45, tip: 0.3, sharp: 0.8 }),
  L([-8, 84], [[-28, 62, 0.026], [-52, 32, 0.02], [-64, -0.01, 0.114], [-70, -0.09, 0.118], [-58, -0.17, 0.16]], { w: [0.028, 0.04, 0.042, 0.038, 0.026], flat: 0.45, tip: 0.3, sharp: 0.8 }),
  L([14, 80], [[44, 44, 0.02], [68, -0.04, 0.114], [76, -0.12, 0.13], [64, -0.18, 0.17]], { w: [0.026, 0.036, 0.036, 0.026], flat: 0.45, tip: 0.3, sharp: 0.8 }),
  fall({ n: 7, from: 112, to: 248, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.118, lowR: 0.124, endY: -0.18, endR: 0.136, tipOut: 0.03, jit: 1.5, layer: 0.005, w: [0.034, 0.044, 0.036], flat: 0.42, tip: 0.3, sharp: 0.8 }),
] }] };

// ==== kbuns: dark blue, sleek, a short fringe, two buns low at the back
STYLES.kbuns = { skin: 0xf3cdb8, parts: [{ color: 0x1e2350, k: 0.008, items: [
  scalpMass({ thick: 0.006, puff: 0.008, back: 0.004, k: 0.008 }),
  ...fringe({ clumps: [[-34, 0.03, 0.028, -6], [-10, 0.034, 0.03, 0], [14, 0.03, 0.03, 4], [36, 0.034, 0.026, 8]], r: 0.098, lift: 0.008 }),
  ...[-1, 1].map(s => ell({ c: [s * 0.05, -0.012, -0.092], r: [0.03, 0.03, 0.022], k: 0.012 })),
  ...[-1, 1].map(s => torus({ c: [s * 0.05, -0.012, -0.098], a: [s * 0.3, 0.1, -1], R: 0.02, r: 0.011, flat: 0.8, k: 0.004 })),
] }] };

// ==== kbraid: hair swept back sleek from the forehead into one long braid
STYLES.kbraid = { skin: 0xf3cdb8, dist: 1.8, ty: -0.12, parts: [{ color: 0x6b50ba, k: 0.006, items: [
  scalpMass({ thick: 0.008, puff: 0.014, back: 0.01, front: 0.07, nape: -0.07, k: 0.006 }),
  // the braid starts at the crown and lies down the back of the head, then hangs
  ...braid([[0, 0.1, -0.06], [0, 0.04, -0.105], [0, -0.05, -0.118], [0, -0.16, -0.12], [0, -0.28, -0.115], [0, -0.38, -0.11]], { n: 16, w0: 0.042, w1: 0.03, k: 0.004 }),
  ...[-60, -30, 0, 30, 60].map(a => L([a, 40], [[a * 0.7, 70, 0.01], [a * 0.3, 0.12, -0.05]], { w: [0.03, 0.034, 0.02], flat: 0.3, point: false, lens: 0.8 })),
  lock({ pts: [[0, -0.38, -0.11], [0, -0.42, -0.11], [0, -0.47, -0.11]], w: [0.02, 0.026, 0.018], flat: 0.7, tip: 0.6, up: [0, 0, -1] }),
] }] };

// ==== kpony: a long high ponytail, a side lock framing the face
STYLES.kpony = { skin: 0xf3cdb8, dist: 1.8, ty: -0.1, parts: [{ color: 0xb8304e, k: 0.009, items: [
  scalpMass({ thick: 0.008, puff: 0.01, back: 0.006, nape: -0.07, k: 0.009 }),
  L([-28, 72], [[-34, 44, 0.014], [-52, 0.02, 0.106], [-56, -0.07, 0.104], [-52, -0.12, 0.104]], { w: [0.018, 0.026, 0.026, 0.02, 0.012], flat: 0.45, tip: 0.35 }),
  torus({ c: [0, 0.098, -0.07], a: [0, 0.55, -0.83], R: 0.017, r: 0.008, color: 0xe2c060, k: 0.003 }),
  // the tail: wide and flat seen from behind, out of the band, arcing over and falling long
  lock({ pts: [[0, 0.098, -0.074], [0, 0.118, -0.11], [0, 0.085, -0.15], [0, -0.03, -0.17], [0, -0.18, -0.165], [0, -0.32, -0.15], [0, -0.44, -0.14]], w: [0.022, 0.04, 0.048, 0.05, 0.044, 0.034, 0.016], flat: 0.7, tip: 0.3, sharp: 0.8, up: [0, 0, 1], lens: 0.3, wave: { amp: 0.01, f: 1 } }),
] }] };

// ==== giulia: big red curly clumps, a beanie pushed back on her head
STYLES.giulia = { skin: 0xe9a782, dist: 1.4, parts: [{ color: 0xa8231b, k: 0.006, items: [
  scalpMass({ thick: 0.012, puff: 0.004, back: 0.014, k: 0.008 }),
  // ringlets: narrow locks twisted into a spiral ridge, falling in two layers around the head
  ...[...Array(13)].map((_, i) => { const a = 58 + i * 244 / 12, y = -0.06 - 0.035 * Math.abs(Math.cos(a * D / 1.2)) - (i % 3) * 0.008;
    return curls([a, 20], [[a, 0.02, 0.122], [a + (i % 2 ? 5 : -5), y * 0.55, 0.13], [a + (i % 2 ? -3 : 3), y, 0.126]], { w: [0.016, 0.022, 0.022, 0.02, 0.012], flat: 0.95, tip: 0.22, sharp: 0.6, f: 7, turn: 1, amp: 0.22, k: 0.004 }); }),
  ...[...Array(10)].map((_, i) => { const a = 70 + i * 220 / 9 + 11, y = -0.03 - 0.02 * Math.abs(Math.cos(a * D / 1.2));
    return curls([a, 30], [[a, 0.035, 0.112], [a + 4, y * 0.5, 0.116], [a, y, 0.114]], { w: [0.014, 0.02, 0.02, 0.014], flat: 0.95, tip: 0.25, sharp: 0.6, f: 5.5, turn: 1, amp: 0.22, k: 0.004 }); }),
  curls([-6, 58], [[-14, 40, 0.03], [-26, 0.07, 0.11], [-40, 0.055, 0.12]], { w: [0.02, 0.028, 0.03, 0.02], flat: 0.95, tip: 0.3, f: 5, turn: 1, amp: 0.22 }),
  curls([-20, 50], [[-30, 30, 0.03], [-44, 0.04, 0.118], [-52, 0.0, 0.12]], { w: [0.018, 0.026, 0.026, 0.018], flat: 0.95, tip: 0.3, f: 5, turn: 1, amp: 0.22 }),
] }, { color: 0x1d8ec4, k: 0.012, rough: 0.85, fabric: true, items: [
  ell({ c: [0.022, 0.056, -0.016], r: [0.102, 0.088, 0.104], u: [0.95, -0.31, 0], v: [0.31, 0.95, 0] }),
  torus({ c: [0.02, 0.04, -0.012], a: [-0.3, 0.95, 0.1], R: 0.1, r: 0.014, flat: 0.8 }),
], cuts: [{ sdf: (x, y, z) => (y - 0.04) + 0.3 * x - 0.1 * z, k: 0.004 }] }] };

// ==== alva: long, centre-parted, a heavy curtain framing the face, flicking out at the ends
STYLES.alva = { skin: 0xf0c8b0, dist: 1.8, ty: -0.12, parts: [{ color: 0x8a6a2a, k: 0.01, items: [
  scalpMass({ thick: 0.008, puff: 0.016, back: 0.008, front: 0.074, k: 0.01 }),
  ...[-1, 1].map(s => L([0, 86], [[s * 30, 62, 0.016], [s * 58, 28, 0.016], [s * 72, -0.06, 0.116], [s * 76, -0.2, 0.148], [s * 70, -0.3, 0.17], [s * 76, -0.34, 0.19]], { w: [0.03, 0.046, 0.052, 0.054, 0.05, 0.04, 0.02], flat: 0.36, tip: 0.2, sharp: 0.7 })),
  fall({ n: 7, from: 98, to: 262, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.114, lowR: 0.134, endY: -0.32, endR: 0.156, flare: 0.02, tipOut: 0.02, jit: 1.5, layer: 0.004, w: [0.036, 0.048, 0.044, 0.026], flat: 0.38, tip: 0.25, sharp: 0.7 }),
] }] };

// ==== nimona: pink-red, short tufts flopping over to one side, the other side shaved
STYLES.nimona = { skin: 0xe9a98a, parts: [{ color: 0xe0543e, k: 0.008, items: [
  scalpMass({ thick: 0.01, puff: 0.02, back: 0.006, ear: 0.02, behind: -0.03, nape: -0.06, shave: { side: -1, y: 0.075 }, k: 0.008 }),
  ...[[-34, 0.1, 0.03], [-12, 0.112, 0.032], [10, 0.11, 0.032], [32, 0.1, 0.03], [52, 0.08, 0.026]].map(([a, y, w], i) =>
    L([a - 16, 82], [[a - 4, 68, 0.028], [a + 14, y, 0.104], [a + 32, y - 0.04, 0.114], [a + 44, y - 0.07 - (i % 2) * 0.012, 0.114]], { w: [w * 0.7, w, w, w * 0.8, w * 0.5], flat: 0.5, tip: 0.42, sharp: 1.0 })),
  L([34, 62], [[50, 38, 0.014], [64, 0.0, 0.108], [68, -0.08, 0.104], [64, -0.13, 0.104]], { w: [0.016, 0.024, 0.024, 0.018], flat: 0.5, tip: 0.35 }),
  fall({ n: 6, from: 104, to: 236, rootAz: 180, fan: 0.6, rootPh: 70, midY: 0.025, midR: 0.106, endY: -0.04, endR: 0.094, tipOut: 0.004, jit: 2, layer: 0.004, w: [0.032, 0.036, 0.032], flat: 0.45, tip: 0.25, sharp: 0.7 }),
] }] };

// ==== anime: blunt bangs in a few pointed clumps, long straight, side locks framing the face
STYLES.anime = { skin: 0xf6e0d6, dist: 1.8, ty: -0.12, parts: [{ color: 0xa8c4d4, k: 0.008, items: [
  scalpMass({ thick: 0.008, puff: 0.014, back: 0.006, front: 0.074, k: 0.008 }),
  ...fringe({ clumps: [[-44, -0.002, 0.032, -4], [-22, -0.014, 0.034, -2], [0, -0.006, 0.034, 0], [22, -0.018, 0.034, 2], [44, -0.004, 0.03, 4]], tip: 0.3, sharp: 1.0, flat: 0.38 }),
  ...[-1, 1].map(s => L([s * 44, 62], [[s * 64, 30, 0.014], [s * 76, -0.04, 0.108], [s * 78, -0.16, 0.124], [s * 72, -0.3, 0.14]], { w: [0.02, 0.028, 0.028, 0.024, 0.014], flat: 0.42, tip: 0.3, sharp: 0.9 })),
  fall({ n: 8, from: 98, to: 262, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.112, lowR: 0.124, endY: -0.38, endR: 0.134, jit: 1.5, layer: 0.004, w: [0.034, 0.044, 0.04, 0.022], flat: 0.38, tip: 0.3, sharp: 0.9 }),
] }] };
