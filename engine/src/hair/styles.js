// В1's hairstyles (experiments/hair/styles.js, carried here as they were, after Pavel's references), as code: each a
// set of parts (surfaces), each part groups of items by name — `cap` (the scalp mass), `fringe`, `back`, `sides`,
// `under`, `tail`, `braid`, `buns`… — so a hair piece (src/hair/hair.js) can take a group away, keep only some, or
// colour one. The helpers build the items: `fall` (locks from the crown round the head, with a rhythm of big and small
// clumps, varied lengths and hooks), `fringe`, `under` (the under-layer of long hair), `sweep` (sleek hair combed to a
// band or bun), `tail`, `braid` (three locks crossing, one chain), `bun`, `ringlet` (a lock wound round its guide).
// All in the design space round the neutral head (src/hair/build.js). Their source is here now (experiments/hair keeps
// В1's own copy, as it was, for its page).
import { lock, clump, ell, torus, scalpMass, scalp, hairline, CRANIUM } from './build.js';
const hash = x => { const v = Math.sin(x * 12.9898) * 43758.5453; return v - Math.floor(v); };
// smaller locks breaking off a clump's end: one on alternate sides, a second on some, each its own length
const autoKids = (i, seed = 0, o = {}) => hash(i * 2.3 + seed + 0.5) < (o.kidP ?? 0.6) ? [] : [{ side: i % 2 ? 1 : -1, at: 0.45 + 0.15 * hash(i + seed), w: (o.kw ?? 0.34) + 0.12 * hash(i * 3.1 + seed), len: 0.9 + 0.3 * hash(i * 7.3 + seed), spread: 0.8 },
  ...(hash(i * 5.7 + seed) > 0.7 ? [{ side: i % 2 ? -1 : 1, at: 0.6, w: (o.kw ?? 0.34) * 0.75, len: 0.8 + 0.25 * hash(i * 9.1 + seed), spread: 0.6 }] : [])];
const D = Math.PI / 180;
const add = (a, b, f = 1) => a.map((v, i) => v + b[i] * f);
// a point beside the head at azimuth th, height y, distance r from the head's vertical axis
// a lock by azimuths/heights/radii lists: [az, y, r] beside the head, the first point on the scalp at [az, elev]
// path points: [az, elev] or [az, elev, lift] on the scalp (elevation in degrees, so always > 1), or [az, y, r] beside it
const onScalp = q => Math.abs(q[1]) > 1;
const L = (root, path, o = {}) => clump({ root: 0.15, pts: [scalp(root[0] * D, root[1] * D, -0.009), ...path.map(q => onScalp(q) ? scalp(q[0] * D, q[1] * D, q[2] ?? o.lift ?? 0.012) : ring(...q))], ...o });
// the hairline's elevation (degrees) at azimuth a, for a cap
const hlEl = cap => a => Math.asin(Math.max(-1, Math.min(1, (hairline(cap, CRANIUM.c[0] + Math.sin(a * D), 0, CRANIUM.c[2] + Math.cos(a * D)) - CRANIUM.c[1]) / CRANIUM.r[1]))) / D + 4;
const ring = (th, y, r) => [CRANIUM.c[0] + Math.sin(th * D) * r, y, CRANIUM.c[2] + Math.cos(th * D) * r];

// a fall of locks around the head: each from the scalp near the crown, over the skull, down to its end
function fall(o) {
  const out = [];
  for (let i = 0; i < o.n; i++) {
    const a = o.n === 1 ? o.from : o.from + (o.to - o.from) * i / (o.n - 1);
    const j = o.jit ? (hash(i + (o.seed || 0) * 1.7) * 2 - 1) * o.jit * 1.5 : 0;
    const lay = (o.layer || 0) * (i % 2 ? 1 : -1);             // alternate locks sit a little out and in: grooves
    const endY = (typeof o.endY === 'function' ? o.endY(a) : o.endY) + j * 0.01;
    const rootPh = typeof o.rootPh === 'function' ? o.rootPh(a) : o.rootPh;
    const sw = o.sweep || 0, ra = o.rootAz !== undefined ? o.rootAz + (a - o.rootAz) * (o.fan ?? 0.35) : a;
    let aa = a; while (aa - ra > 180) aa -= 360; while (aa - ra < -180) aa += 360;   // over the shorter way round
    const pts = [scalp(ra * D, rootPh * D, -0.012), scalp((ra + aa) / 2 * D, (rootPh * 0.55 + 12) * D, (o.lift ?? 0.01) + lay)];
    const midY = o.midY ?? 0.0;
    pts.push(ring(a + sw * 0.5, midY, (o.midR ?? 0.104) + lay));
    if (endY < midY - 0.03) pts.push(ring(a + sw * 0.8, (midY + endY) / 2, (o.lowR ?? o.midR ?? 0.104) + lay + (o.flare || 0) * 0.5));
    pts.push(ring(a + sw + (o.tipTurn || 0), endY, (o.endR ?? 0.1) + lay + (o.flare || 0) + (o.tipOut || 0)));
    const wr = 1 + (o.rhythm ?? 0.3) * (hash(i * 4.1 + (o.seed || 0)) * 2 - 1);   // big clumps and smaller ones between
    out.push(clump({ pts, root: 0.2, hook: (o.hook ?? 0.7) * (hash(i * 6.1 + (o.seed || 0)) * 2 - 1), kids: o.kids === false ? [] : autoKids(i, o.seed || 0, o), w: Array.isArray(o.w) ? o.w.map(v => v * wr) : o.w * wr, flat: (o.flat ?? 0.6) * 0.75, tip: o.tip ?? 0.3, sharp: o.sharp, color: o.color, vert: o.vert, twist: o.twist, k: o.k, wave: o.wave && { ...o.wave, ph: (o.wave.ph || 0) + i * (o.wave.step ?? 1.9) } }));
  }
  return out;
}


