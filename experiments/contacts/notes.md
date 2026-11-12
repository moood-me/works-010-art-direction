# К1 — contacts: a person comes to a place and touches it

Pavel's task (docs/requirements.md, "After the engine is finished"): motions that come to the right places. A person
walks up to a table and leans on it, the hands on the table — a second before the stop the hands are there, at the
last frame still there; one character puts a hand on another's shoulder; a character sits down in an armchair with
armrests of a known height, the hands on the armrests. Motions from Kimodo, not formulas; the body moves only along
Kimodo's path; joins made by Kimodo (`after`); no grips, no fingers.

What came out: all three scenes as asked, on the early engine (`engine/`) and its Anny bodies, in `index.html`.
Kimodo makes the walk up, the stop, the lean, the turn and the sitting, the elbows and the hands' own turn, **given the
places of the palms and of the pelvis as its own constraint**. On our bodies Kimodo's palm lands 4–6 cm off its place
(other arm lengths and shoulders than SOMA's); a small correction of the upper arm and forearm takes it the rest of
the way. The numbers are below and in `measures/*.txt`.

## The principle, step by step (how to do it for another scene)

1. **The scene in our world.** Metres, y up; the person (an engine character) starts at the origin facing +z. The
   thing and the place the hand goes to are written there: the table top 0.74 m high, its near edge 2.2 m ahead, the
   palms 14 cm in from the edge, 38 cm apart (`tools/plan.py: table`).
2. **Into Kimodo's space.** The engine carries Kimodo's path scaled by k = our hip height / SOMA's
   (`engine/src/retarget.js`); so a place x in our world is x / k for Kimodo (the woman: k = 0.896, the man 1.015).
3. **A hand constraint is a whole pose.** Kimodo's `left-hand`/`right-hand`/`end-effector` constraint
   (`kimodo/constraints.py`, `EndEffectorConstraintSet`) is `{local_joints_rot [T, 77, 3] axis-angle, root_positions
   [T, 3]}`: Kimodo runs its forward kinematics on that pose and then holds, at those frames, the hand's joints
   (wrist and all finger joints) where the pose has them, the wrist's turn — **and the pelvis's place, height and
   heading**. So "the hands here" always comes with "the body there", and that is a good thing: it is where we say
   how the person stands (or sits) while touching.
4. **The pose: Kimodo's own, moved.** We take a frame of a motion Kimodo made by itself (standing; sitting) and put
   its pelvis where the person should be (`tools/pose.py: placed`), then turn its arms by plain two-bone IK so each
   palm lands on its place, with the hand turned as Kimodo turns a hand lying on something — taken from a frame where
   Kimodo laid hands on a table by itself (`hand_turn_from`). Only the hands and the pelvis of this pose reach Kimodo;
   the rest of it is just the means of putting the hands there. Kimodo then makes the body between: the lean of the
   back, the bend of the knees, the elbows, the head.
5. **Frames.** Pavel's "a second before the stop, and still at the last frame": the constraint at two frames, 30
   frames apart, the last one the motion's last (the table: lean frames 89 and 119 of 120; the shoulder: 119 and 179;
   the armchair: 134 and 209 — sitting from 4.5 s on).
6. **Chains.** A walk followed by a lean came out better as two motions than as one (one motion with the lean
   constraint walked stooped all the way): `table-walk` (a walk with a `root2d` constraint stopping it 2.05 m on),
   then `table-lean` made with `after: {key: walk, frames: 5}`. A motion made with `after` has its own origin: the
   studio's `startsAt`, **not** exactly the walk's pelvis at frame n−5 (5 cm apart here). It depends only on the
   earlier motion and `frames`, so we read it off a first take and wrote the lean's constraint in it again.
