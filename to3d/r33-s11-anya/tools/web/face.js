// Аня's painted face: the drawing's eyes (tall ovals with a ring pupil and a highlight, a heavy lid, three lashes),
// thin brows, small red lips and open mouths, blush, a tear, and the hairline
// (styles/s11-rubberhose/tools/lib.py `eye`, `brow`, `mouth`, `cheek`; anya.py `head`) ported to a 2D canvas.
// The canvas is the head seen from the front in the drawing's own units (head centre 0,0, radius 70, y down); the 3D
// head carries it by a straight projection from the front, as the drawing's Head.project() lays features on the ball.
// Everything is continuous numbers, so expressions mix and move.
export const X0 = -100, X1 = 100, Y0 = -100, Y1 = 124, PX = 6;
export const INK = '#1b1714', WHITE = '#fbf7ee', MOUTH = '#4a1712', TONGUE = '#d9533f', CHEEK = '#e98a72';
export const SKIN = '#f6dcc4', SKIN_SH = '#e9bfa3', HAIR = '#8d3a1f', LIP = '#c8392f', TEAR = '#bfe0ee';
const LW = 3.2, LWI = 2.2;
// the bare face on the front of the ball (anya.py face_loop): over the forehead along the hairline with its wave,
// down the cheeks, under the chin
export const FACE_LOOP = [[-62, 24], [-64, 4], [-56, -18], [-44, -34], [-30, -40], [-20, -36], [-8, -46], [8, -52], [24, -50],
  [40, -42], [54, -30], [63, -12], [64, 14], [66, 50], [40, 96], [0, 110], [-40, 96], [-66, 50]];

// mouths: six points round the opening (left corner, top middle, right corner, bottom right, bottom middle, bottom
// left), relative to (0, y); a closed mouth has its bottom on its top. Made from the drawing's mouth kinds.
const M6 = {
  grin: (w, o) => [[-w / 2, -4], [0, -1], [w / 2, -4], [w / 2 - w * 0.12, w * 0.3 * o], [0, w * 0.5 * o], [-w / 2 + w * 0.12, w * 0.3 * o]],
  shout: (w, o) => [[-w / 2, 2], [0, -w * 0.12], [w / 2, 2], [w / 2 - w * 0.05, w * 0.45 * o], [0, w * 0.55 * o], [-w / 2 + w * 0.05, w * 0.45 * o]],
  o: (w, o) => [[-w * 0.28, 0], [0, -w * 0.32 * o], [w * 0.28, 0], [w * 0.2, w * 0.3 * o], [0, w * 0.42 * o], [-w * 0.2, w * 0.3 * o]],
  line: (w, c, e = 0) => { const m = [[-w / 2, e], [0, c], [w / 2, e]]; return [...m, m[2], m[1], m[0]]; },
};
const mouthOf = (kind, w, a, y, e) => ({ y, pts: M6[kind](w, a, e).map(p => p.slice()) });

