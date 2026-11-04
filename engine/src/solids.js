// The body as hair and clothes meet it — the one collision a figure offers (figure.solids()):
// - its head's designed form (src/head/head.js), carried by the Head joint and, below the mouth and in front of the
//   ears, by the Jaw joint — baked once per head into a grid of distances over its rest (trilinear, exact near the
//   surface);
// - the body's own skin (but a designed head's, which its form is) as the frames drew it, between the previous frame
//   and this one: a distance from it by moving least squares over the nearest skin points' normals (smooth where the
//   nearest point changes), how fast the skin there moves (friction), and — deeper in than the skin's points reach — a
//   coarse inside: the bones' capsules inside the skin, which say which way is out.
// Tried and dropped as the contact surface: capsules (round a collarbone one stands over the shoulder like a shelf);
// each bone's skin carried rigidly by its bone (neighbours disagreed where the skin bends between them).
// It is updated once a frame by the figure's step (figure.step), before its simulations, and only read by them: what a
// reader asks at a moment is in a moment it keeps itself, so any number of simulations (hair, clothes) read it at once
// and none changes what another sees.
//   const S = figure.solids();                     // made once, kept on the figure; figure.step updates it
//   S.update(previous, pose, how, dt)               // (the figure's step) how: 'go' | 'jump' (the clip began again: the
//                                                     body is not carried across) | 'reset'; dt: seconds
//   const m = S.moment(u, m?)                       // the solids at a share u of the frame (0: the previous, 1: this);
//   const r = S.rest.moment(0, m?)                  //   S.rest: the same at the figure's rest (its own state, unchanged)
//   S.head: null | {local(m, x, out), world(m, l, out), turn(m, v, out), distance(l), normal(l, out)}
//                                                     (l: a point in the head's rest space)
//   S.skin(m, x, y, z, out, limb?) → distance (metres, negative inside; the skin itself, a reader keeps its own
//                             thickness); out = {n: [3], v: [3], head, limb}: which way is out, the skin's velocity there
//                             (m/s), how much of the skin there is head (0–1), the limb of the skin nearest (src/regions.js
//                             LIMBS: 0 the body, 1 2 the arms, 3 4 the legs); limb: the skin of that limb alone, near it
//                             (a sleeve round its own arm where the body's side is nearer: src/cloth/sim.js), else Infinity
//   S.kept(m, x, y, z, out, ids, at, fresh) → the same, over the skin points it found nearest before, of the nearest one's
//                             limb, but the fingers' (a reader keeps them:
//                             ids, an Int32Array, KN of them from `at`, −1 from the first where none was near), looked for
//                             anew when fresh or none was near: the points move with the skin, so they stay the nearest while the reader does not
//                             slide far along it (cloth, which lies on the skin: src/cloth/sim.js); deeper than the skin's
//                             points reach, as deep as the capsules' surface (not past it: their ends stand out of a bent
//                             knee, and cloth lying there was thrown off it as if deep inside); S.FAR: no skin point
//                             within it, a point is at least that far from the skin (or deep inside)
//   S.among(m, x, y, z, out, ids, ats) → the same over the points several of a reader's keep (ats: where each's begin):
//                             a cloth triangle's middle over its corners'
//   S.carrier(m) → the Head joint's {q, p} at that moment; S.headRest: its rest place; S.jumped: its {q, p} before a jump
//   S.capsules(m) → the inner capsules at that moment [{a, b, ra, rb}] (for drawing)
import { qRot3, qSlerp, clamp, sst } from './math.js';
import { headShares, HEAD_JOINTS } from './head/frame.js';
import { normalsOf } from './mesh.js';
import { fitCapsules } from './capsules.js';
import { regionsOf } from './regions.js';
import { Pose } from './pose.js';

// the skin's points are looked up in cells of 3 cm; a point farther than that from every skin point is not near the
// skin, and is asked of the capsules (inside, deep, or out)
const CELL = 0.03, REACH = CELL * CELL, KN = 8;
// the capsules inside the skin (src/capsules.js): each bone's at the nearest tenth of the skin round it, less CORE — so it
// stands out of the skin nowhere (at the median, round a collarbone one stood 3 cm over the shoulder, and pushed hair
// off it in flaps); only what lies farther in than the skin's points reach is asked of them
const SHARE = 0.1, CORE = 0.005;

