// The body as hair (and, later, clothes) meet it — one set of solids a figure offers:
// - its head's shape (the designed form, or a ball fitted to the head: src/head/head.js), carried by the Head joint
//   and, below the mouth, by the Jaw joint (figure.headShape's split) — baked once per head into a grid of distances over
//   its rest (trilinear, refined near the surface);
// - the body's own skin as it is drawn this frame (but the head's, which the head's shape is): a distance from it —
//   moving least squares over the nearest skin points' normals, so it is smooth where the nearest point changes — and
//   how fast the skin there moves (for friction). Capsules round the bones were tried first: round a collarbone one
//   stands over the shoulder like a shelf; each bone's skin carried rigidly by its bone disagreed with its neighbours'
//   where the skin bends between them, and pushed the hair centimetres in a step.
// A simulation's frame runs in small steps from the previous pose to this one: set(previous, pose) once a frame (the
// skin as this frame drew it), at(u) at each small step (u from 0 to 1) for the head; the state a step ago kept, so a
// point lying on a solid can be carried by its motion.
//   const S = figure.solids();           // once (kept on the figure)
//   S.set(previous, pose, fresh?); S.at(u);       // each frame, each small step;  S.rest() — the figure at its rest
//   S.head: null | {local(x, out), was(x, out), world(l, out), turn(v, out), distance(l), normal(l, out)}
//   S.skin(x, y, z, out) → distance (metres, negative inside; beyond 3 cm of the skin: Infinity), out: {n, v} its
//     normal and the skin's velocity there (metres a frame's step, set by set())
//   S.carrier: the Head joint's {now, was: {q, p}, rest}
import { qRot3, qSlerp, clamp, sst } from './math.js';
import { headShares } from './head/frame.js';
import { normalsOf } from './mesh.js';

// the bones whose skin is a solid of its own
const SKIN_PARTS = ['Spine1', 'Spine2', 'Chest', 'Neck1', 'Neck2', 'LeftShoulder', 'RightShoulder', 'LeftArm', 'RightArm'];

export function makeSolids(figure) {
  const rig = figure.rig, sk = rig.skeleton, J = rig.joints, shape = figure.body?.head?.shape ?? null, body = figure.outputs[0], mesh = body.mesh;
  const H = sk.index.Head, JW = sk.index.Jaw;
  // each joint the head rides: its turn and place from the rest, at the frame's two ends, now and a step ago
  const tr = () => ({ q: [0, 0, 0, 1], qi: [0, 0, 0, 1], p: [0, 0, 0] }), joints = [H, JW];
  const T = Object.fromEntries(joints.map(j => [j, { ends: [tr(), tr()], now: tr(), was: tr() }]));
  const grab = (pose, j, o) => { for (let k = 0; k < 4; k++) o.q[k] = pose.Q[j * 4 + k]; o.qi[0] = -o.q[0]; o.qi[1] = -o.q[1]; o.qi[2] = -o.q[2]; o.qi[3] = o.q[3]; for (let k = 0; k < 3; k++) o.p[k] = pose.P[j * 3 + k]; };
  const lerpT = (a, b, u, o) => { const q = qSlerp(a.q, b.q, u); for (let k = 0; k < 4; k++) o.q[k] = q[k]; o.qi[0] = -q[0]; o.qi[1] = -q[1]; o.qi[2] = -q[2]; o.qi[3] = q[3]; for (let k = 0; k < 3; k++) o.p[k] = a.p[k] + (b.p[k] - a.p[k]) * u; };
  const copyT = (a, o) => { for (let k = 0; k < 4; k++) { o.q[k] = a.q[k]; o.qi[k] = a.qi[k]; } for (let k = 0; k < 3; k++) o.p[k] = a.p[k]; };
  const head = shape ? headOf(shape, J, H, JW, T) : null;
  const skin = skinOf(mesh, sk, !!shape);
  const S = {
    head,
    // the Head joint's turn and place now and a step ago (what carries a hairstyle), and its rest place
    carrier: { now: T[H].now, was: T[H].was, rest: [J[H * 3], J[H * 3 + 1], J[H * 3 + 2]] },
    set(previous, pose, fresh = false) {
      for (const j of joints) { grab(previous, j, T[j].ends[0]); grab(pose, j, T[j].ends[1]); }
      skin.set(body.positions, body.normals, fresh);
      S.at(0, true);
    },
    at(u, first = false) {
      for (const j of joints) { const t = T[j]; copyT(t.now, t.was); lerpT(t.ends[0], t.ends[1], u, t.now); if (first) copyT(t.now, t.was); }
    },
    // at the figure's rest (its joints where the rig has them, unturned; the skin at its rest)
    rest() {
      for (const j of joints) for (const t of T[j].ends) { t.q = [0, 0, 0, 1]; t.qi = [0, 0, 0, 1]; for (let k = 0; k < 3; k++) t.p[k] = J[j * 3 + k]; }
      skin.set(mesh.positions, normalsOf(mesh.positions, mesh.triangles, undefined, mesh.used), true);
      S.at(0, true);
    },
    skin: skin.at,
  };
  S.rest();
  return S;
}

