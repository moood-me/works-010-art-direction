# Р6 — Тим, Pixar (С1): from the drawing to 3D

What was done, why, and how to repeat it. Brief: `/home/user/cache/BRIEF-to3d.md` (build the 3D from good ready bases
fitted to our drawing, not by a neural net; second round: the live face, motions, a viewer). The drawing:
`styles/s1-pixar` (tim-figure, tim-turnaround, tim-portrait, tim-expressions; its code `tools/cast.py`, `pix.py`,
`face.py`, `person.py`). Done by one agent in one session; the orchestrator commits.

## The idea

The С1 drawing is itself drawn from small 3D models: the head is a stack of superellipse sections with Gaussian bumps
(`pix.Head`, Tim's numbers in `cast.tim`), the body parts are tubes and sweeps, the hair is ribbons on an ellipsoid
shell. So the drawing's own shapes are the targets in 3D (`tools/drawing.py`), in the drawing's units
(1 unit = 2.8 mm: Tim is 430 units = 1.20 m crown to floor), and the drawing's own orthographic views are the cameras
of the comparisons. The style asks for a face built round big eyes with soft light — so here the eye is modelled: a
ball under real lids (not painted, unlike Р1/Р3/Р4, whose styles are graphic).

## Steps (tools/, in order) and what each base gave

1. `hbm_export.py` (Blender 4.5, background) — Human Base Meshes `GEO-head_stylized`, its two eyes and the stylised
   jaw as arrays (`/home/user/cache/to3d-r6-s1-tim/hbm.npz`).
2. `head.py` (with `eyefit.py`, `features.py`, `quads.py`; run with the libigl venv) — the head:
   - **shape**: both heads are star-shaped from a centre inside; the base's smooth form r_B(dir) (an RBF over
     directions of its outer surface, ears and neck left out) is scaled to the drawn ball r_D(dir) (the drawing's head
     without bumps, ray-cast) — every vertex's radius × r_D/r_B, so the sculpted nose, lips, lids and ears ride on
     top;
   - **eyes**: the base's quad loops round each eye (found by walking edge loops: 6 rings outward, 5 lining rings
     inward) are moved in the eye's spherical coordinates onto a new ball (radius 12.5 units at the drawn eye, x ±18.5,
     its front near the drawn face): the lid margin's polar angle becomes the drawn opening's (`face.eye_shape`, the
     round Pixar eye, 21 × 18 units), the lids keep their angular widths and height over the ball, the lining spreads
     over the ball behind; the outer rings are relaxed (Laplacian with the ball as an obstacle) into a smooth lid;
   - **features**: the nose (made a smaller button, ×0.74) and the mouth with its bag moved down to the drawing's
     places (nose tip y 22.5, mouth 36.5), the ears' rims scaled ×0.72 about their roots; the rest by the biharmonic
     interpolation over the surface (libigl `harmonic`, k = 2) with the eyes, skull and neck held — no kinks.
   - Gave: a child's head an artist modelled, with clean loops round eyes and mouth, an inner mouth, ears; its shape
     is the drawing's. `steps.py` shows the four stages over the drawing's outline (`pics/step-head.webp`).
3. `fitbody.py` — Anny's child (`engine/data/bodies/moood-child`, SOMA): per-joint affine maps (along/across each
   bone), joints rebuilt down the chain, vertices by their skin weights (Р3's deformer); frames kept. Targets from
   `cast.tim_person`: shoulder 0.81 m, leg joint 0.51, knee 0.27, ankle 0.045, thin limbs, legs closer.
4. `build.py` — the model pack (`model.py`, format `tim-pixar/model`, an engine pack + look attributes):
   - the head placed at the drawing's head (head units → metres), its neck made the drawing's thin round neck under
     the jaw (radius 11.5 units, a little more than drawn: the drawn 8.4 reads as a stalk in 3D), cut inside the shirt;
     weights Head → Neck2 → Neck1 down the neck; joints Head, HeadEnd, Jaw, eyes moved to the head;
   - per vertex: the face layer's front projection (u, v), how much it faces front, the lash line (upper lid margin
     and its lining, thickening to the outer corner), the lids' closing angles (`lid_data`: each lid vertex's turn
     about its ball that brings the margin to a closing line low in the opening), the jaw's share (below the mouth
     line, found where the line ring's halves part on the base; soft at the corners);
   - eyes: balls with their own direction for the iris; teeth: two rows of small rounded teeth just behind the lips,
     the upper row with Tim's gap;
   - hair (`hair.py`): the drawing's own locks (`cast.tim_hair`: 20 strips from the whorl to the hairline, the fringe
     tufts, the cowlick) made 3D — the same centre curves on the same shell, the same widths, a lens section with
     thickness and a sharp tip — over a cap (the scalp above the drawing's hairline, lifted 1.4 units), all pushed out
     of the head;
   - clothes cut from the body's own surface (Р3's `meshcut.py`): a shirt (hem 0.50 m, sleeves to 0.6 of the upper
     arm, a crew neck drawn in round the neck, a darker collar band, stripes in the shader by rest height at the
     drawn 128–140 and 146–152), shorts with wide legs, socks (paint), sneakers lofted along each foot (cream with a
     red sole);
   - ambient occlusion baked on the rest model (libigl, 64 rays a vertex).
