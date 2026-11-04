// Савелий Петрович's painted face: the drawing's eyes, lids, pupils, mouths, blush and dome lines
// (styles/s11-rubberhose/tools/lib.py `eye`, `mouth`, `cheek`, `tline`; savely.py `head`) ported to a 2D canvas.
// The canvas is the head seen from the front in the drawing's own units (head centre 0,0, radius 64, y down); the 3D
// head carries it by a straight projection from the front, as the drawing's Head.project() lays features on the ball.
// Everything is continuous numbers, so expressions mix and move: a face is {lid, rot, happy, look, brow, …, mouth}.
export const X0 = -96, X1 = 96, Y0 = -96, Y1 = 100, PX = 6;
export const INK = '#1b1714', WHITE = '#fbf7ee', MOUTH = '#4a1712', TONGUE = '#d9533f', CHEEK = '#e98a72';
export const SKIN = '#f3d2b4', SKIN_SH = '#dfa98a';
const LW = 3.2, LWI = 2.2;

// mouths: six points round the opening (left corner, top middle, right corner, bottom right, bottom middle, bottom
// left), relative to (0, y); a closed mouth has its bottom on its top. Made from the drawing's mouth kinds.
const M6 = {
  grin: (w, o) => [[-w / 2, -4], [0, -1], [w / 2, -4], [w / 2 - w * 0.12, w * 0.3 * o], [0, w * 0.5 * o], [-w / 2 + w * 0.12, w * 0.3 * o]],
  shout: (w, o) => [[-w / 2, 2], [0, -w * 0.12], [w / 2, 2], [w / 2 - w * 0.05, w * 0.45 * o], [0, w * 0.55 * o], [-w / 2 + w * 0.05, w * 0.45 * o]],
  o: (w, o) => [[-w * 0.28, 0], [0, -w * 0.32 * o], [w * 0.28, 0], [w * 0.2, w * 0.3 * o], [0, w * 0.42 * o], [-w * 0.2, w * 0.3 * o]],
  line: (w, c) => { const m = [[-w / 2, 0], [0, c], [w / 2, 0]]; return [...m, m[2], m[1], m[0]]; },
};
const mouthOf = (kind, w, a, y) => ({ y, pts: M6[kind](w, a).map(p => p.slice()) });

// the drawing's EXPR of savely.py as numbers (look, lid, rot, brow, browy, mouth, blush, glasses_up), plus what the
// 3D head does with each: the moustache's droop and the head's squash (build.py SQUASH)
export const EXPR = {
  neutral: { look: [0.1, 0.1], lid: 0.3, rot: 0, happy: 0, brow: -0.35, browY: 0, blush: 1, glasses: 0, droop: 0.6, sq: [1, 1], eyeS: 1, ticks: 0, teeth: 0, mouth: mouthOf('line', 24, -2, 50) },
  joy: { look: [0, 0], lid: 0, rot: 0, happy: 1, brow: 0.25, browY: 0, blush: 1.3, glasses: 0, droop: -0.4, sq: [1.06, 0.95], eyeS: 1, ticks: 1, teeth: 0, mouth: mouthOf('grin', 34, 0.7, 54) },
  surprise: { look: [0, 0], lid: 0, rot: 0, happy: 0, brow: 0.5, browY: -14, blush: 1, glasses: 1, droop: 0, sq: [0.93, 1.09], eyeS: 1.08, ticks: 0, teeth: 0, mouth: mouthOf('o', 26, 1.1, 54) },
  sad: { look: [0, 0.6], lid: 0.42, rot: 0.35, happy: 0, brow: 0.9, browY: 0, blush: 1, glasses: 0, droop: 0.6, sq: [1.02, 0.96], eyeS: 1, ticks: 0, teeth: 0, mouth: mouthOf('line', 24, -5, 60) },
  angry: { look: [0, 0], lid: 0.45, rot: -0.4, happy: 0, brow: -1.0, browY: 6, blush: 1.2, glasses: 0, droop: 0, sq: [1.05, 0.95], eyeS: 1, ticks: 0, teeth: 1, mouth: mouthOf('shout', 34, 1.1, 54) },
};
export const EXPR_RU = { neutral: 'спокойно', joy: 'радость', surprise: 'удивление', sad: 'грусть', angry: 'злость' };
// speech: mouth shapes under the moustache (vowels open, lips shut on м/б/п, a narrow opening on в/ф)
export const VISEME = {
  A: mouthOf('shout', 30, 0.75, 54), O: mouthOf('o', 24, 0.95, 55), U: mouthOf('o', 17, 0.7, 55), E: mouthOf('grin', 32, 0.42, 54),
  I: mouthOf('grin', 30, 0.28, 54), M: mouthOf('line', 24, 0, 52), F: mouthOf('grin', 26, 0.14, 53), C: mouthOf('shout', 26, 0.32, 54),
};

