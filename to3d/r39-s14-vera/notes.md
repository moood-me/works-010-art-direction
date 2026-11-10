# Р39 — Вера, вырезанная бумага (С14 → 3D)

What was done, why, how to repeat. Brief: `docs/briefs/to3d.md`, "Third round". Asked for by Pavel through the
orchestrator: each style gets two characters in 3D; С14 is a new style with none in 3D yet, so this is the first try
of how cut paper lives in 3D. Done by one agent (Claude) together with Р40 (Кира, `to3d/r40-s14-kira`). The second
character was changed twice by Pavel through the orchestrator while this one was being made (Марат → Аня → Кира).

## The idea

In С14 every visible thing is a piece of paper: a closed edge, one colour, a height above the sheet; no line, no
shading inside; depth is layers and their shadows; limbs are strips pinned with brads like Norstein's cut-out puppets.
So in 3D the character is a **cut-out puppet standing in space**:

- each piece of the drawing is a mesh with one colour and its own number — a shell (coat, head, hair), a stiff strip
  on one bone (sleeves, legs), a flat sheet (hand, papers, glasses), or an outline glued on a shell's surface
  (face pieces, placket, buttons, the scarf's end);
- nothing is lit. The picture of "which piece, how far" is turned into paper in one pass (`web/look.js`), which does
  to every piece what `kit.py`'s SVG filters do in the drawing: a crisp contact shadow, a soft cast shadow down-right
  on whatever is further from the eye (three lengths by the gap: > 0.4 mm, > 12 mm, > 70 mm — the drawing's lifts
  1–3), a light rim on the lit edge, brush streaks tied to the piece (they travel with it), the sheet's grain. The
  light is fixed top-left on the picture, as on the drawing's sheets;
- Anny's body and an artist's head base (the brief's points 1–2) are not used: inside a piece there is nothing in
  this style, only its edge from every side matters — the way Р8/Р23 did for the symbolic style. The skeleton is
  SOMA's 77 joints set by the drawing's sizes, frames SOMA's own, so the engine's retargeting carries Kimodo as it is.

Earlier pages read first: Р12/Р35 (a look made each frame from the 3D), Р1/Р3/Р29 (flat styles, the drawing's
filter), Р23 (the drawing's own solids on SOMA, no Anny).

## Files

| File | What |
|---|---|
| `tools/web/paper.js` | the kit: `kit.py`'s outlines (ell, strip, crescent, the closed curve with corners) and 3D makers — `patch` (an outline laid on a surface), `loft`, `tube`, `slab`, `clip` (scissors: a shell cut along a function) |
| `tools/web/look.js` | the look: pieces drawn flat with their number and distance; the paper pass (shadows, rim, grain) |
| `tools/web/face.js` | `face.py` carried over: spec, expressions, eye / lid / lashes / brow / mouth pieces; the head as an egg with a jaw (front outline = `outline(yaw=0)`, depth = the profile outline); pieces glued on it; the nose as a folded wedge |
| `tools/web/body.js` | `body.py` carried over: SOMA joints by sizes (`proportion`), strips, brads, the hand with snips, shoes, trunk shells with pieces on them, the torn ground |
| `tools/web/figure.js` | the puppet on the skeleton (engine: `makeRetarget`, `build`), the held arm, `Life`: blinks, glances, the head after the gaze, speech, expressions |
| `tools/web/vera.js` | **her own**: `vera.py`'s numbers — sizes, coat, scarf, papers, hair, bun, glasses, the stand |
| `tools/web/app.js`, `view.html` | the page and the viewer; `window.A` for pictures and films (`?shots`) |
| `tools/character.py`, `drawing.py`, `make.py`, `shots.mjs`, `svg2png.mjs`, `heavy.sh`, `view_check.mjs` | the drawing's views by the style's code; pictures and films through the page; the shared locks |

To add a character of this style: copy `vera.js` and `character.py`, write its pieces, point `web/char.js` at it.

## Repeat

```
(cd /home/user/cache/to3d-r39-s14-vera && npm install three@0.160.0)   # three.js for the headless page
cd to3d/r39-s14-vera/tools
./heavy.sh python3 drawing.py           # the drawing's views → cache/drawing
python3 make.py compare steps expr hero # pics/*.jpg
python3 make.py films                   # turn, walk, life, bow → pics/*.mp4 (12 drawings a second)
./heavy.sh node view_check.mjs /tmp/v.png   # the viewer opened and pressed
```
A picture takes about a second in software WebGL; a film 1–2 minutes. By hand: serve the repository root, open
`to3d/r39-s14-vera/tools/web/view.html`.

## Decisions along the way

- Face pieces first cut into the head near its edge (the cheek goes round the egg): pieces now stop at 93 % of the
  head's half-width and are lifted along the surface normal; the head shell is dense (96 × 72).
- Near the camera shadows grew with the picture and looked like thick card: beyond 1.4 px a unit they grow at 0.4 of
  the picture's rate (the drawing's portrait also keeps the figure's shadow sizes).
- Brush streaks are in the piece's own coordinates (along the ring and down the shell), not the picture's.
- The coat follows the thighs up to 94 % below the hips and the shins by half at the hem — less than that and the
  knee came through in a stride.
- Kimodo's `idle` was left out (it stoops); `wave` is with the right hand, which holds the papers.
- 12 drawings a second in the films: cut-out animation is shot so, and it suits the stiff strips.

## Bases and licences

| What | Where | Licence |
|---|---|---|
| The drawing and its code (kit.py, face.py, body.py, vera.py) | `styles/s14-paper` | ours |
| SOMA skeleton | `engine/data/skeleton.json` (NVIDIA; `engine/data/soma/NOTICE`) | Apache-2.0 |
| Kimodo motions walk, bow | `engine/motions` (copied to `tools/web/data/motions`) | as the engine's motions |
| three.js 0.160 | jsDelivr | MIT |

No neural images, no third-party meshes.

## What is weak

- The profile: the eye lies on the egg's front and from the side is almost hidden, glasses are edge-on; the style has
  no drawn profile of Вера to follow.
- Shoes: the drawing turns them sideways under a frontal body; in 3D they point forward (toes out 26°) and are small
  from the front. A hand is a sheet: a line from its edge.
- Torn edges with the white core exist only on the ground piece; fold shades of the coat are not made.
- The coat is a skinned shell: in a wide step it flares like a skirt, the knee can still show through for a frame.
- The light does not go round the figure in a turn (fixed on the picture, by design).
- The viewer is slow in software WebGL (about 6 frames a second there); on a graphics card it is light.
