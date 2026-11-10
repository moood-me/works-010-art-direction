// A figure: a character's body moving through a clip — the whole way from Kimodo's data to the skin.
//   retarget (src/retarget.js) → corrections (named, on the pose) → Т7's collarbone share → placed where the
//   character stands → skinning (src/skin.js, with the seam fix) → set on the floor → normals.
import { makeRetarget, build } from './retarget.js';
import { Skinner, normalsOf, clavicleShare } from './skin.js';
import { newSample } from './motion.js';
import { getV } from './math.js';

export class Figure {
  constructor(body, spec, place) {
    this.body = body; this.spec = spec;
    this.retarget = makeRetarget(body, { place, corrections: spec.motion.corrections });
    this.skinner = new Skinner(body, spec.skinning);
    this.positions = new Float32Array(body.N * 3);
    this.normals = new Float32Array(body.N * 3);
    this.sample = newSample(body.skeleton.J);
    this.pose = null;
  }
  get place() { return this.retarget.place; }
  set place(p) { Object.assign(this.retarget.place, p); }

  // the figure at moment t (frames) of a clip; null: at rest, where it stands
  frame(clip, t) {
    const { body } = this, sk = body.skeleton;
    let pose;
    if (!clip) pose = this.restPose();
    else {
      pose = this.retarget.pose(clip.sample(t, this.sample));
      if (this.spec.skinning.clavicleShare > 0) { clavicleShare(pose, body, this.spec.skinning.clavicleShare); build(pose, body, getV(pose.P, sk.index.Hips)); }
      this.retarget.placed(pose);
    }
    this.skinner.skin(pose, this.positions);
    if (clip && this.spec.motion.floor === 'lowest') {
      let lo = Infinity; for (let i = 1; i < this.positions.length; i += 3) if (this.positions[i] < lo) lo = this.positions[i];
      const shift = pose.floor - lo;
      for (let i = 1; i < this.positions.length; i += 3) this.positions[i] += shift;
      for (let j = 0; j < sk.J; j++) pose.P[j * 3 + 1] += shift;
    }
    normalsOf(this.positions, body.triangles, this.normals);
    this.pose = pose;
    return this;
  }
  // the rest pose put where the character stands
  restPose() {
    const { body } = this, J = body.skeleton.J;
    const pose = { Q: new Float64Array(J * 4), P: Float64Array.from(body.joints), floor: body.measures.floor };
    for (let j = 0; j < J; j++) pose.Q[j * 4 + 3] = 1;
    // standing on the floor at the place: the rest's pelvis over the place's origin
    const H = body.skeleton.index.Hips;
    for (let j = 0; j < J; j++) { pose.P[j * 3] -= body.joints[H * 3]; pose.P[j * 3 + 2] -= body.joints[H * 3 + 2]; }
    return this.retarget.placed(pose);
  }
  // where the pelvis goes over a clip, on this figure (for drawing the path)
  path(clip, step = 1) {
    const out = [];
    for (let t = 0; t < clip.frames; t += step) { const p = this.retarget.placed(this.retarget.pose(clip.sample(t, this.sample))); out.push([p.P[0], p.P[2]]); }
    return out;
  }
}
