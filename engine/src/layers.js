// Pose layers: changes on top of Kimodo's motion, applied each frame in the order a character lists them, after the
// retargeting and before placement. Each takes the pose (src/pose.js), a context and its parameters (complete: the
// defaults are filled in by src/character.js), and changes turns — the places are rebuilt after each. They never
// move the body over the floor: that stays Kimodo's.
//   ctx = {rig, body?, t, morphs: {mesh id: {morph: weight}}, build()}  (build: the places again from the pelvis)
// A character's code adds its own: {kind: 'code', apply(pose, ctx)} (src/figure.js) — the same contract.
//   armsOff        {degrees}             the arms a little off the body, out to the sides (for wide hips, for cloth)
//   armsOutOfHead  {margin}              a hand or elbow that would go into the head is swung out of it (big heads)
//   amplifyLimbs   {factor, parts}       the limbs' bends against their parents, more (or less: < 1)
//   dampHeadSpine  {spine, head}         the spine's and the neck-and-head's bends, less (big heads, stiff bodies)
//   clavicleShare  {share}               Т7's fix: the collarbone takes this share of the arm's drop below its rest
//   turn           {joint, axis, degrees}   a joint turned about an axis of its own frame (and all under it): the same
//                                       change src/changes.js applies to the rest — here it rides on every frame
//   morph          {mesh?, name, weight}    a morph of a mesh weighted in this frame (before skinning)
import { qPow, qRot, qMul, qConj, qAxisAngle, getQ, setQ, getV, sub, add, cross, len, normalize } from './math.js';
import { localOf, setLocal, turnUnder } from './pose.js';

const SIDES = ['Left', 'Right'];

export const LAYERS = {
  armsOff(pose, ctx, { degrees }) {
    const sk = ctx.rig.skeleton, fwd = qRot(getQ(pose.Q, sk.index.Chest), [0, 0, 1]);
    for (const [s, sg] of [['Left', 1], ['Right', -1]]) turnUnder(pose, sk, sk.index[s + 'Arm'], qAxisAngle(fwd, sg * degrees * Math.PI / 180));
  },
  amplifyLimbs(pose, ctx, { factor, parts }) {
    const sk = ctx.rig.skeleton;
    for (let j = 0; j < sk.J; j++) if (parts.includes(sk.part[j])) setLocal(pose, sk, j, qPow(localOf(pose, sk, j), factor));
  },
  dampHeadSpine(pose, ctx, { spine, head }) {
    const sk = ctx.rig.skeleton;
    for (let j = 0; j < sk.J; j++) {
      const k = sk.part[j] === 'spine' ? spine : (sk.part[j] === 'neck' || sk.names[j] === 'Head') ? head : null;
      if (k != null) setLocal(pose, sk, j, qPow(localOf(pose, sk, j), k));
    }
  },
  armsOutOfHead(pose, ctx, { margin }) {
    if (!ctx.body) throw new Error('armsOutOfHead needs a body (its head as a ball)');
    const sk = ctx.rig.skeleton, { center, radius } = headBall(ctx.body), H = sk.index.Head, R = radius + margin;
    const rh = getV(ctx.rig.joints, H);
    for (const s of SIDES) {
      const A = sk.index[s + 'Arm'], pts = [s + 'ForeArm', s + 'Hand', s + 'HandMiddle1'].map(n => sk.index[n]);
      for (let it = 0; it < 6; it++) {
        const c = add(getV(pose.P, H), qRot(getQ(pose.Q, H), sub(center, rh)));
        let worst = null, depth = 0;
        for (const j of pts) { const x = getV(pose.P, j), d = len(sub(x, c)); if (R - d > depth) { depth = R - d; worst = x; } }
        if (!worst) break;
        const S = getV(pose.P, A), arm = sub(worst, S), out = normalize(sub(worst, c));
        const axis = cross(arm, out); if (len(axis) < 1e-6) break;
        // the turn about the shoulder that moves the point straight out of the head, by its depth
        const tang = len(cross(normalize(arm), out)) || 1;
        turnUnder(pose, sk, A, qAxisAngle(axis, depth / (len(arm) * tang) + 0.002));
        ctx.build();
      }
    }
  },
  // Т7's first fix (experiments/designed-form): the collarbone takes `share` of the arm's drop below its rest (Т7: a
  // third — as the shoulder girdle does), turning down about the horizontal line across the arm; the arm keeps its
  // turn in the world. A raised arm is left to Kimodo's own collarbone.
  clavicleShare(pose, ctx, { share }) {
    const sk = ctx.rig.skeleton, r = ctx.rig.joints;
    for (const s of SIDES) {
      const c = sk.index[s + 'Shoulder'], a = sk.index[s + 'Arm'], f = sk.index[s + 'ForeArm'];
      const L = qMul(qConj(getQ(pose.Q, c)), getQ(pose.Q, a));          // the arm against its collarbone
      const d = normalize(sub(getV(r, f), getV(r, a))), e = qRot(L, d);  // its direction at rest and now (the collarbone's rest axes)
      const drop = Math.asin(Math.max(-1, Math.min(1, d[1]))) - Math.asin(Math.max(-1, Math.min(1, e[1])));
      const h = [e[0], 0, e[2]];
      if (drop <= 0 || Math.hypot(h[0], h[2]) < 1e-6) continue;
      setQ(pose.Q, c, qMul(getQ(pose.Q, c), qAxisAngle(cross([0, 1, 0], h), share * drop)));
    }
  },
  turn(pose, ctx, { joint, axis, degrees }) {
    const sk = ctx.rig.skeleton, j = sk.index[joint];
    if (j == null) throw new Error(`turn: no joint ${joint}`);
    // the axis in the joint's frame now: Kimodo's frame of it is Q_j · frame_j
    const w = qRot(qMul(getQ(pose.Q, j), getQ(ctx.rig.frames, j)), axis);
    turnUnder(pose, sk, j, qAxisAngle(w, degrees * Math.PI / 180));
  },
  morph(pose, ctx, { mesh = 'body', name, weight }) {
    (ctx.morphs[mesh] ??= {})[name] = weight;
  },
};
// layers that only weigh morphs (no turn changed: no places to rebuild)
export const NO_REBUILD = new Set(['morph']);

// the head as a ball at rest, over the vertices the triangles use: its centre and how far its skin reaches from it on
// average (cached per mesh)
const balls = new WeakMap();
export function headBall(body) {
  const P = body.mesh.positions;
  if (balls.has(P)) return balls.get(P);
  const w = body.part('head'), use = body.mesh.isUsed, c = [0, 0, 0];
  let s = 0;
  for (let i = 0; i < body.N; i++) if (w[i] > 0.9 && use[i]) { c[0] += P[i * 3]; c[1] += P[i * 3 + 1]; c[2] += P[i * 3 + 2]; s++; }
  const center = [c[0] / s, c[1] / s, c[2] / s];
  let r = 0; for (let i = 0; i < body.N; i++) if (w[i] > 0.9 && use[i]) r += Math.hypot(P[i * 3] - center[0], P[i * 3 + 1] - center[1], P[i * 3 + 2] - center[2]);
  const ball = { center, radius: r / s };
  balls.set(P, ball);
  return ball;
}
