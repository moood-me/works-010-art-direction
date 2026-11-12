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

**A third pass** (Pavel, the same day: ask the agents for more where something could be better). The two nearer
scenes that had been skipped were made: a handshake (the man made first with no constraints, the woman's palm
constrained onto his at three frames) and leading by the hand (her palm on his every 10 frames, her pelvis 62 cm
beside him; at 45 cm and every 15 frames his arm went into her shoulder and her hand lagged). In the carry the man
now steps back 63 cm after the set-down; two tries to give the child's legs through the pose made it worse and were
left (`pics/carry4-legs-try.png`).

**A fourth pass** (since the handshake came out, the harder ones were tried). A chain where the lead changes — he
touches her shoulder, she turns, they shake hands, he leads her away, 19 s, every motion `after` the same person's
last — reads from start to end. A hug of two adults, made in turns (he alone, she onto him, he again, she again): the
arms go round, but the chests pass through each other for the whole hold — a hand constraint places the hands and
the pelvis, not the trunk; a whole-pose constraint with upright trunks was not tried. An adult carried in the arms:
Kimodo has no such motion; she is a sitting pose attached to his hands and reads as a stiff doll — it did not come
out. Her look at him in the handshake was got by a whole-pose constraint with only the head turned
(`tools/order_head.py`), not by the prompt; in the leading it is a weak glance.

**What is weak.** His look at her is a neck correction on top (Kimodo kept the head back though asked); the child's
legs hang straight into his shins (up to 6 cm); at the set-down their hands go into each other for a second; Kimodo
has nothing for carrying an adult, so a child is carried. In the handshake the flat hands overlap rather than grip; led by the hand, she walks
leaning forward as if pulled; nobody looks at the other in these two. The orchestrator looked at stills, not at the films.

**The notes, after the test on other bodies (К5).** The agent that repeated the touch on other bodies listed where
К2's notes were not enough; the author checked each point against the code and fixed them: a section on what is the
method's and what is this pair's (prompts, stance, hand turn, look), whose metres each number is in, the exact
settings of the touched points, a rule for where an `after` motion starts (a 0.5 s probe first; the earlier "within
1 cm" was luck — 0.5–5.9 cm over 23 motions), and that one take is luck.

**In the catalogue.** К2 in section К of `gallery/paths.js`, its page in `PAGE`. The branch contains `contacts` (К1),
merged in so that both stand in one section.

**How to repeat.** `experiments/two-people/notes.md` ("The principle", "Second pass", "What Kimodo does badly");
`motions/orders.json` — every motion ordered.
