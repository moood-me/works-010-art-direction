// Patterns: how each garment is cut for a body — the cloth's shape as it is put on (its rest on the body at rest), its
// triangles, what holds it on (its hold: 1 where the skin carries it, as a waistband or a neckline grips, falling to 0
// where it hangs free), its layer (what is worn under what), and the body's skin it lies on (each point's nearest skin
// vertex: its skin weights and its limb).
// Two kinds, as О3 had them (experiments/cloth/wardrobe.js; this is the source now, О3's copy stays for its page):
// - MakeHuman's garments (CC0, data/garments/mh-*: tools/garments.mjs) — each point on three vertices of Anny's mesh, its
//   offset scaled by the body's own measures, so it is laid on any body of that mesh, its rest changes made: simulated
//   as they are (points 2–3 cm apart), drawn with each triangle in four (Loop) — finer cloth would need smaller steps
//   to keep its lengths (src/cloth/sim.js) and cost four times as much;
// - made on the body itself: a blouse, a cardigan, a jacket, a swimsuit (the skin's region offset by the garment's ease,
//   smoothed so the cloth bridges the hollows, the cut points moved onto the cut lines so hem, cuffs, neckline and the
//   open front are clean; the skin's own spacing, about a centimetre, is fine enough), a turtleneck (the neck's skin, Г1's), a flared skirt (a tube from the waist that clears the
//   hips and legs and widens to the hem), a scarf (a strip laid round the back of the neck), a hood (the heads' hood,
//   src/head/pieces.js, now cloth: its shell round the designed head, cut where the body is).
//   PATTERNS[id] → {label, layer, kind, tubes?, self?, hangs?, trousers?, rides?}   what a garment of it is
//   cutFor(body, id, E, ctx) → {positions, triangles, hold, near (each point's nearest skin vertex), flat?, drawn?
//                                (the stencil it is drawn by, subdivided)}
import { normalsOf } from '../mesh.js';
import { regionsOf } from '../regions.js';
import { loadPack } from '../pack.js';
import { clamp, sst, smin } from '../math.js';
import { smax, sdEll, sdCapsule, meshOf } from '../head/shapes.js';

// layer: worn innermost first (0 under 1 under 2…); kind: top, bottom, whole (from the shoulders down), shoes, head;
// tubes: its sleeves and legs belong to their limbs (src/cloth/sim.js); self: it can fold onto itself (kept apart);
// hangs: what of it is below the hips hangs (a skirt, a dress — src/cloth/shape.js: its silhouette from where it hangs);
// trousers: its legs are the body's legs (shape.js); rides: carried by the skin as it is (shoes), not cloth; tight: its
// lengths a share of how it was cut (a swimsuit holds to the body)
export const PATTERNS = {
  'mh-dress': { label: { ru: 'платье', en: 'dress' }, layer: 1, kind: 'whole', self: true, hangs: true },
  'mh-tshirt': { label: { ru: 'футболка', en: 'T-shirt' }, layer: 1, kind: 'top', tubes: true },
  'mh-sweater': { label: { ru: 'свитер', en: 'sweater' }, layer: 1, kind: 'top', tubes: true },
  'mh-polo': { label: { ru: 'поло', en: 'polo shirt' }, layer: 1, kind: 'top', tubes: true },
  'mh-oversized': { label: { ru: 'оверсайз', en: 'oversized top' }, layer: 1, kind: 'top', tubes: true },
  'mh-tunic': { label: { ru: 'туника', en: 'tunic' }, layer: 1, kind: 'whole', tubes: true, self: true, hangs: true },
  'mh-robe': { label: { ru: 'халат', en: 'robe' }, layer: 2, kind: 'whole', tubes: true, self: true, hangs: true },
  'mh-hood': { label: { ru: 'худи с капюшоном', en: 'hooded top' }, layer: 2, kind: 'top', tubes: true },
  'mh-pants': { label: { ru: 'брюки', en: 'trousers' }, layer: 0, kind: 'bottom', tubes: true, self: true, trousers: true },
  'mh-shorts': { label: { ru: 'шорты', en: 'shorts' }, layer: 0, kind: 'bottom', tubes: true, trousers: true },
  'mh-skirt': { label: { ru: 'юбка', en: 'skirt' }, layer: 0, kind: 'bottom', self: true, hangs: true },
  'mh-vikingpants': { label: { ru: 'широкие штаны', en: 'wide trousers' }, layer: 0, kind: 'bottom', tubes: true, self: true, trousers: true },
  'mh-apron': { label: { ru: 'фартук', en: 'apron' }, layer: 3, kind: 'whole', hangs: true },
  'mh-boots': { label: { ru: 'ботинки', en: 'boots' }, layer: 0, kind: 'shoes', rides: true },
  'mh-flats': { label: { ru: 'туфли', en: 'flats' }, layer: 0, kind: 'shoes', rides: true },
  blouse: { label: { ru: 'блузка', en: 'blouse' }, layer: 1, kind: 'top', tubes: true },
  cardigan: { label: { ru: 'кардиган', en: 'cardigan' }, layer: 2, kind: 'top', tubes: true },
  jacket: { label: { ru: 'куртка', en: 'jacket' }, layer: 2, kind: 'top', tubes: true },
  swimsuit: { label: { ru: 'купальник', en: 'swimsuit' }, layer: 0, kind: 'whole', tight: 0.94 },
  turtleneck: { label: { ru: 'высокий ворот', en: 'turtleneck collar' }, layer: 2, kind: 'top' },
  'flared-skirt': { label: { ru: 'юбка-трапеция', en: 'flared skirt' }, layer: 0, kind: 'bottom', self: true, hangs: true },
  scarf: { label: { ru: 'шарф', en: 'scarf' }, layer: 4, kind: 'top', self: true },
  hood: { label: { ru: 'капюшон', en: 'hood' }, layer: 3, kind: 'head' },
};