export function makeSolids(figure) {
  // (a head without a designed form is met as its skin: a ball fitted to it is too coarse for hair to lie on)
  const rig = figure.rig, sk = rig.skeleton, J = rig.joints, given = figure.body?.head?.shape ?? null, shape = given && !given.ball ? given : null, body = figure.outputs[0], mesh = body.mesh;
  const H = sk.index.Head, JW = sk.index.Jaw;
  const { omega } = headShares(mesh, sk), idx = Uint32Array.from(Array.from(mesh.used).filter(i => !shape || omega[i] < 0.5));
  // (where the head is its designed form, its own shape is its inside: the head's bones' capsules are not the skin's)
  const headBones = new Set(HEAD_JOINTS.map(n => sk.index[n]));
  const caps = fitCapsules(rig, mesh, { fit: SHARE, inset: CORE }).filter(c => !shape || !headBones.has(c.joint)).map(c => ({ ...c, bound: Math.hypot(c.b[0] - c.a[0], c.b[1] - c.a[1], c.b[2] - c.a[2]) / 2 + Math.max(c.ra, c.rb) }));
  // (how much of each skin point is head: a reader may lie in the head's skin as deep as it lay at rest — roots under
  // the scalp — but not in the body's)
  // (and which limb each skin point is: its strongest)
  const R = regionsOf(mesh, rig), limbOf = i => { let m = 0; for (let l = 1; l < 5; l++) if (R.limb[i * 5 + l] > R.limb[i * 5 + m]) m = l; return m; };
  // (and where the fingers are: cloth lies on the hand as a mitten — between fingers thinner than its reach it would
  // be pushed from one side of a finger to the other)
  const fingers = Uint8Array.from(idx, i => R.ends[i] > 0.5 && (limbOf(i) === 1 || limbOf(i) === 2) ? 1 : 0);
  const headOfPoint = Float32Array.from(idx, i => omega[i]), limbs = Uint8Array.from(idx, limbOf), now = stateOf(idx, caps, [H, JW], headOfPoint, limbs, fingers), rest = stateOf(idx, caps, [H, JW], headOfPoint, limbs, fingers);
  const head = shape ? headOf(shape, J, H, JW) : null, restNormals = normalsOf(mesh.positions, mesh.triangles, undefined, mesh.used);
  rest.set(null, null, mesh.positions, restNormals, mesh.positions, restNormals, J, 0);
  const S = {
    head, headRest: [J[H * 3], J[H * 3 + 1], J[H * 3 + 2]], jumped: { q: [0, 0, 0, 1], p: [0, 0, 0] },
    rest: { moment: (u, m) => withCover(rest.moment(u, m), u, 'rest') },
    // (a step: the skin as the previous frame and this one drew it; a jump or a reset: only this one's, unmoving)
    update(previous, pose, how, dt) {
      if (how === 'jump') { const t = now.ends[0][1]; for (let k = 0; k < 4; k++) S.jumped.q[k] = t.q[k]; for (let k = 0; k < 3; k++) S.jumped.p[k] = t.p[k]; }
      const P = body.positions, N = body.normals, still = how !== 'go';
      now.set(still ? pose : previous, pose, still ? P : now.P1, still ? N : now.N1, P, N, J, still ? 0 : dt);
      updates++;
    },
    // the way into this frame's pose from the rest (carried whole by the pelvis to where it is now): a reader that is
    // reset lets what it simulates go along it (clothes: a body put straight into a stride would leave a skirt's hem
    // round a leg it should be inside) — {pose (the rest so carried), moment(u, m)}, the skin still at both ends
    entry(pose) {
      if (entryOf !== updates) {
        const Hq = [pose.Q[H0 * 4], pose.Q[H0 * 4 + 1], pose.Q[H0 * 4 + 2], pose.Q[H0 * 4 + 3]], o = [0, 0, 0], E = entryPose, R0 = mesh.positions;
        for (let j = 0; j < rig.J; j++) { for (let k = 0; k < 4; k++) E.Q[j * 4 + k] = Hq[k]; qRot3(Hq, J[j * 3] - J[H0 * 3], J[j * 3 + 1] - J[H0 * 3 + 1], J[j * 3 + 2] - J[H0 * 3 + 2], o); for (let k = 0; k < 3; k++) E.P[j * 3 + k] = pose.P[H0 * 3 + k] + o[k]; }
        for (const i of mesh.used) { qRot3(Hq, R0[i * 3] - J[H0 * 3], R0[i * 3 + 1] - J[H0 * 3 + 1], R0[i * 3 + 2] - J[H0 * 3 + 2], o); for (let k = 0; k < 3; k++) entryP[i * 3 + k] = pose.P[H0 * 3 + k] + o[k]; qRot3(Hq, restNormals[i * 3], restNormals[i * 3 + 1], restNormals[i * 3 + 2], o); for (let k = 0; k < 3; k++) entryN[i * 3 + k] = o[k]; }
        enter.set(E, pose, entryP, entryN, body.positions, body.normals, J, 0); entryOf = updates;
      }
      return { pose: entryPose, moment: (u, m) => enter.moment(u, m) };
    },
    moment: (u, m) => withCover(now.moment(u, m), u, 'now'),
    // clothes over the body, as what lies on them meets them (hair over a collar): their simulation gives their surface
    // at its rest and at each frame's end (cover.rest(P, N), cover.update(P, N, how, dt) — after the body's update, before
    // hair reads it); S.over(m, x, y, z, out) → the distance from it at moment m (as S.skin: out = {n, v}), Infinity
    // where none of it is near
    cover(n) {
      if (covers) throw new Error('a figure has one cover (all its clothes, src/cloth/sim.js)');
      const ids = Uint32Array.from({ length: n }, (_, i) => i);
      covers = { now: stateOf(ids, [], [], null, null), rest: stateOf(ids, [], [], null, null) };
      return {
        rest(P, N) { covers.rest.set(null, null, P, N, P, N, J, 0); covers.now.set(null, null, P, N, P, N, J, 0); },
        update(P, N, how, dt) { const still = how !== 'go', c = covers.now; c.set(null, null, still ? P : c.P1, still ? N : c.N1, P, N, J, still ? 0 : dt); },
      };
    },
    over: (m, x, y, z, out) => m.cover ? m.cover.state.skin(m.cover, x, y, z, out) : Infinity,
    skin: (m, x, y, z, out, limb = -1) => m.state.skin(m, x, y, z, out, limb),
    kept: (m, x, y, z, out, ids, at, fresh) => m.state.kept(m, x, y, z, out, ids, at, fresh), KN, FAR: CELL,
    among: (m, x, y, z, out, ids, ats) => m.state.among(m, x, y, z, out, ids, ats),
    carrier: m => m.joints[0],
    capsules: m => m.state.capsulesAt(m.u),
  };
  let covers = null, updates = 0, entryOf = -1;
  const H0 = sk.index.Hips, entryPose = new Pose(rig.J), entryP = new Float32Array(mesh.N * 3), entryN = new Float32Array(mesh.N * 3), enter = stateOf(idx, caps, [H, JW], headOfPoint, limbs, fingers);
  // a moment of the cover beside a moment of the body (made when there is a cover)
  const withCover = (m, u, which) => { if (covers) m.cover = covers[which].moment(u, m.cover); return m; };
  // (made after a step: as that step left the figure; before any: at rest)
  if (figure.state) S.update(figure.pose, figure.pose, 'reset', 0);
  else now.set(null, null, mesh.positions, restNormals, mesh.positions, restNormals, J, 0);
  return S;
}

