// One retargeting: a Kimodo clip's moment on a rig (src/rig.js) — nothing here looks at a mesh.
//
// Kimodo gives each SOMA joint's rotation in the world (its frame's axes) and the pelvis's place. A rig has its own
// joint frames at rest — the same joints with the same axes as SOMA's (Anny's SOMA rig), only standing differently
// (an A-pose, its own proportions). So each joint's frame is carried as Kimodo turned SOMA's:
//   Q_j = q_j · frame_jᵀ            the turn from the rig's rest to now, in the world (what skinning applies)
//   P_j = P_parent + Q_parent (rest_j − rest_parent)     the rig's own bones, of its own lengths
// The frames are the retargeting reference and the places are the designed rest: a deformer that moved joints (a line
// of action, limbs in arcs, other proportions) keeps its design in every motion, because nothing here measures the
// bones' rest directions.
//
// The rig travels along Kimodo's own root path: the pelvis where Kimodo put it, scaled by how much higher this rig's
// pelvis is than SOMA's (k: a shorter body takes shorter steps, the feet don't slide). `floor` is then how high the
// lowest point should be: as high as SOMA's skin's lowest at that moment, scaled (never below the floor). The rest
// this is measured on is the rig's, or the one the pose layers that change the rest make this frame (`root`): a layer
// of a longer-legged form stands on its longer legs and takes longer steps, as the same change on the rest does.
// Placement (`place`) puts the whole motion anywhere: {position: [x, y, z] (y — the floor there), heading (radians
// about y; 0 — Kimodo's +z)}.
import { qMul, qAxisAngle } from './math.js';
import { build } from './pose.js';

export function makeRetarget(rig) {
  const sk = rig.skeleton, J = sk.J, H = sk.index.Hips;
  const soma = sk.rest[H * 3 + 1] - sk.floor, k = rig.hipHeight / soma;
  const fc = new Float64Array(J * 4);
  for (let j = 0; j < J; j++) { fc[j * 4] = -rig.frames[j * 4]; fc[j * 4 + 1] = -rig.frames[j * 4 + 1]; fc[j * 4 + 2] = -rig.frames[j * 4 + 2]; fc[j * 4 + 3] = rig.frames[j * 4 + 3]; }
  const a = [0, 0, 0, 0], b = [0, 0, 0, 0], o = [0, 0, 0, 0], hip = [0, 0, 0];
  return {
    rig, k,
    // the sample's moment on the rig, into pose
    pose(s, pose) {
      for (let j = 0; j < J; j++) {
        for (let c = 0; c < 4; c++) { a[c] = s.q[j * 4 + c]; b[c] = fc[j * 4 + c]; }
        qMul(a, b, o); pose.Q[j * 4] = o[0]; pose.Q[j * 4 + 1] = o[1]; pose.Q[j * 4 + 2] = o[2]; pose.Q[j * 4 + 3] = o[3];
      }
      this.root(s, pose, rig.joints);
      return pose;
    },
    // the pelvis on Kimodo's path and the floor, scaled by the hip height of `rest` (the rest places this frame),
    // and the places built down its bones
    root(s, pose, rest) {
      const kk = (rest[H * 3 + 1] - rig.floor) / soma;
      hip[0] = s.p[H * 3] * kk; hip[1] = rig.floor + (s.p[H * 3 + 1] - sk.floor) * kk; hip[2] = s.p[H * 3 + 2] * kk;
      build(pose, rig, hip, rest);
      pose.floor = rig.floor + Math.max(0, (s.lowest - sk.floor) * kk);
      pose.shift = 0;
      return hip;
    },
  };
}

// the pose put where the character stands: a turn about y and a move, the floor at position[1]
export function place(pose, rig, { position: p = [0, 0, 0], heading = 0 } = {}) {
  const r = qAxisAngle([0, 1, 0], heading), y0 = rig.floor, J = rig.J, q = [0, 0, 0, 0], o = [0, 0, 0, 0];
  const c = Math.cos(heading), s = Math.sin(heading);
  for (let j = 0; j < J; j++) {
    for (let k = 0; k < 4; k++) q[k] = pose.Q[j * 4 + k];
    qMul(r, q, o); for (let k = 0; k < 4; k++) pose.Q[j * 4 + k] = o[k];
    const x = pose.P[j * 3], y = pose.P[j * 3 + 1] - y0, z = pose.P[j * 3 + 2];
    pose.P[j * 3] = c * x + s * z + p[0]; pose.P[j * 3 + 1] = y + p[1]; pose.P[j * 3 + 2] = -s * x + c * z + p[2];
  }
  pose.floor += p[1] - y0;
  return pose;
}
