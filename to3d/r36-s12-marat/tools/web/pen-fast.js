// The С12 medium in JavaScript: styles/s12-ink-watercolour/tools/kit.py (pen and watercolour as SVG) and the face
// parts of parts.py (eye, brow, mouth, extra), ported line by line so the 3D is drawn with the drawing's own pen.
// Two additions for drawing on a moving 3D form:
//   Doc.map  — after the affine stack, a point may be carried further (onto the 3D face and into the picture) or
//              hidden (null: behind the head, under the hair); a pen stroke is split where its points are hidden.
//   washImage — a wash whose shape is a mask picture (a part of the 3D as it is seen) instead of a polygon: the same
//              watercolour filter, the same offset off the line.
// This is pen.js's fast variant (pen.js beside it is as it was): a stroke's noise is not worked out in advance (four
// tables of 512 random numbers for every stroke) — a number of a table is worked out when the stroke asks for it. The
// numbers are the same, so the strokes are.
export const INK = '#211c19', PAPER = '#fdfaf3';

// ---------------------------------------------------------------- random, noise
export function rng(seed) {
  let a = (seed >>> 0) || 1;
  const at = a => { let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const f = () => { a = (a + 0x6D2B79F5) >>> 0; return at(a); };
  // the next n numbers, taken but not worked out: the function gives the i-th of them (what the i-th call would have)
  f.take = n => { const a0 = a; a = (a + Math.imul(n, 0x6D2B79F5)) >>> 0; return i => at((a0 + Math.imul(i + 1, 0x6D2B79F5)) >>> 0); };
  f.uniform = (lo, hi) => lo + (hi - lo) * f();
  f.int = () => Math.floor(f() * 1073741824);
  f.choice = arr => arr[Math.floor(f() * arr.length)];
  return f;
}
class Noise1 {
  constructor(r, period) { const u = r.take(512); this.r = i => -1 + 2 * u(i); this.p = period; }
  at(s) { const x = s / this.p, i = Math.floor(x); let f = x - i; f = f * f * (3 - 2 * f); return this.r(((i % 512) + 512) % 512) * (1 - f) + this.r((((i + 1) % 512) + 512) % 512) * f; }
}

// ---------------------------------------------------------------- geometry
export function catmull(pts, closed = false, step = 2.0) {
  if (pts.length < 2) return pts.slice();
  let P = pts.slice();
  if (closed) P = [P[P.length - 1], ...P, P[0], P[1]];
  else P = [[2 * P[0][0] - P[1][0], 2 * P[0][1] - P[1][1]], ...P, [2 * P[P.length - 1][0] - P[P.length - 2][0], 2 * P[P.length - 1][1] - P[P.length - 2][1]]];
  const out = [];
  for (let i = 1; i < P.length - 2; i++) {
    const p0 = P[i - 1], p1 = P[i], p2 = P[i + 1], p3 = P[i + 2];
    const n = Math.max(2, Math.floor(Math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step));
    for (let k = 0; k < n; k++) {
      const t = k / n, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(j => 0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)));
    }
  }
  out.push(P[P.length - 2]);
  return out;
}
const fmt = pts => pts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ');

// ---------------------------------------------------------------- the document
export class Doc {
  constructor(w, h, seed = 1) {
    this.w = w; this.h = h; this.rnd = rng(seed);
    this.washes = []; this.whites = []; this.inks = [];
    this.T = [[1, 0, 0, 1, 0, 0]]; this.lw = 1.0; this.fade = null; this.map = null; this.origin = [0, 0];
  }
  push(dx = 0, dy = 0, s = 1, rot = 0, flip = false) {
    const [a, b, c, d, e, f] = this.T[this.T.length - 1];
    const cs = Math.cos(rot * Math.PI / 180), sn = Math.sin(rot * Math.PI / 180), sx = flip ? -s : s;
    const m = [cs * sx, sn * sx, -sn * s, cs * s, dx, dy];
    this.T.push([a * m[0] + c * m[1], b * m[0] + d * m[1], a * m[2] + c * m[3], b * m[2] + d * m[3], a * m[4] + c * m[5] + e, b * m[4] + d * m[5] + f]);
  }
  pop() { this.T.pop(); }
  // local points → the picture; with a map, runs of visible points (a hidden point splits the line)
  runs(pts) {
    const [a, b, c, d, e, f] = this.T[this.T.length - 1];
    const P = pts.map(([x, y]) => [a * x + c * y + e, b * x + d * y + f]);
    if (!this.map) return [P];
    const out = []; let cur = [];
    for (const p of P) { const q = this.map(p[0], p[1]); if (q) cur.push(q); else { if (cur.length) out.push(cur); cur = []; } }
    if (cur.length) out.push(cur);
    return out;
  }
  tp(pts) { const r = this.runs(pts); return r.length === 1 && r[0].length === pts.length ? r[0] : null; }
}

