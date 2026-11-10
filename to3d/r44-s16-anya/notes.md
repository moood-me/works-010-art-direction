# Р44 — Аня, пиксель-арт (С16 → 3D)

Brief: `docs/briefs/to3d.md`, "Third round". Asked by Pavel through the coordinator; made by the same agent (Claude)
right after Р43 (Тим, `to3d/r43-s16-tim`) with the same code. **The way is described in Р43's `notes.md`** — the 3D
looked at through the sprite's own pixels: parts typed as ASCII maps from the front and the side, a voxel a pixel,
one ray a pixel, the style's palette, outline and light, the face stamped, steady pixels. Here: what is hers.

## What is hers (`tools/web/anya.js`)

- **Only the front is drawn** for her in the style (`chars/anya.py: FRONT`; no turn sheet). The front maps of the
  head, trunk, skirt, legs and shoes are cut out of it; every side map and the back of the head and of the cardigan
  are typed here by the style's rules (the profile after the pattern of Тим's and Кира's drawn sides: a nose only in
  profile, the eye near the edge).
- **20 parts.** The hair is three: the cap on the head (with the face), two locks lying on the shoulders in front
  and a sheet behind the back — the locks and the sheet hang on the chest, so they stay when the head turns. The
  skirt is a stiff bell on the hips; the thighs move inside it and only the shins come out in a stride. The book is
  a flat box on the chest; the arms are held to it in every clip (`HOLD.book`: the upper arm hangs as drawn, the
  forearm goes forward and in); to wave, the right arm lets go.
- **The head's colours are chosen pixel by pixel** (`MIX`): what faces sideways is read from the side map (hair),
  what faces forward from the front map (the face in its frame of hair); skin only from the map of the head's own
  view — a cheek from the side map beside the face from the front read as two faces. One map a part (Тим's way)
  smeared the front map's edge column — the drawing's highlight — over the whole side of the hair.
- **The face** (`face()`): each feature is a point on the head — its column in the front map and in the side map —
  put on a whole pixel by the head's turn; stamped only onto skin, so the hair hides it. Eyes of one column, a blush,
  a mouth of three pixels; joy is two arcs.
- **Shared code changed while making her** (the same files are in Р43, its pictures were made again): a highlight
  stays only where it is drawn; a part turns by a whole step only from 22°; stamps only onto skin; `MIX`.
- **Left out**: Kimodo's `bow` and `idle` were tried and dropped — in a deep lean the stiff head-with-hair and the
  bell turn as blocks and the figure becomes a lump.

## Repeat

```
cd to3d/r44-s16-anya/tools
python3 drawing.py anya
python3 conv.py walk run wave        # tools/motions
node make.mjs stills && node make.mjs films
node look.mjs; node look2.mjs walk   # sheets in the cache
flock /home/user/cache/heavy.0.lock node view_check.mjs /home/user/cache/to3d-r44-s16-anya/view.png
```
`character.json`: her key, cache, the pictures' and films' windows. Viewer: `tools/web/view.html`.

## Measured

Standing with the book, from the front, against the drawing's sprite with its outline: 642 of 669 pixels are the
same (96 %); the rest are the hands at the book, the sleeves' edges and two pixels by the neck. A smooth render
shrunk by averaging has 595 colours; ours 29.

## Licences

As Р43: the drawing and its code — ours (`styles/s16-pixel`); SOMA skeleton — NVIDIA, Apache-2.0
(`engine/data/soma/NOTICE`); Kimodo motions walk, run, wave — `engine/motions`. No neural images, no third-party
meshes, no libraries.

## What is weak

- The profile and the back are not from a drawing; the profile is plainer than the front face.
- Between the views (22–67°) the head shows the seam of its maps: a light band of hair left of the face, a wider
  fringe.
- Hair and skirt are stiff: nothing swings. Deep leans are impossible (see above); in the run the trunk and the head
  lean by a 30° step, the book and the locks go in stairs.
- Hands are two or three pixels at the book's corners; in the wave the head stands tilted a step, as Kimodo's wave
  leaves it.
- Sadness reads weakly on the sprite's face (brows of the hair's colour are lost on the skin).
- The portrait is not 3D (the drawing's own, with its eyes and mouth changing); the eye is level only.
