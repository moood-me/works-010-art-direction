# Р5 — Аня, «Клаус», в 3D

What was done, how to repeat it, and the licences of the bases.

## Why

The brief (`/home/user/cache/BRIEF-to3d.md`): make one of our drawn characters a good 3D character from good ready
bases fitted to the drawing, not by a neural net. This one is Аня in style С2 «Клаус» (`styles/s2-klaus`): 2D drawn as
volume — flat colour lit like 3D, warm key against a pink-lilac shadow, soft shadow edge, cast shadows from hair and
nose, a rim, grain. The material had to give that light, not plastic.

## How it is built (tools/)

- `hbm_export.py` (Blender 4.5, background): the stylised head of Human Base Meshes (`GEO-head_stylized` and its eyes)
  as arrays → `/home/user/cache/to3d-r5-s2-anya/hbm.npz`.
  `blender -b human_base_meshes_bundle.blend --python tools/hbm_export.py -- hbm.npz`
- `drawing.py`: reads the drawing's own shapes by running `styles/s2-klaus/tools/anya.py` with a recorder in place of
  `kit.Doc` (every `form()` gives its outline and colour), parses the SVG paths to polygons (shapely).
- `head.py`: eye sockets and lips cut out by ellipses and filled with a bi-harmonic patch (the face continues smoothly;
  eyes, brows, mouth are painted); vertices welded; then the fit: heights matched by landmarks (crown, brow, eyes, nose
  tip, mouth, chin, neck), and at every 5 drawing units of height the base surface is sliced: its side-most point, the
  side-most point of its front part (the face, below the mouth), the front and back of its middle line are sent to the
  drawing's front outline, face outline and profile; an RBF (|r| kernel + affine, regularised) moves the whole head;
  3 passes. Ears made smaller and pulled in. Scale: 1 drawing unit = 0.86 mm. The neck is made 7 cm wide, not the
  drawing's 4 cm (a choice: the drawn one reads as a stick in 3D). `python3 head.py out.png` and `look_head.py` show
  the fitted clay over the drawing.
- `hair.py`: the hair as a shell lofted through rings: per height its width from the front view's hair outline (centre
  shifted to the parting), front and back from the profile, open in front where the face's own outline is; pushed out
  of the head (≥4 mm, more on the skull), smoothed along and across, given a thickness (6 mm, thinner at the tips),
  a dome over the top with its peak over the parting.
- `features.py`: the painted layer of the face per expression: the drawing's `parts.eye` and `parts.brow` with the
  expression's lids, brows and look, the blush and socket tones, a nose highlight, mouths for the front view drawn
  after `anya.mouth`; rendered by `svg2png.mjs` (headless Chromium) to transparent PNG sheets.
- `build.py`: the character pack (engine body format plus attributes for the look):
  Anny `moood-woman` ×1.03, deformed per joint (trunk ×0.8–0.86 in x, limbs thinner round their bones, shoulders lower
  and narrower) with its own SOMA weights; its head and upper neck removed; the fitted head placed with the chin at
  1.422 m and weighted Head → Neck2 → Neck1 → Chest down the neck; hair weighted to the head, its lower curtains half to
  the chest; the cardigan = body pushed out 6 mm, flaring over the hips, chest smoothed; the skirt = an A-line loft
  from 0.97 m to 0.40 m on hip/thigh/shin weights; the scarf = a closed tube round the neck plus a flat band laid on
  the chest; shoes = smoothed feet. Colours per material: base, shadow (the drawing's mix towards `#4a1838` for skin,
  `#3a2a5a`/`#2a1e40` for cloth), rim. Output `/home/user/cache/to3d-r5-s2-anya/out/anya.json|bin` (+ `faces/`).
- `web/view.html`, `web/anya.js`: the viewer on the engine (`createEngine`, `makeBody`, `Figure` — retarget,
  skinning by centres of rotation, `clavicleShare` 0.33, floor `lowest`). The Klaus look:
  `lit = mix(base, key #ffc47a, 0.3)`, `shadow = per-material colour`, `smoothstep(thr−soft, thr+soft, N·L)` with
  thr 0.22, soft 0.14; a 4096 shadow map from the key light, 12-tap Poisson filter with a blur in world units
  (soft cast shadows); the face's normals mixed (70 %) with a smoothed head's (rotated with the Head joint) so the
  face shades as one form; a rim on the edge away from the key; a light band on the hair; the cardigan's opening,
  edges and buttons drawn from the rest position; the painted face layer over the shade (dimmed 14 % in shadow).
  Post: the drawing's backdrop gradient and glow, mottling, grain, vignette (as `kit.bg` and `kit.grain`).
  The light is given in the camera's frame for the drawing's views and the turnaround, in the world for the walk.
- `shots.mjs` (after Р1's): Playwright + SwiftShader, runs jobs of `A.set(...)` and saves pictures or film frames.
  `probe.mjs` prints the pelvis path of a clip. `steps.py` makes the step pictures (software raster, `mesh.raster`).

Repeat:
```
cd to3d/r5-s2-anya/tools
blender -b …/human_base_meshes_bundle.blend --python hbm_export.py -- /home/user/cache/to3d-r5-s2-anya/hbm.npz
python3 features.py /home/user/cache/to3d-r5-s2-anya/out/faces
python3 build.py
node shots.mjs /home/user/cache/to3d-r5-s2-anya/final.json /home/user/cache/to3d-r5-s2-anya/final
ffmpeg -framerate 24 -i turn/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 24 turn.mp4   (walk: 30 fps)
python3 steps.py /home/user/cache/to3d-r5-s2-anya/steps
```
The jobs (cameras of each view, the walk's fixed side camera) are in `tools/jobs-final.json`;
the drawing's views use ortho cameras matched to the drawing's frames (head views: centre y 1.48 m, height 0.516 m
= 600 px; figure: centre 0.816 m, height 1.853 m = 900 px).

## What was tried and dropped

- Slicing the base and scaling every slice to the drawing (as a first fit): banding and folds; replaced by points + RBF.
- Removing the socket linings by "seen from outside" rays: ragged holes; replaced by ellipse cuts + bi-harmonic fill.
- Hair ending at the head's side silhouette (to frame the face in 3/4 as drawn): it then covered the cheek in profile
  and made a helmet; kept half-way.

## Licences of the bases

- Blender Human Base Meshes bundle v1.4.1 — CC0 (Blender Foundation).
- Anny body (moood-woman, baked by moood from Anny) and the SOMA skeleton/skin — as in `engine/data` (SOMA:
  Apache-2.0, `engine/data/soma/NOTICE`); Kimodo motions from the moood studio (`engine/motions`).
- The drawing and its code: ours (`styles/s2-klaus`).
- three.js 0.160 (MIT). No neural image generation; StdGEN not used.
