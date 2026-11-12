# Р13 — Марат, укиё-э: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, third round; brief: `docs/briefs/to3d.md`): Марат of
style С13 (`styles/s13-ukiyo-e`, Japanese woodblock print) made a 3D character that moves by Kimodo through the
engine and is **printed every frame as a sheet** with that style's own brush, colours and patterns. It is the first
try of this style in 3D; the way is Р12's (a look drawn each frame from the 3D by the style's own code), changed for
a print.

## The idea

A print is flat colour areas from colour blocks, a black key line over them, patterns printed flat on cloth, paper
and wood grain; no light, no shade. So the 3D is never shaded. Each frame (`tools/web/marat.js`):

1. **The unseen picture.** The figure rendered into an off-screen buffer: which colour block and which part each
   pixel belongs to, and its depth (16 bit).
2. **The colour blocks.** The figure rendered flat on the page's canvas: each part in its block's one colour
   (`marat.py`'s: paper-skin, black, the jacket's warm white, terracotta, the shoes' black). The cloth's pattern is
   computed in the fragment shader in **the cloth's own flat coordinates** (`puv`, made in `form.py`): seigaiha waves
   on the apron (kit.py's `seigaiha`), ichimatsu checks on the trousers (`checks`), stripes on the towel. Bokashi — a
   second colour wiped along a hem (the apron's lower part, the jacket's hem, the trousers at the shoes) and the
   cheeks' round blush — is a per-vertex amount. The canvas lies 0.8 px off the lines: a print's blocks never
   register exactly.
3. **The key block.** On the CPU every mesh edge is tested: a silhouette (its two triangles face opposite ways) or
   an open edge (a hem, the apron's sides, the hairline), kept where the buffer says it is seen. On the face a
   silhouette is kept only where skin meets something else; the nose's own contour only near profile. Where two parts
   run into each other (the collar on the jacket, a sleeve into it, a trouser leg into the shoe, the neck into the
   collar) there is no silhouette — that line is taken from the buffer: the border between the two parts' pixels where
   the depth does not jump. Edges are chained, smoothed, broken at corners, and each run is one stroke of `kit.py`'s
   brush ported to JavaScript (`tools/web/print.js`, `brushPoly`): its weight changes with the stroke's direction (the
   brush held at a slant), a slow uneven pressure, pointed ends; heavier on cloth (jacket 4.0, apron 3.8) than on skin
   (2.1–2.3), as in `marat.py`. Along the beard's edge short hairs grow outward (`fringe`) wherever skin, cloth or the
   ground lies beyond it — the print's "hair by hair" edge.
4. **The face is drawn, not modelled.** `parts.py`'s `eye`, `brow`, `nose` (front and three-quarter, `broad`) and
   `mouth` with `marat.py`'s numbers, ported (`print.js`), drawn in head units on the 3D head through a grid
   (`build.py`: each node is a point on a head or beard triangle found from the front; every frame it is skinned and
   projected). Each feature has its own frame: the vertical as the head carries it, the horizontal foreshortened as
   the head turns but never below 0.6 (the drawing's far eye is 0.6 of the near one). The nose: the front drawing's
   strokes while he looks at us, the three-quarter drawing's one hooked stroke as he turns, the 3D's contour near
   profile. The mouth is drawn over the black beard, as on the sheet.
5. **Lines and signs of the form** (`build.py`): the apron's waist line and three folds (terracotta, as drawn), the
   jacket's front edge, two buttons, the small grey hooks of the curls.
6. **The sheet**: toned ground with bokashi along the top and an ochre one below, the border, the name's slip and
   the red seal (`kit.py`'s `ground`, `cartouche`); paper, wood grain and age (`kit.py`'s three filters) lie over
   everything and stay still — they are the sheet's, not the figure's.

Films are 12 prints a second, each held for two frames of 24.

## The form (what each base gave) — `tools/form.py`

- **Body and skeleton — Anny's stocky man** from the engine (`engine/data/bodies/anny-T-man-stocky-baby15`: Anny's own
  settings — shoulders 0.41 m against 0.34 of `moood-man`, thick limbs; its baby head is not used), × 1.05, SOMA's 77
  joints and its weights. A human body is enough for Марат: he is about 7 heads tall, only very wide — and the width
  is clothes. No constructor was needed. Of the body are seen the forearms (× 1.22 across), the hands (× 1.15, Anny's
  own fingers — the print draws every finger) and nothing else; its legs pushed out along the normals are the
  trousers; its weights carry all the shells. Shoulders 2 cm higher (a short neck), the stance a little narrower.
- **Head — Blender Human Base Meshes' stylised head** (CC0; Р1's export `hbm_head.npz`), fitted (`head.py`, Р1's way)
  to С13's front and side outlines (`parts.head_pts` with `marat.p`), eye sockets laid flat (the eyes are drawn). The
  head is 1.2 × the figure drawing's (`drawing.py: HEADK`) — nearer to the bust sheets, where it is drawn bigger.
- **Beard** — the lower face's own surface (subdivided once), lifted 3–15 mm off the skin, dropped under the chin and
  smoothed into one mass; its edge follows `marat.BEARDS` (front and side), parted a little under the nose so the
  nose's tip stays on skin.
- **Hair** — a cap of about a hundred round lumps over the skull (a golden-spiral scatter): its silhouette is the
  drawing's scalloped edge from every side; the hairline is `marat.HAIRS`' inner edge with small scallops.
- **Jacket** — a loft of rings: a barrel with the belly forward and a straight back, a round yoke; **collar** — a
  thick soft roll lying low in front; **sleeves** rolled over the elbow (a wide tube with a roll at its end);
  **apron** — a bib and from the waist a panel round the front down to the shins, its **straps** thin bands over the
  shoulders; **towel** over the left shoulder; **shoes** — one rounded form over each foot.
- Weights: shells take the body's nearest weights (the trunk's shells without the arms'), below the hips a skirt
  rule (hips + the leg of that side); in motion the apron and the jacket's hem are pushed off the legs' capsules
  (Р1's skirt code).

Neural models were not used.

## Live — `tools/web/face.js`

Р1's timing (blinks with log-normal intervals, fast-close / slow-open; saccades; the gaze leading head turns;
speech as syllables of mouth shapes through a damped spring; expressions mixed and changing as damped springs, brows
ahead), driving С13's numbers: brows' lift and tilt, the eye's opening (closing into the laugh's arc or into a
blink's line), the look, the mouth (how far open, how wide, corners up or down, bared teeth, the round mouth), the
blush. His own: **the laugh** — bursts of 3–7 "ha" about five a second from a seeded stream, which open the mouth
wider, throw the head back and shake the chest; feelings lean the head and chest (back in laughter, down in sadness).
Expressions: `grin` (his resting state), `calm`, `surprise`, `sad`, `anger`.

Motions: Kimodo's from `engine/motions` through the engine's retargeting and skinning (dual quaternions: centres of
rotation take too long to prepare in the browser). Viewer `tools/web/view.html` (`ui.js`): drag to turn, wheel nearer,
motion, play/pause, scrub, the five expressions and their mix, talk, face close; 12 prints a second.

## Repeat

```
cd to3d/r13-s13-marat/tools
# once: Р1's head export — to3d/r1-s3-anya/notes.md (hbm_export.py → /home/user/cache/to3d-r1-s3-anya/hbm_head.npz)
python3 form.py                 # → /home/user/cache/to3d-r13-s13-marat/form/marat.json   (peek.py: a quick look at it)
python3 build.py                # → ../data/marat.json/.bin
python3 make_pics.py stills     # ../pics: compare, overlays, steps, back, expressions
python3 make_pics.py films      # ../pics: turn, walk, wave, dance, talk
```
`shots.mjs` serves `/home/user/` and drives `web/view.html?pack=…` with Playwright (software WebGL; three.js routed to
`/home/user/cache/n3-cloth/node_modules`); heavy runs go through the shared locks `/home/user/cache/heavy.N.lock`.
By hand: serve the repository root, open `to3d/r13-s13-marat/tools/web/view.html`.

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`; Kimodo's SOMA skin Apache-2.0).
- Kimodo motions: `engine/motions`.
- Р1's and Р12's code (head fitting, the frame's pipeline, the live face's timing) and the С13 drawing and its code
  (`kit.py`, `parts.py`, `marat.py`, ported): this repository.

## What the style keeps in 3D and what it doesn't

Keeps: the sheet (ground, bokashi, border, slip, seal, paper and grain), flat colour with a pattern, the brush line
with weight by direction, the face of a few signs on bare paper, the beard's hairy edge, the curls' scalloped edge.

Doesn't:
- **The pattern follows the cloth.** In the drawing a pattern is printed flat over the shape and ignores folds and
  turns. Here it is flat in the cloth's own coordinates, so it does not swim when he moves — but it narrows at a
  form's turning edge (the trousers' checks squeeze at the leg's sides and blur there; the apron's waves near its
  sides). A pattern fixed to the sheet would be truer in a still and would crawl over him in motion.
- **The line traces the form.** A print's line is a decision — few folds, each a calligraphic gesture; here lines are
  where the 3D has silhouettes. There are no drawn folds except the apron's three; sleeves and jacket are plain.
- **Hands** are Anny's, outlined: every finger is there, as the print wants, but they are a real hand's fingers, not
  the print's soft tapering ones; a fist is a tangle of short lines.
- **Profile**: the mouth is a front sign squeezed onto the beard's side, the nose is the base head's small one
  (the drawing's profile has a big nose that is part of the contour).

## Honest state

- Good: reads as a print at once, also in motion; next to the drawing it is the same man — laughing eyes, the beard
  with hairs at its edge, the curls, the white jacket, the apron's waves, the checks. Big, wide and warm, not a lump.
- Weak: the arms are long against the drawing's (a real man's arms on a figure drawn with short ones) — in the
  drawing's pose the open arm reaches far; the sleeves are boxes at the shoulders; the towel is a stiff strip; the
  apron and the jacket are shells — in a wide step the apron is pushed by the legs, not draped; from behind the
  apron's inside shows between the legs.
- The beard's and the hair's edges are a mesh's: small steps are smoothed by the line, but at the ear the sideburn's
  edge is ragged.
- In films the line's small pressure waves change from print to print (it "breathes" a little), and where a
  silhouette appears or ends the line pops.
