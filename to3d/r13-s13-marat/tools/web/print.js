// The woodblock print's means, in JavaScript: styles/s13-ukiyo-e/tools/kit.py (the brush line with pressure, flat
// colour, bokashi, the sheet with its ground, border, cartouche and seal, paper and wood grain) and the parts of
// parts.py that draw Марат's face (eye, brow, nose, mouth) with marat.py's numbers — ported function by function, so
// what is drawn on the 3D is the drawing's own line. Points are [x, y] or [x, y, 'c'] ('c' — a corner).
export const INK = '#211c1c', PAPER = '#eee3cb', RED = '#b8402f';
export const SKIN = '#f1d7b6', HAIR = '#1f1a1a', SHEEN = '#8a8684', WHITE = '#f8f2e2', TERRA = '#c8683a', TERRA_D = '#9c4a26';
const f = v => (Math.round(v * 10) / 10).toString(), f2 = v => (Math.round(v * 100) / 100).toString();
export function rng(seed) { let a = (seed * 2654435761) >>> 0; const R = () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  R.uniform = (lo, hi) => lo + (hi - lo) * R(); return R; }

// ---------------------------------------------------------------- curves (kit.py)
function crRun(p, n, closed = false) {
  const m = p.length;
  if (m < 3 && !closed) { if (m === 2) { const o = []; for (let i = 0; i <= n; i++) o.push([p[0][0] + (p[1][0] - p[0][0]) * i / n, p[0][1] + (p[1][1] - p[0][1]) * i / n]); return o; } return p.slice(); }
  const out = [], spans = closed ? m : m - 1;
  for (let i = 0; i < spans; i++) {
    let p0, p1, p2, p3;
    if (closed) { p0 = p[(i - 1 + m) % m]; p1 = p[i]; p2 = p[(i + 1) % m]; p3 = p[(i + 2) % m]; }
    else { p1 = p[i]; p2 = p[i + 1]; p0 = i > 0 ? p[i - 1] : [2 * p1[0] - p2[0], 2 * p1[1] - p2[1]]; p3 = i + 2 < m ? p[i + 2] : [2 * p2[0] - p1[0], 2 * p2[1] - p1[1]]; }
    for (let k = 0; k < n; k++) { const t = k / n, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(a => 0.5 * (2 * p1[a] + (-p0[a] + p2[a]) * t + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t2 + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t3))); }
  }
  if (!closed) out.push([p[m - 1][0], p[m - 1][1]]);
  return out;
}
export function curve(pts, closed = false, n = 8) {
  let xy = pts.map(p => [p[0], p[1]]);
  let corners = []; pts.forEach((p, i) => { if (p[2] === 'c') corners.push(i); });
  if (!corners.length) return crRun(xy, n, closed);
  if (closed) { const k = corners[0]; xy = xy.slice(k).concat(xy.slice(0, k), [xy[k]]); corners = corners.map(c => c - k).concat([xy.length - 1]); }
  else corners = [...new Set([0, ...corners, xy.length - 1])].sort((a, b) => a - b);
  let out = [];
  for (let i = 0; i + 1 < corners.length; i++) { const run = crRun(xy.slice(corners[i], corners[i + 1] + 1), n); out = out.concat(out.length ? run.slice(1) : run); }
  if (closed) out.pop();
  return out;
}
export const pathD = (sm, closed = true) => 'M' + sm.map(p => f(p[0]) + ' ' + f(p[1])).join('L') + (closed ? 'Z' : '');
function prof(kind, t) {
  if (typeof kind === 'function') return kind(t);
  if (kind === 'taper') return Math.min(1, t / 0.05 + 0.25) * (0.1 + 0.9 * (1 - t) ** 0.9);
  if (kind === 'tail') return Math.min(1, (1 - t) / 0.05 + 0.25) * (0.1 + 0.9 * t ** 0.9);
  if (kind === 'swell') return 0.12 + 0.88 * Math.sin(Math.PI * t) ** 0.7;
  if (kind === 'even') return Math.min(1, t / 0.06 + 0.3, (1 - t) / 0.06 + 0.3);
  if (kind === 'press') return 0.55 + 0.45 * Math.abs(Math.cos(Math.PI * t)) ** 1.5 * Math.min(1, t / 0.03 + 0.4, (1 - t) / 0.03 + 0.2);
  throw new Error(kind);
}
// The outline of a stroke of varying width along the sampled curve sm. `ends` (px): for a contour taken from the 3D,
// the stroke comes in and goes out over that length whatever its whole length is.
export function brushPoly(sm, w, kind = 'swell', nib = 0.3, closed = false, seed = 0, ends = 0, hand = 1) {
  const R = rng(seed * 7919 + 13), n = sm.length, seg = [0];
  for (let i = 1; i < n; i++) seg.push(seg[i - 1] + Math.hypot(sm[i][0] - sm[i - 1][0], sm[i][1] - sm[i - 1][1]));
  const total = seg[n - 1] || 1, ph1 = R.uniform(0, 6.28), ph2 = R.uniform(0, 6.28), left = [], right = [];
  for (let i = 0; i < n; i++) {
    const a = (closed || i > 0) ? sm[(i - 1 + n) % n] : sm[i], b = (closed || i < n - 1) ? sm[(i + 1) % n] : sm[i];
    const dx = b[0] - a[0], dy = b[1] - a[1], ln = Math.hypot(dx, dy) || 1, nx = -dy / ln, ny = dx / ln, t = seg[i] / total, ang = Math.atan2(dy, dx);
    let k = (1 - nib) + nib * (0.5 + 0.5 * Math.cos(2 * (ang - 1.0)));        // the brush held at a slant
    k *= 1 + hand * (0.10 * Math.sin(ph1 + seg[i] * 0.045) + 0.06 * Math.sin(ph2 + seg[i] * 0.13));   // the hand's slow uneven pressure
    let p = closed ? 1 : ends ? Math.min(1, seg[i] / ends + 0.22, (total - seg[i]) / ends + 0.22) : prof(kind, t);
    const hw = 0.5 * w * k * p;
    left.push([sm[i][0] + nx * hw, sm[i][1] + ny * hw]); right.push([sm[i][0] - nx * hw, sm[i][1] - ny * hw]);
  }
  if (closed) return pathD(left) + pathD(right.reverse());
  return pathD(left.concat(right.reverse()));
}

