# Р17 — Тим, графичный стиль: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, round three; brief: `docs/briefs/to3d.md`, its part
"Third round"): Тим of style С3 (`styles/s3-graphic`) built in 3D the way Р1 Аня was (`to3d/r1-s3-anya`: its code was
the start), from ready bases fitted to the drawing, and played by Kimodo's motions through the engine. The second
character of this round in the same style is Р18 Кира (`to3d/r18-s3-kira`).

## What called for what

- **The style page has only Тим's three-quarter view**, and this way of building needs two flat views. So the front
  and the profile are drawn here, by the style's rules and with its code (`tools/views.py`: `lib.py`, `face.py` and
  `tim.py`'s colours from `styles/s3-graphic/tools`). The 3D is fitted to them; the style's three-quarter is the
  measure it is judged by. The front view's face is not drawn twice: it is the picture `web/face.js` draws
  (`tools/face_png.mjs`), the same code that draws the 3D head's face.
- **Р1's page names its head as fitted by slices** (lumpy), its shoes as Anny's feet repainted, colours smeared over big
  triangles. Done better here: the head lies on one designed form; shoes, socks and mittens are built; stripes, the
  sock's line and the sole are cut per pixel.

## How it is built (and what each base gave)

- **Head — Blender Human Base Meshes, stylised head** (CC0; `tools/hbm_export.py` takes it out of the bundle).
  `tools/head.py`: heights by landmarks (neck end, chin, eye line, crown → the drawing's y 152, 116, 14, −106, a
  monotone curve between them); then every vertex goes toward one designed form — at its height a superellipse
  (power 2.25) whose half-width is the front view's (`views.HEAD_F`, `NECK_F`) and whose front and back are the
  profile's (`views.PLANE_S`); a fifth of the base's own relief is kept on it (`keep=0.2`). The nose is the profile's
  own bump (`HEAD_S` minus `PLANE_S`). The ears are the base's own, rigid, made Тим's size and turned out 36°
  (`EAR` in `build.py`), joined by a smooth weight. Eye sockets and lips are laid flat where the face is painted
  (`flatten`). The base gave: topology, ears, the neck, a fifth of the relief.
- **Face — the drawing's own parts, live** (`tools/web/face.js`): `eye`, `brow`, `closed_eye` of
  `styles/s3-graphic/tools/face.py` as `tim.py` calls them (no lash wing), the mouths of `tim.py` turned into one mouth
  of a few numbers (width, opening, smile, round, box, teeth, skew of the grin; the gap of the missing tooth always),
  the button nose, freckles, blush, the plaster. Drawn every frame into the head's painted layer (front projection).
  Blinks, saccades, gaze leading the head, speech, blended expressions: Р1's `LiveFace`, with the left and right brow
  and lid apart (Тим's resting face is asymmetric).
- **Skeleton and trunk weights — Anny `moood-child` from `engine/data`** (SOMA joints, frames, weights).
  Joints moved to the drawing in `tools/build.py` (a short barrel of a trunk, short legs wide apart, shoulders outside
  the barrel, a big head on a short neck); frames are not touched, so Kimodo retargets as for any engine body.
- **Limbs — tubes along the bones**, as drawn (Anny's limbs are anatomy; tried first: chubby knees and calves that the
  drawing does not have). Their weights are set by the place along the bone. Hands: mittens, rigid on the hand.
- **Clothes — shells from the views' silhouettes**: the shirt (`SHIRT_F` width, `SHIRT_S` depth, a collar ring; weights
  from the nearest skin of Anny's trunk, the arms' share given to the chest so the trunk does not follow the arms),
  short sleeves (tubes on the upper arm with a round cap), the shorts (the trunk's part and a wide leg each), socks,
  sneakers (a loft along the foot, rigid on the foot). The plaster on the knee is a patch on the leg's surface.
- **Hair** (`tools/hair.py`): one cap over the designed head, 9–15 units thicker; its lower edge is the drawing's: in
  front the fringe's teeth read off `views.HAIR_F` (its lowest point at each x), toward the temples the higher of the
  two views' edges, behind the profile's (`HAIR_S`), the nape a little lower; the last row lies on the skin. The
  cowlick, the tuft at the temple and those at the nape are flat cones.
- **Look** (`tools/web/char.js`, three.js 0.160; Р1's viewer made general): flat colour per vertex, one stepped shade,
  a coloured outline (inverted hull), the face layer. New: the pack's header lists `bands` — intervals of a per-vertex
  coordinate `band` with their colours; the shader cuts them per pixel (the shirt's stripes by the drawing's height,
  the sleeve's stripe by the distance along the arm, the sock's line, the sole).
- **Motion**: the pack is made an engine body and played by the engine's retargeting and skinning (`cor`), Kimodo's
  motions from `engine/motions`: walk, run, jump, wave, stomp, dance, idle.

Neural models were not used.

## Repeat

```
cd to3d/r17-s3-tim/tools
C=/home/user/cache/to3d-r17-s3-tim; mkdir -p $C
(cd $C && npm i three@0.160.0)                          # three.js for the headless pictures (shots.mjs routes the CDN to it)
/home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
   --python hbm_export.py -- $C/hbm_head.npz
python3 build.py $C/out                                 # the pack: tim.json/.bin
python3 bases.py $C/out                                 # the bases as they come, for the steps
python3 compare.py /cache/to3d-r17-s3-tim/out/tim.json $C/cmp   # the turnaround (views.py) beside and over the 3D
python3 make_pics.py                                    # ../pics: pictures and the turn
cp $C/out/tim.json $C/out/tim.bin ../data/
python3 make_live.py                                    # ../pics: the live face and the motions (reads ../data)
```

`shots.mjs` serves `/home/user/` and drives `web/view.html?pack=…` with Playwright (software WebGL). Without `?pack`,
`web/view.html` opens `../../data/tim.json` with the controls (`web/ui.js`); serve the repository root.

Files: `views.py` (the front and the profile, the turnaround sheet), `drawing.py` (paths sampled, the scale),
`head.py`, `hair.py`, `build.py`, `mesh.py`, `pack.py`, `overlay.py`, `compare.py`, `make_pics.py`, `make_live.py`,
`bases.py`, `face_png.mjs`, `shots.mjs`, `run.sh` (build and look), `web/` (the viewer). `render_svg.mjs` is Р1's,
unused here. The pack format is Р1's `r1/character`, version 2: plus `bands` in the header.

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`; Kimodo's SOMA skin Apache-2.0).
- Kimodo motions: `engine/motions`.
- The drawing and its code: this repository (`styles/s3-graphic`).

## Honest state, what is weak

- The front and the profile are mine, not the style page's; only the three-quarter is the style's own drawing.
- In profile the face is flat: the mouth and the eye are a painted layer seen from its edge (as Р1). The button nose
  is small.
- Sleeves are balls where the drawing has angular trapezoids.
- Short arms: Kimodo's wave ends at the ear. A wide stance as drawn: Kimodo's step crosses the legs.
- Clothes and hair are rigid shells; no fingers.
- The knee plaster has no drawn lines; hair strands' lines of the drawing are not there.
