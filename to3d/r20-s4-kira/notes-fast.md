# Р20, the fast page

`tools/web/fast.html` (`ui-gpu.js`, `figure-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`ui.js`, `figure.js`) is the page as it was; both run, both take
the same `window.A.set({...})`. `ui-gpu.js` is `ui.js` loading `figure-gpu.js`; `char.js`, `face.js` and `life.js`
serve both.

What differs from `figure.js`:
- the skinning and the normals are in the vertex shader of the two materials (the body, the shadow map's depth); the
  processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin, within about a millimetre of the old;
- the face's displacement (`face.js`) is an attribute, turned with the head in the shader; it is worked out and sent
  only when the face's numbers changed (a still face costs nothing; a living one costs `face.update` for the head's
  points each frame, as before);
- the `rest` attribute is gone (the rest's place is `position` now): with the skinning's four and the face's one the
  shader has its 16;
- the canvas's size is set only when it changed.

What is seen: the same pictures — the face and its expressions are the same — but the shadow's edge lies a little
differently where the form bends (the normals are the rest's, turned with the joints, not recomputed from the posed
triangles; the moved face keeps its own): the shade in the armpit and at the elbow's fold.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html?shots=1` and `new`
the `fast.html?shots=1` (docs/history/2026-11-13-characters-speed.md).
