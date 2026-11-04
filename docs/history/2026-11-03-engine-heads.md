# 2026-11-03 — the engine, stage 2: heads

**What called for it.** The plan's stage 2 (heads), as Pavel and I agreed it ([directions.md](../directions.md), "The
engine view", heads): the base is always Anny's head mesh (alive, no seam, moves with the skeleton); its form by a set
of ways that combine with a strength — Anny's own face settings and a head of another age; deformers on top (face by
points, a cage on the head, smooth warps); a designed form the mesh is wrapped onto (as Г3), made from a drawing's
curves (as Г1) or as a solid fitted to a picture (as Г2); separate pieces where the mesh won't stretch (a long nose, a
ball nose). Features as a separate layer, per feature, painted on the skin or as volume, mixable. Expressions by the
mesh with painted features following. Face light as an option (toon with outline, shading from the designed form, no
cast shadows on the face). For authors: an overlay check against the picture; our heads as preset examples. Dropped:
Г2's sculpting by balls, Г4's rays, a standalone head without Anny. Not now: blending expressions, mouth shapes, a
gaze that follows. The lead agent's task added: presets as code (head forms, features, expressions, light — browsed,
compared, taken as a part and changed), heads in motion (Kimodo, every skinning method, the bodies' deformers), hooks
for hair and clothes (the head's shape to collide with, pieces as meshes on the rig), quality contracts with limits,
cases, gallery entries, docs, pictures; the existing checks to pass; our heads no worse than in their experiments.

**What was done** (all in [engine/](../../engine/README.md); its README has the architecture, formats and how to add):
- *Head units and omega* (`src/head/frame.js`): Г1's units (the cranium's radius 1 above the Head joint) for everything
  of heads; how much of each vertex a change of the head moves.
- *The form, as deformers* (`src/head/face.js`, `wrap.js`, `forms.js`, `shapes.js`), so each goes on the rest or as a
  pose layer with every body deformer: `face` (Anny's 129 face changes, baked onto moood's mesh by
  `tools/face_targets.py` into `data/anny/face.json` at +1 and −1 — they are not linear: a change's two signs differ
  by up to 19 mm), `headOf` (a head of another age, its joints along), `points` (24 landmarks found on the stored body
  the head came from — `body.origin` was added so after a wrap they are the same skin points — one biharmonic warp),
  `cage` (a Bézier lattice), `warps` (pushes, scales by height), `wrap` (Г3's algorithm carried as it is onto two kinds
  of designed forms: Г1's curves and Г2's solids). The wrap measures its folds against the form (`ownFolds`: the
  bodies' unfold, which measures against Anny's own normals, would undo designed changes).
- *The head on its rest* (`src/head/head.js`): the face's picture (front projection), the expressions' morphs, the
  designed form's shading normals, the face's no-shadow mask, pieces (`pieces.js`: the long and ball noses as Г3 made
  them; Г1's hair and headwear as rigid pieces, carried only so the presets look as they were), features as volume
  (`features.js`: a relief of the feature's outline laid on the skin's triangles — a new mesh kind `attached` in
  `src/mesh.js`, laid each frame on its host in `src/figure.js`), the head's shape to collide with
  (`figure.headShape()`).
- *Features* (`paint.js`): Г3's drawing (Г1's with the smile's lifted lower lid) on any 2D canvas, with what the
  expressions ask (a closing eye graded by its weight, happy eyes, a smiling mouth, an open mouth's inside, brows up
  and down). *Expressions* (`expressions.js`): morphs of the skin (Г3's lids, corners and cheeks; brows) and the Jaw joint
  turned (`{kind: "expression"}`, a new pose layer). *Light* (`src/view3d.js`): toon (Г3's soft three-tone ramp, not
  tone-mapped), outline (a shell's back moved out along the normal in the vertex shader), the designed form's normals
  turned each frame by the skin's joints (`src/figure.js`), no cast shadows on the face (three.js's directional shadow
  term mixed out by a vertex attribute).
- *Formats*: character 4 (`head`; `upgrade` 3 → 4 changes only the version), preset 3 (one of changes, head,
  features, expressions, light; 2 → 3 only the version). All 20 characters and 64 presets were upgraded and pinned
  anew by `tools/characters.mjs`; their numbers did not move.
- *Presets* (`tools/heads.mjs` reads the experiments' own data — Г3's page for its nine, Г1's page for Alva and Jesper,
  Г2's `chars.py` for Giulia's solid): 11 head presets with characters `head-*`; the drawn face's expressions; four
  lights; eleven ways of the form (one of them Г2's Giulia, a solid fitted to her picture); two sets of features; five characters combining them, one of them (`head-red-mine`)
  a preset head taken as a part and changed. `tools/characters.mjs` pins heads, bodies inside changes and the cases.
- *The overlay check* (`tools/overlay.mjs`, `overlay.html`): Г2's `fit.py` on the engine's heads — the head at its
  picture's angle (or fitted), landmarks by a similarity, error in pixels, the picture with the outline. Red's picture
  points were marked by eye for it (5.9 px rms at the picture's angle, 4.5 px at the fitted one).
- *The viewer* (`?heads`), *the gallery* (Д5 form, Д6 features, expressions and light, Д7 ready heads, each with its 3D),
  *checks* (cases, contracts — below), *pictures* ([pictures/engine/heads](../pictures/engine/heads/)).

**Decided on the way, and why.**
- Г1's heads are no longer standalone (dropped by the agreement): all seven are wrapped with Anny's mesh as Г3 wrapped
  its four. Their jaw and neck are now Anny's — the main difference against Г1's own pictures.
- The wrap's fold easing runs until no pleat is left (up to 200 rounds, Г3 stopped at 40): Г3 left 40–170 triangles
  turned under the eyes and along long noses (hidden three deep). A long nose with a ball (Jesper): the skin now goes
  over the nose pressed back and without the ball, and the piece is the rest — Г3's page lost the flattening there.
- Г2's solids come over with Г3's wrap and Г2's own placement (cranium on Anny's, her neck measured); `onto` lets the
  wrap lay the skin on the form nearly all the way down the neck as Г2 did. Wrapped so they keep a crease at the throat
  and read rougher than Г2's own build (which cut lids and set eyeballs in Python), so Giulia and Gwen were tried as
  ready heads, looked at, and taken out: only Giulia's solid stays, as a way of the form.
- No clothes and no Г1 turtleneck (garments are stage 4); hair stays Г1's, rigid on the head (stage 3).
- Painted features take their place at the rest, so they follow the skin; the face's picture is front-projected
  everywhere and mixed out in the shader by a mask (1 on the face's front, 0 round the sides, behind, down the neck).
  First the off-face skin took the picture's edge rows (as Г3): the triangles where they switched smeared eye lines
  across the back of a bald head; then its side columns: the back's midline smeared; the mask has no such seam.
- The quality contracts measure what can go wrong with heads; their limits were set from what the heads measure and
  where it shows: in motion ×1.3 of the plain body (the old man's jowls stretch more than a plain neck when he looks
  round), in expressions 2.5× with the lips that open left out (Anny's mouth is closed skin), at rest 12× for wraps and
  9× for Anny's own changes (her small nose and big eyes stretch her nostrils' and closed eye's own tiny edges).

**How, to repeat it.** `python3 engine/tools/face_targets.py` (Anny, torch) → `data/anny/face.json`. `node
engine/tools/heads.mjs` → presets and characters from the experiments; `node engine/tools/characters.mjs presets`,
`pin <ids>`, `cases`. Looked at: every head front, three-quarter and side beside its experiment (Г3's and Г1's pages
shot at the same angles), close-ups of the neck join, expressions, motions (look around, walk, run, dance, jump, sit,
bow), each skinning method, a body deformer on the rest and as a layer, the four lights, features painted and as
volume. Pictures: `node engine/tools/sheets.mjs engine/tools/sheets/heads.json`; the overlay `node engine/tools/overlay.mjs
<dir> head-red head-giulia head-gwen`. Checks: `node engine/check/units.mjs`, `quality.mjs`, `numbers.mjs`,
`pictures.mjs`.

**Seen and left.** An open mouth is the skin between the lips stretched (painted dark), no teeth. Hair goes through
the shoulders in big motions (rigid Г1 hair). Toon light on a head with no designed form shows Anny's small forms as
hard tones. Г2's heads not ready (above). The old man's jowls meet his neck in a shelf at the back, under his hood (Г3's form; its
contract allows it).
