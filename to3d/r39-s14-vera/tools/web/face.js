// С14 in 3D — the head and the face. styles/s14-paper/tools/face.py carried over: the same spec (numbers and
// colours), the same pieces (white, iris, pupil, speck, the lid that casts a shadow on the eye, lashes, lower lid,
// brow, nose, mouth with teeth and tongue), the same expressions. What is new: the face piece is an egg with a jaw —
// its front outline is face.outline(yaw = 0), its depth is face.outline's profile — and the pieces are glued on its
// front, each a little higher than the one under it; the nose is a folded wedge standing off the face.
// Head space: the drawing's units, x to the viewer's right when she faces us, y down, z out of the face.
import { ell, strip, crescent, lens, corner, curve, mix, through, patch, loft, ringAt, slab, mesh0, U } from './paper.js';

export const DEFAULT = {
  skin: '#f0c9a4', rx: 80, ry: 100, jaw: .62, chin: 0, eye_y: 10, eye_gap: 36, eye_w: 15, eye_h: 13,
  iris: '#6b4a2f', lid: null, lash: false, lash_col: '#33241f', brow: '#6b4a2f', brow_w: 7, brow_len: 30, brow_y: -30,
  nose: 'button', nose_y: 38, nose_s: 1, mouth_y: 62, mouth_w: 22, lip: '#b8483f', inside: '#5c1a22',
  cheek: '#e8748a', cheek_r: 17, cheek_op: .42, ear: 1, neck_w: 34, rest: {}, on: {},
};
export const EXPR = {
  calm: { open: .78, tilt: 0, brow: 0, brow_dy: 0, mouth: 'smile', low: 0, eye: 1 },
  joy: { open: .80, tilt: 0, brow: .1, brow_dy: -6, mouth: 'grin', low: .55, eye: 1 },
  laugh: { open: 0, tilt: 0, brow: .15, brow_dy: -8, mouth: 'laugh', low: 0, eye: 1 },
  surprise: { open: 1.1, tilt: 0, brow: .12, brow_dy: -15, mouth: 'o', low: 0, eye: 1.12 },
  sad: { open: .62, tilt: .5, brow: .55, brow_dy: -3, mouth: 'frown', low: 0, eye: 1 },
  angry: { open: .60, tilt: -.55, brow: -.6, brow_dy: 9, mouth: 'grit', low: .25, eye: .95 },
  tired: { open: .58, tilt: .15, brow: .1, brow_dy: 0, mouth: 'flat', low: 0, eye: 1 },
};
export function exprOf(spec, name) {
  const e = { ...EXPR.calm };
  if (!name || name === 'calm') Object.assign(e, spec.rest);
  else Object.assign(e, EXPR[name], (spec.on || {})[name] || {});
  return e;
}
const NUM = ['open', 'tilt', 'brow', 'brow_dy', 'low', 'eye'];
// a mix of expressions {name: weight}: numbers mixed, the mouth is the heaviest one's (paper mouths are swapped, not bent)
export function mixExpr(spec, W) {
  const e = {}; let sum = 0, best = null, bw = -1;
  for (const k in W) if (W[k] > 1e-4) { const x = exprOf(spec, k); sum += W[k]; for (const n of NUM) e[n] = (e[n] || 0) + x[n] * W[k]; if (W[k] > bw) { bw = W[k]; best = x; } }
  if (!best) return exprOf(spec, 'calm');
  for (const n of NUM) e[n] /= sum;
  e.mouth = best.mouth;
  if (e.open < .3 && best.open > .05) e.open = Math.max(e.open, .3);       // passing by «laugh»: not a half-shut stare
  if (best.open <= .05 && bw / sum > .6) e.open = 0;
  return e;
}

