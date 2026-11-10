// The small forms of the surface (Т1's anatomy, experiments/form; Т9's smoothing in centimetres,
// experiments/form-tools: `curvSmooth`).
//   anatomy  the small forms the body has, drawn out (amount > 0: the difference from a Taubin-smoothed copy added
//            again, ×1.6) or smoothed (< 0) — never anything not already there
//   smooth   the small forms within `cm` centimetres gone, the same reach wherever the mesh is fine or coarse (the
//            cotangent Laplacian: (M + t·L) x = M x₀ in one implicit step, solved by conjugate gradients — Anny's mesh
//            is twenty times finer at a nipple, a navel or a toe than on the back); what that takes from a limb's girth
//            is measured along the normal and smoothed again over twice the reach, so the even loss comes back and a
//            navel doesn't. `keep`: how much of their forms the head, the fingers and the toes keep (1 all of them; the
//            toes and fingers are thin and finely meshed: smoothed over centimetres they fold over)
// Both are changes of the surface: on the rest, or as a pose layer by a morph.
import { register } from '../deform.js';
import { taubin } from '../regions.js';
import { normalsOf } from '../mesh.js';
import { lerp } from '../math.js';
import { num } from '../schema.js';

const KEEP = { head: 1, fingers: 1, toes: 1 };

register({
  kind: 'anatomy', of: 'skin',
  params: { amount: num(-3, 3) },
  defaults: { amount: 0.5 },
  rest(p, R) {
    const P = R.mesh.positions, a = p.amount * p.strength, sm = taubin(P, R.nb, () => 1, 6), out = Float32Array.from(P), L = edgeOf(R);
    for (const i of R.mesh.used) {
      // the move no longer than a third of the mesh's own size there: where the mesh is fine (fingers, toes) its small
      // forms are drawn out as far as they can be without folding
      const k = a * (a > 0 ? 1.6 : 1), dx = (P[i * 3] - sm[i * 3]) * k, dy = (P[i * 3 + 1] - sm[i * 3 + 1]) * k, dz = (P[i * 3 + 2] - sm[i * 3 + 2]) * k;
      const l = Math.hypot(dx, dy, dz), lim = 0.33 * L[i], f = l > lim ? lim / l : 1;
      out[i * 3] += dx * f; out[i * 3 + 1] += dy * f; out[i * 3 + 2] += dz * f;
    }
    return { positions: out };
  },
});

register({
  kind: 'smooth', of: 'skin',
  params: { cm: num(0, 20), keep: { type: 'object', props: { head: num(0, 1), fingers: num(0, 1), toes: num(0, 1) } } },
  defaults: { cm: 4, keep: KEEP },
  rest(p, R) {
    const keep = { ...KEEP, ...p.keep }, s = p.strength;
    const amount = i => s * (1 - keep.fingers * R.fingers[i]) * (1 - keep.toes * R.toes[i]) * (1 - keep.head * R.head[i]);
    return { positions: curvSmooth(R, R.mesh.positions, p.cm / 100, amount) };
  },
});

