// One skinning for every skinned mesh a rig moves (src/mesh.js): the body, a wrapped head, clothes on the body.
//
// Methods (options.method):
//   'cor' — skinning with optimized centres of rotation (Le & Hodgins, SIGGRAPH 2016; the default). Each vertex turns
//           by its joints' turns blended as quaternions — so a forearm's twist doesn't collapse into a candy wrapper as
//           in linear blending — about a centre of rotation found once from the rest mesh (where vertices of like
//           weights lie; `sigma` how alike), placed by linear blending — so a bent elbow or knee doesn't bulge as in
//           dual quaternions. Weights stay the artists' (Anny's); nothing is learned. Centres come from the rest the
//           mesh was made with (morphs weighted in each frame move vertices, not their centres).
//   'dqs' — dual quaternions (Kavan et al. 2007): keeps volume at twists, bulges a little at bends.
//   'lbs' — linear blending: the plain way; loses volume at twists and deep bends. For comparison.
// seam {iterations, rings} — Т7's second fix: where the trunk's weights hand the skin over to the collarbone's and the
// arm's, the skin's movement (against the chest's) is smoothed over the surface, so no dent is left where they meet.
// Only the vertices the triangles use are skinned (mesh.used).
// Rigid things on a joint: `matrix(pose, j)` — joint j's transform from the rig's rest to now (3×4, rows), times
// their own matrix at rest, so their own transform is kept.
//
// What depends only on the rest (neighbours, centres, the seam's mask) is computed once per mesh and kept, so
// making another Skinner of the same mesh (another figure, a toggle in the viewer) costs nothing. The loops over
// vertices allocate nothing.
const NEIGHBOURS = new WeakMap(), CENTRES = new WeakMap(), MASKS = new WeakMap();
const cached = (map, key, sub, make) => { let m = map.get(key); if (!m) map.set(key, m = new Map()); if (!m.has(sub)) m.set(sub, make()); return m.get(sub); };

export class Skinner {
  constructor(mesh, rig, { method = 'cor', sigma = 0.1, seam = null } = {}) {
    if (mesh.kind !== 'skinned') throw new Error(`${mesh.id}: a ${mesh.kind} mesh is not skinned`);
    if (!['cor', 'dqs', 'lbs'].includes(method)) throw new Error(`no skinning method "${method}"`);
    Object.assign(this, { mesh, rig, method, sigma, seam, N: mesh.N, J: rig.J, K: mesh.skin.K });
    this.idx = mesh.used;
    this.R = new Float64Array(this.J * 9); this.T = new Float64Array(this.J * 3); this.D = new Float64Array(this.J * 4);
    const nb = cached(NEIGHBOURS, mesh.triangles, mesh.N, () => neighbours(mesh));
    this.nbStart = nb.start; this.nb = nb.list;
    if (method === 'cor') { const c = cached(CENTRES, mesh.positions, `${sigma}|${this.K}`, () => centres(mesh, sigma)); this.cor = c.cor; this.hasCor = c.has; }
    if (seam) {
      const m = cached(MASKS, mesh.positions, seam.rings, () => seamMask(mesh, rig, nb, seam.rings));
      this.mask = m.mask; this.active = m.active; this.near = m.near;
      this.disp = new Float64Array(this.N * 3); this.disp2 = new Float64Array(this.N * 3);
    }
  }