// the garment cut for a body at its rest. ctx: {frame (the head's units, src/head/frame.js), form (a designed head's
// shape, if it has one)} for a hood. Each pattern's cut is made once per body and kept.
const CUTS = new WeakMap();
export async function cutFor(body, id, E, ctx = {}) {
  const P = PATTERNS[id]; if (!P) throw new Error(`no pattern "${id}" (${Object.keys(PATTERNS).join(', ')})`);
  let byBody = CUTS.get(body.mesh.positions); if (!byBody) CUTS.set(body.mesh.positions, byBody = new Map());
  const key = id === 'hood' ? `${id}:${ctx.wide ?? 1}:${ctx.frame.O.join()}:${ctx.frame.R}` : id;
  if (!byBody.has(key)) byBody.set(key, made(body, id, P, E, ctx));
  return byBody.get(key);
}
async function made(body, id, P, E, ctx) {
  const B = onBody(body), g = id.startsWith('mh-') ? mh(B, await sourceOf(E, id)) : MADE[id](B, ctx);
  // (the cloth is simulated as cut; drawn, where it is coarse, subdivided once: `drawn`, the stencil)
  let pos = g.pos, tris = g.tris;
  const hold = P.rides ? new Float32Array(pos.length / 3).fill(1) : (g.hold ?? HOLDS[id] ?? HOLDS[P.kind])(pos, tris, B);
  const near = nearestOn(B.rest, pos, B.used);
  // which way is out: away from the body — the triangles turned so most face away from the skin under them (the inside
  // of a garment is its back)
  tris = Uint32Array.from(tris);
  const nrm = normalsOf(pos, tris); let out = 0;
  for (let i = 0; i < pos.length / 3; i++) { const b = near[i]; out += Math.sign(nrm[i * 3] * B.nrm[b * 3] + nrm[i * 3 + 1] * B.nrm[b * 3 + 1] + nrm[i * 3 + 2] * B.nrm[b * 3 + 2]); }
  if (out < 0 && !g.flat) for (let t = 0; t < tris.length; t += 3) { const b = tris[t + 1]; tris[t + 1] = tris[t + 2]; tris[t + 2] = b; }
  return { positions: pos, triangles: tris, hold, near, flat: g.flat ?? null, drawn: g.drawn ? loopStencil(pos.length / 3, tris) : null };
}
// MakeHuman's source meshes, read once
const SOURCES = new Map();
function sourceOf(E, id) {
  if (!SOURCES.has(id)) SOURCES.set(id, loadPack(new URL(`data/garments/${id}.json`, E.root).href, E.read).then(({ header: h, arrays: a }) => {
    if (h.format !== 'engine/garment' || h.version !== 1) throw new Error(`data/garments/${id}: not a garment of version 1`);
    return { ...a, unit: h.unit, topology: h.topology };
  }));
  return SOURCES.get(id);
}

// what a pattern reads off the body: its rest, normals, joints, each vertex's group (torso, arm, hand, leg, head: shares
// from its skin) and limb (0 trunk and head, 1 2 the left and right arm with the hand, 3 4 the legs)
const BODIES = new WeakMap();
export function onBody(body) {
  if (BODIES.has(body.mesh.positions)) return BODIES.get(body.mesh.positions);
  const mesh = body.mesh, rig = body.rig, sk = rig.skeleton, R = regionsOf(mesh, rig), N = mesh.N, K = mesh.skin.K;
  const GROUP = { torso: 0, clav: 0, arm: 1, fore: 1, hand: 2, thigh: 3, shin: 3, foot: 3, neck: 4, head: 4 };
  const G = new Float32Array(N * 5);
  for (let i = 0; i < N; i++) for (let k = 0; k < K; k++) { const w = mesh.skin.weights[i * K + k]; if (w) G[i * 5 + GROUP[R.segs[R.jseg[mesh.skin.joints[i * K + k]]].kind]] += w; }
  const limb = new Uint8Array(N); for (let i = 0; i < N; i++) { let m = 0; for (let l = 1; l < 5; l++) if (R.limb[i * 5 + l] > R.limb[i * 5 + m]) m = l; limb[i] = m; }
  const J = n => { const j = sk.index[n]; return { x: rig.joints[j * 3], y: rig.joints[j * 3 + 1], z: rig.joints[j * 3 + 2] }; };
  const out = { body, N, rest: mesh.positions, tris: mesh.triangles, used: mesh.used, nrm: normalsOf(mesh.positions, mesh.triangles, undefined, mesh.used), G, limb, J, height: body.measures.height, regions: R };
  BODIES.set(body.mesh.positions, out);
  return out;
}

