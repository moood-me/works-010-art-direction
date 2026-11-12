// Geometry for the rubber-hose Савелий Петрович: everything is a few kinds of forms, as in the drawing
// (styles/s11-rubberhose/tools/lib.py) — sweeps along curves (hoses, fingers, tubes), lofts of rings (the body, the
// shoes), "pillows" laid on a surface (brows, moustache, ears, the tie) and balls. Plain arrays in, BufferGeometry out.
// The sweep is the expressive constructor's (experiments/toon, gallery П2), kept as it was, with a colour per ring.
import * as THREE from 'three';
const V3 = THREE.Vector3, Q = THREE.Quaternion;

export const lerp = (a, b, t) => a + (b - a) * t, clamp = (x, a, b) => Math.max(a, Math.min(b, x)), sst = t => t * t * (3 - 2 * t);

// a smooth curve through keys [[t, v], …] (monotone cubic), used for radii and widths along a form
export function keys(ks, t) {
  const n = ks.length; if (t <= ks[0][0]) return ks[0][1]; if (t >= ks[n - 1][0]) return ks[n - 1][1];
  const h = [], d = []; for (let k = 0; k < n - 1; k++) { h.push(ks[k + 1][0] - ks[k][0]); d.push((ks[k + 1][1] - ks[k][1]) / h[k]); }
  const m = ks.map((_, k) => k === 0 ? d[0] : k === n - 1 ? d[n - 2] : (d[k - 1] * d[k] <= 0 ? 0 : (3 * (h[k - 1] + h[k])) / ((2 * h[k] + h[k - 1]) / d[k - 1] + (h[k] + 2 * h[k - 1]) / d[k])));
  let k = 0; while (t > ks[k + 1][0]) k++;
  const u = (t - ks[k][0]) / h[k], u2 = u * u, u3 = u2 * u;
  return (2 * u3 - 3 * u2 + 1) * ks[k][1] + (u3 - 2 * u2 + u) * h[k] * m[k] + (-2 * u3 + 3 * u2) * ks[k + 1][1] + (u3 - u2) * h[k] * m[k + 1];
}

// a bone as a hose: one arc through shoulder, elbow and wrist instead of two sticks and a break (П2)
export function hosePath(A, E, B, bend = 1, n = 36) {
  const mid = A.clone().add(B).multiplyScalar(0.5), C = mid.clone().lerp(E.clone().multiplyScalar(2).sub(mid), bend);
  const pts = [];
  for (let k = 0; k <= n; k++) { const t = k / n; pts.push(A.clone().multiplyScalar((1 - t) ** 2).addScaledVector(C, 2 * t * (1 - t)).addScaledVector(B, t * t)); }
  return pts;
}
export function bezier(ps, n = 30) {
  const out = [];
  for (let k = 0; k <= n; k++) { let q = ps.map(p => p.clone()); const t = k / n; while (q.length > 1) q = q.slice(1).map((p, i) => q[i].clone().lerp(p, t)); out.push(q[0]); }
  return out;
}
// a Catmull-Rom curve through points (the drawing's `smooth`), n points per span
export function through(ps, n = 8) {
  const out = [];
  for (let i = 0; i < ps.length - 1; i++) {
    const p0 = ps[Math.max(0, i - 1)], p1 = ps[i], p2 = ps[i + 1], p3 = ps[Math.min(ps.length - 1, i + 2)];
    for (let s = 0; s < n; s++) {
      const t = s / n, t2 = t * t, t3 = t2 * t;
      out.push(new V3().addScaledVector(p1, 2).addScaledVector(p2.clone().sub(p0), t).addScaledVector(p0.clone().multiplyScalar(2).addScaledVector(p1, -5).addScaledVector(p2, 4).sub(p3), t2)
        .addScaledVector(p1.clone().multiplyScalar(3).sub(p0).addScaledVector(p2, -3).add(p3), t3).multiplyScalar(0.5));
    }
  }
  out.push(ps[ps.length - 1].clone());
  return out;
}

