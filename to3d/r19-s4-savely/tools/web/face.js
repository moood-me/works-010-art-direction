// The face moved by a few numbers, on top of the skinned body (after Р2's face.mjs and Р7's face.js).
import { CHAR } from './char.js';
// The measures come from face.json (build.py): eye centres, the ball's radius, the mouth's line and corners, in the
// drawing's units (y down, z toward the viewer); which vertices are the skin (the head, shells of hair on it) and
// the irises (ranges, skin).
// params (all 0 at rest):
//   up, low   — the upper / lower lid turned over the ball (degrees; up > 0 closes down, low > 0 closes up)
//   jaw       — the jaw opened (degrees, about a pivot below the ear)
//   smile     — the mouth's corners up and back (+) or down (−); wide — pulled out; pucker — drawn in and forward
//   brow      — the brow skin lifted (+) or lowered (−); inner — the inner ends more (sad +, angry −);
//   knit      — the inner ends drawn together and down (a frown)
//   lookX, lookY — the irises turned (degrees: to her left on screen in front view +, down +); iris — iris scale
// The painted layer (brows, lash line, lips) rides on the skin's vertices, so it moves with them.
const smooth = (x, a, b) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
function rotX(p, c, deg, w) {
  const a = deg * Math.PI / 180 * w, co = Math.cos(a), si = Math.sin(a);
  const y = p[1] - c[1], z = p[2] - c[2];
  p[1] = c[1] + y * co + z * si; p[2] = c[2] - y * si + z * co;
}
function rotY(p, c, deg, w) {
  const a = deg * Math.PI / 180 * w, co = Math.cos(a), si = Math.sin(a);
  const x = p[0] - c[0], z = p[2] - c[2];
  p[0] = c[0] + x * co + z * si; p[2] = c[2] - x * si + z * co;
}
const gauss = (p, c, s) => Math.exp(-(((p[0] - c[0]) / s[0]) ** 2 + ((p[1] - c[1]) / s[1]) ** 2 + ((p[2] - c[2]) / s[2]) ** 2));

