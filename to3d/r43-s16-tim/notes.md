# Р43 — Тим, пиксель-арт (С16 → 3D)

What was done, why, how to repeat. Brief: `docs/briefs/to3d.md`, its part "Third round". Asked by Pavel through the
coordinator: С16 is one of the four new styles with no character in 3D; this is its first try. Р44 (Аня,
`to3d/r44-s16-anya`) is the second, by the same agent (Claude) with the same code.

## The idea: the 3D is looked at through the sprite's own pixels

The style's rule: every pixel is put by a decision; a smooth picture must not be shrunk (it turns to mush). So no
smooth picture is ever made. Read before choosing: Р21/Р22 (small proportions, simple forms on SOMA's joints, the
drawing's own numbers — their retargeting is used here), Р39 (a picture of "which piece, how far" turned into the
style in one pass), Р41 (few flat faces from the drawing's numbers), Р37/Р12 (each frame drawn again by the style's
means). Decided by the agent:

- **A part is typed, as a sprite is.** Head, ears, trunk, hips, thighs, shins, shoes, upper arms, forearms, hands —
  17 parts — each an ASCII map from the front and from the side (the head also from behind), in the style's own
  legend (`chars/tim.py: LEG`). The rows are the drawing's rows: the head, trunk, shorts, legs and shoes are cut out of
  `FRONT` and `SIDE` with the face's pixels given back to the skin; the arms are typed anew, hanging (the drawing has
  them raised and on the hip).
- **Two maps make a volume**, a voxel a pixel: in each row the front's pixels × the side's pixels, corners rounded by
  a superellipse (exponent 2.5), and then every pixel of either map that lost all its voxels gets the one nearest the
  middle back — both silhouettes are exact. The surface is the 0.5 level of the voxels read trilinearly (so it is not
  cubes), its normal the gradient of the same field blurred.
- **A picture**: an orthographic ray through each pixel's centre of the small grid; the nearest part gives the pixel.
  The colour is read from one map per part — the one drawn for the view nearest to the eye's (front, back, right
  side, left side = the side mirrored). Mixing the front's and the side's map on one form by the normal was tried
  first and gave blotches at three quarters; one map at a time gives clean clusters and a drawn pop between
  directions, as a game's direction sprites have.
- **Light**: the maps carry the drawing's shading (light above-left, fixed on the picture). For a pixel, the light's
  level (three levels) of the normal as it stands now is compared with its level in the view its map was drawn for;
  if it is darker now, the colour goes one step down its ramp; if it is lighter now and was in shade, one step up
  (never above the lightest step the part is drawn with). A highlight stays only where it is drawn: lifting mid
  tones gave big light blocks on Аня's hair. A pixel that the light alone has made single goes back. In the drawn
  views nothing changes at all.
- **Face**: `tim.js: face()` — typed pixels (eye 2×2 with the glint, blush, mouth) placed for the head seen at 0°,
  45°, 90° (read off `FRONT`, `Q`, `SIDE`) and moved between by whole pixels; the far eye narrows to a column and
  goes; a face looking left is the mirror with the glint kept on the light's side. Expressions (rest, joy, surprise,
  sadness, anger), a blink and three speech mouths are other sets of the same pixels. They are stamped only where
  the head is the visible part (an arm in front hides them).
- **Outline**: `px.py: outline` ported as it is (`vox.js: outline`).
- **Steady pixels**: parts marked `steady` (head, ears, trunk, hips) move by whole pixels against their rest place
  and turn by whole steps (`STEP` = 30°, about the turn's own axis; below 22° no turn at all — rounding at 15° made
  the head click aside for one drawing in the walk); the view follows the figure by whole pixels;
  12 drawings a second (`stage.js: FPS`); the turn is 16 directions. The viewer can switch each of these off.
