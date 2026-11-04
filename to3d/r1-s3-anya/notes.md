# Р1 — Аня, графичный стиль: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run; brief: `/home/user/cache/BRIEF-to3d.md`): Аня of style С3
(`styles/s3-graphic`) built in 3D from ready bases fitted to the drawing, not by a neural net, and played by Kimodo's
walk through the engine.

## How it is built (and what each base gave)

- **Head — Blender Human Base Meshes, stylised head** (`GEO-head_stylized` and its eyes; `tools/hbm_export.py` takes
  them out of the bundle as arrays). It gave the skull, jaw, nose, neck and ears with clean topology.
  `tools/head.py` fits it: heights piecewise by landmarks (neck end, chin, eye line, crown → drawing y 262, 112, 0,
  −126); then at each height the width is scaled to the front drawing's face (`FACE_F`, the neck as drawn below the
  chin) and the depth mapped to the profile's front and back (`FACE_S`; the nape interpolated); the lower face is
  brought forward toward an arc through the lips (the drawing's face is one round plane, the base has a muzzle); ears
  made smaller (hidden under the hair). The eye sockets, eyeballs and the mouth's crease are laid onto one smooth
  surface (`flatten`: a quadratic fitted to the face around each region) — the folded geometry there is invisible
  because its colour comes from the painted layer, its shade from smoothed normals and the outline is off there.
- **Face — the drawing's own SVG parts** (`tools/faces.py` uses `styles/s3-graphic/tools/face.py`'s `eye`, `brow`,
  `closed_eye`, `shout`), drawn in the front view per expression (dream, joy, surprise, sad, anger; the 3/4 sheet's
  parameters carried to the front), rendered to transparent PNG (`render_svg.mjs`), projected onto the head from the
  front (uv = x, y). The face's shade uses normals of the head smoothed 60 times (one clean shade on the far side).
  So the eye is a painted sign, not a ball with lids — chosen for this style; it cannot blink or look aside yet.
- **Body and skeleton — Anny `moood-woman` from `engine/data`** (its SOMA joints and weights). Joints moved to the
  drawing in `tools/build.py` (neck long — Neck1/Neck2/Head at the drawing's heights; shoulders lower and narrower;
  arms 8 % shorter; hands 0.84; feet shorter; legs closer); vertices follow their joints (each joint's move blended by
  Anny's weights, shins and forearms slimmed about the bone). Frames are not touched, so Kimodo retargets as for any
  engine body. Only hands, wrists, shins and feet are kept — everything else is under the clothes. Feet are smoothed
  into one rounded form and coloured as shoes; socks are colour on the shin.
- **Clothes — shells from the drawing's silhouettes**: the dress (front width `DRESS_F`, profile depth — the
  profile's paths are local to `anya.body_s()` and copied into `drawing.py`), a small yoke into the neck, a round white
  collar, the cardigan (bigger than the dress at every height, open in front by the drawn opening, a round yoke to the
  neck), sleeves as tubes along the A-pose arm. Weights: from the nearest skin of the whole fitted Anny, blended to a
  skirt rule (pelvis, and up to 78 % the thighs at the hem) below the waist, smoothed over the shell.
- **Hair — one shell** (`tools/hair.py`): width from the front's back mass (`BACK_F`), depth from the profile
  (`HAIR_S`), a dome over the crown, a window for the face along the curtains' inner edge (`CURT_F`, a little wider),
  its edge laid on the face; pointed ends; pushed out of the head and the clothes; weights Head → Chest/Neck1 below the
  chin. Its shade uses normals of the shell smoothed 40 times; the inside is the dark hair colour, as drawn.
- **Look** (`tools/web/anya.js`, three.js 0.160): flat colour per vertex, one stepped shade (light relative to the
  camera, as in the drawing: from above, in front, from the picture's right), coloured outline as an inverted hull
  (per-vertex width, off in the painted regions), the face layer.
- **Motion**: the pack is made an engine body (`makeBody`) and played by the engine's `Figure` (retarget → skinning
  `cor`), Kimodo's `walk`. The standing pose for the drawing's views is the rest with the arms aimed down (a pose layer).

Neural models were not used; StdGEN's results were not needed.

## Second round: alive (asked by Pavel through the orchestrator)

Asked: the face alive in its own way (blinks, saccades, gaze leading head turns, speech mouth shapes, smooth
transitions and mixes of the sheet's expressions — timing from real faces, not sines); a few Kimodo motions with the
live face; cheap right fixes of hands, socks and the skirt in a wide step; the viewer able to show all of it.

- **The live face** (`tools/web/face.js`): the drawing's face parts ported to canvas (`eye`, `brow`, `closed_eye` of
  `styles/s3-graphic/tools/face.py`, the mouths of `faces.py` turned into one mouth of a few numbers: width, opening,
  smile, round, box, teeth) and drawn every frame into the head's painted layer (premultiplied, so no dark rim where
  the paint ends). Expressions are weights of the five, mixed parameter by parameter; a change settles as a critically
  damped spring (brows a little faster than the rest). Blinks: log-normal intervals (median 2.8 s), 12 % doubles,
  close 70 ms / hold 30 ms / open 150 ms. Saccades: log-normal fixations (median 0.55 s), 22 ms + 2.7 ms/deg, fast
  start, slower landing. Gaze lead: the head's yaw/pitch over the clip at 100 Hz (`headTrack` in `anya.js`); the eyes
  jump toward where the head will be in 0.25 s and come back smoothly as it follows; most big jumps take a blink.
  Speech: syllables (consonant + vowel visemes: closed, f/v, e/i, a, o, u), words and phrase pauses from a seeded
  generator; the mouth follows them as a spring (co-articulation); the lower face is on the Jaw joint (new weights in
  `build.py`) and opens a little with the mouth. Everything is a function of time from seeded schedules, so a film is
  the same every time and the viewer can scrub. `still: true` turns blinks and saccades off for pictures.
