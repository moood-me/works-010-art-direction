// Shapes by distance, and a mesh of a shape: what designed heads, their pieces (a long nose, a ball nose, a hood) and
// the overlay check are made of. Plain functions of a point (x, y, z), in whatever units the caller uses (heads: head
// units, src/head/frame.js). From Г1's heads (experiments/heads-anime), unchanged in what they give.
import { smin, clamp, lerp } from '../math.js';

export const smax = (a, b, k) => -smin(-a, -b, k);
export const sdSphere = (x, y, z, r) => Math.hypot(x, y, z) - r;
// an ellipsoid's distance, its usual bound (Quilez)
export function sdEll(x, y, z, a, b, c) { const k0 = Math.hypot(x / a, y / b, z / c), k1 = Math.hypot(x / (a * a), y / (b * b), z / (c * c)); return k1 < 1e-9 ? -Math.min(a, b, c) : k0 * (k0 - 1) / k1; }
// a capsule from a to b, its radius r (a number, or [at a, at b])
export function sdCapsule(x, y, z, a, b, r) {
  const px = x - a[0], py = y - a[1], pz = z - a[2], bx = b[0] - a[0], by = b[1] - a[1], bz = b[2] - a[2];
  const h = clamp((px * bx + py * by + pz * bz) / (bx * bx + by * by + bz * bz), 0, 1);
  return Math.hypot(px - bx * h, py - by * h, pz - bz * h) - (typeof r === 'number' ? r : lerp(r[0], r[1], h));
}
// the unsigned distance to a triangle
export function udTriangle(px, py, pz, a, b, c) {
  const v = (p, q) => [p[0] - q[0], p[1] - q[1], p[2] - q[2]], dot = (p, q) => p[0] * q[0] + p[1] * q[1] + p[2] * q[2], cross = (p, q) => [p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0]];
  const P = [px, py, pz], ba = v(b, a), pa = v(P, a), cb = v(c, b), pb = v(P, b), ac = v(a, c), pc = v(P, c), nor = cross(ba, ac);
  const sgn = Math.sign(dot(cross(ba, nor), pa)) + Math.sign(dot(cross(cb, nor), pb)) + Math.sign(dot(cross(ac, nor), pc));
  const seg = (e, p) => { const h = clamp(dot(e, p) / dot(e, e), 0, 1), d = [e[0] * h - p[0], e[1] * h - p[1], e[2] * h - p[2]]; return dot(d, d); };
  return Math.sqrt(sgn < 2 ? Math.min(seg(ba, pa), seg(cb, pb), seg(ac, pc)) : dot(nor, pa) * dot(nor, pa) / dot(nor, nor));
}
// a Catmull–Rom curve through 2D points, n points a span
export function catmull(pts, n = 8) {
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
    for (let k = 0; k < n; k++) { const t = k / n, t2 = t * t, t3 = t2 * t; out.push([0, 1].map(c => 0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3))); }
  }
  out.push(pts[pts.length - 1]);
  return out;
}
// the signed distance to a closed polygon in the (y, z) plane
export function sdPoly2(py, pz, V) {
  let d = (py - V[0][0]) ** 2 + (pz - V[0][1]) ** 2, s = 1;
  for (let i = 0, j = V.length - 1; i < V.length; j = i, i++) {
    const ey = V[j][0] - V[i][0], ez = V[j][1] - V[i][1], wy = py - V[i][0], wz = pz - V[i][1], h = clamp((wy * ey + wz * ez) / (ey * ey + ez * ez), 0, 1);
    d = Math.min(d, (wy - ey * h) ** 2 + (wz - ez * h) ** 2);
    const c1 = pz >= V[i][1], c2 = pz < V[j][1], c3 = ey * wz > ez * wy; if ((c1 && c2 && c3) || (!c1 && !c2 && !c3)) s = -s;
  }
  return s * Math.sqrt(d);
}
// a smooth curve through [y, value] points, y descending (Hermite, Catmull–Rom slopes)
export function keysAt(ks, y) {
  if (y >= ks[0][0]) return ks[0][1]; if (y <= ks[ks.length - 1][0]) return ks[ks.length - 1][1];
  let i = 0; while (i < ks.length - 2 && y < ks[i + 1][0]) i++;
  const [y1, v1] = ks[i], [y2, v2] = ks[i + 1], t = (y1 - y) / (y1 - y2);
  const m1 = i > 0 ? (ks[i + 1][1] - ks[i - 1][1]) / (ks[i - 1][0] - ks[i + 1][0]) * (y1 - y2) : v2 - v1, m2 = i + 2 < ks.length ? (ks[i + 2][1] - v1) / (y1 - ks[i + 2][0]) * (y1 - y2) : v2 - v1;
  const t2 = t * t, t3 = t2 * t; return (2 * t3 - 3 * t2 + 1) * v1 + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * v2 + (t3 - t2) * m2;
}
// a monotone cubic through [y, value] points (no overshoot, flat beyond the ends) — Г2's curves
export function monotone(K) {
  const P = K.slice().sort((a, b) => a[0] - b[0]), n = P.length;
  if (n === 1) return () => P[0][1];
  const d = [], m = new Array(n).fill(0);
  for (let i = 0; i < n - 1; i++) d.push((P[i + 1][1] - P[i][1]) / (P[i + 1][0] - P[i][0]));
  m[0] = d[0]; m[n - 1] = d[n - 2];
  for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2;
  for (let i = 0; i < n - 1; i++) {
    if (d[i] === 0) { m[i] = m[i + 1] = 0; continue; }
    const a = m[i] / d[i], b = m[i + 1] / d[i], h = Math.hypot(a, b);
    if (h > 3) { m[i] = 3 * a / h * d[i]; m[i + 1] = 3 * b / h * d[i]; }
  }
  m[0] = m[n - 1] = 0;
  return q => {
    q = clamp(q, P[0][0], P[n - 1][0]); let i = 0; while (i < n - 2 && P[i + 1][0] < q) i++;
    const hh = P[i + 1][0] - P[i][0], t = (q - P[i][0]) / hh, t2 = t * t, t3 = t2 * t;
    return (2 * t3 - 3 * t2 + 1) * P[i][1] + (t3 - 2 * t2 + t) * hh * m[i] + (-2 * t3 + 3 * t2) * P[i + 1][1] + (t3 - t2) * hh * m[i + 1];
  };
}

