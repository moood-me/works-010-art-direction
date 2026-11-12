# Things that move with the hand: a door, a cup, a box

The next step after К1 (`experiments/contacts/`, the principle and what it cost: read its `notes.md` first). There
everything touched stands still; here the thing moves with the hand. Pavel's words this stands on: "If the model
understands some motions badly, never mind — try other similar tasks and motions; the main thing is to make the
principle work." Asked (by the orchestrator, from Pavel): other kinds of things and motions — a door opened by its
handle and walked through; a cup taken from a table, drunk from, put back; a box taken from the floor in both hands,
carried, put on a table; if strength is left, something pushed or pulled along the floor.

What came out: the door, the cup and the box, each end to end, on the early engine (`engine/`) and its Anny bodies,
in `index.html` (served from the repository's root). The fourth (pushing or pulling) was not tried — see the end.

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

## The scenes and their numbers

All on our bodies (`measures/<scene>.txt`: with the correction and without, over the frames each touch is held).

**Дверь (door).** The woman (moood-woman) walks up and stops half a metre before a door in a wall (0.86 m wide,
hinged on her left, lever at 0.98 m), takes the lever with her right hand, pushes the door away from her and walks
through; the hand stays on the lever till the door is ~68° open and comes off by itself (the frame it leaves the
handle's arc by more than 4 cm), the door swings on to ~80°. Kimodo's palm in its own space 2–7 cm from the asked
places along the arc; on our body 4.2 cm on average from the handle (max 7.2); with the correction 0.1 cm (max 1.2).
While the hand is on the lever, the fingertips touch the door's face, 0.5–1.7 cm into it (straight fingers, no grip).
Reaching for the lever (frames 128–134, before the hand is held on it) Kimodo's fingertips go through the shut door's face; for a few frames as the hand comes off (frames 190–196) it passes 1 cm through the lever. Nothing else of the body
goes into the door or the wall.

**Чашка (cup).** The same walk to К1's table (0.74 m); she takes a mug standing on it with her right hand, drinks
standing, puts it back where it stood. Kimodo's palm on our body 5.6 cm from the cup when taking it, 4.3 cm when
putting it back; with the correction 0.0. At the mouth Kimodo's own hand (and so the rim) was 10–11 cm off our
woman's lips (SOMA's face scaled is not hers, and the hand's turn is Kimodo's): the correction is bigger here,
10.6 cm on average; the rim is then 1 cm from the lips (frames 205–225). The cup, put back, stands 0.1 cm into the
table, tilted 1.1°. The hand goes 0.3 cm into the cup while holding it.

**Коробка (box).** The man (moood-man) squats, takes a box 40×30×30 cm from the floor between his palms, stands,
carries it 3 m at the chest and puts it on a table 0.80 m high. Kimodo's palms on our body 2.7–3.0 cm from the
box's sides on average (max 6.4); with the correction 0.0. The box comes down on its place: 0.1 cm into the table,
tilted 0.7°. The fingers curl into the box's sides 2–3.5 cm (Kimodo's relaxed fingers; no grip). Putting the box
down his left thigh touches the table's edge, 0.9 cm at most (frames 225–260).

## What Kimodo does with these, and what cost tries (11 motions ordered, 12 asks — one failed "busy" and was asked again; every one in `motions/asks.json`)

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
  stands 12 cm farther (the put pose bent 12° so the palms reach).

## The correction on top, and how big

Arms only, as К1: the upper arm and forearm turned, the hand's own turn kept. Door: 4.2 cm on average; cup: 4–6 cm
taking and putting, ~10.6 cm at the mouth; box: ~3 cm. The body, the path, the legs, the spine, the head are Kimodo's.

## What is weak

- **No grip.** Kimodo's fingers are in its relaxed curl: a hand on a lever, a cup, a box lies on it; the fingers go
  0.5–3.5 cm into the thing where a real hand would close around it. The hand on the cup is a flat hand at its side.
- **The drink's correction is big** (~10 cm): the plan gives Kimodo SOMA's mouth (scaled); our woman's mouth is
  elsewhere. A better plan would take the mouth from our body.
- **The door swings on by a rule** after it is let go (a decay, a stop at 100°), not by physics; and it opens by a few
  degrees at once when the hand first reaches the handle (Kimodo's hand comes a little past it).
- The places are planned for one body each (the woman: door, cup; the man: box), as in К1.
- Things are boxes (the cup a cylinder for the eye, a box for the numbers); the table is К1's.
- Each scene was looked at by stills and close-ups from two or more sides; the films were made and looked at in
  stills, not watched through at full speed.

## Not done: pushing or pulling along the floor

Not tried (time). The way would be the same: a chair's back as the place of both hands at several frames as it slides
out, the chair following the hands over the floor only (its height and turn kept), the pelvis stepping back.

## How to repeat

`python3 tools/plan.py <scene>` (door, cup, box; the earlier takes: door_1, door_2, cup_1, box_1) writes
`plans/<scene>.json`; its `constraints` go to `make_motion` as they are, with the prompt in `motions/asks.json` (and
`after` table-walk, 5 frames, for the door and the cup); the motion's body data (`motion(key, data: "body")`, which
the client saves to a file when it is large) is copied to `motions/raw/<id>.json` and stored with
`python3 tools/store.py <id> [startsAt x z]`; `python3 tools/scenes.py` writes `scenes.json` (which motion each scene
plays: DOOR, CUP, BOX at its top); `python3 tools/pictures.py [scene]` makes `measures/` and `pics/` again.
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
distance, then a step back. 11 motions ordered (12 asks, one "busy" asked again), К1's walk reused for two scenes.
