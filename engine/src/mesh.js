// Meshes a rig moves. Every kind gives, each frame, its vertices in the pose (and the engine their normals); the
// floor step (src/figure.js) then looks at every mesh that counts for the floor, over the vertices its triangles use.
//   skinned     {kind: 'skinned', id, positions (rest, N×3), triangles, skin: {joints, weights, K}, morphs?, floor?}
//               skinned by src/skin.js; K influences a vertex (4 for Anny's mesh; any number)
//   rigid       {kind: 'rigid', id, joint, positions (rest, in the body's rest space), triangles, floor?}
//               carried whole by one joint (an eye, a hat, a piece of a head): its own transform kept
//   procedural  {kind: 'procedural', id, N, triangles, build(pose, rig, out), floor?}
//               rebuilt from the pose each frame (sweeps along curves through the joints, bending in arcs)
// triangles: Uint32Array (or Uint16Array while N ≤ 65,536). `used`: the vertices the triangles use — only they are
// skinned, drawn and counted for the floor. morphs: {name: {indices: Uint32Array, deltas: Float32Array (n×3)}} —
// rest changes applied before skinning, each with a weight (src/figure.js: a rest change or a pose layer).
export function makeMesh(o) {
  const kind = o.kind || 'skinned';
  if (!['skinned', 'rigid', 'procedural'].includes(kind)) throw new Error(`no mesh kind "${kind}"`);
  const N = kind === 'procedural' ? o.N : o.positions.length / 3;
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

// vertex normals (area-weighted) over the used vertices, into out
export function normalsOf(pos, tris, out, used) {
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
