# Р15 — Савелий Петрович, «Клаус», в 3D

What was done, why, how to repeat, and the licences of the bases.

## Why

Brief `docs/briefs/to3d.md`, part "Third round": each style gets two more characters in 3D beside the one it has.
Style С2 «Klaus: рисованное как объём» had Р5 (Аня, `to3d/r5-s2-anya`), which came out middling: blotches on the
face, a rough figure, clothes that are the body painted. This is Савелий Петрович in the same style; the task was to
start from Р5's bases and code and do better where its page names the weak spots. Done by one agent in one session
(the same agent then made Р16, Марат, with this code); the orchestrator commits.

## What the drawing gives

`styles/s2-klaus/tools/savely.py` draws him in **one view only — three-quarter** (`head34`, `bust`, `figure`); there
is no front, no profile and no expression sheet (two states: `calm` and `kind`). So:
- the head's outline numbers (half width, the face's and the back's line by height) are read off that one view by
  hand (`tools/head.py`, `_Y/_HW/_FW/_ZF/_ZB`), not taken from drawn front/side outlines as in Р5;
- the drawing cheats, as the findings say drawings do: in its three-quarter view the nose is seen almost in profile
  and the eyes almost from the front. One 3D head cannot do both; the 3D follows the eyes and the head's mass, and
  the nose is shorter in the same view than drawn;
- three of the five expressions (surprise, sad, anger) are made here in the drawing's manner — the drawing has none.

Sizes: the drawn figure is 712 units from the floor to the dome → 1.60 m (he is the second shortest of the cast);
the head is drawn at 0.56 of its own frame → 1 head unit = 1.258 mm. He is 3.9 heads tall: the head is 42 cm.

## How it is built (tools/)

