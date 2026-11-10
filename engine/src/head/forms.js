// Designed heads: a form a head's mesh is wrapped onto (src/head/wrap.js) — a distance in head units (src/head/frame.js).
// Two ways to make one:
//   curves  Г1's (experiments/heads-anime): a face lofted from its drawing's own two curves — the front outline W (its
//           half-width by height) and the side profile P (how far forward the midline reaches by height) — on a domed
//           cranium; the nose from its side curve (ridge, under, widths) or as a capsule with a ball; lips, cheeks and
//           jowls as masses; ears; the neck measured off the body it goes on
//   solid   Г2's (experiments/heads-mesh): one smooth solid read off a picture, in face units (the eyes' line y = 0,
//           the chin's bottom −1, the face's front at the eyes z = 0): a cranium, a face of rounded slices (W, Z, D,
//           B), the jaw's underside, masses, a nose of capsules, lips, the eyeballs' bulge — its cranium laid on
//           Anny's (src/head/wrap.js), or placed in head units by `place` {at, scale}
//   formOf(form, {neck}) → {sdf(x, y, z), nose (the nose's own distance, or null), full (with a piece's nose), ...}
// neck: the body's neck where it meets the head ({c: [x, y, z], r} in head units, measured by the wrap).
import { smin, clamp } from '../math.js';
import { smax, sdEll, sdCapsule, sdSphere, udTriangle, sdPoly2, catmull, keysAt, monotone, frontZ } from './shapes.js';
import { num, flag, vec } from '../schema.js';

const v2 = vec(2, -10, 10), v3 = vec(3, -10, 10);
const curve = { type: 'array', min: 1, items: v2 };
const ELL = { type: 'object', props: { at: v3, r: v3, k: num(0, 2), mirror: flag }, required: ['at', 'r'] };
const CURVES = {
  type: 'object', required: ['kind', 'face'], props: {
    kind: { const: 'curves' }, size: num(0.3, 3),
    cranium: { type: 'object', props: { w: num(0.3, 3), h: num(0.3, 3), d: num(0.3, 3) } },
    ears: { type: 'object', props: { x: num(0, 3), y: num(-3, 3), z: num(-3, 3), s: num(0, 3), h: num(0, 3) } },
    neck: { type: 'object', props: { r: num(0, 2), k: num(0, 1) } },
    face: { type: 'object', required: ['W', 'P'], props: {
      n: num(1, 6), jawRise: num(0, 2), W: curve, P: curve,
      nose: { type: 'object', props: {
        ridge: curve, under: curve, w: { type: 'array', min: 3, max: 3, items: num(0, 1) }, k: num(0, 1), round: num(0, 1), r: num(0, 1),
        root: v3, tip: v3, base: v3, radius: { anyOf: [num(0, 1), { type: 'array', min: 2, max: 2, items: num(0, 1) }] },
        ball: { type: 'object', props: { at: v3, r: num(0, 2), k: num(0, 1) }, required: ['at', 'r'] },
        wings: { type: 'object', props: { y: num(-3, 3), z: num(-3, 3), r: v3 }, required: ['y', 'z', 'r'] },
        piece: flag } },
      lips: { type: 'array', items: ELL }, masses: { type: 'array', items: ELL } } },
  },
};
const MASS = { type: 'object', props: { at: v3, r: v3, k: num(0, 2), mirror: flag }, required: ['at', 'r'] };
const SOLID = {
  type: 'object', required: ['kind', 'face', 'eye'], props: {
    kind: { const: 'solid' }, size: num(0.3, 3), place: { type: 'object', props: { at: v3, scale: num(0.05, 5), neck: { type: 'object', props: { a: v3, b: v3, rx: num(0, 3), rz: num(0, 3) }, required: ['a', 'b', 'rx', 'rz'] } }, required: ['at', 'scale'] },
    cranium: { type: 'object', props: { at: v3, r: v3 }, required: ['at', 'r'] },
    face: { type: 'object', required: ['W', 'Z', 'chinZ', 'jaw'], props: {
      n: num(1, 6), W: curve, Z: curve, D: curve, B: curve, top: num(-3, 3), topK: num(0, 1), chinZ: num(-3, 3), jaw: v2, chinK: num(0, 1), chinFrontY: num(-3, 0) } },
    eye: { type: 'object', required: ['x', 'y', 'z', 'r'], props: { x: num(0, 2), y: num(-2, 2), z: num(-2, 2), r: num(0, 1), skin: num(0, 0.5), k: num(0, 1) } },
    nose: { type: 'object', props: { root: v2, mid: v2, tip: v2, sub: v2, rRoot: num(0, 1), rMid: num(0, 1), rTip: num(0, 1), rSub: num(0, 1), tipW: num(0, 3), tipH: num(0, 3), kTip: num(0, 1), k: num(0, 1),
      wing: { type: 'object', props: { at: v3, r: v3 }, required: ['at', 'r'] } } },
    lips: { type: 'object', props: { y: num(-3, 0), w: num(0, 2), uh: num(0, 1), lh: num(0, 1), ud: num(0, 1), ld: num(0, 1), lw: num(0, 2), depth: num(0, 1), k: num(0, 1), smile: num(-1, 1), groove: num(0, 0.2), corner: num(0, 1.5) } },
    masses: { type: 'array', items: MASS }, kCF: num(0, 2), neck: { type: 'object', props: { r: num(0, 3), k: num(0, 1) } }, ear: v2,
  },
};
export const FORM_SCHEMA = { type: 'union', key: 'kind', cases: { curves: CURVES, solid: SOLID } };

