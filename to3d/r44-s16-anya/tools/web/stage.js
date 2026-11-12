// The picture round the figure: the style's backdrops (the sheet's plain one, the street at dusk) on the same pixel
// grid, the two rows of shadow under the feet (sheets.py: stand), the clips, and the small life of the face.
import { put } from './vox.js';
import { pose, rest, prepare, qbetween, qmul } from './rig.js';

export const FPS = 12;      // drawings a second: a sprite's animation is a few held frames, not a smooth glide

export function Stage(ch, pal, D, fig) {
  const flat = rows => { const g = pal.grid(rows), w = g[0].length, a = new Uint8Array(w * g.length); g.forEach((r, j) => a.set(r, j * w)); return { key: a, w, h: g.length }; };
  const BG = { backdrop: { ...flat(D.backdrop), floor: 58, base: 62 }, street: { ...flat(D.street), floor: 84, base: 90 } };
  const sprites = Object.fromEntries(Object.entries(D.views).map(([v, r]) => [v, flat(r)]));
  const portraits = Object.fromEntries(Object.entries(D.portraits).map(([v, r]) => [v, flat(r)]));

  function ground(bg, w, h, bx = 0, by = 0) { // a window of a backdrop; the street goes round
    const B = BG[bg], out = new Uint8Array(w * h);
    for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) out[r * w + c] = B.key[Math.min(B.h - 1, r + by) * B.w + (((c + bx) % B.w) + B.w) % B.w];
    return out;
  }
  function shadow(key, w, h, cx, row, lift = 0) { // two rows under the feet, narrower when the figure is in the air
    const [a, b] = ch.SHADOW, n = lift > 2 ? 2 : 0, k = pal.idx.d1;
    for (let c = cx - a + n; c < cx + a - n; c++) if (c >= 0 && c < w && row < h) key[row * w + c] = k;
    for (let c = cx - b + n; c < cx + b - n; c++) if (c >= 0 && c < w && row + 1 < h) key[(row + 1) * w + c] = k;
  }
  // o: bg, w, h, bx, by (the window's corner in the backdrop), x (the column of the frame where the figure's middle
  // stands), pose, yaw, face, steady, relight, outline, scroll (the view goes with the figure: whole pixels)
  function frame(o) {
    const B = BG[o.bg || 'backdrop'], w = o.w, h = o.h, by = o.by ?? 0, bx = o.bx ?? 0;
    const ya = (o.yaw || 0) * Math.PI / 180, hx = Math.cos(ya) * o.pose.P.Hips[0] + Math.sin(ya) * o.pose.P.Hips[2], hx0 = Math.cos(ya) * fig.J.Hips[0] + Math.sin(ya) * fig.J.Hips[2];
    const go = Math.round(hx - hx0), cam = [o.follow ? go : 0, 0];
    const key = o.clear ? new Uint8Array(w * h) : ground(o.bg || 'backdrop', w, h, bx + cam[0], by);
    const ox = o.x - Math.floor(ch.CX), oy = B.base + 1 - by - ch.FLOOR;
    let f = fig.render({ pose: o.pose, yaw: o.yaw, w, h, ox, oy, cam, face: o.face, steady: o.steady, relight: o.relight });
    if (o.outline !== false) f = fig.outline(f);
    if (o.shadow !== false) shadow(key, w, h, o.x + (o.follow ? 0 : go), B.base - by, o.lift || 0);
    put(key, w, h, f.key, w, h, 0, 0);
    return { key, w, h, fig: f };
  }
  function drawn(key, w, h, view, x, by = 0, bg = 'backdrop', flip = false) { // the drawing's own sprite, stood as sheets.py stands it
    const B = BG[bg], s = sprites[view], left = x - (s.w >> 1), base = B.base - by;
    for (let c = left + 2; c <= left + s.w - 3; c++) key[base * w + c] = pal.idx.d1;
    for (let c = left + 4; c <= left + s.w - 5; c++) key[(base + 1) * w + c] = pal.idx.d1;
    put(key, w, h, s.key, s.w, s.h, left, base - s.h + 2);
    return left;
  }
  // the portrait in its box, alive as a game's is: only the eyes and the mouth change over the same drawing
  function portrait(face = {}) {
    const p = portraits[face.expr || 'rest'], out = { key: p.key.slice(), w: p.w, h: p.h };
    const patch = (from, [x0, y0, x1, y1]) => { for (let r = y0; r <= y1; r++) for (let c = x0; c <= x1; c++) out.key[r * p.w + c] = from.key[r * p.w + c]; };
    if (face.blink && face.expr !== 'joy' && portraits.blink) patch(portraits.blink, ch.PORTRAIT.eyes);
    if (ch.PORTRAIT.talk[face.mouth]) patch(portraits[ch.PORTRAIT.talk[face.mouth]], ch.PORTRAIT.mouth);
    return out;
  }
  return { BG, sprites, portraits, ground, frame, drawn, portrait, shadow };
}

