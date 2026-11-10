// Т5's changes of the limbs (experiments/lines, `deform`: limbOp) — the arms from the shoulder to the wrist, the legs
// from the hip to the ankle, each as one chain of two bones; every point by its share of that limb (smoothed over the
// surface, so the change fades into the body). On the rest (as a pose layer: that rest change weighed in, src/deform.js).
//   taper     thinner towards the end (`amount` < 0: thicker): every section about its bone, by how far along the limb
//             it is — nothing at the root (the shoulder and the hip keep their form), the most at the wrist and the
//             ankle, back to nothing over the hand and the foot; arms and legs (`arms`, `legs`)
//   straight  straight against curved: one side of each bone flattened, the other swelling — the upper arm's top and
//             the thigh's front curved, the forearm's top and the shin's front straight; the section changes smoothly
//             round the bone (no crease where the sides meet) and fades to nothing at each joint
//   arc       the whole limb as one arc: the arms bowed up off their line, the legs outwards (`legs: "in"`: inwards)
// A point near a joint goes by both bones, by a smooth share across the joint — no step where one bone hands over to
// the next.
import { register } from '../deform.js';
import { clamp, sst } from '../math.js';
import { num, flag } from '../schema.js';

const win = t => t <= 0 || t >= 1 ? 0 : Math.sin(Math.PI * t);
const ACROSS = 0.16;   // how much of the limb's length the hand-over from one bone to the next takes

// the four chains at the rest: for each its joints, bones (root a, unit direction e, length l), the chain's direction
// and the mid joint's share of its length
function chains(R, which) {
  const sk = R.skeleton, J = R.rig.joints, at = j => [J[j * 3], J[j * 3 + 1], J[j * 3 + 2]], out = [];
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    if (which.arms) out.push({ limb: sg > 0 ? 1 : 2, arm: true, sign: sg, js: [s + 'Arm', s + 'ForeArm', s + 'Hand'] });
    if (which.legs) out.push({ limb: sg > 0 ? 3 : 4, arm: false, sign: sg, js: [s + 'Leg', s + 'Shin', s + 'Foot'] });
  }
  for (const c of out) {
    const [A, M, B] = c.js.map(n => at(sk.index[n]));
    const bone = (a, b) => { const e = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], l = Math.hypot(...e); return { a, e: e.map(v => v / l), l }; };
    c.A = A; c.bones = [bone(A, M), bone(M, B)];
    const ab = [B[0] - A[0], B[1] - A[1], B[2] - A[2]]; c.L = Math.hypot(...ab); c.d = ab.map(v => v / c.L);
    c.tm = ((M[0] - A[0]) * c.d[0] + (M[1] - A[1]) * c.d[1] + (M[2] - A[2]) * c.d[2]) / c.L;
    // straight's reference side (arm: up, leg: forward) across each bone; arc's direction (arm: up off the line, leg: out)
    const ref = c.arm ? [0, 1, 0] : [0, 0, 1];
    for (const b of c.bones) { const k = ref[0] * b.e[0] + ref[1] * b.e[1] + ref[2] * b.e[2], n = [ref[0] - k * b.e[0], ref[1] - k * b.e[1], ref[2] - k * b.e[2]], l = Math.hypot(...n); b.n = n.map(v => v / l); }
    if (c.arm) { const k = c.d[1], n = [-k * c.d[0], 1 - k * c.d[1], -k * c.d[2]], l = Math.hypot(...n); c.bow = n.map(v => v / l); } else c.bow = [c.sign, 0, 0];
  }
  return out;
}
// a field of the limbs: bone(c, b, k, st, ox, oy, oz, t) → the factor of the point's offset across bone k of chain c
// (st along that bone, ox… its offset from the bone's line, t along the whole chain), blended over the two bones;
// whole(c, t, isJ) → a move along the chain's own direction c.bow (times the limb's share)
function limbField(R, which, { across, whole }) {
  const cs = chains(R, which);
  return (x, y, z, w, isJ, out) => {
    out[0] = x; out[1] = y; out[2] = z;
    for (let n = 0; n < cs.length; n++) {
      const c = cs[n], k = w[c.limb]; if (k < 0.01) continue;
      const t = ((x - c.A[0]) * c.d[0] + (y - c.A[1]) * c.d[1] + (z - c.A[2]) * c.d[2]) / c.L;
      if (whole) { const m = whole(c, t, isJ) * k; out[0] += m * c.bow[0]; out[1] += m * c.bow[1]; out[2] += m * c.bow[2]; }
      if (!across || isJ) continue;
      const lower = sst((t - c.tm) / ACROSS + 0.5);
      for (let b = 0; b < 2; b++) {
        const share = b ? lower : 1 - lower; if (share <= 0) continue;
        const B = c.bones[b], rx = x - B.a[0], ry = y - B.a[1], rz = z - B.a[2], al = rx * B.e[0] + ry * B.e[1] + rz * B.e[2];
        const ox = rx - B.e[0] * al, oy = ry - B.e[1] * al, oz = rz - B.e[2] * al;
        const f = across(c, b, al / B.l, ox, oy, oz, t) * share * k;
        out[0] += ox * f; out[1] += oy * f; out[2] += oz * f;
      }
    }
  };
}

register({
  kind: 'taper', of: 'figure',
  params: { amount: num(-2, 2), arms: flag, legs: flag },
  defaults: { amount: 0.6, arms: true, legs: true },
  field(p, R) {
    const a = p.amount * p.strength;
    // the section's change along the limb: 0 at the root, −0.3·a at its end, back to 0 over the hand or the foot
    const f = t => -0.3 * a * (t <= 1 ? sst(t) : 1 - sst((t - 1) / 0.18));
    return limbField(R, p, { across: (c, b, st, ox, oy, oz, t) => f(t) });
  },
});

register({
  kind: 'straight', of: 'figure',
  params: { amount: num(-2, 2), arms: flag, legs: flag },
  defaults: { amount: 0.6, arms: true, legs: true },
  field(p, R) {
    const a = p.amount * p.strength;
    return limbField(R, p, { across: (c, b, st, ox, oy, oz) => {
      const B = c.bones[b], rho = Math.hypot(ox, oy, oz); if (rho < 1e-6) return 0;
      // x > 0: the flat side (the upper bone's away from the reference, the lower's towards it)
      const x = (b ? 1 : -1) * (ox * B.n[0] + oy * B.n[1] + oz * B.n[2]) / rho, s = clamp(st, 0, 1);
      return a * (-0.45 * Math.max(0, x) ** 2 * win(s) + 0.3 * Math.max(0, -x) ** 2 * Math.sin(Math.PI * Math.pow(s, 0.8)));
    } });
  },
});

register({
  kind: 'arc', of: 'figure',
  params: { amount: num(-2, 2), arms: flag, legs: { anyOf: [flag, { type: 'string', enum: ['out', 'in'] }] } },
  defaults: { amount: 0.5, arms: true, legs: 'out' },
  field(p, R) {
    const a = p.amount * p.strength, which = { arms: p.arms, legs: !!p.legs }, inward = p.legs === 'in';
    return limbField(R, which, { whole: (c, t) => { const tt = clamp(t, 0, 1); return (c.arm || !inward ? 1 : -1) * a * 0.22 * c.L * Math.sin(Math.PI * tt) * sst(tt / 0.35); } });
  },
});