// a sweep along a path, any section, rounded ends (П2's). sect(i, a) → [x, y] in the ring's frame;
// o.color(i) → [r, g, b] per ring; o.up — a fixed "normal" for the frame; o.capStart/capEnd false — open ends
export function sweep(pts, sect, o = {}) {
  const n = pts.length, R = o.radial || 20;
  const T = pts.map((p, i) => pts[Math.min(n - 1, i + 1)].clone().sub(pts[Math.max(0, i - 1)]).normalize());
  const Ns = [], Bs = [];
  let N0 = o.up ? o.up.clone() : (Math.abs(T[0].y) < 0.9 ? new V3(0, 0, 1) : new V3(1, 0, 0));
  N0.addScaledVector(T[0], -N0.dot(T[0])).normalize(); Ns.push(N0); Bs.push(new V3().crossVectors(T[0], N0));
  for (let i = 1; i < n; i++) {
    const N = Ns[i - 1].clone().applyQuaternion(new Q().setFromUnitVectors(T[i - 1], T[i]));
    if (o.up) N.copy(o.up);
    N.addScaledVector(T[i], -N.dot(T[i])).normalize(); Ns.push(N); Bs.push(new V3().crossVectors(T[i], N));
  }
  const rings = [];
  const meanR = i => { let s = 0; for (let k = 0; k < 8; k++) { const [x, y] = sect(i, k / 8 * Math.PI * 2); s += Math.hypot(x, y); } return s / 8; };
  const CAP = 6;
  if (o.capStart !== false) for (let k = CAP; k >= 1; k--) { const ph = k / CAP * Math.PI / 2 * 0.97; rings.push({ c: pts[0].clone().addScaledVector(T[0], -meanR(0) * Math.sin(ph) * (o.capDepth || 1)), i: 0, k: Math.cos(ph) }); }
  for (let i = 0; i < n; i++) rings.push({ c: pts[i], i, k: 1 });
  if (o.capEnd !== false) for (let k = 1; k <= CAP; k++) { const ph = k / CAP * Math.PI / 2 * 0.97; rings.push({ c: pts[n - 1].clone().addScaledVector(T[n - 1], meanR(n - 1) * Math.sin(ph) * (o.capDepth || 1)), i: n - 1, k: Math.cos(ph) }); }
  const pos = [], col = [], idx = [];
  for (const r of rings) for (let a = 0; a < R; a++) {
    const ang = a / R * Math.PI * 2, [x, y] = sect(r.i, ang);
    const p = r.c.clone().addScaledVector(Ns[r.i], x * r.k).addScaledVector(Bs[r.i], y * r.k);
    pos.push(p.x, p.y, p.z); col.push(...(o.color ? o.color(r.i) : [1, 1, 1]));
  }
  for (let j = 0; j + 1 < rings.length; j++) for (let a = 0; a < R; a++) {
    const a1 = (a + 1) % R, p0 = j * R + a, p1 = j * R + a1, q0 = (j + 1) * R + a, q1 = (j + 1) * R + a1;
    idx.push(p0, p1, q0, p1, q1, q0);
  }
  const close = (ring, tip, flip) => { const v = pos.length / 3; pos.push(tip.x, tip.y, tip.z); col.push(...col.slice(ring * R * 3, ring * R * 3 + 3)); for (let a = 0; a < R; a++) { const a1 = (a + 1) % R; flip ? idx.push(v, ring * R + a, ring * R + a1) : idx.push(v, ring * R + a1, ring * R + a); } };
  close(0, o.capStart !== false ? pts[0].clone().addScaledVector(T[0], -meanR(0) * (o.capDepth || 1)) : pts[0], false);
  close(rings.length - 1, o.capEnd !== false ? pts[n - 1].clone().addScaledVector(T[n - 1], meanR(n - 1) * (o.capDepth || 1)) : pts[n - 1], true);
  if (o.flip) for (let k = 0; k < idx.length; k += 3) { const t = idx[k + 1]; idx[k + 1] = idx[k + 2]; idx[k + 2] = t; }
  return geom(pos, idx, col);
}
export const circle = r => (i, a) => [Math.cos(a) * r(i), Math.sin(a) * r(i)];

