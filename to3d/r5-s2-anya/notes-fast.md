# Р5, the fast page

`tools/web/fast.html` (`anya-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`anya.js`) is the page as it was; both run, both take the same
`window.A.set({...})`. Both need the pack in the address: `?pack=../../data/anya.json` (without it the page asks for
a file named `null` and does not start — the old page is so too).

What differs from `anya.js`:
- the skinning and the normals (from the posed triangles, as before) are worked out on the video card
  (`engine-gpu/`); the processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin;
- the canvas's size is set only when it changed.

What is seen: the same pictures. Old against fast over seven moments (standing, the face close, walking from the
front and from behind, sitting, a bow, a wave): not a pixel differs, but one in the wave.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html?pack=../../data/anya.json` and `new` the
`fast.html?pack=../../data/anya.json` (docs/history/2026-11-13-characters-speed.md).
