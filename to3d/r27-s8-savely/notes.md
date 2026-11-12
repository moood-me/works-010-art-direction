# Р27 — Савелий Петрович, кукольная анимация (С8): from the drawing to 3D

What was done, why, and how to repeat it. Brief: `docs/briefs/to3d.md`, "Third round": each style gets two more
characters in 3D beside its first one. For С8 the first is Р10 (Тим, `to3d/r10-s8-tim`); this is the second, made
from Р10's code (copied into `tools/` and changed for him). The drawing: `styles/s8-stopmotion` (portrait-savely,
figure-savely; its code `tools/cast.py` — `SAVELY`, `SAVELY_BODY`, `SAVELY_FIG`, `savely_hair`, `props.py`).

## The idea (as Р10)

The С8 drawing is drawn from 3D: the head is a loft of elliptic slices, the features are laid on it by (phi, y), the
body is lofts and tubes with numbers. So the drawing's own numbers are the target in every view at once; the bases
(Human Base Meshes' stylised head, Anny's body in the engine) are fitted to them; the look is a real render — Blender
Cycles on a small set (warm key, cool rim, lamps out of focus behind), puppet materials, films on twos (12 fps). Faces
are replacement pieces mixed, lids of skin over glass eyes.

The scale of the cast: in the style's picture of all six Тим's head is 200 px and Савелий's 182; Тим's head in 3D is
0.342 m, so his is 0.311 m and he stands 1.21 m (3.88 heads) — a little taller than Тим, as drawn.

## What is new against Р10 (tools/, in order)

1. `fit_head.py` — the same two-level fit (smooth form onto the drawing's loft, the sculptor's detail back), and:
   - **the nose**: Р10 shrank the base's nose; his is a long big bulb. The base's own nose (as the sculptor made it) is
     stretched to the drawing's nose (root → tip height × 1.35, how far it stands out × 0.86, width × 1.02), set with
     its tip on the drawing's tip, and the skin round it follows by a biharmonic blend (`fix_nose`). Tried first: a
     thin-plate warp of the fitted nose by its ridge and wings — the wings crumpled.
   - **the ears**: Р10 named them weak (smaller than drawn). Now the base's own ear is carried whole (scaled to the
     drawing's height × 1.4, turned out by the drawing's angle + 30°), and the skin round it blends biharmonically
     (`fix_ears`); a soft weight, as before, dragged a skirt of skin out with the lobe on this bald head.
   - less of the base's cheek detail beside the nose (K_NOSE 0.25, K_FACE 0.2): they read as scars on a smooth mask.
2. `fit_hair.py` — the drawing's 21 flat tufts (its page calls them papery) became a wreath of 56 leaf-shaped locks
   in two layers from temple to temple round the back, along the drawing's line: narrow roots sunk into the skull,
   over the ears they leave the head and flick out and up, at the back they lie down to the nape. Paths by the
   drawing's own builders (`hair.surf_path`, `hair.fall`). The first try — the drawing's locks as they are — looked
   like a row of claws.
3. `face.py` — the faces are his: calm, stern, grumpy, tired, joy, surprise, sad, anger (`cast.EXPR`). The bushy
   brows (`head.brow` with `brow_droop`) are thick slabs standing 0.024 head off the forehead. **The moustache**
   (`props.moustache`: the same upper and lower curves, the ends lifted by a smile) is a rounded body on the
   drawing's head, one more replacement piece that goes with the mouth's shapes (a shape per face and per speech
   shape; it rides up a little with an opening mouth) — made a little bigger than drawn (w 0.215, thick 0.115):
   under a 3D nose it reads smaller.
4. `paint.py` — the skin's picture: blush, socket tone, the red nose (`nose_tint`), and the sculpted wrinkles of the
   drawing (three on the forehead, crow's feet) and the two bags under each eye as darker lines + `bump.png`, a
   height picture the skin material reads as grooves.
5. `fit_body.py` — Anny's **old man** (`moood-oldman`), the scales along and across each bone worked out from the
   drawing's joints (hips y 2.05 ± 0.22 head, knees 2.7, ankles 3.27, shoulders 0.8 ± 0.52, arm 0.72 + 0.66):
   trunk × 0.77, thighs × 0.51, shins × 0.41, arms × 0.81.
6. `build.py` — clothes from the drawing's numbers, built differently from Р10's sweater:
   - **the waistcoat is the drawing's own torso loft as a clean grid** (160 × 84), cut open in the drawing's V by a
     signed distance to the V's outline (clean edges), with a wall at its edges (a thickness) and a closed bottom.
     Its weights are taken from Anny's trunk carried out onto the same loft (nearest eight vertices, smooth), trunk
     joints only: a stiff waistcoat on a round body, so arms and legs don't drag it;
   - the shirt: its front inside the V (the loft a little in), a collar stand round the neck, two collar points
     standing over the waistcoat's edge, the tie with a knot, cuffs; the sleeves = Anny's arms carried round their
     bones to the sleeve's radius, each coming out of a ball at the shoulder joint (a puppet's joint under cloth);
   - three buttons, the watch chain (a gold tube with links in the bump); the trousers = Anny's legs carried round
     the leg bones (hanging straight), hems; shoes lofted round the feet;
   - the half-moon glasses (`props.glasses 'half'`): gold wire rims, a bridge, temples to the ears, thin lenses.
