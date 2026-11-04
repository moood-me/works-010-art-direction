// Capsules round a body's bones at its rest: a tapered capsule along each bone that carries enough skin (from the
// joint to its child farthest away — the spine's next joint, not a collarbone), its radius at each end a share of the
// skin's distances round that half of the bone. The body's solids (src/solids.js) take them as its coarse inside, a pose
// layer (src/layers.js armsOff) as what the arms keep clear of.
//   fitCapsules(rig, mesh, {fit = 0.5 (the share: 0.5 the median), inset = 0 (metres off each radius), minVertices = 30})
//     → [{joint, child, a, b, ra, rb}] at rest (cached per mesh, rig and options)
const CACHE = new WeakMap();

export function fitCapsules(rig, mesh, { fit = 0.5, inset = 0, minVertices = 30 } = {}) {
  const key = `${fit}|${inset}|${minVertices}`; let byRig = CACHE.get(mesh.positions); if (!byRig) CACHE.set(mesh.positions, byRig = new WeakMap());
  let m = byRig.get(rig); if (!m) byRig.set(rig, m = new Map());
  if (!m.has(key)) m.set(key, fitted(rig, mesh, fit, inset, minVertices));
  return m.get(key);
}

function fitted(rig, mesh, fit, inset, minVertices) {
  const sk = rig.skeleton, R = rig.joints, P = mesh.positions, K = mesh.skin.K, SJ = mesh.skin.joints, SW = mesh.skin.weights, out = [];
  for (let j = 0; j < sk.J; j++) {
    let child = -1, far = 0;
    for (const k of sk.children[j]) { const d = Math.hypot(R[k * 3] - R[j * 3], R[k * 3 + 1] - R[j * 3 + 1], R[k * 3 + 2] - R[j * 3 + 2]); if (d > far) { far = d; child = k; } }
    if (child < 0 || far < 0.02) continue;
    const a = [R[j * 3], R[j * 3 + 1], R[j * 3 + 2]], b = [R[child * 3], R[child * 3 + 1], R[child * 3 + 2]], ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], L2 = far * far, ts = [], ds = [];
    for (const i of mesh.used) {
      let w = 0; for (let k = 0; k < K; k++) if (SJ[i * K + k] === j) w += SW[i * K + k];
      if (w < 0.5) continue;
      const t = ((P[i * 3] - a[0]) * ab[0] + (P[i * 3 + 1] - a[1]) * ab[1] + (P[i * 3 + 2] - a[2]) * ab[2]) / L2;
      if (t < 0 || t > 1) continue;
      ts.push(t); ds.push(Math.hypot(P[i * 3] - a[0] - ab[0] * t, P[i * 3 + 1] - a[1] - ab[1] * t, P[i * 3 + 2] - a[2] - ab[2] * t));
    }
    if (ts.length < minVertices) continue;
    const at = (lo, hi) => { const d = ds.filter((_, n) => ts[n] >= lo && ts[n] <= hi).sort((x, y) => x - y); return d.length ? d[Math.min(d.length - 1, Math.floor(d.length * fit))] : null; };
    const all = at(0, 1), ra = at(0, 0.5) ?? all, rb = at(0.5, 1) ?? all;
    out.push({ joint: j, child, a, b, ra: Math.max(0.005, ra - inset), rb: Math.max(0.005, rb - inset) });
  }
  return out;
}