export function geom(pos, idx, col) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  if (col) g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  g.setIndex(idx); g.computeVertexNormals();
  return g;
}

// a closed loft of rings: ring(k, a) → [x, y, z] for k = 0…K (k = 0 and K are closed to a point at their centres)
export function loft(K, R, ring, o = {}) {
  const pos = [], idx = [];
  for (let k = 0; k <= K; k++) for (let a = 0; a < R; a++) pos.push(...ring(k, a / R * Math.PI * 2));
  for (let k = 0; k < K; k++) for (let a = 0; a < R; a++) {
    const a1 = (a + 1) % R, p0 = k * R + a, p1 = k * R + a1, q0 = (k + 1) * R + a, q1 = (k + 1) * R + a1;
    idx.push(p0, q0, p1, p1, q0, q1);
  }
  for (const [k, flip] of [[0, false], [K, true]]) {
    const c = [0, 0, 0]; for (let a = 0; a < R; a++) for (let d = 0; d < 3; d++) c[d] += pos[(k * R + a) * 3 + d] / R;
    const v = pos.length / 3; pos.push(...(o.tips ? o.tips[k ? 1 : 0] : c));
    for (let a = 0; a < R; a++) { const a1 = (a + 1) % R; flip ? idx.push(v, k * R + a, k * R + a1) : idx.push(v, k * R + a1, k * R + a); }
  }
  if (o.flip) for (let k = 0; k < idx.length; k += 3) { const t = idx[k + 1]; idx[k + 1] = idx[k + 2]; idx[k + 2] = t; }
  return geom(pos, idx);
}

// a pillow on a surface: a flat shape (outline: [u, v] points round it, star-shaped about `centre`) laid on a surface
// and puffed up — the front bulges by `thick` (rounded like a cushion), the back sinks a little under the surface.
// place(u, v, h) → [x, y, z]: where the point (u, v) of the shape is at height h over the surface.
export function pillow(outline, place, o = {}) {
  const thick = o.thick ?? 6, sink = o.sink ?? 2, K = o.rings ?? 10, n = outline.length;
  const c = o.centre || outline.reduce((s, p) => [s[0] + p[0] / n, s[1] + p[1] / n], [0, 0]);
  const prof = o.profile || (s => Math.sqrt(Math.max(0, 1 - s ** 2.2)));   // height across the shape: 1 in the middle, 0 at the edge
  const pos = [], idx = [];
  // front rings from the edge (k = 0) to the middle (k = K), then back rings from the middle back to the edge
  const ringAt = (s, h) => { for (const p of outline) { const u = c[0] + (p[0] - c[0]) * s, v = c[1] + (p[1] - c[1]) * s; pos.push(...place(u, v, h(s, u, v))); } };
  const ss = []; for (let k = 0; k < K; k++) ss.push(1 - k / K);
  for (const s of ss) ringAt(s, (s, u, v) => thick * prof(s) * (o.shape ? o.shape(u, v) : 1));
  const front = pos.length / 3; pos.push(...place(c[0], c[1], thick * (o.shape ? o.shape(c[0], c[1]) : 1)));
  for (const s of ss.slice(1)) ringAt(s, () => -sink * Math.sqrt(1 - s * s));
  const back = pos.length / 3; pos.push(...place(c[0], c[1], -sink));
  const ring = k => k * n;
  for (let k = 0; k < K - 1; k++) for (let a = 0; a < n; a++) { const a1 = (a + 1) % n; idx.push(ring(k) + a, ring(k + 1) + a, ring(k) + a1, ring(k) + a1, ring(k + 1) + a, ring(k + 1) + a1); }
  for (let a = 0; a < n; a++) idx.push(ring(K - 1) + a, front, ring(K - 1) + (a + 1) % n);
  // back: the edge ring (k = 0) is shared; back rings are after the front tip
  const bring = k => k === 0 ? 0 : front + 1 + (k - 1) * n;
  for (let k = 0; k < K - 1; k++) for (let a = 0; a < n; a++) { const a1 = (a + 1) % n; idx.push(bring(k) + a, bring(k) + a1, bring(k + 1) + a, bring(k) + a1, bring(k + 1) + a1, bring(k + 1) + a); }
  for (let a = 0; a < n; a++) idx.push(bring(K - 1) + a, bring(K - 1) + (a + 1) % n, back);
  if (o.flip) for (let k = 0; k < idx.length; k += 3) { const t = idx[k + 1]; idx[k + 1] = idx[k + 2]; idx[k + 2] = t; }
  return geom(pos, idx);
}

