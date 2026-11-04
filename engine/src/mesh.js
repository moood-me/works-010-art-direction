// Meshes a rig moves. Every kind gives, each frame, its vertices in the pose (and the engine their normals); the
// floor step (src/figure.js) then looks at every mesh that counts for the floor, over the vertices its triangles use.
//   skinned     {kind: 'skinned', id, positions (rest, N×3), triangles, skin: {joints, weights, K}, morphs?, floor?}
//               skinned by src/skin.js; K influences a vertex (4 for Anny's mesh; any number)
//   rigid       {kind: 'rigid', id, joint, positions (rest, in the body's rest space), triangles, floor?}
//               carried whole by one joint (an eye, a hat, a piece of a head): its own transform kept
//   procedural  {kind: 'procedural', id, N, triangles, build(pose, rig, out), floor?}
//               rebuilt from the pose each frame (sweeps along curves through the joints, bending in arcs)
//   attached    {kind: 'attached', id, host (another mesh's name), tri (each vertex's triangle of the host), bary (its
//               place in it, N×3), lift (how far out along the host's normal there, metres), triangles, floor?}
//               laid on another mesh each frame, after it (a feature as volume on the skin: it follows the skin in
//               motion, in its morphs and in every change of its rest)
// A skinned mesh may follow another's rest (`follow`: {host (its name), K, idx (N×K of the host's vertices), w (their
// weights)}, made by followOf): whatever moves the host's rest in a frame — its morphs, a change of the rest as a pose
// layer — moves each of its vertices as it moves the host's vertices it is bound to (a head's piece on its skin).
// triangles: Uint32Array (or Uint16Array while N ≤ 65,536). `used`: the vertices the triangles use — only they are
// skinned, drawn and counted for the floor. morphs: {name: {indices: Uint32Array, deltas: Float32Array (n×3)}} —
// rest changes applied before skinning, each with a weight (src/figure.js: a rest change or a pose layer).
export function makeMesh(o) {
  const kind = o.kind || 'skinned';
  if (!['skinned', 'rigid', 'procedural', 'attached'].includes(kind)) throw new Error(`no mesh kind "${kind}"`);
  const N = kind === 'procedural' ? o.N : kind === 'attached' ? o.tri.length : o.positions.length / 3;
  const triangles = o.triangles instanceof Uint32Array || o.triangles instanceof Uint16Array ? o.triangles : indexArray(o.triangles, N);
  for (let i = 0; i < triangles.length; i++) if (triangles[i] >= N) throw new Error(`${o.id}: a triangle uses vertex ${triangles[i]} of ${N}`);
  const mark = new Uint8Array(N); for (let i = 0; i < triangles.length; i++) mark[triangles[i]] = 1;
  let n = 0; for (let i = 0; i < N; i++) n += mark[i];
  const used = new Uint32Array(n); n = 0; for (let i = 0; i < N; i++) if (mark[i]) used[n++] = i;
  const m = { ...o, kind, N, triangles, used, isUsed: mark, floor: o.floor ?? true, morphs: o.morphs || {} };
  if (kind === 'skinned') {
    const K = o.skin.K ?? 4;
    if (o.skin.joints.length !== N * K || o.skin.weights.length !== N * K) throw new Error(`${o.id}: skin of ${K} influences doesn't match ${N} vertices`);
    m.skin = { ...o.skin, K };
  }
  if (kind === 'rigid' && !Number.isInteger(o.joint)) throw new Error(`${o.id}: a rigid mesh names its joint`);
  if (kind === 'attached' && (typeof o.host !== 'string' || o.bary.length !== N * 3 || o.lift.length !== N)) throw new Error(`${o.id}: an attached mesh names its host and gives each vertex a triangle, a place and a lift`);
  for (const [name, mo] of Object.entries(m.morphs)) if (mo.deltas.length !== mo.indices.length * 3) throw new Error(`${o.id}: morph ${name} has ${mo.indices.length} vertices and ${mo.deltas.length / 3} deltas`);
  return m;
}

// an index array of the smallest type that holds N vertices
export function indexArray(list, N) { return N > 65536 ? Uint32Array.from(list) : Uint16Array.from(list); }

// the mesh's rest with morphs weighted in: {name: weight} → Float32Array N×3 (out, or a new one)
export function morphed(mesh, weights, out = new Float32Array(mesh.positions.length)) {
  out.set(mesh.positions);
  for (const [name, w] of Object.entries(weights)) {
    if (!w) continue;
    const mo = mesh.morphs[name]; if (!mo) throw new Error(`${mesh.id}: no morph "${name}" (it has ${Object.keys(mesh.morphs).join(', ') || 'none'})`);
    const I = mo.indices, D = mo.deltas;
    for (let k = 0; k < I.length; k++) { const i = I[k] * 3; out[i] += w * D[k * 3]; out[i + 1] += w * D[k * 3 + 1]; out[i + 2] += w * D[k * 3 + 2]; }
  }
  return out;
}

