// What people wear: fabrics with their properties, and garments cut for a body — MakeHuman's (dress, skirt,
// T-shirt, sweater, trousers, shorts), and those made here on the body itself (blouse, cardigan, jacket, swimsuit:
// the skin's region offset by the garment's ease, its hollows bridged, cut clean along hem, neckline, cuffs and the
// open front; the scarf: a strip laid round the neck). Each garment says what holds it on the body.
import { parseGarment, fitted, normalsOf } from './people.js';

// density kg/m²; stretch N/m (how hard it holds against pulling); compress — share of that when pushed together (low:
// it folds); bend — bending rigidity N·m (Kawabata's B, per metre of width); damping 1/s; friction on skin and cloth;
// thick — half its thickness and a little air, m; air — how much the air takes it (1: an ordinary weave)
export const FABRICS = {
  jersey:    { ru: 'хлопковый трикотаж', density: 0.16, stretch: 400, compress: 0.25, bend: 6e-6, damping: 0.4, friction: 0.5, thick: 0.0025, air: 1, sheen: 0.3, rough: 0.85 },
  heavyjersey:{ ru: 'плотный трикотаж (футер)', density: 0.30, stretch: 600, compress: 0.4, bend: 2.2e-5, damping: 0.5, friction: 0.55, thick: 0.0035, air: 1, sheen: 0.4, rough: 0.9 },
  linen:     { ru: 'лён', density: 0.17, stretch: 3000, compress: 0.25, bend: 2e-5, damping: 0.4, friction: 0.5, thick: 0.0025, air: 1, sheen: 0.1, rough: 0.95 },
  poplin:    { ru: 'хлопок-поплин', density: 0.12, stretch: 4000, compress: 0.25, bend: 1.2e-5, damping: 0.35, friction: 0.4, thick: 0.0022, air: 1, sheen: 0.1, rough: 0.8 },
  silk:      { ru: 'шёлк', density: 0.07, stretch: 2500, compress: 0.25, bend: 2e-6, damping: 0.25, friction: 0.2, thick: 0.0018, air: 1, sheen: 0.9, rough: 0.35 },
  chiffon:   { ru: 'шифон', density: 0.04, stretch: 1500, compress: 0.25, bend: 6e-7, damping: 0.25, friction: 0.25, thick: 0.0015, air: 1, sheen: 0.5, rough: 0.6, opacity: 0.86 },
  woolknit:  { ru: 'толстая шерстяная вязка', density: 0.45, stretch: 250, compress: 0.75, bend: 4e-5, damping: 0.8, friction: 0.7, thick: 0.0055, air: 0.8, sheen: 0.6, rough: 1 },
  fineknit:  { ru: 'тонкая вязка (мерино)', density: 0.22, stretch: 300, compress: 0.5, bend: 8e-6, damping: 0.6, friction: 0.6, thick: 0.003, air: 1, sheen: 0.5, rough: 0.95 },
  fleece:    { ru: 'флис', density: 0.28, stretch: 500, compress: 0.6, bend: 2e-5, damping: 0.7, friction: 0.7, thick: 0.0045, air: 0.9, sheen: 0.8, rough: 1 },
  denim:     { ru: 'деним', density: 0.40, stretch: 6000, compress: 0.25, bend: 1.2e-4, damping: 0.5, friction: 0.55, thick: 0.0035, air: 1, sheen: 0.1, rough: 0.9 },
  twill:     { ru: 'хлопковый твил', density: 0.25, stretch: 5000, compress: 0.25, bend: 5e-5, damping: 0.5, friction: 0.5, thick: 0.003, air: 1, sheen: 0.1, rough: 0.85 },
  suiting:   { ru: 'костюмная шерсть', density: 0.26, stretch: 4000, compress: 0.25, bend: 3e-5, damping: 0.5, friction: 0.55, thick: 0.003, air: 1, sheen: 0.2, rough: 0.75 },
  tweed:     { ru: 'твид', density: 0.45, stretch: 4000, compress: 0.3, bend: 1.5e-4, damping: 0.6, friction: 0.65, thick: 0.0045, air: 1, sheen: 0.3, rough: 1 },
  nylon:     { ru: 'нейлон (ветровка)', density: 0.08, stretch: 6000, compress: 0.25, bend: 1.5e-5, damping: 0.3, friction: 0.3, thick: 0.002, air: 1, sheen: 0.3, rough: 0.45 },
  lycra:     { ru: 'бифлекс (нейлон с лайкрой)', density: 0.19, stretch: 60, compress: 0.3, bend: 4e-6, damping: 0.8, friction: 0.6, thick: 0.0015, air: 1, sheen: 0.4, rough: 0.4 },
  neoprene:  { ru: 'неопрен', density: 0.9, stretch: 150, compress: 0.5, bend: 2e-4, damping: 1.0, friction: 0.7, thick: 0.0035, air: 1, sheen: 0.1, rough: 0.6 },
};

