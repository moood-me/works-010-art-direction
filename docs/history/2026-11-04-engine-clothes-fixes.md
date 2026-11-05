# 2026-11-04 — the engine, stage 4: clothes after the review

**What called for it.** The independent review of stage 4 (docs/reviews/2026-11-04-engine-clothes.md, twelve findings):
bodies came out through the clothes in ordinary motions, worse than О3 with the same garments; the checks could not see
it; cloth trembled standing; hair over clothes shimmered; formed dresses stood as rigid domes lying; the solver was not
XPBD where it said so and kept workarounds; skin moments, hashes and step loops were made twice; constants were
hard-coded; the docs understated it. The lead agent set the task: fix every finding the right way, with checks that would
have caught them, on every character. Pavel then narrowed it (binding): on the borderline items aim no better than the
experiments did — bodies through clothes in rolls, lying and sitting at О3's level at the same moments with the same
garments (bring back what О3 had: its pinch memory and the own limb); what О3 itself leaves (a deeply bent knee through
the cloth for a few frames, trousers ridden up kneeling, a T-shirt ridden up after a roll) is acceptable, and the checks
must not ask for more; formed dresses lying only what is simple and clearly right; no new workarounds, old ones removed
only where that is realistic; and then: finish soon, don't widen it, don't start what would need complex testing. The
ways below were decided by me within that.

**What was done, finding by finding** (engine/README.md, Clothes, has how it works now).
1. *Bodies through clothes* — О3's two rules carried: the pinch memory (`S.kept`: when the skin found anew faces away
   from the skin a point lay by, and it is still within its thickness of that one, it keeps that one and is left where it
   is until the skin is looked for again) and the own limb for every point of a sleeve or a trouser leg, the hip band's
   too (each on the limb its nearest skin point was dressed; pushed out of its own limb too, and a tube's triangle's middle out of its own limb's skin). The jeans in the forward
   roll now stand up with both legs in the trousers (the tube check: 44 % of the rings off at the roll's end before, 0
   now), shins no longer come through sitting. A knee folded tight still shows through the cloth for some frames of the
   roll (52–64), as О3's does. Tried and dropped: the skin's points kept under the cloth's triangles (every skin point a
   garment covers followed to its nearest cloth and held behind it — beyond what О3 did; at the trousers' hems over the
   feet it pushed the cloth centimetres a small step).
2. *The checks* (`check/through.mjs`, used by `quality.mjs --only clothes`): measured on the drawn meshes, exactly — the
   cloth inside the body at any depth (the nearest skin triangle's angle-weighted pseudo-normal: no band it can't see),
   the body through the cloth (skin with cloth inside the body behind it, along its normal, so between the cloth's
   points too), the skin a garment covers at rest left bare, layers out of order, each ring of a sleeve or trouser leg
   still winding round its bone. The floor is not skipped; the loop's limit is 30 mm; the speed is measured with no cap
   in the cloth. Each limit says why, set by looking, at О3's level in rolls.
