// A face of the style С5 as the drawing draws it (styles/s5-indie/tools/face.py + the character's function, head-on),
// on a canvas, from continuous numbers, so that it can move: lids, blink, gaze, brows (each its own), mouth shapes,
// a tear, mixed between expressions. Grown from Вера's face (to3d/r4-s5-vera/tools/web/face.js): the same drawing
// code, but the character's own numbers come in as `cfg`, and the mouth is any closed shape of two cubic curves
// (so a crooked smirk and a grin with teeth are the same kind of thing as a straight line).
// makeFace(cfg) → {drawFace(ctx, F, px, sw), EXPR, VISEME, exprVec, vecExpr, mixExpr, NH, rect}
import { ringTable0 } from './rings0.js';

export const LINE = '#4a3036', SW = 2.4;
export const EXPR_RU = { neutral: 'спокойно', joy: 'радость', surprise: 'удивление', sad: 'грусть', anger: 'злость' };

// ———————————— mouths as numbers ————————————
// a mouth: the upper curve U (left end → right end, a cubic: 4 points) and the lower curve L (right → left), closed;
// then: fill (an open mouth's dark inside), teeth (all white with a middle line: clenched), band (upper teeth as a
// band) with its lower edge's height at the left and right, gap (a missing tooth), tongue with its place and size,
// dimple (a small line by the right corner)
const NM = 27;
const q3 = (p0, c, p1) => [p0, [p0[0] + 2 / 3 * (c[0] - p0[0]), p0[1] + 2 / 3 * (c[1] - p0[1])], [p1[0] + 2 / 3 * (c[0] - p1[0]), p1[1] + 2 / 3 * (c[1] - p1[1])], p1];
const flat = pts => pts.flat();
const rev = pts => pts.slice().reverse();
export function mouthOf({ U, L, fill = 0, teeth = 0, band = 0, bandL = 0, bandR = 0, gap = 0, tongue = 0, ty = 0, trx = 1, try_ = 1, dimple = 0 }) {
  return [...flat(U), ...flat(L || rev(U)), fill, teeth, band, bandL, bandR, gap, tongue, ty, trx, try_, dimple];
}
// a line mouth: the drawing's quadratic curve, turned into a cubic one exactly
export const lineMouth = (p0, c, p1, more = {}) => mouthOf({ U: q3(p0, c, p1), ...more });
// a symmetric mouth as Вера's face had it: half-width w, corners at cy, the two curves' control heights uc and lc at
// ±au·w and ±al·w, the lower curve's ends at ±kx·w and `side` lower
export function symMouth({ w, cy, uc, lc, au, al, side = 0, kx = 1, fill = 0, teeth = 0, tongue = 0 }) {
  return mouthOf({
    U: [[-w, cy], [-au * w, uc], [au * w, uc], [w, cy]], L: [[kx * w, cy + side], [al * kx * w, lc], [-al * kx * w, lc], [-kx * w, cy + side]],
    fill, teeth: teeth > 0.9 ? 1 : 0, band: teeth > 0.05 && teeth <= 0.9 ? Math.min(1, teeth * 1.5) : 0,
    bandL: Math.min(uc, cy) + (lc - uc) * 0.22 + 0.2, bandR: Math.min(uc, cy) + (lc - uc) * 0.22 + 0.2,
    tongue, ty: (cy + lc) / 2 + (lc - cy) * 0.25, trx: w * 0.62, try_: Math.max(1, (lc - cy) * 0.3),
  });
}
const q2c = (cy, q) => cy + 2 / 3 * (q - cy);
// the drawing's mouths (face.py `mouth`), for a mouth of half-width w
export function mouths(w, smile = 4) {
  const W = 1.1 * w, G = 1.35 * w, k = 1.36;
  return {
    soft: lineMouth([-w, -smile * 0.3], [0, smile], [w, -smile * 0.3]),
    strict: lineMouth([-w, 1.5], [0, -1], [w, 1.5]),
    smirk: lineMouth([-w, 0], [0.1 * w, 4], [1.1 * w, -5]),
    frown: lineMouth([-0.8 * w, 3], [0, -4], [0.8 * w, 3]),
    tight: lineMouth([-w, 0.5], [0, -1.5], [w, 2.5]),
    half: lineMouth([-w, 1.5], [0.2 * w, 2.5], [1.15 * w, -3.5], { dimple: 1 }),
    o: symMouth({ w: 0.45 * w, cy: 3, uc: 3 - 4 / 3 * 0.6 * w, lc: 3 + 4 / 3 * 0.6 * w, au: 1, al: 1, fill: 1 }),
    clench: mouthOf({ U: q3([-W, 2], [0, -4], [W, 2]), L: q3([0.9 * W, 8], [0, 5], [-0.9 * W, 8]), fill: 1, teeth: 1 }),
    // a grin: the upper teeth as a band, a gap in them, a tongue; the lower edge (two curves in the drawing) as one
    grin: mouthOf({
      U: q3([-G, -4], [0, 2], [G, -7]),
      L: [[G, -7], [G - 0.4 * k * G, -7 + k * (0.95 * G + 7)], [-G + 0.2 * k * G, -4 + k * (0.7 * G + 4)], [-G, -4]],
      fill: 1, band: 1, bandL: 4, bandR: 1, gap: 1, tongue: 1, ty: 0.9 * G, trx: 0.6 * G, try_: 0.4 * G,
    }),
  };
}
// mouth shapes of speech, as Вера's, in the size of this mouth
export function visemes(w) {
  const k = w / 8;
  const V = {
    A: { w: 7.5, cy: -1.5, uc: q2c(-1.5, 0.5), lc: (4 * 8.5 + 1.5) / 3, au: 1 / 3, al: 0.85, fill: 1, teeth: 0, tongue: 1 },
    O: { w: 4.2, cy: 3, uc: 3 - 4 / 3 * 4.6, lc: 3 + 4 / 3 * 4.6, au: 1, al: 1, fill: 1, teeth: 0, tongue: 0.4 },
    U: { w: 3, cy: 3, uc: 3 - 4 / 3 * 2.8, lc: 3 + 4 / 3 * 2.8, au: 1, al: 1, fill: 1, teeth: 0, tongue: 0 },
    E: { w: 8, cy: 1, uc: 0, lc: 6, au: 0.5, al: 0.7, fill: 1, teeth: 0.3, tongue: 0.5 },
    I: { w: 8.5, cy: 0.5, uc: -0.2, lc: 4, au: 0.5, al: 0.6, fill: 1, teeth: 0.6, tongue: 0 },
    M: { w: 7.5, cy: 1.5, uc: 1.2, lc: 1.2, au: 1 / 3, al: 1 / 3, fill: 0, teeth: 0, tongue: 0 },
    F: { w: 7, cy: 1, uc: 0.2, lc: 3.2, au: 0.4, al: 0.5, fill: 1, teeth: 0.9, tongue: 0 },
    C: { w: 7, cy: 1.5, uc: 0.6, lc: 4.2, au: 0.45, al: 0.6, fill: 1, teeth: 0.4, tongue: 0.3 },
  };
  return Object.fromEntries(Object.entries(V).map(([n, m]) => [n, symMouth({ ...m, w: m.w * k, uc: m.cy + (m.uc - m.cy) * k, lc: m.cy + (m.lc - m.cy) * k })]));
}

