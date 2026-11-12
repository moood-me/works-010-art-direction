// The С18 kit on a canvas: styles/s18-manga/tools/pen.py ported (stroke — a pen line with pressure; the weight of a
// contour by the light; screentone as dots on a 45° grid), so the 3D is drawn with the drawing's own pen and tone.
export const INK = '#111111', PAPER = '#fbfaf6';
export const INK_RGB = [17, 17, 17], PAPER_RGB = [251, 250, 246];
export const LIGHT = [-0.55, -0.83];       // on the page: the light comes from the upper left
export const PITCH = 4.6;                  // dot pitch of the tone at the drawing's own sizes

export function catmull(pts, closed = false, n = 7) {
  if (pts.length < 3) {
    if (pts.length === 2) { const [a, b] = pts, out = []; for (let i = 0; i <= n; i++) out.push([a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n]); return out; }
    return pts.map(p => [p[0], p[1]]);
  }
  let P = pts.map(p => [p[0], p[1]]);
  if (closed) P = [P[P.length - 1], ...P, P[0], P[1]];
  else P = [[2 * P[0][0] - P[1][0], 2 * P[0][1] - P[1][1]], ...P, [2 * P[P.length - 1][0] - P[P.length - 2][0], 2 * P[P.length - 1][1] - P[P.length - 2][1]]];
  const out = [];
  for (let i = 1; i < P.length - 2; i++) {
    const p0 = P[i - 1], p1 = P[i], p2 = P[i + 1], p3 = P[i + 2];
    for (let k = 0; k < n; k++) {
      const t = k / n, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(j => 0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)));
    }
  }
  if (!closed) out.push(P[P.length - 2]);
  return out;
}
const wfun = w => {
  if (typeof w === 'function') return w;
  if (Array.isArray(w)) return t => { const x = t * (w.length - 1), i = Math.min(Math.floor(x), w.length - 2); return w[i] + (w[i + 1] - w[i]) * (x - i); };
  return () => w;
};
export function fillPoly(ctx, pts, fill) {
  if (pts.length < 3) return;
  ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  ctx.closePath(); ctx.fillStyle = fill; ctx.fill();
}
// a pen line with pressure: a filled band along a smooth centre line, thin at both ends (pen.py stroke)
export function stroke(ctx, pts, w = 1.6, o = {}) {
  const taper = o.taper || [0.18, 0.22], smooth = o.smooth !== false;
  let c = smooth && pts.length > 2 ? catmull(pts, false, o.n || 7) : pts.map(p => [p[0], p[1]]);
  if (c.length < 2) return;
  if (c.length === 2) c = [0, 1, 2, 3, 4].map(i => [c[0][0] + (c[1][0] - c[0][0]) * i / 4, c[0][1] + (c[1][1] - c[0][1]) * i / 4]);
  const L = [0]; for (let i = 1; i < c.length; i++) L.push(L[i - 1] + Math.hypot(c[i][0] - c[i - 1][0], c[i][1] - c[i - 1][1]));
  const tot = L[L.length - 1] || 1, wf = wfun(w), [a, b] = taper, left = [], right = [];
  for (let i = 0; i < c.length; i++) {
    const p0 = c[Math.max(i - 1, 0)], p1 = c[Math.min(i + 1, c.length - 1)];
    const dx = p1[0] - p0[0], dy = p1[1] - p0[1], l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l;
    const t = L[i] / tot; let k = 1;
    if (a > 0 && t < a) k = 0.12 + 0.88 * Math.sin(t / a * Math.PI / 2);
    if (b > 0 && t > 1 - b) k = Math.min(k, 0.08 + 0.92 * Math.sin((1 - t) / b * Math.PI / 2));
    const hw = wf(t) * k / 2;
    left.push([c[i][0] + nx * hw, c[i][1] + ny * hw]); right.push([c[i][0] - nx * hw, c[i][1] - ny * hw]);
  }
  fillPoly(ctx, left.concat(right.reverse()), o.fill || INK);
}
// a closed contour whose weight follows the light (pen.py outline)
export function outline(ctx, pts, w = 2.2, k = 0.75, o = {}) {
  const c = pts, n = c.length;
  let area = 0; for (let i = 0; i < n; i++) area += c[i][0] * c[(i + 1) % n][1] - c[(i + 1) % n][0] * c[i][1];
  const sgn = area > 0 ? 1 : -1, ws = [];
  for (let i = 0; i < n; i++) {
    const a = c[(i - 1 + n) % n], b = c[(i + 1) % n], dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1;
    const d = (-dy / l * LIGHT[0] + dx / l * LIGHT[1]) * sgn;
    ws.push(Math.max(o.wmin ?? 0.35, w * (1 + k * d)));
  }
  stroke(ctx, c.concat([c[0]]), ws.concat([ws[0]]), { taper: [0.04, 0.04], smooth: false, fill: o.fill });
}
// screentone inside a clip: dots of a 45° grid (levels from 0.7 up: white dots on black)
export function toneFill(ctx, clipPts, level, pitch = PITCH) {
  if (clipPts.length < 3) return;
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const [x, y] of clipPts) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
  ctx.save(); ctx.beginPath(); ctx.moveTo(clipPts[0][0], clipPts[0][1]); for (const p of clipPts) ctx.lineTo(p[0], p[1]); ctx.closePath(); ctx.clip();
  const dark = level >= 0.7, r = Math.sqrt((dark ? 1 - level : level) * pitch * pitch / Math.PI), q = Math.SQRT1_2;
  if (dark) { ctx.fillStyle = INK; ctx.fillRect(x0 - 1, y0 - 1, x1 - x0 + 2, y1 - y0 + 2); }
  ctx.fillStyle = dark ? PAPER : INK; ctx.beginPath();
  const us = [(x0 + y0) * q, (x1 + y1) * q], vs = [(x0 - y1) * q, (x1 - y0) * q];
  for (let i = Math.floor(us[0] / pitch); i <= Math.ceil(us[1] / pitch); i++) for (let j = Math.floor(vs[0] / pitch); j <= Math.ceil(vs[1] / pitch); j++) {
    const u = (i + 0.5) * pitch, v = (j + 0.5) * pitch, x = (u + v) * q, y = (u - v) * q;
    if (x < x0 - r || x > x1 + r || y < y0 - r || y > y1 + r) continue;
    ctx.moveTo(x + r, y); ctx.arc(x, y, r, 0, 6.2832);
  }
  ctx.fill(); ctx.restore();
}
// how much ink a pixel of a flat tone gets (the same grid as toneFill), 0…1
export function toneAt(x, y, level, pitch = PITCH) {
  if (level <= 0) return 0; if (level >= 1) return 1;
  const q = Math.SQRT1_2, u = (x + y) * q / pitch, v = (x - y) * q / pitch;
  const du = (u - Math.floor(u) - 0.5) * pitch, dv = (v - Math.floor(v) - 0.5) * pitch, d = Math.hypot(du, dv);
  if (level >= 0.7) { const r = Math.sqrt((1 - level) * pitch * pitch / Math.PI); return 1 - Math.max(0, Math.min(1, r - d + 0.5)); }
  const r = Math.sqrt(level * pitch * pitch / Math.PI);
  return Math.max(0, Math.min(1, r - d + 0.5));
}
