// A copy of К1's ContactFigure (experiments/contacts/contact-figure.js — the early engine's Figure,
// engine/src/figure.js, copied and changed), here for К2: each contact's reach also says the place it went to (a
// rail's place moves with the hand), and a foot can be set on the step under it (standOne, at the end). From К1: a
// small correction that brings a hand the last centimetres onto its place.
//
// Kimodo made the touch: the walk up, the lean, the turn of the elbow, the hand's own turn — it was given the place
// (tools/plan.py). What is left is what Kimodo can't know: our body's arms and shoulders are not SOMA's, so on our
// body the same turns put the palm a few centimetres off. So, after the motion is carried onto the body and set on the
// floor, each contact turns the upper arm and the forearm (two bones, the elbow bending in the plane Kimodo bent it
// in) so that the middle of the palm comes onto its place, keeps the hand's own turn in the world as Kimodo made it,
// and is weighed in and out over a few frames around the touch. The body, the path and the other joints stay
// Kimodo's.
//
//   const fig = new ContactFigure(body, spec, place);
//   fig.contacts = [{ side: 'Left', target: t => [x, y, z] | null, weight: t => 0…1, surface?: y, verts?: [hand's vertices] }];
//   with `surface` the palm's height is not the target's: the hand's lowest skin is put on the surface instead;
//   with `over` too ([[x0, z0], [x1, z1]] — the surface's extent), the hand is kept from going under it at any time;
//   with `outside` (positions, shift → a move or null), the hand is moved out of another body when it goes into it.
//   fig.frame(clip, t)  → fig.positions, fig.pose (P, Q), fig.reach (what each contact did: miss before, after)
import { makeRetarget, build, turnUnder } from '../../engine/src/retarget.js';
import { Skinner, normalsOf, clavicleShare } from '../../engine/src/skin.js';
import { newSample } from '../../engine/src/motion.js';
import { getV, getQ, setQ, qMul, qConj, qBetween, qAxisAngle, sub, add, scale, len, normalize, cross, dot, clamp } from '../../engine/src/math.js';

export class ContactFigure {
  constructor(body, spec, place) {
    this.body = body; this.spec = spec;
    this.retarget = makeRetarget(body, { place, corrections: spec.motion.corrections });
    this.skinner = new Skinner(body, spec.skinning);
    this.positions = new Float32Array(body.N * 3);
    this.normals = new Float32Array(body.N * 3);
    this.sample = newSample(body.skeleton.J);
    this.pose = null;
    this.contacts = [];
    this.correct = true;
    this.reach = [];
    this.feet = [];        // [{side, verts, top: (x, z) → the height of what is under that point}] — К2
    this.stand = [];
  }
  get place() { return this.retarget.place; }

  frame(clip, t) {
    const { body } = this, sk = body.skeleton;
    const pose = this.retarget.pose(clip.sample(t, this.sample));
    if (this.spec.skinning.clavicleShare > 0) { clavicleShare(pose, body, this.spec.skinning.clavicleShare); build(pose, body, getV(pose.P, sk.index.Hips)); }
    this.retarget.placed(pose);
    // set on the floor as the engine does (its lowest point as low as SOMA's skin's then), before the hands are placed
    this.skinner.skin(pose, this.positions);
    let shift = 0;
    if (this.spec.motion.floor === 'lowest') {
      let lo = Infinity; for (let i = 1; i < this.positions.length; i += 3) if (this.positions[i] < lo) lo = this.positions[i];
      shift = pose.floor - lo;
      for (let j = 0; j < sk.J; j++) pose.P[j * 3 + 1] += shift;
    }
    this.shift = shift;
    // a hand lying on something: how far under the palm's middle its skin reaches now (the hand keeps its turn through
    // the correction, so this holds after it): the palm's middle goes that much over the surface (or the skin) touched
    for (const c of this.contacts) {
      if (!c.verts) { c.under = 0; continue; }
      let lo = Infinity; for (const i of c.verts) lo = Math.min(lo, this.positions[i * 3 + 1] + shift);
      c.under = this.palm(pose, c.side)[1] - lo;
    }
    this.reach = this.contacts.map(c => this.reachOne(pose, c, t));
    this.stand = this.feet.map(f => this.standOne(pose, f));
    this.skinner.skin(pose, this.positions);
    normalsOf(this.positions, body.triangles, this.normals);
    this.pose = pose;
    return this;
  }

