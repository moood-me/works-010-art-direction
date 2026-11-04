// The body and its clothes as the player sees them, measured exactly (the clothes' checks, check/quality.mjs): the drawn
// meshes — the body's skin and each garment's drawn surface — not the simulation's own answers about them.
// - the cloth in the body: each drawn point of cloth inside the body's skin (a closed mesh: its nearest triangle's
//   angle-weighted pseudo-normal says which side, Bærentzen & Aanæs 2005 — exact at any depth, no band it can't see),
//   how deep (from the skin nearest it: cloth pinched in a fold of the body lies just under both skins, and is hidden);
// - the body through the cloth: a skin point a garment covered at rest with that garment inside the body behind it (along
//   its normal inward, before the ray leaves the skin) — a knee through a trouser front, between the cloth's points as
//   well as on them;
// - covered skin stays covered: skin a garment covers at rest (its normal meets the garment's inside, farther than
//   MARGIN from the garment's open edges) still meets its inside — not left bare by cloth ridden up, nor through it;
// - layers keep their order: skin covered by two garments meets the one worn under first;
// - tubes go round their bones: each ring of a sleeve or a trouser leg (its points round the limb at rest, a band along
//   the bone) still winds once round the bone.
//   const L = looker(fig, sim)   (at rest, settled: what each garment covers, its rings)
//   L.frame() → {deep: [metres of each drawn cloth point inside, deepest first], through, uncovered, swapped, rings}
//               (the last four shares 0–1 of what they count)
import { LIMBS, regionsOf } from '../src/regions.js';

// MARGIN: how far from a garment's open edge skin it covers at rest must be to be counted (an edge rides a little
// over the skin as the body moves: a hem over the knees sitting is not "uncovered"); SAMPLE: every how many skin points
// are asked (they are a centimetre apart: every fourth is one every 2 cm); DRAWN: every how many of the cloth's drawn
// points (drawn finer than simulated: every third is as dense as its simulated points); REACH: how far from the skin a
// garment's inside is looked for (a bell's hem stands 20–30 cm off the legs); BAND: a tube's ring's width along its bone
const MARGIN = 0.05, SAMPLE = 4, REACH = 0.4, BAND = 0.04, DRAWN = 3;
// PAIRS: how many skin points two garments must both cover for their order to be counted (a few at a hem's edge, a share
// of them is one point's turn); LONG: how many rings a limb's tube must have to be counted (a short sleeve or shorts
// are one or two bands round the top of the limb, and crumple round a shoulder or hip as it turns)
const PAIRS = 30, LONG = 4;
const BONES = { 1: ['LeftArm', 'LeftForeArm', 'LeftHand'], 2: ['RightArm', 'RightForeArm', 'RightHand'], 3: ['LeftLeg', 'LeftShin', 'LeftFoot'], 4: ['RightLeg', 'RightShin', 'RightFoot'] };

