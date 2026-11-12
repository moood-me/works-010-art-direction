# Р36 — Марат, перо и акварель: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, third round; brief: `docs/briefs/to3d.md`, "Third round"):
Марат of style С12 (`styles/s12-ink-watercolour`) — the cook, the biggest of the cast — made a 3D character that moves
by Kimodo through the engine and is drawn every frame with the style's own pen and wash code, as Р12's Аня
(`to3d/r12-s12-anya`) and Р35's Тим (`to3d/r35-s12-tim`) are. Asked for by Pavel through the orchestrator: each style
gets two more characters in 3D, one of them of the two new ones.

## What is shared and what is his own

Shared with Р35 (made in the same run, see its `notes.md`): the renderer `tools/web/figure.js` (Р12's `anya.js` made
to take any character), `pen.js`, `face.js`, `ui.js`, `head.py`, `shells.py`, `mesh.py`, `pack.py`, `shots.mjs`.
His own: `drawing.py` (the drawing's numbers), `build.py` (the form), `web/char.js` (washes, face, expressions, jaw).

- **A body far from Anny's.** `build.py` takes Anny's man (`engine/data/bodies/moood-man`) and moves its joints to
  the drawing's (head units → metres: 1.73 mm a unit, 1.92 m tall, a little over four heads): the legs short, thick
  and apart — the hips put as high as the long apron allows (0.76 m), the knees just above its hem; the trunk 1.6
  times a man's — a barrel from hips to heavy shoulders; no neck to speak of; thick arms. Each limb's skin turns and
  stretches with its bone and is made thicker; the trunk's skin is only a carrier of weights. Of Anny's skin the
  drawing shows the bare forearms; the feet, smoothed and swollen, are the clogs.
- **Clothes are shells of the drawing's sizes**: the jacket — one loft from the stand-up collar over round
  shoulders, the chest and belly leading in front, widest below the waist; rolled sleeves (thick tubes with a fuller
  ring at the elbow); trouser legs; the apron — a bib and a skirt to the shins, open behind, each its own shell so
  the waist is a drawn line; two straps and the towel over the shoulder — flat bands laid on the jacket. Fists are
  big mittens. The skirt is kept off the legs in a step (Р1's push, now for an open shell).
- **White is paper.** The jacket and the towel have no wash; only their shaded side (the unseen picture's "in shade"
  bit) gets `marat.py`'s warm grey, kept a little inside the part's edge. The towel's two stripes are a coordinate
  along it.
- **Curls as form.** Hair: a dome over the skull cut along the drawing's hairline; beard: a cup round the jaw, wider
  than the face and deeper than the chin, open behind, leaving the cheeks and the mouth bare in front. Both carry
  round bumps (domes on seeds spread over the surface), so their silhouette is the drawing's row of curls from any
  side; a bump's silhouette over the hair itself is a thin stroke; a few bumps carry `parts.py`'s `curl()` hook,
  drawn where seen. Dark hair is two layers of wash, as in the drawing.
- **The face** (`char.js`, `head_front`'s numbers): `marat.py`'s `grin()` — teeth are paper left white, the dark of
  the mouth, a tongue when he laughs — and the moustache are drawn in one frame on the head, in the beard's gap; thick
  brows of two strokes; eyes that squint in the laugh, with the cheek's line under them and crow's feet. **The jaw
  drops** (the engine's `Jaw` joint; the lower face and the lower beard are weighted to it) by `marat.py`'s OPEN: the
  smile 0.3, the laugh 1, speech by its syllables — so the beard opens with the mouth.
- **Lines of the form**: the apron's folds and pocket, the collar's V and the flap, two buttons (strokes and marks
  on mesh vertices, smoothed in the picture).
- **`head.py`**: the cheeks' push forward (Р12's) now follows the face's front without the nose — with a big nose it
  swallowed the nose (found here; Р35 has the same fix).

## Repeat

```
cd to3d/r36-s12-marat/tools
/home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
  --python hbm_export.py -- /home/user/cache/to3d-r36-s12-marat/hbm_head.npz      # the base head as arrays (once)
(cd /home/user/cache/to3d-r36-s12-marat && npm install three@0.160.0)              # three.js for the headless shots
python3 build.py                # → ../data/marat.json, marat.bin
python3 make_pics.py stills     # ../pics: compare, overlays, steps, back, expressions
python3 make_pics.py films      # ../pics: turn, walk, wave, stomp, talk (12 drawings a second)
```
Heavy runs go through the shared lock (`flock /home/user/cache/heavy.N.lock …`). By hand: serve the repository root,
open `to3d/r36-s12-marat/tools/web/view.html`.

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`; Kimodo's SOMA skin Apache-2.0).
- Kimodo motions: `engine/motions` (walk, wave, stomp, idle).
- Р12's renderer and the С12 drawing and its code (`kit.py`, `parts.py`, `marat.py`, ported): this repository.

## Honest state

- Reads as the drawing's Марат: the bulk, the white jacket of bare paper, the terracotta apron, the black curls and
  beard, the laugh with teeth and tongue; the figure's pose (leaning back, an arm up, a fist on the hip) repeats well.
- The drawing's turnaround shows shoulders far wider than its own figure sheet; the figure is followed, so in the
  turnaround's views the 3D shoulders are narrower and the head larger than drawn.
- The pen line round the dark hair and beard is nearly lost in the dark wash (the drawing leaves a light gap and a
  bold scalloped line); the beard's upper edge on the cheek is ragged; the hairline is a straight cap.
- Small mouths (surprise, sadness, anger) sit under the moustache as a small spot; from the profile the moustache and
  mouth are small.
- The body is a smooth barrel: no belly line breaking the apron as in the drawing; the apron is a skinned shell, not
  cloth; mittens, not hands; the ladle is not made.
- Kimodo's motions are a man's: with short legs and a long trunk the steps are short, and thick arms pass through
  the belly's sides in a swing.
- As in Р12: the line follows the form exactly, washes follow the seen shape; in films the line "boils" and the
  pigment stays on the screen.