// the solids between two frames: the joints the head rides, the skin's points and normals, the capsules — at both
// ends. A moment (made and kept by its reader) holds the joints at its share u of the frame, and — once the skin is
// asked of it — the skin's points there in a hash of 3 cm cells
function stateOf(idx, caps, joints, HP, LP, FP = null) {
  const n = idx.length, P0 = new Float32Array(n * 3), P1 = new Float32Array(n * 3), N0 = new Float32Array(n * 3), N1 = new Float32Array(n * 3), V = new Float32Array(n * 3);
  const ends = joints.map(() => [tr(), tr()]), C = caps.map(c => ({ ...c, a0: [0, 0, 0], b0: [0, 0, 0], a1: [0, 0, 0], b1: [0, 0, 0] }));
  let version = 0;
  const st = {
    ends, P1, N1,
    // positions and normals at the frame's two ends (the body's skin as drawn, by its vertex indices), the poses at
    // both ends (null: the rig's rest), the skin's velocity over dt (0: unmoving)
    set(pose0, pose1, A, AN, B, BN, rigJoints, dt) {
      // (A may be this state's own P1: read it before writing)
      for (let k = 0; k < n; k++) {
        const i = idx[k];
        for (let c = 0; c < 3; c++) {
          const a = A === P1 ? P1[k * 3 + c] : A[i * 3 + c], an = AN === N1 ? N1[k * 3 + c] : AN[i * 3 + c];
          P0[k * 3 + c] = a; N0[k * 3 + c] = an; P1[k * 3 + c] = B[i * 3 + c]; N1[k * 3 + c] = BN[i * 3 + c];
          V[k * 3 + c] = dt > 0 ? (P1[k * 3 + c] - a) / dt : 0;
        }
      }
      joints.forEach((j, e) => { grab(pose0, rigJoints, j, ends[e][0]); grab(pose1, rigJoints, j, ends[e][1]); });
      for (const c of C) { carried(pose0, c, c.a, c.a0, rigJoints); carried(pose1, c, c.a, c.a1, rigJoints); carried(pose0, c, c.b, c.b0, rigJoints); carried(pose1, c, c.b, c.b1, rigJoints); }
      version++;
    },
    // the moment u: the joints there (slerped); its skin made when first asked (m.skinOf: the version and u it was made for)
    moment(u, m = { state: null, u: 0, joints: joints.map(tr), P: null, N: null, hash: null, skinOf: null }) {
      m.state = st; m.u = u; m.skinOf = null;
      for (let e = 0; e < joints.length; e++) { const [a, b] = ends[e], o = m.joints[e]; qSlerp(a.q, b.q, u, o.q); o.qi[0] = -o.q[0]; o.qi[1] = -o.q[1]; o.qi[2] = -o.q[2]; o.qi[3] = o.q[3]; for (let k = 0; k < 3; k++) o.p[k] = a.p[k] + (b.p[k] - a.p[k]) * u; }
      return m;
    },
    // the skin's points and normals at m's moment; the capsules there (each its ends, its middle); their hash when a
    // search needs it
    skinAt(m) {
      if (m.skinOf === version) return;
      const u = m.u, P = m.P ??= new Float32Array(n * 3), N = m.N ??= new Float32Array(n * 3), K = m.C ??= new Float64Array(C.length * 9);
      for (let i = 0; i < n * 3; i++) { P[i] = P0[i] + (P1[i] - P0[i]) * u; N[i] = N0[i] + (N1[i] - N0[i]) * u; }
      C.forEach((c, k) => { for (let j = 0; j < 3; j++) { const a = c.a0[j] + (c.a1[j] - c.a0[j]) * u, b = c.b0[j] + (c.b1[j] - c.b0[j]) * u; K[k * 9 + j] = a; K[k * 9 + 3 + j] = b; K[k * 9 + 6 + j] = (a + b) / 2; } });
      m.skinOf = version; m.hashed = false;
    },
    hashAt(m) { if (!m.hashed) { (m.hash ??= cellHash()).build(n, m.P); m.hashed = true; } return m.hash; },
    skin(m, x, y, z, out, limb = -1) {
      st.skinAt(m);
      const d = nearest(m.P, m.N, V, st.hashAt(m), x, y, z, out, HP, LP, limb);
      return d === Infinity && limb < 0 ? st.deep(m.C, x, y, z, out) : d;
    },
    // the same, over the skin points a reader found nearest before (ids, at: KN of them kept from `at`), found anew when
    // `fresh` (or none were): the skin's points move with it, so between searches they stay the nearest ones but where
    // the reader slides along the skin
    kept(m, x, y, z, out, ids, at, fresh) {
      st.skinAt(m);
      let d;
      // (none was near when last looked: looked for again — the reader asks because the skin may have come near)
      if (fresh || ids[at] < 0) {
        // (only the limb's of the nearest: between two legs, or an arm and the side, the nearest one's skin alone says
        // which way is out — both together would push sideways, through one of them)
        nearest(m.P, m.N, V, st.hashAt(m), x, y, z, out, HP, LP, -1, FP);
        const bi = out.bi, l = bi[0] >= 0 ? LP[bi[0]] : -1; let k = 0;
        for (let q = 0; q < KN; q++) if (bi[q] >= 0 && LP[bi[q]] === l) ids[at + k++] = bi[q];
        for (; k < KN; k++) ids[at + k] = -1;
        d = ids[at] < 0 ? Infinity : nearOf(m.P, m.N, V, ids, [at], x, y, z, out, HP, LP);
      }
      else d = nearOf(m.P, m.N, V, ids, [at], x, y, z, out, HP, LP);
      return d === Infinity ? st.deep(m.C, x, y, z, out, 0) : d;
    },
    // over the skin points several readers keep (a triangle's middle, over its corners'): the nearest of them all
    among(m, x, y, z, out, ids, ats) { st.skinAt(m); return nearOf(m.P, m.N, V, ids, ats, x, y, z, out, HP, LP); },
    // farther than the skin's points reach: inside a capsule (deep in the body: as deep as the capsule's surface lies
    // under the point, plus `beyond` — the reach: at least that far in), else out of reach (Infinity); K: the capsules
    // at the moment
    deep(K, x, y, z, out, beyond = Math.sqrt(REACH)) {
      let best = Infinity;
      for (let k = 0; k < C.length; k++) {
        const c = C[k], o = k * 9, mx = K[o + 6] - x, my = K[o + 7] - y, mz = K[o + 8] - z;
        // (its bounding sphere first)
        if (mx * mx + my * my + mz * mz > c.bound * c.bound) continue;
        const ax = K[o], ay = K[o + 1], az = K[o + 2], ex = K[o + 3] - ax, ey = K[o + 4] - ay, ez = K[o + 5] - az, L2 = ex * ex + ey * ey + ez * ez || 1e-12, t = clamp(((x - ax) * ex + (y - ay) * ey + (z - az) * ez) / L2, 0, 1);
        const px = x - ax - ex * t, py = y - ay - ey * t, pz = z - az - ez * t, l = Math.hypot(px, py, pz), d = l - (c.ra + (c.rb - c.ra) * t);
        if (d < best) { best = d; if (l > 1e-9) { out.n[0] = px / l; out.n[1] = py / l; out.n[2] = pz / l; } else { out.n[0] = 0; out.n[1] = 1; out.n[2] = 0; } }
      }
      if (best >= 0) return Infinity;
      out.v[0] = out.v[1] = out.v[2] = 0; out.head = 0; out.limb = 0;
      return best - beyond;
    },
    capsulesAt(u) { return C.map(c => ({ joint: c.joint, ra: c.ra, rb: c.rb, a: c.a0.map((v, k) => v + (c.a1[k] - v) * u), b: c.b0.map((v, k) => v + (c.b1[k] - v) * u) })); },
  };
  return st;
}
const tr = () => ({ q: [0, 0, 0, 1], qi: [0, 0, 0, 1], p: [0, 0, 0] });
// a joint's turn and place in a pose (null: at the rig's rest — unturned, where the rig has it)
function grab(pose, J, j, o) {
  if (!pose) { o.q[0] = o.q[1] = o.q[2] = 0; o.q[3] = 1; for (let k = 0; k < 3; k++) o.p[k] = J[j * 3 + k]; return; }
  for (let k = 0; k < 4; k++) o.q[k] = pose.Q[j * 4 + k]; for (let k = 0; k < 3; k++) o.p[k] = pose.P[j * 3 + k];
}
// a capsule's end (rest place x) carried by its joint in a pose
function carried(pose, c, x, out, J) {
  if (!pose) { out[0] = x[0]; out[1] = x[1]; out[2] = x[2]; return; }
  const j = c.joint, q = [pose.Q[j * 4], pose.Q[j * 4 + 1], pose.Q[j * 4 + 2], pose.Q[j * 4 + 3]];
  qRot3(q, x[0] - J[j * 3], x[1] - J[j * 3 + 1], x[2] - J[j * 3 + 2], out); out[0] += pose.P[j * 3]; out[1] += pose.P[j * 3 + 1]; out[2] += pose.P[j * 3 + 2];
}