  // each joint's transform now: x ↦ R x + T (R from the pose's turn; T so the joint's rest place goes to its place now)
  transforms(pose) {
    const r = this.rig.joints, R = this.R, T = this.T;
    for (let j = 0; j < this.J; j++) {
      const x = pose.Q[j * 4], y = pose.Q[j * 4 + 1], z = pose.Q[j * 4 + 2], w = pose.Q[j * 4 + 3], o = j * 9;
      R[o] = 1 - 2 * (y * y + z * z); R[o + 1] = 2 * (x * y - z * w); R[o + 2] = 2 * (x * z + y * w);
      R[o + 3] = 2 * (x * y + z * w); R[o + 4] = 1 - 2 * (x * x + z * z); R[o + 5] = 2 * (y * z - x * w);
      R[o + 6] = 2 * (x * z - y * w); R[o + 7] = 2 * (y * z + x * w); R[o + 8] = 1 - 2 * (x * x + y * y);
      const rx = r[j * 3], ry = r[j * 3 + 1], rz = r[j * 3 + 2];
      T[j * 3] = pose.P[j * 3] - (R[o] * rx + R[o + 1] * ry + R[o + 2] * rz);
      T[j * 3 + 1] = pose.P[j * 3 + 1] - (R[o + 3] * rx + R[o + 4] * ry + R[o + 5] * rz);
      T[j * 3 + 2] = pose.P[j * 3 + 2] - (R[o + 6] * rx + R[o + 7] * ry + R[o + 8] * rz);
    }
  }
  // joint j's transform (3×4, rows) — for something rigid on it
  matrix(pose, j) {
    this.transforms(pose); const R = this.R, T = this.T, o = j * 9;
    return [R[o], R[o + 1], R[o + 2], T[j * 3], R[o + 3], R[o + 4], R[o + 5], T[j * 3 + 1], R[o + 6], R[o + 7], R[o + 8], T[j * 3 + 2]];
  }

