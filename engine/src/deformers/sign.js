// Т4's sign (experiments/form: `signSurface`, carried there by `settle`): the body becomes a pictogram — a ball for
// the head (lifted off the body by `gap`), one plain figure for the trunk (rectangle, trapezoid, inverted, oval; the
// triangle's dress is a garment's and is left to clothes), sticks for the arms and legs `limbs` thick (a share of
// the height), balls for the hands — melted together, and each point of the body carried onto that surface (as Т1:
// where the points want to go, smoothed over the body as one field, then each settles along its normal; a point the
// way went wrong for is relaxed among its neighbours and set on again). The strength blends the body into its sign.
// Usually after smoothing (presets/pictogram).
import { register } from '../deform.js';
import { taubin, normalsAt, smoothField, lerp, clamp } from '../regions.js';
import { cone } from './masses.js';

const num = (min, max) => ({ type: 'number', min, max });
const FIGURES = { inverted: [1.05, 0.45], rectangle: [0.8, 0.8], trapezoid: [0.95, 0.7], oval: [0.75, 0.75] };

register({
  kind: 'sign', of: 'skin',
  params: { figure: { type: 'string', enum: Object.keys(FIGURES) }, gap: num(0, 1), limbs: num(0.2, 3) },
  defaults: { figure: 'rectangle', gap: 0, limbs: 1 },
  rest(p, R) {
    const F = signSurface(p, R), P = R.mesh.positions, hand = Float32Array.from(R.ends, (v, i) => Math.min(1, v + R.head[i]));
    const own = Int8Array.from({ length: R.mesh.N }, (_, i) => { let b = 0; for (let c = 1; c < 5; c++) if (R.limb[i * 5 + c] > R.limb[i * 5 + b]) b = c; return b; });
    const Fi = i => own[i] ? F.part[own[i] - 1] : F;
    const sg = settle(R, Float32Array.from(P), Fi, hand), s = p.strength;
    return { positions: Float32Array.from(P, (v, i) => lerp(v, sg[i], s)) };
  },
});

