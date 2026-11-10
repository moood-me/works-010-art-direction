# 2026-11-03 — the engine's foundation after its review

**What called for it.** An independent review of stage 0 ([reviews/2026-11-03-engine-stage0.md](../reviews/2026-11-03-engine-stage0.md))
found the only chain not seamless and resting on a reconstruction, versioning that protected only top-level defaults,
a floor counting invisible vertices, a coarse picture check with gaps, a foundation missing what the next stages need
(pose layers, a rig apart from meshes, state for simulations, a collision shape, morphs, large meshes), slow skinning,
a hard-coded camera target. The coordinator asked to fix every finding the right way before the next stages build on
it. On versioning Pavel said, during the work: don't overdo it — not a versioned pipeline of behaviours (that would be
versioning the whole engine); characters as plain validated data, pins of the body and motion files they use, a
simple format version with an upgrade step, and the numeric and picture checks to notice when an engine change alters
characters, then decide. A versioned pipeline had been started and was taken out.

**What was done** (all in [engine/](../../engine/README.md); the README has the architecture, formats, how to add):
- *The chain lie → rollover.* Rollover's own data fetched from the studio (`motion(7a4c19b1…, data: "body")`, kept in
  `engine/data/kimodo/`): the reconstruction had been right within a unit of rounding; the flick at frames 180–182
  (the right foot turns 55°, vertices 48–82 mm a frame) is Kimodo's own. Every motion now keeps its whole ask
  (`motion(key)`: prompts, seconds, heading, transition_frames, seed, steps, cfg, constraints, after; `data/kimodo/asks.json`)
  — motion format 2. `clipOf` measures where the next motion stands and which way it faces from the shared frames
  (a turn about the vertical and a move), checks it against the studio's `startsAt`, refuses motions whose first frames
  are not the other's last. Joins say their treatment (`cut`, or `dead`: dead blending, Holden 2023); inertialization
  (Bollo 2016) was tried first and removed the step at 180 but not Kimodo's fast frames after it. lie → rollover:
  dead blend over 12 frames, at most 25 mm a frame (the rollover's own median), picture
  [join.png](../pictures/engine/join.png). Chains pin their motions by content hash.
- *Characters as data.* A schema (`src/schema.js`, `src/character.js`): unknown keys and values refused, with where;
  the body pinned by content hash (`moood-woman@271c4699…`; SHA-256 of canonical JSON and bytes, `src/hash.js`);
  defaults kept in one place; format version 2 and `upgrade` from stage 0's version 1 (`engine/tools/characters.mjs
  upgrade | pin | chains`); the ten presets upgraded.
- *The floor* is its own step after every mesh is drawn, over the vertices triangles use, its shift exposed
  (`pose.shift`); stage 0's bodies stood up to 7 mm high on invisible vertices (now measured: 1.5–7 mm lower).
- *The checks.* `check/numbers.mjs` — 85 cases (90 with the new chain) (every preset in six moments, and moments that exercise DQS, LBS,
  sigma, the collarbone's share, the seam, each correction, a turn as a layer and as a rest change kept and turned,
  a morph both ways, the pelvis floor, placement and heading, the join frame by frame, prone), joints and every 4th
  used vertex of every mesh, in node, tolerance 0.05 mm, naming data that changed; doubling sigma moves 68 of 85.
  `check/pictures.mjs` + `render.html` — 62 pictures (64) framed by the figure's bounds (400 × 400, wide for lying), by
  their own page, not the viewer. `check/units.mjs` — 12 contracts. Each fails with no cases or a wrong `--only`.
  three.js 0.160.0 kept in `engine/vendor/three`.
- *The foundation for the next stages.* A rig (`src/rig.js`) apart from meshes (`src/mesh.js`: skinned with any number
  of influences, rigid, procedural rebuilt each frame); a figure carries several meshes off one pose and one floor
  shift; pose layers in order (`src/layers.js`: the corrections, the collarbone's share, a joint turn, a morph, and a
  character's code); the same changes on the rest (`src/changes.js`) with an explicit `frames: 'keep'` (design) or
  `'turn'` (anatomy; the frame turning of `bodies_anny.py` now also in JS); `frame(clip, t, pose)` writes into the
  pose it is given; `step(clip, t)` keeps the previous pose, the time step and resets (loop, scrub, new clip) and runs
  simulations; tapered capsules per bone as the body to collide with (`src/collision.js`); morphs before skinning
  (moood's `facePlain` read as `plainFace`); 32-bit triangles beyond 65,536 vertices.
- *Performance.* Neighbours, centres and the seam's mask computed once per mesh and kept (a second figure of a body:
  under 1 ms, was 236 ms); only used vertices skinned; loops without allocation — CoR 2.2 → 0.75 ms a frame in node.
  Lights and the shadow fitted each frame to the box around every figure.
- *The viewer* (Д1): several figures side by side, the camera framed by their box (no `floor + 0.52 × height`),
  capsules shown on demand; local three.js. Pictures: [viewer-several.png](../pictures/engine/viewer-several.png),
  [capsules.png](../pictures/engine/capsules.png).
- *Minor:* the missing `src/chain.js` reference, the dead `rbf[0] = rbf[1]` in `bodies_anny.py`, `pack.py` choosing
  uint32 indices for big meshes. The rest now stands at the body's own origin (not with the pelvis moved over it): the
  rest → motion jump is each motion's own frame 0 and stays, a few centimetres.

**How, to repeat it.** Stage 0's outputs were recorded with the old code first (eight cases, every option), and the
new engine compared with them: the same within 0.25 mm apart from what was meant (the floor; the rest's origin).
Measuring the join: max vertex movement per frame around it, cut against blends of 8, 12, 16 frames (12 kept).
Pictures with `node engine/check/pictures.mjs --jobs jobs.json outdir` (close-ups with `focus`), the viewer with
headless Chromium (software WebGL). Checks: `node engine/check/units.mjs`, `numbers.mjs`, `pictures.mjs`.

*A chain to test joins.* walk → stop → look around → turn back, ordered from the studio (`make_motion` with `after`, each
on the one before; the first try failed: the GPU did not wake in 25 minutes; the second made all three in a minute).
Its joins have no flick in Kimodo's own frames (at most what a walking step moves) and stay `cut`; the turn back is
measured from the shared frames and she walks back along her own path. In the viewer and in the checks (5 cases).

**Seen and left.** Skinning stays on the CPU; the collision shape
is capsules only (no distance field); hands, fingers and foot contacts as before.
