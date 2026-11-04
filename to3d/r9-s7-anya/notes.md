# Р9 — Аня, Гибли (style С7) in 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, second round; brief: `/home/user/cache/BRIEF-to3d.md`):
Аня of style С7 (`styles/s7-ghibli`) built in 3D from ready bases and the drawing's own forms, played by Kimodo's
motions through the engine, with a live drawn face and a browser viewer. Built on Р1's pipeline (`to3d/r1-s3-anya`):
its pack format, viewer, engine use and live-face timing; adapted to this style.

## Why this way

С7's drawing is itself built from simple 3D forms (`styles/s7-ghibli/tools`): the head is horizontal rings (half width,
front, back per height) with a profile along the middle (nose, lips, chin); the torso and the skirt are lofts of
rings; arms and legs are tubes along a posed skeleton; the hair is a shell over the skull plus locks along Bézier
curves; the face is flat templates laid on the head's surface. So the 3D takes those very numbers (in centimetres,
the turnaround's 'stand' pose) instead of tracing silhouettes, and every view of the drawing matches by construction.
The proportions are natural (≈7 heads), so Anny's adult body fits as it is.

## How it is built (and what each base gave)

- **Head — Blender Human Base Meshes, stylised head (CC0)** (`hbm_export.py` takes it out as arrays; the npz from
  Р1's cache was reused). `headfit.py`: the eye sockets and the mouth's lining (faces no outside ray reaches) are taken
  out and the holes closed (also the small holes left at the mouth's corners and nostrils — left open, they showed the
  inside of the head as dark spots); heights mapped piecewise (neck end, chin, eye line, crown → head-local −1.42, −1,
  −0.09, +1); at each height the width and front/back scaled to the drawing's ring (with its cheek and middle profile),
  under the jaw to the drawn neck tube; then the face laid onto the drawing's own front surface (`Head.surf`) with a
  weight fading to the sides, relaxed over it (folds out), the seam smoothed, and anything the base kept inside pushed
  out onto the form. The base gave the jaw, the neck, the ears (made smaller, at the drawing's ear) and clean topology;
  the face is the drawing's flat round plane with its small nose.
- **Face — the drawing's own face parts, drawn live** (`web/face.js`): `head.py`'s eye (upper lid as a thick ribbon
  heavier to the outer corner with a flick, the short lower stroke, white, the lid's shadow on it, the tall iris lighter
  below, two glints), brow, hook nose, mouth (line / D / O / shout as curves mixed by weights; teeth, tongue), lower lip,
  blush — ported to a canvas in head-local units and projected on the head from the front (on the drawing's surface a
  template at (x, y) is seen from the front at (x, y), so they go in unchanged). The line width follows how big the head
  is on screen (the drawing draws its lines one width in pixels). The fringe's shadow on the forehead is the drawing's
  rule (front hair shifted down and right, over the skin) computed once in `build.py` and painted in the same layer.
  Expressions are the sheet's `Expr` numbers (`build.py` of the style): calm, dream (the figure's look), joy, surprise,
  sad, anger.
- **Body and skeleton — Anny `moood-woman`** (its SOMA joints and weights). Joints moved to the drawing's skeleton in
  `build.py` (hips 84 cm, shoulders at the drawing's, upper arm 27 / forearm 23 cm, legs from the drawing's hip, knee,
  ankle; neck and head joints at the drawing's neck and head); each joint's move turns its bone to the new direction
  and stretches it (shins slimmed). Frames untouched, so Kimodo retargets as for any engine body. Kept: hands with the
  wrists and the shins below the skirt; the rest is under the clothes.
- **Clothes — the drawing's own lofts as thin solids** (`shapes.py`: outer side, inner side, a rim along open edges, so
  the outline draws real edges): the blouse (torso loft + its ease, bigger than the skirt's top, the V neckline cut as
  drawn), the cardigan (bigger than the blouse everywhere, open in front: narrow at the hem, wide at the neck), the
  skirt (the drawing's rings with its soft folds toward the hem and its four fold lines), the skin under the neckline
  (torso loft closed onto the neck), sleeves (the drawing's arm tube + ease, a wider cuff), the shoes (the drawing's
  heel → instep → toe tube, flat sole). Weights from the nearest skin of the fitted Anny, the skirt blended to the
  pelvis and thighs below the hips; in motion the skirt is pushed off the legs' capsules and the push spread over the
  cloth (Р1's way).
- **Hair — the drawing's own hair** (`hair3d.py`): the shell between hairline and crown (the drawing's volume), tucked
  into the skin at the hairline; every lock and tuft of `anya.HAIRDEF` as a 3D lock along the same Bézier from the same
  root with the same width profile and pointed end — flat across, wide side along the head; the locks' strand lines and
  the shell's flow lines as thin dark strips. Pushed out of the head and the clothes. Weights: head, and below the chin
  over to the neck and chest (the tail on the shoulder).
- **Look** (`web/anya.js`, three.js 0.160): flat colour per vertex in the drawing's exact hexes, one shade tone — the
  drawing's warm multiply (`svgdoc.shade`) — with a hard edge, the light from the picture's upper left in camera space as
  in the drawing; one even dark-brown outline (#2e2320) as an inverted hull, its width in pixels like the drawing's
  1.9 px at the turnaround's scale; for the hair the outline is moved back 1.2 cm so lock edges over the hair mass draw
  no line (the drawing outlines the hair as one shape). The face's shade uses the normal of the drawing's plain head
  form (a clean crescent), the hair's a smoothed form. The neck under the jaw is in the head's shadow, as drawn.
- **Pose layers**: the drawing's 'stand' arm directions (the arms a little further out than drawn: the drawing paints
  the hands over the skirt, in 3D they would be inside it), palms turned to the thighs; on top of every pose and
  motion the fingers together and a little bent toward the palm (Anny's rest has them spread straight).
- **Motion**: the pack is made an engine body (`makeBody`) and played by the engine's `Figure` (retarget → skinning
  `cor`): Kimodo's `walk`, `idle`, `wave`, `sit` from `engine/motions`.
- **Live face** (Р1's `LiveFace`, numbers retuned for this face): log-normal blinks (median 2.8 s, 12 % doubles; the
  upper lid goes down onto the lower one, 70 / 30 / 150 ms), saccades (fixations ≈0.55 s, 22 ms + 2.7 ms/deg), the gaze
  leading head turns read from the clip (with blinks on big ones), speech as consonant/vowel mouth shapes followed by a
  critically damped spring (the jaw opens a little), expressions mixed number by number and settling as springs (brows
  a little ahead). All seeded: a film is the same every time and the viewer can scrub.

Neural models were not used; StdGEN's results were not needed (the drawing's forms give the back and sides).

## Repeat

```
cd to3d/r9-s7-anya/tools
B=/home/user/cache/blender/blender
$B -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
   --python hbm_export.py -- /home/user/cache/to3d-r9-s7-anya/hbm_head.npz
python3 build.py /home/user/cache/to3d-r9-s7-anya/out        # the pack anya.json/.bin (≈10 s)
python3 bases.py /home/user/cache/to3d-r9-s7-anya/out        # the bases as they come, for the steps
python3 compare.py /cache/to3d-r9-s7-anya/out/anya.json /home/user/cache/to3d-r9-s7-anya/cmp
python3 make_pics.py stills turn                             # ../pics (stills, turn.mp4)
cp /home/user/cache/to3d-r9-s7-anya/out/anya.* ../data/
python3 make_live.py                                         # ../pics: the live face and the motions (reads ../data)
```

`shots.mjs` serves `/home/user/` and drives `web/view.html?pack=…` with Playwright (software WebGL; three.js routed to
`/home/user/cache/n3-cloth/node_modules`). Loading takes ≈1.5 min (the engine's skinning centres for 70 k vertices),
then ≈3 s a frame. `look.py` makes quick strips while building. The viewer by hand: serve the repository root with
`python3 -m http.server` and open `to3d/r9-s7-anya/tools/web/view.html`.

Files: `drawing.py` (the style's code as numbers), `headfit.py`, `hair3d.py`, `shapes.py`, `build.py`, `bases.py`,
`compare.py`, `make_pics.py`, `make_live.py`, `look.py`, `mesh.py`, `pack.py` (Р1's), `web/` (viewer: `anya.js`,
`face.js`, `ui.js`, `view.html`). Pack format `r1/character` as Р1's, plus `ob` (outline moved back) and
`face.shadow`.

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`).
- Kimodo motions: `engine/motions`.
- The drawing and its code: this repository (`styles/s7-ghibli`). three.js: MIT.

## Honest state, what is weak

- The straw hat of the drawing is not made (in the turnaround it floats in front of the skirt between the hands; a
  held prop would need its own pose).
- The hands are Anny's (fingers), posed relaxed; in profile they read a little stiff.
- The skirt is skinned and pushed off the legs, not cloth: it does not swing or fold by itself.
- The hair is rigid on the head (the tail goes with the chest); no inertia.
- The nose mark is drawn on the face's right side as in the front and three-quarter views; turned the other way the
  drawing would move it to the far side — the 3D keeps it where it is.
- The drawing's skull is a "face mask" (its back comes forward under the hair); the 3D keeps that, so without hair the
  back of the head is flat — the hair covers it.
- The neck-to-chin and the jaw's shade edge are less clean than the drawing's on close-ups.