export function looker(fig, sim) {
  const body = fig.outputs[0], BP = body.positions, BT = body.mesh.triangles, BN = body.normals, used = body.mesh.used;
  const bodyGrid = triGrid(0.02), bodyPN = pseudo(BT, BP.length / 3);
  const gs = sim.garments.map(g => ({ g, out: g.output, grid: triGrid(0.02), edges: boundary(g.output.mesh.triangles, g.output.positions.length / 3) }));
  const sample = Uint32Array.from({ length: Math.ceil(used.length / SAMPLE) }, (_, k) => used[k * SAMPLE]);
  const hit = { t: 0, tri: -1, inner: false };
  const build = () => { bodyGrid.build(BP, BT); bodyPN.update(BP); for (const G of gs) G.grid.build(G.out.positions, G.out.mesh.triangles); };
  // the garment's inside first met along the skin's normal from skin point v (its distance, or Infinity)
  const along = (G, v, sign = 1) => {
    const o = v * 3, nx = BN[o] * sign, ny = BN[o + 1] * sign, nz = BN[o + 2] * sign;
    return G.grid.ray(G.out.positions, G.out.mesh.triangles, BP[o] + nx * 5e-4, BP[o + 1] + ny * 5e-4, BP[o + 2] + nz * 5e-4, nx, ny, nz, REACH, hit) ? hit : null;
  };
  // ———— at rest ————
  build();
  const cover = gs.map(G => {
    const P = G.out.positions, E = G.edges, list = [], at = [];
    for (const v of sample) {
      const h = along(G, v); if (!h || !h.inner) continue;
      const o = v * 3, n = [BN[o], BN[o + 1], BN[o + 2]], q = [BP[o] + n[0] * h.t, BP[o + 1] + n[1] * h.t, BP[o + 2] + n[2] * h.t];
      let near = Infinity; for (const e of E) near = Math.min(near, Math.hypot(P[e * 3] - q[0], P[e * 3 + 1] - q[1], P[e * 3 + 2] - q[2]));
      if (near > MARGIN) { list.push(v); at.push(h.t); }
    }
    return { v: Uint32Array.from(list), t: Float64Array.from(at) };
  });
  // (skin covered by two: which is under)
  const pairs = [];
  for (let a = 0; a < gs.length; a++) for (let b = a + 1; b < gs.length; b++) {
    const ta = new Map(Array.from(cover[a].v, (v, k) => [v, cover[a].t[k]]));
    cover[b].v.forEach((v, k) => { if (ta.has(v)) { const [inner, outer] = ta.get(v) < cover[b].t[k] ? [a, b] : [b, a]; pairs.push([v, inner, outer]); } });
  }
  // (each simulated point's limb: its nearest skin point's strongest)
  const R = regionsOf(body.mesh, fig.rig), limbOf = v => { let m = 0; for (let l = 1; l < 5; l++) if (R.limb[v * 5 + l] > R.limb[v * 5 + m]) m = l; return m; };
  const nearestSkin = (x, y, z) => { let b = 0, bd = Infinity; for (const v of used) { const d = (BP[v * 3] - x) ** 2 + (BP[v * 3 + 1] - y) ** 2 + (BP[v * 3 + 2] - z) ** 2; if (d < bd) { bd = d; b = v; } } return b; };
  const rings = gs.flatMap(G => G.g.pattern.tubes ? ringsOf(fig, G.g, Uint8Array.from({ length: G.g.n }, (_, i) => limbOf(nearestSkin(G.g.x[i * 3], G.g.x[i * 3 + 1], G.g.x[i * 3 + 2])))) : []);
  return {
    covered: cover.reduce((s, c) => s + c.v.length, 0), rings: rings.length,
    frame() {
      build();
      // the cloth in the body
      const deep = [], q = { d: 0, inside: false };
      for (const G of gs) { const P = G.out.positions, u = G.out.mesh.used; for (let k = 0; k < u.length; k += DRAWN) { const i = u[k] * 3; bodyGrid.nearest(BP, BT, bodyPN, P[i], P[i + 1], P[i + 2], q); deep.push(q.inside ? q.d : 0); } }
      deep.sort((a, b) => b - a);
      // the body through the cloth: skin a garment covered at rest with that garment inside the body behind it, before
      // its ray inward leaves the skin (cloth of another garment pinched between an arm and the side is hidden there)
      // covered skin still covered; layers in their order
      let through = 0, uncovered = 0, swapped = 0, n = 0;
      gs.forEach((G, k) => { for (const v of cover[k].v) {
        n++; const h = along(G, v); if (!h || !h.inner) uncovered++;
        const o = v * 3, nx = -BN[o], ny = -BN[o + 1], nz = -BN[o + 2], ox = BP[o] + nx * 1e-3, oy = BP[o + 1] + ny * 1e-3, oz = BP[o + 2] + nz * 1e-3;
        const exit = bodyGrid.ray(BP, BT, ox, oy, oz, nx, ny, nz, 0.4, hit) ? hit.t : 0.4;
        if (G.grid.ray(G.out.positions, G.out.mesh.triangles, ox, oy, oz, nx, ny, nz, exit, hit)) through++;
      } });
      for (const [v, a, b] of pairs) { const ha = along(gs[a], v), ta = ha && ha.inner ? ha.t : Infinity, hb = along(gs[b], v), tb = hb && hb.inner ? hb.t : Infinity; if (tb < ta - 1e-3 && ta < Infinity) swapped++; }
      // the tubes round their bones
      let off = 0; for (const r of rings) if (Math.abs(r.winding()) < 0.5) off++;
      return { deep, through: n ? through / n : 0, uncovered: n ? uncovered / n : 0, swapped: pairs.length >= PAIRS ? swapped / pairs.length : 0, rings: rings.length ? off / rings.length : 0 };
    },
  };
}

