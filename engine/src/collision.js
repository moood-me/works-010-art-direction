// The body as something to collide with — for hair and cloth: a tapered capsule along each bone that carries enough
// skin (from the joint to its child, its radius at each end fitted to the skin around it at rest), moved by the pose
// each frame. Hair and clothes ask how far a point is from the body and which way is out.
//   const C = makeCollider(rig, mesh);      // once (cached per mesh and rig)
//   C.update(pose);                          // each frame, after the floor step (the pose as drawn)
//   C.distance(x, out?) → d (metres; < 0 inside), out = {normal: [x, y, z], capsule}
//   C.capsules: [{joint, child, a: [3], b: [3], ra, rb}] — now (after update); C.rest: the same at rest
// `inset` (metres) shrinks every radius (the skin is soft: cloth may rest a little into it), `fit` the share of the
// skin's distances the radius covers (0.5: the median).
import { qRot3 } from './math.js';

const CACHE = new WeakMap(), tmp = [0, 0, 0];

export function makeCollider(rig, mesh, { inset = 0, fit = 0.5, minVertices = 30 } = {}) {
  const key = `${inset}|${fit}|${minVertices}`; let byRig = CACHE.get(mesh.positions); if (!byRig) CACHE.set(mesh.positions, byRig = new WeakMap());
  let m = byRig.get(rig); if (!m) byRig.set(rig, m = new Map());
  const rest = m.get(key) ?? fitCapsules(rig, mesh, inset, fit, minVertices); m.set(key, rest);
  const now = rest.map(c => ({ ...c, a: c.a.slice(), b: c.b.slice() }));
  const C = {
    rest, capsules: now,
    update(pose) {
      for (let n = 0; n < rest.length; n++) {
        const c = rest[n], j = c.joint, q = [pose.Q[j * 4], pose.Q[j * 4 + 1], pose.Q[j * 4 + 2], pose.Q[j * 4 + 3]];
        for (const [from, to] of [[c.a, now[n].a], [c.b, now[n].b]]) {
          const v = qRot3(q, from[0] - rig.joints[j * 3], from[1] - rig.joints[j * 3 + 1], from[2] - rig.joints[j * 3 + 2], tmp);
          to[0] = pose.P[j * 3] + v[0]; to[1] = pose.P[j * 3 + 1] + v[1]; to[2] = pose.P[j * 3 + 2] + v[2];
        }
      }
      return C;
    },
    distance(x, out) {
      let best = Infinity, bc = null, bn = null;
      for (const c of now) {
        const abx = c.b[0] - c.a[0], aby = c.b[1] - c.a[1], abz = c.b[2] - c.a[2], L2 = abx * abx + aby * aby + abz * abz;
        let t = L2 > 0 ? ((x[0] - c.a[0]) * abx + (x[1] - c.a[1]) * aby + (x[2] - c.a[2]) * abz) / L2 : 0;
        t = t < 0 ? 0 : t > 1 ? 1 : t;
        const px = x[0] - (c.a[0] + abx * t), py = x[1] - (c.a[1] + aby * t), pz = x[2] - (c.a[2] + abz * t);
        const l = Math.hypot(px, py, pz), d = l - (c.ra + (c.rb - c.ra) * t);
        if (d < best) { best = d; bc = c; bn = l > 1e-9 ? [px / l, py / l, pz / l] : [0, 1, 0]; }
      }
      if (out) { out.normal = bn; out.capsule = bc; }
      return best;
    },
  };
  return C;
}

function fitCapsules(rig, mesh, inset, fit, minVertices) {
  const sk = rig.skeleton, R = rig.joints, P = mesh.positions, K = mesh.skin.K, SJ = mesh.skin.joints, SW = mesh.skin.weights;
  const out = [];
  for (let j = 0; j < sk.J; j++) {
    // the bone: to the child farthest away (the spine's next joint, not a collarbone)
    let child = -1, far = 0;
    for (const k of sk.children[j]) { const d = Math.hypot(R[k * 3] - R[j * 3], R[k * 3 + 1] - R[j * 3 + 1], R[k * 3 + 2] - R[j * 3 + 2]); if (d > far) { far = d; child = k; } }
    if (child < 0 || far < 0.02) continue;
    const a = [R[j * 3], R[j * 3 + 1], R[j * 3 + 2]], b = [R[child * 3], R[child * 3 + 1], R[child * 3 + 2]];
    const ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], L2 = far * far;
    const ts = [], ds = [];
    for (const i of mesh.used) {
      let w = 0; for (let k = 0; k < K; k++) if (SJ[i * K + k] === j) w += SW[i * K + k];
      if (w < 0.5) continue;
      const x = [P[i * 3], P[i * 3 + 1], P[i * 3 + 2]];
      const t = ((x[0] - a[0]) * ab[0] + (x[1] - a[1]) * ab[1] + (x[2] - a[2]) * ab[2]) / L2;
      if (t < 0 || t > 1) continue;
      ts.push(t); ds.push(Math.hypot(x[0] - a[0] - ab[0] * t, x[1] - a[1] - ab[1] * t, x[2] - a[2] - ab[2] * t));
    }
    if (ts.length < minVertices) continue;
    // the radius at each end: the skin's distances in each half, at the share `fit`
    const at = (lo, hi) => { const d = ds.filter((_, n) => ts[n] >= lo && ts[n] <= hi).sort((x, y) => x - y); return d.length ? d[Math.min(d.length - 1, Math.floor(d.length * fit))] : null; };
    const all = at(0, 1), ra = at(0, 0.5) ?? all, rb = at(0.5, 1) ?? all;
    out.push({ joint: j, child, a, b, ra: Math.max(0.005, ra - inset), rb: Math.max(0.005, rb - inset) });
  }
  return out;
}