// ———— meshes ————
export function edgesOf(tris) {
  const m = new Map();
  for (let t = 0; t < tris.length; t += 3) for (let k = 0; k < 3; k++) {
    const a = tris[t + k], b = tris[t + (k + 1) % 3], key = a < b ? a + ',' + b : b + ',' + a;
    m.set(key, (m.get(key) || 0) + 1);
  }
  return m;
}
// Loop subdivision: each triangle in four, the points moved toward the smooth surface (boundaries and seams kept as
// curves of their own)
export function subdivide(pos, tris) {
  const n = pos.length / 3, E = edgesOf(tris), mid = new Map(), opp = new Map();
  for (let t = 0; t < tris.length; t += 3) for (let k = 0; k < 3; k++) {
    const a = tris[t + k], b = tris[t + (k + 1) % 3], c = tris[t + (k + 2) % 3], key = a < b ? a + ',' + b : b + ',' + a;
    (opp.get(key) || opp.set(key, []).get(key)).push(c);
  }
  const out = [];
  for (let i = 0; i < n * 3; i++) out.push(0);
  const nb = Array.from({ length: n }, () => new Set()), bnb = Array.from({ length: n }, () => new Set());
  for (const [key, c] of E) { const [a, b] = key.split(',').map(Number); nb[a].add(b); nb[b].add(a); if (c !== 2) { bnb[a].add(b); bnb[b].add(a); } }
  for (let i = 0; i < n; i++) {
    if (bnb[i].size >= 2) {
      if (bnb[i].size === 2) { const [a, b] = [...bnb[i]]; for (let c = 0; c < 3; c++) out[i * 3 + c] = 0.75 * pos[i * 3 + c] + 0.125 * (pos[a * 3 + c] + pos[b * 3 + c]); }
      else for (let c = 0; c < 3; c++) out[i * 3 + c] = pos[i * 3 + c];
      continue;
    }
    const k = nb[i].size, beta = k === 3 ? 3 / 16 : 3 / (8 * k);
    for (let c = 0; c < 3; c++) { let s = 0; for (const j of nb[i]) s += pos[j * 3 + c]; out[i * 3 + c] = (1 - k * beta) * pos[i * 3 + c] + beta * s; }
  }
  for (const [key, c] of E) {
    const [a, b] = key.split(',').map(Number), o = opp.get(key), id = out.length / 3;
    for (let q = 0; q < 3; q++) out.push(c === 2 ? 0.375 * (pos[a * 3 + q] + pos[b * 3 + q]) + 0.125 * (pos[o[0] * 3 + q] + pos[o[1] * 3 + q]) : 0.5 * (pos[a * 3 + q] + pos[b * 3 + q]));
    mid.set(key, id);
  }
  const T = [], M = (a, b) => mid.get(a < b ? a + ',' + b : b + ',' + a);
  for (let t = 0; t < tris.length; t += 3) {
    const a = tris[t], b = tris[t + 1], c = tris[t + 2], ab = M(a, b), bc = M(b, c), ca = M(c, a);
    T.push(a, ab, ca, ab, b, bc, ca, bc, c, ab, bc, ca);
  }
  return { pos: Float32Array.from(out), tris: Uint32Array.from(T) };
}
// the open edges, as loops of points
export function boundaryLoops(tris) {
  const E = edgesOf(tris), adj = new Map();
  for (const [key, c] of E) if (c === 1) { const [a, b] = key.split(',').map(Number); (adj.get(a) || adj.set(a, []).get(a)).push(b); (adj.get(b) || adj.set(b, []).get(b)).push(a); }
  const seen = new Set(), loops = [];
  for (const s of adj.keys()) { if (seen.has(s)) continue; const L = [], st = [s]; while (st.length) { const v = st.pop(); if (seen.has(v)) continue; seen.add(v); L.push(v); for (const u of adj.get(v)) st.push(u); } loops.push(L); }
  return loops;
}
// distance along the cloth from a set of points
export function along(pos, tris, from) {
  const n = pos.length / 3, d = new Float64Array(n).fill(Infinity), adj = Array.from({ length: n }, () => []);
  for (const key of edgesOf(tris).keys()) { const [a, b] = key.split(',').map(Number), l = Math.hypot(pos[a * 3] - pos[b * 3], pos[a * 3 + 1] - pos[b * 3 + 1], pos[a * 3 + 2] - pos[b * 3 + 2]); adj[a].push(b, l); adj[b].push(a, l); }
  let front = [...from]; for (const i of from) d[i] = 0;
  // a few relaxation sweeps (the meshes are small, the distances short)
  while (front.length) { const next = new Set(); for (const i of front) { const a = adj[i]; for (let k = 0; k < a.length; k += 2) { const j = a[k], v = d[i] + a[k + 1]; if (v < d[j] - 1e-9) { d[j] = v; next.add(j); } } } front = [...next]; }
  return d;
}
const loopStat = (pos, L) => { let x = 0, y = 0, z = 0, ax = 0; for (const v of L) { x += pos[v * 3]; y += pos[v * 3 + 1]; z += pos[v * 3 + 2]; ax += Math.abs(pos[v * 3]); } const k = L.length; return { x: x / k, y: y / k, z: z / k, ax: ax / k, n: k }; };

