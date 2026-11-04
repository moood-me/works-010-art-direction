// The face alive: a function of time made from seeded schedules (a moment always looks the same, so films repeat and
// the viewer can scrub). Timings after how real faces move, not sines:
//   blinks — log-normal intervals (median 2.8 s, 0.5…8 s), 12 % double; closing 70 ms (accelerating), shut 30 ms,
//     opening 150 ms (slowing); a big gaze jump brings one;
//   gaze — fixations log-normal (median 0.6 s), a jump of 25 ms + 2.5 ms per degree to a nearby point; before a head
//     turn the eyes go first: they look where the head will be 0.25 s later (read off the motion) and come back as
//     the head follows;
//   speech — phrases of syllables (a consonant shape 60–110 ms, a vowel 100–200 ms), pauses 0.3–0.9 s; the mouth runs
//     from shape to shape over ~60 ms; the brows lift a little at a phrase's start;
//   expressions — keys {t, w: {name: weight}}; each change eases in over 0.35 s (the brows a little faster).
import { EXPRESSIONS, PARAMS, mixParams } from './face.js';

function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
const gauss = r => Math.sqrt(-2 * Math.log(r() + 1e-9)) * Math.cos(2 * Math.PI * r());
const lognorm = (r, med, sig, lo, hi) => Math.min(hi, Math.max(lo, med * Math.exp(sig * gauss(r))));
const ease = t => t <= 0 ? 0 : t >= 1 ? 1 : t * t * (3 - 2 * t);

const VIS = {   // mouth shapes of speech
  a: { jaw: 11, wide: 0.15 }, o: { jaw: 8, pucker: 0.6 }, u: { jaw: 3, pucker: 1.0 }, e: { jaw: 6, wide: 0.55, upper: 0.3 }, i: { jaw: 3, wide: 0.85, upper: 0.3 },
  m: { jaw: 0, pucker: 0.1 }, f: { jaw: 2, upper: 0.5 }, t: { jaw: 4, wide: 0.3 }, rest: {},
};
const VOW = ['a', 'a', 'o', 'e', 'i', 'u', 'a', 'e'], CON = ['m', 'f', 't', 't', 't', 'm'];

export class Life {
  constructor({ seed = 11, length = 120 } = {}) {
    const r = rng(seed);
    this.blinks = []; let t = 0.4 + r();
    while (t < length) { this.blinks.push(t); if (r() < 0.12) this.blinks.push(t + 0.32); t += lognorm(r, 2.8, 0.5, 0.5, 8); }
    this.fix = []; t = 0;
    while (t < length) { this.fix.push({ t, x: gauss(r) * 5, y: gauss(r) * 3 }); t += lognorm(r, 0.6, 0.45, 0.18, 2.0); }
    this.syl = []; t = 0;
    while (t < length) {
      const n = 3 + Math.floor(r() * 7), start = t;
      for (let i = 0; i < n; i++) {
        const c = CON[Math.floor(r() * CON.length)], dc = 0.06 + r() * 0.05; this.syl.push({ t, v: c }); t += dc;
        const v = VOW[Math.floor(r() * VOW.length)], dv = 0.1 + r() * 0.1; this.syl.push({ t, v }); t += dv;
      }
      this.syl.push({ t, v: 'rest', phrase: start }); t += 0.3 + r() * 0.6;
    }
  }
  blinkAt(t, extra) {
    let b = 0;
    for (const t0 of this.blinks.concat(extra)) {
      const d = t - t0; if (d < -0.01 || d > 0.3) continue;
      const v = d < 0.07 ? (d / 0.07) ** 2 : d < 0.1 ? 1 : 1 - ease((d - 0.1) / 0.15);
      b = Math.max(b, v);
    }
    return b;
  }
  gazeAt(t) {
    let i = 0; while (i + 1 < this.fix.length && this.fix[i + 1].t <= t) i++;
    const f = this.fix[i], p = i > 0 ? this.fix[i - 1] : f;
    const amp = Math.hypot(f.x - p.x, f.y - p.y), dur = 0.025 + 0.0025 * amp;
    const u = ease((t - f.t) / dur);
    return [p.x + (f.x - p.x) * u, p.y + (f.y - p.y) * u];
  }
  speechAt(t) {
    let i = 0; while (i + 1 < this.syl.length && this.syl[i + 1].t <= t) i++;
    const s = this.syl[i], pr = i > 0 ? this.syl[i - 1] : s, u = ease((t - s.t) / 0.06);
    const out = {}; for (const k of ['jaw', 'wide', 'pucker', 'upper']) out[k] = (VIS[pr.v][k] || 0) * (1 - u) + (VIS[s.v][k] || 0) * u;
    return out;
  }
  // o: {expr: [{t, w | name}], talk: [[t0, t1], …], track: {fps, yaw[], pitch[]} | null, still, look: [x, y] | null}
  at(t, o = {}) {
    // expressions
    const keys = (o.expr || [{ t: 0, w: { calm: 1 } }]).map(k => ({ t: k.t, w: k.w || { [k.name]: 1 } }));
    let p = mixParams(keys[0].w);
    for (let i = 1; i < keys.length; i++) {
      if (t < keys[i].t) break;
      const q = mixParams(keys[i].w), u = ease((t - keys[i].t) / 0.35), ub = ease((t - keys[i].t) / 0.25);
      for (const k of PARAMS) { const uu = ['brow', 'inner', 'outer', 'browR'].includes(k) ? ub : u; p[k] = p[k] + (q[k] - p[k]) * uu; }
    }
    p = { ...p };
    // speech
    const talking = (o.talk || []).some(([a, b]) => t >= a && t < b);
    if (talking) {
      const s = this.speechAt(t);
      p.jaw = Math.max(p.jaw * 0.5, 0) + s.jaw; p.wide += s.wide; p.pucker += s.pucker; p.upper = Math.max(p.upper, s.upper);
      const ph = this.syl.find(x => x.phrase !== undefined && x.phrase <= t && t < x.phrase + 0.6);
      if (ph) p.brow += 0.25 * Math.sin(Math.PI * Math.min(1, (t - ph.phrase) / 0.6));
    }
    if (o.still) return p;
    // gaze and its lead before head turns
    let [gx, gy] = o.look || this.gazeAt(t);
    const extra = [];
    if (o.track) {
      const { fps, yaw, pitch } = o.track, at = (A, s) => { const f = Math.max(0, Math.min(A.length - 1, s * fps)), i = Math.floor(f), u = f - i; return A[i] * (1 - u) + A[Math.min(i + 1, A.length - 1)] * u; };
      const dy = (at(yaw, t + 0.25) - at(yaw, t)) * 180 / Math.PI, dp = (at(pitch, t + 0.25) - at(pitch, t)) * 180 / Math.PI;
      gx += Math.max(-25, Math.min(25, dy)); gy += Math.max(-15, Math.min(15, -dp));
      // a fast head turn takes a blink
      for (let s = Math.max(0, t - 0.3); s <= t; s += 1 / fps) { const v = Math.abs(at(yaw, s + 1 / fps) - at(yaw, s)) * fps; if (v > 2.2) { extra.push(s); break; } }
    }
    p.lookX += gx; p.lookY += gy;
    p.blink = Math.max(p.blink || 0, this.blinkAt(t, extra));
    return p;
  }
}
