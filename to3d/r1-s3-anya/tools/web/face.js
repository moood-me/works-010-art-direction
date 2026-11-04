// Аня's face, alive: the drawing's own face parts (styles/s3-graphic/tools/face.py: eye, brow, closed eye; the mouths of
// tools/faces.py) drawn every frame on a canvas from parameters, so the face moves as a drawing moves — the parts are
// signs, they change shape, they are not a 3D eye. The canvas is the head's painted layer (front projection, the same
// box as faces.py: x −120…120, y −130…130 in the drawing's units, 4 px a unit).
//
// What moves, and its timing (from how faces move, not from sines):
//   blinks      — spontaneous, intervals log-normal (median 2.8 s, rarely under 1 s, sometimes 7 s), now and then a
//                 double blink; the lid closes fast (≈70 ms), holds (≈30 ms), opens slower (≈150 ms); also a blink
//                 with most large gaze shifts at head turns.
//   saccades    — fixations log-normal (median ≈0.55 s); the jump lasts 22 ms + 2.7 ms per degree, fast start, slower
//                 landing; targets near the expression's own gaze.
//   gaze leads  — the eyes jump toward where the head will be in ≈0.25 s, then come back smoothly while the head
//                 follows (the head lags the eyes in a real turn).
//   speech      — syllables of consonant + vowel mouth shapes (visemes), words and phrases with pauses; the mouth
//                 follows its targets as a critically damped spring (co-articulation), the jaw opens with it.
//   expressions — weights of the sheet's five, mixed; a change goes to its new weights as a critically damped spring
//                 (≈0.3 s), brows a little ahead of the mouth.
export const X0 = -120, X1 = 120, Y0 = -130, Y1 = 130, PX = 4;
const LW = 2.2, K43 = 4 / 3;
export const C = {
  skin: '#f4cdb0', shade: '#e3a98c', line: '#a8604a', blush: '#f2967f', white: '#fffaf3', iris: '#6b7a3c', pupil: '#2b2416',
  lash: '#3b1d16', hairL: '#4e1d14', lip: '#d77467', mouth: '#7a2a24', tongue: '#e07a70',
};

// ---------------------------------------------------------------- drawing (the drawing's own construction)
function fill(g, d, col, line, w, alpha = 1) {
  const p = new Path2D(d); g.globalAlpha = alpha; g.fillStyle = col; g.fill(p);
  if (line) { g.strokeStyle = line; g.lineWidth = w || LW; g.lineJoin = 'round'; g.lineCap = 'round'; g.stroke(p); }
  g.globalAlpha = 1;
}
function stroke(g, d, line, w, alpha = 1) {
  const p = new Path2D(d); g.globalAlpha = alpha; g.strokeStyle = line; g.lineWidth = w || LW; g.lineJoin = 'round'; g.lineCap = 'round'; g.stroke(p); g.globalAlpha = 1;
}
function ell(g, cx, cy, rx, ry, col, alpha = 1) { g.globalAlpha = alpha; g.fillStyle = col; g.beginPath(); g.ellipse(cx, cy, Math.max(rx, 0.01), Math.max(ry, 0.01), 0, 0, 2 * Math.PI); g.fill(); g.globalAlpha = 1; }
function clipped(g, d, f) { g.save(); g.clip(new Path2D(d)); f(); g.restore(); }

function oval(cx, cy, rx, ry, top = 1, bot = 1, tilt = 0) {
  const x0 = cx - rx, x1 = cx + rx, y0 = cy + tilt, y1 = cy - tilt;
  return `M ${x0} ${y0} C ${x0} ${cy - K43 * ry * top + tilt * .5}, ${x1} ${cy - K43 * ry * top - tilt * .5}, ${x1} ${y1} ` +
    `C ${x1} ${cy + K43 * ry * bot - tilt * .5}, ${x0} ${cy + K43 * ry * bot + tilt * .5}, ${x0} ${y0} Z`;
}

