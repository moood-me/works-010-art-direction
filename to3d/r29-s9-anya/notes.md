# Р29 — Аня, середина века: from the drawing to 3D

What was done, why, and how to repeat it. Brief: `docs/briefs/to3d.md`, its "Third round": the second character of
style С9 after Тим (Р3, `to3d/r3-s9-tim`), built from his code. The drawing: `styles/s9-midcentury` (figure-anya,
turn-anya, expr-anya; the code that draws them: `tools/anya.py`, `face.py`, `kit.py`, `scenery.py`).

## What was decided, and why

- **Тим's way kept**: Anny's body from the engine bent by a map per joint; the Human Base Meshes stylised head with its
  face closed smooth and warped to the drawing's front and side outlines; the features painted by the drawing's own
  code and projected from the front; the gouache shader, then the drawing's backdrop and its own SVG filter; the live
  face redrawn every frame; the viewer.
- **Proportions from figure-anya**: 1 figure unit = 2.28 mm (1.68 m to the top of the hair), the head drawn at 0.5 →
  1 head unit = 1.14 mm. Waist 1.07 m, collar 1.38, chin 1.42; shoulders ±12 cm, a 16 cm waist, thighs 5–6 cm, ankles
  2–3 cm. The busts of turn-anya have wider shoulders than the figure; the figure wins.
- **The bob is its own form, not a shell over the skull** (Тим's crop was a shell): sections every few units of height,
  each a squarish ellipse whose half-width comes from the front view's hair outline and whose front and back come from
  the side view's; the ends flare out (the flip) and turn in underneath; the fringe and the front edge are cut along
  the drawing's lines (`meshcut.cut`, clean curves). The skull under it is painted hair, so nothing pale shows between.
- **Where the drawing contradicts itself the front view wins** (as with Тим): in the side view the hair runs from the
  fringe diagonally across the cheek; in the front view the face is open to its full width. The bob's edge follows the
  side view, the skull's paint leaves the whole front face open. The three-quarter drawing has larger features than the
  front one and a wedge nose at the far cheek; the 3D has one head for all views with the front view's features.
- **The face stays one flat paint**: the skin takes its second tone only where it turns well away from the light
  (threshold −0.42 against Тим's −0.12) — a patch of shade on a girl's cheek read as a blemish. The neck is the
  drawing's darker SKIN_D, and its border with the face follows the front view's chin, so the chin reads round.
- **The nose** is a small wedge of one flat paint (a darker one underneath): from the front only the drawn stroke
  shows, in profile the wedge gives the turned-up tip.
- **The skirt** is a bell lofted from the drawing's outline (waist ±8 cm → hem ±27 cm at 0.5 m), twelve folds deepening
  to the hem and twelve scallops; it hangs on Hips and lower down takes up to 62 % of each side's thigh, blended across
  the middle — so it swings in a step and does not tear. The dots are in the paint: the shader reads the cloth's flat
  coordinates (the cone unrolled for the skirt, a cylinder for the bodice), so the dots stay round.
- **Clothes as Тим's**: the bodice, the cardigan (open in front, sleeves to the wrists) and the round collar are shells
  cut from the body's own surface along clean lines, their edges faired; ballet flats lofted along the feet.

## Steps and what each base gave

1. **Body — Anny's woman** (`engine/data/bodies/moood-woman`). `tools/body.py`: the groups' scales (along the bone,
   across): trunk 1.2 / 0.6 / 0.7, clavicles 0.56, arms 0.82 / 0.6, thighs 1.0 / 0.52, shins 1.0 / 0.42, feet 0.74 / 0.6,
   fingers short.
2. **Head** — `tools/hbm_export.py` (Blender), `tools/head.py` (cut, fair, thin-plate warp to `tools/drawing.py`'s
   outlines), in `build.py`: ears faired away, Taubin smoothing of the cheeks and jaw (lumps go, the form stays),
   nothing wider than the front outline, the neck cut inside the collar.
3. **Face** — `tools/face_tex.py` → `face/<expr>.png` (the stills); `tools/web/face.js` (the live one): her kinds added
   to Тим's port — the `look` eye (a white almond, an iris clipped by it, a heavy lid, a lash; a blink brings the lid
   down), lashes, the `lips` mouth.
4. **Hair, dress, cardigan, collar, shoes** — `tools/build.py`.
5. **Look** — `tools/web/anya.js` (the shader: paints, second tone, dots), `tools/compose.py` (backdrop and filter).
6. **Motion** — one engine body on SOMA's 77 joints; `Figure` retargets Kimodo's motions; nothing of the engine changed.

## How to repeat

```
cd to3d/r29-s9-anya/tools
C=/home/user/cache/to3d-r29-s9-anya; mkdir -p $C; (cd $C && npm i three@0.160.0)
/home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
    --python hbm_export.py -- $C/hbm_head.npz
python3 body.py; python3 head.py; python3 face_tex.py; python3 build.py     # → $C/anya.json/.bin and ../model/
for k in orig faired warped; do python3 look_head.py $k; done
for k in turn expr figure; do python3 compare.py $k '{"motion":["bow"],"t":0}'; done
python3 steps.py; python3 films.py turn walk face dance bow wave look
python3 look.py          # a quick sheet: four sides and the head close → $C/look.jpg
node viewer_check.mjs $C/viewer.png
```
Python needs numpy, scipy, igl (libigl), PIL; node needs playwright (pre-installed) — three.js is served from the cache.
`shots.mjs jobs.json outdir` drives `web/anya.html?shots=1` (served from /home/user).

## Licences of the bases

| What | Licence |
|---|---|
| Anny body (moood-woman, in the engine) | Anny (NAVER, Apache-2.0), MakeHuman (CC0), SOMA rig (NVIDIA, Apache-2.0) |
| Human Base Meshes bundle v1.4.1, `GEO-head_stylized` | CC0 (Blender Foundation) |
| Kimodo motions (walk, dance, bow, wave, idle) | made in the moood studio, in `engine/motions` |
| The drawing and its code | ours (styles/s9-midcentury) |

## What is not done / honest

- The skirt, the cardigan and the hair are shells on bones: nothing crumples, the bob does not swing. Sitting, the knees
  go through the skirt — `sit` is left out of the films and the viewer.
- No pose of the drawing (hands at the waist with a posy, the head tilted): only the engine's motions.
- The wave: Kimodo carries her palm by her forehead; it reads weakly.
- The hands are Anny's fingers shortened, not the drawing's small ovals.
- Three-quarter and profile differ from the drawn ones as said above.
- The mouth speaks by syllable shapes, without sound or a jaw.
