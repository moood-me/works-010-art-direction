// Кира's face of paper pieces, alive. The drawing's own code (styles/s14-paper/tools: kit.py's pieces — a cut outline,
// its cast shadow, the crisp contact shadow, the light rim of the sheet's thickness —, face.py's eye with the lid
// piece and the lash sliver, brow, cheeks, mouth; kira.py's SPEC and expressions) is carried over line for line and
// drawn into a canvas the head takes by its front projection (head_front's units −128…128, y down). The nose and the
// ears are real pieces of the model. Every frame the pieces are cut again from a few numbers:
//   expression — the sheet's five (calm, joy = a smirk, surprise, sad, angry), blended number by number over 0.35 s;
//   blink      — the lid piece comes down: uneven intervals (most 2–6 s, now and then a double), closing ~70 ms,
//                opening ~150 ms; also when the head turns fast;
//   gaze       — her resting look is sideways; small quick jumps (saccades) round it; before a head turn the eyes go
//                first (read off the motion 0.25 s ahead);
//   speech     — syllables of mouth shapes with pauses; her mouth opens little (she mutters).
// Schedules come from a seeded random stream: a moment t always looks the same (films, scrubbing).

const SH = [43, 27, 44];
const LIFT = { 1: [1.3, 2.2, 1.3, 0.40], 2: [2.8, 4.6, 2.8, 0.36], 3: [5.5, 9.5, 5.5, 0.32] };
const SPEC = { skin: '#ecd3bf', eye_y: 12, eye_gap: 31, eye_w: 14.5, eye_h: 11.5, iris: '#6d6688', lid: '#c9a3ab', lash_col: '#231b26',
  brow: '#2b2330', brow_w: 7, brow_len: 28, brow_y: -23, mouth_y: 66, mouth_w: 15, lip: '#a9566a', inside: '#5c1a22',
  cheek: '#dc8a9c', cheek_r: 13, cheek_op: 0.22, ry: 98 };
// face.py: EXPR + kira.py: rest / on. The mouth as numbers: bend (+ smile, − frown), thick, smirk (one corner up), pout
const M = { flat: { bend: -0.03, thick: 0.20, smirk: 0, pout: 0 }, smirk: { bend: 0.10, thick: 0.22, smirk: 1, pout: 0 },
  frown: { bend: -0.34, thick: 0.24, smirk: 0, pout: 0 }, pout: { bend: 0, thick: 0.2, smirk: 0, pout: 1 } };
export const EXPRS = {
  calm: { open: 0.62, tilt: -0.2, brow: -0.3, brow_dy: 4, low: 0, eye: 1, look: 0.9, look_y: 0, ...M.flat },
  joy: { open: 0.7, tilt: 0, brow: -0.05, brow_dy: 0, low: 0, eye: 1, look: 0.6, look_y: 0, ...M.smirk },
  surprise: { open: 1.0, tilt: 0, brow: 0.12, brow_dy: -15, low: 0, eye: 1.1, look: 0, look_y: 0, ...M.pout },
  sad: { open: 0.62, tilt: 0.5, brow: 0.55, brow_dy: -3, low: 0, eye: 1, look: 0, look_y: 0.8, ...M.frown },
  angry: { open: 0.60, tilt: -0.55, brow: -0.6, brow_dy: 9, low: 0.25, eye: 0.95, look: 0, look_y: 0, ...M.frown },
};
const KEYS = Object.keys(EXPRS.calm);