// the whole picture as SVG; the washes and the ink are put in a group moved with the figure (so the paper's grain and
// the pigment's streaks travel with her, not stay on the screen)
export function svg(d, defsId = '') {
  const [ox, oy] = d.origin;
  const fade = d.fade ? fadeDefs(d) : '';
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${d.w} ${d.h}" width="${d.w}" height="${d.h}"><defs>${DEFS}</defs>` +
    `<rect width="${d.w}" height="${d.h}" fill="${PAPER}"/><rect width="${d.w}" height="${d.h}" filter="url(#paper)" opacity="0.5"/>${fade}` +
    `<g transform="translate(${ox.toFixed(1)} ${oy.toFixed(1)})">` +
    `<g style="mix-blend-mode:multiply"${d.fade ? ' mask="url(#fadem)"' : ''}>${d.washes.join('')}</g>` +
    `<g fill="${PAPER}" filter="url(#wcS0)">${d.whites.join('')}</g>` +
    `<g style="mix-blend-mode:multiply" fill="${INK}" filter="url(#nib)">${d.inks.join('')}</g></g></svg>`;
}
function fadeDefs(d) {
  const [y0, y1] = d.fade, [ox, oy] = d.origin;
  return `<defs><linearGradient id="fadeg" gradientUnits="userSpaceOnUse" x1="0" y1="${y0 - oy}" x2="0" y2="${y1 - oy}">` +
    `<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>` +
    `<filter id="fadef"><feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="3" seed="4"/>` +
    `<feDisplacementMap in="SourceGraphic" scale="60" xChannelSelector="R" yChannelSelector="G"/></filter>` +
    `<mask id="fadem" maskUnits="userSpaceOnUse" x="${-ox - 50}" y="${-oy - 50}" width="${d.w + 100}" height="${d.h + 100}">` +
    `<rect x="${-ox - 50}" y="${-oy - 50}" width="${d.w + 100}" height="${d.h + 100}" fill="url(#fadeg)" filter="url(#fadef)"/></mask></defs>`;
}

