// A scene of two people: each plays a chain of Kimodo's motions (made in the order of cause and effect: what one did
// became the other's constraint), placed in one space; on top, the small corrections (contacts) and the attachment
// of one carried. Runs in a browser and in node alike (no three.js here): the page draws it, tools/measure.mjs
// measures it.
//
// A scene (scenes.js):
//   {id, label, frames, people: [{id, character, chain: [motion ids], start: scene frame its chain begins at,
//      place: {position: [x, 0, z], heading}}],
//    contacts: [{who, side: 'Right'|'Left', on, joint, point: [x, y, z] in that joint's frame at rest (the body's
//      own), from, to, ramp}] — who's palm comes onto a point that rides on `on`'s joint, from..to (scene frames),
//      the correction faded in and out over `ramp` frames,
//    carry?: {who, by, ...} — see attach()}
import { loadMotion, clipOf } from '../../engine/src/motion.js';
import { resolve } from '../../engine/src/character.js';
import { build, turnUnder } from '../../engine/src/retarget.js';
import { qMul, qConj, qNorm, qRot, qAxisAngle, qBetween, getQ, setQ, getV, sub, add, scale, len, normalize, cross, dot, clamp } from '../../engine/src/math.js';
import { Figure } from './figure.js';

const motions = new Map();
export async function loadClip(E, base, ids, read) {
  const ms = await Promise.all(ids.map(id => {
    if (!motions.has(id)) motions.set(id, loadMotion(new URL(`motions/${id}.json`, base), E.skeleton, read));
    return motions.get(id);
  }));
  return clipOf(ms);
}

// a joint's transform now: x (the body's rest space) ↦ Q (x − rest_j) + P_j
export const jointAt = (pose, body, j, x) => add(qRot(getQ(pose.Q, j), sub(x, getV(body.joints, j))), getV(pose.P, j));
// the palm's middle, a little in front of the hand's bones, in the body's rest (where the palm touches)
export function palmRest(body, side) {
  const sk = body.skeleton, h = getV(body.joints, sk.index[side + 'Hand']), m = getV(body.joints, sk.index[side + 'HandMiddle1']);
  const i = getV(body.joints, sk.index[side + 'HandIndex1']), r = getV(body.joints, sk.index[side + 'HandRing1']);
  const c = scale(add(h, m), 0.5);
  // the palm's side: across the hand (index → ring) × along it (wrist → middle); at rest (A-pose, palms in) that faces
  // the body's side for the left hand… checked on the body by palmNormal
  let n = normalize(cross(sub(r, i), sub(m, h)));
  if (side === 'Right') n = scale(n, -1);
  return { point: add(c, scale(n, 0.015)), normal: n };
}

// the arm (shoulder ball, elbow hinge) turned by the least to bring a point on the hand to `target`; the rest of the
// pose rebuilt down the bones. The elbow keeps the plane Kimodo bent it in.
export function reachTo(pose, body, side, handPoint, target) {
  const sk = body.skeleton, a = sk.index[side + 'Arm'], b = sk.index[side + 'ForeArm'], c = sk.index[side + 'Hand'];
  const hip = getV(pose.P, sk.index.Hips);
  const A = getV(pose.P, a), B = getV(pose.P, b), C = jointAt(pose, body, c, handPoint);
  const la = len(sub(B, A)), lb = len(sub(C, B));
  const d = Math.min(len(sub(target, A)), la + lb - 1e-4), cur = len(sub(C, A));
  const inner = x => Math.acos(clamp((la * la + lb * lb - x * x) / (2 * la * lb), -1, 1));
  let n = cross(sub(B, A), sub(C, B));
  if (len(n) > 1e-9) {
    n = normalize(n);
    turnUnder(pose, sk, b, qAxisAngle(n, inner(cur) - inner(d)));   // about u×v: bends further
    build(pose, body, hip);
  }
  const C2 = jointAt(pose, body, c, handPoint);
  turnUnder(pose, sk, a, qBetween(normalize(sub(C2, A)), normalize(sub(target, A))));
  build(pose, body, hip);
}

