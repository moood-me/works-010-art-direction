// Тим's painted face, alive. The drawing's own marks (styles/s9-midcentury/tools: kit.py path/sample/brush, face.py
// eye/brow/mouth, tim.py's expressions) are carried over line for line and drawn into a canvas the head takes by its
// front projection (the drawing's head units −128…128, y down). Every frame the marks are drawn again from a state:
//   expression — the sheet's five, blended: numbers (brow ends, mouth size, blush) go over smoothly, a mark of another
//                kind (dot eye → laughing arc) fades over the old one;
//   blink      — at uneven intervals (a gamma-like spread round ~3.5 s, sometimes a double blink) and when the head
//                turns fast; the lid closes fast (~70 ms) and opens slower (~140 ms), as eyes do;
//   gaze       — still most of the time, moving in small quick jumps (saccades, ~40 ms, a little overshoot);
//                before a head turn the eyes go first, towards where the head is going (read off the motion ahead);
//   speech     — mouth shapes of syllables (consonant–vowel, 60–200 ms each, phrases with pauses), each shape eased
//                into the next (coarticulation), the expression's mouth when silent.
// All of it is a timeline made once from a seeded random stream, so a moment t always looks the same (films, scrubbing).

const INK = '#2a201c', LIP = '#c23a2c', MOUTH_IN = '#6e1f1c', CHEEK = '#ee7a66', FRECK = '#c97a52', HAIR_D = '#a8481c';

// ---------- kit.py ----------
function samplePts(pts, closed = false, per = 10) {
  const P = pts.map(q => [q[0], q[1]]), n = P.length, res = [], segs = closed ? n : n - 1;
  for (let i = 0; i < segs; i++) {
    const p0 = (closed || i > 0) ? P[(i - 1 + n) % n] : P[i], p1 = P[i], p2 = P[(i + 1) % n];
    const p3 = (closed || i + 2 < n) ? P[(i + 2) % n] : P[(i + 1) % n];
    for (let s = 0; s < per; s++) {
      const t = s / per, t2 = t * t, t3 = t2 * t;
      res.push([0, 1].map(j => 0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)));
    }
  }
  res.push(closed ? P[0] : P[n - 1]);
  return res;
}
function pathD(pts, closed = true, tension = 1) {
  const n = pts.length, P = pts.map(q => [q[0], q[1]]), corner = q => q.length > 2 && q[2] === 'c';
  let d = `M${P[0][0]},${P[0][1]}`;
  const segs = closed ? n : n - 1;
  for (let i = 0; i < segs; i++) {
    const p0 = (closed || i > 0) ? P[(i - 1 + n) % n] : P[i], p1 = P[i], p2 = P[(i + 1) % n];
    const p3 = (closed || i + 2 < n) ? P[(i + 2) % n] : P[(i + 1) % n], k = tension / 6;
    let c1 = [p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k], c2 = [p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k];
    if (corner(pts[i])) c1 = [p1[0] + (p2[0] - p1[0]) * 0.3, p1[1] + (p2[1] - p1[1]) * 0.3];
    if (corner(pts[(i + 1) % n])) c2 = [p2[0] + (p1[0] - p2[0]) * 0.3, p2[1] + (p1[1] - p2[1]) * 0.3];
    d += `C${c1[0]},${c1[1]} ${c2[0]},${c2[1]} ${p2[0]},${p2[1]}`;
  }
  return d + (closed ? 'Z' : '');
}
function brushD(pts, w, taper = [0.25, 0.35], per = 8) {
  const c = samplePts(pts, false, per), L = [0];
  for (let i = 1; i < c.length; i++) L.push(L[i - 1] + Math.hypot(c[i][0] - c[i - 1][0], c[i][1] - c[i - 1][1]));
  const tot = L[L.length - 1] || 1, left = [], right = [], [a, b] = taper;
  c.forEach((p, i) => {
    const t = L[i] / tot; let k = 1;
    if (a > 0 && t < a) k = 0.18 + 0.82 * Math.sin(t / a * Math.PI / 2);
    if (b > 0 && t > 1 - b) k = Math.min(k, 0.12 + 0.88 * Math.sin((1 - t) / b * Math.PI / 2));
    const q0 = c[Math.max(i - 1, 0)], q1 = c[Math.min(i + 1, c.length - 1)];
    const dx = q1[0] - q0[0], dy = q1[1] - q0[1], dl = Math.hypot(dx, dy) || 1, nx = -dy / dl, ny = dx / dl, hw = w * k / 2;
    left.push([p[0] + nx * hw, p[1] + ny * hw]); right.push([p[0] - nx * hw, p[1] - ny * hw]);
  });
  return 'M' + left.concat(right.reverse()).map(q => `${q[0]},${q[1]}`).join(' L') + 'Z';
}

