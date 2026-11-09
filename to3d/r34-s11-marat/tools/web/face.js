// Марат's painted face: the drawing's pie-cut eyes pushed up by the cheeks, thick black brows, blush, the marks of
// the curls and the beard, and his mouths in the beard — the big grin with a row of teeth, a tongue and a lower lip
// (styles/s11-rubberhose/tools/lib.py `eye`, `brow`, `mouth`, `cheek`; marat.py `head`, `grin`) ported to a 2D canvas.
// The canvas is the head seen from the front in the drawing's own units (head centre 0,0, radius 68, y down); the 3D
// head — the skin ball and the hair-and-beard form over it — carries it by a straight projection from the front, as
// the drawing's Head.project() lays features on the ball. Everything is continuous numbers, so expressions mix and move.
export const X0 = -104, X1 = 104, Y0 = -100, Y1 = 124, PX = 6;
export const INK = '#1b1714', WHITE = '#fbf7ee', MOUTH = '#4a1712', TONGUE = '#d9533f', CHEEK = '#e98a72';
export const SKIN = '#f0c9a6', HAIR = '#33262a', HAIR_HI = '#6a5257', LIP = '#d98468';
const LW = 3.2, LWI = 2.2;
// the bare face on the front of the ball: the wavy hairline of marat.py (`hl`) over it, the beard's upper edge
// (`beard`: sideburns, under the cheeks, up under the nose) below
export const FACE_LOOP = [[-57, 10], [-56, -8], [-52, -26], [-44, -36], [-34, -46], [-22, -45], [-11, -52], [0, -49], [11, -52], [22, -45], [34, -46],
  [44, -36], [52, -26], [56, -8], [57, 10], [50, 32], [36, 42], [20, 37], [0, 35], [-20, 37], [-36, 42], [-50, 32]];

// mouths: nine points round the opening — five along the upper edge from the left corner to the right, four along
// the lower edge back — relative to (0, y); a closed mouth has its lower edge on its upper. With each: the row of
// upper teeth (teeth, its height th) and the lower lip, an ellipse behind the opening (its centre lipD under the
// opening's lowest point, radii lipRx, lipRy) — in a black beard a mouth without them reads as a hole.
const M9 = {
  grin: (w, o) => { const hw = w / 2, dep = w * 0.52 * o; return [[-hw, -8], [-hw * 0.55, -2], [0, 0], [hw * 0.55, -2], [hw, -8], [hw * 0.82, dep * 0.55], [hw * 0.3, dep], [-hw * 0.3, dep], [-hw * 0.82, dep * 0.55]]; },
  shout: (w, o) => { const hw = w / 2; return [[-hw, 2], [-hw * 0.5, -w * 0.09], [0, -w * 0.12], [hw * 0.5, -w * 0.09], [hw, 2], [hw * 0.9, w * 0.45 * o], [hw * 0.3, w * 0.55 * o], [-hw * 0.3, w * 0.55 * o], [-hw * 0.9, w * 0.45 * o]].map(([x, y]) => [x, y + 2]); },
  o: (w) => [180, 225, 270, 315, 0, 36, 72, 108, 144].map(a => [Math.cos(a * Math.PI / 180) * w * 0.28, 4 + w * 0.05 + Math.sin(a * Math.PI / 180) * w * 0.37]),
  shut: (w, c = 3) => { const hw = w / 2, t = [[-hw, c + 2], [-hw * 0.5, c * 0.4 + 2], [0, 2], [hw * 0.5, c * 0.4 + 2], [hw, c + 2]]; return [...t, t[3], [hw * 0.15, 2], [-hw * 0.15, 2], t[1]]; },
};
const mouthOf = (kind, w, a) => ({ y: 54, pts: M9[kind](w, a).map(p => p.slice()) });
const lipOf = (teeth, th, lipD, lipRx, lipRy) => ({ teeth, th, lipD, lipRx, lipRy });

