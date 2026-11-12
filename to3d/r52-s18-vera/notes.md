# Р52 — Вера, манга: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run; brief: `docs/briefs/to3d.md`): Вера of style С18
(`styles/s18-manga`, black-and-white seinen manga after Taniguchi and Urasawa) made a 3D character that moves by
Kimodo through the engine and is drawn every frame with that style's own pen and dot screentone — black and white
only, no shader look. The first try of this style in 3D.

## The idea

The С18 drawing is itself built from volumes (`head.py`: a head of cross-sections with features as 3D curves on it;
`hair.py`: strands on a shell; `body3d.py`: a posed skeleton). So the 3D takes the drawing's own numbers for the head,
and the way of Р12 (pen and watercolour) for the look: the 3D is never shown as 3D — each frame is drawn anew.

1. **The unseen picture** (`web/vera.js`, WebGL, off-screen): for every pixel — which tone it has (skin, hair, coat,
   blouse, lapel, the skirt in the coat's opening, legs, shoes, folder), whether its surface is turned from the light
   (`head.py` LIGHT3, fixed in the camera's frame as on a page), and its depth. The coat's front — the blouse's strip,
   its collar on the chest, the lapels, the opening below — is not geometry: it is found per pixel from where the point
   lies on the resting figure (crisp edges at any size).
2. **Tone**: every pixel becomes black or white. Paper for skin; solid black for hair; dots on a 45° grid, 4.6 px
   apart and fixed to the page (as screentone is), for cloth and for shadow — the levels are `chars/vera.py`'s (coat
   0.6, its shadow 0.9; legs 0.1 / 0.3; shoes 0.7; lapels 0.75; skirt 0.5; the face's shadow 0.16; under the jaw 0.3).
   Cast shadow: a pixel is shaded when something nearer stands up-left of it (the jaw on the neck, an arm on the coat,
   the hem on the legs). The black band on the lower right of a form — the drawing's «black copy moved under the
   white one» — the same test a few pixels away.
3. **Lines from the form** (Р12's way): mesh edges that are silhouettes or open edges, kept where seen, chained,
   smoothed, and drawn with `pen.py`'s `stroke` (ported: `web/pen.js`) — tapered ends, and the weight by `outline`'s
   rule: heavier where the contour faces away from the light. On the face only contours of skin against something
   else are lines; the rest of the face is drawn.
4. **The face is drawn, not modelled**: `head.py`'s eye, brow, nose, mouth, ear lines and `features.py`'s wrinkles
   and glasses, ported line by line (`web/head.js`). There they are 3D curves on the head's surface seen through a
   `View`; here the view is the moving 3D head in the camera (four marker points skinned to the head carry its frame),
   so the same code gives every angle. A line is cut where a hand or the hair stands in front. The open jaw moves the
   chin of the mesh as `Head` moves its sections.
5. **Lines that belong to the form**: the coat's front edges, lapels and collar (curves laid on the surface in
   `build.py`), white streaks of light along the hair's strands on the lit side, black teeth at the hairline, the loose
   strand at the temple.

Films are drawn 12 times a second and each drawing held for two frames of 24 (on twos).

## How the form is built (`tools/build.py`; what each base gave)

- **Body, hands, legs, skeleton — Anny `moood-woman`** (`engine/data`) with SOMA joints and weights, by Р7's way
  (joint moves and per-joint affines, frames untouched): slimmer trunk and limbs, narrower shoulders, legs 4 % longer
  and nearer each other, smaller hands. Units: the drawn figure is 7.39 body units tall with its head on → 1.72 m.
- **Head — the drawing's own** (`head.py` `Head` with `chars/vera.py` `HEAD`): its cross-sections lofted into a mesh
  with the nose wedge and the lips' bump, 1.08 of the body's unit as `figure.py` draws it; ears — the drawing's ear
  plates; neck — its neck rings. No artist's base head here: the look takes only the silhouette and the turn from the
  light from the mesh, and these are the drawing's exactly (findings: «when a style's drawing code already builds a
  volume, fit to those numbers»).
- **Hair — the drawing's shell** (`hair.py` `Hair.shell`, `shell_ray`): a grid whose columns are the strands from the
  hairline to the bun; the bun a ball.
- **Coat** — Anny's trunk and arms pushed out and smoothed (a straight heavy cloth), from the waist a lofted shell to
  the hem (Р7's skirt; kept off the legs in motion by Р1's push), a low stand collar ring. **Shoes** — Р7's loft.
  **Folder** — a board, only in the drawn pose.

No neural models; no Blender; Human Base Meshes not used.

## Live

- `web/face.js` — Р1/Р12's timing (blinks with log-normal intervals, saccades, gaze leading the head's turns with a
  blink on big ones, speech as syllables through a spring, expressions mixed through damped springs, brows first)
  driving `head.py`'s numbers (`EXPR`: open, squint, brows, knit, smile, mopen, mwide, frown, jaw; look). The five
  expressions are the sheet's `EXPR` over Вера's rest (tired lids, a slight frown).
- Motions: Kimodo's from `engine/motions` through the engine's retargeting and skinning (dual quaternions). A pose
  layer curls the fingers a little (Anny's rest hand is flat and spread).
- `web/view.html` (`ui.js`) — drag to turn, wheel nearer, motion, play/pause, scrub, expressions and their mix, talk,
  the face close; drawn 12 times a second.

## Repeat

```
cd to3d/r52-s18-vera/tools
python3 build.py                # → ../data/vera.json|bin (2 s)
python3 make_pics.py stills     # ../pics: compare, overlays, steps, back, expressions
python3 make_pics.py films      # ../pics: turn, walk, wave, talk
```
`shots.mjs` (Р12's) serves `/home/user/` and drives `web/view.html?pack=…` with Playwright (software WebGL; three.js
routed to `/home/user/cache/n3-cloth/node_modules`); every browser run takes one of the shared locks. A drawing takes
about a second in software. `node check_view.mjs out.png` opens the viewer as a person does and reports page errors. By hand: serve the repository root, open `to3d/r52-s18-vera/tools/web/view.html`.

## Licences of the bases

- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`). Kimodo motions: `engine/motions`.
- The С18 drawing and its code (`pen.py`, `head.py`, `features.py`, `hair.py`, `chars/vera.py`): this repository.
- three.js 0.160 (MIT).

## Honest state

- The head and face match the drawing closely in all three views (the same numbers), the picture reads as the same
  manga: pen with pressure, dots, white paper, black hair with streaks.
- The body is Anny made slim, still fuller and softer than the drawn stick figure; shoulders slope where the drawing's
  are square; sleeves crease at the elbow.
- Hands are Anny's realistic hands in outline: larger and busier than the drawing's small simple ones; at the glasses
  the fingers are a tangle.
- The tone is fixed to the page, so in motion the dots stay still and the figure slides under them — right for a
  page, a shimmer in a film. Contours come from mesh edges: in motion small lines at the elbows and the collar come
  and go.
- In a step a hand swinging behind the hip can show through the coat's lower shell as a white patch.
- Coat and hair are skinned shells: no swing of the hem, no folds; the stand collar's edge against the coat is ragged
  at some angles. The nape below the hair is bare, as the drawing's hairline says.
- Kimodo's `wave` tilts the head under the arm, `idle` stoops (the motions' own); the talking film stands still for
  that reason.
- No expression sheet of Вера exists in the style (only of four others); the expressions are the style's `EXPR`.