3. *Standing tremble* — its causes: the triangle's middle met over both legs' skin at the crotch (now only on a sleeve,
   a trouser leg or what hangs, and only where its three corners lie on one limb, their own, a tube's out of its own limb's
   skin); the capsules standing out
   of the skin with the hard 3 cm switch (dropped: the skin is asked at any depth, as far as a reader asks); bending
   toward flat (now toward the angle each hinge had as put on); the pinch's alternate small steps (a pinched point now
   stays pinched until the skin is looked for anew); a stiff hood's shell let go where it touched the head and drawn off
   it again (what hangs alone lets go where it lies). The heavy man 26 mm a frame → 9 (his touching thighs still move the trousers' crotch); the hood 0.2.
4. *Hair shimmer over clothes* — the cover is the cloth's own now (`S.lieOn`, `S.over`): the outermost garment's
   surface where it is at that small step (the planes of its nearest points, not mixed with the garments under it),
   past its open edge as far as from the edge, and hair allowed as near as it lay over it at rest.
5. *Formed dresses lying, rolling, bowing, sitting* — the simple and clearly right part: what hangs lets go of its form
   as the hips leave upright (wholly to 20°, none from 70°) and where it lies on the body or the floor (it drapes over
   the knees sitting).
7. *Solver* — XPBD with each constraint's λ gathered over the small step's passes (lengths, bending), tethers as XPBD
   constraints as stiff as a strip of the cloth; held points pulled as a spring per unit of mass (XPBD's share in its one
   pass, as the form's); the 12 m/s speed cap and the pressed-on-floor rule dropped, and the check no longer skips points
   near the floor. Left, written down: the held points' weight taken off (HELD_MASS) — with their true masses an old
   man's trousers slid off his hips walking. Tried and dropped: the hold as an XPBD constraint carrying the garment's
   weight with 2 mm of give (soft for a light hood, it trembled).
8, 11. *Shared, and the cost* — the figure's step goes through its small steps once for all its simulations (hair and
   cloth: `sim.begin`, `sim.substep`, `sim.end`), each small step at one moment of the solids made once for all; one
   cell hash (`src/cells.js`) for the skin, cloth against itself and under another, a garment laid on the body; no
   arrays made in the step. Hair and cloth keep their own contact rules (hair's friction a share of its slide, cloth's
   Coulomb's): not the same, so not merged. Several characters: each figure has its own solids, cloth and cover.
9. *Constants* — the hold's time, the speed cap, the pressed rule, the held mass, the tethers' share, the near-skin rule
   of the form are gone; the strength's range is 0–2 (README said 0–1); the quality check reads the garment's strength;
   the skin drawn sunk under close cloth follows where the cloth is now (`sim.sink`), not where it was at rest.
12. *Docs* — README, the gallery's Д11–Д13 and this note say what is so now, and what is not right.

**Left open, and why.**
- 6 (by eye): the V hero's toes through the rigid boots, granny's pleats spiking, the scarf a stiff strip, torn cloth's
  dark inside — not started (each its own cause, each would need its own testing).
- 9: per-garment holds (a hem or belt hold for trousers), a tight fit per garment — not started.
- 10: cloth over cloth stays one way, by the masks of where garments lay together at rest; folds from compression not
  made.
- An oversized top's loose sleeves slip off the arms in a run (as before; seen by the new tube check).
- What the checks still break is listed under *Checks* below.

**Checks** (all on the final code). `units.mjs`: 35 of 35 hold. `quality.mjs --only clothes` (all 24 dressed
characters, every motion and chain whole, two winds): 4642 of 4993 hold, 351 broken — what the new exact checks see,
most of it there before them too (the old check called the jeans' roll "0.000 mm in the body"): the body through the
cloth at a motion's end (131) and at most of its moments (83) — knees and shins through trousers lying, rolling sideways
and over, sitting (a few % of the covered skin); trouser legs and sleeves off their limbs at a motion's end (35) — an
oversized top's sleeves in a run, legs in the side roll and the roll over; covered skin left bare past О3's 35 % (31) —
short dresses and T-shirts ridden up lying and rolling; a pop across the walk's loop (23 — the loop's limit is now
against the frame before, and in mm: it was 3× the next frame's); layers out of order (9); standing jitter (4: the hood
12.7 mm, the heavy man 8.8, the V hero 5.5, the oversized top 4.4); granny's pleats 17–29 mm in the body (5); two flicks
just past 12 m/s. The jeans' forward roll (the review's first case) holds every check but the end's through (knees).
`quality.mjs` skin, bones, feet, order, heads, hair: see the report of this stage (hair over clothes: the dress's
shimmer 16.4 → 2.8 mm a frame standing, but its locks now slide 7 cm in 8 s over the arm — not right). `numbers.mjs`,
`pictures.mjs`: stored anew only for the cases the clothes moved — the dressed characters (`clothes-*`), the heads in
their outfits and the hair on them (`head-*`, `hair-g1-alva`, `hair-g3-red`, `hair-red-ariel`), and four hair
characters without clothes whose hair's rest is found a little differently without the capsules (`hair-alva`,
`hair-jack` — a stray strand on the crown smaller —, `hair-kpony`, `hair-marco`, looked at); nothing else moved. A
frame of a dressed figure's whole step: 27–112 ms in node.

**How, to repeat it.** `node engine/check/units.mjs`; `node engine/check/quality.mjs` (`--only clothes --chars a,b` to
split it); `node engine/check/numbers.mjs`, `node engine/check/pictures.mjs`; pictures: `node engine/tools/sheets.mjs
engine/tools/sheets/clothes.json`, `node engine/tools/clothes-o.mjs engine/tools/sheets/clothes-o.json`, `node
engine/tools/gif.mjs engine/tools/sheets/gifs.json`.
