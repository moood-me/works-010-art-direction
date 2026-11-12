// Аня's face alive (as Р11's). The timing is Р4's (to3d/r4-s5-vera/tools/web/live.js), taken from how real eyes and
// faces move, not from waves: events at uneven, seeded times and fast or slow approaches to them.
// - blinks: spontaneous ones log-normal around 2.8 s (0.35–8 s), now and then two in a row or a shallow one; each shuts
//   in 65–95 ms (speeding up), stays shut 25–55 ms, opens in 120–190 ms (slowing down); a big gaze shift brings one;
// - gaze: fixations of ~0.2–1.6 s, then a jump (a saccade, reached in ~2 frames); when the head is about to turn, the
//   eyes jump first to where it goes and turn back in the head as it follows;
// - expressions: every number goes to the new expression by a critically damped spring — except the head's squash and
//   stretch, which is a rubber spring (it overshoots and settles, as the 1930s heads do);
// - speech: a phrase read letter by letter into mouth shapes; pauses at commas and full stops.
import { EXPR, VISEME, exprVec, vecExpr, mixExpr, mouthVec, MOUTH0, SQ0 } from './face.js';

function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

export const PHRASES = ['Ой, смотрите!', 'Какой сегодня чудесный день.', 'А мне приснилось, будто я умею летать.', 'Пойдёмте гулять, ну пожалуйста!', 'Я вам верю.'];
const VOWEL = { а: 'A', я: 'A', о: 'O', ё: 'O', у: 'U', ю: 'U', е: 'E', э: 'E', и: 'I', ы: 'I' };
const CONS = { м: 'M', б: 'M', п: 'M', в: 'F', ф: 'F' };
// spring of each number of the face vector: [ω, ζ]
const N0 = exprVec(EXPR.neutral).length;
const SPRING = Array.from({ length: N0 }, (_, i) => {
  if (i === SQ0 || i === SQ0 + 1) return [15, 0.32];        // squash and stretch: rubber
  if (i === 3 || i === 4) return [16, 1];              // brows
  if (i <= 2) return [19, 1];                          // lids, the happy shut
  if (i >= MOUTH0) return [24, 1];                     // the mouth
  return [16, 1];
});

