// Вера's face alive: the drawn signs of face.js moved by timing taken from how people's eyes and faces move, not by
// waves. Everything is events at uneven, random-but-seeded times, and fast or slow approaches to them:
// - blinks: spontaneous ones every ~3 s (spread wide: from a third of a second to eight), sometimes two in a row,
//   sometimes not quite closed; each shuts fast (≈80 ms, speeding up), stays shut ≈40 ms, opens slower (≈150 ms,
//   slowing down); a big gaze shift (a head turn) and the end of a spoken sentence bring a blink with them;
// - gaze: the eyes rest on a point (fixations of ~0.2–1.5 s) and jump to the next one in one or two frames (a saccade);
//   when the head is about to turn, the eyes jump first to where it is going and then, while the head follows, turn
//   back against it so that they keep looking at the same place; the upper lid follows the eye down and up;
// - expressions: each number of the face goes to the new expression by a critically damped spring (no overshoot),
//   the mouth faster than the brows, a tear slowly; any mix of the sheet's expressions is a mix of their numbers;
// - speech: a Russian text read letter by letter into mouth shapes (vowels long, consonants short, lips shut on
//   м/б/п, teeth on в/ф), commas and full stops as pauses, the brows lifting a little at the start of a phrase.
import { EXPR, VISEME, exprVec, vecExpr, mixExpr, mouthVec } from './face.js';

function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

export const PHRASES = ['Так, внимание.', 'Тетради сдаём на край стола.', 'Кто не успел — принесёт завтра, до урока.', 'Вопросы есть?', 'Нет? Хорошо.'];
const VOWEL = { а: 'A', я: 'A', о: 'O', ё: 'O', у: 'U', ю: 'U', е: 'E', э: 'E', и: 'I', ы: 'I' };
const CONS = { м: 'M', б: 'M', п: 'M', в: 'F', ф: 'F' };

