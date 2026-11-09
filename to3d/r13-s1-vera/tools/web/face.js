// The face moved by a few numbers (Р6's rig; the head's own scale hs and the features' places come from the pack), on the skinned body: lids turned over the balls (a blink shuts each lid by the
// angle its margin needs, found on the model — tools/build.py lid_data), the balls turned (gaze), the jaw opened, the
// mouth's corners up/down/out/in, the upper lip lifted off the teeth, the brows' skin lifted; the face layer's brows
// (paint.js) follow the same numbers. Fields are computed once on the rest head (drawing head units: y up, x his
// left, z forward) and combined each frame; the displacement is turned with the Head joint and added to the skin.
//
// params: blink 0…1 (both lids shut), up / low — extra lid turn, degrees (up > 0 lowers the upper lid, low > 0 raises
//   the lower), lookX / lookY — the balls turned (deg; X to his left, Y down), pupil (scale), jaw (deg), smile
//   (−1 frown … 1), skew (his left corner up more), wide (an «и»), pucker (an «о»/«у»), upper (upper lip up),
//   brow, inner, outer, browR (his right brow alone)
const sm = (x, a, b) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const g3 = (x, y, z, c, s) => Math.exp(-(((x - c[0]) / s[0]) ** 2 + ((y - c[1]) / s[1]) ** 2 + ((z - c[2]) / s[2]) ** 2));

export const PARAMS = ['blink', 'up', 'low', 'lookX', 'lookY', 'pupil', 'jaw', 'smile', 'skew', 'wide', 'pucker', 'upper', 'brow', 'inner', 'outer', 'browR'];

export class FaceRig {
  constructor(h, a) {
    this.h = h; const hs = h.hs || 1, K = h.K * hs, HY = h.headY / hs, HZ = (h.headZ || 0) / hs, P = a.positions, F = a.face, JW = a.jaw;
    this.KH = K; const EX = h.eye.x, EY = -h.eye.y, BY = EY + h.eye.browH + 0.8;
    this.balls = h.balls; this.MY = h.mouthY; this.LZ = h.lipZ;
    const idx = [];
    for (const name of ['head', 'eyeL', 'eyeR', 'teethUp', 'teethLo']) { const [s, e] = h.ranges[name]; for (let i = s; i < e; i++) idx.push(i); }
    const n = idx.length; this.idx = Int32Array.from(idx);
    this.rest = new Float64Array(n * 3); this.kind = new Uint8Array(n); this.lid = new Float32Array(n * 4);
    const kindOf = i => { for (const [k, name] of [[1, 'eyeL'], [2, 'eyeR'], [3, 'teethUp'], [4, 'teethLo']]) { const [s, e] = h.ranges[name]; if (i >= s && i < e) return k; } return 0; };
    for (let k = 0; k < n; k++) {
      const i = idx[k];
      this.rest[k * 3] = P[i * 3] / K; this.rest[k * 3 + 1] = P[i * 3 + 1] / K - HY; this.rest[k * 3 + 2] = P[i * 3 + 2] / K - HZ;
      this.kind[k] = kindOf(i); for (let j = 0; j < 4; j++) this.lid[k * 4 + j] = F[i * 4 + j];
    }
    // static fields
    this.wJaw = new Float32Array(n); this.wCorner = [new Float32Array(n), new Float32Array(n)]; this.wUpLip = new Float32Array(n);
    this.wLips = new Float32Array(n); this.wLoLip = new Float32Array(n); this.wBrow = [[new Float32Array(n), new Float32Array(n)], [new Float32Array(n), new Float32Array(n)]];
    this.wCheek = [new Float32Array(n), new Float32Array(n)];
    const MY = this.MY, LZ = this.LZ;
    for (let k = 0; k < n; k++) {
      const x = this.rest[k * 3], y = this.rest[k * 3 + 1], z = this.rest[k * 3 + 2], kd = this.kind[k];
      if (kd === 1 || kd === 2) continue;
      // the jaw: below the mouth line, forward of the ear, fading under the chin into the neck
      this.wJaw[k] = JW[idx[k]];
      for (const [si, sd] of [[0, 1], [1, -1]]) {
        this.wCorner[si][k] = kd ? 0 : g3(x, y, z, [sd * 11.5, MY, LZ - 3], [7.5, 6, 14]);
        this.wCheek[si][k] = kd ? 0 : g3(x, y, z, [sd * 19, MY + 14, LZ], [9, 7, 18]);
        this.wBrow[si][0][k] = kd ? 0 : g3(x, y, z, [sd * (EX + 7.5), BY, 30], [9, 6, 20]);    // the outer brow
        this.wBrow[si][1][k] = kd ? 0 : g3(x, y, z, [sd * (EX - 7.5), BY - 1, 32], [8, 6, 20]);    // the inner brow
      }
      this.wUpLip[k] = kd ? 0 : g3(x, y, z, [0, MY + 2.2, LZ], [9, 2.6, 6]) * sm(y, MY - 0.2, MY + 1.0);
      this.wLips[k] = kd ? 0 : g3(x, y, z, [0, MY, LZ], [11, 6, 8]);
      this.wLoLip[k] = kd ? 0 : g3(x, y, z, [0, MY - 2.5, LZ + 2], [9, 3.5, 6]) * this.wJawPre(k, JW, idx);
    }
    this.delta = new Float32Array(n * 3);
  }

