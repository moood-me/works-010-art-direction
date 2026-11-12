# Things that move with the hand: a door, a cup, a box

The next step after К1 (`experiments/contacts/`, the principle and what it cost: read its `notes.md` first). There
everything touched stands still; here the thing moves with the hand. Pavel's words this stands on: "If the model
understands some motions badly, never mind — try other similar tasks and motions; the main thing is to make the
principle work." Asked (by the orchestrator, from Pavel): other kinds of things and motions — a door opened by its
handle and walked through; a cup taken from a table, drunk from, put back; a box taken from the floor in both hands,
carried, put on a table; if strength is left, something pushed or pulled along the floor.

What came out: the door, the cup, the box and a chair pulled out from a table, each end to end, on the early engine
(`engine/`) and its Anny bodies, in `index.html` (served from the repository's root). A second pass (asked after the
first was looked at: "what a person sees as wrong now is mostly the hand") closed the fingers round what is held,
kept the mug upright in the fist, got the box put down standing, and added the chair — see "Second pass" below. The
first pass's pictures are kept in `pics/v1/`.

## The principle, as К1 has it, and what is new

К1's way is kept whole: the places are written in our scene, divided by our body's size against SOMA's (k), and
given to Kimodo as its own hand constraint — a whole pose, its pelvis where the person should be, its arm turned by
plain two-bone IK so the palm is on its place with the hand turned as Kimodo turns a hand there (taken from a free
take); Kimodo makes the body between; a small arm correction on our body takes the palm the last centimetres
(`contact-figure.js`, copied from К1). New here:

1. **A moving thing gives several places over time, each a constrained frame with its own pose.** The door's handle
   at the shut door and along its arc as the door opens (0°, 0°, 25°, 50°, 70°); the cup where it stands, at the
   lips, where it is put back; the box's two sides on the floor and on the table. Between them Kimodo moves freely.
2. **The thing follows the hand while it is held** (`holds` in `scenes.json`, `moving.js`). A cup or a box keeps
   the place relative to the hand (one palm's frame; for two hands, the middle between the palms, turned from the
   right palm to the left) that it had the frame it was taken; let go, it stays where it was. A door turns about its
   hinge at the angle of the hand on its handle; let go, it swings on, slowing (a third of a second to lose two
   thirds of its speed, up to its stop) — a door pushed open does that; the person is not moved by it.
3. **A contact's place can depend on Kimodo's hands**, so it is read off Kimodo's pose before any hand is moved
   (the one change in `contact-figure.js`):
   - a door's handle: on its arc about the hinge, at the angle Kimodo's palm is at (never behind shut);
   - a box held in both hands: each side from the middle between Kimodo's two palms, so the palms stay the box's
     width apart; weighed from where it lies (while the hands are on it on the floor, which Kimodo holds still) and
     towards where it is put (15 frames before the hands are asked there), so the box comes down on its place;
   - a cup at the mouth: the rim's point nearest the face, as the hand holds the cup in Kimodo's pose, taken to the
     lips of this body (a skin vertex found once), 1 cm in front of them.
4. **The hand's turn is part of the place.** For a cup or a box Kimodo's own turn from a free take works (palm
   towards the cup, palms towards the box's sides). For a door handle it did not: with no grip, Kimodo's fingers
   stick out straight, and a hand in front of the lever put them through the leaf. The turn is written as the hand
   would hold a lever with straight fingers: on top of it, fingers down behind it, palm facing down and back
   (`hand_to` in `tools/plan.py`). For the drink, the turn of taking the cup tilted 40° with the cup.
5. **Chains** (К1: a walk and then the action, made with `after`, plays far more naturally than one motion with the
   action at its end). The door and the cup go on from К1's own `table-walk` (copied, not ordered again: she walks
   and stops 1.88 m on); its `startsAt` for `after: 5` is known from К1, (−0.0237, 2.0937). The box is one motion of
   three chained prompts, as its free take was.

## Second pass: the hand closed, the mug in the fist, the box put down standing, the chair

