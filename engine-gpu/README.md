# engine-gpu — the early engine's skinning on the video card

Beside `engine/`, not in its place: `engine/` is as it was, and the pages that stand on it are as they were. This
folder takes the engine's own body, skeleton, motions and `Skinner` and moves the per-vertex work — skinning and
normals — onto the video card, so each frame the processor works out only the 77 joints.

```
src/gpuskin.js    GpuSkin: the skin into two textures (places, normals), what a material reads, a few vertices on the processor
bench/            several characters in one scene, the old way and the new: frames a second, the longest gap
check/compare.mjs a page as it was against its fast variant: pictures, their difference, milliseconds a frame
```

## Why

A Р page does this every frame for every vertex, in JavaScript: skinning (`engine/src/skin.js`), the lowest point (to
stand on the floor), normals from the posed triangles (`normalsOf`), and then sends all positions and normals to the
video card. For a character of 38 thousand vertices that is about 5 ms of the processor and as much again to send and
draw (measured on a laptop with an Intel Arc 140T, 1920×1080 — the numbers are in `docs/history/`). One character fits
into a frame; two do not.

## How it works

Each frame the skin is drawn twice into two small float textures, a texel a vertex: first every vertex skinned (its
place in the pose), then every vertex's normal from the posed places of the triangles around it — the same sum as
the engine's `normalsOf`. The materials that draw the skin (the body, an outline's hull, a shadow map's depth) only
read their vertex's two texels. So the skin is skinned once a frame however many times it is drawn, the normals are
the posed skin's own (folds of cloth, bends), and the drawn geometry carries no skinning attributes.

## How to use it

```js
import { GpuSkin } from '<root>/engine-gpu/src/gpuskin.js';
const fig = new Figure(body, spec, place);              // the engine's, as before: retargeting and the Skinner
const gs = new GpuSkin(THREE, fig.skinner);
const g = gs.attributes(new THREE.BufferGeometry());    // position and normal: the rest's (three.js wants them)
// every material that draws the skin:
//   uniforms: { ...gs.uniforms, … }
//   vertexShader: `${gs.glsl} … void main() { vec3 P, N; skinVertex(P, N); … use P and N … }`
// each frame:
const pose = fig.retarget.pose(clip.sample(t, fig.sample)); fig.retarget.placed(pose);
const shift = pose.floor - gs.lowest(pose);             // on the floor, as motion.floor 'lowest'
for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
gs.setPose(pose);
gs.update(renderer);                                    // before the skin is drawn
```

`to3d/r45-s15-anya/tools/web/anya-gpu.js` (page `fast.html`) is a whole page made so, beside its `anya.js`.

## What is the same and what is not

- **Positions: the same.** The first pass does what `Skinner.skin` does, for `cor`, `dqs` and `lbs`: the same blend
  of the joints' turns, the same centres of rotation (the Skinner's own, sent as an attribute).
- **Normals: the same.** The second pass sums the posed triangles around each vertex as `normalsOf` does.
- **The floor: nearly.** `lowest(pose)` skins a probe on the processor and takes its lowest point: for each joint, the
  vertices it leads that lie furthest out in 1000 directions; and where joints share the skin (bends, a skirt between
  the legs), one vertex of every 1.5 cm of space for each set of joints. On Р45 that is 7.4 of 38 thousand vertices,
  and against all vertices it is within 0.4 mm at worst over walk, sit, dance, lie, roll, jump and bow.
- **What a page does to the posed skin on the processor** (a skirt pushed off the legs, a brow moved) stays on the
  processor, for those vertices only: `gs.subset(indices).skin(pose, out)` gives their places (the same numbers as
  the engine's), the page works out an offset, writes it into `gs.skinD` and calls `gs.displace(first, count)`; the
  first pass adds it after skinning, and the normals follow.
- **`Skinner`'s `seam` option** (Т7's smoothing where trunk meets arm) is not carried: no Р page asks for it. A page
  that does takes it as the skirt above.
- **Pages that read every vertex's place on the processor** (section К measures skin against a table or another
  body; the pen pages find their lines there) stay on `engine/`; for a few vertices `subset` is enough.
- **It needs a video card that can draw into float textures** (`EXT_color_buffer_float`; desktop cards and current
  phones have it). Without it `update` stops with an error.

## The check

`node engine-gpu/check/compare.mjs jobs.json out/` opens the old page and the fast one in real Chrome (not the
software renderer: the question is the video card), sets both to the same moments, saves both pictures and their
difference, and times both over a motion. It needs `playwright` (set `PLAYWRIGHT_FROM` to a folder that has it).