// the drawing's EXPR of anya.py as numbers, and the head's squash (build.py SQUASH).
// lid: the upper lid's line (0 open … 1 shut), rot its tilt, happy: the ∩ of a laughing eye, pupil: its size (the
// "spark" of surprise is a small one), hl: the pupil's highlight, heavy: the black crescent over an open eye,
// lips: how much lip is painted round the mouth (the small red lips; an open grin has none), tear
export const EXPR = {
  neutral: { look: [0.15, -0.55], lid: 0.18, rot: 0, happy: 0, brow: 0.15, browY: 0, blush: 1, pupil: 1, hl: 1, heavy: 0, ticks: 1, teeth: 0, lips: 1, tear: 0, sq: [1, 1], mouth: mouthOf('line', 22, 2, 60, -3) },
  joy: { look: [0, 0], lid: 0, rot: 0, happy: 1, brow: -0.05, browY: 0, blush: 1.3, pupil: 1, hl: 1, heavy: 0, ticks: 1, teeth: 0, lips: 0, tear: 0, sq: [1.06, 0.95], mouth: mouthOf('grin', 30, 0.9, 60) },
  surprise: { look: [0, 0], lid: 0, rot: 0, happy: 0, brow: 0.15, browY: -12, blush: 1, pupil: 0.45, hl: 0, heavy: 1, ticks: 0, teeth: 0, lips: 0.55, tear: 0, sq: [0.93, 1.09], mouth: { y: 62, pts: [[-2.6, 0.5], [0, -2.6], [2.6, 0.5], [1.8, 3.2], [0, 4.2], [-1.8, 3.2]] } },
  sad: { look: [0, 0.5], lid: 0.34, rot: 0.32, happy: 0, brow: 0.85, browY: 0, blush: 1, pupil: 1, hl: 1, heavy: 0, ticks: 0, teeth: 0, lips: 1, tear: 1, sq: [1.02, 0.96], mouth: mouthOf('line', 22, 0, 60, 3) },
  angry: { look: [0, 0.1], lid: 0.4, rot: -0.6, happy: 0, brow: -1.3, browY: 10, blush: 1.4, pupil: 1, hl: 1, heavy: 0, ticks: 0, teeth: 1, lips: 0, tear: 0, sq: [1.05, 0.95], mouth: mouthOf('shout', 30, 0.8, 60) },
};
export const EXPR_RU = { neutral: 'спокойно', joy: 'радость', surprise: 'удивление', sad: 'грусть', angry: 'злость' };
// speech: small mouth shapes inside the lips (vowels open, lips shut on м/б/п, a narrow opening on в/ф)
export const VISEME = {
  A: mouthOf('shout', 20, 0.7, 58), O: mouthOf('o', 20, 0.9, 60), U: mouthOf('o', 13, 0.75, 60), E: mouthOf('grin', 24, 0.42, 60),
  I: mouthOf('grin', 24, 0.26, 60), M: mouthOf('line', 20, 1, 60, -1), F: mouthOf('grin', 20, 0.14, 60), C: mouthOf('shout', 19, 0.3, 59),
};

// a face as one vector (to mix and to move by springs) and back
export const SCAL = ['lid', 'rot', 'happy', 'brow', 'browY', 'blush', 'pupil', 'hl', 'heavy', 'ticks', 'teeth', 'lips', 'tear'];
export const mouthVec = m => [m.y, ...m.pts.flat()];
export const vecMouth = v => ({ y: v[0], pts: [0, 1, 2, 3, 4, 5].map(i => [v[1 + i * 2], v[2 + i * 2]]) });
export const exprVec = e => [...SCAL.map(k => e[k]), e.look[0], e.look[1], e.sq[0], e.sq[1], ...mouthVec(e.mouth)];
export const SQ0 = SCAL.length + 2, MOUTH0 = SCAL.length + 4;
export function vecExpr(v) {
  const e = {}; SCAL.forEach((k, i) => e[k] = v[i]);
  e.look = [v[SCAL.length], v[SCAL.length + 1]]; e.sq = [v[SQ0], v[SQ0 + 1]];
  e.mouth = vecMouth(v.slice(MOUTH0)); return e;
}
export function mixExpr(w) {
  let out = null, s = 0;
  for (const [k, a] of Object.entries(w)) { if (!a || !EXPR[k]) continue; const v = exprVec(EXPR[k]); out = out ? out.map((x, i) => x + v[i] * a) : v.map(x => x * a); s += a; }
  if (!out) return exprVec(EXPR.neutral);
  return out.map(x => x / s);
}

