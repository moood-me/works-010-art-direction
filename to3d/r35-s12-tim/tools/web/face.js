// The face over time (Р12's, to3d/r12-s12-anya; the expression sheet is the character's, from char.js), for the pen (anya.js drawFace): the С12 sheet's expressions (parts.py EXPR) mixed and changing
// smoothly, blinks, saccades, the gaze leading head turns, speech. The timing is Р1's (to3d/r1-s3-anya/tools/web/face.js,
// from how faces move: log-normal blink intervals and fixations, saccade durations by amplitude, critically damped
// changes); what it drives here is the drawing's own numbers: brows' lift and tilt, the lid, the pupil's look, the eye's
// size, the mouth's kind, the head's tilt with the feeling, the small marks (a tear, start-lines, a flush).
let EXPR = null, EXPR_NAMES = null;      // the character's sheet (char.js): its expressions as numbers, the first its rest

function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const gauss = R => Math.sqrt(-2 * Math.log(R() + 1e-12)) * Math.cos(2 * Math.PI * R());
const lognorm = (R, median, sigma) => median * Math.exp(sigma * gauss(R));
const lerp = (a, b, t) => a + (b - a) * t;
const settle = (x0, x1, tau, w) => tau <= 0 ? x0 : x1 + (x0 - x1) * (1 + w * tau) * Math.exp(-w * tau);
function blinkCurve(s) {
  if (s < 0) return 0;
  if (s < 0.07) { const u = s / 0.07; return u * u; }
  if (s < 0.10) return 1;
  if (s < 0.25) { const u = (s - 0.10) / 0.15; return (1 - u) * (1 - u); }
  return 0;
}
// speech mouth shapes: open, width change, round
const VIS = { M: [0, -1, 0], F: [0.15, 0, 0], E: [0.35, 3, 0], A: [0.7, 1, 0], O: [0.55, -5, 0.8], U: [0.3, -6, 1] };