// ---------- kit.py ----------
const corner = p => [p[0], p[1], 1];
function pathOf(pts) {          // kit.path_d: a closed curve through the points; (x, y, 1) is a corner
  const n = pts.length, P = pts, C = pts.map(p => p.length > 2 && p[2]), d = new Path2D();
  d.moveTo(P[0][0], P[0][1]);
  for (let i = 0; i < n; i++) {
    const p0 = P[(i - 1 + n) % n], p1 = P[i], p2 = P[(i + 1) % n], p3 = P[(i + 2) % n], c1c = C[i], c2c = C[(i + 1) % n];
    if (c1c && c2c) { d.lineTo(p2[0], p2[1]); continue; }
    const c1 = c1c ? p1 : [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = c2c ? p2 : [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]);
  }
  d.closePath(); return d;
}
function ell(cx, cy, rx, ry = rx, rot = 0, n = 10) {
  const c = Math.cos(rot * Math.PI / 180), s = Math.sin(rot * Math.PI / 180), out = [];
  for (let i = 0; i < n; i++) { const a = 2 * Math.PI * i / n, x = rx * Math.cos(a), y = ry * Math.sin(a); out.push([cx + x * c - y * s, cy + x * s + y * c]); }
  return out;
}
function strip(path, w) {
  const n = path.length, ws = Array.isArray(w) ? w : path.map(() => w), L = [], R = [];
  path.forEach(([x, y], i) => {
    const [x0, y0] = path[Math.max(i - 1, 0)], [x1, y1] = path[Math.min(i + 1, n - 1)];
    const dx = x1 - x0, dy = y1 - y0, dl = Math.hypot(dx, dy) || 1, nx = -dy / dl, ny = dx / dl, h = ws[i] / 2;
    L.push([x + nx * h, y + ny * h]); R.push([x - nx * h, y - ny * h]);
  });
  return [corner(L[0]), ...L.slice(1, -1), corner(L[n - 1]), corner(R[n - 1]), ...R.slice(1, -1).reverse(), corner(R[0])];
}
class Paper {
  constructor(ctx, S) { this.c = ctx; this.S = S; }
  // a piece standing `lift` above what is under it: its cast shadow, the contact shadow, the piece, the light rim
  card(pts, fill, lift = 1, op = 1) {
    const c = this.c, S = this.S, p = pathOf(pts), [dx, dy, b, o] = LIFT[lift];
    c.globalAlpha = op;
    c.save(); c.translate(0.7, 1); c.fillStyle = `rgba(${SH},0.5)`; c.fill(p); c.restore();
    c.save(); c.shadowColor = `rgba(${SH},${o})`; c.shadowBlur = b * 2 * S; c.shadowOffsetX = dx * S; c.shadowOffsetY = dy * S; c.fillStyle = fill; c.fill(p); c.restore();
    c.save(); c.clip(p); const r = new Path2D(); r.rect(-200, -200, 400, 400); c.translate(0.9, 1.1); r.addPath(p);
    c.fillStyle = 'rgba(255,255,255,0.42)'; c.fill(r, 'evenodd'); c.restore();
    c.globalAlpha = 1;
  }
  flat(pts, fill, op = 1) { const c = this.c; c.globalAlpha = op; c.fillStyle = fill; c.fill(pathOf(pts)); c.globalAlpha = 1; }
}

