// Small life on Марат's face over a clip's time (face.mjs states): blinks, the eyes' jumps and a gaze that leads the
// head, speech, expressions going one into another. Made once for the whole clip at 120 Hz from a seeded random
// stream, so a moment always looks the same (films, scrubbing). Timing from how faces move (after Р2/Р3/Р4):
//  - blinks: log-normal intervals (median ~2.8 s, at least 0.8 s apart), 12 % doubled; closing ~75 ms, held ~25 ms,
//    opening ~160 ms; a big gaze shift brings a blink;
//  - gaze: the eyes hold, then jump (fixations 0.3–1.6 s; a jump 20 ms + 2.2 ms per degree, eased); when the head
//    is about to turn (read 0.25 s ahead in the clip) the eyes jump first to where it goes and turn back in the
//    head as it follows;
//  - speech: phrases of syllables — a consonant shape then a vowel shape, 60–110 ms and 100–200 ms — with pauses;
//    the weights follow by a fast critically damped spring, so the shapes run into each other; the brows lift a
//    little at a phrase's start;
//  - expressions: targets at given times, followed by a slower spring.

export const HZ = 120;
export const FACES = ['calm', 'beam', 'laugh', 'surprise', 'sad', 'anger'];
export const VIS = ['A', 'O', 'U', 'E', 'I', 'M', 'F'];

function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return (s >>> 0) / 4294967296; }; }
const lerp = (a, b, t) => a + (b - a) * t;
const ease = t => t * t * (3 - 2 * t);
const gauss = R => Math.sqrt(-2 * Math.log(R() + 1e-9)) * Math.cos(2 * Math.PI * R());

function follow(target, omega, x0 = target[0]) {
  const out = new Float32Array(target.length), dt = 1 / HZ;
  let x = x0, v = 0;
  for (let i = 0; i < target.length; i++) { const a = omega * omega * (target[i] - x) - 2 * omega * v; v += a * dt; x += v * dt; out[i] = x; }
  return out;
}

