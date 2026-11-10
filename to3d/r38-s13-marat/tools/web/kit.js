// The С13 medium in JavaScript: styles/s13-ukiyo-e/tools/kit.py (the woodblock print as SVG: the brush line of the key
// block whose weight follows its direction, flat printed colour, cloth patterns printed flat, bokashi, the sheet with
// its ground, border, name slip and seal, paper and wood grain over everything) and the face of parts.py (eye, brow,
// nose, mouth), ported so the 3D is printed with the drawing's own means.
// What is added for a moving 3D form:
//   Doc.T     — an affine frame (a feature's place on the turned head); curves are sampled in the drawing's units, then
//               carried into the picture, and the brush's width is given there (a line keeps its weight when the form
//               foreshortens);
//   Doc.block — a colour block whose shape is a picture (the parts of the 3D as they are seen) instead of a polygon;
//               a cloth pattern is printed over its own block through that picture as a mask.
export const INK = '#211c1c', PAPER = '#eee3cb', SKIN = '#f4e7d0', RED = '#b8402f', WHITE = '#fbf6e8';

const F = v => String(+v.toFixed(1)), F2 = v => String(+v.toFixed(2));

export function rng(seed) {
  let a = (seed >>> 0) || 1;
  const f = () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  f.uniform = (lo, hi) => lo + (hi - lo) * f();
  return f;
}

// ---------------------------------------------------------------- curves (kit.py: _cr_run, curve)
function crRun(p, n, closed = false) {
  const m = p.length;
  if (m < 3 && !closed) {
    if (m === 2) return Array.from({ length: n + 1 }, (_, i) => [p[0][0] + (p[1][0] - p[0][0]) * i / n, p[0][1] + (p[1][1] - p[0][1]) * i / n]);
    return p.map(q => [q[0], q[1]]);
  }
  const out = [], spans = closed ? m : m - 1;
  for (let i = 0; i < spans; i++) {
    let p0, p1, p2, p3;
    if (closed) { p0 = p[(i - 1 + m) % m]; p1 = p[i]; p2 = p[(i + 1) % m]; p3 = p[(i + 2) % m]; }
    else {
      p1 = p[i]; p2 = p[i + 1];
      p0 = i > 0 ? p[i - 1] : [2 * p1[0] - p2[0], 2 * p1[1] - p2[1]];
      p3 = i + 2 < m ? p[i + 2] : [2 * p2[0] - p1[0], 2 * p2[1] - p1[1]];
    }
    for (let k = 0; k < n; k++) {
      const t = k / n, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(a => 0.5 * (2 * p1[a] + (-p0[a] + p2[a]) * t + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t2 + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t3)));
    }
  }
  if (!closed) out.push([p[m - 1][0], p[m - 1][1]]);
  return out;
}
// a smooth curve through pts; points tagged 'c' ([x, y, 'c']) stay corners
export function curve(pts, closed = false, n = 8) {
  let xy = pts.map(p => [p[0], p[1]]);
  let corners = []; pts.forEach((p, i) => { if (p[2] === 'c') corners.push(i); });
  if (!corners.length) return crRun(xy, n, closed);
  if (closed) { const k = corners[0]; xy = [...xy.slice(k), ...xy.slice(0, k), xy[k]]; corners = [...corners.map(c => c - k), xy.length - 1]; }
  else corners = [...new Set([0, ...corners, xy.length - 1])].sort((a, b) => a - b);
  const out = [];
  for (let i = 0; i + 1 < corners.length; i++) { const run = crRun(xy.slice(corners[i], corners[i + 1] + 1), n); out.push(...(out.length ? run.slice(1) : run)); }
  if (closed) out.pop();
  return out;
}
export const pathD = (sm, closed = true) => 'M' + sm.map(([x, y]) => F(x) + ' ' + F(y)).join('L') + (closed ? 'Z' : '');