export class FaceLive {
  constructor(seed = 11) {
    this.r = rng(seed);
    this.n = exprVec(EXPR.neutral).length;
    this.x = exprVec(EXPR.neutral); this.v = this.x.map(() => 0);
    this.target = { neutral: 1 };
    this.t = 0;
    // blinks
    this.blinks = []; this.nextBlink = this.interval();
    // gaze, in degrees in the body's frame; eye = where the eyes point against the head
    this.G = [0, 0]; this.eye = [0, 0]; this.nextFix = this.fixation();
    // speech
    this.talk = false; this.talkAmt = 0; this.mouth = mouthVec(EXPR.neutral.mouth); this.mv = this.mouth.map(() => 0);
    this.seq = []; this.si = 0; this.sleft = 0; this.phrase = 0; this.browKick = 0;
  }
  gauss() { const u = Math.max(1e-9, this.r()), v = this.r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  lognorm(median, sigma, lo, hi) { return clamp(median * Math.exp(sigma * this.gauss()), lo, hi); }
  interval() { return this.lognorm(2.8, 0.6, 0.35, 8); }
  fixation() { return this.lognorm(0.55, 0.55, 0.18, 1.6); }
  blink(at, depth = 1) {
    if (this.blinks.some(b => Math.abs(b.at - at) < 0.25)) return;
    this.blinks.push({ at, close: 0.065 + 0.03 * this.r(), hold: 0.025 + 0.03 * this.r(), open: 0.12 + 0.07 * this.r(), depth });
  }
  blinkAmount() {
    let s = 0;
    for (const b of this.blinks) {
      const u = this.t - b.at;
      let k = 0;
      if (u < 0) k = 0;
      else if (u < b.close) k = (u / b.close) ** 2;                                   // speeding up as it shuts
      else if (u < b.close + b.hold) k = 1;
      else if (u < b.close + b.hold + b.open) { const w = (u - b.close - b.hold) / b.open; k = 1 - (1 - (1 - w) ** 2); } // slowing as it opens
      s = Math.max(s, k * b.depth);
    }
    return s;
  }
  setExpr(w) { this.target = typeof w === 'string' ? { [w]: 1 } : w; }
  setTalk(on) { this.talk = on; }
  // the next phrase as a list of [mouth shape or null (rest), seconds]
  readPhrase() {
    const txt = PHRASES[this.phrase++ % PHRASES.length].toLowerCase(), seq = [];
    let first = true;
    for (const ch of txt) {
      if (VOWEL[ch]) { seq.push([VOWEL[ch], 0.085 + 0.06 * this.r(), first]); first = false; }
      else if (CONS[ch]) seq.push([CONS[ch], 0.07 + 0.03 * this.r()]);
      else if (/[а-яё]/.test(ch)) seq.push(['C', 0.05 + 0.03 * this.r()]);
      else if (ch === ' ') seq.push(['C', 0.025]);
      else if (ch === ',' || ch === '—') seq.push([null, 0.22 + 0.1 * this.r()]);
      else if ('.?!'.includes(ch)) seq.push([null, 0.6 + 0.35 * this.r(), false, true]);
    }
    return seq;
  }
  // head: {yaw, pitch, aheadYaw, aheadPitch} in degrees — now, and where the head will be in ~0.3 s
  step(dt, head = { yaw: 0, pitch: 0, aheadYaw: 0, aheadPitch: 0 }) {
    const sub = Math.max(1, Math.ceil(dt / (1 / 240))), h = dt / sub;
    for (let k = 0; k < sub; k++) this.tick(h, head);
  }
  tick(dt, head) {
    this.t += dt;
    const t = this.t;
    // spontaneous blinks, now and then a second one right after, now and then a shallow one
    if (t >= this.nextBlink) {
      this.blink(t, this.r() < 0.12 ? 0.7 : 1);
      if (this.r() < 0.12) this.blink(t + 0.28 + 0.15 * this.r());
      this.nextBlink = t + this.interval();
    }
    this.blinks = this.blinks.filter(b => t - b.at < 1);
    // gaze: lead the head, or rest and jump to a near point
    const lead = [head.aheadYaw - this.G[0], head.aheadPitch - this.G[1]];
    const jump = to => {
      const amp = Math.hypot(to[0] - this.G[0], to[1] - this.G[1]);
      this.G = to; this.nextFix = t + this.fixation();
      if (amp > 16 && this.r() < clamp(0.35 + (amp - 16) / 25, 0, 0.95)) { this.blink(t + 0.01); this.nextBlink = Math.max(this.nextBlink, t + 0.8 * this.interval()); }
    };
    if (Math.abs(lead[0]) > 7 || Math.abs(lead[1]) > 6) jump([head.aheadYaw + 2 * this.gauss(), head.aheadPitch + 1.5 * this.gauss()]);
    else if (t >= this.nextFix) jump([head.aheadYaw + 4.5 * this.gauss(), head.aheadPitch + 2.5 * this.gauss() - 0.5]);
    // the eyes: against the head they point at G (turning back as the head turns: the vestibulo-ocular reflex),
    // reaching a new G within ~2 frames (a saccade)
    const want = [clamp(this.G[0] - head.yaw, -26, 26), clamp(this.G[1] - head.pitch, -14, 14)];
    const a = 1 - Math.exp(-dt / 0.016);
    this.eye[0] += (want[0] - this.eye[0]) * a; this.eye[1] += (want[1] - this.eye[1]) * a;
    // the expression's numbers: springs, the mouth faster, the tear slow
    const tgt = mixExpr(this.target);
    for (let i = 0; i < this.n; i++) {
      const w = i === 9 ? 5 : i >= 10 ? 24 : i >= 7 ? 16 : 19;
      this.v[i] += (w * w * (tgt[i] - this.x[i]) - 2 * w * this.v[i]) * dt; this.x[i] += this.v[i] * dt;
    }
    // speech
    this.talkAmt += ((this.talk || this.si < this.seq.length ? 1 : 0) - this.talkAmt) * (1 - Math.exp(-dt / 0.08));
    if (this.si >= this.seq.length && this.talk) { this.seq = this.readPhrase(); this.si = 0; this.sleft = this.seq[0][1]; if (this.seq[0][2]) this.browKick = 1; }
    let shape = null;
    if (this.si < this.seq.length) {
      const cur = this.seq[this.si]; shape = cur[0];
      this.sleft -= dt;
      if (this.sleft <= 0) {
        if (cur[3] && this.r() < 0.5) this.blink(t + 0.05 + 0.1 * this.r());       // a blink at the end of a sentence
        this.si++;
        if (this.si < this.seq.length) { this.sleft += this.seq[this.si][1]; if (this.seq[this.si][2]) this.browKick = Math.max(this.browKick, 0.8); }
      }
    }
    const rest = this.x.slice(10), mt = shape ? mouthVec(VISEME[shape]).map((m, i) => rest[i] + (m - rest[i]) * 0.9) : rest;
    for (let i = 0; i < mt.length; i++) { const w = 42; this.mv[i] += (w * w * (mt[i] - this.mouth[i]) - 2 * w * this.mv[i]) * dt; this.mouth[i] += this.mv[i] * dt; }
    this.browKick *= Math.exp(-dt / 0.35);
  }
  // what face.drawFace needs now
  face() {
    const e = vecExpr(this.x);
    const ta = clamp(this.talkAmt, 0, 1);
    if (ta > 0.001) { const m = e.mouth, keys = Object.keys(m); keys.forEach((k, i) => m[k] = m[k] + (this.mouth[i] - m[k]) * ta); }
    // the upper lid follows the eye down (and lifts as it looks up)
    const down = -this.eye[1] / 14;
    e.lid = [clamp(e.lid[0] + 0.12 * down, 0, 0.95), clamp(e.lid[1] + 0.12 * down, 0, 0.95)];
    const b = this.blinkAmount();
    return { e, gaze: [this.eye[0] / 8.5, -this.eye[1] / 9], blink: [b, b], browAdd: -1.8 * this.browKick };
  }
}
export { exprVec, vecExpr };
