# Р28 — Марат, кукольная анимация (С8): from the drawing to 3D

What was done, why, and how to repeat it. Brief: `docs/briefs/to3d.md`, "Third round". For С8 the first character
in 3D is Р10 (Тим, `to3d/r10-s8-tim`), the second Р27 (Савелий Петрович, `to3d/r27-s8-savely`); this is the third,
made from Р27's code (copied into `tools/` and changed for him). The drawing: `styles/s8-stopmotion` (portrait-marat,
figure-marat, turn-marat, expr-marat; its code `tools/marat.py` — `MARAT`, `MARAT_BODY`, `MARAT_FIG`, `marat_hair`).

## The idea (as Р10, Р27)

The С8 drawing is drawn from 3D (the head a loft of slices, features by (phi, y), the body lofts and tubes), so its
own numbers are the target in every view; the bases (Human Base Meshes' stylised head, Anny's body in the engine) are
fitted to them; the look is a real render on a small set (Blender Cycles, warm key, cool rim, lamps out of focus),
puppet materials, films on twos. Faces are replacement pieces mixed; lids of skin over glass eyes.

The cast's scale: in the style's picture of all six Тим's head is 200 px and Марат's 185; Тим's head in 3D is 0.342 m,
so his is 0.316 m and he stands 1.37 m (4.32 heads) — the tallest and by far the widest.

## What is his own (tools/, in order)

1. `fit_head.py` — as Р27 (the smooth form onto the drawing's loft; the sculptor's nose and ears carried whole onto
   the drawing's): his nose is broad (width × 1.14, length × 1.38 of the base's).