// ---------------------------------------------------------------- the brush (kit.py: _prof, brush_poly)
function prof(kind, t) {
  if (kind === 'taper') return Math.min(1, t / 0.05 + 0.25) * (0.1 + 0.9 * (1 - t) ** 0.9);        // a pressed start, a long tail
  if (kind === 'tail') return Math.min(1, (1 - t) / 0.05 + 0.25) * (0.1 + 0.9 * t ** 0.9);
  if (kind === 'swell') return 0.12 + 0.88 * Math.sin(Math.PI * t) ** 0.7;
  if (kind === 'even') return Math.min(1, t / 0.06 + 0.3, (1 - t) / 0.06 + 0.3);                    // the key block's hair line
  if (kind === 'press') return 0.55 + 0.45 * Math.abs(Math.cos(Math.PI * t)) ** 1.5 * Math.min(1, t / 0.03 + 0.4, (1 - t) / 0.03 + 0.2);
  if (kind === 'full') return 1;
  throw new Error(kind);
}
// the outline of a stroke of varying width along the sampled curve sm (picture points)
export function brushPoly(sm, w, kind = 'swell', nib = 0.3, closed = false, seed = 0, ends = null) {
  const r = rng(seed * 7919 + 13), n = sm.length, seg = [0];
  for (let i = 1; i < n; i++) seg.push(seg[i - 1] + Math.hypot(sm[i][0] - sm[i - 1][0], sm[i][1] - sm[i - 1][1]));
  const total = seg[n - 1] || 1, ph1 = r.uniform(0, 6.28), ph2 = r.uniform(0, 6.28), left = [], right = [];
  for (let i = 0; i < n; i++) {
    const a = closed || i > 0 ? sm[(i - 1 + n) % n] : sm[i], b = closed || i < n - 1 ? sm[(i + 1) % n] : sm[i];
    const dx = b[0] - a[0], dy = b[1] - a[1], ln = Math.hypot(dx, dy) || 1, nx = -dy / ln, ny = dx / ln, t = seg[i] / total;
    // the brush is held at a slant: strokes running down-right are full, up-right are light
    let k = (1 - nib) + nib * (0.5 + 0.5 * Math.cos(2 * (Math.atan2(dy, dx) - 1.0)));
    // the hand: a slow uneven pressure
    k *= 1 + 0.10 * Math.sin(ph1 + seg[i] * 0.045) + 0.06 * Math.sin(ph2 + seg[i] * 0.13);
    let pr = closed ? 1 : prof(kind, t);
    if (ends && !closed) pr = Math.min(1, pr, 0.3 + seg[i] / ends, 0.3 + (total - seg[i]) / ends);    // pointed ends of a fixed length
    const hw = 0.5 * w * k * pr;
    left.push([sm[i][0] + nx * hw, sm[i][1] + ny * hw]); right.push([sm[i][0] - nx * hw, sm[i][1] - ny * hw]);
  }
  if (closed) return pathD(left) + pathD(right.reverse());
  return pathD([...left, ...right.reverse()]);
}

// ---------------------------------------------------------------- cloth patterns, printed flat (kit.py)
export const PATTERNS = {
  stripes: (color, gap = 14, band = 6) => [gap, gap, `<rect width="${F(band)}" height="${F(gap)}" fill="${color}"/>`],
  checks: (color, size = 12) => [2 * size, 2 * size, `<rect width="${F(size)}" height="${F(size)}" fill="${color}"/><rect x="${F(size)}" y="${F(size)}" width="${F(size)}" height="${F(size)}" fill="${color}"/>`],
  dots: (color, gap = 9, r = 1.6) => [gap, gap, `<circle cx="${F(gap * 0.25)}" cy="${F(gap * 0.25)}" r="${F2(r)}" fill="${color}"/><circle cx="${F(gap * 0.75)}" cy="${F(gap * 0.75)}" r="${F2(r)}" fill="${color}"/>`],
  asanoha: (color, size = 22, w = 1.0) => {       // hemp leaf: six-pointed stars of straight lines
    const a = size, h = size * 0.8660254, ln = [];
    const seg = (x1, y1, x2, y2) => ln.push(`M${F(x1)} ${F(y1)}L${F(x2)} ${F(y2)}`);
    for (const [ox, oy] of [[0, 0], [a / 2, h]]) for (const dx of [-a, 0, a]) {
      const cx = ox + dx, cy = oy;
      for (let k = 0; k < 6; k++) {
        const ang = Math.PI / 3 * k, ang2 = ang + Math.PI / 6, r2 = a / Math.sqrt(3), px = cx + r2 * Math.cos(ang2), py = cy + r2 * Math.sin(ang2);
        seg(cx, cy, cx + a * Math.cos(ang), cy + a * Math.sin(ang));
        seg(px, py, cx + a * Math.cos(ang), cy + a * Math.sin(ang));
        seg(px, py, cx + a * Math.cos(ang + Math.PI / 3), cy + a * Math.sin(ang + Math.PI / 3));
      }
    }
    return [a, 2 * h, `<path d="${ln.join('')}" stroke="${color}" stroke-width="${F2(w)}" fill="none"/>`];
  },
  seigaiha: (color, r = 14, w = 1.0) => {         // blue sea waves: overlapping arcs in rows
    const arcs = [];
    for (const [cx, cy] of [[0, r], [2 * r, r], [r, 0], [r, 2 * r], [-r, 0], [3 * r, 0], [-r, 2 * r], [3 * r, 2 * r]])
      for (const k of [1.0, 0.7, 0.4]) { const rr = r * k; arcs.push(`M${F(cx - rr)} ${F(cy)}A${F(rr)} ${F(rr)} 0 0 1 ${F(cx + rr)} ${F(cy)}`); }
    return [2 * r, 2 * r, `<path d="${arcs.join('')}" stroke="${color}" stroke-width="${F2(w)}" fill="none"/>`];
  },
  blossoms: (color, gap = 34, r = 4.0, heart = null) => {      // small five-petal flowers scattered
    let body = '';
    for (const [cx, cy, k] of [[gap * 0.25, gap * 0.3, 1.0], [gap * 0.75, gap * 0.8, 0.8]]) {
      for (let i = 0; i < 5; i++) { const a = (72 * i - 90) * Math.PI / 180; body += `<circle cx="${F(cx + r * k * Math.cos(a))}" cy="${F(cy + r * k * Math.sin(a))}" r="${F2(r * k * 0.62)}" fill="${color}"/>`; }
      if (heart) body += `<circle cx="${F(cx)}" cy="${F(cy)}" r="${F2(r * k * 0.45)}" fill="${heart}"/>`;
    }
    return [gap, gap, body];
  },
  kasuri: (color, gap = 16, size = 5) => {
    let body = '';
    for (const [cx, cy] of [[gap * 0.25, gap * 0.25], [gap * 0.75, gap * 0.75]]) body += `<path d="M${F(cx - size / 2)} ${F(cy)}h${F(size)}M${F(cx)} ${F(cy - size / 2)}v${F(size)}" stroke="${color}" stroke-width="${F2(size * 0.3)}"/>`;
    return [gap, gap, body];
  },
};