// a tube's rings: its simulated points by the limb under each at rest (its nearest skin point's), each limb's two bones,
// bands BAND wide along each bone; a band is a ring where its points go round the bone at rest (no gap wider than 60°,
// winding once) — ordered by their angle round it there
function ringsOf(fig, g, limbOf) {
  const sk = fig.rig.skeleton, P = () => fig.pose.P, x = g.x, out = [];
  for (const [limb, names] of Object.entries(BONES)) {
    const J = names.map(n => sk.index[n]);
    for (let s = 0; s < 2; s++) {
      const a = J[s], b = J[s + 1], len = seg(P(), a, b).len, bands = new Map();
      for (let i = 0; i < g.n; i++) {
        if (limbOf[i] !== +limb) continue;
        // (on the nearer of its limb's two bones)
        const f0 = foot(P(), J[0], J[1], x, i), f1 = foot(P(), J[1], J[2], x, i), f = s === 0 ? f0 : f1, other = s === 0 ? f1 : f0;
        if (other.d < f.d || f.t <= 0 || f.t >= 1) continue;
        const k = Math.floor(f.t * len / BAND); if (!bands.has(k)) bands.set(k, []); bands.get(k).push(i);
      }
      for (const [k, pts] of bands) {
        if (pts.length < 8) continue;
        const t = (k + 0.5) * BAND / len, ang = pts.map(i => angleAt(P(), a, b, t, x, i));
        const order = pts.map((i, j) => [ang[j], i]).sort((p, q) => p[0] - q[0]);
        let gap = 0; for (let j = 0; j < order.length; j++) gap = Math.max(gap, (order[(j + 1) % order.length][0] - order[j][0] + 2 * Math.PI) % (2 * Math.PI) || 0);
        if (gap > Math.PI / 3) continue;
        const ids = order.map(o => o[1]);
        const winding = () => { let w = 0, prev = angleAt(P(), a, b, t, x, ids[ids.length - 1]); for (const i of ids) { const c = angleAt(P(), a, b, t, x, i); let d = c - prev; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; w += d; prev = c; } return w / (2 * Math.PI); };
        if (Math.abs(winding()) > 0.5) out.push({ limb: LIMBS[limb], winding });
      }
    }
  }
  return out.filter(r => out.filter(q => q.limb === r.limb).length >= LONG);
}
function seg(P, a, b) { const e = [P[b * 3] - P[a * 3], P[b * 3 + 1] - P[a * 3 + 1], P[b * 3 + 2] - P[a * 3 + 2]]; return { e, len: Math.hypot(...e) }; }
function foot(P, a, b, x, i) {
  const { e, len } = seg(P, a, b), px = x[i * 3] - P[a * 3], py = x[i * 3 + 1] - P[a * 3 + 1], pz = x[i * 3 + 2] - P[a * 3 + 2], t = (px * e[0] + py * e[1] + pz * e[2]) / (len * len);
  const c = Math.max(0, Math.min(1, t)); return { t, d: Math.hypot(px - e[0] * c, py - e[1] * c, pz - e[2] * c) };
}
// the angle of point i round the bone a→b, about its point at t, in a frame fixed to the bone (its axis and the world's
// least-aligned axis crossed with it)
function angleAt(P, a, b, t, x, i) {
  const { e, len } = seg(P, a, b), u = e.map(v => v / len), r = Math.abs(u[1]) < 0.8 ? [0, 1, 0] : [1, 0, 0];
  const v1 = norm(cross(u, r)), v2 = cross(u, v1), c = [P[a * 3] + e[0] * t, P[a * 3 + 1] + e[1] * t, P[a * 3 + 2] + e[2] * t];
  const d = [x[i * 3] - c[0], x[i * 3 + 1] - c[1], x[i * 3 + 2] - c[2]];
  return Math.atan2(d[0] * v2[0] + d[1] * v2[1] + d[2] * v2[2], d[0] * v1[0] + d[1] * v1[1] + d[2] * v1[2]);
}
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = a => { const l = Math.hypot(...a) || 1; return a.map(v => v / l); };

