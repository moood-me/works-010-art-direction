# Р50 — Марат, низкополигональный (С19 → 3D)

What was done, why, how to repeat. Brief: `docs/briefs/to3d.md` (all rounds). The drawing: `styles/s19-lowpoly`
(`figure-marat`, `turn-marat`, `portrait-marat`, `expr-marat`; code `tools/poly.py`, `body.py`, `face.py`, `marat.py`).
Done by one agent in one session; the orchestrator commits.

## The idea

С19 is 3D by nature: the style's code builds each character from convex facet pieces on a small skeleton and lights
each facet as a plane. So the 3D here is **the drawing's own model**, built by the drawing's own calls, hung on SOMA's
skeleton so Kimodo moves it through the engine, and shown in the browser by the drawing's own light rule. Anny's body
and an artist's head (brief points 1–2) are not used: the style has no anatomy or modelled face to gain from them, and
the drawing's pieces already agree with the drawing in every view (same choice as Р8 for С6, whose `build.py` this
one started from). No style had a character in 3D before in С19; this is the first.

## Steps (tools/)

1. `build.py` (numpy, scipy, shapely — what the style's code needs)
   - **rest** = the drawing's turnaround pose (`marat.POSES['turn']`, `body.Skel`);
   - **pieces**: `parts()` repeats `marat.figure()` line for line and gives each piece a weights rule. Rigid on one
     bone: thighs, shins, shoes, belly (Hips), jacket, collar, towel (Chest), neck (Neck2), sleeves, rolls, forearms,
     hands, ladle, head, nose, ears, curls, beard, moustache. Added: a faceted ball (the limb's ring, a smaller ring
     above and below, two poles) in each knee, elbow, ankle, wrist — the drawing fills a bent joint with a hull built
     for that pose; a ball does it at any angle. Soft: the shoulder slope (its inner points on the chest, its first
     ring 60 % on the arm, its second on the arm) and the apron (bib → Chest, waist → Hips, the hem up to 72 % on the
     thighs, split left/right by a soft step) — so the legs don't walk through it. Hands exist twice (fist as drawn,
     open for waving); the page shows one of each;
   - **decals** (buttons, the apron's tie, the towel's stripes): flat polygons with the weights of the facet's
     triangle they lie on (barycentric), turned to face outward;
   - **face**: the head's features are not baked (see face.js). The jaw and beard keep the drawing's two moves as
     per-vertex offsets, found by building the head at `open` 0, 0.6, 1.6: `dOpen` (the chin beard's top follows the
     mouth) and `dDrop` (`drop = max(0, open − 0.6) · 1.2`: chin and beard go down);
   - **SOMA**: 77 joints placed on the drawing's skeleton. The drawing bends the trunk at the waist only, so Spine1,
     Spine2 sit just under it and Chest at it: the belly stays with the pelvis, the chest turns about the waist.
     Frames: limbs `turn(SOMA bone → our bone) · SOMA's frame` (Kimodo's bones followed with our lengths); the hand by
     two axes — along the hand (wrist → Middle**2**: SOMA's Middle1 sits inside the wrist, using it bent the hand 70°)
     and the palm's normal (Index2 × Pinky2, the side told by the thumb); trunk and head keep SOMA's frames;
   - **poses**: the drawing's `turn`, `stand` (the laughing one with the ladle), `portrait` as joint turns — exact:
     each joint's turn is its segment's rotation in the pose times the inverse of the rest's;
   - writes `web/data/marat.{json,bin}` (an engine body + topology pack: 1 186 vertices, 1 796 triangles, 117 pieces
     listed in the header with colour, material, group), `poses.json`, `face.json` (the spec numbers and `EXPR`).
2. `web/marat.js` — the engine as it is (`makeBody`, `makeRetarget` with its `armsOff` 9° so the thick arms clear the
   barrel, `build`, `Skinner` linear) and the look:
   - skinning on the CPU; the triangles are drawn unshared; each one's colour is `poly.Light.shade` number for
     number (key (−0.72, 0.52, 0.45) warm `#fff1dc`, cool `#5a5f8c`, wrap 0.15, fill 0.22; per material tint, depth,
     warmth), from its normal in the viewer's space — as the drawing does it. A decal takes one normal for the whole
     polygon;
   - the head's front facets take the face canvas straight from the front (how `poly.press` lays decals), shaded as
     the drawing shades decals over skin;
   - a flat cast shadow: every facet flattened onto the ground along the key light, drawn once through the stencil;
     on the plinth it is cut to the plinth's top;
   - the stage: the drawing's backdrop (gradient with faint large facets), the plinth of its sheets, a flat faceted
     ground for motions fading into the backdrop; the camera in the drawing's terms (`poly.Camera`: yaw, pitch, focal
     distance; `draw` mode puts the target at given pixels at a given scale — the comparisons are taken so).
3. `web/face.js` — the drawing's features as numbers: an eye of 5 + 5 points that is the almond or the laughing
   crescent or between (top, bottom, lid drop, smile), iris, pupil, lid band, speck, crease, crow's feet; brows; a
   mouth of 4 + 5 points that is a line or open (with teeth, tongue, lower lip); cheeks. At a pure expression the
   polygons are the drawing's point for point. `EXPR` is `marat.py`'s plus `calm` (eyes open, a smile) — his rest is
   a laugh with shut eyes, where gaze and blinks would not show.
4. `web/live.js` — Р11's timing: blinks log-normal around 2.8 s (shut 65–95 ms, open 120–190 ms, doubles, with big
   gaze shifts), fixations 0.2–1.6 s and saccades, the eyes leading the head by 0.25 s, expressions by critically
   damped springs, speech as letters → mouth shapes with pauses, the jaw and beard following the mouth's opening;
   breath for the drawn stand (3.2–4.6 s, uneven). All seeded.
