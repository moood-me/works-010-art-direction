# К2 — two people: a touch and a carry (2026-11-12)

**What called for it.** The second of the two tasks Pavel had put off until after the engine (requirements, "After
the engine is finished"): two people — B touches A's shoulder and A looks round; one carries another; nearer ones
(a handshake, a hug, leading by the hand) if Kimodo does these badly. On 2026-11-12 he asked to try both tasks with
Opus agents, in new branches from `main`.

**What was done.** An agent made `experiments/two-people/` in the branch `two-people`, on the early engine
(`engine/`) with moood's man, woman and child. Whoever acts first is made first; a point on that person's skin is
followed through the scene and carried into the other one's Kimodo space as a hand constraint; the reaction is made
with `after`. A small correction on top brings the palm the last centimetres. While carried, the child is attached to
the frame between the man's palms and posed by its own Kimodo motion. Two things about Kimodo cost tries: a
constraint's joint turns are Kimodo's own (not the engine's from rest), and constraints on the same frame are merged
into one pose, so each hand's constraint must carry both arms.

**Two passes.** After the first the orchestrator looked at the sheets and close-ups and sent it back once: he stood
at arm's length with a straight arm and his head tilted back, his hand became a claw by her jaw as she turned; the
child was held out and barely lifted, its hands stuck in his chest. The second pass: he stands near with a bent
elbow, the hand slides to the shoulder's edge as she turns; the child is at his chest with its hands constrained
onto his shoulders. The first versions are kept beside (the page and `pics/`).

**What is weak.** His look at her is a neck correction on top (Kimodo kept the head back though asked); the child's
legs hang straight into his shins (up to 6 cm); at the set-down their hands go into each other for a second; Kimodo
has nothing for carrying an adult, so a child is carried. A handshake, an adult hug and leading by the hand were not
made. The orchestrator looked at stills, not at the films.

**In the catalogue.** К2 in section К of `gallery/paths.js`, its page in `PAGE`. The branch contains `contacts` (К1),
merged in so that both stand in one section.

**How to repeat.** `experiments/two-people/notes.md` ("The principle", "Second pass", "What Kimodo does badly");
`motions/orders.json` — every motion ordered.
