# Р48 — Савелий Петрович, пиксель-арт (style С16) in 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, third round; brief: `docs/briefs/to3d.md`): Савелий Петрович
of С16 (`styles/s16-pixel`: a 37-pixel sprite in three views, a 56×56 portrait, an expression sheet) made a 3D character
on SOMA's skeleton that moves by Kimodo — and is shown only as pixel art. First try of this style in 3D.

## Which way, and why

Two ways were open: render the 3D small with the palette and clean it by pixel rules, or draw a sprite by hand with the
3D as a guide. Taken: **the first, with the face from the second** — the way Dead Cells makes its sprites (3D models
rendered small without smoothing), with the style's rules applied to every pixel afterwards, and the face's few pixels
put by rule as a pixel artist would put them.

Why: the style says "every pixel is put by a decision; a smooth picture made smaller gives mush". A small render is
exactly that mush unless something decides each pixel. So the 3D is never shown; it only answers three questions for
each pixel — which material is here, is it turned to the light, how far is it — and `tools/web/pixel.js` decides the
pixel from the answers by the style's rules. What a sprite's ten face pixels are cannot be had from any render (an eye
is one dark pixel, a brow three white ones): those are signs, and they are put as signs.

## How a frame is made (`tools/web/savely.js`, `pixel.js`)

1. **The unseen render**: orthographic, 1 sprite pixel = 1 unit of the model, 4×4 samples a pixel, no smoothing. Each
   sample: material id, light (two readings: for shade and for shine), depth.
2. **One material a pixel**: a pixel is filled when at least half its samples hit the figure; its material is the one
   with most samples, small things weighted up (strap, loupe, lens, bow tie, watch, moustache) so they are not lost.
3. **One step of the material's ramp** (`pal.py`'s ramps): shade where the form turns from the light, shine on the
   bald dome only. The light is held to the view, upper left, in every view, as a sprite's is; the shade reading leans
   sideways so that it sits as the drawing's one column of shade on a form's right and undersides stay lit.
4. **No stray pixels**: a lone pixel of a material among others takes its neighbours'; a pixel sticking out of the
   silhouette alone is dropped; a pixel whose step differs from all its neighbours of the same material takes theirs.
5. **Forms parted by colour**: where one form lies before another of the same colour (a leg passing a leg), the far one
   gets a line of its shade. The white tufts are shaded as the style shades them: a band along the lower edge and where
   hair meets the face.
6. **The face's signs** (`faceSigns`): each pixel of the drawn front face — eyes, brows, cheeks, the red nose with its
   light and shade pixel, the mouth under the moustache — is a point of the head: x and row from the front sprite,
   depth from the side sprite. Each frame the point turns with the head, is put while its side of the head is toward
   the eye and nothing is before it, and only on the head's skin. The same for the vest's pocket edge, the watch chain,
   the watch's white face. Expressions at this size are brow patterns and the eye/mouth pixel (ours — the style's sheet
   is at portrait size only).
7. **The outline**: `px.py`'s `outline` ported line for line — one pixel round the figure, step 0 of the ramp it hugs,
   one step lighter above and to the left of light forms.
8. The backdrop, the floor's dithered edge and the two-row shadow under the feet are `sheets.py`'s.

**Motion**: 12 frames a second (a sprite's animation is few drawings; Kimodo's 30 are sampled). The figure is held to the
pixel grid: the eye goes along with the pelvis exactly and the floor goes by in whole pixels — otherwise the whole
sprite "swims" as it slides between pixels.

**The portrait** (the dialogue box, 56×56): the same 3D seen 2.6× closer through the same rules, put together in layers
as the style's portrait is — body (lower by a neck the small sprite has not), neck, head — and the portrait's own face
laid on the head where its middle falls: `tools/gen.py` runs the lines of `chars/savely.py`'s `portrait(expr)` that draw
eyes, brows, wrinkles, nose, cheeks, moustache and mouth on an empty canvas (and the shirt front, bow tie, buttons for
the chest), for each expression of the sheet. Front view only, as a game's portrait. Alive by whole frames
(`tools/web/live.js`, seeded, no sines): blinks at uneven times, the eyes jumping to a side and back, the mouth of speech
closed / half / open by syllables, a change of expression through a blink.

## The form (what each base gave)