// ---------------------------------------------------------------- the sheet
export class Doc {
  constructor(w, h, seed = 1) {
    this.w = w; this.h = h; this.seed = seed;
    this.blocks = []; this.col = []; this.key = []; this.defs = [];
    this.T = [[1, 0, 0, 1, 0, 0]]; this.map = null; this.wk = 1; this.n = 0; this.ids = 0;
  }
  id(p = 'i') { return p + (++this.ids); }
  // the drawing's units → the picture: an affine frame, or (map set) a point carried onto the 3D face
  tr(pts) {
    if (this.map) return pts.map(([x, y]) => this.map(x, y) || [NaN, NaN]);
    const [a, b, c, d, e, f] = this.T[this.T.length - 1]; return pts.map(([x, y]) => [a * x + c * y + e, b * x + d * y + f]);
  }
  mat() { return `matrix(${this.T[this.T.length - 1].map(F2).join(' ')})`; }
  put(s, layer) { (layer === 'key' ? this.key : this.col).push(s); }
  // a flat printed colour
  fill(pts, color, o = {}) {
    const sm = this.tr(curve(pts, o.closed ?? true, o.n ?? 8));
    this.put(`<path d="${pathD(sm)}" fill="${color}"${o.op != null && o.op !== 1 ? ` opacity="${F2(o.op)}"` : ''}/>`, o.layer || 'col');
    return sm;
  }
  clip(pts, n = 8) { const cid = this.id('c'); this.defs.push(`<clipPath id="${cid}"><path d="${pathD(this.tr(curve(pts, true, n)))}"/></clipPath>`); return cid; }
  open(cid, layer = 'col') { this.put(`<g clip-path="url(#${cid})">`, layer); }
  close(layer = 'col') { this.put('</g>', layer); }
  // one stroke of the brush (w in the drawing's line units)
  line(pts, w = 3.0, kind = 'swell', o = {}) {
    const sm = this.tr(curve(pts, false, o.n ?? 8));
    if (sm.some(q => Number.isNaN(q[0]))) return sm;
    this.put(`<path d="${brushPoly(sm, w * this.wk, kind, o.nib ?? 0.3, false, ++this.n)}" fill="${o.color || INK}"${o.op != null && o.op !== 1 ? ` opacity="${F2(o.op)}"` : ''}/>`, o.layer || (o.color ? 'col' : 'key'));
    return sm;
  }
  // the closed outline of a shape, its weight changing with direction
  contour(pts, w = 3.0, o = {}) {
    const sm = this.tr(curve(pts, true, o.n ?? 8));
    this.put(`<path d="${brushPoly(sm, w * this.wk, 'even', o.nib ?? 0.45, true, ++this.n)}" fill="${o.color || INK}" fill-rule="evenodd"/>`, o.layer || 'key');
  }
  dot(x, y, r, color = INK, layer = 'col') { this.put(`<circle cx="${F(x)}" cy="${F(y)}" r="${F2(r)}" fill="${color}" transform="${this.mat()}"/>`, layer); }
  // bokashi, a round soft patch (a cheek)
  blush(x, y, r, color, op) {
    const gid = this.id('b');
    this.defs.push(`<radialGradient id="${gid}"><stop offset="0" stop-color="${color}" stop-opacity="${F2(op)}"/><stop offset="0.55" stop-color="${color}" stop-opacity="${F2(op * 0.55)}"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></radialGradient>`);
    this.put(`<circle cx="${F(x)}" cy="${F(y)}" r="${F(r)}" fill="url(#${gid})" transform="${this.mat()}"/>`, 'col');
  }
  // a cloth pattern, printed flat over a colour block: kind and its numbers (kit.py), where its origin is in the
  // picture and how many picture pixels a drawing unit is; maskHref — the block as a picture
  pattern(kind, args, at, scale, maskHref, op = 1) {
    const [pw, ph, body] = PATTERNS[kind](...args), pid = this.id('p'), mid = this.id('m');
    this.defs.push(`<pattern id="${pid}" width="${F(pw)}" height="${F(ph)}" patternUnits="userSpaceOnUse" patternTransform="translate(${F(at[0])} ${F(at[1])}) rotate(${F(at[2] || 0)}) scale(${scale.toFixed(4)})">${body}</pattern>` +
      `<mask id="${mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="${this.w}" height="${this.h}" style="mask-type:alpha"><image href="${maskHref}" width="${this.w}" height="${this.h}"/></mask>`);
    this.blocks.push(`<rect width="${this.w}" height="${this.h}" fill="url(#${pid})" mask="url(#${mid})"${op !== 1 ? ` opacity="${F2(op)}"` : ''}/>`);
  }
}

