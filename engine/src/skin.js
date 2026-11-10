// One skinning for everything that moves with a body: the body, and what is attached to it.
//
// Methods (options.method):
//   'cor' — skinning with optimized centres of rotation (Le & Hodgins, SIGGRAPH 2016; the default). Each vertex turns
//           by its joints' turns blended as quaternions — so a forearm's twist doesn't collapse into a candy wrapper as
//           in linear blending — about a centre of rotation found once from the rest mesh (where vertices of like
//           weights lie), placed by linear blending — so a bent elbow or knee doesn't bulge as in dual quaternions.
//           Weights stay the artists' (Anny's); nothing is learned. The centres depend on the rest shape: a body
//           changed by a deformer makes a new Skinner.
//   'dqs' — dual quaternions (Kavan et al. 2007): keeps volume at twists, bulges a little at bends.
//   'lbs' — linear blending: the plain way; loses volume at twists and deep bends. For comparison.
// Fixes from Т7 (experiments/designed-form), as options:
//   clavicleShare (clavicleShare below, on the pose before skinning): the collarbone takes this share of the arm's
//           drop below its rest (Т7: a third), the arm keeping its direction — the shoulder's top rolls down with the
//           arm instead of leaving a shelf above it.
//   seam {iterations, rings}: where the trunk's weights hand the skin over to the collarbone's and the arm's, the skin's
//           movement (against the chest's) is smoothed over the surface, so no dent is left where they meet.
// Attachments: `matrix(pose, j)` — joint j's transform from the body's rest to now (3×4, rows); something rigid on a
// joint (eyes, a hat) is drawn with it times its own matrix at rest, so its own transform is kept.
import { qMul, qConj, qRot, qAxisAngle, getQ, setQ, getV, normalize, sub, cross } from './math.js';

export class Skinner {
  constructor(body, options = {}) {
    this.body = body;
    this.method = options.method || 'cor';
    if (!['cor', 'dqs', 'lbs'].includes(this.method)) throw new Error(`no skinning method "${this.method}"`);
    this.seam = options.seam || null;
    const N = body.N, sk = body.skeleton;
    this.N = N; this.J = sk.J;
    this.R = new Float64Array(this.J * 9); this.T = new Float64Array(this.J * 3);
    this.neighbours();
    if (this.method === 'cor') this.centres();
    if (this.seam) this.seamMask();
  }

  // each vertex's neighbours over the mesh (CSR)
  neighbours() {
    const { N } = this, tris = this.body.triangles, sets = Array.from({ length: N }, () => new Set());
    for (let t = 0; t < tris.length; t += 3) { const a = tris[t], b = tris[t + 1], c = tris[t + 2]; sets[a].add(b).add(c); sets[b].add(a).add(c); sets[c].add(a).add(b); }
    this.nbStart = new Int32Array(N + 1); let n = 0;
    for (let i = 0; i < N; i++) { this.nbStart[i] = n; n += sets[i].size; }
    this.nbStart[N] = n; this.nb = new Int32Array(n); n = 0;
    for (let i = 0; i < N; i++) for (const k of sets[i]) this.nb[n++] = k;
  }

