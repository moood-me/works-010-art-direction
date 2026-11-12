# Р42 — Тим, нуар (С15 → 3D)

Brief: `docs/briefs/to3d.md`, "Third round". The second character of С15 in 3D, made right after Р41 (Савелий
Петрович, `to3d/r41-s15-savely`) by the same agent. The task named Кира first, then Аня, then Тим (Pavel's lots,
passed by the coordinator); only Тим was made.

## What is shared with Р41 and what is his own

The way and the shared code are Р41's — read its `notes.md` for the idea (the form is few flat faces from the
drawing's numbers; a face is a paint in the light and black when turned from it or covered; cast shadows from a depth
picture taken from the light; the rim only where the form is black; the face drawn by the style's own eye, brow and
mouth on the head's forward planes; SOMA and Kimodo through Р22's retargeting). `build.js`, `noir.js`, `face.js`,
`live.js`, `ui.js`, `make.py`, `drawing.py`, `shots.mjs`, `view_check.mjs` are the same files in both folders.

His own: `tools/web/tim.js`, `tools/web/tim_drawing.json` (by `python3 drawing.py tim`), `tools/character.json`.
Added to the shared code for him (and copied back to Р41):
- `headKit(..., { ang })` — how angular the face is; 0.72 for a child (rounder sections);
- `cap` — hair as a cap of faceted columns meeting at the crown, the zigzag bottom line (fringe, temples, nape), and
  `spikes` — tufts standing out of it. A first try with the columns meeting in a high point read as a straw roof;
  rows that follow the skull and separate spikes read as tufts;
- `nose(..., lean, rim)` — his nose is the style's `under` kind: only the plane under the tip is black, so its side
  planes are lit like the face (`lean < 0`), and it has no rim;
- `make.py`: `refViews` (the style drew Тим only in three-quarter view: `tim_hair` has no front or side — the front
  and profile pictures are the 3D alone), `full` (the figure's frame), `exprsheet` (the style's sheet over the 3D),
  the camera's `soft` (a run left the frame with the soft follow).

His forms: the trunk's rings stand on the shirt's band edges — the bands are its faces painted red and cream by turns;
shorts are the hips' block and a wide leg on each thigh; bare legs and arms are `limb`s; socks, red shoes; short
sleeves on the upper arms; fists; the slingshot on the right hand's bone (takes light, throws no shadow). The legs
stand apart as drawn. Carriage: the chest out, the chin up. Standing, the arms hold the drawing's pose (slingshot up,
fist on the hip); in motions they are Kimodo's.

Expressions are the style's numbers (`head.py: EXPR`): his rest is `smile`, joy is `grin` (open, teeth and tongue).

## How to repeat

```
cd to3d/r42-s15-tim/tools
(cd /home/user/cache/to3d-r42-s15-tim && npm i three@0.160.0)
python3 conv.py walk run jump sneak wave idle
python3 drawing.py tim
python3 make.py all
node view_check.mjs /home/user/cache/to3d-r42-s15-tim/view.png
```

## Bases and licences

Ours: the drawing and its code (`styles/s15-noir`), Р41's and Р22's code. SOMA skeleton — NVIDIA, Apache-2.0
(`engine/data/soma/NOTICE`); Kimodo motions — `engine/motions` (walk, run, jump, sneak, wave, idle); three.js — MIT.
No neural images, no third-party meshes, no Blender.

## What is weak

- Little black on a round child's face: the shadow takes the side of the head and the neck, the face stays light —
  less noir than Савелий (the style says the same of its drawing).
- Hair is thinner at the back than the drawing's big black mass with a toothed edge.
- The body is bars; shorts in rest stand as a box; fists are boxes; the slingshot's band is two bars.
- The head's shadow on the shoulders has a slightly lumpy edge.
- As in Р41: faces flip between lit and black at once in motion; speech has no sound.
