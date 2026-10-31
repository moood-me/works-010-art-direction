import { lock, ell, torus, scalpMass, scalp, CRANIUM } from './hair.js';
const D = Math.PI / 180;
const add = (a, b, f = 1) => a.map((v, i) => v + b[i] * f);
// a point beside the head at azimuth th, height y, distance r from the head's vertical axis
// a lock by azimuths/heights/radii lists: [az, y, r] beside the head, the first point on the scalp at [az, elev]
const L = (root, path, o = {}) => lock({ pts: [scalp(root[0] * D, root[1] * D, -0.006), ...path.map(q => q.length === 2 ? scalp(q[0] * D, q[1] * D, o.lift ?? 0.012) : ring(...q))], ...o });
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
    out.push(lock({ pts, w: o.w, flat: o.flat ?? 0.6, tip: o.tip ?? 0.3, sharp: o.sharp, color: o.color, vert: o.vert, twist: o.twist, k: o.k }));
  }
  return out;
}

export const STYLES = {};

// ==== gwen
STYLES.gwen = {
  skin: 0xf1cdb4,
  parts: [{ color: 0xead08f, k: 0.006, items: [
    scalpMass({ thick: 0.004, puff: 0.012, back: 0.004, front: 0.07, temple: 0.04, ear: 0.02, nape: -0.01, k: 0.006 }),
    // the bob: a few big locks from the crown to the jaw, close at the sides, alternating out and in
    fall({ n: 10, from: 76, to: 284, rootAz: 180, fan: 0.75, rootPh: 74, midY: 0.0, midR: 0.1, lowR: 0.098, endY: a => -0.066 - 0.01 * Math.cos(a * D), endR: 0.094, tipOut: 0.008, jit: 1.1, layer: 0.003, w: [0.028, 0.032, 0.03], flat: 0.42, tip: 0.3, sharp: 1.0 }),
    // the side-swept fringe: from a part on her right, over the forehead, down past the left eye
    lock({ pts: [scalp(-28 * D, 70 * D, -0.006), scalp(2 * D, 52 * D, 0.014), scalp(32 * D, 28 * D, 0.012), ring(56, -0.022, 0.1), ring(64, -0.06, 0.095)], w: [0.02, 0.032, 0.032, 0.022, 0.016], flat: 0.5, tip: 0.35, sharp: 0.9 }),
    lock({ pts: [scalp(-18 * D, 74 * D, -0.006), scalp(0, 60 * D, 0.018), scalp(20 * D, 38 * D, 0.016), ring(38, 0.004, 0.102), ring(46, -0.026, 0.097)], w: [0.016, 0.024, 0.024, 0.016], flat: 0.55, tip: 0.4, sharp: 0.9 }),
    lock({ pts: [scalp(-8 * D, 66 * D, -0.006), scalp(12 * D, 48 * D, 0.012), scalp(26 * D, 20 * D, 0.01), ring(42, -0.036, 0.096), ring(54, -0.078, 0.09)], w: [0.012, 0.018, 0.018, 0.012], flat: 0.55, tip: 0.45, sharp: 0.9 }),
    // her right side: short, a lock in front of the ear
    lock({ pts: [scalp(-38 * D, 68 * D, -0.006), scalp(-46 * D, 42 * D, 0.012), ring(-54, 0.004, 0.102), ring(-58, -0.04, 0.097), ring(-56, -0.066, 0.093)], w: [0.018, 0.026, 0.026, 0.018], flat: 0.6, tip: 0.38, sharp: 1 }),
  ] }],
};