  // the mesh's vertices in the pose, into out (Float32Array N×3); rest: the rest to skin (the mesh's, or morphed)
  skin(pose, out, rest = this.mesh.positions) {
    this.transforms(pose);
    const { R, T, K, idx } = this, P = rest, JS = this.mesh.skin.joints, WS = this.mesh.skin.weights, Q = pose.Q;
    if (this.method === 'lbs') {
      for (let n = 0; n < idx.length; n++) {
        const i = idx[n], x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
        let X = 0, Y = 0, Z = 0;
        for (let k = 0; k < K; k++) {
          const w = WS[i * K + k]; if (!w) continue; const j = JS[i * K + k], o = j * 9;
          X += w * (R[o] * x + R[o + 1] * y + R[o + 2] * z + T[j * 3]);
          Y += w * (R[o + 3] * x + R[o + 4] * y + R[o + 5] * z + T[j * 3 + 1]);
          Z += w * (R[o + 6] * x + R[o + 7] * y + R[o + 8] * z + T[j * 3 + 2]);
        }
        out[i * 3] = X; out[i * 3 + 1] = Y; out[i * 3 + 2] = Z;
      }
    } else if (this.method === 'cor') {
      const C = this.cor, has = this.hasCor;
      for (let n = 0; n < idx.length; n++) {
        const i = idx[n], x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
        // a vertex of one joint: its turn about any centre is the same — linear blending of the vertex itself
        const cx = has[i] ? C[i * 3] : x, cy = has[i] ? C[i * 3 + 1] : y, cz = has[i] ? C[i * 3 + 2] : z;
        let X = 0, Y = 0, Z = 0, qx = 0, qy = 0, qz = 0, qw = 0;
        const j0 = JS[i * K] * 4, ax = Q[j0], ay = Q[j0 + 1], az = Q[j0 + 2], aw = Q[j0 + 3];
        for (let k = 0; k < K; k++) {
          const w = WS[i * K + k]; if (!w) continue; const j = JS[i * K + k], o = j * 9, q = j * 4;
          X += w * (R[o] * cx + R[o + 1] * cy + R[o + 2] * cz + T[j * 3]);
          Y += w * (R[o + 3] * cx + R[o + 4] * cy + R[o + 5] * cz + T[j * 3 + 1]);
          Z += w * (R[o + 6] * cx + R[o + 7] * cy + R[o + 8] * cz + T[j * 3 + 2]);
          const s = Q[q] * ax + Q[q + 1] * ay + Q[q + 2] * az + Q[q + 3] * aw < 0 ? -w : w;
          qx += s * Q[q]; qy += s * Q[q + 1]; qz += s * Q[q + 2]; qw += s * Q[q + 3];
        }
        if (!has[i]) { out[i * 3] = X; out[i * 3 + 1] = Y; out[i * 3 + 2] = Z; continue; }
        const l = Math.hypot(qx, qy, qz, qw) || 1; qx /= l; qy /= l; qz /= l; qw /= l;
        const vx = x - cx, vy = y - cy, vz = z - cz;
        const tx = 2 * (qy * vz - qz * vy), ty = 2 * (qz * vx - qx * vz), tz = 2 * (qx * vy - qy * vx);
        out[i * 3] = vx + qw * tx + qy * tz - qz * ty + X;
        out[i * 3 + 1] = vy + qw * ty + qz * tx - qx * tz + Y;
        out[i * 3 + 2] = vz + qw * tz + qx * ty - qy * tx + Z;
      }
    } else {
      // dual quaternions: each joint's (q, ½ t q), blended, normalised
      const D = this.D;
      for (let j = 0; j < this.J; j++) {
        const bx = Q[j * 4], by = Q[j * 4 + 1], bz = Q[j * 4 + 2], bw = Q[j * 4 + 3], ax = T[j * 3], ay = T[j * 3 + 1], az = T[j * 3 + 2];
        D[j * 4] = (ax * bw + ay * bz - az * by) / 2; D[j * 4 + 1] = (-ax * bz + ay * bw + az * bx) / 2;
        D[j * 4 + 2] = (ax * by - ay * bx + az * bw) / 2; D[j * 4 + 3] = (-ax * bx - ay * by - az * bz) / 2;
      }
      for (let n = 0; n < idx.length; n++) {
        const i = idx[n];
        let r0 = 0, r1 = 0, r2 = 0, r3 = 0, d0 = 0, d1 = 0, d2 = 0, d3 = 0;
        const j0 = JS[i * K] * 4;
        for (let k = 0; k < K; k++) {
          const w = WS[i * K + k]; if (!w) continue; const o = JS[i * K + k] * 4;
          const s = Q[o] * Q[j0] + Q[o + 1] * Q[j0 + 1] + Q[o + 2] * Q[j0 + 2] + Q[o + 3] * Q[j0 + 3] < 0 ? -w : w;
          r0 += s * Q[o]; r1 += s * Q[o + 1]; r2 += s * Q[o + 2]; r3 += s * Q[o + 3];
          d0 += s * D[o]; d1 += s * D[o + 1]; d2 += s * D[o + 2]; d3 += s * D[o + 3];
        }
        const l = Math.hypot(r0, r1, r2, r3) || 1;
        r0 /= l; r1 /= l; r2 /= l; r3 /= l; d0 /= l; d1 /= l; d2 /= l; d3 /= l;
        // t = 2 d r* (its vector part); v = r x r*
        const tx = 2 * (-d3 * r0 + d0 * r3 - d1 * r2 + d2 * r1), ty = 2 * (-d3 * r1 + d1 * r3 - d2 * r0 + d0 * r2), tz = 2 * (-d3 * r2 + d2 * r3 - d0 * r1 + d1 * r0);
        const x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
        const ux = 2 * (r1 * z - r2 * y), uy = 2 * (r2 * x - r0 * z), uz = 2 * (r0 * y - r1 * x);
        out[i * 3] = x + r3 * ux + r1 * uz - r2 * uy + tx;
        out[i * 3 + 1] = y + r3 * uy + r2 * ux - r0 * uz + ty;
        out[i * 3 + 2] = z + r3 * uz + r0 * uy - r1 * ux + tz;
      }
    }
    if (this.seam) this.smoothSeam(out, rest);
    return out;
  }

