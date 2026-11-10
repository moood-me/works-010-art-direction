// Corrections on top of Kimodo's motion — named options, none on unless a character asks for it. Each takes the pose
// (src/retarget.js: Q each joint's turn from rest, P its place), the body, and its parameters, and changes the turns;
// the places are rebuilt after each. They never move the body over the floor: that stays Kimodo's.
//   armsOff        {degrees: 7}        the arms a little off the body, out to the sides (for wide hips, for cloth)
//   armsOutOfHead  {margin: 0.02}      a hand or elbow that would go into the head is swung out of it (big heads)
//   amplifyLimbs   {factor: 1.3}       the limbs' bends against their parents, more (or less: < 1)
//   dampHeadSpine  {spine: 0.7, head: 0.7}   the spine's and the neck-and-head's bends, less (big heads, stiff bodies)
import { qPow, qRot, qAxisAngle, getQ, getV, sub, add, cross, len, normalize } from './math.js';
import { localOf, setLocal, turnUnder, build } from './retarget.js';

const SIDES = ['Left', 'Right'];

export const CORRECTIONS = {
  armsOff(pose, body, { degrees = 7 }) {
    const sk = body.skeleton, fwd = qRot(getQ(pose.Q, sk.index.Chest), [0, 0, 1]);
    for (const [s, sg] of [['Left', 1], ['Right', -1]]) turnUnder(pose, sk, sk.index[s + 'Arm'], qAxisAngle(fwd, sg * degrees * Math.PI / 180));
  },
  amplifyLimbs(pose, body, { factor = 1.3, parts = ['upperArm', 'foreArm', 'thigh', 'shin'] }) {
    const sk = body.skeleton;
    for (let j = 0; j < sk.J; j++) if (parts.includes(sk.part[j])) setLocal(pose, sk, j, qPow(localOf(pose, sk, j), factor));
  },
  dampHeadSpine(pose, body, { spine = 0.7, head = 0.7 }) {
    const sk = body.skeleton;
    for (let j = 0; j < sk.J; j++) {
      const k = sk.part[j] === 'spine' ? spine : (sk.part[j] === 'neck' || sk.names[j] === 'Head') ? head : null;
      if (k != null) setLocal(pose, sk, j, qPow(localOf(pose, sk, j), k));
    }
  },
  armsOutOfHead(pose, body, { margin = 0.02 }) {
    const sk = body.skeleton, { center, radius } = headBall(body), H = sk.index.Head, R = radius + margin;
    const rh = getV(body.joints, H);
    const hipNow = getV(pose.P, sk.index.Hips);
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
        build(pose, body, hipNow);
      }
    }
  },
};

// the head as a ball at rest: its centre and how far its skin reaches from it on average (cached per body)
const balls = new WeakMap();
export function headBall(body) {
  if (balls.has(body)) return balls.get(body);
  const w = body.part('head'), c = [0, 0, 0];
  let s = 0;
  for (let i = 0; i < body.N; i++) if (w[i] > 0.9) { c[0] += body.positions[i * 3]; c[1] += body.positions[i * 3 + 1]; c[2] += body.positions[i * 3 + 2]; s++; }
  const center = [c[0] / s, c[1] / s, c[2] / s];
  let r = 0; for (let i = 0; i < body.N; i++) if (w[i] > 0.9) r += Math.hypot(body.positions[i * 3] - center[0], body.positions[i * 3 + 1] - center[1], body.positions[i * 3 + 2] - center[2]);
  const ball = { center, radius: r / s };
  balls.set(body, ball);
  return ball;
}
