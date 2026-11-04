# Р11 — Савелий Петрович, rubber-hose 1930s (С11 → 3D)

What was done, why, and how to repeat it. Brief: `/home/user/cache/BRIEF-to3d.md` (first and second round). Done by
one agent in one session; the orchestrator commits.

## The decision: the expressive constructor on SOMA, not Anny

The С11 drawing (`styles/s11-rubberhose`) is not a human body in a style: a ball head as wide as the shoulders and a
third of the height, a pear body, limbs that are one arc without elbow or knee, three-fingered gloves, shoes as long
as the shin. Fitting Anny to it would mean head ×2.5, legs ×0.4, and the very things Anny is good at — anatomy,
muscles, joints that bend like a person's — would be in the way: a rubber-hose arm must bend as a hose, not at an
elbow. The expressive constructor of `experiments/toon` (gallery П2, which Pavel liked) is made for exactly this:
forms built every frame from the posed joints of SOMA's skeleton — limbs as sweeps along an arc through
shoulder–elbow–wrist and hip–knee–ankle — and it was already moved by Kimodo. So:

- **skeleton**: SOMA's 77 joints (engine `data/skeleton.json`) with Anny's old man's joint *frames*
  (`engine/data/bodies/moood-oldman`) — the retargeting reference — and the drawing's *places*: every bone keeps
  Anny's rest direction and gets the drawing's length (spine 92 units from pelvis to chest, neck short, upper arm 52,
  forearm 50, thigh 40, shin 43; pelvis width, shoulders set where drawn). 1 drawing unit = 4 mm, so he is 1.54 m.
- **motion**: the engine as it is — `makeBody` (our rest mesh, those joints, Anny's frames) → `makeRetarget` (with
  the engine's own corrections: `armsOff` 15°, so the hanging arms clear his belly, and `armsOutOfHead` with a 6 cm
  margin — the engine's head ball is taken from the skull's vertices, passed as the body's `head` part) → `placed`; the soles are put on the
  floor as high as SOMA's lowest point (`pose.floor`). The body travels along Kimodo's path, never on the spot.
  Nothing in the engine was changed.
- **no Human Base Meshes head, no Anny skin**: the drawing's head is two balls with painted features; an artist's
  realistic or stylised head would bring a human face the style does not have.

## The forms (tools/web/savely.js, geo.js) — all in the drawing's numbers

- **Head**: the drawing's `Head(64)` and `muzzle(36, 62, 46, 40, 22)` — a skull ball and a flatter jowl ball forward
  and below — joined softly (smooth max of their radial distances), one mesh. Features lie on it as the drawing's
  `Head.project()` lays them: a canvas in the head's front coordinates projected straight from the front
  (masked where the surface turns away). So eyes, lids, pupils, mouth, blush and dome lines turn on the ball as drawn.
- **Face canvas** (`face.js`): `lib.eye` (kind `dot`, lid line, tilt, ∩ for joy, — for a blink), `lib.mouth`
  (grin, shout, o, line) turned into one six-point mouth so shapes mix and move, `lib.cheek`, the dome lines; the
  sheet's five expressions are savely.py's `EXPR` as numbers.
- **3D on the face**: the nose (a ball with a shine), the brows (the drawing's `cloud` outline, rotated by the
  expression, laid on the skin as a puffed "pillow"), the walrus moustache (`savely.moustache` outline as a pillow,
  drooping and lifted with the mouth, two shade strokes), ears (flat cushions with an inner line), the white tufts
  (lumps of balls), spectacles (rings, bridge, arms) that slide up the forehead in surprise, the loupe on its strap
  (pushed back by the spectacles).
- **Squash and stretch**: the head's scale (the sheet's `SQUASH` per expression) follows a *rubber* spring (ω 15,
  ζ 0.32: it overshoots and settles), stretches a little with an open mouth, and is kicked by the head's vertical
  acceleration in motion (a footfall gives a small bounce).
- **Body**: a loft of rings with the drawing's front widths and profile depths (shirt + waistcoat), trouser top as
  another loft; linear skinning by height over Hips–Spine1–Spine2–Chest–Neck1. The waistcoat is painted per pixel from
  the drawing's coordinates (V with the shirt, its edges, the front line, pocket); collar points and tie are pillows on
  it; buttons, watch chain in 3D.
