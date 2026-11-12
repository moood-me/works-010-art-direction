# Р49 — Вера, Билибин (style С17) in 3D

What was done, why, how to repeat, the bases' licences. Brief: `docs/briefs/to3d.md` (with its second round). Done by
one agent (Claude); the orchestrator commits. First try of this style in 3D.

## The idea

The С17 drawing (`styles/s17-bilibin/tools`: `kit.py` the line and ornament, `parts.py` a head as numbers, `vera.py`
the character) is flat by rule: an even ink contour of one weight, flat fills without light, patterned cloth, a face
of a few lines. So in 3D nothing is lit. The 3D gives three things only — the silhouette, which piece is in front of
which, and where the cloth's surface is — and the picture is made from them by the style's rules:

1. **Flat paint.** Every piece (skin, dress, shawl, hair …) gets the drawing's own hex colour; no shading at all.
2. **The contour from the 3D.** The figure is drawn a second time into a hidden picture twice the screen's size:
   the piece's number and the depth under every pixel. A pixel is inked where, within the line's radius, the piece
   changes (figure against paper, hair against skin, shawl against dress, ear against head) or — inside one piece —
   the depth has a break (an arm in front of the dress, finger over finger). The line's weight on the page is
   `kit.py`'s rule: `3.2 · s^0.25` pixels, `s` the pixels per head unit — one weight for every outline, a little heavier
   when the figure is drawn large. The head's own surface gives no inner lines (the features are drawn).
3. **Ornament on the cloth.** The shawl's roses are not a screen pattern and not a UV tile: each rose has a place on
   the shawl's surface at rest and its own frame there (centre, two tangent directions, radius; `build.py` scatters
   34 big and 16 small ones as `vera.shawl_pattern`'s tile has them — a red disc, three broken darker rings, two
   leaves); the shader paints a pixel by its rest position against the roses near it. So the print bends and
   travels with the cloth. The border of teeth runs along the shawl's cut edge (its distance from the edge and the
   length along it are stored on the shell), the hem's band of teeth round the skirt; the hair's strands (by the
   angle round the axis forehead → knot), the grey lock, the knot's coils, the skirt's folds and the folder's gold
   band are thin lines and shapes in the cloth's own coordinates, of an even weight on the screen.
4. **The face is drawn, not modelled** (`web/face.js`): a port of `kit.py`'s curve/line/lock and `parts.py`'s
   `_eye`, `_brow`, `_nose`, `_mouth`, the blush and laugh lines, and `vera.py`'s glasses, from Python/SVG to a 2D
   canvas. Each frame the viewer finds where the head is on the picture (origin, roll, scale, and its yaw against
   the eye), and the same drawing code that makes the style's turnarounds draws the face there — with the style's
   own rules for a turned head (an eye narrows by `0.25 + 0.75·facing` but stays an almond, the far lens of the
   glasses stands out past the cheek, the nose is a line in front and a contour in three-quarter; the two are
   cross-faded between 5° and 13°). Points are put through the real head's transform, so the face follows any tilt.
   When she faces right the drawing is mirrored, as the style does (`flip`). The face is laid only over pixels of
   the head's skin (a hand or the hair in front covers it); the glasses over everything but hands, sleeves and folder.

## What each base gave

- **Body and skeleton — Anny `moood-woman`** (engine/data) with SOMA joints and weights, scaled to 1.67 m (the
  drawing's 1354 + 112 head units at 1.14 mm) × 1.03, made narrower toward the drawing (`build.py`: chest ×0.79,
  shoulders in by 3.6 cm, arms ×0.84, legs turned in 7° under the narrow skirt; after Р7's way: joints moved, vertices
  follow by Anny's weights, joint frames untouched — Kimodo retargets as for any engine body). Hips and thighs under
  the skirt are cut away.
- **Head, neck, ears — the drawing's own volume.** `parts.P` gives the head as cross-section half-widths `a(y)`, the
  face surface `zs(x, y)` with the nose and lips, the back `bb(y)`; `drawing.py` samples it as a grid (120 rows ×
  200 columns, denser at the nose). The same numbers draw the SVG head at any yaw, so the 3D silhouette is the
  drawing's by construction (the overlays show it). The Human Base Meshes head was **not** used: with flat paint and
  a drawn face the head gives only its silhouette, and a fitted artists' head would add lids, lips and nostrils that
  the contour pass would then have to be told to ignore. The price: this head can't be shown under light.
- **Hair** — the head's surface grown by 7.5 units above the drawing's hairline (`vera.hl()` keys + `shell`'s side
  and back heights), cut per pixel at the hairline; the knot — an ellipsoid at `vera.knot`'s place, its own piece
  (so it gets its contour, as drawn).
- **Dress** — Anny's body pushed out 5 mm (sleeves to the wrist, the round neckline cut per pixel) and a long skirt
  lofted from the waist to the hem (y 1290 → 7 cm above the floor; 97 × 44, soft folds).
- **Shawl** — a shell 11 mm over the dress on the shoulders, upper arms (to the elbow) and trunk, with Anny's
  weights; its V at the neck, its lower edge (higher in front, lower behind) and the sleeve edge are margins stored
  per vertex and cut per pixel.
- **Shoes** — Р7's lofted shoes. **Folder** — a box in the left hand's frame (set from the standing pose).
- **Motions** — Kimodo's from `engine/motions` (walk, wave, idle) through the engine as it is (`createEngine`,
  `Figure`, retarget; dual-quaternion skinning — centres of rotation take too long to prepare on 58k vertices).

