# Р3 — Тим, середина века: from the drawing to 3D

What was done, why, and how to repeat it. Brief: `/home/user/cache/BRIEF-to3d.md` (build the 3D from good ready bases
fitted to our drawing, not by a neural net). The drawing: `styles/s9-midcentury` (figure-tim, turn-tim, expr-tim; the
code that draws them: `tools/tim.py`, `face.py`, `kit.py`, `scenery.py`).

## What was decided, and why

- **The face is painted, not modelled.** In the mid-century style Tim's features are tiny marks (dot eyes, a red
  smirk, round blush with freckles). A modelled eye with lids would not be this style. So the base head's face (eyes,
  nose, mouth and their linings) is cut out and closed by a smooth patch, and the features are a picture drawn by the
  drawing's own code (`face.py` eye/brow/mouth, `tim.py` OWN expressions) projected on the head from the front. An
  expression is another picture: the four of expr-tim are the same calls with other arguments.
- **The look keeps the gouache**: the shader paints flat paints of the drawing (`tim.py` colours) with a second tone
  of the same paint where the form turns from the light (the style's rule: no light-and-shade, a second tone), the
  shirt's stripes by height, faint unevenness of the paint over the form. Then every picture is laid on the drawing's
  own backdrop and passed through the drawing's own SVG filter `gouache` (ragged edge, paint density, grain) and paper
  — so the 3D and the drawing share paper and paint.
- **Proportions from the drawing**: about 3½–4 heads; head 0.27 m chin to crown, body below the chin 0.85 m, thin
  limbs, short arms, short shorts.
- **Where the drawing contradicts itself** the front view wins: the front and profile heads of turn-tim can't be one
  round head (in profile the eye sits 18 units behind the face's front, in front it is only 24 from the middle), so the
  3D profile has the eye nearer the front than the drawn profile. The three-quarter drawing is itself drawn at no single
  angle (eyes like 15°, ear like 26°, nose like 44°); 3D is shown at 29°.
- The back of the hair goes a little lower than the drawn profile (to the nape), so the back view is not bald.

## Steps and what each base gave

1. **Body — Anny's child** (`engine/data/bodies/moood-child`, the engine's, SOMA skeleton). `tools/body.py`: an affine
   map per joint (scale along the bone and across it), joints rebuilt down the chain, every vertex moved by its skin
   weights' blend of its joints' maps; frames kept (the retargeting reference). Gave: a surface that bends well in
   Kimodo's motions, and skin weights for everything cut from it (clothes).
2. **Head — Human Base Meshes, stylised head** (Blender, CC0). `tools/hbm_export.py` (Blender: the head subdivided
   once, faces seen from outside), `tools/hbm.py`, `tools/head.py`: the face cut out and closed by rings of quads,
   faired biharmonically (libigl); then a thin-plate warp (scipy RBF) from landmarks on the base's silhouettes to the
   drawing's front and side outlines (`tools/drawing.py`: the outlines from tim.py), round cross-sections at the jaw,
   the neck to the drawing's thin neck. In `build.py`: the ears made larger and turned out (they stick out in the
   drawing), cheeks smoothed, the chin's underside drawn up flat, a button nose (a small ball where the drawing's nose
   is), the neck a second tone darker under the jaw line (the drawing's SKIN_D). Gave: a skull, ears and clean topology
   that a sculptor made; its face was replaced on purpose.
3. **Colour and features — our SVG**: `tools/face_tex.py` → `face/<expr>.png` (1024², the front view's head units
   −128…128), rasterised by headless Chromium (`svg2png.mjs`). The hair's dry-brush strokes are in the same picture.
4. **Clothes** — shells cut from Anny's own surface (`tools/meshcut.py`: a mesh cut along any level of a scalar, so the
   edges are clean curves): the shirt (hem, short sleeves, a crew neck drawn in round the neck, stripes below the
   shoulders, a cream collar band), shorts (wide legs flaring), socks with a red band (paint on the leg). Shoes are lofted
   along each foot (rounded sections on a flat sole, red with a white sole) — the foot's own shell kept its toes. Each takes the body's skin weights. Paints change only along cut lines
   (`split` in build.py), never across a triangle. Not cloth: no simulation (see "what is not done").
5. **Hair** — a shell over the skull above a hairline: the drawing's zigzag fringe in front, its side outline at the
   sides and back (blended by the angle round the head), thicker on top as the drawing's crop; a cowlick as a tapering
   flattened lock. Rigid on the head.
6. **Look** — `tools/web/tim.js`: a three.js ShaderMaterial; then `tools/compose.py` lays the render on the drawing's
   backdrop through its gouache filter.
