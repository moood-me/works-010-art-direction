# Н4 «Волосы» — notes

What this page compares: our hair (В1, `experiments/hair`: locks along guide curves drawn as swept surfaces, the
hair shading in three.js, chains simulated per lock) against

1. **Blender 4.5's own hair tools** — Curves objects with the hair node groups of its Essentials asset library
   (`datafiles/assets/geometry_nodes/procedural_hair_node_assets.blend`), the Principled Hair BSDF in Cycles, and,
   for motion, Blender's hair dynamics;
2. **HairDeck** (https://github.com/hyz317/HairDeck, Apache-2.0, released 2026-10-30) — stylised hair cards with
   spring-bone chains from one image.

## What ships in Blender 4.5 for hair (checked, not guessed)

The Essentials hair library has 27 node groups: Attach Hair Curves to Surface, Blend, Braid, Clump, Create Guide Index
Map, Curl, Curve Info/Root/Segment/Tip, Displace, Duplicate, Frizz, Generate, Hair Attachment Info, Hair Curves Noise,
Interpolate, Redistribute Curve Points, Restore Curve Segment Length, Roll, Rotate, Set Hair Curve Profile,
Shrinkwrap, Smooth, Straighten, Trim, shape_range. **There is no hair-dynamics node group in 4.5** (none in the
library; the new Curves hair has no built-in simulation). What Blender offers for motion of hair is the older
particle hair system with "Hair Dynamics" (the cloth solver for hair, with collisions). Blender converts a Curves
object to a particle hair system with its own operator `curves.convert_to_particle_system`; that is what is used here.

## How the Blender side was made (tools/)

- `bodies.mjs` (node 22, three 0.170 from npm in the cache): Anny's bodies exactly as `experiments/hair/live.js` puts
  them — the baked woman / child / man from `experiments/data`, the T-shirt, trousers and shoes riding the skin, the
  skin sunk under the clothes, the same timeline, Kimodo motions (`experiments/cloth/motions`) and head turns
  ("look", "snap"). Writes the rest pose (JSON) and every frame's points (PC2) and Head matrices.
  `node --experimental-default-type=module bodies.mjs <repo> <out> woman walk look 6 idle snap 6`
- `scene.py`: the body into Blender, the skull fitted with an ellipsoid (body points above the brows), a scalp mesh cut
  from the body inside a drawn hairline (one per part, UV by Smart UV Project, painted in the hair's colour as grooms
  do), guide curves → a Curves object attached to the scalp (`curves.snap_curves_to_surface`), the hair material
  (Principled Hair BSDF, Chiang, melanin + tint, darker roots), the light and camera of `experiments/hair` (key from
  front-right-above, cool rim from behind, 22° lens, the camera on the head at the same yaw/pitch/distance).
- `styles.py`: four hairstyles of В1 as guide curves (the groom an artist would draw with Blender's curve sculpting,
  written as numbers): Гвен (bob, side part, swept fringe), Альва (long, centre part), K-pop ponytail (with a plain
  torus as the tie), Марко (boy's mushroom cut, on the child).
- `build.py`: per part, Blender's node groups as modifiers: Interpolate Hair Curves (children from the guides over the
  scalp) → Clump (big locks, 3–5 cm) → Clump (small locks) → Shrinkwrap (out of the body where the groom went in) →
  Smooth → Set Hair Curve Profile. Renders front and back in Cycles (CPU, 24 samples, denoised).
  `blender -b --factory-startup -P build.py -- gwen <out> 24`
- `motion.py`: the body by the Mesh Cache modifier (PC2), the scalp and hair on an empty keyed with the Head joint;
  `dyn`: each part's guides converted to a particle hair system with Hair Dynamics on (bending and pin stiffness per
  hairstyle), a collider = the body below the chin, decimated (against the full 17k-point body the hair solver took
  minutes a frame; with the head in the collider every root starts inside it); each frame the simulated guides
  (`co_hair`, resampled) are written back into the Curves object and its node groups grow the hairstyle again.
  `blender -b --factory-startup -P motion.py -- gwen walk-look <out> dyn 2 6` then ffmpeg.
- `uses.py patches`: the node groups by themselves on one patch (the "Что умеет сам по себе" picture).

## HairDeck (tools/hairdeck_pc.py, render_hd.py, to_charm.py)

