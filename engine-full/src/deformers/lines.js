// Т5's deformations of the whole figure (experiments/lines, `deform`), on the engine's bodies. Sizes are shares of the
// body's own height, measured at its rest, so the same change reads the same on a child and on a man.
//   line         the line of action: the whole figure bent along one curve — seen from the front (`view: "front"`,
//                sideways) or from the side (`"side"`, forwards); `curve` "C" (one arc) or "S" (a snake); `bend` the
//                curve's amplitude as a share of the height (+ to the figure's left, or forwards). On the rest, a field:
//                the feet stay put (the bend grows in over the lowest 30 %), each section turns with the curve, so the
//                body keeps its thickness across it. As a pose layer, the same curve's turns of the pelvis and the
//                spine, neck and head (each bone turned by the curve's slope at its middle, so every bone keeps its
//                length): the pelvis stays where Kimodo put it, the legs are put back on their feet.
//   squash       squash and stretch with the volume kept: the height × e^stretch, the width and depth × its inverse
//                square root, about the floor and the pelvis's line (on the rest; as a layer, that rest change
//                weighed in each frame)
//   contrapposto the pelvis tilted one way and the shoulders the other (degrees): from the knees up to the hips the
//                pelvis's tilt grows in, from the waist to the chest it turns over into the shoulders' (×1.1); the arms
//                go with their shoulders. As a pose layer, the same as turns of the pelvis and the spine (the legs put
//                back on their feet).
import { register } from '../deform.js';
import { clamp, sst, qRot, qAxisAngle, getQ } from '../math.js';
import { turnUnder, keepFeet } from '../pose.js';
import { num } from '../schema.js';


// the line's curve: its offset (metres) and its slope's angle at a height y (metres at the rest)
function lineCurve(p, R) {
  const H = R.height, ya = R.levels.floor, amp = p.bend * p.strength * H, n = p.curve === 'S' ? 2 : 1;
  const u = y => clamp((y - ya) / H, 0, 1), g = y => sst(u(y) / 0.3);
  return {
    offset: y => amp * Math.sin(n * Math.PI * u(y)) * g(y),
    angle: y => Math.atan(amp * n * Math.PI * Math.cos(n * Math.PI * u(y)) / H) * g(y),
  };
}

register({
  kind: 'line', of: 'figure',
  params: { view: { type: 'string', enum: ['front', 'side'] }, curve: { type: 'string', enum: ['C', 'S'] }, bend: num(-0.5, 0.5) },
  defaults: { view: 'front', curve: 'C', bend: 0.08 },
  field(p, R) {
    const ax = p.view === 'front' ? 0 : 2, o0 = R.rig.joints[R.skeleton.index.Hips * 3 + ax], L = lineCurve(p, R);
    return (x, y, z, w, isJ, out) => {
      const th = L.angle(y), o = (ax ? z : x) - o0;
      out[0] = x; out[2] = z;
      out[ax] = o0 + L.offset(y) + o * Math.cos(th); out[1] = y - o * Math.sin(th);
    };
  },
  turns(p, R) { const L = lineCurve(p, R); return chainTurns(R, L.angle, p.view, p.space ?? 'pelvis'); },
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

// contrapposto's tilt at a height (radians: + the figure's left side down at the pelvis)
function tiltOf(p, R) {
  const sk = R.skeleton, J = R.rig.joints, y = n => J[sk.index[n] * 3 + 1], t = p.degrees * p.strength * Math.PI / 180;
  const yK = (y('LeftShin') + y('RightShin')) / 2, yH = y('Hips'), yW = y('Spine2'), yC = y('Chest'), yM = yW - 0.6 * (yW - yH);
  const ang = v => v < yK ? 0 : v < yH ? t * sst((v - yK) / (yH - yK)) : v < yM ? t : v < yC ? t + (-t * 1.1 - t) * sst((v - yM) / (yC - yM)) : -t * 1.1;
  return { ang, shoulders: ang((y('LeftArm') + y('RightArm')) / 2) };
}
register({
  kind: 'contrapposto', of: 'figure',
  params: { degrees: num(-45, 45) },
  defaults: { degrees: 10 },
  field(p, R) {
    const { ang, shoulders } = tiltOf(p, R), x0 = R.rig.joints[R.skeleton.index.Hips * 3];
    return (x, yy, z, w, isJ, out) => {
      const arm = Math.min(1, w[1] + w[2]), a0 = ang(yy), a = isJ ? (arm > 0.5 ? shoulders : a0) : a0 + (shoulders - a0) * arm, o = x - x0;
      out[0] = x0 + o * Math.cos(a); out[1] = yy - o * Math.sin(a); out[2] = z;
    };
  },
  turns(p, R) { return chainTurns(R, tiltOf(p, R).ang, 'front', p.space ?? 'pelvis'); },
});

// A bend of the figure given as an angle by height (at the rest) as turns of the pelvis, the spine, the neck and the
// head: each bone of that chain turned by the angle at its middle (about the figure's forward for a bend seen from the
// front, about its side for one seen from the side) — everything above goes with it, the arms with the chest — then
// the legs put back on their feet. `space`: the figure's frame now ('pelvis') or its heading alone ('upright').
const CHAIN = ['Hips', 'Spine1', 'Spine2', 'Chest', 'Neck1', 'Neck2', 'Head'];
function chainTurns(R, angle, view, space) {
  const sk = R.skeleton, J = R.rig.joints, js = CHAIN.map(n => sk.index[n]), ends = [...js.slice(1), sk.index.HeadEnd];
  const seg = js.map((j, k) => angle((J[j * 3 + 1] + J[ends[k] * 3 + 1]) / 2));
  const turn = seg.map((a, k) => (view === 'front' ? -1 : 1) * (a - (k ? seg[k - 1] : 0)));
  const before = { P: new Float64Array(sk.J * 3), Q: new Float64Array(sk.J * 4) }, H = sk.index.Hips, axis = [0, 0, 0];
  if (turn.every(t => !t)) return () => {};
  return (pose, ctx) => {
    before.P.set(pose.P); before.Q.set(pose.Q);
    let r = getQ(pose.Q, H);
    if (space === 'upright') { const f = qRot(r, [0, 0, 1]), yaw = Math.atan2(f[0], f[2]); r = [0, Math.sin(yaw / 2), 0, Math.cos(yaw / 2)]; }
    qRot(r, view === 'front' ? [0, 0, 1] : [1, 0, 0], axis);
    for (let k = 0; k < js.length; k++) if (turn[k]) turnUnder(pose, sk, js[k], qAxisAngle(axis, turn[k]));
    ctx.build();
    keepFeet(pose, ctx, before);
  };
}