// ———— a garment made on the body: the skin's region, offset by the ease ————
// spec: { cut(p, w) → ≥ 0 inside (p rest position, w per-group weights), ease(p, w) → m, smooth: iterations }
function bodyGroups(body) {
  const N = body.N, names = body.names, G = new Float32Array(N * 5); // torso, arm, hand, leg, head
  const group = names.map(n => /Hand|Thumb|Index|Middle|Ring|Pinky/.test(n) ? 2 : /Arm|ForeArm/.test(n) ? 1 : /Leg|Shin|Foot|Toe/.test(n) ? 3 : /Neck|Head|Jaw|Eye/.test(n) ? 4 : 0);
  for (let i = 0; i < N; i++) for (let k = 0; k < 4; k++) G[i * 5 + group[body.joint[i * 4 + k]]] += body.weight[i * 4 + k] / 255;
  return G;
}
export function bodyShell(body, spec) {
  const N = body.N, R = body.rest, NR = body.nrm, G = bodyGroups(body), w = i => G.subarray(i * 5, i * 5 + 5);
  const P = Float32Array.from(R), p = i => [P[i * 3], P[i * 3 + 1], P[i * 3 + 2]];
  const phi = q => spec.cut(q);
  // the points nearest the cut lines moved onto them, so the hem, cuffs and neckline are clean curves
  const T = body.tris, val = new Float32Array(N);
  for (let i = 0; i < N; i++) val[i] = spec.keep(w(i)) ? phi(p(i)) : -1;
  const moved = new Uint8Array(N);
  for (let t = 0; t < T.length; t += 3) for (let k = 0; k < 3; k++) {
    const a = T[t + k], b = T[t + (k + 1) % 3];
    if ((val[a] >= 0) === (val[b] >= 0) || val[a] === -1 || val[b] === -1) continue;
    const i = Math.abs(val[a]) < Math.abs(val[b]) ? a : b; if (moved[i]) continue;
    // along the edge to where the cut crosses it
    const j = i === a ? b : a, s = val[i] / (val[i] - val[j]);
    if (s > 0.5) continue;
    for (let c = 0; c < 3; c++) P[i * 3 + c] += (R[j * 3 + c] - R[i * 3 + c]) * s;
    val[i] = 0; moved[i] = 1;
  }
  const tris = [];
  for (let t = 0; t < T.length; t += 3) if (val[T[t]] >= 0 && val[T[t + 1]] >= 0 && val[T[t + 2]] >= 0) tris.push(T[t], T[t + 1], T[t + 2]);
  // the largest piece (or pieces, if asked: two sleeves are one garment with the torso)
  const used = [...new Set(tris)], id = new Int32Array(N).fill(-1); used.forEach((v, k) => id[v] = k);
  const tr = Uint32Array.from(tris, v => id[v]), n = used.length;
  const parent = Int32Array.from({ length: n }, (_, i) => i), find = i => { while (parent[i] !== i) i = parent[i] = parent[parent[i]]; return i; };
  for (let t = 0; t < tr.length; t += 3) { const a = find(tr[t]), b = find(tr[t + 1]), c = find(tr[t + 2]); parent[b] = a; parent[find(c)] = a; }
  const size = new Map(); for (let i = 0; i < n; i++) { const r = find(i); size.set(r, (size.get(r) || 0) + 1); }
  const keep = new Set([...size].filter(([, s]) => s >= (spec.minPiece ?? 200)).map(([r]) => r));
  const t2 = []; for (let t = 0; t < tr.length; t += 3) if (keep.has(find(tr[t]))) t2.push(tr[t], tr[t + 1], tr[t + 2]);
  const used2 = [...new Set(t2)], id2 = new Int32Array(n).fill(-1); used2.forEach((v, k) => id2[v] = k);
  const tris3 = Uint32Array.from(t2, v => id2[v]), src = Int32Array.from(used2, v => used[v]), m = src.length;
  // offset by the ease, then smoothed: the cloth bridges the hollows; never nearer the skin than its ease allows
  const X = new Float32Array(m * 3), want = new Float32Array(m);
  for (let k = 0; k < m; k++) { const i = src[k], q = p(i); want[k] = spec.ease(q, w(i)); for (let c = 0; c < 3; c++) X[k * 3 + c] = P[i * 3 + c] + NR[i * 3 + c] * want[k]; }
  const E = edgesOf(tris3), nb = Array.from({ length: m }, () => []), bnb = Array.from({ length: m }, () => []);
  for (const [key, c] of E) { const [a, b] = key.split(',').map(Number); nb[a].push(b); nb[b].push(a); if (c === 1) { bnb[a].push(b); bnb[b].push(a); } }
  const Y = new Float32Array(m * 3);
  for (let it = 0; it < (spec.smooth ?? 12); it++) {
    for (let k = 0; k < m; k++) {
      const L = bnb[k].length ? bnb[k] : nb[k];
      for (let c = 0; c < 3; c++) { let s = 0; for (const j of L) s += X[j * 3 + c]; Y[k * 3 + c] = X[k * 3 + c] * 0.4 + 0.6 * s / L.length; }
    }
    for (let k = 0; k < m; k++) {
      const i = src[k]; let d = 0; for (let c = 0; c < 3; c++) d += (Y[k * 3 + c] - P[i * 3 + c]) * NR[i * 3 + c];
      const lo = want[k] * (spec.hold ?? 0.75); if (d < lo) for (let c = 0; c < 3; c++) Y[k * 3 + c] += NR[i * 3 + c] * (lo - d);
    }
    X.set(Y);
  }
  return { pos: X, tris: tris3, src };
}

