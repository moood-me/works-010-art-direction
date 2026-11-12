// The face, alive: the drawing's own face parts (styles/s7-ghibli/tools/head.py: eye with its crease and lash, brow,
// nose, mouth, lower lip, the face's marks, blush) ported to a canvas and drawn every frame from the same numbers (the
// character's FACE and an Expr — both come in the pack's header, written by tools/build.py), so the face moves as
// the drawing would draw it. The canvas is the head's painted layer: head-local units (head 2 tall, crown +1, chin −1),
// front projection — on the drawing's own face surface a feature at (x, y) is seen from the front at (x, y), so the
// templates go in as they are.
//
// What moves, and its timing (from how faces move, not from sines):
//   blinks      — spontaneous, intervals log-normal (median 2.8 s), now and then a double; the upper lid closes fast
//                 (≈70 ms) down to the lower one, holds (≈30 ms), opens slower (≈150 ms); also with big gaze shifts.
//   saccades    — fixations log-normal (median ≈0.55 s); the jump takes 22 ms + 2.7 ms per degree.
//   gaze leads  — the eyes jump toward where the head will be in ≈0.25 s and come back as the head follows.
//   speech      — syllables of consonant + vowel mouth shapes; the mouth follows them as a critically damped spring.
//   expressions — weights of the sheet's (calm, joy, surprise, sad, anger), mixed number by number; a change settles
//                 as a critically damped spring (≈0.3 s), brows a little ahead of the mouth.
export let INK = '#2e2320';
export let P = {};
export let EXPR = {};
export let EXPR_NAMES = [];
const mixc = (a, b, t) => { const p = s => [1, 3, 5].map(i => parseInt(s.slice(i, i + 2), 16)); const A = p(a), B = p(b);
  return '#' + A.map((x, i) => Math.round(x + (B[i] - x) * t).toString(16).padStart(2, '0')).join(''); };
const SHADE = c => { const p = [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16)), m = [0.86, 0.78, 0.84];
  return '#' + p.map((x, i) => Math.round(x * m[i]).toString(16).padStart(2, '0')).join(''); };
const DEF = { open: 1, lid_in: 0, lid_out: 0, smile_eye: 0, closed: 0, iris: 1, lx: 0, ly: 0, brow_up: 0, brow_in: 0, brow_arch: 0,
  mLine: 1, mD: 0, mO: 0, mShout: 0, smile: 0, smirk: 0, mouth_w: 1, mouth_open: 0, teeth: 0, tongue: 1, blush: 0 };
const KEYS = Object.keys(DEF);
// the pack's numbers: the face's design and its expressions (calm — the character's own resting face, plain — the
// neutral one, then the sheet's joy, surprise, sad, anger)
export function configure(params, expr) {
  P = { ...params }; INK = P.ink; P.brow_c = mixc(P.hair, INK, 0.35);
  EXPR = {}; for (const [k, v] of Object.entries(expr)) EXPR[k] = { ...DEF, ...v };
  EXPR_NAMES = Object.keys(EXPR);
}