// ---------------------------------------------------------------- the head: an egg with a jaw
export function headShape(spec) {
  const { rx, ry, jaw, chin } = spec, c = 1 + chin;
  const zf = through([[-1, -.15], [-.9, .40], [-.5, .76], [-.05, .84], [.32, .80], [.62, .74], [.9 * c, .58], [1.0 * c, .30]]);
  const zb = through([[-1, -.15], [-.88, -.65], [-.5, -1.0], [0, -1.08], [.42, -.82], [.6, -.42], [.86 * c, -.12], [1.0 * c, .30]]);
  const yOf = s => ry * s * (s > 0 ? 1 + chin * s ** 3 : 1);
  const wOf = s => rx * Math.sqrt(Math.max(0, 1 - s * s)) * (s > 0 ? 1 - (1 - jaw) * s ** 1.7 : 1);
  const sOf = y => { let s = Math.max(-1, Math.min(1, y / ry)); if (y > 0) for (let i = 0; i < 6; i++) s -= (s * (1 + chin * s ** 3) - y / ry) / (1 + 4 * chin * s ** 3); return Math.max(-1, Math.min(1, s)); };
  const P = .88;                                           // the ring a little square: a flatter front for the face
  const H = { spec, yOf, wOf, sOf, zf: y => rx * zf(y / ry), zb: y => rx * zb(y / ry) };
  // the face's surface under a point of the front view
  H.z = (x, y, grow = 1, add = 0) => {
    const s = sOf(y / grow), hw = wOf(s) * grow + add, f = H.zf(yOf(s)) * grow + add, b = H.zb(yOf(s)) * grow - add, zc = (f + b) / 2, d = (f - b) / 2;
    const cc = Math.min(1, Math.abs(x) / Math.max(hw, 1e-6)) ** (1 / P), ss = Math.sqrt(Math.max(0, 1 - cc * cc));
    return zc + d * ss ** P;
  };
  H.hw = y => wOf(sOf(y));
  // the shell: grow — scaled about the centre, add — pushed out (hair lies over the skull)
  H.shell = (grow = 1, add = 0, n = 40, m = 30) => {
    const rings = [];
    for (let i = 0; i <= m; i++) {
      const a = -Math.PI / 2 + Math.PI * (i + (i === 0 ? .12 : i === m ? -.12 : 0)) / m, s = Math.sin(a), y = yOf(s);
      rings.push(ringAt(y * grow, wOf(s) * grow + add, H.zf(y) * grow + add, H.zb(y) * grow - add, n, P).map(p => [p[0], p[1] - (i === 0 ? add : 0), p[2]]));
    }
    return loft(rings, { cap0: true, cap1: true });
  };
  return H;
}