// the body's outline across, at a height: for each of K directions round the centre, how far out the skin reaches
// (arms and hands left out) — what a skirt must clear
function hull(body, y, band, K, cz) {
  const G = bodyGroups(body), R = new Float32Array(K), P = body.rest;
  for (let i = 0; i < body.N; i++) {
    if (Math.abs(P[i * 3 + 1] - y) > band || G[i * 5 + 1] + G[i * 5 + 2] > 0.3) continue;
    const x = P[i * 3], z = P[i * 3 + 2] - cz, a = Math.atan2(x, z), k = ((Math.round(a / (2 * Math.PI) * K) % K) + K) % K, r = Math.hypot(x, z);
    if (r > R[k]) R[k] = r;
  }
  // gaps filled from the neighbours, then smoothed round
  for (let it = 0; it < K; it++) for (let k = 0; k < K; k++) if (!R[k]) R[k] = Math.max(R[(k + 1) % K], R[(k + K - 1) % K]);
  const S = new Float32Array(K);
  for (let k = 0; k < K; k++) { let m = 0; for (let d = -2; d <= 2; d++) m = Math.max(m, R[(k + d + K) % K]); S[k] = m; }
  return S;
}
// a skirt: a tube of cloth from the waist down, clearing the hips and legs, widening to the hem by its flare; each
// ring as many points as its girth takes (about 1.2 cm apart), neighbouring rings zipped together
function skirt(body, o) {
  const s = body.height / 1.6, hips = J(body, 'Hips'), knee = J(body, 'LeftShin');
  const top = hips.y + o.waist * s, bottom = knee.y + o.hem * s, cz = hips.z, K = 180, step = 0.012;
  const rows = Math.round((top - bottom) / step), radii = [];
  let r = null;
  for (let i = 0; i <= rows; i++) {
    const u = i / rows, y = top - (top - bottom) * u, H = hull(body, y, 0.012, K, cz);
    if (!r) r = Float32Array.from(H, v => v + 0.004);
    else for (let k = 0; k < K; k++) r[k] = Math.max(r[k], H[k] + o.ease);
    radii.push(Float32Array.from(r, v => v + o.flare * s * Math.pow(Math.max(0, (u - 0.15) / 0.85), 1.3)));
  }
  // smoothed down the length and round, so the cloth's own shape has no steps
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
    const A = start[i], na = count[i], B = start[i + 1], nb = count[i + 1];
    let a = 0, b = 0;
    while (a < na || b < nb) {
      const ta = (a + 1) / na, tb = (b + 1) / nb;
      if (b >= nb || (a < na && ta <= tb)) { tris.push(A + a % na, B + b % nb, A + (a + 1) % na); a++; }
      else { tris.push(A + a % na, B + b % nb, B + (b + 1) % nb); b++; }
    }
  }
  return { pos: Float32Array.from(pos), tris: Uint32Array.from(tris), subdivide: 0 };
}

