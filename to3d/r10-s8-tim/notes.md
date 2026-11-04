# Р10 — Тим, кукольная анимация (С8): from the drawing to 3D

What was done, why, and how to repeat it. Brief: `/home/user/cache/BRIEF-to3d.md` (build the 3D from good ready bases
fitted to our drawing, not by a neural net; second round: the live face, Kimodo motions, a browser viewer). The
drawing: `styles/s8-stopmotion` (figure-tim, turn-tim, portrait-tim, expr-tim; its code `tools/cast.py`, `head.py`,
`hair.py`, `body.py`, `figure.py`).

## The idea

The С8 drawing is already drawn from 3D: the head is a loft of elliptic slices (`head.Head`, `cast.TIM['shape']`),
the features are laid on it by (phi, y), the hair locks are 3D paths over the head's shell, the body and limbs are
lofts and tubes with numbers in `cast.TIM_BODY` / `TIM_FIG`. So the drawing's own numbers are the target in every
view at once (no front/profile guessing), the bases are fitted to them, and the cameras of the comparison pictures
are the drawing's views (yaw, px per head unit, the head's place — `build.py` of the style).

Stop motion is natively 3D, so the look is not a shader imitation but a real render: Blender Cycles (CPU), a small
set: one warm key from the upper left, a cool rim behind on the right, a dim fill, a dark backdrop with a warm pool of
light, small lamps far behind going out of focus through a real lens (bokeh), a floor with his shadow. Materials as a
puppet's: resin skin with light under it (subsurface, a faint unevenness), glass eyes (a clear coat over a painted
iris), sculpted hair (grooves and strand lines in the bump), knitting (ribs and stitches in the bump, stripes knitted
in, fuzz by sheen), felt shorts, ribbed socks, red shoes with a pale sole. Films are shot on twos (12 frames a second),
as stop motion is.

Faces are replacement pieces, as on Laika's puppets: the head is one cast; the mouth (lips, the dark of the mouth,
teeth) and the brows are separate pieces with a library of shapes — one per expression of the sheet and one per mouth
shape of speech — and a face is a mix of them; the lids are the head's own lid skin turning over the glass eyes.

## Steps and what each base gave (tools/, in order)

1. `hbm_export.py` (Blender, on `human_base_meshes_bundle.blend`): `GEO-head_stylized` (cage, once subdivided) and its
   eyes → `CACHE/hbm.npz`. `base.py` puts it in head units on the engine's axes.
2. `fit_head.py` → `CACHE/head_raw.npz`. Gave: the skull, the ears, the nose, clean loops round the eyes.
   - the eye-socket linings cut (faces inside the base's eyeballs): the lid margins become two clean loops; the
     mouth's bag and the neck cut too, the lips' seam and the neck closed by rings of quads + biharmonic fairing (a
     puppet's head sits on a neck of its own; the mouth is a replacement piece);
   - two levels: a smooth version of the base (implicit fairing, lid margins held) and the detail (base − smooth) in
     each vertex's frame (normal, up the surface, across);
   - the smooth form onto the drawing's loft: thin-plate RBF (lid margins → the drawing's lid openings, mouth corners →
     the drawing's, 900 points → their nearest loft points, 4 rounds), then every vertex onto the loft;
   - the detail back, scaled per region: nose 0.7, upper face 0.3 fading to 0 below the nose (the drawing's lower face
     is a smooth mask), lips 0, ears 1;
   - under the jaw and the closed mouth: tangential relaxation (neighbours' mean, back onto the loft);
   - ears carried whole onto the drawing's (lower, ×0.8 of the base's height ×1.3, turned to stand out 42° + 12°);
   - eyes: glass balls of the drawing's size (eye_r × 1.05, as the drawing draws them) at the drawing's places; the lid
     margins put onto the drawing's opening laid on a sphere 3 % bigger than the ball (projected along the surface
     normal at the eye), the opening a little rounder and larger than drawn (a leaning lid over a ball reads as a frown;
     a ball shows less than a flat painted eye); the lid skin kept outside the ball; a short lip from each margin in
     toward the ball's centre.
   Tried and dropped: one RBF warp of the whole base (features pinched: the nose became a ridge); a Laplacian
   projection of all non-features (the lips and the jaw folded); the soft union of loft and neck as one target (frills
   at the throat) — replaced by the separate neck.
3. `fit_hair.py` → `CACHE/hair.npz`: `cast.tim_hair` itself (the drawing's 19 locks as 3D paths and widths, the
   hairline line(phi)) — each lock a flattened tube (wide across the head, thin off it), narrow at the root, a point at
   the tip, grooves along its top; the cap a shell over the fitted head (2 cm above it) from the crown down to the
   hairline exactly, with an inner wall; the fringe's falling ends held 0.07 head higher than drawn (in 3D the clumps
   stand off the forehead and hid the brows).
