# Н1 — body and face deformations: ours against libigl

## What was done

libigl's Python bindings (`pip install libigl`, version 2.6.3, MPL-2.0; numpy, scipy, pillow beside it) were run on
exactly the Anny bodies our tools work on, with the same targets as our tools, and both sides were rendered by one
scene (`tools/shot.html` — the light, clay, floor and 24° camera of `experiments/form-tools`).

1. **Meshes out of our pages** — `tools/export.mjs` opens `experiments/form-tools` (with its own `__restPose` hook: the
   body at rest, before posing) and `experiments/lines` in headless Chromium and saves raw float32 positions:
   - form-tools, Disney + princess 0.6 woman: no tool; cage hourglass 0.8 / pear / egg / wedge 1; face elf 1, anime
     1.3, Burton 1.2, Pixar 1.3, hero 1.3 (the presets of `viewer.json`); the joints at rest;
   - form-tools, the raw Anny woman (deg 0) and our smoothings of her through `__sh.dbg`: `curvSmooth` at 2 and 4 cm,
     the old uniform `taubin` (40 passes);
   - lines, the posed woman: no deformation, arc 0.5, arc 1 (and line C, squash — exported, not used).
   The lines page keeps its `group` to itself; for the export the served copy gets one line `window.__group = group`
   through Playwright's `route` — the file in the repository is not touched.
2. **libigl** (each script reads `/home/user/cache/n1-deform/mesh`, writes `/home/user/cache/n1-deform/out`):
   - `cage.py` — silhouette by 10 handles: rings of skin (|height − level| < 0.3 % of the height, arms left out) at
     0.04, 0.27, 0.47, 0.61, 0.76, 0.84, 0.9 of the height, the head above 0.96, the two hands. Each ring gets the
     affine scale our preset's profile gives at its level (the `CAGES` table copied from form-tools); the hands move
     with the shoulder, unscaled, as ours do. `igl.bbw` (8 iterations, ~2 s) on the surface, rows normalised, linear
     blend skinning.
   - `arap.py` — ARAP (`igl.arap_precomputation` / `arap_solve`, 60 iterations) with the body (limb skin weight
     < 0.02), hands, feet and the elbow and knee rings put where our arc puts them.
   - `arap2.py` — the same plus rings at 35, 50, 65 % of each limb carried rigidly onto our arc: centre where ours puts
     it, turned by the arc's direction there. Rings at 20 and 80 % were tried and dropped: the one at 20 % sits next to
     the fixed body and made a hard crease in the crotch; with 35 % the crease is softer but still there.
   - `smooth.py` — implicit mean-curvature flow: `(M − t·L) Uₙ₊₁ = M Uₙ`, `igl.cotmatrix` once, `igl.massmatrix`
     (barycentric) each step, 4 steps of R²/4 for R = 2 and 4 cm (the same reach as our heat step of time R²).
   - `face.py` — the landmarks of form-tools (`landmarksOf` ported line by line; 19 distinct points), each moved by
     exactly the displacement our tool gave it; the skin below the base of the neck fixed; `igl.harmonic(k=2)` for the
     rest. ARAP with the same targets: single points made spikes, so each landmark takes the skin within 6 mm with it.
3. **Pictures** — `python tools/shots.py jobs <set> > jobs.json; node tools/shot.mjs jobs.json; python tools/shots.py
   sheet <set>` for the sets `cage`, `cage-close`, `arap`, `smooth`, `face` → `pics/*.webp`.

Found on the way: the raw Anny mesh (and the posed one in lines) has 4 zero-area triangles at a mouth corner (points
exactly on each other). libigl's cotangent Laplacian gives NaN there, so `common.merged` merges coincident points
(`igl.remove_duplicate_vertices`, 1e-7), drops the collapsed triangles and maps the result back.

## Repeat

```sh
python3 -m venv /home/user/cache/n1-deform/venv && /home/user/cache/n1-deform/venv/bin/pip install libigl scipy pillow
cd /home/user/works-010-art-direction
node tools-demo/n1-deform/tools/export.mjs /home/user/cache/n1-deform/mesh       # ~2 min, Playwright from /opt/node-tools
cd tools-demo/n1-deform/tools
P=/home/user/cache/n1-deform/venv/bin/python
$P cage.py; $P arap.py; $P arap2.py; $P smooth.py; $P face.py                   # seconds each
for s in cage cage-close arap smooth face; do $P shots.py jobs $s > /home/user/cache/n1-deform/jobs.json; \
  (cd ../../.. && node tools-demo/n1-deform/tools/shot.mjs /home/user/cache/n1-deform/jobs.json); $P shots.py sheet $s; done
```

## What came out

- Cage vs BBW: the same silhouettes (differences up to 2–4 cm at single points, invisible at a glance); both clean.
  BBW's advantage — handles anywhere on the body, not on a grid — wasn't needed by these presets.
- Arcs: ARAP keeps limb girth and the knee's form; ours thins the thigh and upper arm. But ARAP bends at angles, not as
  a smooth arc, and makes a crease where the moved limb meets the fixed body.
- Smoothing: the same operator as ours; without our girth return along the normal, limbs dry out (toes gone at 2 cm,
  arms like threads at 4 cm).
- Face: biharmonic weights on the surface ≈ our spatial biharmonic spline (a few mm apart); ARAP breaks mouth and nose.
- Not done: squash and the line of action. ARAP keeps lengths, so it resists a squash; our line of action already turns
  each section with the curve. libigl has no better tool for either.
- No third-party assets: only Anny's bodies from this repository.
