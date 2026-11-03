// Т4's sign (experiments/form: `signSurface`, carried there by `settle`): the body becomes a pictogram — a ball for
// the head (lifted off the body by `gap`), one plain figure for the trunk (rectangle, trapezoid, inverted, oval; the
// triangle's dress is a garment's and is left to clothes) with a bar across the shoulders and one across the hips,
// a stick for each bone of the arms and legs `limbs` thick (a
// share of the height) with a ball at the shoulder, the elbow, the hip, the knee and the ankle, a ball for each hand
// and a rounded foot — melted together. The strength blends the body into its sign. Usually after smoothing
// (presets/pictogram-*). A change of the rest only: it gives its own skin weights.
//
// How the skin gets there. The trunk's and the head's skin settles onto the trunk, neck and head (as Т1: where the
// points want to go, smoothed over the body as one field, then each settles along its normal); each limb's skin goes
// out from its own bones' line to where that ray meets the limb's surface (its sticks, balls, hand, foot); the two are
// blended by the limb's share of each point (smoothed over the surface), then everything is set on the whole sign's
// surface along its normals, the hands' and feet's skin relaxed on it (their fingers and toes would lie folded over),
// and a point the way went wrong for is relaxed among its neighbours and set on again.
//
// Why its own weights. Anny's weights are for Anny's skin: on a stick they spread the skin gathered at the root of the
// arm over the chest and the collarbone, and a stick straight from the shoulder to the wrist bends nowhere — so the
// arm opened at the shoulder and thinned to a ribbon as soon as it swung. Here each piece is carried by its own bone:
// a stick by its bone, a ball at a joint by the two bones it joins, blended across the ball (a ball turned about its
// own centre stays the same ball, so a bent elbow or a raised arm never opens), the hand's ball by the hand, the foot
// by the foot and its toes, the head's ball by the head; the trunk by Anny's weights of the trunk and the neck; where
// a limb meets the trunk, by both as the point belongs to each.
import { register } from '../deform.js';
import { taubin, smoothField } from '../regions.js';
import { normalsOf } from '../mesh.js';
import { lerp, clamp, sst, smin } from '../math.js';
import { cone } from './masses.js';

const num = (min, max) => ({ type: 'number', min, max });
const FIGURES = { inverted: [1.05, 0.45], rectangle: [0.8, 0.8], trapezoid: [0.95, 0.7], oval: [0.75, 0.75] };

register({
  kind: 'sign', of: 'skin', restOnly: true,
  params: { figure: { type: 'string', enum: Object.keys(FIGURES) }, gap: num(0, 1), limbs: num(0.2, 3) },
  defaults: { figure: 'rectangle', gap: 0, limbs: 1 },
  rest(p, R) {
    const S = signOf(p, R), P = R.mesh.positions, s = p.strength;
    const ends = Float32Array.from(R.ends, (v, i) => Math.min(1, v + R.head[i]));
    // the trunk's and head's skin onto the trunk, neck and head
    const T = settle(R, Float32Array.from(P), () => S.trunk, ends);
    // each limb's skin out from its own line onto the limb; blended with the trunk's by the limb's share
    const out = Float32Array.from(P), q = [0, 0, 0];
    for (const i of R.mesh.used) {
      let x = 0, y = 0, z = 0, wl = 0;
      for (let l = 1; l < 5; l++) {
        const w = R.limb[i * 5 + l]; if (w < 1e-3) continue;
        S.limbs[l - 1].onto(P[i * 3], P[i * 3 + 1], P[i * 3 + 2], q);
        x += w * q[0]; y += w * q[1]; z += w * q[2]; wl += w;
      }
      const wb = 1 - wl;
      out[i * 3] = wb * T[i * 3] + x; out[i * 3 + 1] = wb * T[i * 3 + 1] + y; out[i * 3 + 2] = wb * T[i * 3 + 2] + z;
    }
    // then all of it on the whole sign
    normalProject(R, out, () => S.all, 6);
    // the hands and the feet: much skin gathered onto a little ball or foot, their fingers and toes folded over on it —
    // their skin relaxed on the surface (smoothed over it and set back on it, again and again, the wrist and the
    // ankle held), until it lies on it as one even sheet
    const hf = [], wt = i => R.ends[i];
    for (const i of R.mesh.used) if (R.ends[i] > 0.02) hf.push(i);
    let X = out;
    for (let it = 0; it < 60; it++) X = project(R, taubin(X, R.nb, wt, 1, 0), () => S.all, 3, hf);
    const settled = repair(R, taubin(X, R.nb, i => 0.25 + 0.5 * ends[i], 1), () => S.all, P);
    for (const i of R.mesh.used) for (let c = 0; c < 3; c++) out[i * 3 + c] = lerp(P[i * 3 + c], settled[i * 3 + c], s);
    return { positions: out, skin: s > 0 ? weightsOf(R, S, settled) : undefined };
  },
});

