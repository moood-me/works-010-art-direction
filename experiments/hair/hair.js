// Hair as designed volumes: a scalp mass over the skull up to a drawn hairline, and big locks swept along guide
// curves — each a flattened, tapering section lying against the head — all merged into one surface, so a hairstyle
// reads as a few big shapes with soft valleys between them, never as a helmet or as separate ribbons.
// Every lock keeps its guide curve, so later it can hang on a chain of joints from the Head bone.

const len = (x, y, z) => Math.hypot(x, y, z);
export const smin = (a, b, k) => { if (k <= 0) return Math.min(a, b); const h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * 0.25; };
export const smax = (a, b, k) => -smin(-a, -b, k);
const ellip = (x, y, z, rx, ry, rz) => { const k = len(x / rx, y / ry, z / rz); return (k - 1) * Math.min(rx, ry, rz); };
const capsule = (px, py, pz, a, b, r) => {
  const bx = b[0] - a[0], by = b[1] - a[1], bz = b[2] - a[2], qx = px - a[0], qy = py - a[1], qz = pz - a[2];
  const t = Math.max(0, Math.min(1, (qx * bx + qy * by + qz * bz) / (bx * bx + by * by + bz * bz)));
  return len(qx - bx * t, qy - by * t, qz - bz * t) - r;
};

// ———— the neutral head: only there to carry the hair ————
export const CRANIUM = { c: [0, 0.018, -0.006], r: [0.081, 0.094, 0.091] };
export function headSDF(o = {}) {
  const m = o.male ? 1 : 0, cr = CRANIUM;
  const sdf = (x, y, z) => {
    let d = ellip(x - cr.c[0], y - cr.c[1], z - cr.c[2], ...cr.r);
    d = smin(d, ellip(x, y + 0.043, z - 0.018, 0.066 + 0.006 * m, 0.07, 0.072), 0.03);
    d = smin(d, ellip(x, y + 0.093, z - 0.046, 0.026 + 0.01 * m, 0.022, 0.024), 0.03);
    d = smin(d, ellip(x, y + 0.03, z - 0.088, 0.008, 0.012, 0.011), 0.012);              // nose
    for (const s of [-1, 1]) d = smin(d, ellip(x - s * 0.079, y + 0.008, z + 0.006, 0.011, 0.025, 0.016), 0.01); // ears
    d = smin(d, capsule(x, y, z, [0, -0.07, -0.012], [0, -0.22, -0.02], 0.041 + 0.006 * m), 0.03); // neck
    d = smin(d, ellip(x, y + 0.27, z + 0.01, 0.17 + 0.03 * m, 0.065, 0.085), 0.06);    // shoulders
    return d;
  };
  const eyes = [-1, 1].map(s => ({ c: [s * 0.03, -0.014, 0.075], r: [0.0085, 0.012, 0.004] }));
  return { sdf, eyes };
}
// a point on the scalp: azimuth th (0 = front, +pi/2 = the head's left), elevation ph, lifted off by `off`
export function scalp(th, ph, off = 0) {
  const d = [Math.sin(th) * Math.cos(ph), Math.sin(ph), Math.cos(th) * Math.cos(ph)], r = CRANIUM.r, c = CRANIUM.c;
  return [c[0] + d[0] * (r[0] + off), c[1] + d[1] * (r[1] + off), c[2] + d[2] * (r[2] + off)];
}

