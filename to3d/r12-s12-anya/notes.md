# Р12 — Аня, перо и акварель: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, second round; brief: `/home/user/cache/BRIEF-to3d.md`):
Аня of style С12 (`styles/s12-ink-watercolour`, Quentin Blake / Sempé pen and watercolour) made a 3D character that
moves by Kimodo through the engine, and drawn every frame with that style's own pen and wash code — not a shader filter.

## The idea

The hardest look for 3D: a loose pen line and washes that don't fill the line. A toon shader with an outline gives a
"cel" look, not a pen. So the 3D is never shown as such. Each frame:

1. **The unseen picture.** The figure is rendered once into an off-screen buffer: which wash each pixel belongs to
   (skin, hair, cardigan, dress, shoes; plus "in shade" for the hair's darker wash) and its depth (16 bit).
2. **Lines from the form.** On the CPU every mesh edge is tested: a silhouette (its two triangles face opposite ways
   to the camera) or an open edge (a hem, the cardigan's front, the hair round the face). Kept where the buffer says
   it is seen (some pixel round it is not in front of it). On the face, a silhouette is kept only where skin meets
   something else (hair, paper) — the base mesh's lip and nostril folds are not lines of this drawing — except the
   nose. Kept edges are chained into polylines, smoothed (the zig-zag of mesh silhouettes goes), broken where they
   turn sharply, and cut into strokes of 110–260 px with small gaps or overlaps — as a hand lifts the pen. Each stroke
   is drawn by `ink()` — `kit.py`'s pen ported line by line to JavaScript (`tools/web/pen.js`): pressure, taper,
   wobble, tremor, the dip pen's second pass, the nib filter. A line on the figure's outside is a little heavier.
3. **Washes.** Each group's pixels make a mask picture; it is painted with `kit.py`'s own watercolour filter
   (displaced edge, streaky pigment, darker dried rim, grain) as an SVG `<image>`, moved a few pixels off the line
   (each group its own way, as in `anya.py`: dx, dy). So the wash comes out past the line on one side and short of it
   on the other. Colours and opacities are `anya.py`'s. The hair gets a second, darker wash on its shaded side.
4. **The face is drawn, not modelled.** `parts.py`'s `eye`, `brow`, `mouth`, `extra`, the freckles and cheeks are
   drawn in С12's `head_front` units, laid on the 3D head through a grid (build.py: each grid node is a point on a head
   triangle, found by casting rays from the front; every frame it is skinned and projected). Each feature is drawn in
   its own frame there: the vertical as the head carries it, the horizontal foreshortened as the head turns but never
   below 0.62–0.7 of it — a turned eye stays an eye (as the drawing's `head_side` draws it), not a sliver — and moved
   toward the seen cheek as the face turns, so the mouth's near corner stays inside the profile (the drawing's own
   rule). The nose is the 3D's own contour in three-quarter and profile; in front, where a contour gives nothing, the
   front drawing's nose stroke is drawn, fading out as the head turns.
5. **Lines that belong to the form**: a few locks down the hair (columns of the hair's grid), the skirt's folds,
   two buttons — drawn where seen.

The whole picture is one SVG (`kit.py`'s layers: paper, washes multiplied, whites, ink multiplied), put in the page;
the WebGL canvas stays hidden. Films are drawn 12 times a second and each drawing held for two frames of 24 — as
hand-drawn films are; the pen's tremor then "boils" a little from drawing to drawing, which reads as drawn.

## How the form is built (what each base gave)

- **Р1's Аня** (`to3d/r1-s3-anya`: the same girl in the same clothes in another style). Its build (`tools/form.py` =
  Р1's `build.py`, with `head.py`, `hair.py`, `drawing.py`, `faces.py` copied) is re-run with С12's shapes:
  - **body and skeleton — Anny `moood-woman`** from `engine/data` with its SOMA joints and weights (Р1's joint moves,
    kept: hands, shins, feet; mittens; smoothed feet as shoes);
  - **head — Blender Human Base Meshes stylised head** (CC0), fitted (`head.py`) to С12's `head_front` and `head_side`
    outlines (`drawing.py`, bottom: × 1.03, eye line on 0), including the skull's top (Р1's front outline stopped at
    the brow, which pinched the skull to the neck's width above it — covered by hair there, not here); eyeballs
    removed (the eye is drawn); the base's nose (nostrils, wings) laid flat and a small sharp wedge put on instead,
    its profile the drawing's, about ±9 units wide — the drawing's nose is the face's main mark and is drawn by the
    pen as a contour;
  - **hair — Р1's shell** (`hair.py`) from С12's hair: the front mass, the curtain round the face (forehead under a
    middle parting), the profile mass; longer (to 270), a rounder crown, softer pointed ends, the curtains' front edge
    set back at the cheek (the profile shows the whole cheek, the hair behind it), loose waves (build.py);
  - **clothes** — Р1's dress (shorter: to mid-calf, as drawn), cardigan (С12's V from the neck to below the shoulders,
    buttoned to the waist, a little open below), sleeves; the white collar removed.
- **`tools/build.py`** turns that pack into this character's (`data/anya.json/.bin`): wash groups, the edge list,
  where inner lines are allowed, the face grid, the form's strokes.

Neural models were not used; StdGEN's results were not needed.

## Live

- **Face** (`tools/web/face.js`): Р1's timing (blinks with log-normal intervals and fast-close / slow-open; saccades;
  gaze leading head turns, with a blink on big ones; speech as syllables of mouth shapes through a damped spring;
  expressions mixed and changing as damped springs, brows ahead) driving С12's numbers: brows' lift and tilt, lid,
  look, eye size, mouth kind, the head's tilt with the feeling, the marks (tear, start-lines, flush). For speech the
  mouth is a small dark-red wash in a pen outline opening and rounding (a `talk` mouth added to `pen.js` in
  `parts.py`'s manner). Mixed expressions mix their numbers; the mouth kind is the strongest expression's.
- **Motions**: Kimodo's from `engine/motions` through the engine's retargeting and skinning (Р1's frame code: the
  skirt pushed off the legs, on the floor as the engine's Figure).
- **Viewer** `tools/web/view.html` (`ui.js`): drag to turn, wheel nearer, motion, play/pause, scrub, the five
  expressions and their mix, talk, face close; it draws 12 times a second. With a GPU the 3D part takes milliseconds;
  the SVG filters are the cost.

## Repeat

```
cd to3d/r12-s12-anya/tools
# Р1's head bundle export (once): see to3d/r1-s3-anya/notes.md (hbm_export.py → /home/user/cache/to3d-r1-s3-anya/hbm_head.npz)
python3 form.py                 # → /home/user/cache/to3d-r12-s12-anya/form/anya.json (Р1's build with С12's shapes)
python3 build.py                # → ../data/anya.json/.bin
python3 make_pics.py stills     # ../pics: compare, overlays, steps, back, expressions
python3 make_pics.py films      # ../pics: turn, walk, talk, wave (12 drawings a second)
```
`shots.mjs` serves `/home/user/` and drives `web/view.html?pack=…` with Playwright (software WebGL; three.js routed to
`/home/user/cache/n3-cloth/node_modules`). In software rendering a drawing takes 4–15 s (the off-screen render and its
read-back are most of it). By hand: serve the repository root, open `to3d/r12-s12-anya/tools/web/view.html`.

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`; Kimodo's SOMA skin Apache-2.0).
- Kimodo motions: `engine/motions`.
- Р1's build code and the С12 drawing and its code (`kit.py`, `parts.py`, `anya.py`, ported): this repository.

## Honest state

- Close to the drawing in spirit: on white paper it reads as a picture-book drawing — a living, broken pen line, loose
  washes off the line, the drawing's own eyes, brows, mouths, freckles and cheeks. It is not a filter over a render.
- But it is cleaner and more "traced" than Blake: the contours follow the form exactly (a hand would simplify and
  exaggerate), and their tremor is the only looseness. The washes follow the seen shape of each part exactly and are
  then shifted — the drawing's washes are simpler blobs than the true silhouette.
- The wash's pigment streaks are in the picture's space; in films the paper and pigment do not travel with the body
  (the viewer can anchor them to the hips; for the films the camera follows her, so it shows little). The pen line
  "boils" a little from drawing to drawing.
- Hair is a smooth shell: from the front it hangs as a broad sheet beside the face (the drawing's thin locks), its
  ends are cut in soft points; it is rigid (no inertia).
- Under the jaw, where the hair's open edge meets the neck, the pen draws a few short strokes like stubble; a small
  squiggle for the ear shows through the hair in three-quarter.
- Feet: Anny's smoothed feet as shoes; in a step the toes' shape shows in the line.
- The figure's flowers are drawn at the hand (not modelled), only in the still picture compared with the drawing.
- Skirt: skinned and pushed off the legs (Р1's), not cloth.
