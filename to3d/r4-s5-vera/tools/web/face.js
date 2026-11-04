// Вера's face as the drawing draws it (styles/s5-indie/tools/face.py + cast.vera, head-on), on a canvas, from
// continuous numbers, so that it can move: lids, blink, gaze, brows, mouth shapes, a tear, mixed between expressions.
// drawFace(ctx, F, px) draws in the head's own drawing units; F comes from exprParams / FaceLive.
import { ringTable0 } from './rings0.js';

export const LINE = '#4a3036', SW = 2.4;
// the texture's square in head units (as face_tex.py)
export const FX0 = -76, FY0 = -84, FW = 152, FH = 160;

// the head's rings and geo.surf at yaw 0 (linear between rings, as lerp_rings)
const HEAD = [[-72, 0, 0, 0, -3], [-66, 30, 32, 0, -3], [-50, 52, 54, 0, -3], [-24, 59, 60, 0, -2], [4, 59, 58, 0, 2],
  [26, 55, 52, 0, 5], [44, 44, 41, 0, 9], [58, 27, 27, 0, 12], [66, 11, 13, 0, 13], [68, 0, 0, 0, 13]];
const ring = ringTable0(HEAD);
function surf(phi, y, out = 0) {
  const [w, d, cx] = ring(y);
  const x = cx + (w + out) * Math.sin(phi);
  const nx = Math.sin(phi) / Math.max(w, 1e-3), nz = Math.cos(phi) / Math.max(d, 1e-3);
  return [x, y, nz / Math.hypot(nx, nz)];
}
const SPOT = {
  eye: [-1, 1].map(s => surf(s * 0.42, 8)), brow: [-1, 1].map(s => surf(s * 0.42 * 1.05, -9)),
  cheek: [-1, 1].map(s => surf(s * 0.6, 26)), nose: surf(0.02, 30, 1), mouth: surf(0, 44),
};

// ———————————— the expressions of the sheet as numbers ————————————
// eye: lid = (inner, outer) cut from the top, happy = shut into an arc, big, iris; brow: (dy, tilt); mouth: a closed
// shape of two cubic curves (see mouthPath), the drawing's quadratic curves turned into cubic ones exactly
const q2c = (cy, q) => cy + 2 / 3 * (q - cy);          // a quadratic's control as the cubic's control height (a = 1/3)
export const MOUTH = {
  strict: { w: 8, cy: 1.5, uc: q2c(1.5, -1), lc: q2c(1.5, -1), au: 1 / 3, al: 1 / 3, side: 0, kx: 1, fill: 0, teeth: 0, tongue: 0 },
  soft: { w: 8, cy: -1.8, uc: q2c(-1.8, 6), lc: q2c(-1.8, 6), au: 1 / 3, al: 1 / 3, side: 0, kx: 1, fill: 0, teeth: 0, tongue: 0 },
  frown: { w: 6.4, cy: 3, uc: q2c(3, -4), lc: q2c(3, -4), au: 1 / 3, al: 1 / 3, side: 0, kx: 1, fill: 0, teeth: 0, tongue: 0 },
  o: { w: 3.6, cy: 3, uc: 3 - 4 / 3 * 4.8, lc: 3 + 4 / 3 * 4.8, au: 1, al: 1, side: 0, kx: 1, fill: 1, teeth: 0, tongue: 0 },
  clench: { w: 8.8, cy: 2, uc: q2c(2, -4), lc: q2c(8, 5), au: 1 / 3, al: 1 / 3, side: 6, kx: 0.9, fill: 1, teeth: 1, tongue: 0 },
};
// mouth shapes of speech (visemes), drawn in the same way
export const VISEME = {
  A: { w: 7.5, cy: -1.5, uc: q2c(-1.5, 0.5), lc: (4 * 8.5 + 1.5) / 3, au: 1 / 3, al: 0.85, side: 0, kx: 1, fill: 1, teeth: 0, tongue: 1 },
  O: { w: 4.2, cy: 3, uc: 3 - 4 / 3 * 4.6, lc: 3 + 4 / 3 * 4.6, au: 1, al: 1, side: 0, kx: 1, fill: 1, teeth: 0, tongue: 0.4 },
  U: { w: 3, cy: 3, uc: 3 - 4 / 3 * 2.8, lc: 3 + 4 / 3 * 2.8, au: 1, al: 1, side: 0, kx: 1, fill: 1, teeth: 0, tongue: 0 },
  E: { w: 8, cy: 1, uc: 0, lc: 6, au: 0.5, al: 0.7, side: 0, kx: 1, fill: 1, teeth: 0.3, tongue: 0.5 },
  I: { w: 8.5, cy: 0.5, uc: -0.2, lc: 4, au: 0.5, al: 0.6, side: 0, kx: 1, fill: 1, teeth: 0.6, tongue: 0 },
  M: { w: 7.5, cy: 1.5, uc: 1.2, lc: 1.2, au: 1 / 3, al: 1 / 3, side: 0, kx: 1, fill: 0, teeth: 0, tongue: 0 },
  F: { w: 7, cy: 1, uc: 0.2, lc: 3.2, au: 0.4, al: 0.5, side: 0, kx: 1, fill: 1, teeth: 0.9, tongue: 0 },
  C: { w: 7, cy: 1.5, uc: 0.6, lc: 4.2, au: 0.45, al: 0.6, side: 0, kx: 1, fill: 1, teeth: 0.4, tongue: 0.3 },
};
export const EXPR = {
  neutral: { lid: [0.36, 0.3], happy: 0, big: 1, iris: 0.78, look: [0, 0], brow: [2, 3], mouth: MOUTH.strict, tear: 0 },
  joy: { lid: [0, 0], happy: 1, big: 1, iris: 0.78, look: [0, 0], brow: [-4, 3], mouth: MOUTH.soft, tear: 0 },
  surprise: { lid: [0, 0], happy: 0, big: 1.15, iris: 0.72, look: [0, -1], brow: [-12, 0], mouth: MOUTH.o, tear: 0 },
  sad: { lid: [0.25, 0.5], happy: 0, big: 1, iris: 0.78, look: [0, 2], brow: [-3, -9], mouth: MOUTH.frown, tear: 1 },
  anger: { lid: [0.48, 0.1], happy: 0, big: 1, iris: 0.78, look: [0, 0], brow: [4, 9], mouth: MOUTH.clench, tear: 0 },
};
export const EXPR_RU = { neutral: 'спокойно', joy: 'радость', surprise: 'удивление', sad: 'грусть', anger: 'злость' };