// —— the sign's surface, as distances ——
export function signOf(p, R) {
  const sk = R.skeleton, J = R.rig.joints, P = R.mesh.positions, at = n => { const j = sk.index[n]; return [J[j * 3], J[j * 3 + 1], J[j * 3 + 2]]; };
  const H = R.height, floor = R.levels.floor, mid = (a, b, t = 0.5) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
  // the head as a ball: the centre of the skin that is the head's, its reach (the 93rd percentile each way, averaged)
  const c = [0, 0, 0]; let n = 0;
  for (const i of R.mesh.used) if (R.head[i] > 0.9) { c[0] += P[i * 3]; c[1] += P[i * 3 + 1]; c[2] += P[i * 3 + 2]; n++; }
  c[0] /= n; c[1] /= n; c[2] /= n;
  const reach = [[], [], [], [], [], []];
  for (const i of R.mesh.used) if (R.head[i] > 0.9) for (let k = 0; k < 3; k++) { const d = P[i * 3 + k] - c[k]; reach[k * 2 + (d >= 0 ? 0 : 1)].push(Math.abs(d)); }
  const hr = reach.map(v => { v.sort((a, b) => a - b); return v[Math.floor(v.length * 0.93)]; }).reduce((a, b) => a + b, 0) / 6 * 1.08;
  const head = at('Head'), hc = [head[0], (c[1] + head[1]) / 2 + 0.25 * hr + p.gap * 0.06 * H, head[2]];
  // the trunk: between the shoulders' line and below the hips, about the pelvis's own middle
  const hips = at('Hips'), lA = at('LeftArm'), rA = at('RightArm');
  const w = Math.abs(lA[0] - rA[0]) / 2, [rt, rb] = FIGURES[p.figure].map(k => k * w), flat = 0.55, lr = 0.035 * H * p.limbs;
  // its bottom no lower than the hips' bar (below it, between the thighs, it would be skin a raised leg pulls into a web)
  const legY = (at('LeftLeg')[1] + at('RightLeg')[1]) / 2;
  const sh = [hips[0], (lA[1] + rA[1]) / 2 + 0.012 * H, hips[2]], hp = [hips[0], legY - lr + rb * 0.9, hips[2]];
  const ball = (q, r) => (x, y, z) => Math.hypot(x - q[0], y - q[1], z - q[2]) - r;
  const torso = p.figure === 'oval'
    ? (() => { const m = mid(sh, hp), ry = (sh[1] - hp[1]) / 2 + 0.012 * H; return (x, y, z) => (Math.hypot((x - m[0]) / rt, (y - m[1]) / ry, (z - m[2]) / (rt * flat)) - 1) * Math.min(rt * flat, ry); })()
    : (() => { const f = cone(hp, sh, rb, rt); return (x, y, z) => f(x, y, sh[2] + (z - sh[2]) / flat) * flat; })();
  const k = 0.007 * H;   // how far pieces melt into each other
  const neck = cone(at('Neck1'), hc, lerp(0.035 * H, 0.002 * H, p.gap), lerp(0.03 * H, 0.002 * H, p.gap)), hd = ball(hc, hr);
  // the limbs' roots held by the trunk: a bar across the shoulders (the collarbones) and one across the hips (the
  // pelvis), so a ball at a shoulder or a hip always has the trunk right beside it, whatever the trunk's figure
  const lL = at('LeftLeg'), rL = at('RightLeg');
  const yoke = cone(lA, rA, lr * 0.8, lr * 0.8), pelvis = cone(lL, rL, lr * 0.95, lr * 0.95);
  const trunk = (x, y, z) => smin(smin(smin(smin(torso(x, y, z), yoke(x, y, z), k), pelvis(x, y, z), k), neck(x, y, z), k), hd(x, y, z), k);
  // the limbs: a stick per bone, a ball at each joint, the hand's ball, the foot — and the line their skin goes out from
  const limb = (names, r, ballR, endOf) => {
    const pts = names.map(at), end = endOf(pts), axis = [...pts, ...end.axis];   // (the foot's line from the ankle to its heel, then along it)
    const prims = [];
    for (let i = 0; i + 1 < pts.length; i++) prims.push(cone(pts[i], pts[i + 1], r, r));
    pts.forEach((q, i) => prims.push(ball(q, ballR[i])));
    prims.push(...end.prims);
    const f = (x, y, z) => { let d = prims[0](x, y, z); for (let i = 1; i < prims.length; i++) d = smin(d, prims[i](x, y, z), k); return d; };
    return { f, axis, pts, onto: ontoAlong(f, axis) };
  };
  const arm = s => limb([s + 'Arm', s + 'ForeArm', s + 'Hand'], lr * 0.85, [lr * 1.2, lr * 0.95, lr * 0.85], ([, , hand]) => {
    // the hand: a ball a little past the wrist, towards the knuckles
    const hcn = mid(hand, at(s + 'HandMiddle1'), 0.55);
    return { axis: [hcn], prims: [ball(hcn, lr * 1.0)] };
  });
  const leg = (s, l) => limb([s + 'Leg', s + 'Shin', s + 'Foot'], lr, [lr * 1.1, lr * 1.08, lr * 0.95], ([, , ankle]) => {
    // the foot: rounded, its sole on the floor, as long and as high as the foot's own skin — a cone from a ball at its
    // heel to a smaller one at its toes' tips (the line its skin goes out from runs along it)
    const ext = footOf(R, l, ankle[1]), rh = Math.min(lr * 0.8, 0.5 * (ankle[1] - floor)), rt = clamp(0.5 * ext.toeHeight, 0.6 * rh, rh);
    const heel = [ext.x, floor + rh, ext.back + rh], tip = [ext.x, floor + rt, Math.max(ext.back + rh, ext.front - rt)];
    return { axis: [heel, tip], prims: [cone(heel, tip, rh, rt)] };
  });
  const limbs = [arm('Left'), arm('Right'), leg('Left', 3), leg('Right', 4)];
  const all = (x, y, z) => { let d = trunk(x, y, z); for (const l of limbs) d = smin(d, l.f(x, y, z), k * 1.6); return d; };
  return { trunk, limbs, all, hc, hr, lr, k, seam: 1.6 * lr };
}
// a foot's own extent at the rest (below its ankle): its middle across, its back and its front, its height at the toes
function footOf(R, l, ankleY) {
  const P = R.mesh.positions; let x = 0, n = 0, back = Infinity, front = -Infinity;
  for (const i of R.mesh.used) {
    if (R.limb[i * 5 + l] < 0.9 || R.ends[i] < 0.5 || P[i * 3 + 1] > ankleY) continue;
    x += P[i * 3]; n++; back = Math.min(back, P[i * 3 + 2]); front = Math.max(front, P[i * 3 + 2]);
  }
  // how high it is at its toes (over its front fifth)
  let lo = Infinity, hi = -Infinity; const z0 = front - 0.2 * (front - back);
  for (const i of R.mesh.used) {
    if (R.limb[i * 5 + l] < 0.9 || R.ends[i] < 0.5 || P[i * 3 + 1] > ankleY || P[i * 3 + 2] < z0) continue;
    lo = Math.min(lo, P[i * 3 + 1]); hi = Math.max(hi, P[i * 3 + 1]);
  }
  return { x: x / n, back, front, toeHeight: hi - lo };
}
// a limb's skin onto its surface: from the nearest point of its line (shoulder, elbow, wrist, hand — or hip, knee,
// ankle, toes) out through the point, to where that ray meets the surface
function ontoAlong(f, axis) {
  const segs = [];
  for (let i = 0; i + 1 < axis.length; i++) { const a = axis[i], b = axis[i + 1], d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]; segs.push({ a, d, L2: d[0] ** 2 + d[1] ** 2 + d[2] ** 2 }); }
  return (x, y, z, out) => {
    let best = Infinity, cx = 0, cy = 0, cz = 0;
    for (const s of segs) {
      const t = clamp(((x - s.a[0]) * s.d[0] + (y - s.a[1]) * s.d[1] + (z - s.a[2]) * s.d[2]) / s.L2, 0, 1);
      const px = s.a[0] + s.d[0] * t, py = s.a[1] + s.d[1] * t, pz = s.a[2] + s.d[2] * t, dd = (x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2;
      if (dd < best) { best = dd; cx = px; cy = py; cz = pz; }
    }
    let dx = x - cx, dy = y - cy, dz = z - cz; const l = Math.hypot(dx, dy, dz) || 1; dx /= l; dy /= l; dz /= l;
    // inside at the axis; out along the ray until outside, then halve to the surface
    let lo = 0, hi = 0.02; while (f(cx + dx * hi, cy + dy * hi, cz + dz * hi) < 0 && hi < 1) hi *= 2;
    for (let it = 0; it < 24; it++) { const m = (lo + hi) / 2; if (f(cx + dx * m, cy + dy * m, cz + dz * m) < 0) lo = m; else hi = m; }
    const r = (lo + hi) / 2; out[0] = cx + dx * r; out[1] = cy + dy * r; out[2] = cz + dz * r;
    return out;
  };
}