export class FaceLive {
  constructor(seed = 5) {
    this.r = rng(seed);
    this.x = exprVec(EXPR.neutral); this.v = this.x.map(() => 0);
    this.target = { neutral: 1 }; this.t = 0;
    this.blinks = []; this.nextBlink = 0.6 + this.interval() * 0.5;
    this.G = [0, 0]; this.eye = [0, 0]; this.nextFix = this.fixation();
    this.talk = false; this.talkAmt = 0; this.mouth = mouthVec(EXPR.neutral.mouth); this.mv = this.mouth.map(() => 0);
    this.seq = []; this.si = 0; this.sleft = 0; this.phrase = 0; this.browKick = 0;
    this.still = false;
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
      const u = this.t - b.at; let k = 0;
      if (u < 0) k = 0;
      else if (u < b.close) k = (u / b.close) ** 2;
      else if (u < b.close + b.hold) k = 1;
      else if (u < b.close + b.hold + b.open) { const w = (u - b.close - b.hold) / b.open; k = (1 - w) ** 2; }
      s = Math.max(s, k * b.depth);
    }
    return s;
  }
  setExpr(w) { this.target = typeof w === 'string' ? { [w]: 1 } : w; }
  setTalk(on) { this.talk = on; }
  // jump straight to the target (for still pictures)
  settle() { this.x = mixExpr(this.target); this.v = this.x.map(() => 0); this.mouth = this.x.slice(MOUTH0); this.mv = this.mouth.map(() => 0); }
  readPhrase() {
    const txt = PHRASES[this.phrase++ % PHRASES.length].toLowerCase(), seq = [];
    let first = true;
    for (const ch of txt) {
      if (VOWEL[ch]) { seq.push([VOWEL[ch], 0.085 + 0.06 * this.r(), first]); first = false; }
      else if (CONS[ch]) seq.push([CONS[ch], 0.07 + 0.03 * this.r()]);
      else if (/[а-яё]/.test(ch)) seq.push(['C', 0.05 + 0.03 * this.r()]);
      else if (ch === ' ' || ch === '-') seq.push(['C', 0.025]);
      else if (ch === ',' || ch === '—') seq.push([null, 0.22 + 0.1 * this.r()]);
      else if ('.?!'.includes(ch)) seq.push([null, 0.6 + 0.35 * this.r(), false, true]);
    }
    return seq;
  }
  // head: {yaw, pitch, aheadYaw, aheadPitch} in degrees (now, and where the head will be in ~0.25 s)
  step(dt, head = { yaw: 0, pitch: 0, aheadYaw: 0, aheadPitch: 0 }) {
    const sub = Math.max(1, Math.ceil(dt / (1 / 240))), h = dt / sub;
    for (let k = 0; k < sub; k++) this.tick(h, head);
  }
  tick(dt, head) {
    this.t += dt; const t = this.t;
    if (!this.still && t >= this.nextBlink) {
      this.blink(t, this.r() < 0.12 ? 0.7 : 1);
      if (this.r() < 0.12) this.blink(t + 0.28 + 0.15 * this.r());
      this.nextBlink = t + this.interval();
    }
    this.blinks = this.blinks.filter(b => t - b.at < 1);
    const lead = [head.aheadYaw - this.G[0], head.aheadPitch - this.G[1]];
    const jump = to => {
      const amp = Math.hypot(to[0] - this.G[0], to[1] - this.G[1]);
      this.G = to; this.nextFix = t + this.fixation();
      if (!this.still && amp > 16 && this.r() < clamp(0.35 + (amp - 16) / 25, 0, 0.95)) { this.blink(t + 0.01); this.nextBlink = Math.max(this.nextBlink, t + 0.8 * this.interval()); }
    };
    if (!this.still) {
      if (Math.abs(lead[0]) > 7 || Math.abs(lead[1]) > 6) jump([head.aheadYaw + 2 * this.gauss(), head.aheadPitch + 1.5 * this.gauss()]);
      else if (t >= this.nextFix) jump([head.aheadYaw + 5 * this.gauss(), head.aheadPitch + 3 * this.gauss() - 0.5]);
    }
    const want = this.still ? [0, 0] : [clamp(this.G[0] - head.yaw, -26, 26), clamp(this.G[1] - head.pitch, -16, 16)];
    const a = 1 - Math.exp(-dt / 0.016);
    this.eye[0] += (want[0] - this.eye[0]) * a; this.eye[1] += (want[1] - this.eye[1]) * a;
    const tgt = mixExpr(this.target);
    for (let i = 0; i < N0; i++) { const [w, z] = SPRING[i]; this.v[i] += (w * w * (tgt[i] - this.x[i]) - 2 * z * w * this.v[i]) * dt; this.x[i] += this.v[i] * dt; }
    this.talkAmt += ((this.talk || this.si < this.seq.length ? 1 : 0) - this.talkAmt) * (1 - Math.exp(-dt / 0.08));
    if (this.si >= this.seq.length && this.talk) { this.seq = this.readPhrase(); this.si = 0; this.sleft = this.seq[0][1]; if (this.seq[0][2]) this.browKick = 1; }
    let shape = null;
    if (this.si < this.seq.length) {
      const cur = this.seq[this.si]; shape = cur[0]; this.sleft -= dt;
      if (this.sleft <= 0) {
        if (cur[3] && this.r() < 0.5 && !this.still) this.blink(t + 0.05 + 0.1 * this.r());
        this.si++;
        if (this.si < this.seq.length) { this.sleft += this.seq[this.si][1]; if (this.seq[this.si][2]) this.browKick = Math.max(this.browKick, 0.8); }
      }
    }
    const rest = this.x.slice(MOUTH0), mt = shape ? mouthVec(VISEME[shape]) : rest;
    for (let i = 0; i < mt.length; i++) { const w = 42; this.mv[i] += (w * w * (mt[i] - this.mouth[i]) - 2 * w * this.mv[i]) * dt; this.mouth[i] += this.mv[i] * dt; }
    this.browKick *= Math.exp(-dt / 0.35);
  }
  // the face now: the expression's numbers, the mouth (speech over it), the eyes, the blink
  face() {
    const v = this.x.slice(), ta = clamp(this.talkAmt, 0, 1);
    for (let i = 0; i < this.mouth.length; i++) v[MOUTH0 + i] += (this.mouth[i] - v[MOUTH0 + i]) * ta;
    const e = vecExpr(v);
    const down = -this.eye[1] / 16;
    e.lid = clamp(e.lid + 0.12 * Math.max(0, down), 0, 0.95);
    e.brow += 0.35 * this.browKick; e.browY -= 3 * this.browKick;
    const look = this.still ? e.look : [e.look[0] + this.eye[0] / 14, e.look[1] - this.eye[1] / 12];
    return { e, look, blink: this.blinkAmount() };
  }
}
