// Савелий Петрович's live face: the face's form moved by a few numbers, on top of the skinned body.
// Runs in node (the renders) and in the browser (view.html) alike. The measures come from face.json (assemble.py):
// eye centres, the ball's radius, the mouth line, the jaw's pivot, in the drawing's units (y down, z toward the
// viewer), and which of the body's vertices are the head, the irises, the moustache and the face's ink marks.
//
// params (all 0 at rest):
//   up, low  — the upper / lower lid turned over the ball (degrees; up > 0 closes down, low > 0 closes up)
//   jaw      — the jaw opened (degrees, about a pivot below the ear)
//   smile    — the mouth's corners up and back (+) or down (−), the moustache's ends with them
//   wide     — the corners pulled out (an «и»), pucker — drawn in and forward (an «о», «у»)
//   brow     — the brow skin lifted (+) or lowered (−); inner — the inner ends more (sad +, angry −)
//   lookX, lookY — the irises turned (degrees: right on screen in the front view +, down +)
//   iris     — the iris scale (1: as is; < 1 smaller: surprise)
// Each piece is moved by fields over space, so neighbouring pieces (the lip, the moustache over it, a brow mark on
// the brow) move alike. The result is a displacement in the head's rest frame; the caller turns it with the head.

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
  // body: an engine body (rest positions in metres); data: face.json
  constructor(body, data) {
    this.d = data; this.body = body;
    const K = data.K, F = data.floor, P = body.positions;
    const take = r => { const [a, b] = r, out = new Float64Array((b - a) * 3);
      for (let i = a; i < b; i++) { out[(i - a) * 3] = P[i * 3] / K; out[(i - a) * 3 + 1] = F - P[i * 3 + 1] / K; out[(i - a) * 3 + 2] = P[i * 3 + 2] / K; }
      return out; };
    this.pieces = [];
    for (const [name, r] of Object.entries(data.pieces)) this.pieces.push({ name, r, rest: take(r) });
    data.marks.forEach((r, i) => this.pieces.push({ name: 'mark', r, rest: take(r) }));
    this.delta = new Float32Array(body.N * 3);       // metres, the head's rest frame (engine axes)
    this.touched = this.pieces.map(p => p.r);
  }

  // the displacement of every face vertex for these params, into this.delta (engine axes, metres)
  update(q) {
    const d = this.d, K = d.K, E = d.eyes, RB = d.rb, MY = d.mouthY, JAW = d.jaw;
    const p = [0, 0, 0];
    for (const pc of this.pieces) {
      const head = pc.name === 'head' || pc.name === 'mark', iris = pc.name.startsWith('iris');
      const stache = pc.name.startsWith('stache');
      const [a] = pc.r, R = pc.rest, n = R.length / 3;
      for (let i = 0; i < n; i++) {
        p[0] = R[i * 3]; p[1] = R[i * 3 + 1]; p[2] = R[i * 3 + 2];
        const x0 = p[0], y0 = p[1], z0 = p[2];
        if (head) {
          for (const c of E) {
            const dist = Math.hypot(p[0] - c[0], p[1] - c[1], p[2] - c[2]);
            const w = (1 - smooth(dist, RB + 2.0, RB + 6.5)) * smooth(p[2] - c[2], -2, 3);
            if (w > 0) { if (p[1] < c[1]) rotX(p, c, q.up || 0, w); else rotX(p, c, -(q.low || 0), w); }
          }
          if (q.jaw) {
            const wj = smooth(p[1], MY - 1, MY + 4) * (1 - smooth(p[1], 125, 150)) * smooth(p[2], -20, 10);
            if (wj > 0) rotX(p, JAW, q.jaw, wj);
          }
        }
        if (head || stache) {
          const s = q.smile || 0, wd = q.wide || 0, pk = q.pucker || 0;
          for (const side of [1, -1]) {
            const g = gauss(p, [side * 15, MY - 1, 72], [9, 7, 12]);
            if (g < 1e-4) continue;
            p[0] += g * (side * 2.0 * Math.max(s, 0) + side * 3.0 * wd - side * 3.5 * pk);
            p[1] += g * (-4.5 * s);
            p[2] += g * (-2.0 * Math.abs(s) - 1.0 * wd + 2.0 * pk);
          }
          if (pk) { const g = gauss(p, [0, MY, 74], [11, 7, 10]); p[2] += 2.2 * pk * g; }
          if (stache && q.jaw) p[1] -= 0.08 * q.jaw * smooth(p[1], 60, 85);   // the upper lip lifts the moustache a little
        }
        if (head) {
          const b = q.brow || 0, inner = q.inner || 0;
          if (b || inner) for (const side of [1, -1]) {
            p[1] -= gauss(p, [side * 32, 6, 70], [11, 8, 30]) * b;
            p[1] -= gauss(p, [side * 16, 6, 70], [11, 8, 30]) * (b + inner);
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

  // add the displacement, turned by the head's turn now (R: 3×4 rows from skinner.matrix(pose, Head)), to positions
  apply(positions, M) {
    const D = this.delta;
    for (const [a, b] of this.touched) for (let i = a; i < b; i++) {
      const x = D[i * 3], y = D[i * 3 + 1], z = D[i * 3 + 2];
      positions[i * 3] += M[0] * x + M[1] * y + M[2] * z;
      positions[i * 3 + 1] += M[4] * x + M[5] * y + M[6] * z;
      positions[i * 3 + 2] += M[8] * x + M[9] * y + M[10] * z;
    }
  }
}

// the five expressions of the drawing's sheet, as params
export const EXPRESSIONS = {
  calm: {},
  joy: { up: 34, low: 14, jaw: 7, smile: 1.0, brow: 2.5 },
  surprise: { up: -14, low: -8, jaw: 6, brow: 7, iris: 0.82 },
  sad: { up: 16, smile: -1.0, brow: 1.5, inner: 4, lookY: 7 },
  anger: { up: 12, low: 6, jaw: 5, smile: -0.8, brow: -4, inner: -5 },
};
export const PARAMS = ['up', 'low', 'jaw', 'smile', 'wide', 'pucker', 'brow', 'inner', 'lookX', 'lookY', 'iris'];

// a mix of expressions: {joy: 0.6, surprise: 0.4} → params
export function mix(weights) {
  const out = {};
  for (const k of PARAMS) out[k] = k === 'iris' ? 1 : 0;
  let tot = 0; for (const w of Object.values(weights)) tot += w;
  for (const [name, w] of Object.entries(weights)) {
    const e = EXPRESSIONS[name];
    for (const k of PARAMS) out[k] += ((k === 'iris' ? (e.iris ?? 1) - 1 : (e[k] || 0))) * w / Math.max(tot, 1);
  }
  return out;
}