// —— its own skin weights ——
// the trunk: Anny's weights on the trunk's and the neck's joints (the head's own: the head); a limb: by the bone each
// point lies along — a stick its bone, a joint's ball both bones across it, the hand's ball the hand, the foot the foot
// and its toes; the two blended by which of them the point lies on (its settled place: the skin of a shoulder's top
// that went onto the trunk is the trunk's, whatever Anny's weights said)
function weightsOf(R, S, X) {
  const sk = R.skeleton, N = R.mesh.N, K = 4, SJ = R.mesh.skin.joints, SW = R.mesh.skin.weights, K0 = R.mesh.skin.K;
  const ix = n => sk.index[n], HEAD = ix('Head');
  const TRUNK = new Set(['Hips', 'Spine1', 'Spine2', 'Chest', 'Neck1', 'Neck2', 'Head', 'LeftShoulder', 'RightShoulder'].map(ix));
  const toTrunk = j => (sk.part[j] === 'head' || sk.part[j] === 'eye') ? HEAD : TRUNK.has(j) ? j : -1;
  const chains = ['Left', 'Right'].map(s => ({ limb: s === 'Left' ? 1 : 2, js: [s + 'Arm', s + 'ForeArm', s + 'Hand'].map(ix), toe: null }))
    .concat(['Left', 'Right'].map(s => ({ limb: s === 'Left' ? 3 : 4, js: [s + 'Leg', s + 'Shin', s + 'Foot'].map(ix), toe: ix(s + 'ToeBase') })));
  const J = R.rig.joints, at = j => [J[j * 3], J[j * 3 + 1], J[j * 3 + 2]];
  const joints = new Uint8Array(N * K), weights = new Float32Array(N * K), acc = new Float64Array(sk.J), sw = [0, 0, 0];
  for (const c of chains) c.at = c.js.map(at);
  for (let i = 0; i < N; i++) {
    acc.fill(0);
    const x = X[i * 3], y = X[i * 3 + 1], z = X[i * 3 + 2];
    // which piece of the sign the point lies on: the trunk, or the limb it is nearest, by how much nearer — across the
    // seam where they melt, smoothly (a ball at a shoulder or a hip: its outer half the limb's, its inner the trunk's)
    let near = 0, dl = Infinity;
    for (let l = 0; l < 4; l++) { const d = S.limbs[l].f(x, y, z); if (d < dl) { dl = d; near = l + 1; } }
    const share = sst(0.5 + (S.trunk(x, y, z) - dl) / (2 * S.seam));
    let wt = 0;
    for (let k = 0; k < K0; k++) { const j = toTrunk(SJ[i * K0 + k]); if (j >= 0) wt += SW[i * K0 + k]; }
    const wb = 1 - share;
    if (wb > 1e-4) {
      if (wt > 0) for (let k = 0; k < K0; k++) { const j = toTrunk(SJ[i * K0 + k]); if (j >= 0) acc[j] += wb * SW[i * K0 + k] / wt; }
      else acc[near <= 2 ? ix('Chest') : ix('Hips')] += wb;
    }
    // each limb's part: along its bones
    for (const c of chains) {
      const wl = c.limb === near ? share : 0; if (wl < 1e-4) continue;
      boneShares(x, y, z, c.at, S.lr, sw);
      acc[c.js[0]] += wl * sw[0]; acc[c.js[1]] += wl * sw[1];
      if (c.toe == null) acc[c.js[2]] += wl * sw[2];
      else { const f = sst((z - J[c.toe * 3 + 2]) / (0.6 * S.lr) + 0.5); acc[c.js[2]] += wl * sw[2] * (1 - f); acc[c.toe] += wl * sw[2] * f; }
    }
    // the four largest
    for (let k = 0; k < K; k++) {
      let b = -1; for (let j = 0; j < sk.J; j++) if (acc[j] > 1e-5 && (b < 0 || acc[j] > acc[b])) b = j;
      if (b < 0) break;
      joints[i * K + k] = b; weights[i * K + k] = acc[b]; acc[b] = 0;
    }
    let t = 0; for (let k = 0; k < K; k++) t += weights[i * K + k];
    for (let k = 0; k < K; k++) weights[i * K + k] /= t || 1;
  }
  return { joints, weights, K };
}
// a point's shares of a limb's three bones (the root's, the mid's, the end's): across each joint's ball smoothly, by
// how far past the joint along the bone after it the point is
function boneShares(x, y, z, [a, m, b], r, out) {
  const past = (j, d0, d1, d2) => { const l = Math.hypot(d0, d1, d2); return ((x - j[0]) * d0 + (y - j[1]) * d1 + (z - j[2]) * d2) / l; };
  const s1 = sst(past(m, b[0] - m[0], b[1] - m[1], b[2] - m[2]) / (2 * r) + 0.5);
  const s2 = sst(past(b, b[0] - m[0], b[1] - m[1], b[2] - m[2]) / (1.4 * r) + 0.5);
  out[0] = 1 - s1; out[1] = s1 * (1 - s2); out[2] = s1 * s2;
  return out;
}