// ———— the scarf: a strip of cloth laid round the back of the neck, its two ends down the front ————
function scarf(body, o) {
  const neck = J(body, 'Neck1'), s = body.height / 1.6, G = bodyGroups(body), P = body.rest;
  const L = o.length * s, W = o.width * s, du = 0.012, nv = Math.max(6, Math.round(W / du));
  // the neck's girth at its base, read off the skin
  const ds = []; for (let i = 0; i < body.N; i++) { const y = P[i * 3 + 1]; if (Math.abs(y - (neck.y + 0.015)) < 0.012 && G[i * 5 + 4] > 0.5) ds.push(Math.hypot(P[i * 3], P[i * 3 + 2] - neck.z)); }
  ds.sort((a, b) => a - b); const r = ds[Math.floor(ds.length * 0.8)] || 0.06 * s;
  const R = r + 0.022 * s, y0 = neck.y - 0.015 * s, a0 = 0.32 * Math.PI, a1 = 1.68 * Math.PI, ring = R * (a1 - a0), hang = (L - ring) / 2;
  // how far forward the front of the body is at a height, near x
  const front = (x, y) => { let z = -1; for (let i = 0; i < body.N; i++) if (Math.abs(P[i * 3 + 1] - y) < 0.015 && Math.abs(P[i * 3] - x) < 0.03 && G[i * 5 + 1] + G[i * 5 + 2] < 0.3) z = Math.max(z, P[i * 3 + 2]); return z; };
  const centre = [], across = [];
  const nu = Math.round(L / du);
  for (let i = 0; i <= nu; i++) {
    const u = i / nu * L;
    if (u < hang || u > L - hang) {
      const side = u < hang ? 1 : -1, k = u < hang ? hang - u : u - (L - hang), a = side > 0 ? a0 : a1;
      // each end hangs on its own side of the chest, the two not overlapping
      const xs = Math.sin(a) * R, xe = side * Math.max(Math.abs(xs), W / 2 + 0.008 * s), x = xs + (xe - xs) * Math.min(1, k / 0.06), y = y0 - k, z0 = neck.z + Math.cos(a) * R, z = Math.max(z0, front(x, y) + 0.012 * s);
      centre.push([x, y, k < 0.04 ? z0 + (z - z0) * k / 0.04 : z]);
      across.push([side, 0, 0]);
    } else {
      const a = a0 + (u - hang) / ring * (a1 - a0), ox = Math.sin(a), oz = Math.cos(a);
      centre.push([ox * R, y0, neck.z + oz * R]);
      // round the neck the strip lies on the shoulders: across it goes outward and down
      across.push([ox * 0.75, -0.66, oz * 0.75]);
    }
  }
  const pos = [], flat = [];
  for (let i = 0; i <= nu; i++) for (let j = 0; j <= nv; j++) {
    const v = j / nv - 0.5, c = centre[i], d = across[i];
    flat.push(i / nu * L, 0, v * W);
    // round the neck the strip starts at the neck and goes out over the shoulders; down the front it lies flat
    const off = d[1] ? (v + 0.5) * W * 0.8 : v * W;
    pos.push(c[0] + d[0] * off, c[1] + d[1] * off, c[2] + d[2] * off);
  }
  const tris = [];
  // (wound so the face away from the body is the front)
  for (let i = 0; i < nu; i++) for (let j = 0; j < nv; j++) { const a = i * (nv + 1) + j, b = a + 1, c = a + nv + 1, d = c + 1; tris.push(a, b, c, b, d, c); }
  return { pos: Float32Array.from(pos), flat: Float32Array.from(flat), tris: Uint32Array.from(tris), rows: nu + 1, cols: nv + 1, hang, L };
}