  // the skin's movement against the chest's own, smoothed over the surface in the seam's mask
  smoothSeam(out, P) {
    const c = this.rig.skeleton.index.Chest, R = this.R, T = this.T, o = c * 9, m = this.mask, d = this.disp, e = this.disp2;
    const act = this.active, near = this.near, nbS = this.nbStart, nb = this.nb;
    for (let n = 0; n < near.length; n++) {
      const i = near[n], x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
      for (let k = 0; k < 3; k++) d[i * 3 + k] = out[i * 3 + k] - (R[o + k * 3] * x + R[o + k * 3 + 1] * y + R[o + k * 3 + 2] * z + T[c * 3 + k]);
    }
    for (let it = 0; it < this.seam.iterations; it++) {
      for (let n = 0; n < act.length; n++) {
        const i = act[n], a = nbS[i], b = nbS[i + 1]; if (a === b) continue;
        let x = 0, y = 0, z = 0; for (let q = a; q < b; q++) { const k = nb[q]; x += d[k * 3]; y += d[k * 3 + 1]; z += d[k * 3 + 2]; }
        const kk = 0.5 / (b - a), w = m[i];
        e[i * 3] = d[i * 3] + w * (d[i * 3] * -0.5 + x * kk); e[i * 3 + 1] = d[i * 3 + 1] + w * (d[i * 3 + 1] * -0.5 + y * kk); e[i * 3 + 2] = d[i * 3 + 2] + w * (d[i * 3 + 2] * -0.5 + z * kk);
      }
      for (let n = 0; n < act.length; n++) { const i = act[n]; d[i * 3] = e[i * 3]; d[i * 3 + 1] = e[i * 3 + 1]; d[i * 3 + 2] = e[i * 3 + 2]; }
    }
    for (let n = 0; n < act.length; n++) {
      const i = act[n], x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
      for (let k = 0; k < 3; k++) out[i * 3 + k] = R[o + k * 3] * x + R[o + k * 3 + 1] * y + R[o + k * 3 + 2] * z + T[c * 3 + k] + d[i * 3 + k];
    }
  }
}

// each vertex's neighbours over the mesh (CSR)
function neighbours(mesh) {
  const N = mesh.N, tris = mesh.triangles, sets = Array.from({ length: N }, () => new Set());
  for (let t = 0; t < tris.length; t += 3) { const a = tris[t], b = tris[t + 1], c = tris[t + 2]; sets[a].add(b).add(c); sets[b].add(a).add(c); sets[c].add(a).add(b); }
  const start = new Int32Array(N + 1); let n = 0;
  for (let i = 0; i < N; i++) { start[i] = n; n += sets[i].size; }
  start[N] = n; const list = new Int32Array(n); n = 0;
  for (let i = 0; i < N; i++) for (const k of sets[i]) list[n++] = k;
  return { start, list };
}