- **The portrait** (56×56) is not made in 3D — at the sprite's voxel size a head cannot hold it. It is the drawing's
  own, in its dialogue box, and lives as a game's does: `drawing.py` exports the five drawn expressions and a blink
  (the resting face, the eyes' pixels given back to the skin, a lid line typed); `stage.js: portrait` swaps the eyes'
  rows and the mouth's rows.
- **Skeleton and motion**: SOMA's joints (no fingers) at the sprite's places (`tim.js: J`); Kimodo's motions through
  `conv.py` (Р21's) and `rig.js` (the retargeting of `r22-s5-kira/tools/web/core.js` rewritten without three.js:
  each joint's turn against SOMA's rest, a fixed turn that lays our limb along SOMA's, upper arms kept off the body,
  hands kept out of the big head, the feet on the ground). Walk, run, sneak, jump are Kimodo's as they are. The wave
  is the drawing's pose with the forearm swinging over Kimodo's wave of the body (Kimodo's arm on arms this short
  ends at the cheek).
- **Scene**: the style's own backdrops from `sheets.py` (`backdrop`, `street`) on the same grid, the two rows of
  shadow of `sheets.stand`.

No Anny body, no base head, no Blender, no WebGL: at 32 pixels of height nothing of them would be seen. All is a few
hundred lines of JavaScript that run the same in Node (pictures, films) and in the browser (the viewer, 60 frames a
second on a processor alone).

## Files

| File | What |
|---|---|
| `tools/web/vox.js` | the palette, a part from its maps, the picture (rays, maps, light), the face stamps, the outline |
| `tools/web/rig.js` | quaternions, SOMA's joints, Kimodo's motion onto them |
| `tools/web/stage.js` | backdrops, shadow, the drawing's sprites and portrait, clips, the face's life (blinks, speech) |
| `tools/web/tim.js` | **his own**: the parts' maps, joints, face pixels, the drawn pose, clips |
| `tools/web/char.js` | one line: which character the viewer shows |
| `tools/web/app.js`, `view.html` | the viewer |
| `tools/drawing.py` | the style's data → `web/drawing.json` (palette, sprites, portraits, backdrops) |
| `tools/lib.mjs`, `make.mjs`, `png.mjs` | pictures and films (Node; films through ffmpeg under a shared lock) |
| `tools/look.mjs`, `look2.mjs`, `view_check.mjs` | sheets to look at while working; the viewer opened in Chromium |
| `tools/conv.py`, `tools/motions/` | Kimodo's motions from `engine/motions` in the form the retargeting reads |
| `tools/character.json` | the character's key and cache |

## Repeat

```
cd to3d/r43-s16-tim/tools
python3 drawing.py tim                      # web/drawing.json
python3 conv.py walk run sneak jump wave    # tools/motions (needs /home/user/moood/engines/1/soma.bin)
node make.mjs stills                        # ../pics/*.png; prints the pixel counts against the drawing
node make.mjs films                         # ../pics/*.mp4; strips of each clip go to the cache
node look.mjs; node look2.mjs walk          # sheets in the cache to look at
flock /home/user/cache/heavy.0.lock node view_check.mjs /home/user/cache/to3d-r43-s16-tim/view.png
```
A picture takes a few milliseconds; all films under a minute. By hand: serve the repository root, open
`to3d/r43-s16-tim/tools/web/view.html`.

To add a character of this style: copy `tools/`, write `<name>.js` beside `tim.js` (see also `anya.js` in Р44: a
skirt, long hair, a book held), point `web/char.js` and `character.json` at it, add its blink to `drawing.py: BLINK`.

## Options a character may set (`vox.js`)

`MIX` (Аня): the maps are chosen pixel by pixel by the form's own facing as well as the view's — for a head that is
hair all round a small face; skin is still read only from the map of the part's own view. `SIDE_FROM`: from what
turn a part is read from its side map (45°). `SKIN`: the ramps a face may be stamped on (`s`).

## Measured

Standing, from the front, against the drawing's sprite with its outline: in the drawing's pose 406 of 455 pixels
are the same (89 %), every different one belongs to the two arms; with the arms down 386 of 478. The picture shrunk
by averaging from a smooth render has 400 colours; ours has 20.

## Bases and licences

| What | Where | Licence |
|---|---|---|
| The drawing and its code (pal.py, px.py, sprite.py, portrait.py, sheets.py, chars/tim.py) | `styles/s16-pixel` | ours |
| Retargeting (the way of `experiments/indie`, Р21/Р22) | `to3d/r22-s5-kira/tools/web/core.js` | ours |
| SOMA skeleton | `engine/data` (NVIDIA; `engine/data/soma/NOTICE`) | Apache-2.0 |
| Kimodo motions walk, run, sneak, jump, wave | `engine/motions` | as the engine's |

No neural images, no third-party meshes, no libraries in the page.

## What it keeps of the drawing and what it can't (the first try)

Keeps: the grid and the scale; the palette and its ramps (nothing outside them can appear); the coloured selective
outline by the style's rule; the drawn front and side, pixel for pixel, for all that isn't an arm; the face's typed
pixels in every view; clusters (one map on a form, no lone pixels from light); steady pixels in motion; the two
scales with the portrait in a dialogue box.

Can't:
- Decisions are made once — in the maps and the face. Whatever lies between (a leg in a stride, an arm at an angle,
  the head half turned) is put by a rule: steps and stray pixels an artist would not leave.
- The drawing's three-quarter view is another drawing of nearly the same silhouette with the features moved; the 3D
  turns the head honestly and the front map slides over it (the fringe widens; at 112° a cheek without a face).
- Hands are lumps; the open hand of the drawing's wave is lost.
- The trunk keeps its stripes even only while it leans less than 22°; in the run it leans by a 30° step and the
  stripes go in stairs.
- The portrait is not 3D.
- Views from above: no maps typed for them; the eye is level only.