export class LiveFace {
  constructor(seed = 7, expr, names) {
    this.seed = seed; EXPR = expr; EXPR_NAMES = names;
    const R = rng(seed);
    this.blinks = []; for (let t = 0.6 + R() * 1.5; t < 600;) { this.blinks.push(t); if (R() < 0.12) this.blinks.push(t + 0.24 + R() * 0.1); t += Math.max(0.9, lognorm(R, 2.8, 0.55)); }
    this.fix = []; let p = [0, 0];
    for (let t = 0.3; t < 600;) {
      const big = R() < 0.25, q = [gauss(R) * (big ? 0.9 : 0.45), gauss(R) * (big ? 0.6 : 0.3)];
      q[0] = Math.max(-1.3, Math.min(1.3, q[0])); q[1] = Math.max(-1, Math.min(1, q[1]));
      const amp = Math.hypot(q[0] - p[0], q[1] - p[1]) * 12;
      this.fix.push({ t, from: p, to: q, dur: (22 + 2.7 * amp) / 1000 }); p = q; t += Math.max(0.18, lognorm(R, 0.55, 0.5));
    }
    this.exprKeys = [{ t: -10, w: { [names[0]]: 1 } }];
    this.talkFrom = null; this.speech = null; this.lead = null; this.still = false;
  }
  setExpr(t, w) { this.exprKeys = this.exprKeys.filter(k => k.t < t); this.exprKeys.push({ t, w }); }
  exprWeights(t, rate = 12) {
    const cur = {}; const k0 = this.exprKeys[0];
    for (const n of EXPR_NAMES) cur[n] = k0.w[n] || 0;
    for (let i = 1; i < this.exprKeys.length; i++) {
      const k = this.exprKeys[i]; if (k.t > t) break;
      const next = this.exprKeys[i + 1], until = next && next.t <= t ? next.t : t, start = { ...cur };
      for (const n of EXPR_NAMES) cur[n] = settle(start[n], k.w[n] || 0, until - k.t, rate);
    }
    return cur;
  }
  talk(t0, seed = 3) {
    if (t0 == null) { this.talkFrom = null; this.speech = null; return; }
    const R = rng(seed), seq = []; let t = t0 + 0.15;
    const cons = ['M', 'F', 'E', 'M', 'E'], vow = ['A', 'E', 'O', 'A', 'U', 'E', 'A', 'O'];
    while (t < t0 + 600) {
      const words = 3 + Math.floor(R() * 6);
      for (let w = 0; w < words; w++) {
        const syl = 1 + Math.floor(R() * 3);
        for (let s = 0; s < syl; s++) {
          if (R() < 0.75) { seq.push({ t, v: cons[Math.floor(R() * cons.length)] }); t += 0.06 + R() * 0.04; }
          seq.push({ t, v: vow[Math.floor(R() * vow.length)] }); t += 0.11 + R() * 0.1;
        }
        seq.push({ t, v: 'M' }); t += 0.05 + R() * 0.09;
      }
      seq.push({ t, v: 'M' }); t += 0.35 + R() * 0.6;
    }
    const dt = 1 / 200, n = Math.ceil((seq[seq.length - 1].t - t0) / dt), out = new Float32Array(n * 3);
    let k = 0; const x = [0, 0, 0], v = [0, 0, 0], W = 34;
    for (let i = 0; i < n; i++) {
      const tt = t0 + i * dt; while (k + 1 < seq.length && seq[k + 1].t <= tt) k++;
      const tg = VIS[seq[k].v];
      for (let c = 0; c < 3; c++) { const acc = W * W * (tg[c] - x[c]) - 2 * W * v[c]; v[c] += acc * dt; x[c] += v[c] * dt; out[i * 3 + c] = x[c]; }
    }
    this.talkFrom = t0; this.speech = { dt, n, out };
  }
  setHead(track) {
    this.lead = null; if (!track) return;
    const { dt, yaw, pitch } = track, n = yaw.length, ahead = Math.round(0.25 / dt), R = rng(this.seed + 11);
    const lx = new Float32Array(n), ly = new Float32Array(n), turnBlinks = [];
    let cur = [0, 0], sac = null;
    for (let i = 0; i < n; i++) {
      const j = Math.min(n - 1, i + ahead);
      // pupil units: about ±1.5 to the eye's side
      const tg = [Math.max(-1.6, Math.min(1.6, -(yaw[j] - yaw[i]) * 4)), Math.max(-1, Math.min(1, -(pitch[j] - pitch[i]) * 3))];
      const t = i * dt;
      if (sac && t >= sac.t + sac.dur) { cur = sac.to; sac = null; }
      if (!sac && Math.hypot(tg[0] - cur[0], tg[1] - cur[1]) > 0.45) {
        const amp = Math.hypot(tg[0] - cur[0], tg[1] - cur[1]) * 12;
        sac = { t, from: cur, to: tg, dur: (22 + 2.7 * amp) / 1000 };
        if (Math.abs(tg[0] - cur[0]) > 0.7 && R() < 0.65) turnBlinks.push(t + 0.02);
      }
      if (sac) { const u = Math.min(1, (t - sac.t) / sac.dur), e = 1 - Math.pow(1 - u, 2.5); lx[i] = lerp(sac.from[0], sac.to[0], e); ly[i] = lerp(sac.from[1], sac.to[1], e); }
      else { const rate = 7 * dt; cur = [cur[0] + Math.max(-rate, Math.min(rate, tg[0] - cur[0])), cur[1] + Math.max(-rate, Math.min(rate, tg[1] - cur[1]))]; lx[i] = cur[0]; ly[i] = cur[1]; }
    }
    this.lead = { dt, lx, ly, turnBlinks };
  }
  at(t, opts = {}) {
    const w = this.exprWeights(t), wb = this.exprWeights(t, 16);
    const mix = (get, ww = w) => { let s = 0, z = 0; for (const n of EXPR_NAMES) { s += ww[n] * get(EXPR[n]); z += ww[n]; } return s / (z || 1); };
    let dom = EXPR_NAMES[0]; for (const n of EXPR_NAMES) if (w[n] > w[dom]) dom = n;
    const E = EXPR[dom];
    const p = {
      lift: mix(e => e.lift, wb), tilt: mix(e => e.tilt, wb), lid: mix(e => e.lid), eye: mix(e => e.eye),
      ms: mix(e => e.ms ?? 1), tiltHead: mix(e => e.tilt_head ?? 0), squint: mix(e => e.squint ? 1 : 0) > 0.5,
      mouth: E.mouth, dom, w, extra: E.extra, extraK: w[dom] / (EXPR_NAMES.reduce((s, n) => s + w[n], 0) || 1), flush: 0,
    };
    if (E.extra === 'flush') p.extra = null;
    p.flush = (w.anger || 0) / (EXPR_NAMES.reduce((s, n) => s + w[n], 0) || 1);
    const base = [mix(e => e.look[0]), mix(e => e.look[1])];
    let lo = 0, hi = this.fix.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (this.fix[m].t <= t) lo = m; else hi = m - 1; }
    const f = this.fix[lo], u = Math.min(1, Math.max(0, (t - f.t) / f.dur)), ee = 1 - Math.pow(1 - u, 2.5);
    let look = [base[0] + lerp(f.from[0], f.to[0], ee), base[1] + lerp(f.from[1], f.to[1], ee)];
    let blink = 0;
    for (const b of this.blinks) { if (b > t) break; blink = Math.max(blink, blinkCurve(t - b)); }
    const ht = opts.headT ?? t;
    if (this.lead && ht != null && ht >= 0) {
      const i = Math.min(this.lead.lx.length - 1, Math.floor(ht / this.lead.dt));
      look = [look[0] + this.lead.lx[i], look[1] + this.lead.ly[i]];
      for (const b of this.lead.turnBlinks) { if (b > ht) break; blink = Math.max(blink, blinkCurve(ht - b)); }
    }
    look = [Math.max(-1.8, Math.min(1.8, look[0])), Math.max(-1.4, Math.min(1.8, look[1]))];
    if (this.still) { look = base; blink = 0; }
    p.look = look;
    p.lid = Math.min(1, p.lid + (1 - p.lid) * blink * (p.squint ? 0 : 1));
    if (this.speech && t >= this.talkFrom && t < (this.talkTo ?? Infinity)) {
      const S = this.speech, i = Math.floor((t - this.talkFrom) / S.dt) % S.n, o = S.out;
      p.talk = true; p.open = Math.max(0, o[i * 3]); p.dw = o[i * 3 + 1]; p.round = Math.max(0, Math.min(1, o[i * 3 + 2]));
    }
    return p;
  }
}
