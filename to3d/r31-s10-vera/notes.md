# Р31 — Вера, чистая линия (С10 → 3D)

What was done, why, and how to repeat it. Brief: `docs/briefs/to3d.md`, "Third round": each style gets two more
characters beside the one already in 3D. The orchestrator asked for Вера (Р31) and Марат (Р32) in С10; the start was
Р2 (Савелий Петрович, `to3d/r2-s10-savely`) — its bases, fit, look and viewer. Done by one agent; the orchestrator
commits. The work was interrupted twice by container restarts; nothing was lost but running renders.

## The idea (as in Р2)

The С10 drawing is itself built as simple 3D (`styles/s10-ligne-claire/tools`): the head from slices with nose, lips,
chin, ears as bumps, hair and garments as shells, marks as 3D lines. Those shapes are taken as data in the drawing's
units and every base is fitted to them; the cameras are the drawing's own, so overlays are exact.

The style's page had no turnaround and no expression sheet for Вера: `tools/sheets.py` draws them with the style's own
code, unchanged, into the cache (`pics/drawing-turn.webp`, `pics/drawing-expressions.webp`). Nothing was written into
`styles/`.

## Steps (tools/, in order; CACHE = `/home/user/cache/to3d-r31-s10-vera/`)

`who.py` holds the character's measures (base body, scale, floor, eye, mouth, panel colour); the other tools read it,
so the same tools make another character of this style with another `who.py`, `drawing.py` and `body.py`.

1. `drawing.py CACHE` — from the С10 code: the head surface as points, the hair cap (cast.vera's shell cut by its
   hairline, smooth edge) and the knot, every mark for each expression tagged by what made it.
2. `export_hbm.py` (Blender, on `human_base_meshes_bundle.blend`) — the realistic head "for animation" and its eyes.
3. `fit_head.py CACHE` — as Р2, plus:
   - the base is first brought to the drawing's width at every height (Вера's face is much narrower below the eyes;
     without this the skin folded over itself on the cheeks);
   - the mouth drawn in to the drawing's narrow mouth and set at its height before the fit;
   - the mouth's bag found by rays (what lies behind the face's front surface), kept narrow; ears carried at the
     drawing's ear size; the nose's vertices set onto the drawing's steep-sided nose.
4. `body.py CACHE` — Anny's woman (`moood-woman`): per-bone scales (all ×1.17, legs together and straight, forearms
   0.86), fingers laid side by side; clothes from the drawing's shells (jacket with V, blouse front, lapels, collar,
   skirt), sleeves over Anny's arms widened to the drawn sleeve, legs in tights are Anny's (thighs thinned under the
   skirt), shoes as ovals, buttons, seams as thin ink, the folder as a plate on the left hand (placed where it lies
   flat by the skirt in the stand pose: needs `stand.json`, so the first build runs twice — `all.sh` below does it).
   The skirt's weights: both legs' sides blended across the width.
5. `assemble.py CACHE --body` — the scene (`scene.npz/json`) and the engine body pack
   (`CACHE/engine/data/{bodies,topology}/vera.*`, `offsets.json`, `face.json`):
   - the lips sealed and the bag cut away (it came through the narrow cheeks); loose pieces dropped;
   - face marks for Freestyle on the lips and the hands: only their outer contour is drawn;
   - marks sampled densely and laid on the surface by a blend of nearby vertices (long hair strands were jagged);
   - the hair kept above the skull at the crown by height (rays from the axis don't work at the pole);
   - marks baked as ink tubes, each remembering its rings (`tube`), so `render.py` sets its width for each picture;
   - **the drawn mouth**: the drawing's mouth line as pieces (`mouthfill`, `mouthteeth`, `mouthtongue`,
     `mouthline`) whose vertices carry an opening weight; `web/face.mjs` turns them with the jaw by that weight.
6. `stand.mjs CACHE OUT.bin` — the stand (arms down), optional `HEAD='{"pitch":-3,"yaw":4}'` and
   `FACE='{"joy":1}'`. `move.mjs CACHE MOTION OUT.bin [step]` — a Kimodo motion through the engine with the live face
   (`LIFE='{…}'`).
7. `render.py JOB` (Blender) — as Р2, plus a second Freestyle line set for face-marked faces (contour only), tube
   widths per picture, a far camera (a walk toward the camera reached the old one).
