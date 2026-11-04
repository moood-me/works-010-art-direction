# 2026-11-04 — the engine, stage 3: hair

**What called for it.** The plan's stage 3 (hair), as the lead agent passed it on. Pavel on В1 (experiments/hair): «все
пластилиновые! улучшай», and on hair in motion «да. use best practices»; the requirement «Hair moves with inertia, wind
and motion»; the agreed «Hair В1 is one path; on designed heads (Г1, Г3) and on characters not from Anny (П1, П2) it
hasn't been tried» and «Collision with the body shared by clothes and hair». The task: hair as an engine part (В1's
builders and styles as code and presets of parts: style, locks, colour and shading, physics — browsable, combinable,
changed by base, merge, off, strength), on every head the engine has (plain Anny heads, the ready heads Г1/Г3 — their
rigid hair offered moving, keeping its look at rest), fitted to the head's real form; in motion on the stateful step, in
every Kimodo motion and chain, wind presets, collision with the head (with its jaw), neck, body and shoulders — one
collision the body offers; rest kept; not plasticine; checks with limits; gallery Д8–Д10 with a 3D view; docs, pictures.
Not now (agreed): speed for several characters; fingers, contacts, breathing.

**What was done** (the engine's README has how it works now: Hair, the solids, formats, checks).
- *В1 as code* (`engine/src/hair/build.js`, `styles.js`): В1's builders carried as they were, its 14 hairstyles with
  their items in named groups (`cap`, `fringe`, `back`, `sides`, `under`, `tail`, `braid`, `buns`, `hat`…), the guides and
  each surface's binding to them moved from В1's motion.js into the build (in the design space). A build takes 4–16 s,
  so builds are stored (`data/hair/`, quantized: 45 MB for 14; `tools/characters.mjs hair`), keyed by `HEAD_BUILD.hair`.
- *Hair as a piece* (`src/hair/hair.js`, `src/head/pieces.js`): `{kind: "style", style, off, only, color, shading, moves,
  physics: {hold, bend, drag, wind}}` beside the head's other pieces, so the head's merge by id, `off` and the presets
  of parts work for it; presets `hair-v1-*` (group hair) and `wind-*` (a new preset content, `wind`). Formats: preset 5,
  character 6 (only versions changed in the old files). Г1's/Г3's hair pieces take `moves` and `physics`: their locks and
  their masses' clumps get guides of the same simulation.
- *Fitted to the head* (`src/hair/fit.js`): В1's ellipsoid carry, the ellipsoid fitted through the designed form where
  the head has one (rays onto the form), else its skin; offsets grow with the head; the real surface's difference from
  the ellipsoid added near the skull, so roots sit on the scalp.
- *In motion* (`src/hair/sim.js`): В1's simulation on the engine's step (small steps of 1/240 s at most, whatever the
  frame step); the step's frame leaves the hair's meshes to it (`figure.driven`), `frame()` alone draws them at rest.
- *The solids* (`src/solids.js`, `figure.solids()`): the head's shape with its jaw (baked into a grid), and the body's
  skin as the frame drew it (moving least squares over its points' normals). For clothes later too.
- *The look*: locks 0.6 of В1's depth; strand bundles with dark partings, a highlight broken by them, diffuse partly
  along the strands, light through the edges, an outline dark in the hair's own colour (`src/hair/shade.js`).
- *The viewer* `?hair` (hairstyle, moves, hold, wind, close-up), *the gallery* Д8–Д10 (В1's line says where it went),
  *characters* `hair-gwen`, `hair-alva`, `hair-kpony`, `hair-marco`, `hair-jack` (В1 on Anny's woman, child, man),
  `hair-red-ariel` (В1 on Г3's red-haired girl), `hair-g3-red`, `hair-g1-alva` (the ready heads' own hair, moving).

**Decided on the way, and why** (by me, said here; nothing of it asked of Pavel).
- *What made it plasticine*, looked at in В1's sheets and in the engine: thick lens-shaped locks with round rims (clay
  slabs, «pillows» at the back of the bob), strands finer than a pixel at a head's size (a lock read as one smooth
  body), a soft broad sheen, black outlines round every piece. Changed: the locks' depth (`THIN` 0.6 in build.js — all
  styles), bundles and the highlight in the shading, the outline's colour, no outline on the inner layer. Not changed:
  the hairstyles' own design (their big flat pieces are how they were drawn).
- *Collisions*. The engine's capsules first: round a collarbone a capsule stood over the shoulder like a shelf, long
  hair stood off it in flaps (В1 had the same flaps). Then each bone's skin baked and carried rigidly by its bone:
  neighbours disagree where the skin bends between them, and pushed points 2–3 cm in a small step (locks stretched 50–
  150 %, hair jittered at rest). Now the skin as drawn this frame; a lock's lengths are made last in a small step.
- *The rest*: В1's inverse groom (the design is how it hangs), then on the body first draped (bend eased) and then stiff
  — that is the rest; the bend keeps the free-hanging shape (with the draped one the Г1 locks flailed sideways in a walk,
  keeping a curve round a shoulder that had moved away). A reset (start, loop, scrub) settles in its own pose without
  speed (else a pose unlike the rest flung the hair at the first frame); a contact takes the push's speed away.
- *A stateless frame* draws the hair at rest on the head (the design); a moment with hair that moves is the simulation
  stepped from the start (`check/cases.mjs`), in the case's wind.

**Checks, as they stand.** `units.mjs` 29 hold. `quality.mjs --only hair` (8 characters × 19 motions and chains and a
strong wind; 712 contracts) holds with these limits: lengths 1 %, speed 20 m/s, no jitter past 1 mm a frame (measured
≤ 0.6), rest kept 12 mm in 8 s (≤ 9), sag 2 cm (≤ 3 mm), roots within 16 mm of the scalp (≤ 15), surfaces in the body
beyond their rest: 1 % deepest 20 mm, share past 1 cm 3 % — these two set from what the hair measures (9–18 mm,
up to 2.4 % in rolls, lying, jumps, stomps: the chains keep their points out, a lock's surface between them dips into
the skin where arms hang through long hair or a rolling body presses it; no collision of surfaces). `quality.mjs --only
heads` (now with the hair characters): 1 of 890 broken — `hair-gwen`'s inner layer on a head grown by a pose layer, 5.8
mm off the skin against the pieces' 5 mm (a hairstyle is carried as one piece by the affine change of the skin under
it; tried following the cranium only: 6.3). `numbers.mjs`: the 277 old cases as stored; the 56 new hair cases stored.
`pictures.mjs`: the 268 old pictures as stored; 48 new hair pictures stored (all looked at).

**Left open.** The A-pose rest lays long hair on the raised arms. В1's hair on a toon head keeps its own light. A
ponytail keeps its designed arc when the head bows (stiff near the root). Speed: 15–30 ms a frame of one figure with
hair in node (the later task with several characters). Characters not from Anny have no heads in the engine yet, so no
hair there.

**How, to repeat it.** `node engine/tools/characters.mjs presets && … upgrade && … pin && … cases && … hair`. Looked at:
every style on Anny's woman, man, child and on six designed heads front, ¾, side; the ready heads rigid against moving
at rest, looking round, walking; the motions; the wind; the viewer at 1280×850 and at phone width. Pictures: `node
engine/tools/sheets.mjs engine/tools/sheets/hair.json` (docs/pictures/engine/hair/). Checks: `node engine/check/units.mjs`,
`quality.mjs` (`--only hair`), `numbers.mjs`, `pictures.mjs`.