// ---------------------------------------------------------------- the sheet (kit.py Doc)
export class Doc {
  constructor(w, h, seed = 1) { this.w = w; this.h = h; this.out = []; this.defs = []; this.n = 0; this.seed = seed; this.R = rng(seed); this.lw = 1; this.margin = 0; this.groundSvg = ''; this.overSvg = ''; }
  id(p = 'i') { return p + (++this.n); }
  raw(s) { this.out.push(s); }
  open(m, clip) { this.out.push(`<g${m ? ` transform="matrix(${m.map(v => +v.toFixed(4)).join(' ')})"` : ''}${clip ? ` clip-path="url(#${clip})"` : ''}>`); }
  close() { this.out.push('</g>'); }
  fill(pts, color, o = {}) {
    const sm = o.raw ? pts : curve(pts, o.closed ?? true, o.n ?? 8);
    this.out.push(`<path d="${pathD(sm)}" fill="${color}"${o.op != null && o.op !== 1 ? ` opacity="${f2(o.op)}"` : ''}${o.blend ? ` style="mix-blend-mode:${o.blend}"` : ''}/>`);
    return sm;
  }
  clip(pts, n = 8) { const cid = this.id('c'); this.defs.push(`<clipPath id="${cid}"><path d="${pathD(curve(pts, true, n))}"/></clipPath>`); return cid; }
  blush(cx, cy, r, color, op) {
    const gid = this.id('b');
    this.defs.push(`<radialGradient id="${gid}" gradientUnits="userSpaceOnUse" cx="${f(cx)}" cy="${f(cy)}" r="${f(r)}"><stop offset="0" stop-color="${color}" stop-opacity="${f2(op)}"/><stop offset="0.55" stop-color="${color}" stop-opacity="${f2(op * 0.55)}"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></radialGradient>`);
    this.out.push(`<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(r)}" fill="url(#${gid})" style="mix-blend-mode:multiply"/>`);
  }
  // one stroke of the brush
  line(pts, w = 3, kind = 'swell', o = {}) {
    const sm = o.raw ? pts : curve(pts, false, o.n ?? 8);
    if (sm.length < 2) return sm;
    this.out.push(`<path d="${brushPoly(sm, w * this.lw, kind, o.nib ?? 0.3, false, o.seed ?? ++this.n, o.ends ?? 0, o.hand ?? 1)}" fill="${o.color || INK}"${o.op != null && o.op !== 1 ? ` opacity="${f2(o.op)}"` : ''}/>`);
    return sm;
  }
  contour(pts, w = 3, o = {}) {
    const sm = curve(pts, true, o.n ?? 8);
    this.out.push(`<path d="${brushPoly(sm, w * this.lw, 'even', o.nib ?? 0.45, true, o.seed ?? ++this.n)}" fill="${o.color || INK}" fill-rule="evenodd"/>`);
  }
  // short separate hairs growing out of an edge (a beard's edge): sm — sampled points; side: +1 / −1 or a function of
  // the point's index giving it (0 — no hair there)
  fringe(sm, length = 10, w = 1, o = {}) {
    const R = rng(o.seed ?? 1), step = o.step ?? 3, lean = o.lean ?? 0, vary = o.vary ?? 0.4;
    let acc = o.phase ?? 0;
    for (let i = 1; i < sm.length; i++) {
      const dx = sm[i][0] - sm[i - 1][0], dy = sm[i][1] - sm[i - 1][1], ln = Math.hypot(dx, dy);
      acc += ln; if (acc < step || ln === 0) continue; acc = 0;
      const side = typeof o.side === 'function' ? o.side(i) : (o.side ?? 1), r1 = R.uniform(-vary, vary), r2 = R.uniform(-0.15, 0.15);
      if (!side) continue;
      const nx = -dy / ln * side, ny = dx / ln * side, tx = dx / ln, ty = dy / ln, L = length * (1 + r1), le = lean + r2;
      const e = [sm[i][0] + (nx + tx * le) * L, sm[i][1] + (ny + ty * le) * L], m = [sm[i][0] + (nx + tx * le * 0.3) * L * 0.5, sm[i][1] + (ny + ty * le * 0.3) * L * 0.5];
      this.out.push(`<path d="${brushPoly(curve([sm[i], m, e], false, 4), w * this.lw, 'taper', 0.1, false, i)}" fill="${o.color || INK}"/>`);
    }
  }
  dot(x, y, r, color = INK) { this.out.push(`<circle cx="${f(x)}" cy="${f(y)}" r="${f2(r)}" fill="${color}"/>`); }
  ground(color, top, bottom, margin = 26) {
    const m = this.margin = margin, w = this.w - 2 * m, h = this.h - 2 * m;
    let s = `<rect x="${m}" y="${m}" width="${w}" height="${h}" fill="${color}"/>`;
    if (top) { const g = this.id('b');
      this.defs.push(`<linearGradient id="${g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${top}"/><stop offset="0.5" stop-color="${top}" stop-opacity="0.35"/><stop offset="1" stop-color="${top}" stop-opacity="0"/></linearGradient>`);
      s += `<rect x="${m}" y="${m}" width="${w}" height="${f(h * 0.3)}" fill="url(#${g})"/>`; }
    if (bottom) { const g = this.id('b');
      this.defs.push(`<linearGradient id="${g}" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="${bottom}"/><stop offset="0.5" stop-color="${bottom}" stop-opacity="0.35"/><stop offset="1" stop-color="${bottom}" stop-opacity="0"/></linearGradient>`);
      s += `<rect x="${m}" y="${f(m + h * 0.78)}" width="${w}" height="${f(h * 0.22)}" fill="url(#${g})"/>`; }
    this.groundSvg = s;
  }
  cartouche(text, x, y, size = 26, color = RED) {
    const n = text.length, w = size * 1.5, h = size * 1.12 * n + size * 0.7;
    let s = `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" fill="#f3ead6"/><rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" fill="none" stroke="${INK}" stroke-width="1.6"/>`;
    [...text].forEach((ch, i) => { s += `<text x="${f(x + w / 2)}" y="${f(y + size * 1.12 * (i + 1) + size * 0.05)}" font-family="Georgia, 'PT Serif', 'DejaVu Serif', serif" font-size="${f(size)}" text-anchor="middle" fill="${INK}">${ch}</text>`; });
    const sy = y + h + size * 0.45, ss = size * 1.05, sx = x + (w - ss) / 2;
    s += `<rect x="${f(sx)}" y="${f(sy)}" width="${f(ss)}" height="${f(ss)}" rx="2" fill="${color}"/>`;
    s += `<path d="M${f(sx + ss * 0.22)} ${f(sy + ss * 0.3)}h${f(ss * 0.56)}M${f(sx + ss * 0.5)} ${f(sy + ss * 0.3)}v${f(ss * 0.48)}M${f(sx + ss * 0.28)} ${f(sy + ss * 0.78)}h${f(ss * 0.44)}" stroke="#f3ead6" stroke-width="${f2(ss * 0.1)}" fill="none"/>`;
    this.overSvg += s;
  }
  // the sheet in two layers, the colour blocks (the page's canvas) lying between them: the paper with the toned
  // ground, and over the colours — the key block's lines, the border, the name's slip and the seal. The paper's and
  // the wood's texture (texture()) lie over all of it, still.
  layers() {
    const { w, h, margin: m } = this, head = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">`;
    const ground = head + `<defs>${this.defs.filter(s => s.startsWith('<linearGradient')).join('')}</defs><rect width="${w}" height="${h}" fill="${PAPER}"/>${this.groundSvg}</svg>`;
    let over = head + `<defs>${this.defs.filter(s => !s.startsWith('<linearGradient')).join('')}<clipPath id="sheet"><rect x="${m}" y="${m}" width="${w - 2 * m}" height="${h - 2 * m}"/></clipPath></defs><g clip-path="url(#sheet)">${this.out.join('')}</g>` + this.overSvg;
    if (m) over += `<rect x="${m}" y="${m}" width="${w - 2 * m}" height="${h - 2 * m}" fill="none" stroke="${INK}" stroke-width="2.2"/>`;
    return { ground, over: over + '</svg>' };
  }
}
// paper (fibres and tooth), the colour block's wood grain (long light streaks), old paper's blotches: kit.py's filters
export function texture(w, h, sd = 1) {
  const one = (id, turb, mat, op, blend) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" style="position:absolute;left:0;top:0;mix-blend-mode:${blend};opacity:${op};pointer-events:none"><filter id="${id}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">${turb}<feColorMatrix values="${mat}"/></filter><rect width="${w}" height="${h}" filter="url(#${id})"/></svg>`;
  return one('grain', `<feTurbulence type="fractalNoise" baseFrequency="0.0035 0.11" numOctaves="3" seed="${sd + 5}"/>`, '0 0 0 0 0.97  0 0 0 0 0.93  0 0 0 0 0.82  2.4 0 0 0 -1.2', 0.15, 'screen')
    + one('paper', `<feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="${sd}"/>`, '0 0 0 0 0.42  0 0 0 0 0.33  0 0 0 0 0.2  0.85 0 0 0 -0.27', 0.42, 'multiply')
    + one('age', `<feTurbulence type="fractalNoise" baseFrequency="0.006" numOctaves="3" seed="${sd + 9}"/>`, '0 0 0 0 0.5  0 0 0 0 0.36  0 0 0 0 0.16  1.3 0 0 0 -0.5', 0.28, 'multiply');
}

// ---------------------------------------------------------------- Марат's face (parts.py with marat.p), front layout
export const P = { line: 2.0, long: 0.98,
  eye: { w: 32, h: 8.5, iris: 6.2, lid: 4.0, slant: 0, lower: 0.6, white: '#fbf6e8', color: '#2a2220', y: 0 },
  brow: { w: 9.5, len: 44, arch: 7, y: -24, tilt: 0 }, nose: { s: 1.12 }, mouth: { w: 40, y: 66, full: 1.2 }, blush: ['#e2876a', 0.45] };
// what the face does (parts.EXPR with marat.EXPR over it): brows (lift, tilt), eyes (open; arc — the laugh's closed
// arc), the look, the mouth: dep — how far it is open, big — how wide, curve — a closed mouth's corners (+ up),
// snarl / round — the bared teeth of anger, the round mouth of surprise
export const EXPR = {
  grin: { lift: 3, tilt: 0, open: 0, arc: 1, look: [0, 0], blush: 0.5, dep: 18, big: 1.25, curve: 1, snarl: 0, round: 0, lean: -0.06 },
  calm: { lift: 1, tilt: 0, open: 1, arc: 0, look: [0, 0], blush: 0.15, dep: 0, big: 0.9, curve: 1, snarl: 0, round: 0, lean: 0 },
  joy: { lift: 5, tilt: 1, open: 0, arc: 1, look: [0, 0], blush: 0.6, dep: 18, big: 1.25, curve: 1, snarl: 0, round: 0, lean: -0.08 },
  surprise: { lift: 12, tilt: 2, open: 1.6, arc: 0, look: [0, 0], blush: 0, dep: 12, big: 0.5, curve: 0, snarl: 0, round: 1, lean: -0.03 },
  sad: { lift: 0, tilt: 9, open: 0.7, arc: 0, look: [-1, 2.5], blush: 0, dep: 0, big: 0.9, curve: -1, snarl: 0, round: 0, lean: 0.07 },
  anger: { lift: -8, tilt: -10, open: 0.9, arc: 0, look: [0, 0], blush: 0.1, dep: 8.4, big: 0.9, curve: 0, snarl: 1, round: 0, lean: 0.04 },
};
// an eye: a full upper lid drawn with pressure, a hair-thin lower lid, a dark iris half under the lid; closed by the
// laugh into an arc (ex.arc 1) or by a blink into the lid's line (ex.arc 0)
export function eye(d, cx, cy, k, inner, ex) {
  const e = P.eye, w = e.w * k, h = e.h * Math.max(ex.open, 0), sl = e.slant - ex.tilt * 0.35;
  const xi = cx + inner * w / 2, xo = cx - inner * w / 2, lid = e.lid * (k < 0.8 ? 0.8 : 1);
  if (ex.open <= 0.12) {
    const a = ex.arc, up = e.h * (0.75 * a - 0.12 * (1 - a));
    d.line([[xi, cy + 2], [cx + inner * w * 0.1, cy - up], [xo, cy + 1 + sl * 0.3], [xo - inner * 3, cy + 4 * a + 1.5 * (1 - a)]], lid * 1.1, 'swell');
    return;
  }
  const up = [[xi, cy + h * 0.45], [xi - inner * w * 0.2, cy - h * 0.55], [cx - inner * w * 0.02, cy - h], [xo + inner * w * 0.12, cy - h * 0.45 + sl * 0.6], [xo, cy + sl]];
  const lo = [[xo, cy + sl], [cx - inner * w * 0.15, cy + h * 0.72 + sl * 0.4], [cx + inner * w * 0.2, cy + h * 0.78], [xi, cy + h * 0.45]];
  const opening = up.concat(lo.slice(1, -1));
  d.fill(opening, e.white);
  const cid = d.clip(opening), [lx, ly] = ex.look, ix = cx + lx * k - inner * w * 0.03, iy = cy - h * 0.2 + ly;
  d.open(null, cid); d.dot(ix, iy, e.iris * (k < 0.8 ? 0.86 : 1), e.color); d.dot(ix, iy, e.iris * 0.45, INK); d.close();
  d.line(up.concat([[xo - inner * 2, cy + sl]]), lid, 'swell', { nib: 0.1 });
  d.line(lo.slice(0, 3), Math.max(0.9, lid * 0.3), 'even', { op: e.lower, nib: 0 });
}
// pressed at the inner end, tailing off: Sharaku's brow
export function brow(d, cx, k, inner, ex) {
  const b = P.brow, L = b.len * k, y = b.y - ex.lift, tilt = b.tilt + ex.tilt;
  const xi = cx + inner * L / 2, xo = cx - inner * L / 2, yi = y - tilt * 0.5, yo = y + tilt * 0.35 + 2;
  d.line([[xi, yi], [cx + inner * L * 0.1, y - b.arch - Math.abs(tilt) * 0.1], [xo, yo]], b.w, 'taper', { nib: 0.15 });
}
// the broad nose, front: the bridge's stroke down one side, the tip, a wing (op fades the bridge as the head turns;
// then the 3D's own contour carries the nose, as the drawing's profile does)
export function noseFront(d, side, bridge) {
  const s = P.nose.s, lw = P.line * 1.15, wdt = 15, bot = 42, q = (x, y) => [x * s * side, y * s];
  if (bridge > 0.02) d.line([q(-6, 0), q(-7, bot - 18), q(-wdt, bot - 6), q(-wdt + 2, bot + 2), q(-6, bot + 2)], lw * 1.2, 'even', { nib: 0.2, op: bridge });
  d.line([q(-6, bot + 2), q(0, bot + 5), q(6, bot + 2)], lw, 'swell', { nib: 0 });
  d.line([q(6, bot + 2), q(wdt - 1, bot + 1), q(wdt + 1, bot - 6), q(wdt - 4, bot - 12)], lw, 'taper', { nib: 0.1, op: Math.max(bridge, 0.0) * 0.999 + 0.001 });
}
// the broad nose of the three-quarter head (parts.nose 'q', 'broad'): one stroke down from beside the far eye with a
// hook at the tip, and the wing; drawn from its top (0, 0), the tip toward −x
export function noseQ(d, op) {
  const s = P.nose.s, lw = P.line * 1.15, q = (x, y) => [x * s, y * s];
  d.line([q(0, 4), q(-5, 18), q(-16, 30), q(-22, 37), q(-19, 44), q(-10, 46)], lw * 1.2, 'even', { nib: 0.25, op });
  d.line([q(-10, 46), q(-2, 47), q(8, 44), q(11, 36), q(6, 30)], lw, 'taper', { nib: 0.1, op });
}
// the mouth (parts.mouth, front): closed — a line whose corners go up or down, a shadow stroke under the lip; open —
// dark red inside, a white row of teeth above, the tongue below; bared teeth; the round mouth of surprise
export function mouth(d, mx, my, ex, o = {}) {
  const m = P.mouth, w = m.w, lw = P.line, full = m.full, xl = mx - w * 0.5, xr = mx + w * 0.5, onDark = o.onDark ?? true;
  const lineCol = onDark ? '#6b5f5a' : INK;
  if (ex.round > 0.5) {
    const r = w * (0.2 + 0.08 * Math.min(1, ex.dep / 12)) * Math.min(1, 0.3 + ex.round), c = mx;
    const shape = [[c - r * 0.75, my + 2], [c, my - r * 0.75 + 1], [c + r * 0.8, my + 2], [c, my + r * 1.5 + 2]];
    d.fill(shape, '#5a2420'); d.contour(shape, lw * 0.8, { color: onDark ? '#3a1512' : INK });
    return;
  }
  if (ex.dep < 2.2) {
    const c = ex.curve;
    if (!onDark) d.line([[mx - w * 0.225, my + 7], [mx, my + 8.5], [mx + w * 0.25, my + 6.5]], lw * 0.8, 'swell', { nib: 0, op: 0.7 });
    d.line([[xl - 1, my - 2.5 * c + 0.5], [mx - w * 0.2, my + 0.9 * c], [mx, my + 1.0 * c - 0.2], [mx + w * 0.25, my + 0.9 * c], [xr + 2, my - 3.5 * c + 0.5]], lw * (onDark ? 1.5 : 1), 'swell', { nib: 0, color: lineCol });
    return;
  }
  const sn = ex.snarl, big = ex.big, dep = ex.dep * full / 1.2 * (o.depK ?? 1);
  const L = xl - w * 0.18 * big, R = xr + w * 0.22 * big, cxm = (L + R) / 2, W = R - L, lerp = (a, b) => a + (b - a) * sn;
  const top = [[L, lerp(my - 3.5, my + 1), 'c'], [cxm - W * 0.2, lerp(my + 0.5, my - 3)], [cxm + W * 0.2, lerp(my + 0.5, my - 3)], [R, lerp(my - 4.5, my + 2), 'c']];
  const bot = [[cxm + W * lerp(0.3, 0.25), my + dep * lerp(0.8, 1)], [cxm, my + dep * lerp(1, 1.04)], [cxm - W * lerp(0.28, 0.2), my + dep * lerp(0.8, 1)]];
  const shape = top.concat(bot);
  d.fill(shape, '#5a2420');
  const cid = d.clip(shape);
  d.open(null, cid);
  if (sn > 0.5) {
    d.fill([[L - 2, my - 6], [R + 2, my - 6], [R + 2, my + dep + 3], [L - 2, my + dep + 3]], '#fbf6e8', { n: 1 });
    d.line([[L, my + dep * 0.45], [R, my + dep * 0.5]], 1.2, 'even', { nib: 0 });
    for (let i = 1; i < 6; i++) { const x = L + W * i / 6; d.line([[x, my - 3], [x, my + dep]], 0.9, 'even', { nib: 0 }); }
  } else {
    const th = Math.min(dep * 0.36, 6.5);       // the row of teeth keeps its height as the mouth opens wider
    d.fill([[L - 2, my - 8], [R + 2, my - 8], [R + 2, my + th], [cxm, my + th * 1.22], [L - 2, my + th]], '#fbf6e8');
    d.fill([[cxm - W * 0.32, my + dep + 2], [cxm - W * 0.12, my + dep * 0.6], [cxm + W * 0.14, my + dep * 0.58], [cxm + W * 0.34, my + dep + 2]], '#cf6a55');
  }
  d.close();
  d.contour(shape, lw * 0.9, { nib: 0.2 });
  if (!onDark) { d.line([[R + 1, my - 9], [R + 5, my - 3], [R + 3, my + 4]], lw * 0.8, 'swell', { nib: 0 }); d.line([[L - 1, my - 8], [L - 3.5, my - 3], [L - 2, my + 3]], lw * 0.7, 'swell', { nib: 0 }); }
}
