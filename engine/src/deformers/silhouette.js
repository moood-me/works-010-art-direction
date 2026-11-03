// The body as one shape: its width, depth and forward place set along its height by a profile — Т5's silhouettes
// (experiments/lines: rectangle, trapezoid, triangle, V, hourglass, pear, egg, diamond, bean) and Т6's cage
// (experiments/form-tools: pear, wedge, hourglass, egg, column, bean, mass on legs, reed) are the same thing — a width,
// depth and forward profile by height — and are one deformer here; their shapes are presets (presets/silhouette-*).
//
//   keys    [{at, width, depth, forward}, …] — at: a landmark (floor, ankle, knee, crotch, hips, waist, chest, armpit,
//           shoulders, neck, head, top: src/regions.js) or a share of the height from the floor; width and depth: how
//           many times wider and deeper the body is there (about its middle line and its own centre in depth; 1 if not
//           given); forward: a move forwards, as a share of the height (0 if not given). Between keys a curve without
//           overshoot (a monotone cubic), then smoothed over `soft` (a share of the height), so no key makes a corner.
//           Above the last key and below the first the profile holds its end values.
//   arms    "clear" — the arms ride with their shoulder and turn out (away from the body, about the line across the arm
//           and its way out) as far as the new torso needs, so it doesn't swallow them; "ride" — they only ride with
//           their shoulder
// The legs ride with their root (the hip joint, moved by the profile at its height) and below it the profile makes
// each leg thicker or thinner about its own line — by how its width and depth there compare with the root's — so the
// thigh keeps its own form where it meets the body and moves with it as one in motion.
// The strength scales each change (1 + (k − 1)·strength).
//
// Why the profile is smoothed and the limbs ride (what made Т5's hard corner at the hip on the rectangle and the
// hourglass at full strength, and the shelf at the shoulders on the inverted trapezoid and the V): Т5 eased between
// its keys (zero slope at each), so close keys of very different widths made a crease; and it widened everything at
// the shoulders' height by the shoulders' factor while the neck stayed — the top of the shoulder became a shelf
// with the arm hanging under it. Here a body point's change is the smoothed profile at its height — from the
// shoulders the profile eases back to the neck's over the keys an author gives — and the limbs ride with their root.
// (Widening the shoulder along its slope from the neck was tried: it creased the chest at the armpit. Scaling the
// thighs as the torso by height sheared their tops: in a raised leg a step showed where the thigh meets the body.)
import { register } from '../deform.js';
import { levelOf } from '../regions.js';
import { clamp, lerp, sub, cross, dot, len, normalize, qAxisAngle, qRot, qRot3 } from '../math.js';
import { curve } from './curves.js';

const num = (min, max) => ({ type: 'number', min, max });
export const LEVELS = ['floor', 'ankle', 'knee', 'crotch', 'hips', 'waist', 'chest', 'armpit', 'shoulders', 'neck', 'head', 'top'];
const at = { anyOf: [{ type: 'number', min: 0, max: 1 }, { type: 'string', enum: LEVELS }] };
const KEY = { type: 'object', props: { at, width: num(0.05, 5), depth: num(0.05, 5), forward: num(-2, 2) }, required: ['at'] };
const G = 256;

register({
  kind: 'silhouette', of: 'figure',
  params: { keys: { type: 'array', min: 1, items: KEY }, soft: num(0, 0.3), arms: { type: 'string', enum: ['clear', 'ride'] } },
  defaults: { soft: 0.035, arms: 'clear' },
  field(p, R) {
    const prof = profileOf(p, R), H = R.height, y0 = R.levels.floor, sk = R.skeleton, J = R.rig.joints, x0 = J[sk.index.Hips * 3];
    const { zc, wo } = ownOf(R);
    const g = y => clamp((y - y0) / H * (G - 1), 0, G - 1);
    const read = (A, y) => { const v = g(y), i = Math.min(G - 2, Math.floor(v)), f = v - i; return A[i] + (A[i + 1] - A[i]) * f; };
    const body = (x, y, z, out) => {
      out[0] = x0 + (x - x0) * read(prof.w, y);
      const c = read(zc, y); out[2] = c + (z - c) * read(prof.d, y) + read(prof.f, y) * H;
      out[1] = y;
      return out;
    };
    const at = j => [J[j * 3], J[j * 3 + 1], J[j * 3 + 2]];
    // each arm: its root's move, and the turn out that keeps it clear of the new torso
    const arms = [];
    for (const [s, l, sg] of [['Left', 1, 1], ['Right', 2, -1]]) {
      const A = sk.index[s + 'Arm'], F = sk.index[s + 'ForeArm'], Hd = sk.index[s + 'Hand'], root = at(A), moved = body(...root, [0, 0, 0]);
      const d = sub(moved, root);
      // the turn's axis: across the arm and the way out from the body
      const axis = normalize(cross([sg, 0, 0], sub(at(Hd), root)));
      let angle = 0;
      if (p.arms === 'clear') {
        for (const [a, b] of [[A, F], [F, Hd]]) for (let k = 1; k <= 6; k++) {
          const t = k / 6, q = [0, 1, 2].map(c => J[a * 3 + c] + (J[b * 3 + c] - J[a * 3 + c]) * t);
          if (q[1] > root[1]) continue;
          // the torso's growth at this height beyond what the root's move already gives, against how far the point is
          // from the root across the turn's axis
          const v = sub(q, root), dist = len(sub(v, [axis[0] * dot(v, axis), axis[1] * dot(v, axis), axis[2] * dot(v, axis)]));
          const grow = (read(prof.w, q[1]) - 1) * read(wo, q[1]) - sg * d[0];
          if (grow > 0 && dist > 0.03 * H) angle = Math.max(angle, Math.asin(Math.min(1, grow / dist)));
        }
      }
      // turning out: about the axis, the way that moves the hand away from the body
      const r = qAxisAngle(axis, -angle), test = qRot(r, sub(at(Hd), root));
      arms.push({ limb: l, root, d, r: sg * (test[0] - (J[Hd * 3] - root[0])) >= 0 ? r : qAxisAngle(axis, angle) });
    }
    // each leg: its root's move, and its line (hip to ankle) for its thickness
    const legs = [];
    for (const [s, l] of [['Left', 3], ['Right', 4]]) {
      const A = sk.index[s + 'Leg'], B = sk.index[s + 'Foot'], root = at(A), d = sub(body(...root, [0, 0, 0]), root), foot = at(B);
      legs.push({ limb: l, root, d, foot, w: read(prof.w, root[1]), dp: read(prof.d, root[1]) });
    }
    const b = [0, 0, 0], v = [0, 0, 0];
    return (x, y, z, w, isJ, out) => {
      body(x, y, z, b);
      out[0] = b[0]; out[1] = b[1]; out[2] = b[2];
      for (const a of arms) {
        const k = isJ ? (w[a.limb] > 0.5 ? 1 : 0) : w[a.limb]; if (k <= 0) continue;
        qRot3(a.r, x - a.root[0], y - a.root[1], z - a.root[2], v);
        for (let c = 0; c < 3; c++) out[c] = lerp(b[c], a.root[c] + v[c] + a.d[c], k);
      }
      for (const a of legs) {
        const k = isJ ? (w[a.limb] > 0.5 ? 1 : 0) : w[a.limb]; if (k <= 0) continue;
        // the leg's line at this height, and the section about it as the profile there against the root's
        const t = clamp((a.root[1] - y) / (a.root[1] - a.foot[1]), 0, 1.2), lx = lerp(a.root[0], a.foot[0], t), lz = lerp(a.root[2], a.foot[2], t);
        const kx = y < a.root[1] ? read(prof.w, y) / a.w : 1, kz = y < a.root[1] ? read(prof.d, y) / a.dp : 1;
        const lx2 = lx + (x - lx) * kx + a.d[0], ly = y + a.d[1], lz2 = lz + (z - lz) * kz + a.d[2];
        out[0] = lerp(out[0], lx2, k); out[1] = lerp(out[1], ly, k); out[2] = lerp(out[2], lz2, k);
      }
    };
  },
});

