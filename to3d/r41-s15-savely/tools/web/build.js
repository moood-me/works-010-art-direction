// С15 «Нуар» in 3D — the forms. The drawing is flat shapes with straight edges and hard corners, and its black is
// "what is turned from the light". So the 3D is built of few flat planes: every face is wholly lit or wholly black,
// and the black shape's edge is the planes' own edges — straight segments with hard corners, as the style's rule asks.
// Only what the drawing draws round (the skull's dome) has smooth normals.
// Units: a figure is drawn in "figure units" (y up, the ground at 0, 1 unit = 2.5 mm); a head in the style's head
// units (crown y = −100, chin ≈ +100, y down), placed on the figure by its scale.
import * as THREE from 'three';

export const S = 1 / 400;
export const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255);
export const lerp = (a, b, t) => a + (b - a) * t;
export const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
export const smooth = t => { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); };
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const norm = a => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };

// SOMA's joints (no fingers) and their parents
export const PARENT = {
  Hips: null, Spine1: 'Hips', Spine2: 'Spine1', Chest: 'Spine2', Neck1: 'Chest', Neck2: 'Neck1', Head: 'Neck2', HeadEnd: 'Head', Jaw: 'Head', LeftEye: 'Head', RightEye: 'Head',
  LeftShoulder: 'Chest', LeftArm: 'LeftShoulder', LeftForeArm: 'LeftArm', LeftHand: 'LeftForeArm',
  RightShoulder: 'Chest', RightArm: 'RightShoulder', RightForeArm: 'RightArm', RightHand: 'RightForeArm',
  LeftLeg: 'Hips', LeftShin: 'LeftLeg', LeftFoot: 'LeftShin', LeftToeBase: 'LeftFoot', LeftToeEnd: 'LeftToeBase',
  RightLeg: 'Hips', RightShin: 'RightLeg', RightFoot: 'RightShin', RightToeBase: 'RightFoot', RightToeEnd: 'RightToeBase',
};
export const BONES = Object.keys(PARENT), BI = Object.fromEntries(BONES.map((b, i) => [b, i]));