// Г1's nose from its side curve: ridge (root → bridge → tip), then under (tip → base), widths at root, tip, base
function noseSDF(N) {
  const ridge = catmull(N.ridge, 8), under = catmull([N.ridge[N.ridge.length - 1], ...N.under], 6).slice(1);
  const base = N.under[N.under.length - 1], root = N.ridge[0];
  const V = [...ridge, ...under, [base[0], base[1] - 0.25], [root[0], root[1] - 0.25]];
  const y0 = root[0], y1 = N.ridge[N.ridge.length - 1][0], y2 = base[0];
  let ylo = 1e9, yhi = -1e9, zlo = 1e9, zhi = -1e9; for (const [a, b] of V) { ylo = Math.min(ylo, a); yhi = Math.max(yhi, a); zlo = Math.min(zlo, b); zhi = Math.max(zhi, b); }
  const w3 = N.w ?? [0.01, 0.02, 0.04], wmax = Math.max(...w3), M = 0.12;
  return (x, y, z) => {
    const ox = Math.abs(x) - wmax, oy = Math.max(ylo - y, y - yhi), oz = Math.max(zlo - z, z - zhi);
    if (ox > M || oy > M || oz > M) return Math.max(ox, oy, oz);   // far from the nose: the distance to its box is enough
    const d2 = sdPoly2(y, z, V), w = keysAt([[y0, w3[0]], [y1, w3[1]], [y2, w3[2]]], y);
    return smax(d2, Math.abs(x) - w, N.round ?? 0.02) - (N.r ?? 0.004);
  };
}
// the nose the skin goes over when the drawn nose is set on as its own piece: a long one pressed to `depth` of its
// reach (the piece stands out of it), a ball taken off (the capsule from root to tip, or the short ridge, stays)
function flatNose(N, depth = 0.3) {
  const o = { ...N }; delete o.ball;
  if (!N.ridge) return o;
  const z0 = N.ridge[0][1], reach = Math.max(...N.ridge.map(q => q[1])) - z0; if (reach <= depth) return o;
  const k = depth / reach, sz = q => [q[0], z0 + (q[1] - z0) * k];
  o.ridge = N.ridge.map(sz); o.under = N.under.map(sz); delete o.wings; return o;
}

