# Р1, the fast page

`tools/web/fast.html` (`anya-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`anya.js`) is the page as it was; both run, both take the same
`window.A.set({...})`.

What differs from `anya.js`:
- the skinning and the normals (from the posed triangles, as before) are computed on the video card, into two
  textures that the two materials (the body, the outline's hull) read; the processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin, within 1.9 mm of the old over walk, sit,
  dance, lie, roll, jump, bow, run;
- the skirt's push off the legs is computed for the skirt's points only and added on the video card after the
  skinning; the normals follow the push;
- the face's canvas is redrawn and sent only when the face's numbers changed;
- the `morph` option is gone (the pack has no morphs);
- the canvas's size is set only when it changed.

What is seen: the same pictures. Of nine moments compared with the old page (stand, walk, sit, bow, dance, run, the
face close), eight are the same pixel for pixel or but for a few pixels; in one (the dance) the
whole outline differs by a part of a pixel, because the floor there is found about 1 mm off.

Speed was not measured when the page was made.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html` and `new` the
`fast.html` (docs/history/2026-11-13-characters-speed.md).