// the distance from a skin given by its points and normals (P, N; V their velocities, or null), in its hash: moving least
// squares over the nearest KN points' planes, weighed by nearness (smooth where the nearest point changes); beyond REACH
// of every point, Infinity. out: {n, v, head, limb} which way is out, how fast the skin moves there, how much of it is
// head (HP) and the nearest point's limb (LP); limb ≥ 0: that limb's points alone
function nearest(P, N, V, hash, x, y, z, out, HP = null, LP = null, limb = -1, skip = null) {
  const items = hash.items, start = hash.start, bi = out.bi ??= new Int32Array(KN), bd = out.bd ??= new Float64Array(KN);
  bi.fill(-1); bd.fill(Infinity);
  // (the cells round the point's own, but those farther than the reach from it)
  const cx = Math.floor(x / CELL), cy = Math.floor(y / CELL), cz = Math.floor(z / CELL), fx = x / CELL - cx, fy = y / CELL - cy, fz = z / CELL - cz;
  const gap = (f, a) => a < 0 ? f : a > 0 ? 1 - f : 0;
  for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
    if ((gap(fx, a) ** 2 + gap(fy, b) ** 2 + gap(fz, c) ** 2) * CELL * CELL > REACH) continue;
    const h = bucket(cx + a, cy + b, cz + c);
    for (let e = start[h], end = start[h + 1]; e < end; e++) {
      if ((limb >= 0 && LP[items[e]] !== limb) || (skip && skip[items[e]])) continue;
      const k3 = items[e] * 3, d = (P[k3] - x) ** 2 + (P[k3 + 1] - y) ** 2 + (P[k3 + 2] - z) ** 2; if (d >= bd[KN - 1] || d > REACH) continue;
      let q = KN - 1; while (q > 0 && bd[q - 1] > d) { bd[q] = bd[q - 1]; bi[q] = bi[q - 1]; q--; } bd[q] = d; bi[q] = items[e];
    }
  }
  return planes(P, N, V, bi, bd, x, y, z, out, HP, LP);
}
// the same over KN points kept (ids from each of `ats`, KN from each — −1 where fewer: the nearest KN of them all), as
// near as they are now
function nearOf(P, N, V, ids, ats, x, y, z, out, HP, LP) {
  const bi = out.bi ??= new Int32Array(KN), bd = out.bd ??= new Float64Array(KN);
  let n = 0;
  for (const at of ats) for (let q = 0; q < KN; q++) {
    const k = ids[at + q]; if (k < 0) break;
    let dup = false; for (let r = 0; r < n; r++) if (bi[r] === k) dup = true; if (dup) continue;
    const k3 = k * 3, d = (P[k3] - x) ** 2 + (P[k3 + 1] - y) ** 2 + (P[k3 + 2] - z) ** 2;
    if (n === KN && d >= bd[KN - 1]) continue;
    let r = n < KN ? n++ : KN - 1; while (r > 0 && bd[r - 1] > d) { bd[r] = bd[r - 1]; bi[r] = bi[r - 1]; r--; } bd[r] = d; bi[r] = k;
  }
  for (let q = n; q < KN; q++) { bi[q] = -1; bd[q] = Infinity; }
  if (bd[0] > REACH) { bi[0] = -1; }
  return planes(P, N, V, bi, bd, x, y, z, out, HP, LP);
}
// moving least squares over the points bi (bd their squared distances, nearest first)
function planes(P, N, V, bi, bd, x, y, z, out, HP, LP) {
  if (bi[0] < 0) { out.head = 0; return Infinity; }
  out.head = HP ? HP[bi[0]] : 0; out.limb = LP ? LP[bi[0]] : 0;
  const h2 = Math.max(bd[0], 1e-6) * 4 + 1e-5; let sw = 0, sd = 0, nx = 0, ny = 0, nz = 0, vx = 0, vy = 0, vz = 0;
  for (let q = 0; q < KN; q++) {
    // (fading to nothing at the reach: a point as far from the skin as that, its nearest points coming into reach and
    // leaving it, read inside and out a step at a time — an oversized sweater standing that far off, a flicker of 9 mm)
    const k = bi[q]; if (k < 0) break; const k3 = k * 3, w = Math.exp(-bd[q] / h2) * Math.max(0, 1 - bd[q] / REACH) ** 2;
    sw += w; sd += w * ((x - P[k3]) * N[k3] + (y - P[k3 + 1]) * N[k3 + 1] + (z - P[k3 + 2]) * N[k3 + 2]);
    nx += w * N[k3]; ny += w * N[k3 + 1]; nz += w * N[k3 + 2]; if (V) { vx += w * V[k3]; vy += w * V[k3 + 1]; vz += w * V[k3 + 2]; }
  }
  if (!(sw > 1e-12)) return Infinity;
  const l = Math.hypot(nx, ny, nz) || 1; out.n[0] = nx / l; out.n[1] = ny / l; out.n[2] = nz / l; out.v[0] = vx / sw; out.v[1] = vy / sw; out.v[2] = vz / sw;
  return sd / sw;
}
// a still surface's distance (points and normals, n×3): (x, y, z) → metres, negative inside; Infinity beyond 3 cm of it
export function surfaceDistance(P, N) {
  const hash = cellHash(), out = { n: [0, 0, 0], v: [0, 0, 0] }; hash.build(P.length / 3, P);
  return (x, y, z) => nearest(P, N, null, hash, x, y, z, out);
}