1. **Fingers.** Our body's skeleton (SOMA77, as the engine skins it) has every finger: Thumb1–3, Index/Middle/Ring/
   Pinky 1–4. Kimodo gives them one relaxed curl. Now, while a thing is held, each finger's three joints after the
   palm (2, 3, 4; the thumb's 1, 2, 3) are turned towards the palm's side by a few fixed angles per thing, about the
   axis across the finger as it lies, weighed in over 8 frames before the hand takes it and out over 8 after it lets
   go (`curl` in `contact-figure.js`; the angles in `holds[].grip` in `tools/scenes.py`): round the mug (1.0/1.1/0.7
   rad, the thumb 0.4/0.5/0.3), hooked over the lever (1.2/1.2/0.8), over the chair's top bar (1.0/1.1/0.7), the box
   only a little (0.15/0.25/0.2: the palms press its sides). Nothing is measured
   against the thing — a simple curl, not a solver; with the correction off ("с поправкой") the fingers stay Kimodo's.
   With the fingers hooked, the door's face is no longer pierced while the hand is on the lever (only for 2 frames
   as the hand comes in); the fingers go up to 1.3 cm into the mug where they close round it.
2. **The mug in the fist, upright.** With the fingers closed it sits in the hand. It is kept upright while carried —
   turned about its own middle, so it stays in the fist (the wrist does that) — and tilts with the hand only as the
   "rim at the lips" touch is weighed in. Put back, it stands at 0.0° (was 1.1°).
3. **The box put down standing** (`box-3`): the put-down pose taken from the free take's carrying frame (legs nearly
   straight, pelvis 0.98 m), bent forward 12° at the waist so the palms reach, and the prompt "A standing person bends
   forward and places the box…". He stands and bends to put it down. Having let it go, Kimodo goes on down into a
   crouch under the table's edge (frames 270–299): the scene ends at frame 268 (`until`).
4. **The chair** (`chair-1`, the fourth scene): she walks up behind a chair pushed in under a table, takes the top of
   its back in both hands, steps back pulling it out 0.4 m, lets go. The chair slides with the middle between her
   palms, over the floor only and only away from the table (its height and turn kept); the palms' places follow the
   same rule from Kimodo's palms, so the hands stay on the bar. One take; it came out as asked.

## The scenes and their numbers

All on our bodies (`measures/<scene>.txt`: with the correction and without, over the frames each touch is held).

**Дверь (door).** The woman (moood-woman) walks up and stops half a metre before a door in a wall (0.86 m wide,
hinged on her left, lever at 0.98 m), takes the lever with her right hand, pushes the door away from her and walks
through; the hand stays on the lever till the door is ~68° open and comes off by itself (the frame it leaves the
handle's arc by more than 4 cm), the door swings on to ~80°. Kimodo's palm in its own space 2–7 cm from the asked
places along the arc; on our body 4.2 cm on average from the handle (max 7.2); with the correction 0.1 cm (max 1.2).
(First pass, straight fingers: while the hand was on the lever the fingertips went 0.5–1.7 cm into the door's face;
with the fingers hooked, not any more.) Reaching for the lever (frames 128–134, before the hand is held on it) Kimodo's fingertips go through the shut door's face; for a few frames as the hand comes off (frames 190–196) it passes 1 cm through the lever. Nothing else of the body
goes into the door or the wall.

**Чашка (cup).** The same walk to К1's table (0.74 m); she takes a mug standing on it with her right hand, drinks
standing, puts it back where it stood. Kimodo's palm on our body 5.6 cm from the cup when taking it, 4.3 cm when
putting it back; with the correction 0.0. At the mouth Kimodo's own hand (and so the rim) was 10–11 cm off our
woman's lips (SOMA's face scaled is not hers, and the hand's turn is Kimodo's): the correction is bigger here,
10.6 cm on average; the rim is then 1 cm from the lips (frames 205–225). The cup, put back, stands 0.1 cm into the
table, upright. The closed fingers go up to 1.3 cm into the mug.