// ———— motion: a clip at a time, held on whole drawings
export function Player(ch, fig, motions) {
  const J = fig.J, sole = ch.SOLE.map(([b, p]) => [b, fig.toW(p)]), head = { c: fig.toW(ch.HEAD.c), r: ch.HEAD.r };
  for (const m of Object.values(motions)) prepare(m, J);
  const dirs = d => W => { for (const [b, v] of Object.entries(d)) { W[b] = qmul(W.Chest, qbetween([0, -1, 0], v)); if (/ForeArm/.test(b)) W[b.replace('ForeArm', 'Hand')] = W[b]; } };
  const HOLD = Object.fromEntries(Object.entries(ch.HOLD || {}).map(([k, d]) => [k, dirs(d)]));
  function at(clip, t, fps = FPS) {
    if (!clip.motion) return { pose: rest(J, clip.holdAt ? dirs(clip.holdAt(fps ? Math.floor(t * fps + 1e-6) / fps : t)) : HOLD[clip.hold]), lift: 0 };
    const M = motions[clip.motion], dur = (M.n - 1) / M.fps, tt = fps ? Math.floor(t * fps + 1e-6) / fps : t;
    const f = Math.min(M.n - 1, (clip.loop === false ? Math.min(tt, dur) : tt % dur) * M.fps);
    const i = Math.min(M.n - 1, Math.round(f));
    return { pose: pose(M, f, J, { travel: clip.travel, sole, head, armOut: clip.armOut ?? ch.ARM_OUT ?? 0.3, upright: clip.upright, arms: clip.arms, hold: clip.holdAt ? dirs(clip.holdAt(tt)) : HOLD[clip.hold] }), lift: M.foot[i] * J.Hips[1] / M.hipY, dur };
  }
  const dur = clip => clip.motion ? (motions[clip.motion].n - 1) / motions[clip.motion].fps : (clip.dur || 4);
  return { at, dur, HOLD };
}

// ———— the face's small life: blinks at uneven times, speech as open and closed mouths with pauses; the same moment
// always looks the same (a seeded stream, no sines)
function stream(seed) { let a = seed >>> 0; return () => { a = (a + 0x6d2b79f5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
export function Life(seed = 7) {
  const r = stream(seed), blinks = [], says = [];
  for (let t = 0.9; t < 900;) { blinks.push(t); t += 1.5 + 3.6 * r() * r() + (r() < 0.15 ? -1.1 : 0.6); }
  for (let t = 0.3; t < 900;) { // words of 1–4 syllables, a pause after each, a longer one after a phrase
    const n = 1 + Math.floor(r() * 4);
    for (let i = 0; i < n; i++) { const d = 0.17 + 0.1 * r(); says.push([t, t + d * 0.62, r() < 0.3 ? 'round' : 'open']); t += d; }
    t += r() < 0.25 ? 0.5 + 0.5 * r() : 0.12 + 0.1 * r();
  }
  const find = (a, t, key) => { let lo = 0, hi = a.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (key(a[m]) <= t) lo = m; else hi = m - 1; } return a[lo]; };
  return (t, { talk = false, expr = 'rest' } = {}) => {
    const b = find(blinks, t, x => x), blink = t >= b && t - b < 0.14;
    let mouth = null;
    if (talk) { const s = find(says, t, x => x[0]); mouth = t >= s[0] && t < s[1] ? s[2] : 'closed'; }
    return { expr, blink, mouth };
  };
}
