// A head's features as their own layer, per feature: painted on the skin (as: 'paint') or as volume (as: 'volume') —
// mixable. Both are drawn by src/head/paint.js into the face's one picture: the skin takes it by each vertex's place
// in the drawing (picturePlaces, faceUV), so it follows the skin in motion and in expressions; a feature as volume is
// also a relief of its own shape raised from the skin (its eye, brow or lips), attached to the skin's triangles under
// it (src/mesh.js: an attached mesh) and taking the same picture — it follows the skin the same way.
//   FEATURE_SCHEMA            what a feature is ({kind: eye | brow | mouth | marks | blush | tint | mask, …})
//   picturePlaces(drawn, frame) → each vertex's place in the picture (N×2)
//   faceUV(pic, N, omega) → {uv (N×2), mask (N)}
//   reliefsOf(features, {drawn, frame, pic, omega}) → [attached mesh fields]   (drawn: the head the face is drawn on, frame its)
import { SPAN, CY, browLines, mouthLines, grinLines } from './paint.js';
import { clamp, lerp, sst } from '../math.js';
import { headShares } from './frame.js';
import { num, flag, color } from '../schema.js';

const base = kind => ({ kind: { const: kind }, id: { type: 'string', pattern: /^[a-z][a-zA-Z0-9-]*$/ }, as: { type: 'string', enum: ['paint', 'volume'] }, lift: num(0, 0.2) });
export const FEATURE_SCHEMA = { type: 'union', key: 'kind', cases: {
  eye: { type: 'object', required: ['kind', 'x', 'y', 'w', 'h', 'iris', 'lash', 'lashW'], props: { ...base('eye'),
    x: num(0, 1.5), y: num(-1.5, 1), w: num(0.02, 1.5), h: num(0.02, 1.5), tilt: num(-1, 1), iris: { type: 'array', min: 2, max: 2, items: color }, lash: color, lashW: num(0, 0.3),
    wing: num(-1, 1), lower: num(0, 1), glints: { type: 'integer', min: 0, max: 3 }, lashes: { type: 'integer', min: 0, max: 6 }, look: num(-1, 1), irisScale: num(0.1, 3),
    round: flag, crease: flag, sharp: flag, smiley: flag, ringed: flag, bags: color } },
  brow: { type: 'object', required: ['kind', 'x0', 'x1', 'y0', 'y1', 'w0', 'w1', 'color'], props: { ...base('brow'),
    x0: num(-1, 1.5), x1: num(-1, 1.5), y0: num(-1.5, 1), y1: num(-1.5, 1), arch: num(-0.5, 0.5), peak: num(0.05, 0.95), w0: num(0, 0.3), w1: num(0, 0.3), color } },
  mouth: { type: 'object', required: ['kind', 'type'], props: { ...base('mouth'),
    type: { type: 'string', enum: ['drawn', 'grin', 'none'] }, y: num(-2, 0), w: num(0, 1.5), teeth: color, sag: num(-0.2, 0.2), upper: num(0, 0.3), bow: num(0, 0.1), lower: num(0, 0.3), open: num(0, 0.3),
    corners: num(-0.2, 0.2), cL: num(-0.2, 0.2), cR: num(-0.2, 0.2), lip: color, line: color, inside: color, lineW: num(0, 0.1), dimple: flag, lowerLine: num(0, 1), smile: num(0, 0.2), smileHooks: flag, crooked: num(-1, 1) } },
  marks: { type: 'object', required: ['kind', 'lines'], props: { ...base('marks'), lines: { type: 'array', items: { type: 'object', required: ['pts'], props: {
    pts: { type: 'array', min: 2, items: { type: 'array', min: 2, max: 2, items: num(-3, 3) } }, w: num(0, 0.2), color, alpha: num(0, 1), mirror: flag } } } } },
  blush: { type: 'object', required: ['kind', 'amount'], props: { ...base('blush'), amount: num(0, 2), x: num(0, 1.5), y: num(-2, 1), r: num(0, 1) } },
  tint: { type: 'object', required: ['kind', 'color'], props: { ...base('tint'), color, x: num(-1, 1), y: num(-2, 1), r: num(0, 1) } },
  mask: { type: 'object', required: ['kind', 'color', 'dark'], props: { ...base('mask'), color, dark: color, top: num(-2, 1) } },
} };
// a feature's identity in a list (a head's own feature replaces its base's of the same id)
export const featureId = f => f.id ?? f.kind;