// ———— meshes ————
export function edgesOf(tris) {
  const m = new Map();
  for (let t = 0; t < tris.length; t += 3) for (let k = 0; k < 3; k++) {
    const a = tris[t + k], b = tris[t + (k + 1) % 3], key = a < b ? a * 4194304 + b : b * 4194304 + a;
    m.set(key, (m.get(key) || 0) + 1);
  }
  return m;
}
const ends = key => [Math.floor(key / 4194304), key % 4194304];
// Loop subdivision as a stencil: each triangle in four, every point of the finer mesh a weighed sum of the coarse
// mesh's points (toward the smooth surface; open edges kept as curves of their own) — so the cloth is simulated coarse
// and drawn smooth: {triangles, N, start, idx, w} (the finer points' weights, compressed rows)
export function loopStencil(n, tris) {
  const E = edgesOf(tris), opp = new Map(), mid = new Map(), rows = [];
  for (let t = 0; t < tris.length; t += 3) for (let k = 0; k < 3; k++) {
    const a = tris[t + k], b = tris[t + (k + 1) % 3], c = tris[t + (k + 2) % 3], key = a < b ? a * 4194304 + b : b * 4194304 + a;
    (opp.get(key) || opp.set(key, []).get(key)).push(c);
  }
  const nb = Array.from({ length: n }, () => new Set()), bnb = Array.from({ length: n }, () => new Set());
  for (const [key, c] of E) { const [a, b] = ends(key); nb[a].add(b); nb[b].add(a); if (c !== 2) { bnb[a].add(b); bnb[b].add(a); } }
  for (let i = 0; i < n; i++) {
    if (bnb[i].size === 2) { const [a, b] = [...bnb[i]]; rows.push([[i, 0.75], [a, 0.125], [b, 0.125]]); continue; }
    if (bnb[i].size > 2 || !nb[i].size) { rows.push([[i, 1]]); continue; }
    const k = nb[i].size, beta = k === 3 ? 3 / 16 : 3 / (8 * k);
    rows.push([[i, 1 - k * beta], ...[...nb[i]].map(j => [j, beta])]);
  }
  for (const [key, c] of E) {
    const [a, b] = ends(key), o = opp.get(key);
    mid.set(key, rows.length);
    rows.push(c === 2 ? [[a, 0.375], [b, 0.375], [o[0], 0.125], [o[1], 0.125]] : [[a, 0.5], [b, 0.5]]);
  }
  const T = [], M = (a, b) => mid.get(a < b ? a * 4194304 + b : b * 4194304 + a);
  for (let t = 0; t < tris.length; t += 3) { const a = tris[t], b = tris[t + 1], c = tris[t + 2], ab = M(a, b), bc = M(b, c), ca = M(c, a); T.push(a, ab, ca, ab, b, bc, ca, bc, c, ab, bc, ca); }
  const start = new Int32Array(rows.length + 1); rows.forEach((r, i) => { start[i + 1] = start[i] + r.length; });
  const idx = new Int32Array(start[rows.length]), w = new Float32Array(start[rows.length]);
  rows.forEach((r, i) => r.forEach(([j, v], k) => { idx[start[i] + k] = j; w[start[i] + k] = v; }));
  return { triangles: Uint32Array.from(T), N: rows.length, start, idx, w };
}
// the finer points of a stencil from the coarse ones (into out)
export function stenciled(S, P, out = new Float32Array(S.N * 3)) {
  const { start, idx, w } = S;
  for (let i = 0; i < S.N; i++) { let x = 0, y = 0, z = 0; for (let k = start[i]; k < start[i + 1]; k++) { const j = idx[k] * 3, v = w[k]; x += P[j] * v; y += P[j + 1] * v; z += P[j + 2] * v; } out[i * 3] = x; out[i * 3 + 1] = y; out[i * 3 + 2] = z; }
  return out;
}
// the open edges, as loops of points
export function boundaryLoops(tris) {
  const adj = new Map();
  for (const [key, c] of edgesOf(tris)) if (c === 1) { const [a, b] = ends(key); (adj.get(a) || adj.set(a, []).get(a)).push(b); (adj.get(b) || adj.set(b, []).get(b)).push(a); }
  const seen = new Set(), loops = [];
  for (const s of adj.keys()) { if (seen.has(s)) continue; const L = [], st = [s]; while (st.length) { const v = st.pop(); if (seen.has(v)) continue; seen.add(v); L.push(v); for (const u of adj.get(v)) st.push(u); } loops.push(L); }
  return loops;
}
// distance along the cloth from a set of its points
export function along(pos, tris, from) {
  const n = pos.length / 3, d = new Float64Array(n).fill(Infinity), adj = Array.from({ length: n }, () => []);
  for (const key of edgesOf(tris).keys()) { const [a, b] = ends(key), l = Math.hypot(pos[a * 3] - pos[b * 3], pos[a * 3 + 1] - pos[b * 3 + 1], pos[a * 3 + 2] - pos[b * 3 + 2]); adj[a].push(b, l); adj[b].push(a, l); }
  let front = [...from]; for (const i of from) d[i] = 0;
  while (front.length) { const next = new Set(); for (const i of front) { const a = adj[i]; for (let k = 0; k < a.length; k += 2) { const j = a[k], v = d[i] + a[k + 1]; if (v < d[j] - 1e-9) { d[j] = v; next.add(j); } } } front = [...next]; }
  return d;
}
const loopStat = (pos, L) => { let x = 0, y = 0, z = 0, ax = 0; for (const v of L) { x += pos[v * 3]; y += pos[v * 3 + 1]; z += pos[v * 3 + 2]; ax += Math.abs(pos[v * 3]); } const k = L.length; return { x: x / k, y: y / k, z: z / k, ax: ax / k, n: k }; };
// each of Q's points' nearest among P's used points (a hash of 3 cm cells)
export function nearestOn(P, Q, used) {
  const cell = 0.03, grid = new Map(), key = (x, y, z) => x + ',' + y + ',' + z, out = new Int32Array(Q.length / 3);
  for (const i of used) { const k = key(Math.floor(P[i * 3] / cell), Math.floor(P[i * 3 + 1] / cell), Math.floor(P[i * 3 + 2] / cell)); (grid.get(k) || grid.set(k, []).get(k)).push(i); }
  for (let q = 0; q < out.length; q++) {
    const x = Q[q * 3], y = Q[q * 3 + 1], z = Q[q * 3 + 2], cx = Math.floor(x / cell), cy = Math.floor(y / cell), cz = Math.floor(z / cell);
    let best = -1, bd = Infinity;
    for (let r = 0; r < 40 && (best < 0 || Math.sqrt(bd) > (r - 1) * cell); r++) for (let dx = -r; dx <= r; dx++) for (let dy = -r; dy <= r; dy++) for (let dz = -r; dz <= r; dz++) {
      if (Math.max(Math.abs(dx), Math.abs(dy), Math.abs(dz)) !== r) continue;
      const a = grid.get(key(cx + dx, cy + dy, cz + dz)); if (!a) continue;
      for (const i of a) { const d = (P[i * 3] - x) ** 2 + (P[i * 3 + 1] - y) ** 2 + (P[i * 3 + 2] - z) ** 2; if (d < bd) { bd = d; best = i; } }
    }
    out[q] = best;
  }
  return out;
}

