// Т5's deformations of the whole figure (experiments/lines, `deform`), on the engine's bodies — each a field over
// the figure's space (src/deform.js: on the rest, or as a pose layer every frame). Sizes are shares of the body's own
// height, measured at its rest, so the same change reads the same on a child and on a man.
//   line         the line of action: the whole figure bent along one curve — seen from the front (`view: "front"`,
//                sideways) or from the side (`"side"`, forwards); `curve` "C" (one arc) or "S" (a snake); `bend` the
//                curve's amplitude as a share of the height (+ to the figure's left, or forwards). The feet stay put
//                (the bend grows in over the lowest 30 %), each section turns with the curve, so the body keeps its
//                thickness across it.
//   squash       squash and stretch with the volume kept: the height × e^stretch, the width and depth × its inverse
//                square root, about the floor and the pelvis's line
//   contrapposto the pelvis tilted one way and the shoulders the other (degrees): from the knees up to the hips the
//                pelvis's tilt grows in, from the waist to the chest it turns over into the shoulders' (×1.1); the arms
//                go with their shoulders
import { register } from '../deform.js';
import { clamp, sst } from '../regions.js';

const num = (min, max) => ({ type: 'number', min, max });

register({
  kind: 'line', of: 'figure',
  params: { view: { type: 'string', enum: ['front', 'side'] }, curve: { type: 'string', enum: ['C', 'S'] }, bend: num(-0.5, 0.5) },
  defaults: { view: 'front', curve: 'C', bend: 0.08 },
  field(p, R) {
    const H = R.height, ya = R.levels.floor, amp = p.bend * p.strength * H, ax = p.view === 'front' ? 0 : 2;
    const hj = R.skeleton.index.Hips, o0 = R.rig.joints[hj * 3 + ax];
    const S = p.curve === 'S', c = u => amp * Math.sin((S ? 2 : 1) * Math.PI * u), dc = u => amp * (S ? 2 : 1) * Math.PI * Math.cos((S ? 2 : 1) * Math.PI * u) / H;
    return (x, y, z, w, isJ, out) => {
      const u = clamp((y - ya) / H, 0, 1), g = sst(u / 0.3), th = Math.atan(dc(u)) * g, o = (ax ? z : x) - o0;
      out[0] = x; out[2] = z;
      out[ax] = o0 + c(u) * g + o * Math.cos(th); out[1] = y - o * Math.sin(th);
    };
  },
});

register({
  kind: 'squash', of: 'figure',
  params: { stretch: num(-1.5, 1.5) },
  defaults: { stretch: 0.15 },
  field(p, R) {
    const s = Math.exp(p.stretch * p.strength), k = 1 / Math.sqrt(s), y0 = R.levels.floor, hj = R.skeleton.index.Hips;
    const x0 = R.rig.joints[hj * 3], z0 = R.rig.joints[hj * 3 + 2];
    return (x, y, z, w, isJ, out) => { out[0] = x0 + (x - x0) * k; out[1] = y0 + (y - y0) * s; out[2] = z0 + (z - z0) * k; };
  },
});

register({
  kind: 'contrapposto', of: 'figure',
  params: { degrees: num(-45, 45) },
  defaults: { degrees: 10 },
  field(p, R) {
    const sk = R.skeleton, J = R.rig.joints, y = n => J[sk.index[n] * 3 + 1], t = p.degrees * p.strength * Math.PI / 180;
    const yK = (y('LeftShin') + y('RightShin')) / 2, yH = y('Hips'), yW = y('Spine2'), yC = y('Chest'), yM = yW - 0.6 * (yW - yH);
    const ang = v => v < yK ? 0 : v < yH ? t * sst((v - yK) / (yH - yK)) : v < yM ? t : v < yC ? t + (-t * 1.1 - t) * sst((v - yM) / (yC - yM)) : -t * 1.1;
    const shA = ang((y('LeftArm') + y('RightArm')) / 2), x0 = J[sk.index.Hips * 3];
    return (x, yy, z, w, isJ, out) => {
      const arm = Math.min(1, w[1] + w[2]), a0 = ang(yy), a = isJ ? (arm > 0.5 ? shA : a0) : a0 + (shA - a0) * arm, o = x - x0;
      out[0] = x0 + o * Math.cos(a); out[1] = yy - o * Math.sin(a); out[2] = z;
    };
  },
});