// ———————————— drawing ————————————
const smoothstep = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const lerp = (a, b, t) => a + (b - a) * t;
function stroke(ctx, w, col = LINE, alpha = 1) { ctx.globalAlpha = alpha; ctx.lineWidth = w; ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke(); ctx.globalAlpha = 1; }
function ellipse(ctx, x, y, rx, ry) { ctx.beginPath(); ctx.ellipse(x, y, Math.max(rx, 1e-3), Math.max(ry, 1e-3), 0, 0, Math.PI * 2); }
function splitQ(p0, c, p1) { const a = [(p0[0] + c[0]) / 2, (p0[1] + c[1]) / 2], b = [(c[0] + p1[0]) / 2, (c[1] + p1[1]) / 2], m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]; return [p0, a, m, b, p1]; }

export function makeFace(cfg) {
  const [FX0, FY0, FW, FH] = cfg.rect;
  const ring = ringTable0(cfg.head);
  // geo.surf at yaw 0: [x, y, how much the place faces the eye]
  function surf(phi, y, out = 0) {
    const [w, d, cx] = ring(y);
    const x = cx + (w + out) * Math.sin(phi);
    const nx = Math.sin(phi) / Math.max(w, 1e-3), nz = Math.cos(phi) / Math.max(d, 1e-3);
    return [x, y, nz / Math.hypot(nx, nz)];
  }
  const SPOT = {
    eye: [-1, 1].map(s => surf(s * cfg.eye.phi, cfg.eye.y)), brow: [-1, 1].map(s => surf(s * cfg.eye.phi * 1.05, cfg.brow.y)),
    cheek: [-1, 1].map(s => surf(s * cfg.cheek.phi, cfg.cheek.y)), nose: surf(cfg.nose.phi || 0, cfg.nose.y, cfg.nose.out || 0), mouth: surf(cfg.mouth.phi, cfg.mouth.y),
  };
  const EXPR = cfg.expr, VISEME = visemes(cfg.mouth.w);
  // numbers ⇄ a flat list, for mixing and for the springs. NH: how many come before the mouth
  const NH = 12;
  const exprVec = e => [e.lid[0], e.lid[1], e.happy, e.big, e.iris, e.look[0], e.look[1], e.brow[0], e.brow[1], e.brow[2] ?? e.brow[0], e.brow[3] ?? e.brow[1], e.tear, ...e.mouth];
  const vecExpr = v => ({ lid: [v[0], v[1]], happy: v[2], big: v[3], iris: v[4], look: [v[5], v[6]], brow: [v[7], v[8], v[9], v[10]], tear: v[11], mouth: v.slice(NH) });
  function mixExpr(wts) {
    let s = 0; const out = exprVec(EXPR.neutral).map(() => 0);
    for (const [k, w] of Object.entries(wts)) { if (!w || !EXPR[k]) continue; s += w; exprVec(EXPR[k]).forEach((x, i) => out[i] += x * w); }
    return s ? out.map(x => x / s) : exprVec(EXPR.neutral);
  }

  function eye(ctx, x0, y0, fc, side, E, gaze, blink, sw) {
    if (fc < 0.12) return;
    const sq = Math.max(fc, 0.25) ** 0.85, rx = cfg.eye.rx * sq * E.big, ry = cfg.eye.ry * E.big, inner = -side;
    const h = E.happy;
    if (h > 0.01) {   // the happy arc (joy): the eye shut into an upward curve
      ctx.beginPath(); ctx.moveTo(x0 - rx, y0 + ry * 0.25); ctx.quadraticCurveTo(x0, y0 - ry * 1.05, x0 + rx, y0 + ry * 0.25);
      stroke(ctx, sw * 1.35, LINE, smoothstep(0.35, 0.9, h));
    }
    const s = Math.max(blink, smoothstep(0, 0.6, h));
    if (s > 0.995) return;
    const li = E.lid[0], lo = E.lid[1], top = y0 - ry;
    const xi = x0 + inner * rx * 1.25, xo = x0 - inner * rx * 1.25;
    const shut = y0 + ry * 0.45;
    const yi = lerp(top + li * 2 * ry, shut, s), yo = lerp(top + lo * 2 * ry, shut, s);
    const bottom = lerp(y0 + ry * 1.1, shut + 0.3, s);
    const x = x0 + gaze[0] * sq, y = y0 + gaze[1] * 0.6;
    const alpha = 1 - smoothstep(0.6, 1, h);
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.beginPath(); ctx.moveTo(xi, yi); ctx.lineTo(xo, yo); ctx.lineTo(xo, bottom); ctx.lineTo(xi, bottom); ctx.closePath(); ctx.clip();
    ellipse(ctx, x, y, rx, ry); ctx.fillStyle = cfg.irisCol; ctx.fill();
    const ir = Math.min(rx, ry) * E.iris, hr = Math.max(rx, ry) * 0.2;
    const ix = x0 + E.look[0] * sq + gaze[0] * sq * 0.55 + (1 - sq) * rx * 0.6, iy = y0 + E.look[1] + gaze[1] * 0.35 + ry * 0.12;
    ctx.fillStyle = '#fff'; ellipse(ctx, ix - ir * 0.35, iy - ir * 0.38, hr, hr); ctx.fill();
    ctx.globalAlpha = 0.85 * alpha; ellipse(ctx, ix + ir * 0.3, iy + ir * 0.32, hr * 0.45, hr * 0.45); ctx.fill(); ctx.globalAlpha = alpha;
    ellipse(ctx, x, y, rx, ry); stroke(ctx, sw * 0.9, LINE, alpha);
    ctx.restore();
    // the lid line: arched over an open eye, straight and heavy over a lidded one, curved down when shut
    const lidAmt = smoothstep(0, 0.12, Math.max(li, lo) + s);
    const yL = inner < 0 ? yi : yo, yR = inner < 0 ? yo : yi;
    const st = splitQ([x0 - rx * 1.1, yL], [(xi + xo) / 2, (yi + yo) / 2 - ry * lerp(0.08, -0.25, s)], [x0 + rx * 1.1, yR]);
    const op = [[x0 - rx * 1.08, y0 - ry * 0.15], [x0 - rx * 0.7, y0 - ry * 1.08], [x0, y0 - ry * 1.04], [x0 + rx * 0.75, y0 - ry * 1.04], [x0 + rx * 1.08, y0 - ry * 0.2]];
    const Q = op.map((p, i) => [lerp(p[0], st[i][0], lidAmt), lerp(p[1], st[i][1], lidAmt)]);
    ctx.beginPath(); ctx.moveTo(...Q[0]); ctx.quadraticCurveTo(...Q[1], ...Q[2]); ctx.quadraticCurveTo(...Q[3], ...Q[4]);
    stroke(ctx, sw * cfg.lash, LINE, alpha);
    if (cfg.flick) {   // the outer flick (lashes)
      const ox = x0 - inner * rx * 1.05, oy = yo + lerp(-ry * 0.1, ry * 0.1, lidAmt);
      ctx.beginPath(); ctx.moveTo(ox, oy); ctx.lineTo(ox - inner * rx * 0.38, oy - ry * 0.28); stroke(ctx, sw * 1.1, LINE, alpha);
    }
  }
  function eyeExtras(ctx, x, y, fc, side, E, sw) {
    if (fc < 0.12) return;
    const sq = Math.max(fc, 0.25) ** 0.85, rx = cfg.eye.rx * sq * E.big, ry = cfg.eye.ry * E.big;
    if (cfg.bags) { ctx.beginPath(); ctx.moveTo(x - rx * 0.7, y + ry * 1.25); ctx.quadraticCurveTo(x, y + ry * 1.55, x + rx * 0.7, y + ry * 1.25); stroke(ctx, sw * 0.6, LINE, 0.55 * (1 - smoothstep(0.3, 0.9, E.happy))); }
    if (E.tear > 0.02 && side === -1) {
      const tx = x + rx * 0.3, ty = y + ry * 1.3 + (1 - E.tear) * -3;
      ctx.globalAlpha = E.tear; ctx.beginPath(); ctx.moveTo(tx, ty); ctx.quadraticCurveTo(tx - 5, ty + 9, tx, ty + 12); ctx.quadraticCurveTo(tx + 5, ty + 9, tx, ty); ctx.closePath();
      ctx.fillStyle = '#9fd3ea'; ctx.fill(); stroke(ctx, sw * 0.6, LINE, E.tear); ctx.globalAlpha = 1;
    }
  }
  function brow(ctx, x, y, fc, side, B, sw) {
    if (fc < 0.12) return;
    const sq = Math.max(fc, 0.25) ** 0.85, inner = -side, w = cfg.brow.w * sq, [dy, tilt] = B;
    const yi = y + dy + tilt * 0.5, yo = y + dy - tilt * 0.5, xi = x + inner * w * 0.5, xo = x - inner * w * 0.5;
    ctx.beginPath(); ctx.moveTo(xi, yi); ctx.quadraticCurveTo((xi + xo) / 2, Math.min(yi, yo) - cfg.brow.arch, xo, yo); stroke(ctx, sw * cfg.brow.th, cfg.brow.col);
  }
  function mouthPath(ctx, x, y, m) {
    ctx.beginPath(); ctx.moveTo(x + m[0], y + m[1]);
    ctx.bezierCurveTo(x + m[2], y + m[3], x + m[4], y + m[5], x + m[6], y + m[7]);
    ctx.lineTo(x + m[8], y + m[9]);
    ctx.bezierCurveTo(x + m[10], y + m[11], x + m[12], y + m[13], x + m[14], y + m[15]);
    ctx.closePath();
  }
  function mouth(ctx, x, y, m, sw) {
    const [fill, teeth, band, bandL, bandR, gap, tongue, ty, trx, try_, dimple] = m.slice(16);
    const midU = (m[1] + 3 * m[3] + 3 * m[5] + m[7]) / 8, midL = (m[9] + 3 * m[11] + 3 * m[13] + m[15]) / 8;
    const open = Math.max(0, midL - midU) + Math.max(0, m[9] - m[7]);
    const f = smoothstep(0.5, 2.2, open) * Math.min(1, fill * 1.5 + smoothstep(1.5, 4, open));
    if (f < 0.999) {   // a line: the middle of the two lips
      const a = i => (m[i] + m[14 - i + (i % 2 ? 2 : 0)]) / 2;   // U's point i/2 with L's mirrored one
      ctx.beginPath(); ctx.moveTo(x + a(0), y + a(1)); ctx.bezierCurveTo(x + a(2), y + a(3), x + a(4), y + a(5), x + a(6), y + a(7));
      stroke(ctx, sw * cfg.mouth.lw, LINE, 1 - f);
    }
    if (f > 0.001) {
      ctx.save(); ctx.globalAlpha = f;
      mouthPath(ctx, x, y, m); ctx.save(); ctx.clip();
      const mc = [0x7b, 0x2f, 0x35], wt = [0xff, 0xfa, 0xf2];
      ctx.fillStyle = `rgb(${mc.map((c, i) => Math.round(lerp(c, wt[i], teeth > 0.5 ? 1 : 0))).join(',')})`; ctx.fill();
      const xl = x + m[0], xr = x + m[6];
      if (band > 0.03) {   // the upper teeth
        ctx.fillStyle = '#fffaf2'; ctx.globalAlpha = f * Math.min(1, band);
        ctx.beginPath(); ctx.moveTo(xl, y - 30); ctx.lineTo(xr, y - 30); ctx.lineTo(xr, y + bandR); ctx.lineTo(xl, y + bandL); ctx.closePath(); ctx.fill(); ctx.globalAlpha = f;
      }
      if (gap > 0.03) { const W = (m[6] - m[0]) / 2; ctx.globalAlpha = f * gap; ctx.fillStyle = '#7b2f35'; ctx.fillRect(x + (m[0] + m[6]) / 2 - W * 0.15, y + m[1], W * 0.22, 7); ctx.globalAlpha = f; }
      if (tongue > 0.02) { ctx.globalAlpha = f * Math.min(1, tongue); ellipse(ctx, x + (m[0] + m[6]) / 2, y + ty, trx, try_); ctx.fillStyle = '#e0767a'; ctx.fill(); ctx.globalAlpha = f; }
      ctx.restore();
      mouthPath(ctx, x, y, m); stroke(ctx, sw, LINE, f);
      if (teeth > 0.5) {   // the line between clenched teeth
        const uy = (m[1] + m[7]) / 2, ly = (m[9] + m[15]) / 2;
        ctx.beginPath(); ctx.moveTo(x + m[14], y + uy + (ly - uy) * 0.42); ctx.quadraticCurveTo(x + (m[8] + m[14]) / 2, y + uy - 1, x + m[8], y + uy + (ly - uy) * 0.42); stroke(ctx, sw * 0.6, LINE, f);
      }
      ctx.restore();
    }
    if (dimple > 0.03) { const dx = x + m[6] + 0.3 * cfg.mouth.w, dy = y + m[7] - 3; ctx.beginPath(); ctx.moveTo(dx, dy); ctx.quadraticCurveTo(dx + 2.5, dy + 2.5, dx + 0.5, dy + 5.5); stroke(ctx, sw * 0.7, LINE, Math.min(1, dimple)); }
  }
  function nose(ctx, sw) {
    const [nx, ny] = SPOT.nose;
    ctx.beginPath();
    if (cfg.nose.kind === 'fine') { ctx.moveTo(nx - 3, ny); ctx.quadraticCurveTo(nx + 1, ny + 2, nx + 3, ny - 1); }   // Вера's
    else { ctx.moveTo(nx - 2, ny); ctx.quadraticCurveTo(nx, ny + 2, nx + 2, ny); }                                    // cast.small_nose
    stroke(ctx, sw * 0.9);
  }
  // F: {e: expression (vecExpr), gaze: [x, y] the eyes' shift (units), blink: [left, right] 0..1, browAdd: units}
  function drawFace(ctx, F, px, sw = SW) {
    ctx.setTransform(px, 0, 0, px, -FX0 * px, -FY0 * px);
    ctx.clearRect(FX0, FY0, FW, FH);
    const E = F.e;
    for (const s of [0, 1]) {
      const [x, y, fc] = SPOT.cheek[s]; if (fc < 0.2) continue;
      ctx.globalAlpha = cfg.cheek.op; ellipse(ctx, x, y, cfg.cheek.r * Math.max(fc, 0.3), cfg.cheek.r * 0.62); ctx.fillStyle = cfg.cheek.col; ctx.fill(); ctx.globalAlpha = 1;
    }
    if (cfg.under) cfg.under(ctx, surf, sw);
    for (const s of [0, 1]) {
      const side = s ? 1 : -1, [x, y, fc] = SPOT.eye[s];
      eye(ctx, x, y, fc, side, E, F.gaze || [0, 0], F.blink ? F.blink[s] : 0, sw);
      eyeExtras(ctx, x, y, fc, side, E, sw);
      const [bx, by, bf] = SPOT.brow[s];
      brow(ctx, bx, by, bf, side, [E.brow[s * 2] + (F.browAdd || 0), E.brow[s * 2 + 1]], sw);
    }
    nose(ctx, sw);
    const [mx, my] = SPOT.mouth;
    mouth(ctx, mx, my, E.mouth, sw);
    if (cfg.over) cfg.over(ctx, surf, sw);
  }
  return { drawFace, EXPR, VISEME, exprVec, vecExpr, mixExpr, NH, rect: cfg.rect, surf, phrases: cfg.phrases };
}
