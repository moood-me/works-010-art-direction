# Р13 — Вера, Pixar (С1): from the drawing to 3D

What was done, why, and how to repeat it. Brief: `docs/briefs/to3d.md`, its part "Third round" (each style gets two
more characters; start from the style's character already in 3D). The drawing: `styles/s1-pixar` (vera-portrait,
vera-figure; its code `tools/cast.py` — `vera`, `vera_hair`, `vera_person` —, `pix.py`, `face.py`, `person.py`).
Started from Р6 Тим (`to3d/r6-s1-tim`): its `tools/` were copied here and changed. Done by one agent; the
orchestrator commits. The container was restarted twice during the work; nothing was lost but time.

## What is taken from Р6 and what is new

Taken as it is: the bases (the Human Base Meshes stylised head, Anny's body in the engine, SOMA), the head fit
(`head.py`, `eyefit.py`, `features.py`, `quads.py`), the body deformer (`fitbody.py`), cutting clothes from the body's
surface (`meshcut.py`), the model pack (`model.py`), the look (`web/look.js`), the face rig and its timing
(`web/face.js`, `web/life.js`), the face layer (`web/paint.js`), the viewer.

New or changed here:
- **`char.py`** — everything that names the character (the drawing's person, the engine body, the eye's ball, the
  nose's scale, the stills' stance, the films). The fit takes its numbers from the drawing's data instead of constants
  written for Тим: the eye opening's middle and the ball's depth from `face.eye_shape` and the head's surface, the
  nose tip and the mouth from the head's bumps and `mouth_y`; the drawn head's own scale (`hs` 1.12) goes into the
  pack and the face rig.
- **Body**: `moood-woman`, made the drawing's column: trunk ×1.30 long, ×0.62 wide, ×0.52 deep; the legs' joints
  4 cm off the middle (Anny's 12); thin limbs. K = 2.8 mm per unit as Тим's, so Вера is 1.79 m.
- **Head**: the neck under the jaw is the drawing's thin round neck (9.4 head units; drawn 8.2), the jaw line raised
  so that the head is an egg on a stalk, as drawn.
- **The mouth** (Р6's weak place): the lips' rings and the bag's rings are split between the head and the jaw by
  their place along the ring (the two halves of the parting line lie 0.15 units apart in height and cannot be told
  by height: that gave Р6's torn upper lip); the mouth's inside is found by walking the mesh from the bag's rings
  without coming out to the face; a tongue (a flat rounded body on the jaw).
- **Hair** (`hair.py`): the drawing's hair shell (an ellipsoid) above its hairline `hl_bun` as a grid laid from the
  bun, so the strands of the look run the way the hair is combed; toward the hairline it comes down to 3.6 units
  over the scalp (the drawn shell stands 5–11 units off the head — a helmet in 3D) and the edge is turned in; the
  bun (a ball, the drawing's place and radius); the grey streak (a lock laid on the cap). At the nape, which no
  drawing of Вера shows, the hairline is taken 14° lower than `hl_bun`.
- **Glasses**: `cast.glasses(shape='rect', lift=8, cy=1, rx=10.5, ry=7)` as thin tubes — rims, bridge, temples to the
  ears; no lenses. They cast no shadow (on the face the rims' shadow read as lines).
- **Coat**: the top is the body's surface cut at the belt (y 232), the neckline and the wrists, moved out to the
  drawing's own sections (`vera_person`'s last layer: w, zf, zb, superellipse 2.1) — the sleeves to the drawn sleeve
  radius; the skirt is lofted on the same sections from the belt to the hem (y 480), let out where the body under it
  comes nearer than 9 mm. The join is under the belt's darker band. The skirt's skinning: the body's own weights
  above the legs' fork, below it each side goes with its leg and keeps a share of the hips (it lags the step);
  `web/cloth.js` then moves every vertex of the skirt out of the legs' and the seat's capsules each frame, softly —
  the cloth lies over the knee. The coat's front (lapels, the turtleneck's wedge, seam, buttons) is the drawing's
  `coat_deco`, painted into a layer the coat takes by its rest place (`paint.py` → `web/paint.js clothLayer`); the
  belt goes all round in the shader.
- The turtleneck's collar (a tube round the neck), narrow trousers (the legs' surface a little out), flat shoes.
- **The stills' stance** (`web/char.js stancePose`): the rest body with arms and legs turned so that shoulder → elbow
  → wrist and hip → knee → ankle point as the drawing's joints do, fingers curled a little; no Kimodo frame (Р6's
  page named that as weak). The drawn arms hang inside the drawn coat (the sleeve is painted over it), so elbow and
  wrist stand off by the sleeve's thickness (`build.py STANCE`).
- **The comparisons**: the camera can count its turn from where the body or the head faces (`cam.rel`); the head
  sheets aim at the head's centre. The style has no turnaround and no expression sheet of Вера: `drawn.py` draws
  them with the style's code as it is (`build.turnaround`, `build.expressions`) into the cache, for comparing only.
- Expressions (`web/face.js EXPRESSIONS`): calm (her portrait), strict, smile, joy, surprise, sad, anger.

## How to repeat

Heavy commands go through a shared lock: `L="flock /home/user/cache/heavy.$((RANDOM % 3)).lock"`.
```
cd to3d/r13-s1-vera/tools
(cd /home/user/cache/to3d-r13-s1-vera && npm install three@0.160.0)       # the page's three.js for the shots
$L /home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
    --python hbm_export.py -- /home/user/cache/to3d-r13-s1-vera/hbm.npz
python3 head.py                 # → cache/head_fit.npz (+ head_fit*.png looks); numpy, scipy, libigl
python3 paint.py                # → web/data/paint.json
python3 build.py                # → web/data/vera.json/.bin (and the cache)
python3 drawn.py                # the turnaround and the expression sheet by the style's code → cache/drawn
$L python3 compare.py turn figure expr portrait
$L python3 films.py turn walk bow face
python3 steps.py
$L node viewer_check.mjs /tmp/v.png
```
`quick.py out.png` — a software look at the pack; `heads.py out.png [z0.2] calm joy …` — close looks at the head.
`shots.mjs jobs.json outdir` drives `web/view.html?shots=1` with `window.A.set({...})`. The viewer runs from the
repository's root: `/to3d/r13-s1-vera/tools/web/view.html`.

## Licences of the bases

| What | Licence |
|---|---|
| Human Base Meshes bundle v1.4.1: `GEO-head_stylized` (+ its eyes) | CC0 (Blender Foundation) |
| Anny woman body (`moood-woman`, in the engine), SOMA skeleton and weights | Anny (NAVER, Apache-2.0), MakeHuman (CC0), SOMA (NVIDIA, Apache-2.0) — `engine/data/soma/NOTICE` |
| Kimodo motions (walk, bow …) | `engine/motions` (moood studio) |
| The drawing and its code; Р6's code | ours (`styles/s1-pixar`, `to3d/r6-s1-tim`) |
| three.js 0.160 | MIT |

No neural images.

## What is weak / not done

- Skin is paler and pinker than drawn, the coat lighter and bluer (the look's strong key light, as Р6's); the
  paints were moved toward the drawing's shadow colours, not enough.
- The hair still reads as a helmet (so does the drawing); its lower edge at the back of the head overhangs.
- Hands are Anny's. The coat is a shell: no folds; in the deepest bow a small dark gap shows at the back.
  Lapels are painted, not modelled. No lenses in the glasses.
- In Kimodo's motions the head goes forward on the long thin neck: she is less upright than drawn. `idle` stoops
  (known), `wave` brings the hand to the head — neither was filmed.
- Anger is given with pressed lips (the style's sheet opens the mouth); joy shows a full row of teeth.
- The upper lid and the lash line are Р6's (a smooth membrane, a vertex-painted band).
