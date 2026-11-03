// One retargeting: a Kimodo clip's moment on a body.
//
// Kimodo gives each SOMA joint's rotation in the world (its frame's axes) and the pelvis's place. A body has its own
// joint frames at rest (body.frames) — the same joints with the same axes as SOMA's (Anny's SOMA rig), only standing
// differently (an A-pose, its own proportions). So each joint's frame is carried as Kimodo turned SOMA's:
//   Q_j = q_j · frame_jᵀ            the turn from the body's rest to now, in the world (what skinning applies)
//   P_j = P_parent + Q_parent (rest_j − rest_parent)     the body's own bones, of its own lengths
// The frames are the retargeting reference and the places are the designed rest: a deformer that moved joints (a line
// of action, limbs in arcs, other proportions) keeps its design in every motion, because nothing here measures the
// bones' rest directions. (gallery/player-core.js `turns()` turned each bone from its own rest direction to SOMA's,
// which undid such designs.)
//
// The body travels along Kimodo's own root path: the pelvis where Kimodo put it, scaled by how much higher this body's
// pelvis is than SOMA's (a shorter body takes shorter steps, the feet don't slide). Placement puts the whole motion
// anywhere: {position: [x, y, z] (y — the floor there), heading (radians about y; 0 — Kimodo's +z)}.
//
// Corrections on top (src/corrections.js) are named options, all off unless asked for.
import { qMul, qConj, qRot, qAxisAngle, getQ, setQ } from './math.js';
import { CORRECTIONS } from './corrections.js';

export function makeRetarget(body, options = {}) {
  const sk = body.skeleton, J = sk.J, H = sk.index.Hips;
  const somaHip = sk.rest[H * 3 + 1] - sk.floor;
  const st = {
    body, sk, J,
    k: body.measures.hipHeight / somaHip,                  // this body's size against SOMA's, for the path and the height
    place: { position: [0, 0, 0], heading: 0, ...(options.place || {}) },
    corrections: options.corrections || {},
  };
  for (const name of Object.keys(st.corrections)) if (!CORRECTIONS[name]) throw new Error(`no correction "${name}"`);
  const fc = Array.from({ length: J }, (_, j) => qConj(getQ(body.frames, j)));
  const pose = { Q: new Float64Array(J * 4), P: new Float64Array(J * 3), floor: 0, k: st.k };

  st.pose = (s) => {
    for (let j = 0; j < J; j++) setQ(pose.Q, j, qMul(getQ(s.q, j), fc[j]));
    // the pelvis on Kimodo's path, scaled
    const hip = [s.p[H * 3] * st.k, body.measures.floor + (s.p[H * 3 + 1] - sk.floor) * st.k, s.p[H * 3 + 2] * st.k];
    build(pose, body, hip);
    for (const [name, prm] of Object.entries(st.corrections)) if (prm && prm.on !== false) { CORRECTIONS[name](pose, body, prm); build(pose, body, hip); }
    // the lowest point SOMA's skin reached (lying, a little into the floor: never below it)
    pose.floor = body.measures.floor + Math.max(0, (s.lowest - sk.floor) * st.k);
    return pose;
  };
  // the pose put where the character stands: a turn about y and a move, the floor at position[1]
  st.placed = (pose) => {
    const { position: o, heading } = st.place, r = qAxisAngle([0, 1, 0], heading), y0 = body.measures.floor;
    for (let j = 0; j < J; j++) {
      setQ(pose.Q, j, qMul(r, getQ(pose.Q, j)));
      const v = qRot(r, [pose.P[j * 3], pose.P[j * 3 + 1] - y0, pose.P[j * 3 + 2]]);
      pose.P[j * 3] = v[0] + o[0]; pose.P[j * 3 + 1] = v[1] + o[1]; pose.P[j * 3 + 2] = v[2] + o[2];
    }
    pose.floor += o[1] - y0;
    return pose;
  };
  return st;
}

// the joints' places from the pelvis down the body's own bones
export function build(pose, body, hip) {
  const sk = body.skeleton, R = body.joints;
  for (let j = 0; j < sk.J; j++) {
    const p = sk.parent[j];
    if (p < 0) { pose.P[j * 3] = hip[0]; pose.P[j * 3 + 1] = hip[1]; pose.P[j * 3 + 2] = hip[2]; continue; }
    const v = qRot(getQ(pose.Q, p), [R[j * 3] - R[p * 3], R[j * 3 + 1] - R[p * 3 + 1], R[j * 3 + 2] - R[p * 3 + 2]]);
    pose.P[j * 3] = pose.P[p * 3] + v[0]; pose.P[j * 3 + 1] = pose.P[p * 3 + 1] + v[1]; pose.P[j * 3 + 2] = pose.P[p * 3 + 2] + v[2];
  }
}

// a joint's turn against its parent's (both from rest), and back
export const localOf = (pose, sk, j) => { const p = sk.parent[j]; return p < 0 ? getQ(pose.Q, j) : qMul(qConj(getQ(pose.Q, p)), getQ(pose.Q, j)); };
// set joint j's local turn, carrying everything under it along
export function setLocal(pose, sk, j, L) {
  const p = sk.parent[j], now = getQ(pose.Q, j), want = p < 0 ? L : qMul(getQ(pose.Q, p), L);
  turnUnder(pose, sk, j, qMul(want, qConj(now)));
}
// turn joint j and all under it by r (in the world)
export function turnUnder(pose, sk, j, r) { for (const k of sk.under(j)) setQ(pose.Q, k, qMul(r, getQ(pose.Q, k))); }
