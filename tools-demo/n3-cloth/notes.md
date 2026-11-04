# Н3 — Ткань в движении: notes

What the page compares: our О3 cloth (`experiments/cloth`, XPBD written here) against Blender's cloth simulator and
the learned simulators HOOD and ContourCraft — the same garments on the same Anny body through the same Kimodo
motions, drawn in the same studio from the same camera.

## How it was done

1. **Our run, exported** — `tools/export.mjs` runs `experiments/cloth` unchanged in Node (three 0.160.0 from npm in
   `/home/user/cache/n3-cloth/node_modules`): the page's outfit and motion (read from its `index.html`), no wind. It
   writes to `/home/user/cache/n3-cloth/runs/<outfit>-<motion>/`: the body's skin every frame (`body.f32`), the
   joints' matrices (`E.f32`), each garment as dressed (`<g>-rest.f32`, `-tris.u32`, `-hold.f32`, skin weights) and our
   cloth's points every frame (`ours-<g>.f32`). Frame 0 is the rest pose the garments were put on in; then 0.5 s
   standing, 0.9 s easing into the motion, then the motion.
   `node tools/export.mjs w-blouse walk /home/user/cache/n3-cloth/runs/w-blouse-walk` (also `w-blouse sit`, `w-tee roll`).
2. **Blender's cloth** — `tools/blender_cloth.py` (Blender 4.5.15 LTS, background):
   `blender -b -P tools/blender_cloth.py -- <run dir>`. The body is an animated mesh (PC2 point cache + MeshCache) with
   a Collision modifier, the floor a collision plane. Each garment: its dressed shape carried by the skin every frame
   (PC2, what pinned points follow), a pin group from our own hold weights (waistband, neckline, cuffs), Cloth with
   Blender's own presets nearest each fabric (silk 0.15/5/5/0.05, cotton for jersey 0.3/15/5/0.5, wool-ish for
   suiting 0.4/40/40/5, denim 1/40/40/10 — mass/tension/shear/bending), quality 10 steps, collision quality 4,
   distance 5 mm, self-collision on (2 mm). The inner garment also gets a Collision modifier and the outer one collides
   with a collection of floor + body + inner garment (Blender refuses a cycle if both collide with each other).
   Writes `blender-<g>.f32` and `blender.json` (time).
3. **HOOD** — clone `github.com/dolorousrtur/hood` (commit 9bc10761), data from its Google Drive link
   (`hood_data.zip`, 604 MB, via `gdown 1RdA4L6Fy50VsKZ8k7ySp5ps5YtWoHSgs`), unpacked in
   `/home/user/cache/n3-cloth/dl/hood_data`. Environment: `uv venv -p 3.10` (HOOD's dataclasses fail on Python 3.11+),
   torch 2.5.1+cpu, torch_scatter/torch_sparse from data.pyg.org (torch-2.5.0+cpu), torch-geometric 2.4.0, smplx,
   omegaconf, einops, munch…, and pytorch3d 0.7.8 built from source for CPU (`FORCE_CUDA=0`, ~25 min).
   `tools/run_hood.py <run dir> <garment> [frames]` uses HOOD's "from any pose" mode with a mesh sequence (no SMPL
   needed): our dressed garment as the template (`add_coarse_edges(…, 4)` as `obj2template` does), Anny's skin as the
   body sequence, model `postcvpr.pth`, device cpu, 2 threads. Material through HOOD's own overrides: our fabric's
   density and bending rigidity, stretch moduli at the middle of HOOD's range. In this mode HOOD pins nothing: a
   garment hangs on the body by itself, so only tops (T-shirt, blouse) make sense; it simulates one garment at a time.
   HOOD's step i gives the cloth for the body's frame i + 1 (its `pred_pos` goes with the obstacle's `target_pos`).
   `tools/hood_example.py` runs HOOD's own example (skirt.obj on the example SMPL mesh sequence) for "what it is made
   for"; `tools/render_hood_example.py` draws it in Blender EEVEE.
4. **ContourCraft** — clone `github.com/Dolorousrtur/ContourCraft` (commit d606432c). Not run: its inference imports
   `cccollisions` (CUDA kernels for the impulse-based intersection solving that is the point of the method — the
   CCCollisions repo builds only with nvcc against CUDA), and `utils/selfcollisions.py`, `material/utils.py`,
   `utils/simulator.py` move data to `cuda`; its install also asks for RAPIDS cudf/cugraph (GPU only). There is no GPU
   here. The trained `contourcraft.pth` is in the same data archive.
5. **Pictures** — `tools/view.html` is the studio of `experiments/cloth/index.html` (lights, floor, materials, hair and
   shoes carried by the skin, the skin sunk 4 mm under close cloth, camera following the pelvis and eased the same
   way), drawing a run with one simulator's garments; `tools/shoot.cjs` drives it in headless Chromium (no server: the
   page's requests are answered from disk through Playwright's routing); `tools/film.sh` puts the simulators side by
   side in one h264 mp4. `tools/measure.py` counts cloth points deeper than 2 mm in the body (as `sim.js`'s
   `inside()`) and the mean edge stretch against the dressed shape, every other frame.
