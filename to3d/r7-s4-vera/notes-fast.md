# Р7, the fast page

`tools/web/fast.html` (`ui-gpu.js`, `vera-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`ui.js`, `vera.js`) is the page as it was; both run, both take the
same `window.A.set({...})`. `ui-gpu.js` is `ui.js` loading `vera-gpu.js`; `face.js` and `life.js` serve both.

What differs from `vera.js`:
- the skinning and the normals (from the posed triangles, as before) are worked out on the video card
  (`engine-gpu/`); the processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin;
- the face's displacement (`face.js`) is worked out only when the face's numbers changed; turned with the head, it
  goes into the skin's offsets (`gs.skinD`) for the head's and the irises' points when it or the head's turn changed,
  and the normals follow it, as before (a living face still costs `face.update` for the head's points each frame);
- the skirt's push off the legs is computed for the skirt's points only, with numbers instead of small arrays, and
  goes into the skin's offsets too; it is sent only while a point is in a leg;
- the folder has a depth material of its own for the shadow map (the body's reads the skin's textures);
- the canvas's size is set only when it changed.

What is seen: the same pictures. Old against fast over twelve moments (standing, the face close in four expressions,
walking, sitting, a bow, a wave, running): at most one pixel differs.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html?shots=1` and `new` the
`fast.html?shots=1` (docs/history/2026-11-13-characters-speed.md).
