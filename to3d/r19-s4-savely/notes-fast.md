# Р19, the fast page

`tools/web/fast.html` (`ui-gpu.js`, `figure-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`ui.js`, `figure.js`) is the page as it was; both run, both take
the same `window.A.set({...})`. `ui-gpu.js` is `ui.js` loading `figure-gpu.js`; `char.js`, `face.js` and `life.js`
serve both.

What differs from `figure.js`:
- the skinning and the normals (from the posed triangles, as before) are worked out on the video card
  (`engine-gpu/`); the processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin;
- the face's displacement (`face.js`) is worked out only when the face's numbers changed; turned with the head, it
  goes into the skin's offsets (`gs.skinD`) for the head's and the irises' points when it or the head's turn changed,
  and the normals follow it, as before (a living face still costs `face.update` for the head's points each frame);
- the canvas's size is set only when it changed.

What is seen: the same pictures. Old against fast over eleven moments (standing, the face close in four expressions,
walking, a third motion, sitting): not a pixel differs but in two moments (55 pixels walking seen from behind, one sitting).

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html?shots=1` and `new` the
`fast.html?shots=1` (docs/history/2026-11-13-characters-speed.md).