// a mesh's open edges' points
function boundary(T, n) {
  const em = new Map(); for (let t = 0; t < T.length; t += 3) for (let k = 0; k < 3; k++) { const a = T[t + k], b = T[t + (k + 1) % 3], key = a < b ? a * n + b : b * n + a; em.set(key, (em.get(key) || 0) + 1); }
  const out = new Set(); for (const [key, c] of em) if (c === 1) { out.add(Math.floor(key / n)); out.add(key % n); }
  return Uint32Array.from(out);
}
// a closed mesh's pseudo-normals (angle-weighted at its points, the two faces' at its edges, the face's within it):
// which side of the mesh a point is, from its nearest triangle
function pseudo(T, n) {
  const em = new Map(), te = new Int32Array(T.length);
  for (let t = 0; t < T.length; t += 3) for (let k = 0; k < 3; k++) { const a = T[t + k], b = T[t + (k + 1) % 3], key = a < b ? a * n + b : b * n + a; if (!em.has(key)) em.set(key, em.size); te[t + k] = em.get(key); }
  const F = new Float64Array(T.length), V = new Float64Array(n * 3), E = new Float64Array(em.size * 3);
  return {
    F, V, E, te,
    update(P) {
      V.fill(0); E.fill(0);
      for (let t = 0; t < T.length; t += 3) {
        const a = T[t] * 3, b = T[t + 1] * 3, c = T[t + 2] * 3, ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], vx = P[c] - P[a], vy = P[c + 1] - P[a + 1], vz = P[c + 2] - P[a + 2];
        let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx; const l = Math.hypot(nx, ny, nz) || 1; nx /= l; ny /= l; nz /= l;
        F[t] = nx; F[t + 1] = ny; F[t + 2] = nz;
        for (let k = 0; k < 3; k++) {
          const p = T[t + k] * 3, q = T[t + (k + 1) % 3] * 3, r = T[t + (k + 2) % 3] * 3;
          const e1 = [P[q] - P[p], P[q + 1] - P[p + 1], P[q + 2] - P[p + 2]], e2 = [P[r] - P[p], P[r + 1] - P[p + 1], P[r + 2] - P[p + 2]];
          const w = Math.acos(Math.max(-1, Math.min(1, (e1[0] * e2[0] + e1[1] * e2[1] + e1[2] * e2[2]) / ((Math.hypot(...e1) * Math.hypot(...e2)) || 1))));
          V[p] += w * nx; V[p + 1] += w * ny; V[p + 2] += w * nz;
          const e = te[t + k] * 3; E[e] += nx; E[e + 1] += ny; E[e + 2] += nz;
        }
      }
    },
  };
}