export async function loadScene(E, base, def, read) {
  const people = [];
  for (const p of def.people) {
    const spec = typeof p.character === 'string' ? await E.character(p.character) : resolve(p.character);
    const body = await E.body(spec.body);
    const fig = new Figure(body, spec, p.place);
    const clip = await loadClip(E, base, p.chain, read);
    people.push({ ...p, spec, body, fig, clip });
  }
  const by = Object.fromEntries(people.map(p => [p.id, p]));
  const S = { def, people, by, frames: def.frames, corrections: true, misses: {} };
  // contacts: the correction on top, faded in and out; what Kimodo alone missed by is kept (S.misses)
  for (const c of def.contacts || []) {
    const P = by[c.who], O = by[c.on], palm = palmRest(P.body, c.side), j = O.body.skeleton.index[c.joint];
    // the turn about the vertical: the other's joint's heading, and the hand's (wrist → middle finger) when the touch
    // began, as Kimodo made them
    const h = P.body.skeleton.index[c.side + 'Hand'], m = P.body.skeleton.index[c.side + 'HandMiddle1'];
    const handYaw = pose => { const d = sub(getV(pose.P, m), getV(pose.P, h)); return Math.atan2(d[0], d[2]); };
    let yaw0 = 0, hand0 = 0;
    if (c.turnWith) { yaw0 = yawAt(O, j, c.from); P.fig.frame(P.clip, clamp(c.from - P.start, 0, P.clip.frames - 1)); hand0 = handYaw(P.fig.pose); }
    const prev = P.fig.adjust;
    P.fig.adjust = (pose, t) => {
      prev?.(pose, t);
      const T = t + P.start;
      const w = Math.min(clamp((T - c.from + c.ramp) / c.ramp, 0, 1), clamp((c.to + c.ramp - T) / c.ramp, 0, 1));
      if (w <= 0 || !O.fig.pose) return;
      const target = jointAt(O.fig.pose, O.body, j, c.point);
      const now = jointAt(pose, P.body, P.body.skeleton.index[c.side + 'Hand'], palm.point);
      if (T >= c.from && T <= c.to) S.misses[`${P.name || c.who}, ${c.side === 'Right' ? 'правая' : 'левая'} рука`] = len(sub(now, target));
      if (!S.corrections) return;
      // the hand turned about the vertical by a share of how far the other's joint turned since the touch began (a
      // hand resting on a shoulder that turns under it goes partly round with it, partly slides)
      if (c.turnWith) {
        const want = hand0 + c.turnWith * angle(yawOf(getQ(O.fig.pose.Q, j)) - yaw0);
        turnUnder(pose, P.body.skeleton, h, qAxisAngle([0, 1, 0], w * angle(want - handYaw(pose))));
        build(pose, P.body, getV(pose.P, P.body.skeleton.index.Hips));
      }
      const now2 = jointAt(pose, P.body, h, palm.point);
      reachTo(pose, P.body, c.side, palm.point, add(now2, scale(sub(target, now2), w)));
    };
  }
  // looks: who's head turned towards another's head, a share of the way, spread over the neck and the head, at most
  // `max` radians, faded in and out — where Kimodo, asked to look, tilts the head back (a correction on top, off with
  // the others)
  for (const l of def.looks || []) {
    const P = by[l.who], O = by[l.at], sk = P.body.skeleton, prev = P.fig.adjust;
    P.fig.adjust = (pose, t) => {
      prev?.(pose, t);
      const T = t + P.start, w = Math.min(clamp((T - l.from + l.ramp) / l.ramp, 0, 1), clamp((l.to + l.ramp - T) / l.ramp, 0, 1));
      if (!S.corrections || w <= 0 || !O.fig.pose) return;
      const eyes = scale(add(getV(pose.P, sk.index.LeftEye), getV(pose.P, sk.index.RightEye)), 0.5);
      const face = normalize(qRot(getQ(pose.Q, sk.index.Head), [0, 0, 1]));
      const want = normalize(sub(getV(O.fig.pose.P, O.body.skeleton.index.Head), eyes));
      let r = qBetween(face, want); const a = 2 * Math.acos(clamp(r[3], -1, 1));
      const k = w * Math.min(l.share, l.max / Math.max(a, 1e-6));
      const hip = getV(pose.P, sk.index.Hips);
      for (const [n, part] of [['Neck1', 0.3], ['Neck2', 0.3], ['Head', 0.4]]) {
        const ax = normalize([r[0], r[1], r[2]]);
        turnUnder(pose, sk, sk.index[n], qAxisAngle(ax, a * k * part));
      }
      build(pose, P.body, hip);
      S.looked = { who: l.who, degrees: a * 180 / Math.PI, turned: a * k * 180 / Math.PI };
    };
  }
  if (def.carry) attach(S, def.carry);
  // everyone at scene frame T (in the order given: who another depends on comes first)
  S.at = T => {
    for (const p of people) p.fig.frame(p.clip, clamp(T - p.start, 0, p.clip.frames - 1));
    return S;
  };
  return S;
}