// ---------------------------------------------------------------- pen
// a pen stroke through pts (local coordinates): pressure, taper, wobble, the second pass of a dip pen, a dry nib
export function ink(d, pts, o = {}) {
  const { w = 2.0, closed = false, taper = [0.18, 0.35], jit = 0.9, press = 0.5, skip = 0, seed = null, color = null,
    alpha = 0.93, start = 1.0, end = 1.0, retrace = 0.3, raw = false } = o;
  const rnd = seed != null ? rng(seed) : d.rnd;
  const runs = raw ? [pts] : d.runs(pts);
  for (const P of runs) inkRun(d, P, { w, closed: closed && runs.length === 1 && P.length === pts.length, taper, jit, press, skip, rnd, color, alpha, start, end, retrace });
}
function inkRun(d, P, { w, closed, taper, jit, press, skip, rnd, color, alpha, start, end, retrace }) {
  const C = catmull(P, closed, 1.6);
  if (C.length < 3) return;
  const L = [0]; for (let i = 1; i < C.length; i++) L.push(L[i - 1] + Math.hypot(C[i][0] - C[i - 1][0], C[i][1] - C[i - 1][1]));
  const tot = L[L.length - 1] || 1;
  const nlo = new Noise1(rnd, 40), nhi = new Noise1(rnd, 6), nw = new Noise1(rnd, 13), nsk = new Noise1(rnd, 40);
  const W = w * d.lw;
  let left = [], right = []; const pieces = [];
  for (let i = 0; i < C.length; i++) {
    const [x, y] = C[i], j0 = Math.max(0, i - 1), j1 = Math.min(C.length - 1, i + 1);
    const tx = C[j1][0] - C[j0][0], ty = C[j1][1] - C[j0][1], n = Math.hypot(tx, ty) || 1, nx = -ty / n, ny = tx / n;
    const s = L[i], t = s / tot, off = jit * nlo.at(s) + 0.35 * nhi.at(s);
    const [a0, a1] = taper; let prof = 1.0;
    if (!closed) {
      if (t < a0) { const u = t / a0; prof = start < 1 ? start + (1 - start) * (u * u * (3 - 2 * u)) : 0.55 + 0.45 * u; }
      else if (t > 1 - a1) { const u = (1 - t) / a1; prof = end + (1 - end) * (u * u * (3 - 2 * u)); }
    }
    const ww = Math.max(0.3, W * prof * Math.max(0.25, 1 + press * 1.3 * nw.at(s))) / 2;
    const cx = x + nx * off, cy = y + ny * off;
    if (skip > 0 && nsk.at(s) > 1 - 2 * skip) { if (left.length) { pieces.push([left, right]); left = []; right = []; } continue; }
    left.push([cx + nx * ww, cy + ny * ww]); right.push([cx - nx * ww, cy - ny * ww]);
  }
  if (left.length) pieces.push([left, right]);
  if (retrace && C.length > 20 && rnd() < retrace && w > 0.9) {
    const a = rnd.uniform(0.0, 0.5), b = Math.min(1.0, a + rnd.uniform(0.25, 0.5));
    const sub = C.slice(Math.floor(a * C.length), Math.floor(b * C.length));
    if (sub.length > 6) {
      const o = rnd.choice([-1, 1]) * rnd.uniform(1.2, 2.4) * d.lw, k = Math.max(1, Math.floor(sub.length / 5)), pts2 = [];
      for (let i = 0; i < sub.length; i += k) {
        const j0 = Math.max(0, i - 1), j1 = Math.min(sub.length - 1, i + 1);
        const tx = sub[j1][0] - sub[j0][0], ty = sub[j1][1] - sub[j0][1], n = Math.hypot(tx, ty) || 1;
        pts2.push([sub[i][0] - ty / n * o, sub[i][1] + tx / n * o]);
      }
      ink(d, pts2, { w: w * 0.45, jit: jit * 0.5, press, start: 0.2, end: 0.1, retrace: 0, seed: rnd.int(), alpha: alpha * 0.85, raw: true });
    }
  }
  const style = color ? ` fill="${color}"` : '';
  for (const [l, r] of pieces) {
    if (l.length < 2) continue;
    if (closed && pieces.length === 1) d.inks.push(`<path d="M${fmt(l)}Z M${fmt(r.slice().reverse())}Z" fill-rule="evenodd" opacity="${alpha}"${style}/>`);
    else d.inks.push(`<polygon points="${fmt(l.concat(r.slice().reverse()))}" opacity="${alpha}"${style}/>`);
  }
}

export function dot(d, x, y, r = 2.2, seed = null) {
  const rnd = seed != null ? rng(seed) : d.rnd, pts = [];
  for (let i = 0; i < 9; i++) { const a = i / 9 * 2 * Math.PI, rr = r * (1 + rnd.uniform(-0.18, 0.18)); pts.push([x + rr * Math.cos(a), y + rr * Math.sin(a) * 0.95]); }
  const P = d.tp(pts); if (!P) return;
  d.inks.push(`<polygon points="${fmt(catmull(P, true, 1.0))}" opacity="0.95"/>`);
}
// a dot of a fixed size in the picture at a local point (a freckle, a pupil on a turned face keeps its round)
export function dotAt(d, x, y, r, seed = null) {
  const P = d.tp([[x, y]]); if (!P) return;
  const rnd = seed != null ? rng(seed) : d.rnd, pts = [];
  for (let i = 0; i < 9; i++) { const a = i / 9 * 2 * Math.PI, rr = r * (1 + rnd.uniform(-0.18, 0.18)); pts.push([P[0][0] + rr * Math.cos(a), P[0][1] + rr * Math.sin(a) * 0.95]); }
  d.inks.push(`<polygon points="${fmt(catmull(pts, true, 1.0))}" opacity="0.95"/>`);
}
export function white(d, x, y, rx, ry, rot = 0) {
  const c = Math.cos(rot * Math.PI / 180), s = Math.sin(rot * Math.PI / 180), pts = [];
  for (let i = 0; i < 12; i++) { const a = i / 12 * 2 * Math.PI; pts.push([x + rx * Math.cos(a) * c - ry * Math.sin(a) * s, y + rx * Math.cos(a) * s + ry * Math.sin(a) * c]); }
  const P = d.tp(pts); if (!P) return;
  d.whites.push(`<polygon points="${fmt(catmull(P, true, 1.5))}"/>`);
}

