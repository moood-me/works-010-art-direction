# Р7 — Вера, Arcane (style С4) in 3D

What was done, why, how to repeat, the bases' licences. Brief: `/home/user/cache/BRIEF-to3d.md` (with its second
round). Done by one agent; the orchestrator commits.

## The idea

The С4 drawing is itself built as 3D (`styles/s4-arcane/tools/arc.py`: the head a loft of super-elliptic sections with
bumps, a nose surface, a neck loft; features drawn in the face's flat coordinates = the front view's x, y, and wrapped
onto the head). The drawing is weak as a drawing (a mannequin: narrow stick body, angular face), so it is used for
what it is good at — the head's shape and proportions, the features' places, the colours, the light rules — and for
the rest the target is the style's rules and samples (`entry.json` «Правила стиля», `refs/`): near-real anatomy
slightly drawn out, one graphic shadow shape with a clear edge, a warm band at the shadow's edge, a cool rim, painterly
grain. Hence real bases: a sculpted realistic head (it has real lids and eyeballs) and Anny's body.

Units: the drawing's units map to metres as world = (x·K, (1656 − y)·K, z·K + ZOFF), K = 0.97 mm (she is 1.73 m; the
drawing's head of 234 units is then a real 227 mm head, its eyes 62 units apart a real 60 mm).

## Steps (tools/, in order) and what each base gave

1. `export_hbm.py` (Blender 4.5, background) — Human Base Meshes «head for animation» (realistic) with its sculpted
   multires level applied, its scleras and irises (after Р2), plus for every head vertex how much of its hemisphere is
   seen from outside (ray casts): the mouth's inside and the sockets' linings are not, and are not pulled in the fit.
2. `drawing.py` — samples the drawing's own head loft, nose and neck surfaces (`cast.vera()`) as points.
3. `fit_head.py` (after Р2's) — places the base: x by the eyes (±31), heights by a monotone map of the base's
   landmarks (chin, mouth line, subnasale, nose tip, eye, crown) to the drawing's (112, 71, 56, 45, 0, −122) — the
   nose comes out long, as the style asks; the nose's protrusion scaled ×1.44 toward the drawing's nose tip. The eye
   regions (balls and lids) are carried whole, 1.24× the head's scale and 1.12× wider (Arcane: big almond eyes), the
   carried place blending smoothly into the placed head over 16–34 mm (a hard border left a visible step on the
   cheek). Then non-rigid ICP onto the drawing's surfaces (Laplacian stiffness 40 → 10: the base keeps its own form,
   the drawing gives proportions); lips and nose pulled weakly (the drawing's are just bumps). The drawn neck (54–64
   units, a stick in 3D) is taken 1.3× wider. Gave: a real skull, lids, lips, nostrils, ears with clean loops.
4. `build.py` — the pack (engine body format + look attributes):
   - Anny `moood-woman` ×1.088 with SOMA weights: legs 4.5 % longer (Arcane's long legs), trunk and hips slimmer,
     shoulders narrower, each leg turned in 4.5° about its hip (she stands feet together under a narrow skirt) —
     joint frames are not touched, Kimodo retargets as for any engine body (checked in the walk).
   - Anny's head and upper neck removed; the fitted head placed by the drawing's frame, weighted Head → Neck2 → Neck1 →
     Chest down the neck; its neck ends inside the collar. Ears 0.8–0.88 smaller.
   - The coat: Anny's body pushed out 6 mm; Anny's lower neck in the coat's cloth is the stand collar (pushed round the
     head's neck, top edge levelled); the sleeves end at the wrist. The skirt: an A-line loft from the waist to the
     drawing's hem (y 1210), round the hips and the legs, soft folds; weights pelvis → thighs → shins. Under it the
     hips are drawn in 12 mm so nothing shows through. Lapels, the white shirt band, the front edge, the waist seam and
     the red brooch are painted from rest positions in the shader (crisp edges, not per vertex).
   - Shoes: Anny's feet below the ankle cut away, a lofted shoe on each foot (rounded toe, flat sole on the floor).
   - Hair: a cap over the fitted skull above the drawing's own hairline (its `(u, y)` keys), sampled on meridians
     from the crown down to the hairline, thickness 4.5–10 units (fuller on the crown), lying on the skin at the edge;
     a squashed bun at the drawing's place. Strands are painted by an across-coordinate (the angle round the axis from
     the forehead to the bun), so they sweep back into the bun; the grey streak at the front on her left.
   - Glasses: rounded-rectangle frames (`P.glasses`: rx 14, ry 10, squareness) 8.8 units in front of the eye, curved,
     a bridge and arms to the ears; lenses show only a glint (screen-door).
   - The eyes: the base's balls; the iris painted in the shader (pupil, dark ring, light lower half, fibres), the key's
     sharp reflection on the wet ball.
5. `faces.py` — the painted face layer (front projection, 6 px per unit): the drawing's brow shape (`person.brow_shape`)
   as a dark block with hairs at the start; the upper lid's line laid on the **fitted lids' real edge** (found by
   rasterising the head and balls from the front: where the ball shows) — thicker outward, a short wing; the crease;
   the lower lid's line on its outer half; lid shade, bags; lips on the fitted mouth's slit and corners (upper darker,
   lower lighter with a highlight); blush; nostrils; the drawing's own lines of a tired forty (`P.lines`).
