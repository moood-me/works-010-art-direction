// Марат's face — the drawing's own features (styles/s19-lowpoly/tools/face.py: _eye2d, brow, mouth, cheeks), drawn
// flat each frame from a few numbers into a canvas that the head's front facets take straight from the front —
// exactly how the drawing presses them onto the facets (poly.press along z). Head space: cm, x to his left, y up,
// the origin between the ears at eye level.
//
// The drawing has kinds (an eye that is open / wide / low / narrow / a laughing crescent; a mouth that is a line or
// open); here every kind is a set of numbers and points of the same count, so any two mix and one moves into another.
// At a pure expression the shapes are the drawing's, point for point.

const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255);
const mix = (a, b, t) => a.map((v, i) => v * (1 - t) + b[i] * t);
const css = (c, a = 1) => `rgba(${c.map(v => Math.round(Math.min(1, Math.max(0, v)) * 255)).join(',')},${a})`;
const lerp = (a, b, t) => a + (b - a) * t;

// the canvas: x −8…8 cm, y −13…7 cm
export const BOX = { x0: -8, x1: 8, y0: -13, y1: 7, px: 64 };
export const SIZE = [(BOX.x1 - BOX.x0) * BOX.px, (BOX.y1 - BOX.y0) * BOX.px];

export const EXPR_RU = { rest: 'хохочет', calm: 'улыбается', joy: 'радость', surprise: 'удивление', sad: 'грусть', anger: 'злость' };
const EYES = {   // kind → top, bot, lid_drop, smile (the crescent), speck
  open: [1, 0.75, 0, 0, 1], wide: [1.35, 1, 0, 0, 1], low: [0.85, 0.75, 0.35, 0, 1], narrow: [0.62, 0.65, -0.15, 0, 0],
  half: [0.62, 0.7, 0, 0, 1], smile: [1, 0.75, 0, 1, 1],
};
// speech: mouth shapes over the expression (kind, smile, open)
export const VISEME = {
  A: ['open', 0.2, 0.8], O: ['o', 0, 0.95], U: ['o', 0, 0.55], E: ['open', 0.45, 0.5], I: ['open', 0.7, 0.3],
  M: ['tight', 0.1, 0], F: ['open', 0.3, 0.14], C: ['open', 0.3, 0.24],
};

