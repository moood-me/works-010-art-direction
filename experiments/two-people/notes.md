# Two people — through Kimodo's constraints (К2)

Four scenes of two people — a touch, a handshake, leading by the hand, a carry — every motion made by Kimodo (the moood studio's `make_motion`), joined with `after`, played
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
   where a ray from inside the shoulder leaves the skin; `tools/sides.mjs`: the trunk's sides under the arms;
   `tools/trunkpoint.mjs`: the trunk anywhere), pushed 1.5–2.5 cm out *along that ray* (not along the skin's normal),
   and carried by one of its joints (the collarbone; the chest). The settings of every point in `scenes.js` are in
   "Repeating it on other bodies" below. Played
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

## Third pass: both moving — a handshake and leading by the hand

The touch and the carry have one who leads and one who is placed. Here both walk and the meeting point belongs to
neither. Pavel's words: Kimodo makes one person at a time, so make one first, then the other with constraints to the
first's hands; where roles change, make it in turns. That is what was done; nothing new was needed in the tools.

**shake** (`h-p`, `h-q`): he and she walk towards each other, stop, shake right hands, let go.
- He is made first, alone (`h-p`): "walks forward … comes to a stop" + "raises the right arm forward for a handshake,
  shakes someone's hand with the right arm, then lowers it" — the data's own words (its records `…_handshake_…`).
  Seed 1 holds the hand out 2 s (seed 2: 1.3 s).
- She is made second (`h-q`): the same prompts, her right palm constrained onto his palm at three frames of his
  held-out hand (105, 125, 145). The pose sent is his own handshake at his frame 125 — in her own space it faces him,
  so her palm faces his palm; her pelvis where his is against his hand. Her walk is her own; where she stops is set by
  the constraint's pelvis.
- Numbers: her palm against his — Kimodo alone mean 3.5 cm (2.5–3 cm most of the hold, 5–10 cm at its ends), with the
  correction 0.0 cm over frames 100–160 (2 s). One in the other: their fingers 2–3 cm into each other's hand (flat
  hands, no grip: they overlap where real fingers would wrap). Nothing else.
- Looks: two people who walk up and shake hands; the clasp reads, close up the hands overlap rather than grip.

**lead** (`l-lead2`, `g-led2`): he walks and leads her by the hand; she walks beside him.
- He is made first (`l-lead2`): "walks forward at a relaxed pace, holding a child's hand with their left hand down at
  their side" (a first take, "leading someone by the hand with their left hand held a little out to the side", walked
  1 m in 5 s and raised the hand forward). His arm swings as in any walk.
- She is made second (`g-led2`): her right palm on his left palm every 10 frames (14 keyframes), her pelvis 62 cm to
  his left of his at the same frames; the poses from a probe of her own walk holding a hand (`g-probe`). A first take
  (`g-led`: 45 cm apart, a keyframe every 15 frames) put his arm into her shoulder and her hand lagged his swing by up
  to 40 cm between keyframes.
- Numbers: Kimodo alone mean 4.7 cm, max 9.3 cm; with the correction 0.0 cm over 4.5 s. One in the other: their
  joined forearms and hands 2–3 cm (every frame: joined hands are touching).
- Looks: two people walking side by side hand in hand; her gait leans forward a little, as if pulled along.

**The carry, again** (`carry3`): he puts the child down and takes two steps back (`m-down4`, a root2d keyframe 45 cm
behind): 63 cm back. Their hands still go into each other for about a second while he is bent over it at the set-down
(frames 366–390; clear from 396, before: 402). The child's legs: given through the constraint's pose (a fullbody
constraint, `tools/order_full.py`: c-hug2's poses with the legs turned), twice — legs forward-down (`c-hug4`: into his
thighs) and wrapped round his waist (`c-hug5`: they wrap, but one leg sticks out wide, the child's hands went further
into his chest, and it crouches oddly once put down; `pics/carry4-legs-try.png`). Neither is better than the straight
legs, so left, as agreed.

## Fourth pass: a hug, an adult in the arms, a chain where roles change, heads turned

Pavel's four asks, in his order, each to its end before the next; where Kimodo did one badly after a few tries, the
best try is kept and said plainly. 19 orders in this pass (3 of them probes: `sit-probe`, `lift-probe`, `lift-probe2`).

**hug** (`hug-p1`, `hug-p2` → `hug-q` → `hug-p3` → `hug-q2`): they walk up, embrace, hold, let go.
- Made in turns, each with palms on the other's back, the left high and the right low (so the arms cross as in a real
  hug): he alone first (`hug-p2`, of two seeds) — his arms embraced the air above her (`pics/hug-try1.png`); she on
  him (`hug-q`: her palms on points of his back skin, `tools/trunkpoint.mjs`); he again on her (`hug-p3`), his pelvis
  8 cm further back — now both arms go round her (`pics/hug-try2.png`); she again on him (`hug-q2`), her pelvis 10 cm
  further back. Each order's pose: the other person's hug at the hold (her pose for him: her arms already left high,
  right low).
