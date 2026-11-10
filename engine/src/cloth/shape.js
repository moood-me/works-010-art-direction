// A garment's designed silhouette (О1's, experiments/clothes-good-bodies `tailor`; this is the source now): the garment
// as cut is read round an axis — the trunk (the spine, then straight down from the hips), each sleeve along its arm,
// each trouser leg along its leg — as rings of radius by height and by angle, and on those rings its design is drawn:
// how stiff the cloth is (it bridges the body's hollows: each ring toward its convex hull), where it starts to hang and
// falls straight from its widest ring, its silhouette below that (A-line, bell, full, tulip, pencil, trapeze, bubble;
// sleeves fitted, straight, puff, bell, bishop, cap; legs straight, wide, flare, taper, balloon), the shape of its
// section (round to square), its length, and folds as a drawn rhythm round the hem. Each point of the cloth keeps its
// height and angle and takes the designed radius. О1's ladder down to the sign is not carried (the pictogram Т4 keeps
// the sign).
// In the engine the designed form is what the cloth is cut to (its lengths: src/cloth/sim.js) and the shape it is pulled
// toward with the garment's strength — from a stiff petticoat that holds the bell (1) to cloth hanging freely (0).
//   designedForm(cut, B, design, pattern) → Float32Array (the form at the rest, the cut's points)
//   SHAPE: the design's keys (a preset of group garment-shape holds them)
import { num } from '../schema.js';
import { clamp, lerp, sst } from '../math.js';

export const PROFILE = {
  straight: () => 0, aline: u => u, bell: u => 1 - (1 - u) ** 2.2, full: u => Math.sin(Math.min(1, u * 1.25) * Math.PI / 2) ** 0.7,
  tulip: u => 0.55 * Math.sin(Math.PI * u) - 0.35 * u, pencil: u => -0.6 * u * u, trapeze: u => u ** 0.9, bubble: u => 0.8 * Math.sin(Math.PI * Math.min(1, u * 1.05)) ** 0.8 - 0.2 * u,
};
export const SLEEVE = {
  fitted: () => 0, straight: () => 0.08, puff: u => 0.9 * Math.exp(-(((u - 0.18) / 0.16) ** 2)) - 0.12 * u, bell: u => 0.15 + 1.3 * u ** 2.2,
  bishop: u => 0.2 + 1.0 * Math.exp(-(((u - 0.78) / 0.2) ** 2)), cap: u => 0.55 * Math.exp(-(((u - 0.1) / 0.12) ** 2)),
};
export const LEG = {
  fitted: () => 0, straight: () => 0, wide: u => 0.9 * u, flare: u => 1.1 * Math.max(0, u - 0.55) ** 1.3 * 2, taper: u => -0.35 * u,
  balloon: u => 0.7 * Math.sin(Math.PI * Math.min(1, u * 1.05)) ** 0.7 - 0.25 * u,
};
// shape: the trunk's silhouette below where it hangs; flare: how much (a share of the ring's radius); stiff: how much it
// bridges hollows (0 follows the body, 1 its convex hull); from: where it hangs (shoulder, bust, waist, hip); ease (m)
// and fit (how closely it follows the body above that); square (the section's power: 2 round, 4 square) and round (how
// far toward it); length (the hem's, a share of the length below where it hangs); folds, foldN, foldPhase (drawn folds:
// depth, how many, where they start round the ring); sleeve, leg (their silhouettes)
export const SHAPE = {
  shape: { type: 'string', enum: Object.keys(PROFILE) }, flare: num(-1, 3), stiff: num(0, 1), from: { type: 'string', enum: ['shoulder', 'bust', 'waist', 'hip'] },
  ease: num(0, 0.1), fit: num(0, 1), square: num(1, 8), round: num(0, 1), length: num(0.5, 1.6), folds: num(0, 1), foldN: num(2, 40), foldPhase: num(-7, 7),
  sleeve: { type: 'string', enum: Object.keys(SLEEVE) }, leg: { type: 'string', enum: Object.keys(LEG) },
};