// a drawing context in head units: marks are filled shapes, with an opacity
class Pen {
  constructor(ctx) { this.c = ctx; this.alpha = 1; }
  fill(d, color, op = 1) { const c = this.c; c.globalAlpha = op * this.alpha; c.fillStyle = color; c.fill(new Path2D(d)); }
  shape(pts, color, op) { this.fill(pathD(pts), color, op); }
  brush(pts, w, color = INK, taper, op) { this.fill(brushD(pts, w, taper), color, op); }
  ell(cx, cy, rx, ry, color, op = 1, rot = 0) {
    const c = this.c; c.globalAlpha = op * this.alpha; c.fillStyle = color; c.beginPath();
    c.ellipse(cx, cy, Math.max(rx, 0.01), Math.max(ry, 0.01), rot * Math.PI / 180, 0, 2 * Math.PI); c.fill();
  }
  blush(cx, cy, r, color, op = 0.7) {
    const c = this.c; c.save(); c.filter = `blur(${2.2 * this.scale}px)`; this.ell(cx, cy, r, r, color, op); c.restore();
  }
}

// ---------- face.py (the kinds Тим uses), with open: 1 open … 0 shut, and gaze (gx, gy) in head units ----------
function eye(p, x, y, s, kind, side, open = 1, gx = 0, gy = 0) {
  const w = s;
  if (kind === 'dot') {
    if (open > 0.25) p.ell(x + gx, y + gy, 4.2 * w, 5.6 * s * open, INK);
    else p.brush([[x - 6 * w, y - 1 * s], [x, y + 2.5 * s], [x + 6 * w, y - 1 * s]], 2.4 * s, INK, [0.3, 0.3], Math.min(1, (0.25 - open) * 8 + 0.3));
  } else if (kind === 'happy') {
    p.brush([[x - side * 7 * w, y + 2.5 * s], [x, y - 3.5 * s], [x + side * 8 * w, y + 2 * s]], 2.6 * s, INK, [0.25, 0.25]);
  } else if (kind === 'wide') {
    const o = Math.max(open, 0.08);
    p.ell(x, y - 1 * s, 7.6 * w, 9 * s * o, '#fbf6ea');
    if (open > 0.3) p.ell(x + side * 0.6 * w + gx * 0.8, y - 0.5 * s + gy * 0.8 * o, 3.6 * w, 4.6 * s * Math.min(1, o * 1.3), INK);
    p.brush([[x - side * 8 * w, y - 3 * s + (1 - o) * 7 * s], [x, y - 10.8 * s + (1 - o) * 10 * s], [x + side * 8.5 * w, y - 3.5 * s + (1 - o) * 7 * s]], 2.0 * s, INK, [0.3, 0.3]);
  } else if (kind === 'sad') {
    if (open > 0.25) p.ell(x + gx, y + 0.8 * s + gy, 3.8 * w, 4.4 * s * open, INK);
    p.brush([[x - side * 7 * w, y - 4.5 * s + (1 - open) * 4.5 * s], [x + side * 1 * w, y - 4.6 * s + (1 - open) * 5 * s], [x + side * 8 * w, y - 1 * s + (1 - open) * 2 * s]], 2.2 * s, INK, [0.2, 0.3]);
  } else if (kind === 'glare') {
    const o = Math.max(open, 0.15), cy = y + 1 * s;
    const sq = v => cy + (v - cy) * o;
    p.shape([[x - side * 7 * w + gx, sq(y + 1.5 * s), 'c'], [x + side * 8 * w + gx, sq(y - 3.5 * s), 'c'], [x + side * 4 * w + gx, sq(y + 3.6 * s)], [x - side * 3 * w + gx, sq(y + 3.8 * s)]], INK);
    p.brush([[x - side * 8.5 * w, sq(y + 1.2 * s)], [x + side * 9.5 * w, sq(y - 4.2 * s)]], 3.0 * s, INK, [0.1, 0.2]);
  }
}
function brow(p, x, y, s, side, inner, outer, w) {
  const L = 1;
  p.brush([[x - side * 8 * L * s, y + inner * s], [x + side * 1 * L * s, y - 2.4 * s + (inner + outer) * 0.5 * s], [x + side * 10 * L * s, y + outer * s]], w * s, INK, [0.15, 0.6]);
}
function mouth(p, x, y, s, kind, side, width) {
  const W = width * s;
  if (kind === 'smirk') p.brush([[x - side * 7 * W, y + 0.5 * s], [x + side * 2 * W, y + 1.5 * s], [x + side * 8 * W, y - 3.5 * s]], 2.6 * s, LIP, [0.3, 0.2]);
  else if (kind === 'o') { p.ell(x, y + 1 * s, 4 * W, 5 * s, LIP); p.ell(x, y + 1.6 * s, 2.3 * W, 3.2 * s, MOUTH_IN); }
  else if (kind === 'grin') {
    p.shape([[x - side * 10 * W, y - 2 * s, 'c'], [x + side * 10 * W, y - 3 * s, 'c'], [x + side * 5 * W, y + 7 * s], [x - side * 4 * W, y + 7 * s]], MOUTH_IN);
    p.shape([[x - side * 4 * W, y + 4.5 * s], [x + side * 4 * W, y + 4 * s], [x + side * 3 * W, y + 7 * s], [x - side * 3 * W, y + 7 * s]], '#e2706a');
    p.brush([[x - side * 10.5 * W, y - 2 * s], [x, y - 2.8 * s], [x + side * 10.5 * W, y - 3.2 * s]], 1.8 * s, LIP, [0.1, 0.1]);
  } else if (kind === 'sad') p.brush([[x - side * 7 * W, y + 3 * s], [x - side * 2 * W, y - 0.5 * s], [x + side * 3 * W, y - 0.5 * s], [x + side * 7 * W, y + 3.4 * s]], 2.4 * s, LIP, [0.35, 0.35]);
  else if (kind === 'shout') {
    p.shape([[x - side * 10 * W, y - 3 * s, 'c'], [x - side * 2 * W, y - 1 * s], [x + side * 10 * W, y - 3.5 * s, 'c'], [x + side * 7 * W, y + 6 * s, 'c'], [x - side * 7 * W, y + 6 * s, 'c']], MOUTH_IN);
    p.shape([[x - side * 8 * W, y - 2 * s, 'c'], [x + side * 8 * W, y - 2.4 * s, 'c'], [x + side * 7 * W, y + 0.4 * s], [x - side * 7 * W, y + 0.6 * s]], '#f6efe0');
  }
}
// a speaking mouth in the same manner: an opening (dark inside, a little tongue when wide), a red upper lip stroke;
// o: how open 0…1, wd: width ×, rd: roundness 0 (a half-moon, like the grin) … 1 (an O)
function talkMouth(p, x, y, s, o, wd, rd, smile) {
  const W = 8.5 * s * wd, H = 7.5 * s * o;
  if (o < 0.08) { p.brush([[x - W * 0.85, y - 0.5 * s - smile * 1.5 * s], [x, y + 1 * s], [x + W * 0.85, y - 1.5 * s - smile * 2 * s]], 2.4 * s, LIP, [0.3, 0.25]); return; }
  const top = y - 1.5 * s - H * 0.25 * rd, bot = y - 1.5 * s + H;
  const pts = [[x - W, y - 1.5 * s - smile * 1.2 * s, 'c'], [x - W * 0.55, top - H * 0.15 * rd], [x, top - H * 0.2 * rd], [x + W * 0.55, top - H * 0.15 * rd],
               [x + W, y - 1.5 * s - smile * 1.6 * s, 'c'], [x + W * (0.6 + 0.2 * rd), bot - H * 0.15], [x, bot], [x - W * (0.6 + 0.2 * rd), bot - H * 0.15]];
  p.shape(pts, MOUTH_IN);
  if (o > 0.45) p.ell(x, bot - H * 0.2, W * 0.45, H * 0.22, '#e2706a');
  p.brush([[x - W * 1.04, y - 1.5 * s - smile * 1.2 * s], [x, top - H * 0.25 * rd - 0.6 * s], [x + W * 1.04, y - 1.5 * s - smile * 1.6 * s]], 1.7 * s, LIP, [0.12, 0.12]);
}