// vertices no triangle uses are never skinned, drawn or changed: they keep the mesh's rest (in P, in place)
export function keepUnused(mesh, P) {
  for (let i = 0; i < mesh.N; i++) if (!mesh.isUsed[i]) for (let c = 0; c < 3; c++) P[i * 3 + c] = mesh.positions[i * 3 + c];
  return P;
}

// a mesh's vertices (P, N×3) bound to a host mesh's rest (hostP; `name`: what the figure calls the host), each to its K
// nearest host vertices among `only` (a mask; all the used ones if null), weighed by inverse squared distance — see
// `follow` above
export function followOf(name, host, hostP, P, only = null, K = 8) {
  const cell = 0.04, grid = new Map(), key = (a, b, c) => `${a},${b},${c}`, n = P.length / 3;
  for (const i of host.used) { if (only && !only[i]) continue; const k = key(Math.floor(hostP[i * 3] / cell), Math.floor(hostP[i * 3 + 1] / cell), Math.floor(hostP[i * 3 + 2] / cell)); let g = grid.get(k); if (!g) grid.set(k, g = []); g.push(i); }
  if (!grid.size) throw new Error(`${host.id}: nothing to bind to`);
  const idx = new Uint32Array(n * K), w = new Float32Array(n * K), bi = new Int32Array(K), bd = new Float64Array(K);
  for (let v = 0; v < n; v++) {
    const x = P[v * 3], y = P[v * 3 + 1], z = P[v * 3 + 2], cx = Math.floor(x / cell), cy = Math.floor(y / cell), cz = Math.floor(z / cell);
    bd.fill(Infinity); bi.fill(-1);
    for (let r = 0; ; r++) {
      for (let a = -r; a <= r; a++) for (let b = -r; b <= r; b++) for (let c = -r; c <= r; c++) {
        if (Math.max(Math.abs(a), Math.abs(b), Math.abs(c)) !== r) continue;
        const g = grid.get(key(cx + a, cy + b, cz + c)); if (!g) continue;
        for (const i of g) {
          const d = (hostP[i * 3] - x) ** 2 + (hostP[i * 3 + 1] - y) ** 2 + (hostP[i * 3 + 2] - z) ** 2; if (d >= bd[K - 1]) continue;
          let k = K - 1; while (k > 0 && bd[k - 1] > d) { bd[k] = bd[k - 1]; bi[k] = bi[k - 1]; k--; } bd[k] = d; bi[k] = i;
        }
      }
      if (bi[K - 1] >= 0 && Math.sqrt(bd[K - 1]) <= r * cell) break;   // nothing nearer can lie beyond this ring
      if (r > 1000) throw new Error(`${host.id}: fewer than ${K} vertices to bind to`);
    }
    let s = 0; for (let k = 0; k < K; k++) { const q = 1 / (bd[k] + 1e-8); w[v * K + k] = q; s += q; idx[v * K + k] = bi[k]; }
    for (let k = 0; k < K; k++) w[v * K + k] /= s;
  }
  return { host: name, K, idx, w };
}

// vertex normals (area-weighted) over the used vertices, into out (a new array if none is given)
export function normalsOf(pos, tris, out = new Float32Array(pos.length), used = null) {
  out.fill(0);
  for (let t = 0; t < tris.length; t += 3) {
    const a = tris[t] * 3, b = tris[t + 1] * 3, c = tris[t + 2] * 3;
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2];
    const vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    out[a] += nx; out[a + 1] += ny; out[a + 2] += nz; out[b] += nx; out[b + 1] += ny; out[b + 2] += nz; out[c] += nx; out[c + 1] += ny; out[c + 2] += nz;
  }
  const norm = i => { const l = Math.hypot(out[i], out[i + 1], out[i + 2]) || 1; out[i] /= l; out[i + 1] /= l; out[i + 2] /= l; };
  if (used) for (let k = 0; k < used.length; k++) norm(used[k] * 3); else for (let i = 0; i < out.length; i += 3) norm(i);
  return out;
}

// each vertex's neighbours over the mesh's triangles (CSR: start N+1, list) — kept per triangle list, so every
// figure, skinner and deformer of the same topology shares one
const NEIGHBOURS = new WeakMap();
export function neighboursOf(mesh) {
  let byN = NEIGHBOURS.get(mesh.triangles); if (!byN) NEIGHBOURS.set(mesh.triangles, byN = new Map());
  if (byN.has(mesh.N)) return byN.get(mesh.N);
  const N = mesh.N, tris = mesh.triangles, sets = Array.from({ length: N }, () => new Set());
  for (let t = 0; t < tris.length; t += 3) { const a = tris[t], b = tris[t + 1], c = tris[t + 2]; sets[a].add(b).add(c); sets[b].add(a).add(c); sets[c].add(a).add(b); }
  const start = new Int32Array(N + 1); let n = 0;
  for (let i = 0; i < N; i++) { start[i] = n; n += sets[i].size; }
  start[N] = n; const list = new Int32Array(n); n = 0;
  for (let i = 0; i < N; i++) for (const k of sets[i]) list[n++] = k;
  const nb = { start, list };
  byN.set(N, nb);
  return nb;
}
