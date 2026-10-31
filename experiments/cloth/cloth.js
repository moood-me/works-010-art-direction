// Cloth: a garment as a sheet of fabric (XPBD, small steps). Each point has the mass of the fabric around it; edges
// hold against stretching (and give way when pushed together, so the cloth folds instead of shrinking); hinges hold
// against bending as the fabric's bending rigidity says (its bending length); the air pushes on each triangle as it
// faces the flow (wind and the cloth's own motion); the body and the garments under it are solid — the cloth stays a
// fabric's thickness outside them, with friction; the floor too; the cloth doesn't go through itself (points keep
// apart). What holds a garment on: its waistband or neckline gripping the body (points pulled to where the skin carries
// them), and the cloth can't stretch farther from them than it is long (tethers along the cloth).

// ———— a spatial hash: points into cells, to find what is near ————
export class Grid {
  constructor(cell, max) {
    this.cell = cell; this.size = 1; while (this.size < max * 2) this.size <<= 1;
    this.start = new Int32Array(this.size + 1); this.items = new Int32Array(max); this.n = 0;
  }
  key(ix, iy, iz) { return (Math.imul(ix, 92837111) ^ Math.imul(iy, 689287499) ^ Math.imul(iz, 283923481)) & (this.size - 1); }
  build(pos, n) {
    const { start, items, cell } = this, inv = 1 / cell; start.fill(0); this.n = n;
    if (items.length < n) this.items = new Int32Array(n);
    for (let i = 0; i < n; i++) start[this.key(Math.floor(pos[i * 3] * inv), Math.floor(pos[i * 3 + 1] * inv), Math.floor(pos[i * 3 + 2] * inv))]++;
    let s = 0; for (let h = 0; h < this.size; h++) { s += start[h]; start[h] = s; } start[this.size] = s;
    for (let i = 0; i < n; i++) { const h = this.key(Math.floor(pos[i * 3] * inv), Math.floor(pos[i * 3 + 1] * inv), Math.floor(pos[i * 3 + 2] * inv)); this.items[--start[h]] = i; }
  }
}

// neighbours of each point along a mesh's edges (compressed rows)
export function adjacency(n, tris) {
  const sets = Array.from({ length: n }, () => new Set());
  for (let t = 0; t < tris.length; t += 3) for (let k = 0; k < 3; k++) { const a = tris[t + k], b = tris[t + (k + 1) % 3]; sets[a].add(b); sets[b].add(a); }
  const start = new Int32Array(n + 1); for (let i = 0; i < n; i++) start[i + 1] = start[i] + sets[i].size;
  const list = new Int32Array(start[n]); for (let i = 0; i < n; i++) { let k = start[i]; for (const j of sets[i]) list[k++] = j; }
  return { start, list };
}
// from a point of a surface near the last time, to the nearest now: step to a nearer neighbour while there is one
function climb(S, i, x, y, z) {
  const P = S.pos, A = S.adj;
  let d = (P[i * 3] - x) ** 2 + (P[i * 3 + 1] - y) ** 2 + (P[i * 3 + 2] - z) ** 2;
  for (let it = 0; it < 12; it++) {
    let best = -1;
    for (let k = A.start[i], e = A.start[i + 1]; k < e; k++) { const j = A.list[k], dj = (P[j * 3] - x) ** 2 + (P[j * 3 + 1] - y) ** 2 + (P[j * 3 + 2] - z) ** 2; if (dj < d) { d = dj; best = j; } }
    if (best < 0) break; i = best;
  }
  return i;
}

// the same, staying on one limb of the body (S.limb: each point's limb)
function climbOn(S, i, x, y, z, limb) {
  const P = S.pos, A = S.adj, L = S.limb;
  let d = (P[i * 3] - x) ** 2 + (P[i * 3 + 1] - y) ** 2 + (P[i * 3 + 2] - z) ** 2;
  for (let it = 0; it < 12; it++) {
    let best = -1;
    for (let k = A.start[i], e = A.start[i + 1]; k < e; k++) { const j = A.list[k]; if (L[j] !== limb) continue; const dj = (P[j * 3] - x) ** 2 + (P[j * 3 + 1] - y) ** 2 + (P[j * 3 + 2] - z) ** 2; if (dj < d) { d = dj; best = j; } }
    if (best < 0) break; i = best;
  }
  return i;
}