- **Base: the indie constructor's way (as Р4), not Anny, not a Blender head.** The sprite is three heads tall, the head
  a rounded block; `docs/findings.md`: "for 2–3 heads tall, our indie constructor — a human body can't be bent into it".
  `tools/web/forms.js` (the constructor's signed-distance forms and mesher, copied through Р4) gives the meshes;
  the skeleton is SOMA's joints without fingers placed on the sprite; skinning by the constructor's rules.
- **Sizes are the drawn sprite's own grid**: skull 11 × 13 × 10.4, legs 4 wide with 1 between, sleeves 3 wide, vest 9
  wide, shoes with the toes out… From the front the result agrees with the drawing in 79 % of pixels (417 of 529),
  three-quarter 66 %, side 66 % (`make.py` prints it; `pics/turn-overlay.png` shows where they differ).
- Head forward of the body (he stoops, as the side sprite), tufts at the back corners of the head (beside it from the
  front, behind it from the side), moustache of two lobes, the nose a bump for the profile, the strap round the head,
  the loupe over his left eye with its lens.
- **The drawn pose** (right hand with the watch before the belly) is a pose of the arm bones on top of the rest or of a
  motion; the watch rides an upright joint in the hand (not SOMA's). In motions that use the arms the watch is "in the
  pocket" (hidden), the chain stays.
- **Kimodo's motions** from `engine/motions` (walk, idle, wave, stomp), converted by Р4's `conv.py`
  (`tools/motions/`), retargeted Р4's way. Corrections on top: Kimodo's waiting stoop taken out by 70 %; arms kept off
  the vest and out of the head; in the wave the neck's and head's turn against the chest taken at 45 % (Kimodo tips
  the head ~30° sideways there — on a head a third of the figure it read as a broken neck).

No neural networks; nothing third-party but three.js.

## Repeat

```
cd to3d/r48-s16-savely/tools
python3 gen.py                 # web/data.js from styles/s16-pixel/tools: palette, drawn sprites, portrait face layers
python3 make.py stills         # ../pics: comparisons, steps, expressions
python3 make.py films          # ../pics: turn, walk, idle, wave, stomp, face (or name some: make.py walk face)
python3 conv.py walk idle …    # tools/motions from engine/motions (needs /home/user/moood/engines/1/soma.bin)
```
`run.sh` runs `shots.mjs` under one of the shared locks: headless Chromium (software WebGL) opens
`web/view.html?shots`, three.js r160 is routed to `/home/user/cache/n3-cloth/node_modules/three`, and the page returns
each picture as a grid of colour keys; `make.py` turns grids into PNGs enlarged by a whole factor and into mp4s.
A picture takes ~0.15 s in software. By hand: serve the repository root, open `to3d/r48-s16-savely/tools/web/view.html`
(drag to turn; sprite / portrait; motion; expression; talk; play / pause / scrub).

## What it keeps of the drawing and what it can't

Keeps: the palette (only `pal.py`'s keys reach the screen), the grid, the coloured selective outline, shade as
clusters, the face's pixels, the figure's sizes; from the front it is nearly the drawn sprite, and it stays one in any
turn and in motion.

Weak, honestly:
- **A decided pixel is not a placed pixel.** In a turn or a step the silhouette changes by rule, not by an artist's
  choice: single frames have corners a pixel artist would clean (a shoe's toe, a hand's lump, the tuft's edge), and
  from frame to frame a contour pixel can flicker. A hand-drawn walk has 6–8 chosen poses; this one has 12 computed a
  second.
- **Tufts** are smooth lobes — in three-quarter and from the side they read as white balls (cotton, ear-muffs in the
  portrait) rather than the drawing's ragged hair.
- **Side view**: the drawing shows the forearm across the body and the watch hanging on its chain; ours keeps the front
  drawing's pose (watch at the belly), so from the side the watch is half hidden. The loupe's lens is not seen from
  the side.
- **The portrait** is the front only; its face is the style's own code and matches the sheet, but the 3D under it is
  the small sprite's body: narrow square shoulders, a smaller loupe, a thicker strap, round tufts. When a motion tips
  the head, the face layer stays upright (it moves with the head's middle only).
- **Sprite-size expressions** are a few pixels (brows, eye, mouth) — readable enlarged, barely at true size.
- **Wave**: the arms are short, the hand comes to the ear rather than above the head.
- Hands are lumps (as the style's); clothes are part of the body's forms, no cloth.
- The viewer turns left and right only (a sprite has no view from above).

## Licences

Everything is ours: the drawing and its code (`styles/s16-pixel`), the constructor's forms (`experiments/indie`),
Kimodo's motions (`engine/motions`, made in the moood studio). three.js — MIT. SOMA's skeleton: as in `engine/`
(`engine/data/soma/NOTICE`).
