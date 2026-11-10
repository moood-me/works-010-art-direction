# Р33 — Аня, rubber-hose 1930s (С11 → 3D)

What was done, why, and how to repeat it. Brief: `docs/briefs/to3d.md`, part "Third round". Done by one agent in one
session (it also made Р34, Марат, of the same style); the orchestrator commits.

## Started from Р11

The style's first 3D character is Р11, Савелий Петрович (`to3d/r11-s11-savely`): not Anny's body but the expressive
constructor of `experiments/toon` (gallery П2) on SOMA's skeleton — forms rebuilt every frame from the posed joints.
Аня is built the same way and with its code: `tools/web/geo.js` (sweeps, lofts, pillows) and `live.js` (the live
face) are Р11's; its look and stage (flat paint, ink hull, film pass) were taken out of `savely.js` into `stage.js`,
so a character's own file holds only the character. What is new here is in `anya.js` and `face.js`.

- **Skeleton**: SOMA's 77 joints with the joint *frames* of the engine's woman (`engine/data/bodies/moood-woman`) and
  the drawing's *places*: pelvis at y 238 of the drawing, chest 88 units higher, head joint 70 more; shoulders at
  (±30, 120), upper arm 43, forearm 46; hips at (±15, 248), thigh and shin 78 each. Her legs stand straighter than
  Anny's (knee at ±16.5, ankle at ±21.5 — the drawing has ±15 → ±19; a little wider so the feet don't cross in a
  walk). 1 drawing unit = 4 mm as in Р11, so the cast keeps the drawing's relative sizes (she is 2 m with the bow —
  the drawing's Аня is that much taller than its Савелий).
- **Motion**: the engine as it is — `makeBody` → `makeRetarget` with its corrections `armsOff` 13° (the hands clear
  the bell of the skirt) and `armsOutOfHead` 6 cm → `placed`. Nothing in the engine was changed.

## The forms (tools/web/anya.js) — all in the drawing's numbers

- **Head**: the drawing's `Head(70)` and `muzzle(40, 62, 46, 46, 24)` joined softly, one mesh (the head's centre lies
  just outside the cheek ball, which Р11's formula did not expect — fixed). The face is painted on a canvas in the
  head's front coordinates and projected straight from the front.
- **Hair**: the drawing makes it "the ball grown by 10 minus the bare face" (`Head.cap`) over a bob drawn behind.
  Here it is one body of revolution — the radius from the head's centre by the angle from the crown, taken from the
  bob's outline — that sinks under the skin over 10 units from the drawing's `face_loop`, so the bare face is exactly
  the drawn one from the front and the hairline turns with the head. The rolled ends are at the sides only (the
  drawing's two curls); behind the neck the hair ends higher. The hairline's ink and the hair's colour next to it are
  painted on the face canvas; the lighter strokes are thin sweeps on the hair. The bow: two pillows and a knot.
- **Face canvas** (`face.js`): `lib.eye` (ring pupil with a highlight, the lid's line with its tilt, three lashes,
  the black crescent of an eye wide open, ∩ for joy, — for a blink), `lib.brow`, `lib.cheek`, the tear, and the
  mouths: the small red lips (`lips-smile`, `lips-frown`, `lips-o`) and the open ones (`grin`, `shout`) as one
  six-point opening plus "how much lip is painted round it", so that shapes mix and speech moves inside the lips. The
  sheet's five expressions are `anya.py`'s `EXPR` as numbers. Half of "joy" no longer half-shuts the eye.
- **Dress**: one loft from the neckline to the hem with the drawing's front widths and profile depths, the hem in
  soft waves. Its paint is a canvas unrolled round the body by length: the polka dots are the drawing's rows (22.4
  apart, 26 between dots, every other row shifted), each row with as many dots as go round the dress at its height;
  the skirt's two folds in ink. Skinned by height over the spine; the lower skirt sways on a spring pulled by the
  hips' acceleration. Belt — a band over the waist; collar — two pillows; puff sleeves — dotted balls on the shoulders.
