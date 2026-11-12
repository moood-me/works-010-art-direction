# Р51 — Кира, советская мультипликация: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, third round; brief: `docs/briefs/to3d.md`): Кира of style
С20 (`styles/s20-soviet`: Khitruk / Zuykov people of Soyuzmultfilm's 60–70s) made a 3D character that moves by Kimodo
through the engine and is drawn every frame with that style's own pen and paint. The first 3D character of this style;
the way of making the look is Р12's (`to3d/r12-s12-anya`: a look drawn each frame from the 3D by the style's code).

## The idea

The style: one bold caricature shape for the body and one for the head, the face left as paper, a big nose over the
contour, ring eyes by the nose, a pen line with pressure and wobble, paint laid off register. So:

1. **The form is the drawing's own numbers, not a human body.** `styles/s20-soviet/tools/kira.py` writes the hoodie as
   a front and a side silhouette, the head as half-widths at a few heights plus a profile line, hair as masses, legs and
   sleeves as tubes, boots as an outline. `tools/build.py` lofts exactly those into shells (in the drawing's units, feet
   at 0; 428 units = 1.60 m): the hoodie — one bag (superellipse sections, the front width and the side depth of the
   drawing, the slouch as `kira.py` bends it); the head — sections of the front rows deep as the profile's face line,
   the chin a point at the front; the hair — one shell whose lower edge is the drawing's choppy fringe (long over her
   right temple), up over the ears, locks behind them; ears, a neck, a hood lump, sleeves, mitten hands, thin legs,
   heavy boots, lime headphone cups. No Anny body, no Human Base Meshes head: a human body is not this style.
2. **The skeleton is SOMA's** (77 joints) with moood-woman's rest frames (`engine/data/bodies/moood-woman`). That rest
   (arms out, legs apart) is posed into the drawing's stand — arms hanging, legs straight — and baked as this body's
   rest: each posed joint's frame is turned with its bone, so Kimodo's turns mean the same. The slouch (top forward and
   down, head forward, nose down by 5.6°) is in the joints' places and the form only, not in the frames — so it rides
   along in every motion (`engine/src/retarget.js`: places are the designed rest, frames the reference).
   Weights by rule: the bag by height on Hips–Spine1–Spine2–Chest, sleeves and legs along their bones, the rest rigid
   (head, hair, ears on Head; boots on Foot with the toe on ToeBase). Dual-quaternion skinning.
