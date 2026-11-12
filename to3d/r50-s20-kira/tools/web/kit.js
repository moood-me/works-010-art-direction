// The С20 medium in JavaScript: styles/s20-soviet/tools/kit.py (the pen line with pressure and wobble, paint laid off
// register with gouache streaks, crayon, pencil hatching, paper) and the face parts of face.py (eye with its lid, brow,
// nose, mouth), ported so the 3D is drawn with the drawing's own hand. What is added for drawing on a moving 3D form:
//   ink(…, {raw, facing}) — a line given in picture points (a contour found on the 3D), with how much each point looks
//                           down-right (kit.py makes a closed outline heavier there; a contour knows its outside itself);
//   paintImage            — paint whose shape is a mask picture (a part of the 3D as it is seen) instead of a polygon:
//                           the same filter, the same shift off the line;
//   hatchImage            — pencil hatching clipped to a mask picture;
//   Doc.T                 — an affine frame (a face part's place on the turned head), set by the caller.
export const INK = '#1c1512', PAPER = '#f6eedd', SKIN = '#fbf4e6', BLUSH = '#e0574a';
const LIGHT_N = [0.55, 0.83];

export function rng(seed) {
  let a = (seed >>> 0) || 1;
  const f = () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  f.uniform = (lo, hi) => lo + (hi - lo) * f();
  f.int = () => Math.floor(f() * 1073741824);
  return f;
}

// ---------------------------------------------------------------- geometry (kit.py)
export function cr(pts, closed = false, n = 6) {
  let P = pts.slice();
  if (P.length < 2) return P;
  P = closed ? [P[P.length - 1], ...P, P[0], P[1]] : [P[0], ...P, P[P.length - 1]];
  const out = [];
  for (let i = 1; i < P.length - 2; i++) {
    const p0 = P[i - 1], p1 = P[i], p2 = P[i + 1], p3 = P[i + 2];
    const seg = Math.max(2, Math.floor(n * Math.max(1, Math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 18)));
    for (let k = 0; k < seg; k++) {
      const t = k / seg, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(j => 0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)));
    }
  }
  if (!closed) out.push(P[P.length - 2]);
  return out;
}
export function ell(cx, cy, rx, ry, n = 10, rot = 0, start = 0) {
  const c = Math.cos(rot), s = Math.sin(rot), pts = [];
  for (let i = 0; i < n; i++) { const a = start + 2 * Math.PI * i / n, x = rx * Math.cos(a), y = ry * Math.sin(a); pts.push([cx + x * c - y * s, cy + x * s + y * c]); }
  return pts;
}
export function arc(cx, cy, rx, ry, a0, a1, n = 8) {
  return Array.from({ length: n }, (_, i) => [cx + rx * Math.cos(a0 + (a1 - a0) * i / (n - 1)), cy + ry * Math.sin(a0 + (a1 - a0) * i / (n - 1))]);
}
const dOf = (pts, closed = true) => 'M' + pts.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L') + (closed ? 'Z' : '');

// ---------------------------------------------------------------- the document
// S: the picture's points per drawing unit of the figure (kit.py's scaled(s)); T, Sc: the frame local points are in
export class Doc {
  constructor(w, h, S, seed = 1) {
    this.w = w; this.h = h; this.S = S; this.seed = seed * 7919 + 13; this.lw = 1;
    this.under = []; this.paints = []; this.items = [];
    this.T = [1, 0, 0, 1, 0, 0]; this.Sc = S;
  }
  tp(pts) { const [a, b, c, d, e, f] = this.T; return pts.map(([x, y]) => [a * x + c * y + e, b * x + d * y + f]); }
  rnd(seed) { return rng(seed == null ? (this.seed += 7919) : seed * 7919 + 13); }
}
const LWF = d => Math.pow(d.Sc, 0.55);            // a line's width in the picture for width 1 in units: kit.py's lw · LWF · s

