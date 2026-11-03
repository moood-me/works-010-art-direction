// Т5's changes of the limbs (experiments/lines, `deform`: limbOp) — the arms from the shoulder to the wrist, the legs
// from the hip to the ankle, each as one chain; every point by its share of that limb (smoothed over the surface, so
// the change fades into the body). Their directions are the limb's own (turned with it when it moves as a pose layer).
//   taper     thick at the root, thin at the end (`amount` < 0: the reverse); arms and legs (`arms`, `legs`)
//   straight  straight against curved: one side of each limb flat as a ruler, the other swelling — the forearm's top
//             and the shin's front straight, the upper arm's top and the thigh's front curved
//   arc       the whole limb as one arc: the arms bowed up off their line, the legs outwards (`legs: "in"`: inwards)
import { register } from '../deform.js';
import { clamp, sst } from '../regions.js';
import { qRot } from '../math.js';

const num = (min, max) => ({ type: 'number', min, max }), bool = { type: 'boolean' };
const win = t => t <= 0 || t >= 1 ? 0 : Math.sin(Math.PI * t);

// the four chains, with what a field needs of each now: its joints' places, length, direction, the mid joint's share
function chains(R, S, which) {
  const sk = R.skeleton, out = [], J = S.J, v = j => [J[j * 3], J[j * 3 + 1], J[j * 3 + 2]];
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    if (which.arms) out.push({ limb: sg > 0 ? 1 : 2, arm: true, sign: sg, a: sk.index[s + 'Arm'], m: sk.index[s + 'ForeArm'], b: sk.index[s + 'Hand'] });
    if (which.legs) out.push({ limb: sg > 0 ? 3 : 4, arm: false, sign: sg, a: sk.index[s + 'Leg'], m: sk.index[s + 'Shin'], b: sk.index[s + 'Foot'] });
  }
  for (const c of out) {
    c.A = v(c.a); c.M = v(c.m); c.B = v(c.b);
    const ab = sub(c.B, c.A); c.L = len(ab); c.d = scale(ab, 1 / c.L);
    c.tm = dot(sub(c.M, c.A), c.d) / c.L;
    // the limb's own directions now: straight-side reference (arm: up, leg: forward), out to its side, both as at rest
    // turned by the limb's root
    const q = S.turn(c.a);
    c.ref = qRot(q, c.arm ? [0, 1, 0] : [0, 0, 1]); c.out = qRot(q, [c.sign, 0, 0]); c.up = qRot(q, [0, 1, 0]);
  }
  return out;
}
// where a point lies on a chain: t along it all, and on its own bone (s 0 upper, 1 lower): st along, off across
function onChain(c, p) {
  const t = dot(sub(p, c.A), c.d) / c.L, s = t < c.tm ? 0 : 1, a = s ? c.M : c.A, b = s ? c.B : c.M;
  const bd = sub(b, a), bl = len(bd), e = scale(bd, 1 / bl), rel = sub(p, a), st = dot(rel, e) / bl;
  return { t, s, st, off: sub(rel, scale(e, st * bl)), e };
}
function limbField(R, S, which, f) {
  const cs = chains(R, S, which);
  return (x, y, z, w, isJ, out) => {
    out[0] = x; out[1] = y; out[2] = z;
    for (const c of cs) {
      const k = w[c.limb]; if (k < 0.01) continue;
      const p = [x, y, z], d = f(c, p, onChain(c, p), isJ); if (!d) continue;
      out[0] += k * d[0]; out[1] += k * d[1]; out[2] += k * d[2];
    }
  };
}

register({
  kind: 'taper', of: 'figure',
  params: { amount: num(-2, 2), arms: bool, legs: bool },
  defaults: { amount: 0.6, arms: true, legs: true },
  field(p, R, S) {
    const a = p.amount * p.strength;
    return limbField(R, S, p, (c, pt, g, isJ) => isJ ? null
      : scale(g.off, -a * 0.6 * sst(clamp((g.t - 0.1) / 0.9, 0, 1)) + a * 0.08 * Math.sin(Math.PI * clamp(g.t / 0.4, 0, 1)) * sst(clamp(g.t / 0.15, 0, 1))));
  },
});

register({
  kind: 'straight', of: 'figure',
  params: { amount: num(-2, 2), arms: bool, legs: bool },
  defaults: { amount: 0.6, arms: true, legs: true },
  field(p, R, S) {
    const a = p.amount * p.strength;
    return limbField(R, S, p, (c, pt, g, isJ) => {
      if (isJ) return null;
      const n = normalize(sub(c.ref, scale(g.e, dot(c.ref, g.e)))), rn = dot(g.off, n), side = rn * (g.s ? 1 : -1);
      if (side > 0) return scale(n, -rn * a * 0.75 * win(clamp(g.st, 0, 1)) * Math.min(1, side / 0.03));
      return scale(n, rn * a * 0.4 * Math.sin(Math.PI * Math.pow(clamp(g.st, 0, 1), 0.8)));
    });
  },
});

register({
  kind: 'arc', of: 'figure',
  params: { amount: num(-2, 2), arms: bool, legs: { anyOf: [bool, { type: 'string', enum: ['out', 'in'] }] } },
  defaults: { amount: 0.5, arms: true, legs: 'out' },
  field(p, R, S) {
    const a = p.amount * p.strength, which = { arms: p.arms, legs: !!p.legs }, inward = p.legs === 'in';
    return limbField(R, S, which, (c, pt, g) => {
      const tt = clamp(g.t, 0, 1);
      const dir = c.arm ? normalize(sub(c.up, scale(c.d, dot(c.up, c.d)))) : scale(c.out, inward ? -1 : 1);
      return scale(dir, a * 0.22 * c.L * Math.sin(Math.PI * tt) * sst(clamp(tt / 0.35, 0, 1)));
    });
  },
});

const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const scale = (a, k) => [a[0] * k, a[1] * k, a[2] * k], len = a => Math.hypot(a[0], a[1], a[2]);
const normalize = a => scale(a, 1 / (len(a) || 1));