## Standing as drawn

`standPose` (after Р7): arms let down by a two-bone reach; then both wrists put on the folder's front, each hand
turned flat on it (fingers along the folder, the back of the hand outward), the head turned and tilted as in the
figure sheet. For the turnaround sheets the trunk is turned 0.6 of the angle and the head the rest — as
`vera.bust` does.

## The skirt in motion (not cloth)

After skinning (`pushSkirt`): every skirt point moves outward from the body's axis until no leg lies beyond it (the
legs as rows of balls hip → knee → ankle → toe, and a heel); then each ring of the skirt is pulled taut round what it
holds — its convex outline — so the cloth spans from leg to leg instead of wrapping each leg like trousers.

## Live (after Р2/Р7's `life.js`)

Blinks at log-normal intervals (~2.8 s, never closer than 0.8 s; 75 ms shut, 25 ms held, 170 ms open; one with a big
gaze shift), fixations of 0.3–1.6 s with quick jumps, the gaze jumping ahead of a head turn read 0.22 s ahead from
the clip, speech as syllables (a consonant shape, then a vowel) through a fast damped spring, expressions through a
slower one; seeded, so a moment always looks the same and scrubbing works. Here the track is of the drawing's own
numbers (`face.js` `PARAMS`: brow, tilt, open, smile, mouth, wide, round, teeth, cheeks, look, blink, jaw, pucker).
A blink lays the lid line down on the lower line; laughter shuts the eye in an arc up (the drawing's).

## Repeat

```
cd to3d/r49-s17-vera/tools;  C=/home/user/cache/to3d-r49-s17-vera
python3 build.py $C && cp $C/out/vera.json $C/out/vera.bin web/data/
L="flock /home/user/cache/heavy.$((RANDOM % 3)).lock"
NODE_PATH=/opt/node-tools/node_modules $L node shots.mjs jobs/jstill.json $C/st      # stills in the drawing's frames
NODE_PATH=/opt/node-tools/node_modules $L node shots.mjs jobs/jfilm.json $C/fm       # film frames (~1–2 s each, software WebGL)
python3 make_pics.py stills $C/st;  python3 make_pics.py films $C/fm                # → ../pics
```
`shots.mjs` (Playwright + SwiftShader) serves `/home/user/`, opens `web/view.html?shots=1`, routes three.js 0.160 to
`/home/user/cache/n3-cloth/node_modules/three`, and calls `window.A.set({...})` per shot. By hand: serve the
repository root and open `to3d/r49-s17-vera/tools/web/view.html`.

Files: `drawing.py` (the drawing's numbers), `build.py` (the pack), `pack.py`, `mesh.py` (Р7's helpers),
`web/vera.js` (the look, poses, skirt, the face's place), `web/face.js` (the drawn face), `web/life.js`, `web/ui.js`,
`web/view.html`, `web/data/` (the pack), `compare.py`, `make_pics.py`, `jobs/`.

## What is weak (seen by eye)

- The body: Anny's shoulders are wider and lower and her neck longer than the drawn ones, the waist higher; the
  overlays of the bust and the figure differ there though the body was narrowed. The drawing's figure is 7.2 heads
  with shoulders 1.4 heads wide.
- The shawl is a fitted shell to the elbows, not a hanging cloth (the figure sheet's shawl hangs to the hips; the
  bust sheet's lies on the shoulders — the two sheets differ, the bust was followed).
- The skirt is not cloth: no swing; in a wide step the hem stretches, and a heel lifted behind can show through it.
  Kimodo's `bow` and `sit` break it — left out.
- Hands are Anny's realistic hands; in flat paint with a contour they are rougher than the drawn ones.
- The contour follows the form exactly; a hand would simplify. It is made of pixels (averaged 2 × 2), not strokes.
- Under the jaw the drawing's head is a flat-backed mask (as its profile draws it); seen from below it would show.
- The page's frame, landscape and halo are the sheet's, not the character's: films use a flat meadow with flowers.
- `idle` stoops (the motion's own). The folder in motions rides in the left hand.

## Licences

- Anny body (`moood-woman`), SOMA skeleton and weights: as in `engine/data` (`engine/data/soma/NOTICE`).
- Kimodo motions: `engine/motions` (moood studio).
- The drawing and its code (`styles/s17-bilibin`), Р2/Р7's code reused here: ours. three.js 0.160 (MIT).
- No Human Base Meshes, no neural images, no StdGEN.
