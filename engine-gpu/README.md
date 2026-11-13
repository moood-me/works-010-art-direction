# engine-gpu — the early engine's skinning on the video card

Beside `engine/`, not in its place: `engine/` is as it was, and the pages that stand on it are as they were. This
folder takes the engine's own body, skeleton, motions and `Skinner` and moves the per-vertex work — skinning and
normals — into the vertex shader, so each frame the processor works out only the 77 joints.

```
src/gpuskin.js    GpuSkin: the attributes, the joint texture, the shader's skinVertex(), a few vertices on the processor
bench/            several characters in one scene, the old way and the new: frames a second, the longest gap
check/compare.mjs a page as it was against its fast variant: pictures, their difference, milliseconds a frame
```

## Why

A Р page does this every frame for every vertex, in JavaScript: skinning (`engine/src/skin.js`), the lowest point (to
stand on the floor), normals from the posed triangles (`normalsOf`), and then sends all positions and normals to the
video card. For a character of 38 thousand vertices that is about 5 ms of the processor and as much again to send and
draw (measured on a laptop with an Intel Arc 140T, 1920×1080 — the numbers are in `docs/history/`). One character fits
into a frame; two do not.

## How to use it

```js
import { GpuSkin } from '<root>/engine-gpu/src/gpuskin.js';
const fig = new Figure(body, spec, place);              // the engine's, as before: retargeting and the Skinner
const gs = new GpuSkin(THREE, fig.skinner);
const g = gs.attributes(new THREE.BufferGeometry());    // position and normal are the rest's now; + skinJ skinW skinC skinD
// every material that draws the skin (the body, the outline's hull, the shadow map's depth):
//   uniforms: { ...gs.uniforms, … }
//   vertexShader: `${gs.glsl} … void main() { vec3 P, N; skinVertex(position, normal, P, N); … use P and N … }`
// each frame:
const pose = fig.retarget.pose(clip.sample(t, fig.sample)); fig.retarget.placed(pose);
const shift = pose.floor - gs.lowest(pose);             // on the floor, as motion.floor 'lowest'
for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
gs.setPose(pose);
```

`to3d/r45-s15-anya/tools/web/anya-gpu.js` (page `fast.html`) is a whole page made so, beside its `anya.js`.

## What is the same and what is not

- **Positions: the same.** The shader does what `Skinner.skin` does, for `cor`, `dqs` and `lbs`: the same blend of
  the joints' turns, the same centres of rotation (the Skinner's own, sent as an attribute).
- **Normals: nearly.** They are the rest's normals turned with the vertex's blended joint turn, not recomputed from
  the posed triangles. Inside a deep bend (an elbow, a knee, a sitting hip) the light's edge can lie a little
  differently. Look at it; where a page draws designed normals of its own (a head's), nothing changes.
- **The floor: nearly.** `lowest(pose)` skins a probe and takes its lowest point: for each joint, the vertices it
  leads that lie furthest out in 200 directions; and where joints share the skin (bends, a skirt between the legs),
  one vertex of every 1.5 cm of space. On Р45 that is 5.5 of 38 thousand vertices, and against all vertices it is
  within 1.5 mm at worst over walk, sit, dance, lie, roll, jump and bow (0.05 mm on average; lying 0.35).
- **What a page does to the posed skin on the processor** (a skirt pushed off the legs, a seam smoothed) stays on
  the processor, for those vertices only: `gs.subset(indices).skin(pose, out)` gives their places (the same numbers
  as the engine's), the page works out an offset, writes it into `gs.skinD` and calls `gs.displace(first, count)`;
  the shader adds it after skinning. Such vertices keep the normals of the unpushed skin.
- **`Skinner`'s `seam` option** (Т7's smoothing where trunk meets arm) is not carried: no Р page asks for it. A page
  that does takes it as the skirt above.
- **Pages that read every vertex's place on the processor** (section К measures skin against a table or another
  body) stay on `engine/`; for a few vertices `subset` is enough.

## The check

`node engine-gpu/check/compare.mjs jobs.json out/` opens the old page and the fast one in real Chrome (not the
software renderer: the question is the video card), sets both to the same moments, saves both pictures and their
difference, and times both over a motion. It needs `playwright` (set `PLAYWRIGHT_FROM` to a folder that has it).