// a braid: alternating lens-shaped clumps along a curve, each tilted the other way
function braid(pts, o) {
  const out = [], n = o.n || 12;
  const P = [];
  for (let i = 0; i <= n; i++) { const u = i / n * (pts.length - 1), k = Math.min(Math.floor(u), pts.length - 2), t = u - k; P.push(pts[k].map((v, j) => v + (pts[k + 1][j] - v) * t)); }
  for (let i = 0; i < n; i++) {
    const a = P[i], b = P[i + 1], T = b.map((v, j) => v - a[j]), tl = Math.hypot(...T), Tn = T.map(v => v / tl);
    const s = i % 2 ? 1 : -1, side = [Tn[2] * s, 0, -Tn[0] * s], sl = Math.hypot(...side) || 1;
    const w = (o.w0 + (o.w1 - o.w0) * i / n);
    const c = a.map((v, j) => v + T[j] * 0.5 + side[j] / sl * w * 0.25);
    const u = Tn.map((v, j) => v * 0.8 + side[j] / sl * 0.6 * s);
    out.push(ell({ c, r: [tl * 0.85, w, w * 0.7], u, v: [0, 0, 1], color: o.color, k: o.k ?? 0.006 }));
  }
  return out;
}
// a corkscrew curl: a lock along a helix around a falling axis
function curl(top, bottom, o) {
  const pts = [], turns = o.turns || 2, n = Math.round(turns * 8);
  for (let i = 0; i <= n; i++) {
    const t = i / n, a = (o.phase || 0) + t * turns * 2 * Math.PI, r = (o.R || 0.01) * (1 - 0.3 * t);
    const c = top.map((v, j) => v + (bottom[j] - v) * t);
    pts.push([c[0] + Math.cos(a) * r, c[1], c[2] + Math.sin(a) * r]);
  }
  return lock({ pts, w: o.w || 0.009, flat: 0.75, tip: 0.2, sharp: 0.8, n: n * 3, up: [0, 1, 0], lens: 0.2, color: o.color, k: o.k });
}

// ==== gogo: a dark short bob, choppy, a purple streak
STYLES.gogo = {
  skin: 0xf0c7a8,
  parts: [{ color: 0x221c26, k: 0.006, items: [
    scalpMass({ thick: 0.004, puff: 0.01, back: 0.006, front: 0.07, temple: 0.04, ear: 0.02, nape: -0.01, k: 0.006 }),
    fall({ n: 10, from: 74, to: 286, rootAz: 180, fan: 0.75, rootPh: 74, midY: 0.0, midR: 0.102, lowR: 0.1, endY: a => -0.05 - 0.006 * Math.cos(a * D), endR: 0.097, tipOut: 0.014, jit: 1.5, layer: 0.003, w: [0.028, 0.032, 0.03], flat: 0.42, tip: 0.32, sharp: 1.0 }),
    // a full fringe, choppy, cut above the brows
    ...[-40, -18, 4, 26, 46].map((a, i) => L([a * 0.4, 80], [[a * 0.6, 58], [a, 28], [a * 1.05, 0.02 - (i % 2) * 0.006, 0.098]], { w: [0.018, 0.026, 0.024], flat: 0.42, tip: 0.45, sharp: 0.9 })),
    L([30, 80], [[48, 56], [62, 26], [70, 0.0, 0.1], [74, -0.04, 0.098]], { w: [0.012, 0.016, 0.016, 0.012], flat: 0.45, tip: 0.4, color: 0x7a3aa8 }),
  ] }],
};

// ==== jack: messy white, swept up and to the side, soft tufts, not a crown
STYLES.jack = {
  skin: 0xf2d6c4, head: { male: 1 },
  parts: [{ color: 0xe6e4df, k: 0.007, items: [
    scalpMass({ thick: 0.008, puff: 0.012, back: 0.004, front: 0.068, temple: 0.035, ear: 0.0, nape: -0.04, k: 0.007 }),
    // tufts from the crown out over the forehead and the sides, each lifting then falling, tips in different directions
    ...[[-50, 0.06, 0.112], [-25, 0.075, 0.118], [0, 0.08, 0.12], [24, 0.074, 0.118], [48, 0.06, 0.112], [70, 0.04, 0.11], [-72, 0.04, 0.11]].map(([a, y, r], i) =>
      L([a * 0.3 + 180 * 0, 82], [[a * 0.7, 66], [a, y, r], [a * 1.15 + (i % 2 ? 8 : -8), y - 0.03 - (i % 3) * 0.008, r - 0.006]], { w: [0.02, 0.03, 0.028, 0.02], flat: 0.5, tip: 0.45, sharp: 1.0, lift: 0.02 })),
    fall({ n: 8, from: 95, to: 265, rootAz: 180, fan: 0.6, rootPh: 70, midY: 0.02, midR: 0.104, endY: -0.03, endR: 0.096, tipOut: 0.016, jit: 2, layer: 0.004, w: [0.026, 0.03, 0.026], flat: 0.45, tip: 0.4, sharp: 1.0 }),
  ] }],
};