// the skin to meet, but the head's: its points as this frame drew them, in a hash of cells, their normals, and how far
// each moved since the frame before
function skinOf(mesh, sk, withHead) {
  const { omega } = headShares(mesh, sk), idx = Uint32Array.from(Array.from(mesh.used).filter(i => !withHead || omega[i] < 0.5));
  const n = idx.length, P = new Float64Array(n * 3), N = new Float64Array(n * 3), V = new Float64Array(n * 3), cell = 0.03, hash = new Map();
  const key = (a, b, c) => (a + 512) * 1048576 + (b + 512) * 1024 + (c + 512);
  const KN = 8, bi = new Int32Array(KN), bd = new Float64Array(KN);
  return {
    set(positions, normals, fresh = false) {
      hash.clear();
      for (let k = 0; k < n; k++) {
        const i = idx[k];
        for (let c = 0; c < 3; c++) { const x = positions[i * 3 + c]; V[k * 3 + c] = fresh ? 0 : x - P[k * 3 + c]; P[k * 3 + c] = x; N[k * 3 + c] = normals[i * 3 + c]; }
        const h = key(Math.floor(P[k * 3] / cell), Math.floor(P[k * 3 + 1] / cell), Math.floor(P[k * 3 + 2] / cell));
        let list = hash.get(h); if (!list) hash.set(h, list = []); list.push(k);
      }
    },
    at(x, y, z, out) {
      const cx = Math.floor(x / cell), cy = Math.floor(y / cell), cz = Math.floor(z / cell); bd.fill(Infinity); bi.fill(-1);
      for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
        const list = hash.get(key(cx + a, cy + b, cz + c)); if (!list) continue;
        for (const k of list) {
          const d = (P[k * 3] - x) ** 2 + (P[k * 3 + 1] - y) ** 2 + (P[k * 3 + 2] - z) ** 2; if (d >= bd[KN - 1]) continue;
          let m = KN - 1; while (m > 0 && bd[m - 1] > d) { bd[m] = bd[m - 1]; bi[m] = bi[m - 1]; m--; } bd[m] = d; bi[m] = k;
        }
      }
      if (bi[0] < 0 || bd[0] > 0.0009) return Infinity;
      const h2 = Math.max(bd[0], 1e-6) * 4 + 1e-5; let sw = 0, sd = 0, nx = 0, ny = 0, nz = 0, vx = 0, vy = 0, vz = 0;
      for (let m = 0; m < KN; m++) {
        const k = bi[m]; if (k < 0) break; const w = Math.exp(-bd[m] / h2);
        sw += w; sd += w * ((x - P[k * 3]) * N[k * 3] + (y - P[k * 3 + 1]) * N[k * 3 + 1] + (z - P[k * 3 + 2]) * N[k * 3 + 2]);
        nx += w * N[k * 3]; ny += w * N[k * 3 + 1]; nz += w * N[k * 3 + 2]; vx += w * V[k * 3]; vy += w * V[k * 3 + 1]; vz += w * V[k * 3 + 2];
      }
      const l = Math.hypot(nx, ny, nz) || 1; out.n[0] = nx / l; out.n[1] = ny / l; out.n[2] = nz / l; out.v[0] = vx / sw; out.v[1] = vy / sw; out.v[2] = vz / sw;
      return sd / sw;
    },
  };
}

