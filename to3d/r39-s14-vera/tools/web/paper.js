// С14 «Вырезанная бумага» in 3D — the paper kit.
// The 2D half is styles/s14-paper/tools/kit.py carried over (ell, strip, crescent, the closed curve with corners):
// outlines in the drawing's units, y down. The 3D half makes PIECES of paper standing in space: an outline laid on a
// surface (patch), a shell (loft, tube), a shell cut by scissors along a curve (clip). A piece is a mesh with one
// colour, a kind of paper and its own number; look.js draws all pieces flat and gives each its edge, rim and shadow.
import * as THREE from 'three';

export const U = 0.003;          // metres in one unit of the drawing's figure (Вера: 590 units tall → 1.77 m)

// ---------------------------------------------------------------- outlines (kit.py)
export const corner = p => [p[0], p[1], 1];
export function ell(cx, cy, rx, ry = rx, rot = 0, n = 10) {
  const c = Math.cos(rot * Math.PI / 180), s = Math.sin(rot * Math.PI / 180), out = [];
  for (let i = 0; i < n; i++) { const a = 2 * Math.PI * i / n, x = rx * Math.cos(a), y = ry * Math.sin(a); out.push([cx + x * c - y * s, cy + x * s + y * c]); }
  return out;
}
export function strip(path, w, round = false) {
  const n = path.length, ws = Array.isArray(w) ? w : path.map(() => w), L = [], R = [];
  path.forEach(([x, y], i) => {
    const [x0, y0] = path[Math.max(i - 1, 0)], [x1, y1] = path[Math.min(i + 1, n - 1)];
    const dx = x1 - x0, dy = y1 - y0, d = Math.hypot(dx, dy) || 1, nx = -dy / d, ny = dx / d, h = ws[i] / 2;
    L.push([x + nx * h, y + ny * h]); R.push([x - nx * h, y - ny * h]);
  });
  if (round) return [...L, ...R.reverse()];
  return [corner(L[0]), ...L.slice(1, -1), corner(L[n - 1]), corner(R[n - 1]), ...R.slice(1, -1).reverse(), corner(R[0])];
}
export function crescent(x0, y0, x1, y1, bend, thick, n = 9) {
  const dx = x1 - x0, dy = y1 - y0, d = Math.hypot(dx, dy) || 1, nx = -dy / d, ny = dx / d, a = [], b = [];
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1), s = Math.sin(Math.PI * t), px = x0 + dx * t, py = y0 + dy * t;
    a.push([px + nx * (bend * s - thick * s / 2), py + ny * (bend * s - thick * s / 2)]);
    b.push([px + nx * (bend * s + thick * s / 2), py + ny * (bend * s + thick * s / 2)]);
  }
  a[0] = corner(a[0]); a[n - 1] = corner(a[n - 1]);
  return [...a, ...b.slice(1, -1).reverse()];
}
// a lens between two curves up(t), lo(t) over x0..x1 (face.py's mouths and lids)
export function lens(x0, x1, y, up, lo, n = 11) {
  const a = [], b = [];
  for (let i = 0; i < n; i++) { const t = i / (n - 1), x = x0 + (x1 - x0) * t; a.push([x, y + up(t)]); b.push([x, y + lo(t)]); }
  return [corner(a[0]), ...a.slice(1, -1), corner(a[n - 1]), ...b.slice(1, -1).reverse()];
}
// the closed curve through the points as kit.path_d draws it; a point [x, y, 1] is a corner. → a dense polygon
export function curve(pts, seg = 5, k = 1) {
  const n = pts.length, out = [];
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n], c1c = !!p1[2], c2c = !!p2[2];
    if (c1c && c2c) { out.push([p1[0], p1[1]]); continue; }
    const c1 = c1c ? p1 : [p1[0] + (p2[0] - p0[0]) / 6 * k, p1[1] + (p2[1] - p0[1]) / 6 * k];
    const c2 = c2c ? p2 : [p2[0] - (p3[0] - p1[0]) / 6 * k, p2[1] - (p3[1] - p1[1]) / 6 * k];
    for (let j = 0; j < seg; j++) {
      const t = j / seg, u = 1 - t, a = u * u * u, b = 3 * u * u * t, c = 3 * u * t * t, d = t * t * t;
      out.push([a * p1[0] + b * c1[0] + c * c2[0] + d * p2[0], a * p1[1] + b * c1[1] + c * c2[1] + d * p2[1]]);
    }
  }
  return out;
}
export const moveP = (pts, dx, dy) => pts.map(p => [p[0] + dx, p[1] + dy, ...p.slice(2)]);
export const scaleP = (pts, s, sy = s) => pts.map(p => [p[0] * s, p[1] * sy, ...p.slice(2)]);
export function rotP(pts, deg, about = [0, 0]) {
  const c = Math.cos(deg * Math.PI / 180), s = Math.sin(deg * Math.PI / 180), [ax, ay] = about;
  return pts.map(p => [ax + (p[0] - ax) * c - (p[1] - ay) * s, ay + (p[0] - ax) * s + (p[1] - ay) * c, ...p.slice(2)]);
}
export const mirrorP = pts => pts.map(p => [-p[0], p[1], ...p.slice(2)]).reverse();

