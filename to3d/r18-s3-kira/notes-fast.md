# Р18, the fast page

`tools/web/fast.html` (`char-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`char.js`) is the page as it was; both run, both take the same
`window.A.set({...})`.

What differs from `char.js`:
- the skinning and the normals are in the vertex shader of the two materials (the body, the outline's hull); the
  processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin, within 1.0 mm of the old over walk, sit,
  dance, lie, roll, jump, bow, run;
- the skirt's push off the legs (for a pack with a dress; this one has none) is computed for the skirt's points only
  and added in the shader;
- the face's canvas is redrawn and sent only when the face's numbers changed;
- the `morph` option is gone (the pack has no morphs);
- the canvas's size is set only when it changed.

What is seen: the same pictures; the outline differs by a part of a pixel, and inside a deep bend (sitting) the shade's edge
lies a few pixels differently.

Speed was not measured when the page was made.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html` and `new` the
`fast.html` (docs/history/2026-11-13-characters-speed.md).