// ———— MakeHuman's: each point on its three body points, the offset scaled by the body's measures ————
function mh(B, g) {
  const P = B.rest, V = g.refs.length / 3, s = [0, 1, 2].map(k => Math.abs(P[g.measure[k * 2] * 3 + k] - P[g.measure[k * 2 + 1] * 3 + k]) / g.span[k]);
  const out = new Float32Array(V * 3);
  for (let i = 0; i < V; i++) for (let c = 0; c < 3; c++) {
    let v = g.offset[i * 3 + c] * g.unit * s[c];
    for (let k = 0; k < 3; k++) v += g.bary[i * 3 + k] * P[g.refs[i * 3 + k] * 3 + c];
    out[i * 3 + c] = v;
  }
  return { pos: out, tris: g.triangles, drawn: true };
}

// ———— what holds a garment on ————
// 1 near the loop `which` picks, falling off along the cloth from near to far
function holdNear(pos, tris, which, near, far) {
  const loops = boundaryLoops(tris).map(L => ({ L, ...loopStat(pos, L) })), L = which(loops), d = along(pos, tris, L ? L.L : []);
  return Float32Array.from(d, v => 1 - sst(clamp((v - near) / (far - near), 0, 1)));
}
const topLoop = loops => loops.reduce((a, b) => (b.y - b.ax > a.y - a.ax ? b : a));
const neckLoop = loops => loops.filter(l => l.ax < 0.09).reduce((a, b) => (b.y > a.y ? b : a), { y: -Infinity, L: [] });
// a long-sleeved top: held at the neckline, and lightly at the cuffs (a buttoned or ribbed cuff grips the wrist)
function topHold(pos, tris) {
  const neck = holdNear(pos, tris, neckLoop, 0.02, 0.05);
  const loops = boundaryLoops(tris).map(L => ({ L, ...loopStat(pos, L) })), far = loops.reduce((m, l) => Math.max(m, l.ax), 0);
  const cuffs = loops.filter(l => l.ax > far * 0.8 && l.ax > 0.2).flatMap(l => l.L), d = along(pos, tris, cuffs);
  return Float32Array.from(neck, (v, i) => Math.max(v, 0.5 * (1 - sst(clamp((d[i] - 0.01) / 0.02, 0, 1)))));
}
// from the shoulders (a dress: held over them, lightly down to the chest), and its openings above the chest (a
// bodice's top edge, its armholes) where they lie on the body
function shoulderHold(pos, tris, B) {
  const sh = B.J('LeftArm').y, sp = B.J('Spine2').y, ch = B.J('Chest').y;
  const edges = boundaryLoops(tris).filter(L => loopStat(pos, L).y > ch).flat(), d = along(pos, tris, edges);
  return Float32Array.from({ length: pos.length / 3 }, (_, i) => { const y = pos[i * 3 + 1]; return Math.max(y > sh + 0.02 ? 1 : y > sp ? 0.25 * sst((y - sp) / 0.08) : 0, 0.7 * (1 - sst(clamp((d[i] - 0.015) / 0.025, 0, 1)))); });
}
const HOLDS = {
  top: (pos, tris) => holdNear(pos, tris, neckLoop, 0.02, 0.05), bottom: (pos, tris) => holdNear(pos, tris, topLoop, 0.025, 0.05), whole: shoulderHold,
  'mh-sweater': topHold, 'mh-hood': topHold, 'mh-robe': topHold, 'mh-tunic': shoulderHold, 'mh-polo': topHold, blouse: topHold, cardigan: topHold, jacket: topHold,
  'mh-apron': (pos, tris) => holdNear(pos, tris, topLoop, 0.02, 0.04),
  swimsuit: (pos, tris) => { const d = along(pos, tris, boundaryLoops(tris).flat()); return Float32Array.from(d, v => 0.5 * (1 - sst(clamp((v - 0.008) / 0.012, 0, 1))) + 0.15); },
};

