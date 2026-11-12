# Р37 — Аня, японская гравюра: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, third round; brief: `docs/briefs/to3d.md`, "Third round"):
Аня of style С13 (`styles/s13-ukiyo-e`, the woodblock print: ukiyo-e and shin-hanga) made a 3D character that moves by
Kimodo through the engine and is **printed every frame as a sheet of that style** by the style's own means. Asked for
by Pavel through the orchestrator: С13 is one of the four new styles, with no character in 3D yet; this is the first
try at how the style lives in 3D. Р38 (Марат, `to3d/r38-s13-marat`) is made on the same renderer.

## What was decided, and why

- **The starting point is Р12 / Р35 / Р36** (pen and watercolour): there the 3D is never shown as such — each frame is
  drawn from it by the style's code. A print is the same kind of thing (a picture made of a few flat means), and its
  means are simpler than a pen's: so `tools/web/print.js` is Р36's `figure.js` with the print's means in place of the
  pen's, and `tools/web/kit.js` is `styles/s13-ukiyo-e/tools/kit.py` and the face of `parts.py` ported to JavaScript.
- **No light.** The rule of the style: no shadows, no volume. The form is rendered once, unseen, into "which colour
  block is each pixel, how far is it"; nothing is shaded.
- **Colour blocks** are that picture in the drawing's flat colours (one image, softened by half a pixel).
- **A cloth pattern is printed flat** — the style's rule ("узор не гнётся по складкам"). The drawing's own patterns
  (`asanoha` on the cardigan, `blossoms` on the dress) are SVG patterns laid over their block through the block's
  picture as a mask. The pattern's origin travels with a joint of the body (the cardigan's with the chest, the dress's
  with the hips), its size with the figure's size in the picture; it does not turn or bend with the body. In a turn the
  form slides under its pattern — that is what "printed flat" means in motion, and it is said on the page.