- `hbm_export.py` (Blender 4.5, background; Р5's): the stylised head of Human Base Meshes as arrays →
  `/home/user/cache/to3d-r15-s2-savely/hbm.npz`.
- `base_head.py` (from Р5's `head.py`): the base's eye sockets and lips cut out and closed with a bi-harmonic patch,
  halves welded; the fit by points: heights by landmarks, then at every 6 units of height the base's silhouette
  points (side, the face in front of the ears, the middle line's front and back) go to the wanted outline, the whole
  head follows by an RBF (|r| kernel + affine), 3 passes.
- `blobs.py` — new: **the drawing's big soft forms as smooth solids**. Balls strung on curves (`chain`), melted
  together by a smooth union of their distances, meshed by marching cubes (scikit-image), smoothed, decimated
  (libigl). In the Klaus drawing each of these is one flat shape with its own light; in 3D each is one clean solid
  with its own shade and its own cast shadow. Also `tube` for thin made things.
- `head.py` — Савелий's head: the fitted base (its own ears smoothed away, the flare to the shoulders cut off);
  forms: the nose (a bridge, a bulb, two wings), the walrus moustache (two drooping wings), the brows, three tufts
  behind each ear, the ears (a rolled rim round a shallow bowl, a long lobe); things: round glasses with temples and
  two glints, the loupe (barrel, brass ring, glass) and its band round the head (the head sliced by a tilted plane).
  `python3 head.py out.png` shows it in clay.
- `features.py` — the painted layers from the drawing's own parts (`parts.eye`, `kit.Doc.tone`): `skin-*` (the
  sockets' warm tone, cheeks, wrinkles, the chin, the mouth under the moustache: none / smile / two speaking shapes)
  and `eyes-<expr>-<lid><look>` (lid open / half / shut; the iris left / middle / right) — 39 transparent sheets,
  rendered by `svg2png.mjs` (headless Chromium). Front projection onto the face.
- `body.py` — Anny's body as an object: `reshape` (overall scale, each joint's region wider or thinner about its
  bone, **bones longer or shorter**), `prepose` (a habit of standing turned into the rest shape), `cut`, `front`
  (the body's front depth at a place), `weights_at` (weights for a new shell from the body's).
- `build.py` — the pack: Anny's old man (`moood-oldman`) ×0.80, trunk bones ×1.3 and legs ×0.93 (the drawn figure
  has a long round trunk on short legs), belly forward, a round back and shoulders forward as the rest shape; head
  and neck off, the hole capped; the trunk, arms and legs pushed out 11 mm and smoothed into plain cloth forms,
  trouser legs made straight tubes (every leg vertex at least 7–8 cm from its bone); where the vest, the shirt, the
  tie and the trousers are is **drawn by the shader from the rest position** (`deco` GLSL in the pack's header) —
  crisp edges instead of colours smeared between vertices; the collar (a band round the neck); the leather apron — a
  21×44 grid hung in front of the body (the body's front depth + 8 mm, falling straight under the belly), weights
  from the body, the hem half with the pelvis; its straps; the shoes (blobs with a flat sole). The head sits with
  the chin at 1.186 m, 7.5 cm forward of the neck joint — pushed forward and down between the shoulders, as drawn.
  Output `data/savely.json|bin` (41.5k vertices) + `data/faces/`.
- `web/klaus.js`, `web/ui.js`, `web/view.html` — the viewer on the engine (`createEngine`, `makeBody`, `Figure`:
  retarget, dual-quaternion skinning, `clavicleShare` 0.33, floor `lowest`). The look is Р5's, changed where it
  blotched: lit and shadow colours per material as the drawing mixes them (`lit = mix(base, key #ffc47a, k)`,
  `shadow = mix(base, cool, s)`), `smoothstep` edge of the shade (thr 0.08, soft 0.16), a 4096 shadow map with a
  12-tap filter and a slope-dependent bias, the face's normals mixed 85 % with a smoothed head's, a sheen on glossy
  forms (dome, nose, brass, glass), a rim on the edge away from the key, the painted layers over the shade (dimmed in
  shadow), then the backdrop with its glow, mottling, grain, vignette.
  **The live face** (`LIFE`): schedules from a seeded random stream, the same moment always looks the same — blinks
  at uneven intervals (log-normal, ~3 s; shut 75 ms, hold 25, open 160; an expression change comes with a blink),
  the eyes hold 0.4–3.5 s and jump (left / middle / right), speech as syllables of 0.13–0.27 s in phrases with
  pauses (two mouth shapes under the moustache, the moustache bobs). The brows and the moustache are moved after
  skinning in the head's frame (`movers`: lift, turn, tips up or down) and follow their targets with a spring.
  Not done: the gaze leading the head's turn, blended expressions (the sheets are discrete; the change hides in a
  blink).
- `shots.mjs` (after Р1's/Р5's): Playwright + SwiftShader; stills and film frames from `jobs-final.json`.
  `compare.py` puts the drawing and the 3D side by side and over each other; `steps.py` makes the step pictures.

Repeat:
```
cd to3d/r15-s2-savely/tools
C=/home/user/cache/to3d-r15-s2-savely; mkdir -p $C; (cd $C; npm i three@0.160.0)      # three.js for the headless shots
/home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
  --python hbm_export.py -- $C/hbm.npz
python3 features.py ../data/faces
python3 build.py
node shots.mjs jobs-final.json $C/final                # add a regexp to make only some: '^(head|fig)'
python3 compare.py $C/final; python3 steps.py
for f in turn walk wave talk; do ffmpeg -y -framerate 30 -i $C/final/$f/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 26 ../pics/$f.mp4; done
```
Views: head pictures are ortho, 600 px = 600 head units (centre y 1.3495 m, height 0.755 m), the three-quarter at
yaw 0.62 rad shifted 11 cm to sit where the drawing's head sits; figure pictures 900 px = 2.022 m.

## What was tried and changed on the way

- The base's own ears, stretched by the fit, came out long and ridged → smoothed away, the ear made as a form.
- Materials per vertex (vest / shirt / trousers by Anny's parts) gave ragged, smeared borders → the shader draws them.
- Anny's proportions at one scale put the shoulders 6 cm under the chin; the drawing has them above it → trunk bones
  longer, legs shorter, the head forward.
- The blobs at full marching-cubes density made the pack 8 MB → decimated to 40 %, 4 MB.
- The neck's lower flare of the base head showed as a dark horseshoe round the collar → cut off.
- `idle` from Kimodo spreads his arms and stoops (a known weakness) — left out of the films and of the viewer's list.

## Licences of the bases

- Blender Human Base Meshes bundle v1.4.1 — CC0 (Blender Foundation).
- Anny body (`moood-oldman`, baked by moood from Anny) and the SOMA skeleton/skin — as in `engine/data` (SOMA:
  Apache-2.0, `engine/data/soma/NOTICE`); Kimodo motions from the moood studio (`engine/motions`).
- The drawing and its code: ours (`styles/s2-klaus`).
- three.js 0.160 (MIT), scikit-image (BSD), libigl (MPL-2.0), SciPy/NumPy (BSD). No neural image generation; StdGEN
  not used.