// ———— the garments ————
const J = (body, n) => body.J[body.names.indexOf(n)];
const smooth01 = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
// a garment's hold: 1 near the loop (`which` picks it), falling off along the cloth
function holdNear(pos, tris, which, near, far) {
  const loops = boundaryLoops(tris).map(L => ({ L, ...loopStat(pos, L) }));
  const L = which(loops); const d = along(pos, tris, L ? L.L : []);
  return Float32Array.from(d, v => 1 - smooth01(near, far, v));
}
const topLoop = loops => loops.reduce((a, b) => (b.y - b.ax > a.y - a.ax ? b : a));
// a long-sleeved top: held at the neckline, and lightly at the cuffs (a buttoned or ribbed cuff grips the wrist; the
// hand, too thin a solid for the cloth where the fingers are, would otherwise let it slip over)
function topHold(pos, tris) {
  const neck = holdNear(pos, tris, neckLoop, 0.02, 0.05);
  const loops = boundaryLoops(tris).map(L => ({ L, ...loopStat(pos, L) })), far = loops.reduce((m, l) => Math.max(m, l.ax), 0);
  const cuffs = loops.filter(l => l.ax > far * 0.8 && l.ax > 0.2).flatMap(l => l.L), d = along(pos, tris, cuffs);
  return Float32Array.from(neck, (v, i) => Math.max(v, 0.5 * (1 - smooth01(0.01, 0.03, d[i]))));
}
const neckLoop = loops => loops.filter(l => l.ax < 0.09).reduce((a, b) => (b.y > a.y ? b : a));

// The cut shapes of the garments made on the body (rest pose, metres; the body's joints place them).
function torsoCut(body, o) {
  const sh = J(body, 'LeftArm'), hips = J(body, 'Hips'), neck = J(body, 'Neck1'), hand = J(body, 'LeftHand'), s = body.height / 1.6;
  const zc = neck.z, hemY = hips.y + o.hem * s, ax = [hand.x - sh.x, hand.y - sh.y, hand.z - sh.z], al = Math.hypot(...ax);
  const u = ax.map(v => v / al);
  return q => {
    const [x, y, z] = q, X = Math.abs(x);
    let f = y - hemY;                                                               // the hem
    const r = Math.hypot(x, (z - zc) * 1.15);                                       // the neckline
    f = Math.min(f, Math.max(r - (o.neckR ?? 0.07) * s, (neck.y - (o.neckDepth ?? 0.03) * s) - y));
    if (o.vneck && z > zc + 0.02) f = Math.min(f, (neck.y - o.vneck * s + X * 2.2) - y);
    if (o.open && z > zc + 0.03 && y < neck.y + 0.05) f = Math.min(f, X - o.open * s);
    if (X > sh.x * 0.9) { const t = (X - sh.x) * u[0] + (y - sh.y) * u[1] + (z - sh.z) * u[2]; f = Math.min(f, o.sleeve * al - t); }
    return f;
  };
}
const torsoKeep = w => w[2] < 0.3 && w[4] < 0.5 && w[3] < 0.6;