// ---------- face.py ----------
function eye(P, cx, cy, e, side) {
  const w = SPEC.eye_w * e.eye, h = SPEC.eye_h * e.eye, o = e.open, n = 9;
  P.card(ell(cx, cy, w, h), '#fbf6ea', 1);
  const look = Math.max(-1.25, Math.min(1.25, e.look)) * w * 0.3, ir = Math.min(h * 0.82, w * 0.62), iy = cy + h * 0.06 + Math.max(-1, Math.min(1, e.look_y)) * h * 0.3;
  // the iris and pupil are glued flush on the white: cut by its outline
  const c = P.c; c.save(); c.clip(pathOf(ell(cx, cy, w, h)));
  P.flat(ell(cx + look, iy, ir, ir), SPEC.iris); P.flat(ell(cx + look, iy, ir * 0.52, ir * 0.52, 0, 8), '#241a1c');
  P.flat(ell(cx + look - ir * 0.38, iy - ir * 0.42, ir * 0.27, ir * 0.27, 20, 4).map(corner), '#fffaf0');
  c.restore();
  const k = 2 * Math.min(o, 1) - 1, tilt = e.tilt * side, edge = [], top = [];
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1), s = Math.sin(Math.PI * t), x = cx - w * 1.16 + 2.32 * w * t;
    edge.push([x, cy + h * 0.12 - (h * k + h * 0.12) * s + tilt * h * (t - 0.5) * 1.5]);
    top.push([x, cy + h * 0.12 - h * 1.42 * Math.pow(s, 0.75) - h * 0.05]);
  }
  if (o < 1.05) {
    P.card([corner(top[0]), ...top.slice(1, -1), corner(top[n - 1]), ...edge.slice(1, -1).reverse()], SPEC.lid, 1);
    const th = h * 0.26, low = edge.map(([x, y], i) => [x, y + th * Math.pow(Math.sin(Math.PI * i / (n - 1)), 0.6)]);
    const [ox, oy] = side > 0 ? edge[n - 1] : edge[0], flick = [ox + side * w * 0.34, oy - h * 0.42, 1], lr = low.slice(1, -1).reverse();
    const body = side > 0 ? [...edge.slice(0, -1), flick, [ox, oy + th * 0.5], ...lr] : [flick, ...edge.slice(1), ...lr, [ox, oy + th * 0.5]];
    P.flat(body, SPEC.lash_col);
  }
  if (e.low > 0.01) {
    const up = [], dn = [];
    for (let i = 0; i < n; i++) { const s = Math.sin(Math.PI * i / (n - 1)), x = cx - w * 1.25 + 2.5 * w * i / (n - 1); up.push([x, cy + h * (1.05 - 0.95 * e.low * s)]); dn.push([x, cy + h * (1.05 + 0.55 * s)]); }
    P.card([corner(up[0]), ...up.slice(1, -1), corner(up[n - 1]), ...dn.slice(1, -1).reverse()], '#ecd0bc', 1);
  }
}
function brow(P, cx, cy, e, side) {
  const L = SPEC.brow_len, w = SPEC.brow_w, tl = e.brow, xi = cx - side * L * 0.5, xo = cx + side * L * 0.55;
  const yi = cy + e.brow_dy - tl * 13, yo = cy + e.brow_dy + tl * 6 + 3, arch = -7 + 5 * Math.max(0, Math.min(1, -tl * 4));
  P.card(strip([[xi, yi], [(xi + xo) / 2, (yi + yo) / 2 + arch], [xo, yo]], [w, w * 0.9, w * 0.35]), SPEC.brow, 1);
}
function mouth(P, x, y, e, talk) {
  const w = SPEC.mouth_w, n = 11, S = t => Math.sin(Math.PI * t);
  const lens = (x0, x1, up, lo) => {
    const a = [], b = [];
    for (let i = 0; i < n; i++) { const t = i / (n - 1); a.push([x0 + (x1 - x0) * t, y + up(t)]); b.push([x0 + (x1 - x0) * t, y + lo(t)]); }
    return [corner(a[0]), ...a.slice(1, -1), corner(a[n - 1]), ...b.slice(1, -1).reverse()];
  };
  // bend > 0: the middle sags — a smile; bend < 0: the middle rises — a frown
  const upf = t => e.bend * w * S(t) - e.smirk * 0.42 * w * Math.pow(t, 2.2), lof = t => upf(t) + e.thick * w * S(t);
  if (talk && talk[0] > 0.06) {       // a speaking mouth: a dark piece between thin lips, teeth when wide
    const [o, wd, rd] = talk, W = w * wd * (1 - 0.35 * rd), H = w * 0.62 * o;
    const tu = t => upf(t) * 0.6 - H * 0.25 * S(t), tl = t => upf(t) * 0.6 + H * Math.pow(S(t), 0.8);
    P.card(lens(x - W - 1.2, x + W + 1.2, t => tu(t) - 1.6 * S(t), t => tl(t) + 1.8 * S(t)), SPEC.lip, 1);
    P.flat(lens(x - W, x + W, tu, tl), SPEC.inside);
    if (o > 0.4) P.flat(lens(x - W * 0.8, x + W * 0.8, t => tu(t) * 1, t => tu(t) + H * 0.22 * S(t)), '#fbf6ea');
    return;
  }
  let pts = lens(x - w, x + w, upf, lof);
  if (e.pout > 0.01) {          // the lens's points go over to the pout's oval
    const k = pts.length, u = e.pout;
    pts = pts.map((p, i) => { const a = Math.PI + 2 * Math.PI * i / k, tx = x + w * 0.42 * Math.cos(a), ty = y + w * 0.26 * Math.sin(a);
      const o = [p[0] + (tx - p[0]) * u, p[1] + (ty - p[1]) * u]; if (p[2] && u < 0.6) o.push(1); return o; });
  }
  P.card(pts, SPEC.lip, 1);
}

// ---------- the timeline (Р3's) ----------
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const ease = u => u <= 0 ? 0 : u >= 1 ? 1 : u * u * (3 - 2 * u);
function lid(dt) { if (dt < 0) return 1; if (dt < 0.07) return 1 - ease(dt / 0.07); if (dt < 0.1) return 0; if (dt < 0.25) return ease((dt - 0.1) / 0.15); return 1; }