  wJawPre(k, JW, idx) { return JW[idx[k]]; }

  // the displacement (head units) for params q, into this.delta
  update(q) {
    const n = this.idx.length, R = this.rest, D = this.delta, B = this.balls;
    const p = [0, 0, 0];
    const blink = q.blink || 0, up = q.up || 0, low = q.low || 0, lx = q.lookX || 0, ly = q.lookY || 0;
    const jaw = (q.jaw || 0) * Math.PI / 180, JP = [0, -12, -6];
    const smile = q.smile || 0, skew = q.skew || 0, wide = q.wide || 0, pk = q.pucker || 0, upper = q.upper || 0;
    for (let k = 0; k < n; k++) {
      p[0] = R[k * 3]; p[1] = R[k * 3 + 1]; p[2] = R[k * 3 + 2];
      const x0 = p[0], y0 = p[1], z0 = p[2], kd = this.kind[k];
      if (kd === 1 || kd === 2) {
        const b = B[kd - 1];
        rotX(p, b, ly); rotY(p, b, lx);
      } else {
        // lids
        const L = this.lid, w = L[k * 4 + 2];
        if (w > 0) {
          const b = B[L[k * 4 + 3] > 0 ? 0 : 1];
          const cheek = Math.max(smile, 0) * 6;
          if (L[k * 4] > 0) { const full = L[k * 4] * w; rotX(p, b, Math.min(full, blink * full + (up + 0.75 * ly) * w)); }
          else { const full = L[k * 4 + 1] * w; rotX(p, b, -Math.min(full * 1.6, blink * full + (low + cheek - 0.35 * ly) * w)); }
        }
        // jaw
        const wj = this.wJaw[k];
        if (wj > 0 && jaw) rotXa(p, JP, jaw * wj);
        // mouth corners, lips
        for (let si = 0; si < 2; si++) {
          const sd = si === 0 ? 1 : -1, g = this.wCorner[si][k];
          if (g > 1e-4) {
            const sm_ = smile + sd * skew;
            p[0] += g * (sd * 2.4 * Math.max(sm_, 0) + sd * 2.6 * wide - sd * 3.4 * pk);
            p[1] += g * (4.6 * Math.max(sm_, 0) + 3.4 * Math.min(sm_, 0));
            p[2] += g * (-1.6 * Math.max(sm_, 0) - 0.8 * wide + 1.2 * pk);
          }
          const c = this.wCheek[si][k];
          if (c > 1e-4) { const sm_ = Math.max(smile + sd * skew, 0); p[1] += c * 2.2 * sm_; p[2] += c * 1.2 * sm_; }
          const bo = this.wBrow[si][0][k], bi = this.wBrow[si][1][k];
          if (bo + bi > 1e-4) {
            let raise = (q.brow || 0) * 3.2; if (sd < 0 && q.browR != null) raise += q.browR * 2.6;
            p[1] += bo * (raise + (q.outer || 0) * 3) + bi * (raise + (q.inner || 0) * 3.6);
            p[2] += bi * Math.min(0, q.inner || 0) * -1.0;
          }
        }
        if (pk) { const g = this.wLips[k]; p[2] += 2.4 * pk * g; }
        const u = this.wUpLip[k]; if (u > 1e-4) { p[1] += u * upper * 3.4; p[2] -= u * upper * 0.6; }
        const ll = this.wLoLip[k]; if (ll > 1e-4) { const o = (q.jaw || 0) * 0.13 + Math.max(smile, 0) * 0.8; p[1] -= ll * o; p[2] -= ll * o * 0.45; }
      }
      D[k * 3] = p[0] - x0; D[k * 3 + 1] = p[1] - y0; D[k * 3 + 2] = p[2] - z0;
    }
  }