3. **The 3D is never shown as such.** Each frame (`tools/web/kira.js`):
   - the figure is rendered once into an unseen buffer: which paint a pixel belongs to, whether it is on the shaded
     side, its depth;
   - **paint**: each colour's seen pixels make a mask picture, laid shifted up-right from the line (`kit.py` `OFF()`:
     2.6·S^0.45 px, −0.7 of it down) under the `brush` filter (displaced edge, gouache streaks); face, neck and hands
     are the paper colour, flat; pencil hatching (`kit.py` `hatch`) clipped to the hoodie's shaded side;
   - **line**: every mesh edge is tested — a silhouette (its two triangles face opposite ways) or an open edge (the
     hair's edge, a cuff) —, kept where the buffer says it is seen, chained, smoothed, broken at sharp corners, and
     drawn by `ink()` — `kit.py`'s pen ported line by line (`tools/web/kit.js`): a filled outline, thin ends, a wobble
     of three sines, heavier where the contour looks down-right (the contour knows its outside from the 3D's normals);
   - **face**: `face.py`'s parts in head units (ring eye with the lid's line, brows, mouth kinds, crayon blush), each
     in its own frame on the turned head (a grid of head points found by rays from the front, skinned and projected
     every frame). As the head turns, the near eye, brow and cheek go round to the side we see (the drawing's profile
     puts the eye 13 units behind the face line), the far eye gets smaller and goes; the mouth moves toward the seen
     cheek. The nose is a sign drawn upright at the face's middle, the same size from any side, changing from the
     front drawing's hook to the three-quarter's wedge as the face turns, with a patch of paper under it so that it
     lies over the contour;
   - **lines of the form**: the pocket, the hood's strings, lime laces, the headphones' band, the ear's mark, finger
     lines, a light line in the hair — points on the shells, drawn where seen;
   - one bright field behind, a crayon strip under the feet, paper grain over all (the drawing's `Doc`).
   Films are drawn 12 times a second, each drawing held for two frames of 24.

Neural models were not used.

## Live

- **Face** (`tools/web/face.js`): Р1's timing through Р12 (blinks with log-normal intervals, fast close / slow open;
  saccades; the gaze leading head turns; speech as syllables of mouth shapes through a damped spring; expressions
  mixed and changing as damped springs) driving С20's numbers: brow height and tilt, the lid's line across the ring,
  the pupil's look, the round eye of surprise, the mouth's kind, curve and opening. Кира's own expressions from
  `kira.py`: calm is a look from under the lids and sideways with a crooked smirk, joy is the same smirk.
- **Motions**: Kimodo's from `engine/motions` through the engine (retarget, skin, floor).
- **Viewer** `tools/web/view.html` (`ui.js`): drag to turn, wheel nearer, motion, play/pause, scrub, the five
  expressions and their mix, talk, face close.

## Repeat

```
cd to3d/r51-s20-kira/tools
python3 build.py                # → ../data/kira.json/.bin
python3 make_pics.py stills     # ../pics: compare, overlays, steps, back, expressions
python3 make_pics.py films      # ../pics: turn, walk, sneak, talk (12 drawings a second)
```
`shots.mjs` serves `/home/user/` and drives `web/view.html?pack=…` with Playwright (software WebGL; three.js routed to
`/home/user/cache/n3-cloth/node_modules`); a drawing takes about 2 s. By hand: serve the repository root, open
`to3d/r51-s20-kira/tools/web/view.html`. Scratch: `/home/user/cache/to3d-r51-s20-kira/`.

To make another character of С20 this way: write its shells in `build.py` from its module's numbers (the bag's three
outlines, `ROWS` and the profile's face line, the hair's edge table, the tubes), its colours in `kira.js` `PAINT`, its
head numbers in `HEADP` and expressions in `face.js` `EXPR`; `kit.js` already has the noses and mouths Кира needs —
other noses (`potato`, `long`) and the `happy` eye are still to port from `face.py`.

## Licences of the bases

- SOMA skeleton and moood-woman's rest frames: as in `engine/` (`engine/data/soma/NOTICE`; Kimodo's SOMA skin Apache-2.0).
- Kimodo motions: `engine/motions`.
- The С20 drawing and its code (`kit.py`, `face.py`, `kira.py`, ported), Р12's renderer and Р1's live face: this repository.

## Honest state

- Reads as the drawing: the same girl on the same field, the bag of a hoodie, thin legs and heavy boots, paper face,
  the nose over the contour, lidded ring eyes looking sideways, the pen line and the paint past it. Front and
  three-quarter lie close on the drawing; the sheet's four expressions match it almost line for line.
- Where the drawing lies and what was followed: the front has no slouch and the side has — the 3D always slouches
  (0.7), so in front the head sits 8 units lower and hides the neck; the profile draws the short fringe, but the long
  lock hangs over her right temple (front and three-quarter), so in the right profile it hangs before the brow and the
  eye is drawn at its edge; the locks behind the ears follow the front and three-quarter, not the profile; the
  drawing's "three quarters" is a turn of about 25–30°.
- Weaker than the drawing: the line follows the form exactly — a hand would exaggerate; the hair's and the bag's lines
  are tidier than the drawing's. The stand is straighter than the drawn one. In the figure's gesture the hands meet in
  front of the chest instead of being tucked under the arms (mitten hands on straight forearms), the legs cross less.
  Gouache streaks stay on the screen, not on the body.
- Motion: the hoodie is a skinned bag, not cloth — in a wide step its hem stretches a little with the hips; sleeves
  pass through the bag's sides when an arm swings back; `idle` and `stomp` bow the head and trunk (Kimodo's) on top of the slouch, so the
  chin sinks into the hood and in `stomp` a hand goes through the head — not filmed; the talk film stands still. Hair is rigid.
- From behind there is no drawing: the back is the same shells.