// ———— made on the body: the skin's region, offset by the ease ————
// spec: {keep(groups) → whether a vertex of these group shares may be in it, cut(p) → ≥ 0 inside (p its rest place),
// ease(p, groups) → metres, smooth: rounds, hold: the least share of the ease it keeps off the skin, minPiece}
function bodyShell(B, spec) {
  const N = B.N, R = B.rest, NR = B.nrm, G = B.G, w = i => G.subarray(i * 5, i * 5 + 5), P = Float32Array.from(R), p = i => [P[i * 3], P[i * 3 + 1], P[i * 3 + 2]];
  // the points nearest the cut lines moved onto them, so the hem, cuffs and neckline are clean curves
  const T = B.tris, val = new Float32Array(N);
  for (let i = 0; i < N; i++) val[i] = spec.keep(w(i)) ? spec.cut(p(i)) : -1;
  const moved = new Uint8Array(N);
  for (let t = 0; t < T.length; t += 3) for (let k = 0; k < 3; k++) {
    const a = T[t + k], b = T[t + (k + 1) % 3];
    if ((val[a] >= 0) === (val[b] >= 0) || val[a] === -1 || val[b] === -1) continue;
    const i = Math.abs(val[a]) < Math.abs(val[b]) ? a : b; if (moved[i]) continue;
    const j = i === a ? b : a, s = val[i] / (val[i] - val[j]);
    if (s > 0.5) continue;
    for (let c = 0; c < 3; c++) P[i * 3 + c] += (R[j * 3 + c] - R[i * 3 + c]) * s;
    val[i] = 0; moved[i] = 1;
  }
  const tris = [];
  for (let t = 0; t < T.length; t += 3) if (val[T[t]] >= 0 && val[T[t + 1]] >= 0 && val[T[t + 2]] >= 0) tris.push(T[t], T[t + 1], T[t + 2]);
  // the large pieces (two sleeves are one garment with the torso)
  const used = [...new Set(tris)], id = new Int32Array(N).fill(-1); used.forEach((v, k) => id[v] = k);
  const tr = Uint32Array.from(tris, v => id[v]), n = used.length;
  const parent = Int32Array.from({ length: n }, (_, i) => i), find = i => { while (parent[i] !== i) i = parent[i] = parent[parent[i]]; return i; };
  for (let t = 0; t < tr.length; t += 3) { const a = find(tr[t]), b = find(tr[t + 1]); parent[b] = a; parent[find(tr[t + 2])] = a; }
  const size = new Map(); for (let i = 0; i < n; i++) { const r = find(i); size.set(r, (size.get(r) || 0) + 1); }
  const keep = new Set([...size].filter(([, s]) => s >= (spec.minPiece ?? 200)).map(([r]) => r));
  const t2 = []; for (let t = 0; t < tr.length; t += 3) if (keep.has(find(tr[t]))) t2.push(tr[t], tr[t + 1], tr[t + 2]);
  const used2 = [...new Set(t2)], id2 = new Int32Array(n).fill(-1); used2.forEach((v, k) => id2[v] = k);
  const tris3 = Uint32Array.from(t2, v => id2[v]), src = Int32Array.from(used2, v => used[v]), m = src.length;
  // offset by the ease, then smoothed: the cloth bridges the hollows; never nearer the skin than its ease allows
  const X = new Float32Array(m * 3), want = new Float32Array(m);
  for (let k = 0; k < m; k++) { const i = src[k]; want[k] = spec.ease(p(i), w(i)); for (let c = 0; c < 3; c++) X[k * 3 + c] = P[i * 3 + c] + NR[i * 3 + c] * want[k]; }
  const nb = Array.from({ length: m }, () => []), bnb = Array.from({ length: m }, () => []);
  for (const [key, c] of edgesOf(tris3)) { const [a, b] = ends(key); nb[a].push(b); nb[b].push(a); if (c === 1) { bnb[a].push(b); bnb[b].push(a); } }
  const Y = new Float32Array(m * 3);
  for (let it = 0; it < (spec.smooth ?? 12); it++) {
    for (let k = 0; k < m; k++) { const L = bnb[k].length ? bnb[k] : nb[k]; for (let c = 0; c < 3; c++) { let s = 0; for (const j of L) s += X[j * 3 + c]; Y[k * 3 + c] = X[k * 3 + c] * 0.4 + 0.6 * s / L.length; } }
    for (let k = 0; k < m; k++) {
      const i = src[k]; let d = 0; for (let c = 0; c < 3; c++) d += (Y[k * 3 + c] - P[i * 3 + c]) * NR[i * 3 + c];
      const lo = want[k] * (spec.hold ?? 0.75); if (d < lo) for (let c = 0; c < 3; c++) Y[k * 3 + c] += NR[i * 3 + c] * (lo - d);
    }
    X.set(Y);
  }
  return { pos: X, tris: tris3, drawn: false };
}
// the body's outline across, at a height: for each of K directions round the centre, how far out the skin reaches
// (arms and hands left out) — what a skirt must clear
function hull(B, y, band, K, cz) {
  const R = new Float32Array(K), P = B.rest, G = B.G;
  for (const i of B.used) {
    if (Math.abs(P[i * 3 + 1] - y) > band || G[i * 5 + 1] + G[i * 5 + 2] > 0.3) continue;
    const x = P[i * 3], z = P[i * 3 + 2] - cz, a = Math.atan2(x, z), k = ((Math.round(a / (2 * Math.PI) * K) % K) + K) % K, r = Math.hypot(x, z);
    if (r > R[k]) R[k] = r;
  }
  for (let it = 0; it < K; it++) for (let k = 0; k < K; k++) if (!R[k]) R[k] = Math.max(R[(k + 1) % K], R[(k + K - 1) % K]);
  const S = new Float32Array(K);
  for (let k = 0; k < K; k++) { let m = 0; for (let d = -2; d <= 2; d++) m = Math.max(m, R[(k + d + K) % K]); S[k] = m; }
  return S;
}
// a flared skirt: a tube of cloth from the waist down, clearing the hips and legs, widening to the hem; each ring as
// many points as its girth takes (about 2 cm apart, drawn subdivided), neighbouring rings zipped together
function flaredSkirt(B, o) {
  const s = B.height / 1.6, hips = B.J('Hips'), knee = B.J('LeftShin');
  const top = hips.y + o.waist * s, bottom = knee.y + o.hem * s, cz = hips.z, K = 180, step = 0.02;
  const rows = Math.round((top - bottom) / step), radii = [];
  let r = null;
  for (let i = 0; i <= rows; i++) {
    const u = i / rows, y = top - (top - bottom) * u, H = hull(B, y, 0.012, K, cz);
    if (!r) r = Float32Array.from(H, v => v + 0.004); else for (let k = 0; k < K; k++) r[k] = Math.max(r[k], H[k] + o.ease);
    radii.push(Float32Array.from(r, v => v + o.flare * s * Math.pow(Math.max(0, (u - 0.15) / 0.85), 1.3)));
  }
  for (let it = 0; it < 6; it++) for (let i = 1; i < rows; i++) for (let k = 0; k < K; k++) radii[i][k] = Math.max(radii[i][k], (radii[i - 1][k] + radii[i + 1][k]) / 2);
  for (const R of radii) for (let it = 0; it < 4; it++) { const c = Float32Array.from(R); for (let k = 0; k < K; k++) R[k] = (c[(k + K - 1) % K] + 2 * c[k] + c[(k + 1) % K]) / 4; }
  const pos = [], start = [], count = [];
  for (let i = 0; i <= rows; i++) {
    const y = top - (top - bottom) * i / rows, R = radii[i];
    let girth = 0; for (let k = 0; k < K; k++) girth += R[k] * 2 * Math.PI / K;
    const n = Math.max(24, Math.round(girth / step)); start.push(pos.length / 3); count.push(n);
    for (let j = 0; j < n; j++) { const t = j / n * K, k0 = Math.floor(t) % K, f = t - Math.floor(t), rr = R[k0] * (1 - f) + R[(k0 + 1) % K] * f, a = j / n * 2 * Math.PI; pos.push(Math.sin(a) * rr, y, cz + Math.cos(a) * rr); }
  }
  const tris = [];
  for (let i = 0; i < rows; i++) {
    const A = start[i], na = count[i], C = start[i + 1], nc = count[i + 1];
    let a = 0, b = 0;
    while (a < na || b < nc) { const ta = (a + 1) / na, tb = (b + 1) / nc; if (b >= nc || (a < na && ta <= tb)) { tris.push(A + a % na, C + b % nc, A + (a + 1) % na); a++; } else { tris.push(A + a % na, C + b % nc, C + (b + 1) % nc); b++; } }
  }
  return { pos: Float32Array.from(pos), tris: Uint32Array.from(tris), drawn: true };
}
// the scarf: a strip of cloth laid round the back of the neck, its two ends down the front; it keeps the lengths it has
// flat, whatever shape it was laid on in
function scarf(B, o) {
  const neck = B.J('Neck1'), s = B.height / 1.6, P = B.rest, G = B.G;
  const L = o.length * s, W = o.width * s, du = 0.012, nv = Math.max(6, Math.round(W / du));
  const ds = []; for (const i of B.used) { if (Math.abs(P[i * 3 + 1] - (neck.y + 0.015)) < 0.012 && G[i * 5 + 4] > 0.5) ds.push(Math.hypot(P[i * 3], P[i * 3 + 2] - neck.z)); }
  ds.sort((a, b) => a - b); const r = ds[Math.floor(ds.length * 0.8)] || 0.06 * s;
  const R = r + 0.022 * s, y0 = neck.y - 0.015 * s, a0 = 0.32 * Math.PI, a1 = 1.68 * Math.PI, ring = R * (a1 - a0), hang = (L - ring) / 2;
  const front = (x, y) => { let z = -1; for (const i of B.used) if (Math.abs(P[i * 3 + 1] - y) < 0.015 && Math.abs(P[i * 3] - x) < 0.03 && G[i * 5 + 1] + G[i * 5 + 2] < 0.3) z = Math.max(z, P[i * 3 + 2]); return z; };
  const centre = [], across = [], nu = Math.round(L / du);
  for (let i = 0; i <= nu; i++) {
    const u = i / nu * L;
    if (u < hang || u > L - hang) {
      const side = u < hang ? 1 : -1, k = u < hang ? hang - u : u - (L - hang), a = side > 0 ? a0 : a1;
      const xs = Math.sin(a) * R, xe = side * Math.max(Math.abs(xs), W / 2 + 0.008 * s), x = xs + (xe - xs) * Math.min(1, k / 0.06), y = y0 - k, z0 = neck.z + Math.cos(a) * R, z = Math.max(z0, front(x, y) + 0.012 * s);
      centre.push([x, y, k < 0.04 ? z0 + (z - z0) * k / 0.04 : z]); across.push([side, 0, 0]);
    } else {
      const a = a0 + (u - hang) / ring * (a1 - a0), ox = Math.sin(a), oz = Math.cos(a);
      centre.push([ox * R, y0, neck.z + oz * R]); across.push([ox * 0.75, -0.66, oz * 0.75]);
    }
  }
  const pos = [], flat = [], hold = [];
  for (let i = 0; i <= nu; i++) for (let j = 0; j <= nv; j++) {
    const v = j / nv - 0.5, c = centre[i], d = across[i], off = d[1] ? (v + 0.5) * W * 0.8 : v * W, u = i / nu * L;
    flat.push(u, 0, v * W); pos.push(c[0] + d[0] * off, c[1] + d[1] * off, c[2] + d[2] * off);
    hold.push(Math.abs(u - L / 2) / (L / 2 - hang) < 0.5 ? 0.35 : 0);
  }
  const tris = [];
  for (let i = 0; i < nu; i++) for (let j = 0; j < nv; j++) { const a = i * (nv + 1) + j, b = a + 1, c = a + nv + 1, d = c + 1; tris.push(a, b, c, b, d, c); }
  return { pos: Float32Array.from(pos), flat: Float32Array.from(flat), tris: Uint32Array.from(tris), hold: () => Float32Array.from(hold), drawn: false };
}