  // add the displacement turned by the head's turn now (the Head joint's matrix) to the skinned positions
  apply(q, figure, sk) {
    this.update(q);
    const M = figure.skinner.matrix(figure.pose, sk.index.Head), K = this.KH, D = this.delta, pos = figure.positions;
    for (let k = 0; k < this.idx.length; k++) {
      const i = this.idx[k], x = D[k * 3] * K, y = D[k * 3 + 1] * K, z = D[k * 3 + 2] * K;
      if (x === 0 && y === 0 && z === 0) continue;
      pos[i * 3] += M[0] * x + M[1] * y + M[2] * z; pos[i * 3 + 1] += M[4] * x + M[5] * y + M[6] * z; pos[i * 3 + 2] += M[8] * x + M[9] * y + M[10] * z;
    }
  }
}

// turn about the ball's x axis through c by deg (positive: the front goes down), and about its y axis (to his left)
function rotX(p, c, deg) {
  if (!deg) return; const a = deg * Math.PI / 180, co = Math.cos(a), si = Math.sin(a);
  const y = p[1] - c[1], z = p[2] - c[2]; p[1] = c[1] + y * co - z * si; p[2] = c[2] + y * si + z * co;
}
function rotXa(p, c, a) { const co = Math.cos(a), si = Math.sin(a); const y = p[1] - c[1], z = p[2] - c[2]; p[1] = c[1] + y * co - z * si; p[2] = c[2] + y * si + z * co; }
function rotY(p, c, deg) {
  if (!deg) return; const a = deg * Math.PI / 180, co = Math.cos(a), si = Math.sin(a);
  const x = p[0] - c[0], z = p[2] - c[2]; p[0] = c[0] + x * co + z * si; p[2] = c[2] - x * si + z * co;
}

// Вера's faces in these numbers. The style drew no expression sheet for her: these follow the style's sheet
// (styles/s1-pixar/tools/build.py EXPR) held back to her character — she is strict and does not laugh aloud
export const EXPRESSIONS = {
  calm: { smile: -0.12, up: 19, low: 7, inner: -0.15, lookY: 1 },
  strict: { smile: -0.3, up: 13, low: 5, brow: -0.25, inner: -0.7, browR: 0.5, lookX: 6 },
  joy: { smile: 0.95, upper: 0.25, wide: 0.3, low: 8, up: 5, brow: 0.35 },
  surprise: { jaw: 12, pucker: 0.5, up: -7, low: -3, brow: 1.2, pupil: 0.8 },
  sad: { smile: -0.9, inner: 1.2, brow: -0.1, up: 14, lookY: 11, low: 2 },
  anger: { smile: -0.55, jaw: 5, upper: 0.7, wide: 0.5, up: 11, low: 8, brow: -0.6, inner: -1.4 },
};
export function mixParams(weights) {
  const out = {}; for (const k of PARAMS) out[k] = k === 'pupil' ? 1 : 0;
  let tot = 0; for (const w of Object.values(weights)) tot += w;
  for (const [name, w] of Object.entries(weights)) {
    const e = EXPRESSIONS[name]; if (!e) continue;
    for (const k of PARAMS) { if (k === 'browR') continue; out[k] += ((k === 'pupil' ? (e.pupil ?? 1) - 1 : (e[k] || 0))) * w / Math.max(tot, 1e-6); }
    out.browR += (e.browR || 0) * w / Math.max(tot, 1e-6);
  }
  return out;
}
