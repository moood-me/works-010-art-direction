// A hairstyle's geometry (В1, experiments/hair: hair.js, carried here as it was): built round a neutral head — the
// design space (metres, the head's centre near the origin, y up, z forward) — then fitted onto a body's head
// (src/hair/fit.js). A hairstyle is parts, each a surface of its own; a part is groups of items (a scalp mass over the
// skull up to a drawn hairline, big locks swept along guide curves, buns, bands), each group named so a hairstyle can be
// changed by them (src/hair/styles.js). Every lock is drawn twice:
// - as its own swept surface — a lens section (thin side edges, the inner face flatter), thinning to a true point at
//   the tip with an eased start, a hooked tip, smaller locks breaking off a clump's end; normals lean out along the
//   lock, so it shades as a sheet, not a tube;
// - merged with the part's other items into one surface drawn a little inside the locks: the darker inner layer that
//   fills the gaps and that light falls into between clumps.
// Every lock keeps its guide curve: in motion it is a chain of points rooted on the head (src/hair/sim.js) and the
// surfaces ride the chains (bindOf, below: each point bound to the chain where it lies).
import { smin } from '../math.js';
import { smax } from '../head/shapes.js';

const len = (x, y, z) => Math.hypot(x, y, z);
const ellip = (x, y, z, rx, ry, rz) => { const k = len(x / rx, y / ry, z / rz); return (k - 1) * Math.min(rx, ry, rz); };
const capsule = (px, py, pz, a, b, r) => {
  const bx = b[0] - a[0], by = b[1] - a[1], bz = b[2] - a[2], qx = px - a[0], qy = py - a[1], qz = pz - a[2];
  const t = Math.max(0, Math.min(1, (qx * bx + qy * by + qz * bz) / (bx * bx + by * by + bz * bz)));
  return len(qx - bx * t, qy - by * t, qz - bz * t) - r;
};

// ———— the neutral head of the design space: only there to carry the hair (and to shade it at rest) ————
export const CRANIUM = { c: [0, 0.018, -0.006], r: [0.081, 0.094, 0.091] };
export function headSDF(o = {}) {
  const m = o.male ? 1 : 0, cr = CRANIUM;
  const sdf = (x, y, z) => {
    let d = ellip(x - cr.c[0], y - cr.c[1], z - cr.c[2], ...cr.r);
    d = smin(d, ellip(x, y + 0.043, z - 0.018, 0.066 + 0.006 * m, 0.07, 0.072), 0.03);
    d = smin(d, ellip(x, y + 0.093, z - 0.046, 0.026 + 0.01 * m, 0.022, 0.024), 0.03);
    d = smin(d, ellip(x, y + 0.03, z - 0.088, 0.008, 0.012, 0.011), 0.012);              // nose
    for (const s of [-1, 1]) d = smin(d, ellip(x - s * 0.079, y + 0.008, z + 0.006, 0.011, 0.025, 0.016), 0.01); // ears
    d = smin(d, capsule(x, y, z, [0, -0.07, -0.012], [0, -0.22, -0.02], 0.041 + 0.006 * m), 0.03); // neck
    d = smin(d, ellip(x, y + 0.27, z + 0.01, 0.17 + 0.03 * m, 0.065, 0.085), 0.06);    // shoulders
    return d;
  };
  const eyes = [-1, 1].map(s => ({ c: [s * 0.03, -0.014, 0.075], r: [0.0085, 0.012, 0.004] }));
  return { sdf, eyes };
}
// a point on the scalp: azimuth th (0 = front, +pi/2 = the head's left), elevation ph, lifted off by `off`
export function scalp(th, ph, off = 0) {
  const d = [Math.sin(th) * Math.cos(ph), Math.sin(ph), Math.cos(th) * Math.cos(ph)], r = CRANIUM.r, c = CRANIUM.c;
  return [c[0] + d[0] * (r[0] + off), c[1] + d[1] * (r[1] + off), c[2] + d[2] * (r[2] + off)];
}

