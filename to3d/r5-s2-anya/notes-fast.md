# Р5, the fast page

`tools/web/fast.html` (`anya-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`anya.js`) is the page as it was; both run, both take the same
`window.A.set({...})`. Both need the pack in the address: `?pack=../../data/anya.json` (without it the page asks for
a file named `null` and does not start — the old page is so too).

What differs from `anya.js`:
- the skinning and the normals are in the vertex shader of the two materials (the body, the shadow map's depth); the
  processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin, within about a millimetre of the old;
- four per-vertex scalars (`tw`, `pw`, `two`, `hair`) go in one attribute: a vertex shader takes 16 attributes, and
  the skinning takes four of them;
- the canvas's size is set only when it changed.

What is seen: the same pictures, but the shadow's edge lies a little differently where the form bends or stretches
(the normals are the rest's, turned with the joints, not recomputed from the posed triangles): walking, the dark fold
on the skirt between the legs is lighter and narrower; sitting, the light's patch on the sleeve at the shoulder and on
the skirt over the hip is a little other. The face, the hair and the standing figure are the same.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the
`view.html?pack=../../data/anya.json` and `new` the `fast.html?pack=../../data/anya.json`
(docs/history/2026-11-13-characters-speed.md).