// ———— drawing ————
function sample(pts, steps = 10) {   // points along the open Catmull-Rom curve (lib.sample)
  const out = [], n = pts.length;
  for (let i = 0; i < n - 1; i++) {
    const p0 = pts[Math.max(i - 1, 0)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(i + 2, n - 1)];
    for (let s = 0; s < steps; s++) {
      const t = s / steps, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(j => 0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)));
    }
  }
  out.push(pts[n - 1]); return out;
}
export function smoothPath(g, pts, closed = true, k = 1) {   // lib.smooth: Catmull-Rom → cubic Bézier
  const n = pts.length; g.moveTo(pts[0][0], pts[0][1]);
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const p0 = pts[(closed || i > 0) ? (i - 1 + n) % n : 0], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(closed || i + 2 < n) ? (i + 2) % n : n - 1];
    g.bezierCurveTo(p1[0] + (p2[0] - p0[0]) / 6 * k, p1[1] + (p2[1] - p0[1]) / 6 * k, p2[0] - (p3[0] - p1[0]) / 6 * k, p2[1] - (p3[1] - p1[1]) / 6 * k, p2[0], p2[1]);
  }
  if (closed) g.closePath();
}
function tline(g, pts, w0, w1, w2 = w0, col = INK) {   // the tapered brush stroke (lib.tline)
  const s = sample(pts, 10), n = s.length, L = [], R = [];
  s.forEach((p, i) => {
    const a = s[Math.max(i - 1, 0)], b = s[Math.min(i + 1, n - 1)], dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l, t = i / (n - 1);
    const w = t < 0.5 ? w0 + (w1 - w0) * (t / 0.5) : w1 + (w2 - w1) * ((t - 0.5) / 0.5);
    L.push([p[0] + nx * w / 2, p[1] + ny * w / 2]); R.push([p[0] - nx * w / 2, p[1] - ny * w / 2]);
  });
  g.beginPath(); [...L, ...R.reverse()].forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath(); g.fillStyle = col; g.fill();
}
const ell = (g, x, y, rx, ry, rot = 0) => { g.beginPath(); g.ellipse(x, y, Math.max(0.01, rx), Math.max(0.01, ry), rot, 0, Math.PI * 2); };

// one eye (lib.eye, kinds 'ring', 'spark', 'closed-happy', 'closed' as one): side +1 → the outer corner is to the right
function eye(g, cx, cy, rx, ry, e, side, blink, look) {
  const shut = Math.max(e.lid, blink, e.happy);
  const lashes = (y0, down, a = 1) => {   // three lashes at the outer corner
    g.globalAlpha = a;
    for (let i = 0; i < 3; i++) {
      const bx = cx + side * rx * (0.82 + i * 0.1), by = y0 - ry * 0.15 + i * ry * 0.2, d = down;
      tline(g, [[bx, by], [bx + side * 6, by - 7 * (1 - d) + i * 3.5 + 6 * d], [bx + side * 12, by - 9 * (1 - d) + i * 5 + 9 * d]], 3.2, 2.2, 0.5);
    }
    g.globalAlpha = 1;
  };
  if (shut > 0.93) {
    if (e.happy >= blink) {
      tline(g, [[cx - rx, cy + ry * 0.15], [cx, cy - ry * 0.45], [cx + rx, cy + ry * 0.15]], 2, 6.5, 2);
      for (let i = 0; i < 3; i++) { const bx = cx + side * rx * (0.55 + i * 0.22), by = cy - ry * (0.25 - i * 0.18); tline(g, [[bx, by], [bx + side * 9, by - 6 + i * 3]], 3, 2, 0.6); }
    } else {
      tline(g, [[cx - rx, cy + ry * 0.1], [cx, cy + ry * 0.28], [cx + rx, cy + ry * 0.1]], 2, 5.5, 2);
      for (let i = 0; i < 3; i++) { const bx = cx + side * rx * (0.7 + i * 0.2), by = cy + ry * (0.2 - i * 0.02); tline(g, [[bx, by], [bx + side * 9, by + 3 + i * 2]], 3, 2, 0.6); }
    }
    return;
  }
  const path = () => { g.beginPath(); g.moveTo(cx, cy - ry); g.bezierCurveTo(cx + rx * 1.1, cy - ry, cx + rx * 1.05, cy + ry, cx, cy + ry); g.bezierCurveTo(cx - rx * 1.05, cy + ry, cx - rx * 1.1, cy - ry, cx, cy - ry); g.closePath(); };
  g.save(); path(); g.fillStyle = WHITE; g.fill(); g.clip();
  const prx = rx * 0.62 * e.pupil, pry = ry * 0.55 * e.pupil;
  const px = cx + look[0] * rx * 0.45, py = cy + ry * 0.18 + look[1] * ry * 0.35;
  g.fillStyle = INK; ell(g, px, py, prx, pry); g.fill();
  if (e.hl > 0.05) { g.globalAlpha = Math.min(1, e.hl); g.fillStyle = WHITE; ell(g, px - prx * 0.3 * side, py - pry * 0.4, prx * 0.28, pry * 0.22); g.fill(); g.globalAlpha = 1; }
  let lashY = cy - ry * 0.45;
  if (shut > 0.02) {
    const ly = cy - ry + 2 * ry * shut, tilt = e.rot * (1 - Math.max(blink, e.happy)), yIn = ly + tilt * ry * side, yOut = ly - tilt * ry * side;
    const xl = cx - rx * 1.3, xr = cx + rx * 1.3, [yl, yr] = side > 0 ? [yIn, yOut] : [yOut, yIn];
    g.beginPath(); g.moveTo(xl, cy - ry * 2); g.lineTo(xr, cy - ry * 2); g.lineTo(xr, yr); g.lineTo(xl, yl); g.closePath(); g.fillStyle = SKIN; g.fill();
    g.beginPath(); g.moveTo(xl, yl); g.lineTo(xr, yr); g.strokeStyle = INK; g.lineWidth = LW; g.stroke();
    lashY = ly;
  }
  g.restore();
  path(); g.strokeStyle = INK; g.lineWidth = LW; g.lineJoin = 'round'; g.stroke();
  const hv = e.heavy * (1 - Math.min(1, shut * 12));
  if (hv > 0.05) {   // the heavy upper lid of an eye wide open: a black crescent over its top
    const t = 0.4 * hv;
    g.beginPath(); g.moveTo(cx - rx * 0.98, cy - ry * 0.25); g.bezierCurveTo(cx - rx * 0.9, cy - ry * 1.12, cx + rx * 0.9, cy - ry * 1.12, cx + rx * 0.98, cy - ry * 0.25);
    g.bezierCurveTo(cx + rx * 0.8, cy - ry * (1.02 - t), cx - rx * 0.8, cy - ry * (1.02 - t), cx - rx * 0.98, cy - ry * 0.25); g.closePath(); g.fillStyle = INK; g.fill();
  }
  lashes(lashY, Math.max(0, (shut - 0.6) / 0.4));
}