// ———— a lock: a swept, flattened, tapering volume along a Catmull-Rom guide ————
function catmull(pts, n) {
  const P = [pts[0], ...pts, pts[pts.length - 1]], out = [], seg = pts.length - 1;
  for (let i = 0; i <= n; i++) {
    const u = i / n * seg, k = Math.min(Math.floor(u), seg - 1), t = u - k;
    const p0 = P[k], p1 = P[k + 1], p2 = P[k + 2], p3 = P[k + 3], t2 = t * t, t3 = t2 * t;
    out.push([0, 1, 2].map(j => 0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)));
  }
  return out;
}
const lerpArr = (a, s) => { if (typeof a === 'number') return a; const u = s * (a.length - 1), i = Math.min(Math.floor(u), a.length - 2), t = u - i; return a[i] + (a[i + 1] - a[i]) * t; };
export function frames(o, n) {
  const c = catmull(o.pts, n), S = [];
  if (o.wave) for (let i = 0; i <= n; i++) {   // a wave across the lock's fall: sideways, growing towards the tip
    const s = i / n, p = c[i], q = c[Math.min(i + 1, n)], r = c[Math.max(i - 1, 0)], T = [q[0] - r[0], q[1] - r[1], q[2] - r[2]];
    const side = [p[2] - CRANIUM.c[2], 0, -(p[0] - CRANIUM.c[0])], sl = Math.hypot(...side) || 1, amp = o.wave.amp * Math.min(1, s * 2) * Math.sin(s * o.wave.f * 6.283 + (o.wave.ph || 0));
    c[i] = [p[0] + side[0] / sl * amp, p[1], p[2] + side[2] / sl * amp];
  }
  if (o.coil) {   // a ringlet: the lock winds around its guide, the winding growing from the root
    const g = c.map(p => p.slice()); let U = null;
    for (let i = 0; i <= n; i++) {
      const s = i / n, q = g[Math.min(i + 1, n)], r = g[Math.max(i - 1, 0)];
      let T = [q[0] - r[0], q[1] - r[1], q[2] - r[2]]; const tl = len(...T) || 1; T = T.map(v => v / tl);
      if (!U) U = Math.abs(T[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0];
      const ut = U[0] * T[0] + U[1] * T[1] + U[2] * T[2]; U = [U[0] - ut * T[0], U[1] - ut * T[1], U[2] - ut * T[2]]; const ul = len(...U) || 1; U = U.map(v => v / ul);
      const V = [T[1] * U[2] - T[2] * U[1], T[2] * U[0] - T[0] * U[2], T[0] * U[1] - T[1] * U[0]];
      const R = lerpArr(o.coil.R, s) * Math.min(1, s / (o.coil.start ?? 0.15)), a = s * o.coil.turns * 6.283 + (o.coil.ph || 0);
      c[i] = [0, 1, 2].map(j => g[i][j] + (U[j] * Math.cos(a) + V[j] * Math.sin(a)) * R);
    }
  }
  for (let i = 0; i <= n; i++) {
    const s = i / n, p = c[i], q = c[Math.min(i + 1, n)], r = c[Math.max(i - 1, 0)];
    let T = [q[0] - r[0], q[1] - r[1], q[2] - r[2]]; const tl = len(...T) || 1; T = T.map(v => v / tl);
    // the flat side lies against the head: thickness points away from the head's axis, unless a direction is given
    // below the skull the outward side is horizontal; where it runs along the lock, the frame is carried on from above
    const dy = p[1] - CRANIUM.c[1];
    let B = o.up ? o.up.slice() : o.about ? [p[0] - o.about[0], p[1] - o.about[1], p[2] - o.about[2]] : [p[0] - CRANIUM.c[0], dy * (o.vert ?? 1) * (dy < 0 ? 0.3 : 1), p[2] - CRANIUM.c[2]];
    const B0l = len(...B) || 1, bt = B[0] * T[0] + B[1] * T[1] + B[2] * T[2]; B = [B[0] - bt * T[0], B[1] - bt * T[1], B[2] - bt * T[2]];
    const bl = len(...B) || 1; B = B.map(v => v / bl);
    if (S.length) {
      let P = S[S.length - 1].B; const pt = P[0] * T[0] + P[1] * T[1] + P[2] * T[2]; P = [P[0] - pt * T[0], P[1] - pt * T[1], P[2] - pt * T[2]];
      const pl = len(...P) || 1; P = P.map(v => v / pl);
      if (B[0] * P[0] + B[1] * P[1] + B[2] * P[2] < 0) B = B.map(v => -v);
      const q = Math.min(1, (bl / B0l) ** 2) * (o.up || o.about ? 1 : 0.6);
      B = B.map((v, j) => v * q + P[j] * (1 - q)); const l2 = len(...B) || 1; B = B.map(v => v / l2);
    }
    if (o.twist) { const a = lerpArr(o.twist, s), N0 = [T[1] * B[2] - T[2] * B[1], T[2] * B[0] - T[0] * B[2], T[0] * B[1] - T[1] * B[0]]; B = B.map((v, j) => v * Math.cos(a) + N0[j] * Math.sin(a)); }
    const N = [T[1] * B[2] - T[2] * B[1], T[2] * B[0] - T[0] * B[2], T[0] * B[1] - T[1] * B[0]];
    let w = lerpArr(o.w, s); const tip = Math.max(o.tip ?? 0.4, 0.35);
    // the tip thins to a point: the strands of a clump gather and end at different lengths
    if (s > 1 - tip && o.point !== false) { const u = (1 - s) / tip; w *= Math.pow(1 - (1 - u) * (1 - u), Math.max(o.sharp ?? 1.3, 1.25) * 1.2); }   // eased in, so the taper starts without a corner
    if (s < (o.root ?? 0)) w *= 0.6 + 0.4 * s / o.root;
    const th = o.t !== undefined ? lerpArr(o.t, s) * (w / Math.max(lerpArr(o.w, s), 1e-6)) : w * (o.flat ?? 0.42);
    S.push({ s, p, T, B, N, w, t: th, lens: o.lens ?? 0.6 });
  }
  // a hooked tip: the end bends sideways, so one edge runs on and the other curves in to the point
  if (o.hook) {
    const tip = Math.max(o.tip ?? 0.4, 0.35), w0 = Math.max(...S.map(e => e.w));
    for (const e of S) if (e.s > 1 - tip) { const f = ((e.s - (1 - tip)) / tip) ** 2 * o.hook * w0; e.p = e.p.map((v, j) => v + e.N[j] * f); }
  }
  return S;
}
export function lock(o) {
  const S = frames(o, o.n || 24).map(e => ({ ...e, w: Math.max(0.0012, e.w), t: Math.max(0.0012, e.t) }));
  const wmax = Math.max(...S.map(e => e.w));
  const bb = [[1e9, 1e9, 1e9], [-1e9, -1e9, -1e9]];
  for (const e of S) for (let j = 0; j < 3; j++) { bb[0][j] = Math.min(bb[0][j], e.p[j] - e.w); bb[1][j] = Math.max(bb[1][j], e.p[j] + e.w); }
  const curly = o.curly;
  // the segments in runs of 8, each run's bounding sphere round its axis and its widest: a run every segment of which the
  // test below would pass over is passed over whole (the same distance, found sooner)
  const RUN = 8, runs = [];
  for (let i0 = 0; i0 < S.length - 1; i0 += RUN) {
    const i1 = Math.min(S.length - 1, i0 + RUN), c = [0, 0, 0]; let w = 0, r = 0;
    for (let i = i0; i <= i1; i++) { for (let j = 0; j < 3; j++) c[j] += S[i].p[j] / (i1 - i0 + 1); w = Math.max(w, S[i].w); }
    for (let i = i0; i <= i1; i++) r = Math.max(r, Math.hypot(S[i].p[0] - c[0], S[i].p[1] - c[1], S[i].p[2] - c[2]));
    runs.push({ i0, i1, c, r, w });
  }
  // the distance, and (into `out`) where on the lock the nearest point is: along it, across it, its direction
  const sdf = (x, y, z, out) => {
    const ox = Math.max(bb[0][0] - x, 0, x - bb[1][0]), oy = Math.max(bb[0][1] - y, 0, y - bb[1][1]), oz = Math.max(bb[0][2] - z, 0, z - bb[1][2]);
    if (!out && ox + oy + oz > 0.03) return ox + oy + oz;
    let best = 1e9;
    for (const R of runs) {
    if (Math.hypot(x - R.c[0], y - R.c[1], z - R.c[2]) - R.r > R.w + Math.min(best, 0.02) + 0.004 + 1e-9) continue;
    for (let i = R.i0; i < R.i1; i++) {
      const a = S[i], b = S[i + 1];
      const bx = b.p[0] - a.p[0], by = b.p[1] - a.p[1], bz = b.p[2] - a.p[2], qx = x - a.p[0], qy = y - a.p[1], qz = z - a.p[2];
      const L2 = bx * bx + by * by + bz * bz || 1e-9;
      const u = Math.max(0, Math.min(1, (qx * bx + qy * by + qz * bz) / L2));
      const rx = qx - bx * u, ry = qy - by * u, rz = qz - bz * u;
      if (rx * rx + ry * ry + rz * rz > (Math.max(a.w, b.w) + Math.min(best, 0.02) + 0.004) ** 2) continue;
      const w = a.w + (b.w - a.w) * u, t = a.t + (b.t - a.t) * u;
      const m = Math.min(w, t), iu = 1 - u;
      const B0 = a.B[0] * iu + b.B[0] * u, B1 = a.B[1] * iu + b.B[1] * u, B2 = a.B[2] * iu + b.B[2] * u;
      const N0 = a.N[0] * iu + b.N[0] * u, N1 = a.N[1] * iu + b.N[1] * u, N2 = a.N[2] * iu + b.N[2] * u;
      const T0 = a.T[0] * iu + b.T[0] * u, T1 = a.T[1] * iu + b.T[1] * u, T2 = a.T[2] * iu + b.T[2] * u;
      const bl = Math.hypot(B0, B1, B2) || 1, nl = Math.hypot(N0, N1, N2) || 1, tl = Math.hypot(T0, T1, T2) || 1;
      let v1 = (rx * N0 + ry * N1 + rz * N2) / nl / w, v2 = (rx * B0 + ry * B1 + rz * B2) / bl / t;
      const v3 = (rx * T0 + ry * T1 + rz * T2) / tl / m;
      // a lens, not a tube: the outer face curves, the side edges thin out to meet the neighbours
      if (a.lens) { const e = Math.abs(v1); v2 = v2 / Math.max(0.05, 1 - a.lens * e * e); }
      let d = (Math.hypot(v1, v2, v3) - 1) * m;
      if (curly) { const sAlong = (i + u) / (S.length - 1), ang = Math.atan2(v2, v1); d -= curly.amp * m * Math.sin(curly.f * sAlong * 6.283 + curly.turn * ang); }
      if (d < best) { best = d; if (out) { out.s = (i + u) / (S.length - 1); out.a = (rx * N0 + ry * N1 + rz * N2) / nl / w * wmax; out.T = [T0 / tl, T1 / tl, T2 / tl]; } }
    }
    }
    return best;
  };
  return { sdf, bb, color: o.color, k: o.k, o, isLock: true, rig: o.rig };
}

// ———— a big clump with smaller ones breaking off it ————
// Each kid is a thinner lock with its own guide: it starts inside the parent, leaves it at one edge and ends at its own
// length, so the clump's end splits into a main point and a few smaller ones.
export function clump(o) {
  const main = lock(o);
  if (!o.kids || !o.kids.length) return main;
  const F = frames({ ...o, kids: undefined }, 40), at = s => F[Math.min(40, Math.round(s * 40))];
  return [main, ...o.kids.map(k => {
    const s0 = k.at ?? 0.55, e0 = at(s0), w0 = e0.w, pts = [];
    const kl = k.len ?? 1;   // its length against the rest of the parent: shorter ends sooner along it, longer runs on past its end
    for (const f of [0, 0.34, 0.67, 1]) {
      const s = s0 + (1 - s0) * f * Math.min(1, kl), e = at(s), sp = (0.25 + (k.spread ?? 0.9) * f) * w0 * k.side, ou = (k.out ?? 0.002) * f;
      let p = e.p.map((v, j) => v + e.N[j] * sp + e.B[j] * ou);
      if (f === 1 && kl > 1) { const L = (1 - s0) * 0.5 * (kl - 1) * len(...F[40].p.map((v, j) => v - F[0].p[j])); p = p.map((v, j) => v + e.T[j] * L); }
      if (f === 1) p = p.map((v, j) => v + e.N[j] * (k.turn ?? 0) * k.side);
      pts.push(p);
    }
    const wk = w0 * (k.w ?? 0.35);
    const kid = lock({ pts, w: [wk * 0.7, wk, wk * 0.85, wk * 0.6], flat: o.flat ?? 0.42, tip: k.tip ?? 0.55, sharp: 1.15, hook: (k.hook ?? 0.8) * k.side, color: o.color, lens: o.lens, vert: o.vert, up: o.up, n: 16 });
    kid.parent = main;   // in motion it rides its clump's chain
    return kid;
  })];
}

// ———— a lock as its own surface: a lens section swept along the guide, thinning to a true point at the tip ————
// Besides the shape it carries what the hair shading needs: the strand direction, where across the lock (strands
// gather towards the tip) and along it (darker at the root) each point lies.
export function lockMesh(L, M = 14) {
  const o = L.o, S = frames(o, Math.max(48, (o.n || 24) * 2, o.coil ? Math.round(o.coil.turns * 18) : 0)), n = S.length;
  const wmax = Math.max(...S.map(e => e.w)), curly = o.curly, lens = o.lens ?? 0.6;
  const pos = [], tan = [], uv = [], wd = [], idx = [];
  for (let i = 0; i < n; i++) {
    const e = S[i], w = Math.max(e.w, 0.00015), t = Math.max(e.t, 0.0001);
    for (let j = 0; j < M; j++) {
      const ph = j / M * 2 * Math.PI, cx = Math.cos(ph), sy = Math.sin(ph);
      // the section: a lens whose side edges are thin; the inner face (towards the head) flatter than the outer one
      let y = Math.sign(sy) * Math.pow(Math.abs(sy), 0.7 + lens * 0.9) * t * (sy < 0 ? 0.55 : 1);
      let x = cx * w;
      if (curly) { const f = 1 + curly.amp * Math.min(w, t) / Math.max(Math.hypot(x, y), 1e-5) * Math.sin(curly.f * e.s * 6.283 + curly.turn * ph); x *= f; y *= f; }
      pos.push(e.p[0] + e.N[0] * x + e.B[0] * y, e.p[1] + e.N[1] * x + e.B[1] * y, e.p[2] + e.N[2] * x + e.B[2] * y);
      tan.push(...e.T); uv.push(cx * wmax, e.s); wd.push(Math.min(w, t * 1.5));
    }
  }
  for (let i = 0; i < n - 1; i++) for (let j = 0; j < M; j++) {
    const a = i * M + j, b = i * M + (j + 1) % M, c = a + M, d = b + M;
    idx.push(a, c, b, b, c, d);
  }
  // close the root (it sits under the scalp mass anyway)
  const r0 = pos.length / 3; pos.push(...S[0].p); tan.push(...S[0].T); uv.push(0, 0); wd.push(S[0].w);
  for (let j = 0; j < M; j++) idx.push(r0, j, (j + 1) % M);
  const P = new Float32Array(pos), nor = vertexNormals(P, idx);
  // shade the lock as a sheet, not a tube: the outer face's normals lean out along the lock's outward side
  for (let i = 0; i < n; i++) for (let j = 0; j < M; j++) {
    const v = (i * M + j) * 3, B = S[i].B, sg = Math.sign(Math.sin(j / M * 2 * Math.PI)) * (o.sheet ?? 0.9);
    const x = nor[v] + B[0] * sg, y = nor[v + 1] + B[1] * sg, z = nor[v + 2] + B[2] * sg, l = Math.hypot(x, y, z) || 1;
    nor[v] = x / l; nor[v + 1] = y / l; nor[v + 2] = z / l;
  }
  return { pos: P, nor, tan: new Float32Array(tan), uv: new Float32Array(uv), wd: new Float32Array(wd), idx };
}
export function ell(o) {   // an ellipsoid, optionally turned: axes u, v (w follows)
  const c = o.c, r = o.r, u = o.u || [1, 0, 0], v0 = o.v || [0, 1, 0];
  const w = [u[1] * v0[2] - u[2] * v0[1], u[2] * v0[0] - u[0] * v0[2], u[0] * v0[1] - u[1] * v0[0]];
  const v = [w[1] * u[2] - w[2] * u[1], w[2] * u[0] - w[0] * u[2], w[0] * u[1] - w[1] * u[0]];
  const m = Math.max(...r);
  return { sdf: (x, y, z) => { const px = x - c[0], py = y - c[1], pz = z - c[2]; return ellip(px * u[0] + py * u[1] + pz * u[2], px * v[0] + py * v[1] + pz * v[2], px * w[0] + py * w[1] + pz * w[2], ...r); },
    bb: [c.map(q => q - m), c.map(q => q + m)], color: o.color, k: o.k, rig: o.rig };
}
export function torus(o) {   // a ring around axis a
  const c = o.c, a = o.a.map(q => q / len(...o.a)), R = o.R, r = o.r;
  return { sdf: (x, y, z) => { const px = x - c[0], py = y - c[1], pz = z - c[2], h = px * a[0] + py * a[1] + pz * a[2];
    const qx = px - h * a[0], qy = py - h * a[1], qz = pz - h * a[2], ql = len(qx, qy, qz); return Math.hypot(ql - R, h * (o.flat ?? 1)) - r; },
    bb: [c.map(q => q - R - r), c.map(q => q + R + r)], color: o.color, k: o.k, rig: o.rig };
}

// ———— the scalp mass: the skull grown by a thickness, cut by a drawn hairline ————
export function hairline(cap, x, y, z) {
  const th = Math.abs(Math.atan2(x - CRANIUM.c[0], z - CRANIUM.c[2]));
  const K = [[0, cap.front ?? 0.066], [1.0, cap.temple ?? 0.034], [1.45, cap.ear ?? 0.022], [1.95, cap.behind ?? -0.045], [Math.PI, cap.nape ?? -0.075]];
  let h = K[4][1];
  for (let i = 0; i < 4; i++) if (th <= K[i + 1][0]) { const t = (th - K[i][0]) / (K[i + 1][0] - K[i][0]); h = K[i][1] + (K[i + 1][1] - K[i][1]) * (t * t * (3 - 2 * t)); break; }
  if (cap.shave && Math.sign(x) === cap.shave.side) h = Math.max(h, cap.shave.y);
  return h;
}
export function scalpMass(cap, under = 0) {
  const c = CRANIUM.c, r = CRANIUM.r;
  return { isCap: true, cap, under: u => scalpMass(cap, u), sdf: (x, y, z) => {
    const dx = x - c[0], dy = y - c[1], dz = z - c[2], dl = len(dx, dy, dz) || 1;
    // `under`: when locks lie over it, the mass sinks below them, keeping a layer on the skull thicker than the inner layer's inset
    const t = Math.max(under > 0 ? 0.0075 : 0, cap.thick + (cap.puff || 0) * Math.max(0, dy / dl) + (cap.back || 0) * Math.max(0, -dz / dl) + (cap.sides || 0) * Math.abs(dx / dl) - under);
    const d = ellip(dx, dy - (cap.lift || 0), dz, r[0] + t, r[1] + t, r[2] + t);
    return smax(d, hairline(cap, x, y, z) - y, cap.edge ?? 0.008);
  }, bb: [[-0.14, -0.2, -0.15], [0.14, 0.16, 0.14]], color: cap.color, k: cap.k };
}

// ———— a whole hairstyle: parts, each one surface ————
// Each part is drawn twice: its merged volume, a little shrunk, is the inner layer (darker, it fills the gaps and is
// what light falls into between clumps); over it every lock is its own swept surface with a true pointed tip.
// Every point carries the strand direction, across/along coordinates, a per-lock seed and an occlusion term.
export function buildHair(S, head) {
  const parts = S.parts.map(part => {
    const flat = itemsOf(part), hasLocks = flat.some(it => it.isLock) && part.strands !== false;
    const items = flat.map(it => it.isCap && hasLocks ? { ...it.under(part.under ?? 0.012), k: it.k } : it), k = part.k ?? 0.012;
    const bmin = [1e9, 1e9, 1e9], bmax = [-1e9, -1e9, -1e9];
    for (const it of items) for (let j = 0; j < 3; j++) { bmin[j] = Math.min(bmin[j], it.bb[0][j]); bmax[j] = Math.max(bmax[j], it.bb[1][j]); }
    for (let j = 0; j < 3; j++) { bmin[j] -= 0.012; bmax[j] += 0.012; }
    const cuts = part.cuts || [];
    const sdf = (x, y, z) => {
      let d = 1e9;
      for (const it of items) {
        const ox = Math.max(it.bb[0][0] - x, 0, x - it.bb[1][0]), oy = Math.max(it.bb[0][1] - y, 0, y - it.bb[1][1]), oz = Math.max(it.bb[0][2] - z, 0, z - it.bb[1][2]);
        if (ox + oy + oz > Math.min(d, 0.02) + (it.k ?? k)) continue;
        d = smin(d, it.sdf(x, y, z), it.k ?? k);
      }
      for (const cu of cuts) d = smax(d, -cu.sdf(x, y, z), cu.k ?? 0.004);
      return d;
    };
    return { part, items, sdf, bmin, bmax, locks: items.filter(it => it.isLock && part.strands !== false) };
  });
  // everything that can shade a point: the hair's volumes and the head
  const all = (x, y, z) => { let d = head ? head(x, y, z) : 1e9; for (const P of parts) d = Math.min(d, P.sdf(x, y, z)); return d; };
  const occl = (m, off = 0) => {
    const ao = new Float32Array(m.pos.length / 3), H = [0.004, 0.012, 0.028];
    for (let v = 0; v < ao.length; v++) {
      const x = m.pos[v * 3], y = m.pos[v * 3 + 1], z = m.pos[v * 3 + 2], nx = m.nor[v * 3], ny = m.nor[v * 3 + 1], nz = m.nor[v * 3 + 2];
      let o = 0; for (const h of H) o += Math.max(0, h - Math.max(0, all(x + nx * (h + off), y + ny * (h + off), z + nz * (h + off)))) / h;
      ao[v] = Math.max(0, 1 - o / H.length * 1.25);
    }
    return ao;
  };
  const out = [];
  for (const P of parts) {
    const { part, items, locks } = P, palette = paletteOf(part, items), inset = part.inset ?? (locks.length ? Math.max(0.0025, 0.3 * Math.max(part.k ?? 0.012, ...items.map(it => it.k ?? 0))) : 0);   // deeper than the merge's swell
    const m = surfaceNets((x, y, z) => P.sdf(x, y, z) + inset, P.bmin, P.bmax, part.h || (locks.length ? 0.0034 : 0.0028));   // under locks it is only the inner layer: a little coarser
    const nv = m.pos.length / 3;
    m.tan = new Float32Array(nv * 3); m.uv = new Float32Array(nv * 2); m.seed = new Float32Array(nv); m.ci = new Uint8Array(nv);
    const crown = S.crown || [0, 0.13, -0.03], info = {};
    for (let v = 0; v < nv; v++) {
      const x = m.pos[v * 3], y = m.pos[v * 3 + 1], z = m.pos[v * 3 + 2], nx = m.nor[v * 3], ny = m.nor[v * 3 + 1], nz = m.nor[v * 3 + 2];
      // strand direction: from the locks around, weighted by nearness; far from any lock, down from the crown
      let T = [x - crown[0], y - crown[1], z - crown[2]], tw = 0.02, best = 1e9, near = null;
      const tl0 = len(...T) || 1; T = T.map(q => q / tl0 * tw);
      for (const L of locks) {
        const ox = Math.max(L.bb[0][0] - x, 0, x - L.bb[1][0]), oy = Math.max(L.bb[0][1] - y, 0, y - L.bb[1][1]), oz = Math.max(L.bb[0][2] - z, 0, z - L.bb[1][2]);
        if (ox + oy + oz > 0.03) continue;
        const d = L.sdf(x, y, z, info); if (d > 0.03) continue;
        const wgt = 1 / (Math.max(d, 0) + 0.003) ** 2 * 1e-4;
        T[0] += info.T[0] * wgt; T[1] += info.T[1] * wgt; T[2] += info.T[2] * wgt;
        if (d < best) { best = d; near = { L, a: info.a, s: info.s }; }
      }
      const tn = T[0] * nx + T[1] * ny + T[2] * nz; T = [T[0] - tn * nx, T[1] - tn * ny, T[2] - tn * nz];
      const tl = len(...T) || 1; m.tan.set(T.map(q => q / tl), v * 3);
      // the nearest item's colour (a streak or a band keeps its own): its place in the part's palette
      if (palette.length > 1) { let bd = 1e9; for (const it of items) { const d = it.sdf(x, y, z); if (d < bd) { bd = d; m.ci[v] = palette.indexOf(it.color ?? part.color); } } }
      // the inner layer takes its strands from the lock it lies under; away from locks they run out from the crown
      if (near && best < 0.012) { m.uv[v * 2] = near.a; m.uv[v * 2 + 1] = near.s; m.seed[v] = (locks.indexOf(near.L) * 0.618) % 1; }
      else { m.uv[v * 2] = Math.atan2(x - crown[0], z - crown[2]) * 0.06; m.uv[v * 2 + 1] = 0.3; m.seed[v] = 0.5; }
    }
    m.ao = occl(m, inset);
    out.push({ mesh: m, inner: !!locks.length, rough: part.rough, ink: part.ink, plain: !!part.fabric, palette, part, items, locks });
    if (!locks.length) continue;
    // the locks: one geometry for the part
    const ms = locks.map(L => { const q = lockMesh(L); q.L = L; return q; });
    const nT = ms.reduce((a, q) => a + q.pos.length / 3, 0), G = { pos: new Float32Array(nT * 3), nor: new Float32Array(nT * 3), tan: new Float32Array(nT * 3), uv: new Float32Array(nT * 2), wd: new Float32Array(nT), seed: new Float32Array(nT), ci: new Uint8Array(nT), idx: [], lockOf: new Uint16Array(nT) };
    let off = 0;
    for (const q of ms) {
      const c = palette.indexOf(q.L.color ?? part.color), n = q.pos.length / 3;
      G.pos.set(q.pos, off * 3); G.nor.set(q.nor, off * 3); G.tan.set(q.tan, off * 3); G.uv.set(q.uv, off * 2); G.wd.set(q.wd, off);
      const li = locks.indexOf(q.L);
      for (let v = 0; v < n; v++) { G.seed[off + v] = (li * 0.618) % 1; G.ci[off + v] = c; G.lockOf[off + v] = li; }
      for (const i of q.idx) G.idx.push(i + off);
      off += n;
    }
    G.ao = occl(G);
    out.push({ mesh: G, lockLayer: true, rough: part.rough, ink: part.ink, palette, part, items, locks });
  }
  return out;
}
function vertexNormals(P, idx) {
  const N = new Float32Array(P.length);
  for (let t = 0; t < idx.length; t += 3) {
    const a = idx[t] * 3, b = idx[t + 1] * 3, c = idx[t + 2] * 3;
    const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], wx = P[c] - P[a], wy = P[c + 1] - P[a + 1], wz = P[c + 2] - P[a + 2];
    const cx = uy * wz - uz * wy, cy = uz * wx - ux * wz, cz = ux * wy - uy * wx;
    for (const v of [a, b, c]) { N[v] += cx; N[v + 1] += cy; N[v + 2] += cz; }
  }
  for (let v = 0; v < N.length; v += 3) { const l = Math.hypot(N[v], N[v + 1], N[v + 2]) || 1; N[v] /= l; N[v + 1] /= l; N[v + 2] /= l; }
  return N;
}
// a part's items: its groups (each named, a list or one) as one list, each item knowing its group
export function itemsOf(part) {
  const out = [];
  for (const [group, list] of Object.entries(part.items)) for (const it of [list].flat(Infinity)) { it.group = group; out.push(it); }
  return out;
}
// a part's colours: its own first, then each other colour its items have (a streak, a band)
const paletteOf = (part, items) => [part.color, ...new Set(items.map(it => it.color).filter(c => c !== undefined && c !== part.color))];