// colours (kit.mix / dark / lite)
const hex = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
export const mix = (c1, c2, t) => { const a = hex(c1), b = hex(c2); return '#' + a.map((v, i) => Math.round(v + (b[i] - v) * t).toString(16).padStart(2, '0')).join(''); };
export const dark = (c, t = .2) => mix(c, '#2b1b2c', t);
export const lite = (c, t = .2) => mix(c, '#fff6e6', t);

// a smooth curve through (x, y) knots, y = f(x): Catmull-Rom, clamped at the ends
export function through(knots) {
  const K = knots.slice().sort((a, b) => a[0] - b[0]);
  return x => {
    if (x <= K[0][0]) return K[0][1];
    if (x >= K[K.length - 1][0]) return K[K.length - 1][1];
    let i = 0; while (x > K[i + 1][0]) i++;
    const p0 = K[Math.max(i - 1, 0)], p1 = K[i], p2 = K[i + 1], p3 = K[Math.min(i + 2, K.length - 1)];
    const t = (x - p1[0]) / (p2[0] - p1[0]), h = p2[0] - p1[0];
    const m1 = (p2[1] - p0[1]) / (p2[0] - p0[0]) * h, m2 = (p3[1] - p1[1]) / (p3[0] - p1[0]) * h;
    const t2 = t * t, t3 = t2 * t;
    return (2 * t3 - 3 * t2 + 1) * p1[1] + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * p2[1] + (t3 - t2) * m2;
  };
}

// ---------------------------------------------------------------- meshes
// a mesh here: {pos: [x, y, z, …] metres, idx: [...], uv: [u, v, …] the paper's own coordinates in units (for brush streaks)}
export const mesh0 = () => ({ pos: [], idx: [], uv: [] });
export function merge(...ms) {
  const o = mesh0();
  for (const m of ms) { const b = o.pos.length / 3; o.pos.push(...m.pos); o.uv.push(...m.uv); for (const i of m.idx) o.idx.push(i + b); }
  return o;
}
export function transform(m, f) {
  const o = { pos: [], idx: m.idx.slice(), uv: m.uv.slice() };
  for (let i = 0; i < m.pos.length; i += 3) o.pos.push(...f([m.pos[i], m.pos[i + 1], m.pos[i + 2]]));
  return o;
}

// an outline (already a dense polygon, or points for curve()) laid on a surface: surf(x, y) → [X, Y, Z].
// Triangulated, then every triangle split until its edges are short, so the piece follows the surface.
export function patch(pts, surf, { holes = [], maxEdge = 7, dense = false, seg = 5 } = {}) {
  const poly = dense ? pts : curve(pts, seg), hs = holes.map(h => dense ? h : curve(h, seg));
  const V2 = p => new THREE.Vector2(p[0], p[1]);
  const all = [...poly, ...hs.flat()];
  let tris = THREE.ShapeUtils.triangulateShape(poly.map(V2), hs.map(h => h.map(V2)));
  const P = all.map(p => [p[0], p[1]]);
  // split the longest edges (shared midpoints: no cracks)
  for (let pass = 0; pass < 6; pass++) {
    const mid = new Map(), next = []; let any = false;
    const M = (a, b) => { const k = a < b ? a * 65536 + b : b * 65536 + a; if (!mid.has(k)) { P.push([(P[a][0] + P[b][0]) / 2, (P[a][1] + P[b][1]) / 2]); mid.set(k, P.length - 1); } return mid.get(k); };
    const long = (a, b) => Math.hypot(P[a][0] - P[b][0], P[a][1] - P[b][1]) > maxEdge;
    const marks = new Set();
    for (const [a, b, c] of tris) for (const [p, q] of [[a, b], [b, c], [c, a]]) if (long(p, q)) marks.add(p < q ? p * 65536 + q : q * 65536 + p);
    if (!marks.size) break;
    const has = (p, q) => marks.has(p < q ? p * 65536 + q : q * 65536 + p);
    for (const [a, b, c] of tris) {
      const e = [has(a, b), has(b, c), has(c, a)], n = e[0] + e[1] + e[2];
      if (!n) { next.push([a, b, c]); continue; }
      any = true;
      if (n === 3) { const ab = M(a, b), bc = M(b, c), ca = M(c, a); next.push([a, ab, ca], [ab, b, bc], [ca, bc, c], [ab, bc, ca]); }
      else if (n === 1) {
        if (e[0]) { const m = M(a, b); next.push([a, m, c], [m, b, c]); }
        else if (e[1]) { const m = M(b, c); next.push([a, b, m], [a, m, c]); }
        else { const m = M(c, a); next.push([a, b, m], [m, b, c]); }
      } else {
        // two edges marked: three triangles
        const [x, y, z] = !e[0] ? [c, a, b] : !e[1] ? [a, b, c] : [b, c, a];   // the edge y–z is whole
        const xy = M(x, y), zx = M(z, x); next.push([x, xy, zx], [xy, y, z], [xy, z, zx]);
      }
    }
    tris = next; if (!any) break;
  }
  const o = mesh0();
  for (const p of P) { o.pos.push(...surf(p[0], p[1])); o.uv.push(p[0], p[1]); }
  for (const t of tris) o.idx.push(t[0], t[1], t[2]);
  return o;
}

