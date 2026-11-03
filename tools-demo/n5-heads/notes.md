# Н5 — Головы, лица, тела: готовые образцы

What was done for this page, why, and how to repeat it.

## Why

Pavel asked to see, for each ready open tool, how a thing looks with us now and how it can look with the tool. For heads
and faces the "tool" is ready-made professional characters: Blender Studio's rigged characters (Rain, Snow) and
Blender's Human Base Meshes. They are shown as they are, in a neutral light, against our heads Г1/Г2/Г3 and bodies
Т7/Т8, and close up, to see what in their faces is made better (forms of eyes, lids, mouth, corners, edge loops, how
expressions are built). StdGEN (one picture → layered 3D character) was checked and could not be run here.

## Sources and licences

| What | Where | Licence | Credit line |
|---|---|---|---|
| Rain v3.3 (`rain_v3.2.blend`) | https://studio.blender.org/characters/rain/v3/ (free download, no subscription) | CC-BY 4.0 | Rain Rig (CC) Blender Foundation \| studio.blender.org |
| Snow v4 (`snow_v4.2.blend`) | https://studio.blender.org/characters/snow/v4/ (free download) | CC-BY 4.0 | Snow Rig (CC) Blender Foundation \| studio.blender.org |
| Human Base Meshes bundle v1.4.1 | https://www.blender.org/download/demo-files/ → Asset Bundles (mirror: `mirror.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip`) | CC0 | none required (Blender Foundation) |
| StdGEN teaser picture (`pics/stdgen-authors.webp`) | https://stdgen.github.io/static/images/teaser.png — the authors' own picture of their results, not run by us | code Apache-2.0; picture shown as a citation | He et al., StdGEN, CVPR 2025 |

Other Blender Studio characters, checked by their pages: free download links on Huginn (a robot, not a person —
not used), Einar, Autumn, Phil, Jay; Ellie and Mikassa offer no download without a subscription. Downloads and
unpacked files are in `/home/user/cache/n5-heads/` (not in the repository).

## How it was rendered

Blender 4.5.15 LTS, background mode, the `.blend` files as downloaded (scripts in them not run: `cloudrig.py`,
`rain_shading.py`, `snow_post_generation.py` are UI/post-generation helpers; the face drivers work without them).

- `tools/render.py` — opens a character, hides the rig widgets and helper meshes, frames by the rig's own landmarks
  (left eye bone, mouth corners), poses the face with the rig's own controls and renders.
  Engines: `EEVEE` (their materials, 16–24 samples, grey world + two sun lights, AgX) for colour; `WB_CLAY` (Workbench,
  one clay colour, studio light) for the form alone; `wire` adds the base cage as thin dark tubes over the cage
  (a Wireframe-modifier copy of the head, eyes, brows, lashes, body) — that is the topology.
  The clear cornea over the iris is hidden: without ray tracing EEVEE draws it milky and Workbench opaque, both hide
  the iris; the iris and pupil underneath are the character's own.
- `tools/poses.py` — the expressions, made only with the controls the animators use:
  Rain: `ACT-Lips_Corner.L/R` (up/wide), `ACT-Cheek_Outer`, `ACT-Eyelid_Upper/Lower`, `MSTR-Eyebrow` (up/down/in),
  `ACT-Sneer`, `MSTR-Jaw` rotation. Snow: `ACT-Lips_Corner` (x in/out, y up/down), `CheekRaiser`, `CenterCheekRaiser`,
  `MSTR-Eyelid_Upper/Lower`, `MSTR-Eyebrow`, `Jaw` rotation. The rigs turn these into action-constraint poses of
  ~150–250 face bones plus corrective shape keys (Rain: 25 on the head, Snow: 50).
- `tools/job.py` — builds the shot list (character, engine, views, expressions, resolution).
- `tools/run_eevee.sh`, `tools/run_eevee2.sh`, `tools/run_clay.sh` — the batches that made the pictures.
- `tools/face_anim.py` — frames of a face going through its expressions (eased in-between control values),
  Workbench with their material colours; the mp4 is made with
  `ffmpeg -framerate 24 -i f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 26 face.mp4`.
- `tools/render_hbm.py` — Human Base Meshes: each piece alone, smooth (subdivision / multires level), clay; wire on
  the base cage; `parts` mode renders the sheet of what the bundle holds.
- `tools/compose.py` — lays the renders out into the page's webp sheets with Russian labels.
- `tools/grid.py`, `tools/inspect*.py`, `tools/probe_head.py` — quick contact sheets and probes of the files
  (objects, shape keys, drivers, bone collections, action-constraint ranges) used to find the controls.

Repeat: download and unzip into `/home/user/cache/n5-heads/{rain,snow,hbm}`, then run the three `run_*.sh`,
`render_hbm.py` (both modes), `face_anim.py` for each character, ffmpeg, `compose.py`.

## Ours on the page

Existing pictures only, by relative path: `docs/pictures/heads-anime/final1.png`, `sheetC-expr.png` (Г1),
`heads-3d/mesh/sheet-7heads.png`, `heads-3d/sheet-expressions.png` (Г2), `heads-wrap/sheetW7.png`,
`sheetW9-mouths.png` (Г3), `designed-form/sA-final.png` (Т7), `anny-space/bodies-on-moood-mesh.png` (Т8).
Our faces are lit by our own toon shader in three.js and theirs in Blender; the clay sheets compare forms without
colour (Г2's heads are the nearest: geometry only).

## StdGEN

Code and weights are published (github.com/hyz317/StdGEN, Apache-2.0; huggingface.co/hyz317/StdGEN). It needs an
NVIDIA GPU: CUDA builds of torch and xformers, `nvdiffrast` (CUDA rasteriser), `pytorch3d`, SAM ViT-H, two
1024-px diffusion models and a mesh reconstruction model; the code calls `.cuda()` in ~60 places. Here there is no GPU
(4 shared CPU cores), so it was not run. Its own Hugging Face demo (Space hyz317/StdGEN) is down: on 2026-11-03 it
stood on `cpu-basic` hardware with RUNTIME_ERROR "Found no NVIDIA driver". The page shows only the authors' teaser,
labelled as theirs.