// the carried person: their pose is Kimodo's (a motion of their own), their place in the world the carrier's hands.
// carry: {who, by, from, to?} — from scene frame `from` (the hands have come to them) the carried one's whole pose is
// moved rigidly as the carrier's hands moved since then: the hands' frame (between the palms; turned as the line
// across them turns about the vertical, kept upright) now against the same at `from`; after `to` (put down) it stays where it was then. The hands'
// frame is taken from the carrier's pose as Kimodo made it (before the corrections), so the corrections that bring
// the palms onto the carried one's sides can follow the carried one without a loop.
export function attach(S, carry) {
  const W = S.by[carry.who], C = S.by[carry.by];
  const hands = pose => {
    const b = C.body, sk = b.skeleton, l = jointAt(pose, b, sk.index.LeftHand, palmRest(b, 'Left').point), r = jointAt(pose, b, sk.index.RightHand, palmRest(b, 'Right').point);
    // upright: one held under the arms hangs plumb whatever the carrier's back does
    const x = normalize([l[0] - r[0], 0, l[2] - r[2]]), y = [0, 1, 0], z = cross(x, y);
    return { o: scale(add(l, r), 0.5), q: quatOfAxes(x, y, z) };
  };
  const rawAt = T => hands(C.fig.posed(C.clip, clamp(T - C.start, 0, C.clip.frames - 1)));
  const F0 = rawAt(carry.from), Fend = carry.to != null ? rawAt(carry.to) : null;
  S.carryFrame = T => (T < carry.from ? null : carry.to != null && T > carry.to ? Fend : rawAt(T));
  const prev = W.fig.adjust;
  // moved first, then the carried one's own contacts (its hands on the carrier): the carrier's pose they reach for is
  // the one rawAt just made (Kimodo's, its trunk untouched by the corrections of its arms)
  W.fig.adjust = (pose, t) => {
    const F = S.carryFrame(t + W.start);
    if (F) moveRigid(pose, W.body.skeleton.J, qMul(F.q, qConj(F0.q)), F0.o, sub(F.o, F0.o));
    prev?.(pose, t);
  };
}
// a rotation from its axes (columns x, y, z)
export function quatOfAxes(x, y, z) {
  const m00 = x[0], m11 = y[1], m22 = z[2], tr = m00 + m11 + m22;
  let q;
  if (tr > 0) { const s = Math.sqrt(tr + 1) * 2; q = [(y[2] - z[1]) / s, (z[0] - x[2]) / s, (x[1] - y[0]) / s, s / 4]; }
  else if (m00 > m11 && m00 > m22) { const s = Math.sqrt(1 + m00 - m11 - m22) * 2; q = [s / 4, (y[0] + x[1]) / s, (z[0] + x[2]) / s, (y[2] - z[1]) / s]; }
  else if (m11 > m22) { const s = Math.sqrt(1 + m11 - m00 - m22) * 2; q = [(y[0] + x[1]) / s, s / 4, (z[1] + y[2]) / s, (z[0] - x[2]) / s]; }
  else { const s = Math.sqrt(1 + m22 - m00 - m11) * 2; q = [(z[0] + x[2]) / s, (z[1] + y[2]) / s, s / 4, (x[1] - y[0]) / s]; }
  return qNorm(q);
}
// a joint's heading: where its forward (+z at rest) axis points over the floor
const angle = a => Math.atan2(Math.sin(a), Math.cos(a));
const yawOf = q => { const d = qRot(q, [0, 0, 1]); return Math.atan2(d[0], d[2]); };
// the joint's heading at scene frame T (evaluated once, when the scene is loaded)
function yawAt(O, j, T) { O.fig.frame(O.clip, Math.max(0, Math.min(O.clip.frames - 1, T - O.start))); return yawOf(getQ(O.fig.pose.Q, j)); }
// a whole pose moved rigidly: turned by r about the point o, then moved by d
export function moveRigid(pose, J, r, o, d) {
  for (let j = 0; j < J; j++) {
    setQ(pose.Q, j, qMul(r, getQ(pose.Q, j)));
    const v = add(add(qRot(r, sub(getV(pose.P, j), o)), o), d);
    pose.P[j * 3] = v[0]; pose.P[j * 3 + 1] = v[1]; pose.P[j * 3 + 2] = v[2];
  }
}
export { qMul, qConj, qRot, qBetween, getQ, getV, sub, add, scale, len, normalize, cross, dot, clamp };