// rings of points around (same count each) → a shell; caps close the ends
export function loft(rings, { cap0 = false, cap1 = false, uv = null } = {}) {
  // the paper's own coordinates: along the ring (units, a seam where the ring begins) and down the piece
  const o = mesh0(), m = rings[0].length, M = m + 1;
  let per = 0; for (const r of rings) { let s = 0; for (let k = 0; k < m; k++) s += Math.hypot(r[(k + 1) % m][0] - r[k][0], r[(k + 1) % m][1] - r[k][1], r[(k + 1) % m][2] - r[k][2]); per = Math.max(per, s); }
  let down = 0;
  rings.forEach((r, i) => {
    if (i) down += Math.hypot(r[0][0] - rings[i - 1][0][0], r[0][1] - rings[i - 1][0][1], r[0][2] - rings[i - 1][0][2]);
    for (let k = 0; k <= m; k++) { const p = r[k % m]; o.pos.push(p[0], p[1], p[2]); const t = uv ? uv(i, k, p) : [k / m * per / U, down / U]; o.uv.push(t[0], t[1]); }
  });
  for (let i = 0; i + 1 < rings.length; i++) for (let k = 0; k < m; k++) {
    const a = i * M + k, b = a + 1, c = a + M, d = b + M;
    o.idx.push(a, b, c, b, d, c);
  }
  const cap = (i, flip) => {
    const r = rings[i], c = [0, 0, 0]; r.forEach(p => { c[0] += p[0] / m; c[1] += p[1] / m; c[2] += p[2] / m; });
    const ci = o.pos.length / 3; o.pos.push(...c); o.uv.push(o.uv[i * M * 2], o.uv[i * M * 2 + 1]);
    for (let k = 0; k < m; k++) { const a = i * M + k, b = a + 1; flip ? o.idx.push(ci, b, a) : o.idx.push(ci, a, b); }
  };
  if (cap0) cap(0, true);
  if (cap1) cap(rings.length - 1, false);
  return o;
}

const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], mul = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = a => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
export const V = { sub, add, mul, cross, norm, len: a => Math.hypot(a[0], a[1], a[2]), lerp: (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t] };

// a strip of paper seen from every side: a tube from a to b with round ends (radii ra, rb; flat: depth against width)
export function tube(a, b, ra, rb = ra, { n = 14, flat = 1, ends = 4, side = null } = {}) {
  const ax = norm(sub(b, a)), ref = side || (Math.abs(ax[1]) > .9 ? [0, 0, 1] : [0, 1, 0]);
  const x = norm(cross(ref, ax)), z = cross(ax, x), rings = [], L = V.len(sub(b, a));
  const ring = (c, r) => Array.from({ length: n }, (_, k) => { const t = 2 * Math.PI * k / n; return add(c, add(mul(x, r * Math.cos(t)), mul(z, r * flat * Math.sin(t)))); });
  for (let i = ends; i >= 1; i--) { const t = i / ends * Math.PI / 2; rings.push(ring(add(a, mul(ax, -ra * Math.sin(t) * .9)), ra * Math.cos(t))); }
  const m = 4; for (let i = 0; i <= m; i++) rings.push(ring(add(a, mul(ax, L * i / m)), ra + (rb - ra) * i / m));
  for (let i = 1; i <= ends; i++) { const t = i / ends * Math.PI / 2; rings.push(ring(add(b, mul(ax, rb * Math.sin(t) * .9)), rb * Math.cos(t))); }
  return loft(rings, { cap0: true, cap1: true });
}

