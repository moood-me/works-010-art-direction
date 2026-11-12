# Two people — through Kimodo's constraints (К2)

Two scenes of two people, every motion made by Kimodo (the moood studio's `make_motion`), joined with `after`, played
on the early engine (`engine/`) with Anny bodies of `engine/data/bodies` (moood's man, woman, child). Each is here in
its second version (`touch3`, `carry2` in `scenes.js`, the page's first two buttons — made after a look at how the
first ones read, see "Second pass" below) and its first beside it ("первая версия"):

- **touch** — a woman stands; a man walks up from behind and puts his right hand on her right shoulder; she looks
  round over that shoulder; his hand stays on the shoulder while it turns.
- **carry** — a child (1.31 m) stands and raises its arms; the man walks up, bends, takes it under the arms, lifts it
  to his chest, carries it 2 m, bends and puts it down on its feet; the child hugs him while carried and lets go.

Page: `index.html` (scene, play/pause/scrub, slow, the correction on/off, the contact point, views, closer to the
touch; the camera turns with the mouse). Measures: `tools/measure.mjs <scene>`; pictures and films:
`tools/pictures.mjs tools/jobs-touch.json` (and `jobs-carry.json`).

## The principle, step by step

Kimodo makes one person and knows nothing of a second. Two are tied by making them **in the order of cause and
effect**: whoever acts first is made first; what of them the other must meet becomes the other's constraint.

1. **Who is first.** In *touch*, the woman (A) only stands: `a-stand` (5 s). In *carry*, the child (C) stands and
   raises its arms: `c-wait`. They lead; the second person follows.
2. **Place both in one space.** Each motion has its own Kimodo space (origin at its first pelvis, facing +z). The
   scene puts each person somewhere with a heading (`scenes.js`: A at the origin; B at z −4.0; the child at the
   origin facing −z; the man at z −4.0). The engine carries a motion onto a body scaling the pelvis's path by the
   body's hip height against SOMA's (`k`: man 1.015, woman 0.896, child 0.707), so the scene is in *our bodies'*
   metres, not Kimodo's.
3. **A place on the first person, on our body.** A point of the first one's *skin at rest* (`tools/shoulder.mjs`:
   where a ray from inside the shoulder leaves the skin; `tools/sides.mjs`: the trunk's sides under the arms), pushed
   1.5–2.5 cm out along the skin's normal, and carried by one of its joints (the collarbone; the chest). Played
   through the scene it gives that point's place in the world at every frame — on *our* body, of *its* proportions
   (`tools/targets.mjs`).
4. **Into the second person's Kimodo space.** The world point minus the second person's placement, turned back by
   its heading, divided by its `k` (`tools/targets.mjs … x0,z0,heading,k`). So a man 1.5 % larger than SOMA is asked
   to reach 1.5 % less far, and lands on the woman's real shoulder, not on where SOMA's shoulder would be.
5. **A pose Kimodo made, reaching there.** A hand constraint is a whole pose (Kimodo takes the hand from its FK). The
   pose is a frame of a motion Kimodo made of the same action without constraints (a *probe*: `b-probe` — walks up and
   taps a shoulder; `m-probe` — bends and takes a large thing at waist height), turned and moved so its pelvis stands
   where asked, its arm (shoulder ball, elbow hinge) turned by the least to bring the palm onto the point
   (`tools/order_hand.py`, `tools/pose.py`). What goes to Kimodo is that pose; Kimodo makes the walk, the lean, the
   elbow and everything between.
6. **Frames.** The constraint's frames are chosen from the script: B's hand at his frames 118 and 149 = scene frames
   160 and 191 (B starts at 42), A's shoulder taken at those very frames. The man's hands at frame 126 (grip) and 168
   (lifted, drawn in to his chest).
7. **The reaction (`after`).** A's look round is made `after` her stand (Kimodo starts it from her last five frames),
   so it begins without a jerk; the touch is timed so she turns about half a second after it.
8. **The follower again.** While she turns, B is made again (`b-hold`, `after` `b-touch`) with his hand on her
   shoulder *as it moves* — her shoulder taken at the frames of her turn, the hand also turned about the vertical with
   her shoulder (1.4 × her turn: a hand left as it was ends with its fingers on her jaw as her chin comes round).
   The roles change in turn: she followed his touch; now his hand follows her turn.
9. **The carried one is attached.** From the frame the hands reach the child, its whole pose (its own Kimodo motion:
   arms up, then hugging, then letting go) is moved rigidly as the man's hands move: the frame between his palms,
   turned as the line across them turns, kept upright (one held under the arms hangs plumb). It is taken from his pose
   as Kimodo made it, before the corrections, so nothing loops. To put it down, his last motion (`m-down`) is
   constrained with *the same pose as at the grip* (the studio's `from`: m-lift's frame 126, moved 3.33 m) — set down
   at the height it was taken up, its feet come to the floor (0.2 cm above it, measured). From then it stays where
   it was put and goes on with its own motion.
10. **A small correction on top.** Kimodo misses by centimetres (at the constrained frames by our proportions; between
   them more: it constrains only keyframes, sparse). `scene.js` brings the palm the rest of the way: the same
   two-bone turn of the arm (`reachTo`), faded in and out over 8–10 frames, after the engine's retargeting and before
   skinning (`figure.js`, a copy of the engine's with an `adjust` hook). In *touch* it also turns the hand about the
   vertical towards 1.4 × her shoulder's turn. Its size is measured below; the page switches it off ("поправка рук").

## Second pass: what a person sees

The first versions held the contact, but read badly: in the touch he stood at arm's length, arm straight, head tilted
back, and after she turned his hand was a claw beside her jaw with a bent wrist (from the side, a hand at her throat);
in the carry the child was held out from him, barely off the floor, its hands stuck in his chest. What changed:

**touch3** (`b-touch3`, `b-hold4`):
- He stands nearer and behind her left (pelvis 51 cm behind the touch, 28 cm to her left of it), so his right arm
  reaches across to her right shoulder: the elbow bent and hanging (a new `elbowPole` in `tools/order_hand.py` turns
  the arm about shoulder → wrist so the elbow points down; the probe's tap had it stuck out sideways), the fingers flat
  (`fingersFrom`: the probe's own flat tapping hand), the hand pointing forward over her shoulder.
- The touch is on the outer top of her shoulder, and as she looks round his hand is made by Kimodo to slide out to the
  shoulder's edge (`b-hold4`'s keyframes on a point further out). Her chin comes round over the top of her shoulder:
  a hand left on the top (v1, and `b-hold3`) ends at her chin, whatever way it is turned; one at the edge stays clear.
  The hand is not turned on its own any more (turned to follow her shoulder it bent the wrist 75–85°).
- His head: asked to "look down at them", Kimodo still tilted it back 6–10°. A correction on top (`looks` in
  `scenes.js`, `scene.js`) turns his neck and head towards her head, 0.6 of the way, at most 25°, spread over the two
  neck joints and the head, faded in and out — the one correction here that is not a contact; off with the others.
- Tries on the way, kept in `motions/` and `orders.json`: `b-touch2`/`b-hold2` (nearer but from her right: the
  forearm came inward and the fingers lay towards her chin), `b-hold3` (from her left, the hand on the top: her chin
  came onto the fingers again).

**carry2** (`m-lift2`, `m-walk2`, `m-down3`; `c-wait`, `c-hug2`, `c-rest2`):
- His second keyframe lifts the child 42 cm (v1: 30) and draws it in so its front comes to his chest (v1: 9 cm off).
- The child's hands are constrained onto the top of his shoulders: the same principle the other way round. The points
  on his shoulders, at four frames of the carry, are carried back through the attachment (the rigid move of his hands
  since the lift), the child's placement and size, into the child's own Kimodo space (`tools/carried_targets.mjs`);
  the pose is the child's own v1 hug, its arms turned to reach (`motions/c-hug2.spec.json`). Kimodo then makes the hug
  around them; a correction on top brings the palms the rest of the way.
- He takes a step back after putting it down (`m-down3`).
- A try to keep the child's feet off his shins ("with knees bent and feet lifted behind them", `c-hug3`): Kimodo kept
  them under it; not used.

Numbers of the second versions:
- touch3: his palm against its place — Kimodo alone mean 4.1 cm, max 6.4 cm while she stands (frames 160–192), mean
  2.2 cm, max 3.5 cm while she turns (200–249); with the correction 0.0 cm. One in the other: 6 frames of 125, at
  most 0.7 cm (his thumb on her shoulder). The look correction: 25° (it is at its limit; Kimodo's head was 50–60° off
  her head).
- carry2: his palms on the child's sides — Kimodo alone mean 5.2 / 6.0 cm, max 15 cm; with the correction 0.0 cm.
  The child's palms on his shoulders, frames 205–362 — Kimodo alone mean 5.4 / 6.9 cm (2–10 cm most of the time; up to
  25 cm at the ends of the window, where it lets go); with the correction mean 1.9 cm, max 4 cm (its arm can't
  always reach). The child's lowest point 36–42 cm above the floor while carried; 0.1 cm once put down.
  One in the other: his thumbs 1–3.5 cm into the child's sides; the child's dangling foot into his shin up to 6 cm as
  he walks (its legs hang straight in front of his); the child's forearm into his shoulder up to 6 cm around frames
  320–340 (as he stops and his shoulders rise); at the set-down (frames 366–396, 1 s) the child's letting-go hands and
  his fingers go into each other's belly and hips up to 6 cm (they stand pressed together; his step back is 12 cm).
  The measure's search reaches 6 cm, so "6" means "6 or more".

## Numbers of the first versions (`tools/measure.mjs`, every 2nd frame; `pics/*-measure.json`)

**touch** — B's palm against its point on A's shoulder, frames 160–249 (3 s of contact):
- Kimodo alone: mean 5.0 cm, max 8.7 cm. At the constrained frames 2–3.5 cm (proportions); between them up to
  8.7 cm (`pics/touch-raw.png`: the hand floats off and comes back).
- With the correction: 0.0 cm (the arm reaches it every frame). The hand turn added on top: up to 35° (frame 190,
  just before `b-hold`'s first keyframe), 15–29° later.
- One body in the other (> 5 mm): 14 of 125 frames, at most 1.4 cm — his palm and thumb pressing into her shoulder
  at the touch. Nothing else passes through (the walk, the bodies).

**carry** — the man's palms against the child's sides, frames 152–376 (7.5 s held):
- Kimodo alone: mean 6.6 / 6.7 cm, max 14.3 / 12.1 cm (Kimodo's hands come together and apart as for a box; the
  child is rigid). With the correction 0.0 cm.
- The child's feet: on the floor before the lift; 30–34 cm up while carried; 0.2 cm above the floor once put down.
- One body in the other: up to 3.4 cm while he reaches (his fingers through the child's raised forearm); up to
  6 cm while carrying — mostly the child's forearm and fingers into his chest and shoulder (its hug was made for
  someone of Kimodo's size, not for him), and his thumbs 2–3 cm into the child's chest.

## What Kimodo does badly, and what was found

- **Its local turns are its own.** A hand constraint's `local_joints_rot` is not the turn from SOMA's rest
  (`G = q R0ᵀ`, what the engine uses) but the turn between the joints' own frames, `q_parentᵀ q_j` (the studio's `q`
  directly). Sent the other way, the hand came 45 cm high, exactly where that reading puts it (`tools/pose.py
  native`).
- **Hand constraints of one frame are merged into one pose.** Each hand's constraint must carry both arms; one sent
  with only its own arm left the other arm in the T-pose at that frame and its hand 60 cm off.
- **One prompt for walk and touch** made the arm held out the whole walk ("zombie"), and through her back: a chain
  of two prompts (walk and stop; then put the hand) fixed it.
- **A root2d stop** at a frame earlier than Kimodo's own walk would stop was overrun by 60 cm and pulled back in a few
  frames: start further away instead, so the natural walk ends where the hand constraint wants the pelvis.
- **Looking back**: "looks back over their right shoulder" barely turned the head (two seeds); "turns to their
  right and looks back, diagonally to the right side" (the data's own words) turned it, a second late (seed 2 of 2).
- **Keyframes are sparse**: between two constrained frames the hand drifts up to 9 cm (touch) — more keyframes
  would cut it, at more of the ask's size (a pose is ~1.5 KB a frame).
- **Hug** is made for an imagined person of Kimodo's size: the child's arms go into the man (v1). Constrained to his
  shoulders (v2), it hugs him.
- **Head**: "looks at them", "looks down at them" — the man's head stayed tilted back (6–10°, two orders).
- **Feet**: "with knees bent and feet lifted behind them" did nothing to a child's legs held in the air.
- **A pose sent must have 77 joints exactly**: one typed out by hand had 76 and was refused ("Constraint joint count
  (76) does not match…"). Print the constraint from the tool and copy it.
- Joints a hand constraint does not use may be sent as zero (a shorter ask) — but both arms' chains go into every
  hand constraint of a frame (above).
- **The child moves as an adult** (Kimodo has no age); the lift itself is Kimodo's "picks up a large object at waist
  level" — it reads as lifting a child, not as a box, once the second keyframe draws the hands to the chest (without
  it the child was held out at arm's length).

## What is weak, honestly (the first versions; the second's below)

Second versions: his head's look at her is a correction on top, not Kimodo's; the child's legs hang straight and its
foot meets his shin as he walks; at the set-down their hands go into each other for a second; the child's hug is still
more hands-on-shoulders than arms-round-the-neck; his thumbs press into the child's sides. In the touch, seen from
behind-right her turned head is near his hand (they don't touch: 0.7 cm at most, at the shoulder).

First versions:

- The man's head is tilted back a little in *touch* (Kimodo's, 5–13°): he looks over her rather than at her.
- He stands at arm's length behind her (the pelvis was put 0.6 m behind the shoulder): it reads as reaching, not as
  closeness. A closer stance is one number in `motions/b-touch.spec.json` and two orders.
- His hand on her turning shoulder ends with the wrist strongly bent (the turn is asked of the hand alone; Kimodo did
  part of it, the correction the rest, up to 35°).
- The child's hands while carried rest against the man's chest rather than round his neck, and its forearms go into
  him up to 5–6 cm. The way to fix it is the same principle the other way round — the child's hands constrained to
  points on his shoulders, in the child's space through the attachment — not done. A correction on top was tried and
  reverted: Kimodo's hands were 24–38 cm off, too far for a "small" correction.
- Fingers: no grips, as agreed; hands are flat, so thumbs and fingertips press 1–3 cm into skin at the contacts.
- The child is held under the arms the whole carry (no forearm under the seat): the simple means.
- Films are 10–15 frames a second (software rendering).
- Not tried: a handshake, a hug of two adults, leading by the hand — the two scenes asked for worked, so the nearer
  ones were not needed; the same steps make them (a probe, a pose to the other's hand, `after`).

## Files

- `index.html`, `page.js` — the page; `scenes.js` — the scenes (places, chains, contacts, carrying); `scene.js` —
  playing two people, the contacts' correction, the attachment; `figure.js` — the engine's figure with an `adjust`
  hook.
- `motions/<id>.json` — Kimodo's data as the engine keeps them; `motions/orders.json` — what was asked for each (prompts,
  seconds, seed, constraints, `after`, `startsAt`) and the takes thrown away; `motions/*.spec.json` → `tools/order_hand.py`
  → `motions/*.constraint.json` — the hand constraints exactly as sent.
- `tools/carried_targets.mjs` (a point on the carrier in the carried one's Kimodo space, through the attachment),
  `tools/startsat.py` (an `after` motion's startsAt, as the studio computes it),
- `tools/keep.py` (a made motion's body data and order in), `tools/convert.py` (into the engine's format; copied from
  `engine/tools/motions.py`), `tools/targets.mjs`, `tools/shoulder.mjs`, `tools/sides.mjs`, `tools/bodies.mjs`,
  `tools/measure.mjs`, `tools/feet.mjs`, `tools/pictures.mjs` (+ `jobs-*.json`).

## Repeating it for another scene

Order the leader's motion; keep it (`motion(key, data: "body")` → `tools/keep.py`, `tools/convert.py`); add the
scene to `scenes.js`; find the point on the leader's body at rest; `tools/targets.mjs` gives it in the follower's
Kimodo space at the frames you choose; order a probe of the follower's action without constraints, pick its frame;
write a `*.spec.json` (source, frame, hip, targets) and run `tools/order_hand.py`; send the constraint with the
follower's prompts (a chain: approach, then act); keep it; add the contact to the scene; measure; look. For a reaction
order `after` the leader's motion; for a follower that must keep up, order it again `after` itself with the
leader's new places. `startsAt` of an `after` motion is the earlier one's pelvis at its frame n−k less the new one's
at frame 0 (checked against the studio's own within 0.5 mm).