4. `fit_body.py`: Anny's child (`engine/data/bodies/moood-child`) — per-joint affine maps (along the bone / across),
   joints rebuilt down the chain, vertices by their skin weights (after Р3), legs brought together (the drawing's
   stance); frames kept. Targets from `TIM_FIG` (1 head unit = 0.342 m; he is 1.15 m, 3.36 heads): hips 0.41, knees
   0.23, ankles 0.05, shoulders 0.72 (±0.14), neck base 0.74, the head's pivot 0.84.
5. `face.py` → `CACHE/face.npz/json`: the replacement pieces from the drawing's own `head.mouth()` and `head.brow()`
   curves — for every expression of `cast.EXPR` (calm, dream, joy, surprise, sad, anger, grin) and seven speech shapes
   (A, O, U, E, I, M, F in the drawing's mouth numbers) — fixed topology, each point laid on the head (nearest surface
   point, raised along its normal: lips as two rolls, the inside dark, teeth a band, brows a raised strip, a little
   higher than drawn); the lids' weights (falling off over 8 rings from the margin, less toward the corners, turning
   about an axis through the ball's centre along the opening's chord); the lash line (a dark strip on the upper margin
   with a wing); the lids' turn per expression from the sheet's open / lid_up / lid_lo (× 0.6).
6. `paint.py` → `tools/web/tex/face.png` (front-projected skin: the drawing's blush, its seeded freckles, the socket
   tone, a warm nose tip), `iris.png`.