// —— carrying points onto a surface given as a distance (Т1: project, normalProject, settle, repair) ——
// (the tolerances and steps are shares of the body's height: the same on a child and on a man)
function project(R, arr, F, its, only) {
  const H = R.height, e = 0.0009 * H, tol = 0.00025 * H, far = 0.012 * H;
  for (const i of only ?? R.mesh.used) {
    let x = arr[i * 3], y = arr[i * 3 + 1], z = arr[i * 3 + 2];
    for (let it = 0; it < its; it++) {
      const S = F(i), d = S(x, y, z); if (Math.abs(d) < tol) break;
      const gx = (S(x + e, y, z) - d) / e, gy = (S(x, y + e, z) - d) / e, gz = (S(x, y, z + e) - d) / e, g2 = gx * gx + gy * gy + gz * gz;
      if (g2 < 1e-8) break;
      // a step no longer than about two centimetres: a far point walks to the surface, it does not jump past it
      let k = d / g2; const step = Math.abs(k) * Math.sqrt(g2); if (step > far) k *= far / step;
      x -= gx * k; y -= gy * k; z -= gz * k;
    }
    arr[i * 3] = x; arr[i * 3 + 1] = y; arr[i * 3 + 2] = z;
  }
  return arr;
}
// onto the surface along each point's own normal only: points keep their spacing, nothing slides into a heap
function normalProject(R, arr, F, its) {
  const H = R.height, nrm = normalsOf(arr, R.mesh.triangles), e = 0.0009 * H, tol = 0.0002 * H, far = 0.009 * H;
  for (const i of R.mesh.used) {
    const nx = nrm[i * 3], ny = nrm[i * 3 + 1], nz = nrm[i * 3 + 2];
    let x = arr[i * 3], y = arr[i * 3 + 1], z = arr[i * 3 + 2];
    for (let it = 0; it < its; it++) {
      const S = F(i), d = S(x, y, z); if (Math.abs(d) < tol) break;
      let dn = (S(x + nx * e, y + ny * e, z + nz * e) - d) / e;
      if (Math.abs(dn) < 0.25) dn = dn < 0 ? -0.25 : 0.25;
      const step = clamp(-d / dn, -far, far);
      x += nx * step; y += ny * step; z += nz * step;
    }
    arr[i * 3] = x; arr[i * 3 + 1] = y; arr[i * 3 + 2] = z;
  }
  return arr;
}
// where the points want to go, as one smooth field over the body; then each settles along its normal. F(i): the
// surface (a distance) point i goes onto
export function settle(R, arr, F, ends) {
  const from = Float32Array.from(arr);
  project(R, arr, F, 12);
  const disp = Float32Array.from(arr, (v, i) => v - from[i]);
  smoothField(disp, 3, R.nb, 20);
  for (let i = 0; i < arr.length; i++) arr[i] = from[i] + disp[i];
  normalProject(R, arr, F, 8);
  arr = taubin(arr, R.nb, i => 0.3 + 0.4 * ends[i], 1);
  normalProject(R, arr, F, 4);
  return repair(R, arr, F, from);
}
// where a point was carried too far for its normal to know the way, or a triangle turned over: straighten it there
function repair(R, arr, F, from) {
  const T = R.mesh.triangles, N = R.mesh.N, nb = R.nb, n0 = normalsOf(from, T), H = R.height;
  for (let round = 0; round < 4; round++) {
    const bad = new Uint8Array(N);
    for (let t = 0; t < T.length; t += 3) {
      const a = T[t] * 3, b = T[t + 1] * 3, c = T[t + 2] * 3;
      const ux = arr[b] - arr[a], uy = arr[b + 1] - arr[a + 1], uz = arr[b + 2] - arr[a + 2], vx = arr[c] - arr[a], vy = arr[c + 1] - arr[a + 1], vz = arr[c + 2] - arr[a + 2];
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      const turned = nx * n0[a] + ny * n0[a + 1] + nz * n0[a + 2] < 0;
      const l0 = Math.hypot(from[b] - from[a], from[b + 1] - from[a + 1], from[b + 2] - from[a + 2]) + 1e-6, l1 = Math.hypot(ux, uy, uz);
      if (turned || l1 > 4 * l0 + 0.006 * H) bad[T[t]] = bad[T[t + 1]] = bad[T[t + 2]] = 1;
    }
    for (const i of R.mesh.used) if (!bad[i] && Math.abs(F(i)(arr[i * 3], arr[i * 3 + 1], arr[i * 3 + 2])) > 0.0035 * H) bad[i] = 1;
    let count = 0; for (let i = 0; i < N; i++) count += bad[i];
    if (!count) break;
    const grow = Uint8Array.from(bad); for (let i = 0; i < N; i++) if (bad[i]) for (let q = nb.start[i]; q < nb.start[i + 1]; q++) grow[nb.list[q]] = 1;
    arr = taubin(arr, nb, i => grow[i] ? 1 : 0, 4);
    const sub = []; for (const i of R.mesh.used) if (grow[i]) sub.push(i);
    project(R, arr, F, 10, sub);
  }
  return arr;
}
