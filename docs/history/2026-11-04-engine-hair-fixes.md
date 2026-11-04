# 2026-11-04 — the engine, stage 3: hair after the review

**What called for it.** The independent review of stage 3 (docs/reviews/2026-11-04-engine-hair.md, 14 findings), passed
on by the lead agent with notes: most important — nothing worse than В1 (experiments/hair) by eye, at rest and in
motion, where В1 looked better bring it back (Pavel called В1 «пластилиновые», improve it but never by making it worse),
compared side by side with В1's own page; one body collision, updated once a frame step, interpolated in the small steps,
read by many, with a deep inside test, made to be shared with clothes next; no pops at loops; checks measuring quality
over whole clips, their limits set from what looks right; the failing heads contract to pass by fixing its cause; the
leak and allocations fixed, several characters made possible later (the speed task itself later, no GPU path unless
small and right); the stored builds much smaller, no full copies added to git again. Decided by the lead agent's notes;
the ways below decided by me (nothing asked of Pavel).

**What was done, finding by finding** (the engine's README has how it works now: Hair, the solids, formats, checks).
1. *Surfaces stretched, unseen*: measured now on the drawn surfaces — the locks' edges torn past 2× (`quality.mjs`), the
   inner layer's stretch per point each frame (`output.parted`); where the inner layer is stretched past 1.8× it is
   hidden, its shadow too (`shade.js PARTED`: where locks part, what is under them shows, not a dark web). Binding the
   inner layer more smoothly was tried and was worse (×4 the edges past 1.5×: rigid frames of different chains blended
   pull a point far off both). The locks part less in the first place: hair against hair (below), and where a lock lay
   on the body at rest it is turned about itself to lie on it as it lay (flat on the back stays flat, not edge-on),
   that turn changing no faster than 12° a segment.
2. *Collision blind past 3 cm, the skin not between frames*: `src/solids.js` rewritten. The skin is kept at both ends of
   the frame and each small step asks it at its own moment (the positions in between, a hash of 3 cm cells built per
   moment); farther in than the skin's points reach, the bones' capsules (`src/capsules.js`, at the nearest tenth of the
   skin less 5 mm, so they stand out of the skin nowhere — at the median one stood 3 cm over the shoulder and made the
   flaps) say how deep and which way is out; the head's bones' capsules left out where the head is its designed form
   (they pushed Г3's and Г1's hair 3 cm off the scalp near the roots).
3. *Not ready to share*: the solids are updated once by `figure.step` before its simulations, then only read; a reader
   keeps its own moments (`S.moment(u)`), so any number of simulations read it at once. `figure.collider`, `headShape`,
   `neckShape` and `src/collision.js` are gone (folded into the solids; capsule fitting kept as `src/capsules.js` for the
   solids and the `armsOff` layer). Thickness: the answer is the skin itself, a reader keeps its own (hair: half a
   lock's depth; in the head's skin as deep as at rest — roots under the scalp — and, new, out of the body's skin
   however the design lay on the neutral head's small shoulders).
4. *Every loop popped*: `figure.step(clip, t, {loop: true})` carries on across the clip's end (the viewer's playing);
   the hair is moved with the head's jump and its velocity kept against the head's own motion. Reset only on a scrub or
   a new clip (its 60 small steps of settling stay there). Kimodo's clips are not cycles — across the end the arms jump
   29 cm against the head in a walk — so where the body jumps into the hair it is pushed out; on the whole the hair
   moves on the head a tenth of what starting afresh moves it (units).
5. *Checks measured less*: `quality.mjs --only hair` rewritten — every motion and chain whole; roots against each one's
   designed depth under the scalp; a shimmer measure (a point turning back and forth two frames running) against the
   head's own (Kimodo's run shakes the head 7 mm at the hair's tips: that is not the hair's); the surfaces' depth by the
   new solids, deep inside too; locks torn; the inner layer hidden; the frame rate; the wind's lean. Each limit says why.
   Two are set after looking where they are worst, close to what is measured there, and say so: the surfaces in the body
   (the 1 % deepest 30 mm, more than 1 cm in 2.5 % — Ariel face down, Г3 rolling, Ariel waving, Alva sneaking: it lies
   inside the hair's own mass, the far side of a wide mass over an arm, hair under a face on the floor; nothing seen
   through the skin) and locks' edges past 2× (2 % — crumpled in a roll, no wedge seen). Hair pressed between the body and
   the floor (within 2.5 cm of it) is not counted for depth, tears or shimmer: it has no room and is not seen. `units.mjs`: the solids, the loop, every stored style through the hash of
   the code they are built by.
6. *Wind*: the hair takes the wind three times as much as the air of its own motion (`sim.js WIND`) — light leans long
   hair 16–22°, strong 60–64°, as the presets say. Making the air stronger for both (drag ×4, ×8) was tried first: the
   wind came right, but running hair stood out in wings — the motion's air stays В1's.