// ---------------------------------------------------------------- watercolour
export function wash(d, poly, color, opacity = 0.62, o = {}) {
  const { dx = 0, dy = 0, closed = true, seed = null, rough = null, angle = null } = o;
  const rnd = seed != null ? rng(seed) : d.rnd;
  const P0 = d.tp(poly.map(([x, y]) => [x + dx, y + dy])); if (!P0) return;
  const P = catmull(P0, closed, 3);
  const xs = P.map(p => p[0]), ys = P.map(p => p[1]);
  const size = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
  const r = rough || (size < 90 ? 'S' : 'L'), k = Math.floor(rnd() * 6), ang = angle ?? rnd.uniform(-60, 60);
  const cx = (Math.min(...xs) + Math.max(...xs)) / 2, cy = (Math.min(...ys) + Math.max(...ys)) / 2;
  const ca = Math.cos(-ang * Math.PI / 180), sa = Math.sin(-ang * Math.PI / 180);
  const R = P.map(([x, y]) => [cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca]);
  d.washes.push(`<polygon points="${fmt(R)}" fill="${color}" fill-opacity="${opacity}" filter="url(#wc${r}${k})" transform="rotate(${ang.toFixed(1)} ${cx.toFixed(1)} ${cy.toFixed(1)})"/>`);
}
// a wash whose shape is a mask picture (data url, its box x, y, w, h in the picture): the same filter as wash()
export function washImage(d, href, box, color, opacity, o = {}) {
  const { seed = 1, angle = 0, rough = 'L', dx = 0, dy = 0 } = o;
  const [x, y, w, h] = box, k = ((seed % 6) + 6) % 6, cx = x + w / 2 + dx, cy = y + h / 2 + dy;
  d.washes.push(`<g transform="rotate(${angle.toFixed(1)} ${cx.toFixed(1)} ${cy.toFixed(1)})" filter="url(#wc${rough}${k})">` +
    `<image href="${href}" x="${(x + dx).toFixed(1)}" y="${(y + dy).toFixed(1)}" width="${w}" height="${h}" preserveAspectRatio="none" opacity="${opacity}" ` +
    `transform="rotate(${(-angle).toFixed(1)} ${cx.toFixed(1)} ${cy.toFixed(1)})"/></g>`);
}
export function blot(d, x, y, r, color, opacity = 0.4, seed = null) {
  const rnd = seed != null ? rng(seed) : d.rnd, pts = [];
  for (let i = 0; i < 10; i++) { const a = i / 10 * 2 * Math.PI; pts.push([x + r * Math.cos(a) * rnd.uniform(0.85, 1.1), y + r * Math.sin(a) * rnd.uniform(0.75, 1.0)]); }
  const P = d.tp(pts); if (!P) return;
  d.washes.push(`<polygon points="${fmt(catmull(P, true, 2))}" fill="${color}" fill-opacity="${opacity}" filter="url(#blush)"/>`);
}