// the drawing's closed smooth outline (Catmull-Rom through points, `lib.smooth`) sampled to a polygon
export function outline(pts, per = 8, k = 1) {
  const out = [], n = pts.length;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6 * k, p1[1] + (p2[1] - p0[1]) / 6 * k], c2 = [p2[0] - (p3[0] - p1[0]) / 6 * k, p2[1] - (p3[1] - p1[1]) / 6 * k];
    for (let s = 0; s < per; s++) { const t = s / per, u = 1 - t; out.push([u * u * u * p1[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * p2[0], u * u * u * p1[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * p2[1]]); }
  }
  return out;
}
// the drawing's scalloped cloud (savely.cloud): n round bumps along the top, a soft curve under — as a polygon
export function cloud(w, h, nb, per = 7) {
  const pts = [];
  for (let i = 0; i <= nb; i++) { const ang = Math.PI * (1 - i / nb); pts.push([Math.cos(ang) * w / 2, -Math.sin(ang) * h / 2]); }
  const out = [];
  const quad = (a, c, b) => { for (let s = 0; s < per; s++) { const t = s / per, u = 1 - t; out.push([u * u * a[0] + 2 * u * t * c[0] + t * t * b[0], u * u * a[1] + 2 * u * t * c[1] + t * t * b[1]]); } };
  for (let i = 0; i < nb; i++) {
    const [x0, y0] = pts[i], [x1, y1] = pts[i + 1], mx = (x0 + x1) / 2, my = (y0 + y1) / 2, L = Math.hypot(mx, my) || 1, bump = Math.hypot(x1 - x0, y1 - y0) * 0.55;
    quad([x0, y0], [mx + mx / L * bump, my + my / L * bump], [x1, y1]);
  }
  quad(pts[nb], [0, h * 0.35], pts[0]);
  return out;   // y down, as drawn
}

// many geometries as one (positions, normals, colours if all have them)
export function merge(gs) {
  const pos = [], nor = [], idx = [], col = [];
  let off = 0; const hasCol = gs.every(g => g.attributes.color);
  for (const g of gs) {
    const p = g.attributes.position, n = g.attributes.normal;
    for (let i = 0; i < p.count; i++) { pos.push(p.getX(i), p.getY(i), p.getZ(i)); nor.push(n.getX(i), n.getY(i), n.getZ(i)); if (hasCol) col.push(g.attributes.color.getX(i), g.attributes.color.getY(i), g.attributes.color.getZ(i)); }
    const ix = g.index.array; for (let k = 0; k < ix.length; k++) idx.push(ix[k] + off);
    off += p.count; g.dispose();
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  if (hasCol) g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  g.setIndex(idx); return g;
}
export function ball(c, r, seg = 20) { const g = new THREE.SphereGeometry(1, seg, Math.round(seg * 0.7)); g.scale(...(Array.isArray(r) ? r : [r, r, r])); g.translate(c[0], c[1], c[2]); return g; }
