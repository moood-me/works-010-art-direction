// After Р2's life.mjs and Р7's life.js (to3d/r2-s10-savely, r7-s4-vera), for Вера's drawn face (face.js: the track
// is of the drawing's own numbers — lid opening, iris place, mouth opening and width, brows). Small life on the face, as a track of face params over a clip's time (face.mjs): blinks, the eyes' jumps and a gaze
// that leads the head, speech, and expressions going one into another. Computed once for the whole clip at 120 Hz
// (so scrubbing back and forth gives the same face), deterministic from a seed.
//
// Timing from how faces move, not from sines:
//  - blinks come at uneven intervals (log-normal, ~3 s apart, never closer than 0.8 s), close fast (~75 ms) and
//    open slower (~170 ms); a large gaze shift brings a blink with it, as it does in people;
//  - the eyes hold still and jump (saccades): small fixational jumps every 0.3–1.6 s; a jump's time grows with its
//    size (~20 ms + 2.2 ms per degree); when the head is about to turn, the eyes jump first to where it is going
//    and then turn back in the head as the head catches up (the vestibulo-ocular reflex), so the gaze leads;
//  - speech: phrases of syllables (~4–6 per second) with pauses; each syllable a consonant then a vowel shape
//    (jaw, wide, pucker), joined by a fast critically damped follow (the shapes run into each other); brows lift a
//    little at phrase starts;
//  - expressions: the targets change at given times and the face follows with a slower critically damped spring.
import { mix, PARAMS } from './face.js';

const HZ = 120;
const LOOK = 0.11;               // head units of iris travel per degree of gaze

function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return (s >>> 0) / 4294967296; }; }
const lerp = (a, b, t) => a + (b - a) * t;
const ease = t => t * t * (3 - 2 * t);

// critically damped follow of a target track (one value per step)
function follow(target, omega, x0 = target[0]) {
  const out = new Float32Array(target.length), dt = 1 / HZ;
  let x = x0, v = 0;
  for (let i = 0; i < target.length; i++) {
    const a = omega * omega * (target[i] - x) - 2 * omega * v;
    v += a * dt; x += v * dt; out[i] = x;
  }
  return out;
}