5. `paint.py` → `web/data/paint.json` — the face layer's data from `cast.tim`: freckles, blush, the brows' build, lips.
6. The page (`tools/web/`): `tim.js` (the pack made an engine body; the engine's `Figure` retargets Kimodo motions
   and skins by centres of rotation; the engine's `armsOutOfHead` correction), `look.js` (the look), `face.js` (the
   face rig), `life.js` (timing), `paint.js` (the face layer), `ui.js` + `view.html` (the viewer).
7. `compare.py turn figure expr portrait` (the drawing's views, same scale and place: side by side and overlaid),
   `films.py walk turn face look wave` (mp4s; `sit` is defined but was not rendered: the machine was loaded), `steps.py`, `viewer_check.mjs` (the viewer as the site serves it).

## The look (`web/look.js`)

One shader for every material: a warm key from the upper left (fixed to the camera for the drawing's views, to the
world for films) with a wrapped falloff and, on skin, a red terminator (light under the skin), soft PCF shadows from
our own shadow pass (2048²), a cool fill, a sky/ground ambient times the baked occlusion, a soft GGX-like highlight,
a rim; ACES-like tone map. The eye: sclera, a procedural iris (rays, a dark ring, light pooling on the side away from
the light — a concave iris under a clear cornea), the pupil (scales with the expression), two catchlights. Hair:
clumps darker at roots and edges, a light streak along the middle, a strand variation. Skin → lip → mouth inside
blend continuously across triangles. No outline (the style has none).

## The live face (`web/face.js`, `web/life.js`)

Params: blink, lids up/low, gaze (the balls turn; the upper lid follows the gaze down), pupil, jaw (about a pivot
before the ear), smile/frown with skew (Tim's crooked smile), wide/pucker (speech), upper lip up (the teeth), the
lower lip down with the jaw, brows (raise, inner, outer, his right alone) as skin lift and in the face layer; cheeks
rise with a smile and push the lower lids up. Fields are computed once on the rest head (drawing units) and combined
each frame; the displacement is turned with the Head joint and added after skinning. The sheet's expressions as
numbers: calm, smirk (the portrait), joy, surprise, sad, anger; any mix. Timing (seeded, a moment always looks the
same): blinks log-normal (median 2.8 s), 12 % doubles, close 70 ms / shut 30 ms / open 150 ms; fixations log-normal
(median 0.6 s), jumps 25 ms + 2.5 ms/deg; the eyes lead head turns (the head's direction 0.25 s ahead, read off the
clip) and a fast turn takes a blink; speech as syllables (consonant 60–110 ms, vowel 100–200 ms), phrases with pauses,
shapes eased over 60 ms, the brows lift at a phrase's start; expressions ease in over 0.35 s (brows 0.25 s).

## How to repeat

```
cd to3d/r6-s1-tim/tools
/home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
    --python hbm_export.py -- /home/user/cache/to3d-r6-s1-tim/hbm.npz
PY=/home/user/cache/n1-deform/venv/bin/python        # numpy, scipy, libigl
$PY head.py                     # → cache/head_fit.npz (+ head_fit*.png looks)
python3 paint.py                # → web/data/paint.json
$PY build.py                    # → web/data/tim.json/.bin (and the cache)
python3 compare.py turn figure expr portrait
python3 films.py walk turn face look wave          # ~2–8 s a frame on SwiftShader
$PY steps.py
node viewer_check.mjs /tmp/v.png
```
`shots.mjs jobs.json outdir` drives `web/view.html?shots=1` (served from /home/user; three.js r160 from the n3-cloth
cache) with `window.A.set({...})`. The viewer runs from the repository's root: `/to3d/r6-s1-tim/tools/web/view.html`.

## Licences of the bases

| What | Licence |
|---|---|
| Human Base Meshes bundle v1.4.1: `GEO-head_stylized` (+ its eyes) | CC0 (Blender Foundation) |
| Anny child body (`moood-child`, in the engine), SOMA skeleton and weights | Anny (NAVER, Apache-2.0), MakeHuman (CC0), SOMA (NVIDIA, Apache-2.0) — `engine/data/soma/NOTICE` |
| Kimodo motions (walk, idle, wave, sit, bow …) | `engine/motions` (moood studio) |
| The drawing and its code | ours (`styles/s1-pixar`) |
| three.js 0.160 | MIT |

No neural images; StdGEN not used.

## What is weak / not done

- The open mouth is the weakest part: the base's mouth bag is shallow, so only the front teeth show (the gap reads),
  and the inside is a dark pocket, no tongue.
- The lids: the upper lid is a smooth membrane relaxed over the ball, not sculpted; the lash line is a vertex-painted
  band, a little jagged up close.
- Clothes are shells skinned with the body, not cloth; the shirt is a little A-shaped where the drawing is boxy; the
  shorts are a bit shorter and wider than drawn. Hair is rigid on the head.
- Hands are Anny's (shortened), not the drawing's soft mittens.
- The drawn stance (feet together, arms straight, a hand behind the back in figure-tim) is not posed: the stills use
  frame 0 of Kimodo's `bow` (standing upright).
- Brows sit 3.5 units higher than drawn: in 3D the upper lid's fold is where the drawing paints them, and it moves
  with blinks.
