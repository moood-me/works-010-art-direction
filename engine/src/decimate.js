// A surface made simpler (Garland & Heckbert 1997, quadric error metrics, by half-edge collapses: a vertex is folded onto
// a neighbour, so every vertex left is one of the surface's own, with all it carries — its strand direction, its binding
// — exact). Each vertex sums the squared distances to the planes of its triangles; folding u onto v costs v's distance
// to the planes of both. The cheapest fold first, as long as it moves the surface less than `error`, keeps the
// surface whole (two triangles round the edge, no more shared neighbours than that), turns no triangle over, leaves no
// edge longer than `longest`, and folds only vertices that `same(u, v)` lets go together (where a seam must stay).
// An open edge is kept where it is (its vertices are not folded away).
//   decimate(positions, triangles, {error, longest, same?}) → {keep: Uint32Array (the vertices left, in order),
//     triangles: Uint32Array (indices into keep)}
export function decimate(P, T, { error, longest, same = () => true }) {
  const nv = P.length / 3, nt = T.length / 3, Q = new Float64Array(nv * 10), tri = Int32Array.from(T), alive = new Uint8Array(nt).fill(1);
  // each vertex's triangles (grown as folds move them), and its quadric
  const vt = Array.from({ length: nv }, () => []);
  for (let t = 0; t < nt; t++) for (let e = 0; e < 3; e++) vt[tri[t * 3 + e]].push(t);
  const plane = t => {
    const a = tri[t * 3] * 3, b = tri[t * 3 + 1] * 3, c = tri[t * 3 + 2] * 3;
    const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], wx = P[c] - P[a], wy = P[c + 1] - P[a + 1], wz = P[c + 2] - P[a + 2];
    let nx = uy * wz - uz * wy, ny = uz * wx - ux * wz, nz = ux * wy - uy * wx; const l = Math.hypot(nx, ny, nz);
    if (l < 1e-18) return null;
    nx /= l; ny /= l; nz /= l; return [nx, ny, nz, -(nx * P[a] + ny * P[a + 1] + nz * P[a + 2]), l / 2];
  };
  for (let t = 0; t < nt; t++) {
    const p = plane(t); if (!p) continue;
    const [a, b, c, d, w] = p, q = [a * a, a * b, a * c, a * d, b * b, b * c, b * d, c * c, c * d, d * d];
    for (let e = 0; e < 3; e++) { const v = tri[t * 3 + e] * 10; for (let k = 0; k < 10; k++) Q[v + k] += q[k] * w; }
  }
  // an open edge (one triangle): its vertices stay
  const fixed = new Uint8Array(nv), edges = new Map(), ek = (a, b) => a < b ? a * nv + b : b * nv + a;
  for (let t = 0; t < nt; t++) for (let e = 0; e < 3; e++) { const k = ek(tri[t * 3 + e], tri[t * 3 + (e + 1) % 3]); edges.set(k, (edges.get(k) || 0) + 1); }
  for (const [k, n] of edges) if (n !== 2) { fixed[Math.floor(k / nv)] = 1; fixed[k % nv] = 1; }
  const cost = (u, v) => { const q = u * 10, r = v * 10, x = P[v * 3], y = P[v * 3 + 1], z = P[v * 3 + 2]; let s = 0; for (const o of [q, r]) s += Q[o] * x * x + 2 * Q[o + 1] * x * y + 2 * Q[o + 2] * x * z + 2 * Q[o + 3] * x + Q[o + 4] * y * y + 2 * Q[o + 5] * y * z + 2 * Q[o + 6] * y + Q[o + 7] * z * z + 2 * Q[o + 8] * z + Q[o + 9]; return s; };
  // (the quadrics are weighed by area: a fold's cost divided by the area round it is a squared distance)
  const area = u => { let a = 0; for (const t of vt[u]) if (alive[t]) { const p = plane(t); if (p) a += p[4]; } return a || 1e-12; };
  const heap = new Heap(), stamp = new Uint32Array(nv), E2 = error * error, L2 = longest * longest;
  const offer = u => {
    stamp[u]++; if (fixed[u]) return;
    const seen = new Set();
    for (const t of vt[u]) if (alive[t]) for (let e = 0; e < 3; e++) { const v = tri[t * 3 + e]; if (v === u || seen.has(v)) continue; seen.add(v); if (!same(u, v)) continue; const c = cost(u, v) / (area(u) + area(v)); if (c <= E2) heap.push(c, u, v, stamp[u]); }
  };
  for (let u = 0; u < nv; u++) offer(u);
  const gone = new Uint8Array(nv), d = (a, b) => (P[a * 3] - P[b * 3]) ** 2 + (P[a * 3 + 1] - P[b * 3 + 1]) ** 2 + (P[a * 3 + 2] - P[b * 3 + 2]) ** 2;
  while (heap.size) {
    const [, u, v, s] = heap.pop();
    if (gone[u] || gone[v] || s !== stamp[u]) continue;
    // the triangles round u: those on the edge u–v go, the others take v in u's place
    const round = vt[u].filter(t => alive[t]), onEdge = round.filter(t => tri[t * 3] === v || tri[t * 3 + 1] === v || tri[t * 3 + 2] === v);
    if (onEdge.length !== 2) continue;
    // (no more shared neighbours than the two across the edge: else the surface pinches)
    const nu = new Set(), nvv = new Set();
    for (const t of round) for (let e = 0; e < 3; e++) nu.add(tri[t * 3 + e]);
    for (const t of vt[v]) if (alive[t]) for (let e = 0; e < 3; e++) nvv.add(tri[t * 3 + e]);
    let shared = 0; for (const w of nu) if (w !== u && w !== v && nvv.has(w)) shared++;
    if (shared !== 2) continue;
    // no triangle turned over or made a sliver, no edge too long
    let ok = true;
    for (const t of round) {
      if (onEdge.includes(t)) continue;
      const before = plane(t); const k = [0, 1, 2].find(e => tri[t * 3 + e] === u); tri[t * 3 + k] = v; const after = plane(t); tri[t * 3 + k] = u;
      if (!before || !after || before[0] * after[0] + before[1] * after[1] + before[2] * after[2] < 0.3) { ok = false; break; }
      for (let e = 0; e < 3; e++) { const w = tri[t * 3 + e]; if (w !== u && d(w, v) > L2) { ok = false; break; } }
      if (!ok) break;
    }
    if (!ok) continue;
    for (const t of onEdge) alive[t] = 0;
    for (const t of round) if (alive[t]) { const k = [0, 1, 2].find(e => tri[t * 3 + e] === u); tri[t * 3 + k] = v; vt[v].push(t); }
    for (let k = 0; k < 10; k++) Q[v * 10 + k] += Q[u * 10 + k];
    gone[u] = 1;
    // the folds round v cost anew
    offer(v); for (const w of nvv) if (!gone[w] && w !== v) offer(w); for (const w of nu) if (!gone[w] && w !== v && w !== u) offer(w);
  }
  const keep = [], at = new Int32Array(nv).fill(-1);
  for (let t = 0; t < nt; t++) if (alive[t]) for (let e = 0; e < 3; e++) { const v = tri[t * 3 + e]; if (at[v] < 0) { at[v] = keep.length; keep.push(v); } }
  const out = []; for (let t = 0; t < nt; t++) if (alive[t]) out.push(at[tri[t * 3]], at[tri[t * 3 + 1]], at[tri[t * 3 + 2]]);
  return { keep: Uint32Array.from(keep), triangles: Uint32Array.from(out) };
}

// a binary heap of [cost, u, v, stamp], the cheapest on top
class Heap {
  constructor() { this.a = []; }
  get size() { return this.a.length; }
  push(c, u, v, s) { const a = this.a; a.push([c, u, v, s]); let i = a.length - 1; while (i > 0) { const p = (i - 1) >> 1; if (a[p][0] <= a[i][0]) break; [a[p], a[i]] = [a[i], a[p]]; i = p; } }
  pop() {
    const a = this.a, top = a[0], last = a.pop();
    if (a.length) { a[0] = last; let i = 0; for (;;) { const l = i * 2 + 1, r = l + 1; let m = i; if (l < a.length && a[l][0] < a[m][0]) m = l; if (r < a.length && a[r][0] < a[m][0]) m = r; if (m === i) break; [a[m], a[i]] = [a[i], a[m]]; i = m; } }
    return top;
  }
}
