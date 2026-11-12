// The face alive, the way a sprite's face is: by whole frames. Blinks at uneven times (a closed frame or two), the
// eyes of the portrait jumping to a side and back, the mouth of speech as closed / half open / open by syllables,
// a change of expression through a blink. The times come from a seeded stream (no sines): the same second of a film
// always looks the same. Timing as in Р4's live.js: blinks log-normal around 2.8 s, 12 % doubled; fixations 0.3–1.6 s;
// vowels 85–145 ms, consonants 50–100 ms, pauses 0.25–0.9 s.
function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const logn = (r, med, s) => med * Math.exp(s * Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(6.2831853 * r()));
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const LEN = 120;
export class Live {
  constructor(seed = 16) {
    let r = rng(seed), t = 0.9;
    this.blinks = [];                              // [start, end]
    while (t < LEN) { this.blinks.push([t, t + 0.11]); if (r() < 0.12) this.blinks.push([t + 0.27, t + 0.36]); t += clamp(logn(r, 2.8, 0.55), 0.6, 8); }
    r = rng(seed + 1); t = 0; this.looks = [];     // [start, 'l' | 'r' | null]
    while (t < LEN) { const u = r(); this.looks.push([t, u < 0.62 ? null : u < 0.81 ? 'l' : 'r']); t += clamp(logn(r, 0.7, 0.5), 0.3, 1.6) * (u < 0.62 ? 1.6 : 1); }
    r = rng(seed + 2); t = 0.3; this.mouths = [];  // [start, 0 | 1 | 2]
    while (t < LEN) {
      const syl = 3 + Math.floor(r() * 7);
      for (let i = 0; i < syl; i++) { this.mouths.push([t, 0]); t += 0.05 + r() * 0.05; this.mouths.push([t, r() < 0.45 ? 2 : 1]); t += 0.085 + r() * 0.06; }
      this.mouths.push([t, 0]); t += r() < 0.3 ? 0.6 + r() * 0.3 : 0.25 + r() * 0.1;
    }
    this.expr = 'rest'; this.changed = -9;
  }
  at(t, expr, talk) {
    const u = ((t % LEN) + LEN) % LEN, find = a => { let v = a[0][1]; for (const [s, k] of a) { if (s > u) break; v = k; } return v; };
    if (expr !== this.expr) { this.expr = expr; this.changed = t; }
    const blink = this.blinks.some(([a, b]) => u >= a && u < b) || (t - this.changed >= 0 && t - this.changed < 0.1);
    return { expr, blink, look: expr === 'rest' && !blink ? find(this.looks) : null, mouth: talk ? find(this.mouths) : 0 };
  }
}