// head(t) → {yaw, pitch} degrees (the head's facing in the world); opts: {seconds, seed, talk, talkFrom, talkTo,
// expr: {joy: 1} | [[t, {joy: 1}], …], still: no blinks or saccades (pictures)}
export function lifeTrack(head, opts) {
  const T = opts.seconds, n = Math.ceil(T * HZ) + 1, R = rng(opts.seed ?? 7);
  const tr = { blink: new Float32Array(n), gy: new Float32Array(n), gp: new Float32Array(n), sp: new Float32Array(n), brow: new Float32Array(n) };
  for (const k of FACES) tr['e' + k] = new Float32Array(n);
  for (const k of VIS) tr['v' + k] = new Float32Array(n);
  // expressions
  const ex = Array.isArray(opts.expr) ? opts.expr : [[0, opts.expr || { calm: 1 }]];
  for (const k of FACES) {
    const tg = new Float32Array(n);
    for (let i = 0, e = 0; i < n; i++) { const t = i / HZ; while (e + 1 < ex.length && ex[e + 1][0] <= t) e++; tg[i] = ex[e][1][k] || 0; }
    tr['e' + k] = follow(tg, 8.5);
  }
  if (!opts.still) {
    // gaze
    const shifts = []; let gy = 0, gp = 0, jump = null, nextFix = 0.3 + R() * 1.2;
    for (let i = 0; i < n; i++) {
      const t = i / HZ, h = head(t);
      if (!jump || t > jump.t0 + jump.dur) {
        const ah = head(Math.min(T, t + 0.25));
        const worldNow = gy + h.yaw;
        let to = null;
        if (Math.abs(ah.yaw - worldNow) > 9) to = [ah.yaw - h.yaw + (R() - 0.5) * 3, (R() - 0.5) * 3];
        else if (t >= nextFix) {
          to = [Math.max(-14, Math.min(14, gy * 0.5 + (R() - 0.5) * 9)), Math.max(-8, Math.min(8, gp * 0.4 + (R() - 0.5) * 6))];
          nextFix = t + Math.min(1.6, Math.max(0.3, Math.exp(Math.log(0.6) + 0.5 * gauss(R))));
        }
        if (to) {
          to[0] = Math.max(-28, Math.min(28, to[0]));
          const amp = Math.hypot(to[0] - gy, to[1] - gp);
          jump = { t0: t, dur: 0.02 + 0.0022 * amp, from: [gy, gp], to };
          if (amp > 14) shifts.push(t);
        }
      }
      if (jump) {
        const u = Math.min(1, (t - jump.t0) / jump.dur), e = ease(u);
        gy = lerp(jump.from[0], jump.to[0], e); gp = lerp(jump.from[1], jump.to[1], e);
      }
      // while the head turns between jumps, the eyes stay on their target in the world (they turn back in the head)
      if (jump && t > jump.t0 + jump.dur && i > 0) {
        const dh = h.yaw - head((i - 1) / HZ).yaw;
        gy = Math.max(-28, Math.min(28, gy - dh));
        jump.to = [gy, gp];
      }
      tr.gy[i] = gy; tr.gp[i] = gp;
    }
    // blinks
    const blinks = [];
    for (let b = 0.4 + R() * 2; b < T;) {
      blinks.push(b);
      if (R() < 0.12) blinks.push(b + 0.32 + R() * 0.1);
      b += Math.max(0.8, Math.exp(Math.log(2.8) + 0.45 * gauss(R)));
    }
    for (const ts of shifts) if (!blinks.some(b => Math.abs(b - ts) < 0.6)) blinks.push(ts);
    blinks.sort((a, b) => a - b);
    for (const b0 of blinks) {
      const close = 0.075, hold = 0.025, open = 0.16;
      for (let i = Math.floor(b0 * HZ); i < Math.min(n, (b0 + close + hold + open) * HZ); i++) {
        const s = i / HZ - b0;
        const k = s < close ? ease(s / close) : s < close + hold ? 1 : 1 - ease((s - close - hold) / open);
        tr.blink[i] = Math.max(tr.blink[i], k);
      }
    }
    tr.blinks = blinks;
  }
  if (opts.talk) {
    const from = opts.talkFrom ?? 0, to = opts.talkTo ?? T;
    const tg = {}; for (const k of VIS) tg[k] = new Float32Array(n);
    const spT = new Float32Array(n), brow = new Float32Array(n);
    const vowels = ['A', 'O', 'U', 'E', 'I', 'A', 'E', 'O'], cons = ['M', 'F', 'E', 'I', 'U'];
    let s = from + 0.2 + R() * 0.3;
    while (s < to - 0.3) {
      const syl = 3 + Math.floor(R() * 6);
      for (let i = Math.floor(s * HZ); i < Math.min(n, (s + 0.45) * HZ); i++) brow[i] = 1;
      for (let k = 0; k < syl && s < to - 0.2; k++) {
        const dc = 0.06 + R() * 0.05, dv = 0.1 + R() * 0.1;
        const c = cons[Math.floor(R() * cons.length)], v = vowels[Math.floor(R() * vowels.length)];
        for (let i = Math.floor(s * HZ); i < Math.min(n, (s + dc + dv) * HZ); i++) {
          spT[i] = 1; tg[(i / HZ < s + dc) ? c : v][i] = 1;
        }
        s += dc + dv;
      }
      s += 0.3 + R() * 0.7;
    }
    for (const k of VIS) tr['v' + k] = follow(tg[k], 34);
    tr.sp = follow(spT, 14);
    tr.brow = follow(brow, 10);
  }
  return {
    seconds: T, tr,
    at(time) {
      const x = Math.max(0, Math.min(n - 1, time * HZ)), i = Math.floor(x), f = x - i, j = Math.min(n - 1, i + 1);
      const g = k => tr[k][i] + (tr[k][j] - tr[k][i]) * f;
      const e = {}, v = {};
      for (const k of FACES) e[k] = Math.max(0, g('e' + k));
      for (const k of VIS) v[k] = Math.max(0, g('v' + k));
      return { e, v, sp: Math.min(1, Math.max(0, g('sp'))), blink: g('blink'), gaze: [g('gy'), g('gp')], brow: g('brow') };
    },
  };
}

export function headFacing(pose, hi, qRot) {
  const q = [pose.Q[hi * 4], pose.Q[hi * 4 + 1], pose.Q[hi * 4 + 2], pose.Q[hi * 4 + 3]];
  const f = qRot(q, [0, 0, 1]);
  return { yaw: Math.atan2(f[0], f[2]) * 180 / Math.PI, pitch: -Math.asin(Math.max(-1, Math.min(1, f[1]))) * 180 / Math.PI };
}