// ———— what a cloth collides with: the body's skin and the garments under it, each a surface of points with normals ————
// a source: {pos, nrm, prev, n, off (how far outside its points its surface is; offs: more, point by point), grid, adj,
// move (how far any of its points went this step)}
export function nearestPerSource(sources, x, y, z, out) {
  // out[s] = index of the nearest point of source s within reach, or -1
  for (let s = 0; s < sources.length; s++) {
    const S = sources[s], g = S.grid, inv = 1 / g.cell, cx = Math.floor(x * inv), cy = Math.floor(y * inv), cz = Math.floor(z * inv), P = S.pos;
    let best = -1, bd = g.cell * g.cell * 2.25;
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
      const h = g.key(cx + dx, cy + dy, cz + dz), e = g.start[h + 1];
      for (let k = g.start[h]; k < e; k++) {
        const i = g.items[k], ax = P[i * 3] - x, ay = P[i * 3 + 1] - y, az = P[i * 3 + 2] - z, d = ax * ax + ay * ay + az * az;
        if (d < bd) { bd = d; best = i; }
      }
    }
    out[s] = best;
  }
}

export function nearestIn(S, x, y, z) {
  const g = S.grid, inv = 1 / g.cell, cx = Math.floor(x * inv), cy = Math.floor(y * inv), cz = Math.floor(z * inv), P = S.pos;
  let best = -1, bd = g.cell * g.cell * 2.25;
  for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
    const h = g.key(cx + dx, cy + dy, cz + dz), e = g.start[h + 1];
    for (let k = g.start[h]; k < e; k++) {
      const i = g.items[k], ax = P[i * 3] - x, ay = P[i * 3 + 1] - y, az = P[i * 3 + 2] - z, d = ax * ax + ay * ay + az * az;
      if (d < bd) { bd = d; best = i; }
    }
  }
  return best;
}

