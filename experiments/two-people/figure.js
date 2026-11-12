// A figure: a character's body moving through a clip. Copied from engine/src/figure.js and changed in one place:
// after the pose is placed in the scene and before it is skinned, `adjust(pose, t)` may change it — where this item
// puts its small corrections on top of Kimodo (a hand brought the last centimetres to its place) and where the
// carried person is attached to the carrier. Everything else is the engine's, imported as it is.
import { makeRetarget, build } from '../../engine/src/retarget.js';
import { Skinner, normalsOf, clavicleShare } from '../../engine/src/skin.js';
import { newSample } from '../../engine/src/motion.js';
import { getV } from '../../engine/src/math.js';

export class Figure {
  constructor(body, spec, place) {
    this.body = body; this.spec = spec;
    this.retarget = makeRetarget(body, { place, corrections: spec.motion.corrections });
    this.skinner = new Skinner(body, spec.skinning);
    this.positions = new Float32Array(body.N * 3);
    this.normals = new Float32Array(body.N * 3);
    this.sample = newSample(body.skeleton.J);
    this.pose = null;
    this.adjust = null;          // (pose, t) => void: changes the placed pose before skinning
    this.floorShift = true;      // set the lowest point on the floor (off for one carried: the carrier holds them)
  }
  get place() { return this.retarget.place; }
  set place(p) { Object.assign(this.retarget.place, p); }

  // the pose alone (no skin): placed, adjusted
  posed(clip, t) {
    const { body } = this, sk = body.skeleton;
    const pose = this.retarget.pose(clip.sample(t, this.sample));
    if (this.spec.skinning.clavicleShare > 0) { clavicleShare(pose, body, this.spec.skinning.clavicleShare); build(pose, body, getV(pose.P, sk.index.Hips)); }
    this.retarget.placed(pose);
    return pose;
  }
  frame(clip, t) {
    const { body } = this, sk = body.skeleton;
    const pose = this.posed(clip, t);
    // on the floor as the engine sets it (the lowest point as high as SOMA's skin's then), measured before any
    // adjustment, so a correction of a hand never lifts the body
    if (this.floorShift && this.spec.motion.floor === 'lowest') {
      this.skinner.skin(pose, this.positions);
      let lo = Infinity; for (let i = 1; i < this.positions.length; i += 3) if (this.positions[i] < lo) lo = this.positions[i];
      const shift = pose.floor - lo;
      for (let j = 0; j < sk.J; j++) pose.P[j * 3 + 1] += shift;
    }
    if (this.adjust) this.adjust(pose, t);
    this.skinner.skin(pose, this.positions);
    normalsOf(this.positions, body.triangles, this.normals);
    this.pose = pose;
    return this;
  }
}