- **Hands**: Anny's spread fingers replaced by mittens as drawn (fingers together, a small thumb), rigid on the hand
  joint (`build.py`, HANDS). Kimodo's finger turns are not used.
- **Socks and shoes**: the legs carry their rest height per vertex (`band`); the shader cuts shoe (below 0.06 m) and
  sock (below 0.134 m, the drawn sock top) per pixel — clean edges instead of colours smeared over big triangles.
- **Skirt in a step**: the thighs' share at the hem lowered to 55 % (less of a trouser leg), and after skinning every
  skirt point below mid-thigh that is inside a leg's capsule (lower thigh r 6 cm, shin r 4.8 cm) is put on its surface
  (`pushSkirt` in `anya.js`) — the shin no longer shows through the hem. Not cloth: no swing, no folds.
- **Motions** (`tools/make_live.py`): idle (looking round), walk, wave (talking), sit, stomp, all Kimodo's from
  `engine/motions` through the engine's retargeting and skinning (`anya.js` does what `Figure.frame` does, plus the
  jaw and the skirt push), and two close films of the face.
- **Viewer** (`tools/web/view.html` → `ui.js`): drag to turn, wheel nearer, motion select, play/pause, scrub,
  expression buttons and five mix sliders, talk on/off, face close, front view.

## Repeat

```
cd to3d/r1-s3-anya/tools
B=/home/user/cache/blender/blender
$B -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
   --python hbm_export.py -- /home/user/cache/to3d-r1-s3-anya/hbm_head.npz
python3 faces.py /home/user/cache/to3d-r1-s3-anya/faces
NODE_PATH=/opt/node-tools/node_modules node render_svg.mjs /home/user/cache/to3d-r1-s3-anya/faces /home/user/cache/to3d-r1-s3-anya/faces/*.svg
python3 build.py /home/user/cache/to3d-r1-s3-anya/out          # the pack: anya.json/.bin
cp /home/user/cache/to3d-r1-s3-anya/faces/face-*.png /home/user/cache/to3d-r1-s3-anya/out/
python3 bases.py /home/user/cache/to3d-r1-s3-anya/out          # the bases as they come, for the steps
NODE_PATH=/opt/node-tools/node_modules python3 compare.py /cache/to3d-r1-s3-anya/out/anya.json /home/user/cache/to3d-r1-s3-anya/cmp
NODE_PATH=/opt/node-tools/node_modules python3 make_pics.py    # ../pics: pictures and the turn (~5 min)
python3 make_live.py                                           # ../pics: the live face and motions (~15 min; reads ../data)
cp /home/user/cache/to3d-r1-s3-anya/out/anya.* /home/user/cache/to3d-r1-s3-anya/out/face-*.png ../data/
```

`shots.mjs` serves `/home/user/` and drives `web/view.html?pack=…` with Playwright (software WebGL); three.js is
routed to the local copy in `/home/user/cache/n3-cloth/node_modules`. Without `?pack`, `web/view.html` opens
`../../data/anya.json` by hand: drag to turn, «стоит» / «идёт (Kimodo)», the five expressions (serve the repository
root with `python3 -m http.server`).

Files: `drawing.py` (the drawing's paths sampled, silhouettes), `head.py`, `hair.py`, `build.py`, `faces.py`,
`mesh.py` (smoothing, normals, loops), `pack.py` (engine packs in Python), `overlay.py`, `compare.py`, `make_pics.py`,
`bases.py`, `web/` (viewer). The pack format `r1/character` = an engine body's arrays (positions, triangles,
skinJoints, skinWeights, joints, frames) plus look: `col`, `shd`, `lin` (fill, shade, line colours), `ow` (outline
width), `uv`/`tex` (the face layer), `pn`/`pw`/`pj` (smoothed normals for the shade, their weight and joint), `two`
(two-sided); `pieces`/`trianglePieces` name the parts.

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`; Kimodo's SOMA skin Apache-2.0).
- Kimodo walk: `engine/motions/walk.json`.
- The drawing and its code: this repository (`styles/s3-graphic`).

## Honest state, what is weak

- The eye is a painted sign (no ball, no lids): exact to the drawing; it blinks and looks, drawn.
- Hands are mittens: no fingers, so no grip or gesture of fingers.
- Shoes are smoothed feet coloured; their shape is still Anny's foot.
- The skirt is skinned and pushed off the legs, not cloth: it does not swing or fold.
- Hair is rigid (Head, with the ends on the chest); no inertia.
- The profile shows more cheek and an ear in the drawing; the 3D follows the front view there (the two drawings
  disagree a little).
- Legs are thicker and further apart than the drawing's sticks, on purpose (Kimodo's step would cross them).
- Back and side views have no drawing; they are built from the same shapes.
