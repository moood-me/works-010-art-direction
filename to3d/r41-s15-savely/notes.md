# Р41 — Савелий Петрович, нуар (С15 → 3D)

What was done, why, how to repeat. Brief: `docs/briefs/to3d.md`, its part "Third round". Asked by Pavel through the
coordinator: С15 is one of the four new styles, no character of it was in 3D; this is the first try, Р42 (Тим,
`to3d/r42-s15-tim`) the second, by the same agent with the same code. (The task first named Кира as the second, then
Аня, then Тим — Pavel's lots; only Тим was made.)

## The idea: the black shape comes from the light, the form is made of planes

The style's drawing (`styles/s15-noir/tools/noir.py: form`) paints a form black and lays its lit copy over it, moved
towards the light; its rules ask for a shadow edge of straight segments with hard corners and no half-tones. Looked at
before choosing: Р8/Р23/Р24 (the drawing's own solids, the look from a real lamp), Р21/Р22 (simple forms on SOMA's
joints, a drawn face on the head, their retargeting and viewer), Р12/Р35 (the look drawn each frame), and the warning
of Р19/Р20 (a realistic base under a stylised look gives blotchy shadow edges).

Decided (by the agent): no base head or body from outside. The figure is **few flat faces built from the drawing's
numbers**, every face wholly lit or wholly black:
- `tools/web/build.js` — `Forms` (triangles with paint and bones → one mesh with flat normals), `headKit` (the head
  from the drawing's front and side outlines: at each height the front outline gives the width, the side outline the
  front and back; the section is planes — half of the front, the cheek, the side — and becomes round toward the
  skull's dome, the only part with smooth normals), `skull`, `nose`, `ears`, `curtain` (hair hung round the head, its
  zigzag bottom line is the drawing's pointed ends), `cap` (Тим's hair), `limb` (a faceted tube through three joints
  with a hard corner), `box8` sections.
- `tools/web/noir.js` — the look and the rest: a paint where `normal · light > 0.1`, black otherwise; cast shadows from
  a 4096² depth picture taken from the light (16 weighed depths, then a hard step — a clean edge); the rim — back
  faces pushed out 4.5 mm in the style's `RIM` colour, only where the form is turned from the light; the drawn face
  as a canvas projected on the head's forward planes; SOMA's joints and Kimodo's motions retargeted (the code of
  `to3d/r22-s5-kira/tools/web/core.js`, itself `experiments/indie`'s way); posture and held arm poses on top of a
  motion; the night scene (paving that takes the shadow, a drum with the style's town and pale disc); cameras.
- `tools/web/face.js` — `head.py`'s front-view `eye`, `brow`, `mouth` ported to canvas, an expression as numbers
  (`op`, `brow`, `tilt`, `look`, `cheeks`, the mouth as six numbers so that expressions and speech shapes blend).
  `live.js` (blinks, saccades, gaze leading the head, speech) and `ui.js` are Р22's.
- `tools/web/savely.js` — his numbers: joints, trunk sections, waistcoat as painted faces of the shirt (the strip in
  the middle stays shirt), hair columns, glasses (brass rings and temples as forms, lenses as two translucent discs
  with a glare), the moustache as two wings on the head bone that the mouth's numbers turn, the watch, expressions,
  arm poses, clips.
- `tools/drawing.py` — takes the numbers from the style's code (`web/sav_drawing.json`) and draws its busts in any
  view and expression for comparison (`refs`).

## Departures from an honest light, and from the drawing

- The nose's side planes are lit as if turned further (`nose(..., lean)`): the style paints the side of a man's nose
  black in three-quarter view too, a true plane would be lit there.
- The nose, ears and moustache cast no shadows (set `soft`, movers): their shadows cut the face into pieces.
- Eye sockets (black under the brows), forehead and nose-to-mouth folds are drawn on the face canvas, as the style
  draws them — not light.
- His joy is a closed smile under a lifted moustache; the style's code would draw its common `grin` (an open mouth) —
  he has no sheet of his own in the style, and an open laugh did not suit him (the agent's choice).
- The head sits as in the drawing's figure (chin in front of the collar), not as in its bust sheets (a long neck);
  its scale is 0.72 against the drawing's 0.68.
- The drawing's three-quarter head has its whole side black; the 3D light, the same for all views, lights the temple
  and cheek there. The drawing's views don't share one light; the front view was followed.

## How to repeat

```
cd to3d/r41-s15-savely/tools
(cd /home/user/cache/to3d-r41-s15-savely && npm i three@0.160.0)
python3 conv.py walk idle bow wave …      # engine/motions → tools/motions (needs /home/user/moood/engines/1/soma.bin)
python3 drawing.py sav                    # web/sav_drawing.json
python3 make.py all                       # refs, compare, portrait, figure, steps, expr, exprsheet, films → ../pics
python3 make.py films:walk                # one film; strips of its moments go to the cache to look at
node view_check.mjs /home/user/cache/to3d-r41-s15-savely/view.png   # the viewer as a person opens it
```
`character.json` holds what `make.py` needs (the character's key in the style, frames, films). Browser runs go
through the shared locks (`make.py: heavy` takes the first free of the three). By hand: serve the repository root, open
`to3d/r41-s15-savely/tools/web/view.html`.

To add a character of this style: copy `tools/`, write `<name>.js` beside `savely.js`/`tim.js` (joints, forms, face
numbers, clips), `python3 drawing.py <key>`, set `character.json` and the script in `view.html`. `build.js`,
`noir.js`, `face.js`, `live.js`, `ui.js`, `make.py`, `drawing.py`, `shots.mjs` are the same files in Р41 and Р42.

## Bases and licences

| What | Where | Licence |
|---|---|---|
| The drawing and its code | `styles/s15-noir` | ours |
| Retargeting, live face, viewer | `to3d/r22-s5-kira` (from `experiments/indie`, Р4) | ours |
| SOMA skeleton | `engine/data` (NVIDIA, Apache-2.0, see `engine/data/soma/NOTICE`) | Apache-2.0 |
| Kimodo motions | `engine/motions` (walk, idle, bow, wave) | as the engine's |
| three.js 0.160 | jsDelivr / npm | MIT |

No neural images, no third-party meshes, no Blender.

## What is weak

- The body is a straight block on thin legs; arms are bars with a wedge for a hand, no fingers; elbows and knees are
  plain creases (they thin in a deep bend: the shared ring is halved between two bones).
- Faces flip between lit and black at once as the figure moves (the style's nature, but on the trunk's side it can
  flicker in a walk).
- Three-quarter view is lighter than the drawing's (see above); on the lit side the nose merges with the face.
- Eyes behind the lenses are dim (the drawing's too): expressions rest on brows, moustache and mouth.
- No watch chain; the watch's dial faces up, the drawing turns it to the viewer.
- The rim shows faintly on some lit edges too (it is decided per vertex, not per pixel).
- Speech has no sound. Clothes are forms, not cloth.
