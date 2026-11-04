// The body as hair and clothes meet it — the one collision a figure offers (figure.solids()):
// - its head's designed form (src/head/head.js), carried by the Head joint and, below the mouth and in front of the
//   ears, by the Jaw joint — baked once per head into a grid of distances over its rest (trilinear, exact near the
//   surface);
// - the body's own skin (but a designed head's, which its form is) as the frames drew it, between the previous frame
//   and this one: a distance from it by moving least squares over the nearest skin points' normals (smooth where the
//   nearest point changes), how fast the skin there moves (friction), and — deeper in than the skin's points reach — a
//   coarse inside: the bones' capsules shrunk inside the skin, which say which way is out.
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
//   S.skin(m, x, y, z, out) → distance (metres, negative inside; the skin itself, a reader keeps its own thickness);
//                             out = {n: [3], v: [3]}: which way is out, and the skin's velocity there (m/s)
//   S.carrier(m) → the Head joint's {q, p} at that moment; S.headRest: its rest place; S.jumped: its {q, p} before a jump
//   S.capsules(m) → the inner capsules at that moment [{a, b, ra, rb}] (for drawing)
import { qRot3, qSlerp, clamp, sst } from './math.js';
import { headShares } from './head/frame.js';
import { normalsOf } from './mesh.js';
import { fitCapsules } from './capsules.js';

// the skin's points are looked up in cells of 3 cm; a point farther than that from every skin point is not near the
// skin, and is asked of the capsules (inside, deep, or out)
const CELL = 0.03, REACH = CELL * CELL, KN = 8;
// the capsules inside the skin (src/capsules.js): each bone's at the skin's median distance round it, less this (so it
// never stands out of the skin, where the skin is thinner than its median — round a collarbone)
const CORE = 0.012;

export function makeSolids(figure) {
  // (a head without a designed form is met as its skin: a ball fitted to it is too coarse for hair to lie on)
  const rig = figure.rig, sk = rig.skeleton, J = rig.joints, given = figure.body?.head?.shape ?? null, shape = given && !given.ball ? given : null, body = figure.outputs[0], mesh = body.mesh;
  const H = sk.index.Head, JW = sk.index.Jaw;
  const { omega } = headShares(mesh, sk), idx = Uint32Array.from(Array.from(mesh.used).filter(i => !shape || omega[i] < 0.5));
  const caps = fitCapsules(rig, mesh, { inset: CORE }).map(c => ({ ...c, bound: Math.hypot(c.b[0] - c.a[0], c.b[1] - c.a[1], c.b[2] - c.a[2]) / 2 + Math.max(c.ra, c.rb) }));
  const now = stateOf(idx, caps, [H, JW]), rest = stateOf(idx, caps, [H, JW]);
  const head = shape ? headOf(shape, J, H, JW) : null, restNormals = normalsOf(mesh.positions, mesh.triangles, undefined, mesh.used);
  rest.set(null, null, mesh.positions, restNormals, mesh.positions, restNormals, J, 0);
  const S = {
    head, headRest: [J[H * 3], J[H * 3 + 1], J[H * 3 + 2]], jumped: { q: [0, 0, 0, 1], p: [0, 0, 0] },
    rest: { moment: (u, m) => rest.moment(u, m) },
    // (a step: the skin as the previous frame and this one drew it; a jump or a reset: only this one's, unmoving)
    update(previous, pose, how, dt) {
      if (how === 'jump') { const t = now.ends[0][1]; for (let k = 0; k < 4; k++) S.jumped.q[k] = t.q[k]; for (let k = 0; k < 3; k++) S.jumped.p[k] = t.p[k]; }
      const P = body.positions, N = body.normals, still = how !== 'go';
      now.set(still ? pose : previous, pose, still ? P : now.P1, still ? N : now.N1, P, N, J, still ? 0 : dt);
    },
    moment: (u, m) => now.moment(u, m),
    skin: (m, x, y, z, out) => m.state.skin(m, x, y, z, out),
    carrier: m => m.joints[0],
    capsules: m => m.state.capsulesAt(m.u),
  };
  // (made after a step: as that step left the figure; before any: at rest)
  if (figure.state) S.update(figure.pose, figure.pose, 'reset', 0);
  else now.set(null, null, mesh.positions, restNormals, mesh.positions, restNormals, J, 0);
  return S;
}

