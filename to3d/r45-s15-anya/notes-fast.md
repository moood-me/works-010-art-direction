# Р45, the fast page

`tools/web/fast.html` (`anya-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`anya.js`) is the page as it was; both run, both take the same
`window.A.set({...})`.

What differs from `anya.js`:
- the skinning and the normals are on the video card (engine-gpu draws the posed skin into two textures; the body,
  the rim's hull and the shadow map's depth read them); the processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin, within 0.4 mm of the old;
- the skirt's push off the legs is computed for the skirt's points only and added on the video card;
- the face's canvas is redrawn and sent only when the face's numbers changed;
- the `morph` option is gone (the pack has no morphs).

What is seen: the same pictures (of eight moments five are the same to the pixel, the rest differ in 1–310 pixels of
the page). Speed on a laptop with an Intel Arc 140T at 1920×1080, walking: the processor 5.3 → 2.0 ms a frame;
sixteen such characters in one scene hold 60 frames a second (`engine-gpu/bench/`), the old way four do not.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html` and `new` the
`fast.html` (docs/history/2026-11-13-characters-speed.md).