// a hash of cells: each skin point in the cell it lies in (counting sort into flat arrays, kept and grown — nothing made
// anew each frame); a bucket may hold more than one cell (the distances tell them apart)
const BUCKETS = 1 << 15, bucket = (a, b, c) => (((a * 73856093) ^ (b * 19349663) ^ (c * 83492791)) >>> 0) & (BUCKETS - 1);
function cellHash() {
  const start = new Int32Array(BUCKETS + 1), fill = new Int32Array(BUCKETS + 1), key = new Int32Array(0), h = { start, items: new Int32Array(0), key };
  h.build = (n, P) => {
    if (h.key.length < n) { h.key = new Int32Array(n); h.items = new Int32Array(n); }
    start.fill(0);
    for (let k = 0; k < n; k++) { const b = bucket(Math.floor(P[k * 3] / CELL), Math.floor(P[k * 3 + 1] / CELL), Math.floor(P[k * 3 + 2] / CELL)); h.key[k] = b; start[b + 1]++; }
    for (let b = 0; b < BUCKETS; b++) start[b + 1] += start[b];
    fill.set(start);
    for (let k = 0; k < n; k++) h.items[fill[h.key[k]]++] = k;
  };
  return h;
}

// the head's shape in its rest space: a point carried there by the Head joint and, below the mouth and in front of the
// ears, by the Jaw joint (blended); carried out by the Head joint (the jaw's small part with it). A moment's joints:
// [Head, Jaw].
function headOf(shape, J, H, JW) {
  const F = shape.frame, { y: jy, z: jz } = shape.jaw;
  const back = (st, j, x, o) => { qRot3(st.qi, x[0] - st.p[0], x[1] - st.p[1], x[2] - st.p[2], o); o[0] += J[j * 3]; o[1] += J[j * 3 + 1]; o[2] += J[j * 3 + 2]; return o; };
  const grid = cached(shape, () => gridOf((x, y, z) => shape.sdf((x - F.O[0]) / F.R, (y - F.O[1]) / F.R, (z - F.O[2]) / F.R) * F.R,
    [F.O[0] - 1.9 * F.R, F.O[1] - 2.3 * F.R, F.O[2] - 1.9 * F.R], [F.O[0] + 1.9 * F.R, F.O[1] + 1.9 * F.R, F.O[2] + 1.9 * F.R], 0.045 * F.R));
  return {
    local(m, x, out) {
      const jj = out.jj ??= [0, 0, 0]; back(m.joints[0], H, x, out);
      const hy = (out[1] - F.O[1]) / F.R, hz = (out[2] - F.O[2]) / F.R, w = sst(clamp((jy - hy) / 0.15, 0, 1)) * sst(clamp((hz - jz) / 0.3, 0, 1));
      if (w) { back(m.joints[1], JW, x, jj); for (let k = 0; k < 3; k++) out[k] += (jj[k] - out[k]) * w; }
      return out;
    },
    world(m, l, out) { const st = m.joints[0]; qRot3(st.q, l[0] - J[H * 3], l[1] - J[H * 3 + 1], l[2] - J[H * 3 + 2], out); out[0] += st.p[0]; out[1] += st.p[1]; out[2] += st.p[2]; return out; },
    turn: (m, v, out) => qRot3(m.joints[0].q, v[0], v[1], v[2], out),
    distance: l => grid.at(l[0], l[1], l[2]),
    normal: (l, out) => grid.normal(l[0], l[1], l[2], out),
  };
}