function curvesForm(H, neck) {
  const F = H.face, n = F.n ?? 2.3, yTop = 0.4, yChin = F.W[F.W.length - 1][0], cr = { w: 1, h: 1, d: 1.05, ...H.cranium };
  const ears = { x: 0.92, y: -0.32, z: -0.12, s: 1, h: 1, ...H.ears }, nk = { r: 0.36, k: 0.28, ...H.neck };
  const build = N0 => {
    const NS = N0 && N0.ridge ? noseSDF(N0) : null;
    const nose = NS ? NS : N0 && N0.root ? (x, y, z) => { let d = N0.base ? udTriangle(x, y, z, N0.root, N0.tip, N0.base) - N0.radius : sdCapsule(x, y, z, N0.root, N0.tip, N0.radius); if (N0.ball) d = smin(d, sdSphere(x - N0.ball.at[0], y - N0.ball.at[1], z - N0.ball.at[2], N0.ball.r), N0.ball.k ?? 0.05); return d; } : null;
    const sdf = (x, y, z) => {
      let d = sdEll(x, y - 0.02, z + 0.04, cr.w, cr.h, cr.d);
      // the face: at each height a section as wide as the outline and reaching forward to the profile
      const yy = clamp(y, yChin, yTop), w = Math.max(0.04, keysAt(F.W, yy)), f = keysAt(F.P, yy), back = f - Math.max(1.2, w * 1.6), c = (f + back) / 2, h = (f - back) / 2;
      const q = Math.pow(Math.pow(Math.abs(x) / w, n) + Math.pow(Math.abs(z - c) / h, n), 1 / n);
      let fd = (q - 1) * Math.min(w, h * 0.6);
      const chinF = keysAt(F.P, yChin), under = yChin + (F.jawRise ?? 0.42) * Math.max(0, chinF - 0.1 - z);
      fd = smax(fd, Math.max(y - yTop, under - y), 0.08);
      d = smin(d, fd, 0.18);
      if (nose) d = smin(d, nose(x, y, z), N0.k ?? (NS ? 0.04 : 0.06));
      if (N0?.wings) d = smin(d, sdEll(x, y - N0.wings.y, z - N0.wings.z, ...N0.wings.r), NS ? 0.05 : 0.06);
      for (const L of F.lips || []) d = smin(d, sdEll(x, y - L.at[1], z - L.at[2], ...L.r), L.k ?? 0.04);
      for (const M of F.masses || []) for (const s of M.mirror === false ? [1] : [-1, 1]) d = smin(d, sdEll(x - s * M.at[0], y - M.at[1], z - M.at[2], ...M.r), M.k ?? 0.2);
      if (neck) d = smin(d, sdCapsule(x, y, z, [0, yChin + 0.5, -0.18], neck.c, [nk.r, neck.r]), nk.k);
      for (const s of [-1, 1]) d = smin(d, sdEll(x - s * ears.x, y - ears.y, z - ears.z, 0.1 * ears.s, 0.27 * ears.s * ears.h, 0.19 * ears.s), 0.06);
      return d;
    };
    return { sdf, nose };
  };
  const full = build(F.nose), skin = F.nose?.piece ? build(flatNose(F.nose)) : full;
  return { kind: 'curves', sdf: skin.sdf, full: full.sdf, nose: full.nose, chin: yChin, ears, piece: F.nose?.piece ? F.nose : null };
}