// where each vertex is in the face's picture (head units seen from the front, N×2): its place on the head the face is
// drawn on — `drawn`, the head right after its wrap (a designed form's features are drawn where its marks put Anny's
// eyes and mouth), or Anny's own head before its form (there features are drawn where her eyes, brows and lips are:
// src/head/face.js landmarksOf). So the drawing is laid on the skin once, and whatever changes the head after — a face
// by points, Anny's own face, a head of another age, a pose layer, an expression — carries it with the skin.
export function picturePlaces(drawn, frame) {
  const P = drawn.mesh.positions, N = drawn.mesh.N, pic = new Float32Array(N * 2);
  for (let i = 0; i < N; i++) { const l = frame.toL(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]); pic[i * 2] = l[0]; pic[i * 2 + 1] = l[1]; }
  return pic;
}
// the texture coordinates of the picture's places, and how much of the picture each vertex shows (mask): 1 where the
// head faces the front — a front projection there lays the picture on the skin as drawn — fading to 0 as the skin turns
// away (round the sides, under the chin: there it would smear the picture along the skin), down the neck and outside
// the picture; there the plain skin. N: the normals of the head the face is drawn on; omega: its share of the head
export function faceUV(pic, N, omega) {
  const n = omega.length, uv = new Float32Array(n * 2), mask = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const u = 0.5 + pic[i * 2] / (2 * SPAN), v = 0.5 + (pic[i * 2 + 1] - CY) / (2 * SPAN);
    uv[i * 2] = clamp(u, 0.002, 0.998); uv[i * 2 + 1] = clamp(v, 0.002, 0.998);
    const inside = sst(clamp(Math.min(u, 1 - u, v, 1 - v) / 0.03, 0, 1));
    mask[i] = sst(clamp((omega[i] - 0.2) / 0.2, 0, 1)) * sst(clamp((N[i * 3 + 2] - 0.2) / 0.3, 0, 1)) * inside;
  }
  return { uv, mask };
}