7. `build.py` → `CACHE/engine/data/{bodies,topology}/tim8.*` (one engine body on its own topology, every piece on
   SOMA's 77 joints), `CACHE/engine/face.*` (the face rig), `CACHE/model.json`, `CACHE/rest.npz`, and the viewer's copy
   in `data/`. Clothes from the drawing's numbers: the sweater = Anny's trunk and arms carried out radially to the
   drawing's barrel (`TIM_FIG['torso']`) and round the arm bones to the sleeve's radius, the shoulders lifted (the
   barrel closes up to the neck), keeping Anny's weights; ribbed bands at the neckline, hem and cuffs; the shorts =
   hips and thighs carried round the thigh bones to the drawing's wide legs; socks on the shins; shoes lofted round the
   feet (the drawing's half-ellipsoid shoe); the thin neck from `TIM_BODY['neck']` (Neck1 → Neck2 → Head by height).
8. `move.mjs` — the engine as it is (`createEngine`, `figure`, `clip`; retargeting, skinning by centres of rotation,
   the floor), its reading pointed at `tim8`; the face (`web/face.mjs`) applied after skinning, turned with the Head
   joint (rigid, so exact); `web/life.mjs` gives the face's timeline; for stills: a head turn on top and `level`
   (the pose's head pitch and yaw taken out).
9. `render.py` (Blender 4.5, Cycles CPU, OIDN): the set, the materials, the lights turning with the camera (a
   turntable), the set behind placed per view; cameras: `view` (the drawing's view: a 300 mm lens from far, nearly
   orthographic, S px per head unit, the head's centre on the drawing's pixel) and `persp`.
10. `stills.py turn|portrait|figure|expr` → the drawing / 3D / overlay sheets; `films.py turn|walk|face|wave` →
    `pics/*.mp4`; `steps.py` → `pics/steps-*.webp`; `viewshot.mjs` pictures of the viewer.

## How to repeat

```
cd to3d/r10-s8-tim/tools
B=/home/user/cache/blender/blender; PY=/home/user/cache/n1-deform/venv/bin/python     # numpy, scipy, libigl
$B -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
   --python hbm_export.py -- /home/user/cache/to3d-r10-s8-tim/hbm.npz
python3 paint.py
$PY fit_head.py; $PY fit_hair.py; $PY face.py; $PY build.py          # ~3 min
for s in turn portrait figure expr; do python3 stills.py $s 24; done  # 2–10 min each on 4 shared cores
for f in turn walk face wave; do python3 films.py $f 14; done         # ~1 min a frame
$PY steps.py
NODE_PATH=/opt/node-tools/node_modules node viewshot.mjs OUT '[{"name":"a","set":{"motion":"walk","t":1}}]'
```
The viewer: serve the repository's root (`python3 -m http.server`) and open `to3d/r10-s8-tim/tools/web/view.html`.

## Second round: alive

- **The face** (`tools/web/face.mjs`, `life.mjs`): replacement pieces mixed (the expression's shape, or while speaking
  the speech shapes), lids turning over the glass eyes, the eyes turning in their sockets. Timing (after Р2–Р4, from
  how faces move, seeded so a moment always looks the same): blinks at log-normal intervals (median 2.8 s, ≥ 0.8 s),
  12 % doubled, closing 75 ms, held 25 ms, opening 160 ms, and with big gaze shifts; the eyes hold and jump (fixations
  0.3–1.6 s, a jump 20 ms + 2.2 ms per degree), leading the head (its facing read 0.25 s ahead in the clip) and
  turning back in the head as it follows; speech: phrases of 3–8 syllables, a consonant shape (60–110 ms) then a vowel
  shape (100–200 ms), pauses 0.3–1 s, weights following a fast critically damped spring (ω 34) so shapes run into each
  other, the brows lifting at a phrase's start; expressions following a slower spring (ω 8.5).
- **Motions** (engine/motions only): walk, wave, idle (the face close-up), bow frame 0 levelled (the turntable and the
  stills), wave frame 38 (figure-tim: he waves with his right hand — Kimodo's wave; the drawing waves with the left).
- **Viewer** `tools/web/view.html` + `view.mjs`: the engine in the browser (dual-quaternion skinning there: centres of
  rotation take long to prepare 50 000 vertices), three.js physical materials after the render's (the knit's stripes
  and ribs drawn in the shader from the same paint coordinates), a key with soft shadows, a rim, the set painted
  behind; drag to turn, wheel nearer, motion, expression (follows by a spring), talk on/off, play/pause, scrub, a face
  close-up. `?shots=1` hides the controls (`window.A.set` for scripted pictures).

## Licences of the bases

| What | Licence |
|---|---|
| Human Base Meshes bundle v1.4.1, `GEO-head_stylized` and its eyes | CC0 (Blender Foundation) |
| Anny child body (moood-child, in the engine), SOMA skeleton and weights | Anny (NAVER, Apache-2.0), MakeHuman (CC0), SOMA rig (NVIDIA, Apache-2.0) — `engine/data/soma/NOTICE` |
| Kimodo motions (walk, wave, idle, bow) | `engine/motions` (moood studio) |
| The drawing and its code | ours (`styles/s8-stopmotion`) |
| three.js 0.160 (viewer) | MIT |

No neural images; StdGEN not used.

## What is weak (honestly)

- Clothes are shells skinned with the body, not cloth: the sweater doesn't crumple or swing; hair is rigid on the head.
- Hands are Anny's (shortened, thickened) — not the drawing's sculpted mittens.
- The face is close to the drawing but not equal: the eyes are glass balls under lids of skin, so they read rounder
  and deeper than the painted ones; the opening was made a little larger and rounder than drawn on purpose; the brows
  sit a little higher; the lower face is smoother than the base (the drawing's mask) and the base's cheek folds
  beside the nose still show a little.
- The mouth is a piece laid on the face (as a replacement mouth is), not a cavity: an open mouth reads by its dark and
  the lips' rolls, not by depth; seen from the side it stands slightly proud.
- The figure still waves with the other hand than the drawing (Kimodo's wave), and the pose leans; the drawing's
  ears are bigger.
- Films are 12 fps on purpose (stop motion on twos); the CPU renders are slow (~1 min a frame on the shared machine).
- The viewer's materials are an approximation of the renders (no subsurface, no real bokeh); there the glass eyes
  read whiter and flatter than in the renders.
- In Kimodo's wave his short arm and big head make the hand wave by the hair, the head tilts toward it.