export class Face {
  constructor(body, data, H) {
    this.d = data; this.body = body;
    const K = H.K, F = H.FEET, Z = H.ZOFF, P = body.positions;
    this.K = K;
    const take = ([a, b]) => { const out = new Float64Array((b - a) * 3);
      for (let i = a; i < b; i++) { out[(i - a) * 3] = P[i * 3] / K; out[(i - a) * 3 + 1] = F - P[i * 3 + 1] / K; out[(i - a) * 3 + 2] = (P[i * 3 + 2] - Z) / K; }
      return out; };
    this.pieces = [...(data.skin || ['head']), 'irisL', 'irisR'].map(name => ({ name, r: data.ranges[name], rest: take(data.ranges[name]) }));
    this.delta = new Float32Array(body.N * 3);
  }
  update(q) {
    const d = this.d, K = this.K, E = d.eyes, RB = d.rb, MY = d.mouth.y, MW = d.mouth.w, MZ = d.mouth.z, JAW = d.jaw;
    const p = [0, 0, 0];
    for (const pc of this.pieces) {
      const iris = pc.name.startsWith('iris'), head = !iris;   // skin: the head and the hair shells lying on it (brows, moustache)
      const [a] = pc.r, R = pc.rest, n = R.length / 3;
      for (let i = 0; i < n; i++) {
        p[0] = R[i * 3]; p[1] = R[i * 3 + 1]; p[2] = R[i * 3 + 2];
        const x0 = p[0], y0 = p[1], z0 = p[2];
        if (head) {
          for (const c of E) {
            const dist = Math.hypot(p[0] - c[0], p[1] - c[1], p[2] - c[2]);
            const w = (1 - smooth(dist, RB + 1.5, RB + 7.0)) * smooth(p[2] - c[2], -2, 3) * (1 - smooth(Math.abs(p[0] - c[0]), 20, 26));
            if (w > 0) { if (p[1] < c[1] - 0.5) rotX(p, c, q.up || 0, w); else rotX(p, c, -(q.low || 0), w); }
          }
          if (q.jaw) {
            const wj = smooth(p[1], MY - 0.5, MY + 3) * (1 - smooth(p[1], 125, 150)) * smooth(p[2], -30, 0);
            if (wj > 0) rotX(p, JAW, q.jaw, wj);
          }
          const s = q.smile || 0, wd = q.wide || 0, pk = q.pucker || 0;
          if (s || wd || pk) for (const side of [1, -1]) {
            const g = gauss(p, [side * MW, MY, MZ - 4], [9, 8, 14]);
            if (g < 1e-4) continue;
            p[0] += g * (side * 3.0 * Math.max(s, 0) + side * 3.0 * wd - side * 3.5 * pk);
            p[1] += g * (-6.0 * s);
            p[2] += g * (-1.8 * Math.abs(s) - 1.0 * wd + 2.0 * pk);
            // the cheek rises with a smile (pushes the lower lid up a little)
            const gc = gauss(p, [side * 30, 32, MZ - 14], [14, 12, 20]);
            p[1] -= gc * 2.2 * Math.max(s, 0);
          }
          if (pk) { const g = gauss(p, [0, MY, MZ], [12, 8, 10]); p[2] += 2.2 * pk * g; }
          const b = q.brow || 0, inner = q.inner || 0, kn = q.knit || 0;
          if (b || inner || kn) for (const side of [1, -1]) {
            const gO = gauss(p, [side * 40, -22, 70], [13, 10, 40]);
            const gI = gauss(p, [side * 16, -20, 74], [11, 10, 40]);
            p[1] -= gO * b + gI * (b + inner) - gI * kn * 2.5;
            p[0] -= gI * side * kn * 2.5;
          }
        }
        if (iris) {
          const c = pc.name.endsWith('L') ? E[0] : E[1];
          if (q.lookY) rotX(p, c, -q.lookY, 1);
          if (q.lookX) rotY(p, c, q.lookX, 1);
          const k = q.iris ?? 1;
          if (k !== 1) { p[0] = c[0] + (p[0] - c[0]) * k; p[1] = c[1] + (p[1] - c[1]) * k; }
        }
        const j = (a + i) * 3;
        this.delta[j] = (p[0] - x0) * K; this.delta[j + 1] = -(p[1] - y0) * K; this.delta[j + 2] = (p[2] - z0) * K;
      }
    }
    return this.delta;
  }
  // add the displacement, turned by the head's turn now (M: 3×4 rows from skinner.matrix(pose, Head)), to positions
  apply(positions, M) {
    const D = this.delta;
    for (const pc of this.pieces) for (let i = pc.r[0]; i < pc.r[1]; i++) {
      const x = D[i * 3], y = D[i * 3 + 1], z = D[i * 3 + 2];
      if (x === 0 && y === 0 && z === 0) continue;
      positions[i * 3] += M[0] * x + M[1] * y + M[2] * z;
      positions[i * 3 + 1] += M[4] * x + M[5] * y + M[6] * z;
      positions[i * 3 + 2] += M[8] * x + M[9] * y + M[10] * z;
    }
  }
}

// the drawing's expressions as params of the 3D face: char.js
export const EXPRESSIONS = CHAR.expressions;
export const PARAMS = ['up', 'low', 'jaw', 'smile', 'wide', 'pucker', 'brow', 'inner', 'knit', 'lookX', 'lookY', 'iris'];

// a mix of expressions: {joy: 0.6, surprise: 0.4} → params (weights normalised when their sum is over 1)
export function mix(weights) {
  const out = {};
  for (const k of PARAMS) out[k] = k === 'iris' ? 1 : 0;
  let tot = 0; for (const w of Object.values(weights)) tot += w;
  for (const [name, w] of Object.entries(weights)) {
    const e = EXPRESSIONS[name]; if (!e) continue;
    for (const k of PARAMS) out[k] += ((k === 'iris' ? (e.iris ?? 1) - 1 : (e[k] || 0))) * w / Math.max(tot, 1);
  }
  return out;
}