function wcFilter(name, i, freq, scale, erode, blur, dfreq = '0.008 0.02', dm = -4.0, db = 2.6, rimk = 0.8) {
  return `<filter id="${name}${i}" x="-15%" y="-15%" width="130%" height="130%" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="${freq}" numOctaves="4" seed="${i * 7 + 3}" result="n1"/>
<feDisplacementMap in="SourceGraphic" in2="n1" scale="${scale}" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feGaussianBlur in="d" stdDeviation="${blur}" result="ds"/>
<feTurbulence type="fractalNoise" baseFrequency="${dfreq}" numOctaves="3" seed="${i * 5 + 21}" result="n2"/>
<feColorMatrix in="n2" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ${dm} ${db}" result="dens"/>
<feComposite in="ds" in2="dens" operator="in" result="dd"/>
<feMorphology in="d" operator="erode" radius="${erode}" result="er"/>
<feComposite in="d" in2="er" operator="out" result="rim"/>
<feGaussianBlur in="rim" stdDeviation="0.6" result="rimb"/>
<feComponentTransfer in="rimb" result="rimc"><feFuncA type="linear" slope="${rimk}"/></feComponentTransfer>
<feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="${i + 40}" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.1 1.25" result="ga"/>
<feComposite in="dd" in2="ga" operator="in" result="gr"/>
<feMerge><feMergeNode in="gr"/><feMergeNode in="rimc"/></feMerge>
</filter>`;
}
// the filters, once per page (an <svg> of defs the pictures refer to)
export const DEFS = [0, 1, 2, 3, 4, 5].map(i => wcFilter('wcL', i, 0.03, 12, 1.6, 0.2)).join('') +
  [0, 1, 2, 3, 4, 5].map(i => wcFilter('wcS', i, 0.06, 6, 1.1, 0.2, '0.016 0.04')).join('') +
  `<filter id="blush" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="nib" x="-5%" y="-5%" width="110%" height="110%">
<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="1" seed="5" result="t"/>
<feDisplacementMap in="SourceGraphic" in2="t" scale="1.3" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="paper" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="11" result="t"/>
<feColorMatrix in="t" type="matrix" values="0 0 0 0 0.45 0 0 0 0 0.40 0 0 0 0 0.33 0 0 0 -0.35 0.2"/>
<feComposite operator="in" in2="SourceGraphic"/></filter>`;

// ---------------------------------------------------------------- the face parts (parts.py)
export const SKIN = '#f0bf98', BLUSH = '#e57d68', LIPS = '#d4594b';
export const EXPR = {
  calm: { lift: 0, tilt: 0, lid: 0.25, look: [0, 0], mouth: 'soft', eye: 1.0 },
  dream: { lift: 2, tilt: 1, lid: 0.5, look: [-0.5, -1], mouth: 'soft', eye: 1.0 },
  joy: { lift: 7, tilt: 0, lid: 0.0, look: [0, 0], mouth: 'laugh', eye: 0.9, squint: true, ms: 1.6, tilt_head: -10 },
  surprise: { lift: 17, tilt: 3, lid: 0.0, look: [0, 0], mouth: 'O', eye: 1.3, ms: 1.5, tilt_head: -4, extra: 'start' },
  sad: { lift: 3, tilt: 11, lid: 0.5, look: [0, 1.5], mouth: 'down', eye: 1.0, ms: 1.4, tilt_head: 12, extra: 'tear' },
  anger: { lift: -7, tilt: -12, lid: 0.3, look: [0, 0], mouth: 'shout', eye: 1.0, ms: 1.6, tilt_head: 6, extra: 'flush' },
};

export function extra(d, e, eyeX, eyeY, cheekX, cheekY, topY, k = 1) {
  if (e.extra === 'tear' && k > 0.5) {
    const x = eyeX - 2, y = eyeY + 16, pts = [[x, y], [x - 4, y + 10], [x, y + 15], [x + 4, y + 10], [x, y]];
    wash(d, pts, '#7fb6dc', 0.7, { rough: 'S', seed: 91 }); ink(d, pts, { w: 1.0, retrace: 0, seed: 92 });
  } else if (e.extra === 'start' && k > 0.5) {
    for (const [dx] of [[-26], [0], [26]]) ink(d, [[eyeX + dx, topY - 8], [eyeX + dx * 1.4, topY - 26]], { w: 1.5, start: 1.0, end: 0.1, retrace: 0, seed: 93 + dx });
  } else if (e.extra === 'flush' && k > 0.01) {
    blot(d, cheekX, cheekY, 26, '#e0503c', 0.45 * k, 94);
    if (k > 0.5) for (const dx of [-10, 0, 10]) ink(d, [[cheekX + dx - 3, cheekY - 6], [cheekX + dx + 3, cheekY + 4]], { w: 0.9, retrace: 0, seed: 95 + dx });
  }
}

