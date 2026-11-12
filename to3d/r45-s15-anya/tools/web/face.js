// Аня's noir face, alive: the drawing's own face parts (styles/s15-noir/tools/head.py: eye, brow, mouth, the nose's
// black plane; noir.py's path with hard and soft corners, the stroke with pressure) ported to canvas and drawn every
// frame from a few numbers, in the front view. The canvas is the head's painted layer (front projection; the box is
// x −120…120, y −130…130 in the pack's units, 4 px a unit; a head unit of the drawing is HS units, its eye line y 12).
// The timing (blinks, saccades, gaze leading the head, speech, expressions as damped springs) is Р1's
// (to3d/r1-s3-anya/tools/web/face.js): schedules from a seeded stream, so a moment always looks the same.
export const X0 = -120, X1 = 120, Y0 = -130, Y1 = 130, PX = 4;
const HS = 1.37, EYE_Y = 12;
export const C = { black: '#07070b', white: '#ece6d6', iris: '#3d2a1e', lip: '#b0453c', hole: '#1a0d10' };
// the character's numbers (cast.py ANYA)
const EK = { w: 31, h: 11.5, r: 8, lid: 4.2 }, BR = { t: 4.2, len: 0.95, y: -3 }, MO = { y: 63, w: 17 * 0.95 }, NOSE = { ty: 38, nw: 9 };

// ---------------------------------------------------------------- noir.py
// a path through points: [x, y] — a hard corner, [x, y, 1] — the line passes smoothly
function d(pts, closed = true) {
  const n = pts.length;
  const tan = i => { if (!pts[i][2] || (!closed && (i === 0 || i === n - 1))) return [0, 0]; const a = pts[(i - 1 + n) % n], b = pts[(i + 1) % n]; return [(b[0] - a[0]) / 6, (b[1] - a[1]) / 6]; };
  let out = `M${pts[0][0]} ${pts[0][1]}`;
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const j = (i + 1) % n, p = pts[i], q = pts[j], t0 = tan(i), t1 = tan(j);
    if (!t0[0] && !t0[1] && !t1[0] && !t1[1]) out += `L${q[0]} ${q[1]}`;
    else out += `C${p[0] + t0[0]} ${p[1] + t0[1]} ${q[0] - t1[0]} ${q[1] - t1[1]} ${q[0]} ${q[1]}`;
  }
  return out + (closed ? 'Z' : '');
}
const shape = (g, pts, col) => { g.fillStyle = col; g.fill(new Path2D(d(pts))); };
const line = (g, pts, col, w) => { g.strokeStyle = col; g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'miter'; g.stroke(new Path2D(d(pts, false))); };
function wedge(g, a, b, w0, w1, col, bend = 0) {
  const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L;
  const mx = (a[0] + b[0]) / 2 + nx * bend, my = (a[1] + b[1]) / 2 + ny * bend, wm = (w0 + w1) / 2;
  shape(g, [[a[0] + nx * w0 / 2, a[1] + ny * w0 / 2], [mx + nx * wm / 2, my + ny * wm / 2, 1], [b[0] + nx * w1 / 2, b[1] + ny * w1 / 2],
    [b[0] - nx * w1 / 2, b[1] - ny * w1 / 2], [mx - nx * wm / 2, my - ny * wm / 2, 1], [a[0] - nx * w0 / 2, a[1] - ny * w0 / 2]], col);
}
const clipped = (g, pts, f) => { g.save(); g.clip(new Path2D(d(pts))); f(); g.restore(); };
const lerp = (a, b, t) => a + (b - a) * t;

