# The engine

The foundation characters stand on: one description of a body, one skinning, one format of Kimodo's motions and one
way to carry them onto a body, a versioned description of a character, and a check that the characters stay as they
were. Clothes, hair, deformers, heads and the player all take these. Built beside the experiments (`../experiments`,
`../gallery` stay as they are). Served from the repository's root (`python3 -m http.server`), three.js 0.160.0 from
jsDelivr; the code is plain ES modules that run in a browser and in node (`src/` has no three.js except `view3d.js`).

The viewer: `viewer/index.html` (in the gallery: Д1). Choose the body; play a motion or a chain; pause, scrub; the
camera follows, the floor has a metre grid and the pelvis's path; front and side views from where the figure faces;
skinning methods, Т7's fixes and the corrections as toggles; the joints shown.

## Layout

```
src/       engine.js      the entry: createEngine({root?}) → body(id), motion(id), clip([ids]), character(id), figure(c, place)
           skeleton.js    SOMA's 77 joints (data/skeleton.json)
           body.js        the body description, its measures
           motion.js      Kimodo motions; clips (one motion or a chain) — sample(t)
           retarget.js    a clip's moment on a body: the turns, the bones, the travel, placement
           corrections.js named corrections on top of Kimodo (off unless asked for)
           skin.js        skinning (centres of rotation / dual quaternions / linear), Т7's fixes, normals, attachments
           character.js   the character description, its versions and their defaults
           figure.js      the pipeline: retarget → corrections → collarbone share → place → skin → floor → normals
           view3d.js      three.js stage and mesh (the viewer's and the check's)
           pack.js, math.js
data/      skeleton.json, soma/ (Kimodo's SOMA skin, Apache-2.0: NOTICE), topology/anny-moood.*, bodies/*.json + .bin
motions/   <id>.json, index.json (motions and chains)
characters/<id>.json, index.json
viewer/    the viewer
check/     check.mjs (the picture check), shots.json (its moments), pictures/ (the stored ones), shots.mjs (pictures of
           the viewer for a list of jobs), serve.mjs, browser.mjs, node-read.mjs
tools/     Python that makes data/ and motions/: soma.py, bodies_moood.py, bodies_anny.py, motions.py, pack.py
```

## Formats

**Pack** (`src/pack.js`, `tools/pack.py`): `<name>.json` — a header with `format`, `version`, its fields and
`arrays: {key: {dtype, shape, offset}}`, `bin: "<name>.bin"`; `<name>.bin` — the arrays, little-endian, one after
another. Bodies and topologies are packs.

