# Р47, the fast page

`tools/web/fast.html` (`ui-gpu.js`, `vera-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`ui.js`, `vera.js`) is the page as it was; both run, both take the
same `window.A.set({...})`.

What took the time: the processor skinned all 58 thousand vertices every frame (8 ms of 12), and pushed the skirt off
the legs (4 ms).

What differs from `vera.js`:
- the skinning is in the vertex shader of the body's two paints (the piece picture and the flat paint); the folder and
  the ground keep the old shader; the processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin — the page's own, not `gs.lowest()`: this
  pack's shells lie one inside another with different joints (the foot inside the shoe), and engine-gpu's probe, which
  takes one vertex of every 1.5 cm of space where joints share the skin, was 12 mm off in the walk. Here it is one
  vertex of every such place for every different sharing of the joints, and 1000 directions instead of 200 for the
  parts one joint leads (a shoe's flat sole has many vertices nearly as low). Against all vertices over walk, idle and
  wave it is the same to 0.01 mm; it is built once in 0.1 s and costs 1 ms a frame;
- the skirt is pushed and pulled taut for the skirt's points only (skinned here as the engine does) and added in the
  shader; the legs' balls are a flat list;
- the canvas's size is set only when it changed;
- the clay look (`clay`, for the steps picture) takes the rest's normals turned with the joints, not normals
  recomputed from the posed skin: the skirt's shading differs a little there.

What is seen: the same pictures — stand, walk from two sides, wave, idle from behind, the face close differ in 0–2
pixels; the clay picture in 0.7 %. Speed on a laptop with an Intel Arc 140T at 1920×1080, walking: the processor
16–22 → 3.5–4.5 ms a frame; the page 41–53 → 57–60 frames a second.

What is still heavy: the video card's part, about 16 ms a frame at this size, as before — the piece picture at twice
the page's size, the paint multisampled, the contour found in the picture, and the face's and the glasses' canvases
(each the page's size) sent to the card every frame (2 ms of it). Not looked into further.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html?shots=1` and `new`
the `fast.html?shots=1` (docs/history/2026-11-13-characters-speed.md).