  // the centres of rotation (Le & Hodgins 2016, eq. 3–4): for vertex i, the area-weighted mean of the triangles'
  // centroids, each by how alike its weights are to i's — s(wᵢ, w_t) = Σ_{j<k} wᵢⱼ wᵢₖ w_tⱼ w_tₖ exp(−((wᵢⱼ w_tₖ − wᵢₖ w_tⱼ)/σ)²)
  centres(sigma = 0.1) {
    const { N, body } = this, P = body.positions, tris = body.triangles, J = body.skin.joints, W = body.skin.weights;
    const T = tris.length / 3, pairs = new Map();
    for (let t = 0; t < T; t++) {
      const a = tris[t * 3], b = tris[t * 3 + 1], c = tris[t * 3 + 2];
      const w = new Map();
      for (const v of [a, b, c]) for (let k = 0; k < 4; k++) { const wt = W[v * 4 + k]; if (wt > 0) w.set(J[v * 4 + k], (w.get(J[v * 4 + k]) || 0) + wt / 3); }
      const e1 = sub(getV(P, b), getV(P, a)), e2 = sub(getV(P, c), getV(P, a));
      const area = 0.5 * Math.hypot(e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]);
      const cx = (P[a * 3] + P[b * 3] + P[c * 3]) / 3, cy = (P[a * 3 + 1] + P[b * 3 + 1] + P[c * 3 + 1]) / 3, cz = (P[a * 3 + 2] + P[b * 3 + 2] + P[c * 3 + 2]) / 3;
      const js = [...w.keys()].sort((x, y) => x - y);
      for (let x = 0; x < js.length; x++) for (let y = x + 1; y < js.length; y++) {
        const key = js[x] * 256 + js[y]; let L = pairs.get(key); if (!L) pairs.set(key, L = []);
        L.push(w.get(js[x]), w.get(js[y]), area, cx, cy, cz);
      }
    }
    const cor = new Float64Array(N * 3), has = new Uint8Array(N), s2 = sigma * sigma;
    for (let i = 0; i < N; i++) {
      const js = [], ws = [];
      for (let k = 0; k < 4; k++) if (W[i * 4 + k] > 0) { js.push(J[i * 4 + k]); ws.push(W[i * 4 + k]); }
      if (js.length < 2) continue;
      let nx = 0, ny = 0, nz = 0, d = 0;
      for (let x = 0; x < js.length; x++) for (let y = x + 1; y < js.length; y++) {
        let ja = js[x], jb = js[y], wa = ws[x], wb = ws[y];
        if (ja > jb) { [ja, jb] = [jb, ja]; [wa, wb] = [wb, wa]; }
        const L = pairs.get(ja * 256 + jb); if (!L) continue;
        for (let o = 0; o < L.length; o += 6) {
          const ta = L[o], tb = L[o + 1], e = wa * tb - wb * ta, s = wa * wb * ta * tb * Math.exp(-e * e / s2) * L[o + 2];
          nx += s * L[o + 3]; ny += s * L[o + 4]; nz += s * L[o + 5]; d += s;
        }
      }
      if (d > 1e-14) { cor[i * 3] = nx / d; cor[i * 3 + 1] = ny / d; cor[i * 3 + 2] = nz / d; has[i] = 1; }
    }
    this.cor = cor; this.hasCor = has;
  }

  // where the trunk's weights meet the collarbone's and the arm's: a mask, softened over a few rings
  seamMask() {
    const { N, body } = this, sk = body.skeleton, J = body.skin.joints, W = body.skin.weights;
    const trunk = new Set(['Spine1', 'Spine2', 'Chest', 'Neck1'].map(n => sk.index[n]));
    const arm = new Set(['LeftShoulder', 'RightShoulder', 'LeftArm', 'RightArm'].map(n => sk.index[n]));
    let m = new Float64Array(N);
    for (let i = 0; i < N; i++) {
      let a = 0, b = 0;
      for (let k = 0; k < 4; k++) { const j = J[i * 4 + k], w = W[i * 4 + k]; if (trunk.has(j)) a += w; if (arm.has(j)) b += w; }
      m[i] = Math.min(1, 4 * a * b * 1.5);
    }
    const rings = this.seam.rings ?? 3;
    for (let r = 0; r < rings; r++) {   // grow, then soften
      const g = Float64Array.from(m);
      for (let i = 0; i < N; i++) for (let o = this.nbStart[i]; o < this.nbStart[i + 1]; o++) g[i] = Math.max(g[i], 0.8 * m[this.nb[o]]);
      m = g;
    }
    this.mask = m;
    this.active = Int32Array.from({ length: N }, (_, i) => i).filter(i => m[i] > 0.01);
  }

  // each joint's transform now: x ↦ R x + T (R from the pose's turn; T so the joint's rest place goes to its place now)
  transforms(pose) {
    const r = this.body.joints;
    for (let j = 0; j < this.J; j++) {
      const q = getQ(pose.Q, j), [x, y, z, w] = q, R = this.R, o = j * 9;
      R[o] = 1 - 2 * (y * y + z * z); R[o + 1] = 2 * (x * y - z * w); R[o + 2] = 2 * (x * z + y * w);
      R[o + 3] = 2 * (x * y + z * w); R[o + 4] = 1 - 2 * (x * x + z * z); R[o + 5] = 2 * (y * z - x * w);
      R[o + 6] = 2 * (x * z - y * w); R[o + 7] = 2 * (y * z + x * w); R[o + 8] = 1 - 2 * (x * x + y * y);
      const rx = r[j * 3], ry = r[j * 3 + 1], rz = r[j * 3 + 2];
      this.T[j * 3] = pose.P[j * 3] - (R[o] * rx + R[o + 1] * ry + R[o + 2] * rz);
      this.T[j * 3 + 1] = pose.P[j * 3 + 1] - (R[o + 3] * rx + R[o + 4] * ry + R[o + 5] * rz);
      this.T[j * 3 + 2] = pose.P[j * 3 + 2] - (R[o + 6] * rx + R[o + 7] * ry + R[o + 8] * rz);
    }
  }
  // joint j's transform (3×4, rows) — for something rigid on it
  matrix(pose, j) {
    this.transforms(pose); const R = this.R, T = this.T, o = j * 9;
    return [R[o], R[o + 1], R[o + 2], T[j * 3], R[o + 3], R[o + 4], R[o + 5], T[j * 3 + 1], R[o + 6], R[o + 7], R[o + 8], T[j * 3 + 2]];
  }

  // the body's vertices in the pose, into out (Float32Array N×3)
  skin(pose, out) {
    this.transforms(pose);
    const { N, R, T, body } = this, P = body.positions, J = body.skin.joints, W = body.skin.weights;
    const lbs = (i, x, y, z) => {
      let X = 0, Y = 0, Z = 0;
      for (let k = 0; k < 4; k++) {
        const w = W[i * 4 + k]; if (!w) continue; const j = J[i * 4 + k], o = j * 9;
        X += w * (R[o] * x + R[o + 1] * y + R[o + 2] * z + T[j * 3]);
        Y += w * (R[o + 3] * x + R[o + 4] * y + R[o + 5] * z + T[j * 3 + 1]);
        Z += w * (R[o + 6] * x + R[o + 7] * y + R[o + 8] * z + T[j * 3 + 2]);
      }
      return [X, Y, Z];
    };
    // the joints' turns blended as quaternions (signs to the first's hemisphere)
    const blend = i => {
      let qx = 0, qy = 0, qz = 0, qw = 0, j0 = J[i * 4];
      const r0 = [pose.Q[j0 * 4], pose.Q[j0 * 4 + 1], pose.Q[j0 * 4 + 2], pose.Q[j0 * 4 + 3]];
      for (let k = 0; k < 4; k++) {
        const w = W[i * 4 + k]; if (!w) continue; const o = J[i * 4 + k] * 4;
        const s = (pose.Q[o] * r0[0] + pose.Q[o + 1] * r0[1] + pose.Q[o + 2] * r0[2] + pose.Q[o + 3] * r0[3]) < 0 ? -w : w;
        qx += s * pose.Q[o]; qy += s * pose.Q[o + 1]; qz += s * pose.Q[o + 2]; qw += s * pose.Q[o + 3];
      }
      const l = Math.hypot(qx, qy, qz, qw) || 1;
      return [qx / l, qy / l, qz / l, qw / l];
    };
    if (this.method === 'lbs') {
      for (let i = 0; i < N; i++) { const v = lbs(i, P[i * 3], P[i * 3 + 1], P[i * 3 + 2]); out[i * 3] = v[0]; out[i * 3 + 1] = v[1]; out[i * 3 + 2] = v[2]; }
    } else if (this.method === 'cor') {
      const C = this.cor, has = this.hasCor;
      for (let i = 0; i < N; i++) {
        const x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
        if (!has[i]) { const v = lbs(i, x, y, z); out[i * 3] = v[0]; out[i * 3 + 1] = v[1]; out[i * 3 + 2] = v[2]; continue; }
        const c = [C[i * 3], C[i * 3 + 1], C[i * 3 + 2]], t = lbs(i, c[0], c[1], c[2]), q = blend(i);
        const v = qRot(q, [x - c[0], y - c[1], z - c[2]]);
        out[i * 3] = v[0] + t[0]; out[i * 3 + 1] = v[1] + t[1]; out[i * 3 + 2] = v[2] + t[2];
      }
    } else {
      // dual quaternions: each joint's (q, ½ t q), blended, normalised
      const D = this.dual ??= new Float64Array(this.J * 4);
      for (let j = 0; j < this.J; j++) {
        const q = getQ(pose.Q, j), t = [T[j * 3], T[j * 3 + 1], T[j * 3 + 2], 0], d = qMul(t, q);
        D[j * 4] = d[0] / 2; D[j * 4 + 1] = d[1] / 2; D[j * 4 + 2] = d[2] / 2; D[j * 4 + 3] = d[3] / 2;
      }
      for (let i = 0; i < N; i++) {
        let r = [0, 0, 0, 0], d = [0, 0, 0, 0]; const j0 = J[i * 4];
        for (let k = 0; k < 4; k++) {
          const w = W[i * 4 + k]; if (!w) continue; const j = J[i * 4 + k], o = j * 4;
          const s = (pose.Q[o] * pose.Q[j0 * 4] + pose.Q[o + 1] * pose.Q[j0 * 4 + 1] + pose.Q[o + 2] * pose.Q[j0 * 4 + 2] + pose.Q[o + 3] * pose.Q[j0 * 4 + 3]) < 0 ? -w : w;
          for (let c = 0; c < 4; c++) { r[c] += s * pose.Q[o + c]; d[c] += s * D[o + c]; }
        }
        const l = Math.hypot(...r) || 1; r = r.map(v => v / l); d = d.map(v => v / l);
        const t = qMul(d, qConj(r)), v = qRot(r, [P[i * 3], P[i * 3 + 1], P[i * 3 + 2]]);
        out[i * 3] = v[0] + 2 * t[0]; out[i * 3 + 1] = v[1] + 2 * t[1]; out[i * 3 + 2] = v[2] + 2 * t[2];
      }
    }
    if (this.seam) this.smoothSeam(out);
    return out;
  }

  // the skin's movement against the chest's own, smoothed over the surface in the seam's mask
  smoothSeam(out) {
    const c = this.body.skeleton.index.Chest, R = this.R, T = this.T, o = c * 9, P = this.body.positions, m = this.mask;
    const d = this.disp ??= new Float64Array(this.N * 3), e = this.disp2 ??= new Float64Array(this.N * 3), act = this.active;
    const rigid = (i, k) => R[o + k * 3] * P[i * 3] + R[o + k * 3 + 1] * P[i * 3 + 1] + R[o + k * 3 + 2] * P[i * 3 + 2] + T[c * 3 + k];
    // the movement of the seam and of the ring around it (its fixed edge)
    const near = this.near ??= (() => { const s = new Set(act); for (const i of act) for (let q = this.nbStart[i]; q < this.nbStart[i + 1]; q++) s.add(this.nb[q]); return Int32Array.from(s); })();
    for (const i of near) for (let k = 0; k < 3; k++) d[i * 3 + k] = out[i * 3 + k] - rigid(i, k);
    for (let it = 0; it < (this.seam.iterations ?? 10); it++) {
      for (const i of act) {
        const a = this.nbStart[i], b = this.nbStart[i + 1]; if (a === b) continue;
        let x = 0, y = 0, z = 0; for (let q = a; q < b; q++) { const n = this.nb[q]; x += d[n * 3]; y += d[n * 3 + 1]; z += d[n * 3 + 2]; }
        const kk = 0.5 / (b - a), w = m[i];
        e[i * 3] = d[i * 3] + w * (d[i * 3] * -0.5 + x * kk); e[i * 3 + 1] = d[i * 3 + 1] + w * (d[i * 3 + 1] * -0.5 + y * kk); e[i * 3 + 2] = d[i * 3 + 2] + w * (d[i * 3 + 2] * -0.5 + z * kk);
      }
      for (const i of act) { d[i * 3] = e[i * 3]; d[i * 3 + 1] = e[i * 3 + 1]; d[i * 3 + 2] = e[i * 3 + 2]; }
    }
    for (const i of act) for (let k = 0; k < 3; k++) out[i * 3 + k] = rigid(i, k) + d[i * 3 + k];
  }
}