function mouth(g, m, e) {
  const P = m.pts.map(p => [p[0], p[1] + m.y]);
  const top = [P[0], P[1], P[2]];
  const h = Math.max(P[4][1] - P[1][1], (P[3][1] + P[5][1]) / 2 - (P[0][1] + P[2][1]) / 2);
  const w = P[2][0] - P[0][0], hw = w / 2, cx = (P[0][0] + P[2][0]) / 2, k = Math.max(0, Math.min(1.2, e.lips));
  const open = h >= 2.2;
  if (k > 0.04) {   // the small red lips (lib.mouth 'lips…'): a cupid's bow over, a full lip under; they go round an opening
    const ly = (P[0][1] + P[2][1]) / 2, up = Math.max(-1, Math.min(1, (P[1][1] - ly - 1) / 4)), cy = P[1][1] - 1 - up, gap = Math.max(0, P[4][1] - P[1][1]);
    const gx = open ? 2.4 : 0, lx = P[0][0] - gx, rx = P[2][0] + gx, H = hw + gx;
    g.globalAlpha = Math.min(1, k * 3);
    g.beginPath(); g.moveTo(lx, ly);
    g.bezierCurveTo(cx - H * 0.6, cy - 5 * k, cx - H * 0.25, cy - 7 * k, cx, cy - 3 * k);
    g.bezierCurveTo(cx + H * 0.25, cy - 7 * k, cx + H * 0.6, cy - 5 * k, rx, ly);
    const by = cy + gap * 1.4 + (7 + up) * k + (open ? 2 : 0);
    g.bezierCurveTo(cx + H * 0.5, by, cx - H * 0.5, by, lx, ly); g.closePath();
    g.fillStyle = LIP; g.fill(); g.strokeStyle = INK; g.lineWidth = LWI; g.lineJoin = 'round'; g.stroke();
    if (!open) { g.beginPath(); smoothPath(g, [[P[0][0] + 2, ly + (ly - cy) * 0.0 + up], [cx, P[1][1] - 1 + up], [P[2][0] - 2, ly + up]], false); g.lineWidth = 1.6; g.stroke(); }
    g.globalAlpha = 1;
  }
  if (!open) {
    if (k < 0.5) { g.globalAlpha = 1 - k * 2; tline(g, top, 2.2, 4.5, 2.2); g.globalAlpha = 1; }
  } else {
    g.save(); g.beginPath(); smoothPath(g, P, true, 0.9); g.fillStyle = MOUTH; g.fill(); g.clip();
    g.fillStyle = TONGUE; ell(g, cx + w * 0.06, P[4][1] - w * 0.02, w * 0.3, w * 0.2); g.fill();
    if (e.teeth > 0.05) { g.globalAlpha = Math.min(1, e.teeth); g.fillStyle = WHITE; g.fillRect(P[0][0] - 2, Math.min(P[0][1], P[2][1]) - 8, w + 4, 12); g.globalAlpha = 1; }
    g.restore();
    g.beginPath(); smoothPath(g, P, true, 0.9); g.strokeStyle = INK; g.lineWidth = LWI + 0.4; g.lineJoin = 'round'; g.stroke();
  }
  const sm = Math.max(0, Math.min(1, (P[1][1] - (P[0][1] + P[2][1]) / 2) / 3));   // cheek ticks at the corners of a smile
  if (e.ticks * sm > 0.05) {
    g.globalAlpha = Math.min(1, e.ticks * sm); g.strokeStyle = INK; g.lineWidth = 1.9; g.lineCap = 'round';
    g.beginPath(); g.moveTo(P[0][0] - 3.5, P[0][1] - 5); g.lineTo(P[0][0] + 0.5, P[0][1]); g.moveTo(P[2][0] + 3.5, P[2][1] - 5); g.lineTo(P[2][0] - 0.5, P[2][1]); g.stroke();
    g.globalAlpha = 1;
  }
}

