// Small math on plain arrays (no three.js): vectors [x, y, z], quaternions [x, y, z, w] (unit, rotating v as q v q*),
// kept in flat typed arrays by the other modules (a joint j's quaternion at j*4). Everything the engine computes
// runs in a browser and in node alike.

export const qId = () => [0, 0, 0, 1];

export function qMul(a, b, out = [0, 0, 0, 0]) {
  const [ax, ay, az, aw] = a, [bx, by, bz, bw] = b;
  out[0] = aw * bx + ax * bw + ay * bz - az * by;
  out[1] = aw * by - ax * bz + ay * bw + az * bx;
  out[2] = aw * bz + ax * by - ay * bx + az * bw;
  out[3] = aw * bw - ax * bx - ay * by - az * bz;
  return out;
}
export const qConj = q => [-q[0], -q[1], -q[2], q[3]];
export function qNorm(q) { const l = Math.hypot(q[0], q[1], q[2], q[3]) || 1; return [q[0] / l, q[1] / l, q[2] / l, q[3] / l]; }
export function qRot(q, v, out = [0, 0, 0]) {
  const [x, y, z, w] = q, [vx, vy, vz] = v;
  const tx = 2 * (y * vz - z * vy), ty = 2 * (z * vx - x * vz), tz = 2 * (x * vy - y * vx);
  out[0] = vx + w * tx + y * tz - z * ty; out[1] = vy + w * ty + z * tx - x * tz; out[2] = vz + w * tz + x * ty - y * tx;
  return out;
}
// the same on a vector given by its parts (nothing allocated)
export function qRot3(q, vx, vy, vz, out) {
  const x = q[0], y = q[1], z = q[2], w = q[3];
  const tx = 2 * (y * vz - z * vy), ty = 2 * (z * vx - x * vz), tz = 2 * (x * vy - y * vx);
  out[0] = vx + w * tx + y * tz - z * ty; out[1] = vy + w * ty + z * tx - x * tz; out[2] = vz + w * tz + x * ty - y * tx;
  return out;
}
export function qAxisAngle(axis, a) { const l = Math.hypot(...axis) || 1, s = Math.sin(a / 2) / l; return [axis[0] * s, axis[1] * s, axis[2] * s, Math.cos(a / 2)]; }
// the smallest turn carrying unit direction a to unit direction b (into out, if given)
export function qBetween(a, b, out = [0, 0, 0, 0]) {
  const d = a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  if (d < -0.999999) { const ax = Math.abs(a[0]) < 0.9 ? cross(a, [1, 0, 0]) : cross(a, [0, 1, 0]), q = qAxisAngle(ax, Math.PI); for (let k = 0; k < 4; k++) out[k] = q[k]; return out; }
  const cx = a[1] * b[2] - a[2] * b[1], cy = a[2] * b[0] - a[0] * b[2], cz = a[0] * b[1] - a[1] * b[0], w = 1 + d, l = Math.hypot(cx, cy, cz, w) || 1;
  out[0] = cx / l; out[1] = cy / l; out[2] = cz / l; out[3] = w / l; return out;
}
export function qSlerp(a, b, t, out = [0, 0, 0, 0]) {
  let bx = b[0], by = b[1], bz = b[2], bw = b[3], c = a[0] * bx + a[1] * by + a[2] * bz + a[3] * bw;
  if (c < 0) { bx = -bx; by = -by; bz = -bz; bw = -bw; c = -c; }
  let ka = 1 - t, kb = t;
  if (c <= 0.9995) { const th = Math.acos(c), s = Math.sin(th); ka = Math.sin((1 - t) * th) / s; kb = Math.sin(t * th) / s; }
  out[0] = a[0] * ka + bx * kb; out[1] = a[1] * ka + by * kb; out[2] = a[2] * ka + bz * kb; out[3] = a[3] * ka + bw * kb;
  if (c > 0.9995) { const l = Math.hypot(out[0], out[1], out[2], out[3]) || 1; for (let k = 0; k < 4; k++) out[k] /= l; }
  return out;
}
// a turn taken t times (t < 1 less of it, t > 1 more): about the same axis
export function qPow(q, t) {
  const w = Math.max(-1, Math.min(1, q[3])), sgn = w < 0 ? -1 : 1, a = 2 * Math.acos(w * sgn), s = Math.sqrt(Math.max(0, 1 - w * w));
  if (s < 1e-8) return qId();
  return qAxisAngle([q[0] * sgn / s, q[1] * sgn / s, q[2] * sgn / s], a * t);
}
// the part of q that swings the direction d (unit) away — q = swing · twist, twist about d
export function qSwing(q, d) { return qBetween(d, normalize(qRot(q, d))); }
export const qAngle = q => 2 * Math.acos(Math.min(1, Math.abs(q[3])));
// rotation matrix, row by row (9)
export function qMat(q, out = new Array(9)) {
  const [x, y, z, w] = q;
  out[0] = 1 - 2 * (y * y + z * z); out[1] = 2 * (x * y - z * w); out[2] = 2 * (x * z + y * w);
  out[3] = 2 * (x * y + z * w); out[4] = 1 - 2 * (x * x + z * z); out[5] = 2 * (y * z - x * w);
  out[6] = 2 * (x * z - y * w); out[7] = 2 * (y * z + x * w); out[8] = 1 - 2 * (x * x + y * y);
  return out;
}

