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
With `?heads` (Д5–Д7) the heads' panel: the chosen figure's head (a head preset, or none), its form's ways with their
strengths, each feature painted or as volume, the face's light, an expression and its weight, a close-up of the face;
`&h=<head preset>&hf=<preset>:<strength>,…&hl=<light preset>&x=<expression>:<weight>&face`.
With `?hair` (Д8–Д10) the hair's panel: the chosen figure's hairstyle (a preset of group hair — В1's, or a ready head's —
its own, or none), whether it moves, how firmly it holds its shape, the wind every figure stands in, a close-up of the
head; `&hs=<hair preset>|none&hm=0|1&hh=<hold>&w=<wind preset>&face`.
With `?clothes` (Д11–Д13) the clothes' panel: what the chosen figure wears — each garment's fabric, its silhouette and
how firmly the cloth holds it, taken off, a garment put on — and the wind; `&g=<pattern>:<fabric>[:<silhouette>[:<strength>]],…`
(presets by id; `-` no silhouette) dresses the first figure in these alone, `&w=<wind preset>`.

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
           deform.js      deformers: their registry; on the rest; as pose layers (turns, or the rest change weighed in)
           regions.js     what deformers read off a body: parts along bones, limb shares, landmarks by height; smoothing
           deformers/     lines.js (line, squash, contrapposto), limbs.js (taper, straight, arc), silhouette.js,
                          proportions.js (proportions, caricature), surface.js (anatomy, smooth), contour.js, masses.js,
                          sign.js, curves.js; index.js registers them
           head/          heads (stage 2): frame.js (head units, what of the skin is head), shapes.js (distances, a mesh
                          of a shape), forms.js (designed forms: curves, solid), wrap.js (the wrap deformer), face.js (Anny's
                          face, a head of another age, points, cage, warps), features.js (painted and volume features),
                          paint.js (the face's drawing), expressions.js, pieces.js (noses, Г1's hair, headwear), head.js
                          (a head made on its body: picture, morphs, shading, pieces, its shape to collide with),
                          version.js (how heads are built, versioned)
           hair/          hair (stage 3): build.js (В1's builders, the source now: locks along guide curves, the scalp
                          mass, the inner layer made simpler, surfaces; the guides and each surface bound to them),
                          styles.js (В1's 14 hairstyles, their groups named), fit.js (a hairstyle onto a head), sim.js
                          (hair in motion), hair.js (hair as a head's piece, stored builds, the simulations a figure's
                          meshes ask for), shade.js (how hair takes the light, three.js given)
           cloth/         clothes (stage 4): patterns.js (how each garment is cut for a body: MakeHuman's source meshes,
                          О3's made on the body, the hood; what holds it on; drawn finer than simulated), shape.js (О1's
                          designed silhouettes), sim.js (О3's cloth on the figure's step), clothes.js (a character's
                          clothes: fabrics, garments, their meshes and simulation)
           wind.js        the air hair and clothes move in (a wind preset at a point and moment)
           parts.js       parts over the parts they start from, by id (a head's, a character's clothes)
           solids.js      the body as hair and clothes meet it — the one collision a figure offers: the head's shape
                          with its jaw, the body's skin between two frames, its inside deep in; updated once a step,
                          read by any number of simulations
           capsules.js    capsules round a body's bones at rest (the solids' coarse inside, a layer's arms kept clear)
           decimate.js    a surface made simpler (quadric error metrics, half-edge collapses)
           skin.js        skinning (centres of rotation / dual quaternions / linear), Т7's seam fix
           figure.js      a rig with its meshes: pose → layers (turns, changes of the rest, morphs) → place → meshes →
                          floor → normals; frame and step
           character.js   the character description: schema, defaults, upgrade
           schema.js, hash.js, pack.js, math.js
           view3d.js      three.js stage (lights and shadows for any number of figures, a camera framed by a box)
data/      skeleton.json, soma/ (Kimodo's SOMA skin, Apache-2.0: NOTICE), topology/anny-moood.*, bodies/*.json + .bin,
           kimodo/ (the studio's asks, asks.json, and data of motions not kept in experiments/motions-raw)
           anny/specs.json (the new bodies' Anny settings), bodies/index.json (every body by group, pinned),
           anny/face.json + .bin (Anny's 129 changes of the face on moood's mesh, tools/face_targets.py),
           wraps/ (wrapped heads stored by the key of what they are made from, tools/characters.mjs wraps),
           hair/ (В1's hairstyles built in their design space, stored by their key, tools/characters.mjs hair),
           garments/ (MakeHuman's garments as source meshes on Anny's mesh, tools/garments.mjs)
motions/   <id>.json, index.json (motions and chains)
characters/<id>.json, index.json
presets/   <id>.json, index.json — presets of parts (deformers with their parameters), by group, pinned
viewer/    the viewer
check/     numbers.mjs (the numeric check), pictures.mjs + render.html (the picture check), units.mjs (contracts),
           quality.mjs (quality contracts with limits: folds, stretch, bones, feet, floor, order),
           cases.json (their moments), numbers/ and pictures/ (the stored ones), serve.mjs, browser.mjs, node-read.mjs
tools/     Python that makes data/ and motions/: soma.py, bodies_moood.py, bodies_anny.py, bodies_new.py, motions.py,
           pack.py; characters.mjs (upgrade characters, pin bodies, presets, chains and the cases; index presets and
           bodies); sheets.mjs + sheet.py + sheets/ (labelled sheets of moments for the docs); face_targets.py (Anny's
           face changes); heads.mjs (our heads Г1, Г3, Г2 as head presets, the outfits they were drawn in); overlay.mjs +
           overlay.html (the overlay check against a picture); garments.mjs (MakeHuman's garments into data/garments)
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

**Preset** `presets/<id>.json` (`engine/preset` 2): `id`, `label {ru, en}`, `group`, `about {ru, en}`, `changes` —
deformers with their parameters and strengths (or other presets). A character takes one by `{kind: "preset", id:
"<id>@<hash>", strength, frames}` in its rest or `{…, space?}` in its pose; each change's strength is multiplied by the
reference's. Version 2 names a silhouette's keys (`{at, width, depth, forward}`); `tools/characters.mjs presets`
upgrades version 1 (tuples). `presets/index.json` lists them by group (silhouette, line, squash, contrapposto, limbs, proportions,
caricature, surface, contour, masses, pictogram) with their pins.

Version 3 adds the head's parts: a preset holds one of `changes`, `head` (a whole head, as a character's), `features`,
`expressions` or `light`; version 2 presets were upgraded by `tools/characters.mjs presets` (only their version changed).
Version 4 adds `pieces` (hair, headwear) as a preset's content, and a head's parts changed by their id or name (below,
Character); version 3 presets were upgraded (only their version changed). Groups of the head: `head`, `head-form`,
`features`, `hair`, `headwear`, `expressions`, `face-light`.

**Face changes** `data/anny/face.json` (`engine/face-targets` 2, a pack on `anny-moood`): per change of Anny's (`nose-…`,
`l-eye-…`, `mouth-…`, `chin-…`, `head-…`…) the vertices it moves and their moves at +1 and at −1 (int16 × `unit` m) —
Anny's changes are not linear, so both signs are kept — sampled through moood's head mapped onto Anny's skin fitted onto
it (`fit`), with the vertices that still move unlike their neighbours let go (`spikes` per change and sign: how many;
`tools/face_targets.py`).

**Stored wraps** `data/wraps/<key>.json` (+ `.bin`, `engine/wrap` 1): a wrapped head's positions, stored by the key of
everything it is made from (`src/head/wrap.js: wrapKey` — the wrap's version, its parameters but its strength, the body
it is laid on); `data/wraps/index.json` lists the keys. Written by `tools/characters.mjs wraps` for every character and
case; a wrap not stored (an author's new form) is made where it is needed.

Version 5 (preset) and 6 (character) add hair: a piece of kind `style` (В1's hairstyle: `style`, `off`/`only` groups,
`color`, `shading`, `moves`, `physics: {hold, bend, drag, wind, friction, damping, together}`), `moves` and `physics` on Г1's `hair` pieces, and
`wind: {speed, dir, gust, turbulence}` as a preset's content (group `wind`); earlier files were upgraded by
`tools/characters.mjs presets` and `upgrade` (only their versions changed).

**Stored hairstyles** `data/hair/<key>.json` (+ `.bin`, `engine/hair` 2): what of a hairstyle is slow to build, in its
design space, by the key of what it is built from (`src/hair/hair.js: styleKey` — how hair is built, `HEAD_BUILD.hair`,
the style, its groups kept): each part's inner layer (or a fabric's surface) — positions in 1/65535ths of its box (the
box in the header), triangles, normals and strand directions (bytes), its place across and along the lock above
(1/32767ths), seed, occlusion, colour index (bytes), its binding to the guides (three chains, their places in 1/2048ths
of a node, weights in bytes) — and its locks' occlusion (bytes). The locks themselves, the guides and how the locks ride
them are quick and made where the hairstyle is used. 4.6 MB for the 14 styles (version 1 stored everything: 45 MB).
`index.json` keeps the hash of the code they are built by (`source`, `BUILD_SOURCES`): when it changed,
`tools/characters.mjs hair` builds every stored one again and refuses if one comes out otherwise (then
`HEAD_BUILD.hair` goes up, and they are stored anew — rarely: each version is a copy in git).

**Garments** `data/garments/mh-<name>` (`engine/garment` 1, a pack on `anny-moood`): MakeHuman's garments (CC0) as moood
bakes them — each point's three vertices of Anny's mesh (`refs`), its place among them (`bary`), an offset (`offset`,
int16 × `unit` m) scaled by the body's own measures (`measure`: three pairs of vertices, `span`: their distances on the
body it was made for), the triangles; `index.json` lists them. Written by `tools/garments.mjs` from experiments/data.

Version 7 (character) and 6 (preset) add clothes: a character's `clothes: [garment…]` — `{kind: "garment", id?, pattern,
fabric, color, shape?, strength?, moves?, wide?}`, an outfit `{kind: "preset", id}`, `{kind: "off", id}`, or `{id, …keys}` —
over its base's by id (`src/parts.js`, as a head's pieces); a preset's content `clothes` (group outfit), `fabric` (group
fabric: `{density, stretch, compress, bend, damping, friction, thick, air, sheen, rough, opacity}`) or `shape` (group
garment-shape: О1's design keys, `src/cloth/shape.js` SHAPE); earlier files were upgraded (only their versions changed).
The hoods the ready heads wore as rigid pieces (`wear-hood`, `wear-old`, the piece kind `hood`) are gone: they are
garments of the outfits `outfit-hood`, `outfit-old` (tools/heads.mjs).

**Bodies' index** `data/bodies/index.json`: every body with its pin, group (moood, t8, t8-head, age, build, origin),
label and height. **Anny's settings** `data/anny/specs.json`: per new body its phenotype (`ph`), local changes (`lc`)
and an optional head of another age (`head: {ph, lc, r}`).

**Character** `characters/<id>.json` (`engine/character` 5), checked against a schema (unknown keys and values refused):
`base?: "<character>@<hash>"`, `body: "<id>@<hash>"` (required without a base), `rest: [changes]`, `pose: [layers]`,
`skinning: {method, sigma, seam}`, `motion: {floor}`, `look: {skin, roughness}` — the whole list in `src/character.js`;
the defaults are kept there (`DEFAULTS`). Rest changes and pose layers include every deformer and presets. `base`
starts from another character (a full-body preset as a part): its body, rest and pose, then this one's — its body if it
names one, its rest changes and pose layers after the base's, its skinning, motion and look keys over the base's; the
base is pinned by its description's content (`E.resolve` reads it; `tools/characters.mjs pin` pins it anew). Version 3
(upgraded from 2 by `tools/characters.mjs upgrade`): a silhouette's keys named; `space` only on layers that are turns.
Version 4 adds `head` (a character without one is as it was): `{preset?, strength?, size?, form?, features?,
expressions?, pieces?, light?, skin?, ref?}` — the head preset it starts from, its own form's changes (deformers or
presets of them, made on the rest after the character's own, frames kept), features (painted or as volume),
expressions, pieces (or presets of each), light (or a preset of it), the face picture's skin colour, and the picture it
was drawn after. Over its base character's head and its preset's: size, skin and light keys over theirs; its form's
ways, features, expressions and pieces go over theirs by name (a form's way: its `name`, else a preset's id, else a
deformer's kind; an expression's `name`) or id (features, pieces): `{kind: "off", id | name}` takes one away, one
without a kind changes only the keys it gives (`{id: "eyes", as: "volume"}`, `{name: "form-red", strength: 0.5}`;
then checked whole), a whole one takes the place of theirs, a new one comes after; `strength` weighs the whole form it
starts from. Version 5 (upgraded from 4, only its version changed) added the changes by id and name and `strength`.
Pose layers take `{kind: "expression", name, weight}`.

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
the order listed, each seeing what the ones before did (turns rebuild the places; a change of the rest moves this
frame's rest places of the joints, `ctx.rest`, by its weight, and the places are rebuilt down the bones as they now are;
morphs weigh a mesh's morphs) → if the rest changed, the pelvis set on Kimodo's path again by this frame's hip height →
placed → every mesh off that pose (skinned meshes with this frame's morphs and changes of the rest weighed in, about this
frame's joints and centres of rotation) → **the floor**: with `motion.floor: "lowest"`, the lowest point of every mesh that counts for the floor (`mesh.floor`), over
the vertices its triangles use, is set as high as SOMA's skin's lowest at that moment (scaled) — on the feet, lying,
rolling, nothing in the floor; the one shift moves every mesh and the pose (`pose.shift`) → normals. `frame(clip, t,
pose)` keeps nothing and writes into the pose it is given; `step(clip, t)` is the stateful frame for simulations: it
keeps the current and previous pose (`figure.pose`, `figure.previous`, valid until the next step), the time step, and
a reset on the first step, a new clip, a jump back (a scrub) or ahead of more than `maxGap` frames; `step(clip, t, {loop:
true})` goes on across the clip's end (the clip begun again: the time goes on, the body jumps back, a simulation carries
on from where it was on the body). Then the body's solids (`figure.solids()`, once made) are updated once, and each
simulation (`addSimulation({step(ctx)})`) runs with `{pose, previous, dt, reset, jump, t, solids}`, after the floor.

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
from moood's woman smoothed by 6 steps (this gives Т8's own bodies again within 1e-7 m), joints by Anny's regression. The
heavy ones are her weight slider (1.2) with her own local sliders of fat — the upper and lower arms and legs, a double
chin, the head, the waist's and hips' girths, the belly; her weight alone stays mild even far past its range (at 1.7
the waist was 10 % deeper than at 0).

**Deformers** (`src/deform.js`, `src/deformers/`). A deformer has a strength and its parameters; a character lists them
in its order. Two kinds by what they act on at the rest. *Of the figure* (line of action, squash and stretch,
contrapposto, the silhouette, taper, straight against curved, arcs) — a field over the body's rest that moves every
point by where it is and which limb it belongs to (each vertex's share of the five limbs, from the skin, smoothed over
the surface), and every joint the same way. *Of the surface* (proportions, caricature, anatomy, smoothing, contours,
masses, the sign) — computed on the surface. Sizes are shares of the body's own height measured at its rest. On the rest
either moves the body and its joints once (then `frames` keep or turn), and turns no triangle over: where a change would
fold the skin, its move is smoothed over the surface there until it doesn't (`regions.js: unfold`; the large move — a
head lowered, a limb thinned — stays). As a pose layer, by what it is:
- *a change of the pose* (line of action, contrapposto) — turns of the pelvis, the spine, the neck and the head, each
  bone by the curve's slope at its middle, in the figure's frame now (`space: "pelvis"`: a lying figure bends along its
  length) or its heading (`"upright"`); every bone keeps its length, the arms ride with the chest, and the legs are put
  back on their feet (`pose.js: keepFeet`, two bones on the rest's own lengths); where a hip turned away from its foot
  farther than the leg reaches, the pelvis goes down as far as that leg needs.
- *a change of the form* (every other) — its rest change, weighed in every frame: the vertices, the centres of rotation
  and the joints' rest places moved as the same change on the rest moves them, then skinned and posed like the rest.
  At weight 1 the figure is the one the same change on the rest (frames kept) gives; a code layer before it can set
  its weight (`ctx.weights["<place>:<kind>"]`, `figure.restLayers`). Another skinned mesh (clothes) follows by the
  same field when the deformer is one of the figure. The sign gives its own skin weights: a change of the rest only.
No field is evaluated over the posed figure (stage 1 did: a field made for the rest's heights met a raised forearm at
the wrong height and shortened it, and planted feet slid).

*Where the figure stands* (what the engine promises): the pelvis is on Kimodo's path, scaled by the hip height of the
rest it moves — the rest's changes included, and a change of the form as a layer the same; the feet go where that path
and the body's own legs put them (a longer-legged form takes longer steps, so they don't slide). A change of the pose as
a layer leaves both: the pelvis where Kimodo put it (lowered only as far as a leg needs), the feet where they were.
The floor step then sets the lowest point on the floor.
- *Silhouette* — Т5's body-as-one-shape and Т6's cage were the same thing (width, depth and forward by height): one
  deformer, keys at landmarks (`regions.js`: floor, ankle, knee, crotch, hips, waist, chest, armpit, shoulders, neck,
  head, top) or shares of the height (`{at, width, depth, forward}`), a monotone curve between them smoothed over
  `soft`; the arms ride with their root and turn out (about the line across the arm and its way out) as far as the new
  torso needs; the legs ride with their root and below it grow thicker or thinner about their own line (scaling the
  thighs as the torso by height sheared their tops: a raised leg showed a step where it meets the body). Т5's hard corner at the hip (its keys eased with zero slope each, close
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
  displacement smoothed where two parts meet, so no pinch is left (only there: inside a part the move is a
  similarity a smoothing over a fine finger would spoil); the neck grows along the torso's line. *Caricature* —
  against the average of bodies of one topology, each scaled to this one's height about its pelvis's line and floor.
- *Smooth* (Т9: the cotangent Laplacian, one implicit step, the girth given back along the normal; the head, the fingers
  and the toes keep their forms by default — thin and finely meshed, smoothed over centimetres they fold), *anatomy*
  (Т1: the small forms drawn out no farther than a third of the mesh's own edge there).
- *Sign* (Т4) — a stick per bone with balls at the shoulders, elbows, hips, knees and ankles, a bar across the
  shoulders and one across the hips, a ball for each hand, a rounded foot as long and as high as the foot's own skin,
  the head's ball, the trunk's figure; the trunk's skin settles onto the trunk, each limb's goes out from its bones'
  line onto the limb, blended by the limb shares, then all is set on the whole sign. It gives its own skin weights: a
  stick its bone, a joint's ball both bones across it (a ball turned about its own centre stays the same ball, so a bent
  elbow or a raised arm never opens), a hand's ball the hand, the foot the foot and its toes, the trunk Anny's trunk
  weights, the head the head — blended across a seam by which piece the settled point lies on. (With Anny's weights a
  stick from the shoulder straight to the wrist opened at the shoulder and thinned to a ribbon in any swing.)

**Presets** (`presets/`) are plain data: Т5's ten silhouettes and Т6's four others, six lines, squash, stretch,
contrapposto, five limbs, fifteen proportions, caricature and its reverse, anatomy both ways, smoothing 2, 4, 8 cm, Т7's
three contours and their masses and the shoulder, four pictograms. Full-body presets are characters (princess of
Disney, mother of Pixar, girl of anime, Burton-thin, pear old woman, V hero, egg baby, two pictograms): a base body and
presets with strengths, some with pose layers; another character takes one whole as its `base` and adds its own.

**Heads** (stage 2, `src/head/`). The base is always Anny's head mesh: one skin with the neck (no seam), moved by the
skeleton (the Head, Jaw and eye joints with Anny's weights). Everything of heads is measured in *head units*: the
cranium's radius 1, its centre a little above the Head joint (Г1's), x the person's left, y up, z forward; *omega* is
how much of each vertex a change of the head moves — all of the head, fading down the neck (its weight on the head's
joints, smoothed over the surface). A head is made in two steps:
- *Its form* — changes of the rest of the head only (`head.form`, made after the character's own rest changes), each
  with its strength, in the author's order; they are deformers like the bodies' (`src/deform.js`), so each also goes as
  a pose layer and with every other deformer:
  `face` — Anny's own face settings: her 129 local changes of the head and face, made by people, at their value (each
  sign its own move), on moood's mesh (`data/anny/face.json`; scaled to the head's size; carried there through a map of
  moood's head onto Anny's skin fitted onto it — her teeth, tongue and eyeballs left out — with the few vertices that
  still move unlike their neighbours, where moood's face differs in kind, let go and filled in from around them); `headOf` — a head of another
  age (or of any body of the same mesh) laid in this head's place at its size, its joints going with it; `points` — the
  face by points: 24 landmarks found on the head's own skin (on the stored body it came from: so after a wrap they are
  the same points of the skin) moved by [dx, dy, dz], one biharmonic warp through them, the neck held, mirrored unless
  told; `cage` — a Bézier lattice round the head, its points moved; `warps` — pushes (a point and around it, falling off
  over r) and scales by height; `wrap` — Anny's head laid onto a designed form (`forms.js`): from a drawing's curves (Г1's
  — a front outline and a side profile lofted on a domed cranium, a nose from its side curve or as a capsule with a
  ball, lips, cheeks and jowls as masses, ears) or a solid fitted to a picture (Г2's — rounded slices, the jaw's
  underside, masses, a capsule nose, lips, the eyeballs' bulge; its cranium laid on Anny's, her neck measured for it).
  The wrap is Г3's: Anny's landmarks (`landmarksOf`: eyes, mouth corners and middle, ears, chin, top, back) moved to
  where the form has them (`marks`), her midline laid along the form's profile, her lips' seam along the drawn mouth (a
  drawn mouth's line; a grin's dark inside, midway between its teeth and its bottom), the neck held →
  one biharmonic warp → onto the form in rounds, each round's pull smoothed over the mesh → exactly onto it, the spacing
  evened, the join with the neck eased (`onto` says how far down: Г3's 0.35–0.95 of omega, Г2's 0.02–0.17) → folds
  eased until none is left (Г3 stopped at 40 rounds and left a few three-deep pleats under the eyes; now up to 200),
  the eyes' middles and a grin's parting held where they were laid. A nose too long for the skin, or a ball of a nose,
  is drawn on as its own piece (`nose.piece`): the skin goes over the nose pressed back, the piece is what of the form
  stands out of that. A wrap takes 3–20 s: its result is stored by the key of what it is made from (`data/wraps/`) and
  read, not made again, at every load (a head loads in 1–3 s).
- *On that rest* (`head.js`): every vertex's place in the face's picture — on the head the face is drawn on: right
  after its wrap (where the form's marks put Anny's eyes and mouth), or Anny's own head before its form, where features
  are drawn on her eyes, brows and lips; so whatever changes the head after (a face by points, Anny's face, a head of
  another age, a layer, an expression) carries the drawing with the skin — and how much of the picture it shows (1
  where the head faces the front, fading as the skin turns away, down the neck and outside the picture — mixed in the
  shader, so nothing of the drawing smears round the sides or shows behind the head); the mouth set on where the lips
  part (a drawn mouth moved onto it, a grin's teeth ending above it: an open jaw opens in the mouth); the expressions'
  morphs of the skin, placed by where the features are drawn; the shading normals of the designed form, weighed in as
  far as the skin lies on it; which vertices are face (no cast shadows there); the pieces (noses, Г1's hair as it was,
  coarse headwear): skinned to the Head joint and following the skin under them — each carried as one by the affine
  change that best carries its skin's vertices this frame (`src/mesh.js: followOf`, `src/figure.js`), so an
  expression moves a nose, a bigger head as a layer grows Г1's hair (a hairstyle of В1 is fitted onto the grown head:
  below, Hair); a nose piece takes the face's washes of colour (a
  tint, the blush across it); the features as volume (a drawn mouth's lips each its own relief on its side of the lips'
  parting); the head's shape to collide with (`head.shape`: the designed form, or a ball fitted to the head; met as the
  body's solids meet it, `figure.solids()`, carried by the Head joint and, below the mouth, by the Jaw joint).
*Features* (`features.js`, `paint.js`), a layer of their own, per feature: an eye, a brow, a mouth (drawn from its own
lines, or a grin), marks, blush, a tint, a mask — painted on the skin (Г1's and Г3's drawings, drawn into one picture
the skin takes by its place at the rest, so the drawing follows the skin in every motion and expression), or as
volume: a relief of its own outline raised from the skin (`lift`), laid on the skin's triangles under it (an
`attached` mesh, `src/mesh.js`: each frame on its host, after it, along its normal), taking the same picture — mixable.
*Expressions* (`expressions.js`) by the mesh: each a morph of the skin made on the head as it is (lids swelling over
the eye, the mouth's corners up and back, cheeks rising, brows lifting) and the jaw turned by its joint, played by a
pose layer `{kind: "expression", name, weight}`; what each asks of the painted features (close, happy, smile, open, up,
down) the picture redraws (`figure.ctx.expressions`). *Face light* (`head.light`, `view3d.js`) is an option: toon —
three soft tones, not tone-mapped — with an outline (the back of a shell a little outside), shading from the designed
form (its normals at each vertex's rest, turned each frame as the skin's joints turned them: `src/figure.js`), no cast
shadows on the face; the toon's cast shadows taken through its own tones (a shadowed point is lit as the side away
from the light is; `shade`: its darkest tone) — three.js's multiplying of the light by the shadow map left grey blotches
and stepped edges; a ball nose's shine drawn by the key light; a closed piece casts its shadow from its back faces (no
acne on thin locks); or the stage's own light. On a head wrapped exactly onto its form the form's shading differs from
the mesh's own only a little (the skin lies on the form): it shows where the skin leaves it, and on a toon head.
*For authors*: the overlay check (`tools/overlay.mjs`): the head seen at its picture's angle (or the angle that fits
best), its landmarks — the drawn eyes' and mouth's places on the skin, the nose's tip (a nose piece's), the chin —
carried onto the picture's by a similarity, the error in pixels, the picture with the face's outline (without hair and
headwear) and both sets of points. *How heads are built* is versioned (`src/head/version.js`: the wrap, the picture,
the expressions, the pieces): what is stored is keyed by it, and the numbers check keeps it and each head's picture.
*Presets* (`presets/`): 11 heads (Г3's four, Г1's seven — now wrapped with Anny's mesh; `tools/heads.mjs` writes them
from the experiments' own data, with characters `head-*` wearing them on the moood body each was drawn on), each taking
its parts as presets of their own — its form (`form-*`, group head-form), features (`features-*`), hair (`hair-*`) and
headwear (`wear-*`) — so a part of one head goes on another and a head taken as a part is changed by its parts' ids;
the drawn face's expressions, four lights, eleven more ways of the form (Anny's face: small nose, big eyes, soft chin,
strong; a toddler's head; points: cute, long; cages: pear, tall cranium; warps; Г2's Giulia as a solid fitted to her
picture), two sets of features for Anny's own face (dot eyes; features as volume — on her eyes and lips); and five
characters that combine them (`head-anny-face`, `head-anny-age`, `head-points`, `head-cage`, `head-red-mine` — the
red-haired girl taken as a part, her eyes as volume, a long face by points).

**Hair** (stage 3, `src/hair/`). A hairstyle is one of a head's pieces, so it is taken, changed and taken away as the
head's other parts are (by its id, `hair`): `{kind: "style", style, off?, only?, color?, shading?, moves?, physics?}` —
В1's hairstyles (experiments/hair) as code, each a set of parts (surfaces) of named groups of items (`cap`, `fringe`,
`back`, `sides`, `under`, `tail`, `braid`, `buns`, `hat`…), so `off: ["fringe"]` takes a group away, `only` keeps some;
14 presets `hair-v1-*` (group hair) hold them, and four winds `wind-*`. Г1's and Г3's hair (the ready heads' `hair-*`)
stays as it was drawn — rigid on the head — unless `moves: true`: then its locks (ribbons along their curves) and its
masses' clumps hang on guides of the same simulation, the cap, buns and ties ride the head (`hair-g3-red`,
`hair-g1-alva`; the viewer's «движутся»).
- *Built* in the design space round В1's neutral head (`build.js`, the source now; В1's own copy stays in
  experiments/hair for its page): each lock a swept lens section thinning to a pointed tip, drawn twice — its own
  surface, and merged with the part's other items into the inner layer a little inside, dark, that fills the gaps;
  strand directions, places across and along each lock, a seed per lock, an occlusion term from the hair's own volume.
  The locks have В1's depth: thinned to 0.6 of it (stage 3's first take, against Pavel's «все пластилиновые») they left
  gaps and dark cracks at the crown and a ragged look; the plasticine is fought by the light (below), not by thinning.
  The inner layer is made simpler where it is flat (`src/decimate.js`: quadric error metrics, half-edge collapses, at
  most 0.4 mm off, edges up to 12 mm, the seams where it is bound to another guide or takes another colour kept — a
  fifth of its points). Each lock's guide curve becomes a chain of points every 2 cm, stiff by its length (short hair
  holds its shape, long hair swings, heavy tails and braids slow); a clump's smaller locks ride their clump's chain, a
  braid is one chain, combed hair and buns ride the head; every surface point is bound to up to three chains where it
  lies (the inner layer sharply, so it parts where locks part). What is slow (the inner layers, the occlusion, 5–20 s a
  style) is stored (`data/hair/`); the locks, the guides and their binding are made where it is used.
- *Fitted* onto the head (`fit.js`): its cranium fitted with an ellipsoid through the head's designed form where it has
  one (a wrap's form, found along rays), else through its skin, above the brows; every point carried as В1 carried it
  (on the designed skull → on the head's, off it → its direction and its distance, grown with the head); then, near
  the skull (fading out by half a skull's radius off it), moved along the skull's normal until it lies as far from the
  head's real surface — its form's distance, else its skin's (moving least squares, as the solids measure it) — as it
  lay from the designed head, grown with the head: roots as deep under the scalp as designed, the hairline on it (the
  first take added the surface's difference from the ellipsoid by direction, coarsely: the skin stood through the cap at
  the hairline, kpony's was ragged). The surfaces are skinned to the Head joint, shaded by their own normals and
  strands (`mesh.shading`, turned with the joint: `src/figure.js`). A change of the rest as a pose layer (a bigger head)
  moves the hair as it moves the hairstyle fitted onto the changed skin against the skin before it — the surfaces at
  rest and, moving, the guides, where the groom pulls and where the hair hangs — weighed in each frame; the head the hair
  rides is the Head joint as this frame's rest has it.
- *In motion* (`sim.js`, В1's simulation on the engine's step): `figure.step` runs it after the floor in small steps of
  1/240 s — always that, whatever the frame's step: what a frame leaves over is carried to the next, and the free points
  are drawn carried on by their velocity over it, the roots where the head is (fixed small steps: the hair moves the same
  at 20, 30, 60 or 144 frames a second, within half a millimetre on the whole; the first take took the frame's step in
  pieces of different sizes, its dampings by the small step, the skin as the frame ended — 27/21/20/30 mm apart). The
  step's frame leaves the hair's meshes to it (`figure.driven`), `frame(clip, t)` alone draws them at rest on the head.
  Each small step: gravity and the air (wind with gusts and turbulence round each lock, less the lock's own speed, drag
  as its square, across a lock more than along it — a lock of hair is light for its surface: a loose one falls no faster
  than some 2 m/s, so a gentle breeze leans long hair some 20°, a strong wind 50–60°, and running streams it back; В1's
  air was eight times weaker, a strong wind leaned it 24°); twice the groom — each point pulled toward where the
  hairstyle has it, carried by the head; each segment bent back toward its angle against the one above (XPBD's share
  k·h²/(1+k·h²)); the solids at that small step's moment, with friction against their motion, a point pushed out leaving
  without the push's speed (no bounce); lengths exactly (follow-the-leader with its velocity correction, twice: last;
  ringlets give like springs); the hair's own friction (its motion against the head dies at the hair's rate, or, where
  its pull is stiff — short hair — at 0.4 of that spring's critical rate: stiff short hair followed a running head
  ringing, a shimmer at 30 frames), hair against hair — each point's velocity drawn toward its
  neighbours' in the other locks near it at rest, as film smooths hair's velocities (Petrovic et al. 2005: neighbouring
  locks move as a mass, Г3's ribbons don't fall apart, long hair doesn't crumple into spikes in a roll) — and zigzags
  damped, each a rate (1/s). The inner layer is hidden where the hair in motion stretches it past 1.8× (`shade.js`:
  where locks part, what is under them shows, not a web drawn out between them; its shadow with it).
  The rest: designed as it hangs, so the groom is set against the weight (let hang, moved up by the sag, five times),
  then let settle on the standing body — first draped (the bend eased, so locks lie over the shoulders, not stand off
  them), then stiff — and that is the rest (В1 left locks standing off the shoulders like flaps). The bend keeps the shape
  it hangs in free, only the pull takes the body's settling in. A reset (the first step, a new clip, a scrub back)
  places it where it hangs at rest on the head and lets it settle without speed in that pose; a loop (`step(clip, t,
  {loop: true})`, the viewer's playing) carries it on across the clip's end as it was on the head — moved with the head's
  jump, swinging on as it swung on it (Kimodo's clips are not cycles: where the body jumps into the hair, it is pushed
  out); the same moment again moves nothing. `physics` weighs the hairstyle's own: `hold`, `bend`, `drag`, `wind`,
  `friction` (against the body), `damping` (its own motion against the head, its zigzags), `together` (hair against
  hair). The wind: a preset (`sim.wind`), the viewer's «Ветер».
- *The solids* (`src/solids.js`, `figure.solids()` — the one collision the body offers, for clothes too): updated once
  a figure step (`S.update(previous, pose, how, dt)`, before its simulations), then only read — a reader keeps its own
  moments (`S.moment(u)`: the solids at a share of the frame, made at each of its small steps), so hair and clothes
  read it at once and none changes what another sees. The head's shape (the designed form, `head.shape`) carried by the
  Head joint and, below the mouth, the Jaw joint, baked into a grid per head (trilinear); the body's own skin (but a
  designed head's) between the previous frame and this one, at the moment asked: a distance from it by moving least
  squares over its nearest points' normals (in a hash of 3 cm cells, made at a moment the first time it is asked), how
  fast it moves there (friction); and, farther in than the skin's points reach, a coarse inside — the bones' capsules
  (`src/capsules.js`) shrunk inside the skin — which says how deep and which way is out (the first take had nothing
  past 3 cm, and took the end of the frame's skin for every small step: a hand at 5 m/s jumped 17 cm). The answer is the
  skin itself; a reader keeps its own thickness (hair: half a lock's depth, and as deep as it lay at rest). Tried first
  and dropped as the contact surface: the engine's capsules (round a collarbone one stands over the shoulder like a
  shelf, and long hair stood off it in flaps); each bone's skin carried rigidly by its bone (neighbours disagree where
  the skin bends between them, and pushed the hair centimetres in a step); one distance from the nearest skin point (it
  jumps where that point changes: jitter). A lock's segments are kept exactly — the lengths are made last in a small
  step, so what the solids push out a second time is left to the next.
- *Light* (`shade.js`): В1's hair shading with the stage's lights — strands fine and coarse, bundles a centimetre or two
  across with dark partings (В1's strands were finer than a pixel at a head's size, so a lock read as one smooth body),
  darker roots and inner layer, the diffuse light taken partly along the strands (Kajiya-Kay), a two-lobe highlight
  along the strands broken by the bundles, light through the thin edges against the light, the colour richer in shade;
  the locks outlined in a dark of their own colour (В1's black), the inner layer not.

**Clothes** (stage 4, `src/cloth/`). One clothing system, as agreed with Pavel: О3's real cloth as the base (garments,
fabrics with their properties, collisions, wind, every motion), О1's designed silhouette of a garment as the shape the
cloth is pulled toward with a strength, О2's MakeHuman garments as source meshes. A character wears `clothes` — garments,
each of a pattern in a fabric with a colour, and outfits (presets of them) — taken, changed and taken off by id over
its base's, as a head's pieces are; 16 fabrics `fabric-*` (О3's), 22 silhouettes `shape-*` (О1's dresses, skirts,
sleeves, legs), 11 outfits `outfit-*` (what the ready heads were drawn in), and 10 dressed characters `clothes-*`.
- *Cut* for the body (`patterns.js`, the source now; О3's copy stays for its page): MakeHuman's garments (dress, T-shirt,
  sweater, polo, oversized top, tunic, robe, hooded top, trousers, shorts, skirt, wide trousers, apron, boots, flats) laid
  on any body of Anny's mesh by their three vertices and offsets scaled by its measures (its rest changes made, its head
  made — a deformed body, a ready head's character); О3's made on the skin itself (blouse, cardigan, jacket, swimsuit:
  the skin's region offset by the garment's ease, smoothed so the cloth bridges the hollows, the cut points moved onto
  the cut lines), a flared skirt (a tube that clears the hips and legs), a scarf (a strip laid round the neck, its flat
  lengths kept); Г1's turtleneck (the neck's skin); the heads' hood (its shell round the designed head, the face open,
  cut where it meets the shoulders) — the hoods the ready heads wore as rigid shells are cloth now, and don't go
  through the shoulders. Each says what holds it on (a waistband, a neckline, a cuff lightly, a dress over the
  shoulders and its openings above the chest; 1 where the skin carries it, fading along the cloth), its layer (worn
  under what), whether its sleeves and legs belong to limbs, whether it can fold onto itself, whether it hangs. Shoes
  ride the skin (`moves: false`, which any garment can take).
- *Its silhouette* (`shape.js`, О1's `tailor`, the source now): the garment read round an axis (the trunk, each arm,
  each leg) as rings of radius by height and angle, and on them its design drawn — how stiff it is (each ring toward
  its convex hull), where it hangs from and falls straight from its widest ring, its silhouette below that (A-line,
  bell, full, tulip, pencil, trapeze, bubble; sleeves fitted, straight, puff, bell, bishop, cap; legs straight, wide,
  flare, taper, balloon), its section (round to square), its length, folds as a drawn rhythm round the hem. The cloth
  is *cut* to that form (its lengths are the form's: a bell has more cloth at the hem), and *pulled toward* it as the
  body carries it with the garment's `strength` (a spring of 2000/s² at 1 — the cloth sags 5 mm from its form under its
  own weight: a stiff petticoat holds the bell — to 0: the cloth hangs freely as it was cut, in the folds of its extra
  fabric); where the body stands in the form (a knee rising into a bell, sitting, the floor) it is not pulled there
  but lies on the body (Pavel on О1's: "a weaker pull to the form when sitting"). A garment with no design and a
  strength is pulled toward its cut (a stiff hood keeps its shell). О1's ladder down to the sign is not carried (the
  pictogram Т4 keeps the sign).
- *Carried* by the skin: each point skinned as the skin nearest it is (never a hand's), the weights smoothed over the
  cloth (taken point by point, two points side by side under an arm took a collarbone's and a chest's and were torn
  apart in a pose), what hangs below the hips carried by the pelvis as far as it hangs (a bell's hem swings with the
  hips, not with each thigh, and points between the legs are not torn apart by them). That is where a held point is
  pulled, where the form is, and what `frame()` alone draws (the cut on the skin, as О1's "ride").
- *Simulated* (`sim.js`, О3's XPBD cloth, the source now) on the figure's step: all of a figure's cloth in one
  simulation, the innermost garment first in each small step of 1/240 s (always that: what a frame leaves over goes to
  the next, the cloth drawn carried on by its velocity over it — the same at 20, 30, 60 or 144 frames a second); per
  small step gravity, the fabric's damping and the air (the hair's winds, `src/wind.js`, pressing on each point as its
  surface faces the flow less its own velocity); lengths three times (each edge holds against stretching with the
  fabric's stretch, gives way when pushed together, so it folds; the edges ordered by their distance from where the
  garment hangs, so a pass carries the weight down from the top), bending (Kawabata's rigidity per
  hinge), what holds it on (a held point an elastic to where the skin carries it, its weight taken up so a waistband of
  a hundred points carries trousers of five thousand), its form, soft tethers (no farther from a held point than the
  cloth between is long, a share of the excess a step), its own points kept apart, then the body: the figure's solids
  (`src/solids.js`), the one collision hair uses too — the skin between the frames at that small step's moment, each
  point keeping the skin points nearest it (`S.kept`: looked for afresh every other step, of the nearest one's limb
  only — between the legs, both legs' skin together pushed a skirt sideways through one — but the fingers', on which
  cloth lies as on a mitten), deep in as deep as the capsules' surface; with the fabric's thickness and as far as the
  cloth between two points sags in over the body's tightest curve; each triangle's middle out of the skin too (a knee
  goes between points two or three centimetres apart, though each keeps out); a sleeve or a trouser leg also out of
  its own limb's skin; the head's designed form; the garments under it where they lie together as dressed, not past
  their edge; the floor — cloth pressed between the body and the floor left lying on it; friction against the skin's
  own motion, and no bounce (a point pushed out leaves without the push's speed).
- *Its rest*: put on the body at rest (out of the skin and the garments under it; its lengths as it lies then), then
  let hang 1.2 s. A reset (the first step, a new clip, a scrub back) takes it from there carried by the pelvis to where
  the body is, the body going into its pose over 0.4 s along the solids' entry (`S.entry`) with the cloth along it — as
  a person dressed standing goes into a stride (placed straight into a stride, a skirt's hem was left round a leg
  that should be inside it) — then 30 small steps without speed; a loop carries every point with the skin under it.
- *Drawn* finer than simulated: MakeHuman's garments, the flared skirt and the hood are simulated as cut (points 2–3 cm
  apart) and drawn with each triangle in four by the butterfly scheme (through the simulated points: Loop's smoothing
  pulled a surface drawn tight over a knee into it); the skin under close cloth drawn sunk 4 mm (О3's: the skin's finer
  bulges would show between the cloth's points; drawn only); the fabric's sheen and roughness, its inside darker, a
  toon head's light and outline on its clothes too. Hair lies over the clothes (`S.over`: the cloth's surface, out to
  its thickness, at the hair's moments — a collar, a blouse's shoulders; what lies under them at rest, under a hood, is
  the hood's to keep off).
Tried and dropped: simulating MakeHuman's garments subdivided (О3's: points a centimetre apart need small steps of 1/960
s to keep their lengths, 0.1–0.4 s a frame); cloth meeting the skin by one search a point every small step (four times
the cost: the points kept do it); hard tethers (they fought the body where cloth goes round it and threw it at 60 m/s);
placing a reset straight in the pose; limiting how far an edge is shortened in a pass where it touches the body (against
a knee drawn through the cloth: it tore a dress pressed on the legs by the wind instead). A frame of a dressed figure's
whole step costs 24–126 ms in node (a dress 24–30, a T-shirt and trousers 65–77, three garments 98–126); several characters at once,
on the GPU, are the later task — the step allocates nothing and works on flat arrays, garment by garment.

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

**Capsules round the bones** (`src/capsules.js`): a tapered capsule along each bone that carries enough skin, its radius
at each end a share of the skin's distances round it at rest (`fit`: 0.5 the median; `inset` shrinks it). The body's
solids take them, shrunk inside the skin, as its coarse inside (below, Hair: the solids); a layer (`armsOff`) as what
the arms keep clear of; the viewer's «капсулы» draws the solids' ones as the step left them.

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
and the floor, large meshes, morphs, rest changes and frames, capsules; deformers refused where they don't belong (the
sign as a layer, `space` on a change of the form, a preset whose content changed), every deformer at strength 0 leaving
the body as it is on the rest and as a layer, a layer the same wherever the figure stands and faces and carrying every
mesh and the joints, a surface layer as its rest change, every preset making a body, a character from a base, the
landmarks in order on five bodies (118 pictures, 19 contracts). `quality.mjs` (~40 s): whether things are still sound,
each a measure with a limit — no triangle turned over by any preset on five bodies (moood's woman, child and old man,
the heavy man, the chibi baby; a few allowed only where a change presses the skin into itself on a body with no room:
a reed's hips into a heavy man's thighs, a baby's difference from grown-ups drawn out), every full-body preset's edges
at rest against its base and in walk, run, sit, jump and dance no more stretched than the plain body's (×1.2), pose
layers keeping every bone's length (turns exactly; changes of the form as their rest change makes them), planted feet
not sliding with a layer, the lowest point on the floor, layers that don't commute giving two figures in two orders, a
change as a layer equal to it on the rest, and a weight set by a code layer (388 contracts). Each fails with no cases
or a wrong `--only`.
Since stage 2: every head character in every moment, expressions, the face's light options, skinning methods,
a body's deformer on the rest and as a layer with a head, placed and turned (numbers and pictures, close-ups of the
face; the numbers keep each head's picture places, how much of it each vertex shows, a hash of its drawing at that
moment and how heads were built, and name what changed); `units.mjs`: every head preset makes a head, refusals, a head
from a preset with its own changes, a head taken as a part — weakened, a way taken away, a feature changed by its id, a
features preset — an expression at weight 0 and 1, a face deformer on the rest and as a layer, the head's and the neck's
shapes in the pose they are given (the jaw's part with the jaw), every character's wrap stored and the stored wrap
what the wrap makes now; `quality.mjs --only heads` — the plain body's own limits where a head has a counterpart: per
head no triangle turned (on a wrapped head against its form, and after it against that head); no vertex standing out of
its neighbours (a spike, a crumple: 1.5 mm against the base, or against the skin laid exactly on the form); edges at
rest (3× as the bodies'; 5× on Anny's own changes — they open moood's closed eye slit; 8× on a wrap — its design); in
seven motions, with every skinning method, on a body changed on the rest and as a layer, and smiling in a motion, no
more stretched than the plain body (×1.2); in expressions 2.5× (the lips that open left out); no crease where the head
meets the neck, under the jaw or at the nape; the picture not smeared where it shows (5×); the drawn eyes on the skin's
eyes and the mouth's parting on the lips' (3 mm); reliefs no more stretched than the skin; a nose piece on the skin in
motion, and every piece on a head grown by a layer (5 mm).
Since stage 3: a moment of a figure whose hair moves is its simulation stepped frame by frame from the clip's start to
that moment (in the case's `wind`), so the numbers and pictures keep it; cases for every hair character in every
`each` moment, the wind and gusts, looking round, jump, dance, bow, roll. `units.mjs`: every hairstyle preset stored,
what is stored what is built now (one built again; the hash of the code they are built by as stored); a hairstyle
changed by its groups, colour and physics, refused a group it hasn't; the body's solids (the skin between two frames
where it was in between, its velocity, deep inside and which way is out, two readers at once); the head's solid with
its jaw; the step — a scrub back the same as a fresh start, a loop carrying the hair on (a tenth of what starting
afresh moves it), the same moment again moving nothing; a ready head's hair rigid unless it moves, and moving, on the
head within 1 cm of its design at rest. `quality.mjs --only hair` (every character whose hair moves, every motion and
chain whole; ~45 min), each limit saying what looks right: at rest it sags from its design no more than 2 cm, leaves
its rest no more than 12 mm in 8 s, jitters no more than 1 mm a frame, its roots as deep under the scalp as designed
(3 mm); in every motion and in a strong wind: every point a number, every lock's length kept (1 %; ringlets 35 %), no
point faster than 10 m/s, shimmering no more than the head that carries it and 1 mm (Kimodo's run shakes the head so,
7 mm at the hair's tips; not in a strong wind, where tips flutter), the hair's surfaces no deeper in the body than at
rest (the 1 % deepest by 30 mm, more than 1 cm in it 2.5 % — where it is worst it lies inside the hair's own mass: the
far side of a wide mass over an arm, hair under a face on the floor; looked at), no lock's edges past twice their length
(2 %: crumpled in a roll, no wedge torn out) — hair pressed between the body and the floor not counted —, the inner layer
hidden where locks part (a quarter at most); walking at 20, 60 and 144 frames a second as at 30 (5 mm on the whole, 3 cm at most); long locks leaning in a
light wind 12–30°, in a strong one 45–75°. `quality.mjs --only heads`: a hairstyle on a head grown by a layer lies as
far off the skin's surface as at rest (5 mm).
Since stage 4: a moment of a figure whose clothes move is its simulation stepped from the clip's start (as hair's); every
dressed character (`clothes-*`, the ready heads in their outfits, the hair characters that start from them) in every
`each` moment, and cases for the wind (strong, light), the silhouette's strength (0, ½, 1), fabrics (chiffon, denim),
jump, dance, roll, bow, a hood looking round, hair over a blouse. `units.mjs`: every pattern cut on a body (its
points, triangles, what holds it on, the skin under it, drawn finer); garments refused where they are not (an unknown
pattern or key, a fabric missing its keys, a preset of another kind as a fabric or a shape); clothes over a base by id
(taken away, changed by a key, replaced whole, added; an outfit taken in); the silhouette (a bell's hem wider than the
dress's own, strength 0 pulling nothing, strength 1 hanging nearer its form); the step (the same moment again moves
nothing, a scrub back is a fresh start, `frame()` draws the cloth on the skin); the solids (a limb's own skin, the points
kept nearest, the cover hair lies over). `quality.mjs --only clothes` (every dressed character, every motion and chain
whole, a strong wind, a light wind walking; `--chars a,b` for some), each limit saying what looks right: at strength 1
hanging off its designed form no more than 1 cm on the whole; standing still it leaves where it settled no more than 12
mm in 8 s and moves no more than 2 mm a frame (a pixel of a figure shown whole); no point not a number, none faster than
15 m/s from frame to frame; the cloth in the body — the 1 % deepest 35 mm (pinched in a fold of a heavy body bowing or
sitting), more than 1 cm in 3 % —, edges past 1.5× their cut 7 % (cloth under a rolling body drawn out over it; no tear
seen); walking at 20, 60 and 144 frames a second as at 30 (15 mm on the whole, 15 cm for the 1 % farthest: a fold or a
hem's swing a little earlier or later, looked at side by side);
across a loop it moves on the body no more than three of the next frames do (or 3 cm); a scrub back is a fresh start.
The time a frame of each dressed character's step takes is printed.
`pictures.mjs --jobs jobs.json outdir` makes pictures of any moments (`focus` on a joint for a close-up).

## Adding things

- *A body*: write a pack with `format: engine/body` on an existing topology (`tools/bodies_moood.py: body_file`), or a
  new topology beside it; joints from Anny's regression if it is Anny's mesh (`tools/bodies_anny.py: Regression`).
- *A body from Anny's settings*: a line in `data/anny/specs.json`, `python3 engine/tools/bodies_new.py <id>`, then
  `node engine/tools/characters.mjs bodies`.
- *A deformer*: `register({kind, of: 'figure' | 'skin', params, defaults, field | rest, prepare?, turns?, restOnly?})`
  in a file of `src/deformers/` imported by its `index.js` — the schema of characters and presets takes it from there;
  `turns` if as a pose layer it is a change of the pose; a case for it in `check/units.mjs` (strength 0 leaves the
  body), in `check/cases.json`, and its presets in `check/quality.mjs`' lists if it is a layer.
- *A preset*: `presets/<id>.json` with its label and about in both languages, then `node engine/tools/characters.mjs
  presets` (checks it, pins what it takes, writes the index); a character takes it by its pin.
- *Pictures of bodies*: a sheet in `tools/sheets/bodies.json`, `node engine/tools/sheets.mjs
  engine/tools/sheets/bodies.json <name>`.
- *A rig not from Anny*: `makeRig({skeleton, joints, frames, floor})` and its meshes (`makeMesh`), then
  `new Figure({rig, meshes, layers, floor})`.
- *A mesh on a character*: `E.figure(id, {meshes: [{mesh, name}]})` or `figure.addMesh(mesh)`; `floor: false` for one
  that must not lift the figure (hair, simulated cloth).
- *A simulation*: `figure.addSimulation({step({pose, previous, dt, reset, jump, t, solids})})`, driven by `figure.step`;
  it meets the body through `figure.solids()` — moments it keeps itself (`S.moment(u)` at each of its small steps), the
  skin's distance, normal and velocity there (`S.skin(m, x, y, z, out)`), the head's shape in its rest space (`S.head`),
  the Head joint (`S.carrier(m)`): read only, so clothes and hair read it at once.
- *A motion*: order it in the moood studio (`make_motion`; `after` to go on from another), keep its ask (`motion(key)`)
  in `data/kimodo/asks.json` and its body data (`motion(key, data: "body")`) as `data/kimodo/<key>.json`, add a line
  to `tools/motions.py` and run it. A chain: a line in `CHAINS` with its joins, then `node
  engine/tools/characters.mjs chains` (pins its motions; refuses motions that don't join).
- *A character*: `characters/<id>.json` (with its body — or the character it starts from, `base` — pinned: `node
  engine/tools/characters.mjs pin <id>`), listed in
  `characters/index.json`; then `node engine/check/numbers.mjs --update --only <id>` and `pictures.mjs --update
  --only <id>` after looking at its pictures.
- *A head*: a head preset (`presets/<id>.json`, group `head`, `head: {form, features, expressions, pieces, light, size,
  skin, ref}`), or a character's own `head` starting from one (`head.preset`) — then `node engine/tools/characters.mjs
  presets` and `pin <id>`. Our heads from the experiments: `node engine/tools/heads.mjs`, then the same. Look at it
  from the front, three-quarter and side, in motion and in its expressions; check it against its picture with `node
  engine/tools/overlay.mjs outdir <character> [--fit]`. A way of the head's form: a deformer registered in a file of
  `src/head/` (or `src/deformers/`) and its strength-0 case in `check/units.mjs`. Anny's face changes again:
  `python3 engine/tools/face_targets.py` (needs Anny and torch). Pictures: `node engine/tools/sheets.mjs
  engine/tools/sheets/heads.json [names]`. After presets or bodies change, `characters.mjs cases` pins the cases anew.
- *A hairstyle*: a style in `src/hair/styles.js` (its parts, its items in named groups, В1's helpers), a preset
  `presets/hair-<id>.json` (`pieces: [{id: "hair", kind: "style", style, physics}]`), then `node engine/tools/characters.mjs
  presets` and `hair` (builds and stores it). A head takes it among its pieces (`{kind: "preset", id}`: it takes the place
  of the head's own piece `hair`); changed by its id: `{id: "hair", off: ["fringe"], color, physics: {hold: 2}, moves}`.
  A ready head's hair moves with `{id: "hair", moves: true}`. Look at it from the front, ¾, side, at rest, in motion and
  in the wind (`?hair`, `tools/sheets/hair.json`). A wind: a preset of group wind (`wind: {speed, dir, gust, turbulence}`).
- *Clothes*: a garment in a character's `clothes` (`{kind: "garment", pattern, fabric: "fabric-…", color, shape?:
  "shape-…", strength?}`), an outfit (a preset of group outfit: `clothes: [garment…]`), a fabric (`presets/fabric-<id>.json`,
  `fabric: {density, stretch, bend, …}`), a silhouette (`presets/shape-<id>.json`, `shape: {…}` — О1's keys), then `node
  engine/tools/characters.mjs presets` and `pin`. A pattern: a line in `src/cloth/patterns.js` PATTERNS and how it is cut
  (`MADE`), or a MakeHuman garment added to `tools/garments.mjs` and run. Look at it from the front, ¾, side, at rest, in
  motion (sitting, lying, rolling too) and in the wind (`?clothes`, `tools/sheets/clothes.json`); against О1 and О3:
  `node engine/tools/clothes-o.mjs engine/tools/sheets/clothes-o.json`.
- *A change of the format*: `VERSION` up in `src/character.js`, its schema, and a step in `upgrade`.
- **Before and after changing the engine**: `node engine/check/units.mjs`, `quality.mjs`, `numbers.mjs`, `pictures.mjs`. A
  difference is either a bug or a change meant — then look at the new pictures and store them with `--update`.

## Not done yet

Bodies (stage 1): the pictogram's crotch creases where its legs spread far (sitting with knees wide): the skin between
the hip balls stretches over a short way. With an arm raised to the side the shoulder of every body reads boxy: Kimodo's
collarbone already rises with the arm, so it is the skinning of Anny's weights at the shoulder; making it round needs
corrective shapes driven by the arm's turn (none exist for Anny here), not something the weights or the seam fix give.
Anny's origin sliders differ in Anny herself by 2.5 % of the head's height on average (8 % at most) at the face and by
her height: the bodies carry that, no more. A layer of the form whose weight is animated changes the hip height the
path is scaled by, so where the figure is moves with it. The contour deformer keeps the body's small forms unless `own`
< 1; Т7's look also needs its smoothing and proportions (the full presets combine them).

Heads (stage 2): Anny's mouth is closed skin, so an open jaw stretches the skin between the lips into a dark membrane
(painted as the mouth's inside), no teeth or tongue; eyes are painted (or a relief), not eyeballs under cut lids (Г2
cut lids along mesh edges in Python — not carried: a cut changes the topology every body shares). moood's face differs
from Anny's in kind — its eyes are closed slits, its nostrils and lips softer — so Anny's changes of the eye's opening
and the nostrils act on forms moood's mesh hasn't: they read rougher there (the slit's sub-millimetre edges pulled open),
whatever map carries them. Г2's solids come over wrapped Г3's way and read rougher than Г2's own build (a crease at the
throat, the face rougher): Г2's heads are not ready heads here, only Giulia's solid as a way of the form. Г1's hair is
carried as rigid pieces on the head (it goes through the shoulders in big motions; hair is stage 3); headwear (hoods,
hats) is a coarse shell on the head that goes through the shoulders in motion and follows a bigger head only roughly —
the clothes' stage makes garments of it (stage 4), and no clothes are carried (the outfits and Г1's turtleneck). A piece
is carried as one (by the affine change of the skin under it): it can't follow the head's own unevenness — a bigger
head grows its cranium more than its face, a piece's far side lags by a few millimetres. The old man's nape and jowls
keep the ledge his Г3 form has (his cranium over a thick neck, jowls over it). A drawn mouth is set on where its lips
part after the wrap's easing (up to ~5 mm from its design on the long-nosed man). On Anny's own head, lips as volume don't open well:
her mouth is closed skin, and an open jaw parts the two reliefs over a square gap of stretched, painted skin that reads
as a hole with a tongue — the two plain heads with lips as volume (`head-points`, `head-anny-age`) take no open mouth
(`{kind: "off", name: "open"}`); a painted mouth on her head opens as a small dark mouth. Expressions are one at a time
(blending them, mouth shapes for speech, a gaze that follows: not now); a closing eye is drawn graded by its weight, a
smile's happy eyes switch at half. Toon light on a head without a designed form (Anny's own, deformed) shows the mesh's
small forms as hard tones.

Hair (stage 3): В1's hairstyles keep their design — their big flat pieces are how they were drawn; the light changed.
On a toon-lit head В1's hair keeps its own light (no toon light for it yet). In the A-pose rest long hair lies on the
raised arms. A long lock bent sideways in its own plane (over a shoulder, in a roll) stretches its outer edge: a lock
is a sheet carried by its chain's frames, which bend it as a rope would (a kink limit on the chains was tried: it fought
the solids under a rolling body and flung the hair). The inner layer is hidden where it parts, not kept whole. Г3's
ribbons part at their tips where they lie spread on the back (tapered ribbons with nothing under them, as drawn). Г1's
and Г3's hair on a head grown by a layer is carried by the affine change of the skin under it (fitted anew only for
В1's hairstyles), and a designed head's collision shape does not grow with a layer. A ponytail keeps its designed arc
near the root when the head bows. A frame of one figure with hair costs 18–30 ms in node (the skin between the frames
asked at every small step, the surfaces' binding); a figure with hair is made in 3–7 s (its groom); several characters
at once are the later task. Characters not from Anny (П1, П2) have no hair yet (their heads are the next stage's).

Clothes (stage 4): the cloth is simulated as cut — MakeHuman's garments with points 2–3 cm apart (drawn finer), so
folds are that coarse and small ones (a sleeve's wrinkles at the elbow) are not there; a knee or an elbow pressing hard
into tight cloth can stand out between its points for a moment (a high knee in a run under a bell held stiff). A
garment meets the ones under it only where they lay together as dressed; layers are as cut (a jacket over a T-shirt,
a top over trousers), not buttons or pockets. Cloth lies on the fingers as on a mitten (it is not pushed between them)
and is not carried by the hand. The hood is cloth round the head and over its rigid hair, which it does not meet; hair
lies over the clothes but clothes don't feel the hair. О1's ladder down to the sign is not carried (the pictogram Т4
has the sign); О1's "the form recomputed round the axes each frame" is not either (the cloth is the form's rest).
Standing still, most cloth keeps within a millimetre or two a frame, but not all: the heavy man's sweater and trousers
(between his thighs, which touch: no room; on his back, where the cloth stands about 3 cm off the skin) tremble by
1–3 cm, an oversized
sweater standing off the body and a trouser hem at the ankle (over a rigid boot the cloth does not meet) by up to 9 mm
at a few points. Hair lying over clothes is not right yet: over a dress (Г3's red-haired girl, Г1's Alva, Ariel) it
shimmers by 1–3 mm a frame in motion and up to 13 mm standing, where a lock goes under the dress's edge and out again;
over a blouse (clothes-hair) by 5–8 mm jumping, dancing, sitting, with locks drawn out past twice their length (3 %);
the hair's own checks fail on these four characters (all hair without clothes passes them). Gloves, belts, buttons and openings that close are not made. A frame of a dressed figure costs 24–126 ms in node:
several characters at once (the GPU) are the later task.

Hands and fingers are carried (all 77 joints) but not checked closely; feet are set on the floor only as a whole
(no foot contacts); the arm can press into the chest's side at the armpit when it hangs close (Anny's weights;
`armsOff` is for it); skinning is on the CPU (fast enough for a few figures; on the GPU when many are needed);
the collision shape is capsules only (no distance field); the rest stands at the body's own origin, so switching from
rest to a motion still jumps by where that motion's frame 0 puts the pelvis (a few centimetres; each motion differs).