// ---------- tim.py's expressions ----------
export const EXPRS = {
  calm: { eye: 'dot', brow: [0, 0], brow2: [4, -6], mouth: 'smirk', ms: 1, cheek: 1 },
  joy: { eye: 'happy', brow: [-4, -2], brow2: [-4, -2], mouth: 'grin', ms: 1.45, cheek: 1.3 },
  surprise: { eye: 'wide', brow: [-10, -8], brow2: [-10, -8], mouth: 'o', ms: 1.35, cheek: 1 },
  sad: { eye: 'sad', brow: [-7, 5], brow2: [-7, 5], mouth: 'sad', ms: 1.2, cheek: 1 },
  anger: { eye: 'glare', brow: [9, -6], brow2: [9, -6], mouth: 'shout', ms: 1.45, cheek: 1.3 },
};
const FRECKLES = [[-48, 30], [-38, 26], [-28, 32], [-42, 38], [48, 30], [38, 26], [28, 32], [42, 38]];

// ---------- the timeline ----------
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const ease = u => u <= 0 ? 0 : u >= 1 ? 1 : u * u * (3 - 2 * u);
// the blink lid: closing ~70 ms, held ~30 ms, opening ~140 ms → openness 1…0…1
function lid(dt) { if (dt < 0) return 1; if (dt < 0.07) return 1 - ease(dt / 0.07); if (dt < 0.1) return 0; if (dt < 0.24) return ease((dt - 0.1) / 0.14); return 1; }