const CACHE = new WeakMap(), cached = (key, make) => { if (!CACHE.has(key)) CACHE.set(key, make()); return CACHE.get(key); };
// a distance f(x, y, z) (metres) on a grid from lo to hi, h apart: coarse everywhere, exact near the surface; outside
// the grid at least as far as its edge
function gridOf(f, lo, hi, h) {
  const n = [0, 1, 2].map(c => Math.ceil((hi[c] - lo[c]) / h) + 1), D = new Float32Array(n[0] * n[1] * n[2]);
  const at = (i, j, k) => i + n[0] * (j + n[1] * k);
  const C = 4, far = C * h * 1.8;
  for (let k = 0; k < n[2]; k += C) for (let j = 0; j < n[1]; j += C) for (let i = 0; i < n[0]; i += C) D[at(i, j, k)] = f(lo[0] + i * h, lo[1] + j * h, lo[2] + k * h);
  for (let k = 0; k < n[2]; k++) for (let j = 0; j < n[1]; j++) for (let i = 0; i < n[0]; i++) {
    if (i % C === 0 && j % C === 0 && k % C === 0) continue;
    // the coarse corners round it: far from the surface their blend is enough, near it the distance itself
    const i0 = Math.min(Math.floor(i / C) * C, n[0] - 1), j0 = Math.min(Math.floor(j / C) * C, n[1] - 1), k0 = Math.min(Math.floor(k / C) * C, n[2] - 1);
    const i1 = Math.min(i0 + C, Math.floor((n[0] - 1) / C) * C), j1 = Math.min(j0 + C, Math.floor((n[1] - 1) / C) * C), k1 = Math.min(k0 + C, Math.floor((n[2] - 1) / C) * C);
    let mn = Infinity, s = 0, c = 0;
    for (const a of [i0, i1]) for (const b of [j0, j1]) for (const e of [k0, k1]) { const v = D[at(a, b, e)]; mn = Math.min(mn, Math.abs(v)); s += v; c++; }
    D[at(i, j, k)] = mn < far ? f(lo[0] + i * h, lo[1] + j * h, lo[2] + k * h) : s / c;
  }
  const g = {
    at(x, y, z) {
      const u = clamp((x - lo[0]) / h, 0, n[0] - 1.001), v = clamp((y - lo[1]) / h, 0, n[1] - 1.001), w = clamp((z - lo[2]) / h, 0, n[2] - 1.001);
      const i = Math.floor(u), j = Math.floor(v), k = Math.floor(w), a = u - i, b = v - j, c = w - k, q = at(i, j, k), sx = 1, sy = n[0], sz = n[0] * n[1];
      const x00 = D[q] + (D[q + sx] - D[q]) * a, x10 = D[q + sy] + (D[q + sy + sx] - D[q + sy]) * a, x01 = D[q + sz] + (D[q + sz + sx] - D[q + sz]) * a, x11 = D[q + sz + sy] + (D[q + sz + sy + sx] - D[q + sz + sy]) * a;
      const inside = (x00 + (x10 - x00) * b) + ((x01 + (x11 - x01) * b) - (x00 + (x10 - x00) * b)) * c;
      // (outside the grid: at least as far as its edge)
      const ox = Math.max(lo[0] - x, 0, x - lo[0] - (n[0] - 1) * h), oy = Math.max(lo[1] - y, 0, y - lo[1] - (n[1] - 1) * h), oz = Math.max(lo[2] - z, 0, z - lo[2] - (n[2] - 1) * h);
      return inside + Math.hypot(ox, oy, oz);
    },
    normal(x, y, z, out) {
      const e = h * 0.5; out[0] = g.at(x + e, y, z) - g.at(x - e, y, z); out[1] = g.at(x, y + e, z) - g.at(x, y - e, z); out[2] = g.at(x, y, z + e) - g.at(x, y, z - e);
      const l = Math.hypot(out[0], out[1], out[2]) || 1; out[0] /= l; out[1] /= l; out[2] /= l; return out;
    },
  };
  return g;
}