8. `jobs.py` (jobs of the comparison pictures and the turnaround), `compare.py`, `exprsheet.py` (the five
   expressions of the live face), `films.py` + `film.sh` + `film.py` (a moving picture), `steps.py`, `montage.py`,
   `web_data.py` (the viewer's data), `web/shot.mjs` (a picture of the viewer).

`heavy.sh` runs a heavy command through one of the three shared locks (`/home/user/cache/heavy.N.lock`).

```
T=to3d/r31-s10-vera/tools; C=/home/user/cache/to3d-r31-s10-vera; mkdir -p $C/cmp; cd $C
$T/heavy.sh blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend -P $T/export_hbm.py -- hbm_head.npz
python3 $T/drawing.py . ; python3 $T/sheets.py . ; python3 $T/fit_head.py .
python3 $T/body.py . ; python3 $T/assemble.py . --body ; node $T/stand.mjs . stand.bin     # first pass: no folder yet
python3 $T/body.py . ; python3 $T/assemble.py . --body ; python3 $T/jobs.py .
node $T/stand.mjs . stand.bin ; HEAD='{"pitch":-3,"yaw":4}' node $T/stand.mjs . stand_head.bin ; cp stand_head.bin stand_fig.bin ; cp stand_head.json stand_fig.json
for j in turn portrait figure turnaround; do $T/heavy.sh blender -b -P $T/render.py -- job_$j.json; done
python3 $T/compare.py cmp/compare-turn.png draw/turn-vera.png "0,0,420,472;420,0,420,472;840,0,420,472" cmp/turn0_0000.png cmp/turn1_0000.png cmp/turn2_0000.png
python3 $T/exprsheet.py .
LIFE='{"seed":3}' $T/film.sh . walk walk full 2 15          # likewise wave (full) and face (walk, face)
python3 $T/steps.py . ; python3 $T/web_data.py .
```

Times: a still 5–20 s, a walk of 60 frames about 2 min when the machine is free.

## Bases and licences

| What | Where | Licence |
|---|---|---|
| Human Base Meshes bundle v1.4.1, `GEO-head_animation_realistic` + its eyes | blender.org demo files; local `/home/user/cache/n5-heads/hbm/` | CC0 |
| Anny woman (`moood-woman`), SOMA skeleton and weights | `engine/data` (Anny: NAVER, Apache-2.0; MakeHuman CC0; SOMA rig: NVIDIA, Apache-2.0) | as in `engine/data/soma/NOTICE` |
| Kimodo walk, wave | `engine/motions` (moood studio) | as the engine's motions |
| The drawing | `styles/s10-ligne-claire` (ours) | — |
| three.js 0.160.0 (the viewer; from jsDelivr) | MIT | |

No neural images.

## What was decided on the way, and why

- **The mouth is drawn, not modelled.** With the base's lips, Freestyle gave a tangle of lip lines under the drawn
  mouth (Р2's moustache hid it); the base's mouth bag came through the narrow cheeks as stray strokes; teeth and a
  tongue put inside showed through. The lips were sealed and the mouth made of the drawing's own line that opens.
- **Hands as one contour.** Fingers laid together and the hands face-marked: the style's hand is a clear shape.
- **No arm holes in the jacket.** With a hole, the arm let down opened the back of the shoulder; the sleeve now goes
  into the shoulder without a seam line.
- **Thighs thinned under the skirt, the skirt's blend made sharper** — the forward thigh came through the skirt.
  It still shows for a moment in the widest step.
- **The face film is on the walk**: Kimodo's `idle` drops the head, `bow` bends her to the floor, chains of the same
  motion are refused by the engine (`wave,wave`).

## What did not work / is left

- Clothes are skinned shells: no folds; the skirt between the legs is not cloth.
- The nose line from the brow in the portrait view: Freestyle draws only true silhouettes (the drawing's renderer
  draws a line at a depth step); the nose's form matches the drawing within 1–2 units.
- The folder is rigid on the hand; the drawing's pose (the folder held at the hip) is not among the motions.
- The viewer: three.js comes from jsDelivr — this container's network doesn't let it through, so the picture of the
  viewer was taken with a local copy (`THREE_DIR=…/node_modules/three node web/shot.mjs …`, npm in the cache). Its
  line is pixel-made, thicker and rougher than Freestyle's; mark widths are fixed there.
- The steps sheet's fitted Anny shows the thinned thighs and the long neck joint — that body is under the clothes.