function signSurface(p, R) {
  const sk = R.skeleton, J = R.rig.joints, P = R.mesh.positions, at = n => { const j = sk.index[n]; return [J[j * 3], J[j * 3 + 1], J[j * 3 + 2]]; };
  // the head as a ball: the centre of the skin that is the head's, its mean reach (Т1's head mass, its six radii)
  const c = [0, 0, 0]; let n = 0;
  for (const i of R.mesh.used) if (R.head[i] > 0.9) { c[0] += P[i * 3]; c[1] += P[i * 3 + 1]; c[2] += P[i * 3 + 2]; n++; }
  c[0] /= n; c[1] /= n; c[2] /= n;
  const reach = [[], [], [], [], [], []];
  for (const i of R.mesh.used) if (R.head[i] > 0.9) for (let k = 0; k < 3; k++) { const d = P[i * 3 + k] - c[k]; reach[k * 2 + (d >= 0 ? 0 : 1)].push(Math.abs(d)); }
  const hr = reach.map(v => { v.sort((a, b) => a - b); return v[Math.floor(v.length * 0.93)]; }).reduce((a, b) => a + b, 0) / 6 * 1.08;
  const height = R.height, lift = p.gap * 0.06 * height, head = at('Head');
  const hc = [head[0], (c[1] + head[1]) / 2 + 0.25 * hr + lift, head[2]];
  const hips = at('Hips'), sh = [0, (at('LeftArm')[1] + at('RightArm')[1]) / 2 + 0.02, hips[2]], hp = [0, hips[1] - 0.05 * height, hips[2]];
  const w = Math.abs(at('LeftArm')[0] - at('RightArm')[0]) / 2, [rt, rb] = FIGURES[p.figure].map(k => k * w), flat = 0.55;
  const ball = (q, r) => (x, y, z) => Math.hypot(x - q[0], y - q[1], z - q[2]) - r;
  const torso = p.figure === 'oval'
    ? (x, y, z) => { const m = [(sh[0] + hp[0]) / 2, (sh[1] + hp[1]) / 2, (sh[2] + hp[2]) / 2], ry = (sh[1] - hp[1]) / 2 + 0.02, k0 = Math.hypot((x - m[0]) / rt, (y - m[1]) / ry, (z - m[2]) / (rt * flat)); return (k0 - 1) * Math.min(rt * flat, ry); }
    : (() => { const f = cone(hp, sh, rb, rt); return (x, y, z) => f(x, y, sh[2] + (z - sh[2]) / flat) * flat; })();
  const lr = 0.035 * height * p.limbs, stick = (a, b, r) => cone(at(a), at(b), r, r);
  const parts = [ball(hc, hr), torso, stick('LeftArm', 'LeftHand', lr * 0.85), stick('RightArm', 'RightHand', lr * 0.85),
    stick('LeftLeg', 'LeftFoot', lr), stick('RightLeg', 'RightFoot', lr), ball(at('LeftHandMiddle2'), lr * 1.15), ball(at('RightHandMiddle2'), lr * 1.15),
    stick('LeftFoot', 'LeftToeEnd', lr * 0.9), stick('RightFoot', 'RightToeEnd', lr * 0.9),
    cone(at('Neck1'), hc, lerp(0.035 * height, 0.003, p.gap), lerp(0.03 * height, 0.003, p.gap)),
    // round shoulders: the arm's root as a ball, so the skin between the trunk and the arm has a surface to go to
    ball(at('LeftArm'), lr * 1.25), ball(at('RightArm'), lr * 1.25)];
  // the arms meet the trunk in a rounder joint than the rest; each limb's skin goes onto the trunk and that limb only
  // (Т1's surfaceOf): the skin of an armpit is not torn between the trunk's side and the arm
  const U = (list, k) => (x, y, z) => { let d = list[0](x, y, z); for (let i = 1; i < list.length; i++) d = smin(d, list[i](x, y, z), k[i]); return d; };
  const [hd, tr, aL, aR, lL, lR, hL, hR, fL, fR, nk, sL, sR] = parts;
  const trunk = U([tr, hd, nk], [0, 0.012, 0.012]);
  const arm = (a, h, s) => U([a, h, s], [0, 0.012, 0.03]), leg = (l, f) => U([l, f], [0, 0.012]);
  const A = [arm(aL, hL, sL), arm(aR, hR, sR), leg(lL, fL), leg(lR, fR)];
  const all = (x, y, z) => { const t = trunk(x, y, z); return Math.min(smin(t, A[0](x, y, z), 0.035), smin(t, A[1](x, y, z), 0.035), smin(t, A[2](x, y, z), 0.012), smin(t, A[3](x, y, z), 0.012)); };
  all.part = A.map((f, i) => (x, y, z) => smin(trunk(x, y, z), f(x, y, z), i < 2 ? 0.035 : 0.012));
  return all;
}
function smin(a, b, k) { const h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * 0.25; }

