// Вера's face over time, for the pen (head.js): the С18 sheet's expressions (head.py EXPR — numbers: lids, brows,
// mouth, jaw) mixed and changing smoothly, blinks, saccades, the gaze leading head turns, speech. The timing is Р1's
// (to3d/r1-s3-anya/tools/web/face.js, through Р12: log-normal blink intervals and fixations, saccade durations by
// amplitude, critically damped changes; all from a seeded stream, so a moment always looks the same).
import { EXPR } from './head.js';
export const EXPR_NAMES = ['rest', 'joy', 'surprise', 'sadness', 'anger'];
const KEYS = ['open', 'squint', 'brow_in', 'brow_out', 'knit', 'smile', 'mopen', 'mwide', 'frown', 'jaw', 'smirk', 'small'];

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
// speech mouth shapes: open, wide, jaw
const VIS = { M: [0, 0, 0], F: [0.12, 0.1, 0.05], E: [0.3, 0.5, 0.15], A: [0.65, 0.1, 0.45], O: [0.5, -0.7, 0.35], U: [0.28, -0.9, 0.2] };

export class LiveFace {
  constructor(rest, seed = 7) {
    this.seed = seed;
    // every expression as the full set of numbers over the character's rest
    this.E = {}; for (const n of EXPR_NAMES) this.E[n] = { ...EXPR.rest, ...rest, ...(n === 'rest' ? {} : EXPR[n]) };
    const R = rng(seed);
    this.blinks = []; for (let t = 0.6 + R() * 1.5; t < 600;) { this.blinks.push(t); if (R() < 0.12) this.blinks.push(t + 0.24 + R() * 0.1); t += Math.max(0.9, lognorm(R, 2.8, 0.55)); }
    this.fix = []; let p = [0, 0];
    for (let t = 0.3; t < 600;) {
      const big = R() < 0.25, q = [gauss(R) * (big ? 0.5 : 0.22), gauss(R) * (big ? 0.35 : 0.15)];
      q[0] = Math.max(-0.8, Math.min(0.8, q[0])); q[1] = Math.max(-0.6, Math.min(0.6, q[1]));
      const amp = Math.hypot(q[0] - p[0], q[1] - p[1]) * 20;
      this.fix.push({ t, from: p, to: q, dur: (22 + 2.7 * amp) / 1000 }); p = q; t += Math.max(0.18, lognorm(R, 0.55, 0.5));
    }
    this.exprKeys = [{ t: -10, w: { rest: 1 } }];
    this.talkFrom = null; this.speech = null; this.lead = null; this.still = false;
  }
  setExpr(t, w) { this.exprKeys = this.exprKeys.filter(k => k.t < t); this.exprKeys.push({ t, w }); }
  exprWeights(t, rate = 12) {
    const cur = {}, k0 = this.exprKeys[0];
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
      // the picture's right is the character's left: a turn to her left moves the iris to +x of the head
      const tg = [Math.max(-1, Math.min(1, (yaw[j] - yaw[i]) * 2.5)), Math.max(-0.7, Math.min(0.7, -(pitch[j] - pitch[i]) * 2))];
      const t = i * dt;
      if (sac && t >= sac.t + sac.dur) { cur = sac.to; sac = null; }
      if (!sac && Math.hypot(tg[0] - cur[0], tg[1] - cur[1]) > 0.28) {
        const amp = Math.hypot(tg[0] - cur[0], tg[1] - cur[1]) * 20;
        sac = { t, from: cur, to: tg, dur: (22 + 2.7 * amp) / 1000 };
        if (Math.abs(tg[0] - cur[0]) > 0.45 && R() < 0.65) turnBlinks.push(t + 0.02);
      }
      if (sac) { const u = Math.min(1, (t - sac.t) / sac.dur), e = 1 - Math.pow(1 - u, 2.5); lx[i] = lerp(sac.from[0], sac.to[0], e); ly[i] = lerp(sac.from[1], sac.to[1], e); }
      else { const rate = 4 * dt; cur = [cur[0] + Math.max(-rate, Math.min(rate, tg[0] - cur[0])), cur[1] + Math.max(-rate, Math.min(rate, tg[1] - cur[1]))]; lx[i] = cur[0]; ly[i] = cur[1]; }
    }
    this.lead = { dt, lx, ly, turnBlinks };
  }
  // the face's numbers at time t (head.js Head.setExpr takes them)
  at(t, opts = {}) {
    const w = this.exprWeights(t), wb = this.exprWeights(t, 16), E = this.E;
    const mix = (k, ww) => { let s = 0, z = 0; for (const n of EXPR_NAMES) { s += ww[n] * (E[n][k] ?? 0); z += ww[n]; } return s / (z || 1); };
    const e = {};
    for (const k of KEYS) e[k] = mix(k, k.startsWith('brow') || k === 'knit' ? wb : w);      // the brows go first
    let base = [0, 0], z = 0; for (const n of EXPR_NAMES) { base[0] += w[n] * E[n].look[0]; base[1] += w[n] * E[n].look[1]; z += w[n]; }
    base = [base[0] / (z || 1), base[1] / (z || 1)];
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
    look = [Math.max(-1.1, Math.min(1.1, look[0])), Math.max(-0.8, Math.min(0.9, look[1]))];
    if (this.still) { look = base; blink = 0; }
    e.look = look;
    e.open = e.open * (1 - blink);
    if (this.speech && t >= this.talkFrom && t < (this.talkTo ?? Infinity)) {
      const S = this.speech, i = Math.floor((t - this.talkFrom) / S.dt) % S.n, o = S.out;
      e.mopen = Math.max(e.mopen, Math.max(0, o[i * 3]) * 0.75); e.mwide += o[i * 3 + 1] * 0.5; e.jaw = Math.max(e.jaw, Math.max(0, o[i * 3 + 2]));
    }
    return e;
  }
}