// the gradient of a distance (central differences, e apart)
export function gradOf(f, x, y, z, e = 0.004, out = [0, 0, 0]) {
  out[0] = (f(x + e, y, z) - f(x - e, y, z)) / (2 * e); out[1] = (f(x, y + e, z) - f(x, y - e, z)) / (2 * e); out[2] = (f(x, y, z + e) - f(x, y, z - e)) / (2 * e);
  return out;
}
// a point taken onto the surface along the gradient (its steps)
export function projectOn(f, p, steps = 4) {
  let [x, y, z] = p; const g = [0, 0, 0];
  for (let k = 0; k < steps; k++) { const d = f(x, y, z); gradOf(f, x, y, z, 0.004, g); const l = Math.hypot(g[0], g[1], g[2]) || 1; x -= g[0] / l * d; y -= g[1] / l * d; z -= g[2] / l * d; }
  return [x, y, z];
}
// where a ray from the front (along −z, from z0) at (x, y) meets the surface
export function frontZ(f, x, y, z0 = 2.5) { let z = z0; for (let k = 0; k < 120; k++) { const d = f(x, y, z); if (d < 0.001) break; z -= Math.max(d, 0.004); } return z; }

// a shape as a mesh: surface nets on a grid of step h over the box, the distance sampled coarsely first and finely only
// near the surface; a few passes of smoothing along it, then back onto it (the nets leave a faint grid). Returns
// {positions, normals (the distance's gradient), triangles} — plain arrays of numbers
export function meshOf(sdf, bmin, bmax, h) {
  const nx = Math.ceil((bmax[0] - bmin[0]) / h) + 1, ny = Math.ceil((bmax[1] - bmin[1]) / h) + 1, nz = Math.ceil((bmax[2] - bmin[2]) / h) + 1;
  const F = new Float32Array(nx * ny * nz).fill(NaN), id = (i, j, k) => i + nx * (j + ny * k);
  const C = 4, cnx = Math.ceil((nx - 1) / C), cny = Math.ceil((ny - 1) / C), cnz = Math.ceil((nz - 1) / C), thr = C * h * 1.9;
  const CV = new Float32Array((cnx + 1) * (cny + 1) * (cnz + 1)), cid = (i, j, k) => i + (cnx + 1) * (j + (cny + 1) * k);
  for (let k = 0; k <= cnz; k++) for (let j = 0; j <= cny; j++) for (let i = 0; i <= cnx; i++) CV[cid(i, j, k)] = sdf(bmin[0] + i * C * h, bmin[1] + j * C * h, bmin[2] + k * C * h);
  for (let ck = 0; ck < cnz; ck++) for (let cj = 0; cj < cny; cj++) for (let ci = 0; ci < cnx; ci++) {
    let mn = 1e9, s = 0;
    for (let c = 0; c < 8; c++) { const v = CV[cid(ci + (c & 1), cj + (c >> 1 & 1), ck + (c >> 2 & 1))]; mn = Math.min(mn, Math.abs(v)); s = v; }
    const near = mn < thr;
    for (let k = ck * C; k <= Math.min(ck * C + C, nz - 1); k++) for (let j = cj * C; j <= Math.min(cj * C + C, ny - 1); j++) for (let i = ci * C; i <= Math.min(ci * C + C, nx - 1); i++) {
      const q = id(i, j, k); if (!Number.isNaN(F[q]) && !near) continue;
      if (near) { if (Number.isNaN(F[q]) || Math.abs(F[q]) >= thr * 0.999) F[q] = sdf(bmin[0] + i * h, bmin[1] + j * h, bmin[2] + k * h); }
      else F[q] = s > 0 ? thr : -thr;
    }
  }
  for (let q = 0; q < F.length; q++) if (Number.isNaN(F[q])) F[q] = thr;
  const VI = new Int32Array(nx * ny * nz).fill(-1), pos = [], E = [[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [1, 3], [4, 6], [5, 7], [0, 4], [1, 5], [2, 6], [3, 7]], d = new Float32Array(8);
  for (let k = 0; k < nz - 1; k++) for (let j = 0; j < ny - 1; j++) for (let i = 0; i < nx - 1; i++) {
    let m = 0;
    for (let c = 0; c < 8; c++) { d[c] = F[id(i + (c & 1), j + (c >> 1 & 1), k + (c >> 2 & 1))]; if (d[c] < 0) m |= 1 << c; }
    if (m === 0 || m === 255) continue;
    let sx = 0, sy = 0, sz = 0, n = 0;
    for (const [a, b] of E) { if ((d[a] < 0) === (d[b] < 0)) continue; const t = d[a] / (d[a] - d[b]); sx += (a & 1) + ((b & 1) - (a & 1)) * t; sy += (a >> 1 & 1) + ((b >> 1 & 1) - (a >> 1 & 1)) * t; sz += (a >> 2 & 1) + ((b >> 2 & 1) - (a >> 2 & 1)) * t; n++; }
    VI[id(i, j, k)] = pos.length / 3; pos.push(bmin[0] + (i + sx / n) * h, bmin[1] + (j + sy / n) * h, bmin[2] + (k + sz / n) * h);
  }
  const idx = [], quad = (a, b, c, e, flip) => { if (a < 0 || b < 0 || c < 0 || e < 0) return; if (flip) idx.push(a, c, b, a, e, c); else idx.push(a, b, c, a, c, e); };
  for (let k = 1; k < nz - 1; k++) for (let j = 1; j < ny - 1; j++) for (let i = 1; i < nx - 1; i++) {
    const inside = F[id(i, j, k)] < 0;
    if (inside !== (F[id(i + 1, j, k)] < 0)) quad(VI[id(i, j - 1, k - 1)], VI[id(i, j, k - 1)], VI[id(i, j, k)], VI[id(i, j - 1, k)], inside);
    if (inside !== (F[id(i, j + 1, k)] < 0)) quad(VI[id(i - 1, j, k - 1)], VI[id(i - 1, j, k)], VI[id(i, j, k)], VI[id(i, j, k - 1)], inside);
    if (inside !== (F[id(i, j, k + 1)] < 0)) quad(VI[id(i - 1, j - 1, k)], VI[id(i, j - 1, k)], VI[id(i, j, k)], VI[id(i - 1, j, k)], inside);
  }
  const nor = new Float32Array(pos.length), g = [0, 0, 0], e = h * 0.5;
  const gradAt = (x, y, z, v) => { gradOf(sdf, x, y, z, e, g); const l = Math.hypot(g[0], g[1], g[2]) || 1; nor[v] = g[0] / l; nor[v + 1] = g[1] / l; nor[v + 2] = g[2] / l; };
  for (let v = 0; v < pos.length; v += 3) gradAt(pos[v], pos[v + 1], pos[v + 2], v);
  for (let t = 0; t < idx.length; t += 3) {
    const a = idx[t] * 3, b = idx[t + 1] * 3, c = idx[t + 2] * 3;
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2], wx = pos[c] - pos[a], wy = pos[c + 1] - pos[a + 1], wz = pos[c + 2] - pos[a + 2];
    if ((uy * wz - uz * wy) * (nor[a] + nor[b] + nor[c]) + (uz * wx - ux * wz) * (nor[a + 1] + nor[b + 1] + nor[c + 1]) + (ux * wy - uy * wx) * (nor[a + 2] + nor[b + 2] + nor[c + 2]) < 0) { const s = idx[t + 1]; idx[t + 1] = idx[t + 2]; idx[t + 2] = s; }
  }
  const P = Float32Array.from(pos), nb = Array.from({ length: P.length / 3 }, () => new Set());
  for (let t = 0; t < idx.length; t += 3) for (let q = 0; q < 3; q++) { nb[idx[t + q]].add(idx[t + (q + 1) % 3]); nb[idx[t + q]].add(idx[t + (q + 2) % 3]); }
  for (let it = 0; it < 2; it++) {
    const Q2 = Float32Array.from(P);
    for (let v = 0; v < nb.length; v++) { if (!nb[v].size) continue; let x = 0, y = 0, z = 0; for (const u of nb[v]) { x += P[u * 3]; y += P[u * 3 + 1]; z += P[u * 3 + 2]; } const n = nb[v].size; Q2[v * 3] = lerp(P[v * 3], x / n, 0.5); Q2[v * 3 + 1] = lerp(P[v * 3 + 1], y / n, 0.5); Q2[v * 3 + 2] = lerp(P[v * 3 + 2], z / n, 0.5); }
    for (let v = 0; v < nb.length; v++) { const x = Q2[v * 3], y = Q2[v * 3 + 1], z = Q2[v * 3 + 2], s = sdf(x, y, z); gradOf(sdf, x, y, z, e, g); const l = Math.hypot(g[0], g[1], g[2]) || 1; P[v * 3] = x - s * g[0] / l; P[v * 3 + 1] = y - s * g[1] / l; P[v * 3 + 2] = z - s * g[2] / l; nor[v * 3] = g[0] / l; nor[v * 3 + 1] = g[1] / l; nor[v * 3 + 2] = g[2] / l; }
  }
  return { positions: P, normals: nor, triangles: idx };
}