2. `fit_hair.py` — **curls**. The drawing lays curls as a jittered honeycomb of spots over the head
   (`hair.curl_spots`: a point and a radius; the same seed gives the same curls) and draws each as a lit ball with a
   spiral cut. Here every spot is a real ball of clay (a little flattened onto the head; the spiral is in the bump and
   the colour of the material, from the ball's own coordinates): 339 on top, 193 in the beard — the same ones as in
   the drawing. Under them an under-mass closes the gaps: the cap above the drawing's hairline, and for the beard the
   drawing's own beard surface (`beard_at`: on the cheeks down to the jaw, then a bowl hanging from it).
3. `face.py` — his faces: calm, beam (his resting face — a wide smile with teeth), laugh (his joy), surprise, sad,
   anger (`marat.EXPR` + `cast.EXPR`). The mouth has a **tongue** (head.mouth's ellipse low in the open mouth; teeth
   above it) — a piece of its own with a shape per face. **The moustache** is curls too (the same honeycomb, seed 6):
   in the drawing its lower edge rises with a smile so the mouth is never covered, and curls under the edge are
   dropped; here the same curls are squeezed up under that edge, so one set serves every face and the faces mix. The
   thick black brows: head.brow's shape × 1.25, standing off the forehead.
4. `fit_body.py` — Anny's **man** (`moood-man`), scales worked out from the drawing's joints (hips y 2.3 ± 0.32 head,
   knees 3.05, ankles 3.7, shoulders 0.92 ± 0.72, arm 0.62 + 0.6): trunk × 0.89 and 1.15 wide, collarbones × 1.39
   (shoulders far apart), thighs × 0.55, shins × 0.48, forearms 1.12 thick, hands 0.66 long and 0.92 wide (big for
   his arms).
5. `build.py` — clothes from the drawing's numbers:
   - the jacket: the drawing's torso loft as a clean closed grid (its lean — the table `x` — left out: a pose);
     weights from Anny's trunk carried onto the loft, trunk joints only; sleeves = Anny's upper arms carried round
     their bones (r 0.2 → 0.175 head) from a ball at the shoulder to a roll at the elbow; forearms and hands are skin;
   - the apron: the bib cut from the loft a little out by the drawing's outline (`marat.BIB`) with an edge wall, a
     rolled top hem, two straps, a tie round the waist; below it the drawing's apron loft in front of the legs — its
     weights: the hips, and lower down each side a little with its thigh, so a step pushes it forward;
   - the towel over his left shoulder: a strip from the back over the top down the chest, the two terracotta stripes
     by its length coordinate; trousers = Anny's legs carried round the leg bones (r 0.22 → 0.16), shoes lofted.
6. `render.py` — materials: the curl (ball with a spiral), a dark under-mass, white jacket cloth, terracotta apron
   cloth, terry towel with stripes, his warmer skin; his set (`build.py` LOOK: warm brown, seed 14).
7. `stills.py` (turn, portrait, figure — Kimodo's wave, frame 40: he raises his right arm as in the drawing —, expr),
   `films.py` (turn, walk, wave, face, dance), `steps.py`, `pics.py`, `viewshot.mjs`, `peek.py`.

## How to repeat

```
cd to3d/r28-s8-marat/tools
C=/home/user/cache/to3d-r28-s8-marat; B=/home/user/cache/blender/blender      # python3 with numpy, scipy, igl, Pillow
$B -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
   --python hbm_export.py -- $C/hbm.npz
python3 paint.py; python3 fit_head.py; python3 fit_hair.py; python3 face.py; python3 build.py     # ~1 min
for s in turn figure expr portrait; do python3 stills.py $s 28; done; python3 pics.py
for f in turn walk wave face dance; do python3 films.py $f 12; done
python3 steps.py
(cd $C && npm install three@0.160.0); node viewshot.mjs OUT '[{"name":"a","set":{"motion":"wave","t":1.3}}]'
```
Heavy runs go through `CACHE/heavy.sh` (whichever of the three shared locks is free).
The viewer: serve the repository's root (`python3 -m http.server`) and open `to3d/r28-s8-marat/tools/web/view.html`.

## Licences of the bases

| What | Licence |
|---|---|
| Human Base Meshes bundle v1.4.1, `GEO-head_stylized` and its eyes | CC0 (Blender Foundation) |
| Anny man (moood-man, in the engine), SOMA skeleton and weights | Anny (NAVER, Apache-2.0), MakeHuman (CC0), SOMA rig (NVIDIA, Apache-2.0) — `engine/data/soma/NOTICE` |
| Kimodo motions (walk, wave, dance, idle, bow) | `engine/motions` (moood studio) |
| The drawing and its code | ours (`styles/s8-stopmotion`) |
| three.js 0.160 (viewer) | MIT |

No neural images; StdGEN not used.

## Alive (as Р10, Р27)

`tools/web/face.mjs`, `life.mjs`: replacement pieces mixed (lips, the dark, tongue, teeth, the moustache's curls go
with the mouth's shapes), lids over the glass eyes (the sheet's lid numbers × 1.3: his eyes narrow when he laughs, and
the opening is cut a little larger than drawn), blinks, the eyes' holds and jumps, the gaze leading the head, speech,
expressions by a spring. His resting face is `beam`. Motions (engine/motions only): wave (his), walk, idle (the face
close-up), bow frame 0 levelled for the stills; dance, stomp and the rest in the viewer.

A fix that Р27 got too: in the stills the eyes are now really on the camera. Р10's `stills.py` turned the eyes to
his left, while the camera of a view stands on his right (render.py) and the head's own part of the drawing's yaw
turns it further away — so the eyes looked away from the lens; here the gaze comes back to the camera by both.

## What is weak (honestly)

- The mouth is a piece laid on the face, not a cavity: the big laugh reads from the front by its dark, teeth and
  tongue, but from the side it has no depth.
- The curls are the drawing's own honeycomb, and as real balls they read more regular and beady than the drawn ones
  (which overlap and hide each other); the hair's top is a little helmet-like.
- No ladle (Anny's open hand has no grip) and the fist-on-hip pose of the figure is not made: the figure is Kimodo's
  wave, the raised arm as drawn. In the wave the head leans far toward the arm (the engine's arms-out-of-head
  correction on a short arm and a big head).
- Clothes are shells: the jacket is a stiff barrel, the apron below the waist is skinned to hips and thighs (it
  stretches in a wide step, it doesn't swing), the towel is stuck to the chest; sleeves and trousers have no folds.
- The skin is paler than the drawing's warm clay; the forearms are Anny's (thickened), the hands hers.
- The viewer's materials are simpler than the renders; it has 91 000 vertices and is slower to start than Р10's.
