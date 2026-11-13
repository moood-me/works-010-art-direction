# Р10, the fast page

`tools/web/fast.html` (`view-gpu.mjs`) is this character's page with the skin skinned on the video card
(`engine-gpu/`, its README). `tools/web/view.html` (`view.mjs`) is the page as it was; both run, both take the same
`window.A.set({...})` and `?shots=1`. `face.mjs` and `life.mjs` are shared by both, unchanged.

What took the time in `view.mjs`, every frame, for each of 50 thousand vertices, in JavaScript: the skinning (dual
quaternions) — about a half; the normals twice — the engine's, which the page never used, and three.js's
`computeVertexNormals` — about a third; copying and sending every place and normal — the rest. The face was a
hundredth of it.

What differs from `view.mjs`:
- the skin's places and normals are worked out on the video card each frame (engine-gpu: every vertex skinned, then
  its normal summed from the posed triangles around it); the puppet's physical materials (three.js's, through
  `onBeforeCompile`, beside the additions they had) and the shadow's depth material read them; the processor works
  out the joints;
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin (engine-gpu's README): within 0.6 mm, but sitting 1 mm on average and 1.9 mm at worst, of
  the old over walk, sit, bow, dance, jump and run;
- the face is laid on as before — each vertex it moves by the head's turn of (displaced − rest) — but for those
  vertices only, as an offset the video card adds after its skinning (`gs.skinD`), so the normals there are the moved
  skin's; the face's shapes are mixed only when its numbers changed.

What is seen: the same puppet. Compared picture by picture (standing; walking from the front, the side and the back;
a bow from the front and the side; sitting; dancing; the face close — calm, speaking, sad, angry): the face close and the walk from the front and the back differ by a
few pixels; standing, the bow, the dance and the walk from the side 0.1–0.26 %, sitting 1 % — the whole figure stands
a part of a pixel off (sitting, a pixel): the floor, above. The sweater's folds are lit as in the old page.

Speed on a laptop with an Intel Arc 140T at 1920×1080, walking, measured roughly (other pages used the machine at the
same time): the main thread 20 → 3 ms a frame, 50 → 60 frames a second. What is left on the processor: the floor's probe
(6.3 thousand vertices, about 0.8 ms — the largest part), the face (0.2–0.4 ms), and three.js drawing
the puppet's materials.

To check again: open both pages with `?shots=1`, give both the same `A.set({motion, t, expr, near, talk})`, compare
the canvases. (`engine-gpu/check/compare.mjs` wants `A.render()`, which these pages do not have.)