// ———— a surface out of a distance: naive surface nets, near the surface only ————
export function surfaceNets(sdf, bmin, bmax, h) {
  const nx = Math.ceil((bmax[0] - bmin[0]) / h) + 1, ny = Math.ceil((bmax[1] - bmin[1]) / h) + 1, nz = Math.ceil((bmax[2] - bmin[2]) / h) + 1;
  const F = new Float32Array(nx * ny * nz).fill(NaN);
  const id = (i, j, k) => i + nx * (j + ny * k);
  const C = 4, cnx = Math.ceil((nx - 1) / C), cny = Math.ceil((ny - 1) / C), cnz = Math.ceil((nz - 1) / C);
  const thr = C * h * 1.9;
  const CV = new Float32Array((cnx + 1) * (cny + 1) * (cnz + 1));
  const cid = (i, j, k) => i + (cnx + 1) * (j + (cny + 1) * k);
  for (let k = 0; k <= cnz; k++) for (let j = 0; j <= cny; j++) for (let i = 0; i <= cnx; i++) CV[cid(i, j, k)] = sdf(bmin[0] + i * C * h, bmin[1] + j * C * h, bmin[2] + k * C * h);
  for (let ck = 0; ck < cnz; ck++) for (let cj = 0; cj < cny; cj++) for (let ci = 0; ci < cnx; ci++) {
    let mn = 1e9, s = 0;
    for (let c = 0; c < 8; c++) { const v = CV[cid(ci + (c & 1), cj + (c >> 1 & 1), ck + (c >> 2 & 1))]; mn = Math.min(mn, Math.abs(v)); s = v; }
    const near = mn < thr;
    for (let k = ck * C; k <= Math.min(ck * C + C, nz - 1); k++) for (let j = cj * C; j <= Math.min(cj * C + C, ny - 1); j++) for (let i = ci * C; i <= Math.min(ci * C + C, nx - 1); i++) {
      const q = id(i, j, k); if (!Number.isNaN(F[q]) && !near) continue;
      if (near) { if (Number.isNaN(F[q]) || Math.abs(F[q]) >= thr * 0.999) F[q] = sdf(bmin[0] + i * h, bmin[1] + j * h, bmin[2] + k * h); }
      else F[q] = s > 0 ? thr : -thr;
    }
  }
  for (let q = 0; q < F.length; q++) if (Number.isNaN(F[q])) F[q] = thr;
  const VI = new Int32Array(nx * ny * nz).fill(-1), pos = [];
  const E = [[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [1, 3], [4, 6], [5, 7], [0, 4], [1, 5], [2, 6], [3, 7]];
  const d = new Float32Array(8);
  for (let k = 0; k < nz - 1; k++) for (let j = 0; j < ny - 1; j++) for (let i = 0; i < nx - 1; i++) {
    let m = 0;
    for (let c = 0; c < 8; c++) { d[c] = F[id(i + (c & 1), j + (c >> 1 & 1), k + (c >> 2 & 1))]; if (d[c] < 0) m |= 1 << c; }
    if (m === 0 || m === 255) continue;
    let sx = 0, sy = 0, sz = 0, n = 0;
    for (const [a, b] of E) {
      if ((d[a] < 0) === (d[b] < 0)) continue;
      const t = d[a] / (d[a] - d[b]);
      sx += (a & 1) + ((b & 1) - (a & 1)) * t; sy += (a >> 1 & 1) + ((b >> 1 & 1) - (a >> 1 & 1)) * t; sz += (a >> 2 & 1) + ((b >> 2 & 1) - (a >> 2 & 1)) * t; n++;
    }
    VI[id(i, j, k)] = pos.length / 3;
    pos.push(bmin[0] + (i + sx / n) * h, bmin[1] + (j + sy / n) * h, bmin[2] + (k + sz / n) * h);
  }
  const idx = [];
  const quad = (a, b, c, e, flip) => { if (a < 0 || b < 0 || c < 0 || e < 0) return; if (flip) idx.push(a, c, b, a, e, c); else idx.push(a, b, c, a, c, e); };
  for (let k = 1; k < nz - 1; k++) for (let j = 1; j < ny - 1; j++) for (let i = 1; i < nx - 1; i++) {
    const inside = F[id(i, j, k)] < 0;
    if (inside !== (F[id(i + 1, j, k)] < 0)) quad(VI[id(i, j - 1, k - 1)], VI[id(i, j, k - 1)], VI[id(i, j, k)], VI[id(i, j - 1, k)], inside);
    if (inside !== (F[id(i, j + 1, k)] < 0)) quad(VI[id(i - 1, j, k - 1)], VI[id(i - 1, j, k)], VI[id(i, j, k)], VI[id(i, j, k - 1)], inside);
    if (inside !== (F[id(i, j, k + 1)] < 0)) quad(VI[id(i - 1, j - 1, k)], VI[id(i, j - 1, k)], VI[id(i, j, k)], VI[id(i - 1, j, k)], inside);
  }
  // smooth the points a little over the surface, then normals from the distance itself
  const P = new Float32Array(pos), nv = P.length / 3, nb = Array.from({ length: nv }, () => []);
  for (let t = 0; t < idx.length; t += 3) for (let e = 0; e < 3; e++) { const a = idx[t + e], b = idx[t + (e + 1) % 3]; nb[a].push(b); nb[b].push(a); }
  for (let it = 0; it < 6; it++) { const Q = Float32Array.from(P); for (let v = 0; v < nv; v++) { const ns = nb[v]; if (!ns.length) continue; let x = 0, y = 0, z = 0; for (const u of ns) { x += Q[u * 3]; y += Q[u * 3 + 1]; z += Q[u * 3 + 2]; } const f = it % 2 ? -0.53 : 0.5; P[v * 3] += f * (x / ns.length - Q[v * 3]); P[v * 3 + 1] += f * (y / ns.length - Q[v * 3 + 1]); P[v * 3 + 2] += f * (z / ns.length - Q[v * 3 + 2]); } }
  const nor = new Float32Array(P.length), e = h * 0.5;
  for (let v = 0; v < P.length; v += 3) {
    const x = P[v], y = P[v + 1], z = P[v + 2];
    const gx = sdf(x + e, y, z) - sdf(x - e, y, z), gy = sdf(x, y + e, z) - sdf(x, y - e, z), gz = sdf(x, y, z + e) - sdf(x, y, z - e);
    const l = Math.hypot(gx, gy, gz) || 1; nor[v] = gx / l; nor[v + 1] = gy / l; nor[v + 2] = gz / l;
  }
  // the shading follows the big form: normals averaged over the surface a little, so the lock's segments don't show
  for (let it = 0; it < 3; it++) { const Q = Float32Array.from(nor); for (let v = 0; v < nv; v++) { const ns = nb[v]; if (!ns.length) continue; let x = Q[v * 3] * 2, y = Q[v * 3 + 1] * 2, z = Q[v * 3 + 2] * 2; for (const u of ns) { x += Q[u * 3]; y += Q[u * 3 + 1]; z += Q[u * 3 + 2]; } const l = Math.hypot(x, y, z) || 1; nor[v * 3] = x / l; nor[v * 3 + 1] = y / l; nor[v * 3 + 2] = z / l; } }
  for (let t = 0; t < idx.length; t += 3) {
    const a = idx[t] * 3, b = idx[t + 1] * 3, c = idx[t + 2] * 3;
    const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], wx = P[c] - P[a], wy = P[c + 1] - P[a + 1], wz = P[c + 2] - P[a + 2];
    const cx = uy * wz - uz * wy, cy = uz * wx - ux * wz, cz = ux * wy - uy * wx;
    if (cx * (nor[a] + nor[b] + nor[c]) + cy * (nor[a + 1] + nor[b + 1] + nor[c + 1]) + cz * (nor[a + 2] + nor[b + 2] + nor[c + 2]) < 0) { const s = idx[t + 1]; idx[t + 1] = idx[t + 2]; idx[t + 2] = s; }
  }
  return { pos: P, nor, idx };
}

