// The indie constructor's simple forms (signed distances) and its mesher, copied unchanged from
// experiments/indie/index.html (lines 72–208) so this page can use them as a module.
const lerp = (a, b, t) => a + (b - a) * t, clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const smooth = t => t * t * (3 - 2 * t);
function smin(a, b, k) { const h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * 0.25; }
function smax(a, b, k) { return -smin(-a, -b, k); }
function ellipsoid(cx, cy, cz, rx, ry, rz) {
  return (x, y, z) => {
    const px = (x - cx) / rx, py = (y - cy) / ry, pz = (z - cz) / rz;
    const k0 = Math.sqrt(px * px + py * py + pz * pz);
    const qx = px / rx, qy = py / ry, qz = pz / rz, k1 = Math.sqrt(qx * qx + qy * qy + qz * qz);
    return k1 < 1e-9 ? -Math.min(rx, ry, rz) : k0 * (k0 - 1) / k1;
  };
}
// an ellipsoid along its own axes: u (with ru), v (rv), w = u × v (rw)
function oell(c, u, v, ru, rv, rw) {
  const n = a => { const l = Math.hypot(a[0], a[1], a[2]); return [a[0] / l, a[1] / l, a[2] / l]; };
  u = n(u); v = n(v);
  const d = u[0] * v[0] + u[1] * v[1] + u[2] * v[2]; v = n([v[0] - u[0] * d, v[1] - u[1] * d, v[2] - u[2] * d]);
  const w = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
  const e = ellipsoid(0, 0, 0, ru, rv, rw);
  return (x, y, z) => { const px = x - c[0], py = y - c[1], pz = z - c[2]; return e(px * u[0] + py * u[1] + pz * u[2], px * v[0] + py * v[1] + pz * v[2], px * w[0] + py * w[1] + pz * w[2]); };
}
function cone(a, b, r1, r2) {
  const bax = b[0] - a[0], bay = b[1] - a[1], baz = b[2] - a[2];
  const l2 = bax * bax + bay * bay + baz * baz, rr = r1 - r2, a2 = l2 - rr * rr, il2 = 1 / l2;
  return (x, y, z) => {
    const pax = x - a[0], pay = y - a[1], paz = z - a[2];
    const yy = pax * bax + pay * bay + paz * baz, zz = yy - l2;
    const xx = pax * l2 - bax * yy, xy = pay * l2 - bay * yy, xz = paz * l2 - baz * yy;
    const x2 = xx * xx + xy * xy + xz * xz, y2 = yy * yy * l2, z2 = zz * zz * l2;
    const k = Math.sign(rr) * rr * rr * x2;
    if (Math.sign(zz) * a2 * z2 > k) return Math.sqrt(x2 + z2) * il2 - r2;
    if (Math.sign(yy) * a2 * y2 < k) return Math.sqrt(x2 + y2) * il2 - r1;
    return (Math.sqrt(x2 * a2 * il2) + yy * rr) * il2 - r1;
  };
}
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
const mix = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];

function surfaceNets(sdf, bmin, bmax, h) {
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
    const v0 = F[id(i, j, k)], inside = v0 < 0;
    if (inside !== (F[id(i + 1, j, k)] < 0)) quad(VI[id(i, j - 1, k - 1)], VI[id(i, j, k - 1)], VI[id(i, j, k)], VI[id(i, j - 1, k)], inside);
    if (inside !== (F[id(i, j + 1, k)] < 0)) quad(VI[id(i - 1, j, k - 1)], VI[id(i - 1, j, k)], VI[id(i, j, k)], VI[id(i, j, k - 1)], inside);
    if (inside !== (F[id(i, j, k + 1)] < 0)) quad(VI[id(i - 1, j - 1, k)], VI[id(i, j - 1, k)], VI[id(i, j, k)], VI[id(i - 1, j, k)], inside);
  }
  // normals from the distance itself, and the winding made to agree with them
  const nor = new Float32Array(pos.length), e = h * 0.5;
  for (let v = 0; v < pos.length; v += 3) {
    const x = pos[v], y = pos[v + 1], z = pos[v + 2];
    let gx = sdf(x + e, y, z) - sdf(x - e, y, z), gy = sdf(x, y + e, z) - sdf(x, y - e, z), gz = sdf(x, y, z + e) - sdf(x, y, z - e);
    const l = Math.hypot(gx, gy, gz) || 1; nor[v] = gx / l; nor[v + 1] = gy / l; nor[v + 2] = gz / l;
  }
  for (let t = 0; t < idx.length; t += 3) {
    const a = idx[t] * 3, b = idx[t + 1] * 3, c = idx[t + 2] * 3;
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2], wx = pos[c] - pos[a], wy = pos[c + 1] - pos[a + 1], wz = pos[c + 2] - pos[a + 2];
    const cx = uy * wz - uz * wy, cy = uz * wx - ux * wz, cz = ux * wy - uy * wx;
    if (cx * (nor[a] + nor[b] + nor[c]) + cy * (nor[a + 1] + nor[b + 1] + nor[c + 1]) + cz * (nor[a + 2] + nor[b + 2] + nor[c + 2]) < 0) { const s = idx[t + 1]; idx[t + 1] = idx[t + 2]; idx[t + 2] = s; }
  }
  return { pos: new Float32Array(pos), nor, idx };
}