export function makeFace(data) {
  const s = data.spec, w = s.lip_w, my = s.mouth_y;
  const lipC = hex(s.lip), ink = hex(s.eye), skin = hex(s.skin), black = [0, 0, 0];
  const COL = {
    white: mix(hex('#f3ece6'), skin, 0.18), eye: ink, pupil: mix(ink, black, 0.6), lid: mix(ink, black, 0.3),
    speck: hex('#fbf7f2'), crease: mix(skin, ink, 0.32), brow: hex(s.brow), crow: mix(skin, ink, 0.35),
    line: mix(lipC, hex('#2a1820'), 0.55), open: hex('#3a1a22'), teeth: hex('#f4eee4'), tongue: hex('#c45a5e'), lip: lipC,
    cheek: s.cheek_col ? hex(s.cheek_col) : null,
  };

  // ---- the mouth: an upper chain of 4 points (left → right), a lower chain of 5 (right → left), teeth, tongue, lip
  function mouthShape(kind, sm, op) {
    let upper, lower, ww, bot, col, a = 0;
    if (kind === 'o') {
      ww = w * 0.55; const top = 0.45; bot = -0.9 * op; col = COL.open;
      upper = [[-ww, my - 0.1], [-ww * 0.6, my + top], [ww * 0.6, my + top], [ww, my - 0.1]];
      lower = [[ww, my - 0.1], [ww * 0.6, my + bot], [0, my + bot], [-ww * 0.6, my + bot], [-ww, my - 0.1]];
    } else if (kind === 'laugh' || kind === 'shout' || kind === 'open') {
      ww = w * (kind === 'laugh' ? 1.3 : 1.05); const up = sm * 0.5, top = 0.25; bot = -1.5 * op; col = COL.open; a = 1;
      upper = [[-ww, my + up], [-ww * 0.45, my + top], [ww * 0.45, my + top], [ww, my + up]];
      lower = [[ww, my + up], [ww * 0.55, my + bot * 0.85], [0, my + bot], [-ww * 0.55, my + bot * 0.85], [-ww, my + up]];
    } else {   // line, smile, down, tight
      const th = s.mouth_line * (kind === 'tight' ? 0.7 : 1), cw = w * (kind === 'smile' ? 1.15 : kind === 'tight' ? 0.85 : 1), c = sm * 0.55;
      ww = cw; bot = -th; col = COL.line; op = 0;
      upper = [[-cw, my + c], [-0.35 * cw, my + 0.05 + c * 0.25], [0.35 * cw, my + 0.05 + c * 0.25], [cw, my + c]];
      lower = [[cw, my + c - th], [0.35 * cw, my - th + c * 0.15], [0, my - th + c * 0.15], [-0.35 * cw, my - th + c * 0.15], [-cw, my + c - th]];
    }
    const teeth = [[-ww * 0.8, my + 0.12 + sm * 0.25], [ww * 0.8, my + 0.12 + sm * 0.25], [ww * 0.62, my - 0.38], [-ww * 0.62, my - 0.38]];
    const tongue = [[-ww * 0.45, my + bot * 0.8], [0, my + bot * 0.55], [ww * 0.45, my + bot * 0.8], [ww * 0.25, my + bot * 0.97], [-ww * 0.25, my + bot * 0.97]];
    const lip = [[-ww * 0.6, my + bot - 0.05], [ww * 0.6, my + bot - 0.05], [ww * 0.35, my + bot - 0.6], [-ww * 0.35, my + bot - 0.6]];
    return [op, ...upper.flat(), ...lower.flat(), ...teeth.flat(), ...tongue.flat(), ...lip.flat(), a, a, a * 0.8, ...col];
  }
  const N_FACE = 11;      // browUp, browTilt, eye top, bot, lid drop, smile, crow's feet, speck, look x, y, cheek up
  // an expression of the drawing (marat.py EXPR's words) → numbers
  function exprVec(e) {
    const eye = EYES[e.eye || 'open'], look = e.look || [0, 0];
    const kind = e.mouth || 'line', sm = e.smile ?? s.smile ?? 0, op = e.open ?? 1;
    return [e.brow_up || 0, e.brow_tilt || 0, eye[0], eye[1], eye[2], eye[3], e.crow || 0, eye[4], look[0], look[1], e.cheek_up || 0,
      ...mouthShape(kind, sm, op)];
  }
  const EXPR = { ...data.expr, calm: { eye: 'open', mouth: 'smile', smile: 0.9, brow_up: 0.25, cheek_up: 0.3 } };
  const VEC = Object.fromEntries(Object.entries(EXPR).map(([k, e]) => [k, exprVec(e)]));
  const mixExpr = W => {
    let tot = 0; for (const k in W) tot += W[k];
    if (tot < 1e-6) return VEC.rest.slice();
    const out = VEC.rest.map(() => 0);
    for (const k in W) { const v = VEC[k], a = W[k] / tot; for (let i = 0; i < out.length; i++) out[i] += a * v[i]; }
    return out;
  };
  const visemeVec = name => { const [k, sm, op] = VISEME[name]; return mouthShape(k, sm, op); };

  // ---- drawing
  const cv = document.createElement('canvas'); cv.width = SIZE[0]; cv.height = SIZE[1];
  const ctx = cv.getContext('2d');
  const X = x => (x - BOX.x0) * BOX.px, Y = y => (BOX.y1 - y) * BOX.px;
  const poly = (pts, col, a = 1) => {
    if (a <= 0.003) return;
    ctx.beginPath(); pts.forEach((p, i) => (i ? ctx.lineTo(X(p[0]), Y(p[1])) : ctx.moveTo(X(p[0]), Y(p[1])))); ctx.closePath();
    ctx.fillStyle = css(col, a); ctx.fill();
  };
  const pairs = (v, o, n) => Array.from({ length: n }, (_, i) => [v[o + 2 * i], v[o + 2 * i + 1]]);
  const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];

  function eye(v, side, blink, look) {
    const ew = s.eye_w, h = s.eye_h, [top, bot, ld, smile] = [v[2], v[3], v[4], v[5]], hh = h * top;
    const cx = side * s.eye_x, cy = s.eye_y, t = s.eye_tilt || 0;
    const at = ([a, b]) => [cx + side * a, cy + b + t * a];
    // the open almond and the laughing crescent, five points up and five down each
    const uA = [[-ew, 0], [-0.55 * ew, 0.78 * hh + 0.1 * ld], [0.15 * ew, hh - 0.2 * ld * h], [0.75 * ew, 0.62 * hh - ld * h * 0.9], [1.05 * ew, 0.12 * h - ld * h * 0.5]];
    const lA = [uA[4], [0.6 * ew, -0.42 * h * bot], [-0.15 * ew, -0.55 * h * bot], [-0.7 * ew, -0.4 * h * bot], uA[0]];
    const c1 = [-0.35 * ew, 0.5 * h + 0.15], c2 = [0.45 * ew, 0.55 * h + 0.15], d1 = [0.45 * ew, 0.3 * h], d2 = [-0.4 * ew, 0.22 * h];
    const uC = [[-ew, -0.05], c1, mid(c1, c2), c2, [1.08 * ew, 0.05]], lC = [[1.08 * ew, 0.05], d1, mid(d1, d2), d2, [-ew, -0.05]];
    let up = uA.map((p, i) => [lerp(p[0], uC[i][0], smile), lerp(p[1], uC[i][1], smile)]);
    const lo = lA.map((p, i) => [lerp(p[0], lC[i][0], smile), lerp(p[1], lC[i][1], smile)]);
    if (blink > 0) up = up.map((p, i) => [p[0], lerp(p[1], lo[4 - i][1] + 0.02, blink)]);   // the upper lid comes down
    const almond = [...up, ...lo.slice(1, 4)];
    const open = 1 - smile;
    poly(almond.map(at), mix(COL.white, COL.lid, smile));
    if (open > 0.01) {
      ctx.save(); ctx.beginPath(); almond.map(at).forEach((p, i) => (i ? ctx.lineTo(X(p[0]), Y(p[1])) : ctx.moveTo(X(p[0]), Y(p[1])))); ctx.closePath(); ctx.clip();
      const r = h * (s.iris || 0.95), ix = side * look[0] * ew * 0.45, iy = 0.05 * h + look[1] * h * 0.3;   // look x: to his left
      const ring = (rad, n, ph) => Array.from({ length: n }, (_, k) => { const a = Math.PI * (2 * k / n + ph); return [ix + rad * Math.cos(a), iy + rad * Math.sin(a)]; });
      poly(ring(r, 8, 1 / 8).map(at), COL.eye, open);
      poly(ring(r * 0.42, 6, 0).map(at), COL.pupil, open);
      ctx.restore();
      var speck = [ix - r * 0.35, iy + r * 0.35];
    }
    const th = (s.lid_th ?? 0.22) * open;
    poly([...up, ...up.slice().reverse().map(([x, y]) => [x, y - th * (0.6 + 0.8 * Math.max(0, x / ew))])].map(at), COL.lid);
    if (open > 0.01) {
      const sp = 0.16 * h / 0.7, [sx, sy] = speck;
      poly([[sx - sp, sy], [sx, sy + sp], [sx + sp, sy], [sx, sy - sp]].map(at), COL.speck, open * v[7] * (1 - blink));
      const cr = [[-0.85 * ew, 0.95 * hh + 0.25], [0.1 * ew, hh + 0.42 - 0.2 * ld], [0.95 * ew, 0.62 * hh + 0.32 - 0.6 * ld * h]];
      poly([...cr, ...cr.slice().reverse().map(([x, y]) => [x + 0.05, y - 0.13])].map(at), COL.crease, open);
    }
    if (v[6] * smile > 0.01) poly([[1.25 * ew, -0.1], [1.9 * ew, 0.1], [1.9 * ew, -0.05], [1.25 * ew, -0.3]].map(([a, b]) => [cx + side * a, cy + b]), COL.crow, v[6] * smile);
  }
  function brow(v, side) {
    const up = v[0], tilt = v[1], L = s.brow_len, th = s.brow_th, arch = s.brow_arch || 0;
    const x0 = side * s.brow_in, y0 = s.eye_y + s.eye_h + s.brow_lift + 0.55 + up;
    const yin = y0 - tilt * 0.45, yout = y0 + 0.25 + tilt * 0.25 - arch * 0.3, ymid = (yin + yout) / 2 + 0.25 + arch * 0.35;
    const xm = side * (s.brow_in + L * 0.55), xo = side * (s.brow_in + L);
    poly([[x0, yin + th * 0.6], [xm, ymid + th * 0.55], [xo, yout + th * 0.1], [xo, yout - th * 0.25], [xm, ymid - th * 0.5], [x0, yin - th * 0.5]], COL.brow);
  }
  function mouth(m) {
    const up = pairs(m, 1, 4), lo = pairs(m, 9, 5), teeth = pairs(m, 19, 4), tongue = pairs(m, 27, 5), lip = pairs(m, 37, 4);
    poly([...up, ...lo], [m[48], m[49], m[50]]);
    poly(teeth, COL.teeth, m[45]); poly(tongue, COL.tongue, m[46]); poly(lip, COL.lip, m[47]);
  }
  // v: the face's numbers; opts: blink 0…1, look [x, y] (−1…1, x to his left)
  function draw(v, { blink = 0, look = null } = {}) {
    ctx.clearRect(0, 0, cv.width, cv.height);
    const lk = look || [v[8], v[9]];
    for (const side of [1, -1]) { eye(v, side, blink, lk); brow(v, side); }
    mouth(v.slice(N_FACE));
    if (COL.cheek) for (const side of [1, -1]) {
      const cx = side * (s.cheek_w - 0.6), cy = s.cheek_y - 1.6 + v[10];
      poly([[-1.2, 0.3], [0, 0.9], [1.3, 0.2], [0.2, -0.8]].map(([a, b]) => [cx + side * a, cy + b]), COL.cheek, 0.35);
    }
  }
  return { canvas: cv, draw, exprVec, mixExpr, visemeVec, VEC, EXPR, N_FACE, MOUTH0: N_FACE, names: Object.keys(EXPR_RU) };
}