// a fringe: a few clumps from the front of the crown over the forehead; each tip its own length and turn,
// tips tucking in towards the face; widths overlap so they read as one sheet notched only at the tips
function fringe(o) {
  return o.clumps.map(([a, y, w, turn = 0]) => L([a * 0.35 + (o.part || 0), o.rootEl ?? 78], [[a * 0.7 + (o.part || 0) * 0.4, 56, o.lift ?? 0.014], [a + turn * 0.4, 0.045, o.r ?? 0.1], [a + turn, y, (o.r ?? 0.1) + (o.tipR ?? -0.002)]],
    { w: [w * 0.7, w, w, w * 0.9], flat: o.flat ?? 0.42, tip: o.tip ?? 0.6, sharp: o.sharp ?? 1.5, color: o.color, k: o.k }));
}
// a braid: three locks crossing over and under each other along the braid's line, thinning to the end
// (in motion the braid is one chain along its line, `rig`, the three strands and what hangs below following it)
function braid(pts, o) {
  const n = 60, G = [], rig = { guide: o.to ? [...pts, o.to] : pts, dyn: o.dyn };
  for (let i = 0; i <= n; i++) { const u = i / n * (pts.length - 1), k = Math.min(Math.floor(u), pts.length - 2), t = u - k; G.push(pts[k].map((v, j) => v + (pts[k + 1][j] - v) * t)); }
  const out = [0, 1, 2].map(k => {
    const P = G.map((g, i) => {
      const s = i / n, q = G[Math.min(i + 1, n)], r = G[Math.max(i - 1, 0)], T = q.map((v, j) => v - r[j]), tl = Math.hypot(...T);
      const side = [T[2], 0, -T[0]].map(v => v / (Math.hypot(T[2], T[0]) || 1));
      let out = [g[0] - CRANIUM.c[0], 0, g[2] - CRANIUM.c[2]]; const ol = Math.hypot(...out) || 1; out = out.map(v => v / ol);
      const A = (o.w0 + (o.w1 - o.w0) * s) * 0.55, t = s * o.cross * 6.283 + k * 6.283 / 3;
      return g.map((v, j) => v + side[j] * A * Math.sin(t) + out[j] * A * 0.55 * Math.sin(2 * t));
    }).filter((_, i) => i % 2 === 0);
    return lock({ pts: P, n: 90, w: [o.w0 * 0.42, o.w0 * 0.45, o.w1 * 0.42, o.w1 * 0.3], flat: 0.55, lens: 0.5, tip: 0.12, sharp: 1.3, sheet: 0.5, color: o.color, rig });
  });
  out.rig = rig;
  return out;
}
// a bun: locks wound around a centre, spiralling in to the top of the bun
function bun(c, ax, R, o = {}) {
  const a = ax.map(v => v / Math.hypot(...ax)), u0 = Math.abs(a[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0];
  const ud = u0.reduce((q, v, j) => q + v * a[j], 0), U0 = u0.map((v, j) => v - ud * a[j]), ul = Math.hypot(...U0), U = U0.map(v => v / ul);
  const V = [a[1] * U[2] - a[2] * U[1], a[2] * U[0] - a[0] * U[2], a[0] * U[1] - a[1] * U[0]];
  return [0, 1, 2].map(k => {
    const pts = [];
    for (let i = 0; i <= 14; i++) {
      const s = i / 14, th = k * 2.1 + s * 6.283 * 1.15, rr = R * (1.0 - 0.75 * s), h = R * (-0.5 + 1.1 * Math.sin(s * 1.6));
      pts.push(c.map((v, j) => v + (U[j] * Math.cos(th) + V[j] * Math.sin(th)) * rr + a[j] * h));
    }
    return lock({ pts, n: 60, about: c.map((v, j) => v - a[j] * R * 0.4), w: [R * 0.45, R * 0.55, R * 0.45, R * 0.3], flat: 0.55, lens: 0.5, tip: 0.35, sharp: 1.3, color: o.color, k: o.k, rig: 'head' });
  });
}
// hair combed from the hairline to one place (a band, a bun, the crown): sleek locks lying on the skull
function sweep(o) {
  const out = [], [taz, tel] = o.to;
  for (let i = 0; i < o.n; i++) {
    const a = o.from + (o.upto - o.from) * i / (o.n - 1), el0 = typeof o.el === 'function' ? o.el(a) : o.el;
    const pts = [];
    // along the great circle from the root to the gathering place, lying on the skull
    const dir = (az, el) => [Math.sin(az * D) * Math.cos(el * D), Math.sin(el * D), Math.cos(az * D) * Math.cos(el * D)];
    const d0 = dir(a, el0 - 2), d1 = dir(taz, tel);
    for (let k = 0; k <= 5; k++) {
      const f = k / 5, d = d0.map((v, j) => v * (1 - f) + d1[j] * f), dl = Math.hypot(...d);
      pts.push(scalp(Math.atan2(d[0], d[2]), Math.asin(d[1] / dl), k === 0 ? -0.003 : (o.lift ?? 0.007) * Math.min(1, f * 1.6)));
    }
    if (o.end) pts.push(o.end);
    const w = o.w * (1 + 0.25 * (hash(i * 3.3 + (o.seed || 0)) * 2 - 1));
    out.push(lock({ pts, w: [w * 0.75, w, w, w * 0.8], flat: o.flat ?? 0.22, lens: 0.5, root: 0.2, point: false, sheet: 1.2, color: o.color, k: o.k, rig: 'head' }));   // combed tight: moves with the head
  }
  return out;
}
// a tail out of a band: several locks from the same knot, each its own path and end
function tail(o) {
  const out = [];
  for (let i = 0; i < o.n; i++) {
    const f = (i + 0.5) / o.n * 2 - 1, h = hash(i * 7.7 + (o.seed || 0));
    const pts = o.path.map((p, k) => { const s = k / (o.path.length - 1); return [p[0] + f * o.spread * Math.sin(s * 2.4), p[1] + (k === o.path.length - 1 ? (h - 0.3) * o.lenJit : 0), p[2] + (h - 0.5) * 0.02 * s]; });
    out.push(clump({ pts, w: o.w.map(v => v * (0.75 + 0.5 * hash(i * 2.9))), flat: 0.5, up: o.up, lens: 0.5, tip: 0.45, sharp: 1.3, hook: (h - 0.5) * 1.2, wave: o.wave && { ...o.wave, ph: i * 1.3 }, kids: i % 2 ? [{ side: f > 0 ? 1 : -1, at: 0.55, w: 0.4, len: 0.85 + 0.3 * h }] : [], color: o.color, rig: o.rig, dyn: o.dyn }));
  }
  return out;
}
// the under-layer of long hair: locks from behind the ears hanging down the back, seen between the face-framing locks
const under = o => fall({ n: o.n ?? 7, from: o.from ?? 66, to: o.to ?? 294, rootAz: 180, fan: 0.9, rootPh: o.rootPh ?? 50, midY: -0.04, midR: o.midR ?? 0.096, lowR: o.lowR ?? 0.11, endY: o.endY, endR: o.endR ?? 0.12, jit: 1.5, w: o.w, flat: 0.4, tip: 0.35, kids: false, hook: 0.5, seed: 11, lift: 0.004 });
// a ringlet: a lock wound in a spiral around its guide
const ringlet = (root, path, o) => L(root, path, { n: 80, flat: 0.75, lens: 0.3, sheet: 0.4, tip: 0.3, sharp: 1.2, ...o, coil: { R: o.R ?? 0.009, turns: o.turns ?? 3.5, ph: o.ph || 0 } });
// a curly clump: a big lock whose surface is twisted into spiral ridges
const curls = (root, path, o) => L(root, path, { ...o, curly: { amp: o.amp ?? 0.22, f: o.f ?? 7, turn: o.turn ?? 3 }, lens: 0.1 });

export const STYLES = {};
// their names as the gallery shows them
export const NAMES = { gwen: 'Гвен: каре с пробором', gogo: 'Гоу-Гоу: тёмное каре с прядью', jack: 'Джек: растрёпанные белые', marco: 'Марко: чёлка набок', ginger: 'рыжий мальчик: начёс', ariel: 'рыжая девушка: длинные', doll: 'девочка-кукла: фиолетовые', kbuns: 'K-pop: пучки', kbraid: 'K-pop: коса', kpony: 'K-pop: хвост', giulia: 'Джулия: кудри под шапкой', alva: 'Альва: шторка', nimona: 'Нимона: вихры', anime: 'аниме: чёлка и длинные' };

// ==== gwen: a blonde bob, a deep side part, a long swept fringe over one eye, the other side short
STYLES.gwen = { skin: 0xf1cdb4, parts: [{ color: 0xead08f, k: 0.007, items: {
  cap: scalpMass({ thick: 0.007, puff: 0.012, back: 0.006, k: 0.007 }),
  back: fall({ n: 8, from: 84, to: 276, rootAz: 180, fan: 0.75, rootPh: 74, midY: 0.0, midR: 0.104, lowR: 0.102, endY: a => -0.066 - 0.01 * Math.cos(a * D), endR: 0.1, tipOut: 0.006, jit: 1.0, layer: 0.003, w: [0.032, 0.036, 0.034], flat: 0.42, tip: 0.18, sharp: 0.6 }),
  fringe: [
    L([-30, 72], [[2, 52, 0.016], [32, 28, 0.014], [56, -0.022, 0.104], [64, -0.064, 0.098]], { w: [0.022, 0.034, 0.034, 0.026, 0.018], flat: 0.45, tip: 0.35, sharp: 0.9 }),
    L([-20, 74], [[0, 60, 0.02], [20, 38, 0.018], [38, 0.004, 0.104], [46, -0.03, 0.1]], { w: [0.018, 0.026, 0.026, 0.018], flat: 0.5, tip: 0.4, sharp: 0.9 }),
    L([-40, 68], [[-46, 42, 0.014], [-56, 0.004, 0.104], [-60, -0.04, 0.1], [-58, -0.064, 0.096]], { w: [0.02, 0.028, 0.028, 0.02], flat: 0.5, tip: 0.35, sharp: 1 }),
  ],
  // the temples and the top behind the part: locks from the part line down to the sides
  temples: [-1, 1].map(s => L([-30 + s * 6, 78], [[s * 50, 56, 0.012], [s * 72, 24, 0.012], [s * 78, -0.03, 0.102], [s * 80, -0.07, 0.1]], { w: [0.024, 0.032, 0.032, 0.026, 0.018], flat: 0.42, hook: 0.5 * s, kids: [{ side: -s, at: 0.6, w: 0.4, len: 0.9 }] })),
  sides: [
    L([-12, 34], [[-36, 42, 0.01], [-66, 34, 0.012], [-88, 0.0, 0.104], [-92, -0.05, 0.1]], { w: [0.02, 0.026, 0.028, 0.024, 0.016], flat: 0.4, hook: -0.4 }),
    L([-30, 82], [[-80, 70, 0.012], [-120, 40, 0.012], [-128, 0.0, 0.106], [-130, -0.06, 0.1]], { w: [0.026, 0.034, 0.034, 0.028, 0.02], flat: 0.42 }),
    L([-24, 82], [[30, 74, 0.014], [96, 50, 0.012], [112, 0.0, 0.106], [116, -0.062, 0.1]], { w: [0.026, 0.034, 0.034, 0.028, 0.02], flat: 0.42 }),
  ],
} }] };

// ==== gogo: a dark short bob, choppy, the fringe in a few big pieces, a purple streak
STYLES.gogo = { skin: 0xf0c7a8, parts: [{ color: 0x241d28, k: 0.007, items: {
  cap: scalpMass({ thick: 0.007, puff: 0.012, back: 0.006, k: 0.007 }),
  back: fall({ n: 8, from: 80, to: 280, rootAz: 180, fan: 0.75, rootPh: 74, midY: 0.0, midR: 0.104, lowR: 0.102, endY: a => -0.048 - 0.01 * Math.cos(a * D), endR: 0.1, tipOut: 0.016, jit: 1.6, layer: 0.003, w: [0.032, 0.036, 0.034], flat: 0.42, tip: 0.2, sharp: 0.7 }),
  fringe: fringe({ clumps: [[-48, 0.004, 0.026, -10], [-26, 0.012, 0.03, 2], [-6, -0.004, 0.034, 6], [16, 0.022, 0.024, 4], [34, 0.008, 0.03, 10]] }),
  sides: [-1, 1].map(s => L([s * 40, 76], [[s * 56, 52, 0.014], [s * 66, 0.03, 0.104], [s * 70, -0.02, 0.104], [s * 66, -0.06, 0.104]], { w: [0.022, 0.03, 0.03, 0.024, 0.016], flat: 0.42, hook: -0.6 * s, kids: [{ side: s, at: 0.55, w: 0.38, len: 0.8 }] })),
  streak: L([30, 76], [[50, 52, 0.03], [64, 0.03, 0.114], [70, -0.03, 0.112]], { w: [0.012, 0.02, 0.02, 0.014], flat: 0.4, tip: 0.45, color: 0x8a3fc0 }),
} }] };

// ==== jack: messy white, short, flopping forward and to the side in soft tufts
STYLES.jack = { skin: 0xf2d6c4, head: { male: 1 }, parts: [{ color: 0xe8e5de, k: 0.009, items: {
  cap: scalpMass({ thick: 0.012, puff: 0.02, back: 0.006, ear: 0.02, behind: -0.03, nape: -0.06, k: 0.009 }),
  // tufts falling forward over the forehead and out to the sides in pointed ends — tousled
  tufts: [[-62, 0.05, 0.026, -14, 0.0], [-40, 0.1, 0.03, -10, 0.01], [-16, 0.12, 0.032, -2, 0.02], [8, 0.125, 0.032, 6, 0.018], [32, 0.11, 0.03, 14, 0.01], [54, 0.08, 0.028, 18, 0.0], [72, 0.03, 0.024, 20, -0.01]].map(([a, y, w, t, f], i) =>
  L([a * 0.6, 66], [[a * 0.8, 72, 0.018], [a + t * 0.4, 0.105 - Math.abs(a) * 0.0004, 0.106], [a + t, 0.05 + (i % 2) * 0.025 - Math.abs(a) * 0.0006 + f, 0.118]], { w: [w, w * 1.2, w * 1.1, w * 0.8], flat: Math.abs(a) > 60 ? 0.32 : 0.5, tip: 0.5, lens: 0.4, hook: i % 2 ? 0.7 : -0.7 })),
  // from the crown, combed forward over the top to the front tufts
  top: [-60, -36, -12, 12, 36, 60].map((a, i) => L([180 - a * 0.6, 74], [[180 - a * 0.4, 84, 0.01], [a * 0.6 + (i % 2 ? 6 : -6), 86, 0.016], [a * 1.05, 66, 0.022], [a * 1.15, 0.075 - (i % 3) * 0.012, 0.114]], { w: [0.024, 0.032, 0.034, 0.03, 0.018], flat: 0.5, tip: 0.4, lens: 0.4, hook: i % 2 ? 0.6 : -0.6 })),
  back: fall({ n: 9, from: 88, to: 272, rootAz: 180, fan: 0.6, rootPh: 74, midY: 0.03, midR: 0.1, endY: a => -0.03 - 0.03 * Math.abs(Math.cos(a * D)), endR: 0.094, tipOut: 0.0, jit: 2.2, layer: 0.005, w: [0.032, 0.036, 0.032], flat: 0.45, tip: 0.25, sharp: 0.7 }),
} }] };

// ==== marco: a brown boy's cut, a big rounded fringe swept to one side
STYLES.marco = { skin: 0xf0c8a6, head: { male: 1 }, parts: [{ color: 0x3e2618, k: 0.008, items: {
  cap: scalpMass({ thick: 0.01, puff: 0.016, back: 0.008, ear: 0.02, behind: -0.035, nape: -0.06, k: 0.008 }),
  fringe: fringe({ part: -30, clumps: [[-38, 0.034, 0.03, 14], [-14, 0.026, 0.036, 22], [12, 0.034, 0.03, 24], [32, 0.024, 0.034, 28], [52, 0.036, 0.026, 26]], tip: 0.55, lift: 0.02 }),
  sides: [-1, 1].map(s => L([s * 44, 74], [[s * 62, 50, 0.016], [s * 76, 0.03, 0.106], [s * 80, -0.025, 0.102]], { w: [0.022, 0.032, 0.032, 0.024], flat: 0.42, hook: 0.5 * s })),
  back: fall({ n: 8, from: 92, to: 268, rootAz: 180, fan: 0.6, rootPh: 74, midY: 0.025, midR: 0.106, endY: a => -0.035 - 0.02 * Math.abs(Math.cos(a * D)), endR: 0.092, jit: 1, layer: 0.003, w: [0.032, 0.036, 0.032], flat: 0.45, tip: 0.22, sharp: 0.65 }),
} }] };

// ==== ginger: a big swept quiff rising from the forehead, over and back to one side
STYLES.ginger = { skin: 0xf3c9a5, head: { male: 1 }, parts: [{ color: 0xc8632b, k: 0.008, under: 0.016, items: {
  cap: scalpMass({ thick: 0.01, puff: 0.014, back: 0.006, ear: 0.02, behind: -0.035, nape: -0.06, k: 0.008 }),
  // the quiff: locks from the front hairline rising steeply, arcing over the top and back down to his left side
  quiff: [
    [[-52, 0.006, 0.026], [-36, 0.012, 0.03], [-20, 0.02, 0.034], [-4, 0.026, 0.036], [12, 0.022, 0.034], [28, 0.014, 0.03], [42, 0.004, 0.026]].map(([a, dy, w], i) =>
    L([a, 32], [[a + 2, 44, 0.024], [a + 8, 0.122 + dy, 0.108], [a + 30, 0.15 + dy, 0.086], [a + 66, 0.135 + dy * 0.6, 0.094], [a + 96 + i * 4, 0.08 - i * 0.004, 0.108]], { w: [w * 0.9, w * 1.2, w * 1.45, w * 1.45, w * 1.3, w * 0.8], flat: 0.36, tip: 0.35, lens: 0.4, hook: i % 2 ? 0.5 : -0.3, kids: i % 3 === 1 ? [{ side: 1, at: 0.65, w: 0.35, len: 1.1 }] : [], dyn: { lTip: 8000, gTip: 2500 } })),   // (set hard: it holds its shape in motion),
    // the quiff's body under its locks, so it is not hollow seen from behind
    ell({ c: [0.015, 0.122, 0.02], r: [0.08, 0.042, 0.07], u: [0.97, 0.24, 0], v: [-0.24, 0.97, 0] }),
  ],
  // a lock falling forward off the quiff's front onto the brow
  forelock: L([-30, 36], [[-30, 50, 0.03], [-20, 0.14, 0.1], [-8, 0.1, 0.12], [-16, 0.06, 0.116]], { w: [0.016, 0.022, 0.022, 0.016, 0.01], flat: 0.5, tip: 0.45, hook: 0.6, dyn: { lTip: 3000, gTip: 600 } }),
  back: fall({ n: 11, from: 84, to: 276, rootAz: 180, fan: 0.75, rootPh: 80, midY: 0.025, midR: 0.104, endY: -0.045, endR: 0.092, jit: 1, layer: 0.003, w: [0.032, 0.038, 0.032], flat: 0.45, tip: 0.22, sharp: 0.65 }),
} }] };

// ==== ariel: long flowing red, high volume at the crown, a big swoop on one side, waves to the waist
STYLES.ariel = { skin: 0xf6dccd, dist: 1.9, ty: -0.13, parts: [{ color: 0xd2321e, k: 0.012, under: 0.03, items: {
  cap: scalpMass({ thick: 0.014, puff: 0.032, back: 0.012, lift: 0.008, k: 0.012 }),
  // the swoop: a big lock lifting from a side part, over the forehead, down past the face in a long S
  front: [
    L([-26, 74], [[4, 64, 0.04], [34, 38, 0.034], [58, -0.01, 0.12], [66, -0.1, 0.12], [56, -0.2, 0.15], [46, -0.3, 0.16], [56, -0.4, 0.15]], { w: [0.03, 0.048, 0.052, 0.05, 0.046, 0.04, 0.032, 0.016], flat: 0.42, tip: 0.25, sharp: 0.8 }),
    L([-30, 74], [[-44, 52, 0.03], [-58, 0.02, 0.118], [-64, -0.09, 0.12], [-52, -0.2, 0.15], [-42, -0.3, 0.16], [-52, -0.38, 0.15]], { w: [0.028, 0.042, 0.046, 0.042, 0.038, 0.03, 0.014], flat: 0.42, tip: 0.25, sharp: 0.8 }),
  ],
  back: fall({ n: 7, from: 104, to: 256, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.12, lowR: 0.15, endY: a => -0.42 - 0.03 * Math.sin(a * 3 * D), endR: 0.14, flare: 0.02, jit: 2, layer: 0.006, w: [0.04, 0.05, 0.046, 0.026], flat: 0.4, tip: 0.3, sharp: 0.8, wave: { amp: 0.012, f: 1.1, step: 0.35 } }),
  // from the part over the crown to the back: the volume on top
  top: fall({ n: 6, from: 70, to: 250, rootAz: -28, fan: 0.3, rootPh: 80, lift: 0.022, midY: 0.0, midR: 0.13, lowR: 0.15, endY: a => -0.36 - 0.03 * Math.cos(a * 2 * D), endR: 0.15, flare: 0.02, jit: 2, w: [0.04, 0.05, 0.046, 0.026], flat: 0.4, tip: 0.3, seed: 5, wave: { amp: 0.012, f: 1.1, step: 0.5 } }),
  under: under({ endY: -0.4, w: [0.036, 0.046, 0.04, 0.024], midR: 0.1, lowR: 0.13, endR: 0.13 }),
} }] };

// ==== doll: violet, voluminous, a big swooping fringe over one brow, locks to the shoulders flicking out
STYLES.doll = { skin: 0xf2c9a8, dist: 1.5, ty: -0.08, parts: [{ color: 0x6b2fd6, k: 0.01, under: 0.026, items: {
  cap: scalpMass({ thick: 0.012, puff: 0.03, back: 0.01, lift: 0.006, k: 0.01 }),
  front: [
    L([-4, 84], [[18, 66, 0.03], [42, 38, 0.024], [62, 0.004, 0.118], [72, -0.05, 0.116]], { w: [0.03, 0.044, 0.046, 0.036, 0.024], flat: 0.45, tip: 0.3, sharp: 0.8 }),
    L([-8, 84], [[-28, 62, 0.026], [-52, 32, 0.02], [-64, -0.01, 0.114], [-70, -0.09, 0.118], [-58, -0.17, 0.16]], { w: [0.028, 0.04, 0.042, 0.038, 0.026], flat: 0.45, tip: 0.3, sharp: 0.8 }),
    L([14, 80], [[44, 44, 0.02], [68, -0.04, 0.114], [76, -0.12, 0.13], [64, -0.18, 0.17]], { w: [0.026, 0.036, 0.036, 0.026], flat: 0.45, tip: 0.3, sharp: 0.8 }),
  ],
  back: fall({ n: 7, from: 112, to: 248, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.118, lowR: 0.124, endY: -0.18, endR: 0.136, tipOut: 0.03, jit: 1.5, layer: 0.005, w: [0.034, 0.044, 0.036], flat: 0.42, tip: 0.3, sharp: 0.8 }),
  top: fall({ n: 6, from: 76, to: 250, rootAz: 4, fan: 0.3, rootPh: 84, lift: 0.02, midY: 0.0, midR: 0.122, lowR: 0.128, endY: -0.16, endR: 0.138, tipOut: 0.03, jit: 1.5, w: [0.036, 0.046, 0.036], flat: 0.42, tip: 0.3, seed: 4 }),
  under: under({ endY: -0.17, w: [0.032, 0.04, 0.032], midR: 0.1, lowR: 0.112, endR: 0.125 }),
} }] };

// ==== kbuns: dark blue, sleek, a short fringe, two buns low at the back
const capB = { thick: 0.006, puff: 0.008, back: 0.004, k: 0.008 };
STYLES.kbuns = { skin: 0xf3cdb8, parts: [{ color: 0x1e2350, k: 0.008, items: {
  cap: scalpMass(capB),
  fringe: fringe({ clumps: [[-38, 0.028, 0.026, -8], [-16, 0.036, 0.028, -2], [6, 0.03, 0.03, 3], [26, 0.038, 0.026, 6], [44, 0.026, 0.022, 10]], r: 0.1, lift: 0.01 }),
  // combed from the hairline and the crown down to each bun
  combed: [
    [-1, 1].flatMap(s => [
    sweep({ from: s * 30, upto: s * 176, n: 10, el: hlEl(capB), to: [s * 150, -14], end: [s * 0.05, -0.012, -0.09], w: 0.028, seed: s }),
    sweep({ from: s * 6, upto: s * 120, n: 6, el: 72, to: [s * 150, -10], end: [s * 0.05, -0.012, -0.09], w: 0.028, seed: s + 3 }),
  ]),
    sweep({ from: 156, upto: 204, n: 4, el: hlEl(capB), to: [180, -6], end: [0, -0.008, -0.098], w: 0.026, seed: 9 }),
  ],
  buns: [
    [-1, 1].map(s => ell({ c: [s * 0.05, -0.012, -0.098], r: [0.024, 0.024, 0.018], k: 0.01 })),
    [-1, 1].flatMap(s => bun([s * 0.05, -0.012, -0.1], [s * 0.3, 0.1, -1], 0.027)),
  ],
} }] };

// ==== kbraid: hair swept back sleek from the forehead into one long braid
const capR = { thick: 0.008, puff: 0.014, back: 0.01, front: 0.07, nape: -0.07, k: 0.006 };
STYLES.kbraid = { skin: 0xf3cdb8, dist: 1.8, ty: -0.12, parts: [{ color: 0x6b50ba, k: 0.006, items: (() => {
  const sw = sweep({ from: -178, upto: 178, n: 22, el: hlEl(capR), to: [180, 52], end: [0, 0.085, -0.08], w: 0.028 });
  // the braid starts at the crown and lies down the back of the head, then hangs
  const br = braid([[0, 0.09, -0.07], [0, 0.04, -0.105], [0, -0.05, -0.118], [0, -0.16, -0.12], [0, -0.28, -0.115], [0, -0.38, -0.11]], { w0: 0.05, w1: 0.034, cross: 5.5, to: [0, -0.52, -0.112], dyn: { heavy: 1 } });
  return { cap: scalpMass(capR), combed: sw, braid: [br,
    tail({ n: 4, path: [[0, -0.37, -0.11], [0, -0.41, -0.112], [0, -0.46, -0.114], [0, -0.5, -0.112]], spread: 0.012, lenJit: 0.03, w: [0.012, 0.016, 0.012], up: [0, 0, -1], rig: br.rig }),
    torus({ c: [0, -0.375, -0.11], a: [0, 1, 0], R: 0.012, r: 0.006, color: 0xe2c060, k: 0.003, rig: br.rig })] };
})() }] };

// ==== kpony: a long high ponytail, a side lock framing the face
const capP = { thick: 0.008, puff: 0.01, back: 0.006, nape: -0.07, k: 0.009 };
STYLES.kpony = { skin: 0xf3cdb8, dist: 1.8, ty: -0.1, parts: [{ color: 0xb8304e, k: 0.009, items: {
  cap: scalpMass(capP),
  combed: sweep({ from: -178, upto: 178, n: 22, el: hlEl(capP), to: [180, 56], end: [0, 0.098, -0.075], w: 0.028 }),
  sideLock: L([-28, 72], [[-34, 44, 0.014], [-52, 0.02, 0.106], [-56, -0.07, 0.104], [-50, -0.13, 0.106]], { w: [0.018, 0.026, 0.026, 0.02, 0.012], flat: 0.45, tip: 0.4, hook: 0.6, kids: [{ side: 1, at: 0.6, w: 0.4, len: 0.8 }] }),
  band: torus({ c: [0, 0.098, -0.07], a: [0, 0.55, -0.83], R: 0.017, r: 0.008, color: 0xe2c060, k: 0.003 }),
  // the tail: out of the band, arcing over and falling long, in several locks
  tail: tail({ n: 7, path: [[0, 0.098, -0.074], [0, 0.118, -0.11], [0, 0.085, -0.15], [0, -0.03, -0.17], [0, -0.18, -0.165], [0, -0.32, -0.15], [0, -0.44, -0.14]], spread: 0.03, lenJit: 0.08, w: [0.012, 0.02, 0.024, 0.022, 0.018, 0.012], up: [0, 0, 1], wave: { amp: 0.008, f: 1 }, dyn: { heavy: 1 } }),
} }] };

// ==== giulia: big red curly clumps, a beanie pushed back on her head
STYLES.giulia = { skin: 0xe9a782, dist: 1.4, parts: [{ color: 0xa8231b, k: 0.006, items: {
  cap: scalpMass({ thick: 0.012, puff: 0.004, back: 0.014, k: 0.008 }),
  // ringlets: locks wound in spirals, falling in two layers around the head, each its own length and turn
  ringlets: [
    [...Array(15)].map((_, i) => { const a = 56 + i * 248 / 14 + (hash(i) - 0.5) * 8, y = -0.07 - 0.035 * Math.abs(Math.cos(a * D / 1.2)) - hash(i * 3.3) * 0.025;
    return ringlet([a, 18], [[a, 0.025, 0.124], [a + (i % 2 ? 6 : -6), y * 0.5, 0.136], [a + (i % 2 ? -4 : 4), y, 0.132]], { w: [0.012, 0.014, 0.014, 0.012, 0.009], R: [0.004, 0.011, 0.014, 0.012], turns: 3.2 + hash(i * 5.1), ph: i * 1.7, kids: false }); }),
    [...Array(11)].map((_, i) => { const a = 68 + i * 224 / 10 + 9, y = -0.035 - 0.02 * Math.abs(Math.cos(a * D / 1.2)) - hash(i * 7.7) * 0.015;
    return ringlet([a, 30], [[a, 0.04, 0.114], [a + 5, y * 0.4, 0.12], [a, y, 0.118]], { w: [0.011, 0.013, 0.013, 0.01], R: [0.004, 0.01, 0.012, 0.01], turns: 2.6 + hash(i * 2.2), ph: i * 2.3 }); }),
  ],
  // her right side: curls bursting out from under the hat, up over it and down past the cheek
  burst: [[-8, 60, -20, 0.075, -34, 0.06], [-22, 50, -34, 0.06, -48, 0.02], [-34, 40, -44, 0.03, -56, -0.03], [-14, 56, -30, 0.09, -44, 0.08], [-40, 30, -56, -0.01, -62, -0.07]].map(([a, el, a1, y1, a2, y2], i) =>
  ringlet([a, el], [[a - 4, el - 10, 0.03], [a1, y1, 0.118], [a2, y2, 0.13]], { w: [0.013, 0.016, 0.016, 0.012], R: [0.004, 0.012, 0.015, 0.012], turns: 2.8 + hash(i * 9.3) * 0.8, ph: i * 1.1 })),
} }, { color: 0x1d8ec4, k: 0.012, rough: 0.85, fabric: true, items: {
  hat: [
    ell({ c: [0.022, 0.056, -0.016], r: [0.102, 0.088, 0.104], u: [0.95, -0.31, 0], v: [0.31, 0.95, 0] }),
    torus({ c: [0.02, 0.04, -0.012], a: [-0.3, 0.95, 0.1], R: 0.1, r: 0.014, flat: 0.8 }),
  ],
}, cuts: [{ sdf: (x, y, z) => (y - 0.04) + 0.3 * x - 0.1 * z, k: 0.004 }] }] };

// ==== alva: long, centre-parted, a heavy curtain framing the face, flicking out at the ends
STYLES.alva = { skin: 0xf0c8b0, dist: 1.8, ty: -0.12, parts: [{ color: 0x8a6a2a, k: 0.01, items: {
  cap: scalpMass({ thick: 0.008, puff: 0.016, back: 0.008, front: 0.074, k: 0.01 }),
  curtain: [-1, 1].map(s => L([0, 86], [[s * 30, 62, 0.016], [s * 58, 28, 0.016], [s * 72, -0.06, 0.116], [s * 76, -0.2, 0.148], [s * 70, -0.3, 0.17], [s * 76, -0.34, 0.19]], { w: [0.03, 0.046, 0.052, 0.054, 0.05, 0.04, 0.02], flat: 0.36, tip: 0.2, sharp: 0.7 })),
  back: fall({ n: 7, from: 98, to: 262, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.114, lowR: 0.134, endY: -0.32, endR: 0.156, flare: 0.02, tipOut: 0.02, jit: 1.5, layer: 0.004, w: [0.036, 0.048, 0.044, 0.026], flat: 0.38, tip: 0.25, sharp: 0.7 }),
  sides: [-1, 1].map(s => L([s * 6, 84], [[s * 60, 50, 0.014], [s * 86, 10, 0.014], [s * 92, -0.08, 0.12], [s * 90, -0.22, 0.15], [s * 94, -0.31, 0.17]], { w: [0.028, 0.04, 0.044, 0.044, 0.036, 0.018], flat: 0.36, hook: -0.5 * s })),
  under: under({ endY: -0.3, w: [0.034, 0.044, 0.038, 0.022], midR: 0.1, lowR: 0.125, endR: 0.145 }),
} }] };

// ==== nimona: pink-red, short tufts flopping over to one side, the other side shaved
STYLES.nimona = { skin: 0xe9a98a, parts: [{ color: 0xe0543e, k: 0.008, items: {
  cap: scalpMass({ thick: 0.01, puff: 0.02, back: 0.006, ear: 0.02, behind: -0.03, nape: -0.06, shave: { side: -1, y: 0.075 }, k: 0.008 }),
  tufts: [[-34, 0.1, 0.03], [-12, 0.112, 0.032], [10, 0.11, 0.032], [32, 0.1, 0.03], [52, 0.08, 0.026]].map(([a, y, w], i) =>
  L([a - 16, 82], [[a - 4, 68, 0.028], [a + 14, y, 0.104], [a + 32, y - 0.04, 0.114], [a + 44, y - 0.07 - (i % 2) * 0.012, 0.114]], { w: [w * 0.7, w, w, w * 0.8, w * 0.5], flat: 0.5, tip: 0.42, sharp: 1.0 })),
  sideLocks: [
    L([34, 62], [[50, 38, 0.014], [64, 0.0, 0.108], [68, -0.08, 0.104], [64, -0.13, 0.104]], { w: [0.016, 0.024, 0.024, 0.018], flat: 0.5, tip: 0.35 }),
    L([60, 70], [[74, 40, 0.016], [82, 0.0, 0.106], [84, -0.05, 0.102]], { w: [0.022, 0.03, 0.03, 0.02], flat: 0.42, hook: 0.5 }),
  ],
  back: fall({ n: 6, from: 104, to: 236, rootAz: 180, fan: 0.6, rootPh: 70, midY: 0.025, midR: 0.106, endY: -0.04, endR: 0.094, tipOut: 0.004, jit: 2, layer: 0.004, w: [0.032, 0.036, 0.032], flat: 0.45, tip: 0.25, sharp: 0.7 }),
  // over the crown from the shaved side's edge, flopping across to the long side
  crown: [[-70, 0.05, 0.03], [-110, 0.04, 0.032], [-150, 0.03, 0.03], [170, 0.04, 0.03], [130, 0.03, 0.028]].map(([a, y, w], i) =>
  L([a * 0.5 - 20, 80], [[a * 0.5 + (a < 0 ? 30 : -10), 76, 0.024], [a > 0 ? a - 10 : 180 + (a + 180) * 0.3, 60, 0.026], [a > 0 ? a : 160 + (a + 180) * 0.2, y, 0.11], [a > 0 ? a + 6 : 150, y - 0.07, 0.106]], { w: [w * 0.7, w, w, w * 0.8], flat: 0.45, hook: i % 2 ? 0.6 : -0.6 })),
} }] };

// ==== anime: blunt bangs in a few pointed clumps, long straight, side locks framing the face
STYLES.anime = { skin: 0xf6e0d6, dist: 1.8, ty: -0.12, parts: [{ color: 0xa8c4d4, k: 0.008, items: {
  cap: scalpMass({ thick: 0.008, puff: 0.014, back: 0.006, front: 0.074, k: 0.008 }),
  fringe: fringe({ clumps: [[-46, 0.006, 0.028, -6], [-28, -0.016, 0.03, -3], [-10, -0.004, 0.026, 0], [6, -0.022, 0.032, 1], [24, -0.008, 0.028, 3], [42, -0.018, 0.03, 6]], flat: 0.36 }),
  sideLocks: [-1, 1].map(s => L([s * 44, 62], [[s * 64, 30, 0.014], [s * 76, -0.04, 0.108], [s * 78, -0.16, 0.124], [s * 72, -0.3, 0.14]], { w: [0.02, 0.028, 0.028, 0.024, 0.014], flat: 0.42, tip: 0.3, sharp: 0.9 })),
  back: fall({ n: 8, from: 98, to: 262, rootAz: 180, fan: 0.55, rootPh: 70, midY: -0.02, midR: 0.112, lowR: 0.124, endY: -0.38, endR: 0.134, jit: 1.5, layer: 0.004, w: [0.034, 0.044, 0.04, 0.022], flat: 0.38, tip: 0.3, sharp: 0.9 }),
  sides: [-1, 1].map(s => L([s * 10, 82], [[s * 62, 52, 0.014], [s * 88, 14, 0.014], [s * 92, -0.1, 0.116], [s * 92, -0.24, 0.13], [s * 90, -0.36, 0.136]], { w: [0.026, 0.036, 0.04, 0.038, 0.03, 0.016], flat: 0.38, hook: 0.4 * s })),
  under: under({ endY: -0.37, w: [0.032, 0.04, 0.036, 0.02], midR: 0.1, lowR: 0.116, endR: 0.126 }),
} }] };