// triangles in cells (each in every cell its box touches): the nearest of them to a point (and which side by the
// pseudo-normals), the first a ray meets
function triGrid(cell) {
  const SIZE = 1 << 16, start = new Int32Array(SIZE + 1); let items = new Int32Array(0), stamp = new Int32Array(0), mark = 0;
  const key = (a, b, c) => (((a * 73856093) ^ (b * 19349663) ^ (c * 83492791)) >>> 0) & (SIZE - 1), cellOf = v => Math.floor(v / cell);
  const boxes = (P, T, f) => { for (let t = 0; t < T.length; t += 3) { const a = T[t] * 3, b = T[t + 1] * 3, c = T[t + 2] * 3; const lo = [0, 1, 2].map(k => cellOf(Math.min(P[a + k], P[b + k], P[c + k]))), hi = [0, 1, 2].map(k => cellOf(Math.max(P[a + k], P[b + k], P[c + k]))); for (let i = lo[0]; i <= hi[0]; i++) for (let j = lo[1]; j <= hi[1]; j++) for (let k = lo[2]; k <= hi[2]; k++) f(key(i, j, k), t / 3); } };
  const g = {
    build(P, T) {
      start.fill(0); let n = 0; boxes(P, T, h => { start[h + 1]++; n++; });
      for (let h = 0; h < SIZE; h++) start[h + 1] += start[h];
      if (items.length < n) items = new Int32Array(n); if (stamp.length < T.length / 3) stamp = new Int32Array(T.length / 3);
      const fill = start.slice(); boxes(P, T, (h, t) => { items[fill[h]++] = t; });
    },
    // the nearest triangle to (x, y, z): out.d its distance, out.inside by the pseudo-normal of what is nearest on it
    nearest(P, T, PN, x, y, z, out) {
      mark++; const cx = cellOf(x), cy = cellOf(y), cz = cellOf(z), cp = [0, 0, 0]; let best = Infinity, bt = -1, bf = 0;
      for (let r = 0; r < 64; r++) {
        if (best < (r - 1) * cell) break;
        for (let i = -r; i <= r; i++) for (let j = -r; j <= r; j++) for (let k = -r; k <= r; k++) {
          if (Math.max(Math.abs(i), Math.abs(j), Math.abs(k)) !== r) continue;
          const h = key(cx + i, cy + j, cz + k);
          for (let e = start[h]; e < start[h + 1]; e++) {
            const t = items[e]; if (stamp[t] === mark) continue; stamp[t] = mark;
            const f = closest(P, T, t * 3, x, y, z, cp), d = (x - cp[0]) ** 2 + (y - cp[1]) ** 2 + (z - cp[2]) ** 2;
            if (d < best * best) { best = Math.sqrt(d); bt = t; bf = f; out.px = cp[0]; out.py = cp[1]; out.pz = cp[2]; }
          }
        }
      }
      out.d = best; if (bt < 0) { out.inside = false; return out; }
      // (the pseudo-normal of the feature nearest: the face, an edge, a point)
      const t3 = bt * 3; let n;
      if (bf === 0) n = [PN.F[t3], PN.F[t3 + 1], PN.F[t3 + 2]];
      else if (bf < 4) { const e = PN.te[t3 + bf - 1] * 3; n = [PN.E[e], PN.E[e + 1], PN.E[e + 2]]; }
      else { const v = T[t3 + bf - 4] * 3; n = [PN.V[v], PN.V[v + 1], PN.V[v + 2]]; }
      out.inside = (x - out.px) * n[0] + (y - out.py) * n[1] + (z - out.pz) * n[2] < 0;
      return out;
    },
    // the first triangle a ray from o along unit d meets within tmax: out {t, tri, inner (met from its back: the side
    // its normal points away from)}; false if none
    ray(P, T, ox, oy, oz, dx, dy, dz, tmax, out) {
      mark++; let best = tmax, found = false;
      const steps = Math.ceil(tmax / (cell / 3));
      for (let s = 0; s <= steps; s++) {
        const u = Math.min(tmax, s * cell / 3), h = key(cellOf(ox + dx * u), cellOf(oy + dy * u), cellOf(oz + dz * u));
        if (u > best + cell) break;
        for (let e = start[h]; e < start[h + 1]; e++) {
          const t = items[e]; if (stamp[t] === mark) continue; stamp[t] = mark;
          const r = rayTri(P, T, t * 3, ox, oy, oz, dx, dy, dz); if (r === null || r.t >= best || r.t < 0) continue;
          best = r.t; found = true; out.t = r.t; out.tri = t; out.inner = r.back;
        }
      }
      return found;
    },
  };
  return g;
}
// Möller–Trumbore: the distance along the ray to the triangle (and whether it is met from its back), or null
const RT = { t: 0, back: false };
function rayTri(P, T, t3, ox, oy, oz, dx, dy, dz) {
  const a = T[t3] * 3, b = T[t3 + 1] * 3, c = T[t3 + 2] * 3;
  const e1x = P[b] - P[a], e1y = P[b + 1] - P[a + 1], e1z = P[b + 2] - P[a + 2], e2x = P[c] - P[a], e2y = P[c + 1] - P[a + 1], e2z = P[c + 2] - P[a + 2];
  const px = dy * e2z - dz * e2y, py = dz * e2x - dx * e2z, pz = dx * e2y - dy * e2x, det = e1x * px + e1y * py + e1z * pz;
  if (Math.abs(det) < 1e-14) return null;
  const inv = 1 / det, sx = ox - P[a], sy = oy - P[a + 1], sz = oz - P[a + 2], u = (sx * px + sy * py + sz * pz) * inv; if (u < 0 || u > 1) return null;
  const qx = sy * e1z - sz * e1y, qy = sz * e1x - sx * e1z, qz = sx * e1y - sy * e1x, v = (dx * qx + dy * qy + dz * qz) * inv; if (v < 0 || u + v > 1) return null;
  RT.t = (e2x * qx + e2y * qy + e2z * qz) * inv;
  // (the face's normal e1 × e2 against the ray: along it, the ray comes from its back)
  RT.back = det < 0; return RT;
}
// the point of triangle t3 nearest (x, y, z) into cp; which feature it is on: 0 the face, 1–3 the edge from corner
// k−1 to k, 4–6 corner k−4 (Ericson, Real-Time Collision Detection 5.1.5)
function closest(P, T, t3, x, y, z, cp) {
  const A = T[t3] * 3, B = T[t3 + 1] * 3, C = T[t3 + 2] * 3;
  const abx = P[B] - P[A], aby = P[B + 1] - P[A + 1], abz = P[B + 2] - P[A + 2], acx = P[C] - P[A], acy = P[C + 1] - P[A + 1], acz = P[C + 2] - P[A + 2];
  const apx = x - P[A], apy = y - P[A + 1], apz = z - P[A + 2], d1 = abx * apx + aby * apy + abz * apz, d2 = acx * apx + acy * apy + acz * apz;
  const set = (s, t, f) => { cp[0] = P[A] + abx * s + acx * t; cp[1] = P[A + 1] + aby * s + acy * t; cp[2] = P[A + 2] + abz * s + acz * t; return f; };
  if (d1 <= 0 && d2 <= 0) return set(0, 0, 4);
  const bpx = x - P[B], bpy = y - P[B + 1], bpz = z - P[B + 2], d3 = abx * bpx + aby * bpy + abz * bpz, d4 = acx * bpx + acy * bpy + acz * bpz;
  if (d3 >= 0 && d4 <= d3) return set(1, 0, 5);
  const vc = d1 * d4 - d3 * d2; if (vc <= 0 && d1 >= 0 && d3 <= 0) return set(d1 / (d1 - d3), 0, 1);
  const cpx = x - P[C], cpy = y - P[C + 1], cpz = z - P[C + 2], d5 = abx * cpx + aby * cpy + abz * cpz, d6 = acx * cpx + acy * cpy + acz * cpz;
  if (d6 >= 0 && d5 <= d6) return set(0, 1, 6);
  const vb = d5 * d2 - d1 * d6; if (vb <= 0 && d2 >= 0 && d6 <= 0) return set(0, d2 / (d2 - d6), 3);
  const va = d3 * d6 - d5 * d4; if (va <= 0 && d4 - d3 >= 0 && d5 - d6 >= 0) { const w = (d4 - d3) / ((d4 - d3) + (d5 - d6)); return set(1 - w, w, 2); }
  const den = 1 / (va + vb + vc); return set(vb * den, vc * den, 0);
}