// the centres of rotation (Le & Hodgins 2016, eq. 3–4): for vertex i, the area-weighted mean of the triangles'
// centroids, each by how alike its weights are to i's — s(wᵢ, w_t) = Σ_{j<k} wᵢⱼ wᵢₖ w_tⱼ w_tₖ exp(−((wᵢⱼ w_tₖ − wᵢₖ w_tⱼ)/σ)²)
function centres(mesh, sigma) {
  const N = mesh.N, P = mesh.positions, tris = mesh.triangles, K = mesh.skin.K, J = mesh.skin.joints, W = mesh.skin.weights;
  const T = tris.length / 3, pairs = new Map(), key = (a, b) => a * 65536 + b;
  for (let t = 0; t < T; t++) {
    const a = tris[t * 3], b = tris[t * 3 + 1], c = tris[t * 3 + 2];
    const w = new Map();
    for (const v of [a, b, c]) for (let k = 0; k < K; k++) { const wt = W[v * K + k]; if (wt > 0) w.set(J[v * K + k], (w.get(J[v * K + k]) || 0) + wt / 3); }
    const e1x = P[b * 3] - P[a * 3], e1y = P[b * 3 + 1] - P[a * 3 + 1], e1z = P[b * 3 + 2] - P[a * 3 + 2];
    const e2x = P[c * 3] - P[a * 3], e2y = P[c * 3 + 1] - P[a * 3 + 1], e2z = P[c * 3 + 2] - P[a * 3 + 2];
    const area = 0.5 * Math.hypot(e1y * e2z - e1z * e2y, e1z * e2x - e1x * e2z, e1x * e2y - e1y * e2x);
    const cx = (P[a * 3] + P[b * 3] + P[c * 3]) / 3, cy = (P[a * 3 + 1] + P[b * 3 + 1] + P[c * 3 + 1]) / 3, cz = (P[a * 3 + 2] + P[b * 3 + 2] + P[c * 3 + 2]) / 3;
    const js = [...w.keys()].sort((x, y) => x - y);
    for (let x = 0; x < js.length; x++) for (let y = x + 1; y < js.length; y++) {
      const kk = key(js[x], js[y]); let L = pairs.get(kk); if (!L) pairs.set(kk, L = []);
      L.push(w.get(js[x]), w.get(js[y]), area, cx, cy, cz);
    }
  }
  const cor = new Float64Array(N * 3), has = new Uint8Array(N), s2 = sigma * sigma;
  for (let i = 0; i < N; i++) {
    const js = [], ws = [];
    for (let k = 0; k < K; k++) if (W[i * K + k] > 0) { js.push(J[i * K + k]); ws.push(W[i * K + k]); }
    if (js.length < 2) continue;
    let nx = 0, ny = 0, nz = 0, d = 0;
    for (let x = 0; x < js.length; x++) for (let y = x + 1; y < js.length; y++) {
      let ja = js[x], jb = js[y], wa = ws[x], wb = ws[y];
      if (ja > jb) { [ja, jb] = [jb, ja]; [wa, wb] = [wb, wa]; }
      const L = pairs.get(key(ja, jb)); if (!L) continue;
      for (let o = 0; o < L.length; o += 6) {
        const ta = L[o], tb = L[o + 1], e = wa * tb - wb * ta, s = wa * wb * ta * tb * Math.exp(-e * e / s2) * L[o + 2];
        nx += s * L[o + 3]; ny += s * L[o + 4]; nz += s * L[o + 5]; d += s;
      }
    }
    if (d > 1e-14) { cor[i * 3] = nx / d; cor[i * 3 + 1] = ny / d; cor[i * 3 + 2] = nz / d; has[i] = 1; }
  }
  return { cor, has };
}

// where the trunk's weights meet the collarbone's and the arm's: a mask, softened over a few rings
function seamMask(mesh, rig, nb, rings) {
  const N = mesh.N, sk = rig.skeleton, K = mesh.skin.K, J = mesh.skin.joints, W = mesh.skin.weights;
  const trunk = new Set(['Spine1', 'Spine2', 'Chest', 'Neck1'].map(n => sk.index[n]));
  const arm = new Set(['LeftShoulder', 'RightShoulder', 'LeftArm', 'RightArm'].map(n => sk.index[n]));
  let m = new Float64Array(N);
  for (let i = 0; i < N; i++) {
    let a = 0, b = 0;
    for (let k = 0; k < K; k++) { const j = J[i * K + k], w = W[i * K + k]; if (trunk.has(j)) a += w; if (arm.has(j)) b += w; }
    m[i] = Math.min(1, 4 * a * b * 1.5);
  }
  for (let r = 0; r < rings; r++) {   // grow, then soften
    const g = Float64Array.from(m);
    for (let i = 0; i < N; i++) for (let o = nb.start[i]; o < nb.start[i + 1]; o++) g[i] = Math.max(g[i], 0.8 * m[nb.list[o]]);
    m = g;
  }
  const active = Int32Array.from({ length: N }, (_, i) => i).filter(i => m[i] > 0.01 && mesh.isUsed[i]);
  const s = new Set(active); for (const i of active) for (let q = nb.start[i]; q < nb.start[i + 1]; q++) s.add(nb.list[q]);
  return { mask: m, active, near: Int32Array.from(s) };
}