**Коробка (box).** The man (moood-man) squats, takes a box 40×30×30 cm from the floor between his palms, stands,
carries it 3 m at the chest and puts it on a table 0.80 m high. Kimodo's palms on our body 2.7–3.0 cm from the
box's sides on average (max 6.4); with the correction 0.0. The box comes down on its place: 0.1 cm into the table,
tilted 0.7°. The fingers curl into the box's sides 2–3.5 cm (Kimodo's relaxed fingers; no grip). Putting the box
down his left thigh touches the table's edge, 0.9 cm at most (frames 225–260). Seen from the side, putting it down he bends the knees deeply
(the pelvis at 0.86 m, Kimodo's own way from the free take): it reads a little as half-sitting at the table.

**Стул (chair).** The woman walks up (К1's walk) behind a chair pushed in under a table, takes the top of its back
in both hands (palms 32 cm apart, 0.86 m high), steps back 0.45 m pulling it out 0.4 m, lets go. Kimodo's palms on our
body 5.3–6.0 cm from the bar on average (max 9.8); with the correction 0.0–0.1 cm (max 2.3, the left hand for a few
frames). The fingers hooked over the bar go through it (it is 3.5 cm thick: up to 1.7 cm in, its middle). Nothing
else goes into the chair or the table.

**The box with standing put-down (`box-3`).** As before, Kimodo's palms 2.7–3.1 cm from the box's sides, 0.0 with the
correction; the box lands 0.1 cm into the table, tilted 0.7°. Bending over the table to put it down his left
collarbone touches the box by up to 1.9 cm. Worse than `box-2` at the hands: as he puts it down (frames ~240–260) the
right hand's fingers go up to 6 cm into the box's side — the put-down pose's hand turn is the carrying one (from the
free take's frame 150), and its fingers point into the box; the curl on the box was made small (0.15/0.25/0.2) for
that, which did not change much (7.1 → 6.3 cm). Seen from the side it does not show; close up (`pics/box-close.png`) the hands at the box read badly: at the take
the palm is at the box's lower front corner with the fingers bent like a claw, at the put-down the left hand is at
its front corner rather than on its side. The box is the scene where the hands were improved least.

## What Kimodo does with these, and what cost tries (13 motions ordered, 16 asks — three failed "busy" and were asked again; every one in `motions/asks.json`)

- **Free takes** (no constraints): the door — it did not walk, reached a handle 0.7 m ahead at once and *pulled*
  the door, then walked through; the cup — it walked and **sat down on nothing** to drink (its data has people
  drinking from cups seated at tables); the box — squats, takes it, carries, puts it down: all by itself, well
  (the first ask failed "busy").
- **Door, one motion** (walk + door, `door-1`): walked the 2 m with the right arm stretched out for the handle the
  whole way. As a chain (`door-2`, after the walk): natural. Kimodo's hand turn in front of the lever put the
  fingers through the leaf — `door-3` with the hand hooked over the lever.
- **The door let go in the way**: let go at 50–65°, the door stood where her hand and left arm passed. Fixed by
  holding on as long as Kimodo's hand stays on the handle (it does, to ~68°) and letting the pushed door swing on.
- **The door's angle at the first touch**: Kimodo's palm comes a few cm past the shut handle; the door's angle is
  the handle's angle less the shut handle's (not less the palm's at that frame), so the door opens by those few
  degrees when the hand gets there instead of the hand holding a handle that isn't there.
- **Cup**: `cup-1` drank but half-sitting on nothing; `cup-2` with a standing drink pose (the hand-to-head relation
  of `cup-1` put on a bent standing pose) — the cup came beside the head; `cup-3` with the drink written as the
  cup's place (rim at the lips, cup tilted 40°) on an upright pose — the cup at the mouth, Kimodo within 2–3 cm in
  its own space.
- **Box**: `box-1` stood as close to the table as the free take: thighs under its edge, belly on the box; `box-2`
  stands 12 cm farther, but puts the box down with deep knees — from the side, sitting down on air beside the table;
  `box-3` with a standing put-down pose bent forward: stands and bends (then crouches after letting go: cut).
- **Chair**: `chair-1`, as asked, first time.

## The correction on top, and how big

Arms only, as К1: the upper arm and forearm turned, the hand's own turn kept. Door: 4.2 cm on average; cup: 4–6 cm
taking and putting, ~10.6 cm at the mouth; box: ~3 cm. The body, the path, the legs, the spine, the head are Kimodo's.

## What is weak

- **The grip is a fixed curl.** The fingers close by set angles, not onto the thing's surface: round the mug they
  go up to 1.3 cm in; on the box the palms press flat and the fingers bend only a little (2–3.5 cm into its sides,
  the box's figures as before); the thumb is turned the same simple way. It reads as holding; seen close it is not
  a fitted grip.
- **The mug is kept upright by a rule** while carried (not by Kimodo's wrist).
- **The drink's correction is big** (~10 cm): the plan gives Kimodo SOMA's mouth (scaled); our woman's mouth is
  elsewhere. A better plan would take the mouth from our body.
- **The door swings on by a rule** after it is let go (a decay, a stop at 100°), not by physics; and it opens by a few
  degrees at once when the hand first reaches the handle (Kimodo's hand comes a little past it).
- The places are planned for one body each (the woman: door, cup; the man: box), as in К1.
- Things are boxes (the cup a cylinder for the eye, a box for the numbers); the table is К1's.
- Each scene was looked at by stills and close-ups from two or more sides; the films were made and looked at in
  stills, not watched through at full speed.

- **The box scene is cut at frame 268**: after letting go Kimodo crouches under the table's edge.
- **The chair** slides by a rule (with the hands, over the floor, never forward); its legs are not checked against
  the floor or the table's legs.

## How to repeat

`python3 tools/plan.py <scene>` (door, cup, box, chair; the earlier takes: door_1, door_2, cup_1, box_1, box_2) writes
`plans/<scene>.json`; its `constraints` go to `make_motion` as they are, with the prompt in `motions/asks.json` (and
`after` table-walk, 5 frames, for the door and the cup); the motion's body data (`motion(key, data: "body")`, which
the client saves to a file when it is large) is copied to `motions/raw/<id>.json` and stored with
`python3 tools/store.py <id> [startsAt x z]`; `python3 tools/scenes.py` writes `scenes.json` (which motion each scene
plays: DOOR, CUP, BOX, CHAIR); `python3 tools/pictures.py [scene]` makes `measures/` and `pics/` again.
`python3 tools/peek.py <id>` prints a motion's pelvis and palms every few frames (Kimodo's space) — to read a free
take before writing constraints from it.

## Files

- `index.html`, `moving.js` — the page (scene choice, play/pause/scrub, the correction on/off, the numbers);
  `contact-figure.js` — К1's figure with the touch step (places read before any hand moves); `scenes.json`.
- `tools/` — `kimodo.py`, `pose.py`, `kimodo_neutral.json`, `store.py`, `sheet.py`, `shots.cjs` (copied from К1);
  `plan.py`, `scenes.py`, `report.py`, `pictures.py` (copied and changed); `peek.py` (new).
- `motions/` — every motion used, in the engine's format with its ask; `motions/raw/` — the studio's data of every
  take, kept; `motions/asks.json` — every ask with what came of it. `plans/` — the constraints as sent, per take.
- `measures/`, `pics/` — numbers, sheets, close-ups, films.

## History

2026-11-12, at the orchestrator's request (Pavel's direction: other kinds of things and motions after К1). Free takes
of the three; the door as one motion, then as a chain, then with the hand hooked over the lever; the cup with the
drink seated, then standing beside the head, then with the cup's rim at the lips; the box at the free take's
distance, then a step back. Second pass (the same day, asked after the first was looked at): the fingers closed round
what is held, the mug kept upright in the fist, the box put down standing (`box-3`), the chair (`chair-1`). 13 motions
ordered in all (16 asks, three "busy" asked again), К1's walk reused for three scenes.
