// A head's features as their own layer, per feature: painted on the skin (as: 'paint') or as volume (as: 'volume') —
// mixable. Both are drawn by src/head/paint.js into the face's one picture: the skin takes it by each vertex's place
// in the drawing at the rest (faceUV), so it follows the skin in motion and in expressions; a feature as volume is
// also a relief of its own shape raised from the skin (its eye, brow or lips), attached to the skin's triangles under
// it (src/mesh.js: an attached mesh) and taking the same picture — it follows the skin the same way.
//   FEATURE_SCHEMA            what a feature is ({kind: eye | brow | mouth | marks | blush | tint | mask, …})
//   faceUV(P, mesh, frame, omega) → {uv (N×2), mask (N)}
//   reliefsOf(features, {body, frame, omega}) → [attached mesh fields]
import { SPAN, CY, browLines, mouthLines } from './paint.js';
import { clamp, lerp, sst } from '../math.js';

const num = (min, max) => ({ type: 'number', min, max }), color = { type: 'string', pattern: /^#[0-9a-f]{6}$/i }, flag = { type: 'boolean' };
const base = kind => ({ kind: { const: kind }, id: { type: 'string', pattern: /^[a-z][a-zA-Z0-9-]*$/ }, as: { type: 'string', enum: ['paint', 'volume'] }, lift: num(0, 0.2) });
export const FEATURE_SCHEMA = { type: 'union', key: 'kind', cases: {
  eye: { type: 'object', required: ['kind', 'x', 'y', 'w', 'h', 'iris', 'lash', 'lashW'], props: { ...base('eye'),
    x: num(0, 1.5), y: num(-1.5, 1), w: num(0.02, 1.5), h: num(0.02, 1.5), tilt: num(-1, 1), iris: { type: 'array', min: 2, max: 2, items: color }, lash: color, lashW: num(0, 0.3),
    wing: num(-1, 1), lower: num(0, 1), glints: { type: 'integer', min: 0, max: 3 }, lashes: { type: 'integer', min: 0, max: 6 }, look: num(-1, 1), irisScale: num(0.1, 3),
    round: flag, crease: flag, sharp: flag, smiley: flag, ringed: flag, bags: color } },
  brow: { type: 'object', required: ['kind', 'x0', 'x1', 'y0', 'y1', 'w0', 'w1', 'color'], props: { ...base('brow'),
    x0: num(-1, 1.5), x1: num(-1, 1.5), y0: num(-1.5, 1), y1: num(-1.5, 1), arch: num(-0.5, 0.5), peak: num(0.05, 0.95), w0: num(0, 0.3), w1: num(0, 0.3), color } },
  mouth: { type: 'object', required: ['kind', 'type'], props: { ...base('mouth'),
    type: { type: 'string', enum: ['drawn', 'grin', 'none'] }, y: num(-2, 0), w: num(0, 1.5), sag: num(-0.2, 0.2), upper: num(0, 0.3), bow: num(0, 0.1), lower: num(0, 0.3), open: num(0, 0.3),
    corners: num(-0.2, 0.2), cL: num(-0.2, 0.2), cR: num(-0.2, 0.2), lip: color, line: color, inside: color, lineW: num(0, 0.1), dimple: flag, lowerLine: num(0, 1), smile: num(0, 0.2), smileHooks: flag, crooked: num(-1, 1) } },
  marks: { type: 'object', required: ['kind', 'lines'], props: { ...base('marks'), lines: { type: 'array', items: { type: 'object', required: ['pts'], props: {
    pts: { type: 'array', min: 2, items: { type: 'array', min: 2, max: 2, items: num(-3, 3) } }, w: num(0, 0.2), color, alpha: num(0, 1), mirror: flag } } } } },
  blush: { type: 'object', required: ['kind', 'amount'], props: { ...base('blush'), amount: num(0, 2), x: num(0, 1.5), y: num(-2, 1), r: num(0, 1) } },
  tint: { type: 'object', required: ['kind', 'color'], props: { ...base('tint'), color, x: num(-1, 1), y: num(-2, 1), r: num(0, 1) } },
  mask: { type: 'object', required: ['kind', 'color', 'dark'], props: { ...base('mask'), color, dark: color, top: num(-2, 1) } },
} };
// a feature's identity in a list (a head's own feature replaces its base's of the same id)
export const featureId = f => f.id ?? f.kind;

// each vertex's place in the face's drawing (head units seen from the front, everywhere), and how much of the drawing
// it shows (mask: 1 on the face's front, fading to 0 round the sides of the head and down the neck — there the plain
// skin): so the drawing follows the skin and never shows behind the head, and no triangle smears it
export function faceUV(P, mesh, frame, omega) {
  const N = mesh.N, uv = new Float32Array(N * 2), mask = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    const [x, y, z] = frame.toL(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]);
    uv[i * 2] = clamp(0.5 + x / (2 * SPAN), 0.002, 0.998); uv[i * 2 + 1] = clamp(0.5 + (y - CY) / (2 * SPAN), 0.002, 0.998);
    mask[i] = sst(clamp((omega[i] - 0.2) / 0.2, 0, 1)) * sst(clamp((z + 0.15) / 0.3, 0, 1));
  }
  return { uv, mask };
}

