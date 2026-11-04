# Findings: other people's tools, drawn styles, drawings to 3D

What three rounds of work found (2026-11-03/04), for the agents who come next. Details, numbers and how to repeat are
in each page's `notes.md`; the briefs the agents worked from are in [briefs/](briefs/).

## The main finding

**Draw first, then build the 3D from good ready bases fitted to the drawing.** An agent draws a character in a
style taken from real works (rules written from samples, the drawing in SVG by code), and the 3D is assembled from
artist-made bases — Anny's body on SOMA, a head from Blender's Human Base Meshes — fitted to the drawing's front and
profile, with the face and colour from the drawing's own code, judged by overlaying on the drawing. Four of five
characters made this way came out close to their drawings and attractive (`to3d/` Р1–Р4), better than anything built
from parameters before. Decisions about beauty are made where an agent makes them well — on the drawing — and the 3D
follows.

## Drawing styles (`styles/`)

- Taking a style from real works and writing its rules from samples gives far more attractive characters than
  inventing a look. The same cast in twelve styles makes the styles comparable.
- SVG drawn by code is native for flat and graphic styles: graphic flat (С3), mid-century gouache (С9), 1930s rubber
  hose (С11), pen and watercolour (С12), ligne claire (С10), Klaus-like light (С2) came out best.
- Styles drawn by projecting a 3D proxy (Pixar С1, Arcane С4) looked like dolls and mannequins: the life of drawing
  is lost. A proxy is good for consistent turnarounds; the look needs drawn decisions on top.
- Weak everywhere: hands (hidden, mittens, tubes), stiff standing poses without a line of action, an even line
  without pressure. Women's faces are harder than old men and children — caricature carries those.
- A style's drawing code is reusable: shared parts (head, face, line, colour) apart from per-character modules; each
  style's `notes.md` says how to add a character.

## Drawings to 3D (`to3d/`)

- **Bases.** Anny's body (engine packs, SOMA, Kimodo through the engine) for human proportions; Anny's child bodies
  for children; for 2–3 heads tall, our indie constructor (`experiments/indie`) — a human body can't be bent into it.
  Heads from Human Base Meshes (CC0): the "animation" head for ligne claire, the stylised one fitted by points
  elsewhere; fitting by points of the silhouette works, fitting by height slices gives folds.
- **Faces.** In drawn styles keep the face as a drawn layer: the style's own SVG functions projected from the front,
  redrawn each frame from a few numbers — expressions match the sheet line for line. A modelled eye with lids (Р2)
  suits a style whose eyes are dots in lids. Close eye sockets and lips of the base with a smooth patch when the
  features are drawn.
- **Where the drawing lies.** Drawn front and profile often don't make one head (the eye deeper in profile than the
  front allows; three-quarters drawn at different angles for eyes, ear, nose). Follow the front and say so.
- **Looks.** Flat colour + one shadow step + outline works in the browser; ligne claire via Blender Freestyle, an
  even pixel outline in the browser; Klaus light (warm key, lilac shadow, rim, cast shadows) works on the head but
  blotches appear where face normals aren't smoothed. Running the render through the drawing's own SVG filter keeps
  paper and gouache (Р3).
- **Alive.** Blinks at uneven intervals (close ~70–80 ms, open ~140–170 ms, also on big gaze shifts), saccades with
  holds of 0.2–1.6 s, the gaze leading a head turn by ~0.25 s, speech as syllable mouth shapes with pauses, expressions
  blended — schedules from a seeded random stream, no sines; the same moment always looks the same (scrubbing works).
- **Motion.** Kimodo's motions retarget well onto these bodies. Weak: `idle`/`stand` stoop or bow the head; short
  arms make waves tiny and hands reach the ears; sitting puts them on the floor. Clothes and hair are skinned shells,
  not cloth — skirts in a wide step stretch like trousers.
- **Not good yet:** realistic Anny hands against drawn mittens (replace them), shells for clothes and hair, the
  hardest face (a young woman in a painterly style, Р5).
- Engine note: centres-of-rotation skinning takes ~15 s to prepare on a 48k-vertex dressed mesh — too slow for the
  browser; viewers used dual quaternions. Worth an issue.

## Other people's tools (`tools-demo/`)

- **Better than ours:** Blender Studio's character heads (Rain, Snow…, CC-BY) — eyeballs under thick lids, lips with
  a rim, mouth corners into cheeks, loops around eyes and mouth, expressions as skin motion. Use as a model and as
  parts (eyes, teeth), not whole characters. Human Base Meshes (CC0) are the bases used in `to3d/`.
- **Partly better:** GarmentCode — garments as sewing patterns sewn and draped on Anny, honest fit and folds; realism
  only, rest only, 4–17 min per garment on CPU (its simulator's licence is non-commercial). MToon — a cleaner shade
  and outline, but beauty comes from the artist's textures, not the shader.
- **Not better:** libigl (our deformers stand on the same maths; ARAP keeps limb thickness — worth as a layer over our
  arc), Blender cloth and HOOD against our О3, Blender hair (a realistic wig, not cartoon locks), Monster Mash (soft
  joins, flat depth). HairDeck looks right for stylised hair with springs, but its main path needs a GPU and two gated
  models (SAM 3, DINOv3).
- **StdGEN (picture → 3D body, clothes, hair).** Guesses the shape from all sides in ~3 min on an A100; surfaces are a
  cheap-toy draft (blotches, holes, smeared faces). Cleanest on flat simple styles; breaks on strong caricature, on
  silhouettes, on painterly and watercolour. Its copy `completelyreal/StdGEN` on Hugging Face needs Python 3.10 and
  pydantic 2.10.6 pinned; it doesn't fit 24 GB. Useful at most as a hint for unseen sides.

## Working

- One agent per page with a common brief, working only in its folder and a cache outside the repository; the
  orchestrator looks at every result and commits. Asking every page for "what the tool does in its own cases" made
  the tool pages understandable.
- The studio's Kimodo GPU can take longer than 25 minutes to wake; an order may fail with `wake` and succeed later.