// the profile on a grid over the height: width, depth, forward
function profileOf(p, R) {
  const keys = p.keys.map(k => [levelOf(R, k.at), k.width ?? 1, k.depth ?? 1, k.forward ?? 0]).sort((a, b) => a[0] - b[0]);
  const H = R.height, y0 = R.levels.floor, out = { w: new Float64Array(G), d: new Float64Array(G), f: new Float64Array(G) };
  const one = keys.length === 1;
  const cs = [1, 2, 3].map(c => one ? () => keys[0][c] : curve(dedupe(keys.map(k => [k[0], k[c]]))));
  for (let i = 0; i < G; i++) { const y = y0 + i / (G - 1) * H; out.w[i] = cs[0](y); out.d[i] = cs[1](y); out.f[i] = cs[2](y); }
  const sig = p.soft * (G - 1);
  for (const k of ['w', 'd', 'f']) { if (sig > 0.3) out[k] = blur(out[k], sig); }
  const s = p.strength;
  for (let i = 0; i < G; i++) { out.w[i] = 1 + (out.w[i] - 1) * s; out.d[i] = 1 + (out.d[i] - 1) * s; out.f[i] *= s; }
  return out;
}
const dedupe = ks => ks.filter((k, i) => i === 0 || k[0] > ks[i - 1][0] + 1e-6);
function blur(A, sig) {
  const n = A.length, out = new Float64Array(n), r = Math.ceil(sig * 3);
  for (let i = 0; i < n; i++) {
    let s = 0, ws = 0;
    for (let k = -r; k <= r; k++) { const j = clamp(i + k, 0, n - 1), w = Math.exp(-0.5 * (k / sig) ** 2); s += A[j] * w; ws += w; }
    out[i] = s / ws;
  }
  return out;
}
// the body's own centre in depth and half-width (arms left out) at each height, at its rest — kept per rest
const OWN = new WeakMap();
function ownOf(R) {
  if (OWN.has(R)) return OWN.get(R);
  const P = R.mesh.positions, H = R.height, y0 = R.levels.floor, x0 = R.rig.joints[R.skeleton.index.Hips * 3];
  const lo = new Float64Array(G).fill(Infinity), hi = new Float64Array(G).fill(-Infinity), wo = new Float64Array(G);
  for (const i of R.mesh.used) {
    if (R.limb[i * 5 + 1] + R.limb[i * 5 + 2] > 0.5) continue;
    const b = Math.round(clamp((P[i * 3 + 1] - y0) / H, 0, 1) * (G - 1));
    lo[b] = Math.min(lo[b], P[i * 3 + 2]); hi[b] = Math.max(hi[b], P[i * 3 + 2]); wo[b] = Math.max(wo[b], Math.abs(P[i * 3] - x0));
  }
  let zc = Float64Array.from(lo, (v, i) => Number.isFinite(v) ? (v + hi[i]) / 2 : NaN);
  for (let i = 1; i < G; i++) { if (Number.isNaN(zc[i])) zc[i] = zc[i - 1]; if (!wo[i]) wo[i] = wo[i - 1]; }
  for (let i = G - 2; i >= 0; i--) if (Number.isNaN(zc[i])) zc[i] = zc[i + 1];
  const o = { zc: blur(zc, 0.04 * (G - 1)), wo: blur(wo, 0.01 * (G - 1)) };
  OWN.set(R, o);
  return o;
}