// —— features as volume: a relief of the feature's own shape raised from the skin ——
// its outline as two curves (corner to corner) in head units, per side
function outlines(f) {
  if (f.kind === 'brow') return [-1, 1].map(s => { const { top, bot } = browLines(f, s); const o = { top: top.map(([x, y]) => [x, y + 0.01]), bot: bot.map(([x, y]) => [x, y - 0.01]) }; if (s < 0) { o.top.reverse(); o.bot.reverse(); } return o; });
  if (f.kind === 'eye') return [-1, 1].map(s => {
    const n = 16, cx = s * f.x, top = [], bot = [], c = Math.cos(f.tilt || 0), sn = Math.sin(f.tilt || 0), hw = f.w * (0.62 + Math.max(0, f.wing ?? 0) * 0.3);
    for (let k = 0; k <= n; k++) { const u = -1 + 2 * k / n, e = Math.sqrt(Math.max(0, 1 - u * u)), x = u * hw, yt = f.h * 0.62 * e + f.lashW * 0.6, yb = -f.h * 0.58 * e - 0.01;
      const rot = (x, y) => [cx + s * (x * c + y * sn), f.y + (-x * sn + y * c)]; top.push(rot(x, yt)); bot.push(rot(x, yb)); }
    if (s < 0) { top.reverse(); bot.reverse(); }
    return { top, bot };
  });
  if (f.kind === 'mouth' && f.type === 'drawn') { const { upper, lower } = mouthLines(f); return [{ top: upper.map(([x, y]) => [x * 1.06, y + 0.012]), bot: lower.map(([x, y]) => [x * 1.06, y - 0.012]) }]; }
  if (f.kind === 'mouth' && f.type === 'grin') {
    const ww = f.w, cr = (f.crooked || 0) * ww, A = [-ww * 1.04, f.y + 0.12 * ww - cr], B = [ww * 1.04, f.y + 0.12 * ww + cr], cu = [0, f.y - 0.25 * ww + 0.03], cl = [0, f.y - 0.9 * ww - 0.03], n = 24;
    const qb = (a, c, b, t) => [0, 1].map(k => (1 - t) * (1 - t) * a[k] + 2 * (1 - t) * t * c[k] + t * t * b[k]);
    return [{ top: Array.from({ length: n + 1 }, (_, k) => qb(A, cu, B, k / n)).map(([x, y]) => [x, y + 0.012]), bot: Array.from({ length: n + 1 }, (_, k) => qb(A, cl, B, k / n)) }];
  }
  throw new Error(`a ${f.kind}${f.type ? ' (' + f.type + ')' : ''} has no volume: as paint only`);
}
const LIFT = { eye: 0.035, brow: 0.018, mouth: 0.025 };
export function reliefsOf(features, { body, frame, omega }) {
  const out = [], P = body.mesh.positions, T = body.mesh.triangles;
  // the skin's triangles of the head that face forward, in head units, for laying the reliefs on (seen from the front)
  const tris = [], L = Float64Array.from({ length: body.mesh.N * 3 }, (_, k) => (P[k] - frame.O[k % 3]) / frame.R);
  for (let t = 0; t < T.length; t += 3) {
    const a = T[t] * 3, b = T[t + 1] * 3, c = T[t + 2] * 3; if (Math.min(omega[a / 3], omega[b / 3], omega[c / 3]) < 0.5) continue;
    // facing forward: its normal (whichever way the triangle winds) out from the head's middle has z > 0
    const ux = L[b] - L[a], uy = L[b + 1] - L[a + 1], uz = L[b + 2] - L[a + 2], vx = L[c] - L[a], vy = L[c + 1] - L[a + 1], vz = L[c + 2] - L[a + 2];
    const n = [uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx], out = n[0] * (L[a] + L[b] + L[c]) + n[1] * (L[a + 1] + L[b + 1] + L[c + 1] + 0.9) + n[2] * (L[a + 2] + L[b + 2] + L[c + 2]);
    if (n[2] * Math.sign(out) > 0) tris.push(t / 3);
  }
  const hit = (x, y) => {
    let best = null;
    for (const t of tris) {
      const a = T[t * 3], b = T[t * 3 + 1], c = T[t * 3 + 2], ax = L[a * 3], ay = L[a * 3 + 1], bx = L[b * 3], by = L[b * 3 + 1], cx = L[c * 3], cy = L[c * 3 + 1];
      const d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy); if (Math.abs(d) < 1e-12) continue;
      const w0 = ((by - cy) * (x - cx) + (cx - bx) * (y - cy)) / d, w1 = ((cy - ay) * (x - cx) + (ax - cx) * (y - cy)) / d, w2 = 1 - w0 - w1;
      if (w0 < -1e-6 || w1 < -1e-6 || w2 < -1e-6) continue;
      const z = w0 * L[a * 3 + 2] + w1 * L[b * 3 + 2] + w2 * L[c * 3 + 2];
      if (!best || z > best.z) best = { t, z, w: [w0, w1, w2] };
    }
    return best;
  };
  for (const f of features) {
    if ((f.as ?? 'paint') !== 'volume') continue;
    const lift = (f.lift ?? LIFT[f.kind]) * frame.R, rows = 7;
    for (const [side, { top, bot }] of outlines(f).entries()) {
      const n = top.length, tri = [], bary = [], lifts = [], uv = [], idx = [];
      for (let k = 0; k < n; k++) for (let r = 0; r <= rows; r++) {
        const v = r / rows, x = lerp(top[k][0], bot[k][0], v), y = lerp(top[k][1], bot[k][1], v), h = hit(x, y);
        if (!h) throw new Error(`${featureId(f)}: its relief at (${x.toFixed(2)}, ${y.toFixed(2)}) is off the face`);
        tri.push(h.t); bary.push(...h.w);
        const e = k / (n - 1); lifts.push(lift * Math.sin(Math.PI * v) ** 0.5 * Math.sin(Math.PI * e) ** 0.35);
        uv.push(clamp(0.5 + x / (2 * SPAN), 0, 1), clamp(0.5 + (y - CY) / (2 * SPAN), 0, 1));
      }
      for (let k = 0; k + 1 < n; k++) for (let r = 0; r < rows; r++) { const a = k * (rows + 1) + r, b = a + rows + 1; idx.push(a, a + 1, b, b, a + 1, b + 1); }
      out.push({ kind: 'attached', id: `${featureId(f)}${side ? '-r' : ''}`, host: 'body', tri: Uint32Array.from(tri), bary: Float32Array.from(bary), lift: Float32Array.from(lifts), uv: Float32Array.from(uv), triangles: idx, floor: false, painted: true, toon: true });
    }
  }
  return out;
}