6. **Uses** — `tools/blender_uses.py <out> table|flag`: Blender's cloth as its manual uses it (a tablecloth falling on
   a round table with the Cotton preset as is; a flag in gusty wind with a pinned edge, its mass per point from the
   fabric's weight — with the preset's 0.3 kg per point no wind lifts 3721 points; the wind set a little across the
   flag's plane — along a flat cloth it pushes on nothing), EEVEE 8 samples. A pressure cushion was tried and dropped
   (it crumpled and slid out of frame: my setup, not shown). Encoded with ffmpeg (libx264, crf 26).

## What came out (also on the page)

- Blender's masses: its presets give mass per point for coarse meshes; on our 5–9 thousand points the garments are
  far too heavy (they sag, stretch a few per cent). Physical mass per point (fabric kg/m² × area / points) with the
  same stiffness and quality 10 made the blouse unstable mid-walk (sleeves torn into strings, 12% mean stretch, 4% of
  points in the body) — `pics/blender-light-mass.webp`; the page shows the preset runs.
- HOOD on our body: tops (T-shirt, blouse) sit well while the body stands, and slide through/off the body as soon as it
  moves (blouse: 20% of points inside the body on average). On HOOD's own mesh-sequence example the unpinned skirt
  slides to the floor too (this mode pins nothing). Possible reasons, not checked further: the network is trained on
  SMPL bodies and its own garments' mesh density (ours: cloth edges ~9 mm, body ~6 mm; HOOD's ~12–14 mm — its
  successor lists "re-meshing to support outfits of arbitrary resolution" as not done yet); our body moves about twice
  as far per frame as in its example.

## Times (4 shared cores, heavily loaded by other agents; times are wall clock)

| run (frames) | ours (Node) | Blender | HOOD (CPU, 2 threads) |
|---|---|---|---|
| blouse+skirt walk (200) | 51–57 s | 473 s (at the same load as ours' 51 s); 1744 s under heavy load | blouse only, 150 frames: 2343 s |
| blouse+skirt sit (175) | 74 s | 1932 s (heavy load) | — |
| tee+shorts roll (180) | 28 s | 970 s (heavy load) | T-shirt only: 1953 s |
| HOOD's example skirt (90) | | | 1032 s |

Measures (`tools/measure.py`, every other frame; points >2 mm in the body, mean / max %; mean edge stretch %):
walk — blouse ours 0/0.01, 1.3%; Blender 0.02/0.09, 2.9%; HOOD 20/32, 2.5%. skirt ours 0/0.02, 1.1%; Blender 0/0,
0.2%. sit — blouse ours 0.04/0.22, 4.5%; Blender 0.03/0.13, 8.3%; skirt ours 0.07/0.32, 2.8%; Blender 0.01/0.26,
0.3%. roll — T-shirt ours 0/0.04, 3.6%; Blender 0/0.04, 8.8%; HOOD 0.01/0.21, 5.3% (the metric misses cloth lying a
hair under the skin; HOOD's T-shirt visibly goes into the body). The run files and these numbers are in
`/home/user/cache/n3-cloth/runs/*/` (`measure.json`, `blender.json`, `hood-*.json`).

## Licences

- HOOD, ContourCraft: MIT (Artur Grigorev). Their data archive: the example skirt/body come from SMPL-based data
  (the SMPL model itself is not included and wasn't used).
- Blender: GPL; the pictures are our scenes.
- The Anny body, garments and motions are ours (`experiments/cloth`, `experiments/data`).