// ==== marco: a brown boy's cut, a big fringe swept to one side
STYLES.marco = {
  skin: 0xf0c8a6, head: { male: 1 },
  parts: [{ color: 0x3b2418, k: 0.007, items: [
    scalpMass({ thick: 0.008, puff: 0.014, back: 0.006, front: 0.07, temple: 0.03, ear: 0.0, nape: -0.04, k: 0.007 }),
    ...[-40, -16, 8, 30, 52].map((a, i) => L([a * 0.3 - 20, 82], [[a * 0.7 - 6, 62], [a + 6, 34], [a + 14, 0.035 - i * 0.003, 0.104]], { w: [0.02, 0.03, 0.028, 0.02], flat: 0.45, tip: 0.4, sharp: 1.0, lift: 0.02 })),
    fall({ n: 8, from: 90, to: 270, rootAz: 180, fan: 0.6, rootPh: 70, midY: 0.02, midR: 0.104, endY: -0.035, endR: 0.096, jit: 1, layer: 0.003, w: [0.026, 0.03, 0.026], flat: 0.45, tip: 0.35, sharp: 1.0 }),
  ] }],
};

// ==== ariel: long flowing red, a big swoop on one side, to the waist
STYLES.ariel = {
  skin: 0xf6dccd, dist: 1.9, ty: -0.13,
  parts: [{ color: 0xd2321e, k: 0.008, items: [
    scalpMass({ thick: 0.008, puff: 0.02, back: 0.006, front: 0.07, temple: 0.04, ear: 0.01, nape: -0.04, lift: 0.004, k: 0.008 }),
    // the swoop: from a side part over the forehead, a big curve down past the face
    L([-20, 72], [[10, 58], [38, 30], [60, -0.02, 0.11], [62, -0.12, 0.11], [52, -0.26, 0.15], [40, -0.36, 0.13]], { w: [0.03, 0.04, 0.042, 0.04, 0.036, 0.03, 0.02], flat: 0.45, tip: 0.25, sharp: 0.8, lift: 0.02 }),
    L([-30, 72], [[-40, 50], [-54, 0.02, 0.106], [-60, -0.1, 0.108], [-48, -0.24, 0.15], [-40, -0.34, 0.13]], { w: [0.026, 0.036, 0.038, 0.034, 0.028, 0.02], flat: 0.45, tip: 0.25, sharp: 0.8 }),
    // the long fall at the back, waving
    fall({ n: 9, from: 100, to: 260, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.11, lowR: 0.13, endY: a => -0.4 - 0.03 * Math.sin(a * 3 * D), endR: 0.12, flare: 0.02, jit: 2, layer: 0.005, w: [0.03, 0.038, 0.036, 0.02], flat: 0.4, tip: 0.3, sharp: 0.8 }),
  ] }],
};

// ==== ginger: a big swept quiff, up and to the side
STYLES.ginger = {
  skin: 0xf3c9a5, head: { male: 1 },
  parts: [{ color: 0xc8622a, k: 0.008, items: [
    scalpMass({ thick: 0.008, puff: 0.012, back: 0.004, front: 0.07, temple: 0.03, ear: 0.0, nape: -0.04, k: 0.008 }),
    // the quiff: big locks rising from the forehead, sweeping back and to his left, curling over
    ...[[-30, 0], [-10, 0.006], [10, 0.01], [30, 0.006]].map(([a, dy], i) =>
      L([a, 30], [[a + 6, 50, 0.03], [a + 20, 0.16 + dy, 0.07], [a + 50, 0.15 + dy, 0.1], [a + 75, 0.12, 0.11]], { w: [0.022, 0.03, 0.032, 0.028, 0.02], flat: 0.5, tip: 0.35, sharp: 0.9, lift: 0.03 })),
    L([-50, 40], [[-60, 55, 0.02], [-50, 0.12, 0.08], [-20, 0.15, 0.08]], { w: [0.02, 0.026, 0.024, 0.016], flat: 0.5, tip: 0.4 }),
    fall({ n: 8, from: 95, to: 265, rootAz: 180, fan: 0.6, rootPh: 66, midY: 0.02, midR: 0.104, endY: -0.04, endR: 0.096, jit: 1, layer: 0.003, w: [0.026, 0.03, 0.026], flat: 0.45, tip: 0.35, sharp: 1.0 }),
  ] }],
};

