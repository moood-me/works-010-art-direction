// A spatial hash of points — the one the engine searches points by: the body's skin (src/solids.js), a garment's points
// against itself and under another (src/cloth/sim.js), a garment laid on the body (src/cloth/patterns.js). Each point in
// the cell of `cell` metres it lies in, counted into flat arrays that are kept and grown (building it again makes
// nothing new); a bucket may hold more than one cell (the distances tell them apart).
//   const h = cellHash(cell)
//   h.build(P, n, ids?)        P's first n points (or those of ids, an index array); h.items hold their indices into P
//   h.bucket(ix, iy, iz)       a cell's bucket: its points are h.items[h.start[b] … h.start[b + 1]]
//   h.nearest(P, x, y, z, reach) → the point of P nearest (x, y, z) within reach, or −1
export function cellHash(cell) {
  let size = 0, start = new Int32Array(1), fill = new Int32Array(1), items = new Int32Array(0), keys = new Int32Array(0);
  const h = {
    cell, start, items,
    bucket: (a, b, c) => (((a * 73856093) ^ (b * 19349663) ^ (c * 83492791)) >>> 0) & (size - 1),
    build(P, n, ids = null) {
      // (twice as many buckets as points, at least 1024)
      let want = 1024; while (want < n * 2) want <<= 1;
      if (want !== size) { size = want; start = h.start = new Int32Array(size + 1); fill = new Int32Array(size + 1); }
      if (items.length < n) { items = h.items = new Int32Array(n); keys = new Int32Array(n); }
      start.fill(0); const inv = 1 / cell;
      for (let k = 0; k < n; k++) { const i = ids ? ids[k] : k, b = h.bucket(Math.floor(P[i * 3] * inv), Math.floor(P[i * 3 + 1] * inv), Math.floor(P[i * 3 + 2] * inv)); keys[k] = b; start[b + 1]++; }
      for (let b = 0; b < size; b++) start[b + 1] += start[b];
      fill.set(start);
      for (let k = 0; k < n; k++) items[fill[keys[k]]++] = ids ? ids[k] : k;
      return h;
    },
    nearest(P, x, y, z, reach) {
      const inv = 1 / cell, cx = Math.floor(x * inv), cy = Math.floor(y * inv), cz = Math.floor(z * inv), R = Math.ceil(reach * inv);
      let best = -1, bd = reach * reach;
      // (shell by shell outwards, until no nearer point can be farther out)
      for (let r = 0; r <= R && (best < 0 || Math.sqrt(bd) > (r - 1) * cell); r++)
        for (let a = -r; a <= r; a++) for (let b = -r; b <= r; b++) for (let c = -r; c <= r; c++) {
          if (Math.max(Math.abs(a), Math.abs(b), Math.abs(c)) !== r) continue;
          const k = h.bucket(cx + a, cy + b, cz + c);
          for (let e = start[k], end = start[k + 1]; e < end; e++) { const i = items[e], d = (P[i * 3] - x) ** 2 + (P[i * 3 + 1] - y) ** 2 + (P[i * 3 + 2] - z) ** 2; if (d < bd) { bd = d; best = i; } }
        }
      return best;
    },
  };
  return h;
}
