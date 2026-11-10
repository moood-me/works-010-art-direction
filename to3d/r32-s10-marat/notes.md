# Р32 — Марат, чистая линия (С10 → 3D)

What was done, why, and how to repeat it. Brief: `docs/briefs/to3d.md`, "Third round". The orchestrator asked for Вера
(Р31) and Марат (Р32) in С10, starting from Р2 (Савелий Петрович). Марат was made second, on Вера's tools
(`to3d/r31-s10-vera/notes.md` tells what those changed against Р2 and why); this note says what is his own.

## What is different from Р31

`who.py` holds his measures; `drawing.py` and `body.py` are his own; the rest is Вера's with these changes:

- **`drawing.py`** — from `styles/s10-ligne-claire/tools/marat.py`: the head (no lips or chin under the beard), the
  hair and the beard as meshes (the shells cut by the drawing's own scalloped lines, written as margins so the edges
  are smooth, then pushed into curls by the drawing's `extra.bumps`), the laughing mouth's upper line and lower edge
  on the beard (`extra.grin_marks` at his rest), all marks tagged. The rest expression is `marat.REST` (a wide smile).
- **`fit_head.py`** — the nose made broader before the fit (`who.NOSE_W`).
- **`body.py`** — Anny's man (`moood-man`). The body far from Anny's proportions was made by scaling bones, not by
  bending the mesh: the trunk ×1.36 tall, the arms set ×1.55 wider, forearms ×0.82, hands ×1.22 (girth 1.3, fingers
  1.42, laid side by side). The barrel is the drawing's jacket shell skinned to the trunk; Anny's trunk is only kept
  inside it. Bare forearms set to the drawn radii about their bones (`along`). Sleeves and trouser legs: shells over
  Anny at the drawn radii (legs thinner under the apron: 56 → 50 instead of 78 → 50, or a step brings them through
  it); the trouser hem cut straight. The apron: the front of the drawing's shell, its points below the hips take both
  legs' weights blended across the width (12 % of the hips'). Towel, buttons, the flap's edge, the apron's fold and
  pocket, the towel's stripes from the drawing (lines sampled in the shell's own coordinates, so they lie on it).
  No folder-like prop: the ladle is left out.
- **`assemble.py`** — the beard as a piece (kept off the face like the hair); the clearance map fixed (empty cells of
  the radius map took zeros into the smoothing, so the sideburns could sink — a larger maximum filter first; the map
  now covers heights to 180); curl marks that fall beyond the hair's or beard's edge dropped (the drawing clips
  them); the mouth pieces carry, beside the opening weight, their gap to the upper line (`gap` in `face.json`);
  the mouth pieces are kept in stills too (`keep_still`), and the drawn mouth marks skipped there (a fan of
  triangles can't fill the curved band of teeth).
- **`web/face.mjs`** — `shut` (the drawn opening taken away), the beard moved by the jaw to its end, his own
  expressions (calm is the rest laugh). `stand.mjs` — the head's roll.
- **`jobs.py`** — `who.HEAD_SHIFT`: the drawing's pose (its line of action) carries the head back and aside; the
  comparison cameras of the head are shifted by it, since he stands straight here.
- **`steps.py`** — step 3 shows the mouth's own pieces.

## How to repeat (CACHE = `/home/user/cache/to3d-r32-s10-marat/`)

```
T=to3d/r32-s10-marat/tools; C=/home/user/cache/to3d-r32-s10-marat; mkdir -p $C/cmp; cd $C
$T/heavy.sh blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend -P $T/export_hbm.py -- hbm_head.npz
python3 $T/drawing.py . ; python3 $T/fit_head.py . ; python3 $T/body.py . ; python3 $T/assemble.py . --body ; python3 $T/jobs.py .
FACE='{"calm":1}' node $T/stand.mjs . stand.bin
FACE='{"calm":1}' HEAD='{"pitch":-7,"yaw":10,"roll":-7}' node $T/stand.mjs . stand_head.bin ; cp stand_head.bin stand_fig.bin ; cp stand_head.json stand_fig.json
for j in turn portrait figure turnaround; do $T/heavy.sh blender -b -P $T/render.py -- job_$j.json; done
S=styles/s10-ligne-claire/pics   # from the repository's root
python3 $T/compare.py cmp/compare-turn.png $S/turn-marat.png "0,0,420,472;420,0,420,472;840,0,420,472" cmp/turn0_0000.png cmp/turn1_0000.png cmp/turn2_0000.png
python3 $T/compare.py cmp/compare-portrait.png $S/portrait-marat.png "0,0,500,600" cmp/portrait_0000.png --layout=row
python3 $T/compare.py cmp/compare-figure.png $S/figure-marat.png "0,0,500,900" cmp/figure_0000.png --layout=row
python3 $T/exprsheet.py .
LIFE='{"seed":3}' $T/film.sh . walk walk full 2 15 ; $T/film.sh . wave wave full 2 15 -20 ; $T/film.sh . face walk face 2 15 -18
python3 $T/steps.py . ; python3 $T/web_data.py .
THREE_DIR=$C/npm/node_modules/three node $T/web/shot.mjs $C/shot wave 0.4      # npm install three@0.160.0 in $C/npm
```

The `LIFE` values of the films on the page: wave — `{"seed":4,"talk":true,"talkFrom":0.6,"talkTo":2.6,"expr":[[0,{"calm":1}],[0.4,{"joy":1}],[2.6,{"calm":1}]]}`;
face — `{"seed":5,"talk":true,"talkFrom":0.2,"talkTo":1.6,"expr":[[0,{"calm":1}],[1.7,{"joy":1}],[2.3,{"surprise":1}],[2.9,{"sad":1}],[3.4,{"anger":1}],[3.75,{"calm":1}]]}`.

## Bases and licences

| What | Where | Licence |
|---|---|---|
| Human Base Meshes bundle v1.4.1, `GEO-head_animation_realistic` + its eyes | blender.org demo files; local `/home/user/cache/n5-heads/hbm/` | CC0 |
| Anny man (`moood-man`), SOMA skeleton and weights | `engine/data` (Anny: NAVER, Apache-2.0; MakeHuman CC0; SOMA rig: NVIDIA, Apache-2.0) | as in `engine/data/soma/NOTICE` |
| Kimodo walk, wave | `engine/motions` (moood studio) | as the engine's motions |
| The drawing | `styles/s10-ligne-claire` (ours) | — |
| three.js 0.160.0 (the viewer; from jsDelivr) | MIT | |

No neural images.

## What did not work / is left

- The drawing's pose (leaning back, a fist on the hip, the ladle up) is not made: the stills stand with the arms
  down, as his turnaround sheet does. The overlay of the full figure therefore matches in height, apron and legs,
  not in the arms and the lean.
- The apron is a skinned shell: in a step its hem opens in a notch at the middle (where the two legs' weights
  meet), and the knee can touch it from inside. The jacket has no folds.
- Sleeves are shorter and narrower than the drawn rolled sleeves (they are Anny's upper arms at radius 54).
- The shut mouth on the dark beard is nearly invisible (in the drawing too).
- Freestyle draws dark strokes along the curls' bumps inside the hair.
- The viewer's line is pixel-made; small pieces (buttons) come out as dots. three.js comes from jsDelivr, which this
  container's network doesn't let through: the viewer's picture was taken with a local copy (`THREE_DIR`).