5. `web/app.js`, `ui.js`, `view.html` — the page (`window.A` for pictures) and the viewer.
6. `shots.mjs` (headless Chromium, swiftshader), `make.py` (comparisons, steps, stills, films), `viewer_check.mjs`.

Repeat:
```
cd to3d/r50-s19-marat/tools
python3 build.py
python3 make.py compare steps stills      # ≈ 1 min
python3 make.py films                     # turn, walk, wave, dance, face, talk — ≈ 3 min
NODE_PATH=/opt/node-tools/node_modules node viewer_check.mjs /tmp/v.png
```
`make.py` runs each browser and ffmpeg through `flock /home/user/cache/heavy.N.lock`. three.js 0.160 is read from
`/home/user/cache/n3-cloth/node_modules/three` when headless (the page itself takes it from jsDelivr).

## Motions

From `engine/motions`, copied into `tools/web/data/motions` (nothing ordered): walk (with the ladle in his fist),
wave (open right hand), dance, bow, stomp, idle. `sit` was left out: Kimodo sits on the floor and the apron folds
into the legs. The standing picture is the drawing's own pose with breath, not Kimodo's idle.

## Bases and licences

| What | Where | Licence |
|---|---|---|
| The drawing and its code (poly.py, body.py, face.py, marat.py) | `styles/s19-lowpoly` | ours |
| SOMA skeleton | `engine/data/skeleton.json` (NVIDIA, see `engine/data/soma/NOTICE`) | Apache-2.0 |
| Kimodo motions | `engine/motions` (moood studio) | as the engine's motions |
| three.js 0.160 | jsDelivr | MIT |

No neural images, no third-party meshes.

## What is weak

- The apron is skinned, not cloth: its hem follows the thighs and folds into a point on a wide step; at the hip the
  belly shows beside it. It has no ties at the back (the drawing has none).
- Hands are fists and flat palms of a few facets; fingers don't move (Kimodo has none); the fist ↔ open hand is a
  swap per motion, not a move.
- In the wave Kimodo's arm passes right by the head (the engine's `armsOutOfHead` was not tried: it needs a head
  part in the body). Kimodo's idle stoops and holds the elbows out.
- The shoulder slope stretches as one piece when the arm goes up; the upper sleeve and it overlap rather than join.
- In the drawn stand the apron's hem differs a little from the drawing (there it is rigid on the pelvis).
- The light is the drawing's, tied to the viewer: turning him turns the shadow with it. No fog or coloured air as in
  Virginia.
- The engine was not changed. A history note in `docs/history/` is for the orchestrator (work only in this folder).
