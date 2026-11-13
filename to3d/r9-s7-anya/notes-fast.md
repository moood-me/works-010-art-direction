# Р9, the fast page

`tools/web/fast.html` (`anya-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`anya.js`) is the page as it was; both run, both take the same
`window.A.set({...})`.

What differs from `anya.js`:
- the skinning and the normals are in the vertex shader of the two materials (the body, the outline's hull); the
  processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin, within 2.7 mm of the old over walk, sit,
  dance, lie, roll, jump, bow, run;
- the skirt's push off the legs is computed for the skirt's points only and added in the shader; the pushed skirt
  keeps the unpushed skirt's normals;
- the face's canvas is redrawn and sent only when the face's numbers or its line's width changed;
- the canvas's size is set only when it changed.

What is seen: the same character, but the shade differs in places, because the normals are not recomputed from the posed
triangles: on the skirt where the legs push it out (bowing: a band of shade down the skirt's front where the old page has
it only under the cardigan; sitting, running), on the cardigan's back when sitting (the old page's patch of shade is
gone), small patches at the armpit. The face is the same.

Speed was not measured when the page was made.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html` and `new` the
`fast.html` (docs/history/2026-11-13-characters-speed.md).