export const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
export const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
export const scale = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
export const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
export const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
export const len = a => Math.hypot(a[0], a[1], a[2]);
export const normalize = a => { const l = len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
export const lerp = (a, b, t) => a + (b - a) * t;
export const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
// smoothstep on 0..1
export const sst = t => t <= 0 ? 0 : t >= 1 ? 1 : t * t * (3 - 2 * t);
// the smooth minimum of two distances over k (Inigo Quilez's polynomial; k ≤ 0: the plain minimum)
export function smin(a, b, k) { if (k <= 0) return Math.min(a, b); const h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * 0.25; }

// typed-array access: the j-th quaternion or vector
export const getQ = (A, j) => [A[j * 4], A[j * 4 + 1], A[j * 4 + 2], A[j * 4 + 3]];
export const setQ = (A, j, q) => { A[j * 4] = q[0]; A[j * 4 + 1] = q[1]; A[j * 4 + 2] = q[2]; A[j * 4 + 3] = q[3]; };
export const getV = (A, j) => [A[j * 3], A[j * 3 + 1], A[j * 3 + 2]];
export const setV = (A, j, v) => { A[j * 3] = v[0]; A[j * 3 + 1] = v[1]; A[j * 3 + 2] = v[2]; };

// a smooth warp through points (src → dst): biharmonic radial basis (|r|) plus an affine part — as a function
// (x, y, z, out) → the move there
export function biharmonic(src, dst) {
  const n = src.length, m = n + 4, A = Array.from({ length: m }, () => new Float64Array(m)), B = [0, 1, 2].map(() => new Float64Array(m));
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) A[i][j] = Math.hypot(src[i][0] - src[j][0], src[i][1] - src[j][1], src[i][2] - src[j][2]);
    A[i][n] = 1; A[i][n + 1] = src[i][0]; A[i][n + 2] = src[i][1]; A[i][n + 3] = src[i][2];
    for (let k = 0; k < 4; k++) A[n + k][i] = A[i][n + k];
    for (let c = 0; c < 3; c++) B[c][i] = dst[i][c] - src[i][c];
  }
  const W = B.map(b => solve(A, b)), S = Float64Array.from(src.flat());
  return (x, y, z, out = [0, 0, 0]) => {
    for (let c = 0; c < 3; c++) {
      const w = W[c]; let v = w[n] + w[n + 1] * x + w[n + 2] * y + w[n + 3] * z;
      for (let i = 0; i < n; i++) v += w[i] * Math.hypot(x - S[i * 3], y - S[i * 3 + 1], z - S[i * 3 + 2]);
      out[c] = v;
    }
    return out;
  };
}
// Gauss–Jordan with partial pivoting
export function solve(A0, b0) {
  const m = A0.length, a = A0.map(r => Float64Array.from(r)), b = Float64Array.from(b0);
  for (let i = 0; i < m; i++) {
    let p = i; for (let r = i + 1; r < m; r++) if (Math.abs(a[r][i]) > Math.abs(a[p][i])) p = r;
    [a[i], a[p]] = [a[p], a[i]]; [b[i], b[p]] = [b[p], b[i]];
    const d = a[i][i] || 1e-12;
    for (let r = 0; r < m; r++) { if (r === i) continue; const f = a[r][i] / d; if (!f) continue; for (let c = i; c < m; c++) a[r][c] -= f * a[i][c]; b[r] -= f * b[i]; }
  }
  return Float64Array.from(b, (v, i) => v / (a[i][i] || 1e-12));
}