// the drawing's EXPR of marat.py as numbers, and the head's squash (build.py SQUASH). lower: the lower lid pushed up
// by the laughing cheeks; pie: the cut wedge of the pupil; pupil: its size (the "spark" of surprise is a small one)
const E0 = { look: [0, 0], lid: 0, rot: 0, happy: 0, lower: 0, brow: 0, browY: 0, blush: 1, pupil: 1, pie: 1, sq: [1, 1] };
export const EXPR = {
  neutral: { ...E0, look: [0.3, 0], lower: 0.3, brow: 0.25, mouth: mouthOf('grin', 50, 0.62), ...lipOf(1, 8.2, 1, 15.5, 5.5) },
  joy: { ...E0, happy: 1, brow: 0.45, browY: -5, blush: 1.35, sq: [1.06, 0.95], mouth: mouthOf('grin', 62, 1), ...lipOf(1, 9.5, 1, 19.2, 5.5) },
  surprise: { ...E0, pupil: 0.45, pie: 0, brow: 0.6, browY: -12, sq: [0.93, 1.09], mouth: mouthOf('o', 34), ...lipOf(0, 6, -10.3, 15, 18) },
  sad: { ...E0, look: [0, 0.65], lid: 0.36, rot: 0.4, brow: 1.0, sq: [1.02, 0.96], mouth: mouthOf('shut', 26), ...lipOf(0, 6, 5.5, 13, 7.5) },
  angry: { ...E0, look: [0, 0.1], lid: 0.4, rot: -0.45, brow: -1.1, browY: 9, blush: 1.3, sq: [1.05, 0.95], mouth: mouthOf('shout', 42, 1.05), ...lipOf(1, 9, -4.3, 17, 5.5) },
};
export const EXPR_RU = { neutral: 'спокойно (улыбается)', joy: 'радость', surprise: 'удивление', sad: 'грусть', angry: 'злость' };
// speech: mouth shapes in the beard (vowels open, lips shut on м/б/п, a narrow opening on в/ф)
export const VISEME = {
  A: mouthOf('grin', 46, 0.95), O: mouthOf('o', 30), U: mouthOf('o', 21), E: mouthOf('grin', 50, 0.5),
  I: mouthOf('grin', 52, 0.32), M: mouthOf('shut', 36, -2), F: mouthOf('grin', 42, 0.14), C: mouthOf('grin', 44, 0.34),
};

// a face as one vector (to mix and to move by springs) and back
export const SCAL = ['lid', 'rot', 'happy', 'lower', 'brow', 'browY', 'blush', 'pupil', 'pie', 'teeth', 'th', 'lipD', 'lipRx', 'lipRy'];
export const mouthVec = m => [m.y, ...m.pts.flat()];
export const vecMouth = v => ({ y: v[0], pts: [0, 1, 2, 3, 4, 5, 6, 7, 8].map(i => [v[1 + i * 2], v[2 + i * 2]]) });
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
// how far the mouth is open (for the head's stretch)
export const mouthOpen = m => Math.max(0, (m.pts[6][1] + m.pts[7][1]) / 2 - m.pts[2][1]);

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