// a flat piece with a little thickness: an outline in a plane (o + x·X + y·Y), both faces and the edge
export function slab(pts, place, { thick = .0016, dense = false, holes = [], maxEdge = 40 } = {}) {
  const front = patch(pts, (x, y) => place(x, y, thick / 2), { dense, holes, maxEdge });
  const back = patch(pts, (x, y) => place(x, y, -thick / 2), { dense, holes, maxEdge });
  for (let i = 0; i < back.idx.length; i += 3) { const t = back.idx[i]; back.idx[i] = back.idx[i + 1]; back.idx[i + 1] = t; }
  const o = merge(front, back), poly = dense ? pts : curve(pts);
  const edge = ring => { const b = o.pos.length / 3; ring.forEach(p => { o.pos.push(...place(p[0], p[1], thick / 2), ...place(p[0], p[1], -thick / 2)); o.uv.push(p[0], p[1], p[0], p[1]); }); const n = ring.length; for (let k = 0; k < n; k++) { const a = b + k * 2, c = b + (k + 1) % n * 2; o.idx.push(a, c, a + 1, c, c + 1, a + 1); } };
  edge(poly); holes.forEach(h => edge(dense ? h : curve(h)));
  return o;
}

// scissors: keep the part of a mesh where f(point) > 0; triangles crossing the cut are cut along it
export function clip(m, f) {
  const o = mesh0(), n = m.pos.length / 3, val = new Float64Array(n), map = new Int32Array(n).fill(-1), cuts = new Map();
  const P = i => [m.pos[i * 3], m.pos[i * 3 + 1], m.pos[i * 3 + 2]];
  for (let i = 0; i < n; i++) val[i] = f(P(i));
  const keep = i => { if (map[i] < 0) { map[i] = o.pos.length / 3; o.pos.push(...P(i)); o.uv.push(m.uv[i * 2], m.uv[i * 2 + 1]); } return map[i]; };
  const cut = (a, b) => {                                   // a inside, b outside
    const k = a * 1e6 + b; if (cuts.has(k)) return cuts.get(k);
    // the crossing found by bisection on the true function (a crisp, smooth edge)
    let lo = 0, hi = 1; const pa = P(a), pb = P(b);
    for (let it = 0; it < 14; it++) { const t = (lo + hi) / 2; f(V.lerp(pa, pb, t)) > 0 ? lo = t : hi = t; }
    const t = (lo + hi) / 2, p = V.lerp(pa, pb, t), i = o.pos.length / 3;
    o.pos.push(...p); o.uv.push(m.uv[a * 2] + (m.uv[b * 2] - m.uv[a * 2]) * t, m.uv[a * 2 + 1] + (m.uv[b * 2 + 1] - m.uv[a * 2 + 1]) * t);
    cuts.set(k, i); return i;
  };
  for (let t = 0; t < m.idx.length; t += 3) {
    const T = [m.idx[t], m.idx[t + 1], m.idx[t + 2]], inn = T.map(i => val[i] > 0), c = inn[0] + inn[1] + inn[2];
    if (c === 3) o.idx.push(keep(T[0]), keep(T[1]), keep(T[2]));
    else if (c === 1) { const k = inn.indexOf(true), a = T[k], b = T[(k + 1) % 3], d = T[(k + 2) % 3]; o.idx.push(keep(a), cut(a, b), cut(a, d)); }
    else if (c === 2) { const k = inn.indexOf(false), a = T[k], b = T[(k + 1) % 3], d = T[(k + 2) % 3]; const ib = keep(b), id = keep(d), cb = cut(b, a), cd = cut(d, a); o.idx.push(cb, ib, id, cb, id, cd); }
  }
  return o;
}

// a closed surface of revolution-like shell given by sections: at each height y a ring through (hw(y), front(y), back(y))
// → points (x = hw·cosᵖ, z between back and front); p < 1 squares the ring a little (a flatter front)
export function ringAt(y, hw, zf, zb, n = 32, p = .9) {
  const zc = (zf + zb) / 2, d = (zf - zb) / 2, r = [];
  for (let k = 0; k < n; k++) {
    const t = 2 * Math.PI * k / n, c = Math.cos(t), s = Math.sin(t);
    r.push([hw * Math.sign(c) * Math.abs(c) ** p, y, zc + d * Math.sign(s) * Math.abs(s) ** p]);
  }
  return r;
}