// —— features as volume: a relief of the feature's own shape raised from the skin ——
// its outline as two curves (corner to corner) in head units, per side (the person's left: +x)
const SIDE = { 1: 'l', '-1': 'r' };
function outlines(f) {
  if (f.kind === 'brow') return [-1, 1].map(s => { const { top, bot } = browLines(f, s); const o = { top: top.map(([x, y]) => [x, y + 0.01]), bot: bot.map(([x, y]) => [x, y - 0.01]) }; if (s < 0) { o.top.reverse(); o.bot.reverse(); } return { side: SIDE[s], ...o }; });
  if (f.kind === 'eye') return [-1, 1].map(s => {
    const n = 16, cx = s * f.x, top = [], bot = [], c = Math.cos(f.tilt || 0), sn = Math.sin(f.tilt || 0), hw = f.w * (0.62 + Math.max(0, f.wing ?? 0) * 0.3);
    for (let k = 0; k <= n; k++) { const u = -1 + 2 * k / n, e = Math.sqrt(Math.max(0, 1 - u * u)), x = u * hw, yt = f.h * 0.62 * e + f.lashW * 0.6, yb = -f.h * 0.58 * e - 0.01;
      const rot = (x, y) => [cx + s * (x * c + y * sn), f.y + (-x * sn + y * c)]; top.push(rot(x, yt)); bot.push(rot(x, yb)); }
    if (s < 0) { top.reverse(); bot.reverse(); }
    return { side: SIDE[s], top, bot };
  });
  // a drawn mouth's lips, each its own relief on its own side of the lips' parting (the upper on what the jaw doesn't
  // carry, the lower on what it does: so an open jaw parts them, stretching neither)
  if (f.kind === 'mouth' && f.type === 'drawn') { const { upper, lower, line } = mouthLines(f); return [{ side: 'upper', jaw: false, top: upper.map(([x, y]) => [x * 1.06, y + 0.012]), bot: line.map(([x, y]) => [x * 1.06, y]) }, { side: 'lower', jaw: true, top: line.map(([x, y]) => [x * 1.06, y]), bot: lower.map(([x, y]) => [x * 1.06, y - 0.012]) }]; }
  if (f.kind === 'mouth' && f.type === 'grin') { const { top, bot } = grinLines(f, {}, 24); return [{ side: null, top: top.map(([x, y]) => [x * 1.04, y + 0.012]), bot: bot.map(([x, y]) => [x * 1.04, y - 0.03]) }]; }
  throw new Error(`a ${f.kind}${f.type ? ' (' + f.type + ')' : ''} has no volume: as paint only`);
}
const LIFT = { eye: 0.035, brow: 0.018, mouth: 0.025 };
export function reliefsOf(features, { drawn, frame, pic, omega }) {
  const out = [], P = drawn.mesh.positions, T = drawn.mesh.triangles;
  // the skin's triangles that face forward on the head the face is drawn on, for laying the reliefs on by where they are
  // in the picture
  const tris = [], L = Float64Array.from({ length: drawn.mesh.N * 3 }, (_, k) => (P[k] - frame.O[k % 3]) / frame.R);
  for (let t = 0; t < T.length; t += 3) {
    const a = T[t] * 3, b = T[t + 1] * 3, c = T[t + 2] * 3; if (Math.min(omega[a / 3], omega[b / 3], omega[c / 3]) < 0.5) continue;
    // facing forward: its normal (whichever way the triangle winds) out from the head's middle has z > 0
    const ux = L[b] - L[a], uy = L[b + 1] - L[a + 1], uz = L[b + 2] - L[a + 2], vx = L[c] - L[a], vy = L[c + 1] - L[a + 1], vz = L[c + 2] - L[a + 2];
    const n = [uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx], out = n[0] * (L[a] + L[b] + L[c]) + n[1] * (L[a + 1] + L[b + 1] + L[c + 1] + 0.9) + n[2] * (L[a + 2] + L[b + 2] + L[c + 2]);
    if (n[2] * Math.sign(out) > 0) tris.push(t / 3);
  }
  // where (x, y) of the picture is on the skin: the front-most triangle there (where the picture folds over), among those
  // a side of the lips' parting allows (jaw: true — what the jaw carries, false — what it doesn't), or the nearest of them
  const { jaw } = headShares(drawn.mesh, drawn.rig.skeleton), carried = t => jaw[T[t * 3]] + jaw[T[t * 3 + 1]] + jaw[T[t * 3 + 2]] > 1.5;
  const hit = (x, y, side) => {
    let best = null, near = null, nd = Infinity;
    for (const t of tris) {
      if (side != null && carried(t) !== side) continue;
      const a = T[t * 3], b = T[t * 3 + 1], c = T[t * 3 + 2], ax = pic[a * 2], ay = pic[a * 2 + 1], bx = pic[b * 2], by = pic[b * 2 + 1], cx = pic[c * 2], cy = pic[c * 2 + 1];
      const d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy); if (Math.abs(d) < 1e-12) continue;
      const w0 = ((by - cy) * (x - cx) + (cx - bx) * (y - cy)) / d, w1 = ((cy - ay) * (x - cx) + (ax - cx) * (y - cy)) / d, w2 = 1 - w0 - w1;
      if (side != null) { const e = Math.hypot((ax + bx + cx) / 3 - x, (ay + by + cy) / 3 - y); if (e < nd) { nd = e; near = { t, w: [w0, w1, w2] }; } }
      if (w0 < -1e-6 || w1 < -1e-6 || w2 < -1e-6) continue;
      const z = w0 * L[a * 3 + 2] + w1 * L[b * 3 + 2] + w2 * L[c * 3 + 2];
      if (!best || z > best.z) best = { t, z, w: [w0, w1, w2] };
    }
    if (best || !near) return best;
    const w = near.w.map(v => Math.max(0, v)), s = w[0] + w[1] + w[2];
    return { t: near.t, w: w.map(v => v / s) };
  };
  for (const f of features) {
    if ((f.as ?? 'paint') !== 'volume') continue;
    const lift = (f.lift ?? LIFT[f.kind]) * frame.R, rows = 7;
    for (const { side, jaw: carriedSide, top, bot } of outlines(f)) {
      const n = top.length, tri = [], bary = [], lifts = [], uv = [], idx = [];
      for (let k = 0; k < n; k++) for (let r = 0; r <= rows; r++) {
        const v = r / rows, x = lerp(top[k][0], bot[k][0], v), y = lerp(top[k][1], bot[k][1], v), h = hit(x, y, carriedSide);
        if (!h) throw new Error(`${featureId(f)}: its relief at (${x.toFixed(2)}, ${y.toFixed(2)}) is off the face`);
        tri.push(h.t); bary.push(...h.w);
        const e = k / (n - 1); lifts.push(lift * Math.sin(Math.PI * v) ** 0.5 * Math.sin(Math.PI * e) ** 0.35);
        uv.push(clamp(0.5 + x / (2 * SPAN), 0, 1), clamp(0.5 + (y - CY) / (2 * SPAN), 0, 1));
      }
      for (let k = 0; k + 1 < n; k++) for (let r = 0; r < rows; r++) { const a = k * (rows + 1) + r, b = a + rows + 1; idx.push(a, a + 1, b, b, a + 1, b + 1); }
      out.push({ kind: 'attached', id: side ? `${featureId(f)}-${side}` : featureId(f), host: 'body', tri: Uint32Array.from(tri), bary: Float32Array.from(bary), lift: Float32Array.from(lifts), uv: Float32Array.from(uv), triangles: idx, floor: false, painted: true, toon: true });
    }
  }
  return out;
}