// ---------------------------------------------------------------- the ink line (kit.py ink)
export function ink(d, pts, o = {}) {
  const { lw = 2.2, closed = false, taper = 0.22, weight = 0.55, wob = 0.45, smooth = true, color = INK, op = 1, press = null,
    seed = null, raw = false, facing = null } = o;
  const r = d.rnd(seed);
  let P = raw ? pts : d.tp(smooth ? cr(pts, closed) : (closed ? [...pts, pts[0]] : pts));
  if (P.length < 2) return;
  const W = lw * LWF(d) * d.lw, n = P.length;
  let CX = 0, CY = 0; for (const p of P) { CX += p[0]; CY += p[1]; } CX /= n; CY /= n;
  const L = [0]; for (let i = 1; i < n; i++) L.push(L[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]));
  const tot = L[n - 1] || 1;
  const amp = wob * 1.4 * LWF(d) * d.lw, ph = [r.uniform(0, 6.28), r.uniform(0, 6.28), r.uniform(0, 6.28)], lam = [55 * d.Sc, 23 * d.Sc, 140 * d.Sc];
  const left = [], right = [];
  for (let k = 0; k < n; k++) {
    const a = closed ? P[(k - 1 + n) % n] : P[Math.max(0, k - 1)], b = closed ? P[(k + 1) % n] : P[Math.min(n - 1, k + 1)];
    const dx = b[0] - a[0], dy = b[1] - a[1], ln = Math.hypot(dx, dy) || 1, nx = -dy / ln, ny = dx / ln, t = L[k] / tot;
    let w = W;
    if (!closed) { const e = Math.min(t, 1 - t); if (taper > 0 && e < taper) w *= 0.25 + 0.75 * Math.sin(0.5 * Math.PI * e / taper); }
    let fc = 0.35;
    if (facing) fc = facing[k];
    else if (closed) { const vx = P[k][0] - CX, vy = P[k][1] - CY, sg = vx * nx + vy * ny > 0 ? 1 : -1; fc = Math.max(0, sg * (nx * LIGHT_N[0] + ny * LIGHT_N[1])); }
    w *= 1 + weight * fc;
    if (press) { const f = t * (press.length - 1), j = Math.min(Math.floor(f), press.length - 2); w *= press[j] + (press[j + 1] - press[j]) * (f - j); }
    const s = L[k], ob = amp * (0.55 * Math.sin(6.283 * s / lam[0] + ph[0]) + 0.3 * Math.sin(6.283 * s / lam[1] + ph[1]) + 0.4 * Math.sin(6.283 * s / lam[2] + ph[2]));
    const cx = P[k][0] + nx * ob, cy = P[k][1] + ny * ob;
    left.push([cx + nx * w / 2, cy + ny * w / 2]); right.push([cx - nx * w / 2, cy - ny * w / 2]);
  }
  const at = op === 1 ? '' : ` opacity="${op.toFixed(2)}"`;
  if (closed) d.items.push(`<path d="${dOf(left)} ${dOf(right)}" fill="${color}" fill-rule="evenodd"${at}/>`);
  else d.items.push(`<path d="${dOf(left.concat(right.reverse()))}" fill="${color}"${at}/>`);
}
export function dot(d, x, y, r, color = INK) {
  const rr = r * Math.pow(d.Sc, -0.135);
  d.items.push(`<path d="${dOf(d.tp(ell(x, y, rr, rr * 1.08, 12)))}" fill="${color}"/>`);
}
// a flat patch (the white of an eye, a lid, the mouth's inside): no texture, on the line
export function paint(d, pts, color, o = {}) {
  const { smooth = true, op = 1 } = o;
  d.items.push(`<path d="${dOf(d.tp(smooth ? cr(pts, true) : pts))}" fill="${color}"${op === 1 ? '' : ` opacity="${op.toFixed(2)}"`}/>`);
}
export function blush(d, x, y, rx, op = 0.85, color = BLUSH) {
  d.items.push(`<path d="${dOf(d.tp(ell(x, y, rx, rx * 0.8, 14)))}" fill="${color}" opacity="${op.toFixed(2)}" filter="url(#rub)"/>`);
}