// head: (t seconds) → {yaw, pitch} in degrees (the head's facing in the world; yaw + toward the person's left)
// opts: {seconds, seed, talk, expr: [[t, {joy: 1}], …] or {joy: 1}, talkFrom, talkTo}
export function lifeTrack(head, opts) {
  const T = opts.seconds, n = Math.ceil(T * HZ) + 1, R = rng(opts.seed ?? 7);
  const tr = {}; for (const k of PARAMS) tr[k] = new Float32Array(n);

  // expressions
  const ex = Array.isArray(opts.expr) ? opts.expr : [[0, opts.expr || { calm: 1 }]];
  const tgt = {}; for (const k of PARAMS) tgt[k] = new Float32Array(n);
  for (let i = 0, e = 0; i < n; i++) {
    const t = i / HZ;
    while (e + 1 < ex.length && ex[e + 1][0] <= t) e++;
    const m = mix(ex[e][1]);
    for (const k of PARAMS) tgt[k][i] = m[k];
  }
  for (const k of PARAMS) tr[k] = follow(tgt[k], 9);

  // gaze and saccades
  const gaze = { yaw: new Float32Array(n), pitch: new Float32Array(n) };
  const shifts = [];          // [t, amplitude]
  let gy = head(0).yaw, gp = 0, t = 0;
  const jumpsTo = [];
  let nextFix = 0.3 + R() * 1.2;
  let jump = null;          // {t0, dur, from: [y, p], to: [y, p]}
  for (let i = 0; i < n; i++) {
    t = i / HZ;
    if (!jump || t > jump.t0 + jump.dur) {
      const ahead = head(Math.min(T, t + 0.22));
      let to = null;
      if (Math.abs(ahead.yaw - gy) > 9) to = [ahead.yaw + (R() - 0.5) * 3, (R() - 0.5) * 3];           // lead the head
      else if (t >= nextFix) { to = [gy + (R() - 0.5) * 6, gp * 0.4 + (R() - 0.5) * 4]; nextFix = t + 0.3 + R() * 1.3; }
      if (to) {
        const amp = Math.hypot(to[0] - gy, to[1] - gp);
        jump = { t0: t, dur: 0.02 + 0.0022 * amp, from: [gy, gp], to };
        if (amp > 14) shifts.push([t, amp]);
      }
    }
    if (jump) {
      const u = Math.min(1, (t - jump.t0) / jump.dur), e = ease(u);
      gy = lerp(jump.from[0], jump.to[0], e); gp = lerp(jump.from[1], jump.to[1], e);
      if (u >= 1) { gy = jump.to[0]; gp = jump.to[1]; }
    }
    gaze.yaw[i] = gy; gaze.pitch[i] = gp;
    const h = head(t);
    // on the sheet the iris goes toward −x when she looks to her left (+ yaw): face.js draws in her own x
    tr.lookX[i] += Math.max(-24, Math.min(24, gy - h.yaw)) * LOOK;
    tr.lookY[i] += Math.max(-15, Math.min(15, gp - 0.5 * h.pitch)) * LOOK;
  }

  // blinks: uneven intervals, and with large gaze shifts
  const blinks = [];
  for (let b = 0.4 + R() * 2; b < T; ) {
    blinks.push(b);
    const ln = Math.exp(Math.log(2.8) + 0.45 * Math.sqrt(-2 * Math.log(R() + 1e-9)) * Math.cos(2 * Math.PI * R()));
    b += Math.max(0.8, ln);
  }
  for (const [ts] of shifts) if (!blinks.some(b => Math.abs(b - ts) < 0.6)) blinks.push(ts);
  blinks.sort((a, b) => a - b);
  for (const b0 of blinks) {
    const close = 0.075, hold = 0.025, open = 0.17;
    for (let i = Math.floor(b0 * HZ); i < Math.min(n, (b0 + close + hold + open) * HZ); i++) {
      const s = i / HZ - b0;
      const k = s < close ? ease(s / close) : s < close + hold ? 1 : 1 - ease((s - close - hold) / open);
      tr.blink[i] = Math.max(tr.blink[i], k);
    }
  }

  // speech
  if (opts.talk) {
    const from = opts.talkFrom ?? 0, to = opts.talkTo ?? T;
    const jaw = new Float32Array(n), wide = new Float32Array(n), puck = new Float32Array(n), brow = new Float32Array(n);
    const V = [{ jaw: 10, wide: 0.15 }, { jaw: 7, pucker: 0.9 }, { jaw: 3.5, pucker: 1.1 }, { jaw: 6, wide: 0.6 }, { jaw: 3.5, wide: 1.0 }];
    const Cn = [{ jaw: 0, pucker: 0.15 }, { jaw: 2, wide: 0.2 }, { jaw: 3, wide: 0.0 }, { jaw: 1, pucker: 0.4 }];
    let s = from + 0.2 + R() * 0.3;
    while (s < to - 0.3) {
      const phrase = 1.0 + R() * 1.8, end = Math.min(to - 0.2, s + phrase);
      for (let i = Math.floor(s * HZ); i < Math.min(n, (s + 0.45) * HZ); i++) brow[i] = 1.4;
      while (s < end) {
        const dur = 0.13 + R() * 0.14, c = Cn[Math.floor(R() * Cn.length)], v = V[Math.floor(R() * V.length)];
        const split = s + dur * 0.35;
        for (let i = Math.floor(s * HZ); i < Math.min(n, (s + dur) * HZ); i++) {
          const sh = i / HZ < split ? c : v;
          jaw[i] = sh.jaw || 0; wide[i] = sh.wide || 0; puck[i] = sh.pucker || 0;
        }
        s += dur;
      }
      s += 0.35 + R() * 0.55;
    }
    const J = follow(jaw, 30), W = follow(wide, 26), P = follow(puck, 26), B = follow(brow, 10);
    for (let i = 0; i < n; i++) { tr.jaw[i] += J[i] * 0.045; tr.swide[i] += W[i]; tr.pucker[i] += P[i]; tr.brow[i] += B[i]; }
  }

  return {
    seconds: T, track: tr, blinks,
    at(time) {
      const x = Math.max(0, Math.min(n - 1, time * HZ)), i = Math.floor(x), f = x - i, j = Math.min(n - 1, i + 1), out = {};
      for (const k of PARAMS) out[k] = tr[k][i] + (tr[k][j] - tr[k][i]) * f;
      return out;
    },
  };
}

// the head's facing from a pose (engine: Q world turns from rest; the rest faces +z): yaw + toward +x (his left)
export function headFacing(pose, headIndex, qRot) {
  const q = [pose.Q[headIndex * 4], pose.Q[headIndex * 4 + 1], pose.Q[headIndex * 4 + 2], pose.Q[headIndex * 4 + 3]];
  const f = qRot(q, [0, 0, 1]);
  return { yaw: Math.atan2(f[0], f[2]) * 180 / Math.PI, pitch: -Math.asin(Math.max(-1, Math.min(1, f[1]))) * 180 / Math.PI };
}
