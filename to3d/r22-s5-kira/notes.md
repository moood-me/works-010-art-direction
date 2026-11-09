# Р22 — Кира, инди (style С5) in 3D

Third round of "Рисунок в 3D" (`docs/briefs/to3d.md`, "Third round"): the style's third character, after Вера (Р4)
and Тим (Р21). Asked by Pavel through the coordinator; made by the same agent right after Тим.

## What was done, and why this way

- **Base and code: as Тим (Р21).** The indie constructor's simple forms on SOMA's joints, not Anny: Кира here is ~3
  heads tall (368 units, the head 123). `tools/web/core.js`, `face.js`, `live.js`, `forms.js`, `ui.js`, `view.html`
  are Тим's files unchanged; hers are `kira.js` (rings, paints, joints, parts, clips) and `face_def.js` (the face's
  numbers). See `to3d/r21-s5-tim/notes.md` for what the shared code does (the face's turn on the head, lines as thin
  tubes, the tilt about the head's centre).
- **The forms are the drawing's own numbers** (`styles/s5-indie/tools/kira.py`): head, the back mass of hair, hoodie,
  hood, boots and soles are its ring stacks; sleeves are its limbs of changing width (cones); legs its tubes; the
  fringe is the head grown by 6 units above the hairline keys; spikes under the back hair and tufts on the crown are
  cones at the drawing's places; headphones — a band round the back of the neck and two cups — the hem's line, the
  cords, the pouch pocket's outline, the laces, the ear with two rings: at the drawing's coordinates.
- **The slouch is the rest pose.** The drawing leans the upper body (`extra.lean`: −3.5° sideways seen from the
  front, 7° forward seen from the side, about (6, −150)) and puts the head 13 units forward, bowed 4° and tilted 7°.
  Here these are real turns in space: every upper-body form is built upright from the numbers and then turned
  (`up()`, `hd()` in `kira.js`), the joints with them. The legs are as drawn too: the weight on her left, the right
  knee out. Kimodo's turns are added on top of this rest pose, so she slouches in every motion.
- **Departures from the numbers:** the back mass of hair is kept behind the ears (the drawing lays it behind the head
  as a layer; as a solid it would cover the cheeks); the ear sits a little further back; the headphone cups are discs
  lying on the chest (the drawing squeezes them by eye); the pouch pocket is its outline on the hoodie, not a patch.
- **Face** (`face_def.js`): smaller eyes than Тим's, heavy lash line with a flick, flat low brows, the highlights
  shifted sideways; mouths `tight` (neutral), `half` with its dimple (her joy — she never smiles openly), `o`, `frown`,
  `clench`; no tear in sadness. Her left eye is under the fringe: the hair is a form over the drawn face, so it shows
  as much of that eye as the fringe leaves.
- **Arms:** her right hand is deep in the pocket — that sleeve goes with the body (weighted along the spine); when a
  motion frees the arms (sneak), the same sleeve is on the arm's bones with a hand at its end. The left arm hangs on
  its own bones.
- **Motions** (`tools/motions`, from `engine/motions`): walk with the hand in the pocket (arms not taken from the
  motion), sneak (arms free), waiting and looking round (Kimodo's `idle` with 80 % of its average stoop taken out —
  her own slouch stays —, head turns on top, the eyes leading), sitting down on the floor.

## How to repeat

```
cd to3d/r22-s5-kira/tools
(cd /home/user/cache/to3d-r22-s5-kira && npm i three@0.160.0)
python3 conv.py walk sneak idle sit
python3 face_tex.py && node face_check.mjs      # the canvas face against the drawing's: <cache>/tex/check.png
python3 make.py stills
python3 make.py turn walk sneak sit look face
```

## What is weak (honestly)

see `entry.json`, «Что слабо» (written after looking at the pictures).

## Licences

Ours: the drawing and its code (`styles/s5-indie`), the constructor's forms and mesher (`experiments/indie`), Вера's
and Тим's page code, Kimodo's motions (`engine/motions`). three.js — MIT. No third-party models, no neural networks.