  // the middle of the palm: between the wrist and the knuckles of the index and the little finger
  palm(pose, side) {
    const i = this.body.skeleton.index, P = pose.P;
    const a = getV(P, i[side + 'Hand']), b = getV(P, i[side + 'HandIndex1']), c = getV(P, i[side + 'HandPinky1']);
    return [(a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3, (a[2] + b[2] + c[2]) / 3];
  }

  reachOne(pose, c, t) {
    let target = c.target(t, pose); const w = target ? clamp(c.weight(t), 0, 1) : 0;
    if (target && c.surface != null) target = [target[0], c.surface + c.under, target[2]];
    const palm0 = this.palm(pose, c.side);
    const before = target ? len(sub(palm0, target)) : null;
    // where the palm goes: towards its place as much as the contact is weighed in; and, coming down onto a surface
    // (c.over: its extent over the floor, [[x0, z0], [x1, z1]]), never lower than lying on it — Kimodo knows nothing of
    // the table, and on our body its hand can cut its edge on the way
    let goal = target && w > 0 ? add(palm0, scale(sub(target, palm0), w)) : palm0.slice();
    let lifted = false;
    if (c.over && c.surface != null) {
      const [[x0, z0], [x1, z1]] = c.over, m = 0.04;
      if (goal[0] > x0 - m && goal[0] < x1 + m && goal[2] > z0 - m && goal[2] < z1 + m && goal[1] < c.surface + c.under) { goal[1] = c.surface + c.under; lifted = true; }
    }
    // and never into another body (c.outside: how far, and which way, the hand's skin has to go to be out of it)
    // — tested where the hand will be: the hand keeps its turn, so its skin moves as its palm does (twice: the first
    // move can bring another part of the hand into the skin)
    if (c.outside) for (let k = 0; k < 2; k++) {
      const d = c.outside(this.positions, this.shift, sub(goal, palm0));
      if (!d) break;
      goal = add(goal, d); lifted = true;
    }
    if (!this.correct || (!lifted && (!target || w <= 0))) return { side: c.side, w, before, after: before, target };
    const sk = this.body.skeleton, i = sk.index, S = i[c.side + 'Arm'], E = i[c.side + 'ForeArm'], H = i[c.side + 'Hand'];
    const hip = getV(pose.P, i.Hips);
    const handTurn = getQ(pose.Q, H);
    const want = add(getV(pose.P, H), sub(goal, palm0));
    const s = getV(pose.P, S), e = getV(pose.P, E), h = getV(pose.P, H);
    const a = len(sub(e, s)), b = len(sub(h, e)), d = clamp(len(sub(want, s)), Math.abs(a - b) + 1e-4, a + b - 1e-4);
    // 1) the elbow: bend so the shoulder–wrist distance is d, about the axis it bends on now
    let n = cross(sub(e, s), sub(h, e));
    if (len(n) < 1e-6) n = cross(sub(e, s), [0, 1, 0]);
    n = normalize(n);
    const cosNow = clamp(dot(normalize(sub(s, e)), normalize(sub(h, e))), -1, 1), cosWant = clamp((a * a + b * b - d * d) / (2 * a * b), -1, 1);
    const dAng = Math.acos(cosWant) - Math.acos(cosNow);           // opening the elbow by dAng
    turnUnder(pose, sk, E, qAxisAngle(n, -dAng));
    build(pose, this.body, hip);
    if (Math.abs(len(sub(getV(pose.P, H), s)) - d) > 1e-3) { turnUnder(pose, sk, E, qAxisAngle(n, 2 * dAng)); build(pose, this.body, hip); }
    // 2) the whole arm from the shoulder: the smallest turn that points the wrist at its place
    const h2 = getV(pose.P, H), s2 = getV(pose.P, S);
    turnUnder(pose, sk, S, qBetween(normalize(sub(h2, s2)), normalize(sub(want, s2))));
    // 3) the hand keeps the turn Kimodo gave it (a flat palm stays flat on the table)
    turnUnder(pose, sk, H, qMul(handTurn, qConj(getQ(pose.Q, H))));
    build(pose, this.body, hip);
    return { side: c.side, w, before, after: target ? len(sub(this.palm(pose, c.side), target)) : null, target };
  }

  // К2: a foot on a step. Kimodo was given each foot's place on its step; on our body (other legs, other feet, and the
  // body set on the floor by its lowest point as a whole) a foot standing on a step can be a few centimetres in it or
  // over it. So: how far the foot's skin is in what is under it (the deepest of its points) or over it (the nearest);
  // in it — the foot is lifted out by that much; over it by less than 5 cm — it is let down onto it, the less the
  // farther (a foot in the air, taking a step, is left as Kimodo made it). The leg's two bones turn (the knee bending
  // in the plane it bends in), the foot keeps the turn Kimodo gave it.
  standOne(pose, f) {
    const pos = this.positions, sh = this.shift, sk0 = this.body.skeleton.index;
    // the step it stands on is the one under its ankle; its sole (lowest skin) against that step's top. (Toes reaching
    // over the next step's front are not lifted for: that is the foot's length, not its height — measured apart.)
    const ankle = getV(pose.P, sk0[f.side + 'Foot']), top = f.top(ankle[0], ankle[2]);
    let lo = Infinity; for (const i of f.verts) lo = Math.min(lo, pos[i * 3 + 1] + sh);
    const deep = top - lo, sole = lo - top;
    const gap = deep > 0 ? -deep : sole, near = 0.05;
    const s = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);
    const dy = gap < 0 ? -gap : gap < near ? -gap * (1 - s(gap / near)) : 0;
    if (!this.correct || Math.abs(dy) < 1e-4) return { side: f.side, before: gap, after: gap };
    const sk = this.body.skeleton, i = sk.index, S = i[f.side + 'Leg'], E = i[f.side + 'Shin'], H = i[f.side + 'Foot'];
    const hip = getV(pose.P, i.Hips), footTurn = getQ(pose.Q, H);
    const want = add(getV(pose.P, H), [0, dy, 0]);
    const p = getV(pose.P, S), e = getV(pose.P, E), h = getV(pose.P, H);
    const a = len(sub(e, p)), b = len(sub(h, e)), d = clamp(len(sub(want, p)), Math.abs(a - b) + 1e-4, a + b - 1e-4);
    let n = cross(sub(e, p), sub(h, e)); if (len(n) < 1e-6) n = cross(sub(e, p), [1, 0, 0]); n = normalize(n);
    const cosNow = clamp(dot(normalize(sub(p, e)), normalize(sub(h, e))), -1, 1), cosWant = clamp((a * a + b * b - d * d) / (2 * a * b), -1, 1);
    const dAng = Math.acos(cosWant) - Math.acos(cosNow);
    turnUnder(pose, sk, E, qAxisAngle(n, -dAng)); build(pose, this.body, hip);
    if (Math.abs(len(sub(getV(pose.P, H), p)) - d) > 1e-3) { turnUnder(pose, sk, E, qAxisAngle(n, 2 * dAng)); build(pose, this.body, hip); }
    const h2 = getV(pose.P, H), p2 = getV(pose.P, S);
    turnUnder(pose, sk, S, qBetween(normalize(sub(h2, p2)), normalize(sub(want, p2))));
    turnUnder(pose, sk, H, qMul(footTurn, qConj(getQ(pose.Q, H))));
    build(pose, this.body, hip);
    return { side: f.side, before: gap, after: gap + dy, moved: dy };
  }
}
