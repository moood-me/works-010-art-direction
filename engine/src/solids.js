// The body as hair (and, later, clothes) meet it — one set of solids a figure offers:
// - its head's shape (the designed form, or a ball fitted to the head: src/head/head.js), carried by the Head joint
//   and, below the mouth, by the Jaw joint (figure.headShape's split);
// - its neck, trunk, shoulders and upper arms — where hair lies and cloth hangs, and where a capsule round a bone is
//   too coarse (a capsule round the collarbone stands over the shoulder like a shelf) — as the skin itself: each of
//   these bones carries the skin it moves most at rest, as a distance from that skin (signed by its normals), carried by
//   the bone;
// - the body's other capsules (src/collision.js: the forearms, hands, legs).
// A simulation's frame runs in small steps from the previous pose to this one, so the solids move between the two:
// set(previous, pose) once a frame, at(u) at each small step (u from 0 to 1), the state a step ago kept, so a point
// lying on a solid can be carried by its motion (friction).
//   const S = figure.solids();           // once (kept on the figure)
//   S.set(previous, pose); S.at(u);       // each frame, each small step;  S.rest() — the figure at its rest
//   S.parts: [{head?, local(x, out), was(x, out), world(l, out), distance(l), normal(l, out)}]  in the part's rest
//   S.head: the head's part, or null;  S.caps: [{a, b, ra, rb, a0, b0}] — now and a step ago
//   S.carrier: the Head joint's {now, was: {q, p}, rest}
// Distances are baked once per head and per body into grids over each part's rest (trilinear between their points,
// refined only near the surface), so a lookup costs a few reads.
import { qRot3, qSlerp, clamp, sst } from './math.js';
import { makeCollider } from './collision.js';
import { HEAD_JOINTS } from './head/frame.js';
import { normalsOf } from './mesh.js';

// the bones whose skin is a solid of its own
const SKIN_PARTS = ['Spine1', 'Spine2', 'Chest', 'Neck1', 'Neck2', 'LeftShoulder', 'RightShoulder', 'LeftArm', 'RightArm'];