// ---------------------------------------------------------------- the pieces (face.py)
function eye(cx, cy, w0, h0, sp, e, side) {
  const w = w0 * e.eye, h = h0 * e.eye, out = [], lidC = sp.lid || mix(sp.skin, '#c97a6a', .30), o = e.open, K = side < 0 ? 'L' : 'R';
  if (o <= .05) return [{ key: 'shut' + K, pts: crescent(cx - w * 1.05, cy + h * .25, cx + w * 1.05, cy + h * .25, -h * .75, h * .42), color: sp.lash_col, kind: 'card', layer: 2 }];
  out.push({ key: 'white' + K, pts: ell(cx, cy, w, h, 0, 10), color: '#fbf6ea', kind: 'card', layer: 2 });
  const look = (e.look || 0) * w * .3, ir = Math.min(h * .82, w * .62), iy = cy + h * .06 + (e.look_y || 0) * h * .3;
  out.push({ key: 'iris' + K, pts: ell(cx + look, iy, ir, ir, 0, 10), color: sp.iris, kind: 'flat', layer: 3 },
    { key: 'pupil' + K, pts: ell(cx + look, iy, ir * .52, ir * .52, 0, 8), color: '#241a1c', kind: 'flat', layer: 4 },
    { key: 'speck' + K, pts: ell(cx + look - ir * .38, iy - ir * .42, ir * .27, ir * .27, 20, 4).map(corner), color: '#fffaf0', kind: 'flat', layer: 5 });
  const k = 2 * Math.min(o, 1) - 1, tilt = e.tilt * side, n = 9, edge = [], top = [];
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1), s = Math.sin(Math.PI * t), x = cx - w * 1.16 + 2.32 * w * t;
    edge.push([x, cy + h * .12 - (h * k + h * .12) * s + tilt * h * (t - .5) * 1.5]);
    top.push([x, cy + h * .12 - h * 1.42 * s ** .75 - h * .05]);
  }
  if (o < 1.05) {
    out.push({ key: 'lid' + K, pts: [corner(top[0]), ...top.slice(1, -1), corner(top[n - 1]), ...edge.slice(1, -1).reverse()], color: lidC, kind: 'card', layer: 6 });
    if (sp.lash) {
      const th = h * .26, low = edge.map(([x, y], i) => [x, y + th * Math.sin(Math.PI * i / (n - 1)) ** .6]);
      const [ox, oy] = side > 0 ? edge[n - 1] : edge[0], flick = [ox + side * w * .34, oy - h * .42, 1];
      const body = side > 0 ? [...edge.slice(0, -1), flick, [ox, oy + th * .5], ...low.slice(1, -1).reverse()] : [flick, ...edge.slice(1), ...low.slice(1, -1).reverse(), [ox, oy + th * .5]];
      out.push({ key: 'lash' + K, pts: body, color: sp.lash_col, kind: 'flat', layer: 7 });
    }
  }
  if (e.low > .02) {
    const lo = e.low, X = i => cx - w * 1.25 + 2.5 * w * i / (n - 1), S = i => Math.sin(Math.PI * i / (n - 1));
    const up = Array.from({ length: n }, (_, i) => [X(i), cy + h * (1.05 - .95 * lo * S(i))]), dn = Array.from({ length: n }, (_, i) => [X(i), cy + h * (1.05 + .55 * S(i))]);
    out.push({ key: 'low' + K, pts: [corner(up[0]), ...up.slice(1, -1), corner(up[n - 1]), ...dn.slice(1, -1).reverse()], color: mix(sp.skin, '#e8a79a', .12), kind: 'card', layer: 6 });
  }
  return out;
}
function brow(cx, cy, sp, e, side) {
  const L = sp.brow_len, w = sp.brow_w, tl = e.brow, xi = cx - side * L * .5, xo = cx + side * L * .55;
  const yi = cy + e.brow_dy - tl * 13, yo = cy + e.brow_dy + tl * 6 + 3, arch = -4 - (tl >= 0 ? 3 : -2);
  return { key: 'brow' + (side < 0 ? 'L' : 'R'), pts: strip([[xi, yi], [(xi + xo) / 2, (yi + yo) / 2 + arch], [xo, yo]], [w, w * .9, w * .35]), color: sp.brow, kind: 'card', layer: sp.brow_layer ?? 3 };
}
function mouth(x, y, sp, e) {
  const w = sp.mouth_w, kind = e.mouth, lip = sp.lip, inside = sp.inside, x0 = x - w, x1 = x + w, S = t => Math.sin(Math.PI * t);
  const L = (up, lo) => lens(x0, x1, y, up, lo), one = pts => [{ key: 'mouth', pts, color: lip, kind: 'card', layer: 2 }];
  if (kind === 'smile') return one(L(t => w * .30 * S(t), t => w * .56 * S(t)));
  if (kind === 'flat') return one(L(t => -w * .03 * S(t), t => w * .17 * S(t)));
  if (kind === 'frown') return one(L(t => -w * .34 * S(t), t => -w * .10 * S(t)));
  if (kind === 'smirk') { const up = t => -w * .42 * t ** 2.2 + w * .10 * S(t); return one(L(up, t => up(t) + w * .22 * S(t))); }
  if (kind === 'o') return [{ key: 'mouth', pts: ell(x, y + w * .25, w * .50, w * .66, 0, 10), color: inside, kind: 'card', layer: 2 }, { key: 'tongue', pts: ell(x, y + w * .62, w * .30, w * .22, 0, 8), color: '#d9606a', kind: 'flat', layer: 3 }];
  if (kind === 'talk') {                                   // speaking: the mouth open by e.say (0..1); teeth show when wide
    const a = e.say ?? .5, up = t => -w * .05 * S(t), lo = t => w * (.14 + .62 * a) * S(t) ** .8, k = .78;
    const m = [{ key: 'mouth', pts: lens(x - w * k, x + w * k, y, up, lo), color: a < .12 ? lip : inside, kind: 'card', layer: 2 }];
    if (a > .45) m.push({ key: 'teeth', pts: lens(x - w * k, x + w * k, y, up, t => up(t) + (lo(t) - up(t)) * .3), color: '#fbf6ea', kind: 'flat', layer: 3 });
    return m;
  }
  if (kind === 'grit') {
    const up = t => -w * .30 * S(t), lo = t => -w * .30 * S(t) + w * .50 * S(t) ** .7;
    return [{ key: 'mouth', pts: L(up, lo), color: inside, kind: 'card', layer: 2 }, { key: 'teeth', pts: L(t => up(t) + (lo(t) - up(t)) * .18, t => up(t) + (lo(t) - up(t)) * .82), color: '#fbf6ea', kind: 'flat', layer: 3 }];
  }
  const deep = w * (kind === 'grin' ? .78 : 1.15), up = t => w * .10 * S(t), lo = t => w * .10 * S(t) + deep * S(t) ** .8;
  return [{ key: 'mouth', pts: L(up, lo), color: inside, kind: 'card', layer: 2 },
    { key: 'teeth', pts: L(up, t => up(t) + (lo(t) - up(t)) * .36), color: '#fbf6ea', kind: 'flat', layer: 3 },
    { key: 'tongue', pts: L(t => lo(t) - (lo(t) - up(t)) * (.42 * S(t) ** 2), lo), color: '#d9606a', kind: 'flat', layer: 4 }];
}
export function noseOutline(sp) {
  const s = sp.nose_s, y = sp.nose_y, x = 0;
  if (sp.nose === 'button') return ell(x, y, 9.5 * s, 8 * s, 0, 8);
  if (sp.nose === 'broad') return [[x - 6 * s, y - 26 * s], [x + 4 * s, y - 22 * s], [x + 17 * s, y + 2 * s], [x + 12 * s, y + 11 * s], [x, y + 13 * s], [x - 14 * s, y + 10 * s], [x - 17 * s, y + 1 * s]];
  if (sp.nose === 'long') return [[x - 4 * s, y - 40 * s], [x + 5 * s, y - 36 * s], [x + 11 * s, y - 2 * s], [x + 9 * s, y + 9 * s], [x, y + 12 * s], [x - 10 * s, y + 8 * s], [x - 10 * s, y - 2 * s]];
  return [[x - 2 * s, y - 22 * s], [x + 4 * s, y - 18 * s], [x + 9 * s, y + 3 * s], [x + 1 * s, y + 9 * s], [x - 8 * s, y + 4 * s]];
}

