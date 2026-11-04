# Р4 — Вера, инди (style С5) in 3D

## What was done, and why this way

- **Base: the indie constructor, not Anny.** Вера in С5 is ~3.1 heads tall: a ball head as wide as her shoulders, a
  coat-cone body, stick legs. Anny is a human adult body; to reach these proportions it would have to be squashed into
  something it is not (head ×2.5, legs ×0.4), and everything that makes it good (anatomy, muscles) would be lost or
  in the way. The indie constructor (`experiments/indie`, gallery П1) is made for exactly this: simple forms with
  smooth joins, each tied to a SOMA joint (no fingers), skinned, moved by Kimodo with motions retargeted onto short
  limbs. Brief point 1 (Anny) and point 2 (an artist's head base) are therefore not used here: a Blender base head has
  a human skull and face; Вера's face is a few graphic signs on a ball.
- **The forms are the drawing's own numbers.** The С5 drawings are not hand-drawn curves: `styles/s5-indie/tools/cast.py`
  builds Вера from 3D volumes — stacks of elliptic rings `(y, w, d, cx, cz)` for the head, bun, turtleneck, coat and
  shoes; tubes for arms and legs; spheres for hands — and projects them at a yaw. `tools/web/vera.js` takes the same
  rings and turns each into a signed distance (`rings()`: the ring ellipse's distance, smoothed through the rings as
  the drawing's outline is, corrected for slanted walls), so the 3D is the drawing's volume by construction. The hair
  is the head grown by 4 units and cut by the drawing's hairline keys `(phi, y)`; the bun joins it. The pencil, the
  folder with its bookmark, the coat's front line and buttons, ears with earrings — all at the drawing's coordinates.
  1 drawing unit = 2.5 mm, so she is 1.16 m tall.
- **One departure from the numbers:** by its numbers the drawn upper arm lies inside the coat, and the drawing simply
  paints the sleeve over it. In 3D the shoulder and elbow are moved out and forward (shoulder ±45 → elbow ±55, z 22)
  so the sleeves lie on the coat as drawn.
- **Skeleton:** SOMA's joint names and hierarchy (the constructor's `PARENT`), placed on the drawing: hips at y −105
  inside the coat, chest at the shoulders, the head's pivot at the turtleneck, legs straight down to the shoes, the
  arms as drawn (holding the folder). The coat and turtleneck are weighted by height along hips → spine → chest (a
  small addition to the constructor's `buildParts`, which otherwise ties a form to one bone or splits it at a joint).
- **Face and colour from the SVG.** `tools/face_tex.py` calls `cast.vera(0, expr)` from the style's own code, keeps
  only the face layer (eyes with lids and highlights, brows, nose, mouth, blush, bags, the tear), drops the head's
  placement and tilt, and renders it head-on on a transparent ground (8 px per unit) — one texture per expression of
  the sheet. The head carries it by a straight projection from the front (masked off where the head turns away).
  Glasses are 3D: two rounded-rectangle frames standing ~5 units off the face and turned with it, a bridge, arms to
  the ears, a white glint. Every paint is the drawing's hex; the shade of each paint is the drawing's rule
  (`geo.shade_of`: 28 % toward `#2a1f3d`), skin uses the drawing's own skin shade.
- **Look:** a shader of two tones — the paint and its shade, the border where the surface turns from a light held to
  the view at the upper left (as the drawing's shade sits lower right on every form) — and an inverted-hull outline in
  the drawing's line colour `#4a3036`, 2.1 units on figures (thinner on close-ups, as the drawing does). Paints go to
  the screen as written (no tone mapping), so the colours match the SVG exactly.
- **Motion:** Kimodo's walk from `experiments/indie/motions/walk.json`, retargeted the constructor's way: each SOMA
  joint turns as in the motion, a fixed turn first brings our leg bones to SOMA's rest direction, the pelvis goes as
  high and as far as our legs make it (×0.26), the feet are put on the floor. The arms keep the folder at the chest:
  they take no turns of their own from the motion. While she holds the folder, sleeves, hands and folder are weighted
  along the body like the coat (hips → spine → chest): tied to the chest alone, the folder's lower edge went into the
  coat as soon as the spine bent. The arm bones are in the skeleton for motions that free the arms (not made here).
  The coat skirt is on the hips; the thighs move inside it.
- **Judged by eye**, many times, in the drawing's own views (same viewBox, same pixels, orthographic like the
  drawing): side by side and with the drawing's edges over the render.

## How to repeat

```
cd to3d/r4-s5-vera/tools
python3 face_tex.py        # tex/face-*.png from the style's code (needs node + playwright)
python3 make.py stills     # turn / figure / portrait / expressions / back / steps → ../pics
python3 make.py films      # turn.mp4, walk.mp4 → ../pics (≈ 1 s per frame on swiftshader)
```
`shots.mjs` serves the repository, opens `tools/web/view.html` in headless Chromium (software WebGL), routes three.js
r160 to the local copy in `/home/user/cache/n3-cloth/node_modules/three`, and calls `window.A.set({...})` per shot.
`compare.py` makes the side-by-side and overlay pictures. Building the meshes takes ~15 s in the page.

Files: `tools/web/forms.js` — the constructor's forms and mesher, copied unchanged from `experiments/indie/index.html`;
`tools/web/vera.js` — Вера, the look, the skeleton, the motion; `tools/web/view.html` — the page.

## What is weak (honestly)

- The drawing's turnaround cheats: the face turns ~0.38·sin(yaw) further than the skull, so in three-quarter and
  profile the drawn eyes are fuller. The 3D face is a real one on the ball: in profile the eye is narrow and the face
  sits nearer the edge. Not done: a view-dependent cheat would break the model for the engine.
- The projected face is right from the front and slightly stretched at the cheeks; lines are drawn at the figure's
  width, so on a close-up (the portrait) the face lines are thicker than the drawing's.
- The sleeves join the coat without a line on their inner side (the drawing outlines every tube all round).
- The hairline edge shows a faint light sliver at the parting on close-ups (the mesher at a thin edge).
- The walk is Kimodo's with held arms; the coat does not swing (it is rigid on the hips).

## Licences

Everything here is ours: the drawing and its code (`styles/s5-indie`), the constructor (`experiments/indie`),
Kimodo's walk (made in the moood studio, `experiments/indie/motions`), three.js (MIT). No third-party models, no
neural networks.