// ———— a lock: a swept, flattened, tapering volume along a Catmull-Rom guide ————
function catmull(pts, n) {
  const P = [pts[0], ...pts, pts[pts.length - 1]], out = [], seg = pts.length - 1;
  for (let i = 0; i <= n; i++) {
    const u = i / n * seg, k = Math.min(Math.floor(u), seg - 1), t = u - k;
    const p0 = P[k], p1 = P[k + 1], p2 = P[k + 2], p3 = P[k + 3], t2 = t * t, t3 = t2 * t;
    out.push([0, 1, 2].map(j => 0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)));
  }
  return out;
}
const lerpArr = (a, s) => { if (typeof a === 'number') return a; const u = s * (a.length - 1), i = Math.min(Math.floor(u), a.length - 2), t = u - i; return a[i] + (a[i + 1] - a[i]) * t; };
export function lock(o) {
  const n = o.n || 24, c = catmull(o.pts, n), S = [];
  if (o.wave) for (let i = 0; i <= n; i++) {   // a wave across the lock's fall: sideways, growing towards the tip
    const s = i / n, p = c[i], q = c[Math.min(i + 1, n)], r = c[Math.max(i - 1, 0)], T = [q[0] - r[0], q[1] - r[1], q[2] - r[2]];
    const side = [T[2], 0, -T[0]], sl = Math.hypot(...side) || 1, amp = o.wave.amp * Math.min(1, s * 2) * Math.sin(s * o.wave.f * 6.283 + (o.wave.ph || 0));
    c[i] = [p[0] + side[0] / sl * amp, p[1], p[2] + side[2] / sl * amp];
  }
  for (let i = 0; i <= n; i++) {
    const s = i / n, p = c[i], q = c[Math.min(i + 1, n)], r = c[Math.max(i - 1, 0)];
    let T = [q[0] - r[0], q[1] - r[1], q[2] - r[2]]; const tl = len(...T) || 1; T = T.map(v => v / tl);
    // the flat side lies against the head: thickness points away from the head's axis, unless a direction is given
    let B = o.up ? o.up.slice() : [p[0] - CRANIUM.c[0], (p[1] - CRANIUM.c[1]) * (o.vert ?? 1), p[2] - CRANIUM.c[2]];
    const bt = B[0] * T[0] + B[1] * T[1] + B[2] * T[2]; B = [B[0] - bt * T[0], B[1] - bt * T[1], B[2] - bt * T[2]];
    const bl = len(...B) || 1; B = B.map(v => v / bl);
    if (S.length && B[0] * S[S.length - 1].B[0] + B[1] * S[S.length - 1].B[1] + B[2] * S[S.length - 1].B[2] < 0) B = B.map(v => -v);
    if (o.twist) { const a = lerpArr(o.twist, s), N0 = [T[1] * B[2] - T[2] * B[1], T[2] * B[0] - T[0] * B[2], T[0] * B[1] - T[1] * B[0]]; B = B.map((v, j) => v * Math.cos(a) + N0[j] * Math.sin(a)); }
    const N = [T[1] * B[2] - T[2] * B[1], T[2] * B[0] - T[0] * B[2], T[0] * B[1] - T[1] * B[0]];
    let w = lerpArr(o.w, s); const tip = o.tip ?? 0.35;
    if (s > 1 - tip && o.point !== false) w *= Math.pow((1 - s) / tip, o.sharp ?? 0.7);
    if (s < (o.root ?? 0) ) w *= 0.6 + 0.4 * s / o.root;
    const th = Math.max(0.0012, o.t !== undefined ? lerpArr(o.t, s) * (w / Math.max(lerpArr(o.w, s), 1e-6)) : w * (o.flat ?? 0.42));
    S.push({ p, T, B, N, w: Math.max(0.0012, w), t: th, lens: o.lens ?? 0.6 });
  }
  const bb = [[1e9, 1e9, 1e9], [-1e9, -1e9, -1e9]];
  for (const e of S) for (let j = 0; j < 3; j++) { bb[0][j] = Math.min(bb[0][j], e.p[j] - e.w); bb[1][j] = Math.max(bb[1][j], e.p[j] + e.w); }
  const curly = o.curly;
  const sdf = (x, y, z) => {
    const ox = Math.max(bb[0][0] - x, 0, x - bb[1][0]), oy = Math.max(bb[0][1] - y, 0, y - bb[1][1]), oz = Math.max(bb[0][2] - z, 0, z - bb[1][2]);
    if (ox + oy + oz > 0.03) return ox + oy + oz;
    let best = 1e9;
    for (let i = 0; i < S.length - 1; i++) {
      const a = S[i], b = S[i + 1];
      const bx = b.p[0] - a.p[0], by = b.p[1] - a.p[1], bz = b.p[2] - a.p[2], qx = x - a.p[0], qy = y - a.p[1], qz = z - a.p[2];
      const L2 = bx * bx + by * by + bz * bz || 1e-9;
      const u = Math.max(0, Math.min(1, (qx * bx + qy * by + qz * bz) / L2));
      const rx = qx - bx * u, ry = qy - by * u, rz = qz - bz * u;
      if (rx * rx + ry * ry + rz * rz > (Math.max(a.w, b.w) + Math.min(best, 0.02) + 0.004) ** 2) continue;
      const w = a.w + (b.w - a.w) * u, t = a.t + (b.t - a.t) * u;
      const m = Math.min(w, t), iu = 1 - u;
      const B0 = a.B[0] * iu + b.B[0] * u, B1 = a.B[1] * iu + b.B[1] * u, B2 = a.B[2] * iu + b.B[2] * u;
      const N0 = a.N[0] * iu + b.N[0] * u, N1 = a.N[1] * iu + b.N[1] * u, N2 = a.N[2] * iu + b.N[2] * u;
      const T0 = a.T[0] * iu + b.T[0] * u, T1 = a.T[1] * iu + b.T[1] * u, T2 = a.T[2] * iu + b.T[2] * u;
      const bl = Math.hypot(B0, B1, B2) || 1, nl = Math.hypot(N0, N1, N2) || 1, tl = Math.hypot(T0, T1, T2) || 1;
      let v1 = (rx * N0 + ry * N1 + rz * N2) / nl / w, v2 = (rx * B0 + ry * B1 + rz * B2) / bl / t;
      const v3 = (rx * T0 + ry * T1 + rz * T2) / tl / m;
      // a lens, not a tube: the outer face curves, the side edges thin out to meet the neighbours
      if (a.lens) { const e = Math.abs(v1); v2 = v2 / Math.max(0.05, 1 - a.lens * e * e); }
      let d = (Math.hypot(v1, v2, v3) - 1) * m;
      if (curly) { const sAlong = (i + u) / (S.length - 1), ang = Math.atan2(v2, v1); d -= curly.amp * m * Math.sin(curly.f * sAlong * 6.283 + curly.turn * ang); }
      if (d < best) best = d;
    }
    return best;
  };
  return { sdf, bb, color: o.color, k: o.k };
}
export function ell(o) {   // an ellipsoid, optionally turned: axes u, v (w follows)
  const c = o.c, r = o.r, u = o.u || [1, 0, 0], v0 = o.v || [0, 1, 0];
  const w = [u[1] * v0[2] - u[2] * v0[1], u[2] * v0[0] - u[0] * v0[2], u[0] * v0[1] - u[1] * v0[0]];
  const v = [w[1] * u[2] - w[2] * u[1], w[2] * u[0] - w[0] * u[2], w[0] * u[1] - w[1] * u[0]];
  const m = Math.max(...r);
  return { sdf: (x, y, z) => { const px = x - c[0], py = y - c[1], pz = z - c[2]; return ellip(px * u[0] + py * u[1] + pz * u[2], px * v[0] + py * v[1] + pz * v[2], px * w[0] + py * w[1] + pz * w[2], ...r); },
    bb: [c.map(q => q - m), c.map(q => q + m)], color: o.color, k: o.k };
}
export function torus(o) {   // a ring around axis a
  const c = o.c, a = o.a.map(q => q / len(...o.a)), R = o.R, r = o.r;
  return { sdf: (x, y, z) => { const px = x - c[0], py = y - c[1], pz = z - c[2], h = px * a[0] + py * a[1] + pz * a[2];
    const qx = px - h * a[0], qy = py - h * a[1], qz = pz - h * a[2], ql = len(qx, qy, qz); return Math.hypot(ql - R, h * (o.flat ?? 1)) - r; },
    bb: [c.map(q => q - R - r), c.map(q => q + R + r)], color: o.color, k: o.k };
}

