# Р30 — Марат, середина века: from the drawing to 3D

What was done, why, and how to repeat it. Brief: `docs/briefs/to3d.md`, its "Third round": the third character of
style С9, after Тим (Р3, `to3d/r3-s9-tim`) and Аня (Р29, `to3d/r29-s9-anya`), built from their code. The drawing:
`styles/s9-midcentury` (figure-marat, turn-marat, expr-marat; the code: `tools/marat.py`, `face.py`, `kit.py`).

## What was decided, and why

- **Тим's way kept** (see his notes and Аня's): Anny's body bent by a map per joint, the Human Base Meshes head warped
  to the drawing's outlines with its face closed smooth, features painted by the drawing's code and projected from the
  front, the gouache shader and the drawing's own filter, the live face, the viewer.
- **Proportions from figure-marat**: 1 figure unit = 2.28 mm as Аня's (the cast stands at one scale in cast-six), the
  head drawn at 0.62 → 1 head unit = 1.414 mm; 1.85 m to the top of the curls. Legs to the hip joint 0.66 m, the trunk
  0.75 m long and 0.7 m wide at the belly, the chin at 1.475 m with the beard on the chest.
- **The body is far from Anny's**, so two things were added to Тим's deformer (`tools/body.py`): what lies behind a
  trunk joint is scaled by 0.62 of what lies before it (the belly goes first, the back stays), and a joint may be
  shifted after its parent's map placed it (the hip joints 7.5 cm inwards: the legs stand close under the barrel).
  Scales: hips 1.55 × 1.75, belly 1.62 long, 2.0 wide, 2.3 deep, chest 1.62 / 1.75 / 1.75, thighs and shins 0.7 long
  and 1.12–1.3 thick, arms 1.4–1.5 thick, hands 1.25–1.35. The engine's correction `armsOff` (16°) keeps the arms
  off the barrel, `armsOutOfHead` off the head; the model's header carries them (`corrections`).
- **Curls are balls**: the drawing makes the hair of round dabs of the brush, so the cap is ~90 balls on the skull —
  the forehead's row taken from the front view, the rest set greedily over the skull above the hairline; the skull
  under them is painted hair.
- **The beard is its own form** (as Аня's bob): sections by height from the front view's width and the side view's
  front and back; its upper edge cut along the drawing's line (ears → cheeks → mouth corners), a rim turned in; balls
  along its sides and lower edge. The mouth and the moustache are in the face picture and lie on the beard.
- **The face picture is wider** than Тим's: −160…160 head units (the beard reaches 148).
- **The apron** is measured off the jacket: at each height and angle, how far the jacket reaches from the trunk's
  axis; below the belly's widest round it hangs straight, falling in a little; the bib is the same sheet's middle;
  pocket and tie are paint split on clean lines; the tie goes on round the back as a band; the straps are paint on the
  jacket, a little proud. Below the hips it is skinned to Hips and up to 45 % to each side's thigh.
- **Not done on purpose**: the ladle (a prop in a hand that Kimodo moves), the figure's pose.

## Steps

1. `tools/body.py` — the body. 2. `tools/hbm_export.py`, `tools/head.py` (outlines in `tools/drawing.py`) — the head.
3. `tools/face_tex.py` — the still face pictures; `tools/web/face.js` — the live face (his kinds: block brows, the
beam and the laugh with teeth and tongue, laugh lines, the moustache over the mouth, upper teeth in speech).
4. `tools/build.py` — curls, beard, nose, ears, jacket, collar, trousers, shoes, apron, towel; one pack on SOMA.
5. `tools/web/marat.js` — the shader (paints, second tone, the towel's stripes), the engine's Figure.

## How to repeat

Heavy commands go through a shared lock (`L="flock /home/user/cache/heavy.$((RANDOM % 3)).lock"`), one at a time.
```
cd to3d/r30-s9-marat/tools
C=/home/user/cache/to3d-r30-s9-marat; mkdir -p $C; (cd $C && npm i three@0.160.0)
$L /home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
    --python hbm_export.py -- $C/hbm_head.npz
python3 body.py; python3 head.py; $L python3 face_tex.py; python3 build.py   # → $C/marat.json/.bin and ../model/
for k in orig faired warped; do $L python3 look_head.py $k; done
for k in turn expr figure; do $L python3 compare.py $k '{"motion":["bow"],"t":0}'; done
$L python3 steps.py; for f in turn walk wave dance stomp look face; do $L python3 films.py $f; done
$L python3 look.py          # a quick sheet: four sides and the head close → $C/look.jpg
$L node viewer_check.mjs $C/viewer.png
```

## Licences of the bases

| What | Licence |
|---|---|
| Anny body (moood-man, in the engine) | Anny (NAVER, Apache-2.0), MakeHuman (CC0), SOMA rig (NVIDIA, Apache-2.0) |
| Human Base Meshes bundle v1.4.1, `GEO-head_stylized` | CC0 (Blender Foundation) |
| Kimodo motions (walk, wave, dance, stomp, idle) | made in the moood studio, in `engine/motions` |
| The drawing and its code | ours (styles/s9-midcentury) |

## What is not done / honest

- No pose of the drawing, no ladle, no jacket buttons.
- The bib's edge and the straps are uneven: the jacket under them is coarse after the body's stretching.
- The towel is a thick shell; the apron is stiff and hangs as part of a cylinder (seen from behind); sitting, the legs
  go through it — `sit` is left out.
- The wave goes over his head (the head correction swings the arm out).
- The beard does not move with speech; no jaw.