// the whole painted face: f = vecExpr(…) plus live things {look, blink}
export function drawFace(cv, f, live = {}) {
  const g = cv.getContext('2d');
  g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, cv.width, cv.height);
  g.setTransform(PX, 0, 0, PX, -X0 * PX, -Y0 * PX);
  g.lineCap = 'round'; g.lineJoin = 'round';
  g.fillStyle = CHEEK; g.globalAlpha = 0.45;
  for (const x of [-44, 44]) { ell(g, x, 38, 12 * f.blush, 12 * f.blush * 0.8); g.fill(); }
  g.globalAlpha = 1;
  const look = live.look || f.look, blink = live.blink || 0;
  for (const [side, x] of [[-1, -22], [1, 22]]) {
    eye(g, x, 6, 20, 29, f, side, blink, look);
    // the thin arched brow (lib.brow): tilt > 0 lifts the inner end
    const bx = x + side * 3, by = -38 + f.browY, w = 24, t = f.brow, xi = bx - side * w / 2, xo = bx + side * w / 2;
    tline(g, [[xi, by - t * w * 0.35], [bx, by - 0.25 * w * 0.5 - t * w * 0.1], [xo, by + t * w * 0.1]], 3.6 * 0.55, 3.6, 3.6 * 0.3);
  }
  if (f.tear > 0.05) {
    g.globalAlpha = Math.min(1, f.tear); const X = 32, Y = 34;
    g.beginPath(); smoothPath(g, [[X, Y - 8], [X + 6, Y + 4], [X, Y + 9], [X - 6, Y + 4]]); g.fillStyle = TEAR; g.fill(); g.strokeStyle = INK; g.lineWidth = 2; g.stroke(); g.globalAlpha = 1;
  }
  mouth(g, f.mouth, f);
  // the hair over the forehead and beside the cheeks: everything outside the bare face, and the hairline in ink
  g.beginPath(); g.rect(X0, Y0, X1 - X0, Y1 - Y0); smoothPath(g, FACE_LOOP, true); g.fillStyle = HAIR; g.fill('evenodd');
  g.beginPath(); smoothPath(g, FACE_LOOP, true); g.strokeStyle = INK; g.lineWidth = LW; g.stroke();
}