- The image path (what HairDeck is for) needs SAM 3 and DINOv3; both are **gated** on Hugging Face (licence must be
  accepted by a logged-in person, then `hf auth login`). This session has no token, so the image model could not run
  here. The authors' hosted demo (a Hugging Face Space on ZeroGPU) was not used: sending pictures to a public service
  was not allowed from this session.
- The release targets one NVIDIA CUDA GPU; `HAIRDECK_DEVICE=cpu` exists ("correct, far too slow for the diffusion
  models"). Its **point-cloud model** needs no gated weights (Dora-VAE 1.1, Apache-2.0, public) and was run here on the
  CPU: `scripts/setup/download_weights.py --only charm_test_pc dora` plus the checkpoints from hyz317/HairDeck
  (card VAE, point-cloud DiT, chain DiT, data files), torch 2.8.0 CPU in a venv (Python 3.13).
  Two CHARM test point clouds: conditioning 11 s, 50 Euler steps with CFG 2 for both: 384 s on 2 threads of a
  shared, busy 4-core machine (21 and 166 cards).
- `to_charm.py` turns our Blender hairstyle into a CHARM-format point cloud (10,000 points with normals, moved into
  the dataset frame by the mean skull centre and hair top of CHARM's test characters); HairDeck's cards for it are
  moved back onto the same Anny body and rendered in the same views (`render_hd.py ours`).
- Not done: chains for these cards and their motion. HairDeck's chain model works in its "head frame" (a fitted head
  per character, which our heads don't have in their data), and its own head-turn preview renders with pyrender
  through EGL/OSMesa, which this machine lacks (libEGL missing — the same reason Blender's EEVEE doesn't start).

## Sources and licences of third-party pictures

- `pics/hd-teaser.webp`, `hd-spring.webp`, `hd-style.webp`, `hd-gen.mp4`, `hd-move.mp4`: HairDeck's own published
  figures and demo video (https://huggingface.co/hyz317/HairDeck, `assets/`), Apache-2.0 per the repository; the
  character images inside them are the authors' inputs. Reduced in size, the video cut (2–10 s and 15.5–21.5 s).
- `pics/hd-cpu-charm.webp`: CHARM test point clouds 000 and 001 (https://huggingface.co/datasets/hyz317/CHARM,
  GPL-3.0) and HairDeck's cards for them, made here.
- `pics/now-*.webp`: cut from our `docs/pictures/hair/motion/sheet-rest.png` (the designed hairstyle, front and back).

## Versions

Blender 4.5.15 LTS; HairDeck at commit of 2026-11-03 (shallow clone in `/home/user/cache/n4-hair/hairdeck`);
torch 2.8.0+cpu; three 0.170.0; node 22.

## Results and timings (this machine: 4 shared cores, 5–6 agents at once)

- Static pictures: Cycles CPU, 440×520, 24 samples: about 1–2 minutes a view; 59–73 thousand strands per hairstyle.
- Motion: the hair solver with the coarse collider ~0.2 s a frame without collisions, a few seconds with; the render
  is the cost: 360×420, 6 samples, ~40 s a frame (Гвен: 6 s walk with "look" head turns, every 2nd frame → 15 fps;
  Альва: 5 s standing with "snap" head turns, every 3rd frame → 10 fps). `ffmpeg -framerate 15 -pattern_type glob
  -i '0*.png' -c:v libx264 -crf 24 -pix_fmt yuv420p mot-gwen.mp4`.
- Seen in the motion: the hair sways softly, but on a head turn the fringe and side locks fall across the face — the
  head can't be in the collider (the roots grow from it), only the pin spring holds them.
- Look: real strands with a physical hair shader read as a realistic wig, not as the big drawn locks of the
  references; Clump gives locks, but no clean stylised silhouette came out of these node groups here.
- HairDeck on our clouds: 23 cards (Гвен), 30 (Альва), 371 s for both on 2 threads; crown left bare, a card over the
  face; our heads are not its VRoid heads and the frame mapping is approximate.

## Not used / dead ends

- EEVEE: does not start headless here (no libEGL), so Cycles CPU only.
- The first collider (whole body, then a decimated whole body) made the hair solver take 10–130 s a frame; the
  collider below the chin fixed it.
- Shrinkwrap Hair Curves with Above Surface 0.5 pulled the whole groom onto the skin (flat hair); 0 only pushes out
  what went under the surface.