const TAU = Math.PI * 2, NTH = 64, DS = 0.012;
// an axis through the joints, bent smoothly through them (centripetal Catmull–Rom), as segments 1 cm long
function polyAxis(pts) {
  const n = pts.length, ext = [sub3(pts[0], sub3(pts[1], pts[0])), ...pts, add3(pts[n - 1], sub3(pts[n - 1], pts[n - 2]))], dense = [];
  for (let i = 1; i < n; i++) {
    const [p0, p1, p2, p3] = [ext[i - 1], ext[i], ext[i + 1], ext[i + 2]], t = (a, b) => Math.max(1e-6, Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]) ** 0.5);
    const t0 = 0, t1 = t0 + t(p0, p1), t2 = t1 + t(p1, p2), t3 = t2 + t(p2, p3);
    for (let s = 0; s < 40; s++) {
      const u = t1 + (t2 - t1) * s / 40, L = (a, b, ta, tb) => a.map((v, c) => ((tb - u) * v + (u - ta) * b[c]) / (tb - ta));
      const A1 = L(p0, p1, t0, t1), A2 = L(p1, p2, t1, t2), A3 = L(p2, p3, t2, t3), B1 = L(A1, A2, t0, t2), B2 = L(A2, A3, t1, t3);
      dense.push(L(B1, B2, t1, t2));
    }
  }
  dense.push(pts[n - 1]);
  // (spaced evenly along it)
  const acc = [0]; for (let k = 1; k < dense.length; k++) acc.push(acc[k - 1] + dist3(dense[k], dense[k - 1]));
  const len = acc[acc.length - 1], m = Math.max(8, Math.round(len / 0.01)), even = [];
  for (let q = 0, k = 0; q <= m; q++) { const s = len * q / m; while (k < acc.length - 2 && acc[k + 1] < s) k++; const f = (s - acc[k]) / Math.max(1e-12, acc[k + 1] - acc[k]); even.push(dense[k].map((v, c) => v + (dense[k + 1][c] - v) * f)); }
  const segs = []; let s0 = 0;
  for (let k = 0; k + 1 < even.length; k++) { const a = even[k], e = sub3(even[k + 1], a), L = Math.hypot(...e); segs.push({ a, e: e.map(v => v / L), L, s0 }); s0 += L; }
  return { segs, len: s0 };
}
// a point's height along the axis, its angle round it (0 to the front, π/2 to the body's left), its distance from it
function cyl(ax, x) {
  let best = null, bd = Infinity;
  for (const sg of ax.segs) { const d = sub3(x, sg.a), t = clamp(dot3(d, sg.e), 0, sg.L), c = sg.a.map((v, k) => v + sg.e[k] * t), q = dist3(x, c) ** 2; if (q < bd) { bd = q; best = { sg, t, c }; } }
  const { sg, t, c } = best, e = sg.e;
  let f = [-e[0] * e[2], -e[1] * e[2], 1 - e[2] * e[2]]; if (Math.hypot(...f) < 1e-3) f = [-e[0] * e[1], 1 - e[1] * e[1], -e[2] * e[1]];
  const fl = Math.hypot(...f); f = f.map(v => v / fl);
  const sd = cross3(e, f), d0 = sub3(x, c), al = dot3(d0, e), d = d0.map((v, k) => v - e[k] * al);
  return { s: sg.s0 + t, th: Math.atan2(dot3(d, sd), dot3(d, f)), r: Math.hypot(...d), c, e, f, sd };
}
function hull2(P) {
  P.sort((a, b) => a[0] - b[0] || a[1] - b[1]); const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = []; for (const p of P) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); }
  for (let i = P.length - 1; i >= 0; i--) { const p = P[i]; while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], p) <= 0) up.pop(); up.push(p); }
  up.pop(); lo.pop(); return lo.concat(up);
}
// the radius of a convex outline seen from the axis at an angle
function rayHull(H, th) {
  const dx = Math.cos(th), dy = Math.sin(th); let best = 0;
  for (let k = 0; k < H.length; k++) { const [ax, ay] = H[k], [bx, by] = H[(k + 1) % H.length], ex = bx - ax, ey = by - ay, den = dx * ey - dy * ex; if (Math.abs(den) < 1e-12) continue;
    const t = (ax * ey - ay * ex) / den, u = (ax * dy - ay * dx) / den; if (t > 0 && u >= -1e-6 && u <= 1 + 1e-6) best = Math.max(best, t); }
  return best;
}
// the rings of a part: the outermost cloth in each cell of height × angle, the gaps filled from the neighbours
function rings(pts) {
  let smax = 0; for (const p of pts) smax = Math.max(smax, p.s);
  const NS = Math.ceil(smax / DS) + 2, E = new Float32Array(NS * NTH).fill(-1);
  for (const p of pts) { const i = Math.round(p.s / DS), j = ((Math.round(p.th / TAU * NTH) % NTH) + NTH) % NTH; E[i * NTH + j] = Math.max(E[i * NTH + j], p.r); }
  let first = NS, last = 0; for (let i = 0; i < NS; i++) for (let j = 0; j < NTH; j++) if (E[i * NTH + j] >= 0) { first = Math.min(first, i); last = Math.max(last, i); }
  for (let pass = 0; pass < 60; pass++) {
    let any = false; const F = Float32Array.from(E);
    for (let i = first; i <= last; i++) for (let j = 0; j < NTH; j++) { if (E[i * NTH + j] >= 0) continue; let s = 0, n = 0; for (const [a, b] of [[0, 1], [0, -1], [1, 0], [-1, 0]]) { const ii = i + a, jj = (j + b + NTH) % NTH; if (ii < first || ii > last) continue; const v = E[ii * NTH + jj]; if (v >= 0) { s += v; n++; } } if (n) { F[i * NTH + j] = s / n; any = true; } }
    E.set(F); if (!any) break;
  }
  return { E, NS, first, last };
}
// smoothing round the rings and along the length; at the first and the last ring the form goes on as it was going
function ringSmooth(R, NS, it, ka = 0.5, ks = 0.5, first = 0, last = NS - 1) {
  let A = Float32Array.from(R), B = Float32Array.from(R);
  for (let k = 0; k < it; k++) {
    for (let i = first; i <= last; i++) for (let j = 0; j < NTH; j++) {
      const c = A[i * NTH + j], l = A[i * NTH + (j + 1) % NTH], r = A[i * NTH + (j + NTH - 1) % NTH];
      let u = i > first ? A[(i - 1) * NTH + j] : null, d = i < last ? A[(i + 1) * NTH + j] : null; if (u == null) u = d == null ? c : 2 * c - d; if (d == null) d = 2 * c - u;
      B[i * NTH + j] = c + ka * ((l + r) / 2 - c) * 0.5 + ks * ((u + d) / 2 - c) * 0.5;
    }
    [A, B] = [B, A];
  }
  return A;
}
// the section of a ring drawn as a superellipse over its own front, back and side extents (n 2 round, 4+ square)
function superRing(R, n) {
  const ext = [0, 0, 0, 0];
  for (let j = 0; j < NTH; j++) { const th = j / NTH * TAU, x = R[j] * Math.cos(th), y = R[j] * Math.sin(th); ext[0] = Math.max(ext[0], x); ext[2] = Math.max(ext[2], -x); ext[1] = Math.max(ext[1], y); ext[3] = Math.max(ext[3], -y); }
  return Array.from({ length: NTH }, (_, j) => { const th = j / NTH * TAU, c = Math.cos(th), s = Math.sin(th), a = c >= 0 ? ext[0] : ext[2], b = s >= 0 ? ext[1] : ext[3]; return 1 / Math.pow(Math.abs(c / a) ** n + Math.abs(s / b) ** n, 1 / n); });
}