// ---------------------------------------------------------------- geometry (geo.py)
function bezier(ctrl, n) {
  const k = ctrl.length - 1, out = [], C = (n_, r) => { let c = 1; for (let i = 1; i <= r; i++) c = c * (n_ - r + i) / i; return c; };
  for (let i = 0; i < n; i++) { const t = i / (n - 1); let x = 0, y = 0;
    for (let j = 0; j <= k; j++) { const b = C(k, j) * (1 - t) ** (k - j) * t ** j; x += b * ctrl[j][0]; y += b * ctrl[j][1]; }
    out.push([x, y]); }
  return out;
}
function spline(pts, n) {
  const Pp = [[2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1]], ...pts, [2 * pts.at(-1)[0] - pts.at(-2)[0], 2 * pts.at(-1)[1] - pts.at(-2)[1]]];
  const out = [], segs = Pp.length - 3, per = Math.max(2, Math.floor(n / segs));
  for (let i = 0; i < segs; i++) { const [p0, p1, p2, p3] = Pp.slice(i, i + 4);
    for (let s = 0; s < per; s++) { const t = s / per, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(c => 0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3))); } }
  out.push(Pp.at(-2)); return out;
}
// a ribbon around a centre line with a width per point (a lid, a brow, a closed eye)
function ribbon(C, W) {
  const n = C.length, L = [], R = [];
  for (let i = 0; i < n; i++) { const a = C[Math.max(0, i - 1)], b = C[Math.min(n - 1, i + 1)]; let tx = b[0] - a[0], ty = b[1] - a[1]; const l = Math.hypot(tx, ty) || 1; tx /= l; ty /= l;
    const w = W[i] / 2; L.push([C[i][0] - ty * w, C[i][1] + tx * w]); R.push([C[i][0] + ty * w, C[i][1] - tx * w]); }
  return [...L, ...R.reverse()];
}
const tmpl = (cx, cy, uv, mirror) => uv.map(([u, v]) => [cx + (mirror ? -u : u), cy + v]);
const ellipse = (cx, cy, rx, ry, n = 40) => Array.from({ length: n }, (_, i) => { const t = 2 * Math.PI * i / n; return [cx + rx * Math.cos(t), cy + ry * Math.sin(t)]; });

// ---------------------------------------------------------------- the canvas
let G = null, LW = 0.02;
const path = (pts, close = true) => { const p = new Path2D(); pts.forEach(([x, y], i) => i ? p.lineTo(x, y) : p.moveTo(x, y)); if (close) p.closePath(); return p; };
const fill = (p, c, a = 1) => { G.globalAlpha = a; G.fillStyle = c; G.fill(p); G.globalAlpha = 1; };
const line = (pts, w, c = INK, a = 1) => { G.globalAlpha = a; G.strokeStyle = c; G.lineWidth = w; G.lineJoin = 'round'; G.lineCap = 'round'; G.stroke(path(pts, false)); G.globalAlpha = 1; };
const clip = (p, f) => { G.save(); G.clip(p); f(); G.restore(); };

