# Other bodies — К1's table and К2's touch repeated on other bodies

The task (from the orchestrator, for Pavel): the catalogue is for agents who will take a way and make their own
characters by it — other bodies, other proportions. Every scene of К1 and К2 was ordered for one body, and nobody but
its author had repeated one. Here a next agent, with only what is in `experiments/contacts/` (К1) and
`experiments/two-people/` (К2) — their notes, code and recorded orders — repeats two of their scenes on other bodies:

1. **К1's table lean** for a child and for a heavy man (a real table, 0.74 m), once with a bar counter (1.1 m), and,
   as a stress case, for the tallest body the repository has (2.31 m).
2. **К2's touch with the look back** (its second version, touch3) for pairs of clearly different heights: a man
   (1.77 m) and a short woman (1.49 m); a child (1.31 m) and the woman (1.59 m), the child touching her arm where it
   can reach.
3. Seeds: the child's lean with seeds 0, 1, 2; the man's touch with seeds 1, 2, 3.

**What the most useful result is** — where the notes of К1 and К2 were not enough — is in its own section below.

Page: `index.html` (the scene chosen there; each scene plays on `table.html` — К1's page, copied — or `touch.html` —
К2's page, copied; play/pause/scrub, the correction on and off, camera views, closer to the touch).

## Bodies

From `engine/data/bodies` (moood's Anny bodies), seen side by side in `pics/bodies.png` (left to right: woman, man,
child, old man, the Т8 "elf", old woman, girl, anny-C-pear, anny-C-hero).

| who here | body | height | k (hip / SOMA's) | note |
|---|---|---|---|---|
| child | moood-child | 1.31 m | 0.707 | |
| heavy man | moood-oldman | 1.74 m | 0.972 | the only heavy man: a big belly (its front 21 cm before the pelvis; the woman's 14 cm) |
| very tall | anny-C-elf | 2.31 m | 1.408 | the only tall body; it is a woman's body, long-legged (Т8). There is no tall man in the repository |
| short woman | anny-C-pear | 1.49 m | 0.809 | has no character file in `engine/characters`; given as an inline character |
| man, woman | moood-man, moood-woman | 1.77, 1.59 m | 1.015, 0.896 | К1's and К2's own |

"A tall man" was asked for; the repository has none (the man, 1.77 m, is the tallest male body). The man is used as
the tall one against the short woman; the 2.31 m body is used at the table as the tall extreme.

## What was done, step by step

### The table (К1)

1. Copied К1's `tools/` (`kimodo.py`, `pose.py`, `plan.py`, `scenes.py`, `shots.cjs`, `report.py`, `pictures.py`,
   `sheet.py`) into `tools/table/` and its page into `table.html`, `table.js`, `contact-figure.js`.
2. `tools/table/plan.py` made per body. К1's `table()` has the woman's numbers built in; each had to be read as a
   rule for another body (see "where the notes were not enough"):
   - the places are divided by the body's k (as К1 says);
   - the palms' spread: К1's ±0.19 m scaled by the shoulders' width;
   - where the pelvis stands: К1's 0.27 m before the edge is read as the woman's front (14 cm before her pelvis) and
     13 cm more; the 13 cm scaled by k, the front taken from each body (the heavy man stands 35 cm off, the child
     21 cm);
   - the palm's lift over the skin (0.022 m) scaled by k.
   Check: the woman's plan comes out exactly as К1's sent constraint (`plans/lean-woman.json` against К1's
   `plans/table_lean.json`: identical to the last digit).
3. **The walk is К1's own** (`table-walk`, Kimodo's space; the same for every body), and the lean is made `after` it
   as in К1. So the table stands where each body arrives (the child's edge 1.73 m from the start, the heavy man's
   2.44 m, the tall one's 3.37 m): the table moves with the body. A game with a table at a fixed place orders its own
   walk with its own `root2d` stop (one more order per body).
4. One lean ordered per body: `lean-child`, `lean-oldman`, `bar-oldman` (1.1 m), `lean-elf`; К1's prompt unchanged
   ("A standing person leans forward and rests both hands on the table in front of them."), seed 0. The pose that
   carries the hands is К1's (its standing frame, bent at the waist until the arms reach): the child and the bar
   needed no bend, the heavy man 12°, the tall one 44° (К1's loop stopped at 58° without a word if it never reached;
   it goes to 88° here).
5. Scenes written by `tools/table/scenes.py` into `table-scenes.json`; the correction weighed in from frame 192 as in
   К1. Pictures and numbers by `tools/table/pictures.py <scene>`.

### The touch (К2)

1. Copied К2's `scene.js`, `figure.js`, `page.js` (→ `touch.js`), `index.html` (→ `touch.html`), `scenes.js`
   (→ `touch-scenes.js`) and its tools into `tools/touch/` (+ `tools/keep.py`, `tools/convert.py`).
2. **The touched points on the other body.** К2's point on the woman's shoulder had to be found again for a body of
   other proportions. `tools/touch/points.mjs`: К2's two points are `shoulder.mjs: shoulderSurface` pushed 2 cm out
   along its ray — the touch at share 1.1, angle 0.45 (1.9 mm from К2's point), the slide at share 1.4, angle 0.2
   (exact). The same settings give the points on the short woman. For the child, a point on the back of the woman's
   upper arm (`armSurface`: 35 % of the way to the elbow, 1.2 rad back from straight out, 2 cm out; carried by
   `RightArm`) — the child's hand reaches 1.18 m, her shoulder is at 1.32 m.
3. **Targets**: `tools/touch/targets.mjs` (К2's, taught to take a body without a character file: `body:anny-C-pear`)
   gives the point at scene frames 160, 191 (touch) and 200, 215, 247 (hold) in the toucher's Kimodo space. Check:
   К2's own command gives exactly the targets in К2's `b-touch3.spec.json` and `b-hold4.spec.json`.
4. **The orders**, as К2: the touch — a chain "walks and stops" + "puts the right hand on…", right-hand constraint at
   frames 118 and 149, the pose `b-probe` frame 120 with `handYaw −0.25` and `elbowPole` (`tools/touch/order_hand.py`,
   specs in `motions/*.spec.json`); then the hold, `after` the touch (5 frames), with her moving point at its frames
   13, 28, 60.
   - The man: the pelvis 50.8 cm behind and 28.3 cm to her left of the touch, as К2. The child is placed at
     z −2.8 m (not −4.0) so that its walk in Kimodo's space is as long as the man's.
   - The child, first try (`c-touch`, `c-hold`): the pelvis 42 cm behind (Kimodo's metres; 30 cm on the child) and the
     prompt "reaches up … looks up at them". It stood pressed to her: its face at her back, the arm along her arm,
     2–3 cm into it; its left hand went to its mouth; with "looks up" and the head correction the head was thrown back.
     Second try (`c-touch2`, `c-hold2`): 62 cm behind (44 cm on the child) and plain prompts ("puts their right hand on
     the arm of someone in front of them"). That one reads: a child steps up behind her and lays a hand on her arm.
5. **startsAt before the hold is ordered**: ordered a 0.5 s "stands still" `after` the touch (a probe, data not kept)
   and read its `startsAt` from `motion(key)`; the hold was ordered with it. Every hold then had exactly that
   `startsAt` (`tools/touch/startsat.py` on the made hold gives the same to 1 mm).
6. Scenes in `touch-scenes.js`; numbers by `node tools/touch/measure.mjs <scene>`; pictures by
   `node tools/touch/pictures.mjs tools/touch/jobs-<scene>.json`.

All orders are in `motions/orders.json` (key, prompts, seconds, seed, constraints or the file they are in, `after`,
`startsAt`, notes; the ones copied from К1/К2 are marked `copied`); the constraints as sent are
`motions/*.constraint.json` (touch) and `plans/*.json` (table). Orders made here: 4 leans (3 of them failed "busy" the
first time and were asked again), 2 more seeds of the child's lean, 3 touches (the man; the child twice) + 2 more
seeds of the man's, 3 holds, 3 probes for `startsAt` — 17 made, 3 failed.

## Numbers per body

On our body, over the frames the touch is held; "Kimodo" — before the correction, "corrected" — after it.
`measures/<scene>.txt` (table), `pics/<scene>-measure.json` (touch).

### The table (К1: the woman — Kimodo 4.6 cm mean, max 5.8; corrected 0.0)

| scene | Kimodo's palms in its own space at the two keyframes | pelvis in Kimodo's space | Kimodo's palm on our body | corrected | into the table |
|---|---|---|---|---|---|
| child, 0.74 m | 2.8–3.4 cm | 3.4–3.5 cm | mean 4.7 / 4.9 cm, max 5.2; within 7 cm from frame 172 | 0.0 cm, skin on the top | the hands into the top's edge 1.7 cm on the way (frames 143–169, as К1's woman) |
| heavy man, 0.74 m | 2.8–3.8 cm | 3.5–4.5 cm | mean 7.6 / 8.0 cm, max 9.3 — never within 7 cm | 0.0 cm | nothing |
| heavy man, bar 1.1 m | 2.6–3.2 cm | 3.7–4.1 cm | mean 7.8 / 8.6 cm, max 9.0 (within 7 cm at frame 164, then drifts out to 8) | 0.0 cm, skin on the top | the right hand into the top's edge 1.7 cm on the way (frames 146–161) |
| very tall, 0.74 m | 3.4–4.5 cm | 2.4–4.6 cm | mean 22 cm, max 30 — the hands hang 15–22 cm over the top | **not reached**: 6.7 / 9.6 cm left (max 17), the skin 4–16 cm over the top — the arm is straight and can't reach | nothing |

### The touch (К2's touch3 on the woman: Kimodo 4.1 cm mean, max 6.4 standing; 2.2 / 3.5 while she turns; one in the other 0.7 cm at most)

| scene | Kimodo's palm in its own space at the keyframes | Kimodo's palm on our body | corrected | one body in the other |
|---|---|---|---|---|
| man → short woman | 0.0–0.1 cm (pelvis ≤ 4 cm) | standing mean 5.2, max 7.9 cm; turning mean 2.1, max 3.2 cm | 0.0 cm | his hand 1.4–1.9 cm into her shoulder while she turns (frames 195–249), her shoulder 1.3 cm into his hand |
| child → woman's arm | 0.0–0.1 cm (pelvis ≤ 4 cm) | mean 5.0, max 8.7 cm | 0.0 cm | its hand into her upper arm 1–3 cm while held, 4.6 cm at frames 183–197 (the join of touch and hold, as she starts to turn) |
| child, first try | 0.0–0.1 cm | mean 5.1, max 6.7 cm | 0.0 cm | its hand and forearm 2–3 cm into her arm |

### Seeds

- **The child's lean**, seeds 0, 1, 2 (`lean-child`, `-s1`, `-s2`): in Kimodo's space the palms 2.8–3.4, 2.3–3.1,
  2.4–3.0 cm off, the pelvis 3.4, 3.1–5.2, 2.6–2.7 cm. On the child: Kimodo's palms mean 4.7–4.9, 5.8–5.9, 5.1–5.3 cm off (max 5.2, 6.9, 5.7); within 7 cm from frame 172, 163, 155; the hands into the top's edge 1.7 cm on the way in all three. The numbers hardly change; the look does: seed 0 stoops deep with the head low over the top, seed 1 stands nearly upright with the hands on the table and a slight lean (the one that reads as a child at a table), seed 2 between (`pics/lean-child-s1-sheet.png`, `-s2-sheet.png`). So the "child stoops like an adult" below is partly luck.
- **The man's touch**, seeds 1, 2, 3 (`m-touch`, `-s2`, `-s3`; the coming up and the touch only): at the keyframes
  all three are exact in Kimodo's space (0.0–0.1 cm); between them on our body mean 5.2 / 11.5 / 5.8 cm, max 7.9 /
  20.8 / 8.4 cm. Seed 2's hand leaves the shoulder by up to 21 cm between the two keyframes — the correction then
  moves the arm 20 cm, no longer "small". A third of the takes was bad: luck matters, and one take is not a measure.

## How it looks (by eye)

- **Man → short woman** (`pics/man-short-sheet.png`, films): reads as К2's scene does. He walks up, lays his hand on
  her shoulder, she looks round, his hand stays. Weak: his arm comes out nearly level and straight (he is 28 cm
  taller, and the stance is К2's, made for the 1.59 m woman — he should stand nearer or bend the elbow more); as she
  turns, her chin comes close over his fingers (`pics/man-short-contact.png`, 6.8 s) — what К2's slide to the edge
  was meant to prevent, and on a shorter woman it is not enough; his hand is 1.5–1.9 cm in her shoulder then.
  Before the touch (4.7 s) his hand passes at the height of her face.
- **Child → woman's arm** (second try, `pics/child-woman2-sheet.png`): reads — a child comes up behind her, reaches
  up and lays a hand on her arm; she looks round over that shoulder (over the child's head: her look is К2's, made
  for someone at her height; nothing turns it down to the child). Weak: the child's hand lies with the fingers up,
  the palm flat against the back of her arm (the hand's turn is the one К2 chose for a hand over a shoulder, from
  above) — a child would rather lay it fingers forward; the hand is 1–3 cm in her arm (К2's correction has no
  keep-out), 4.6 cm for half a second as she starts to turn.
- **Child at the table** (`pics/lean-child-sheet.png`): it comes up and puts both hands on the table, but bends deep
  over it, knees bent, the head low over the top — like an adult stooping over a low table, not a child resting its
  hands on a table at its chest. Kimodo does the "leans forward" of the prompt; for a child at 0.74 m (in Kimodo's
  terms a counter 1.05 m high) there is nothing to lean down to, and it leans anyway. Seed 1 of the same order
  stands nearly upright and reads much better (see Seeds); a prompt that does not say "leans" would be the next try
  (not made).
- **Heavy man at the table** (`pics/lean-oldman-sheet.png`): the best of the tables. He walks up, stops, leans deep on straight arms with the knees bent, the belly clear of the edge — reads as a heavy, tired man leaning on a table. The hands lie on the top with the correction (8 cm off without it, `pics/lean-oldman-close.png`).
- **Heavy man at the bar** (`pics/bar-oldman-sheet.png`): reads: he comes up, puts both hands on the counter, leans a little forward; the elbows bent, the knees a little bent. Kimodo's hands 8 cm off on his body (`pics/bar-oldman-close.png`), the correction lays them on.
- **Very tall at the table** (`pics/lean-elf-sheet.png`): **fails**. It walks up and folds over the table, the back bent nearly level, the arms hanging straight down, and the hands stay 15–22 cm over the top; the correction, its arm already straight, gets them only within 7–10 cm (`pics/lean-elf-close.png`: hands hovering at the edge). The reason is the proportions, not Kimodo: in its own space Kimodo put the palms 3.4–4.5 cm off, as for the others. The engine scales the motion by hip height (k = 1.41), but this body's arms are short for its legs (arm / k = 0.44 m against SOMA's 0.56 m), so every place that is right for SOMA scaled by k is 20+ cm out of its reach. К1's and К2's notes divide places by k "for our proportions"; for a body whose limbs are not SOMA's proportions the whole pose has to be planned for its own arm length, which neither tool does.

## Where the notes of К1 and К2 were not enough

What a next agent would stumble on, in the order met.

**К1 (the table)**

1. **The plan is written for one body.** `plan.py` has `K_WOMAN` and the woman's numbers built in (0.27 m from the
   edge, ±0.19 m, palm lift 0.022 m); the notes say "another body needs its own order (or a bigger correction)" but
   not how those numbers follow from a body. I had to decide what each one means: the 0.27 m as "her front plus
   13 cm", the spread as "by the shoulders". A guess; the heavy man's belly made the guess matter (without it he would
   have stood with the belly against the edge).
2. **The table moves with the walk.** The walk was ordered once in Kimodo's space, so it ends at a different place
   for each body (×k). The notes say the scene is "the table 2.2 m ahead"; that holds for the woman only. Either the
   table goes where the body arrives (done here) or a new walk is ordered per body.
3. **"Within 7 cm, then weigh in over 15 frames"** — the rule for when the correction starts — is not a rule that
   holds on other bodies: the heavy man's Kimodo palms never come within 7 cm (7.6–8 cm all the hold). Frame 192 was
   kept as К1's.
4. **The bend loop gives up silently**: the input pose is bent until the palms reach, up to 58°, and then used
   whatever the miss. For a low table and a tall body that limit matters (the tall one needed 44°).
5. **`startsAt` "depends only on the earlier motion and `frames`"** — true (checked: all 6 leans after `table-walk`
   have the same one, and three holds have the probe's), and it is the useful fact К2's notes lack (below).
6. **Rendering** К1's way (every 2nd frame, two views, a 4096 shadow map, software GL) took 15–25 min a scene here,
   and the browser died once under the machine's load; `pictures.py` here renders every 3rd frame.

**К2 (the touch)**

7. **The touched point is not reproducible from the notes.** The notes say "a point of her skin at rest, pushed
   1.5–2.5 cm out along the skin's normal"; `scenes.js` has only the resulting numbers. The parameters
   (`shoulderSurface` share 1.1, angle 0.45; share 1.4, angle 0.2) are nowhere; I found them by search. And the push
   is along the ray of `shoulderSurface`, not the skin's normal (the slide point matches the ray exactly).
8. **"His pelvis 51 cm behind, 28 cm to her left"** is in Kimodo's metres (the spec's `hip`), not the scene's — the
   same for the man (k ≈ 1), not for a child (×0.71).
9. **`startsAt` of the hold can't be known before ordering it from К2's notes.** К2's `startsat.py` computes it after
   the fact (`earlier[n−k] − new[0]`); its `b-hold3` was ordered with a guess (the pelvis at n−5) that came 6 cm off.
   Here: a 0.5 s probe `after` the touch, ordered first, gives the exact `startsAt` (one cheap order instead of a
   wrong take).
10. **`targets.mjs` takes only a character id** — a body without a character file (any Anny body but the ten) needs
    a change (done: `body:<id>`). And its Kimodo y is `world_y / k + SOMA's floor` (−0.26 cm), not just "/ k".
11. **The recorded constraint differs from the tool's output**: `order_hand.py` on К2's own `b-touch3.spec.json`
    gives the ring and little fingers' turns that `b-touch3.constraint.json` (as sent) has as zeros. Small (fingers),
    but "made by this tool from this spec" is not exactly true.
12. **The prompts and the stance are for adults of one height.** "looks down at them", the stance distance, the hand's
    turn (`handYaw`, `elbowPole`, fingers from a tap over a shoulder) — all are the scene's, not the way's. For the
    child they gave a hand lying fingers-up and, with the first stance, a child pressed into her back. The notes call
    these "one number in the spec"; on another body they are the main work.
13. **The woman's look round is her own motion**, carried onto any body; nothing in К2 lets her look *down* to a
    child. A new order of `a-look` (or a head correction for A like B's) would be needed.

**Both**

0. **"Divide by k" assumes SOMA's proportions.** Both notes carry places into Kimodo's space by k = hip height / SOMA's
   and leave "the last centimetres" to the correction. That holds while the body is SOMA scaled (woman, man, child,
   heavy man: 5–8 cm left). For a body whose arms are short for its legs (the 2.31 m Т8 body: arm / k 0.44 m against
   SOMA's 0.56) Kimodo's pose, right in its own space to 3–4 cm, leaves the hands 22 cm off, and the arm correction,
   already straight, can't close it. Neither note warns that k is a single number for a whole body; such a body needs
   its places planned for its own arm (e.g. the pelvis lower or nearer), which neither tool does.
14. **Two definitions of "the palm".** К1 measures the palm's middle as the mean of the wrist and the index and little
    finger knuckles; К2 as between the wrist and the middle finger's knuckle, 1.5 cm out on the palm side. Numbers of
    the two are not directly comparable. In Kimodo's own space К1's leans land 2–4.5 cm off at the keyframes, К2's
    hands 0.0–0.1 cm — К1 sends `end-effector` with joint names, К2 `right-hand`; why they differ so much I did not
    check.
15. **The pelvis is held only within `root_margin` (0.04 m by default)** — the pelvis came 2.4–5.2 cm off its place in
    every order here. Neither note says it; it explains "pelvis 3 cm" in К1.
16. **The studio**: of four orders sent together, three failed "busy" at once; `motion(key, data: "body")` answers
    "not made (yet)" for a failed order exactly as for one still being made — only `motion(key)` without data says
    "failed: busy", and it returns the whole constraint. With a large constraint it is cheaper to order one at a time.

## What is weak

- The table moves with the body (the walk is shared); a fixed table needs a walk per body.
- The 2.31 m body does not reach the table at all (proportions: short arms for its legs; k by hip height does not
  fit it). The child bends over the table like an adult in two seeds of three; the heavy man's palms land 8 cm off
  before the correction (the woman's 4.6).
- In the touch, the stance and hand turn are К2's adult ones, adjusted only by distance for the child; the woman's
  look round does not look down to the child; the hand presses 1–3 cm into the other (no keep-out in К2's correction).
- No body here is a tall man; the 2.31 m body is a long-legged woman's (Т8).
- Measured, not checked: whether the feet slide (not measured anywhere in К1/К2); the films at 10–15 frames a second; films only for the child's lean and the two touches (side), the other table scenes have sheets and close-ups only — software rendering under the machine's load took 15–25 min a film.
- Not made: a table at a fixed place with walks per body; a lean prompt without "leans" for the child; a new `a-look`
  for the child scene.

## Files

- `index.html` — chooses a scene; `table.html` + `table.js` + `contact-figure.js` + `table-scenes.json` (К1's page);
  `touch.html` + `touch.js` + `scene.js` + `figure.js` + `touch-scenes.js` (К2's page).
- `tools/table/plan.py <who> [height] [name]` — a lean's constraint for a body (`plans/<name>.json`);
  `tools/table/scenes.py`; `tools/table/pictures.py <scene>` (numbers → `measures/`, pictures → `pics/`).
- `tools/touch/points.mjs` — the touched points on a body; `targets.mjs`, `order_hand.py`, `measure.mjs`,
  `pictures.mjs` (+ `jobs-*.json`), `startsat.py` — К2's.
- `tools/keep.py`, `tools/convert.py` — a studio motion into `motions/<id>.json`.
- `motions/orders.json` — every order; `motions/<id>.json` — the motions (К1's `table-walk`, `table-free*` and К2's
  `a-stand`, `a-look`, `b-probe`, `b-touch3`, `b-hold4` copied); `motions/*.spec.json`, `*.constraint.json`.

## History

2026-11-12, by an agent at the orchestrator's request (the task above). Read К1's and К2's notes, code and orders;
reproduced their constraints exactly from their tools (the woman's lean; `b-touch3`'s and `b-hold4`'s targets) before
changing anything; ordered for other bodies; looked at every sheet and close-up; the child's touch made again after a
look (too close). Nothing in `experiments/contacts/`, `experiments/two-people/`, `engine/` was changed.