// the cotangent Laplacian's weights (per neighbour, in the order of the mesh's neighbour lists) and the lumped areas
function cotan(R, pos) {
  const T = R.mesh.triangles, nb = R.nb, N = R.mesh.N, W = new Float64Array(nb.list.length), M = new Float64Array(N);
  const slot = (a, b) => { for (let q = nb.start[a]; q < nb.start[a + 1]; q++) if (nb.list[q] === b) return q; return -1; };
  for (let t = 0; t < T.length; t += 3) {
    const v = [T[t], T[t + 1], T[t + 2]];
    const ax = pos[v[1] * 3] - pos[v[0] * 3], ay = pos[v[1] * 3 + 1] - pos[v[0] * 3 + 1], az = pos[v[1] * 3 + 2] - pos[v[0] * 3 + 2];
    const bx = pos[v[2] * 3] - pos[v[0] * 3], by = pos[v[2] * 3 + 1] - pos[v[0] * 3 + 1], bz = pos[v[2] * 3 + 2] - pos[v[0] * 3 + 2];
    const area = 0.5 * Math.hypot(ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx);
    for (const i of v) M[i] += area / 3;
    for (let k = 0; k < 3; k++) {
      const a = v[k], b = v[(k + 1) % 3], c = v[(k + 2) % 3];
      const ux = pos[a * 3] - pos[c * 3], uy = pos[a * 3 + 1] - pos[c * 3 + 1], uz = pos[a * 3 + 2] - pos[c * 3 + 2];
      const wx = pos[b * 3] - pos[c * 3], wy = pos[b * 3 + 1] - pos[c * 3 + 1], wz = pos[b * 3 + 2] - pos[c * 3 + 2];
      const dot = ux * wx + uy * wy + uz * wz, cr = Math.hypot(uy * wz - uz * wy, uz * wx - ux * wz, ux * wy - uy * wx) || 1e-12;
      const w = Math.max(0, 0.5 * dot / cr);
      W[slot(a, b)] += w; W[slot(b, a)] += w;
    }
  }
  for (let i = 0; i < N; i++) if (!M[i]) M[i] = 1;
  return { W, M };
}
// (M + t·L) x = M·b for one scalar field, by conjugate gradients with a diagonal preconditioner
function heat(R, L, b, t) {
  const { W, M } = L, nb = R.nb, N = M.length, D = new Float64Array(N);
  for (let i = 0; i < N; i++) { let s = 0; for (let q = nb.start[i]; q < nb.start[i + 1]; q++) s += W[q]; D[i] = M[i] + t * s; }
  const A = (x, out) => { for (let i = 0; i < N; i++) { let s = 0, sw = 0; for (let q = nb.start[i]; q < nb.start[i + 1]; q++) { s += W[q] * x[nb.list[q]]; sw += W[q]; } out[i] = M[i] * x[i] + t * (sw * x[i] - s); } };
  const x = Float64Array.from(b), r = new Float64Array(N), z = new Float64Array(N), p = new Float64Array(N), q = new Float64Array(N);
  A(x, q); let bn = 0; for (let i = 0; i < N; i++) { r[i] = M[i] * b[i] - q[i]; bn += (M[i] * b[i]) ** 2; }
  for (let i = 0; i < N; i++) { z[i] = r[i] / D[i]; p[i] = z[i]; }
  let rz = 0; for (let i = 0; i < N; i++) rz += r[i] * z[i];
  for (let it = 0; it < 400; it++) {
    A(p, q); let pq = 0; for (let i = 0; i < N; i++) pq += p[i] * q[i];
    const al = rz / pq; let rr = 0;
    for (let i = 0; i < N; i++) { x[i] += al * p[i]; r[i] -= al * q[i]; rr += r[i] * r[i]; }
    if (rr < 1e-14 * bn) break;
    let rz2 = 0; for (let i = 0; i < N; i++) { z[i] = r[i] / D[i]; rz2 += r[i] * z[i]; }
    const be = rz2 / rz; rz = rz2; for (let i = 0; i < N; i++) p[i] = z[i] + be * p[i];
  }
  return x;
}
export function curvSmooth(R, pos, reach, amount) {
  const N = R.mesh.N, L = cotan(R, pos), S = new Float32Array(pos.length);
  for (let c = 0; c < 3; c++) { const x = heat(R, L, Float64Array.from({ length: N }, (_, i) => pos[i * 3 + c]), reach * reach); for (let i = 0; i < N; i++) S[i * 3 + c] = x[i]; }
  const n = normalsOf(S, R.mesh.triangles), d = new Float64Array(N);
  for (let i = 0; i < N; i++) d[i] = (pos[i * 3] - S[i * 3]) * n[i * 3] + (pos[i * 3 + 1] - S[i * 3 + 1]) * n[i * 3 + 1] + (pos[i * 3 + 2] - S[i * 3 + 2]) * n[i * 3 + 2];
  const ds = heat(R, L, d, 4 * reach * reach), out = Float32Array.from(pos);
  for (const i of R.mesh.used) { const w = amount(i); for (let c = 0; c < 3; c++) out[i * 3 + c] = lerp(pos[i * 3 + c], S[i * 3 + c] + ds[i] * n[i * 3 + c], w); }
  return out;
}

// each vertex's mean edge length at the rest
function edgeOf(R) {
  const P = R.mesh.positions, nb = R.nb, L = new Float32Array(R.mesh.N);
  for (const i of R.mesh.used) {
    let s = 0; const a = nb.start[i], b = nb.start[i + 1];
    for (let q = a; q < b; q++) { const j = nb.list[q]; s += Math.hypot(P[i * 3] - P[j * 3], P[i * 3 + 1] - P[j * 3 + 1], P[i * 3 + 2] - P[j * 3 + 2]); }
    L[i] = b > a ? s / (b - a) : 0;
  }
  return L;
}