// ==== doll: violet, a big swooping fringe over one brow, locks to the shoulders flicking out
STYLES.doll = {
  skin: 0xf2c9a8, dist: 1.5, ty: -0.08,
  parts: [{ color: 0x6b2fd6, k: 0.008, items: [
    scalpMass({ thick: 0.01, puff: 0.022, back: 0.008, front: 0.07, temple: 0.04, ear: 0.01, nape: -0.04, lift: 0.004, k: 0.008 }),
    L([0, 82], [[20, 62, 0.02], [44, 34, 0.018], [62, 0.0, 0.112], [70, -0.05, 0.11]], { w: [0.03, 0.042, 0.042, 0.034, 0.024], flat: 0.45, tip: 0.3, sharp: 0.8 }),
    L([-6, 82], [[-26, 60, 0.02], [-50, 30, 0.016], [-62, -0.01, 0.11], [-70, -0.08, 0.11], [-60, -0.17, 0.15]], { w: [0.026, 0.036, 0.038, 0.034, 0.024], flat: 0.45, tip: 0.3, sharp: 0.8 }),
    L([10, 78], [[40, 40, 0.016], [66, -0.04, 0.11], [74, -0.12, 0.13], [62, -0.18, 0.17]], { w: [0.026, 0.034, 0.034, 0.026], flat: 0.45, tip: 0.3, sharp: 0.8 }),
    fall({ n: 7, from: 110, to: 250, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.112, lowR: 0.12, endY: -0.18, endR: 0.13, tipOut: 0.03, jit: 1.5, layer: 0.005, w: [0.03, 0.04, 0.034], flat: 0.42, tip: 0.3, sharp: 0.8 }),
  ] }],
};

// ==== kbuns: dark blue, flat fringe, two buns low at the back
STYLES.kbuns = {
  skin: 0xf3cdb8,
  parts: [{ color: 0x1d2246, k: 0.006, items: [
    scalpMass({ thick: 0.004, puff: 0.006, back: 0.0, front: 0.07, temple: 0.04, ear: 0.01, nape: -0.04, k: 0.006 }),
    ...[-36, -12, 12, 36].map(a => L([a * 0.4, 80], [[a * 0.7, 56], [a, 26], [a * 1.05, 0.04, 0.1]], { w: [0.02, 0.028, 0.026], flat: 0.4, tip: 0.4, sharp: 0.9 })),
    // hair pulled back sleek to the buns
    fall({ n: 8, from: 70, to: 290, rootAz: 0, fan: 0.2, rootPh: 70, midY: 0.03, midR: 0.1, endY: -0.0, endR: 0.06, w: [0.026, 0.03, 0.02], flat: 0.35, tip: 0.2, point: false, k: 0.01 }),
    ...[-1, 1].map(s => torus({ c: [s * 0.055, -0.005, -0.085], a: [s * 0.5, 0.2, -1], R: 0.02, r: 0.014, flat: 0.9 })),
    ...[-1, 1].map(s => ell({ c: [s * 0.058, -0.005, -0.092], r: [0.026, 0.026, 0.02] })),
  ] }],
};

// ==== kbraid: long braid from the crown, side-swept top
STYLES.kbraid = {
  skin: 0xf3cdb8, dist: 1.8, ty: -0.12,
  parts: [{ color: 0x6a4fb8, k: 0.007, items: [
    scalpMass({ thick: 0.006, puff: 0.012, back: 0.004, front: 0.072, temple: 0.045, ear: 0.02, nape: -0.02, k: 0.007 }),
    // hair swept back from the forehead into the braid
    fall({ n: 9, from: 60, to: 300, rootAz: 0, fan: 0.15, rootPh: 30, midY: 0.09, midR: 0.08, endY: 0.06, endR: 0.06, lift: 0.006, w: [0.026, 0.03, 0.02], flat: 0.35, tip: 0.25, point: false, k: 0.01 }),
    ...braid([[0, 0.09, -0.07], [0, 0.03, -0.11], [0, -0.07, -0.12], [0, -0.2, -0.11], [0, -0.34, -0.1]], { n: 14, w0: 0.03, w1: 0.02 }),
  ] }],
};