// ---------------------------------------------------------------- paint and hatching from mask pictures
// kit.py OFF(): the paint's shift off the line
export const OFF = d => { const k = 2.6 * Math.pow(d.S, 0.45); return [k, -0.7 * k]; };
export function paintImage(d, href, box, o = {}) {
  const { tex = 'brush', off = true, op = 1, under = false } = o;
  const [dx, dy] = off ? OFF(d) : [0, 0], [x, y, w, h] = box;
  (under ? d.under : d.paints).push(`<image href="${href}" x="${(x + dx).toFixed(1)}" y="${(y + dy).toFixed(1)}" width="${w}" height="${h}" preserveAspectRatio="none"` +
    `${tex === 'flat' ? '' : ` filter="url(#${tex})"`}${op === 1 ? '' : ` opacity="${op}"`}/>`);
}
let hatchN = 0;
export function hatchImage(d, href, box, o = {}) {
  const { color = INK, angle = -0.9, step = 5, lw = 0.8, op = 0.55, jitter = 0.25, seed = 5 } = o;
  const r = d.rnd(seed), [x, y, w, h] = box, [dx, dy] = OFF(d);
  const cx = x + w / 2, cy = y + h / 2, R = Math.hypot(w, h) / 2 + 4, c = Math.cos(angle), s = Math.sin(angle);
  const st = step * Math.pow(d.S, 0.73) * d.lw; let k = -R, path = '';       // kit.py: step · LWF^0.6 units
  while (k < R) {
    const j1 = r.uniform(-jitter, jitter) * R * 0.3, j2 = r.uniform(-jitter, jitter) * R * 0.3;
    path += `M${(cx - c * R - s * k + c * j1).toFixed(1)} ${(cy - s * R + c * k + s * j1).toFixed(1)}L${(cx + c * R - s * k + c * j2).toFixed(1)} ${(cy + s * R + c * k + s * j2).toFixed(1)}`;
    k += st * r.uniform(0.8, 1.25);
  }
  const id = 'hm' + (hatchN++ % 64);
  d.paints.push(`<mask id="${id}" maskUnits="userSpaceOnUse" x="${x}" y="${y}" width="${w}" height="${h}"><image href="${href}" x="${(x + dx).toFixed(1)}" y="${(y + dy).toFixed(1)}" width="${w}" height="${h}" preserveAspectRatio="none"/></mask>` +
    `<g mask="url(#${id})"><path d="${path}" stroke="${color}" stroke-width="${(lw * LWF(d) * d.lw).toFixed(2)}" fill="none" stroke-linecap="round" opacity="${op}" filter="url(#pencil)"/></g>`);
}
// the dry-brush strip under the feet (build.py shadow())
export function ground(d, x, y, rx, ry, color = '#2a3a10', op = 0.35) {
  d.under.push(`<path d="${dOf(cr(ell(x, y, rx, ry, 12), true))}" fill="${color}" opacity="${op}" filter="url(#crayon)"/>`);
}