// numbers ⇄ a flat list, for mixing and for the springs
const MK = ['w', 'cy', 'uc', 'lc', 'au', 'al', 'side', 'kx', 'fill', 'teeth', 'tongue'];
export const mouthVec = m => MK.map(k => m[k]);
export const vecMouth = v => Object.fromEntries(MK.map((k, i) => [k, v[i]]));
export function exprVec(e) { return [e.lid[0], e.lid[1], e.happy, e.big, e.iris, e.look[0], e.look[1], e.brow[0], e.brow[1], e.tear, ...mouthVec(e.mouth)]; }
export function vecExpr(v) { return { lid: [v[0], v[1]], happy: v[2], big: v[3], iris: v[4], look: [v[5], v[6]], brow: [v[7], v[8]], tear: v[9], mouth: vecMouth(v.slice(10)) }; }
// a mix of the sheet's expressions by weights {neutral: .5, joy: .5, …}
export function mixExpr(wts) {
  let s = 0; const out = exprVec(EXPR.neutral).map(() => 0);
  for (const [k, w] of Object.entries(wts)) { if (!w) continue; s += w; exprVec(EXPR[k]).forEach((x, i) => out[i] += x * w); }
  return s ? out.map(x => x / s) : exprVec(EXPR.neutral);
}

// ———————————— drawing ————————————
const smoothstep = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const lerp = (a, b, t) => a + (b - a) * t;
function stroke(ctx, w, col = LINE, alpha = 1) { ctx.globalAlpha = alpha; ctx.lineWidth = w; ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke(); ctx.globalAlpha = 1; }
function ellipse(ctx, x, y, rx, ry) { ctx.beginPath(); ctx.ellipse(x, y, Math.max(rx, 1e-3), Math.max(ry, 1e-3), 0, 0, Math.PI * 2); }
// a quadratic split in two at its middle: [p0, c1, m, c2, p1]
function splitQ(p0, c, p1) { const a = [(p0[0] + c[0]) / 2, (p0[1] + c[1]) / 2], b = [(c[0] + p1[0]) / 2, (c[1] + p1[1]) / 2], m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]; return [p0, a, m, b, p1]; }

