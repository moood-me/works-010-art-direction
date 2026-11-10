# Р38 — Марат, японская гравюра: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, third round; brief: `docs/briefs/to3d.md`, "Third round"):
Марат of style С13 (`styles/s13-ukiyo-e`) — the cook, the biggest of the cast — made a 3D character that moves by Kimodo
through the engine and is printed every frame as a sheet of the style, the way Р37's Аня is (`to3d/r37-s13-anya`: read
its `notes.md` first — the idea, the renderer and what the style keeps and doesn't keep in 3D are told there). Asked
for by Pavel through the orchestrator: the second character of С13 (for a while the task named Кира instead; Pavel's
last word was Марат).

## What is shared and what is his own

Shared with Р37, the same files: `tools/web/print.js`, `kit.js`, `face.js`, `ui.js`, `head.py`, `shells.py`,
`mesh.py`, `pack.py`, `make_pics.py`, `shots.mjs`, `look.sh`, `viewer_check.mjs`.
His own: `drawing.py` (the drawing's numbers), `build.py` (the form), `web/char.js` (blocks, patterns, face,
expressions, the jaw, the beard's hairs), `who.py` (the sheets' scales, the figure's pose, the films).

- **The form is Р36's build** (`to3d/r36-s12-marat`: the same man in pen and watercolour) with the С13 drawing's
  numbers. Here he is eight heads tall and long-legged (1.22 mm a head unit, 1.92 m), so nearer to Anny's man than in
  С12: the joints are moved to the drawing's (legs apart, the trunk 1.5 times a man's — a barrel from hips to heavy
  shoulders, a short neck), each limb's skin turns, stretches and thickens with its bone. Of Anny's skin the forearms
  and the hands are seen (real fingers, as Р37 — the print draws each finger), and the feet, smoothed and swollen
  into clogs.
- **Clothes are shells of the drawing's sizes**: the jacket — one loft from the collar over round shoulders, the belly
  leading in front; rolled sleeves; trouser legs down into the clogs; the apron — a bib that widens to the skirt's
  width at the waist, and a skirt to the shins, open behind, each its own shell so the waist is a line; straps; the
  towel over the shoulder.
- **Patterns printed flat** (`char.js`, the drawing's own): waves (`seigaiha`) on the apron, the chequer board on
  the trousers, stripes on the towel. The white jacket is the print's white — a flat colour with the heaviest line.
- **Curls as form.** The hair is a dome over the skull with round bumps (Р36's): its silhouette is the drawing's
  scalloped edge from any side; a bump's silhouette over the hair itself is a short light arc (the drawing's grey
  arcs), and a few bumps carry one more.
- **The beard** is a smooth cup round the jaw and over the mouth, open under the nose; the bare cheek follows the
  profile's inner edge (from the mouth's corner up to the ear) — taken from the front view alone it was a black box
  from the side. Its edge is not a line but `kit.py`'s `fringe`: separate hairs growing out of the dark, wherever the
  edge is seen (against the cheek, the jacket, the ground) — `onContour` in `char.js`.
- **The face**: eyes closed into arcs by the laugh, heavy brows pressed at the inner end, the broad nose's stroke laid
  on the 3D nose, the open mouth with a white row of teeth and the tongue drawn on the beard (its place is on the
  head under the beard). **The jaw drops** (the engine's `Jaw` joint; the lower face and the lower beard are weighted
  to it): the grin 0.45, the laugh 1, speech by its syllables. The cheeks' bokashi is printed on skin only (the skin's
  block as a mask — `print.js`, for both characters).
- Lines of the form: the apron's folds (the drawing's darker terracotta), the jacket's flap, two buttons.

## Repeat

```
cd to3d/r38-s13-marat/tools
C=/home/user/cache/to3d-r38-s13-marat; mkdir -p $C; (cd $C && npm install three@0.160.0)
/home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
    --python hbm_export.py -- $C/hbm_head.npz        # the base head as arrays (once; here Р37's file was copied — the same)
python3 build.py                # → ../data/marat.json, marat.bin
./look.sh                       # a quick sheet to look at ($C/look.json: as Р37's, with h 2.2, cy 0.98 and h 0.62, cy 1.72)
python3 make_pics.py stills     # ../pics: compare, overlays, portrait, steps, back, expressions
python3 make_pics.py films      # ../pics: turn, walk, wave, talk (12 pictures a second)
node viewer_check.mjs $C/viewer.png walk      # the viewer with its controls (through a shared lock)
```
Heavy runs go through the shared locks (`make_pics.py` and `look.sh` take the first free one). By hand: serve the
repository root, open `to3d/r38-s13-marat/tools/web/view.html`.

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`; Anny: NAVER, Apache-2.0; MakeHuman
  CC0; SOMA rig: NVIDIA, Apache-2.0).
- Kimodo motions: `engine/motions` (walk, wave, idle).
- Р36's build, Р12's renderer and face timing, the С13 drawing and its code (`kit.py`, `parts.py`, `marat.py`,
  ported): this repository. three.js 0.160.0: MIT. No neural images.

## Honest state

See the page's verdict (`entry.json`); in short: the front and the three-quarter read as the drawing's Марат; the
profile, the towel and the hands are the weak places; the ladle is not made; the body is a smooth barrel under a
skinned apron, not cloth.