// one eye (lib.eye, kinds 'pie', 'spark', 'closed-happy', 'closed' as one, with the lower lid): side +1 → outer corner right
function eye(g, cx, cy, rx, ry, e, side, blink, look) {
  const hp = Math.min(1, Math.max(0, (e.happy - 0.3) / 0.5));   // half a laugh is not a half-shut eye
  const shut = Math.max(e.lid * (1 - hp), blink, hp);
  if (shut > 0.93) {
    if (hp >= blink) tline(g, [[cx - rx, cy + ry * 0.15], [cx, cy - ry * 0.45], [cx + rx, cy + ry * 0.15]], 2, 6.5, 2);
    else tline(g, [[cx - rx, cy + ry * 0.1], [cx, cy + ry * 0.28], [cx + rx, cy + ry * 0.1]], 2, 5.5, 2);
    return;
  }
  const path = () => { g.beginPath(); g.moveTo(cx, cy - ry); g.bezierCurveTo(cx + rx * 1.1, cy - ry, cx + rx * 1.05, cy + ry, cx, cy + ry); g.bezierCurveTo(cx - rx * 1.05, cy + ry, cx - rx * 1.1, cy - ry, cx, cy - ry); g.closePath(); };
  g.save(); path(); g.fillStyle = WHITE; g.fill(); g.clip();
  const prx = rx * 0.62 * e.pupil, pry = ry * 0.55 * e.pupil;
  const px = cx + look[0] * rx * 0.45, py = cy + ry * 0.18 + look[1] * ry * 0.35;
  g.fillStyle = INK; ell(g, px, py, prx, pry); g.fill();
  if (e.pie > 0.05) {   // the pie-cut: a wedge of white from the pupil's centre to its upper edge
    const wa = (side > 0 ? -60 : -120) * Math.PI / 180, r1 = Math.max(prx, pry) * 1.3, h = 0.32 * Math.min(1, e.pie);
    g.beginPath(); g.moveTo(px + prx * 0.15 * Math.cos(wa), py + pry * 0.2 * Math.sin(wa)); g.lineTo(px + r1 * Math.cos(wa - h), py + r1 * Math.sin(wa - h)); g.lineTo(px + r1 * Math.cos(wa + h), py + r1 * Math.sin(wa + h)); g.closePath(); g.fillStyle = WHITE; g.fill();
  }
  if (shut > 0.02) {
    const ly = cy - ry + 2 * ry * shut, tilt = e.rot * (1 - Math.max(blink, hp)), yIn = ly + tilt * ry * side, yOut = ly - tilt * ry * side;
    const xl = cx - rx * 1.3, xr = cx + rx * 1.3, [yl, yr] = side > 0 ? [yIn, yOut] : [yOut, yIn];
    g.beginPath(); g.moveTo(xl, cy - ry * 2); g.lineTo(xr, cy - ry * 2); g.lineTo(xr, yr); g.lineTo(xl, yl); g.closePath(); g.fillStyle = SKIN; g.fill();
    g.beginPath(); g.moveTo(xl, yl); g.lineTo(xr, yr); g.strokeStyle = INK; g.lineWidth = LW; g.stroke();
  }
  if (e.lower > 0.02) {   // the lower lid, pushed up by the cheek
    const ly = cy + ry - 2 * ry * e.lower, xl = cx - rx * 1.3, xr = cx + rx * 1.3;
    g.beginPath(); g.moveTo(xl, cy + ry * 2); g.lineTo(xr, cy + ry * 2); g.lineTo(xr, ly); g.quadraticCurveTo(cx, ly - ry * 0.25, xl, ly); g.closePath(); g.fillStyle = SKIN; g.fill();
    g.beginPath(); g.moveTo(xl, ly); g.quadraticCurveTo(cx, ly - ry * 0.25, xr, ly); g.strokeStyle = INK; g.lineWidth = LWI; g.stroke();
  }
  g.restore();
  path(); g.strokeStyle = INK; g.lineWidth = LW; g.lineJoin = 'round'; g.stroke();
}

