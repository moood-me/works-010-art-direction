# The engine

The foundation characters stand on: a rig and the meshes it moves, one skinning, one format of Kimodo's motions and
one way to carry them onto a rig, chains joined where Kimodo joined them, changes as a rest change or as a pose
layer, a stateful step for simulations, the body as something to collide with, characters as checked data, and
checks that see when an engine change moves a character. Clothes, hair, deformers, heads and the player take these.
Built beside the experiments (`../experiments`, `../gallery` stay as they are). Served from the repository's root
(`python3 -m http.server`); three.js 0.160.0 is kept in `vendor/three` (MIT); the code is plain ES modules that run in a
browser and in node (`src/` has no three.js except `view3d.js`, which is given it).

The viewer: `viewer/index.html` (in the gallery: Д1). Several figures side by side (＋, ✕; the panel edits the chosen
one); a motion or a chain; pause, scrub; the camera follows the box around all of them; front and side from where the
chosen one faces; skinning methods, Т7's fixes and pose layers as toggles; the joints and the collision capsules
shown. `?c=woman,man&m=walk&t=40&paused`. With `?bodies` (in the gallery: Д2–Д4) the bodies' panel: the chosen figure's
base body (any of `data/bodies/index.json`) and its deformers — presets added from `presets/index.json`, each with its
strength, on the rest (frames kept or turned) or as a pose layer, taken away; `&b=<body>&d=<preset>:<strength>[:pose],…`.

## Layout

```
src/       engine.js      the entry: createEngine({root?, read?}) → body(ref), motion(ref), clip(what), character(id),
                          description(id), figure(c, {place, layers, meshes})   (ref: id or id@hash)
           skeleton.js    SOMA's 77 joints (data/skeleton.json)
           rig.js         a rig: skeleton, joint places and frames at rest, floor, hip height — apart from any mesh
           mesh.js        meshes a rig moves: skinned, rigid, procedural (rebuilt each frame); used vertices; morphs
           body.js        a body: a rig and its skin mesh, parts, measures, its content hash
           pose.js        a pose (Q turns, P places, floor, shift) that belongs to whoever made it; build, local turns
           motion.js      Kimodo's motions; clips (one motion or a chain) — sample(t); the joins' blending
           soma.js        SOMA's skin, for the lowest point of frames the studio didn't give
           retarget.js    a clip's moment on a rig: the turns, the bones, the travel, placement
           layers.js      pose layers on every frame (the corrections, Т7's collarbone share, a joint turn, a morph)
           changes.js     the same changes on the rest, with the frames kept (design) or turned (anatomy)
           deform.js      deformers: their registry; on the rest; as pose layers (a mesh layer after skinning, or a morph)
           regions.js     what deformers read off a body: parts along bones, limb shares, landmarks by height; smoothing
           deformers/     lines.js (line, squash, contrapposto), limbs.js (taper, straight, arc), silhouette.js,
                          proportions.js (proportions, caricature), surface.js (anatomy, smooth), contour.js, masses.js,
                          sign.js, curves.js; index.js registers them
           skin.js        skinning (centres of rotation / dual quaternions / linear), Т7's seam fix
           collision.js   the body as tapered capsules per bone, moved by the pose: distance and normal
           figure.js      a rig with its meshes: pose → layers → place → meshes → floor → normals; frame and step
           character.js   the character description: schema, defaults, upgrade
           schema.js, hash.js, pack.js, math.js
           view3d.js      three.js stage (lights and shadows for any number of figures, a camera framed by a box)
data/      skeleton.json, soma/ (Kimodo's SOMA skin, Apache-2.0: NOTICE), topology/anny-moood.*, bodies/*.json + .bin,
           kimodo/ (the studio's asks, asks.json, and data of motions not kept in experiments/motions-raw)
           anny/specs.json (the new bodies' Anny settings), bodies/index.json (every body by group, pinned)
motions/   <id>.json, index.json (motions and chains)
characters/<id>.json, index.json
presets/   <id>.json, index.json — presets of parts (deformers with their parameters), by group, pinned
viewer/    the viewer
check/     numbers.mjs (the numeric check), pictures.mjs + render.html (the picture check), units.mjs (contracts),
           cases.json (their moments), numbers/ and pictures/ (the stored ones), serve.mjs, browser.mjs, node-read.mjs
tools/     Python that makes data/ and motions/: soma.py, bodies_moood.py, bodies_anny.py, bodies_new.py, motions.py,
           pack.py; characters.mjs (upgrade characters, pin bodies, presets and chains; index presets and bodies);
           sheets.mjs + sheet.py + sheets/ (labelled sheets of moments for the docs)
vendor/    three.js
```