// ---------------------------------------------------------------- head.py's parts, with continuous numbers
// an eye (kind 'f': lash, lower lid, a highlight). s = +1: the inner corner on the left. op: how open (1 as drawn calm),
// laugh 0…1: the eye shut into an arc
function eye(g, cx, cy, w, h, s, p) {
  const X = t => cx + s * t, op = p.op, t = EK.lid;
  if (p.laugh > 0.5) {
    shape(g, [[X(-w / 2), cy + 2], [X(-w / 6), cy - h * 0.55, 1], [X(w / 4), cy - h * 0.5, 1], [X(w / 2 + 2), cy + 3],
      [X(w / 4), cy - h * 0.5 + t + 1, 1], [X(-w / 6), cy - h * 0.55 + t, 1]], C.black);
    return;
  }
  const hh = Math.max(0.05, h * op);
  const alm = [[X(-w / 2), cy + 2], [X(-w / 6), cy - hh, 1], [X(w / 4), cy - hh * 0.92, 1], [X(w / 2), cy - 1], [X(w / 8), cy + hh * 0.55, 1]];
  const ix = X(-w * 0.06) + p.look[0], iy = cy - hh * 0.12 + p.look[1], r = EK.r;
  if (hh > 0.8) {
    shape(g, alm, C.white);
    clipped(g, alm, () => {
      g.fillStyle = C.iris; g.beginPath(); g.ellipse(ix, iy, r, r * 1.08, 0, 0, 2 * Math.PI); g.fill();
      if (op > 0.5) { g.fillStyle = C.white; g.beginPath(); g.arc(ix - r * 0.35, iy - r * 0.4, r * 0.28, 0, 2 * Math.PI); g.fill(); }
    });
  }
  // the upper lid: a black band growing to the outer corner, with the lash
  shape(g, [[X(-w / 2 - 1), cy + 2.5], [X(-w / 6), cy - hh - t * 0.55, 1], [X(w / 4), cy - hh * 0.92 - t * 0.9, 1], [X(w / 2 + 6), cy - hh * 0.5 - 6], [X(w / 2 + 1), cy],
    [X(w / 2), cy - 0.5], [X(w / 4), cy - hh * 0.92 + 0.6, 1], [X(-w / 6), cy - hh + 0.4, 1]], C.black);
  if (hh > 2) wedge(g, [X(w / 2 - 1), cy], [X(0), cy + hh * 0.55 + 1], 1.8, 0.6, C.black, -s * 1.5);
}
// a brow from the inner end a to the outer end b; tilt > 0 pulls the inner end down (anger)
function brow(g, a, b, t, p) {
  const r = p.brow, tl = p.tilt;
  a = [a[0], a[1] - r + tl]; b = [b[0], b[1] - r - tl * 0.5];
  const mx = a[0] * 0.4 + b[0] * 0.6, my = a[1] * 0.4 + b[1] * 0.6 - 4 - Math.max(0, -tl) * 0.3;
  shape(g, [[a[0], a[1] - t * 0.5], [mx, my - t * 0.55, 1], b, [mx, my + t * 0.35, 1], [a[0], a[1] + t * 0.5]], C.black);
}
// the mouth from numbers: c — the corners' height (−5 a smile, +5 sad), mid — the middle's, wk — width, open 0…1,
// grin 0…1 (an open mouth between the round «о» and the wide grin), smile 0…1 (the corners go into the cheeks)
function mouth(g, my, w0, m) {
  const mx = 0, lips = 1;
  if (m.open > 0.08) {
    const k = m.grin, w = w0 * m.wk, w2 = w * lerp(1, 1.35, k), o = Math.min(1, m.open), sm = k < 0.5 ? 1 : 0;
    const L = (a, b) => lerp(a, b, k), Y = y => my + y * o;
    const hole = [[L(-w * 0.6, -w2), Y(L(2, -5)), sm], [mx, Y(L(-6, -1)), 1], [L(w * 0.55, w2), Y(L(1, -7)), sm], [L(w * 0.35, w2 * 0.55), Y(L(14, 13)), 1], [L(-w * 0.3, -w2 * 0.3), Y(L(15, 17)), 1]];
    const teeth = [[L(-w * 0.5, -w2), Y(L(-8, -8))], [L(w * 0.5, w2), Y(L(-8, -9))], [L(w * 0.45, w2), Y(L(-1.5, 0.5))], [mx, Y(L(-1.25, 4.5)), k > 0.5 ? 1 : 0], [L(-w * 0.45, -w2), Y(L(-1, 1))]];
    const tongue = [[L(-w * 0.6, -w2 * 0.6), Y(18)], [L(-w * 0.1, -w2 * 0.2), Y(L(9, 10)), 1], [L(w * 0.4, w2 * 0.5), Y(10), 1], [L(w * 0.6, w2 * 0.7), Y(18)]];
    shape(g, hole, C.hole);
    clipped(g, hole, () => { if (m.teeth > 0.3) shape(g, teeth, C.white); shape(g, tongue, C.lip); });
    shape(g, [[hole[0][0] - 1, hole[0][1] + 1], [mx - w * 0.4, Y(L(-9, -8)), 1], [mx, Y(L(-9, -5)), 1], [mx + w * 0.5, Y(-10), 1], [hole[2][0] + 1, hole[2][1] + 1], [mx, hole[1][1] + 0.5, 1]], C.lip);
    return;
  }
  const w = w0 * m.wk, c = m.c, a = [mx - w, my + c], b = [mx + w, my + c], M = [mx, my + m.mid];
  shape(g, [a, [mx - w * 0.5, M[1] + 0.5, 1], [M[0], M[1] + 1, 1], [mx + w * 0.5, M[1] + 0.5, 1], b, [mx + w * 0.45, M[1] + 6 * lips, 1], [mx - w * 0.4, M[1] + 6.5 * lips, 1]], C.lip);
  shape(g, [a, [mx - w * 0.45, M[1] - 4.5 * lips, 1], [mx - 1, M[1] - 3 * lips], [mx + w * 0.45, M[1] - 5 * lips, 1], b, [mx + w * 0.5, M[1] + 0.8, 1], [M[0], M[1] + 1.2, 1], [mx - w * 0.5, M[1] + 0.8, 1]], C.lip);
  line(g, [a, [mx - w * 0.5, M[1] + 0.6, 1], [M[0], M[1] + 1, 1], [mx + w * 0.5, M[1] + 0.6, 1], b], C.black, 1.6);
  shape(g, [[mx - w * 0.35, M[1] + 8], [mx + w * 0.4, M[1] + 7.5], [mx + w * 0.2, M[1] + 10.5], [mx - w * 0.2, M[1] + 11]], C.black);
  if (m.smile > 0.05) {     // the corners go into the cheeks
    const s = m.smile;
    wedge(g, b, [b[0] + 4 * s, b[1] - 6 * s], 2.4, 0.5, C.black, 1.5 * s);
    wedge(g, a, [a[0] - 2 * s, a[1] - 5 * s], 2, 0.5, C.black, -1 * s);
  }
}