// the solids between two frames: the joints the head rides, the skin's points and normals, the capsules — at both
// ends. A moment (made and kept by its reader) holds the joints at its share u of the frame, and — once the skin is
// asked of it — the skin's points there in a hash of 3 cm cells
function stateOf(idx, caps, joints) {
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
    // the skin's points and normals at m's moment, in its hash
    skinAt(m) {
      if (m.skinOf === version) return;
      const u = m.u, P = m.P ??= new Float32Array(n * 3), N = m.N ??= new Float32Array(n * 3);
      for (let i = 0; i < n * 3; i++) { P[i] = P0[i] + (P1[i] - P0[i]) * u; N[i] = N0[i] + (N1[i] - N0[i]) * u; }
      (m.hash ??= cellHash()).build(n, P);
      m.skinOf = version;
    },
    skin(m, x, y, z, out) {
      st.skinAt(m);
      const P = m.P, N = m.N, hash = m.hash, items = hash.items, start = hash.start;
      const bi = out.bi ??= new Int32Array(KN), bd = out.bd ??= new Float64Array(KN);
      bi.fill(-1); bd.fill(Infinity);
      const cx = Math.floor(x / CELL), cy = Math.floor(y / CELL), cz = Math.floor(z / CELL);
      for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
        const h = bucket(cx + a, cy + b, cz + c);
        for (let e = start[h], end = start[h + 1]; e < end; e++) {
          const k3 = items[e] * 3, d = (P[k3] - x) ** 2 + (P[k3 + 1] - y) ** 2 + (P[k3 + 2] - z) ** 2; if (d >= bd[KN - 1] || d > REACH) continue;
          let q = KN - 1; while (q > 0 && bd[q - 1] > d) { bd[q] = bd[q - 1]; bi[q] = bi[q - 1]; q--; } bd[q] = d; bi[q] = items[e];
        }
      }
      if (bi[0] < 0) return st.deep(m.u, x, y, z, out);
      const h2 = Math.max(bd[0], 1e-6) * 4 + 1e-5; let sw = 0, sd = 0, nx = 0, ny = 0, nz = 0, vx = 0, vy = 0, vz = 0;
      for (let q = 0; q < KN; q++) {
        const k = bi[q]; if (k < 0) break; const k3 = k * 3, w = Math.exp(-bd[q] / h2);
        sw += w; sd += w * ((x - P[k3]) * N[k3] + (y - P[k3 + 1]) * N[k3 + 1] + (z - P[k3 + 2]) * N[k3 + 2]);
        nx += w * N[k3]; ny += w * N[k3 + 1]; nz += w * N[k3 + 2]; vx += w * V[k3]; vy += w * V[k3 + 1]; vz += w * V[k3 + 2];
      }
      const l = Math.hypot(nx, ny, nz) || 1; out.n[0] = nx / l; out.n[1] = ny / l; out.n[2] = nz / l; out.v[0] = vx / sw; out.v[1] = vy / sw; out.v[2] = vz / sw;
      return sd / sw;
    },
    // farther than the skin's points reach: inside a capsule (deep in the body: as deep as the capsule's surface lies
    // under the point, plus the reach — at least that far in), else out of reach (Infinity)
    deep(u, x, y, z, out) {
      let best = Infinity, bc = null;
      for (const c of C) {
        const ax = c.a0[0] + (c.a1[0] - c.a0[0]) * u, ay = c.a0[1] + (c.a1[1] - c.a0[1]) * u, az = c.a0[2] + (c.a1[2] - c.a0[2]) * u;
        const bx = c.b0[0] + (c.b1[0] - c.b0[0]) * u, by = c.b0[1] + (c.b1[1] - c.b0[1]) * u, bz = c.b0[2] + (c.b1[2] - c.b0[2]) * u;
        // (its bounding sphere first)
        const mx = (ax + bx) / 2 - x, my = (ay + by) / 2 - y, mz = (az + bz) / 2 - z; if (mx * mx + my * my + mz * mz > c.bound * c.bound) continue;
        const ex = bx - ax, ey = by - ay, ez = bz - az, L2 = ex * ex + ey * ey + ez * ez || 1e-12, t = clamp(((x - ax) * ex + (y - ay) * ey + (z - az) * ez) / L2, 0, 1);
        const px = x - ax - ex * t, py = y - ay - ey * t, pz = z - az - ez * t, l = Math.hypot(px, py, pz), d = l - (c.ra + (c.rb - c.ra) * t);
        if (d < best) { best = d; bc = c; if (l > 1e-9) { out.n[0] = px / l; out.n[1] = py / l; out.n[2] = pz / l; } else { out.n[0] = 0; out.n[1] = 1; out.n[2] = 0; } }
      }
      if (best >= 0) return Infinity;
      out.v[0] = out.v[1] = out.v[2] = 0;
      return best - Math.sqrt(REACH);
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