// ———— a garment's cloth ————
// o: {pos: rest positions (the garment as cut and put on), tris, fabric, hold: Float32Array per point (0 free … 1 held
// where the skin carries it), skinJ/skinW (each point's four joints and weights, to carry held points)}
export class Cloth {
  constructor(o) {
    const n = o.pos.length / 3, F = o.fabric, T = o.tris;
    Object.assign(this, { n, tris: T, fabric: F, hold: o.hold, skinJ: o.skinJ, skinW: o.skinW, name: o.name });
    this.rest = Float32Array.from(o.pos);
    this.x = Float32Array.from(o.pos); this.v = new Float32Array(n * 3); this.p = Float32Array.from(o.pos);
    this.target = Float32Array.from(o.pos); this.nrm = new Float32Array(n * 3); this.sgn = new Float32Array(n).fill(1);
    // masses from the fabric's weight per square metre
    const m = new Float64Array(n); let area = 0;
    for (let t = 0; t < T.length; t += 3) { const A = triArea(this.x, T[t], T[t + 1], T[t + 2]); area += A; for (let k = 0; k < 3; k++) m[T[t + k]] += A / 3 * F.density; }
    // (points of the smallest triangles are given at least a share of a usual point's mass: the cloth weighs the same
    // within a few per cent, and slivers don't fly off)
    const med = Float64Array.from(m).sort()[n >> 1];
    for (let i = 0; i < n; i++) m[i] = Math.max(m[i], med * 0.4);
    this.area = area; this.mass = m; this.w = Float32Array.from(m, v => 1 / Math.max(v, 1e-9));
    // edges and hinges
    const em = new Map(), hinge = [];
    for (let t = 0; t < T.length; t += 3) for (let k = 0; k < 3; k++) {
      const a = T[t + k], b = T[t + (k + 1) % 3], c = T[t + (k + 2) % 3], key = a < b ? a * n + b : b * n + a;
      const e = em.get(key); if (e) e.push(c); else em.set(key, [Math.min(a, b), Math.max(a, b), c]);
    }
    const E = [], H = [];
    const BE = [];
    for (const e of em.values()) { E.push(e[0], e[1]); if (e.length === 4) H.push(e[0], e[1], e[2], e[3]); else if (e.length === 3) BE.push(e[0], e[1], e[2]); }
    this.BE = Uint32Array.from(BE); this.rim = new Float32Array(n * 3);
    this.E = Uint32Array.from(E); this.EL = new Float32Array(E.length / 2);
    let sum = 0; for (let k = 0; k < this.EL.length; k++) { this.EL[k] = dist(this.x, this.E[k * 2], this.E[k * 2 + 1]); sum += this.EL[k]; }
    this.edge = sum / this.EL.length;
    this.H = Uint32Array.from(H); this.HC = new Float32Array(H.length / 4);
    // each hinge's bending compliance from the fabric's rigidity B (N·m): k = 3 B e / (h1 + h2)
    for (let k = 0; k < this.HC.length; k++) {
      const [a, b, c, d] = [H[k * 4], H[k * 4 + 1], H[k * 4 + 2], H[k * 4 + 3]], e = dist(this.x, a, b) || 1e-4;
      const h1 = 2 * triArea(this.x, a, b, c) / e, h2 = 2 * triArea(this.x, a, b, d) / e;
      // a hinge of slivers says nothing about the cloth's curvature: left out
      this.HC[k] = Math.min(h1, h2) < this.edge * 0.25 ? -1 : (h1 + h2) / (3 * F.bend * e);
    }
    this.selfGrid = new Grid(Math.max(F.thick * 2, this.edge * 0.55), n);
    this.normals();
  }
  // tethers: each point no farther from the nearest held point than the cloth between them is long
  tether(slack) {
    const n = this.n, d = new Float64Array(n).fill(Infinity), from = new Int32Array(n).fill(-1), adj = Array.from({ length: n }, () => []);
    for (let k = 0; k < this.EL.length; k++) { const a = this.E[k * 2], b = this.E[k * 2 + 1]; adj[a].push(b, this.EL[k]); adj[b].push(a, this.EL[k]); }
    const heap = [];
    const push = (i, v) => { heap.push([v, i]); let c = heap.length - 1; while (c > 0) { const p = (c - 1) >> 1; if (heap[p][0] <= heap[c][0]) break; [heap[p], heap[c]] = [heap[c], heap[p]]; c = p; } };
    const pop = () => { const top = heap[0], last = heap.pop(); if (heap.length) { heap[0] = last; let c = 0; for (;;) { const l = c * 2 + 1, r = l + 1; let m = c; if (l < heap.length && heap[l][0] < heap[m][0]) m = l; if (r < heap.length && heap[r][0] < heap[m][0]) m = r; if (m === c) break; [heap[m], heap[c]] = [heap[c], heap[m]]; c = m; } } return top; };
    for (let i = 0; i < n; i++) if (this.hold[i] > 0.5) { d[i] = 0; from[i] = i; push(i, 0); }
    while (heap.length) { const [v, i] = pop(); if (v > d[i]) continue; const a = adj[i]; for (let k = 0; k < a.length; k += 2) { const j = a[k], nv = v + a[k + 1]; if (nv < d[j]) { d[j] = nv; from[j] = from[i]; push(j, nv); } } }
    this.anchor = from; this.reach = Float32Array.from(d, v => Number.isFinite(v) ? v * slack : 0);
  }
  // at the garment's edges, which way is off the cloth (in its surface, away from it): what lies past the edge is not
  // under this cloth
  rims() {
    const { x, BE, rim } = this; rim.fill(0);
    for (let k = 0; k < BE.length; k += 3) {
      const a = BE[k] * 3, b = BE[k + 1] * 3, c = BE[k + 2] * 3;
      let ex = x[b] - x[a], ey = x[b + 1] - x[a + 1], ez = x[b + 2] - x[a + 2]; const el = Math.hypot(ex, ey, ez) || 1; ex /= el; ey /= el; ez /= el;
      let ox = (x[a] + x[b]) / 2 - x[c], oy = (x[a + 1] + x[b + 1]) / 2 - x[c + 1], oz = (x[a + 2] + x[b + 2]) / 2 - x[c + 2];
      const d = ox * ex + oy * ey + oz * ez; ox -= d * ex; oy -= d * ey; oz -= d * ez;
      rim[a] += ox; rim[a + 1] += oy; rim[a + 2] += oz; rim[b] += ox; rim[b + 1] += oy; rim[b + 2] += oz;
    }
  }
  normals() {
    const { x, tris: T, nrm } = this; nrm.fill(0);
    for (let t = 0; t < T.length; t += 3) {
      const a = T[t] * 3, b = T[t + 1] * 3, c = T[t + 2] * 3;
      const ux = x[b] - x[a], uy = x[b + 1] - x[a + 1], uz = x[b + 2] - x[a + 2], vx = x[c] - x[a], vy = x[c + 1] - x[a + 1], vz = x[c + 2] - x[a + 2];
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      nrm[a] += nx; nrm[a + 1] += ny; nrm[a + 2] += nz; nrm[b] += nx; nrm[b + 1] += ny; nrm[b + 2] += nz; nrm[c] += nx; nrm[c + 1] += ny; nrm[c + 2] += nz;
    }
    for (let i = 0; i < this.n; i++) { const s = this.sgn[i] / (Math.hypot(nrm[i * 3], nrm[i * 3 + 1], nrm[i * 3 + 2]) || 1); nrm[i * 3] *= s; nrm[i * 3 + 1] *= s; nrm[i * 3 + 2] *= s; }
  }