6. `web/vera.js` — the look (three.js 0.160 on the engine: `makeBody`, `Figure`, retarget, `cor` skinning): one key
   light from the upper left (in the camera's frame for the drawing's views, in the world for films); the shadow a
   clear step whose edge is brushed by noise on the surface (not the screen); a 4096 shadow map for cast shadows
   (nose, glasses, hair, arm); a warm saturated band along the shadow's edge; red-brown skin shadows; a cool rim on the
   shadow side; painterly streaks in the shade; the face's normals mixed 88 % with a smoothed head's (the face
   shades as big planes, as the style says); the face layer over it, dimmer and warmer in shade. Post: the drawing's
   backdrop (`person.background`: radial glow #9fb4c8 → #4a5668 → #191c24), canvas weave, grain. The drawing's cameras
   are reproduced exactly (`draw: {yaw, s, cx, cy}` = `View(yaw, s, cx, cy)`), so the overlays are true.
   - Stand pose: arms hang by a two-bone reach; the left hand brings the folder to the chest as drawn (the folder is a
     separate object on the left hand's joint, set once from the standing pose, so in motions it is carried in the hand).
   - The skirt is not cloth: after skinning, its points that a leg (a capsule round the thigh and the shin) reaches
     are put on the leg's outside — the side away from the body's axis — so a stepping leg carries the skirt forward
     (pushing to the nearest capsule point left the skirt behind a leg that had swung through it).
7. `web/face.js` (after Р2's face.mjs) — the 3D face moved by a few numbers: lids turned over the ball (blink, squint,
   wide), jaw, mouth corners (smile, wide, pucker), brows (lift, inner ends, knit), irises (gaze). The painted layer
   rides on the vertices, so brows and the lid line move with the skin. The five expressions = the drawing's
   neutral (`CAST.vera.neutral`: heavy lids, a slight knit) and its sheet `EXPR` (joy, surprise, sad, anger).
8. `web/life.js` (Р2's life.mjs, unchanged in timing) — blinks at log-normal intervals (~2.8 s, never closer than
   0.8 s; close 75 ms, hold 25 ms, open 170 ms; one with every big gaze shift), fixational saccades (0.3–1.6 s, a jump
   20 ms + 2.2 ms/degree), the eyes jumping ahead of a head turn (read 0.22 s ahead from the clip) and turning back as
   the head follows, speech as syllables (consonant then vowel shapes) followed by a fast critically damped spring,
   expressions followed by a slower one; all seeded, so a film is the same each time and the viewer can scrub.
9. `web/view.html` + `ui.js` — the 3D tab: drag to turn, wheel/two fingers nearer, motion (stand, walk, idle, wave,
   bow), expression buttons and a mix by sliders, speech on/off, face close, play/pause, scrub. Data in `web/data/`.
10. `shots.mjs` (Playwright + SwiftShader; jobs of `A.set`), `compare.py` (side by side, overlay), `steps.py` (clay).

## Repeat

```
cd to3d/r7-s4-vera/tools;  C=/home/user/cache/to3d-r7-s4-vera
blender -b …/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend -P export_hbm.py -- $C/hbm_head.npz
python3 drawing.py $C && python3 fit_head.py $C && python3 build.py $C && python3 faces.py $C
cp $C/out/{vera.json,vera.bin,face.json,face.png} web/data/
NODE_PATH=/opt/node-tools/node_modules node shots.mjs $C/jstill.json $C/st     # stills in the drawing's frames
NODE_PATH=/opt/node-tools/node_modules node shots.mjs $C/jfilm.json $C/fm      # film frames (~1–2 s each)
python3 compare.py turn $C/st $C/st/turn;  python3 steps.py $C steps.jpg
ffmpeg -framerate 25 -i $C/fm/turn/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 26 ../pics/turn.mp4   (motions: 30 fps)
```
The job files are kept in `tools/jobs/`.

## What is weak (seen by eye)

- The body is real-proportioned (Anny), much fuller than the drawing's stick figure: shoulders, hips and skirt are
  wider than drawn (overlay). Chosen: the drawing's widths are a mannequin's; the style's rules ask for real anatomy.
- The coat and skirt are skinned shells, not cloth: no swing, no folds from motion; the skirt is pushed off the legs.
- The face's shadow edge is sometimes broken into small islands near the nose and the jaw (cast shadows + the brushed
  edge); Arcane's shapes are cleaner. Skin inside the light is almost flat.
- Expressions: joy and anger are milder than in the drawing's sheet; the open mouth has no teeth; at the mouth's
  corners the painted lips and the 3D slit don't always meet exactly (a small dark stitch).
- Hair is one shell with painted strands — no separate locks, no loose strands at the temples (drawn in the drawing).
- A deep bow (Kimodo's `bow`) breaks the skirt open (the legs show): left out of the page and the viewer.
- Kimodo's `idle` stoops and drops the head (the motion's own).
- The folder in motions simply rides in the left hand; hands and fingers are Anny's (realistic).

## Licences

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body (`moood-woman`), SOMA skeleton and weights: as in `engine/data` (`engine/data/soma/NOTICE`).
- Kimodo motions: `engine/motions` (moood studio).
- The drawing and its code: ours (`styles/s4-arcane`). three.js 0.160 (MIT). No neural images; StdGEN not used.