// ———— the scalp mass: the skull grown by a thickness, cut by a drawn hairline ————
function hairline(cap, x, y, z) {
  const th = Math.abs(Math.atan2(x - CRANIUM.c[0], z - CRANIUM.c[2]));
  const K = [[0, cap.front ?? 0.066], [1.0, cap.temple ?? 0.034], [1.45, cap.ear ?? 0.022], [1.95, cap.behind ?? -0.045], [Math.PI, cap.nape ?? -0.075]];
  let h = K[4][1];
  for (let i = 0; i < 4; i++) if (th <= K[i + 1][0]) { const t = (th - K[i][0]) / (K[i + 1][0] - K[i][0]); h = K[i][1] + (K[i + 1][1] - K[i][1]) * (t * t * (3 - 2 * t)); break; }
  if (cap.shave && Math.sign(x) === cap.shave.side) h = Math.max(h, cap.shave.y);
  return h;
}
export function scalpMass(cap) {
  const c = CRANIUM.c, r = CRANIUM.r;
  return { sdf: (x, y, z) => {
    const dx = x - c[0], dy = y - c[1], dz = z - c[2], dl = len(dx, dy, dz) || 1;
    const t = cap.thick + (cap.puff || 0) * Math.max(0, dy / dl) + (cap.back || 0) * Math.max(0, -dz / dl) + (cap.sides || 0) * Math.abs(dx / dl);
    const d = ellip(dx, dy - (cap.lift || 0), dz, r[0] + t, r[1] + t, r[2] + t);
    return smax(d, hairline(cap, x, y, z) - y, cap.edge ?? 0.008);
  }, bb: [[-0.14, -0.2, -0.15], [0.14, 0.16, 0.14]], color: cap.color, k: cap.k };
}