  // one small step of h seconds: sources — what it collides with (the body first, then the garments under it)
  step(h, sources, wind, t) {
    const { n, x, v, p, w, fabric: F } = this, g = -9.81, damp = Math.exp(-F.damping * h), odd = (this.sub = (this.sub || 0) + 1) & 1;
    // the air on each triangle: wind minus the cloth's own velocity, as it meets the triangle (every other step, for two)
    if (F.air > 0 && odd) this.air(2 * h, wind, t);
    for (let i = 0; i < n; i++) {
      const k = i * 3;
      v[k] *= damp; v[k + 1] = (v[k + 1] + g * h) * damp; v[k + 2] *= damp;
      const sp = Math.hypot(v[k], v[k + 1], v[k + 2]); if (sp > 12) { const s = 12 / sp; v[k] *= s; v[k + 1] *= s; v[k + 2] *= s; }
      p[k] = x[k]; p[k + 1] = x[k + 1]; p[k + 2] = x[k + 2];
      x[k] += v[k] * h; x[k + 1] += v[k + 1] * h; x[k + 2] += v[k + 2] * h;
    }
    const h2 = 1 / (h * h);
    // (lengths twice: bending pushes against them, and the cloth must not give in length to it)
    this.stretch(h2); this.bend(h2); this.stretch(h2); this.held(h); this.tethers();
    if (F.self && !odd) this.selfApart();
    this.collide(sources, h);
    const ih = 1 / h; let mv = 0;
    for (let k = 0; k < n * 3; k += 3) {
      const dx = x[k] - p[k], dy = x[k + 1] - p[k + 1], dz = x[k + 2] - p[k + 2];
      v[k] = dx * ih; v[k + 1] = dy * ih; v[k + 2] = dz * ih; const m = dx * dx + dy * dy + dz * dz; if (m > mv) mv = m;
    }
    this.moved = Math.sqrt(mv);
  }
  stretch(h2) {
    const { x, w, E, EL, fabric: F } = this, aT = 1 / (F.stretch) * h2, aC = 1 / (F.stretch * F.compress) * h2;
    for (let k = 0; k < EL.length; k++) {
      const a = E[k * 2] * 3, b = E[k * 2 + 1] * 3, wa = w[a / 3], wb = w[b / 3];
      const dx = x[b] - x[a], dy = x[b + 1] - x[a + 1], dz = x[b + 2] - x[a + 2], l = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (l < 1e-9) continue;
      const C = l - EL[k], al = C > 0 ? aT : aC, s = C / ((wa + wb + al) * l);
      x[a] += wa * s * dx; x[a + 1] += wa * s * dy; x[a + 2] += wa * s * dz;
      x[b] -= wb * s * dx; x[b + 1] -= wb * s * dy; x[b + 2] -= wb * s * dz;
    }
  }
  // the dihedral angle at each inner edge, toward flat (fabric is flat; its own rigidity resists bending)
  bend(h2) {
    const { x, w, H, HC } = this;
    for (let k = 0; k < HC.length; k++) {
      if (HC[k] < 0) continue;
      const i1 = H[k * 4], i2 = H[k * 4 + 1], i3 = H[k * 4 + 2], i4 = H[k * 4 + 3];
      const ox = x[i1 * 3], oy = x[i1 * 3 + 1], oz = x[i1 * 3 + 2];
      const p2x = x[i2 * 3] - ox, p2y = x[i2 * 3 + 1] - oy, p2z = x[i2 * 3 + 2] - oz;
      const p3x = x[i3 * 3] - ox, p3y = x[i3 * 3 + 1] - oy, p3z = x[i3 * 3 + 2] - oz;
      const p4x = x[i4 * 3] - ox, p4y = x[i4 * 3 + 1] - oy, p4z = x[i4 * 3 + 2] - oz;
      // n1 = p2×p3, n2 = p2×p4
      let n1x = p2y * p3z - p2z * p3y, n1y = p2z * p3x - p2x * p3z, n1z = p2x * p3y - p2y * p3x;
      let n2x = p2y * p4z - p2z * p4y, n2y = p2z * p4x - p2x * p4z, n2z = p2x * p4y - p2y * p4x;
      const l1 = Math.sqrt(n1x * n1x + n1y * n1y + n1z * n1z), l2 = Math.sqrt(n2x * n2x + n2y * n2y + n2z * n2z);
      if (l1 < 1e-12 || l2 < 1e-12) continue;
      n1x /= l1; n1y /= l1; n1z /= l1; n2x /= l2; n2y /= l2; n2z /= l2;
      // d = n1·n2 is −1 when the cloth is flat at this edge: C = acos(d) − π (Müller et al. 2007; with these normals the
      // q_i below are −∂d/∂p_i, checked by finite differences)
      let d = n1x * n2x + n1y * n2y + n1z * n2z; d = d > 1 ? 1 : d < -1 ? -1 : d;
      const C = Math.acos(d) - Math.PI; if (C > -1e-3) continue;
      const q3x = ((p2y * n2z - p2z * n2y) + (n1y * p2z - n1z * p2y) * d) / l1, q3y = ((p2z * n2x - p2x * n2z) + (n1z * p2x - n1x * p2z) * d) / l1, q3z = ((p2x * n2y - p2y * n2x) + (n1x * p2y - n1y * p2x) * d) / l1;
      const q4x = ((p2y * n1z - p2z * n1y) + (n2y * p2z - n2z * p2y) * d) / l2, q4y = ((p2z * n1x - p2x * n1z) + (n2z * p2x - n2x * p2z) * d) / l2, q4z = ((p2x * n1y - p2y * n1x) + (n2x * p2y - n2y * p2x) * d) / l2;
      const q2x = -((p3y * n2z - p3z * n2y) + (n1y * p3z - n1z * p3y) * d) / l1 - ((p4y * n1z - p4z * n1y) + (n2y * p4z - n2z * p4y) * d) / l2;
      const q2y = -((p3z * n2x - p3x * n2z) + (n1z * p3x - n1x * p3z) * d) / l1 - ((p4z * n1x - p4x * n1z) + (n2z * p4x - n2x * p4z) * d) / l2;
      const q2z = -((p3x * n2y - p3y * n2x) + (n1x * p3y - n1y * p3x) * d) / l1 - ((p4x * n1y - p4y * n1x) + (n2x * p4y - n2y * p4x) * d) / l2;
      const q1x = -q2x - q3x - q4x, q1y = -q2y - q3y - q4y, q1z = -q2z - q3z - q4z;
      // ∇C = q / sqrt(1 − d²); Δλ = −C / (Σ w|∇C|² + α/h²); Δx_i = w_i ∇C_i Δλ
      const s = Math.sqrt(1 - d * d); if (s < 1e-6) continue;
      const w1 = w[i1], w2 = w[i2], w3 = w[i3], w4 = w[i4];
      const sum = (w1 * (q1x * q1x + q1y * q1y + q1z * q1z) + w2 * (q2x * q2x + q2y * q2y + q2z * q2z) + w3 * (q3x * q3x + q3y * q3y + q3z * q3z) + w4 * (q4x * q4x + q4y * q4y + q4z * q4z)) / (s * s);
      const dl = -C / (sum + HC[k] * h2), f = dl / s;
      x[i1 * 3] += w1 * q1x * f; x[i1 * 3 + 1] += w1 * q1y * f; x[i1 * 3 + 2] += w1 * q1z * f;
      x[i2 * 3] += w2 * q2x * f; x[i2 * 3 + 1] += w2 * q2y * f; x[i2 * 3 + 2] += w2 * q2z * f;
      x[i3 * 3] += w3 * q3x * f; x[i3 * 3 + 1] += w3 * q3y * f; x[i3 * 3 + 2] += w3 * q3z * f;
      x[i4 * 3] += w4 * q4x * f; x[i4 * 3 + 1] += w4 * q4y * f; x[i4 * 3 + 2] += w4 * q4z * f;
    }
  }
  // held points go where the skin carries them, as firmly as they are held
  // (as an elastic band would: a held point goes a share of the way each step, the share as it is held)
  held(h) {
    const { x, hold, target } = this, rate = h / 0.012;
    for (let i = 0; i < this.n; i++) {
      const s = hold[i]; if (s <= 0) continue;
      const k = i * 3, f = Math.min(1, s * rate);
      x[k] += (target[k] - x[k]) * f; x[k + 1] += (target[k + 1] - x[k + 1]) * f; x[k + 2] += (target[k + 2] - x[k + 2]) * f;
    }
  }
  tethers() {
    const { x, anchor, reach } = this; if (!anchor) return;
    for (let i = 0; i < this.n; i++) {
      const a = anchor[i]; if (a < 0 || a === i) continue;
      const dx = x[i * 3] - x[a * 3], dy = x[i * 3 + 1] - x[a * 3 + 1], dz = x[i * 3 + 2] - x[a * 3 + 2], l = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (l > reach[i]) { const s = reach[i] / l; x[i * 3] = x[a * 3] + dx * s; x[i * 3 + 1] = x[a * 3 + 1] + dy * s; x[i * 3 + 2] = x[a * 3 + 2] + dz * s; }
    }
  }
  // points of the cloth keep apart, unless they were near at rest (neighbours along the cloth)
  selfApart() {
    const { x, rest, n, w, selfGrid: G } = this, r = G.cell, r2 = r * r, inv = 1 / r;
    G.build(x, n);
    for (let i = 0; i < n; i++) {
      const xi = x[i * 3], yi = x[i * 3 + 1], zi = x[i * 3 + 2], cx = Math.floor(xi * inv), cy = Math.floor(yi * inv), cz = Math.floor(zi * inv);
      for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
        const hh = G.key(cx + dx, cy + dy, cz + dz), e = G.start[hh + 1];
        for (let k = G.start[hh]; k < e; k++) {
          const j = G.items[k]; if (j <= i) continue;
          const ax = x[j * 3] - x[i * 3], ay = x[j * 3 + 1] - x[i * 3 + 1], az = x[j * 3 + 2] - x[i * 3 + 2], d2 = ax * ax + ay * ay + az * az;
          if (d2 >= r2 || d2 < 1e-14) continue;
          const rx = rest[j * 3] - rest[i * 3], ry = rest[j * 3 + 1] - rest[i * 3 + 1], rz = rest[j * 3 + 2] - rest[i * 3 + 2];
          if (rx * rx + ry * ry + rz * rz < r2 * 2.6) continue;
          const d = Math.sqrt(d2), c = (r - d) / d / (w[i] + w[j]);
          x[i * 3] -= ax * c * w[i]; x[i * 3 + 1] -= ay * c * w[i]; x[i * 3 + 2] -= az * c * w[i];
          x[j * 3] += ax * c * w[j]; x[j * 3 + 1] += ay * c * w[j]; x[j * 3 + 2] += az * c * w[j];
        }
      }
    }
  }
  // the body and the garments under: stay a thickness outside the nearest surface of each, with friction
  collide(sources, h) {
    const { x, p, n, fabric: F } = this, r = F.thick, mu = F.friction, S = sources.length;
    // what is surely far from every surface is not looked at: each point keeps how far it was at least, less what it
    // and the surfaces have moved since; near ones are looked up afresh every other step and in between follow their
    // nearest point over the surface (a step's following can't jump to another part of the body coming near)
    if (!this.near || this.near.length !== n * S) { this.near = new Int32Array(n * S).fill(-1); this.clear = new Float32Array(n); }
    const masks = this.masks, near = this.near, clear = this.clear, fresh = (this.tick = (this.tick || 0) + 1) % 2 === 0;
    let move = 0, reach = 0; for (const src of sources) { move = Math.max(move, src.move || 0); reach = Math.max(reach, src.off + (src.offs ? 0.005 : 0)); }
    reach += r + 0.003;
    for (let i = 0; i < n; i++) {
      const k = i * 3;
      clear[i] -= move + Math.sqrt((x[k] - p[k]) ** 2 + (x[k + 1] - p[k + 1]) ** 2 + (x[k + 2] - p[k + 2]) ** 2);
      if (clear[i] > reach) { if (x[k + 1] >= r) continue; }
      else {
        let c = Infinity;
        for (let s = S - 1; s >= 0; s--) {
          if (masks && masks[s] && !masks[s][i]) continue;
          const b0 = near[i * S + s];
          const b = fresh || b0 < 0 ? nearestIn(sources[s], x[k], x[k + 1], x[k + 2]) : climb(sources[s], b0, x[k], x[k + 1], x[k + 2]);
          near[i * S + s] = b;
          if (b < 0) { c = Math.min(c, sources[s].grid.cell); continue; }
          const src = sources[s], P = src.pos, N = src.nrm, bk = b * 3;
          // pinched: the nearest surface now faces the other way from the one it was by, and it is still under that one
          // (a knee or an elbow folded on it, two legs pressed together — skin into skin): it is left where it is, not
          // pushed through to the far side
          if (b0 >= 0 && b !== b0) {
            const q = b0 * 3;
            if (N[q] * N[bk] + N[q + 1] * N[bk + 1] + N[q + 2] * N[bk + 2] < -0.3 &&
                (x[k] - P[q]) * N[q] + (x[k + 1] - P[q + 1]) * N[q + 1] + (x[k + 2] - P[q + 2]) * N[q + 2] < r + src.off) { near[i * S + s] = b0; c = 0; continue; }
          }
          const ex = x[k] - P[bk], ey = x[k + 1] - P[bk + 1], ez = x[k + 2] - P[bk + 2];
          c = Math.min(c, Math.sqrt(ex * ex + ey * ey + ez * ez) - src.off - 0.01);
          const R = src.rim; if (R && (R[bk] || R[bk + 1] || R[bk + 2]) && ex * R[bk] + ey * R[bk + 1] + ez * R[bk + 2] > 0) continue;
          this.contact(k, src, b, r, mu);
          // a sleeve or a trouser leg is round its own limb: where another part of the body is nearer (a leg pressed to
          // the other, an arm to the side), it keeps outside its own limb too, and its own limb has the last word — it
          // goes into the other one (hidden between them), not through its own
          if (s === 0 && this.home && this.home[i] && src.limb[b] !== this.home[i]) {
            this.homeNear[i] = climbOn(src, this.homeNear[i], x[k], x[k + 1], x[k + 2], this.home[i]);
            this.contact(k, src, this.homeNear[i], r, mu);
          }
        }
        clear[i] = c;
      }
      // the floor
      if (x[k + 1] < r) {
        const pen = r - x[k + 1]; x[k + 1] = r;
        const tx = x[k] - p[k], tz = x[k + 2] - p[k + 2], tl = Math.hypot(tx, tz), mf = 0.8;
        if (tl > 1e-12) { const f = tl < mf * pen ? 1 : mf * pen / tl; x[k] -= tx * f; x[k + 2] -= tz * f; }
      }
    }
  }
  // one point against one surface point: out to the thickness along its normal, its slide over it held back by friction
  contact(k, src, b, r, mu) {
    const { x, p } = this, P = src.pos, N = src.nrm, Q = src.prev, bk = b * 3;
    const d = (x[k] - P[bk]) * N[bk] + (x[k + 1] - P[bk + 1]) * N[bk + 1] + (x[k + 2] - P[bk + 2]) * N[bk + 2], want = r + src.off + (src.offs ? src.offs[b] : 0);
    if (d >= want) return;
    const pen = want - d;
    x[k] += N[bk] * pen; x[k + 1] += N[bk + 1] * pen; x[k + 2] += N[bk + 2] * pen;
    let tx = (x[k] - p[k]) - (P[bk] - Q[bk]), ty = (x[k + 1] - p[k + 1]) - (P[bk + 1] - Q[bk + 1]), tz = (x[k + 2] - p[k + 2]) - (P[bk + 2] - Q[bk + 2]);
    const dn = tx * N[bk] + ty * N[bk + 1] + tz * N[bk + 2]; tx -= dn * N[bk]; ty -= dn * N[bk + 1]; tz -= dn * N[bk + 2];
    const tl = Math.sqrt(tx * tx + ty * ty + tz * tz);
    if (tl > 1e-12) { const f = tl < mu * pen ? 1 : mu * pen / tl; x[k] -= tx * f; x[k + 1] -= ty * f; x[k + 2] -= tz * f; }
  }
  air(h, wind, t) {
    const { x, v, w, tris: T, mass, fabric: F } = this, rho = 1.2;
    for (let q = 0; q < T.length; q += 3) {
      const a = T[q], b = T[q + 1], c = T[q + 2];
      const ux = x[b * 3] - x[a * 3], uy = x[b * 3 + 1] - x[a * 3 + 1], uz = x[b * 3 + 2] - x[a * 3 + 2];
      const vx = x[c * 3] - x[a * 3], vy = x[c * 3 + 1] - x[a * 3 + 1], vz = x[c * 3 + 2] - x[a * 3 + 2];
      let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      const l = Math.sqrt(nx * nx + ny * ny + nz * nz); if (l < 1e-12) continue;
      const A = l / 2; nx /= l; ny /= l; nz /= l;
      const cx = (x[a * 3] + x[b * 3] + x[c * 3]) / 3, cy = (x[a * 3 + 1] + x[b * 3 + 1] + x[c * 3 + 1]) / 3, cz = (x[a * 3 + 2] + x[b * 3 + 2] + x[c * 3 + 2]) / 3;
      const W = wind ? wind(cx, cy, cz, t) : ZERO;
      const rx = (v[a * 3] + v[b * 3] + v[c * 3]) / 3 - W[0], ry = (v[a * 3 + 1] + v[b * 3 + 1] + v[c * 3 + 1]) / 3 - W[1], rz = (v[a * 3 + 2] + v[b * 3 + 2] + v[c * 3 + 2]) / 3 - W[2];
      const vn = rx * nx + ry * ny + rz * nz, m = (mass[a] + mass[b] + mass[c]) / 3;
      // pressure on the face (drag 1.2), a little on its length (skin friction): never more than to stop it in the flow
      let dvn = 0.5 * rho * 1.2 * F.air * A * vn * Math.abs(vn) * h / (m * 3);
      if (Math.abs(dvn) > Math.abs(vn)) dvn = vn;
      const tx = rx - vn * nx, ty = ry - vn * ny, tz = rz - vn * nz;
      let ft = 0.5 * rho * 0.03 * A * Math.hypot(tx, ty, tz) * h / (m * 3); if (ft > 1) ft = 1;
      const ax = -(dvn * nx + ft * tx), ay = -(dvn * ny + ft * ty), az = -(dvn * nz + ft * tz);
      for (const i of [a, b, c]) { v[i * 3] += ax; v[i * 3 + 1] += ay; v[i * 3 + 2] += az; }
    }
  }
}
const ZERO = [0, 0, 0];
function dist(x, a, b) { return Math.hypot(x[a * 3] - x[b * 3], x[a * 3 + 1] - x[b * 3 + 1], x[a * 3 + 2] - x[b * 3 + 2]); }
function triArea(x, a, b, c) {
  const ux = x[b * 3] - x[a * 3], uy = x[b * 3 + 1] - x[a * 3 + 1], uz = x[b * 3 + 2] - x[a * 3 + 2], vx = x[c * 3] - x[a * 3], vy = x[c * 3 + 1] - x[a * 3 + 1], vz = x[c * 3 + 2] - x[a * 3 + 2];
  return Math.hypot(uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx) / 2;
}