// face.py eye(): white oval, iris, pupil, two highlights, the upper lid cutting the top and shading the eye, a filled
// lash shape thick to the outer corner with a wing, a lower lid pushed up for smiles
function eye(g, cx, cy, rx, ry, { look = [0, 0], lid = 0, lidtilt = 0, lower = 0, ir, sq = 1, flick = 1, lash = 2.4 }) {
  ir = ir || ry * 0.62;
  const d = oval(cx, cy, rx, ry), ix = cx + look[0], iy = cy + look[1];
  const h = cy - ry + 2 * ry * lid, e = ry * 0.15 * lid, ya = cy + e + lidtilt, yb = cy + e - lidtilt, yc = (4 * h - (ya + yb) / 2) / 3;
  const edge = `M ${cx - rx - 3} ${ya} C ${cx - rx} ${yc}, ${cx + rx} ${yc}, ${cx + rx + 3} ${yb}`;
  const yl = cy + K43 * ry * (1 - 2.2 * lower);
  clipped(g, d, () => {
    fill(g, d, C.white);
    ell(g, ix, iy, ir * sq, ir, C.iris); ell(g, ix, iy, ir * .55 * sq, ir * .55, C.pupil);
    ell(g, ix - ir * .35 * sq, iy - ir * .4, ir * .28 * sq, ir * .28, '#fff'); ell(g, ix + ir * .35 * sq, iy + ir * .38, ir * .12, ir * .12, '#fff', .85);
    fill(g, edge + ` L ${cx + rx + 3} ${yb + 7} C ${cx + rx} ${yc + 7}, ${cx - rx} ${yc + 7}, ${cx - rx - 3} ${ya + 7} Z`, C.line, null, 0, .18);
  });
  // the lids' skin over a slightly bigger oval, so no white rim is left at the eye's edge where a lid covers it
  clipped(g, oval(cx, cy, rx + 1.4, ry + 1.4), () => {
    fill(g, edge + ` L ${cx + rx + 6} ${cy - ry - 30} L ${cx - rx - 6} ${cy - ry - 30} Z`, C.skin);
    if (lower > 0) fill(g, `M ${cx - rx - 3} ${cy + ry * .1} C ${cx - rx * .7} ${yl}, ${cx + rx * .7} ${yl}, ${cx + rx + 3} ${cy + ry * .1} L ${cx + rx + 6} ${cy + ry + 30} L ${cx - rx - 6} ${cy + ry + 30} Z`, C.skin);
  });
  const th = LW * lash;
  let lashD;
  if (flick >= 0) {
    const xi = cx - rx - 1, yi = ya, xo = cx + rx + 2, yo = yb;
    const wing = ` C ${xo + 4} ${yo - 2}, ${xo + 8} ${yo - th * .9}, ${xo + 10} ${yo - th * 2.2} C ${xo + 4} ${yo - th * 1.6}, ${xo} ${yo - th * 1.3}, ${xo - 4} ${yo - th * 1.2}`;
    lashD = `M ${xi} ${yi + 1} C ${cx - rx} ${yc}, ${cx + rx} ${yc}, ${xo} ${yo}${wing} C ${cx + rx * .7} ${yc - th * 1.1}, ${cx - rx * .8} ${yc - th * .5}, ${xi} ${yi + 1} Z`;
  } else {
    const xi = cx + rx + 1, yi = yb, xo = cx - rx - 2, yo = ya;
    const wing = ` C ${xo - 4} ${yo - 2}, ${xo - 8} ${yo - th * .9}, ${xo - 10} ${yo - th * 2.2} C ${xo - 4} ${yo - th * 1.6}, ${xo} ${yo - th * 1.3}, ${xo + 4} ${yo - th * 1.2}`;
    lashD = `M ${xi} ${yi + 1} C ${cx + rx} ${yc}, ${cx - rx} ${yc}, ${xo} ${yo}${wing} C ${cx - rx * .7} ${yc - th * 1.1}, ${cx + rx * .8} ${yc - th * .5}, ${xi} ${yi + 1} Z`;
  }
  fill(g, lashD, C.lash, C.lash, LW * .5);
  if (lower > 0) stroke(g, `M ${cx - rx * .8} ${cy + ry * .55 - lower * ry * .5} C ${cx - rx * .5} ${yl + 2}, ${cx + rx * .5} ${yl + 2}, ${cx + rx * .8} ${cy + ry * .55 - lower * ry * .5}`, C.line, LW * .8);
  else stroke(g, `M ${cx - rx * .55} ${cy + ry} C ${cx - rx * .2} ${cy + ry * 1.12}, ${cx + rx * .3} ${cy + ry * 1.1}, ${cx + rx * .65} ${cy + ry * .95}`, C.line, LW * .7, .55);
}
const closedEye = (g, cx, cy, rx, w) => stroke(g, `M ${cx - rx} ${cy} C ${cx - rx * .5} ${cy - rx * .8}, ${cx + rx * .5} ${cy - rx * .8}, ${cx + rx} ${cy}`, C.lash, LW * w);
function brow(g, x0, y0, x1, y1, bend, t) {
  const mx = (x0 + x1) / 2, my = (y0 + y1) / 2 - bend;
  fill(g, `M ${x0} ${y0 + t * .5} Q ${mx} ${my + t * .4} ${x1} ${y1} Q ${mx} ${my - t * .6} ${x0} ${y0 - t * .5} Z`, C.hairL, C.hairL, LW * .6);
}

