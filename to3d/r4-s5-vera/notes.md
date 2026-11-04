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

## Second round: alive (asked by Pavel through the coordinator, for the good ones)

What was asked: the face alive in its own drawn way (blinks at uneven times and on head turns, the eyes jumping in
small quick saccades and leading a head turn, mouth shapes for speech, smooth changes between the sheet's expressions
and mixes of them — timing from how real eyes and faces move, not sines); a few Kimodo motions from `engine/motions`
with the live face (walk, sit, look round, one with the arms free), framed so she is big; the 3D viewer able to show
it all (turn with the mouse, motion, expression, play/pause/scrub, speech on/off) for the site's 3D tab.

How:
- **The face is drawn live.** `tools/web/face.js` is a port of the drawing's face code (`face.py` `eye`/`brow`/`mouth`
  and `cast.vera`'s placement at yaw 0) to a 2D canvas, but from continuous numbers instead of named cases: lids
  (inner, outer cut), a "happy" amount that shuts the eye into the joy arc, eye size and highlight size, the drawing's
  highlight shift, brows (height, tilt), the tear, and the mouth as one closed shape of two cubic curves (every
  quadratic curve of the drawing turned into the cubic one exactly; the `o` mouth as a cubic ellipse; teeth and tongue
  as amounts). Each sheet expression is one set of these numbers; a mix is their weighted mean. `face_check.mjs`
  draws the five expressions with it beside the SVG-rendered textures (`tex/`) and overlays them: they match line for
  line. The head now carries a canvas texture (6 px per unit) redrawn every frame.
- **Timing** (`tools/web/live.js`, all random events seeded, so a film is the same every time):
  blinks — spontaneous intervals log-normal around 2.8 s (0.35–8 s), 12 % doubled, 12 % shallow; each closes in
  65–95 ms (accelerating), stays shut 25–55 ms, opens in 120–190 ms (decelerating); gaze shifts over ~16° bring a blink
  (more likely the bigger), and the end of a spoken sentence does half the time. Gaze — fixations log-normal around
  0.55 s (0.18–1.6 s), then a jump to a nearby point; the eyes reach a new target in ~2 frames (time constant 16 ms);
  while the head turns, they keep the same target (they turn back against the head). The eyes lead the head: when the
  head's direction 0.3 s ahead (read from the motion) differs from the gaze by >7°, they jump there first. The upper
  lid follows the eye down. Expressions — every number follows by a critically damped spring (brows ω 16, lids 19,
  mouth 24, the tear 5 per second); the head's tilt of each expression follows too. Speech — a few Russian phrases read
  letter by letter into mouth shapes (а/я→A, о/ё→O, у/ю→U, е/э→E, и/ы→I, м/б/п→closed, в/ф→teeth, other consonants
  a half-open shape), vowels 85–145 ms, consonants 50–100 ms, commas 0.22–0.32 s and full stops 0.6–0.95 s of rest; the
  shapes follow by a fast spring (ω 42) so they run into each other; the brows lift a little at a phrase's start.
  Without sound: the timing is the text's, not a voice's.
- **Motions** are converted from `engine/motions` (`tools/conv.py`, same maths as `experiments/indie/conv.py`) into
  `tools/motions/`. Clips: walk (the camera goes along; travel goes on across loops), sit (Kimodo's sit on the floor;
  the coat that would go under the floor lies on it: no vertex goes below the floor), wait and look round, wave.
  Engine/motions has no "look round": it is Kimodo's waiting motion with the head turned left and right on top
  (minimum-jerk turns of 0.55–0.65 s with rests; 60 % head, 40 % neck); the eyes lead it as above. Kimodo's waiting
  motion stoops ~25° forward on average; for Вера 85 % of that average lean is taken out (the upper body turned back
  about the waist by a constant), its movement kept.
- **Arms free** (wave): a second set of sleeves/hands on the arm bones, retargeted like the legs (a fixed turn from our
  bone to SOMA's rest direction), kept off the coat (upper arm at least ~25° out to the side) and out of the head; the
  folder hangs from the left hand on an upright joint of its own (`LeftProp`, not SOMA's, as in experiments/indie).
  Holding the folder (all other clips) the arms go with the body as before.
- **The coat's skirt front** below the hips now goes partly (up to 60 %) with the thigh behind it, so a stepping leg
  or a rising knee carries the coat front instead of going through it.
- **Viewer** (`tools/web/view.html` + `ui.js`): drag to turn (two fingers / wheel to come closer), the motions, the
  five expressions or a mix (sliders), speech on/off, play/pause and a scrub bar; the picture is centred above the
  controls, which fold away. `?shots` turns the controls off (used by `shots.mjs`).

Repeat: `python3 tools/make.py walk sit look wave face` (≈ 2.3 s a frame on swiftshader); `node tools/face_check.mjs <dir>`.

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