- **Limbs**: bare hoses (П2's `hosePath`): arms r 7, legs r 16 → 12 → 6; a thin neck. Gloves — Р11's, smaller. Shoes —
  Р11's loft of the drawing's side shoe at 0.8, red (the left shoe's triangles are turned back after mirroring — in
  Р11 the black shoe hid that it was inside out).
- **Look**: Р11's — the drawing's hex as flat paint, a faint second tone, hard shines on the shoes, nose and bow, an
  ink hull of 2.6 units, then the film pass (ink wobble stepping 12 times a second, grain, vignette, black-and-white).

## The live face, the viewer

`live.js` is Р11's (Р4's timing): uneven blinks, fixations and saccades, the eyes leading the head, expressions on
critically damped springs, the head's squash on a rubber spring, speech from Russian phrases letter by letter.
`tools/web/view.html` (app.js + ui.js): drag to turn, wheel to come closer; motions (stand — the drawing's pose, and
Kimodo's idle, walk, wave, dance, bow, jump, run, sit from `engine/motions`); the five expressions or a mix; talk;
colour or black-and-white film; the face close; play / pause / scrub. It loads the engine and its data from `engine/`.

## Repeat

```
cd /home/user/cache/to3d-r33-s11-anya && npm i three@0.160.0     # the page's three.js, served locally to the shots
cd to3d/r33-s11-anya/tools
python3 make.py stills steps films      # pictures → ../pics (films ~12 min on swiftshader)
python3 make.py film:walk               # one film
```
`shots.mjs jobs.json outdir` drives the page headless; `compare.py` makes drawing / 3D / overlay sheets. The cameras
of the comparisons are the drawing's: orthographic, 1.36 px per unit for the turnaround (soles at y 800), 1.55 for the
expressions with the head turned 0.3 rad (17.2°); the three-quarter at 0.55 rad (31.5°), the "profile" at 1.25 rad
(72°) as the drawing's `Head(a)`.

## Bases and licences

| What | Where | Licence |
|---|---|---|
| SOMA skeleton; Anny woman's joint frames (`moood-woman`) | `engine/data` | SOMA rig NVIDIA Apache-2.0; Anny NAVER Apache-2.0; MakeHuman CC0 (`engine/data/soma/NOTICE`) |
| Expressive constructor (sweep, hose path, glove) | `experiments/toon` (ours), through Р11 | — |
| Р11's code: geometry, look, stage, live face, viewer | `to3d/r11-s11-savely/tools/web` (ours) | — |
| Kimodo motions | `engine/motions` (moood studio) | as the engine's motions |
| The drawing and its code | `styles/s11-rubberhose` (ours) | — |
| three.js 0.160 | jsDelivr (npm for the shots) | MIT |

No neural images, no StdGEN, no Human Base Meshes (the drawing's head is two balls with painted features).

## What is weak / not done

- The bob is a smooth helmet: no drawn locks, the rolled ends read less than in the drawing.
- With the arms down the gloves are seen edge-on and look smaller than drawn (the drawing turns the hand to the viewer).
- The drawing's profile is a cheat (the body drawn in pure side and narrower, the head at 72°): the 3D differs there.
- Kimodo's `idle` stoops: the head goes down until the chin covers the collar (the close films follow the head).
- Kimodo's wave brings the hand to a person's head; on her big head it stays by the face (`armsOutOfHead` keeps it
  out): the wave film is shot from the side.
- Half-way between the calm face and joy the eyes are half-shut for a moment (softened: the laughing eye shuts only
  past 0.3 of joy).
- Testing the hairline where the hair itself is (instead of on the outer bob) was tried and taken back: the hair then
  lies on the skin over a band and the edge flickers. It is kept for Р34's beard, where the forms are further apart.
- The dress is a form that bends with the body, not cloth. The drawing's pose with the daisy is not made (no such
  motion in `engine/motions`).
- Heavy runs go through the shared locks: `flock /home/user/cache/heavy.$((RANDOM % 3)).lock python3 make.py …`.