// Г2's solid (experiments/heads-mesh/py/target.py), in face units placed into head units
function solidForm(P, neck, place) {
  const F = P.face, W = monotone(F.W), Zf = monotone(F.Z), Dz = monotone(F.D ?? [[0, 0.62]]), Db = monotone(F.B ?? [[0, 0.5]]), n = F.n ?? 2.2;
  const chinY = Math.min(...F.W.map(k => k[0])), s = place.scale;
  const E = P.eye, eyes = [[E.x, E.y, E.z], [-E.x, E.y, E.z]], cr = P.cranium ?? { at: [0, 0.2, -0.85], r: [0.9, 0.95, 1] };
  const B = [chinY, F.chinZ], A = F.jaw, tl = Math.hypot(A[0] - B[0], A[1] - B[1]), nrm = [(A[1] - B[1]) / tl, -(A[0] - B[0]) / tl];
  const N = P.nose, L = P.lips;
  const noseD = N ? (x, y, z) => {
    const root = [0, ...N.root], mid = [0, ...N.mid], tip = [0, ...N.tip], sub = [0, ...N.sub], rt = N.rTip;
    let dn = smin(sdCapsule(x, y, z, root, mid, [N.rRoot, N.rMid]), sdCapsule(x, y, z, mid, [tip[0], tip[1], tip[2] - rt * 0.6], [N.rMid, rt * 0.75]), 0.03);
    dn = smin(dn, sdEll(x, y - tip[1], z - (tip[2] - rt * 0.55), rt * (N.tipW ?? 1), rt * (N.tipH ?? 0.9), rt), N.kTip ?? 0.04);
    if (N.wing) for (const sx of [1, -1]) dn = smin(dn, sdEll(x - sx * N.wing.at[0], y - N.wing.at[1], z - N.wing.at[2], ...N.wing.r), 0.03);
    return smin(dn, sdCapsule(x, y, z, [tip[0], tip[1] - rt * 0.4, tip[2] - rt * 0.5], sub, [rt * 0.55, N.rSub ?? 0.03]), 0.07);
  } : null;
  const faceFront = (xq, yq) => { const W_ = W(yq), Z_ = Zf(yq), D_ = Dz(yq); return Z_ - D_ + D_ * Math.pow(clamp(1 - Math.pow(Math.abs(xq) / W_, n), 0, 1), 1 / n); };
  const base = (x, y, z) => {
    let d = sdEll(x - cr.at[0], y - cr.at[1], z - cr.at[2], ...cr.r);
    const w = W(y), zf = Zf(y), dz = Dz(y), zc = zf - dz, db = Db(y);
    const ax = Math.abs(x) / w, az = z > zc ? (z - zc) / dz : (zc - z) / db, q = Math.pow(ax ** n + az ** n, 1 / n);
    let df = (q - 1) * Math.min(w, dz);
    df = smax(df, y - (F.top ?? 0.15), F.topK ?? 0.3);
    df = smax(df, (y - B[0]) * nrm[0] + (z - B[1]) * nrm[1], F.chinK ?? 0.12);
    d = smin(d, df, P.kCF ?? 0.25);
    for (const m of P.masses || []) for (const sx of m.mirror ? [1, -1] : [1]) d = smin(d, sdEll(x - sx * m.at[0], y - m.at[1], z - m.at[2], ...m.r), m.k ?? 0.08);
    if (noseD) d = smin(d, noseD(x, y, z), N.k ?? 0.06);
    if (L) {
      const R0 = L.depth ?? 0.14;
      for (const [h, sy, dz_] of [[L.uh, 1, L.ud], [L.lh, -1, L.ld]]) {
        if (!(dz_ > 0)) continue; const yc = L.y + sy * h * 0.5;
        d = smin(d, sdEll(x, y - yc, z - (faceFront(0, yc) - R0 + dz_), L.w * (sy > 0 ? 0.9 : L.lw ?? 0.8), h * 0.75, R0), L.k ?? 0.07);
      }
    }
    for (const e of eyes) d = smin(d, Math.hypot(x - e[0], y - e[1], z - e[2]) - (E.r + (E.skin ?? 0.03)), E.k ?? 0.08);
    return d;
  };
  // the lips' parting: a thin groove along the mouth's curve, at the face's front there
  let groove = null;
  if (L && (L.groove ?? 0.012) > 0) {
    const gr = L.groove ?? 0.012, c = L.corner ?? 0.92, xs = Array.from({ length: 9 }, (_, i) => -L.w * c + i * 2 * L.w * c / 8), ys = xs.map(x => L.y + (L.smile ?? 0) * (x / L.w) ** 2), zs = xs.map((x, i) => frontZ(base, x, ys[i], 2));
    groove = (x, y, z) => { let g = 9; for (let i = 0; i < 8; i++) g = Math.min(g, sdCapsule(x, y, z, [xs[i], ys[i], zs[i]], [xs[i + 1], ys[i + 1], zs[i + 1]], [gr * Math.sin(Math.PI * i / 8) ** 0.7, gr * Math.sin(Math.PI * (i + 1) / 8) ** 0.7])); return g; };
    groove.k = gr * 0.8;
  }
  const nk = { r: 1, k: 0.2, ...P.neck };
  // face units → head units: p_head = at + scale · p_face; distances scale by `scale`
  const toF = (x, y, z) => [(x - place.at[0]) / s, (y - place.at[1]) / s, (z - place.at[2]) / s];
  const sdf = (x, y, z) => {
    const [u, v, w] = toF(x, y, z); let d = base(u, v, w);
    if (groove) d = smax(d, -groove(u, v, w), groove.k);
    d *= s;
    // her neck (measured when laid on her: src/head/wrap.js), joined smoothly under the jaw — an elliptic capsule
    const n = place.neck;
    if (n) { const q = n.rx / n.rz; d = smin(d, sdCapsule(x, y, z * q, [0, n.a[1], n.a[2] * q], [0, n.b[1], n.b[2] * q], n.rx * nk.r), nk.k * s); }
    return d;
  };
  const toH = p => [place.at[0] + s * p[0], place.at[1] + s * p[1], place.at[2] + s * p[2]];
  // the ears: on the head's side at their height and depth (face units: P.ear [y, z]), standing out of it a little
  const [ey_, ez_] = P.ear ?? [-0.3, -0.75]; let ex = 2; while (ex > 0 && base(ex, ey_, ez_) > 0) ex -= 0.005;
  const ear = toH([ex + 0.12 / s, ey_, ez_]);   // (Г2: 12 mm out — about 0.12 head units)
  return { kind: 'solid', sdf, full: sdf, nose: noseD ? (x, y, z) => noseD(...toF(x, y, z)) * s : null, chin: place.at[1] + s * chinY, ears: { x: ear[0], y: ear[1], z: ear[2] }, piece: null, toHead: toH };
}

export function formOf(form, { neck = null, place = null } = {}) {
  if (form.kind === 'curves') return curvesForm(form, neck);
  if (form.kind === 'solid') return solidForm(form, neck, place ?? form.place);
  throw new Error(`no designed form "${form.kind}"`);
}