// one frame of the face from its numbers
export function draw(g, p) {
  g.setTransform(PX * HS, 0, 0, PX * HS, -X0 * PX, (-Y0 - EYE_Y * HS) * PX);
  g.clearRect(-200, -200, 400, 400);
  const ey = EYE_Y, by = ey - 15 + BR.y, dn = p.cheeks * -1.5, w = EK.w * 0.92;
  const { ty, nw } = NOSE;
  // the nose: only the black plane under the tip
  shape(g, [[-nw * 0.75, ty + 4], [0, ty + 1, 1], [nw * 0.9, ty + 2], [nw * 0.7, ty + 7], [2, ty + 9, 1], [-nw * 0.6, ty + 7]], C.black);
  if (p.cheeks > 0.3) {     // a grin's folds beside the mouth
    const k = MO.w * 1.16, y = MO.y;
    g.globalAlpha = Math.min(1, (p.cheeks - 0.3) / 0.4);
    shape(g, [[k * 1.5, y - 20], [k * 1.9, y - 8, 1], [k * 1.55, y + 6], [k * 1.72, y - 8, 1]], C.black);
    shape(g, [[-k * 1.5, y - 20], [-k * 1.8, y - 8, 1], [-k * 1.55, y + 6], [-k * 1.68, y - 8, 1]], C.black);
    g.globalAlpha = 1;
  }
  const blink = { ...p, op: p.op * (1 - p.blink) };
  eye(g, -27, ey + dn, w, EK.h, -1, blink); brow(g, [-9, by + 1], [-9 - 37 * BR.len, by - 4], BR.t, p);
  eye(g, 27, ey + dn, w, EK.h, 1, blink); brow(g, [9, by + 1], [9 + 37 * BR.len, by - 4], BR.t, p);
  mouth(g, MO.y, MO.w, p.mouth);
}