export const GARMENTS = {
  dress: { ru: 'платье', layer: 1, make: (b, d) => mh(b, d), hold: (pos, tris, b) => { const sh = J(b, 'LeftArm').y, sp = J(b, 'Spine2').y; return Float32Array.from({ length: pos.length / 3 }, (_, i) => { const y = pos[i * 3 + 1]; return y > sh + 0.02 ? 1 : y > sp ? 0.25 * smooth01(sp, sp + 0.08, y) : 0; }); }, fabrics: ['poplin', 'silk', 'chiffon', 'jersey'], self: true },
  skirt: { ru: 'юбка', layer: 0, make: b => skirt(b, { waist: 0.035, hem: -0.07, ease: 0.006, flare: 0.09 }), hold: (pos, tris) => holdNear(pos, tris, topLoop, 0.02, 0.045), fabrics: ['suiting', 'chiffon', 'denim'], self: true },
  tshirt: { ru: 'футболка', layer: 1, make: (b, d) => mh(b, d), hold: (pos, tris) => holdNear(pos, tris, neckLoop, 0.02, 0.05), fabrics: ['jersey', 'heavyjersey', 'linen'], tubes: true },
  sweater: { ru: 'свитер', layer: 1, make: (b, d) => mh(b, d), hold: topHold, fabrics: ['woolknit', 'fineknit', 'fleece'], tubes: true },
  pants: { ru: 'брюки', layer: 0, make: (b, d) => mh(b, d), hold: (pos, tris) => holdNear(pos, tris, topLoop, 0.025, 0.05), fabrics: ['denim', 'suiting', 'twill', 'linen'], tubes: true, self: true },
  shorts: { ru: 'шорты', layer: 0, make: (b, d) => mh(b, d), hold: (pos, tris) => holdNear(pos, tris, topLoop, 0.02, 0.045), fabrics: ['denim', 'twill', 'nylon'], tubes: true },
  blouse: { ru: 'блузка', layer: 1, make: b => made(b, bodyShell(b, { keep: torsoKeep, cut: torsoCut(b, { hem: -0.07, sleeve: 0.97, neckR: 0.068, vneck: 0.1 }), ease: (q, w) => 0.014 + 0.014 * w[1] * cuff(b, q) + 0.014 * smooth01(J(b, 'Chest').y, J(b, 'Hips').y - 0.07, q[1]), smooth: 40, hold: 0.6 })), hold: topHold, fabrics: ['silk', 'chiffon', 'poplin'], tubes: true },
  cardigan: { ru: 'кардиган', layer: 2, make: b => made(b, bodyShell(b, { keep: torsoKeep, cut: torsoCut(b, { hem: -0.1, sleeve: 0.95, neckR: 0.07, vneck: 0.2, open: 0.012 }), ease: (q, w) => 0.018 + 0.01 * w[1], smooth: 40, hold: 0.6 })), hold: topHold, fabrics: ['woolknit', 'fineknit'], tubes: true },
  jacket: { ru: 'куртка', layer: 2, make: b => made(b, bodyShell(b, { keep: torsoKeep, cut: torsoCut(b, { hem: -0.08, sleeve: 0.96, neckR: 0.075, neckDepth: 0.0, open: 0.01 }), ease: (q, w) => 0.028 + 0.008 * w[1], smooth: 50, hold: 0.6 })), hold: topHold, fabrics: ['denim', 'tweed', 'nylon'], tubes: true },
  swimsuit: { ru: 'купальник', layer: 0, tight: 0.94, make: b => made(b, bodyShell(b, { keep: w => w[1] < 0.5 && w[2] < 0.1 && w[4] < 0.7, cut: swimCut(b), ease: () => 0.0015, smooth: 2, hold: 1 })), hold: (pos, tris) => { const L = boundaryLoops(tris).flat(); const d = along(pos, tris, L); return Float32Array.from(d, v => 0.5 * (1 - smooth01(0.008, 0.02, v)) + 0.15); }, fabrics: ['lycra', 'neoprene'] },
  scarf: { ru: 'шарф', layer: 3, make: b => scarfGarment(b), hold: (pos, tris, b, g) => g.hold, fabrics: ['woolknit', 'silk', 'chiffon'], self: true },
};

// a buttoned cuff: the sleeve's fullness gathered into it over the last centimetres before the wrist (0 at the wrist)
function cuff(body, q) {
  const h = J(body, q[0] > 0 ? 'LeftHand' : 'RightHand'), d = Math.hypot(q[0] - h.x, q[1] - h.y, q[2] - h.z);
  return smooth01(0.05, 0.13, d) * 0.85 + 0.15;
}
function swimCut(body) {
  const hips = J(body, 'Hips'), leg = J(body, 'LeftLeg'), chest = J(body, 'Chest'), arm = J(body, 'LeftArm'), neck = J(body, 'Neck1'), s = body.height / 1.6;
  const crotch = leg.y - 0.075 * s, top = chest.y + 0.09 * s, zc = hips.z;
  return ([x, y, z]) => {
    const X = Math.abs(x);
    let f = y - (crotch + Math.max(0, X - 0.035 * s) * 1.25);          // the leg openings, cut high over the hips
    let up = top - y;                                                    // the top edge over the bust and across the back
    if (z < zc) up = top - 0.05 * s - y;
    const strap = Math.min(0.017 * s - Math.abs(X - 0.07 * s), neck.y + 0.06 - y);   // straps over the shoulders
    up = Math.max(up, strap);
    return Math.min(f, up);
  };
}