export class LiveFace {
  constructor({ seed = 7, length = 120 } = {}) {
    const r = rng(seed); this.length = length;
    // blinks: intervals spread like real ones (most 2–5 s, now and then a quick double)
    this.blinks = [];
    for (let t = 0.8 + r() * 1.5; t < length;) {
      this.blinks.push(t);
      if (r() < 0.12) this.blinks.push(t + 0.32 + r() * 0.12);
      const g = -Math.log(r() * r() + 1e-9) / 2;            // a gamma(2)-like spread
      t += 1.2 + g * 2.6;
    }
    // saccades: fixations of 0.3–2.2 s, small jumps about the middle (head units), each with a little overshoot
    this.sacc = [{ t: 0, x: 0, y: 0 }];
    for (let t = 0.6 + r(); t < length; t += 0.3 + r() * r() * 2.2 + r() * 0.4)
      this.sacc.push({ t, x: (r() - 0.5) * 4.4, y: (r() - 0.5) * 2.2 });
    // speech: phrases of syllables (a consonant shape, then a vowel shape), pauses between phrases
    const V = { a: [0.95, 1.05, 0.2], e: [0.5, 1.2, 0], i: [0.35, 1.1, 0], o: [0.8, 0.62, 1], u: [0.45, 0.48, 1] };
    const C = { m: [0, 0.9, 0.2], f: [0.15, 0.95, 0], t: [0.3, 1, 0.2], k: [0.4, 0.95, 0.4], s: [0.2, 1.1, 0] };
    const vk = Object.keys(V), ck = Object.keys(C);
    this.speech = [];
    for (let t = 0.4; t < length;) {
      const n = 3 + Math.floor(r() * 7);
      for (let i = 0; i < n; i++) {
        const c = C[ck[Math.floor(r() * ck.length)]], v = V[vk[Math.floor(r() * vk.length)]];
        const dc = 0.06 + r() * 0.05, dv = 0.1 + r() * 0.12;
        this.speech.push({ t, d: dc, s: c }); t += dc;
        this.speech.push({ t, d: dv, s: v }); t += dv;
      }
      this.speech.push({ t, d: 0.3 + r() * 0.7, s: [0, 0.9, 0.2], pause: true }); t += this.speech[this.speech.length - 1].d;
    }
    this.extraBlinks = [];
    this.expr = [{ t: 0, name: 'calm' }];
    this.talking = false;
    this.lead = null;      // (t) → head turn ahead, radians (+: towards his left)
  }
  // expressions over time: [{t, name}] — each change blends over 0.35 s
  setExpressions(list) { this.expr = list.length ? list : [{ t: 0, name: 'calm' }]; }
  // blinks the head's turns call for (from the motion: where the head turns fast)
  setHeadTurns(times) { this.extraBlinks = times.slice(); }

