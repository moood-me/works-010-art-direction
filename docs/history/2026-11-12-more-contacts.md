# К3, К4, К5 — things in the hand, contacts with the body, other bodies (2026-11-12)

**What called for it.** After К1 and К2 Pavel said: other scenarios are worth making too — other kinds of objects,
other kinds of motions; and asked whether the two requests would be covered well. The orchestrator answered that
nobody but the authors had repeated the way and every scene stood on one body, and Pavel allowed more agents (the
studio has three slots). Three Opus agents were started, each in a branch of its own from `contacts` or
`two-people`, each in a new folder, copying what it needed from К1.

**К3 — `experiments/moving-things/`** (branch `moving-things`). К1's way for things that move with the hand: a door
opened by its lever, a cup taken from a table, drunk from and put back, a box carried in both hands, a chair pulled
out. Each place of the hand is a constraint at its own frame; the thing follows the hand while held. After the first
pass the orchestrator sent it back: no grip (the mug stuck to a flat hand), the box put down as if sitting on air.
Second pass: the body's skeleton has fingers, so they close round the thing by a simple curl per thing on top of
Kimodo; the box is put down standing; the chair was added. The box's hands stayed poor.

**К4 — `experiments/body-contacts/`** (branch `body-contacts`). Contacts that are not a palm: the back against a
wall, feet on steps and a hand sliding on a rail, sitting and lying on a bed, forearms on a table. The place is given
as a whole pose, as feet, as the pelvis with feet or hands; the pose always comes from a motion Kimodo made by
itself, put against the thing by the skin. Sent back once: she lay as a starfish and sank 8–9 cm into the mattress.
Second pass: a new free lying take (on the back), the pelvis asked higher by the known offset; moving the feet back
on the stairs did not help (it is the swinging foot's toes).

**К5 — `experiments/other-bodies/`** (branch `other-bodies`). A fresh agent with only К1's and К2's folders repeated
the table and the shoulder touch on other bodies and with other seeds. The way repeats on bodies of usual
proportions; it fails on a 2.31 m body whose arms are short for its legs (places are scaled by one number per body);
one seed in three of the touch was bad. Its list of where the notes were not enough went to the authors: К1's notes
and table plan were fixed (named parameters, the bend search stops with an error, a section on where the way stops
working); К4's notes were written with those points in mind.

**In the catalogue.** К3, К4, К5 in section К of `gallery/paths.js` with their pages in `PAGE`; all branches merged
into `two-people`, which now holds the whole section.

**What the orchestrator looked at.** Sheets and close-ups of every scene; not the films.

**How to repeat.** Each folder's `notes.md`; every motion ordered is in its `motions/asks.json` (`orders.json`).