// ---------------------------------------------------------------- the sheet's expressions (head.py EXPR) and speech
const M0 = { c: 0, mid: 0, wk: 1, open: 0, grin: 0, smile: 0, teeth: 1 };
export const EXPR = {
  calm: { brow: 2, tilt: -1, op: 0.85, look: [0, 0], cheeks: 0, laugh: 0, mouth: { ...M0, c: -5, mid: 1.5, smile: 1 } },                 // Аня's rest: «smile»
  joy: { brow: 3, tilt: -2, op: 0.55, look: [0, 0], cheeks: 1, laugh: 0, mouth: { ...M0, c: -5, open: 1, grin: 1, smile: 1 } },
  surprise: { brow: 9, tilt: -3, op: 1.45, look: [0, 0], cheeks: 0, laugh: 0, mouth: { ...M0, open: 1, grin: 0, teeth: 0 } },
  sad: { brow: 2, tilt: -7, op: 0.75, look: [0, 2], cheeks: 0, laugh: 0, mouth: { ...M0, c: 5, mid: -1 } },
  anger: { brow: -5, tilt: 7, op: 0.7, look: [0, 0], cheeks: 0, laugh: 0, mouth: { ...M0, c: 4, mid: -1, wk: 0.85 } },
};
export const EXPR_NAMES = Object.keys(EXPR);
// mouth shapes for speech: how open, wide (1) or round (0), teeth: closed lips (m b p), teeth on the lip (f v), wide
// (e i), open (a), round (o), small round (u)
const VIS = {
  M: { o: 0, g: 0.5, w: 1, t: 0 }, F: { o: 0.16, g: 0.8, w: 1, t: 1 }, E: { o: 0.3, g: 1, w: 1.05, t: 1 },
  A: { o: 0.62, g: 0.6, w: 1, t: 0.6 }, O: { o: 0.5, g: 0, w: 0.9, t: 0 }, U: { o: 0.26, g: 0, w: 0.7, t: 0 },
};

// ---------------------------------------------------------------- time (Р1's)
function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const gauss = R => Math.sqrt(-2 * Math.log(R() + 1e-12)) * Math.cos(2 * Math.PI * R());
const lognorm = (R, median, sigma) => median * Math.exp(sigma * gauss(R));
// a critically damped approach from x0 to x1, τ seconds after the change
const settle = (x0, x1, tau, w) => tau <= 0 ? x0 : x1 + (x0 - x1) * (1 + w * tau) * Math.exp(-w * tau);

// a blink's closing at time since its start: fast close, short hold, slower open
function blinkCurve(s) {
  if (s < 0) return 0;
  if (s < 0.07) { const u = s / 0.07; return u * u; }
  if (s < 0.10) return 1;
  if (s < 0.25) { const u = (s - 0.10) / 0.15; return (1 - u) * (1 - u); }
  return 0;
}