// the mouth from a few numbers: half width w, opening o, smile s (−1…1), round r, box b (the angry mouth), teeth top/bottom
function mouth(g, m) {
  const { w, o, s, r, b, tT, tB } = m;
  const open = Math.min(1, o * 5);
  let yc = (76 - 6 * s) * (1 - open) + (72 - 6 * s) * open + 12 * r * open;
  if (o < 0.04) {
    const ym = 76 + 2 * s;
    stroke(g, `M ${-w} ${yc} C ${-w * .4} ${ym + 2 * s}, ${w * .4} ${ym + 2 * s}, ${w} ${yc}`, C.line, LW * 1.1);
    if (s > 0) fill(g, 'M -8 82 C -2 86, 4 86, 8 82 C 2 84, -2 84, -8 82 Z', C.lip, C.lip, LW * .8, Math.min(1, s * 1.5));
    if (s < 0) stroke(g, 'M -8 90 C -2 92, 4 92, 8 90', C.lip, LW, Math.min(1, -s * 1.5));
    return;
  }
  const H = 40 * o * (1 - 0.55 * r), ytc = yc + 4 * s - 10 * r - 8 * b, yb = yc + H;
  const d = `M ${-w} ${yc} C ${-w * .4} ${ytc}, ${w * .4} ${ytc}, ${w} ${yc} C ${w * (.9 + .1 * b)} ${yc + H * (.8 + .1 * b)}, ${w * .4} ${yb}, 0 ${yb} C ${-w * .4} ${yb}, ${-w * (.9 + .1 * b)} ${yc + H * (.8 + .1 * b)}, ${-w} ${yc} Z`;
  fill(g, d, b > 0.5 ? '#5e1f1a' : C.mouth);
  clipped(g, d, () => {
    if (tT > 0.02) fill(g, `M ${-w - 10} ${ytc - 12} L ${w + 10} ${ytc - 12} L ${w + 10} ${yc + H * .3 * tT} L ${-w - 10} ${yc + H * .34 * tT} Z`, '#fff');
    if (tB > 0.02) fill(g, `M ${-w - 10} ${yb - H * .22 * tB} L ${w + 10} ${yb - H * .26 * tB} L ${w + 10} ${yb + 10} L ${-w - 10} ${yb + 10} Z`, '#fff');
    if (o > 0.25 && tB < 0.5) ell(g, 0, yb, w * .66, H * .28, C.tongue, Math.min(1, (o - .25) * 4) * (1 - tB));
  });
  stroke(g, d, C.line, LW);
}