// ---------------------------------------------------------------- filters (kit.py _filters, in the picture's points)
function defs(S) {
  const f = v => (v / S / S).toFixed(5);
  return `<filter id="brush" x="-5%" y="-5%" width="110%" height="110%">
<feTurbulence type="fractalNoise" baseFrequency="${f(0.035)}" numOctaves="2" seed="3" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="3.2" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feTurbulence type="fractalNoise" baseFrequency="${f(0.006)} ${f(0.045)}" numOctaves="2" seed="8" result="t"/>
<feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.6 1.45" result="tm"/>
<feComposite in="tm" in2="d" operator="in" result="streak"/>
<feComponentTransfer in="streak" result="st"><feFuncA type="linear" slope="0.20"/></feComponentTransfer>
<feMerge><feMergeNode in="d"/><feMergeNode in="st"/></feMerge></filter>
<filter id="crayon" x="-5%" y="-5%" width="110%" height="110%">
<feTurbulence type="fractalNoise" baseFrequency="${f(0.04)}" numOctaves="2" seed="4" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="3.0" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feTurbulence type="fractalNoise" baseFrequency="${f(0.55)} ${f(0.9)}" numOctaves="2" seed="11" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 4.5 -1.55" result="gm"/>
<feComposite in="d" in2="gm" operator="in"/></filter>
<filter id="rub" x="-30%" y="-30%" width="160%" height="160%">
<feGaussianBlur in="SourceGraphic" stdDeviation="1.6" result="b"/>
<feTurbulence type="fractalNoise" baseFrequency="${f(0.5)}" numOctaves="2" seed="21" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 4 -1.4" result="gm"/>
<feComposite in="b" in2="gm" operator="in"/></filter>
<filter id="pencil" x="-5%" y="-5%" width="110%" height="110%">
<feTurbulence type="fractalNoise" baseFrequency="${f(0.7)}" numOctaves="2" seed="31" result="g"/>
<feDisplacementMap in="SourceGraphic" in2="g" scale="1.4" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 3 -0.9" result="gm"/>
<feComposite in="d" in2="gm" operator="in"/></filter>
<filter id="paper" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="2" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.28  0 0 0 0 0.18  0 0 0 -1.3 0.75"/></filter>
<filter id="fibre" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.008 0.011" numOctaves="3" seed="12" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.36  0 0 0 0 0.22  0 0 0 -1.4 0.82"/></filter>`;
}
// the whole picture: one bright field, what lies under the figure, paint, then line and face in the order drawn, grain
export function svg(d, bg, grain = true) {
  const g = grain ? `<rect width="${d.w}" height="${d.h}" filter="url(#paper)" opacity="0.32" style="mix-blend-mode:multiply"/>` +
    `<rect width="${d.w}" height="${d.h}" filter="url(#fibre)" opacity="0.16" style="mix-blend-mode:multiply"/>` : '';
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${d.w}" height="${d.h}" viewBox="0 0 ${d.w} ${d.h}"><defs>${defs(d.S)}</defs>` +
    `<rect width="${d.w}" height="${d.h}" fill="${bg}"/>${d.under.join('')}${d.paints.join('')}${d.items.join('')}${g}</svg>`;
}