7. *By eye*: the locks have В1's depth again (thinned to 0.6 they left gaps and dark cracks at the crown — Ariel, Gwen —
   and a ragged look; the plasticine is fought by the light, kept); the fit puts the hairline and the roots on the scalp
   as designed (kpony's ragged hairline was the skin standing through a cap fitted coarsely); Ariel is as wide and full
   as В1's (its square-cut lock is В1's own design: a top lock under the back ones); the hairstyle's surfaces are laid
   on the skin where a lock lies near it (a lock's width over a round shoulder, its side tilted into an arm); hair
   against hair (velocities drawn toward neighbouring locks', and neighbours kept within a third more than their gap;
   the rest found with it, else hair crept 15 mm in 8 s) keeps Г3's ribbons and long hair together in a run and a roll
   (no spiky heaps); stiff short hair is damped at 0.4 of its pull's critical rate (Jack's tufts rang in a run); Г1's
   side locks swing without worms.
8. *Cost*: the per-step cache leak is gone (fixed small steps: the shares made once), the small step allocates nothing,
   the skin hash is typed arrays kept and refilled, the inner layers have a fifth of their points (the surfaces' binding
   costs that much less), a figure is made in 3–7 s (most of the rest was a follow-map built for hair and thrown away).
   A frame of one figure with hair still costs 18–30 ms in node: what was saved went into asking the skin between the
   frames and the surfaces' contact. The speed task (several characters, the GPU) is left for later, as agreed.
9. *Frame rate*: fixed small steps of 1/240 s, what a frame leaves over carried to the next and the free points drawn
   on by their velocity over it; dampings as rates. Walking 2 s at 20, 24, 60, 90, 120, 144 frames a second against 30:
   0.5–0.6 mm apart on the whole, 6–12 mm at most (before: 27/21/20/30 mm, 162 mm at most).
10. *Fitting*: near the skull each point is moved along the skull's normal until it lies as far from the head's real
   surface (form, else skin by moving least squares) as from the designed head (within 1 mm), in the skull's own units.
   A change of the rest as a pose layer fits the hairstyle anew onto the changed skin and moves it by the difference —
   the surfaces and, moving, the guides, where the groom pulls and where it hangs; the head the hair rides is this
   frame's rest Head joint. The heads contract measured a hairstyle against the skin's points under it, which a hair
   fitted onto a grown head slides over; it measures it off the skin's surface now: 1.3–2.8 mm (limit 5).
11. *Stored builds*: only what is slow is stored (inner layers, made simpler, and occlusion; positions in 1/65535ths of
   their box): 45 MB → 4.6 MB for the 14; the locks, guides and binding are made at load (40 ms). The code they are built
   by is hashed beside them: the tool builds every stored one again when it changed and refuses if one differs without
   the version raised (so the version — a copy in git — goes up only when what is built changes). Old copies stay in git's
   history (rewriting pushed history was not done).
12. *Presets*: `physics` takes `friction`, `damping`, `together`; the no-op `physics` taken out of the 14 presets;
   `color` stays each part's own colour, what has its own (a streak, a band, a hat) keeps it — said so.
13. *Hard-coded and dead*: `sim.js`'s numbers named with why (H, PIN, MU, AIR, ZIGZAG, TOGETHER, NEAR, LINK, LIE, TWIST,
   WIND, the groom's), `windAt` described; `SKIN_PARTS`, `irr / 3.14159 * 3.14159`, the stale comments, `neckShape`,
   `collider` gone; build.js and styles.js say they are the source now (В1's copy stays for its page).
14. *Viewer*: the camera follows by time, not frames (on a slow screen it fell metres behind a runner); a scrub goes
   straight to the figure.

**Tried and dropped** (said in the code where it matters): a kink limit on chains (a lock bending no sharper than 40°)
fought the solids where hair lies pressed under a body and flung it (8000 m/s); smoother inner binding; a surface
contact by the full skin query per vertex (twice the frame's cost: the plane of the skin under each segment does it);
stronger air for motion and wind alike; damping stiff short hair by its springs' critical rate (no change: the shimmer
in a run was the head's).

**Left open.** Long locks bending sideways in their own plane over a shoulder stretch their outer edge (0.2–0.7 % of lock
edges past 2× in long styles' runs and rolls); the A-pose rest lays long hair on the raised arms; В1's hair on a toon
head keeps its own light; Г1/Г3's hair on a head grown by a layer is still carried by the affine change of the skin
(`followOf`), not fitted; the designed head's collision shape does not grow with a layer; Г3's ribbon tips part on the
back as they are drawn (tapered ribbons, no inner layer); the speed for several characters.

**Checks.** `units.mjs`: 29 hold. `quality.mjs --only hair`: all 1168 hold. `--only heads`: all 890 hold (the hairstyle
on a grown head 1.3–2.8 mm off the skin's surface). `numbers.mjs`: the 277 cases without moving hair as stored, the 56
hair cases stored anew (every hair character changed on purpose: its build, fit and simulation). `pictures.mjs`: the 268
others as stored; the 48 hair pictures stored anew, all looked at. Pictures in docs/pictures/engine/hair/: the six
sheets refreshed, `b1-side.png` new (В1's page and the engine at the same moments), `viewer-hair.png` refreshed.

**How, to repeat it.** `node engine/tools/characters.mjs presets && … pin && … cases && … hair` (builds what is slow,
checks the stored against the code); checks as above; pictures: `node engine/tools/sheets.mjs engine/tools/sheets/hair.json`
and `node engine/tools/hair-b1.mjs engine/tools/sheets/hair-b1.json` (В1's page and the engine at the same moments —
В1 stands 0.5 s and goes into its motion over 0.9 s first, so its frame is the motion's + 42).