// ———— the guides, and each surface bound to them (В1's motion.js, in the design space) ————
// Each lock's guide curve becomes a chain (guideOf); a clump's smaller locks ride their clump's
// chain; a braid is one chain (`rig` of its items); combed hair, buns and bands ride the head (`rig: 'head'`, chain 0).
// How stiff each point is, as a spring's (1/s²): `hold` pulls it toward where the hairstyle has it, carried by the
// head (firm where the lock lies on the skull, fading down the free part); `bend` turns each segment back toward its
// designed angle against the one above (stiff at the root, softer toward the tip). Short hair holds its shape all
// along, long hair swings; heavy hair (tails, braids) swings slower and the air holds it less.
// → {guides: [{points (n×3), s (its lock's parameter at each), rad, hold, bend, drag, inner, stretch, heavy}],
//    binds: per surface {c, u, w} (each vertex's three chains, the place on each — node index and fraction — and weights)}
// a guide from a curve ({p, s, t}: its points, its lock's parameter and thickness there): a chain of points every 2 cm
// or so, with how stiff each is; onSkull(p): whether a point lies on the skull (from the root, while it does, held firmly)
export function guideOf(curve, dyn, coil, onSkull) {
  const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  const acc = [0]; for (let i = 1; i < curve.length; i++) acc.push(acc[i - 1] + Math.hypot(...curve[i].p.map((v, j) => v - curve[i - 1].p[j])));
  const L = acc[acc.length - 1], nseg = Math.max(2, Math.min(24, Math.round(L / 0.02))), points = [], s = [], rad = [];
  for (let k = 0, i = 0; k <= nseg; k++) {
    const a = L * k / nseg; while (i < acc.length - 2 && acc[i + 1] < a) i++;
    const f = Math.min(1, Math.max(0, (a - acc[i]) / Math.max(1e-9, acc[i + 1] - acc[i]))), A = curve[i], B = curve[i + 1];
    points.push(A.p.map((v, j) => v + (B.p[j] - v) * f)); s.push(A.s + (B.s - A.s) * f); rad.push(Math.min(0.012, 0.55 * (A.t + (B.t - A.t) * f) + 0.002));
  }
  const heavy = dyn.heavy ? 1 : 0, lg = (a, b) => Math.exp(Math.log(a) + (Math.log(b) - Math.log(a)) * smooth(0.1, 0.3, L));
  const bendTip = dyn.lTip ?? (coil ? 600 : heavy ? 600 : lg(6000, 250)), holdTip = dyn.gTip ?? (heavy ? 8 : lg(3000, 6));
  let leave = 0; while (leave < nseg && onSkull(points[leave + 1])) leave++;
  const hold = [], bend = [];
  for (let k = 0; k <= nseg; k++) {
    const a = L * k / nseg, aL = L * leave / nseg, u = smooth(0, 1, (a - aL * 0.5) / Math.max(0.02, L - aL * 0.5));
    hold.push(k <= leave ? 20000 : holdTip * Math.pow(4000 / holdTip, Math.exp(-(a - aL) / (heavy ? 0.03 : 0.06))));
    bend.push(20000 * Math.pow(bendTip / 20000, u));
  }
  return { points, s, rad, hold, bend, drag: dyn.drag ?? (heavy ? 0.1 : 0.21), inner: heavy ? 2.5 : 3, stretch: coil ? 0.18 : 0, heavy };
}