// —— carrying points onto a surface given as a distance (Т1: project, normalProject, settle, repair) ——
function project(R, arr, F, its, only) {
  const e = 0.0015;
  for (const i of only ?? R.mesh.used) {
    let x = arr[i * 3], y = arr[i * 3 + 1], z = arr[i * 3 + 2];
    for (let it = 0; it < its; it++) {
      const S = F(i), d = S(x, y, z); if (Math.abs(d) < 0.0004) break;
      const gx = (S(x + e, y, z) - d) / e, gy = (S(x, y + e, z) - d) / e, gz = (S(x, y, z + e) - d) / e, g2 = gx * gx + gy * gy + gz * gz;
      if (g2 < 1e-8) break;
      // a step no longer than two centimetres: a far point walks to the surface, it does not jump past it
      let k = d / g2; const step = Math.abs(k) * Math.sqrt(g2); if (step > 0.02) k *= 0.02 / step;
      x -= gx * k; y -= gy * k; z -= gz * k;
    }
    arr[i * 3] = x; arr[i * 3 + 1] = y; arr[i * 3 + 2] = z;
  }
  return arr;
}
// onto the surface along each point's own normal only: points keep their spacing, nothing slides into a heap
function normalProject(R, arr, F, its) {
  const nrm = normalsAt(arr, R.mesh.triangles), e = 0.0015;
  for (const i of R.mesh.used) {
    const nx = nrm[i * 3], ny = nrm[i * 3 + 1], nz = nrm[i * 3 + 2];
    let x = arr[i * 3], y = arr[i * 3 + 1], z = arr[i * 3 + 2];
    for (let it = 0; it < its; it++) {
      const S = F(i), d = S(x, y, z); if (Math.abs(d) < 0.0003) break;
      let dn = (S(x + nx * e, y + ny * e, z + nz * e) - d) / e;
      if (Math.abs(dn) < 0.25) dn = dn < 0 ? -0.25 : 0.25;
      const step = clamp(-d / dn, -0.015, 0.015);
      x += nx * step; y += ny * step; z += nz * step;
    }
    arr[i * 3] = x; arr[i * 3 + 1] = y; arr[i * 3 + 2] = z;
  }
  return arr;
}
// where the points want to go, as one smooth field over the body; then each settles along its normal. F(i): the
// surface (a distance) point i goes onto
export function settle(R, arr, F, hand) {
  const from = Float32Array.from(arr);
  project(R, arr, F, 12);
  const disp = Float32Array.from(arr, (v, i) => v - from[i]);
  smoothField(disp, 3, R.nb, 20);
  for (let i = 0; i < arr.length; i++) arr[i] = from[i] + disp[i];
  normalProject(R, arr, F, 8);
  arr = taubin(arr, R.nb, i => 0.3 + 0.4 * hand[i], 1);
  normalProject(R, arr, F, 4);
  return repair(R, arr, F, from);
}
// where a point was carried too far for its normal to know the way, or a triangle turned over: straighten it there
function repair(R, arr, F, from) {
  const T = R.mesh.triangles, N = R.mesh.N, nb = R.nb;
  for (let round = 0; round < 4; round++) {
    const bad = new Uint8Array(N), n0 = normalsAt(from, T);
    for (let t = 0; t < T.length; t += 3) {
      const a = T[t] * 3, b = T[t + 1] * 3, c = T[t + 2] * 3;
      const ux = arr[b] - arr[a], uy = arr[b + 1] - arr[a + 1], uz = arr[b + 2] - arr[a + 2], vx = arr[c] - arr[a], vy = arr[c + 1] - arr[a + 1], vz = arr[c + 2] - arr[a + 2];
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      const turned = nx * n0[a] + ny * n0[a + 1] + nz * n0[a + 2] < 0;
      const l0 = Math.hypot(from[b] - from[a], from[b + 1] - from[a + 1], from[b + 2] - from[a + 2]) + 1e-6, l1 = Math.hypot(ux, uy, uz);
      if (turned || l1 > 4 * l0 + 0.01) bad[T[t]] = bad[T[t + 1]] = bad[T[t + 2]] = 1;
    }
    for (const i of R.mesh.used) if (!bad[i] && Math.abs(F(i)(arr[i * 3], arr[i * 3 + 1], arr[i * 3 + 2])) > 0.006) bad[i] = 1;
    let count = 0; for (let i = 0; i < N; i++) count += bad[i];
    if (!count) break;
    const grow = Uint8Array.from(bad); for (let i = 0; i < N; i++) if (bad[i]) for (let q = nb.start[i]; q < nb.start[i + 1]; q++) grow[nb.list[q]] = 1;
    arr = taubin(arr, nb, i => grow[i] ? 1 : 0, 4);
    const sub = []; for (const i of R.mesh.used) if (grow[i]) sub.push(i);
    project(R, arr, F, 10, sub);
  }
  return arr;
}