// a Blake eye: a round of white paper, a loose upper line, a dot of a pupil; squint: a happy closed arc.
// pupil: the pupil's radius in the picture (kept round on a turned face), or null for parts.py's own
export function eye(d, x, y, s = 1, look = [0, 0], lid = 0.25, o = {}) {
  const { lash = false, side = -1, squint = false, w = 1.0, seed = null, pupil = null } = o;
  const rx = 7.6 * s, ry = 8.4 * s;
  if (squint) { ink(d, [[x - rx * 1.2, y + 1], [x, y - ry * 0.9], [x + rx * 1.2, y + 1]], { w: 2.2 * w, start: 0.4, end: 0.3, seed }); return; }
  lid = Math.min(1, lid);
  if (lid < 0.92) {
    white(d, x, y + lid * ry * 0.45, rx, ry * (1 - lid * 0.5));
    const px = x + look[0] * 2.4 * s, py = y + look[1] * 2.0 * s + lid * ry * 0.5;
    if (pupil) dotAt(d, px, py, pupil, seed); else dot(d, px, py, 3.1 * s, seed);
  }
  const top = y - ry + lid * ry * 1.1;
  ink(d, [[x - rx * 1.1, y + 0.5 * s + lid * 2], [x - rx * 0.4, top - 0.5], [x + rx * 0.5, top - 0.3], [x + rx * 1.1, y + 0.5 * s + lid * 2]], { w: 1.8 * w, start: 0.5, end: 0.3, seed });
  if (lid < 0.92) ink(d, [[x - rx * 0.6, y + ry * 0.95], [x + rx * 0.5, y + ry * 0.9]], { w: 0.8 * w, start: 0.2, end: 0.2, jit: 0.3, seed: seed == null ? null : seed + 1 });
  if (lash) { const ox = x + side * rx * 1.05; ink(d, [[ox, y + lid * 2], [ox + side * 5 * s, y - 4 * s + lid * 2]], { w: 1.6 * w, start: 1, end: 0.1, seed: seed == null ? null : seed + 2 }); }
}
export function brow(d, x, y, length = 22, lift = 0, tilt = 0, o = {}) {
  const { side = -1, w = 1.6, arch = 4, seed = null } = o;
  const yi = y - lift - tilt, yo = y - lift + tilt * 0.3, xi = x - side * length * 0.5, xo = x + side * length * 0.5;
  ink(d, [[xi, yi], [(xi + xo) / 2, (yi + yo) / 2 - arch], [xo, yo + 2]], { w: w * 1.4, start: 1.0, end: 0.15, seed });
}
// parts.py's mouths; and 'talk': the open mouth of speech from numbers (open o 0…1, width change dw, round r) —
// the closed line opening into the drawing's small dark-red wash in a pen outline
export function mouth(d, x, y, kind = 'soft', s = 1, o = {}) {
  const { side = -1, w = 1, lips = true, seed = null, open = 0, dw = 0, round = 0 } = o;
  const a = x + side * 12 * Math.min(s, 1.0), b = x - side * 9 * s - side * 12 * (Math.max(s, 1.0) - 1);
  const xm = (a + b) / 2;
  if (kind === 'talk') {
    const hw = Math.max(4, (Math.abs(a - b) / 2 + dw * 0.6) * (1 - 0.45 * round)), H = 3 + 14 * open * (1 - 0.3 * round);
    const pts = [[xm - hw, y], [xm, y - 2 - 2 * round], [xm + hw, y], [xm + hw * 0.7, y + H * 0.7], [xm, y + H], [xm - hw * 0.7, y + H * 0.7]];
    if (open < 0.08) {
      ink(d, [[a, y - 1], [xm, y + 2.5 * s], [b, y - 2.5 * s]], { w: 1.7 * w, start: 0.4, end: 0.2, seed });
      if (lips) wash(d, [[a, y - 2], [b, y - 4], [b, y + 5], [xm, y + 9 * s], [a, y + 4]], LIPS, 0.45, { seed: 71 });
      return;
    }
    wash(d, pts, '#b43c38', 0.7, { seed: 72, rough: 'S' });
    ink(d, [...pts, pts[0]], { w: 1.6 * w, start: 0.8, end: 0.6, seed, retrace: 0 });
    return;
  }
  if (kind === 'soft') {
    ink(d, [[a, y - 1], [xm, y + 2.5 * s], [b, y - 2.5 * s]], { w: 1.7 * w, start: 0.4, end: 0.2, seed });
    if (lips) {
      wash(d, [[a, y - 2], [b, y - 4], [b, y + 5], [xm, y + 9 * s], [a, y + 4]], LIPS, 0.45, { seed: 71 });
      ink(d, [[xm - 4 * s, y + 8 * s], [xm + 4 * s, y + 8 * s]], { w: 0.9 * w, jit: 0.2, seed: seed == null ? null : seed + 1 });
    }
  } else if (kind === 'flat') {
    ink(d, [[a, y + 1], [xm, y], [b, y + 2]], { w: 1.8 * w, start: 0.6, end: 0.4, seed });
    ink(d, [[b, y + 2], [b - side * 3, y + 5]], { w: 1.0 * w, seed: seed == null ? null : seed + 1 });
  } else if (kind === 'grin') {
    ink(d, [[a, y - 1], [xm, y + 4 * s], [b, y - 4 * s], [b - side * 3, y - 7 * s]], { w: 1.8 * w, start: 0.4, end: 0.2, seed });
  } else if (kind === 'down') {
    ink(d, [[a, y + 4], [xm, y - 1], [b, y + 4]], { w: 1.7 * w, start: 0.4, end: 0.3, seed });
  } else if (kind === 'laugh') {
    const pts = [[a, y - 3], [xm - side * 2, y - 2], [b + side * 1, y - 6 * s], [b - side * 2, y + 6 * s], [xm, y + 14 * s], [a - side * 2, y + 6 * s]];
    wash(d, pts, '#c4473f', 0.75, { seed: 73 });
    ink(d, [...pts, pts[0]], { w: 1.7 * w, start: 0.8, end: 0.6, seed });
    ink(d, [[a - side * 4, y - 1], [b + side * 1, y - 3 * s]], { w: 0.8, jit: 0.2, seed: 74 });
  } else if (kind === 'O') {
    const xx = xm, pts = [[xx - side * 1, y - 5 * s], [xx + 5 * s, y + 1], [xx, y + 9 * s], [xx - 5 * s, y + 2]];
    wash(d, pts, '#b43c38', 0.7, { seed: 75 });
    ink(d, [...pts, pts[0]], { w: 1.6 * w, start: 0.8, end: 0.6, seed });
  } else if (kind === 'shout') {
    const pts = [[a, y - 2], [xm, y - 4 * s], [b, y - 1], [b + side * 1, y + 7 * s], [xm, y + 10 * s], [a - side * 1, y + 6 * s]];
    wash(d, pts, '#b43c38', 0.75, { seed: 76 });
    ink(d, [...pts, pts[0]], { w: 1.9 * w, start: 0.9, end: 0.7, seed });
    ink(d, [[a - side * 2, y + 0.5], [b + side * 2, y + 1]], { w: 0.8, jit: 0.2, seed: 77 });
  }
}

// kit.py's paper(): paper left white in any shape (teeth in an open mouth) — over the washes, under the ink
export function paper(d, poly) {
  const P = d.tp(poly); if (!P) return;
  d.whites.push(`<polygon points="${fmt(catmull(P, true, 1.5))}"/>`);
}
// parts.py's curl(): one small curl inside a mass of curly hair — an open hook of the pen, most of a turn
export function curl(d, x, y, r = 6, rot = 0, o = {}) {
  const { w = 1.0, seed = null, raw = false } = o, pts = [];
  for (let i = 0; i < 7; i++) { const a = rot * Math.PI / 180 + i / 6 * 1.5 * Math.PI, k = r * (1 - 0.07 * i); pts.push([x + k * Math.cos(a), y + k * Math.sin(a) * 0.85]); }
  ink(d, pts, { w, start: 0.5, end: 0.1, jit: 0.3, retrace: 0, seed, raw });
}
