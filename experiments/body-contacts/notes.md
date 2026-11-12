# К2 — the body against things: a back on a wall, feet on steps and a hand on a rail, lying on a bed, forearms on a table

Pavel's task, after К1 (`experiments/contacts/`, a palm laid on a still surface once): other kinds of things and of
motions — contacts of the body, and a hand that slides. "If the model understands some motions badly, never mind —
try other similar tasks and motions; the main thing is to make the principle work." Asked, in this order: leaning on a
wall; stairs with a handrail; lying down on a bed and getting up; sitting at a table with the forearms on it; if there
is strength left, stepping over something and sitting on the floor against a wall.

What came out: the first four, end to end, on the early engine (`engine/`) and moood-woman (1.585 m), in
`index.html`. The fifth was not tried (see "Not done"). The principle is К1's and it held for all four: the place is
written in our scene, carried into Kimodo's space (÷ k, k = 0.896 for the woman), sent as Kimodo's own constraint —
only now the constraint is not a hand but the whole body (a lean, a lying), the feet (stairs), the pelvis with the
feet (sitting), the hands with the pelvis (forearms on the table), and a hand at many frames (the rail). A correction
on top is needed only on the stairs (feet and the hand on the rail); elsewhere Kimodo's body is shown as it is.

## The principle for the body, step by step (what is new against К1)