- **The key block**: silhouettes and open edges found on the mesh (Р12's way), chained, smoothed, and drawn as brush
  strokes by `kit.py`'s `brush_poly`: the weight follows the stroke's direction (the brush held at a slant), heavier
  and more varied on cloth (3.1–3.4, nib 0.6) than on skin (2.0, nib 0.3), ends pointed; no tremor, no breaks along a
  line (a cut line, not a pen's). A line lifts at a sharp corner. Folds of the skirt are strokes of the form with the
  print's "nail head" start and long tail (`taper`). `kit.py`'s rule that a line keeps part of its weight when the
  figure is small is kept (`wk = px-per-unit ^ 0.45`).
- **Hair**: a flat dark mass (one shell from the crown to the shoulder blades, open in front along the drawing's
  hairline, falling along the cheek and behind the shoulders); the hairline is `kit.py`'s `fringe` — separate hairs
  growing out of the shell's edge onto the forehead; a few light lines down the hair (`strands`' colour) are columns
  of the shell. The ears are under the hair (laid flat on the head's side: left out, they were a hole seen in profile; left as they are, their tips came through the hair).
- **The face is drawn, not modelled** (as in Р12): `parts.py`'s `eye`, `brow`, `nose`, `mouth` and the cheek's bokashi
  in the head's front units, laid on the 3D head through a grid (build.py). Each feature has its own frame on the
  turned head; the far eye is shorter and kept on the face; near the profile the near eye sits back from the contour
  and the far half of the mouth shortens (the drawing's `layout('s')`). The nose is `parts.nose`'s stroke — down with
  a hook, and the nostril — laid on the 3D nose on its far side; in profile the head's contour carries the nose.
- **A print's face is flatter than a head.** With a head of true depth the far eye of a three-quarter view is already
  round the corner at 43°. `head.py` got two numbers (`PUSH_TOP`, `FACE_R` in `drawing.py`): the face is made one plain
  round plane from the forehead down; and the comparison's three-quarter is taken at 0.55 rad, not 0.75.
- **The sheet**: the tinted ground with the band of bokashi along its top, the border, the name slip and the red seal,
  and wood grain, paper and age over everything — `kit.py`'s `svg()`. They belong to the sheet: they stay still while
  the figure moves. In films the camera follows the figure, so it walks "in place on the sheet".
- **Hands**: Anny's own hands, a little smaller, drawn with the thin line of skin — the print draws every finger as a
  separate tapering shape, so real fingers suit it better than the mittens of other styles.

## Steps and what each base gave

1. **Body — Anny's woman** (`engine/data/bodies/moood-woman`): SOMA's 77 joints and weights. `build.py` moves the
   joints to the drawing's (1.07 mm a head unit, 1.68 m to the hair's top, 7.8 heads): long legs close together, a
   short trunk, a long thin neck, narrow sloping shoulders; each limb's skin turns and stretches with its bone and is
   thinned. Of the skin the hands, the shins and the feet are seen (feet smoothed into slippers, the sole kept flat;
   the slipper's colour is cut by the foot's rest height).
2. **Head — Human Base Meshes stylised head** (CC0), `head.py` (Р36's): heights by landmarks, then each height's width
   and front/back to `parts.head_pts` 'f' and 's' (`drawing.py`); between the cheekbone and the chin the width is
   measured in front of the ears only (`FACE_ONLY`). Eyes and mouth laid flat (they are drawn); the nose laid flat and
   the drawing's small one put on.
3. **Clothes** (`shells.py`): the dress — one loft from the round neckline (the top rows dip in front) to the hem
   below the knee, soft folds and a waved hem; a patch of chest inside the neckline; the cardigan — open in front, a
   round yoke; sleeves — tubes. The skirt hangs on the hips and takes part of each thigh; in a step it is pushed off
   the legs (Р1's).
4. **Hair** — `build.py` (`hair_row`).
5. **Look** — `web/print.js`, `web/kit.js`, `web/char.js` (what is hers: blocks, patterns, face, expressions, sheet).
6. **Alive** — `web/face.js` (Р12's timing: blinks, saccades, gaze leading the head, speech, blended expressions)
   driving `parts.EXPR`'s numbers. A blink brings the lid down (the print's closed eye of a laugh is an arc up —
   another thing). Speech is the sheet's round mouth by syllables.
7. **Motion** — one engine body; `Figure` retargets Kimodo's motions; nothing of the engine changed.

## How to repeat

```
cd to3d/r37-s13-anya/tools
C=/home/user/cache/to3d-r37-s13-anya; mkdir -p $C; (cd $C && npm install three@0.160.0)
/home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
    --python hbm_export.py -- $C/hbm_head.npz        # the base head as arrays (once; through a shared lock)
python3 build.py                # → ../data/anya.json, anya.bin
./look.sh                       # a quick sheet to look at → $C/look/body.jpg, head.jpg (needs $C/look.json, see below)
python3 make_pics.py stills     # ../pics: compare, overlays, portrait, steps, back, expressions
python3 make_pics.py films      # ../pics: turn, walk, bow, talk (12 pictures a second)
```
`make_pics.py` and `look.sh` run the browser through the shared locks (`/home/user/cache/heavy.N.lock`, the first free
one). `shots.mjs jobs.json outdir` serves `/home/user/` and drives `web/view.html?pack=…` with Playwright (software
WebGL; three.js routed to the cache's `node_modules`). `look.json` is a jobs file of seven shots (`f q s b hf hq hs`:
the figure from four sides, `cam: {mode: 'ortho', h: 1.9, cy: 0.86, yaw}`, and the head, `h: 0.5, cy: 1.5`).
By hand: serve the repository root, open `to3d/r37-s13-anya/tools/web/view.html` (three.js from jsDelivr).

`who.py` holds what is this character's for `make_pics.py`: the drawing's sheets' scales, the figure's pose, the films.

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`; Anny: NAVER, Apache-2.0; MakeHuman
  CC0; SOMA rig: NVIDIA, Apache-2.0).
- Kimodo motions: `engine/motions` (walk, bow, idle).
- Р12 / Р36's renderer, build and face timing, and the С13 drawing and its code (`kit.py`, `parts.py`, `anya.py`,
  ported): this repository. three.js 0.160.0: MIT. No neural images.

## What the style keeps in 3D and what it doesn't (the first try)

Keeps: the sheet (ground, bokashi band, border, name slip, seal, paper and grain), flat colour, the patterns printed
flat, the brush line whose weight follows direction, the face of a few exact lines with its expressions line for
line, the hairline's separate hairs, folds as tapering strokes.

Doesn't:
- **The print's three-quarter face is not a turned head.** The drawing's `q` head is its own outline with a wide far
  cheek; the 3D gives a true turn — the far cheek narrower, a long jaw line from the chin to the hair. The profile
  is the 3D's own, nearer to a real profile than to the drawing's.
- **Composition.** A print's figure is built as one arc (the tilt of the head, the bend of the back, the step); the
  3D stands as Kimodo and a simple pose put it. The figure sheet's pose is approximated (the head bent, an arm across
  the chest); the sprig of camomile is not made.
- **Lines are traced.** A master cuts few lines and each is a gesture; here every silhouette is drawn, exactly.
- **The pattern in motion** stays flat and upright while the body turns under it — true to the rule, odd to the eye
  in a fast turn.
- Hair, skirt and cardigan are skinned shells, not cloth: the hair does not swing.
- Feet seen from the front read as standing on tiptoe (the drawing turns the feet sideways).