function mouth(g, m, e) {
  const P = m.pts.map(p => [p[0], p[1] + m.y]), top = P.slice(0, 5);
  const bot = Math.max(P[6][1], P[7][1]), h = (P[6][1] + P[7][1]) / 2 - P[2][1], w = P[4][0] - P[0][0], cx = (P[0][0] + P[4][0]) / 2;
  // the lower lip
  ell(g, cx, bot + e.lipD, e.lipRx, e.lipRy); g.fillStyle = LIP; g.fill(); g.strokeStyle = INK; g.lineWidth = LWI; g.stroke();
  if (h < 2.5) return;
  g.save(); g.beginPath(); smoothPath(g, P, true, 0.9); g.fillStyle = MOUTH; g.fill(); g.clip();
  const dep = bot - P[2][1];
  ell(g, cx + w * 0.04, bot + dep * 0.02, w * 0.3, dep * 0.42); g.fillStyle = TONGUE; g.fill(); g.strokeStyle = INK; g.lineWidth = 1.6; g.stroke();
  g.beginPath(); g.moveTo(cx + w * 0.04, bot - dep * 0.28); g.lineTo(cx + w * 0.05, bot); g.strokeStyle = '#a8382b'; g.lineWidth = 1.4; g.stroke();
  if (e.teeth > 0.05) {   // the row of upper teeth along the upper edge, the gaps between them
    g.globalAlpha = Math.min(1, e.teeth);
    g.beginPath(); smoothPath(g, [...top.map(([x, y]) => [x, y - 6]), ...top.slice().reverse().map(([x, y]) => [x, y + e.th])], true, 0.8);
    g.fillStyle = WHITE; g.fill(); g.strokeStyle = INK; g.lineWidth = 1.6; g.stroke();
    g.strokeStyle = '#9a8f84'; g.lineWidth = 1.2;
    for (const k of [-1.5, -0.5, 0.5, 1.5]) { const x = cx + k * w / 2 * 0.36; g.beginPath(); g.moveTo(x, P[2][1] - 8); g.lineTo(x, P[2][1] + e.th + 2); g.stroke(); }
    g.globalAlpha = 1;
  }
  g.restore();
  g.beginPath(); smoothPath(g, P, true, 0.9); g.strokeStyle = INK; g.lineWidth = LWI + 0.6; g.lineJoin = 'round'; g.stroke();
}

// the whole painted face: f = vecExpr(…) plus live things {look, blink}. The canvas stays clear where nothing is
// painted: the skin ball and the hair form show their own paint there.
export function drawFace(cv, f, live = {}) {
  const g = cv.getContext('2d');
  g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, cv.width, cv.height);
  g.setTransform(PX, 0, 0, PX, -X0 * PX, -Y0 * PX);
  g.lineCap = 'round'; g.lineJoin = 'round';
  // the lighter ticks of the curls and the beard
  g.strokeStyle = HAIR_HI; g.lineWidth = 2.2;
  for (const [x, y] of [[-44, 62], [-22, 86], [8, 92], [36, 74], [52, 50], [-56, 40], [-30, -66], [-4, -74], [24, -68], [-50, -44], [46, -50], [8, -58]]) {
    const s = y < 0 ? -1 : 1; g.beginPath(); smoothPath(g, [[x - 7, y - 3 * s], [x - 2, y + 5 * s], [x + 6, y + 1 * s]], false); g.stroke();
  }
  g.fillStyle = CHEEK; g.globalAlpha = 0.5;
  g.save(); g.beginPath(); smoothPath(g, FACE_LOOP, true); g.clip();   // (on the skin only)
  for (const x of [-42, 42]) { ell(g, x, 20, 11 * f.blush, 11 * f.blush * 0.8); g.fill(); }
  g.restore(); g.globalAlpha = 1;
  const look = live.look || f.look, blink = live.blink || 0;
  for (const [side, x] of [[-1, -18], [1, 18]]) eye(g, x, -2, 15, 19.5, f, side, blink, look);
  mouth(g, f.mouth, f);
  // the edge of the hair and the beard round the bare face, in ink
  g.beginPath(); smoothPath(g, FACE_LOOP, true); g.strokeStyle = INK; g.lineWidth = LW; g.stroke();
  // the thick black brows (lib.brow, th 13), over the hairline
  for (const [side, x] of [[-1, -18], [1, 18]]) {
    const bx = x + side * 3, by = -30 + f.browY, w = 30, t = f.brow, xi = bx - side * w / 2, xo = bx + side * w / 2;
    tline(g, [[xi, by - t * w * 0.35], [bx, by - 0.3 * w * 0.5 - t * w * 0.1], [xo, by + t * w * 0.1]], 13 * 0.55, 13, 13 * 0.3);
  }
}