1. **Which constraint carries the place.** Kimodo has `fullbody` (every joint's place at a frame), hand and foot
   constraints (`left-hand`, `right-foot`, `end-effector` with any of LeftHand, RightHand, LeftFoot, RightFoot), and
   `root2d`. There is no constraint "the back here": a body part other than the hands and feet is placed by a
   **`fullbody`** pose (wall, bed) — or, because every hand/foot constraint also holds the pelvis's place, height and
   heading (К1's finding), by the **pelvis of a foot or hand constraint** (sitting on the bed's edge: `end-effector`
   of both feet; sitting at the table: of both hands).
2. **The pose comes from Kimodo, placed by its skin.** As in К1 the pose is a frame of a motion Kimodo made by itself
   with the posture wanted (`*-free` in `motions/asks.json`): leaning back on nothing (`wall-free`), climbing stairs
   on nothing (`stairs-free`), lying flat on the floor (`lie-free`), sitting with the forearms on a table
   (`desk-free`), sitting on a chair (К1's `chair-free`). New: it is put against the thing by **SOMA's skin**, not by
   joints — `tools/somaskin.py` poses Kimodo's own SOMA skin (as the engine's `tools/motions.py` does for the lowest
   point), and `tools/plan.py: placed_against` moves the pose until the skin of the named parts (the back; the
   buttocks and thighs; the back and pelvis) just touches the plane of the thing (the wall's face, the mattress top,
   the seat).
3. **Feet on steps.** For each stance of `stairs-free` (the middle of each time a foot stands still), that frame's pose
   is moved up and ahead so the foot's skin stands on our step: the sole on the step's top, the toes 5 cm short of
   the next riser (people put the ball of the foot on a step; SOMA's foot, 25 cm, is longer than the 24.6 cm tread);
   sent as `left-foot`/`right-foot` at that frame (5 each). The last frame: Kimodo's own standing pose with both feet
   on the landing (`end-effector` of both feet).
4. **A sliding hand** is Kimodo's hand constraint at many frames: every half second (10 frames, Kimodo takes < 20 per
   type), the pose of that moment (moved as the stances around it) with its right arm turned so the palm lies on the
   rail 12 cm ahead of the shoulder, the hand turned palm down along the rail. Between those frames Kimodo keeps the
   hand near the rail by itself (3–6 cm). The first take, with five frames a second apart, let the hand leave the
   rail by up to 20 cm between them.
5. **Chains.** Long scenes are several motions, each made with `after` the one before (wall: lean, then push off;
   bed: sit, lie, get up; table: sit, get up). A constraint of the next motion is written in its own space, whose
   origin is the studio's `startsAt` — known only after it is made (К1). New: it is close to **the middle of the two
   hip joints** at the earlier motion's frame n − 5 (`plan.py: after_origin`) — 0.6 cm off for a standing person
   (wall-off), but 5 cm off for a seated one (bed-lie): the lying pose landed 5 cm from where it was planned (still on
   the bed's middle). Where the next motion needs only "stand there" (`root2d`), that is enough.
6. **On our body** the page measures every frame (`tools/shots.cjs` → `measures/*.json`, summed by `tools/report.py`
   into `measures/*.txt`): for each "touch" (a part of the body resting on a thing) the nearest of its skin to the
   thing's faces, negative when inside; for each foot, its sole against the step under its ankle; for the hand on
   the rail, the palm's middle to the rail's top and the hand's skin to the rail; and everything of the body inside
   any thing.
7. **The correction** (`contact-figure.js`, К1's, with one step added; off with "с поправкой" or `?raw`):
   - a foot standing on a step: in it — lifted out; over it by less than 5 cm — let down onto it (the less, the
     farther: a foot in the air stays Kimodo's); by the leg's two bones, the knee in its own plane, the foot keeping
     Kimodo's turn (`standOne`). The step is the one under the ankle; toes over the next riser are not "lifted for";
   - the hand on the rail: К1's arm correction, its place the rail's top (+ the palm's thickness, 2.2 cm) at the
     point of the rail nearest to Kimodo's own palm, so the hand slides as Kimodo slides it.

To make another scene: write the thing and the place in `tools/plan.py`, choose a free take with the posture, run
`python3 tools/plan.py <scene>`, order it (`make_motion`, the constraints from `plans/<scene>.json`, a prompt saying
the same), put the studio's body data in `motions/raw/<id>.json` (`tools/keep_raw.py`), `python3 tools/store.py <id>
[startsAt x z]`, describe the scene in `tools/scenes.py` (which motions: `tools/scene_list.json`), look, then
`python3 tools/pictures.py <scene>`.

## The scenes and their numbers

All on our woman; the numbers are in `measures/<scene>.txt` (the "held" frames are the ones Kimodo was given).

**Спиной к стене (wall).** The woman walks 2.4 m to a wall (its face 2.6 m ahead), turns round and leans back on it;
stands 4 s; pushes off and walks away 1.4 m. Two motions (`wall-lean`, then `wall-off` with `after`). The whole lean
pose was given at frames 95, 150, 209. Held (95–209): the back's skin 0–0.6 cm off the wall (mean 0.2), at most 0.1 cm
in it (12 frames). Nothing else of the body touches anything. No correction.

**Лестница с перилами (stairs).** Ten steps, 14 cm high and 22 cm deep, a landing; a rail 80 cm over the step fronts
on her right. One motion, 6 s. The right palm, weighed in from frame 25 to 160: Kimodo's own 4.6 cm from the rail's
top on average (max 8.7); corrected onto it (0.0); the hand's skin then 0.1–2.5 cm into the rail (the curled
fingers). Feet, over the frames each stands (sole within 5 cm of its step): Kimodo's soles from 7.4 cm in the step to
4.8 cm over it (mean 0.4 over); corrected 0–4.8 cm over (mean 0.8–1.0: a foot just landing or lifting, let down only
partly). The toes go into the next riser in many frames by 1–3 cm, at the first step 7 cm (frame 19). Without the
correction the hand's skin is 2.5 cm in to 8 cm off the rail.

**Лечь на кровать — second pass (bed2, shown first on the page).** The same bed and the same three steps, `bed2-sit`, `bed2-lie`,
`bed2-up`. Sitting: the pelvis asked 9.3 cm higher and 4.5 cm further in (Kimodo's metres) than in the first pass;
Kimodo again sat ~6 cm under what was asked, which now lands right: the buttocks and thighs 0.4 cm over to 1.0 cm
into the mattress (150–179; the first pass 7.8–8.6 cm in). Lying: the whole pose of `lie-back-free` (on the back, the
arms along the body), its origin read off a probe (exact): at the held frames (305–354) the back 1.9 cm in to 3.8 cm
over (mean 0.2 in), the head 0.7 in to 3.9 over; between them, after lying down (frames 210–300), the pelvis 4–8 cm
in. Getting up (its origin read off a second probe): into the mattress up to 9 cm (the pelvis, rolling up, frame
440), a shin and a foot 6–7.6 cm into the bed's frame for a few frames (around 445–461) as she swings the legs off —
as in the first pass. To the eye (`pics/bed2-sheet.png`, `bed2-close.png`): she lies straight on her back, arms
along the body — reads as a person lying on a bed; on the way down one leg goes up for a moment. No correction.

**Лечь на кровать — first pass (bed, kept beside).** A bed across the way (mattress top 48 cm, its near side 2.2 m ahead). Three motions:
`bed-sit` (walk up, turn, sit on the edge: pelvis and feet given at 150, 179), `bed-lie` (`after`; lying pose given at
its 130, 179), `bed-up` (`after`; only "stand there" at the end). Sitting (150–179): the buttocks and thighs 7.8–8.6 cm
into the mattress (Kimodo sat 5 cm lower than asked). Lying (clip 305–354): the back 0.7–1.4 cm over the mattress,
the head 1.2–2.3 cm. Into the mattress over the whole clip: up to 9 cm (sitting down, rolling up to get up: the
pelvis, thighs, an upper arm, a hand, the feet as she swings them off); a foot 6.6 cm into the bed's frame for a few
frames while getting up (frame 464). No correction.

**За столом (desk).** A chair (seat 42 cm) beside her, a table (top 72 cm). Two motions: `desk` (step to the chair,
sit, forearms on the table: pelvis and hands given at 120, 179), `desk-up` (`after`; "stand there" beside the chair).
Held (120–240): the forearms 0–1.4 cm over the top (mean 0.7); the buttocks 2.5 cm into the seat. On the way: the
right thigh and pelvis 2 cm into the chair's back (frame 33, 13 frames), feet and shins up to 1.7 cm into the chair's
legs, a hand 1.7 cm into the table top for a moment (frame 57). No correction.

## What Kimodo did, and what it did badly

- **Without constraints it did each posture**, but not in our place: it leaned back on nothing; climbed 10 steps of
  its own irregular height (14–18 cm) on nothing; "lay down on a sunbed" as a recline with the feet on the floor
  (`bed-free`, not used: no bed lying in it); sat at a table with the forearms on it by itself (`desk-free`). Its
  data has these ("A person stands leaning back on a wall", stairs, "walking up to a bed, sitting on it, and then
  lying", "seated by the table" — searched in `timelines.jsonl` before writing prompts).
- **Wall.** With the lean held at the end only (two frames), Kimodo leaned back 5 cm *through* the wall first and
  slid out by frame 160 (`wall-lean-try1`); held from the moment the back arrives (three frames), it stays 0–0.3 cm
  off the wall. The push-off, without a constraint, stayed leaning 3 s more (`wall-off-try1`); with a `root2d` "be
  25 cm away at 1.3 s, 1.6 m at 4 s" it pushes off at once.
- **Stairs.** The first take put the ankle 7 cm behind the step's front: the toes went 14 cm into the next riser,
  and the hand, given every second, left the rail by 20 cm between; the last two steps came 5–17 cm high. The second
  (toes 1.5 cm short of the riser in Kimodo's space, the hand every half second): feet on their steps in Kimodo's
  space, hand 3–6 cm off the rail; on our body the toes still 3–4 cm into the risers (our woman's feet are longer than
  SOMA's scaled), and at the end she went on lifting her feet as if there were more steps. The third (toes 5 cm
  short in our world, both feet on the landing at the last frame, "… and stops at the top") is the one shown.
- **Bed.** She sat on the edge 5 cm lower than asked (the seated pelvis is not held exactly) — on our body her
  buttocks go 8–9 cm into the mattress. Lying: Kimodo turned on the bed, swung the legs up (higher than one would)
  and lay along it, flat, arms over the head, legs apart (that is how `lie-free` lay). Getting up — only "stand
  there" at the end — it rolled up, sat, put the feet down and stood: by itself.
- **Table.** Right away: steps to the chair, sits, forearms on the top, 0–1.5 cm over it; gets up and steps out
  with only "stand there".

## What is weak

- **Soft things.** Where the body sits or lies, on our body it goes into the seat and the mattress: the chair
  2.5 cm; the bed's edge 8–9 cm in the first pass, 0.7–2.5 cm in the second (the pelvis asked higher); lying in the
  second pass 2–5 cm at the held frames and up to 8 cm between them; getting up up to 8–9 cm (the pelvis, a thigh)
  in both, and a shin or foot 6–8 cm into the bed's frame for a few frames as she swings her legs off. On a mattress
  that reads as sinking into it; a hard bench would show it as passing through. The things are boxes; nothing
  deforms.
- **The first bed's lying pose is a starfish** (arms over the head, legs apart: `lie-free`). The second pass asked
  for two more free lyings: "on the back, the arms by the sides" (`lie-back-free`: straight, arms along the body —
  used) and "on the side, the knees bent" (`lie-side-free`: curled up, the head on the floor — not used). On the
  way down Kimodo still lifts one leg high for a moment (frame ~225).
- **Fingers go into the rail** by about 2.4 cm: Kimodo's fingers are curled, and with the palm on the rail's top they
  curl round it — there is no grip (as in К1, no fingers). From afar it reads as holding the rail; close up the
  fingertips are inside the wood.
- **Toes in the steps**: with the correction the soles stand on the steps; what still goes into the steps (1–3 cm in
  many frames, 7 cm at frame 21) is mostly the *swinging* foot's toes catching a step's nose on the way up, not a
  standing foot. A fourth take with the standing feet 3 cm further back (`stairs4`, toes 8 cm short of the riser) was
  not better (max 7.2 cm, frames over 2 cm 38 against 34) and is not used. Kimodo's swing does not know our steps'
  noses; holding the swing would need constraints between the stances (not tried).
- **The `after` origin** is known exactly only after the motion is made; the hip-joints guess is 0.6–5 cm off
  (the first bed's lying landed 5 cm from the plan). The second pass orders first a 0.5 s probe `after` the earlier
  motion (`bed2-probe`, `bed2-probe2` in `motions/asks.json`) and reads its `startsAt`: exact, one cheap order (the
  way found by the agent who repeated К1 on other bodies).
- **The desk:** at the start she steps between the chair and the table; her pelvis brushes the chair's back (1.9 cm)
  and her feet touch the chair's legs (1–1.7 cm) for a few frames.
- **The wall** is held by the whole body: from frame 95 to the push-off she stands as Kimodo's own lean, only
  breathing a little; Kimodo's lean touches with the shoulder blades and not the buttocks (the buttocks 9 cm off) —
  that is how it leaned on nothing.
- One body (the woman); another body needs its own orders or a bigger correction (К1's note holds).
- The orders were made against the studio's GPU shared with other agents; four failed with "busy" and were asked
  again (same keys).

## Not done

- **Stepping over / onto a box, sitting on the floor against a wall** (item 5): not tried in either pass — the
  four scenes and the second pass took the time; the way would be the stairs' (feet on the box/kerb) and the wall's plus `lie-free`'s floor sitting.
- Films are every third frame (10 a second): software WebGL draws a frame in ~2 s.

## Which numbers are the woman's, and how to get them for another body

Everything here was planned for moood-woman (k = 0.896, `K_WOMAN` in `tools/plan.py`). For another body:

- **k** — its hip height over SOMA's (`engine/src/retarget.js`); every place in our world is divided by it. It
  assumes SOMA's proportions: a body whose arms (or legs) are short for its hips gets its hands (feet) farther off
  than the few centimetres the correction can take (the other-bodies agent saw 22 cm on a 2.31 m body). The hand on
  the rail is the most exposed here.
- **Where a pose is put against a thing** is read off **SOMA's skin** (`somaskin.py`, `placed_against`), so it
  carries to any body only up to the difference between SOMA's skin scaled and that body's skin: for the woman
  her back reaches 0.5 cm further (the wall: the plane put 0.6 cm off — `face − 0.006`), her buttocks 3.5 cm lower
  (the bed's edge: `0.035 / k` in `bed_sit`), her feet are longer (the stairs: `toes_short = 0.05`). These three
  numbers are hers: measure them on the page for another body (the "touches" and "feet" lines; `?raw`) in a first
  take, write them in, order again.
- **What Kimodo does not hold exactly** is not the body's but Kimodo's: it sits ~5.4 cm lower and 4.5 cm short of an
  asked seated pelvis on a bed's edge (in its metres; `bed_sit(lift=True)` adds that). Likely the same for any body,
  not checked.
- **The things' sizes that follow the pose** (the table's edge and height from the seated forearms, `desk()`) are
  the woman's pose's: for another body either re-read them from the pose placed for that body, or keep the table and
  let the correction take the rest (no hand correction is wired for the table here: the forearms lay 0–1.4 cm over
  it).
- **Frames** (the stances of `stairs-free`, the held frames, when the hand on the rail is weighed in, `HAND_ON`) are
  Kimodo's timing, not the body's: they carry as they are, but `HAND_ON` was read off this take's numbers.
- **Where the way stops working:** a part of the body other than the hands, feet and pelvis can only be placed by a
  whole-body pose (no "back" constraint); a pose Kimodo has not made by itself on nothing cannot be put anywhere
  (the sunbed "lying" was a recline); a contact between the held frames is Kimodo's (the swinging foot through a
  step's nose; the body sinking into the mattress between two held lying frames); fingers do not grip.

## Files

- `index.html`, `body-contacts.js` — the page (a copy of К1's `contacts.js`, changed: things as boxes with a tilt, a
  rail, touches, feet); `contact-figure.js` — К1's figure with `standOne`; `scenes.json` — made by `tools/scenes.py`.
- `tools/plan.py` (scenes → constraints; `plans/*.json` — what was sent), `tools/somaskin.py` (SOMA's skin in Kimodo's
  space), `tools/kimodo.py`, `tools/pose.py` (from К1), `tools/keep_raw.py`, `tools/store.py`, `tools/shots.cjs`,
  `tools/report.py`, `tools/sheet.py`, `tools/pictures.py` (all of `pics/` and `measures/` again).
- `motions/asks.json` — every motion ordered (17 in the first pass, 8 in the second, and К1's two free takes used): key, prompt, seconds,
  constraints (or the plan), `after`, `startsAt`, what came of it. `motions/<id>.json` — the motions played.
  `motions/raw/` — the free takes' data the poses came from (the others can be fetched again by key).

## History

2026-11-12, made at the orchestrator's request from Pavel's task (after К1). Order of work: four free takes (wall,
stairs, sunbed, table) and searches of Kimodo's descriptions; the wall (two takes of the lean, two of the push-off);
the stairs (three takes; the foot correction written after the second); the bed (sit; the sunbed recline was not a
lying, so a free lying on the floor was ordered; lie; get up); the table (sit; get up). 17 orders, 4 "busy" asked
again.

Second pass (the coordinator, from Pavel, after looking: the bed is weak to the eye; the bed's edge sinks; toes in
the risers; the fifth scenes if there is strength): two free lyings (back, side); the bed's sitting asked 9.3 cm higher
and 4.5 cm further in; a probe for the exact origin; the lying on the back; a probe; getting up — the second bed
(`bed2`), the first kept beside; a stairs take with the feet 3 cm further back (not better, not used). 8 orders.