// head.py Head.eye — one eye at side ±1 (the image's right is +x)
function eye(side, E) {
  const w = P.eye_w, h = P.eye_h, ex = P.eye_x, ey = P.eye_y, mirror = side < 0, cx = side * ex, cy = ey;
  const o = E.open * (1 - E.closedOpen);
  const up = bezier([[-0.5 * w, 0], [-0.28 * w, (0.95 - E.lid_in) * h * o], [0.22 * w, (1 - E.lid_out) * h * o], [0.5 * w, (0.35 - 0.3 * E.lid_out) * h * o]], 26);
  const raise = E.smile_eye * 0.35 * h;
  const lo = bezier([[-0.5 * w, 0], [-0.22 * w, -0.48 * h + raise], [0.25 * w, -0.46 * h + raise], [0.5 * w, (0.35 - 0.3 * E.lid_out) * h * o]], 26);
  for (const c of [up, lo]) for (const p of c) p[1] += P.eye_tilt * p[0] / w;
  if (E.closed > 0.5) {
    // joy: the eye shut in a soft upward arc
    const arc = bezier([[-0.5 * w, -0.1 * h], [-0.2 * w, 0.6 * h], [0.25 * w, 0.6 * h], [0.52 * w, -0.05 * h]], 24);
    const pts = tmpl(cx, cy, arc, mirror), th = pts.map((_, i) => Math.sin(0.15 + (Math.PI - 0.3) * i / (pts.length - 1)) * LW * 1.3 + LW * 0.5);
    fill(path(ribbon(pts, th)), INK); if (P.lashes) lashes(cx, cy, arc, mirror); return;
  }
  // a blink: the upper lid goes down onto the lower one
  const b = E.blink; for (let i = 0; i < up.length; i++) up[i][1] += (lo[i][1] - up[i][1]) * b;
  const whiteP = path(tmpl(cx, cy, [...up, ...lo.slice().reverse()], mirror));
  if (b < 0.97) clip(whiteP, () => {
    fill(whiteP, P.white);
    const lidSh = path(tmpl(cx, cy, [...up, ...up.slice().reverse().map(([u, v]) => [u, v - 0.22 * h])], mirror));
    fill(lidSh, mixc(P.white, '#8a8aa6', 0.35));
    const rw = P.iris_w * E.iris, rh = P.iris_h * E.iris;
    const icx = E.lx * 0.22 * w, icy = 0.42 * h * E.open + E.ly * 0.15 * h - (E.iris >= 1 ? 0 : 0.08 * h * (1 - E.iris) / 0.22);
    const irisP = path(ellipse(cx + icx, cy + icy, rw, rh));
    clip(irisP, () => {
      fill(irisP, P.iris);
      fill(path(ellipse(cx + icx, cy + icy - rh * 0.5, rw * 0.8, rh * 0.45)), mixc(P.iris, P.iris_light, 0.55));
      clip(lidSh, () => fill(irisP, mixc(P.iris, '#000000', 0.3)));
    });
    for (const [hx, hy, hr] of [[-0.35, 0.40, 0.24], [0.30, -0.35, 0.10]]) fill(path(ellipse(cx + icx + hx * rw, cy + icy + hy * rh, hr * rw, hr * rw, 16)), '#ffffff');
  });
  // the upper lid: a thick line, heavier toward the outer corner, a small flick past it
  const upl = [...up, [0.56 * w, up.at(-1)[1] - 0.06 * h * P.flick]];
  const pts = tmpl(cx, cy, upl, mirror), n = pts.length;
  const th = pts.map((_, i) => { const s = i / (n - 1); return LW * (0.6 + P.lid_w * Math.sin(Math.min(1, s * 1.05) * Math.PI * 0.85) ** 0.8); });
  th[n - 1] = LW * 0.4;
  fill(path(ribbon(pts, th)), INK);
  // the lower lid: a short thin stroke toward the outer corner
  const seg = lo.slice(Math.floor(lo.length * 0.40), Math.floor(lo.length * 0.96));
  line(tmpl(cx, cy, seg, mirror), LW * 0.6);
  const openA = Math.max(0, 1 - b * 1.6);
  if (P.crease && openA > 0) line(tmpl(cx, cy, up.slice(Math.floor(up.length * 0.2), Math.floor(up.length * 0.85)).map(([u, v]) => [u, v + 0.32 * h * P.crease]), mirror), LW * 0.45, INK, openA);
  if (P.lashes) lashes(cx, cy, up, mirror);
}
function lashes(cx, cy, up, mirror) {
  const w = P.eye_w;
  for (let j = 0; j < P.lashes; j++) { const i = up.length - 3 - j * 3; if (i < 1) break; const p = up[i];
    line(tmpl(cx, cy, [p, [p[0] + 0.07 * w, p[1] + 0.09 * w * (1 - j * 0.15)]], mirror), LW * 0.7); }
}

function brow(side, E) {
  const w = P.brow_w, bx = P.eye_x, by = P.eye_y + P.brow_y + E.brow_up * 0.08;
  const arch = P.brow_arch + E.brow_arch * 0.03, tilt = E.brow_in * 0.07;
  const uv = bezier([[-0.5 * w, -tilt], [-0.15 * w, arch - tilt * 0.4], [0.2 * w, arch], [0.5 * w, -0.03]], 20);
  const pts = tmpl(side * bx, by, uv, side < 0), n = pts.length;
  const th = pts.map((_, i) => LW * P.brow_th * (1 - 0.75 * i / (n - 1)) + LW * 0.3);
  fill(path(ribbon(pts, th)), P.brow_c);
}

// the nose's hook is drawn on the face's far side (side ±1); in profile the nose is in the outline, only its wing is drawn
function nose(s, profile) {
  const yt = P.nose_y, nw = P.nose_w, nl = P.nose_len;
  const pts = spline([[s * nw * 0.55, yt + nl], [s * nw * 0.95, yt + 0.035], [s * nw * 0.55, yt - 0.025], [s * nw * 0.05, yt - 0.03]], 20);
  line(profile ? pts.slice(pts.length >> 1) : pts, LW * 0.75);
}