// a part riding a joint: a point carried into the joint's rest (back by its turn and place now or a step ago), its
// distance there from a baked grid, and a rest point carried out again
function partOf(grid, J, j, t, into = null) {
  const back = (st, x, out) => { qRot3(st.qi, x[0] - st.p[0], x[1] - st.p[1], x[2] - st.p[2], out); out[0] += J[j * 3]; out[1] += J[j * 3 + 1]; out[2] += J[j * 3 + 2]; return out; };
  return {
    grid, joint: j, c: [0, 0, 0], r: grid.r,
    // (its grid's middle where the joint carries it now, and how far its grid reaches: a point beyond is not looked at)
    place() { const st = t.now, m = grid.mid; qRot3(st.q, m[0] - J[j * 3], m[1] - J[j * 3 + 1], m[2] - J[j * 3 + 2], this.c); for (let k = 0; k < 3; k++) this.c[k] += st.p[k]; },
    local: into ? (x, out) => into(t.now, x, out) : (x, out) => back(t.now, x, out),
    was: into ? (x, out) => into(t.was, x, out) : (x, out) => back(t.was, x, out),
    turn: (v, out) => qRot3(t.now.q, v[0], v[1], v[2], out),
    world: (l, out) => { const st = t.now; qRot3(st.q, l[0] - J[j * 3], l[1] - J[j * 3 + 1], l[2] - J[j * 3 + 2], out); out[0] += st.p[0]; out[1] += st.p[1]; out[2] += st.p[2]; return out; },
    distance: l => grid.at(l[0], l[1], l[2]),
    normal: (l, out) => grid.normal(l[0], l[1], l[2], out),
  };
}

// the head's shape in its rest space: a point carried there by the Head joint and, below the mouth and in front of the
// ears, by the Jaw joint (blended as figure.headShape does); carried out by the Head joint (the jaw's small part with it)
function headOf(shape, J, H, JW, T) {
  const F = shape.frame, { y: jy, z: jz } = shape.jaw, hj = [0, 0, 0], jj = [0, 0, 0];
  const back = (st, j, x, o) => { qRot3(st.qi, x[0] - st.p[0], x[1] - st.p[1], x[2] - st.p[2], o); o[0] += J[j * 3]; o[1] += J[j * 3 + 1]; o[2] += J[j * 3 + 2]; return o; };
  const into = (st, x, out) => {
    const sj = st === T[H].now ? T[JW].now : T[JW].was;
    back(st, H, x, hj);
    const hy = (hj[1] - F.O[1]) / F.R, hz = (hj[2] - F.O[2]) / F.R, w = sst(clamp((jy - hy) / 0.15, 0, 1)) * sst(clamp((hz - jz) / 0.3, 0, 1));
    if (w) { back(sj, JW, x, jj); for (let k = 0; k < 3; k++) hj[k] += (jj[k] - hj[k]) * w; }
    out[0] = hj[0]; out[1] = hj[1]; out[2] = hj[2]; return out;
  };
  const grid = cached(shape, () => gridOf((x, y, z) => shape.sdf((x - F.O[0]) / F.R, (y - F.O[1]) / F.R, (z - F.O[2]) / F.R) * F.R,
    [F.O[0] - 1.9 * F.R, F.O[1] - 2.3 * F.R, F.O[2] - 1.9 * F.R], [F.O[0] + 1.9 * F.R, F.O[1] + 1.9 * F.R, F.O[2] + 1.9 * F.R], 0.045 * F.R));
  return { ...partOf(grid, J, H, T[H], into), head: true };
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
    mid: lo.map((v, c) => (v + hi[c]) / 2), r: Math.hypot(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]) / 2,
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