export class LiveFace {
  constructor(seed = 7) {
    this.seed = seed;
    const R = rng(seed);
    // spontaneous blinks and fixations for ten minutes
    this.blinks = []; for (let t = 0.6 + R() * 1.5; t < 600;) { this.blinks.push(t); if (R() < 0.12) this.blinks.push(t + 0.24 + R() * 0.1); t += Math.max(0.9, lognorm(R, 2.8, 0.55)); }
    this.fix = []; let p = [0, 0];
    for (let t = 0.3; t < 600;) {
      const big = R() < 0.25, q = [gauss(R) * (big ? 3.6 : 1.8), gauss(R) * (big ? 1.6 : 0.9)];
      q[0] = Math.max(-5, Math.min(5, q[0])); q[1] = Math.max(-2.5, Math.min(2.5, q[1]));
      const amp = Math.hypot(q[0] - p[0], q[1] - p[1]) * 4;           // head units → degrees, roughly
      this.fix.push({ t, from: p, to: q, dur: (22 + 2.7 * amp) / 1000 }); p = q; t += Math.max(0.18, lognorm(R, 0.55, 0.5));
    }
    this.exprKeys = [{ t: -10, w: { calm: 1 } }];
    this.talkFrom = null; this.speech = null;
    this.lead = null;
  }
  // expression changes: at time t go to weights w ({name: weight})
  setExpr(t, w) { this.exprKeys = this.exprKeys.filter(k => k.t < t); this.exprKeys.push({ t, w }); }
  exprWeights(t, rate = 12) {
    const cur = {};
    const prev = this.exprKeys[0]; for (const n of EXPR_NAMES) cur[n] = prev.w[n] || 0;
    for (let i = 1; i < this.exprKeys.length; i++) {
      const k = this.exprKeys[i]; if (k.t > t) break;
      const next = this.exprKeys[i + 1], until = next && next.t <= t ? next.t : t;
      const start = { ...cur };
      for (const n of EXPR_NAMES) cur[n] = settle(start[n], k.w[n] || 0, until - k.t, rate);
    }
    return cur;
  }
  // speech from time t0 on (null: silent)
  talk(t0, seed = 3) {
    if (t0 == null) { this.talkFrom = null; this.speech = null; return; }
    const R = rng(seed), seq = []; let t = t0 + 0.15;
    const cons = ['M', 'F', 'E', 'M', 'E'], vow = ['A', 'E', 'O', 'A', 'U', 'E', 'A', 'O'];
    while (t < t0 + 600) {
      const words = 3 + Math.floor(R() * 6);
      for (let w = 0; w < words; w++) {
        const syl = 1 + Math.floor(R() * 3);
        for (let s = 0; s < syl; s++) {
          if (R() < 0.75) { const dd = 0.06 + R() * 0.04; seq.push({ t, v: cons[Math.floor(R() * cons.length)] }); t += dd; }
          const dd = 0.11 + R() * 0.1; seq.push({ t, v: vow[Math.floor(R() * vow.length)] }); t += dd;
        }
        seq.push({ t, v: 'M' }); t += 0.05 + R() * 0.09;
      }
      seq.push({ t, v: 'M' }); t += 0.35 + R() * 0.6;
    }
    // the mouth follows the targets as a critically damped spring, sampled at 200 Hz
    const dt = 1 / 200, n = Math.ceil((seq[seq.length - 1].t - t0) / dt), out = new Float32Array(n * 4);
    let k = 0; const x = [0, 0.5, 1, 0], v = [0, 0, 0, 0], W = 34;
    for (let i = 0; i < n; i++) {
      const tt = t0 + i * dt; while (k + 1 < seq.length && seq[k + 1].t <= tt) k++;
      const s = VIS[seq[k].v], tg = [s.o, s.g, s.w, s.t];
      for (let c = 0; c < 4; c++) { const a = W * W * (tg[c] - x[c]) - 2 * W * v[c]; v[c] += a * dt; x[c] += v[c] * dt; out[i * 4 + c] = x[c]; }
    }
    this.talkFrom = t0; this.speech = { dt, n, out };
  }
  // the head's motion over a clip, for gaze leading and turn blinks: yaw/pitch at 100 Hz from t=0
  setHead(track) {
    this.lead = null; if (!track) return;
    const { dt, yaw, pitch } = track, n = yaw.length, ahead = Math.round(0.25 / dt), R = rng(this.seed + 11);
    const lx = new Float32Array(n), ly = new Float32Array(n), turnBlinks = [];
    let cur = [0, 0], sac = null;
    for (let i = 0; i < n; i++) {
      const j = Math.min(n - 1, i + ahead);
      const tg = [Math.max(-5.5, Math.min(5.5, (yaw[j] - yaw[i]) * 13)), Math.max(-2.5, Math.min(2.5, -(pitch[j] - pitch[i]) * 9))];
      const t = i * dt;
      if (sac && t >= sac.t + sac.dur) { cur = sac.to; sac = null; }
      if (!sac && Math.hypot(tg[0] - cur[0], tg[1] - cur[1]) > 1.5) {
        const amp = Math.hypot(tg[0] - cur[0], tg[1] - cur[1]) * 4;
        sac = { t, from: cur, to: tg, dur: (22 + 2.7 * amp) / 1000 };
        if (Math.abs(tg[0] - cur[0]) > 2.5 && R() < 0.65) turnBlinks.push(t + 0.02);
      }
      if (sac) { const u = Math.min(1, (t - sac.t) / sac.dur), e = 1 - Math.pow(1 - u, 2.5); lx[i] = lerp(sac.from[0], sac.to[0], e); ly[i] = lerp(sac.from[1], sac.to[1], e); }
      else { // the eyes come back smoothly while the head follows
        const rate = 24 * dt; cur = [cur[0] + Math.max(-rate, Math.min(rate, tg[0] - cur[0])), cur[1] + Math.max(-rate, Math.min(rate, tg[1] - cur[1]))];
        lx[i] = cur[0]; ly[i] = cur[1];
      }
    }
    this.lead = { dt, lx, ly, turnBlinks };
  }
  // the face's numbers at time t (seconds)
  at(t, opts = {}) {
    const w = this.exprWeights(t), wb = this.exprWeights(t, 16);       // brows a little ahead
    const mix = (get, ww = w) => { let s = 0, z = 0; for (const n of EXPR_NAMES) { s += ww[n] * get(EXPR[n]); z += ww[n]; } return s / (z || 1); };
    const p = {
      brow: mix(e => e.brow, wb), tilt: mix(e => e.tilt, wb), op: mix(e => e.op), cheeks: mix(e => e.cheeks), laugh: mix(e => e.laugh),
      mouth: Object.fromEntries(Object.keys(M0).map(k => [k, mix(e => e.mouth[k])])),
    };
    // gaze: the expression's own, the fixations, the lead of a head turn
    const base = [mix(e => e.look[0]), mix(e => e.look[1])];
    let lo = 0, hi = this.fix.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (this.fix[m].t <= t) lo = m; else hi = m - 1; }
    const f = this.fix[lo], u = Math.min(1, Math.max(0, (t - f.t) / f.dur)), e = 1 - Math.pow(1 - u, 2.5);
    let look = [base[0] + lerp(f.from[0], f.to[0], e) * 0.6, base[1] + lerp(f.from[1], f.to[1], e) * 0.6];
    let blink = 0;
    for (const b of this.blinks) { if (b > t) break; blink = Math.max(blink, blinkCurve(t - b)); }
    const ht = opts.headT ?? t;              // the clip's own time, for what the head does
    if (this.lead && ht != null && ht >= 0) {
      const i = Math.min(this.lead.lx.length - 1, Math.floor(ht / this.lead.dt));
      look = [look[0] + this.lead.lx[i], look[1] + this.lead.ly[i]];
      for (const b of this.lead.turnBlinks) { if (b > ht) break; blink = Math.max(blink, blinkCurve(ht - b)); }
    }
    look[0] = Math.max(-6, Math.min(6, look[0])); look[1] = Math.max(-3, Math.min(3, look[1]));
    if (this.still) { look = base; blink = 0; }      // a still picture: the expression as drawn
    p.look = look; p.blink = blink;
    // speech over the expression's mouth
    if (this.speech && t >= this.talkFrom && t < (this.talkTo ?? Infinity)) {
      const S = this.speech, i = Math.floor((t - this.talkFrom) / S.dt) % S.n, o = S.out, m = p.mouth;
      m.open = lerp(m.open * 0.5, Math.max(0, o[i * 4]) + m.open * 0.2, 0.9); m.grin = lerp(m.grin, o[i * 4 + 1], 0.8);
      m.wk *= o[i * 4 + 2]; m.teeth = o[i * 4 + 3];
    }
    p.jaw = Math.max(0, p.mouth.open) * lerp(1, 0.7, p.mouth.grin);
    return p;
  }
}