// the mouth: the drawing's four (line, D, O, shout) as weights, their curves mixed
function mouth(E) {
  const my = P.mouth_y, mw = P.mouth_w * E.mouth_w, sm = E.smile * 0.06, n = 24;
  const U = Array.from({ length: n }, (_, i) => -mw + 2 * mw * i / (n - 1));
  const sq = u => Math.sqrt(Math.max(0, 1 - (u / mw) ** 2));
  const mo = E.mouth_open * 0.11;
  if (mo < 0.012) {
    // a crooked mouth (smirk): one corner pulled up and out, the other stays
    const v = U.map(u => sm * (u / mw) ** 2 - sm * 0.3 + P.mouth_curve * (1 - (u / mw) ** 2) + 0.07 * Math.abs(E.smirk) * Math.max(0, Math.min(1, E.smirk * u / mw)) ** 1.6);
    const pts = U.map((u, i) => [u, my + v[i]]);
    fill(path(ribbon(pts, pts.map((_, i) => LW * (0.45 + 0.55 * Math.sin(Math.PI * i / (n - 1)))))), INK);
  } else {
    const wsum = E.mD + E.mO + E.mShout + E.mLine || 1;
    // a line mouth opened by speech: the D's shape
    const kD = (E.mD + E.mLine) / wsum, kO = E.mO / wsum, kS = E.mShout / wsum;
    const top = U.map(u => kD * (my + sm * (u / mw) ** 2 * 0.8 + 0.01) + kO * (my + mo * 0.35 * sq(u)) + kS * (my + 0.012 * (1 - (u / mw) ** 2) - 0.03 * (u / mw) ** 2));
    const bot = U.map(u => kD * (my - mo * sq(u) + sm * (u / mw) ** 2 * 0.5) + kO * (my - mo * 0.75 * sq(u)) + kS * (my - mo * (1 - 0.35 * (u / mw) ** 2) - 0.03 * (u / mw) ** 2));
    const T = U.map((u, i) => [u, top[i]]), B = U.map((u, i) => [u, bot[i]]);
    const g = path([...T, ...B.slice().reverse()]);
    clip(g, () => {
      fill(g, P.mouth_c);
      // the tongue
      const tu = Array.from({ length: 14 }, (_, i) => -mw * 0.55 + mw * 1.1 * i / 13);
      const tb = tu.map(u => { const k = (u + mw) / (2 * mw) * (n - 1), i = Math.min(n - 2, Math.floor(k)), f = k - i; return bot[i] * (1 - f) + bot[i + 1] * f; });
      if (E.tongue > 0.05) fill(path([...tu.map((u, i) => [u, tb[i] + mo * 0.45]), ...tu.map((u, i) => [u, tb[i] - 0.01]).reverse()]), '#d9706e', Math.min(1, E.tongue));
      if (E.teeth > 0.05) fill(path([...T, ...T.map(([u, v]) => [u, v - 0.022 * Math.min(1, E.teeth)]).reverse()]), '#fbf6ef');
    });
    G.strokeStyle = INK; G.lineWidth = LW * 0.7; G.lineJoin = 'round'; G.stroke(g);
  }
  if (P.lower_lip && E.mouth_open <= 0.3) {
    const ll = P.lower_lip, uu = Array.from({ length: 10 }, (_, i) => -ll + 2 * ll * i / 9);
    line(uu.map(u => [u, my - 0.075 - E.mouth_open * 0.11 + 0.01 * (u / ll) ** 2]), LW * 0.5, INK, Math.min(1, (0.3 - E.mouth_open) / 0.1));
  }
}

// lines that are part of the face's design (tired lines under the eyes)
function marks() {
  for (const m of P.marks || []) for (const side of [-1, 1]) line(spline(m.pts.map(([x, y]) => [side * x, y]), 24), LW * m.w, INK, m.op);
}

