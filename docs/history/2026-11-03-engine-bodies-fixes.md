# 2026-11-03 — the engine, stage 1 (bodies): fixing what the review found

**What called for it.** The review of stage 1 ([reviews/2026-11-03-engine-bodies.md](../reviews/2026-11-03-engine-bodies.md))
found thirteen things, most important first: the pictogram broken at rest and in every motion; figure deformers as pose
layers changing limb lengths and making planted feet slide; smoothing folding the toes and anatomy the fingers;
corners, lumps and kinks in silhouettes and limbs; boxy shoulders with the arms raised and hands into the thighs; rest
and layer anchored differently; layers not in the written order; per-vertex allocations and fields rebuilt every frame;
hard-coded metres; duplicated helpers; checks that see change but not quality; positional silhouette keys, full
presets not usable as parts, a viewer panel cut off with three figures, "Тело" and "Основа" read as the same; heavy and
the origins barely different. The task (from the lead agent, for Pavel): fix each the right way, no workarounds, keep
the checks, look with our own eyes, don't deliver anything worse; Pavel's requirements rule ([requirements.md](../requirements.md):
real sizes of body parts, no broken arms; motion from Kimodo, corrections on top allowed; presets of parts matter).

**What was decided, and how** (the engine's README has the whole of it, [engine/README.md](../../engine/README.md)):
- *Pose layers* (findings 2, 6, 7). A field over the posed figure can't keep bones: a field made for the rest's
  heights meets a raised forearm at the wrong height. So no field is evaluated over the posed figure any more. A
  deformer as a layer is one of two: a change of the pose — the line of action and contrapposto as turns of the pelvis
  and the spine chain (each bone by the curve's slope at its middle), the legs put back on their feet by two-bone IK on
  the rest's lengths, the pelvis lowered only as far as a leg needs to reach; or a change of the form — its rest change
  weighed in each frame (vertices, centres of rotation and the joints' rest places, carried through skinning, the
  pelvis's path scaled by that rest's hip height, as for the rest change). What the engine promises (finding 6): the
  pelvis on Kimodo's path scaled by the hip height of the rest it moves (layers of the form included); the feet where
  that path and the body's legs put them; a layer of the pose leaves both. All layers in one list, run in the order
  written (the figure's "mesh layers" stage is gone, so finding 7's joint places without turns is gone with it).
- *The pictogram* (1). A rest change may now carry its own skin weights (`withRest({skin})`); the sign gives them from
  its own pieces: a stick per bone, balls at the shoulders, elbows, hips, knees and ankles, a bar across the shoulders
  and one across the hips (so a limb's ball always has the trunk right beside it), a hand's ball a little past the
  wrist, a rounded foot as long and as high as the foot's own skin (a foot shaped from the joints was taller than the
  toes, and the front of it got no skin — a flat cut face), the trunk's bottom no lower than the hips' bar (below it the
  skin between the thighs became a web in a raised leg). Weights: a stick its bone, a ball both bones across it (a ball
  turned about its centre stays the ball), the hand's ball the hand, the head's the head, the trunk Anny's trunk
  weights; between trunk and limb by which piece the settled point lies on, over a seam 1.6 stick-radii wide (0.4 left
  thin webs under a raised arm). Tried and dropped: relaxing the hands' and feet's skin on the surface (it pulled the
  toes back and made the front flat again), melting them first by smoothing (more folds). In motion its edges now
  stretch less than the plain man's (sitting: 99.9 % of edges within 2.2× of their rest against his 2.5×; at worst, against
  the longer of their length on the body and on the sign, within his ×1.2), against 9–11× before.
- *Folds* (3). Smoothing keeps the toes (and fingers) by default; anatomy moves no farther than a third of the local
  edge; any rest change (but the sign) that would still turn a triangle over has its move smoothed over the surface
  there until none is (`regions.js: unfold`: first tried as taking the move back, which made a short neck fold six
  hundred triangles — the head goes down, the neck's skin stayed); proportions smooth their move only where two parts
  meet (smoothing inside a finger spoiled its similarity).
- *Limbs and silhouettes* (4). Taper from nothing at the root to the most at the wrist and ankle, back to nothing over
  the hand and foot (no shoulder lump, no pin wrist); straight against curved as a smooth section (the crease where its
  two sides met is gone); a point near a joint goes by both bones across it smoothly. The silhouette's legs ride with
  their root and grow thinner or thicker about their own line (the egg's step at body–thighs came from shearing the
  thighs' tops by the torso's profile); arms turn out about their own axis. Long neck: same girth, 1.45 long; broad
  shoulders: collarbones 1.25 with Т7's shoulder cap and slope (1.4 alone made a square corner and a notch).
- *Hands into thighs* (5): `armsOff` takes `clear` — after its degrees, a forearm or hand nearer the hips or thighs
  (their capsules) than that is turned out further. The pear old woman's hands no longer go into her hips. *Boxy
  shoulders with the arms raised*: measured — Kimodo's collarbone already rises 40–50° with the arms up; the square
  shoulder at a horizontal arm is the skinning of Anny's weights, and neither the seam fix nor more of it changes it.
  Rounding it needs corrective shapes driven by the arm's turn, which Anny doesn't have here: not done, said in the
  README.
- *Caricature* about the hips, the neck grown along the torso, the sign's sizes and tolerances in shares of the height,
  the masses' search and the contour's empty bins in the body's own sizes (9); `keepUnused`, `smin`, normals and vector
  helpers each once (10); no per-vertex allocations, fields made once, a layer's rest change cached by what it depends
  on (8: a layer of the form costs 0.05–0.2 ms a frame instead of 2–3).
- *Quality checks* (11): `check/quality.mjs` — contracts with limits: no triangle turned over by any preset on five
  bodies (a few allowed only where a change presses skin into itself on a body with no room — a reed's hips into a
  heavy man's thighs, a baby's difference from adults drawn out); edges of every full preset at rest and in five motions
  no more stretched than the plain body's (×1.2); pose layers keeping bones (to 0.01 mm) and feet (to 1 mm); the lowest
  point on the floor; layers that don't commute differ in two orders; a layer of the form equal to its rest change; a
  weight from a code layer.
- *Presets and viewer* (12): silhouette keys named `{at, width, depth, forward}` (preset format 2, upgraded by
  `tools/characters.mjs presets`); a character may start from another (`base`, pinned by content: a full preset as a
  part, character format 3, upgraded by `tools/characters.mjs upgrade`); the viewer's panel folds skinning and layers
  away under `?bodies` and stays whole with three figures at 850 px; "Персонаж" and "Тело-основа" instead of "Тело" and
  "Основа".
- *Bodies* (13): heavy is Anny's weight 1.2 with her own fat sliders (arms, legs, neck, head, waist, hips, belly); her
  weight alone stays mild past its range (measured: at 1.7 the waist only 10 % deeper than at 0). The origins: measured
  in Anny herself, her three origin sliders differ by 2.5 % of the head's height on average at the face (8 % at most)
  and by height; the bodies carry that — more would be features she doesn't give, so it was left.

**How, to repeat it.** `node engine/check/units.mjs`, `quality.mjs` (`--print` shows every measure), `numbers.mjs`,
`pictures.mjs`. Stored numbers and pictures were updated for the cases that have a deformer (64 numbers, 51 pictures);
the plain characters didn't move. Pictures: `node engine/tools/sheets.mjs engine/tools/sheets/bodies.json` →
[pictures/engine/bodies](../pictures/engine/bodies/). Bodies: `python3 engine/tools/bodies_new.py anny-f-heavy
anny-m-heavy`, `node engine/tools/characters.mjs bodies`. Looked at front, side and three-quarter, at rest and in walk,
run, sit, lie, jump and dance, close-ups at the shoulders, hips, hands and feet.

**Seen and left.** The pictogram's crotch creases when its knees spread wide sitting. Shoulders read square with an arm
raised to the side (above). A layer of the form whose weight a code layer animates rescales the path by the changing
hip height.
