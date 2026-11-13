# Р16, the fast page

`tools/web/fast.html` (`klaus-gpu.js`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`klaus.js`) is the page as it was; both run, both take the same
`window.A.set({...})`, both use the same `ui.js`.

What differs from `klaus.js`:
- the skinning (dual quaternions, with the collarbone's share) and the normals are in the vertex shader of the two
  materials (the body, the shadow map's depth); the processor works out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin, within about a millimetre of the old;
- the forms that move on the face (the moustache, the beard) are moved in the shader: the processor works out their
  offset for their own points only and sends it while a form is off its place;
- the `rp` attribute is gone (the rest's place is `position` now): with the skinning's four the shader has its 16;
- the canvas's size is set only when it changed.

What is seen: the same pictures — the face, its expressions, the moving moustache and beard are the same — but the
shadow's edge lies a little differently where the form bends or stretches (the normals are the rest's, turned with
the joints, not recomputed from the posed triangles): walking, the dark fold on the apron between the legs is lighter
and narrower; sitting and bowing, the light's patches on the apron and on the shirt's back are a little other.

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html?shots=1` and `new`
the `fast.html?shots=1` (docs/history/2026-11-13-characters-speed.md); set `live: false` and `wait: true` so both
faces are at the same moment with their pictures loaded.