// one frame of the face from its parameters
export function draw(g, p) {
  g.setTransform(PX, 0, 0, PX, -X0 * PX, -Y0 * PX);
  g.clearRect(X0, Y0, X1 - X0, Y1 - Y0);
  for (const x of [-46, 46]) ell(g, x, 44, 20, 12, C.blush, .45);
  for (const [sx, flick] of [[-1, -1], [1, 1]]) {
    const cx = 36 * sx, rs = p.rs;
    const lid = p.lid + (1 - p.lid) * p.blink;
    if (p.happy > 0.55) { clipped(g, oval(cx, 0, 22 * rs + 2, 26 * rs + 2), () => fill(g, oval(cx, 0, 30, 34), C.skin)); closedEye(g, cx, 6, 21, 2.2); }
    else eye(g, cx, 0, 22 * rs, 26 * rs, { look: p.look, lid: Math.min(1, lid + p.happy * 0.5), lidtilt: sx * p.lidtilt, lower: p.happy * 1.1, ir: p.ir, flick });
    const B = p.brow; brow(g, sx * -B[0], B[1], sx * -B[2], B[3], B[4], B[5]);
  }
  fill(g, 'M -2 22 C 4 34, 10 40, 8 46 C 4 50, -4 50, -8 47 C -4 44, 0 40, -2 22 Z', C.shade);
  stroke(g, 'M -9 46 C -4 50, 4 50, 9 46', C.line, LW * .9);
  mouth(g, p.mouth);
  for (const [x, y] of [[-50, 28], [-40, 34], [-58, 36], [-32, 26], [50, 28], [40, 34], [58, 36], [32, 26], [-46, 42], [46, 42]]) ell(g, x, y, 1.9, 1.9, '#c7745a', .7);
}

// ---------------------------------------------------------------- the sheet's expressions and the speech shapes
// brow: inner x, inner y, outer x, outer y, bend, thickness (the image-left brow; the other mirrored)
export const EXPR = {
  dream: { brow: [-12, -38, -56, -36, 5, 6], lid: .26, lidtilt: 0, look: [0, -3], ir: 16, rs: 1, happy: 0, mouth: { w: 20, o: 0, s: .5, r: 0, b: 0, tT: 0, tB: 0 } },
  joy: { brow: [-12, -44, -56, -42, 8, 6], lid: .1, lidtilt: 0, look: [0, 0], ir: 16, rs: 1, happy: 1, mouth: { w: 24, o: .8, s: 1, r: 0, b: 0, tT: 1, tB: 0 } },
  surprise: { brow: [-12, -54, -56, -52, 10, 6], lid: 0, lidtilt: 0, look: [0, 0], ir: 13, rs: 1.12, happy: 0, mouth: { w: 9, o: .75, s: 0, r: 1, b: 0, tT: 0, tB: 0 } },
  sad: { brow: [-12, -46, -56, -32, 2, 6], lid: .34, lidtilt: -5, look: [0, 4], ir: 16, rs: 1, happy: 0, mouth: { w: 16, o: 0, s: -1, r: 0, b: 0, tT: 0, tB: 0 } },
  anger: { brow: [-12, -26, -56, -44, -2, 7], lid: .3, lidtilt: 6, look: [0, 2], ir: 16, rs: 1, happy: 0, mouth: { w: 24, o: .55, s: -.4, r: 0, b: 1, tT: 1, tB: 1 } },
};
export const EXPR_NAMES = Object.keys(EXPR);
// mouth shapes for speech (o, w change, r, teeth): closed lips (m b p), teeth on the lip (f v), wide (e i),
// open (a), round (o), small round (u)
const VIS = {
  M: { o: 0, dw: -2, r: 0, tT: 0 }, F: { o: .12, dw: 0, r: 0, tT: 1 }, E: { o: .28, dw: 4, r: 0, tT: .8 },
  A: { o: .55, dw: 1, r: 0, tT: .3 }, O: { o: .42, dw: -9, r: .8, tT: 0 }, U: { o: .2, dw: -11, r: 1, tT: 0 },
};

// ---------------------------------------------------------------- time
function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const gauss = R => Math.sqrt(-2 * Math.log(R() + 1e-12)) * Math.cos(2 * Math.PI * R());
const lognorm = (R, median, sigma) => median * Math.exp(sigma * gauss(R));
const lerp = (a, b, t) => a + (b - a) * t;
// a critically damped approach from x0 to x1, τ seconds after the change
const settle = (x0, x1, tau, w) => tau <= 0 ? x0 : x1 + (x0 - x1) * (1 + w * tau) * Math.exp(-w * tau);