// a stroke along picture points (a contour found on the 3D form, a fold): no resampling, the brush's outline only
export function stroke(d, P, w, kind = 'even', o = {}) {
  if (P.length < 2) return;
  d.put(`<path d="${brushPoly(P, w * d.wk, kind, o.nib ?? 0.45, !!o.closed, o.seed ?? ++d.n, o.ends ? o.ends * d.wk : null)}" fill="${o.color || INK}"${o.closed ? ' fill-rule="evenodd"' : ''}${o.op != null && o.op !== 1 ? ` opacity="${F2(o.op)}"` : ''}/>`, o.layer || 'key');
}
// short separate hairs growing out of an edge (kit.py's fringe: the hairline of a print, a beard's edge); P — picture
// points along the edge, side — which way they grow, lengths in picture pixels
export function fringe(d, P, o = {}) {
  const { length = 10, w = 1.0, color = INK, lean = 0, step = 3, side = 1, vary = 0.4, seed = 1, layer = 'key' } = o;
  const r = rng(seed); let acc = 0;
  for (let i = 1; i < P.length; i++) {
    const dx = P[i][0] - P[i - 1][0], dy = P[i][1] - P[i - 1][1], ln = Math.hypot(dx, dy);
    acc += ln; if (acc < step || ln === 0) continue; acc = 0;
    const nx = -dy / ln * side, ny = dx / ln * side, tx = dx / ln, ty = dy / ln;
    const L = length * (1 + r.uniform(-vary, vary)), le = lean + r.uniform(-0.15, 0.15);
    const e = [P[i][0] + (nx + tx * le) * L, P[i][1] + (ny + ty * le) * L], m = [P[i][0] + (nx + tx * le * 0.3) * L * 0.5, P[i][1] + (ny + ty * le * 0.3) * L * 0.5];
    d.put(`<path d="${brushPoly(curve([P[i], m, e], false, 4), w * d.wk, 'taper', 0.1, false, i)}" fill="${color}"/>`, layer);
  }
}