// ———————————— a mesh of flat faces, gathered triangle by triangle ————————————
// A triangle carries its paint, its bones, and what it is: lit (black where turned from the light), unlit (a sign in
// its own colour: brass, the watch's face), whether the rim of back light is drawn round it, whether the drawn face
// lies on it. Points are in figure units.
export class Forms {
  constructor() { this.T = []; this.partN = 0; }
  // o: {col, w: bone | [[bone, weight]…] | p => …, unlit, rim (default 1), face, smooth: p => bool, set: 'body' | 'props'}
  part(o) { return { id: this.partN++, rim: 1, set: 'body', ...o, colRGB: hex(o.col) }; }
  // a triangle whose normal must point away from `inside`
  tri(part, a, b, c, inside, col) {
    const n = cross(sub(b, a), sub(c, a));
    if (Math.hypot(...n) < 1e-9) return;
    if (inside && dot(n, sub([(a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3, (a[2] + b[2] + c[2]) / 3], inside)) < 0) [b, c] = [c, b];
    this.T.push({ part, p: [a, b, c], col: col ? hex(col) : part.colRGB });
  }
  quad(part, a, b, c, d, inside, col) { this.tri(part, a, b, c, inside, col); this.tri(part, a, c, d, inside, col); }
  // a flat polygon (convex or nearly): a fan from its middle
  poly(part, pts, inside, col) {
    const m = [0, 1, 2].map(k => pts.reduce((s, p) => s + p[k], 0) / pts.length);
    for (let i = 0; i < pts.length; i++) this.tri(part, m, pts[i], pts[(i + 1) % pts.length], inside, col);
  }
  // rings of the same number of points joined ring to ring; closed loops (or arcs when open); caps as fans
  loft(part, rings, { open = false, cap0 = true, cap1 = true, cols = null } = {}) {
    const cen = r => [0, 1, 2].map(k => r.reduce((s, p) => s + p[k], 0) / r.length);
    const C = rings.map(cen), n = rings[0].length;
    for (let i = 0; i < rings.length - 1; i++) {
      const a = rings[i], b = rings[i + 1], ins = [0, 1, 2].map(k => (C[i][k] + C[i + 1][k]) / 2);
      for (let j = 0; j < (open ? n - 1 : n); j++) { const k = (j + 1) % n; this.quad(part, a[j], a[k], b[k], b[j], ins, cols ? cols(i, j) : null); }
    }
    if (!open) {
      const L = rings.length - 1;
      if (cap0) this.poly(part, rings[0], C[Math.min(1, L)]);
      if (cap1) this.poly(part, rings[L], C[Math.max(L - 1, 0)]);
    }
  }
  // a flat shape with thickness: the outline `pts` (any polygon, in the plane given by its own points) pushed by
  // `back` (a vector); front, back and the edge
  slab(part, pts, back, col) {
    const tri = THREE.ShapeUtils.triangulateShape(flat2(pts), []);
    const q = pts.map(p => [p[0] + back[0], p[1] + back[1], p[2] + back[2]]);
    const mid = [0, 1, 2].map(k => (pts.reduce((s, p) => s + p[k], 0) / pts.length + q.reduce((s, p) => s + p[k], 0) / q.length) / 2);
    for (const [a, b, c] of tri) { this.tri(part, pts[a], pts[b], pts[c], mid, col); this.tri(part, q[a], q[b], q[c], mid, col); }
    for (let i = 0; i < pts.length; i++) { const j = (i + 1) % pts.length; this.quad(part, pts[i], pts[j], q[j], q[i], mid, col); }
  }
  // a box along a → b, w wide (across `side`) and t thick
  bar(part, a, b, w, t, side = [1, 0, 0], col) {
    const ax = norm(sub(b, a)), u = norm(cross(cross(ax, side), ax)), v = cross(ax, u);
    const ring = p => [[1, 1], [1, -1], [-1, -1], [-1, 1]].map(([i, j]) => [0, 1, 2].map(k => p[k] + u[k] * i * w / 2 + v[k] * j * t / 2));
    this.loft(part, [ring(a), ring(b)], { cols: col ? () => col : null });
  }

  // → geometry per set, in metres, with flat normals (smooth where the part says), bones, paints
  geometry(J) {
    const out = {};
    const key = p => `${Math.round(p[0] * 50)},${Math.round(p[1] * 50)},${Math.round(p[2] * 50)}`;
    // normals: a face's own; and per part the average at each place (for round things and for the rim's push)
    const acc = new Map();
    for (const t of this.T) {
      const n = cross(sub(t.p[1], t.p[0]), sub(t.p[2], t.p[0])); t.n = norm(n);
      // the angle at the corner weighs it: a fan of thin triangles must not outweigh one big face
      for (let i = 0; i < 3; i++) {
        const a = norm(sub(t.p[(i + 1) % 3], t.p[i])), b = norm(sub(t.p[(i + 2) % 3], t.p[i])), ang = Math.acos(clamp(dot(a, b), -1, 1));
        const k = (t.part.merge ?? t.part.id) + '|' + key(t.p[i]); const s = acc.get(k) || [0, 0, 0]; s[0] += t.n[0] * ang; s[1] += t.n[1] * ang; s[2] += t.n[2] * ang; acc.set(k, s);
      }
    }
    for (const set of new Set(this.T.map(t => t.part.set))) {
      const T = this.T.filter(t => t.part.set === set), nv = T.length * 3;
      const pos = new Float32Array(nv * 3), nor = new Float32Array(nv * 3), sn = new Float32Array(nv * 3), col = new Float32Array(nv * 3), aux = new Float32Array(nv * 4), rp = new Float32Array(nv * 3);
      const si = new Uint16Array(nv * 4), sw = new Float32Array(nv * 4);
      let v = 0;
      for (const t of T) for (let i = 0; i < 3; i++, v++) {
        const p = t.p[i], P = t.part, s = norm(acc.get((P.merge ?? P.id) + '|' + key(p)));
        const n0 = P.smooth && (P.smooth === true || P.smooth(p)) ? s : t.n, n = P.nrm ? P.nrm(n0) : n0;
        pos.set([p[0] * S, p[1] * S, p[2] * S], v * 3); nor.set(n, v * 3); sn.set(s, v * 3); col.set(t.col, v * 3); rp.set(p, v * 3);
        aux.set([P.unlit ? 1 : 0, P.face ? P.face(p, t.n) : 0, P.rim, P.cast === false ? 0 : 1], v * 4);
        let w = typeof P.w === 'function' ? P.w(p) : P.w;
        if (typeof w === 'string') w = [[w, 1]];
        w = w.filter(x => x[1] > 1e-4).sort((a, b) => b[1] - a[1]).slice(0, 4);
        const tot = w.reduce((q, x) => q + x[1], 0);
        w.forEach(([b, x], k) => { si[v * 4 + k] = BI[b]; sw[v * 4 + k] = x / tot; });
      }
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
      g.setAttribute('smoothN', new THREE.BufferAttribute(sn, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3));
      g.setAttribute('aux', new THREE.BufferAttribute(aux, 4)); g.setAttribute('rp', new THREE.BufferAttribute(rp, 3));
      g.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(si, 4)); g.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));
      out[set] = g;
    }
    return out;
  }
}
// a polygon's points in its own plane (for triangulating)
function flat2(pts) {
  let n = [0, 0, 0];
  for (let i = 0; i < pts.length; i++) { const a = pts[i], b = pts[(i + 1) % pts.length]; n[0] += (a[1] - b[1]) * (a[2] + b[2]); n[1] += (a[2] - b[2]) * (a[0] + b[0]); n[2] += (a[0] - b[0]) * (a[1] + b[1]); }
  n = norm(n);
  const u = norm(cross(Math.abs(n[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0], n)), v = cross(n, u);
  return pts.map(p => new THREE.Vector2(dot(p, u), dot(p, v)));
}

// ———————————— sections ————————————
// a rectangle with cut corners round (cx, y, cz): w, d — half sizes; cut — how much of each corner is cut (0…1)
export function box8(cx, y, cz, w, d, cut = 0.45) {
  const a = w * (1 - cut), b = d * (1 - cut);
  return [[a, d], [w, b], [w, -b], [a, -d], [-a, -d], [-w, -b], [-w, b], [-a, d]].map(([x, z]) => [cx + x, y, cz + z]);
}
// a section across a direction: `n` points round `c`, radii ru along u and rv along v
export function ringAt(c, u, v, ru, rv, n = 6, turn = 0) {
  const out = [];
  for (let i = 0; i < n; i++) { const a = turn + i / n * 2 * Math.PI; out.push([0, 1, 2].map(k => c[k] + u[k] * ru * Math.cos(a) + v[k] * rv * Math.sin(a))); }
  return out;
}
// weights by height along a chain of joints
export const chain = (J, names) => p => {
  const hs = names.map(n => J[n][1]);
  if (p[1] <= hs[0]) return [[names[0], 1]];
  for (let i = 0; i < names.length - 1; i++) if (p[1] <= hs[i + 1]) { const t = smooth((p[1] - hs[i]) / (hs[i + 1] - hs[i])); return [[names[i], 1 - t], [names[i + 1], t]]; }
  return [[names[names.length - 1], 1]];
};
// a sleeve, a trouser leg: a faceted tube through three joints with a hard corner at the middle one (the drawing's
// `limb`). r: [[ru, rv] at each joint]; the corner is shared by the two bones
export function limb(F, part0, J, [b0, b1], pts, r, { n = 6, side = [1, 0, 0], turn = Math.PI / 6, capEnd = true } = {}) {
  const [a, b, c] = pts, d0 = norm(sub(b, a)), d1 = norm(sub(c, b)), dm = norm([d0[0] + d1[0], d0[1] + d1[1], d0[2] + d1[2]]);
  const fr = d => { const u = norm(cross(cross(d, side), d)); return [u, cross(d, u)]; };
  const at = (p, q, t) => [0, 1, 2].map(k => lerp(p[k], q[k], t));
  const R = (i, j, t) => [lerp(r[i][0], r[j][0], t), lerp(r[i][1], r[j][1], t)];
  const mk = (p, d, rr) => { const [u, v] = fr(d); return ringAt(p, u, v, rr[0], rr[1], n, turn); };
  const rings = [mk(a, d0, r[0]), mk(at(a, b, 0.78), d0, R(0, 1, 0.78)), mk(b, dm, r[1]), mk(at(b, c, 0.22), d1, R(1, 2, 0.22)), mk(c, d1, r[2])];
  const wts = [[[b0, 1]], [[b0, 1]], [[b0, 0.5], [b1, 0.5]], [[b1, 1]], [[b1, 1]]];
  const lookup = new Map();
  rings.forEach((rg, i) => rg.forEach(p => lookup.set(p, wts[i])));
  const part = F.part({ ...part0 }); part.w = p => lookup.get(p) || [[b1, 1]];
  F.loft(part, rings, { cap0: true, cap1: capEnd });
  // caps' middles are new points: give them their ring's bone
  part.w = p => lookup.get(p) || (Math.hypot(...sub(p, a)) < Math.hypot(...sub(p, c)) ? [[b0, 1]] : [[b1, 1]]);
  return rings;
}

// ———————————— the head from the drawing's front and side outlines ————————————
// D: drawing.py's numbers. place: {c: [x, y, z] figure units of the head's centre, s: scale}. Returns the head's
// surface as functions (for hair, moustache, glasses) in head units, and `to` (head units → figure units).
export function headKit(D, place, { ang = 1 } = {}) {
  const ZS = 18;                                   // the side outline's middle (its x runs −65 … +100)
  const ext = (poly, y) => {
    let lo = 1e9, hi = -1e9;
    for (let i = 0; i < poly.length; i++) {
      const a = poly[i], b = poly[(i + 1) % poly.length];
      if ((a[1] - y) * (b[1] - y) > 0 || a[1] === b[1]) continue;
      const x = a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]); lo = Math.min(lo, x); hi = Math.max(hi, x);
    }
    return [lo, hi];
  };
  const yTop = Math.min(...D.front.map(p => p[1])), yBot = Math.max(...D.front.map(p => p[1]));
  const ySideBot = Math.max(...D.side.map(p => p[1]));
  const dims = y => {
    const yy = clamp(y, yTop + 0.8, Math.min(yBot, ySideBot) - 0.8);
    const f = ext(D.front, yy), s = ext(D.side, yy);
    return { w: (f[1] - f[0]) / 2, zf: ZS - s[0], zb: ZS - s[1] };
  };
  // the half section, front to back: the face in planes (half of the front, the cheek, the side), the skull round
  const ANG = [0, 26, 56, 90, 122, 152, 180].map(a => a * Math.PI / 180);
  function half(y) {
    const { w, zf, zb } = dims(y), Dp = zf - zb, t = ang * smooth((y + 62) / 44);   // ang < 1: a rounder face (a child's)
    const A = [[0, zf], [0.76 * w, zf - 0.27 * w], [0.96 * w, zf - 0.36 * Dp], [w, zf - 0.55 * Dp], [0.92 * w, zf - 0.78 * Dp], [0.5 * w, zb + 0.04 * Dp], [0, zb]];
    const zc = (zf + zb) / 2;
    return A.map((p, i) => [lerp(w * Math.sin(ANG[i]), p[0], t), lerp(zc + Dp / 2 * Math.cos(ANG[i]), p[1], t)]);
  }
  const loop = y => { const h = half(y); return [...h, ...h.slice(1, -1).reverse().map(p => [-p[0], p[1]])]; };
  const to = (X, Y, Z) => [place.c[0] + X * place.s, place.c[1] - Y * place.s, place.c[2] + Z * place.s];
  // the surface along a ray from the head's axis at angle phi (0 front, + toward +X), pushed out by `out`
  function surf(phi, y, out = 0) {
    const L = loop(y), { zf, zb } = dims(y), zc = (zf + zb) / 2, dx = Math.sin(phi), dz = Math.cos(phi);
    let best = 0;
    for (let i = 0; i < L.length; i++) {
      const a = L[i], b = L[(i + 1) % L.length], ex = b[0] - a[0], ez = b[1] - a[1], den = dx * ez - dz * ex;
      if (Math.abs(den) < 1e-9) continue;
      const t = ((a[0]) * ez - (a[1] - zc) * ex) / den, u = ((a[0]) * dz - (a[1] - zc) * dx) / den;
      if (t > 0 && u >= -1e-6 && u <= 1 + 1e-6) best = Math.max(best, t);
    }
    return [dx * (best + out), y, zc + dz * (best + out)];
  }
  // the face's front at (x, y): how far forward the surface is
  function frontZ(x, y) {
    const L = loop(y); let z = -1e9;
    for (let i = 0; i < L.length; i++) {
      const a = L[i], b = L[(i + 1) % L.length];
      if ((a[0] - x) * (b[0] - x) > 0 || a[0] === b[0]) continue;
      z = Math.max(z, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]));
    }
    return z > -1e8 ? z : dims(y).zf - 40;
  }
  return { dims, loop, surf, frontZ, to, ZS, yTop, yBot: Math.min(yBot, ySideBot), D, place };
}
// the skull and face. ys: the heights of the sections. The drawn face lies on the planes that look forward
export function skull(F, K, { col, w = 'Head', ys = [-99, -95, -86, -72, -54, -34, -10, 14, 34, 56, 76, 92] } = {}) {
  const yb = K.yBot - 0.8; ys = [...ys.filter(y => y < yb - 4), yb];
  const part = F.part({ col, w, smooth: p => (K.place.c[1] - p[1]) / K.place.s < -40, face: (p, n) => n[2] > 0.3 ? 1 : 0 });
  const rings = ys.map(y => K.loop(y).map(([x, z]) => K.to(x, y, z)));
  F.loft(part, rings);
  return part;
}
// the nose: its own piece of light with the side plane and the plane under the tip (those go black by themselves)
export function nose(F, K, { col, w = 'Head', width = null, bridge = 3, set = 'body', lean = 0.43, rim = 1 } = {}) {
  // the side planes are lit as if turned further from the front than they are: the style draws the side of a man's
  // nose black as soon as the light is on its other side (a three-quarter view too), which the true plane would not give
  const nrm = lean ? n => Math.abs(n[0]) > 0.5 ? [Math.sign(n[0]) * 0.9, n[1] * 0.3, -lean] : n : null;
  const n = K.D.nose, sp = K.D.sidePts, part = F.part({ col, w, set, nrm, rim });
  const yr = n.root[1] - 4, yt = sp.tip[1], yb = sp.nosebase[1], nw = width ?? (n.wing[0] - n.base[0]) * 0.75;
  const R = K.to(0, yr, K.frontZ(0, yr) + 1), T = K.to(0, yt, K.ZS - sp.tip[0]), Bm = K.to(0, yb, K.frontZ(0, yb) - 1);
  const yw = n.wing[1], WL = K.to(-nw, yw, K.frontZ(nw, yw) - 2), WR = K.to(nw, yw, K.frontZ(nw, yw) - 2);
  const RL = K.to(-bridge, yr, K.frontZ(bridge, yr) - 1), RR = K.to(bridge, yr, K.frontZ(bridge, yr) - 1);
  const ins = K.to(0, (yr + yb) / 2, K.frontZ(0, yt) - 20);
  F.tri(part, R, T, WL, ins); F.tri(part, R, WL, RL, ins); F.tri(part, R, WR, T, ins); F.tri(part, R, RR, WR, ins);
  F.tri(part, T, Bm, WL, ins); F.tri(part, T, WR, Bm, ins);
  return part;
}
// an ear: the drawing's side-view shape as a plate standing off the head's side
export function ears(F, K, { col, w = 'Head', x0 = 36, out = 9, set = 'body' } = {}) {
  const k = K.D.ear, ey = K.D.eye_y + 14;
  const shp = [[x0 - 8, ey - 20 * k], [x0 + 10 * k, ey - 24 * k], [x0 + 15 * k, ey - 6 * k], [x0 + 4 * k, ey + 18 * k], [x0 - 7, ey + 12 * k]];
  for (const sg of [-1, 1]) {
    const part = F.part({ col, w, set });
    const pts = shp.map(([x, y], i) => { const z = K.ZS - x, wd = K.dims(y).w; return K.to(sg * (wd - 3 + (x - (x0 - 8)) / 23 * out), y, z); });
    F.slab(part, pts, [sg * -5 * K.place.s, 0, 2 * K.place.s]);
  }
}
// hair as a curtain hung on the head: columns round it, each [phi°, top y, bottom y] — the bottom line's zigzag is
// the drawing's pointed ends; `thick` out from the skull; rows of flat faces
export function curtain(F, K, cols, { col, w = 'Head', thick = 10, yHold = 20, rows = [0, 0.3, 0.75, 1], top = 'edge', closeEnds = true, lift = () => 0, part = null } = {}) {
  part = part || F.part({ col, w });
  const P = (phi, y, out) => { const s = K.surf(phi * Math.PI / 180, Math.min(y, yHold), out); return K.to(s[0], y, s[2]); };
  const colPts = cols.map(([phi, y0, y1, th = thick]) => {
    const o = rows.map(t => P(phi, lerp(y0, y1, t), (t === 0 && top === 'edge' ? 1.5 : th * (t === 1 ? 0.75 : 1)) + lift(phi, lerp(y0, y1, t))));
    return { o, i0: P(phi, y0, -3), i1: P(phi, y1 - (y1 - y0) * 0.12, 0.5) };
  });
  const mid = (a, b) => [0, 1, 2].map(k => (a.i0[k] + a.i1[k] + b.i0[k] + b.i1[k]) / 4);
  for (let c = 0; c < colPts.length - 1; c++) {
    const a = colPts[c], b = colPts[c + 1], ins = mid(a, b);
    for (let r = 0; r < rows.length - 1; r++) F.quad(part, a.o[r], b.o[r], b.o[r + 1], a.o[r + 1], ins);
    F.quad(part, a.o[rows.length - 1], b.o[rows.length - 1], b.i1, a.i1, ins);     // the underside
    if (top === 'edge') F.quad(part, a.i0, b.i0, b.o[0], a.o[0], ins);
  }
  if (closeEnds) for (const [e, nb] of [[colPts[0], colPts[1]], [colPts[colPts.length - 1], colPts[colPts.length - 2]]]) F.poly(part, [e.i0, ...e.o, e.i1], mid(e, nb));
  return { part, colPts };
}