- How far the constraints carry it: the palms land on the backs (Kimodo alone mean 7–18 cm over the whole hold, a few
  cm at the keyframes; with the correction 0–5 cm, the right hands up to 15–21 cm at the ends of the hold, where the
  arms are still coming round). The pelvis goes where it is put. **The chests do not**: whatever the pelvis distance,
  Kimodo leans both trunks into the hug, so the chests and her head pass into him — more than 6 cm (the test's
  limit), 2 000–2 700 skin points, the whole hold. Moving the pelvises apart by 18 cm in all only made both lean more.
  A hand constraint carries the arm's chain only; the trunk's lean is the prompt's. The next thing to try would be a
  fullbody constraint at the hold (the trunks upright, set by us) — not tried.
- Looks: two people embracing — arms round each other, her head beside his — but from the side their bodies merge
  into one (`pics/hug-close.png`).

**cradle** (`w-sit`, `m-cradle` → `m-cradle2`): an adult lifted in the arms, under the back and the knees.
- She: her own Kimodo motion, "sits on the floor with knees bent and hands resting on the knees", 10 s, attached to
  his hands (as the child is) from the moment he lifts. He: Kimodo's "squats down low, picks up a large heavy object
  from the floor with both arms under it, and stands up holding it at chest level" (the data has no person carried in
  the arms; `lift-probe2` is the probe), his left palm constrained under her back (Spine2), his right under her right
  thigh by the knee, at his squat frames 128 and 138.
- First take (`m-cradle`): he stood up raising his hands to his chest, 80 cm apart — she, fixed to them, went up to his
  head. Second (`m-cradle2`): also his palms at frames 215 and 245, where her same two points would be if lifted
  0.80 m (0.70 was 8 cm out of his left arm's reach) — her seat at his waist, his forearms under her.
- Numbers: his palms on her — Kimodo alone mean 6–7 cm (max 12–13), with the correction 0–1 cm (max 6). One in the
  other: up to 5.6 cm, ~200 skin points through the lift and the carry (his arms in her thighs and back, her side in his
  chest).
- Looks: he squats, slips his arms under her, stands with her in his arms and steps on. But she is a sitting doll: her
  pose is sitting on the floor, rigid — knees apart, hands on her knees, legs sticking out to the side — not someone
  held (who would curl into him and put an arm round his neck). The next step would be her arm round his neck through
  a constraint, as the child's; not done. The nearer one (helping someone walk, an arm over the shoulders) was not tried.

**exchange** (one chain: `a-stand, a-look, a-shake, a-led` and `b-touch3, b-hold4, b-shake3, b-lead`): he lays his
hand on her shoulder, she looks round and turns, he steps back and offers his hand, they shake, he turns and leads her
away by the hand. 19 s. Every motion goes on from the same person's last one (`after`, 5 frames); whose motion is
made first changes: he (touch) → she (looks round; his hold made on her) → he (offers his hand) → she (her palm on
his) → he (turns and walks, hand held out) → she (her palm on his, her pelvis at his left, every 10 frames).
- Twice Kimodo would not do it from words alone: after his hand lay on her shoulder, "lowers the right hand … steps
  back" + "a handshake" (`b-shake`, `b-shake2`, two seeds) kept his hand up at her shoulder's height and hardly stepped
  back. With his own handshake pose (`h-p`) as a hand constraint, 30 cm behind (`b-shake3`), he did.
- Where an `after` motion's space lands (needed to put the other person's targets into it before it is made): I took
  the earlier motion's pelvis at its frame n−k; it came under 1 cm off here — because both earlier motions end
  standing still: over all 23 `after` motions here that guess is 0.5–5.9 cm off (see "Repeating it on other bodies", 3).
- Numbers: his palm on her shoulder 2–4 cm (Kimodo), her palm on his in the handshake 4.9 cm mean (14 at the ends),
  her palm on his while led 3.2 cm mean (max 4.7); 0 with the correction. One in the other: up to 4.4 cm as she turns
  inside his reach (frame 290), 2–2.5 cm in the handshake (fingers).
- Looks: a scene that reads from start to end; the joints between motions don't show. Weak: while leading, his left arm
  is bent with the hand at his hip (Kimodo walked "holding someone's hand" with it raised to 1 m), so her hand is
  pulled up; as she turns round his hand is still near her shoulder for a moment.