7. **Motion** — the model is one engine body (`makeBody`) on SOMA's 77 joints; `Figure` of `engine/src` retargets
   Kimodo's motions (walk, bow) and skins it by centres of rotation; nothing of the engine was changed.

## How to repeat

```
cd to3d/r3-s9-tim/tools
/home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
    --python hbm_export.py -- /home/user/cache/to3d-r3-s9-tim/hbm_head.npz
PY=/home/user/cache/n1-deform/venv/bin/python          # numpy, scipy, libigl
python3 body.py; $PY head.py; python3 face_tex.py; $PY build.py      # → /home/user/cache/to3d-r3-s9-tim/tim.json/.bin
for k in turn expr figure; do python3 compare.py $k '{"motion":["bow"],"t":0}'; done
python3 steps.py; python3 films.py turn; python3 films.py walk
```
`look_head.py orig|faired|warped` — clay pictures of the head's steps with the drawing's outlines.
`shots.mjs jobs.json outdir` drives `web/tim.html` (served from /home/user, three.js from the n3-cloth cache).
`motions.py` converts a studio motion (`motion(key, data: "body")`) into the engine's format in the cache — two were
ordered for the stills (a still stand; hands behind the back as in figure-tim), but the studio's GPU did not wake
within the work; the stills use frame 0 of the engine's `bow` (standing upright before the bow).

## Licences of the bases

| What | Licence |
|---|---|
| Anny body (moood-child, in the engine) | Anny (NAVER, Apache-2.0), MakeHuman (CC0), SOMA rig (NVIDIA, Apache-2.0) |
| Human Base Meshes bundle v1.4.1, `GEO-head_stylized` | CC0 (Blender Foundation) |
| Kimodo motions (walk, bow) | made in the moood studio |
| The drawing and its code | ours (styles/s9-midcentury) |

## What is not done / honest

- Clothes are shells skinned with the body, not cloth: they don't crumple or swing. Hair is rigid.
- Expressions are swapped pictures; there is no in-between and no jaw.
- The hands are Anny's fingers thinned and shortened, not the drawing's mittens.
- The neck: the base's neck under the jaw is still a little conical in profile; the drawing's head sits on a thinner
  stalk.
- No slingshot (figure-tim's detail) and no pose with hands behind the back (the motion did not arrive).

## Alive (second round, asked by Pavel through the orchestrator)

- **The face** (`tools/web/face.js`): kit.py's path/sample/brush and face.py's eye/brow/mouth ported to JavaScript line
  for line; the face is drawn every frame into a canvas the head takes (a CanvasTexture, the same front projection).
  The timeline is made once from a seeded random stream (a moment always looks the same — films, scrubbing):
  blinks at gamma-like intervals (mostly 2–5 s, 12 % doubles), lid closing ~70 ms, held ~30 ms, opening ~140 ms;
  saccades: fixations 0.3–2.2 s, jumps of ~40 ms with 10 % overshoot settling in ~60 ms; gaze lead: the head's world yaw
  is read off the clip, the eyes jump towards yaw(t + 0.28 s) − yaw(t), and a turn faster than 1.6 rad/s calls a blink
  (not more than one per 0.9 s); speech: syllables of a consonant shape (60–110 ms) and a vowel shape (100–220 ms),
  phrases of 3–9 syllables with 0.3–1 s pauses, each shape eased into the next over ≤70 ms; expressions blend over
  0.35 s (numbers interpolated, a mark of another kind cross-faded). The blush, freckles and hair strokes are a cached
  layer (a blur is dear to draw each frame).
- **Hands**: the finger joints get a short and thick map (along 0.36, across 0.95), the thumb 0.45/0.9: with the
  thinned palm they read as a small mitten-like fist; Kimodo still moves the fingers.
- **Profile compromise tried and dropped**: the face's sides drawn back (the midline and the front outline kept) so the
  profile's eye sits deeper — the eye hid behind the cheek in profile and a crease came in three-quarter.
- **Films** (`films.py walk sit wave jump look face turn`): perspective camera following him, a painted ground (one
  paint, faint blotches fixed to the ground, a soft spot under him) so the travel shows; the face film is a close look
  while he stands (Kimodo's bow, frame 0).
- **Viewer** (`tools/web/tim.html` + `ui.js`): the model in `model/tim.json` (written by build.py); paths relative, so
  it runs from the repository's root; `?shots=1` turns the controls off for `shots.mjs`. `viewer_check.mjs` opens it
  as the site serves it and takes a picture.