// a face as one vector (to mix and to move by springs) and back
const SCAL = ['lid', 'rot', 'happy', 'brow', 'browY', 'blush', 'glasses', 'droop', 'eyeS', 'ticks', 'teeth'];
export const mouthVec = m => [m.y, ...m.pts.flat()];
export const vecMouth = v => ({ y: v[0], pts: [0, 1, 2, 3, 4, 5].map(i => [v[1 + i * 2], v[2 + i * 2]]) });
export const exprVec = e => [...SCAL.map(k => e[k]), e.look[0], e.look[1], e.sq[0], e.sq[1], ...mouthVec(e.mouth)];
export const MOUTH0 = SCAL.length + 4;
export function vecExpr(v) {
  const e = {}; SCAL.forEach((k, i) => e[k] = v[i]);
  e.look = [v[SCAL.length], v[SCAL.length + 1]]; e.sq = [v[SCAL.length + 2], v[SCAL.length + 3]];
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
function smoothPath(g, pts, closed = true, k = 1) {   // lib.smooth: Catmull-Rom → cubic Bézier
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

// one eye (lib.eye, kind 'dot' as Савелий's): lid 0…1, rot the lid's tilt, happy → the ∩ arc, blink → shut
function eye(g, cx, cy, rx, ry, e, side, blink, look) {
  const shut = Math.max(e.lid, blink, e.happy);
  if (shut > 0.93) {
    if (e.happy >= blink) tline(g, [[cx - rx, cy + ry * 0.15], [cx, cy - ry * 0.45], [cx + rx, cy + ry * 0.15]], 2, 6.5, 2);
    else tline(g, [[cx - rx, cy + ry * 0.1], [cx, cy + ry * 0.28], [cx + rx, cy + ry * 0.1]], 2, 5.5, 2);
    return;
  }
  const path = () => { g.beginPath(); g.moveTo(cx, cy - ry); g.bezierCurveTo(cx + rx * 1.1, cy - ry, cx + rx * 1.05, cy + ry, cx, cy + ry); g.bezierCurveTo(cx - rx * 1.05, cy + ry, cx - rx * 1.1, cy - ry, cx, cy - ry); g.closePath(); };
  g.save(); path(); g.fillStyle = WHITE; g.fill(); g.clip();
  const px = cx + look[0] * rx * 0.45, py = cy + ry * 0.18 + look[1] * ry * 0.35;
  g.fillStyle = INK; ell(g, px, py, 7 * 0.7, 9 * 0.75); g.fill();
  // the lid: skin above a straight line, tilted; it closes over the eye with a blink or a smile
  const lid = shut + (1 - shut) * 0;   // the lid line goes down to the eye's bottom as it shuts
  if (lid > 0.001) {
    const ly = cy - ry + 2 * ry * lid, tilt = e.rot * (1 - Math.max(blink, e.happy)), yIn = ly + tilt * ry * side, yOut = ly - tilt * ry * side;
    const xl = cx - rx * 1.3, xr = cx + rx * 1.3, [yl, yr] = side > 0 ? [yIn, yOut] : [yOut, yIn];
    g.beginPath(); g.moveTo(xl, cy - ry * 2); g.lineTo(xr, cy - ry * 2); g.lineTo(xr, yr); g.lineTo(xl, yl); g.closePath(); g.fillStyle = SKIN; g.fill();
    g.beginPath(); g.moveTo(xl, yl); g.lineTo(xr, yr); g.strokeStyle = INK; g.lineWidth = LW; g.stroke();
  }
  g.restore();
  path(); g.strokeStyle = INK; g.lineWidth = LW; g.lineJoin = 'round'; g.stroke();
}

function mouth(g, m, e) {
  const P = m.pts.map(p => [p[0], p[1] + m.y]);
  const top = [P[0], P[1], P[2]], bot = [P[2], P[3], P[4], P[5], P[0]];
  const h = Math.max(P[4][1] - P[1][1], (P[3][1] + P[5][1]) / 2 - (P[0][1] + P[2][1]) / 2);
  const w = P[2][0] - P[0][0];
  if (h < 2.2) {   // closed: a brush line (smile, frown)
    tline(g, top, 2.2, 4.5, 2.2);
  } else {
    g.save(); g.beginPath(); smoothPath(g, P, true, 0.9); g.fillStyle = MOUTH; g.fill(); g.clip();
    const cx = (P[0][0] + P[2][0]) / 2;
    g.fillStyle = TONGUE; ell(g, cx + w * 0.06, P[4][1] - w * 0.02, w * 0.3, w * 0.2); g.fill();
    if (e.teeth > 0.05) { g.globalAlpha = Math.min(1, e.teeth); g.fillStyle = WHITE; g.fillRect(P[0][0] - 2, Math.min(P[0][1], P[2][1]) - 6, w + 4, 8 + (P[1][1] - Math.min(P[0][1], P[2][1])) + 6); g.globalAlpha = 1; }
    g.restore();
    g.beginPath(); smoothPath(g, P, true, 0.9); g.strokeStyle = INK; g.lineWidth = LWI + 0.4; g.lineJoin = 'round'; g.stroke();
  }
  if (e.ticks > 0.05) {   // cheek ticks at the corners of a grin
    g.globalAlpha = Math.min(1, e.ticks); g.strokeStyle = INK; g.lineWidth = 2; g.lineCap = 'round';
    g.beginPath(); g.moveTo(P[0][0] - 4, P[0][1] - 5); g.lineTo(P[0][0] + 1, P[0][1] + 1); g.moveTo(P[2][0] + 4, P[2][1] - 5); g.lineTo(P[2][0] - 1, P[2][1] + 1); g.stroke();
    g.globalAlpha = 1;
  }
}

// the whole painted face: f = vecExpr(…) plus live things {look, blink}
export function drawFace(cv, f, live = {}) {
  const g = cv.getContext('2d');
  g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, cv.width, cv.height);
  g.setTransform(PX, 0, 0, PX, -X0 * PX, -Y0 * PX);
  g.lineCap = 'round'; g.lineJoin = 'round';
  // dome lines (age) — fade a little when the brows lift (the skin there moves)
  g.strokeStyle = SKIN_SH; g.lineWidth = 1.6;
  for (const y of [-34, -27]) { const yy = y - Math.max(0, f.brow) * 2; g.beginPath(); smoothPath(g, [[-20, yy], [0, yy - 3], [20, yy]], false); g.stroke(); }
  // blush: two round spots (lib.cheek)
  g.fillStyle = CHEEK; g.globalAlpha = 0.4;
  for (const x of [-40, 40]) { ell(g, x, 30, 11 * f.blush, 11 * f.blush * 0.8); g.fill(); }
  g.globalAlpha = 1;
  const look = live.look || f.look, blink = live.blink || 0;
  for (const [side, x] of [[-1, -20], [1, 20]]) eye(g, x, 2, 13 * f.eyeS, 17 * f.eyeS, f, side, blink, look);
  mouth(g, f.mouth, f);
}