**Heads turned** (`h-q3`, `g-led3`; one ask each): instead of the prompt, a fullbody constraint built from the
motion's own poses at three frames, with only the neck and head turned to the other's eyes (`tools/order_head.py`:
the turn shared by Neck1, Neck2, Head). The rest of the pose is the motion's own, so the hand stays where it was.
- Handshake (`shake-look`): her head now points within 2–6° of his eyes through the whole clasp (it was 22–28° off,
  over his shoulder). Reads: she looks up at his face. He still looks ahead over her head (he is made first; not
  re-made).
- Leading (`lead-look`): the full turn to him would be 108°, so it was capped at 60°; at the keyframes her head turns
  that far, between them it goes back to the walk's own (100–114° off): glances that read weakly, more a tilt than a
  look. A keyframe every 10 frames would hold it; not done.
- The old versions stay beside them (`shake`, `lead`).

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
- **Leading by the hand**: "leading someone by the hand … held a little out to the side" made a slow walk with the
  hand raised forward; "holding a child's hand … down at their side" made a normal walk with the hand swinging.
- **Busy**: orders sent while the GPU wakes, or while another session's run is on it, can fail with `busy` — send
  the same ask again (the same key, a new making).
- **A pose sent must have 77 joints exactly**: one typed out by hand had 76 and was refused ("Constraint joint count
  (76) does not match…"). Print the constraint from the tool and copy it.
- Joints a hand constraint does not use may be sent as zero (a shorter ask) — but both arms' chains go into every
  hand constraint of a frame (above).
- **The child moves as an adult** (Kimodo has no age); the lift itself is Kimodo's "picks up a large object at waist
  level" — it reads as lifting a child, not as a box, once the second keyframe draws the hands to the chest (without
  it the child was held out at arm's length).

## What is weak, honestly (the first versions; the second's below)

Third pass: the handshake's and the held hands' fingers overlap instead of gripping (2–3 cm); in leading, her
gait leans forward and her hand follows his arm's swing — between keyframes Kimodo lags it up to 9 cm, the
correction brings the rest; nobody turns a head to the other (Kimodo's heads look ahead). The carry: the child's legs
still hang straight (two tries through the pose made it worse), and the set-down's second of hands in bellies stays.

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
- Not tried: a hug of two adults. (The handshake and leading by the hand: the third pass.)

## Files

- `index.html`, `page.js` — the page; `scenes.js` — the scenes (places, chains, contacts, carrying); `scene.js` —
  playing two people, the contacts' correction, the attachment; `figure.js` — the engine's figure with an `adjust`
  hook.
- `motions/<id>.json` — Kimodo's data as the engine keeps them; `motions/orders.json` — what was asked for each (prompts,
  seconds, seed, constraints, `after`, `startsAt`) and the takes thrown away; `motions/*.spec.json` → `tools/order_hand.py`
  → `motions/*.constraint.json` — the hand constraints exactly as sent.
- `tools/order_full.py` (a fullbody constraint from a hand constraint's poses, with the legs set),
  `tools/order_head.py` (a fullbody constraint from a motion's own frames, the neck and head turned to a point),
  `tools/trunkpoint.mjs` (a point on a body's trunk skin at rest: where the hug's and the cradle's palms go),
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
at frame 0 (checked against the studio's own within 0.5 mm) — known only once it is made; before, see below.

## Repeating it on other bodies: what is the method's, what is this pair's

A fresh agent repeated the touch on other bodies (a man and a short woman; a child and a woman) from this folder
alone (`experiments/other-bodies/notes.md`); where these notes were not enough is written down here.

1. **The touched points.** All in the woman's rest space, carried by `RightShoulder`; made with
   `node tools/shoulder.mjs surface <body> <side> <share> <angle> <out>` — a ray from the collarbone's line (at `share`
   of the way from the `Shoulder` joint (the collarbone's root) to the `Arm` joint (the shoulder ball); above 1 is
   beyond the ball), going up and back at
   `angle` (0 straight up, π/2 straight back), to where it leaves the skin, then `out` metres further along the ray:
   - the touch `[-0.1625, 1.3196, -0.0155]`: `moood-woman Right 1.1 0.45 0.018` (gives it to 0.1 mm; 1.1 and 1.2 hit
     the same skin point);
   - the slide `[-0.1903, 1.2948, 0.0063]`: `moood-woman Right 1.4 0.2 0.02`.
   The hug's points: `node tools/trunkpoint.mjs <body> <joint> <dy> <dx,dy,dz> <out>` (in `hug-*.spec.json`); the
   cradle's under-thigh point is a hand-set point on `RightLeg` (in `m-cradle.spec.json`). On another body: the same
   settings give the same place on its own shoulder; check it on a picture (`pics/*-contact.png` jobs).
2. **Whose metres.** World places (`scenes.js` positions, `targets.mjs` "world", contact points) are in our bodies'
   metres. Everything in a `*.spec.json` (`target`, `targets`, `hip`) and in a constraint is in the *ordered person's
   Kimodo* metres: world ÷ that person's k. So "his pelvis 51 cm behind the touch, 28 cm to her left" (touch3) is
   Kimodo's: ×1.015 on the man, but ×0.707 on a child (36 × 20 cm). k: `node tools/bodies.mjs <body id> …` (hip height ÷ SOMA's; also arm ÷ k against SOMA's 0.559 — far from it, k alone won't carry the hands).
3. **Where an `after` motion starts, before ordering it.** Its `startsAt` depends only on the earlier motion and the
   `after` frames, not on the new one's prompt or constraints (here: `b-hold3` and `b-hold4` after `b-touch3` have the
   same one; `m-down2`/`m-down3` within 1 mm). So:
   - if any motion was already made `after` the same motion with the same frames, use its `startsAt`;
   - else, where centimetres matter (a hand constraint), order a 0.5 s probe `after` it first ("A person stands
     still.") and read `startsAt` from `motion(key)`; one cheap order instead of a take 6 cm off (`b-hold3`);
   - the guess "the earlier pelvis at frame n−k" is 0.5–5.9 cm off over the 23 here: under 1 cm where the earlier
     motion ends standing still (`a-look`, `b-shake*`, `a-shake`, `a-led`), 2–6 cm where it ends walking, bending or
     reaching (`m-walk*`, `b-hold3/4` after the touch). `tools/startsat.py` gives the exact one once made.
   Then: the new motion's space = the earlier one's space moved by `startsAt` (no turn); the target in it = the
   target in the earlier one's space − `startsAt`.
4. **Bodies without a character file**: `tools/targets.mjs body:<body id> …` (added after that test).
5. **The as-sent constraints are the truth**, not the tool's output today: `b-touch3.constraint.json` has the ring and
   little fingers zero (that payload was copied into the order by hand), while `order_hand.py` on its spec now gives
   them from `fingersFrom`. Only fingers; they don't move the palm's point (it hangs on the hand joint and the middle
   finger's root, whose places don't depend on finger turns).
6. **This pair's, not the method's** — on another pair these are the main work, chosen by looking:
   - the prompts: "looks down at them" fits a man over a woman's shoulder. For the child (the other agent's test)
     "reaches up … looks up at them" threw its head back; the plain "puts their right hand on the arm of someone in
     front of them" read well;
   - the stance: his pelvis 51 cm behind and 28 cm to her left of the touch (Kimodo's metres), chosen so his right arm
     crosses to her right shoulder with the elbow bent: the shoulder ball is 0.42 m from the target, against an arm of
     0.58 m (upper arm + forearm + half the hand) — about 0.7 of the reach. That ratio, from behind on the side away
     from the hand, is a start for another pair, not a rule (the child's first stance pressed it into her back);
   - the hand: `handYaw −0.25` (fingers forward over her shoulder; the touch only), `elbowPole [-0.4,-1,0]` (the elbow
     down and a little out to his right; touch and hold), `fingersFrom b-probe 120` (a flat tapping hand) — all for a
     palm laid on top of a shoulder from behind. On an arm they put the child's hand fingers-up; there they must be
     chosen again;
   - the look: B's head turned 0.6 of the way to her head, 25° at most (a correction). A's look round is her own motion,
     over her shoulder at a man's height; nothing here makes her look down to a child (a new `a-look` would).
   Look at a sheet from the side and the front, then a close-up of the contact, before keeping a setting.
7. **The palm's middle** (here, in `scene.js palmRest` and `order_hand.py palm_rest` alike): halfway between the hand
   joint and the middle finger's root, pushed 1.5 cm out on the palm's side (the normal of index-root → ring-root ×
   wrist → middle-root; flipped for the right hand). К1 uses another (the mean of the wrist and the index and little
   finger roots): numbers of the two are not comparable to the centimetre.
8. **One take is luck.** The other agent's three seeds of the same touch: one let the hand leave the shoulder by 21 cm
   between the keyframes (the correction then moves the arm 20 cm — no longer small). Before accepting a take, run
   `tools/measure.mjs <scene>` and look at "Kimodo alone": the max, not only the mean, and the frames between the
   keyframes; more than ~10 cm between them → another seed, or a keyframe more (every 10–15 frames, as `g-led2`).
   Then look at the sheet.
9. **The studio**: an order that failed (often "busy" when several are sent at once) answers `motion(key, data:
   "body")` with "not made (yet)", exactly as one still running; only `motion(key)` without data shows the making's
   `outcome: failed`. Poll with `motion(key)`; a failed one is asked again as it was (a new making of the same key).
   Send big constraints one at a time.
