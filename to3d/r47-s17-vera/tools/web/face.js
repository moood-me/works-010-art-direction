// Вера's face, drawn — a port of the style's own drawing code (styles/s17-bilibin/tools: kit.py's line, parts.py's
// head volume, eye, brow, nose, mouth; vera.py's glasses) from Python/SVG to a 2D canvas. The 3D head carries no
// features: every frame they are drawn anew from a few numbers at the head's real place and turn, the way the
// drawing draws them at any yaw (an eye stays an almond when the head turns; the nose is a line in front and a
// contour in three-quarter).
// Head units: eye line y = 0, y down, z toward the viewer, x to her left. A `sheet` is given by the caller:
//   sheet.pt(x, y, z) → the point on the picture in sheet coordinates (head units, the face turned to the sheet's
//   left: the caller mirrors when she looks right), sheet.yaw (degrees, ≥ 0), sheet.lw (the line's weight factor).

// ---------------------------------------------------------------- kit.py: curves
function crRun(p, n, closed) {
  const m = p.length;
  if (m < 3 && !closed) {
    if (m === 2) { const o = []; for (let i = 0; i <= n; i++) o.push([p[0][0] + (p[1][0] - p[0][0]) * i / n, p[0][1] + (p[1][1] - p[0][1]) * i / n]); return o; }
    return p.slice();
  }
  const out = [], spans = closed ? m : m - 1;
  for (let i = 0; i < spans; i++) {
    let p0, p1, p2, p3;
    if (closed) { p0 = p[(i - 1 + m) % m]; p1 = p[i]; p2 = p[(i + 1) % m]; p3 = p[(i + 2) % m]; }
    else {
      p1 = p[i]; p2 = p[i + 1];
      p0 = i > 0 ? p[i - 1] : [2 * p1[0] - p2[0], 2 * p1[1] - p2[1]];
      p3 = i + 2 < m ? p[i + 2] : [2 * p2[0] - p1[0], 2 * p2[1] - p1[1]];
    }
    for (let k = 0; k < n; k++) {
      const t = k / n, t2 = t * t, t3 = t2 * t, q = [0, 0];
      for (const a of [0, 1]) q[a] = 0.5 * (2 * p1[a] + (-p0[a] + p2[a]) * t + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t2 + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t3);
      out.push(q);
    }
  }
  if (!closed) out.push([p[m - 1][0], p[m - 1][1]]);
  return out;
}
export function curve(pts, closed = false, n = 6) {
  let xy = pts.map(p => [p[0], p[1]]);
  let corners = []; pts.forEach((p, i) => { if (p[2] === 'c') corners.push(i); });
  if (!corners.length) return crRun(xy, n, closed);
  if (closed) { const k = corners[0]; xy = [...xy.slice(k), ...xy.slice(0, k), xy[k]]; corners = [...corners.map(c => c - k), xy.length - 1]; }
  else corners = [...new Set([0, ...corners, xy.length - 1])].sort((a, b) => a - b);
  let out = [];
  for (let i = 0; i + 1 < corners.length; i++) { const run = crRun(xy.slice(corners[i], corners[i + 1] + 1), n, false); out = out.concat(out.length ? run.slice(1) : run); }
  if (closed) out.pop();
  return out;
}
function taperPoly(sm, w, prof) {
  const s = [0]; for (let i = 1; i < sm.length; i++) s.push(s[i - 1] + Math.hypot(sm[i][0] - sm[i - 1][0], sm[i][1] - sm[i - 1][1]));
  const tot = s[s.length - 1] || 1, n = sm.length, L = [], R = [];
  for (let i = 0; i < n; i++) {
    const t = s[i] / tot;
    const wd = prof === 'swell' ? w * (0.15 + 0.85 * Math.sin(Math.PI * t) ** 0.8) : w * (1 - t) ** 0.8 * Math.min(1, t / 0.08 + 0.35);
    const a = sm[Math.max(0, i - 1)], b = sm[Math.min(n - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], ln = Math.hypot(dx, dy) || 1, hw = wd / 2;
    L.push([sm[i][0] + dy / ln * hw, sm[i][1] - dx / ln * hw]); R.push([sm[i][0] - dy / ln * hw, sm[i][1] + dx / ln * hw]);
  }
  return L.concat(R.reverse());
}

// the Doc of kit.py on a canvas context (already transformed to sheet coordinates)
export const INK = '#1d1712';
class Doc {
  constructor(g, lw) { this.g = g; this.lw = lw; this.LINE = 3.2; this.THIN = 1.7; }
  path(sm, closed) { const g = this.g; g.beginPath(); g.moveTo(sm[0][0], sm[0][1]); for (let i = 1; i < sm.length; i++) g.lineTo(sm[i][0], sm[i][1]); if (closed) g.closePath(); }
  fill(pts, color, n = 6, op = 1) { const sm = curve(pts, true, n); this.path(sm, true); this.g.globalAlpha = op * this.alpha; this.g.fillStyle = color; this.g.fill(); this.g.globalAlpha = this.alpha; return sm; }
  ink(pts, w, closed = false, color = INK, n = 6, op = 1) {
    const sm = curve(pts, closed, n), g = this.g; this.path(sm, closed);
    g.globalAlpha = op * this.alpha; g.strokeStyle = color; g.lineWidth = (w ?? this.LINE) * this.lw; g.lineJoin = 'round'; g.lineCap = 'round'; g.stroke(); g.globalAlpha = this.alpha; return sm;
  }
  thin(pts, o = {}) { return this.ink(pts, this.THIN * (o.k ?? 1), false, o.color ?? INK, 6, o.op ?? 1); }
  lock(pts, w = 4, color = INK, prof = 'taper') { const poly = taperPoly(curve(pts, false, 6), w * this.lw, prof); this.path(poly, true); this.g.fillStyle = color; this.g.fill(); }
  dot(x, y, r, color = INK) { const g = this.g; g.beginPath(); g.arc(x, y, Math.max(0, r), 0, 7); g.fillStyle = color; g.fill(); }
  ellipse(x, y, rx, ry, color, op = 1) { const g = this.g; g.beginPath(); g.ellipse(x, y, Math.max(0, rx), Math.max(0, ry), 0, 0, 7); g.globalAlpha = op * this.alpha; g.fillStyle = color; g.fill(); g.globalAlpha = this.alpha; }
  clipped(pts, fn) { const g = this.g; g.save(); this.path(curve(pts, true, 6), true); g.clip(); fn(); g.restore(); }
}
Doc.prototype.alpha = 1;

// ---------------------------------------------------------------- parts.py: the head's volume
function interp(tab, y) {
  const n = tab.length;
  if (y <= tab[0][0]) return tab[0][1];
  if (y >= tab[n - 1][0]) return tab[n - 1][1];
  const xs = tab.map(t => t[0]), vs = tab.map(t => t[1]), dk = [];
  for (let i = 0; i < n - 1; i++) dk.push((vs[i + 1] - vs[i]) / ((xs[i + 1] - xs[i]) || 1e-6));
  const m = [dk[0]]; for (let i = 1; i < n - 1; i++) m.push(dk[i - 1] * dk[i] <= 0 ? 0 : (dk[i - 1] + dk[i]) / 2); m.push(dk[n - 2]);
  for (let i = 0; i < n - 1; i++) {
    if (dk[i] === 0) { m[i] = m[i + 1] = 0; }
    else { const a = m[i] / dk[i], b = m[i + 1] / dk[i], h = a * a + b * b; if (h > 9) { const t = 3 / Math.sqrt(h); m[i] = t * a * dk[i]; m[i + 1] = t * b * dk[i]; } }
  }
  let i = 0; while (xs[i + 1] < y) i++;
  const h = xs[i + 1] - xs[i], t = (y - xs[i]) / h, t2 = t * t, t3 = t2 * t;
  return (2 * t3 - 3 * t2 + 1) * vs[i] + (t3 - 2 * t2 + t) * h * m[i] + (-2 * t3 + 3 * t2) * vs[i + 1] + (t3 - t2) * h * m[i + 1];
}
export class Head {
  constructor(c) { Object.assign(this, c); }
  a(y) { const c = this; return interp([[c.crown, 6], [c.crown + 12, 42], [c.crown + 34, c.skull * 0.93], [-50, c.skull], [-20, c.temple], [8, c.cheek], [30, c.cheek * 0.6 + c.jaw * 0.4], [c.jaw_y, c.jaw], [c.chin - 20, c.chin_w + 17], [c.chin - 9, c.chin_w + 7], [c.chin - 3, c.chin_w * 0.7], [c.chin, 1]], y); }
  bf(y) { const c = this; return y < -78 ? interp([[c.crown, 6], [c.crown + 14, 40], [c.crown + 36, c.forehead * 0.8], [-78, c.forehead * 0.9]], y) : this.zm(y); }
  zm(y) { const c = this; return interp([[-78, c.forehead * 0.9], [-55, c.forehead], [c.brow_y + 4, c.brow_z], [2, c.brow_z - 7], [c.nose_y, c.brow_z - 5], [c.mouth_y - 4, c.lip_z], [c.mouth_y + 12, c.chin_z - 6], [c.chin - 10, c.chin_z], [c.chin, c.chin_z - 14]], y); }
  zf(y) {
    const c = this, n0 = c.nose_y;
    return interp([[-78, c.forehead * 0.9], [-55, c.forehead], [c.brow_y + 4, c.brow_z], [-2, c.brow_z - 5], [n0 - 22, c.brow_z - 2 + (c.nose_z - c.brow_z) * 0.35],
      [n0 - 3, c.nose_z], [n0 + 4, c.nose_z - 6], [n0 + 9, c.lip_z - 4], [c.mouth_y - 5, c.lip_z], [c.mouth_y + 1, c.lip_z - 6], [c.mouth_y + 7, c.lip_z - 3],
      [c.mouth_y + 14, c.chin_z - 8], [c.chin - 10, c.chin_z], [c.chin, c.chin_z - 12]], y);
  }
  zs(x, y) {
    const a = this.a(y), u = Math.min(1, Math.abs(x) / Math.max(a, 1));
    let base = this.bf(y) * (1 - u ** 2.4) ** (1 / 2.4);
    if (y > -78) {
      const extra = this.zf(y) - this.zm(y);
      if (extra > 0) { const k = Math.max(0, 1 - Math.abs(x) / (y < this.nose_y + 8 ? this.nose_w * 1.3 : this.mouth_w * 1.3)); base += extra * k * k * (3 - 2 * k); }
    }
    return base;
  }
}

// ---------------------------------------------------------------- expressions as numbers (parts.EXPR; Вера's calm from vera.py)
const CALM = { brow: -1, tilt: -1.5, open: 0.8, smile: -0.1, mouth: 0, wide: 0.95, round: 0, teeth: 0, cheeks: 0, smirk: 0 };
export const EXPR = {
  calm: CALM,
  joy: { ...CALM, brow: 4, tilt: -1, open: 0.45, smile: 1.0, mouth: 0.55, wide: 1.25, cheeks: 1 },
  surprise: { ...CALM, brow: 10, tilt: 1.5, open: 1.35, smile: 0.0, mouth: 0.6, wide: 0.7, round: 1 },
  sad: { ...CALM, brow: 3, tilt: 5, open: 0.75, smile: -0.6, mouth: 0.0, wide: 0.85, lookY: 2.5 },
  anger: { ...CALM, brow: -5, tilt: -6, open: 0.85, smile: -0.7, mouth: 0.35, wide: 1.1, teeth: 1 },
};
// brow…smirk: the drawing's numbers; lookX/lookY: the iris moved (head units); blink 0…1; jaw, swide, pucker: speech
export const PARAMS = ['brow', 'tilt', 'open', 'smile', 'mouth', 'wide', 'round', 'teeth', 'cheeks', 'smirk', 'lookX', 'lookY', 'blink', 'jaw', 'swide', 'pucker'];
export function mix(w) {
  const out = {}; for (const k of PARAMS) out[k] = 0;
  let tot = 0; for (const k in w) tot += w[k];
  const ws = { ...w }; if (tot < 1) ws.calm = (ws.calm || 0) + 1 - tot;
  tot = Math.max(tot, 1);
  for (const k in ws) { const e = EXPR[k]; if (!e) continue; for (const p in e) out[p] += e[p] * ws[k] / tot; }
  return out;
}

// ---------------------------------------------------------------- parts.py: the features
function eye(d, v, side, e, p) {
  const x0 = p.eye_x * side, f = v.facing(x0, 0);
  if (f < 0.22) return;
  const [cx, cy] = v.surf(x0, 0, -6);
  const w = p.eye_w * (0.25 + 0.75 * f);
  const op = e.open * (1 - e.blink), h = p.eye_h * op, inner = -side, tilt = p.eye_tilt;
  const ic = [cx + inner * w * 0.5 * (v.yaw < 60 ? 1 : 0.6), cy + 1.5], oc = [cx - inner * w * 0.5, cy - tilt];
  const top = [ic, [cx + inner * w * 0.2, cy - h * 1.05], [cx - inner * w * 0.18, cy - h * 1.0], oc];
  const bot = [oc, [cx - inner * w * 0.1, cy + h * 0.55 + 1], [cx + inner * w * 0.25, cy + h * 0.45 + 1], ic];
  const under = () => { for (let i = 0; i < p.under; i++) d.thin([[cx + inner * w * 0.35, cy + p.eye_h * e.open * 0.9 + 3 + 4 * i], [cx, cy + p.eye_h * e.open * 1.15 + 4 + 4 * i], [cx - inner * w * 0.4, cy + p.eye_h * e.open * 0.6 + 3 + 4 * i]], { k: 0.6, op: 0.65 }); };
  if (op < 0.25) {
    // shut: with laughter an arc up (the drawing's); in a blink the lid lies down on the lower line
    const laugh = e.blink < 0.5 ? 1 : 0;
    d.ink([ic, laugh ? [cx, cy - 4 - 3 * e.smile] : [cx, cy + p.eye_h * e.open * 0.5 + 1.5], oc], p.lid * 2.6);
    if (!laugh) { for (let i = 0; i < p.lashes; i++) { const t = i / Math.max(1, p.lashes - 1); d.lock([[oc[0] + inner * w * 0.15 * t, oc[1] + 1], [oc[0] + inner * w * 0.15 * t - inner * 4, oc[1] + 3.5 + 1.5 * t]], 2.2); } under(); }
    return;
  }
  const eyePts = top.concat(bot.slice(1, -1));
  d.fill(eyePts, '#fbf6ea');
  const ir = p.iris * (0.6 + 0.4 * f) * (e.round > 0.5 ? 0.85 : 1);
  const ix = cx + e.lookX + (-v.s * w * 0.18), iy = cy - h * 0.12 + e.lookY;
  d.clipped(eyePts, () => {
    d.ellipse(ix, iy, ir * (0.7 + 0.3 * f), ir, p.iris_col);
    d.dot(ix, iy, ir * 0.48, INK);
    d.dot(ix + ir * 0.35, iy - ir * 0.4, ir * 0.22, '#fffaf0');
  });
  d.ink(top, 2.6 * p.lid);
  d.thin(bot, { k: 0.8 });
  if (op > 0.6) d.thin([[ic[0] - inner * w * -0.05, ic[1] - h * 0.9], [cx, cy - h * 1.75], [oc[0] + inner * 1.5, oc[1] - h * 1.1]], { k: 0.7, op: 0.7 * Math.min(1, (op - 0.6) / 0.1) });
  for (let i = 0; i < p.lashes; i++) { const t = i / Math.max(1, p.lashes - 1), bx = oc[0] + inner * w * 0.15 * t, by = oc[1] - h * 0.2 * t; d.lock([[bx, by], [bx - inner * 4, by - 4 - 1.5 * t]], 2.2); }
  under();
}
function brow(d, v, side, e, p) {
  const x0 = p.eye_x * side, f = v.facing(x0, p.brow_y);
  if (f < 0.15) return;
  const r = e.brow, tilt = e.tilt;
  const xs = [x0 - side * 16, x0 - side * 2, x0 + side * 13];
  const ys = [p.brow_y - r - tilt + 2, p.brow_y - r - 4, p.brow_y - r + 1 + tilt * 0.3];
  d.lock(xs.map((x, i) => v.surf(x, ys[i], 2)), (p.brow === 'thick' ? 8 : p.brow === 'straight' ? 5.5 : 4.4) * p.brow_w, p.brow_col, 'swell');
}
function nose(d, v, e, p) {
  const n0 = p.nose_y, front = 1 - Math.min(1, Math.max(0, (v.yaw - 5) / 8));
  if (front > 0) {
    // front: a single line down the shadow side, two nostril hooks (fading as the head turns and the contour takes over)
    const a0 = d.alpha; d.alpha = a0 * front; d.g.globalAlpha = d.alpha;
    d.thin([v.surf(-5, n0 - 24), v.surf(-6, n0 - 12), v.surf(-8, n0 - 2)].map(q => q), { k: 0.9 });
    const S = (x, y) => { const q = v.pt(x, y, p.zm(y) + 2); return q; };
    d.thin([S(-p.nose_w, n0 - 1), S(-p.nose_w - 2, n0 + 5), S(-p.nose_w + 4, n0 + 8), S(-3, n0 + 7)]);
    d.thin([S(p.nose_w, n0 - 1), S(p.nose_w + 2, n0 + 5), S(p.nose_w - 4, n0 + 8), S(3, n0 + 7)]);
    d.alpha = a0; d.g.globalAlpha = a0;
  }
  if (front >= 1) return;
  const a0 = d.alpha; d.alpha = a0 * (1 - front); d.g.globalAlpha = d.alpha;
  if (v.yaw < 75) {
    const pts = [-4, n0 - 22, n0 - 8].map(y => v.pt(1.5, y, p.zf(y)));
    d.thin([...pts, v.pt(2, n0, p.nose_z - 2), v.pt(1, n0 + 6, p.nose_z - 9)], { k: 1.05 });
  }
  if (v.facing(p.nose_w, n0) > 0.05) {
    const [wx, wy] = v.surf(p.nose_w * 0.95, n0 + 2, 3);
    d.thin([[wx - 2, wy - 7], [wx + 3, wy - 1], [wx, wy + 5], [wx - 6, wy + 5]]);
  }
  d.alpha = a0; d.g.globalAlpha = a0;
}
function mouth(d, v, e, p) {
  const my = p.mouth_y, sm = e.smile, mw = p.mouth_w * e.wide * (1 + 0.12 * e.swide - 0.3 * e.pucker), sk = e.smirk;
  const opn = e.mouth + e.jaw, round = e.round + e.pucker > 0.5;
  let lc = v.surf(-mw, my - sm * 5 + sk * 3, 1); const rc = v.surf(mw, my - sm * 5 - sk * 6, 1);
  if (v.facing(-mw, my) < 0.25) lc = v.pt(-mw * 0.3, my - sm * 5, p.zf(my) - 4);
  if (v.facing(0, my) < 0.0) return;
  if (opn > 0.05) {
    const h = 22 * opn; let top, bot;
    if (round) { top = [lc, v.surf(0, my - h * 0.35, 2), rc]; bot = [rc, v.surf(0, my + h * 0.75, 2), lc]; }
    else {
      top = [lc, v.surf(-mw * 0.45, my - 3 - sm * 2, 2), v.surf(0, my - 2.5, 2), v.surf(mw * 0.45, my - 3 - sm * 2, 2), rc];
      bot = [rc, v.surf(mw * 0.5, my + h * 0.8 - sm, 2), v.surf(0, my + h, 2), v.surf(-mw * 0.5, my + h * 0.8 - sm, 2), lc];
    }
    const poly = top.concat(bot.slice(1, -1));
    d.fill(poly, '#6e1f1c');
    const topY = Math.min(...top.map(q => q[1])), botY = Math.max(...bot.map(q => q[1])), hh = botY - topY;
    d.clipped(poly, () => {
      const tb = round ? 0.22 : 0.32;
      d.fill([[lc[0] - 6, topY - 8, 'c'], [rc[0] + 6, topY - 8, 'c'], [rc[0] + 6, topY + hh * tb * 0.7, 'c'], [(lc[0] + rc[0]) / 2, topY + hh * tb + 2], [lc[0] - 6, topY + hh * tb * 0.7, 'c']], '#fbf6ea');
      if (e.teeth > 0.5) d.fill([[lc[0] - 6, botY + 8, 'c'], [rc[0] + 6, botY + 8, 'c'], [rc[0] + 6, botY - hh * 0.28, 'c'], [(lc[0] + rc[0]) / 2, botY - hh * 0.22], [lc[0] - 6, botY - hh * 0.28, 'c']], '#fbf6ea');
      else d.ellipse((lc[0] + rc[0]) / 2, botY - hh * 0.05, Math.abs(rc[0] - lc[0]) * 0.3, hh * 0.38, '#c8605a');
    });
    d.ink(poly, 2.4, true);
    return;
  }
  const line = [lc, v.surf(-mw * 0.4, my + sm * 1.2, 1), v.surf(0, my + sm * 2.5, 1), v.surf(mw * 0.4, my + sm * 1.2, 1), rc];
  if (p.lip !== 'none') {
    const lw = p.lip === 'thin' ? 1 : 1.5;
    d.fill([v.surf(-mw * 0.55, my + 1.5, 1), v.surf(0, my + 6.5 * lw, 1), v.surf(mw * 0.55, my + 1.5, 1), v.surf(0, my + 2.5, 1)], p.lip_col, 6, 0.85);
  }
  d.ink(line, 2.2);
  for (const [q, sd] of [[lc, -1], [rc, 1]]) if (Math.abs(sm) > 0.3) d.thin([[q[0] - sd, q[1]], [q[0] + sd * 3, q[1] - sm * 4]], { k: 0.8, op: Math.min(1, (Math.abs(sm) - 0.3) / 0.15) });
}
// vera.py extra(): narrow glasses with thin dark rims
function glasses(d, v, p) {
  const C = '#3a2a22';
  for (const sd of [1, -1]) {
    const f = v.facing(p.eye_x * sd, 0);
    if (f < 0.25) continue;
    const [cx, cy] = v.surf(p.eye_x * sd, 1, 8), w = 22 * (0.3 + 0.7 * f), h = 13;
    d.ink([[cx - w, cy - h, 'c'], [cx + w, cy - h, 'c'], [cx + w * 0.9, cy + h, 'c'], [cx - w * 0.9, cy + h, 'c']], 2.6, true, C, 2);
  }
  if (v.yaw < 70) { const l = v.surf(-p.eye_x + 20, -3, 10), r = v.surf(p.eye_x - 20, -3, 10); d.ink([l, [(l[0] + r[0]) / 2, l[1] - 3], r], 2.4, false, C); }
  if (v.facing(p.eye_x + 22, 0) > 0.1) d.ink([v.surf(p.eye_x + 22, -6, 6), v.pt(p.a(0) * 0.98, -4, -12)], 2.4, false, C);
}

// the view of parts.py, on the real head: sheet.pt gives the picture's point of a head point
function view(p, sheet) {
  const yr = sheet.yaw * Math.PI / 180;
  return {
    p, yaw: sheet.yaw, s: Math.sin(yr), c: Math.cos(yr),
    pt: (x, y, z) => sheet.pt(x, y, z),
    surf: (x, y, lift = 0) => sheet.pt(x, y, p.zs(x, y) + lift),
    facing: (x, y = 0) => Math.cos(Math.atan2(x, Math.max(p.zs(x, y), 1)) - yr),
  };
}
// draw the face (g: a 2D context already in sheet coordinates) — parts.head()'s order: blush, nose, mouth, eyes, brows, laugh lines
export function drawFace(g, p, sheet, e) {
  if (sheet.yaw > 112) return;
  const d = new Doc(g, sheet.lw), v = view(p, sheet);
  if (e.cheeks > 0.02) for (const sd of [1, -1]) { const f = v.facing(p.eye_x * sd, 28); if (f > 0.3) { const [bx, by] = v.surf(p.eye_x * sd * 1.05, 28); d.ellipse(bx, by, 12 * f, 7, '#d9776a', (0.18 + 0.15 * 0.6) * e.cheeks); } }
  nose(d, v, e, p);
  mouth(d, v, e, p);
  for (const sd of [1, -1]) { eye(d, v, sd, e, p); brow(d, v, sd, e, p); }
  if (e.cheeks > 0.3 && e.smile > 0.5) for (const sd of [1, -1]) if (v.facing(sd * 24, 55) > 0.35)
    d.thin([v.surf(sd * 15, p.nose_y + 4, 2), v.surf(sd * 22, p.mouth_y - 4, 1), v.surf(sd * 22, p.mouth_y + 6, 1)], { k: 0.8, op: Math.min(1, (e.cheeks - 0.3) / 0.3) });
}
export function drawGlasses(g, p, sheet) {
  if (sheet.yaw > 112) return;
  glasses(new Doc(g, sheet.lw), view(p, sheet), p);
}
