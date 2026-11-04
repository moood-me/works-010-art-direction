# Р2 — Савелий Петрович, чистая линия (С10 → 3D)

What was done, why, and how to repeat it. Brief: `/home/user/cache/BRIEF-to3d.md` (build the 3D from good bases
fitted to our drawing, not by a neural net). Done by an agent in one session; the orchestrator commits.

## The idea

The С10 drawing (`styles/s10-ligne-claire/tools`) is itself built as simple 3D: the head from horizontal slices with
nose, lips, chin and ears as bumps, hair and garments as shells, marks (lids, brows, wrinkles, glasses) as 3D lines
on the surface. So the drawing's own shapes were taken as data in the drawing's units, and every base was fitted to
them; the overlays are exact because the cameras are the drawing's own (orthographic `View(yaw, pitch, s, cx, cy)`).

## Steps (tools/, in order)

1. `drawing.py CACHE` — dumps from the С10 code: the head surface as points (the fitting target), the hair horseshoe
   as a grid mesh with a smooth cut edge (outside corners slid to where the cut's margin crosses zero), the moustache
   wings, every face mark for each expression of `features.EXPR`, tagged by what made it (eye, brow, mouth, nose,
   glasses, detail).
2. `export_hbm.py` (Blender, on `human_base_meshes_bundle.blend`) — the realistic head "for animation" with its
   multires level applied (the bare cage has lids too closed), and its scleras and irises.
3. `fit_head.py CACHE` — places the base by landmarks (eyes, crown, chin; separate scales above and below the eyes),
   enlarges its nose about the root toward the drawing's nose, carries the eye regions (with the deep socket pocket)
   and the ears whole to the drawing's eyes/ears, then non-rigid ICP: nearest drawing point with agreeing normal +
   Laplacian of the placed base (stiffness 30 → 2); the neck pulled onto the drawing's neck tube; the inside of the
   mouth follows. Note: the drawing's frame flips handedness — normals are flipped back (`SGN`).
4. `body.py CACHE` — Anny's old man (`engine/data/bodies/moood-oldman`): per-bone scales (legs 0.8, shins straight,
   trunk 0.92 tall and wider, arms 0.9); vertices follow by Anny's weights `v' = Σ w (J' + A (v − J))`; neck/head
   joints set where the drawing's head turns; joint frames untouched. Trunk kept inside the drawing's torso shell.
   Clothes: vest and shirt from the drawing's torso shells (V and arm holes as smooth margins), trouser top from its
   hips shell, sleeves/trouser legs as offset shells of Anny (legs widened to the drawing's radii 60→42, the sleeve
   top tucked under the vest), shoes/bow/collar/buttons/watch/chain from the drawing's shapes. Weights for shell
   points: Anny's weights of the 24 nearest body vertices blended by distance, top four (nearest-only gave a jagged
   vest in motion).
5. `assemble.py CACHE --body` — the scene for the renderer (`scene.npz/json`), the hair pushed off the skull
   (radial map, ears left out — they stand in front of the hair, as drawn), the marks laid onto the new surface,
   the head's shoulders cut (the neck ends in the collar), head weights by height (Head → Neck2 → Neck1 → Chest),
   rigid pieces on Head; face marks also baked as ink tubes for moving pictures (`BAKE_LW`). `pack_engine.py` writes
   an engine body + its own topology (`CACHE/engine/data/{bodies,topology}/savely.*`, triangles uint32) and
   `offsets.json` (which vertices are which piece).
6. `move.mjs CACHE walk walk.bin` — the engine as it is (`createEngine`, `figure`, `clip`), only its file reading
   pointed at our body pack; writes skinned positions per frame. `stand.mjs` — a still stand (arms let down from the
   A pose, optional head turn `HEAD='{"pitch":14,"yaw":-14}'`) skinned by the engine's Skinner — not a motion.
7. `expressions.py CACHE` — lids turned over the eyeball about its centre, jaw turned about a pivot below the ear,
   mouth corners (and moustache ends) moved, brow skin lifted, irises turned; writes `expr.bin` (one frame each).
8. `render.py JOB` (Blender 4.5 `-b`) — Cycles CPU, emission materials (flat colour), Freestyle (silhouette, border,
   material boundary, external contour; crease off), even width; marks as ink tubes/filled shapes whose width follows
   the picture's line width; frames mode replaces each piece's vertices per frame, can follow the walker, turns the
   marks with the head (Kabsch on head vertices) for posed stills; `pair` renders view i with frame i.
9. `compare.py` (drawing / render / overlay sheets), `film.py` (frames → mp4 with the drawing's floor band and
   frame), `steps.py` (the steps sheet), `dots.py` (point plots for looking at fits).

Jobs used (in CACHE = `/home/user/cache/to3d-r2-s10-savely/`): `job_cmp.json`, `job_cmpH.json`, `job_turnaround.json`,
`job_walk.json`, `job_expr.json`, `steps/job*.json`. A walk frame takes ~10 s (Freestyle over ~64k vertices).

## Bases and licences

| What | Where | Licence |
|---|---|---|
| Human Base Meshes bundle v1.4.1, `GEO-head_animation_realistic` + its eyes | blender.org demo files (asset bundles); local `/home/user/cache/n5-heads/hbm/` | CC0 |
| Anny old man (`moood-oldman`), SOMA skeleton and weights | `engine/data` (Anny: NAVER, Apache-2.0; MakeHuman CC0; SOMA rig: NVIDIA, Apache-2.0) | as in `engine/data/soma/NOTICE` |
| Kimodo walk | `engine/motions/walk.json` (moood studio) | as the engine's motions |
| The drawing | `styles/s10-ligne-claire` (ours) | — |

No neural images, no StdGEN.

## What did not work / is left

- The nose is smaller and straighter than the drawing's caricature (enlarged ×1.25/1.23, the Laplacian keeps it a
  realistic nose); needs its own sculpt by the drawing's profile.
- Hands are Anny's realistic hands, held a little forward; the drawing's watch is in the hand, ours in the pocket.
- Clothes are skinned shells, no cloth: no folds; in the walk a sleeve can pass through the vest. Freestyle draws no
  line where two pieces pass through each other, and adds short strokes on small details (nostrils, ear rims).
- Kimodo's "idle" stoops and drops the head, so the stills use a stand made from the rest pose.
- The first attempt with the stylised HBM head was dropped: its eyes are twice the drawing's; the realistic head's
  eye size matches the drawing (eye width ≈ 0.1 head).