## Formats

**Pack** (`src/pack.js`, `tools/pack.py`): `<name>.json` — a header with `format`, `version`, its fields and
`arrays: {key: {dtype, shape, offset}}`, `bin: "<name>.bin"`; `<name>.bin` — the arrays, little-endian, one after
another (float32/64, uint32, int32, uint16, int16, uint8). Bodies and topologies are packs. Its content hash: the
header's canonical JSON and the bytes (`src/hash.js`, SHA-256 written out, so it works on any page).

**Skeleton** `data/skeleton.json` (`engine/skeleton` 1): `joints: [{name, parent, side, part, rest, frame}]` — SOMA's
T-pose (the rest Kimodo's rotations are measured against), `floor` — its skin's lowest point at rest. Axes
everywhere: metres, y up, the body facing +z, its left +x.

**Topology** `data/topology/<id>` (`engine/topology` 1): `triangles` (T×3; uint32 beyond 65,536 vertices),
`skinJoints` (N×4), `skinWeights` (N×4, summing to 1), `parts` (N×P, /255; names in the header), `face` (the face's
vertices), `unused` (how many vertices no triangle uses: 1561 on Anny's — they are never skinned, drawn or counted).

**Body** `data/bodies/<id>` (`engine/body` 1): `topology`, `skeleton`, `label`, `source`; `positions` (N×3), `joints` (77×3:
each joint's place at rest), `frames` (77×4: each joint's frame at rest), optional `facePlain` (read as the morph
`plainFace`), `eyes`. In memory (`src/body.js`): `rig`, `mesh`, `parts`, `measures`, `hash`. *Places are the designed
rest; frames are the retargeting reference.*

**Motion** `motions/<id>.json` (`engine/motion` 2): `kimodo: {key, made, ask, startsAt}` — the whole ask as the studio
keeps it (prompts, seconds, heading, transition_frames, seed, steps, cfg, cfg_weight, constraints, postprocess,
root_margin, after), `after: {motion, frames} | null`, `fps`, `frames`, `data: {names, q, p}` — the studio's own data
unchanged (every joint's world rotation, int16/32767, x y z w; its place, int16 mm), `derived.lowest` (SOMA's posed
skin's lowest point each frame). `motions/index.json` (`engine/motions` 2): the motions, and the chains
(`motions: [id@hash…]`, `joins: [{blend: 'cut'} | {blend: 'dead', frames}]`).

**Preset** `presets/<id>.json` (`engine/preset` 1): `id`, `label {ru, en}`, `group`, `about {ru, en}`, `changes` —
deformers with their parameters and strengths (or other presets). A character takes one by `{kind: "preset", id:
"<id>@<hash>", strength, frames}` in its rest or `{…, space?}` in its pose; each change's strength is multiplied by the
reference's. `presets/index.json` lists them by group (silhouette, line, squash, contrapposto, limbs, proportions,
caricature, surface, contour, masses, pictogram) with their pins.

**Bodies' index** `data/bodies/index.json`: every body with its pin, group (moood, t8, t8-head, age, build, origin),
label and height. **Anny's settings** `data/anny/specs.json`: per new body its phenotype (`ph`), local changes (`lc`)
and an optional head of another age (`head: {ph, lc, r}`).

**Character** `characters/<id>.json` (`engine/character` 2), checked against a schema (unknown keys and values refused):
`body: "<id>@<hash>"`, `rest: [changes]`, `pose: [layers]`, `skinning: {method, sigma, seam}`, `motion: {floor}`,
`look: {skin, roughness}` — the whole list in `src/character.js`; the defaults are kept there (`DEFAULTS`). Rest
changes and pose layers include every deformer and presets (stage 1 added them to version 2: what a description of
version 2 already said means the same).

## How it works, and why so

**Rig and meshes.** A rig (`src/rig.js`) is what a motion is carried onto: the skeleton, each joint's rest place and
frame, the floor at rest and the hip height — no mesh. A body is a rig and its skin; a character not from Anny brings
its own rig (its bone lengths, its floor). A figure (`src/figure.js`) is one rig with any number of meshes off its one
pose: the body, and what `addMesh` adds — skinned meshes (a wrapped head, clothes on the body), rigid ones on a joint
(an eye, a piece of a head; their own transform kept), procedural ones rebuilt from the pose each frame (sweeps).

**Bodies.** moood's baked Anny bodies (`experiments/data`: the bytes of moood's `engines/1/bodies`) are read as they
are: their joints and frames are the inverse binds moood baked from Anny's SOMA rig. Т8's bodies (Anny's own settings
carried onto moood's mesh, `experiments/anny-space/out`) had no joints; `tools/bodies_anny.py` gives them Anny's own:
Anny's SOMA rig places each joint as a fixed linear combination of its SOMA-topology vertices (`sparse_rbf_matrix`);
that regression is carried onto moood's mesh once (Anny's SOMA surface of the fitted woman laid on moood's woman:
6 mm mean apart), and each body's joints are moood woman's moved as the regression of how its surface moved from hers.
Frames turn with their bones (one-child joints by the smallest turn of the bone; others by the best rotation of the
skin they carry) — the same as `turnFrames` in `src/changes.js`. `--check` compares with Anny's own exact joints on
bodies of Anny's settings alone: 16–35 mm mean apart (about what Anny's two topologies differ by for such shapes).

