# Р47, the fast page

`tools/web/fast.html` (`ui-gpu.js`, `vera-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`ui.js`, `vera.js`) is the page as it was; both run, both take the
same `window.A.set({...})`.

What took the time: the processor skinned all 58 thousand vertices every frame (8 ms of 12), and pushed the skirt off
the legs (4 ms).

What differs from `vera.js`:
- the skinning and the normals are on the video card (engine-gpu draws the posed skin into two textures; the body's
  two paints — the piece picture and the flat paint — read them); the folder and the ground keep the old shader; the
  processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin (`gs.lowest()`). This page showed what the
  probe needed: the pack's shells lie one inside another with different joints (the foot inside the shoe), and a shoe's
  flat sole has many vertices nearly as low — the probe now takes that into account;
- the skirt is pushed and pulled taut for the skirt's points only (skinned here as the engine does) and added in the
  shader; the legs' balls are a flat list;
- the canvas's size is set only when it changed.

What is seen: the same pictures — stand, walk from two sides, wave, idle from behind, the face close and the clay look
differ in 0–18 pixels of the page. Speed on a laptop with an Intel Arc 140T at 1920×1080, walking: the processor
12 → 3 ms a frame.

What is still heavy: the video card's part, about 16 ms a frame at this size, as before — the piece picture at twice
the page's size, the paint multisampled, the contour found in the picture, and the face's and the glasses' canvases
(each the page's size) sent to the card every frame (2 ms of it). Not looked into further.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html?shots=1` and `new`
the `fast.html?shots=1` (docs/history/2026-11-13-characters-speed.md).