// vertex normals of a mesh (area-weighted), into out
export function normalsOf(pos, tris, out) {
  out.fill(0);
  for (let t = 0; t < tris.length; t += 3) {
    const a = tris[t] * 3, b = tris[t + 1] * 3, c = tris[t + 2] * 3;
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2];
    const vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    for (const i of [a, b, c]) { out[i] += nx; out[i + 1] += ny; out[i + 2] += nz; }
  }
  for (let i = 0; i < out.length; i += 3) { const l = Math.hypot(out[i], out[i + 1], out[i + 2]) || 1; out[i] /= l; out[i + 1] /= l; out[i + 2] /= l; }
  return out;
}

// Т7's first fix: the collarbone takes `share` of the arm's drop below its rest (Т7: a third — as the shoulder girdle
// does), turning down about the horizontal line across the arm; the arm keeps its turn in the world. A raised arm is
// left to Kimodo's own collarbone.
export function clavicleShare(pose, body, share) {
  const sk = body.skeleton, r = body.joints;
  for (const s of ['Left', 'Right']) {
    const c = sk.index[s + 'Shoulder'], a = sk.index[s + 'Arm'], f = sk.index[s + 'ForeArm'];
    const L = qMul(qConj(getQ(pose.Q, c)), getQ(pose.Q, a));          // the arm against its collarbone
    const d = normalize(sub(getV(r, f), getV(r, a))), e = qRot(L, d);  // its direction at rest and now (the collarbone's rest axes)
    const drop = Math.asin(Math.max(-1, Math.min(1, d[1]))) - Math.asin(Math.max(-1, Math.min(1, e[1])));
    const h = [e[0], 0, e[2]];
    if (drop <= 0 || Math.hypot(h[0], h[2]) < 1e-6) continue;
    setQ(pose.Q, c, qMul(getQ(pose.Q, c), qAxisAngle(cross([0, 1, 0], h), share * drop)));
  }
}