// a blink's closing at time since its start: fast close, short hold, slower open
function blinkCurve(s) {
  if (s < 0) return 0;
  if (s < 0.07) { const u = s / 0.07; return u * u; }
  if (s < 0.10) return 1;
  if (s < 0.25) { const u = (s - 0.10) / 0.15; return 1 - (1 - (1 - u) * (1 - u)) ; }
  return 0;
}

// A face over time. head(t): the head's yaw and pitch (radians) at time t, or null when it does not move
export class LiveFace {
  constructor(seed = 7) {
    this.seed = seed;
    const R = rng(seed);
    // spontaneous blinks and fixations for ten minutes
    this.blinks = []; for (let t = 0.6 + R() * 1.5; t < 600;) { this.blinks.push(t); if (R() < 0.12) this.blinks.push(t + 0.24 + R() * 0.1); t += Math.max(0.9, lognorm(R, 2.8, 0.55)); }
    this.fix = []; let p = [0, 0];
    for (let t = 0.3; t < 600;) {
      const big = R() < 0.25, q = [gauss(R) * (big ? 6 : 3), gauss(R) * (big ? 3 : 1.6)];
      q[0] = Math.max(-8, Math.min(8, q[0])); q[1] = Math.max(-5, Math.min(5, q[1]));
      const amp = Math.hypot(q[0] - p[0], q[1] - p[1]) * 2.5;           // drawing units → degrees, roughly
      this.fix.push({ t, from: p, to: q, dur: (22 + 2.7 * amp) / 1000 }); p = q; t += Math.max(0.18, lognorm(R, 0.55, 0.5));
    }
    this.exprKeys = [{ t: -10, w: { dream: 1 } }];
    this.talkFrom = null; this.speech = null;
    this.lead = null;
  }
  // expression changes: at time t go to weights w ({name: weight})
  setExpr(t, w) { this.exprKeys = this.exprKeys.filter(k => k.t < t); this.exprKeys.push({ t, w }); }
  exprWeights(t, rate = 12) {
    let cur = {};
    for (const n of EXPR_NAMES) cur[n] = 0;
    let prev = this.exprKeys[0]; for (const n of EXPR_NAMES) cur[n] = prev.w[n] || 0;
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
          if (R() < 0.75) { const d = 0.06 + R() * 0.04; seq.push({ t, v: cons[Math.floor(R() * cons.length)] }); t += d; }
          const d = 0.11 + R() * 0.1; seq.push({ t, v: vow[Math.floor(R() * vow.length)] }); t += d;
        }
        seq.push({ t, v: 'M' }); t += 0.05 + R() * 0.09;
      }
      seq.push({ t, v: 'M' }); t += 0.35 + R() * 0.6;
    }
    // the mouth follows the targets as a critically damped spring, sampled at 200 Hz
    const dt = 1 / 200, n = Math.ceil((seq[seq.length - 1].t - t0) / dt), out = new Float32Array(n * 4);
    let k = 0, x = [0, 0, 0, 0], v = [0, 0, 0, 0], W = 34;
    for (let i = 0; i < n; i++) {
      const tt = t0 + i * dt; while (k + 1 < seq.length && seq[k + 1].t <= tt) k++;
      const g = VIS[seq[k].v], tg = [g.o, g.dw, g.r, g.tT];
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
      const tg = [Math.max(-9, Math.min(9, (yaw[j] - yaw[i]) * 22)), Math.max(-5, Math.min(5, -(pitch[j] - pitch[i]) * 18))];
      const t = i * dt;
      if (sac && t >= sac.t + sac.dur) { cur = sac.to; sac = null; }
      if (!sac && Math.hypot(tg[0] - cur[0], tg[1] - cur[1]) > 2.5) {
        const amp = Math.hypot(tg[0] - cur[0], tg[1] - cur[1]) * 2.5;
        sac = { t, from: cur, to: tg, dur: (22 + 2.7 * amp) / 1000 };
        if (Math.abs(tg[0] - cur[0]) > 4 && R() < 0.65) turnBlinks.push(t + 0.02);
      }
      if (sac) { const u = Math.min(1, (t - sac.t) / sac.dur), e = 1 - Math.pow(1 - u, 2.5); lx[i] = lerp(sac.from[0], sac.to[0], e); ly[i] = lerp(sac.from[1], sac.to[1], e); }
      else { // the eyes come back smoothly while the head follows
        const rate = 40 * dt; cur = [cur[0] + Math.max(-rate, Math.min(rate, tg[0] - cur[0])), cur[1] + Math.max(-rate, Math.min(rate, tg[1] - cur[1]))];
        lx[i] = cur[0]; ly[i] = cur[1];
      }
    }
    this.lead = { dt, lx, ly, turnBlinks };
  }
  // the face's parameters at time t (seconds)
  at(t, opts = {}) {
    const w = this.exprWeights(t), wb = this.exprWeights(t, 16);       // brows a little ahead
    let sum = 0; for (const n of EXPR_NAMES) sum += w[n]; sum = sum || 1;
    const mix = (get, ww = w) => { let s = 0, z = 0; for (const n of EXPR_NAMES) { s += ww[n] * get(EXPR[n]); z += ww[n]; } return s / (z || 1); };
    const p = {
      brow: [0, 1, 2, 3, 4, 5].map(i => mix(e => e.brow[i], wb)), lid: mix(e => e.lid), lidtilt: mix(e => e.lidtilt),
      ir: mix(e => e.ir), rs: mix(e => e.rs), happy: (h => h <= .35 ? 0 : (h - .35) / .65)(mix(e => e.happy)),
      mouth: Object.fromEntries(['w', 'o', 's', 'r', 'b', 'tT', 'tB'].map(k => [k, mix(e => e.mouth[k])])),
    };
    // gaze: the expression's own, the fixations, the lead of a head turn
    const base = [mix(e => e.look[0]), mix(e => e.look[1])];
    let f = this.fix[0]; { let lo = 0, hi = this.fix.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (this.fix[m].t <= t) lo = m; else hi = m - 1; } f = this.fix[lo]; }
    const u = Math.min(1, Math.max(0, (t - f.t) / f.dur)), e = 1 - Math.pow(1 - u, 2.5);
    let look = [base[0] + lerp(f.from[0], f.to[0], e) * 0.6, base[1] + lerp(f.from[1], f.to[1], e) * 0.6];
    let blink = 0;
    for (const b of this.blinks) { if (b > t) break; blink = Math.max(blink, blinkCurve(t - b)); }
    const ht = opts.headT ?? t;              // the clip's own time, for what the head does
    if (this.lead && ht != null && ht >= 0) {
      const i = Math.min(this.lead.lx.length - 1, Math.floor(ht / this.lead.dt));
      look = [look[0] + this.lead.lx[i], look[1] + this.lead.ly[i]];
      for (const b of this.lead.turnBlinks) { if (b > ht) break; blink = Math.max(blink, blinkCurve(ht - b)); }
    }
    const lim = (p.rs * 22) - p.ir * 0.7; look[0] = Math.max(-lim, Math.min(lim, look[0])); look[1] = Math.max(-8, Math.min(8, look[1]));
    p.look = look; p.blink = blink * (1 - p.happy);
    // speech over the expression's mouth
    if (this.speech && t >= this.talkFrom && t < (this.talkTo ?? Infinity)) {
      const S = this.speech, i = Math.floor((t - this.talkFrom) / S.dt) % S.n, o = S.out;
      const k = 0.9, m = p.mouth;
      m.o = lerp(m.o * 0.6, Math.max(0, o[i * 4]) + m.o * 0.25, k); m.w = m.w + o[i * 4 + 1] * k; m.r = Math.max(m.r * 0.5, o[i * 4 + 2]);
      m.tT = Math.max(m.tT * 0.5, o[i * 4 + 3]); m.b *= 0.4; m.tB *= 0.3;
    }
    p.jaw = Math.max(0, p.mouth.o) * (1 - 0.5 * p.mouth.r);
    return p;
  }
}
