# Р28, the fast page

`tools/web/fast.html` (`view-gpu.mjs`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`view.mjs`) is the page as it was; both run, both take the same
`window.A.set({...})` and `?shots=1`. `face.mjs` and `life.mjs` are shared by both, unchanged.

What took the time in `view.mjs`, every frame, for each of 91 thousand vertices, in JavaScript: the skinning (dual
quaternions) — about a half; the normals twice — the engine's, which the page never used, and three.js's
`computeVertexNormals` — about a third; copying and sending every place and normal — the rest. The face was a
hundredth of it.

What differs from `view.mjs`:
- the skinning and the normals are in the vertex shader: added to the puppet's physical materials (three.js's, through
  `onBeforeCompile`, beside the additions they had) and to the shadow's depth material; the processor works out the
  joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin (engine-gpu's README): within 1.6 mm (0.2 mm on average) of
  the old over walk, sit, bow, dance, jump and run;
- the face: its vertices are moved at rest — the head is rigid on its joint (every vertex the face moves has the Head
  joint's whole weight), so the skinning carries the moved rest as the old turn of (displaced − rest) did; their
  normals and their neighbours' are found again from the rest's triangles; both are worked out and sent (that part of
  the buffers only) only when the face's numbers changed.

What is seen: the same puppet — face, hair, materials, shadow. Compared picture by picture (standing; walking from
the front, the side and the back; a bow from the front and the side; sitting; dancing; the face close — calm,
speaking, sad, angry), 0.01–0.7 % of a picture differs. It is the light on cloth where the body bends: the old page
lit the skinning's own small ripples and creases (a band across the apron's bib when the trunk leans, the folds between the knees when he sits); the fast page's normals are the rest's turned with the
joints, so the cloth is smoother there. Outlines lie within a pixel.

Speed on a laptop with an Intel Arc 140T at 1920×1080, walking, measured roughly (other pages used the machine at the
same time): the main thread 39 → 4.4 ms a frame, 27 → 60 frames a second. What is left on the processor: the floor's probe
(8.6 thousand vertices, 0.3–1 ms), the face (about 0.5 ms: its numbers change with the gaze nearly every
frame), and three.js drawing the puppet's materials.

To check again: open both pages with `?shots=1`, give both the same `A.set({motion, t, expr, near, talk})`, compare
the canvases. (`engine-gpu/check/compare.mjs` wants `A.render()`, which these pages do not have.)