// ==== kpony: a high ponytail, long, red-pink, a side fringe
STYLES.kpony = {
  skin: 0xf3cdb8, dist: 1.8, ty: -0.1,
  parts: [{ color: 0xb8304e, k: 0.007, items: [
    scalpMass({ thick: 0.005, puff: 0.01, back: 0.0, front: 0.07, temple: 0.045, ear: 0.02, nape: -0.02, k: 0.007 }),
    fall({ n: 9, from: 60, to: 300, rootAz: 0, fan: 0.15, rootPh: 30, midY: 0.1, midR: 0.075, endY: 0.1, endR: 0.05, lift: 0.006, w: [0.026, 0.03, 0.02], flat: 0.35, tip: 0.25, point: false, k: 0.01 }),
    L([-24, 70], [[-30, 40], [-48, 0.02, 0.104], [-52, -0.06, 0.1]], { w: [0.02, 0.026, 0.024, 0.016], flat: 0.45, tip: 0.35 }),
    // the tail: rising from a band at the back of the crown, arcing back and falling long
    torus({ c: [0, 0.1, -0.06], a: [0, 0.6, -0.8], R: 0.016, r: 0.007, color: 0xe8c86a }),
    lock({ pts: [[0, 0.1, -0.065], [0, 0.13, -0.11], [0, 0.08, -0.17], [0, -0.06, -0.19], [0, -0.22, -0.17], [0, -0.38, -0.15]], w: [0.022, 0.038, 0.044, 0.04, 0.032, 0.02], flat: 0.6, tip: 0.3, sharp: 0.8, up: [1, 0, 0], lens: 0.3 }),
    lock({ pts: [[0.01, 0.1, -0.065], [0.03, 0.12, -0.12], [0.04, 0.05, -0.17], [0.05, -0.1, -0.18], [0.04, -0.28, -0.15]], w: [0.016, 0.026, 0.03, 0.026, 0.016], flat: 0.6, tip: 0.3, up: [1, 0, 0] }),
  ] }],
};

// ==== giulia: red curls in clumps of corkscrews, a beanie
STYLES.giulia = {
  skin: 0xe9a782, dist: 1.4,
  parts: [{ color: 0xa8231b, k: 0.004, h: 0.0024, items: [
    scalpMass({ thick: 0.006, puff: 0.004, back: 0.008, front: 0.066, temple: 0.03, ear: 0.0, nape: -0.04, k: 0.006 }),
    ...[...Array(16)].map((_, i) => { const a = 70 + i * 220 / 15, y0 = 0.03 + 0.02 * Math.cos(a * D); return curl(ring(a, y0, 0.11), ring(a + 6, -0.075 - (i % 3) * 0.012, 0.12), { R: 0.012, turns: 2.2, phase: i * 1.7, w: 0.011 }); }),
    // a curly tuft out from under the beanie on the forehead
    curl(ring(-20, 0.07, 0.1), ring(-40, 0.03, 0.12), { R: 0.012, turns: 1.6, w: 0.012 }),
    curl(ring(-35, 0.06, 0.1), ring(-50, 0.0, 0.118), { R: 0.011, turns: 1.6, phase: 1, w: 0.011 }),
  ] }, { color: 0x1d8ec4, k: 0.01, rough: 0.8, items: [
    // the beanie: a soft dome pushed back and to one side, a rolled brim
    ell({ c: [0.012, 0.055, -0.012], r: [0.1, 0.085, 0.102], u: [0.95, -0.3, 0], v: [0.3, 0.95, 0] }),
    torus({ c: [0.012, 0.035, -0.008], a: [-0.25, 1, 0.12], R: 0.099, r: 0.012, flat: 0.8 }),
  ], cuts: [{ sdf: (x, y, z) => -((y - 0.03) + 0.25 * x - 0.12 * z), k: 0.004 }] }],
};