  exprAt(t) {
    let i = 0; while (i + 1 < this.expr.length && this.expr[i + 1].t <= t) i++;
    const cur = this.expr[i], prev = i > 0 ? this.expr[i - 1] : cur, u = ease((t - cur.t) / 0.35);
    return { a: EXPRS[prev.name], b: EXPRS[cur.name], u: i > 0 ? u : 1 };
  }
  openAt(t) {
    let o = 1;
    for (const b of this.blinks) { if (b > t) break; o = Math.min(o, lid(t - b)); }
    for (const b of this.extraBlinks) { if (b > t + 0.01) continue; o = Math.min(o, lid(t - b)); }
    return o;
  }
  gazeAt(t) {
    let i = 0; while (i + 1 < this.sacc.length && this.sacc[i + 1].t <= t) i++;
    const s = this.sacc[i], p = i > 0 ? this.sacc[i - 1] : s, dt = t - s.t;
    // a saccade: ~40 ms to 110 %, then settling back over ~60 ms
    const k = dt < 0.04 ? ease(dt / 0.04) * 1.1 : dt < 0.1 ? 1.1 - 0.1 * ease((dt - 0.04) / 0.06) : 1;
    let x = p.x + (s.x - p.x) * k, y = p.y + (s.y - p.y) * k;
    if (this.lead) {   // the eyes go first where the head is turning (they get there in one quick jump, then the head follows)
      const a = this.lead(t);
      x = x * (1 - Math.min(1, Math.abs(a) * 3)) + Math.max(-1, Math.min(1, a * 3.2)) * 5.5;
    }
    return [x, y];
  }
  mouthAt(t) {
    if (!this.talking) return null;
    const S = this.speech; let i = 0, lo = 0, hi = S.length - 1;
    while (lo <= hi) { const m = (lo + hi) >> 1; if (S[m].t <= t) { i = m; lo = m + 1; } else hi = m - 1; }
    const cur = S[i], prev = i > 0 ? S[i - 1] : cur, u = ease((t - cur.t) / Math.min(0.07, cur.d * 0.6));
    return [0, 1, 2].map(k => prev.s[k] + (cur.s[k] - prev.s[k]) * u);
  }