// ---------------------------------------------------------------- the face parts (face.py Head), in head units
// e: brow, tilt, lid, look [x, y], wide (0…1: the round eye of surprise), mouth, curve, open
export function eye(d, x, y, r0, e, side, o = {}) {
  const { lw = 2.3, skin = SKIN, profile = 0, seed = 1 } = o;
  const wide = e.wide || 0, r = r0 * (1 + 0.25 * wide), rx = r * (0.9 - 0.08 * profile), ry = r * 1.08, l = lw * 0.8;
  const ring = ell(x, y, rx, ry, 12), lid = Math.min(1, e.lid || 0);
  paint(d, ring, '#fffaf0');
  const pr = r * (0.42 - 0.12 * wide);
  dot(d, x + e.look[0] * (rx - pr), y + e.look[1] * (ry - pr) * 0.8, pr);
  if (lid > 0.03) {
    const yl = y - ry + 2 * ry * lid;
    paint(d, [[x - rx - 2, y - ry - 3], [x + rx + 2, y - ry - 3], [x + rx + 2, yl], [x - rx - 2, yl]], skin, { smooth: false });
    if (lid < 0.5) ink(d, arc(x, y, rx, ry, Math.PI, 2 * Math.PI, 9).slice(1, -1), { lw: l * 0.7, taper: 0.4, seed });
    ink(d, [[x - rx * 1.15, yl + 0.5], [x, yl - 0.6], [x + rx * 1.15, yl + 0.5]], { lw: lw * 1.05, seed: seed + 1 });
    if (lid < 0.93) ink(d, arc(x, y, rx, ry, 0, Math.PI, 9), { lw: l * 0.85, taper: 0.3, seed: seed + 2 });
  } else ink(d, ring, { lw: l, closed: true, weight: 0.6, seed });
}
export function brow(d, x, y, e, side, o = {}) {
  const { len = 9, lw = 3.2, k = 1, seed = 1 } = o;
  const L = len * k, t = e.tilt * side, b = e.brow, angIn = -t * L * 0.9;
  let pts = [[x - side * L, y + b], [x, y + b - 1.5 - angIn * 0.5], [x + side * L * 0.95, y + b - angIn]];
  if (side < 0) pts = pts.reverse();
  ink(d, pts, { lw, taper: 0.35, weight: 0.2, seed });
}
// the nose (face.py nose_draw 'button'): u — how far the face is turned (0: to us, 1: three quarters and on); it lies
// over the contour, so it is given a patch of skin first
export function nose(d, x0, y, s, u, o = {}) {
  const { lw = 2.3, skin = SKIN, seed = 1 } = o;
  const F = [[1.2, -7], [2.4, -3.2], [4, 2], [0.5, 4], [-3, 3]], T3 = [[-3, -8], [3, -1], [7, 4], [2, 6.5], [-3, 5]];
  const pts = F.map((p, i) => [x0 + s * (p[0] + (T3[i][0] - p[0]) * u), y + s * (p[1] + (T3[i][1] - p[1]) * u)]);
  if (u > 0.3) paint(d, pts, skin, { op: Math.min(1, (u - 0.3) / 0.3) });
  ink(d, pts, { lw, taper: 0.25 + 0.05 * (1 - u), seed });
}
export function mouth(d, x0, y, w, e, o = {}) {
  const { lw = 2.3, seed = 1 } = o;
  const xl = x0 - w, xr = x0 + w, xm = (xl + xr) / 2, c = e.curve || 0;
  if (e.talk != null) {       // speech: the closed line opening into the drawing's dark mouth with the band of teeth
    const op = e.talk, rd = e.round || 0, hw = w * (1 - 0.35 * rd) + (e.dw || 0), h = w * 1.5 * op * (1 + 0.2 * rd);
    if (op < 0.07) { ink(d, [[x0 - hw, y + 1], [x0, y + 1.2], [x0 + hw, y - 1.5]], { lw, taper: 0.35, seed }); return; }
    const top = [[x0 - hw, y - 0.5], [x0, y - 1 - rd], [x0 + hw, y - 1.5]], bot = [[x0 + hw * 0.8, y + h * 0.6], [x0, y + h], [x0 - hw * 0.8, y + h * 0.55]];
    const pts = top.concat(bot);
    paint(d, pts, '#5a1e1a');
    if (op > 0.3 && rd < 0.5) paint(d, [[x0 - hw + 1, y], [x0 + hw - 1, y - 1], [x0 + hw - 1.5, y + h * 0.22], [x0 - hw + 1.5, y + h * 0.25]], '#fffaf0', { smooth: false });
    ink(d, pts, { lw, closed: true, weight: 0.7, seed });
    return;
  }
  if (e.mouth === 'smirk') return ink(d, [[xl, y + 1.5], [xm, y + 1], [xr, y - 4], [xr + 2, y - 5.5]], { lw, taper: 0.35, seed });
  if (e.mouth === 'line') return ink(d, [[xl, y - c * 4], [xm, y + c * 3], [xr, y - c * 4]], { lw, taper: 0.35, seed });
  if (e.mouth === 'o') {
    const pts = ell(xm, y + 3, w * 0.38, w * 0.45 * (0.6 + (e.open ?? 0.8)), 10);
    paint(d, pts, '#5a1e1a'); return ink(d, pts, { lw, closed: true, seed });
  }
  const h = w * 0.9 * (e.open ?? 0.7);         // 'teeth': anger
  const pts = [[xl, y - 2], [xm, y + 1], [xr, y - 3], [xr - 1, y + h * 0.6], [xm, y + h * 0.75], [xl + 1, y + h * 0.5]];
  paint(d, pts, '#5a1e1a');
  paint(d, [[xl + 1, y - 1], [xr - 1, y - 2], [xr - 1, y + h * 0.55], [xl + 1, y + h * 0.48]], '#fffaf0', { smooth: false });
  ink(d, [[xm, y + 0.5], [xm + 0.3, y + h * 0.65]], { lw: lw * 0.5, seed: seed + 1 });
  ink(d, [[xl, y + h * 0.27], [xr, y + h * 0.22]], { lw: lw * 0.5, seed: seed + 2 });
  ink(d, pts, { lw, closed: true, seed });
}