// the whole sheet as SVG: paper, the printed ground with a band of bokashi along its top (and bottom), the colour
// blocks, the key block's lines, the name slip and the seal, the border; over everything — wood grain, paper, age
export function svg(d, sh = {}) {
  const { w, h } = d, m = sh.margin ?? Math.round(Math.min(w, h) * 0.033), sd = d.seed, iw = w - 2 * m, ih = h - 2 * m;
  let defs = d.defs.join('') +
    `<filter id="paper" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB"><feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="${sd}"/><feColorMatrix values="0 0 0 0 0.42  0 0 0 0 0.33  0 0 0 0 0.2  0.85 0 0 0 -0.27"/></filter>` +
    `<filter id="grain" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB"><feTurbulence type="fractalNoise" baseFrequency="0.0035 0.11" numOctaves="3" seed="${sd + 5}"/><feColorMatrix values="0 0 0 0 0.97  0 0 0 0 0.93  0 0 0 0 0.82  2.4 0 0 0 -1.2"/></filter>` +
    `<filter id="age" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB"><feTurbulence type="fractalNoise" baseFrequency="0.006" numOctaves="3" seed="${sd + 9}"/><feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.36  0 0 0 0 0.16  1.3 0 0 0 -0.5"/></filter>` +
    `<filter id="soft" x="0" y="0" width="100%" height="100%"><feGaussianBlur stdDeviation="0.55"/></filter>` +
    `<clipPath id="sheet"><rect x="${m}" y="${m}" width="${iw}" height="${ih}"/></clipPath>`;
  let ground = '', over = '';
  if (sh.ground) {
    ground = `<rect x="${m}" y="${m}" width="${iw}" height="${ih}" fill="${sh.ground}"/>`;
    if (sh.top) {
      defs += `<linearGradient id="gtop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${sh.top}"/><stop offset="0.5" stop-color="${sh.top}" stop-opacity="0.35"/><stop offset="1" stop-color="${sh.top}" stop-opacity="0"/></linearGradient>`;
      ground += `<rect x="${m}" y="${m}" width="${iw}" height="${F(ih * 0.3)}" fill="url(#gtop)"/>`;
    }
    if (sh.bottom) {
      defs += `<linearGradient id="gbot" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="${sh.bottom}"/><stop offset="0.5" stop-color="${sh.bottom}" stop-opacity="0.35"/><stop offset="1" stop-color="${sh.bottom}" stop-opacity="0"/></linearGradient>`;
      ground += `<rect x="${m}" y="${F(m + ih * 0.78)}" width="${iw}" height="${F(ih * 0.22)}" fill="url(#gbot)"/>`;
    }
  }
  if (sh.name) {       // the title slip — the name, written downwards — and the red seal under it
    const size = sh.size ?? Math.max(13, Math.min(w, h) * 0.034), n = [...sh.name].length, cw = size * 1.5, chh = size * 1.12 * n + size * 0.7;
    const x = w - m - cw - size * 0.9, y = m + size * 1.1;
    over += `<rect x="${F(x)}" y="${F(y)}" width="${F(cw)}" height="${F(chh)}" fill="#f3ead6"/><rect x="${F(x)}" y="${F(y)}" width="${F(cw)}" height="${F(chh)}" fill="none" stroke="${INK}" stroke-width="${F2(size * 0.06)}"/>`;
    [...sh.name].forEach((ch, i) => { over += `<text x="${F(x + cw / 2)}" y="${F(y + size * 1.12 * (i + 1) + size * 0.05)}" font-family="Georgia, 'PT Serif', 'DejaVu Serif', serif" font-size="${F(size)}" text-anchor="middle" fill="${INK}">${ch}</text>`; });
    const sy = y + chh + size * 0.45, ss = size * 1.05, sx = x + (cw - ss) / 2;
    over += `<rect x="${F(sx)}" y="${F(sy)}" width="${F(ss)}" height="${F(ss)}" rx="2" fill="${RED}"/>` +
      `<path d="M${F(sx + ss * 0.22)} ${F(sy + ss * 0.3)}h${F(ss * 0.56)}M${F(sx + ss * 0.5)} ${F(sy + ss * 0.3)}v${F(ss * 0.48)}M${F(sx + ss * 0.28)} ${F(sy + ss * 0.78)}h${F(ss * 0.44)}" stroke="#f3ead6" stroke-width="${F2(ss * 0.1)}" fill="none"/>`;
  }
  const paper = sh.plain ? '' :
    `<rect width="${w}" height="${h}" filter="url(#grain)" opacity="0.15" style="mix-blend-mode:screen"/>` +
    `<rect width="${w}" height="${h}" filter="url(#paper)" opacity="0.42" style="mix-blend-mode:multiply"/>` +
    `<rect width="${w}" height="${h}" filter="url(#age)" opacity="0.28" style="mix-blend-mode:multiply"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}"><defs>${defs}</defs>` +
    `<rect width="${w}" height="${h}" fill="${PAPER}"/>${ground}` +
    `<g clip-path="url(#sheet)"><g filter="url(#soft)">${d.blocks.join('')}</g>${d.col.join('')}${d.key.join('')}</g>${over}` +
    (m ? `<rect x="${m}" y="${m}" width="${iw}" height="${ih}" fill="none" stroke="${INK}" stroke-width="${F2(Math.max(1.4, Math.min(w, h) * 0.0027))}"/>` : '') +
    paper + '</svg>';
}

