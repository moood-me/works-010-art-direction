# Р21 — Тим, инди (style С5) in 3D

Third round of "Рисунок в 3D" (`docs/briefs/to3d.md`, "Third round"): the style's second character after Вера (Р4,
`to3d/r4-s5-vera`). Asked by Pavel through the coordinator; made by an agent, one after the other with Кира (Р22).

## What was done, and why this way

- **Base: the indie constructor, as for Вера, not Anny.** Тим in С5 is 2.2 heads tall (269 units, the head 123): a
  human body can't be bent into that, and his face is a few signs on a ball. So: simple forms as signed distances,
  meshed (surface nets), each tied to a SOMA joint, a flat two-tone look with an outline, Kimodo's motions retargeted
  onto short limbs — Вера's code. No third-party base is used.
- **Вера's code was split so a character is only its numbers.** `tools/web/core.js` is the figure every character of
  the style shares (ring stacks → distances, building and skinning, the look, the scene, the camera, the retargeting,
  the clips); `face.js` + `live.js` are the drawn face and its life; `tim.js` and `face_def.js` are Тим: the drawing's
  rings, paints, joints, parts, expressions. Кира (Р22) uses the same `core.js`, `face.js`, `live.js` unchanged.
- **The forms are the drawing's own numbers** (`styles/s5-indie/tools/cast.py`, `tim`): head, tee, shorts, sneakers,
  the cap's brim are its ring stacks; legs, arms, socks its tubes; hands its spheres; the hair is the head grown by 6
  units above the hairline keys with its tufts, the cap the head grown by 9 above the cap's line; stripes, the white
  sole line, the plaster on the knee, the slingshot at the back pocket — at the drawing's coordinates. 1 unit = 2.5 mm
  (as Вера), so he is 0.69 m tall beside her 1.16 m.
- **Departures from the numbers:** the ears are discs turned outward (9 wide from the front, ~12 from the side; the
  drawing draws an ellipse 9 wide from the front and 15 from the side — no one solid does both) and sit a little
  further back than phi 1.57, as the drawing's turn puts them; the hair thins toward its edge so the tufts lie on the
  forehead; the tee's stripes go all round (the drawing draws only the front half); the button is on the cap's top
  (the drawing shows it as an ellipse a little below the top, as if seen from above).
- **Lines the outline can't give.** The inverted-hull outline draws silhouettes, not an edge lying on another form.
  The drawing strokes the hairline and the cap's edge, so these are thin dark tubes along the same lines
  (group `edges`); the ear's inner line likewise.
- **Face.** `face.js` is Вера's port of the drawing's face code (`face.py`) made general: the character's numbers
  come as a config (eye size and place, brow, cheeks, lash weight, extras — his freckles and the plaster on the cheek),
  each brow has its own numbers (his neutral face has one brow up), and a mouth is any closed shape of two cubic curves
  with teeth, a gap, a tongue as amounts — so his crooked smirk, the grin with the missing tooth and the clenched teeth
  mix and move like Вера's straight line. `face_check.mjs` puts it beside the drawing's own face (`face_tex.py` takes
  the face layer from `cast.tim`): the five expressions match line for line (the grin's lower edge is one curve in
  place of the drawing's two — a hair's difference).
- **The face turns on the head as the drawing turns it** (new; Вера's page named this as her weak spot). The drawing
  puts face signs 0.38·sin(yaw) further round the head than the skull (`cast.fs`), so in three-quarter and profile the
  face doesn't sink into the edge. Here the head's shader does the same for the eye that looks: the drawn face slides
  round the head by that angle (uniform `uCheat`, set every frame from where the camera is against the head). The
  model itself is untouched — geometry, skeleton, texture are honest; the engine may leave the turn out
  (`A.set({cheat: 0})`), `pics/cheat.jpg` shows both. In a turn of the head the face goes a little ahead of it.
- **Face lines** follow the outline's width (`line` in `A.set`), so on a close-up they are as thin as the drawing's.
- **The head's tilt** of each expression turns the head about its own centre, as the drawing does (Вера's turned it
  about the neck; with his −6° that would shift the head sideways).
- **Shade:** skin has a narrower crescent than clothes (threshold 0.1 against 0.28), as the drawing's offsets (.05
  against .09) make it.
- **Skeleton:** SOMA's joints placed on the drawing; the arms' rest is the drawn one — hands behind his back.
- **Motions** (`tools/motions`, converted from `engine/motions` by `conv.py`): walk, run, sneak, jump, wave — arms on
  their own bones, retargeted as the legs are, kept ~17° off the body and out of the big head; look round — Kimodo's
  waiting motion (85 % of its average stoop taken out) with head turns on top, the arms kept as drawn, behind the
  back. Live face as Вера's (blinks, saccades, the gaze leading the head, speech, blended expressions), with his own
  phrases.
- **Viewer** `tools/web/view.html` (+ `ui.js`): Вера's, the clips and their cameras now come from the character.
- A flat ground ellipse stands behind the feet in the drawing's views (a floor is edge-on there); on the floor in others.

## How to repeat

```
cd to3d/r21-s5-tim/tools
(cd /home/user/cache/to3d-r21-s5-tim && npm i three@0.160.0)   # three.js for the headless pictures
python3 conv.py walk run sneak jump wave idle sit   # tools/motions from engine/motions (needs /home/user/moood/engines/1/soma.bin)
python3 face_tex.py && node face_check.mjs          # the canvas face against the drawing's: <cache>/tex/check.png
python3 make.py stills                              # the pictures → ../pics
python3 make.py turn walk run sneak jump look face  # the films → ../pics (software WebGL: 1–4 s a frame)
```
`shots.mjs` serves the repository, opens `tools/web/view.html?shots` in headless Chromium (Playwright), routes
three.js r160 to the local copy, and calls `window.A.set({...})` / `A.frame({...})` per shot. Building the meshes
takes ~15–30 s in the page.

To add a character of this style: copy `core.js face.js live.js forms.js rings0.js ui.js view.html`, write
`<name>.js` + `face_def.js` with its numbers (see `tim.js`; Кира's `kira.js` shows a leaned rest pose and an arm held
by the body).

## What is weak (honestly)

- Arms are tubes of one width and hang to mid-thigh; in the jump and the wave the hands come to the big head and are
  pushed outward by rule, so the gesture is smaller and stiffer than Kimodo's.
- The tufts' tips are sharper than the drawing's rounded ones, and their edge is slightly uneven on close-ups.
- In profile the mouth is almost out of sight (the drawing shows it on the edge); the ear is smaller than drawn.
- The face's turn on the head is a trick of the picture: with it the eyes come nearer the ear in profile than in
  the drawing, where ears and hairline turn too.
- In the sneak, with the arms bent before the chest, the short sleeve's edge pinches into a sharp corner at the elbow.
- Clothes are rigid shells: the tee doesn't crease, the shorts' legs go with the thighs and show a fold at the hip.
- Speech has no sound; its rhythm is the text's.

## Finished by a second agent

The first agent's run was cut off by a container restart after the stills and the turn, walk and run films. A second
agent (same task, from the coordinator) made the three films the page named but didn't have — `python3 make.py sneak
look face`, through the shared lock (`flock /home/user/cache/heavy.N.lock …`) —, looked at every picture and film, and
moved the face film's camera back (dist 1.05 → 1.2: the ear was cut by the frame). Nothing else was changed.

## Licences

Ours: the drawing and its code (`styles/s5-indie`), the constructor's forms and mesher (`experiments/indie`), Вера's
page code, Kimodo's motions (made in the moood studio, `engine/motions`). three.js — MIT. No third-party models, no
neural networks.