export function makeSolids(figure) {
  const rig = figure.rig, sk = rig.skeleton, J = rig.joints, shape = figure.body?.head?.shape ?? null, mesh = figure.body ? figure.body.mesh : figure.outputs[0].mesh;
  const headJ = new Set(HEAD_JOINTS.map(n => sk.index[n])), skinJ = SKIN_PARTS.map(n => sk.index[n]).filter(j => j !== undefined);
  const C = makeCollider(rig, mesh);
  const rest = C.rest.filter(c => !(shape && headJ.has(c.joint)) && !skinJ.includes(c.joint));
  const caps = rest.map(c => ({ ra: c.ra, rb: c.rb, joint: c.joint, a: c.a.slice(), b: c.b.slice(), a0: c.a.slice(), b0: c.b.slice() }));
  const ends = rest.map(() => ({ A: [new Float64Array(3), new Float64Array(3)], B: [new Float64Array(3), new Float64Array(3)] }));
  const H = sk.index.Head, JW = sk.index.Jaw, tmp = [0, 0, 0];
  // each joint a part rides: its turn and place from the rest, at the frame's two ends, now and a step ago
  const tr = () => ({ q: [0, 0, 0, 1], qi: [0, 0, 0, 1], p: [0, 0, 0] }), joints = [H, JW, ...skinJ];
  const T = Object.fromEntries(joints.map(j => [j, { ends: [tr(), tr()], now: tr(), was: tr() }]));
  const grab = (pose, j, o) => { for (let k = 0; k < 4; k++) o.q[k] = pose.Q[j * 4 + k]; for (let k = 0; k < 3; k++) o.p[k] = pose.P[j * 3 + k]; };
  const lerpT = (a, b, u, o) => { const q = qSlerp(a.q, b.q, u); for (let k = 0; k < 4; k++) o.q[k] = q[k]; o.qi[0] = -q[0]; o.qi[1] = -q[1]; o.qi[2] = -q[2]; o.qi[3] = q[3]; for (let k = 0; k < 3; k++) o.p[k] = a.p[k] + (b.p[k] - a.p[k]) * u; };
  const copyT = (a, o) => { for (let k = 0; k < 4; k++) { o.q[k] = a.q[k]; o.qi[k] = a.qi[k]; } for (let k = 0; k < 3; k++) o.p[k] = a.p[k]; };
  const carry = (pose, c, from, out) => { const j = c.joint, q = [pose.Q[j * 4], pose.Q[j * 4 + 1], pose.Q[j * 4 + 2], pose.Q[j * 4 + 3]]; qRot3(q, from[0] - J[j * 3], from[1] - J[j * 3 + 1], from[2] - J[j * 3 + 2], tmp); for (let k = 0; k < 3; k++) out[k] = pose.P[j * 3 + k] + tmp[k]; };
  const head = shape ? headOf(shape, J, H, JW, T) : null;
  const parts = [...(head ? [head] : []), ...skinParts(mesh, rig, skinJ, T)];
  const S = {
    head, parts, caps,
    // the Head joint's turn and place now and a step ago (what carries a hairstyle), and its rest place
    carrier: { now: T[H].now, was: T[H].was, rest: [J[H * 3], J[H * 3 + 1], J[H * 3 + 2]] },
    set(previous, pose) {
      rest.forEach((c, n) => { carry(previous, c, c.a, ends[n].A[0]); carry(pose, c, c.a, ends[n].A[1]); carry(previous, c, c.b, ends[n].B[0]); carry(pose, c, c.b, ends[n].B[1]); });
      for (const j of joints) { grab(previous, j, T[j].ends[0]); grab(pose, j, T[j].ends[1]); }
      S.at(0, true);
    },
    at(u, first = false) {
      for (let n = 0; n < caps.length; n++) {
        const c = caps[n], e = ends[n];
        for (let k = 0; k < 3; k++) { c.a0[k] = c.a[k]; c.b0[k] = c.b[k]; c.a[k] = e.A[0][k] + (e.A[1][k] - e.A[0][k]) * u; c.b[k] = e.B[0][k] + (e.B[1][k] - e.B[0][k]) * u; }
        if (first) for (let k = 0; k < 3; k++) { c.a0[k] = c.a[k]; c.b0[k] = c.b[k]; }
        // (its middle and how far it reaches from there)
        c.m ??= [0, 0, 0]; for (let k = 0; k < 3; k++) c.m[k] = (c.a[k] + c.b[k]) / 2;
        c.reach = Math.hypot(c.b[0] - c.a[0], c.b[1] - c.a[1], c.b[2] - c.a[2]) / 2 + Math.max(c.ra, c.rb);
      }
      for (const j of joints) { const t = T[j]; copyT(t.now, t.was); lerpT(t.ends[0], t.ends[1], u, t.now); if (first) copyT(t.now, t.was); }
      for (const p of parts) p.place();
    },
    // at the figure's rest (its joints where the rig has them, unturned)
    rest() {
      rest.forEach((c, n) => { for (let s = 0; s < 2; s++) for (let k = 0; k < 3; k++) { ends[n].A[s][k] = c.a[k]; ends[n].B[s][k] = c.b[k]; } });
      for (const j of joints) for (const t of T[j].ends) { t.q = [0, 0, 0, 1]; for (let k = 0; k < 3; k++) t.p[k] = J[j * 3 + k]; }
      S.at(0, true);
    },
    // how far a point is from a capsule now (negative inside), its outward normal (into n), and where along it (t)
    capsule(c, x, y, z, n) {
      const bx = c.b[0] - c.a[0], by = c.b[1] - c.a[1], bz = c.b[2] - c.a[2], L2 = bx * bx + by * by + bz * bz || 1e-12;
      const t = clamp(((x - c.a[0]) * bx + (y - c.a[1]) * by + (z - c.a[2]) * bz) / L2, 0, 1);
      const dx = x - c.a[0] - bx * t, dy = y - c.a[1] - by * t, dz = z - c.a[2] - bz * t, l = Math.hypot(dx, dy, dz);
      if (l > 1e-9) { n[0] = dx / l; n[1] = dy / l; n[2] = dz / l; } else { n[0] = 0; n[1] = 1; n[2] = 0; }
      n.t = t;
      return l - (c.ra + (c.rb - c.ra) * t);
    },
  };
  S.rest();
  return S;
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

// the skin each bone moves most (its vertices whose weight on it is the largest, and those it moves by a third or
// more), as a distance at rest: to the nearest of those vertices, along its normal where it is near (signed: inside
// the skin is negative), straight beyond — on a grid round them, 8 mm apart on a grown-up, kept per body
function skinParts(mesh, rig, joints, T) {
  const P = mesh.positions, K = mesh.skin.K, SJ = mesh.skin.joints, SW = mesh.skin.weights, J = rig.joints;
  const all = cached(mesh, () => {
    const N = normalsOf(P, mesh.triangles, undefined, mesh.used), out = new Map();
    for (const j of joints) {
      const vs = [];
      for (const i of mesh.used) { let w = 0, top = 0, tj = -1; for (let k = 0; k < K; k++) { const a = SW[i * K + k]; if (SJ[i * K + k] === j) w += a; if (a > top) { top = a; tj = SJ[i * K + k]; } } if (tj === j || w >= 0.33) vs.push(i); }
      if (vs.length < 30) continue;
      const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
      for (const i of vs) for (let c = 0; c < 3; c++) { lo[c] = Math.min(lo[c], P[i * 3 + c] - 0.04); hi[c] = Math.max(hi[c], P[i * 3 + c] + 0.04); }
      const cell = 0.03, hash = new Map(), key = (a, b, c) => `${a},${b},${c}`;
      for (const i of vs) { const k = key(Math.floor(P[i * 3] / cell), Math.floor(P[i * 3 + 1] / cell), Math.floor(P[i * 3 + 2] / cell)); if (!hash.has(k)) hash.set(k, []); hash.get(k).push(i); }
      const f = (x, y, z) => {
        const cx = Math.floor(x / cell), cy = Math.floor(y / cell), cz = Math.floor(z / cell); let best = Infinity, bi = -1;
        for (let r = 0; r <= 3 && bi < 0 || r <= 1; r++) for (let a = -r; a <= r; a++) for (let b = -r; b <= r; b++) for (let c = -r; c <= r; c++) {
          if (Math.max(Math.abs(a), Math.abs(b), Math.abs(c)) !== r) continue;
          for (const i of hash.get(key(cx + a, cy + b, cz + c)) ?? []) { const d = (P[i * 3] - x) ** 2 + (P[i * 3 + 1] - y) ** 2 + (P[i * 3 + 2] - z) ** 2; if (d < best) { best = d; bi = i; } }
        }
        if (bi < 0) return 0.09;
        const dx = x - P[bi * 3], dy = y - P[bi * 3 + 1], dz = z - P[bi * 3 + 2], along = dx * N[bi * 3] + dy * N[bi * 3 + 1] + dz * N[bi * 3 + 2], d = Math.sqrt(best);
        return d < 0.02 ? along : Math.sign(along) * d;
      };
      out.set(j, gridOf(f, lo, hi, 0.008 * Math.cbrt(rig.hipHeight / 0.9)));
    }
    return out;
  });
  return [...all.entries()].map(([j, grid]) => partOf(grid, J, j, T[j]));
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