function mh(body, buf) { const g = parseGarment(buf); return { pos: fitted(g, body.rest), tris: Uint32Array.from(g.tris), subdivide: 1 }; }
function made(body, sh, k = 1) { return { pos: sh.pos, tris: sh.tris, subdivide: k }; }
function scarfGarment(body) {
  const S = scarf(body, { length: 1.45, width: 0.12 });
  const hold = new Float32Array(S.pos.length / 3);
  for (let i = 0; i < S.rows; i++) { const u = i / (S.rows - 1) * S.L, mid = Math.abs(u - S.L / 2) / (S.L / 2 - S.hang); for (let j = 0; j < S.cols; j++) hold[i * S.cols + j] = mid < 0.5 ? 0.35 : 0; }
  return { pos: S.pos, flat: S.flat, tris: S.tris, subdivide: 0, hold };
}

// ———— a garment cut for a body: its rest shape, triangles, hold and skin (to carry what it holds) ————
export function cut(body, name, data) {
  const G = GARMENTS[name], g = G.make(body, data);
  let pos = g.pos, tris = g.tris;
  for (let k = 0; k < g.subdivide; k++) ({ pos, tris } = subdivide(pos, tris));
  const hold = G.hold(pos, tris, body, g);
  // each point skinned as the nearest skin is
  const n = pos.length / 3, skinJ = new Uint8Array(n * 4), skinW = new Uint8Array(n * 4), near = nearestOn(body.rest, pos);
  for (let i = 0; i < n; i++) for (let k = 0; k < 4; k++) { skinJ[i * 4 + k] = body.joint[near[i] * 4 + k]; skinW[i * 4 + k] = body.weight[near[i] * 4 + k]; }
  // which way is out: away from the body; the triangles turned to face out (the inside of a garment is its back)
  const outward = () => { const nrm = normalsOf(pos, tris), sgn = new Float32Array(n); for (let i = 0; i < n; i++) { const b = near[i]; let d = 0; for (let c = 0; c < 3; c++) d += nrm[i * 3 + c] * (body.nrm[b * 3 + c]); sgn[i] = d >= 0 ? 1 : -1; } return sgn; };
  // (the whole garment at once: its triangles agree with each other, and most of them face away from the body)
  let sgn = outward(), out = 0;
  tris = Uint32Array.from(tris);
  for (let t = 0; t < tris.length; t += 3) out += sgn[tris[t]] + sgn[tris[t + 1]] + sgn[tris[t + 2]];
  if (out < 0 && !g.flat) for (let t = 0; t < tris.length; t += 3) { const b = tris[t + 1]; tris[t + 1] = tris[t + 2]; tris[t + 2] = b; }
  sgn = new Float32Array(n).fill(1);
  // (a garment laid on as cut flat — the scarf — keeps the lengths it has flat, whatever shape it was laid on in)
  return { name, pos, flat: g.flat || null, tris, hold, skinJ, skinW, sgn, near, layer: G.layer, tight: G.tight ?? 1, self: !!G.self, tubes: !!G.tubes };
}
export function nearestOn(P, Q) {
  const cell = 0.03, grid = new Map(), key = (x, y, z) => x + ',' + y + ',' + z, N = P.length / 3, out = new Int32Array(Q.length / 3);
  for (let i = 0; i < N; i++) { const k = key(Math.floor(P[i * 3] / cell), Math.floor(P[i * 3 + 1] / cell), Math.floor(P[i * 3 + 2] / cell)); (grid.get(k) || grid.set(k, []).get(k)).push(i); }
  for (let q = 0; q < out.length; q++) {
    const x = Q[q * 3], y = Q[q * 3 + 1], z = Q[q * 3 + 2], cx = Math.floor(x / cell), cy = Math.floor(y / cell), cz = Math.floor(z / cell);
    let best = -1, bd = Infinity;
    for (let r = 0; r < 12 && best < 0; r++) for (let dx = -r; dx <= r; dx++) for (let dy = -r; dy <= r; dy++) for (let dz = -r; dz <= r; dz++) {
      if (Math.max(Math.abs(dx), Math.abs(dy), Math.abs(dz)) !== r) continue;
      const a = grid.get(key(cx + dx, cy + dy, cz + dz)); if (!a) continue;
      for (const i of a) { const d = (P[i * 3] - x) ** 2 + (P[i * 3 + 1] - y) ** 2 + (P[i * 3 + 2] - z) ** 2; if (d < bd) { bd = d; best = i; } }
    }
    out[q] = best < 0 ? 0 : best;
  }
  return out;
}