**Retargeting** (`src/retarget.js`). The joint frames are SOMA's frames (Anny's SOMA rig): a joint's child lies in the
same direction of its frame within a few degrees on moood's woman and on SOMA. So each frame is carried as Kimodo
turned SOMA's (`Q = q · frameᵀ`), and the bones keep the rig's own lengths and rest offsets. Nothing measures bone
directions at rest, so a design in the rest rides along in motion. The pelvis follows Kimodo's own path, scaled by hip
height against SOMA's — the body travels, never walks on the spot; `place: {position, heading}` puts the whole motion
anywhere.

**The frame** (`src/figure.js`), in this order: the pose (retargeted, or the rig at rest as it stands) → pose layers in
their order → placed → every mesh off that pose (skinned meshes with this frame's morphs weighed in first) → **the
floor**: with `motion.floor: "lowest"`, the lowest point of every mesh that counts for the floor (`mesh.floor`), over
the vertices its triangles use, is set as high as SOMA's skin's lowest at that moment (scaled) — on the feet, lying,
rolling, nothing in the floor; the one shift moves every mesh and the pose (`pose.shift`) → normals. `frame(clip, t,
pose)` keeps nothing and writes into the pose it is given; `step(clip, t)` is the stateful frame for simulations: it
keeps the current and previous pose (`figure.pose`, `figure.previous`, valid until the next step), the time step, and
a reset on the first step, a new clip, a jump back (loop, scrub) or ahead of more than `maxGap` frames; then each
simulation (`addSimulation({step(ctx)})`) runs with `{pose, previous, dt, reset, t, collider}`, after the floor.

**Changes: a rest change or a pose layer, each explicitly.** The same change can go either way: in `rest` it is made
once to the body (`src/changes.js`: `turnAtRest`, `morphAtRest`, `withRest` for any deformer), and says what the
frames do — `frames: "keep"` (design: the frames stay, the change rides along in every motion) or `"turn"` (anatomy:
the frames turn with the bones, a motion moves the body as Kimodo moved SOMA; the change shows at rest); in `pose` it
rides on every frame (`src/layers.js`). A character's code adds its own pose layers (`{kind: 'code', apply(pose,
ctx)}`) and meshes when it makes its figure. Morphs (`mesh.morphs`: indices and deltas) are weighed in before skinning
each frame (`{kind: "morph", name, weight}` as a pose layer — a code layer can animate the weight — or baked into the
rest).

**Bodies: the base** (stage 1). Always Anny with her own settings: moood's seven, Т8's 24 and 28 new ones made by Anny
herself (`tools/bodies_new.py` from `data/anny/specs.json`: ages, builds, her origin sliders). The new ones are made as
Т8's were — Anny run (a head of another age blended in over the neck when asked), carried onto moood's mesh as a change
from moood's woman smoothed by 6 steps (this gives Т8's own bodies again within 1e-7 m), joints by Anny's regression.

**Deformers** (`src/deform.js`, `src/deformers/`). A deformer has a strength and its parameters; a character lists them
in its order. Two kinds by what they act on. *Of the figure* (line of action, squash and stretch, contrapposto, the
silhouette, taper, straight against curved, arcs) — a field over the figure's space that moves every point by where it
is and which limb it belongs to (each vertex's share of the five limbs, from the skin, smoothed over the surface), and
every joint the same way. On the rest they move the body and its joints once (then `frames` keep or turn); as a pose
layer they move the posed figure every frame after skinning, in the figure's own space — `space: "pelvis"` (rest-like
coordinates under the pelvis's turn and place now: a lying figure is bent along its length) or `"upright"` (its
heading only, the vertical kept); every mesh of the figure follows by its own limb shares, the joints' places too, then
the floor step. Sizes are shares of the body's own height measured at its rest, so a field doesn't change from frame to
frame. *Of the surface* (proportions, caricature, anatomy, smoothing, contours, masses, the sign) — computed on the
rest; as a pose layer, its rest change is a morph of the body weighed by strength (a code layer can animate it); those
that move joints (proportions, caricature) are rest changes only and are refused as layers.
- *Silhouette* — Т5's body-as-one-shape and Т6's cage were the same thing (width, depth and forward by height): one
  deformer, keys at landmarks (`regions.js`: floor, ankle, knee, crotch, hips, waist, chest, armpit, shoulders, neck,
  head, top) or shares of the height, a monotone curve between them smoothed over `soft`; the arms ride with their root
  and turn out as far as the new torso needs. Т5's hard corner at the hip (its keys eased with zero slope each, close
  keys of very different widths) and its shoulder shelf (everything at shoulder height widened by the shoulders' factor
  up to the head) are gone; widening the shoulder along its slope from the neck was tried and creased the chest.
- *Contour* — a body's own sections read as Т7's `construct()` reads them (8 directions round each bone, 24 places
  along, the 70th percentile, smoothed), and Т7's drawn forms in the same terms (four contours of each limb, the
  torso's side, front and back, in the body's own units): strength blends the radii; `own` how much of the body's small
  forms ride on the new section (0: the drawn form itself); edits multiply radii by part and direction. The change is
  smoothed where parts meet; hands, feet and head stay.
- *Masses* — simple solids (ellipsoids, capsules) set at joints in body units, melted in by a smooth union along each
  point's normal (Т7's bust, buttocks, the shoulder's cap and its slope from the neck).
- *Proportions* — Т1's `placeIn`: each part laid along its bone, longer or wider, its children carried along; the
  displacement smoothed a little so where two parts meet no pinch is left. *Caricature* — against the average of
  bodies of one topology scaled to this one's height.
- *Smooth* (Т9: the cotangent Laplacian, one implicit step, the girth given back along the normal), *anatomy* (Т1).
- *Sign* (Т4) — the trunk's skin settles onto the sign's surface, each limb's skin goes round its own axis onto its
  stick (and the hand's ball, the foot's stick), blended by the limb shares: no armpit is torn between two surfaces.

**Presets** (`presets/`) are plain data: Т5's ten silhouettes and Т6's four others, six lines, squash, stretch,
contrapposto, five limbs, fifteen proportions, caricature and its reverse, anatomy both ways, smoothing 2, 4, 8 cm, Т7's
three contours and their masses and the shoulder, four pictograms. Full-body presets are characters (princess of
Disney, mother of Pixar, girl of anime, Burton-thin, pear old woman, V hero, egg baby, two pictograms): a base body and
presets with strengths, some with pose layers.

**Chains** (`clipOf`). A motion made with `make_motion(after: {key, frames})` begins with the other's last frames.
Where it stands and which way it faces in the other's space is measured from those shared frames (the same pose in
both: a turn about the vertical and a move), checked against the studio's `startsAt`; a motion whose first frames are
not the other's last, or not made after it, is refused. The chain plays the first whole, then the next from its
`frames`-th frame. Each join says how it is treated: `cut` — Kimodo's frames as they are; `dead` — dead blending
(Holden 2023): where Kimodo's own first generated frames move away fast (lie → rollover: the right foot turns 55°
in frames 180–182, vertices jump 48–82 mm a frame, in Kimodo's data itself), the last given frame is carried on at
its speed, slowing, and crossfaded into Kimodo's frames over n frames, joint by joint on the turns against their
parents and on the pelvis; SOMA's lowest point is computed again for those frames (`src/soma.js`). lie → rollover
uses 12 frames: at most 25 mm a frame, the rollover's own median speed (`../docs/pictures/engine/join.png`).
Inertialization (Bollo 2016) was tried first: it removes the step at frame 180 but not Kimodo's fast frames after it.
walk → stop → look around → turn back (ordered to test joins) joins without a flick in Kimodo's own frames: its joins
are `cut`; she walks back along her own path, the turn measured from the shared frames.

**Skinning** (`src/skin.js`). Centres of rotation (Le & Hodgins 2016) by default: per vertex the joints' turns blended
as quaternions (no candy-wrapper collapse at a twisting forearm, which linear blending has) about a centre found from
the rest mesh, placed linearly (no bulge at a bent elbow or knee, which dual quaternions have); weights stay Anny's.
Dual quaternions and linear blending stay as options. Т7's fixes: the collarbone's share of the arm's drop (a pose
layer, `clavicleShare`) and `seam` (where trunk and collarbone/arm weights meet, the skin's movement against the
chest is smoothed over the surface). What depends only on the rest (neighbours, centres, the seam's mask) is computed
once per mesh and kept; only used vertices are skinned; the loops allocate nothing. In node a frame of one figure
takes 1.5 ms (skinning 0.75 ms with centres of rotation, 0.9 dual quaternions, 0.25 linear); a second figure of a body
already seen is made in under a millisecond (the first: 0.27 s for the centres).

**The body to collide with** (`src/collision.js`): a tapered capsule along each bone that carries enough skin, its
radius at each end fitted to the skin around it at rest (the median distance; `inset` shrinks it), moved by the pose;
`distance(x)` → how far (negative inside) and which way is out. `figure.collider()` makes it; the step updates it.

**Characters as data** (`src/character.js`). A description is checked against its schema: an unknown key, an unknown
value, a joint that isn't there, a number out of range is refused with where it is. Its body is pinned by content
hash: when the body's data changes, the character is refused until someone looks and pins it anew; chains pin their
motions the same way. The format has a version; a description of an earlier version is refused with the way to
upgrade it (`node engine/tools/characters.mjs upgrade`, which turned stage 0's version 1 into 2: the collarbone's
share and the corrections became pose layers in the order they were applied). Whether an engine change moves a
character is not promised away by versions: the checks see it, and then it is decided.

**The checks** (`check/`). `numbers.mjs`: every case of `cases.json` — every preset at rest, walking, running, sitting,
lying, at the chain's join, and moments that exercise each option (dual quaternions, linear, sigma, the collarbone's
share, the seam, each correction, a turn as a pose layer and as a rest change kept and turned, a morph both ways,
the pelvis floor, placement and heading, the joins frame by frame, prone; and since stage 1 the full-body presets and
deformers: squash, straight and arcs, caricature, a line with frames turned, a silhouette in a run, a line as a pose
layer in a walk, lying in both spaces, placed and turned, squash as a layer in a jump, smoothing as a layer, a contour
at half strength sitting, a new Anny body walking — 157 cases) — computed in node: the joints and every
4th used vertex of every mesh, compared in millimetres (tolerance 0.05 mm), naming the body or motion whose data
changed under it. Doubling the centres' sigma moved 68 of the 85 cases it had then. `pictures.mjs`: the cases marked `picture`
drawn by their own page (`render.html`: the camera framed by the figure's bounds, 400 × 400 or wide for lying, the
repository's three.js), compared with the stored ones; for eyes. `units.mjs`: refusals, poses, the step, several meshes
and the floor, large meshes, morphs, rest changes and frames, capsules; deformers refused where they don't belong (a
joint-moving one as a layer, a preset whose content changed), every deformer at strength 0 leaving the body as it is on
the rest and as a layer, a layer of the figure the same wherever it stands and faces and carrying every mesh and the
joints, a surface layer as its rest change, every preset making a body, the landmarks in order on five bodies (118
pictures, 18 contracts). Each fails with no cases or a wrong `--only`.
`pictures.mjs --jobs jobs.json outdir` makes pictures of any moments (`focus` on a joint for a close-up).

## Adding things

- *A body*: write a pack with `format: engine/body` on an existing topology (`tools/bodies_moood.py: body_file`), or a
  new topology beside it; joints from Anny's regression if it is Anny's mesh (`tools/bodies_anny.py: Regression`).
- *A body from Anny's settings*: a line in `data/anny/specs.json`, `python3 engine/tools/bodies_new.py <id>`, then
  `node engine/tools/characters.mjs bodies`.
- *A deformer*: `register({kind, of: 'figure' | 'skin', joints?, params, defaults, field | rest, prepare?})` in a file of
  `src/deformers/` imported by its `index.js` — the schema of characters and presets takes it from there; a case for it
  in `check/units.mjs` (strength 0 leaves the body) and in `check/cases.json`.
- *A preset*: `presets/<id>.json` with its label and about in both languages, then `node engine/tools/characters.mjs
  presets` (checks it, pins what it takes, writes the index); a character takes it by its pin.
- *Pictures of bodies*: a sheet in `tools/sheets/bodies.json`, `node engine/tools/sheets.mjs
  engine/tools/sheets/bodies.json <name>`.
- *A rig not from Anny*: `makeRig({skeleton, joints, frames, floor})` and its meshes (`makeMesh`), then
  `new Figure({rig, meshes, layers, floor})`.
- *A mesh on a character*: `E.figure(id, {meshes: [{mesh, name}]})` or `figure.addMesh(mesh)`; `floor: false` for one
  that must not lift the figure (hair, simulated cloth).
- *A simulation*: `figure.addSimulation({step({pose, previous, dt, reset, collider})})`, driven by `figure.step`.
- *A motion*: order it in the moood studio (`make_motion`; `after` to go on from another), keep its ask (`motion(key)`)
  in `data/kimodo/asks.json` and its body data (`motion(key, data: "body")`) as `data/kimodo/<key>.json`, add a line
  to `tools/motions.py` and run it. A chain: a line in `CHAINS` with its joins, then `node
  engine/tools/characters.mjs chains` (pins its motions; refuses motions that don't join).
- *A character*: `characters/<id>.json` (with its body pinned: `node engine/tools/characters.mjs pin <id>`), listed in
  `characters/index.json`; then `node engine/check/numbers.mjs --update --only <id>` and `pictures.mjs --update
  --only <id>` after looking at its pictures.
- *A change of the format*: `VERSION` up in `src/character.js`, its schema, and a step in `upgrade`.
- **Before and after changing the engine**: `node engine/check/units.mjs`, `numbers.mjs`, `pictures.mjs`. A
  difference is either a bug or a change meant — then look at the new pictures and store them with `--update`.

## Not done yet

Bodies (stage 1): the pictogram reads at rest and walking, but with an arm swung far (running, sitting with the arms
forward) its thin shoulder opens — the skin gathered at the stick's root spreads under Anny's weights; the seam fix does
not help. Anny's own "heavy" stays mild even far past her range. The contour deformer keeps the body's small forms
unless `own` < 1; Т7's look also needs its smoothing and proportions (the full presets combine them).

Hands and fingers are carried (all 77 joints) but not checked closely; feet are set on the floor only as a whole
(no foot contacts); the arm can press into the chest's side at the armpit when it hangs close (Anny's weights;
`armsOff` is for it); skinning is on the CPU (fast enough for a few figures; on the GPU when many are needed);
the collision shape is capsules only (no distance field); the rest stands at the body's own origin, so switching from
rest to a motion still jumps by where that motion's frame 0 puts the pelvis (a few centimetres; each motion differs).