export class LiveFace {
  constructor({ seed = 14, length = 120 } = {}) {
    const r = rng(seed); this.length = length;
    this.blinks = [];
    for (let t = 1.1 + r() * 1.5; t < length;) {
      this.blinks.push(t);
      if (r() < 0.12) this.blinks.push(t + 0.32 + r() * 0.12);
      t += 1.4 + (-Math.log(r() * r() + 1e-9) / 2) * 2.8;
    }
    // saccades: fixations of 0.3–2.4 s; mostly small jumps round her sideways look, now and then a glance across
    this.sacc = [{ t: 0, x: 0, y: 0 }];
    for (let t = 0.8 + r(); t < length; t += 0.3 + r() * r() * 2.4 + r() * 0.5)
      this.sacc.push(r() < 0.18 ? { t, x: -1.3 - r() * 0.5, y: (r() - 0.5) * 0.5 } : { t, x: (r() - 0.6) * 0.7, y: (r() - 0.4) * 0.7 });
    const V = { a: [0.8, 1.0, 0.2], e: [0.45, 1.1, 0], i: [0.3, 1.05, 0], o: [0.7, 0.7, 1], u: [0.4, 0.55, 1] };
    const C = { m: [0, 0.9, 0.2], f: [0.12, 0.95, 0], t: [0.25, 1, 0.2], k: [0.35, 0.95, 0.4], s: [0.18, 1.05, 0] };
    const vk = Object.keys(V), ck = Object.keys(C);
    this.speech = [];
    for (let t = 0.4; t < length;) {
      const n = 2 + Math.floor(r() * 6);
      for (let i = 0; i < n; i++) {
        const c = C[ck[Math.floor(r() * ck.length)]], v = V[vk[Math.floor(r() * vk.length)]], dc = 0.06 + r() * 0.05, dv = 0.1 + r() * 0.12;
        this.speech.push({ t, d: dc, s: c }); t += dc; this.speech.push({ t, d: dv, s: v }); t += dv;
      }
      const d = 0.35 + r() * 0.9; this.speech.push({ t, d, s: [0, 0.9, 0.2] }); t += d;
    }
    this.extraBlinks = []; this.expr = [{ t: 0, name: 'calm' }]; this.talking = false; this.lead = null; this.still = false;
  }
  setExpressions(list) { this.expr = list.length ? list : [{ t: 0, name: 'calm' }]; }
  setHeadTurns(times) { this.extraBlinks = times.slice(); }
  // the expression's numbers at t: each change blends over 0.35 s; a list item may be {t, mix: {name: weight}}
  exprAt(t) {
    const num = it => { if (it.mix) { const o = {}; let s = 0; for (const w of Object.values(it.mix)) s += w;
      for (const k of KEYS) { o[k] = 0; for (const [nm, w] of Object.entries(it.mix)) o[k] += EXPRS[nm][k] * w / (s || 1); } return o; } return EXPRS[it.name]; };
    let i = 0; while (i + 1 < this.expr.length && this.expr[i + 1].t <= t) i++;
    const b = num(this.expr[i]); if (i === 0) return { ...b };
    const a = num(this.expr[i - 1]), u = ease((t - this.expr[i].t) / 0.35), o = {};
    for (const k of KEYS) o[k] = a[k] + (b[k] - a[k]) * (k === 'brow' || k === 'brow_dy' ? ease(Math.min(1, (t - this.expr[i].t) / 0.26)) : u);   // the brows go first
    return o;
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
    const k = dt < 0.04 ? ease(dt / 0.04) * 1.1 : dt < 0.1 ? 1.1 - 0.1 * ease((dt - 0.04) / 0.06) : 1;
    let x = p.x + (s.x - p.x) * k, y = p.y + (s.y - p.y) * k, lead = 0;
    if (this.lead) { const a = this.lead(t); lead = Math.max(-1, Math.min(1, a * 3.2)); x *= 1 - Math.min(1, Math.abs(a) * 3); }
    return [x, y, lead];
  }
  mouthAt(t) {
    if (!this.talking) return null;
    const S = this.speech; let i = 0, lo = 0, hi = S.length - 1;
    while (lo <= hi) { const m = (lo + hi) >> 1; if (S[m].t <= t) { i = m; lo = m + 1; } else hi = m - 1; }
    const cur = S[i], prev = i > 0 ? S[i - 1] : cur, u = ease((t - cur.t) / Math.min(0.07, cur.d * 0.6));
    return [0, 1, 2].map(k => prev.s[k] + (cur.s[k] - prev.s[k]) * u);
  }
  // draw the face at time t into a 2D canvas (square; head units −128…128)
  draw(ctx, t) {
    const S = ctx.canvas.width / 256, P = new Paper(ctx, S);
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.setTransform(S, 0, 0, S, 128 * S, 128 * S);
    const e = this.exprAt(t), ey = SPEC.eye_y, g = SPEC.eye_gap;
    if (!this.still) {
      const [gx, gy, lead] = this.gazeAt(t);
      e.look = e.look * (1 - Math.abs(lead)) + gx + lead * 1.2; e.look_y += gy;
      e.open *= this.openAt(t);
    }
    for (const side of [-1, 1]) P.flat(ell(side * g * 1.42, ey + SPEC.ry * 0.36 - (e.low > 0.3 ? 4 : 0), SPEC.cheek_r, SPEC.cheek_r), SPEC.cheek, SPEC.cheek_op);
    for (const side of [-1, 1]) { eye(P, side * g, ey, e, side); brow(P, side * (g + 2), ey + SPEC.brow_y, e, side); }
    mouth(P, 0, SPEC.mouth_y, e, this.mouthAt(t));
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
  }
}