7. `render.py` — materials: woven cloth (two crossed waves + dye unevenness) for waistcoat, shirt, tie, trousers;
   white sculpted hair for tufts, brows and moustache; gold metal; a lens (clear with a little glare); his set
   (`build.py` LOOK: warm brown, seed 5).
8. `move.mjs` — `turns: [{joint, axis, deg}]`: a limb turned on top of the pose, for the one still that shows the
   drawing's pose (the figure: his left forearm brought up in front of the belly, where he holds the watch).
9. `drawn.py` — the style's page has no turnaround and no expression sheet of him (its notes: dropped, the flat
   moustache and tufts don't hold in profile). To compare all the same views, the two sheets are made by the style's
   own functions (`build.py turnaround()`, `expressions()`) into the cache; nothing in the style's folder is touched.
10. `stills.py`: the eyes are now really on the camera. Р10's turned the eyes to his left, while the camera of a view
    stands on his right (render.py) and the head's own part of the drawing's yaw turns it further away — so the eyes
    looked away from the lens; here the gaze comes back to the camera by both.
11. `stills.py`, `films.py` (turn, walk, face, bow), `steps.py`, `pics.py`, `viewshot.mjs`, `peek.py` (quick clay
    looks while building). Heavy runs go through `CACHE/heavy.sh` (whichever of the three shared locks is free).

## How to repeat

```
cd to3d/r27-s8-savely/tools
C=/home/user/cache/to3d-r27-s8-savely; B=/home/user/cache/blender/blender      # python3 with numpy, scipy, igl, Pillow
$B -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
   --python hbm_export.py -- $C/hbm.npz
python3 paint.py; python3 fit_head.py; python3 fit_hair.py; python3 face.py; python3 build.py     # ~1 min
python3 drawn.py                                                      # the drawing's turn and expression sheets
for s in turn figure expr portrait; do python3 stills.py $s 28; done; python3 pics.py     # ~1 min a sheet
for f in turn walk face bow; do python3 films.py $f 12; done         # 20–40 s a frame on the shared machine
python3 steps.py
(cd $C && npm install three@0.160.0); node viewshot.mjs OUT '[{"name":"a","set":{"motion":"walk","t":1}}]'
```
The viewer: serve the repository's root (`python3 -m http.server`) and open `to3d/r27-s8-savely/tools/web/view.html`.

## Alive (as Р10)

`tools/web/face.mjs`, `life.mjs`: replacement pieces mixed (the pieces that go with the mouth are listed in the face
pack's header: lips, the dark, teeth, the moustache), lids turning over the glass eyes, the eyes turning; blinks at
uneven intervals, the eyes' holds and jumps, the gaze leading the head, speech as syllable shapes, expressions by a
spring — all from a seeded stream. Motions (engine/motions only): walk, bow (a gentleman's), idle (the face close-up),
bow frame 0 levelled for the stills.

## Licences of the bases

| What | Licence |
|---|---|
| Human Base Meshes bundle v1.4.1, `GEO-head_stylized` and its eyes | CC0 (Blender Foundation) |
| Anny old man (moood-oldman, in the engine), SOMA skeleton and weights | Anny (NAVER, Apache-2.0), MakeHuman (CC0), SOMA rig (NVIDIA, Apache-2.0) — `engine/data/soma/NOTICE` |
| Kimodo motions (walk, bow, idle) | `engine/motions` (moood studio) |
| The drawing and its code | ours (`styles/s8-stopmotion`) |
| three.js 0.160 (viewer) | MIT |

No neural images; StdGEN not used.

## What is weak (honestly)

- The skin is paler and smoother than the drawing's ruddy clay; the face is rounder and softer — a kinder old man than
  the drawn grump.
- The pocket watch is not made: the hand is Anny's open hand (no grip), so in the figure he raises an empty hand.
- Clothes are shells: the waistcoat is stiff by design, but its hem doesn't follow the legs (in a wide step the legs
  come out from under it oddly), sleeves and trousers are smooth tubes without folds; hair is rigid.
- Kimodo's `idle` stoops him hard (a known weakness), so stills use `bow` frame 0; the mouth is a piece laid on the
  face, not a cavity; the far lens of the glasses sometimes catches a dark reflection.
- The viewer's materials are simpler than the renders (no light under the skin, no bokeh).

Viewer note: the cloth's weave of the renders is left out in the viewer (finer than a screen pixel, it turned to moiré).
