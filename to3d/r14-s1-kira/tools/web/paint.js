// The painted layers. The face layer: what the drawing paints on the face — blush, the brows (they move with the
// expression), the lips' colour in the drawing's own shapes, her lines — drawn into a canvas the head takes by its front
// projection (u = (x + 60) / 120, v = (y + 60) / 120 in the drawing's head units, y down). The brows follow face.py
// draw_brow line for line, with the expression's numbers continuous. The cloth layer: the hoodie's front (pocket,
// cords, folds) in the drawing's person units, taken by the hoodie's rest place.
import * as THREE from 'three';

const S = 1024;
export class FacePaint {
  constructor(d) {
    this.d = d;
    this.canvas = document.createElement('canvas'); this.canvas.width = this.canvas.height = S;
    this.ctx = this.canvas.getContext('2d');
    this.texture = new THREE.CanvasTexture(this.canvas); this.texture.flipY = false; this.texture.anisotropy = 4;
    this.texture.colorSpace = THREE.SRGBColorSpace;
    this.base = this.baseLayer();
    this.key = '';
  }
  X(x) { return (x + 60) / 120 * S; }
  Y(y) { return (y + 60) / 120 * S; }
  // what does not move: blush, freckles, the nostrils' tint
  baseLayer() {
    const c = document.createElement('canvas'); c.width = c.height = S; const g = c.getContext('2d'), d = this.d, k = S / 120;
    for (const sd of [-1, 1]) {
      const x = this.X(sd * d.blush_x), y = this.Y(d.blush_y), r = 11 * k;
      const gr = g.createRadialGradient(x, y, 0, x, y, r);
      gr.addColorStop(0, hexA(d.blush, Math.min(1, d.blush_a * 1.25))); gr.addColorStop(0.55, hexA(d.blush, d.blush_a * 0.55)); gr.addColorStop(1, hexA(d.blush, 0));
      g.fillStyle = gr; g.beginPath(); g.ellipse(x, y, r, r * 0.75, 0, 0, 7); g.fill();
    }
    // the lips: the drawing's two shapes in its lip colour (the upper a little darker), their edges soft
    g.save(); g.filter = `blur(${0.25 * k}px)`;
    for (const [pts, col, a] of [[d.lips.up, mixHex(d.lip, '#3a1515', 0.18), d.lip_soft ? 0.45 : 0.85], [d.lips.low, d.lip, d.lip_soft ? 0.55 : 0.9]]) {
      g.fillStyle = hexA(col, a); g.beginPath(); smooth(g, pts.map(([x, y]) => [this.X(x), this.Y(y)])); g.fill();
    }
    g.restore();
    // her lines (the drawing's «lines»: by the mouth, between the brows)
    g.save(); g.filter = `blur(${0.3 * k}px)`; g.lineCap = 'round'; g.lineWidth = 0.8 * k;
    for (const [path, a] of d.lines || []) { g.strokeStyle = hexA(mixHex(d.skin_sh, '#4a2018', 0.25), Math.min(1, a * 2.2)); g.beginPath(); smooth(g, path.map(([x, y]) => [this.X(x), this.Y(y)]), false); g.stroke(); }
    g.restore();
    for (const [x, y, r, col, a] of d.spots) {
      g.fillStyle = hexA(col, a * 0.85); g.beginPath(); g.arc(this.X(x), this.Y(y + 1.5), r * k * 1.0, 0, 7); g.fill();
    }
    return c;
  }
  // p: the face's params (face.js): brow (raise), inner (inner ends up +), outer, browL (his right brow alone), lip
  draw(p) {
    const key = [p.brow, p.inner, p.outer, p.browR].map(v => (v || 0).toFixed(3)).join(',');
    if (key === this.key) return; this.key = key;
    const g = this.ctx, d = this.d, k = S / 120;
    g.clearRect(0, 0, S, S); g.drawImage(this.base, 0, 0);
    for (const side of [-1, 1]) {
      const x0 = d.eye_x * side, y0 = d.eye_y - d.brow_h - d.brow_up;   // higher than drawn: in 3D the upper lid's fold is there, and it moves
      const L = d.brow_len, th = d.brow_w;
      // side −1 is screen left in the front view: his right brow
      let raise = (p.brow || 0) * 5; if (side < 0 && p.browR != null) raise += p.browR * 4;
      const bi = (p.inner || 0) * 6, bo = (p.outer || 0) * 5, arch = d.brow_arch;
      const top = [], bot = [];
      for (let i = 0; i <= 8; i++) {
        const t = i / 8, x = x0 + side * (-L * 0.52 + L * t);
        const y = y0 - raise - arch * Math.sin(Math.PI * t ** 0.8) - bi * (1 - t) ** 1.5 - bo * t ** 1.5 + t * 1.0;
        const w = th * (0.75 + 0.5 * Math.sin(Math.PI * Math.min(1, t * 1.3))) * (1.15 - 0.85 * t ** 2.2);
        top.push([x, y - w * 0.55]); bot.push([x, y + w * 0.45]);
      }
      const pts = top.concat(bot.reverse());
      g.fillStyle = d.brow_col; g.beginPath(); smooth(g, pts.map(([x, y]) => [this.X(x), this.Y(y)])); g.fill();
      g.strokeStyle = 'rgba(255,240,220,0.18)'; g.lineWidth = 0.35 * k; g.beginPath(); smooth(g, top.slice(0, 5).map(([x, y]) => [this.X(x), this.Y(y)]), false); g.stroke();
    }
    this.texture.needsUpdate = true;
  }
}