  // draw the face at time t into a 2D canvas (square; the head units −128…128)
  draw(ctx, t) {
    const S = ctx.canvas.width / 256, p = new Pen(ctx); p.scale = S;
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.setTransform(S, 0, 0, S, 128 * S, 128 * S);
    const { a, b, u } = this.exprAt(t), mix = (x, y) => x + (y - x) * u;
    const cheek = mix(a.cheek, b.cheek), ms = mix(a.ms, b.ms);
    const bi = mix(a.brow[0], b.brow[0]), bo = mix(a.brow[1], b.brow[1]), b2i = mix(a.brow2[0], b.brow2[0]), b2o = mix(a.brow2[1], b.brow2[1]);
    const open = this.openAt(t), [gx, gy] = this.gazeAt(t), talk = this.mouthAt(t);
    // the hair's dry brush, the cheeks: a layer kept while the blush's size stays (a blur is dear to draw)
    const ck = Math.round(cheek * 50) / 50;
    if (!this.base || this.baseKey !== ck || this.base.width !== ctx.canvas.width) {
      this.base = this.base && this.base.width === ctx.canvas.width ? this.base : Object.assign(document.createElement('canvas'), { width: ctx.canvas.width, height: ctx.canvas.height });
      const bc = this.base.getContext('2d'), bp = new Pen(bc); bp.scale = S;
      bc.setTransform(1, 0, 0, 1, 0, 0); bc.clearRect(0, 0, this.base.width, this.base.height); bc.setTransform(S, 0, 0, S, 128 * S, 128 * S);
      bp.brush([[-56, -70], [-16, -106], [30, -110]], 2.6, HAIR_D, [0.3, 0.5], 0.7);
      bp.brush([[-10, -74], [30, -100], [64, -76]], 2.6, HAIR_D, [0.3, 0.5], 0.7);
      bp.blush(-40, 40, 16 * ck, CHEEK); bp.blush(40, 40, 16 * ck, CHEEK);
      for (const [x, y] of FRECKLES) bp.ell(x, y, 1.9, 1.9, FRECK, 0.85);
      this.baseKey = ck;
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.drawImage(this.base, 0, 0); ctx.setTransform(S, 0, 0, S, 128 * S, 128 * S);
    // eyes (kinds fading into each other), brows lifting a little with a wide look
    const lift = open < 0.5 ? (0.5 - open) * 2 : 0;
    const eyes = (e, al) => { p.alpha = al; eye(p, -24, 14, 1.45, e, -1, open, gx, gy); eye(p, 24, 14, 1.45, e, 1, open, gx, gy); };
    if (a.eye !== b.eye && u < 1) { eyes(a.eye, 1 - u); eyes(b.eye, u); } else eyes(b.eye, 1);
    p.alpha = 1;
    brow(p, -25, -10 + lift * 1.2, 1.2, -1, bi, bo, 3.2); brow(p, 25, -12 + lift * 1.2, 1.2, 1, b2i, b2o, 3.2);
    // the mouth: speaking shapes, or the expression's own
    if (talk) {
      const smile = b.mouth === 'smirk' || b.mouth === 'grin' ? 1 : b.mouth === 'sad' ? -1 : 0;
      talkMouth(p, 2, 58, 1.3, talk[0], talk[1], talk[2], smile * (1 - (a === b ? 0 : 0)));
    } else if (a.mouth !== b.mouth && u < 1) {
      p.alpha = 1 - u; mouth(p, 2, 58, 1.3 * mix(a.ms, b.ms), a.mouth, 1, 0.85);
      p.alpha = u; mouth(p, 2, 58, 1.3 * ms, b.mouth, 1, 0.85); p.alpha = 1;
    } else mouth(p, 2, 58, 1.3 * ms, b.mouth, 1, 0.85);
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
  }
}
