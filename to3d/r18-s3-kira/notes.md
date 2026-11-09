# Р18 — Кира, графичный стиль: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, round three; brief: `docs/briefs/to3d.md`, its part
"Third round"): Кира of style С3 (`styles/s3-graphic`, drawn in round three of the styles) built in 3D the way Р1 Аня
was, with what Р17 Тим (`to3d/r17-s3-tim`, made just before by the same agent) changed: the head on one designed form,
limbs as tubes, built shoes, colour bands cut per pixel. Its code is a copy of Р17's tools, with Кира's own
`shapes.py`, `hair.py`, `build.py`, `web/face.js`.

## How it is built (and what each base gave)

- **The drawing** is the style's own turnaround: `tools/shapes.py` names the shapes of
  `styles/s3-graphic/tools/kira.py` that the 3D is fitted to (those local to `body_f()`/`body_s()` are copied as they
  are there), and says where the head stands in the figure (pitched 12° down about its neck point, 40 units forward,
  14 down) and how the upper body leans (6° back about the hips, `kira.LEAN`).
- **The slouch is in the rest itself**, not a pose layer: `build.py` puts the joints where the profile is drawn — the
  legs slant back (the feet 57 units behind the hips), the spine leans back from the hips, the neck goes forward, the
  head is pitched down. The engine's frames are not touched ("places are the designed rest; frames are the
  retargeting reference", `engine/README.md`), so Kimodo's motions carry the slouch along.
- **Head — Blender Human Base Meshes, stylised head** (CC0), fitted as in Р17 (`tools/head.py`): heights by landmarks,
  then onto a superellipse at every height (half-width from `kira.FACE_F` and the neck, front and back from
  `kira.FACE_S` and the profile's neck), a fifth of the base's relief kept; the nose is the profile's wedge; the ears
  small (under the hair). Built upright in the head's own units; `build.py` then places it (`place`).
- **Face — the drawing's own parts, live** (`tools/web/face.js`): `eye` (heavy flat lid, thick lash with a wing, the
  tired line under it), `brow`, the mouths of `kira.py` as one mouth of a few numbers (width, bend, skew — the smirk is
  a shut mouth with one corner up —, opening, round, box, teeth), the lower lip, the corner ticks. Speech shapes are
  small: she talks through her teeth. Blinks, saccades, gaze leading the head, blended expressions: Р1's `LiveFace`.
- **Skeleton and trunk weights — Anny `moood-girl`** (`engine/data`). Legs: thin tapering tubes on the bones
  (narrow trousers). Hands: mittens, rigid on the hand; only the fingertips come out of the sleeves.
- **Clothes from the drawing's silhouettes**: the hoodie (a loft: `HOODIE_F` width, `HOODIE_S` depth leaned back; a
  darker hem; weights from the nearest skin of Anny's trunk, the arms' and the head's share given to chest and neck),
  the hood (a closed cushion from `HOOD_F`/`HOOD_S`), sleeves (wide tubes down to the knuckles, a darker cuff, a round
  cap at the shoulder), the pocket (a patch raised off the front, its outline the drawn one). The pocket's outline,
  two folds of the chest and the drawstrings are thin cords on the surface — the flat look has no other way to put a
  line inside a form.
- **Boots**: a shaft round the ankle (shin → foot), the foot a loft rigid on the foot, the sole cut by height in the
  shader (`bands`), four lime strips across the shaft for laces. **Headphones**: the cups (dark rim, lime face) lie on
  the hood's front, the band goes behind the neck; they go with the chest.
- **Hair** (`tools/hair.py`): a cap over the designed head that hangs straight from the head's widest places (a bob);
  its lower edge is the drawing's: in front the lowest point of `NEAR_F` and `FRINGE_F` at each x (the fringe slanting
  over her left eye, the lock by her right cheek), behind the profile's choppy ends; three flat cones for tufts.
- **Look, motion, viewer**: Р17's `web/char.js` and `web/ui.js` unchanged but for names and sizes.

Neural models were not used.

## Repeat

```
cd to3d/r18-s3-kira/tools
C=/home/user/cache/to3d-r18-s3-kira; mkdir -p $C
# three.js for the headless pictures is taken from Р17's cache (shots.mjs): (cd /home/user/cache/to3d-r17-s3-tim && npm i three@0.160.0)
/home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
   --python hbm_export.py -- $C/hbm_head.npz
python3 build.py $C/out                                 # the packs: kira.json/.bin, kira-head (the head upright, for the steps)
python3 bases.py $C/out                                 # the bases as they come
python3 compare.py /cache/to3d-r18-s3-kira/out/kira.json $C/cmp
python3 make_pics.py                                    # ../pics: pictures and the turn
cp $C/out/kira.json $C/out/kira.bin ../data/
python3 make_live.py                                    # ../pics: the live face and the motions (reads ../data)
```

`web/view.html` opens `../../data/kira.json` with the controls; serve the repository root.

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`; Kimodo's SOMA skin Apache-2.0).
- Kimodo motions: `engine/motions`.
- The drawing and its code: this repository (`styles/s3-graphic`).

## Honest state, what is weak

- The drawn front and profile disagree about the hair by the cheek (front: a lock over the face's edge; profile: hair
  only behind the ear). The 3D follows the front, a little later round the head; in profile the lock hides the cheek.
- In profile the face is a painted layer seen from its edge (as Р1, Р17).
- The neck shows long when she walks: the head is carried forward as drawn, and in motion that is more visible.
- Both arms hang; the drawing's hand in the pocket is not made. Hands are mittens.
- Hoodie, hood and hair are rigid shells: no folds, and sitting crumples the hoodie into a lump.
- Legs are straight; the drawing's knees are a little bent. Side tufts of the hair by the cheeks were tried as cones
  and removed (they read as bows).
