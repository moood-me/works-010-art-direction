# Р34 — Марат, rubber-hose 1930s (С11 → 3D)

What was done, why, and how to repeat it. Brief: `docs/briefs/to3d.md`, part "Third round". Done by one agent in one
session, right after Р33 (Аня) of the same style; the orchestrator commits.

## Started from Р11 and Р33

As Р11 (Савелий Петрович, `to3d/r11-s11-savely`) and Р33 (Аня): the expressive constructor of `experiments/toon`
(gallery П2) on SOMA's skeleton — forms rebuilt every frame from the posed joints — not Anny's body. Марат is the
case the brief names: huge, a barrel chest, thick forearms, short legs, no neck. A human body does not bend into
that; here his body is simply the drawing's widths and depths. `tools/web/geo.js`, `stage.js`, `live.js`, `app.js`,
`ui.js` are Р33's (Р11's code, the look and stage apart from the character); new is `marat.js` and `face.js`.

- **Skeleton**: SOMA's 77 joints with the joint *frames* of the engine's man (`engine/data/bodies/moood-man`) and the
  drawing's *places*: pelvis at y 378 of the drawing, chest 208 units higher (a very long trunk), the head joint 102
  more, the spine's own curve halved (an upright barrel); shoulders at (±102, 122), upper arm 77, forearm 73; hips at
  (±42, 400), thigh and shin 43 each. 1 unit = 4 mm as in Р11 and Р33 (he is 2.4 m: the drawing's Марат is that much
  bigger than its Савелий).
- **Motion**: the engine as it is, with its corrections `armsOff` 20° (the arms clear the barrel) and `armsOutOfHead`
  8 cm. Nothing in the engine was changed.

## The forms (tools/web/marat.js) — all in the drawing's numbers

- **Head**: the skin is the drawing's ball `Head(68)`; over it one form of **hair and beard** — the drawing's cap (the
  ball grown by 4) joined softly with the beard's volume `muzzle(44, 70, 56, 54, 24)` — which sinks under the skin
  over 7 units from the bare face's edge (the drawing's hairline `hl` over it, the beard's upper edge `beard` below).
  So the face is exactly the drawn one from the front and its edge turns with the head. **Curls** are bumps spread
  evenly (a Fibonacci sphere) over the cap and over the beard, so the outline is scalloped from every side, as the
  drawing's ring of circles makes it in its three views; the front of the cap and the beard round the mouth stay
  smooth, as drawn. Both the skin and the hair-beard form carry the face canvas, so the mouth lies on the beard. The
  head is scaled 1.08, as in the drawing's figure. Nose — a broad ball with a shine; ears — cushions out of the curls.
- **Face canvas** (`face.js`): `lib.eye` with the pie-cut pupil, the lid's tilted line and the lower lid pushed up by
  the cheeks (his resting face); thick brows (`lib.brow`, 13 thick) over the hairline; blush (on the skin only); the
  ticks of the curls and the beard; and his mouths as one nine-point opening — the big `grin` of `marat.py` with a row
  of upper teeth along its upper edge, a tongue and a lower lip; `o`, `shout`, and the shut mouth of the pout, where
  only the lip shows. Teeth, their height and the lip's place and size are numbers too, so expressions mix and speech
  moves in the beard. A mouth in a black beard without teeth and lip reads as a hole (the styles' brief says so).
- **Body**: the barrel (the jacket) — a loft with the front widths and profile depths; the apron — another, a little
  wider over the belly, skinned by height, its lower part swaying on a spring; the waistband, its bow with two tails,
  the pocket (a flat patch — its outline is its ink), two folds and the jacket's flap as ink sweeps, two rows of
  brass buttons. The towel — a striped ribbon (vertex colours) down the chest and over the top of the barrel.
- **Limbs**: arms r 16 → 22 → 13.5 (the forearm swells below the sleeve), the rolled-up sleeve over the first 0.41 of
  the arm with a thicker cuff; legs r 25 → 20, short, under the apron; gloves at 1.2 and shoes at 1.2 (Р11's).
- **Look, live face, viewer**: Р11's, as in Р33. Motions in the viewer: stand (the drawing's pose) and Kimodo's
  idle, walk, wave, dance, stomp, bow, sit from `engine/motions`.

## Repeat

```
mkdir -p /home/user/cache/to3d-r34-s11-marat && cd /home/user/cache/to3d-r34-s11-marat && npm i three@0.160.0
cd to3d/r34-s11-marat/tools
python3 make.py stills steps films      # pictures → ../pics (films ~12 min on swiftshader, longer on a busy machine)
python3 make.py film:walk               # one film
```
The cameras of the comparisons are the drawing's: orthographic, 1.14 px per unit for the turnaround (soles at y 800,
the body's middle at the drawing's x = 4); the expression heads are drawn at 1.3 without the figure's head scale, so
the 3D is shot at 1.3 / 1.08 with the head turned 0.3 rad (17.2°); three-quarter 31.5°, "profile" 72°.

## Bases and licences

| What | Where | Licence |
|---|---|---|
| SOMA skeleton; Anny man's joint frames (`moood-man`) | `engine/data` | SOMA rig NVIDIA Apache-2.0; Anny NAVER Apache-2.0; MakeHuman CC0 (`engine/data/soma/NOTICE`) |
| Expressive constructor (sweep, hose path, glove) | `experiments/toon` (ours), through Р11 | — |
| Р11's and Р33's code: geometry, look, stage, live face, viewer | `to3d/r11-s11-savely`, `to3d/r33-s11-anya` (ours) | — |
| Kimodo motions | `engine/motions` (moood studio) | as the engine's motions |
| The drawing and its code | `styles/s11-rubberhose` (ours) | — |
| three.js 0.160 | jsDelivr (npm for the shots) | MIT |

No neural images, no StdGEN, no Human Base Meshes.

## What is weak / not done