// ———— a whole hairstyle: parts, each one surface ————
export function buildHair(S) {
  const out = [];
  for (const part of S.parts) {
    const items = part.items.flat();
    const k = part.k ?? 0.012;
    const bmin = [1e9, 1e9, 1e9], bmax = [-1e9, -1e9, -1e9];
    for (const it of items) for (let j = 0; j < 3; j++) { bmin[j] = Math.min(bmin[j], it.bb[0][j]); bmax[j] = Math.max(bmax[j], it.bb[1][j]); }
    for (let j = 0; j < 3; j++) { bmin[j] -= 0.012; bmax[j] += 0.012; }
    const cuts = part.cuts || [];
    const sdf = (x, y, z) => {
      let d = 1e9;
      for (const it of items) {
        const ox = Math.max(it.bb[0][0] - x, 0, x - it.bb[1][0]), oy = Math.max(it.bb[0][1] - y, 0, y - it.bb[1][1]), oz = Math.max(it.bb[0][2] - z, 0, z - it.bb[1][2]);
        if (ox + oy + oz > Math.min(d, 0.02) + (it.k ?? k)) continue;
        d = smin(d, it.sdf(x, y, z), it.k ?? k);
      }
      for (const cu of cuts) d = smax(d, -cu.sdf(x, y, z), cu.k ?? 0.004);
      return d;
    };
    const m = surfaceNets(sdf, bmin, bmax, part.h || 0.0028);
    // colour each point by its nearest item, so a streak or a band keeps its own colour
    if (items.some(it => it.color !== undefined && it.color !== part.color)) {
      const col = new Float32Array(m.pos.length), base = hex(part.color);
      for (let v = 0; v < m.pos.length; v += 3) {
        let best = 1e9, c = base;
        for (const it of items) { const d = it.sdf(m.pos[v], m.pos[v + 1], m.pos[v + 2]); if (d < best) { best = d; c = it.color !== undefined ? hex(it.color) : base; } }
        col[v] = c[0]; col[v + 1] = c[1]; col[v + 2] = c[2];
      }
      m.col = col;
      out.push({ mesh: m, color: 0xffffff, rough: part.rough, ink: part.ink });
    } else out.push({ mesh: m, color: part.color, rough: part.rough, ink: part.ink });
  }
  return out;
}
const hex = c => [((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255].map(v => Math.pow(v, 2.2));

// ———— a surface out of a distance: naive surface nets, near the surface only ————
export function surfaceNets(sdf, bmin, bmax, h) {
  const nx = Math.ceil((bmax[0] - bmin[0]) / h) + 1, ny = Math.ceil((bmax[1] - bmin[1]) / h) + 1, nz = Math.ceil((bmax[2] - bmin[2]) / h) + 1;
  const F = new Float32Array(nx * ny * nz).fill(NaN);
  const id = (i, j, k) => i + nx * (j + ny * k);
  const C = 4, cnx = Math.ceil((nx - 1) / C), cny = Math.ceil((ny - 1) / C), cnz = Math.ceil((nz - 1) / C);
  const thr = C * h * 1.9;
  const CV = new Float32Array((cnx + 1) * (cny + 1) * (cnz + 1));
  const cid = (i, j, k) => i + (cnx + 1) * (j + (cny + 1) * k);
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
  const VI = new Int32Array(nx * ny * nz).fill(-1), pos = [];
  const E = [[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [1, 3], [4, 6], [5, 7], [0, 4], [1, 5], [2, 6], [3, 7]];
  const d = new Float32Array(8);
  for (let k = 0; k < nz - 1; k++) for (let j = 0; j < ny - 1; j++) for (let i = 0; i < nx - 1; i++) {
    let m = 0;
    for (let c = 0; c < 8; c++) { d[c] = F[id(i + (c & 1), j + (c >> 1 & 1), k + (c >> 2 & 1))]; if (d[c] < 0) m |= 1 << c; }
    if (m === 0 || m === 255) continue;
    let sx = 0, sy = 0, sz = 0, n = 0;
    for (const [a, b] of E) {
      if ((d[a] < 0) === (d[b] < 0)) continue;
      const t = d[a] / (d[a] - d[b]);
      sx += (a & 1) + ((b & 1) - (a & 1)) * t; sy += (a >> 1 & 1) + ((b >> 1 & 1) - (a >> 1 & 1)) * t; sz += (a >> 2 & 1) + ((b >> 2 & 1) - (a >> 2 & 1)) * t; n++;
    }
    VI[id(i, j, k)] = pos.length / 3;
    pos.push(bmin[0] + (i + sx / n) * h, bmin[1] + (j + sy / n) * h, bmin[2] + (k + sz / n) * h);
  }
  const idx = [];
  const quad = (a, b, c, e, flip) => { if (a < 0 || b < 0 || c < 0 || e < 0) return; if (flip) idx.push(a, c, b, a, e, c); else idx.push(a, b, c, a, c, e); };
  for (let k = 1; k < nz - 1; k++) for (let j = 1; j < ny - 1; j++) for (let i = 1; i < nx - 1; i++) {
    const inside = F[id(i, j, k)] < 0;
    if (inside !== (F[id(i + 1, j, k)] < 0)) quad(VI[id(i, j - 1, k - 1)], VI[id(i, j, k - 1)], VI[id(i, j, k)], VI[id(i, j - 1, k)], inside);
    if (inside !== (F[id(i, j + 1, k)] < 0)) quad(VI[id(i - 1, j, k - 1)], VI[id(i - 1, j, k)], VI[id(i, j, k)], VI[id(i, j, k - 1)], inside);
    if (inside !== (F[id(i, j, k + 1)] < 0)) quad(VI[id(i - 1, j - 1, k)], VI[id(i, j - 1, k)], VI[id(i, j, k)], VI[id(i - 1, j, k)], inside);
  }
  // smooth the points a little over the surface, then normals from the distance itself
  const P = new Float32Array(pos), nv = P.length / 3, nb = Array.from({ length: nv }, () => []);
  for (let t = 0; t < idx.length; t += 3) for (let e = 0; e < 3; e++) { const a = idx[t + e], b = idx[t + (e + 1) % 3]; nb[a].push(b); nb[b].push(a); }
  for (let it = 0; it < 6; it++) { const Q = Float32Array.from(P); for (let v = 0; v < nv; v++) { const ns = nb[v]; if (!ns.length) continue; let x = 0, y = 0, z = 0; for (const u of ns) { x += Q[u * 3]; y += Q[u * 3 + 1]; z += Q[u * 3 + 2]; } const f = it % 2 ? -0.53 : 0.5; P[v * 3] += f * (x / ns.length - Q[v * 3]); P[v * 3 + 1] += f * (y / ns.length - Q[v * 3 + 1]); P[v * 3 + 2] += f * (z / ns.length - Q[v * 3 + 2]); } }
  const nor = new Float32Array(P.length), e = h * 0.5;
  for (let v = 0; v < P.length; v += 3) {
    const x = P[v], y = P[v + 1], z = P[v + 2];
    const gx = sdf(x + e, y, z) - sdf(x - e, y, z), gy = sdf(x, y + e, z) - sdf(x, y - e, z), gz = sdf(x, y, z + e) - sdf(x, y, z - e);
    const l = Math.hypot(gx, gy, gz) || 1; nor[v] = gx / l; nor[v + 1] = gy / l; nor[v + 2] = gz / l;
  }
  // the shading follows the big form: normals averaged over the surface a little, so the lock's segments don't show
  for (let it = 0; it < 3; it++) { const Q = Float32Array.from(nor); for (let v = 0; v < nv; v++) { const ns = nb[v]; if (!ns.length) continue; let x = Q[v * 3] * 2, y = Q[v * 3 + 1] * 2, z = Q[v * 3 + 2] * 2; for (const u of ns) { x += Q[u * 3]; y += Q[u * 3 + 1]; z += Q[u * 3 + 2]; } const l = Math.hypot(x, y, z) || 1; nor[v * 3] = x / l; nor[v * 3 + 1] = y / l; nor[v * 3 + 2] = z / l; } }
  for (let t = 0; t < idx.length; t += 3) {
    const a = idx[t] * 3, b = idx[t + 1] * 3, c = idx[t + 2] * 3;
    const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], wx = P[c] - P[a], wy = P[c + 1] - P[a + 1], wz = P[c + 2] - P[a + 2];
    const cx = uy * wz - uz * wy, cy = uz * wx - ux * wz, cz = ux * wy - uy * wx;
    if (cx * (nor[a] + nor[b] + nor[c]) + cy * (nor[a + 1] + nor[b + 1] + nor[c + 1]) + cz * (nor[a + 2] + nor[b + 2] + nor[c + 2]) < 0) { const s = idx[t + 1]; idx[t + 1] = idx[t + 2]; idx[t + 2] = s; }
  }
  return { pos: P, nor, idx };
}