function blush(E, scale) {
  const amt = Math.max(E.blush, P.blush); if (amt < 0.01) return;
  G.save(); G.filter = `blur(${(0.018 * scale).toFixed(2)}px)`;
  for (const side of [-1, 1]) fill(path(ellipse(side * (P.eye_x + 0.04), P.eye_y - 0.21, 0.12, 0.055, 30)), '#e8706a', 0.55 * amt);
  G.restore();
}

// one frame of the face. box: {x0, x1, y0, y1} head-local, px per unit; extra: lw — the line's width, shadow — the
// fringe's shadow on the forehead, noseSide and profile — how the head is turned from the camera
export function draw(ctx, E, box, px, extra = {}) {
  G = ctx; LW = extra.lw ?? 0.02;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  ctx.setTransform(px, 0, 0, -px, -box.x0 * px, box.y1 * px);
  if (extra.shadow) for (const poly of extra.shadow) fill(path(poly), SHADE(P.skin));
  blush(E, px); marks();
  for (const side of [-1, 1]) { eye(side, E); brow(side, E); }
  nose(extra.noseSide ?? 1, !!extra.profile); mouth(E);
}

// ---------------------------------------------------------------- time
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
// mouth shapes for speech: open, width change, round (→ the O), teeth
const VIS = { M: { o: 0, dw: -0.1, r: 0, tT: 0 }, F: { o: 0.14, dw: 0, r: 0, tT: 1 }, E: { o: 0.3, dw: 0.2, r: 0, tT: 0.8 },
  A: { o: 0.6, dw: 0.05, r: 0, tT: 0.3 }, O: { o: 0.5, dw: -0.35, r: 0.9, tT: 0 }, U: { o: 0.28, dw: -0.45, r: 1, tT: 0 } };