// the cut shapes of the garments made on the body (rest, metres; the body's joints place them)
function torsoCut(B, o) {
  const sh = B.J('LeftArm'), hips = B.J('Hips'), neck = B.J('Neck1'), hand = B.J('LeftHand'), s = B.height / 1.6;
  const zc = neck.z, hemY = hips.y + o.hem * s, ax = [hand.x - sh.x, hand.y - sh.y, hand.z - sh.z], al = Math.hypot(...ax), u = ax.map(v => v / al);
  return ([x, y, z]) => {
    const X = Math.abs(x);
    let f = y - hemY;
    const r = Math.hypot(x, (z - zc) * 1.15);
    f = Math.min(f, Math.max(r - (o.neckR ?? 0.07) * s, (neck.y - (o.neckDepth ?? 0.03) * s) - y));
    if (o.vneck && z > zc + 0.02) f = Math.min(f, (neck.y - o.vneck * s + X * 2.2) - y);
    if (o.open && z > zc + 0.03 && y < neck.y + 0.05) f = Math.min(f, X - o.open * s);
    if (X > sh.x * 0.9) { const t = (X - sh.x) * u[0] + (y - sh.y) * u[1] + (z - sh.z) * u[2]; f = Math.min(f, o.sleeve * al - t); }
    return f;
  };
}
const torsoKeep = w => w[2] < 0.3 && w[4] < 0.5 && w[3] < 0.6;
// a buttoned cuff: the sleeve's fullness gathered into it over the last centimetres before the wrist
function cuff(B, q) { const h = B.J(q[0] > 0 ? 'LeftHand' : 'RightHand'), d = Math.hypot(q[0] - h.x, q[1] - h.y, q[2] - h.z); return sst(clamp((d - 0.05) / 0.08, 0, 1)) * 0.85 + 0.15; }
function swimCut(B) {
  const hips = B.J('Hips'), leg = B.J('LeftLeg'), chest = B.J('Chest'), neck = B.J('Neck1'), s = B.height / 1.6;
  const crotch = leg.y - 0.075 * s, top = chest.y + 0.09 * s, zc = hips.z;
  return ([x, y, z]) => {
    const X = Math.abs(x);
    const f = y - (crotch + Math.max(0, X - 0.035 * s) * 1.25);
    let up = z < zc ? top - 0.05 * s - y : top - y;
    up = Math.max(up, Math.min(0.017 * s - Math.abs(X - 0.07 * s), neck.y + 0.06 - y));
    return Math.min(f, up);
  };
}
// the neck's skin from under the jaw to its base (Г1's turtleneck, experiments/heads-anime), standing a little off it
function turtleneck(B) {
  const top = B.J('Head').y - 0.01, bot = B.J('Neck1').y - 0.03;
  return bodyShell(B, { keep: w => w[4] > 0.2 || w[0] > 0.5, cut: ([, y]) => Math.min(top - y, y - bot), ease: () => 0.012, smooth: 20, hold: 0.7, minPiece: 50 });
}
// the hood round the designed head (or Anny's own): the heads' hood shell (src/head/pieces.js) as one sheet — its outer
// surface, the face left open, and below where it meets the shoulders cut along the skin
const HOOD_STEP = 0.2;
function hood(B, ctx) {
  const F = ctx.frame; if (!F) throw new Error('a hood is cut round a head: its frame (the head\'s units) is needed');
  const W = ctx.wide ?? 1;
  const shell = (x, y, z) => smin(sdEll(x, y - 0.12, z + 0.1, 1.24 * W, 1.32, 1.32), sdCapsule(x, y, z, [0, -0.7, -0.3], [0, -2.2, -0.4], [1.15 * W, 1.4 * W]), 0.5);
  const open = (x, y, z) => smax((Math.hypot(x / (0.92 * W), (y + 0.42) / 1.18) - 1) * 0.92, -(z - 0.05), 0.1);
  const m = meshOf((x, y, z) => smax(shell(x, y, z), -open(x, y, z), 0.12), [-2.4, -3.2, -2.2], [2.4, 2.2, 2.2], HOOD_STEP);
  const P = new Float32Array(m.positions.length);
  for (let i = 0; i < P.length; i += 3) P.set(F.toW(m.positions[i], m.positions[i + 1], m.positions[i + 2]), i);
  // (where the shell would be inside the body — its shoulders, its chest — it is cut; what is left is one piece)
  const near = nearestOn(B.rest, P, B.used), keep = [], out = new Uint8Array(P.length / 3);
  for (let v = 0; v < out.length; v++) { const b = near[v]; let d = 0; for (let c = 0; c < 3; c++) d += (P[v * 3 + c] - B.rest[b * 3 + c]) * B.nrm[b * 3 + c]; out[v] = d > 0.008 && P[v * 3 + 1] > B.J('Neck1').y - 0.06 ? 1 : 0; }
  const T = m.triangles; for (let t = 0; t < T.length; t += 3) if (out[T[t]] && out[T[t + 1]] && out[T[t + 2]]) keep.push(T[t], T[t + 1], T[t + 2]);
  const used = [...new Set(keep)], id = new Int32Array(out.length).fill(-1); used.forEach((v, k) => id[v] = k);
  const pos = new Float32Array(used.length * 3); used.forEach((v, k) => pos.set(P.subarray(v * 3, v * 3 + 3), k * 3));
  const tris = Uint32Array.from(keep, v => id[v]);
  // held where it meets the shoulders (sewn to the top it belongs to): its lowest open edge
  return { pos, tris, drawn: true, hold: (p, t) => holdNear(p, t, loops => loops.reduce((a, b) => (b.y < a.y ? b : a)), 0.015, 0.04) };
}
const MADE = {
  blouse: B => bodyShell(B, { keep: torsoKeep, cut: torsoCut(B, { hem: -0.07, sleeve: 0.97, neckR: 0.068, vneck: 0.1 }), ease: (q, w) => 0.014 + 0.014 * w[1] * cuff(B, q) + 0.014 * sst(clamp((q[1] - B.J('Chest').y) / (B.J('Hips').y - 0.07 - B.J('Chest').y), 0, 1)), smooth: 40, hold: 0.6 }),
  cardigan: B => bodyShell(B, { keep: torsoKeep, cut: torsoCut(B, { hem: -0.1, sleeve: 0.95, neckR: 0.07, vneck: 0.2, open: 0.012 }), ease: (q, w) => 0.018 + 0.01 * w[1], smooth: 40, hold: 0.6 }),
  jacket: B => bodyShell(B, { keep: torsoKeep, cut: torsoCut(B, { hem: -0.08, sleeve: 0.96, neckR: 0.075, neckDepth: 0.0, open: 0.01 }), ease: (q, w) => 0.028 + 0.008 * w[1], smooth: 50, hold: 0.6 }),
  swimsuit: B => bodyShell(B, { keep: w => w[1] < 0.5 && w[2] < 0.1 && w[4] < 0.7, cut: swimCut(B), ease: () => 0.0015, smooth: 2, hold: 1 }),
  turtleneck, hood,
  'flared-skirt': B => flaredSkirt(B, { waist: 0.035, hem: -0.07, ease: 0.006, flare: 0.09 }),
  scarf: B => scarf(B, { length: 1.45, width: 0.12 }),
};
