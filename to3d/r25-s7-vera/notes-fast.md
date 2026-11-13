# Р25, the fast page

`tools/web/fast.html` (`char-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`char.js`) is the page as it was; both run, both take the same
`window.A.set({...})`.

What differs from `char.js`:
- the skinning and the normals are in the vertex shader of the two materials (the body, the outline's hull); the
  processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin, within 1.9 mm of the old over walk, sit,
  dance, lie, roll, jump, bow, run;
- the face's canvas is redrawn and sent only when the face's numbers, its line's width or the nose's side changed;
- the canvas's size is set only when it changed.

What is seen: the same pictures; the outline differs by a part of a pixel, and the shade's edge on the sleeves and the
trousers' folds lies a few pixels differently in deep bends (sitting).

Speed was not measured when the page was made.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html` and `new` the
`fast.html` (docs/history/2026-11-13-characters-speed.md).
