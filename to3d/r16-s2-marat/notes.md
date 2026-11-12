# Р16 — Марат, «Клаус», в 3D

What was done, why, how to repeat, and the licences of the bases.

## Why

Brief `docs/briefs/to3d.md`, part "Third round": style С2 «Klaus» gets two more characters in 3D beside Р5 (Аня).
This is the second, Марат — the new, huge one; the first is Р15 (Савелий Петрович, `to3d/r15-s2-savely`), made just
before by the same agent. The code is Р15's (which started from Р5's), copied here and changed for Марат; read
Р15's `notes.md` for what each tool is. The orchestrator commits.

## What the drawing gives

`styles/s2-klaus/tools/marat.py`: the head in front, three-quarter and profile, an expression sheet (joy, surprise,
sadness, anger; his rest is a wide smile), the figure laughing with a ladle up and a fist on the hip.
Sizes: the drawn figure is 835 units from the floor to the top of the hair → 1.94 m (the tallest of the cast); the
head is drawn at 0.46 of its frame → 1 head unit = 1.069 mm. The trunk is drawn 276 units wide — 64 cm.

## How it is built (tools/) — what differs from Р15

- `head.py`: the outline numbers (`_Y/_HW/_FW/_ZF/_ZB`) are read from the drawn front and profile: a wide heavy
  head, a short thick neck. Forms (blobs.py): the broad nose; the ears; the moustache with its tips swept up;
  **the beard** — the head's own surface points under the drawing's beard line (`in_beard`), thinned to one every
  9 units, a ball on each (thin at the sideburns, thick at the chin), a row of big balls under the jaw, all melted
  into one mass (k=6); **the hair** — 150 even directions from the skull's middle, a ball of ~2 cm where the ray
  meets the head above the hairline, hardly melted (k=1.6): each ball is a curl, the outline is the drawing's row of
  round arcs.
- `features.py`: the drawing's own functions — `marat.mouth` (every open mouth has teeth and a tongue),
  `marat.thick_brow`, `marat.smile_eye` (the eyes shut by laughter), `parts.eye` — laid out as in `head_front`.
  `skin-<mouth>`: smile, laugh, o, sad, angry and `a` (a smaller laugh, for speech); `eyes-<expr>-<lid><look>`.
  The brows are painted (black on skin, they change shape with the expression), not solids as Савелий's.
  The mouth is painted on the beard: the beard takes the `skin` sheet in the mouth's place, its normals there mixed
  with a smoothed beard's so the mouth lies on a plain form.
- `build.py`: Anny's man (`moood-man`) at its own height, made a barrel: hips ×1.9/2.0, waist ×2.1/2.2, chest
  ×1.95/1.9 (across/deep), trunk bones ×1.15, legs ×0.9 and 7 cm further apart, collarbones ×2.1 (the shoulders
  out), upper arms ×1.6 thick, forearms ×1.95, hands ×1.45, the belly forward, the chest a little back. The jacket
  is the trunk and upper arms pushed out 12 mm and smoothed (its folds, two rows of buttons and the trousers under
  the apron are drawn by the shader from the rest position); forearms and hands bare; a thick ring at each elbow —
  the rolled sleeve; the stand collar; **the long apron** — a shell round the hips and legs from the waist to the
  shins (30 rings × 72), on the pelvis, the thighs and a little the shins, a waistband and two folds by the shader;
  **the towel** — a strip laid over his left shoulder along the body's front and back depth, two pale stripes; clogs.
  Output `data/marat.json|bin` (52k vertices) + `data/faces/`.
- `web/klaus.js`: Р15's, plus the beard as a mover (it drops with an open mouth), and the first sheets' names taken
  from the pack.

Repeat: as in Р15's notes with this folder's names (`/home/user/cache/to3d-r16-s2-marat`, `marat.json`); heavy
commands through `flock /home/user/cache/heavy.$((RANDOM % 3)).lock`. Views: head pictures ortho, 600 px = 600
head units (centre y 1.688 m, height 0.6414 m); figure pictures 900 px = 2.091 m.

## What was tried and changed on the way

- The beard first reached the eyes and swallowed the moustache and the ears (balls too big, the line too high) →
  thinner, the line lower at the sides; twice.
- The rolled sleeves' rings first took their radius from the whole body's vertices near the elbow's plane and came
  out as hoops a metre wide → only the arm's own vertices.
- The apron's faces were turned inside out and shaded dark → turned back.
- The clogs were put at the floor's absolute height while the shortened legs ended higher → under the feet.
- The trunk at ×1.5–1.6 was only a big man; the drawing's barrel needed ×2.

## Not done

- The drawn pose (the ladle up, a fist on the hip, the body in one laughing arc): he stands plainly, arms off the
  barrel. No ladle.
- The mouth is painted from the front: in profile it is seen edge-on, a sliver; the drawing's profile has its own
  mouth. The eye in profile is likewise the front eye seen from the side.
- The beard's lower edge is lumps, not the drawing's row of small curls; the hair has no single cool sheen.
- The gaze leading the head, blended expressions (as in Р15).

## Licences of the bases

- Blender Human Base Meshes bundle v1.4.1 — CC0 (Blender Foundation).
- Anny body (`moood-man`, baked by moood from Anny) and the SOMA skeleton/skin — as in `engine/data` (SOMA:
  Apache-2.0, `engine/data/soma/NOTICE`); Kimodo motions from the moood studio (`engine/motions`).
- The drawing and its code: ours (`styles/s2-klaus`).
- three.js 0.160 (MIT), scikit-image (BSD), libigl (MPL-2.0), SciPy/NumPy (BSD). No neural image generation; StdGEN
  not used.