- **Limbs**: sweeps along П2's `hosePath` each frame — sleeves r 9.5→8.6; trousers as knickerbockers r 21→18.6, then
  a quick taper to the lower leg 13→11. Gloves: П2's hand — a palm, three fat fingers and a thumb along Kimodo's own
  finger joints (shortened), a rolled cuff. Shoes: lofts of the drawing's side shoe and its front width, rigid on the
  foot, a sole.
- **Look**: flat paint (the drawing's hex, no colour conversions), a faint second tone, hard white shines on the nose,
  dome, shoes, buttons, lens; an ink hull of 2.6 units (the drawing's outer line); then a film pass — the ink wobble
  of the drawing's `feTurbulence` filter (2.4 px on a 900-px sheet; the noise steps 12 times a second, so the line
  "boils" as hand-inked film does), grain, vignette, and the black-and-white film of `cast-bw`.

## The live face (tools/web/live.js)

Timing as Р4's (`to3d/r4-s5-vera/tools/web/live.js`): blinks log-normal around 2.8 s, shut 65–95 ms / open 120–190 ms,
doubles and shallow ones, blinks with big gaze shifts and at ends of sentences; fixations 0.2–1.6 s with saccades;
the eyes lead the head (the head's turn read 0.25 s ahead in the clip); expressions by critically damped springs,
the squash by the rubber spring, the spectacles slower; speech — Russian phrases read letter by letter into mouth
shapes under the moustache. All seeded: a film is the same every time.

## Viewer

`tools/web/view.html` (app.js + ui.js): drag to turn, wheel to come closer; motions (stand — the drawing's pose, and
Kimodo's idle, walk, wave, dance, stomp, sit, bow from `engine/motions`); the five expressions or a mix (sliders);
talk on/off; colour or black-and-white film; the face close; play / pause / scrub. It loads the engine and its data
from `engine/` of this repository (skeleton, the old man's frames, motions) — nothing else is needed.

## Repeat

```
cd to3d/r11-s11-savely/tools
python3 make.py stills steps films      # pictures → ../pics (films ~15 min on swiftshader)
python3 make.py film:walk               # one film
```
`shots.mjs jobs.json outdir` drives the page headless (three.js from `/home/user/cache/n3-cloth/node_modules/three`);
`compare.py` makes drawing / 3D / overlay sheets. The cameras of the comparisons are the drawing's: orthographic,
1.6 px per unit for the turnaround (soles at y 800), 1.55 for the expressions, head turned 0.3 rad (17.2°), the
three-quarter at 0.55 rad (31.5°) and the "profile" at 1.25 rad (72°) as the drawing's `Head(a)`.

## Bases and licences

| What | Where | Licence |
|---|---|---|
| SOMA skeleton; Anny old man's joint frames (`moood-oldman`) | `engine/data` | SOMA rig NVIDIA Apache-2.0; Anny NAVER Apache-2.0; MakeHuman CC0 (`engine/data/soma/NOTICE`) |
| Expressive constructor (sweep, hose path, glove) | `experiments/toon` (ours) | — |
| Live-face timing | `to3d/r4-s5-vera/tools/web/live.js` (ours) | — |
| Kimodo motions | `engine/motions` (moood studio) | as the engine's motions |
| The drawing and its code | `styles/s11-rubberhose` (ours) | — |
| three.js 0.160 | jsDelivr | MIT |

No neural images, no StdGEN, no Human Base Meshes (see the decision above).

## What is weak / not done

- The drawing's own poses (the watch held up, a hand behind the back) are not made: there is no such Kimodo motion in
  `engine/motions`, and new ones were not to be ordered. Stills use a standing pose made from the rest (arms let down).
- Clothes are forms that bend with the body, not cloth.
- The "profile" of the drawing is a cheat (body drawn in pure side, head at 72°); the 3D at 72° shows a little more
  of the body's front. The three-quarter drawing shifts the features more than a real turn does.
- The loupe reads as a dark lump more than the drawing's neat trapezoid with a blue lens.
- Kimodo's wave and dance bring the hand to a person's head; on his huge head the hand stays just in front of the face
  (kept out of it by `armsOutOfHead`, but it still covers the face from the front: the wave film is shot from the side).
- Kimodo's idle stoops and lowers the head a little; the close films follow the head.
- In motion an arm can touch the belly (the hull draws no line where forms touch closely).