// ———————————— more simple forms ————————————
const sph = (c, r) => (x, y, z) => Math.hypot(x - c[0], y - c[1], z - c[2]) - r;
const ell = (c, r) => ellipsoid(c[0], c[1], c[2], r[0], r[1], r[2]);
// a box with rounded edges, turned by yaw (about y) and roll (about z)
function rbox(c, h, r, yaw = 0, roll = 0, pitch = 0) {
  const cy = Math.cos(yaw), sy = Math.sin(yaw), cr = Math.cos(roll), sr = Math.sin(roll), cp = Math.cos(pitch), sp = Math.sin(pitch);
  return (x, y, z) => {
    let px = x - c[0], py = y - c[1], pz = z - c[2];
    let t = cy * px - sy * pz; pz = sy * px + cy * pz; px = t;
    t = cr * px + sr * py; py = -sr * px + cr * py; px = t;
    t = cp * py + sp * pz; pz = -sp * py + cp * pz; py = t;
    const qx = Math.abs(px) - h[0] + r, qy = Math.abs(py) - h[1] + r, qz = Math.abs(pz) - h[2] + r;
    return Math.hypot(Math.max(qx, 0), Math.max(qy, 0), Math.max(qz, 0)) + Math.min(Math.max(qx, qy, qz), 0) - r;
  };
}
// a ring around an axis ('x', 'y' or 'z')
function torus(c, R, r, ax = 'y') {
  return (x, y, z) => {
    const p = [x - c[0], y - c[1], z - c[2]], a = { x: 0, y: 1, z: 2 }[ax];
    const h = p[a], q = Math.hypot(p[(a + 1) % 3], p[(a + 2) % 3]) - R;
    return Math.hypot(q, h) - r;
  };
}
const inter = (f, g, k) => (x, y, z) => smax(f(x, y, z), g(x, y, z), k);
const cut = (f, g, k) => (x, y, z) => smax(f(x, y, z), -g(x, y, z), k);
// a cone standing on its base (a hat, a horn's stub); tip above
const capsule = (a, b, r) => cone(a, b, r, r);
// an upright cylinder with rounded edges
const cylY = (c, r, h) => (x, y, z) => { const dx = Math.hypot(x - c[0], z - c[2]) - r + 0.01, dy = Math.abs(y - c[1]) - h + 0.01; return Math.min(Math.max(dx, dy), 0) + Math.hypot(Math.max(dx, 0), Math.max(dy, 0)) - 0.01; };
// a curved horn: a chain of round cones along a quadratic curve
function horn(a, ctrl, tip, r0, r1, n = 6) {
  const pts = []; for (let i = 0; i <= n; i++) { const t = i / n; pts.push([0, 1, 2].map(k => (1 - t) * (1 - t) * a[k] + 2 * (1 - t) * t * ctrl[k] + t * t * tip[k])); }
  const segs = []; for (let i = 0; i < n; i++) segs.push(cone(pts[i], pts[i + 1], lerp(r0, r1, i / n), lerp(r0, r1, (i + 1) / n)));
  return (x, y, z) => { let d = 1e9; for (const s of segs) d = Math.min(d, s(x, y, z)); return d; };
}


export { lerp, clamp, smooth, smin, smax, ellipsoid, oell, cone, add, sub, mul, mix, surfaceNets, sph, ell, rbox, torus, inter, cut, capsule, cylY, horn };