7. **On our body.** The motion is carried onto the body by the engine as it is; then `contact-figure.js` (the
   engine's `Figure`, copied, one step added) finishes each touch:
   - the palm's middle (between the wrist and the knuckles of the index and little fingers) is brought onto its place
     by turning the upper arm and forearm (the elbow bending in the plane Kimodo bent it in), the hand keeping the turn
     Kimodo gave it; weighed in over the 15 frames after Kimodo's own palm comes within 7 cm of its place, then held;
   - on a surface (a table top, an armrest) the height is not the palm's middle but the hand's lowest skin, put on the
     surface (how far the skin reaches under the palm's middle is read off the skinned hand each frame);
   - a hand over a surface is kept from going under it, and a hand near the other person is moved out of their skin,
     on the way and while it lies there (Kimodo, making one person, knows nothing of the table or of the other; and a
     hand turned as Kimodo turned it can dip its fingers into a sloping shoulder: there the palm stays 1.7 cm from the
     point, lying on the skin around it).
   Off with "с поправкой" on the page, or `?raw` in the address.
8. **Measured** on the page every frame (`tools/shots.cjs` with `measure`, summed up by `tools/report.py`): the palm's
   distance to its place, Kimodo's and corrected; the hand's lowest skin against the surface or the other's skin; the
   deepest point of the body inside each part of a thing (boxes) and inside the other person (by the nearest vertex
   of their skin and its normal).

To make another scene: write its places in `tools/plan.py` (a function like `table`), choose a frame of a Kimodo
motion with the posture you want (standing, sitting, crouching…) and one with the hand turned as it should lie, run
`python3 tools/plan.py <scene>`, give the constraint to `make_motion` with a prompt saying the same thing, keep the
motion (`motions/asks.json`, `python3 tools/store.py <id>`), describe the scene in `tools/scenes.py`, measure, look.

## The scenes and their numbers

All numbers on our bodies, over the frames the touch is held (`measures/<scene>.txt`).

**Стол (the table).** The woman (moood-woman, 1.585 m) walks 2 m to a table 0.74 m high, stops, leans and puts both
hands on it; holds 1.4 s. Kimodo's palms (its own space): 2–3 cm from their places, pelvis 3 cm. On our body:
Kimodo's palm 4.6 cm from its place on average (max 5.8), the hand's skin hovering 3.4–5.8 cm over the top; with the
correction 0.0 cm, the skin on the top. On the way Kimodo's right hand cut 1.7 cm into the table's edge (frames
155–166); the "over the surface" step keeps it out (0.0 cm). Nothing else goes into the table.

**Рука на плечо (the shoulder).** The man (moood-man, 1.768 m) walks 1.4 m to the woman, who stands in her own Kimodo
motion facing him, and puts his right hand on the top of her left shoulder; holds 2 s. The place is a point of her
skin, as the page plays her (`tools/other.mjs`), every frame; Kimodo was given it at the two frames.
Kimodo's palm on our body 4.7 cm from the point on average (max 6.7), its skin 0.1–2.6 cm over hers; with the
correction the palm's middle 1.7 cm from the point (max 1.9) — it lies on the skin around it: the hand's skin
0.2–0.4 cm over hers, nothing of it inside her. On the way, Kimodo's hand passes 4.2 cm into the edge of her
shoulder and upper arm (frames 100–110); kept out, 0.4 cm at most (frame 103). His body does not touch hers.

**Кресло (the armchair).** The woman walks 2 m, turns round, sits in an armchair (seat 0.42 m, armrests 0.62 m,
0.52 m apart inside) and puts her hands on the armrests; holds 2.5 s. Kimodo walked, turned and sat by itself.
Kimodo's palms on our body 4.1–4.2 cm from their places on average (max 5.1), the hands' skin 0.1–3.8 cm over the
armrests; with the correction 0.0 cm, the skin on the armrests. On the way down Kimodo's right hand cut 3.4 cm into
the armrest (frame 113): kept out, 0.0. The left thigh touches the inner side of the left armrest by 1.6 cm while she
sits down (frame 97, a few frames). Seated, the thighs go 3.5–4 cm into the front half of the seat (the buttocks
0–1 cm): as into a soft cushion; on a hard box seat it is a pass-through — said honestly. Nothing goes into the
backrest (the first take, before the pelvis was placed from the body's measures, went 6–8 cm into it).

## What Kimodo does badly, and what was done instead

- **Without constraints it doesn't do these at all.** "Walks to a table and leans on it with both hands" — it sat down
  at the table (its data has tables mostly with chairs); "leans forward to rest both hands flat on the table" — it
  stood with the hands in front, no lean; "places their right hand on the shoulder of someone in front" — it did not
  walk, stretched the arm forward for a second. "Armrests" is not in its data's descriptions; it sat with the hands on
  the seat, then on the lap. The constraint is what makes the touch; the prompt only has to agree with it.
- **One motion with a deep lean at its end walked stooped all the way** (`table-s0` in `motions/asks.json`); a walk
  and then a lean made with `after` is natural.
- **The first constraints came out absurd** (arms out, a crouch): Kimodo reads local rotations against its own
  neutral skeleton, a T-pose (`tools/kimodo_neutral.json`, from Kimodo's assets), not the SOMA skin's A-pose rest the
  engine carries bodies by (`engine/data/skeleton.json`). The studio's per-joint data is Kimodo's own global rotations;
  local = parentᵀ · own. With that, Kimodo puts the hands within 2–3 cm of where it is asked.
- **The hand's own place is good, the arm near it is Kimodo's**: in the shoulder scene the man's arm comes up nearly
  level, the elbow a little out — how Kimodo reaches a shoulder; the first take, standing 60 cm away, held the arm
  straight like a bar, so the plan has him stand 45 cm away. Kimodo knows nothing of the other person: his hand comes
  in through the edge of her shoulder for a few frames before it settles (see below).
- **Holding still**: at the held frames the pelvis is held too, so the person holds the pose; Kimodo still breathes
  and shifts a little between them.
- **Fingers**: SOMA's fingers are in Kimodo's relaxed curl; a hand "lies" with its palm and fingertips, no grip.

## The correction on top, and how big

Arms only (the upper arm and the forearm turned, the hand's own turn kept): the palm moved 4.6 cm on average at the
table (max 5.8), 4.7 cm (to 1.7 cm off the point, lying on the skin around it) at the shoulder, 4.1 cm at the armchair. The body, the path, the legs, the
spine, the head are Kimodo's. Weighed in over 15 frames once Kimodo's own palm is within 7 cm, so it finishes what
Kimodo did and never pulls a hand still on its way. The keep-out steps (a surface, another's skin) move the hand by
1–2 cm for a few frames on the way.

## What is weak

- The places are planned for one body each (the woman at the table and in the armchair, the man at the shoulder): the
  Kimodo motion is made for that body's size (k). Another body needs its own order (or a bigger correction).
- The `startsAt` of a motion made with `after` is known only after a first take; the plan takes it from there.
- The seated pelvis height and the backrest distance were read off our body in a first take (it sat 8 cm into the
  seat and 6–8 cm into the backrest); a scene with another chair needs that measure again (two numbers in `plan.py`).
- The things are boxes; contact is measured against boxes, and the other person against the nearest vertex of her
  skin (a coarse but honest test; it can miss a point between vertices).
- The camera "follows" only over the floor; there is no foot contact handling (the engine sets the body on the floor
  as a whole).
- Seen in the pictures: the armchair is crude (boxes); sitting, Kimodo keeps the knees wide apart.

## Files

- `index.html`, `contacts.js` — the page; `contact-figure.js` — the engine's Figure with the touch step;
  `scenes.json` — what the page plays (made by `tools/scenes.py`).
- `tools/kimodo.py` (Kimodo's data, its FK and constraint format), `tools/pose.py` (the constraint's pose),
  `tools/plan.py` (scenes → constraints; `plans/*.json` — what was sent), `tools/other.mjs` (the other person's
  shoulder as a place), `tools/store.py` (a studio motion → `motions/<id>.json`), `tools/shots.cjs` (pictures,
  films, numbers), `tools/report.py`, `tools/sheet.py`, `tools/pictures.py` (all of `pics/` and `measures/` again).
- `motions/asks.json` — every motion ordered: its key, prompt, seconds, seed, constraints (or the plan file they are
  in), `after`, and what came of it; `motions/<id>.json` — the motions used, in the engine's format, with their ask;
  `motions/raw/` — the studio's data of the free takes the poses were taken from.
- `measures/` — the numbers every frame, with and without the correction, and their summaries.

## History

2026-11-12, made at the orchestrator's request from Pavel's task (requirements: "After the engine is finished").
The order of work: three free takes (no constraints) to see what Kimodo does; the constraint format and Kimodo's
T-pose found (first constrained take absurd, then the convention fixed); the table as one motion (stooped walk), then
as a walk + a lean (`after`), the lean's origin corrected from the studio's `startsAt`; the armchair (a second take
with the pelvis placed from measures of the first); the shoulder (three takes: 60 cm away — a straight arm; 45 cm —
the hand by the neck; 45 cm with the point on the top of the shoulder). 17 motions asked in all (one failed with
"busy" and was asked again), every one in `motions/asks.json`.
