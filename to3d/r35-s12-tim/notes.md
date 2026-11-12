# Р35 — Тим, перо и акварель: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, third round; brief: `docs/briefs/to3d.md`, "Third round"):
Тим of style С12 (`styles/s12-ink-watercolour`, Quentin Blake / Sempé pen and watercolour) made a 3D character that
moves by Kimodo through the engine and is drawn every frame with that style's own pen and wash code — the way Р12's Аня
is (`to3d/r12-s12-anya`), so the two stand side by side as characters of one style. Asked for by Pavel through the
orchestrator: each style gets two more characters in 3D, starting from the one already made.

## What is taken from Р12 and what is new

Taken: the whole idea and its code — the 3D is never shown as such; each frame the figure is rendered unseen into
"which wash, how far", silhouettes and open edges are found on the mesh, chained, broken into strokes and drawn with
`kit.py`'s pen ported to JavaScript (`tools/web/pen.js`); the washes are the seen parts as masks under `kit.py`'s
watercolour filter, moved off the line; the face is drawn with `parts.py`'s eye, brow and mouth on a grid laid on the
head; the live face (`face.js`), the viewer (`ui.js`), the shots.

New here:
- **The renderer takes any character of the style.** Р12's `anya.js` is split: `figure.js` (the renderer) and
  `char.js` (what is the character's own: washes and colours, the face as `head_front` draws it, its sheet's
  expressions, which wash a point is where the mesh doesn't say). Р36 (Марат) uses the same `figure.js`.
- **The body is built for the drawing, not borrowed.** Р12 re-ran Р1's Аня. Here `tools/build.py` builds Тим in one
  go: Anny's child (`engine/data/bodies/moood-child`) re-proportioned by joints (`J1`) and a per-joint affine map that
  turns and stretches each limb's bone and thins it — hips low (short legs under long shorts), a short trunk, narrow
  shoulders, short arms, thin legs straight down; of Anny's skin only knees, shins and feet are seen (the feet
  smoothed into sneakers). The jumper, the sleeves, the shorts (the hips' shell and a wide leg each) and the mittens
  are shells of the drawing's sizes (`shells.py`), skinned by the fitted body's nearest weights.
- **Hair as form: spikes.** The drawing's hair is a wash with an outline of tufts. Here it is a dome over the skull
  (an icosphere cut along the drawing's hairline — across the forehead, level along the side, down behind the ear to
  the nape; the edge toothed — tufts over the forehead) with 48 cones of uneven height leaning back. Its silhouette
  is then tufts from any side and stays put when he turns; the pen keeps the points (no smoothing of the chain, no
  lifting at corners — `sharp` in `char.js`). Silhouettes of spikes over the hair itself are thin strokes, every second.
- **Stripes.** The jumper's stripes are a coordinate down the body and along the sleeves (`stripe`); the unseen
  picture puts stripe pixels in their own wash group; the pale wash covers the whole jumper, the strong one the
  stripes — as `tim.py` paints them. Socks (paper), their red band and the sneakers are cut by the legs' rest height.
- **Ears.** Р12 hid the ears under the hair; his stick out (the base's ears kept, moved to the middle of the head's
  side and turned outward), and the pen draws them as contours.
- **A part's silhouette over itself** is now decided per vertex (`inner`: 0 no — the face's folds; 1 yes; 2 thin —
  hair), by looking at the wash on both sides of the edge.
- **The far eye and the mouth on a turned face** are moved in the picture toward the near cheek and the far eye made
  smaller, as `head34` draws them (in Р12 the far eye could stand on the contour and an open mouth stick out of the
  profile).
- **Poses** (`standPose`): the trunk's lean, the arms and legs by directions — the drawing's figure (leaning forward,
  hands behind the back) is such a pose.

## How the form is built (what each base gave)

- **Body and skeleton — Anny `moood-child`** (engine): SOMA's 77 joints and the skin's weights. Height 1.25 m; head
  units of the drawing → metres: 1.36 mm a unit (figure: 0.66 px a unit).
- **Head — Blender Human Base Meshes stylised head** (CC0), fitted by `head.py` (Р12's, numbers from `drawing.py`) to
  `head_front` and `head_side`: heights by landmarks (neck's end, chin, eye line, crown), then each height's width and
  front/back. Eyes and mouth laid flat (they are drawn); the base's nose laid flat and the drawing's upturned button
  put on (profile from `head_side`, width from `head_front`).
- **Clothes** — shells from the drawing's sizes; **hair** — the dome with spikes.
- `head.py`'s push of the cheeks forward follows the face's front without the nose (`NOSE_SPAN`; found on Марат, whose
  big nose it swallowed).
- Neural models were not used.

## Repeat

```
cd to3d/r35-s12-tim/tools
/home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
  --python hbm_export.py -- /home/user/cache/to3d-r35-s12-tim/hbm_head.npz        # the base head as arrays (once)
(cd /home/user/cache/to3d-r35-s12-tim && npm install three@0.160.0)                # three.js for the headless shots
python3 build.py                # → ../data/tim.json, tim.bin
python3 make_pics.py stills     # ../pics: compare, overlays, steps, back, expressions
python3 make_pics.py films      # ../pics: turn, walk, sneak, jump, talk (12 drawings a second)
```
`shots.mjs` serves `/home/user/` and drives `web/view.html?pack=…` with Playwright (software WebGL). A drawing takes
2–6 s there. By hand: serve the repository root, open `to3d/r35-s12-tim/tools/web/view.html`.

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`; Kimodo's SOMA skin Apache-2.0).
- Kimodo motions: `engine/motions` (walk, sneak, jump, idle).
- Р12's renderer and the С12 drawing and its code (`kit.py`, `parts.py`, `tim.py`, ported): this repository.

## Honest state

- Reads as the drawing's Тим: the round head on a thin body, the tufty ginger hair, ears, freckles, the lopsided grin
  with the gap tooth, the striped jumper. Stands beside Р12's Аня as the same book.
- The hair's line is thinner and more broken than the drawing's bold zigzag, and at the size of the whole figure the
  spikes read partly as a ragged mop; the drawing's tufts are bigger and fewer.
- The drawn front and profile don't make one head at the hairline and the ear (as `docs/findings.md` says); the front
  is followed. The neck is longer and thinner than drawn.
- The profile's nose is a small point, less of a button than drawn; the jaw is narrower than the drawing's round face.
- Mittens, not hands; the figure's jam jar is not made. Shorts and jumper are skinned shells: in a wide step the
  shorts' legs stretch.
- As in Р12: the line follows the form exactly (a hand would simplify), the washes follow the seen shape and are only
  shifted; in films the line "boils" from drawing to drawing and the pigment stays on the screen, not on the body.
