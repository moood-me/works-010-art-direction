# Н2 — Одежда выкройками (GarmentCode)

## What was done and why

Pavel asked to see, for each open tool, our thing against the tool's. Here: GarmentCode (Korosteleva & Sorkine-Hornung,
SIGGRAPH Asia 2023; GarmentCodeData, ECCV 2024) — garments written as parametric **sewing patterns in code**
(pygarment), sewn and draped on a body by its own cloth simulation (a fork of NVIDIA Warp). Our О1 draws garments as
designed shapes around the body's axes, О3 simulates MakeHuman garments as cloth; GarmentCode starts from the cut
(flat panels + seams), so the shape comes from the pattern and gravity.

Made with GarmentCode, on our Anny body (engine `moood-woman`, the woman of О3 pictures), at rest:
two dresses with designed silhouettes (bell = circle skirt; A-line with puff sleeves), a loose straight dress
("trapeze" asked of its Shirt with flare 1.5 — it barely flares: the shirt's flare is mild), a long-sleeved shirt
with a circle skirt and with trousers (GarmentCode makes a top and a bottom as one garment sewn at the waistband:
the shirt reads as tucked in; alone, a skirt or trousers leave Anny bare above — drapes `skirt-circle`, `pants` kept
in out/ but not shown); one dress with its parameters changed (suns 0.3 / 1.5 with length, V-neck);
the tool's own uses: patterns as code (2D pieces), one design made to measure on other bodies (its own female and
male), random designs from its dataset sampler.

## How (to repeat)

Everything heavy is in `/home/user/cache/n2-garments/` (not in the repository).

1. Sources (MIT): `git clone --depth 1 https://github.com/maria-korosteleva/GarmentCode src` (main, pygarment 2.0.2),
   `git clone --depth 1 https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode warp` (1.0.0-beta.6, commit
   63baf68, 2024-09-02; NVIDIA's licence for Warp).
2. `uv venv -p 3.11 venv`; `uv pip install "numpy<2" scipy pyyaml svgwrite psutil matplotlib svgpathtools cairosvg
   trimesh libigl cgal pyrender`.
3. Warp for CPU (no CUDA here): `chmod +x warp/tools/packman/packman && cd warp && python build_lib.py --no_build_llvm`
   (fetches NVIDIA's prebuilt clang/LLVM through packman and builds `warp.so` + `warp-clang.so`), `uv pip install -e ./warp`.
   pygarment is used from the source tree (`PYTHONPATH=src`, run from `src/`, which needs `src/system.json` — a copy
   of `system.template.json` with `output` set).
4. **A bug of GarmentCode on CPU** (fixed in our runner, not in its code): `Cloth.update` keeps
   `current_verts = particle_q.numpy()`; on CPU that is a view, not a copy, and with 10 substeps it is the same buffer
   every frame, so the "is it at rest?" test sees no motion and stops the drape after the zero-gravity frames (the
   pieces stay unsewn round the body). `tools/gc_run.py` copies the array after each frame.
5. **Our body for GarmentCode**: `tools/anny_export.py` writes the engine body as `.obj` (metres, only the vertices
   its triangles use, waist centred at z = 0 as GarmentCode's bodies are), the part segmentation GarmentCode wants
   (`body`, `left_arm`, … from the engine topology's `parts`; no `face_internal`), and the map back to engine ids.
   `tools/measure.py` takes GarmentCode's 26 measurements (its PDF in `src/docs`) from the mesh: horizontal tapes as
   convex hulls of sections (waist the narrowest, bust and hips at the breasts' / bottom's most prominent points),
   back widths from side to side round the back, tapes over the front/back profile, the arm/trunk junction for
   shoulder and armpit. Checked on GarmentCode's own `mean_all` body against its numbers: most within 1–3 cm, but
   `bum_points` 10 vs 18 cm and `back_width` 44 vs 48 (they matter only for dart places and the front/back split).
   GarmentCode's own measuring tool (GarmentMeasurements) works only on its own body model. Anny `moood-woman`:
   height 158.5, bust 82, waist 67, hips 95 cm, arms 47° down (`arm_pose_angle`).
6. Drapes: `tools/jobs.sh` (each line a design: overrides of GarmentCode's `assets/design_params/default.yaml`,
   run through `tools/gc_run.py`, its `gui` sim settings — "mid-softness fabric"). On this shared CPU a drape takes
   4–50 min; the bell dress at GarmentCode's resolution (27k cloth points) ran into the 50-min cap at frame 552
   while its skirt was still falling (it looked settled in GarmentCode's preview, but beside the same dress at 1.6 its
   hem is visibly wider) — so the page and out/ use `dress-bell16`, the same design at 1.6. The rest: `RES=1.6` (coarser), except those with a short edge (cuffs, collars): at resolution > 1
   GarmentCode crashes on its own warning (`Edge` has no `name`) — those ran at 1.0.
   Dropped: `dress-bell` (above), `var-suns15-long` (suns 1.5 to the ankles) had not settled within the 50-minute cap — still spread out
   in the air; a sleeve variant of the bell (needs resolution 1.0, ~50 min). Replaced by a short full skirt and a V-neck.
7. Pictures: `tools/render_all.sh` (Blender 4.5, Cycles CPU, 32 samples; `tools/render.py` — beige floor and
   backdrop like our clothes pictures), sheets by `tools/sheets.py`. GarmentCode's own preview renders
   (`*_render_front.png`, pyrender) are in the runs too.
8. The sewing film: the shirt-with-skirt draped once more with `gc_run.py --dump` (cloth points every 4th frame),
   `tools/film.py` renders them on the box mesh in Blender, ffmpeg → `pics/sewing.mp4`.
9. `tools/sample.py`: its dataset sampler (`pyg.DesignSampler` + `pattern_sampler.assert_param_combinations`), seed 7,
   12 designs fitted to Anny's measurements; three of them draped.

Meshes for Н3: `/home/user/cache/n2-garments/out/` (README there).

## Licences

GarmentCode, pygarment: MIT (Maria Korosteleva). NvidiaWarp-GarmentCode: NVIDIA Source Code License (non-commercial
research use in its fork's licence — check before any product use). GarmentCode's bodies `mean_all`, `mean_female`,
`mean_male`: its own body model (GarmentMeasurements). Anny: NAVER, Apache-2.0; MakeHuman CC0.

## Pictures

All `pics/*.webp`, `pics/sewing.mp4` made here from GarmentCode's output, except `pics/gc-header.webp` — GarmentCode's
repository picture `assets/img/header.png` (MIT), put on a light background.
