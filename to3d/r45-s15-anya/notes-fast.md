# Р45, the fast page

`tools/web/fast.html` (`anya-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`anya.js`) is the page as it was; both run, both take the same
`window.A.set({...})`.

What differs from `anya.js`:
- the skinning and the normals are in the vertex shader of the three materials (the body, the rim's hull, the shadow
  map's depth); the processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin, within 1.5 mm of the old;
- the skirt's push off the legs is computed for the skirt's points only and added in the shader; the pushed skirt
  keeps the unpushed skirt's normals;
- the face's canvas is redrawn and sent only when the face's numbers changed;
- the `morph` option is gone (the pack has no morphs).

What is seen: the same pictures, but the black's edge on the skirt and on the jacket's folds lies a few pixels
differently in some poses. Speed on a laptop with an Intel Arc 140T at 1920×1080, walking: the processor 5.3 → 1.7 ms
a frame; sixteen such characters in one scene hold 60 frames a second (`engine-gpu/bench/`), the old way four do not.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html` and `new` the
`fast.html` (docs/history/2026-11-13-characters-speed.md).