// hair as a cap: columns [phi°, bottom y, thickness] all round the head, meeting at the crown; the bottom line's zigzag
// is the fringe's and the nape's pointed ends, uneven thickness gives tufts; `spikes`: [phi°, y, length, width] — tufts
// that stand out of the cap
export function cap(F, K, cols, { col, w = 'Head', yHold = 20, apex = [0, -112, 0], yTop = -100, rows = [0, 0.22, 0.48, 0.74, 1], spikes = [] } = {}) {
  const part = F.part({ col, w });
  const P = (phi, y, out) => { const q = K.surf(phi * Math.PI / 180, Math.min(y, yHold), out); return K.to(q[0], y, q[2]); };
  const A = K.to(...apex), n = cols.length, ins = K.to(0, -30, 0);
  const C = cols.map(([phi, yb, th]) => ({ o: rows.map(t => P(phi, lerp(yTop, yb, t), th * (t === 1 ? 0.7 : t === 0 ? 0.55 : 1))), i: P(phi, yb - (yb - yTop) * 0.1, 0.5) }));
  for (let c = 0; c < n; c++) {
    const a = C[c], b = C[(c + 1) % n];
    F.tri(part, A, a.o[0], b.o[0], ins);
    for (let r = 0; r < rows.length - 1; r++) F.quad(part, a.o[r], b.o[r], b.o[r + 1], a.o[r + 1], ins);
    F.quad(part, a.o[rows.length - 1], b.o[rows.length - 1], b.i, a.i, [(a.i[0] + b.i[0]) / 2, (a.i[1] + b.i[1]) / 2 + 10, (a.i[2] + b.i[2]) / 2]);
  }
  for (const [phi, y, len, wd, th = 14, up = 0.5] of spikes) {
    const c = P(phi, y, th * 0.6), tip0 = P(phi, y, th + len), tip = [tip0[0], tip0[1] + len * up * K.place.s, tip0[2]];
    const base = [P(phi - wd, y, th * 0.8), P(phi, y - wd * 0.9, th * 0.8), P(phi + wd, y, th * 0.8), P(phi, y + wd * 0.9, th * 0.8)];
    for (let i = 0; i < 4; i++) F.tri(part, base[i], base[(i + 1) % 4], tip, c);
  }
  return part;
}
