// A rig: what a motion is carried onto, apart from any mesh — the skeleton, each joint's rest place and rest frame,
// the floor at rest and the hip height. One rig moves every mesh of a character (the body, a wrapped head, pieces,
// clothes, sweeps rebuilt each frame) off one pose. A body from Anny makes its rig from its joints and its skin's
// lowest point (src/body.js); a character not from Anny gives its own (its bone lengths, its floor).
//   joints   Float64Array J×3 — each joint's place at rest (the designed rest: a deformer moves these)
//   frames   Float64Array J×4 — each joint's frame at rest (quaternions x y z w): the retargeting reference
//   floor    the lowest point at rest (metres, y): where the feet stand
//   hipHeight   the pelvis over the floor at rest — the rig's size against SOMA's, for the path and the height
export function makeRig({ skeleton, joints, frames, floor }) {
  const J = skeleton.J;
  if (joints.length !== J * 3 || frames.length !== J * 4) throw new Error(`a rig needs ${J} joints and frames`);
  if (!Number.isFinite(floor)) throw new Error('a rig needs its floor');
  const H = skeleton.index.Hips;
  const rig = {
    skeleton, J, joints: Float64Array.from(joints), frames: Float64Array.from(frames), floor,
    hipHeight: joints[H * 3 + 1] - floor,
  };
  if (!(rig.hipHeight > 0)) throw new Error(`a rig whose pelvis is not above its floor (${rig.hipHeight})`);
  rig.with = o => makeRig({ skeleton, joints: rig.joints, frames: rig.frames, floor: rig.floor, ...o });
  return rig;
}