// one eye: E = {lid, happy, big, iris}, look = the eye's place (units), blink 0..1
function eye(ctx, x0, y0, fc, side, E, gaze, blink, sw) {
  if (fc < 0.12) return;
  const sq = Math.max(fc, 0.25) ** 0.85, rx = 8 * sq * E.big, ry = 10.5 * E.big, inner = -side;
  const h = E.happy;
  // the happy arc (joy): the eye shut into an upward curve
  if (h > 0.01) {
    ctx.beginPath(); ctx.moveTo(x0 - rx, y0 + ry * 0.25); ctx.quadraticCurveTo(x0, y0 - ry * 1.05, x0 + rx, y0 + ry * 0.25);
    stroke(ctx, sw * 1.35, LINE, smoothstep(0.35, 0.9, h));
  }
  // the open eye shuts as the lids come down: by blink, and into the arc by joy
  const s = Math.max(blink, smoothstep(0, 0.6, h));
  if (s > 0.995) return;
  const li = E.lid[0], lo = E.lid[1], top = y0 - ry;
  const xi = x0 + inner * rx * 1.25, xo = x0 - inner * rx * 1.25;
  const shut = y0 + ry * 0.45;                        // where the lids meet
  const yi = lerp(top + li * 2 * ry, shut, s), yo = lerp(top + lo * 2 * ry, shut, s);
  const bottom = lerp(y0 + ry * 1.1, shut + 0.3, s);    // the lower lid rises a little as it shuts
  const x = x0 + gaze[0] * sq, y = y0 + gaze[1] * 0.6;
  const alpha = 1 - smoothstep(0.6, 1, h);
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.beginPath(); ctx.moveTo(xi, yi); ctx.lineTo(xo, yo); ctx.lineTo(xo, bottom); ctx.lineTo(xi, bottom); ctx.closePath(); ctx.clip();
  ellipse(ctx, x, y, rx, ry); ctx.fillStyle = '#2f2426'; ctx.fill();
  const ir = Math.min(rx, ry) * E.iris, hr = Math.max(rx, ry) * 0.2;
  // highlights: where the drawing puts them (its `look`), and with the gaze, less than the eye (the light stays)
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
  const P = op.map((p, i) => [lerp(p[0], st[i][0], lidAmt), lerp(p[1], st[i][1], lidAmt)]);
  ctx.beginPath(); ctx.moveTo(...P[0]); ctx.quadraticCurveTo(...P[1], ...P[2]); ctx.quadraticCurveTo(...P[3], ...P[4]);
  stroke(ctx, sw * 1.5, LINE, alpha);
  // the outer flick (lashes)
  const ox = x0 - inner * rx * 1.05, oy = yo + lerp(-ry * 0.1, ry * 0.1, lidAmt);
  ctx.beginPath(); ctx.moveTo(ox, oy); ctx.lineTo(ox - inner * rx * 0.38, oy - ry * 0.28); stroke(ctx, sw * 1.1, LINE, alpha);
}
function eyeExtras(ctx, x, y, fc, side, E, sw) {
  if (fc < 0.12) return;
  const sq = Math.max(fc, 0.25) ** 0.85, rx = 8 * sq * E.big, ry = 10.5 * E.big;
  // bags under the eyes (Вера: tired), and the tear of sorrow under the left one
  ctx.beginPath(); ctx.moveTo(x - rx * 0.7, y + ry * 1.25); ctx.quadraticCurveTo(x, y + ry * 1.55, x + rx * 0.7, y + ry * 1.25); stroke(ctx, sw * 0.6, LINE, 0.55 * (1 - smoothstep(0.3, 0.9, E.happy)));
  if (E.tear > 0.02 && side === -1) {
    const tx = x + rx * 0.3, ty = y + ry * 1.3 + (1 - E.tear) * -3;
    ctx.globalAlpha = E.tear; ctx.beginPath(); ctx.moveTo(tx, ty); ctx.quadraticCurveTo(tx - 5, ty + 9, tx, ty + 12); ctx.quadraticCurveTo(tx + 5, ty + 9, tx, ty); ctx.closePath();
    ctx.fillStyle = '#9fd3ea'; ctx.fill(); stroke(ctx, sw * 0.6, LINE, E.tear); ctx.globalAlpha = 1;
  }
}
function brow(ctx, x, y, fc, side, B, sw) {
  if (fc < 0.12) return;
  const sq = Math.max(fc, 0.25) ** 0.85, inner = -side, w = 21 * sq, [dy, tilt] = B;
  const yi = y + dy + tilt * 0.5, yo = y + dy - tilt * 0.5, xi = x + inner * w * 0.5, xo = x - inner * w * 0.5;
  ctx.beginPath(); ctx.moveTo(xi, yi); ctx.quadraticCurveTo((xi + xo) / 2, Math.min(yi, yo) - 1, xo, yo); stroke(ctx, sw * 1.9, '#3c2f3b');
}
function mouthPath(ctx, x, y, m) {
  const { w, cy, uc, lc, au, al, side, kx } = m;
  ctx.beginPath(); ctx.moveTo(x - w, y + cy);
  ctx.bezierCurveTo(x - au * w, y + uc, x + au * w, y + uc, x + w, y + cy);
  ctx.lineTo(x + kx * w, y + cy + side);
  ctx.bezierCurveTo(x + al * kx * w, y + lc, x - al * kx * w, y + lc, x - kx * w, y + cy + side);
  ctx.closePath();
}
function mouth(ctx, x, y, m, sw) {
  const open = Math.max(0, (0.75 * m.lc + 0.25 * (m.cy + m.side)) - (0.75 * m.uc + 0.25 * m.cy)) + m.side;
  const f = smoothstep(0.5, 2.2, open) * Math.min(1, m.fill * 1.5 + smoothstep(1.5, 4, open));
  if (f < 0.999) {   // a line: the middle of the two lips
    const c = (m.uc + m.lc) / 2, a = (m.au + m.al) / 2;
    ctx.beginPath(); ctx.moveTo(x - m.w, y + m.cy); ctx.bezierCurveTo(x - a * m.w, y + c, x + a * m.w, y + c, x + m.w, y + m.cy);
    stroke(ctx, sw * 1.1, LINE, 1 - f);
  }
  if (f > 0.001) {
    ctx.save(); ctx.globalAlpha = f;
    mouthPath(ctx, x, y, m); ctx.save(); ctx.clip();
    const mc = [0x7b, 0x2f, 0x35], wt = [0xff, 0xfa, 0xf2], t = m.teeth;
    ctx.fillStyle = `rgb(${mc.map((c, i) => Math.round(lerp(c, wt[i], t > 0.9 ? 1 : 0))).join(',')})`; ctx.fill();
    if (t > 0.05 && t <= 0.9) {   // the upper teeth showing in speech
      ctx.fillStyle = '#fffaf2'; ctx.globalAlpha = f * Math.min(1, t * 1.5);
      ctx.fillRect(x - m.w, y + Math.min(m.uc, m.cy) - 2, 2 * m.w, (m.lc - m.uc) * 0.22 + 2.2); ctx.globalAlpha = f;
    }
    if (m.tongue > 0.02) { ctx.globalAlpha = f * m.tongue; ellipse(ctx, x, y + (m.cy + m.lc) / 2 + (m.lc - m.cy) * 0.25, m.w * 0.62, Math.max(1, (m.lc - m.cy) * 0.3)); ctx.fillStyle = '#e0767a'; ctx.fill(); ctx.globalAlpha = f; }
    ctx.restore();
    mouthPath(ctx, x, y, m); stroke(ctx, sw, LINE, f);
    if (t > 0.9) { const W = m.w * m.kx; ctx.beginPath(); ctx.moveTo(x - W, y + m.cy + m.side * 0.42); ctx.quadraticCurveTo(x, y + m.cy - 1, x + W, y + m.cy + m.side * 0.42); stroke(ctx, sw * 0.6, LINE, f); }
    ctx.restore();
  }
}
// F: {e: expression (vecExpr), gaze: [x, y] the eyes' shift (units), blink: [left, right] 0..1, browAdd: units}
export function drawFace(ctx, F, px) {
  const sw = SW;
  ctx.setTransform(px, 0, 0, px, -FX0 * px, -FY0 * px);
  ctx.clearRect(FX0, FY0, FW, FH);
  const E = F.e;
  for (const s of [0, 1]) {   // cheeks
    const [x, y, fc] = SPOT.cheek[s]; if (fc < 0.2) continue;
    ctx.globalAlpha = 0.3; ellipse(ctx, x, y, 9 * Math.max(fc, 0.3), 9 * 0.62); ctx.fillStyle = '#e98a7c'; ctx.fill(); ctx.globalAlpha = 1;
  }
  for (const s of [0, 1]) {
    const side = s ? 1 : -1, [x, y, fc] = SPOT.eye[s];
    eye(ctx, x, y, fc, side, E, F.gaze || [0, 0], F.blink ? F.blink[s] : 0, sw);
    eyeExtras(ctx, x, y, fc, side, E, sw);
    const [bx, by, bf] = SPOT.brow[s];
    brow(ctx, bx, by, bf, side, [E.brow[0] + (F.browAdd || 0), E.brow[1]], sw);
  }
  const [nx, ny] = SPOT.nose;
  ctx.beginPath(); ctx.moveTo(nx - 3, ny); ctx.quadraticCurveTo(nx + 1, ny + 2, nx + 3, ny - 1); stroke(ctx, sw * 0.9);
  const [mx, my] = SPOT.mouth;
  mouth(ctx, mx, my, E.mouth, sw);
}