// ==== alva: long, centre-parted, a heavy curtain framing the face, flicking out at the ends
STYLES.alva = {
  skin: 0xf0c8b0, dist: 1.8, ty: -0.12,
  parts: [{ color: 0x8a6a2a, k: 0.008, items: [
    scalpMass({ thick: 0.006, puff: 0.014, back: 0.006, front: 0.072, temple: 0.04, ear: 0.0, nape: -0.04, k: 0.008 }),
    ...[-1, 1].map(s => L([0, 84], [[s * 30, 60, 0.012], [s * 58, 26, 0.012], [s * 72, -0.06, 0.11], [s * 78, -0.2, 0.14], [s * 70, -0.32, 0.17]], { w: [0.03, 0.044, 0.05, 0.05, 0.044, 0.028], flat: 0.38, tip: 0.2, sharp: 0.7 })),
    fall({ n: 8, from: 95, to: 265, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.11, lowR: 0.13, endY: -0.34, endR: 0.15, flare: 0.02, tipOut: 0.02, jit: 1.5, layer: 0.004, w: [0.032, 0.044, 0.04, 0.026], flat: 0.38, tip: 0.25, sharp: 0.7 }),
  ] }],
};

// ==== nimona: pink-red tufts, a shaved side, short
STYLES.nimona = {
  skin: 0xe9a98a,
  parts: [{ color: 0xe0543e, k: 0.006, items: [
    scalpMass({ thick: 0.008, puff: 0.018, back: 0.004, front: 0.068, temple: 0.03, ear: 0.0, nape: -0.03, shave: { side: -1, y: 0.07 }, k: 0.006 }),
    // tufts flopping over to her left from the top, pointed tips
    ...[[-30, 0.1], [-10, 0.11], [12, 0.105], [32, 0.095], [-40, 0.06]].map(([a, y], i) => L([a - 20, 80], [[a - 6, 64, 0.02], [a + 12, y, 0.1], [a + 30, y - 0.035, 0.11], [a + 40, y - 0.06 - (i % 2) * 0.01, 0.112]], { w: [0.022, 0.032, 0.03, 0.022, 0.014], flat: 0.5, tip: 0.45, sharp: 1.1, lift: 0.024 })),
    // two long front locks on her left falling past the cheek
    L([30, 60], [[48, 36], [62, 0.0, 0.106], [66, -0.08, 0.1], [62, -0.13, 0.1]], { w: [0.016, 0.022, 0.022, 0.018], flat: 0.5, tip: 0.35 }),
    fall({ n: 6, from: 100, to: 230, rootAz: 180, fan: 0.6, rootPh: 66, midY: 0.02, midR: 0.104, endY: -0.03, endR: 0.096, tipOut: 0.014, jit: 2, layer: 0.004, w: [0.026, 0.03, 0.026], flat: 0.45, tip: 0.4, sharp: 1.0 }),
  ] }],
};

// ==== anime: blunt bangs split into pointed clumps, long straight, side locks framing the face
STYLES.anime = {
  skin: 0xf6e0d6, dist: 1.8, ty: -0.12,
  parts: [{ color: 0xa8c4d4, k: 0.006, items: [
    scalpMass({ thick: 0.006, puff: 0.012, back: 0.004, front: 0.072, temple: 0.045, ear: 0.0, nape: -0.04, k: 0.006 }),
    ...[-44, -26, -8, 10, 28, 46].map((a, i) => L([a * 0.3, 84], [[a * 0.6, 62], [a, 30], [a * 1.04, -0.005 - (i % 2) * 0.008, 0.1]], { w: [0.018, 0.026, 0.026, 0.02], flat: 0.38, tip: 0.5, sharp: 1.1 })),
    ...[-1, 1].map(s => L([s * 40, 60], [[s * 62, 30], [s * 74, -0.04, 0.104], [s * 76, -0.16, 0.12], [s * 70, -0.3, 0.14]], { w: [0.018, 0.026, 0.026, 0.022, 0.012], flat: 0.42, tip: 0.3, sharp: 0.9 })),
    fall({ n: 9, from: 95, to: 265, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.108, lowR: 0.12, endY: -0.38, endR: 0.13, jit: 1.5, layer: 0.004, w: [0.03, 0.04, 0.036, 0.02], flat: 0.38, tip: 0.3, sharp: 0.9 }),
  ] }],
};