// the pieces of the face for an expression e (numbers + mouth), in head units
export function facePieces(sp, e) {
  const out = [], ey = sp.eye_y, g = sp.eye_gap, cr = sp.cheek_r;
  for (const side of [-1, 1]) {
    const x = side * g;
    out.push({ key: 'cheek' + side, pts: ell(x + side * g * .42, ey + sp.ry * .36 - (e.low > .3 ? 4 : 0), cr, cr, 0, 10), color: mix(sp.skin, sp.cheek, sp.cheek_op * .7), kind: 'flat', layer: 1 });
    out.push(...eye(x, ey, sp.eye_w, sp.eye_h, sp, e, side));
    out.push(brow(x + side * 2, ey + sp.brow_y, sp, e, side));
  }
  out.push(...mouth(0, sp.mouth_y, sp, e));
  return out;
}

// ---------------------------------------------------------------- pieces → paper on the head
export const LAYER = .0006;                               // metres between glued layers
// hu: metres in one head unit. A piece's outline laid on the head's front, `layer` layers above the skin.
export function onHead(H, hu, pts, layer, o = {}) {
  const g = o.grow ?? 1, a = o.add ?? 0;
  return patch(pts, (x, y) => [x * hu, -y * hu, (H.z(x, y, g, a)) * hu + layer * LAYER], { maxEdge: o.maxEdge ?? 6, holes: o.holes || [], dense: o.dense, seg: o.seg ?? 4 });
}
// the nose: its front outline on the face, folded along the middle and standing off by `out` units at the tip
export function noseGeo(H, hu, sp) {
  const poly = curve(noseOutline(sp), 5), s = sp.nose_s, out = (sp.nose === 'button' ? 11 : sp.nose === 'broad' ? 17 : 19) * s;
  const ys = poly.map(p => p[1]), y0 = Math.min(...ys), y1 = Math.max(...ys), xc = poly.reduce((a, p) => a + p[0], 0) / poly.length;
  const prof = sp.nose === 'button' ? through([[0, .15], [.5, 1], [1, .25]]) : through([[0, 0], [.55, .62], [.8, 1], [.92, .9], [1, .3]]);
  const o = mesh0(), n = poly.length;
  for (const [x, y] of poly) {
    o.pos.push(x * hu, -y * hu, H.z(x, y) * hu); o.uv.push(x, y);
    const t = (y - y0) / (y1 - y0), xr = xc + (x - xc) * .12;
    o.pos.push(xr * hu, -y * hu, (H.z(xr, y) + out * prof(t)) * hu); o.uv.push(xr, y);
  }
  for (let i = 0; i < n; i++) { const a = i * 2, b = (i + 1) % n * 2; o.idx.push(a, b, a + 1, b, b + 1, a + 1); }
  // the ridge is a thin strip between the two sides: close it
  for (let i = 1; i + 1 < n; i++) o.idx.push(1, i * 2 + 1, (i + 1) * 2 + 1);
  return o;
}
// an ear: a flat piece standing out of the head's side
export function earGeo(H, hu, sp, side, r0 = 15) {
  const r = r0 * sp.ear, y0 = sp.eye_y + 12, A = 50 * Math.PI / 180, x0 = side * (H.hw(y0) - 3), z0 = (H.zf(y0) + H.zb(y0)) / 2 - 2;
  const place = (x, y, t) => [(x0 + side * x * Math.cos(A)) * hu + side * t * Math.sin(A), -(y0 + y) * hu, (z0 - x * Math.sin(A)) * hu + t * Math.cos(A)];
  return [slab(ell(r * .55, 0, r * .8, r * 1.25, -8, 10), place, { thick: .0012 }),
    slab(ell(r * .65, r * .1, r * .36, r * .7, -8, 8), (x, y, t) => place(x, y, t * 1.9), { thick: .0012 })];
}