// ---------------------------------------------------------------- the face (parts.py), in head units: the eye line
// y = 0, the face's middle x = 0. p — the character's numbers (parts.P); ex — what the face does now:
// {open, lift, tilt, look: [x, y], mouth, blush}
export function P(o = {}) {
  const p = {
    skin: SKIN, line: 2.0, long: 1.0,
    eye: { w: 36, h: 9, iris: 7.2, lid: 3.4, slant: -2.0, lower: 0.5, white: WHITE, color: '#2e2422', lash: 0.0, y: 0 },
    brow: { kind: 'arc', w: 2.6, len: 40, arch: 5, y: -25, tilt: 0 },
    nose: { kind: 'soft', s: 1.0 }, mouth: { w: 22, y: 62, lip: RED, full: 1.0 }, blush: ['#e8a48a', 0.0],
  };
  for (const [k, v] of Object.entries(o)) p[k] = v && typeof v === 'object' && !Array.isArray(v) && p[k] ? { ...p[k], ...v } : v;
  return p;
}
// An eye: a full upper lid drawn with pressure, a hair-thin lower lid, a dark iris half under the lid. k — its width
// against the near eye; inner — the side of the inner corner (−1 left, +1 right). ex.closed (0…1): a blink — the lid
// comes down (not the arc of a laugh, which is ex.open 0)
export function eye(d, p, cx, cy, k, inner, ex) {
  const e = p.eye, w = e.w * k, sl = e.slant - ex.tilt * 0.35, xi = cx + inner * w / 2, xo = cx - inner * w / 2, lid = e.lid * (k < 0.8 ? 0.8 : 1.0);
  if (ex.open <= 0.05) {          // laughing: the eye closes into an arc
    d.line([[xi, cy + 2], [cx + inner * w * 0.1, cy - e.h * 0.75], [xo, cy + 1 + sl * 0.3], [xo - inner * 3, cy + 4]], lid * 1.1, 'swell');
    if (e.lash) d.line([[xo, cy + 1], [xo - inner * 5, cy + 1]], lid * 0.5, 'taper');
    return;
  }
  const h0 = e.h * ex.open, c = Math.max(0, Math.min(1, ex.closed || 0));
  if (c > 0.85) {                 // shut in a blink: the lid's line lies on the lower one
    d.line([[xi, cy + h0 * 0.45], [cx + inner * w * 0.2, cy + h0 * 0.8], [cx - inner * w * 0.15, cy + h0 * 0.74 + sl * 0.4], [xo, cy + sl], [xo - inner * (2 + e.lash * 4), cy + sl + 1 - e.lash]], lid, 'swell', { nib: 0.1 });
    return;
  }
  const up0 = [[xi, cy + h0 * 0.45], [xi - inner * w * 0.2, cy - h0 * 0.55], [cx - inner * w * 0.02, cy - h0], [xo + inner * w * 0.12, cy - h0 * 0.45 + sl * 0.6], [xo, cy + sl]];
  const lo = [[xo, cy + sl], [cx - inner * w * 0.15, cy + h0 * 0.72 + sl * 0.4], [cx + inner * w * 0.2, cy + h0 * 0.78], [xi, cy + h0 * 0.45]];
  // the lid on its way down: the upper line moves toward the lower one
  const dn = [lo[3], [xi - inner * w * 0.2, cy + h0 * 0.7], lo[2], lo[1], lo[0]];
  const up = up0.map((q, i) => [q[0] + (dn[i][0] - q[0]) * c, q[1] + (dn[i][1] - q[1]) * c]);
  const opening = [...up, ...lo.slice(1, -1)];
  d.fill(opening, e.white);
  const cid = d.clip(opening), ix = cx + ex.look[0] * k - inner * w * 0.03, iy = cy - h0 * 0.2 + ex.look[1];
  d.open(cid); d.dot(ix, iy, e.iris * (k < 0.8 ? 0.86 : 1.0), e.color); d.dot(ix, iy, e.iris * 0.45, INK); d.close();
  d.line([...up, [xo - inner * (2 + e.lash * 4), cy + sl - e.lash * 2 * (1 - c)]], lid, 'swell', { nib: 0.1 });
  if (e.lower) d.line(lo.slice(0, 3), Math.max(0.9, lid * 0.3), 'even', { op: e.lower, nib: 0.0 });
  if (e.crease && c < 0.3) d.line([[xi - inner * w * 0.1, cy - h0 * 0.9 - 3], [cx, cy - h0 - 4.5], [xo + inner * w * 0.1, cy - h0 * 0.5 - 3 + sl]], 1.0, 'swell', { op: e.crease, nib: 0 });
}
export function brow(d, p, cx, k, inner, ex, cy = 0) {
  const b = p.brow, L = b.len * k, y = cy + b.y - ex.lift + p.eye.y, tilt = b.tilt + ex.tilt;
  const xi = cx + inner * L / 2, xo = cx - inner * L / 2, yi = y - tilt * 0.5, yo = y + tilt * 0.35 + 2;
  const pts = [[xi, yi], [cx + inner * L * 0.1, y - b.arch - Math.abs(tilt) * 0.1], [xo, yo]];
  if (b.kind === 'arc') d.line(pts, b.w, 'swell', { nib: 0.1 });            // a thin high arc: the brow of the beauties
  else d.line(pts, b.w, 'taper', { nib: 0.15 });                             // pressed at the inner end, tailing off: Sharaku's
}
// the nose seen from the front: one stroke down with a hook at the tip, and the nostril (parts.nose, view 'f')
export function noseFront(d, p, op = 1, sg = 1) {
  const nz = p.nose, s = nz.s, k = nz.kind, lw = p.line * 1.15, oy = p.eye.y, f = (x, y) => [sg * x * s, oy + y * s];
  if (k === 'soft' || k === 'long' || k === 'snub') {
    const top = { soft: 6, long: 0, snub: 22 }[k], bot = { soft: 38, long: 44, snub: 34 }[k];
    d.line([f(-5, top), f(-6, bot - 14), f(-9, bot - 3), f(-5, bot + 1)], lw, 'tail', { nib: 0.2, op });
    d.line([f(-5, bot + 1), f(0, bot + 3), f(6, bot + 1)], lw * 0.9, 'swell', { nib: 0, op });
    d.line([f(8, bot - 1), f(11, bot - 4), f(9, bot - 8)], lw * 0.8, 'taper', { nib: 0, op });
  } else {
    const wdt = k === 'broad' ? 15 : 12, bot = k === 'big' ? 46 : 42;
    d.line([f(-6, 0), f(-7, bot - 18), f(-wdt, bot - 6), f(-wdt + 2, bot + 2), f(-6, bot + 2)], lw * 1.2, 'even', { nib: 0.2, op });
    d.line([f(-6, bot + 2), f(0, bot + 5), f(6, bot + 2)], lw, 'swell', { nib: 0, op });
    d.line([f(6, bot + 2), f(wdt - 1, bot + 1), f(wdt + 1, bot - 6), f(wdt - 4, bot - 12)], lw, 'taper', { nib: 0.1, op });
  }
}
// the mouth (parts.mouth): mx, my — its centre; fl, fr — its left and right share (0.5, 0.5 in front)
export function mouth(d, p, ex, mx, my, fl = 0.5, fr = 0.5) {
  const m = p.mouth, w = m.w, kind = ex.mouth, lip = m.lip, full = m.full, xl = mx - w * fl, xr = mx + w * fr, lw = p.line, as = (fr - fl) * w;
  const lips = (up = 1.0, low = 1.0, dy = 0.0) => {
    if (!lip) {       // a man's mouth: only a shadow stroke under the lower lip
      d.line([[mx - w * fl * 0.45, my + 7 + dy], [mx + as * 0.2, my + 8.5 + dy], [mx + w * fr * 0.5, my + 6.5 + dy]], lw * 0.8, 'swell', { nib: 0, op: 0.7 });
      return;
    }
    if (up) d.fill([[xl + w * 0.08, my + dy, 'c'], [mx - w * fl * 0.35, my - 3.6 * full * up + dy], [mx + as * 0.1, my - 2.0 * full * up + dy], [mx + w * fr * 0.4, my - 3.6 * full * up + dy], [xr - w * 0.08, my + dy, 'c'], [mx + as * 0.1, my + 0.8 + dy]], lip);
    if (low) d.fill([[xl + w * 0.2, my + 0.5 + dy, 'c'], [mx + as * 0.1, my + 1.6 + dy], [xr - w * 0.2, my + 0.5 + dy, 'c'], [mx + w * fr * 0.35, my + 5.5 * full * low + dy], [mx - w * fl * 0.3, my + 5.5 * full * low + dy]], lip);
  };
  if (kind === 'calm') {
    lips();
    d.line([[xl, my - 0.5], [mx - w * fl * 0.4, my + 0.8], [mx + as * 0.1, my + 0.2], [mx + w * fr * 0.5, my + 0.9], [xr, my - 0.8]], lw, 'swell', { nib: 0 });
  } else if (kind === 'smile') {
    lips();
    d.line([[xl - 1, my - 2.5], [mx - w * fl * 0.4, my + 1.0], [mx + as * 0.1, my + 1.2], [mx + w * fr * 0.5, my + 1.0], [xr + 2, my - 3.5]], lw, 'swell', { nib: 0 });
  } else if (kind === 'pressed') {
    lips(0.6, 0.6);
    d.line([[xl - 1, my + 1.0], [mx, my], [xr + 2, my + 1.0]], lw * 1.25, 'even', { nib: 0 });
    d.line([[xr + 2, my - 1.5], [xr + 3.5, my + 1], [xr + 2, my + 3.5]], lw * 0.7, 'swell', { nib: 0 });
  } else if (kind === 'sad') {
    lips(0.8, 1.0);
    d.line([[xl - 1, my + 3], [mx - w * fl * 0.4, my + 0.2], [mx + as * 0.1, my - 0.4], [mx + w * fr * 0.5, my + 0.4], [xr + 1, my + 3.5]], lw, 'swell', { nib: 0 });
  } else if (kind === 'frown') {        // the へ mouth of Sharaku's actors: pulled down, a hook at each corner
    lips(0.5, 0.8, -1);
    d.line([[xl - 2, my + 6], [xl, my + 2.5], [mx - w * fl * 0.3, my - 1.5], [mx + as * 0.1, my - 2], [mx + w * fr * 0.5, my - 1], [xr, my + 3], [xr + 2.5, my + 7]], lw * 1.5, 'even', { nib: 0 });
  } else if (kind === 'o' || kind === 'gasp' || kind === 'talk') {
    // speech: the round mouth of the sheet's surprise, its size and roundness by the syllable
    const op = kind === 'talk' ? ex.talkOpen : 1, rd = kind === 'talk' ? ex.talkRound : 1;
    const r = w * (kind === 'gasp' ? 0.28 : 0.2) * (kind === 'talk' ? 0.75 + 0.5 * op : 1), c = mx + as * 0.25;
    const rx = kind === 'talk' ? r * (1.5 - 0.6 * rd) : r, ry = kind === 'talk' ? r * (0.25 + 1.5 * op) : r;
    const shape = [[c - rx * 0.75, my + 2], [c, my - ry * 0.75 + 1], [c + rx * 0.8, my + 2], [c, my + ry * 1.5 + 2]];
    if (lip) d.fill(shape.map(([x, y]) => [x + (x - c) * 0.45, y + (y - my - 2 - ry * 0.3) * 0.5]), lip);
    d.fill(shape, '#5a2420'); d.contour(shape, lw * 0.8);
  } else if (kind === 'snarl') {        // bared teeth: a white band cut by the teeth's lines
    const L = xl - w * 0.16, R = xr + w * 0.2, dep = 7 * full, cxm = (L + R) / 2 + as * 0.1;
    const shape = [[L, my + 1, 'c'], [cxm - (R - L) * 0.2, my - 3], [cxm + (R - L) * 0.2, my - 3], [R, my + 2, 'c'], [cxm + (R - L) * 0.25, my + dep], [cxm - (R - L) * 0.2, my + dep]];
    d.fill(shape, WHITE);
    const cid = d.clip(shape); d.open(cid, 'key');
    d.line([[L, my + dep * 0.45], [R, my + dep * 0.5]], 1.2, 'even', { nib: 0 });
    for (let i = 1; i < 6; i++) { const x = L + (R - L) * i / 6; d.line([[x, my - 3], [x, my + dep]], 0.9, 'even', { nib: 0 }); }
    d.close('key');
    d.contour(shape, lw * 0.9, { nib: 0.2 });
  } else if (kind === 'laugh' || kind === 'grin') {
    // an open mouth: dark red inside, a white row of teeth above, the tongue below. ex.jaw (0…1): how far it is open
    const big = kind === 'laugh' ? 0.8 : 1.25, L = xl - w * 0.18 * big, R = xr + w * 0.22 * big;
    const dep = (kind === 'laugh' ? 9 : 15) * full * (0.45 + 0.55 * (ex.jaw ?? 1)), cxm = (L + R) / 2 + as * 0.1;
    const top = [[L, my - 3.5, 'c'], [cxm - (R - L) * 0.2, my + 0.5], [cxm + (R - L) * 0.2, my + 0.5], [R, my - 4.5, 'c']];
    const bot = [[cxm + (R - L) * 0.3, my + dep * 0.8], [cxm, my + dep], [cxm - (R - L) * 0.28, my + dep * 0.8]];
    const shape = [...top, ...bot];
    d.fill(shape, '#5a2420');
    const cid = d.clip(shape); d.open(cid);
    d.fill([[L - 2, my - 8], [R + 2, my - 8], [R + 2, my + dep * 0.36], [cxm, my + dep * 0.44], [L - 2, my + dep * 0.36]], WHITE);
    d.fill([[cxm - (R - L) * 0.32, my + dep + 2], [cxm - (R - L) * 0.12, my + dep * 0.6], [cxm + (R - L) * 0.14, my + dep * 0.58], [cxm + (R - L) * 0.34, my + dep + 2]], '#cf6a55');
    d.close();
    d.contour(shape, lw * 0.9, { nib: 0.2 });
    if (lip) d.line([[L + 2, my + dep * 0.85 + 1.5], [cxm, my + dep + 3], [R - 3, my + dep * 0.85 + 1.5]], lw * 1.6, 'swell', { color: lip, nib: 0, layer: 'key' });
    // the laugh pushes the cheeks: a stroke at each corner
    d.line([[R + 1, my - 9], [R + 5, my - 3], [R + 3, my + 4]], lw * 0.8, 'swell', { nib: 0 });
    d.line([[L - 1, my - 8], [L - 3.5, my - 3], [L - 2, my + 3]], lw * 0.7, 'swell', { nib: 0 });
  }
}