export function bindOf(built) {
  const guides = [{ head: true, points: [[0, 0, 0], [0, 0, 0]] }];
  const onSkull = p => { const c = CRANIUM.c, r = CRANIUM.r, qx = (p[0] - c[0]) / r[0], qy = (p[1] - c[1]) / r[1], qz = (p[2] - c[2]) / r[2], k0 = Math.hypot(qx, qy, qz) || 1e-6, k1 = Math.hypot(qx / r[0], qy / r[1], qz / r[2]) || 1e-6; return k0 * (k0 - 1) / k1 < 0.03; };
  const chainOf = (curve, dyn, coil) => { guides.push(guideOf(curve, dyn, coil, onSkull)); return guides.length - 1; };
  const own = new Map(), groups = new Map();
  const lockChain = L => {
    if (L.rig === 'head') return 0;
    if (L.rig) return groupChain(L.rig);
    if (L.parent) return lockChain(L.parent);
    if (!own.has(L)) own.set(L, chainOf(frames({ ...L.o, coil: undefined }, 64).map(e => ({ p: e.p, s: e.s, t: e.t })), L.o.dyn || {}, !!L.o.coil));
    return own.get(L);
  };
  const groupChain = g => {
    if (!groups.has(g)) groups.set(g, chainOf(frames({ pts: g.guide, w: 0.03, t: 0.012 }, 64).map(e => ({ p: e.p, s: e.s, t: 0.016 })), g.dyn || {}, false));
    return groups.get(g);
  };
  // the chain's parameter where its lock's parameter s lies; the nearest place on a chain to a point
  const paramOfS = (g, s) => { const S = g.s; let i = 0; while (i < S.length - 2 && S[i + 1] < s) i++; return i + Math.min(1, Math.max(0, (s - S[i]) / Math.max(1e-9, S[i + 1] - S[i]))); };
  const project = (g, x, y, z) => {
    let best = 1e9, u = 0;
    for (let i = 0; i < g.points.length - 1; i++) {
      const a = g.points[i], b = g.points[i + 1], bx = b[0] - a[0], by = b[1] - a[1], bz = b[2] - a[2], L2 = bx * bx + by * by + bz * bz || 1e-9;
      const t = Math.max(0, Math.min(1, ((x - a[0]) * bx + (y - a[1]) * by + (z - a[2]) * bz) / L2)), d = (x - a[0] - bx * t) ** 2 + (y - a[1] - by * t) ** 2 + (z - a[2] - bz * t) ** 2;
      if (d < best) { best = d; u = i + t; }
    }
    return u;
  };
  const placeOn = (L, c, P, v, s) => own.get(L) === c ? paramOfS(guides[c], s) : project(guides[c], P[v * 3], P[v * 3 + 1], P[v * 3 + 2]);
  const binds = built.map(e => {
    const m = e.mesh, nv = m.pos.length / 3, c = new Uint16Array(nv * 3), u = new Float32Array(nv * 3), w = new Float32Array(nv * 3);
    const set = (v, k, ci, ui, wi) => { c[v * 3 + k] = ci; u[v * 3 + k] = ui; w[v * 3 + k] = wi; };
    if (e.lockLayer) {
      for (let v = 0; v < nv; v++) { const L = e.locks[m.lockOf[v]], ch = lockChain(L); set(v, 0, ch, ch ? placeOn(L, ch, m.pos, v, m.uv[v * 2 + 1]) : 0, 1); }
    } else if (!e.locks?.length) {
      for (let v = 0; v < nv; v++) set(v, 0, 0, 0, 1);
    } else {
      // the inner layer: bound to what it lies under, the nearest few blended by nearness — sharply, so where locks part
      // it parts with them rather than stretching into a web between them
      const info = {}, cand = [];
      for (let v = 0; v < nv; v++) {
        const x = m.pos[v * 3], y = m.pos[v * 3 + 1], z = m.pos[v * 3 + 2]; cand.length = 0; let dmin = 1e9;
        for (const it of e.items) {
          const ox = Math.max(it.bb[0][0] - x, 0, x - it.bb[1][0]), oy = Math.max(it.bb[0][1] - y, 0, y - it.bb[1][1]), oz = Math.max(it.bb[0][2] - z, 0, z - it.bb[1][2]);
          if (ox + oy + oz > Math.min(dmin + 0.01, 0.04)) continue;
          const d = it.isLock ? it.sdf(x, y, z, info) : it.sdf(x, y, z); if (d > dmin + 0.01) continue;
          dmin = Math.min(dmin, d); cand.push({ it, d, s: it.isLock ? info.s : 0 });
        }
        const acc = new Map();
        for (const q of cand) {
          if (q.d > dmin + 0.003) continue;
          const wt = Math.exp(-(q.d - dmin) / 0.0007); let ch = 0, uu = 0;
          if (q.it.isLock) { ch = lockChain(q.it); if (ch) uu = placeOn(q.it, ch, m.pos, v, q.s); }
          else if (q.it.rig && q.it.rig !== 'head') { ch = groupChain(q.it.rig); uu = project(guides[ch], x, y, z); }
          const a = acc.get(ch) || { w: 0, u: 0 }; a.w += wt; a.u += uu * wt; acc.set(ch, a);
        }
        const best = [...acc.entries()].sort((a, b) => b[1].w - a[1].w).slice(0, 3), ws = best.reduce((t, b) => t + b[1].w, 0) || 1;
        if (!best.length) set(v, 0, 0, 0, 1);
        best.forEach(([ch, a], k) => set(v, k, ch, a.u / a.w, a.w / ws));
      }
    }
    return { c, u, w };
  });
  return { guides, binds };
}