**Skeleton** `data/skeleton.json` (`engine/skeleton` 1): `joints: [{name, parent, side, part, rest, frame}]` — SOMA's T-pose
(the rest Kimodo's rotations are measured against), `floor` — its skin's lowest point at rest. Axes everywhere: metres,
y up, the body facing +z, its left +x.

**Topology** `data/topology/<id>` (`engine/topology` 1): `triangles` (T×3), `skinJoints` (N×4), `skinWeights` (N×4,
summing to 1), `parts` (N×P, /255; names in the header: pelvis, spine, neck, head, L/R clavicle, upperArm, foreArm,
hand, thigh, shin, foot), `face` (the face's vertices).

**Body** `data/bodies/<id>` (`engine/body` 1): `topology`, `skeleton`, `label`, `source`; `positions` (N×3), `joints` (77×3:
each joint's place at rest), `frames` (77×4: each joint's frame at rest), optional `facePlain`, `eyes`. In memory
(`src/body.js`) also `skin`, `parts`, `measures` (floor, height, hipHeight, legLength, armLength, shoulderWidth,
headHeight, headCenter). *Places are the designed rest; frames are the retargeting reference*: a deformer moves
vertices and joints (`body.withRest(positions, joints)`) and never the frames.

**Motion** `motions/<id>.json` (`engine/motion` 1): `kimodo` (the studio key, prompts, seconds; `after: {motion,
frames}` and `startsAt: {x, z}` for one made to go on from another), `fps`, `frames`, `data: {names, q, p}` — the
studio's own data unchanged (every joint's world rotation, int16/32767, x y z w; its place, int16 mm), `derived.lowest`
(SOMA's posed skin's lowest point each frame). `motions/index.json`: the motions, and the chains (`motions: [ids]`).

**Character** `characters/<id>.json` (`engine/character` 1): `body` (a body id), `skinning: {method, clavicleShare,
seam}`, `motion: {floor, corrections}`, `look: {skin, roughness}`. Defaults live per version in `src/character.js`
(`DEFAULTS[1]`): a later engine adds a version instead of changing what version 1 means.

## How it works, and why so

**Bodies.** moood's baked Anny bodies (`experiments/data`: the bytes of moood's `engines/1/bodies`) are read as they
are: their joints and frames are the inverse binds moood baked from Anny's SOMA rig. Т8's bodies (Anny's own settings
carried onto moood's mesh, `experiments/anny-space/out`) had no joints; `tools/bodies_anny.py` gives them Anny's own:
Anny's SOMA rig places each joint as a fixed linear combination of its SOMA-topology vertices (`sparse_rbf_matrix`);
that regression is carried onto moood's mesh once (Anny's SOMA surface of the fitted woman laid on moood's woman:
6 mm mean apart), and each body's joints are moood woman's moved as the regression of how its surface moved from hers.
So joints follow each body's own final surface (the head of another age, the smoothing included). Frames turn with
their bones (one-child joints by the smallest turn of the bone; others by the best rotation of the skin they carry).
`--check` compares with Anny's own exact joints on bodies of Anny's settings alone: 16–35 mm mean apart (about what
Anny's two topologies differ by for such shapes), against 35–60 mm for the old guess from skin displacement
(`view.html`); far-extrapolated bodies (the elf, 2.3 m) differ more.

**Retargeting** (`src/retarget.js`). The bodies' joint frames are SOMA's frames (Anny's SOMA rig): checked, a joint's
child lies in the same direction of its frame within a few degrees on moood's woman and on SOMA. So each frame is
carried as Kimodo turned SOMA's (`Q = q · frameᵀ`), and the bones keep the body's own lengths and rest offsets. Nothing
measures bone directions at rest, so a design in the rest (Т5's line of action, limbs in arcs) rides along in motion —
the separation asked for: the designed rest (places) is not the retargeting reference (frames). The pelvis follows
Kimodo's own path, scaled by hip height against SOMA's — the body travels, never walks on the spot; `place: {position,
heading}` puts the whole motion anywhere. `motion.floor: "lowest"` then lifts or lowers the whole body so its lowest
point is as high as SOMA's skin's lowest at that moment (scaled): on its feet, lying, rolling, nothing in the floor.

**Chains** (`clipOf`). A motion made with `make_motion(after: {key, frames})` begins with the other's last frames; the
chain plays the first whole, then the next from its `frames`-th frame, its origin at `startsAt` in the first's space
(the studio says it), the heading kept. A chain of motions not made so is refused: Kimodo has to make the join.

**Skinning** (`src/skin.js`). Centres of rotation (Le & Hodgins 2016) by default: per vertex the joints' turns blended
as quaternions (no candy-wrapper collapse at a twisting forearm, which linear blending has) about a centre found from
the rest mesh, placed linearly (no bulge at a bent elbow or knee, which dual quaternions have); weights stay Anny's.
Dual quaternions and linear blending stay as options to compare. Т7's two fixes are options: `clavicleShare` (the
collarbone takes a share — Т7: a third — of the arm's drop below rest; a raised arm is left to Kimodo's collarbone) and
`seam` (where trunk and collarbone/arm weights meet, the skin's movement against the chest is smoothed over the
surface). Rigid things on a joint use `skinner.matrix(pose, j)` times their own rest matrix, so their own transforms
are kept (the gallery's shared Skinner dropped them).

**Corrections** (`src/corrections.js`): `armsOff`, `armsOutOfHead`, `amplifyLimbs`, `dampHeadSpine` — named, off unless
a character asks; they change turns, never the travel.

## Adding things

- *A body*: write a pack with `format: engine/body` on an existing topology (`tools/bodies_moood.py: body_file`), or a
  new topology beside it; joints from Anny's regression if it is Anny's mesh (`tools/bodies_anny.py: Regression`).
- *A deformer* (stage 1): a function body → body (`body.withRest(positions, joints)`), moving joints with the surface,
  never the frames. Then `new Skinner(newBody, …)` (its centres of rotation follow the new rest).
- *A motion*: order it in the moood studio (`make_motion`; `after` to go on from another), keep its body data
  (`motion(key, data: "body")`) in `experiments/motions-raw/` (or anywhere), add a line to `tools/motions.py` and run it.
  A chain: a line in `CHAINS`.
- *A correction*: a function in `CORRECTIONS` (pose, body, params), off by default; give it a toggle in the viewer.
- *A skinning method or a change of a default*: a new method name, or `DEFAULTS[2]` in `src/character.js` with the
  change — never a change to `DEFAULTS[1]`.
- *A character*: `characters/<id>.json`, listed in `characters/index.json`; then `node engine/check/check.mjs --update
  --only <id>` after looking at its pictures.
- **Before and after changing the engine**: `node engine/check/check.mjs`. A difference is either a bug or a change
  meant — then look at the new pictures, and store them with `--update`.

## Not done yet

Hands and fingers are carried (all 77 joints) but not checked closely; feet are set on the floor only as a whole
(no foot contacts); the arm can press into the chest's side at the armpit when it hangs close (Anny's weights; the
`armsOff` correction is for that); Kimodo's first frames after `after` can flick a foot fast (seen at the
lie → rollover join, frames 180–182: Kimodo's own); computing the centres of rotation takes about 0.3 s a body.