// the designed form of a garment as cut (cut: {positions, triangles, near}) on the body B (src/cloth/patterns.js onBody)
export function designedForm(cut, B, d, pattern) {
  const P = cut.positions, V = P.length / 3, T = cut.triangles, R0 = B.regions, segs = R0.segs, J = n => { const j = B.J(n); return [j.x, j.y, j.z]; };
  const hangs = !!pattern.hangs, trousers = !!pattern.trousers, hip = J('Hips');
  const trunkAx = polyAxis([J('Neck1'), J('Chest'), J('Spine2'), J('Spine1'), hip, [hip[0], hip[1] - 1.4, hip[2]]]), ax = { trunk: trunkAx };
  for (const s of ['Left', 'Right']) {
    const h = J(s + 'Hand'), f = J(s + 'ForeArm'); ax['arm' + s] = polyAxis([J(s + 'Arm'), f, h, add3(h, sub3(h, f).map(v => v * 0.5))]);
    const ft = J(s + 'Foot'); ax['leg' + s] = polyAxis([J(s + 'Leg'), J(s + 'Shin'), ft, [ft[0], ft[1] - 0.1, ft[2]]]);
  }
  // each point's part: by the skin it lies on
  const part = new Array(V);
  for (let i = 0; i < V; i++) {
    const sg = segs[R0.seg[cut.near[i] * 2]], side = sg.side > 0 ? 'Left' : 'Right';
    part[i] = ['arm', 'fore', 'hand'].includes(sg.kind) ? 'arm' + side : trousers && ['thigh', 'shin', 'foot'].includes(sg.kind) && P[i * 3 + 1] < hip[1] - 0.06 ? 'leg' + side : 'trunk';
  }
  // where on the form each point goes is read from the cloth smoothed first: a real crease folds the cloth back on
  // itself, and read as it is it would fold the drawn form too
  const nb = Array.from({ length: V }, () => new Set());
  for (let t = 0; t < T.length; t += 3) { const a = T[t], b = T[t + 1], c = T[t + 2]; nb[a].add(b).add(c); nb[b].add(a).add(c); nb[c].add(a).add(b); }
  const NB = nb.map(x => Int32Array.from(x));
  let Q = Float32Array.from(P), Tm = new Float32Array(Q.length);
  for (let k = 0; k < 30; k++) for (const lam of [0.6, -0.62]) { for (let i = 0; i < V; i++) { const ns = NB[i]; for (let q = 0; q < 3; q++) { if (!ns.length) { Tm[i * 3 + q] = Q[i * 3 + q]; continue; } let sm = 0; for (const j of ns) sm += Q[j * 3 + q]; Tm[i * 3 + q] = Q[i * 3 + q] + lam * (sm / ns.length - Q[i * 3 + q]); } } [Q, Tm] = [Tm, Q]; }
  // the garment's pieces (a lining, a flap, a belt): each a connected part of the mesh
  const comp = new Int32Array(V).fill(-1); let ncomp = 0;
  for (let i = 0; i < V; i++) { if (comp[i] >= 0) continue; const st = [i]; comp[i] = ncomp; while (st.length) { const v = st.pop(); for (const w of NB[v]) if (comp[w] < 0) { comp[w] = ncomp; st.push(w); } } ncomp++; }
  const Qn = new Float32Array(Q.length);
  for (let t = 0; t < T.length; t += 3) { const a = T[t] * 3, b = T[t + 1] * 3, c = T[t + 2] * 3, u = [Q[b] - Q[a], Q[b + 1] - Q[a + 1], Q[b + 2] - Q[a + 2]], w = [Q[c] - Q[a], Q[c + 1] - Q[a + 1], Q[c + 2] - Q[a + 2]], n = cross3(u, w); for (const k of [a, b, c]) for (let q = 0; q < 3; q++) Qn[k + q] += n[q]; }
  for (let i = 0; i < Qn.length; i += 3) { const l = Math.hypot(Qn[i], Qn[i + 1], Qn[i + 2]) || 1; Qn[i] /= l; Qn[i + 1] /= l; Qn[i + 2] /= l; }
  const by = {}, C = new Array(V);
  for (let i = 0; i < V; i++) { C[i] = cyl(ax[part[i]], [Q[i * 3], Q[i * 3 + 1], Q[i * 3 + 2]]); (by[part[i]] ??= []).push(i); }
  const out = Float32Array.from(P);
  // the body under the trunk, ring by ring: a fitted bodice follows it with a little ease
  const skinT = [];
  for (const i of B.used) { const k = segs[R0.seg[i * 2]].kind; if (k === 'torso' || k === 'clav') skinT.push(cyl(trunkAx, [B.rest[i * 3], B.rest[i * 3 + 1], B.rest[i * 3 + 2]])); }
  for (const [pname, idx] of Object.entries(by)) {
    // a sleeve or a trouser leg is drawn only where the design says what it is (a dress's strap is left as it is)
    if (pname.startsWith('arm') && !d.sleeve) continue;
    if (pname.startsWith('leg') && !d.leg && !trousers) continue;
    const Rg = rings(idx.map(i => C[i])), { NS, first, last } = Rg, E = ringSmooth(Rg.E, NS, 2, 0.5, 0.5, first, last), R = new Float32Array(NS * NTH);
    const isTrunk = pname === 'trunk', isArm = pname.startsWith('arm');
    // stiffness: the cloth bridges the body's hollows — the outline of each ring toward its convex hull
    for (let i = first; i <= last; i++) {
      const row = E.subarray(i * NTH, i * NTH + NTH), H = hull2(Array.from(row, (r, j) => [r * Math.cos(j / NTH * TAU), r * Math.sin(j / NTH * TAU)]));
      for (let j = 0; j < NTH; j++) R[i * NTH + j] = lerp(row[j], rayHull(H, j / NTH * TAU) || row[j], d.stiff ?? 0.6);
    }
    // where it hangs from: below that the cloth falls straight from its widest ring
    let h0 = first;
    if (isTrunk) { const sAt = n => cyl(trunkAx, J(n)).s; h0 = Math.round(({ shoulder: sAt('Chest') - 0.04, bust: sAt('Chest') + 0.05, waist: sAt('Spine1'), hip: sAt('Hips') + 0.04 })[d.from ?? (hangs ? 'waist' : 'bust')] / DS); h0 = clamp(h0, first, last); }
    else h0 = first + Math.round(0.03 / DS);
    // above it the cloth is fitted: the body's own rings (their hollows bridged as the cloth is stiff) and the ease;
    // no ring of the drawn form inside the body
    let floor = null;
    if (isTrunk) {
      const Bg = rings(skinT.filter(p => p.s <= (h0 + 2) * DS)), Bm = ringSmooth(Bg.E, Bg.NS, 2, 0.5, 0.5, Bg.first, Bg.last).map((v, k) => Math.max(v, Bg.E[k])), ease = d.ease ?? 0.012, fitK = d.fit ?? 0.85;
      for (let i = Math.max(first, Bg.first); i <= Math.min(h0, Bg.last); i++) {
        const row = Bm.subarray(i * NTH, i * NTH + NTH), H = hull2(Array.from(row, (r, j) => [r * Math.cos(j / NTH * TAU), r * Math.sin(j / NTH * TAU)]));
        for (let j = 0; j < NTH; j++) R[i * NTH + j] = lerp(R[i * NTH + j], lerp(row[j], rayHull(H, j / NTH * TAU) || row[j], d.stiff ?? 0.6) + ease, fitK);
      }
      const Ba = rings(skinT), BmA = ringSmooth(Ba.E, Ba.NS, 2, 0.5, 0.5, Ba.first, Ba.last).map((v, k) => Math.max(v, Ba.E[k]));
      floor = new Float32Array(NS * NTH); for (let i = Math.max(first, Ba.first); i <= Math.min(last, Ba.last); i++) for (let j = 0; j < NTH; j++) floor[i * NTH + j] = BmA[i * NTH + j] + 0.006;
    }
    if (isTrunk ? (hangs || d.from) : true) for (let i = h0 + 1; i <= last; i++) for (let j = 0; j < NTH; j++) R[i * NTH + j] = Math.max(R[i * NTH + j], R[(i - 1) * NTH + j] * (isTrunk ? 1 : 0.985));
    // the silhouette below where it hangs
    const prof = isTrunk ? PROFILE[d.shape ?? 'straight'] : isArm ? SLEEVE[d.sleeve ?? 'fitted'] : LEG[d.leg ?? 'straight'], amp = isTrunk ? d.flare ?? 0.5 : 1, top = isTrunk ? h0 : first;
    let base = 0; for (let j = 0; j < NTH; j++) base += R[top * NTH + j]; base /= NTH;
    for (let i = top; i <= last; i++) { const k = prof((i - top) / Math.max(1, last - top)) * amp; for (let j = 0; j < NTH; j++) R[i * NTH + j] = Math.max(R[i * NTH + j] * 0.6, R[i * NTH + j] + base * k); }
    // the section: toward a superellipse of the ring's own extents
    for (let i = first; i <= last; i++) { const row = R.subarray(i * NTH, i * NTH + NTH), se = superRing(row, d.square ?? 2.2); for (let j = 0; j < NTH; j++) row[j] = lerp(row[j], se[j], d.round ?? 0.6); }
    // smooth along its length and round its rings: what is left of the real cloth's creases goes
    if (floor) for (let k = 0; k < R.length; k++) R[k] = Math.max(R[k], floor[k]);
    let Rs = ringSmooth(R, NS, 3, 0.5, 0, first, last); Rs = ringSmooth(Rs, NS, 14, 0, 0.9, first, last);
    // folds as a drawn rhythm: n soft flutes round the ring, growing toward the hem
    if ((d.folds ?? 0) > 0 && (!isTrunk || hangs || d.from)) {
      const n = d.foldN ?? 8, depth = d.folds;
      for (let i = top; i <= last; i++) { const u = (i - top) / Math.max(1, last - top); for (let j = 0; j < NTH; j++) { const w = Math.cos(n * j / NTH * TAU + (d.foldPhase ?? 0)); Rs[i * NTH + j] *= 1 + depth * u ** 1.4 * (0.5 * w + 0.5 * Math.sign(w) * Math.abs(w) ** 0.5); } }
    }
    Rs = ringSmooth(Rs, NS, 1, 0.3, 0.3, first, last);
    if (floor) for (let k = 0; k < Rs.length; k++) Rs[k] = Math.max(Rs[k], floor[k] - 0.004);
    const look = (i, th) => { const x = clamp(i, first, last), j0 = ((th / TAU * NTH) % NTH + NTH) % NTH, ja = Math.floor(j0), jb = (ja + 1) % NTH, f = j0 - ja; return [Rs[x * NTH + ja] * (1 - f) + Rs[x * NTH + jb] * f, E[x * NTH + ja] * (1 - f) + E[x * NTH + jb] * f]; };
    // pieces lying under others keep their order (each a few millimetres inside the one over it); and where the cloth
    // folds back on itself (a turned-up hem, a wrap) the folded part faces inward and stays inside
    const sum = new Float64Array(ncomp), cnt = new Float64Array(ncomp), depthOf = new Float32Array(idx.length);
    idx.forEach((i, k) => { const p = C[i], fi = p.s / DS, i0 = Math.floor(fi), t = fi - i0, Ed = lerp(look(i0, p.th)[1], look(i0 + 1, p.th)[1], t); depthOf[k] = p.r - Ed; sum[comp[i]] += depthOf[k]; cnt[comp[i]]++; });
    const layer = new Int32Array(ncomp); for (let k = 0; k < ncomp; k++) layer[k] = cnt[k] > 0 && sum[k] / cnt[k] < -0.006 ? 1 : 0;
    const facing = new Float64Array(ncomp), inward = new Uint8Array(idx.length);
    idx.forEach((i, k) => { const p = C[i], ct = Math.cos(p.th), st = Math.sin(p.th); depthOf[k] = Qn[i * 3] * (p.f[0] * ct + p.sd[0] * st) + Qn[i * 3 + 1] * (p.f[1] * ct + p.sd[1] * st) + Qn[i * 3 + 2] * (p.f[2] * ct + p.sd[2] * st); facing[comp[i]] += depthOf[k]; });
    idx.forEach((i, k) => inward[k] = depthOf[k] * Math.sign(facing[comp[i]]) < -0.15 ? 1 : 0);
    idx.forEach((i, k) => {
      const p = C[i], fi = p.s / DS, i0 = Math.floor(fi), t = fi - i0, [ra, ea] = look(i0, p.th), [rb, eb] = look(i0 + 1, p.th), Rd = lerp(ra, rb, t) - layer[comp[i]] * 0.004 - inward[k] * 0.005, Ed = lerp(ea, eb, t);
      // sleeves and trouser legs keep to the cloth where they meet the trunk; a layer under the outermost (a lining, a
      // flap behind a slit) stays a little inside it
      const w = isTrunk ? 1 : sst(clamp(p.s / 0.05, 0, 1)), rn = lerp(p.r, Rd - (p.r < Ed - 0.015 ? 0.005 : 0), w);
      // the hem's length, as the design wants it
      const ds = isTrunk && (hangs || d.from) && d.length && p.s > h0 * DS ? (p.s - h0 * DS) * (d.length - 1) : 0, ct = Math.cos(p.th), st = Math.sin(p.th);
      for (let q = 0; q < 3; q++) out[i * 3 + q] = p.c[q] + p.e[q] * ds + (p.f[q] * ct + p.sd[q] * st) * rn;
    });
  }
  return out;
}
const sub3 = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add3 = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], dot3 = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross3 = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]], dist3 = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