function mixHex(a, b, t) { const p = parseInt(a.slice(1), 16), q = parseInt(b.slice(1), 16), m = s => Math.round(((p >> s) & 255) * (1 - t) + ((q >> s) & 255) * t); return '#' + ((1 << 24) | (m(16) << 16) | (m(8) << 8) | m(0)).toString(16).slice(1); }

// the garment's front, painted once: 4 px per unit of the drawing (a patch, seams — lines with a width, an opacity and
// a blur —, dots)
export function clothLayer(d) {
  const c = d.cloth, [x0, y0, w, h] = c.box, k = 4;
  const cv = document.createElement('canvas'); cv.width = w * k; cv.height = h * k; const g = cv.getContext('2d');
  const X = x => (x - x0) * k, Y = y => (y - y0) * k, path = (pts, closed) => { g.beginPath(); smooth(g, pts.map(([x, y]) => [X(x), Y(y)]), closed); };
  if (c.patch) { g.fillStyle = hexA(c.patch_col, 0.55); path(c.patch, true); g.fill(); }
  g.lineCap = 'round'; g.lineJoin = 'round';
  for (const s of c.seams || []) { g.save(); if (s.blur) g.filter = `blur(${s.blur * k}px)`; g.strokeStyle = hexA(s.col, s.a); g.lineWidth = s.w * k; path(s.pts, false); g.stroke(); g.restore(); }
  for (const [x, y, r, col] of c.dots || []) { g.fillStyle = col; g.beginPath(); g.arc(X(x), Y(y), r * k, 0, 7); g.fill(); }
  const t = new THREE.CanvasTexture(cv); t.flipY = false; t.anisotropy = 4; t.colorSpace = THREE.SRGBColorSpace; return t;
}

function hexA(h, a) { const n = parseInt(h.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
// Catmull-Rom through points (as pix.smooth_path)
function smooth(g, P, closed = true) {
  const n = P.length; g.moveTo(P[0][0], P[0][1]);
  const m = closed ? n : n - 1;
  for (let i = 0; i < m; i++) {
    const p0 = P[(i - 1 + n) % n], p1 = P[i], p2 = P[(i + 1) % n], p3 = P[(i + 2) % n];
    const q0 = closed || i > 0 ? p0 : p1, q3 = closed || i + 2 < n ? p3 : p2;
    g.bezierCurveTo(p1[0] + (p2[0] - q0[0]) / 6, p1[1] + (p2[1] - q0[1]) / 6, p2[0] - (q3[0] - p1[0]) / 6, p2[1] - (q3[1] - p1[1]) / 6, p2[0], p2[1]);
  }
  if (closed) g.closePath();
}