export class LiveFace {
  constructor(seed = 7) {
    this.seed = seed;
    const R = rng(seed);
    this.blinks = []; for (let t = 0.6 + R() * 1.5; t < 600;) { this.blinks.push(t); if (R() < 0.12) this.blinks.push(t + 0.24 + R() * 0.1); t += Math.max(0.9, lognorm(R, 2.8, 0.55)); }
    this.fix = []; let p = [0, 0];
    for (let t = 0.3; t < 600;) {
      const big = R() < 0.25, q = [gauss(R) * (big ? 0.35 : 0.16), gauss(R) * (big ? 0.3 : 0.14)];
      q[0] = Math.max(-0.6, Math.min(0.6, q[0])); q[1] = Math.max(-0.5, Math.min(0.5, q[1]));
      const amp = Math.hypot(q[0] - p[0], q[1] - p[1]) * 25;      // look units → degrees, roughly
      this.fix.push({ t, from: p, to: q, dur: (22 + 2.7 * amp) / 1000 }); p = q; t += Math.max(0.18, lognorm(R, 0.55, 0.5));
    }
    this.exprKeys = [{ t: -10, w: { calm: 1 } }];
    this.talkFrom = null; this.speech = null; this.lead = null;
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
    const dt = 1 / 200, n = Math.ceil((seq.at(-1).t - t0) / dt), out = new Float32Array(n * 4);
    let k = 0; const x = [0, 0, 0, 0], v = [0, 0, 0, 0], W = 34;
    for (let i = 0; i < n; i++) {
      const tt = t0 + i * dt; while (k + 1 < seq.length && seq[k + 1].t <= tt) k++;
      const g = VIS[seq[k].v], tg = [g.o, g.dw, g.r, g.tT];
      for (let c = 0; c < 4; c++) { const a = W * W * (tg[c] - x[c]) - 2 * W * v[c]; v[c] += a * dt; x[c] += v[c] * dt; out[i * 4 + c] = x[c]; }
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
      // the eyes turn the face's way: + look is toward the character's left (+x on the face)
      const tg = [Math.max(-0.8, Math.min(0.8, (yaw[j] - yaw[i]) * 2.2)), Math.max(-0.6, Math.min(0.6, -(pitch[j] - pitch[i]) * 2.0))];
      const t = i * dt;
      if (sac && t >= sac.t + sac.dur) { cur = sac.to; sac = null; }
      if (!sac && Math.hypot(tg[0] - cur[0], tg[1] - cur[1]) > 0.22) {
        const amp = Math.hypot(tg[0] - cur[0], tg[1] - cur[1]) * 25;
        sac = { t, from: cur, to: tg, dur: (22 + 2.7 * amp) / 1000 };
        if (Math.abs(tg[0] - cur[0]) > 0.4 && R() < 0.65) turnBlinks.push(t + 0.02);
      }
      if (sac) { const u = Math.min(1, (t - sac.t) / sac.dur), e = 1 - Math.pow(1 - u, 2.5); lx[i] = lerp(sac.from[0], sac.to[0], e); ly[i] = lerp(sac.from[1], sac.to[1], e); }
      else { const rate = 3.5 * dt; cur = [cur[0] + Math.max(-rate, Math.min(rate, tg[0] - cur[0])), cur[1] + Math.max(-rate, Math.min(rate, tg[1] - cur[1]))]; lx[i] = cur[0]; ly[i] = cur[1]; }
    }
    this.lead = { dt, lx, ly, turnBlinks };
  }
  // the face's numbers at time t (seconds)
  at(t, opts = {}) {
    const w = this.exprWeights(t), wb = this.exprWeights(t, 16);
    const mix = (k, ww = w) => { let s = 0, z = 0; for (const n of EXPR_NAMES) { s += ww[n] * EXPR[n][k]; z += ww[n]; } return s / (z || 1); };
    const E = {};
    for (const k of KEYS) E[k] = mix(k, k.startsWith('brow') ? wb : w);
    E.closedOpen = 0.9 * Math.min(1, (E.closed / 0.5) ** 3);   // a joy eye closes on its way to the arc (a mix keeps it open)
    let look = [E.lx, E.ly];
    const base = look.slice();
    let f = this.fix[0]; { let lo = 0, hi = this.fix.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (this.fix[m].t <= t) lo = m; else hi = m - 1; } f = this.fix[lo]; }
    const u = Math.min(1, Math.max(0, (t - f.t) / f.dur)), e = 1 - Math.pow(1 - u, 2.5);
    look = [look[0] + lerp(f.from[0], f.to[0], e) * 0.6, look[1] + lerp(f.from[1], f.to[1], e) * 0.6];
    let blink = 0;
    for (const b of this.blinks) { if (b > t) break; blink = Math.max(blink, blinkCurve(t - b)); }
    const ht = opts.headT ?? t;
    if (this.lead && ht != null && ht >= 0) {
      const i = Math.min(this.lead.lx.length - 1, Math.floor(ht / this.lead.dt));
      look = [look[0] + this.lead.lx[i], look[1] + this.lead.ly[i]];
      for (const b of this.lead.turnBlinks) { if (b > ht) break; blink = Math.max(blink, blinkCurve(ht - b)); }
    }
    look[0] = Math.max(-1, Math.min(1, look[0])); look[1] = Math.max(-0.9, Math.min(0.9, look[1]));
    if (this.still) { look = base; blink = 0; }
    E.lx = look[0]; E.ly = look[1]; E.blink = blink * (1 - Math.min(1, E.closed * 2));
    if (this.speech && t >= this.talkFrom && t < (this.talkTo ?? Infinity)) {
      const S = this.speech, i = Math.floor((t - this.talkFrom) / S.dt) % S.n, o = S.out;
      E.mouth_open = Math.max(0, o[i * 4]) + E.mouth_open * 0.3;
      E.mouth_w = E.mouth_w * (1 + o[i * 4 + 1]);
      const r = Math.max(0, Math.min(1, o[i * 4 + 2]));
      const sum = E.mLine + E.mD + E.mO + E.mShout || 1;
      E.mO = lerp(E.mO / sum, 1, r); E.mD = (E.mD + E.mLine) / sum * (1 - r); E.mShout = E.mShout / sum * (1 - r) * 0.4; E.mLine = 0;
      E.teeth = Math.max(E.teeth * 0.5, o[i * 4 + 3]);
    }
    E.jaw = Math.max(0, E.mouth_open - 0.1) * (1 - 0.4 * E.mO);
    return E;
  }
}
