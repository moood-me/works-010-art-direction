# Р16, the fast page

`tools/web/fast.html` (`klaus-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`klaus.js`) is the page as it was; both run, both take the same
`window.A.set({...})`, both use the same `ui.js`.

What differs from `klaus.js`:
- the skinning (dual quaternions, with the collarbone's share) and the normals (from the posed triangles, as before) are worked out on the video card
  (`engine-gpu/`); the processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin;
- the forms that move on the face (the moustache, the beard) are moved in the page's shaders, after the skin: the processor
  works out their offset for their own points only and sends it while a form is off its place. They are not put into
  the skin's own offsets (`gs.skinD`): the page as it was moves them after its normals are found, so they keep the
  unmoved skin's normals, and so they do here;
- the canvas's size is set only when it changed.

What is seen: the same pictures, the face and its moving forms too. Old against fast over standing, the face close in
three expressions, walking from the front and from behind, sitting, a bow, a wave: at most 0.004 % of the picture differs (sitting: the floor's probe is
off by 0.6 mm there; 1.6 mm at worst in the dance); nothing the eye finds.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html?shots=1` and `new` the
`fast.html?shots=1` (docs/history/2026-11-13-characters-speed.md);
set `live: false` and `wait: true` so both faces are at the same moment with their pictures loaded.
