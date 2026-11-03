# Н6 — MToon: toon light and outline

## What was done, and why
Pavel asked to see, for each ready open tool, how our thing looks now and how it looks with the tool. For the toon look
(stepped shade + outline) the tool is MToon, VRM's standard toon material, in pixiv's three-vrm. Later he also asked to
show the tool in the cases it was made for (`uses`), and to say in each compare block what the method is and why it
exists.

- **Our scenes with MToon, same models, views and light.** `tools/run.html` runs an experiment page of this repository
  as it is (fetches its HTML, adds three hooks: scene, renderer and camera to `window`, holds "ready"), with the page's
  own folder as base, so it loads its own data and builds the same meshes. `tools/mtoon.js` then swaps every lit
  figure material (MeshToonMaterial / MeshStandardMaterial of things that cast shadows) for an `MToonMaterial` with the
  same colour, texture and vertex colours, hides our own outline shells (back-faced dark copies), and adds MToon's
  outline the way three-vrm's loader does (the triangles twice, the second time with an outline copy of the material).
  `look(scene, 'ours')` puts everything back, so ours and MToon are shot from the same page load. The engine's viewer
  exposes its stage (`window.__viewer`), so there `mtoon.js` is imported into the viewer itself.
- **Looks** (`LOOKS` in `mtoon.js`): `hard` toony 0.95, `soft` toony 0.3, shade = base colour × 0.42; `tint` shade
  = base × (0.55, 0.36, 0.48) (warm, reddish-violet); `rim` adds a parametric rim (#c89a7a, power 4) and a matcap
  (a soft spot drawn on a canvas, factor 0.5); outlines `thin`/`tint`/`thick` in world units (0.8, 2.2, 6 mm × a scale
  per scene: 0.8 for heads, 2.7 for the П2 cast so that `tint` = our 6 mm, 1.5 for the full body) and `screen`
  (0.006 of half the picture height). `+one` turns the scene's back (rim) light off: MToon treats every directional
  light as a sun and our back light lifts the shade almost to lit.
- **Scenes:** Г1 `experiments/heads-anime` (anime girl and red-haired girl in three-quarter, hooded woman from the
  side), П2 `experiments/toon?v=2` (jester, imp, cat), Д1 `engine/viewer` (woman, walk frame 20, three-quarter and
  head). П1 (`experiments/indie`) was not used: its materials are shared and re-set on every redraw.
- **Uses:** two open VRM samples loaded by three-vrm with their own MToon settings, one sun as in three-vrm's examples
  (`tools/vrm.html`): as authored, without the outline (the outline materials hidden), and with a plain
  MeshStandardMaterial on the same textures; a 3 s turn.

## How to repeat
```
# shots of our scenes (headless Chromium, swiftshader; ~1 min per scene)
NODE_PATH=/opt/node-tools/node_modules node tools-demo/n6-toon/tools/shot.mjs jobs.json /home/user/cache/n6-toon/out
# the VRM samples, from a folder with Seed-san.vrm and VRM1_Constraint_Twist_Sample.vrm
NODE_PATH=/opt/node-tools/node_modules node tools-demo/n6-toon/tools/vrmshot.mjs /home/user/cache/n6-toon/vrm /home/user/cache/n6-toon/vout
# the page's sheets
sh tools-demo/n6-toon/tools/build.sh
```
`jobs.json` used (a job: `src` + the page's own query, or `engine`; `looks`; `over.outlineScale`):
```json
[{"name":"g-anime-tq","src":"experiments/heads-anime/index.html","q":"c=anime&view=tq","looks":["ours","hard","hard+one","soft+one","tint+one","rim+one","thin+one","thick+one","screen+one"],"w":600,"h":600,"over":{"outlineScale":0.8}},
 {"name":"g-red-tq","src":"experiments/heads-anime/index.html","q":"c=red&view=tq","looks":["ours","hard","hard+one","soft+one","tint+one","rim+one"],"w":600,"h":600,"over":{"outlineScale":0.8}},
 {"name":"g-hood-side","src":"experiments/heads-anime/index.html","q":"c=hood&view=side","looks":["ours","hard+one","soft+one","tint+one","rim+one"],"w":600,"h":600,"over":{"outlineScale":0.8}},
 {"name":"p-three","src":"experiments/toon/index.html","q":"c=jester,imp,cat&v=2","looks":["ours","hard","hard+one","soft+one","tint+one","rim+one","thin+one","thick+one","screen+one"],"w":1200,"h":700,"over":{"outlineScale":2.7}},
 {"name":"d-woman","engine":{"char":"woman","clip":"walk","t":20,"view":"three"},"looks":["ours","hard","hard+one","soft+one","tint+one","rim+one","screen+one","ours"],"w":600,"h":800,"over":{"outlineScale":1.5}},
 {"name":"d-woman-face","engine":{"char":"woman","clip":"walk","t":20,"view":"three","dist":0.9,"focus":"Head","pitch":0.05},"looks":["ours","hard+one","soft+one","tint+one","rim+one","ours"],"w":600,"h":600,"over":{"outlineScale":0.8}}]
```
Open by hand: serve the repository and go to
`tools-demo/n6-toon/tools/run.html?src=experiments/toon/index.html&c=imp&v=2&look=tint+one`
(`look=ours` for ours; in the console `__look('soft+one')`).

## Versions, sources, licences
- `@pixiv/three-vrm-materials-mtoon@3.5.5` and `@pixiv/three-vrm@3.5.5` (MIT, pixiv), from cdn.jsdelivr.net;
  three.js 0.160.0 as our pages. The npm package was also unpacked into `/home/user/cache/n6-toon/package` to read it.
- Seed-san.vrm — VirtualCast, Inc., VRM Public License 1.0 (redistribution and modification allowed), from
  https://github.com/vrm-c/vrm-specification/tree/master/samples/Seed-san
- VRM1_Constraint_Twist_Sample.vrm — (c) 2022 pixiv Inc., VRM Public License 1.0, from
  https://github.com/vrm-c/vrm-specification/tree/master/samples/VRM1_Constraint_Twist_Sample
  (also in three-vrm's examples). The models are not in the repository (10 MB each), only pictures of them.

## What was seen
- MToon's single shade edge is cleaner on our heads than our three-step ramp (which leaves blotches on face and neck);
  shade colour, rim and matcap are one setting each.
- With our light (key + back light + sky) MToon's shade nearly vanishes; with one key light it works as meant.
- The outline is the same inverted-hull technique as ours, with the same faults (lines inside hair locks).
- On Anny's body the shade edge follows every small dent of the mesh: a ragged patch on the face. VRM authors avoid
  it with painted shading-shift textures and smoothed face normals.
- The VRM samples look good mostly from their painted textures; MToon adds the outline, the soft shade step and the
  skin's shade colour.
