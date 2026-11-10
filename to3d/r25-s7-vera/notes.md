# Р25 — Вера, Гибли (style С7) in 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, third round; brief: `docs/briefs/to3d.md`, "Third round";
asked for by Pavel through the orchestrator): Вера of style С7 (`styles/s7-ghibli`) built in 3D the way Р9 (Аня of the
same style, `to3d/r9-s7-anya`) was, from the same bases, with the same look, live face and viewer — and the tools made
to serve any character of this style (Р26 Кира is built by the same tools; only `tools/config.py` differs).

## Why this way

С7's drawing is itself built from simple 3D forms (`styles/s7-ghibli/tools`): head rings with a middle profile, a
torso loft, limbs as tubes along a posed skeleton, hair as a shell plus locks along Bézier curves, the face as flat
templates on the head's surface. Р9 showed that taking those very numbers makes every view match by construction.
So here too. Вера has no turnaround and no expression sheet on the style's page (only a portrait and a figure):
`tools/refs.py` draws both with the style's own code, unchanged (`build.turnaround('vera', calm=True)`,
`build.expressions('vera')`), into the cache — the style's folder is not touched. The page shows them as the drawing.

## What is new against Р9 (and what its page named as weak)

- **One set of tools for the style.** `config.py` names the character; `drawing.py` reads its module; `build.py`
  follows its garment spec (a top with a turtleneck collar or a hood, a jacket open in front, trousers wide or narrow,
  shoes or boots, headphones, earrings); the face's design and the sheet's expressions go into the pack's header and
  `web/face.js` draws from them (lash, lid crease, eye tilt, the tired lines under the eyes, a crooked mouth).
- **The nose's hook goes to the far side of the face** as the head turns from the camera, and in profile only its wing
  is drawn — as the drawing does (Р9 kept it on one side).
- **Hands.** Р9 aimed the hand and bent the fingers by SOMA's first finger joints, which lie in the wrist; here the hand
  is aimed by the knuckles (joints 2), the fingers are brought together and bent at joints 2–4, the thumb is laid down
  along the hand. The hand now hangs as drawn.
- **Trousers as one piece** (`blob.py`): the pelvis loft and the legs' tubes as distance fields joined softly and meshed
  by marching cubes — the drawing fills them as one shape; no seam at the hips, the legs wide over the shoes as drawn.
- **Arms where the drawing has them** (only 2 % further out; Р9 had to move them off the skirt).
- **Ears and neck**: the ears' inner folds flattened (the outline draws the ear, not every fold of the base); the
  neck's shade follows the drawing's skull form; the jaw's seam smoothed more.
- **Skinning by dual quaternions** (`dqs` of the engine) instead of centres of rotation: the viewer opens in seconds
  (Р9: about a minute and a half).
- The line's width is set in pixels (`linePx`), so a picture rendered twice as large keeps the drawing's line.

## How it is built (and what each base gave)

- **Head — Blender Human Base Meshes, stylised head (CC0)** (`hbm_export.py`, `headfit.py`): as Р9 — sockets and mouth
  closed, heights mapped by landmarks, width and depth to the drawing's rings, the face laid on the drawing's own front
  surface. The base gave jaw, neck, ears, topology.
- **Face — the drawing's face parts, drawn live** (`web/face.js`): Вера's eye under a heavy lid with a crease and one
  lash, thin straight brows, the hook nose, the mouth with corners a little down, the tired lines under the eyes;
  expressions: `calm` (her resting face from the style's `build.py` CALM), `plain`, and the sheet's joy, surprise, sad,
  anger.
- **Body and skeleton — Anny `moood-woman`**: SOMA joints moved to the drawing's skeleton (hips 87 cm, shoulders 135,
  upper arm 28 / forearm 24). Kept of Anny: the hands with the wrists; everything else is under the clothes.
- **Clothes — the drawing's forms**: the sweater (torso loft + ease) with the turtleneck collar (a tube round the neck
  up to the chin, its top rolled in, one fold line); the jacket (bigger than the sweater everywhere, open in front as
  drawn, two buttons by the opening); sleeves (the arm tube + ease, a wider cuff, a fold line at the elbow); trousers
  (above); shoes (the drawing's heel → instep → toe tube, flat on the floor); gold earrings.
- **Hair — the drawing's hair** (`hair3d.py`): the shell, the swept front locks, the loose strand by the cheek, the
  tufts at the back, the knot as a ball, the flow lines as thin dark strips.
- **Look** (`web/char.js`, three.js 0.160): as Р9 — flat colour in the drawing's hexes, one warm shade tone with a hard
  edge, the light from the picture's upper left in camera space, one even dark-brown outline (inverted hull).
- **Motion**: the pack is an engine body (`makeBody`), played by the engine's `Figure` (retarget → skinning `dqs`):
  Kimodo's motions from `engine/motions` — walk, idle, bow, sit on the page; all of them in the viewer.
- **Live face**: Р9's (Р1's) `LiveFace` — log-normal blinks, saccades, the gaze leading head turns, speech mouth
  shapes on a spring, expressions mixed and settling as springs; seeded, so a film is the same every time.

Neural models were not used.

## Repeat

```
cd to3d/r25-s7-vera/tools
C=/home/user/cache/to3d-r25-s7-vera
(cd $C && npm install three@0.160.0)                         # the viewer's three.js for the headless renders
L="flock /home/user/cache/heavy.$((RANDOM % 3)).lock"        # heavy runs take turns (the brief)
$L /home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
   --python hbm_export.py -- $C/hbm_head.npz
python3 refs.py                                              # the drawing's turnaround and expression sheet → $C/refs
python3 build.py                                             # the pack $C/out/vera.json/.bin (≈20 s)
python3 bases.py                                             # the bases as they come, for the steps
$L python3 compare.py /cache/to3d-r25-s7-vera/out/vera.json $C/cmp
$L python3 make_pics.py stills turn                          # ../pics (stills, turn.mp4)
cp $C/out/vera.* ../data/
$L python3 make_live.py                                      # ../pics: the live face and the motions (reads ../data)
```

`shots.mjs` serves `/home/user/` and drives `web/view.html?pack=…` with Playwright (software WebGL; three.js routed to
the cache's `node_modules`). `look.py` makes quick strips while building. The viewer by hand: serve the repository
root with `python3 -m http.server` and open `to3d/r25-s7-vera/tools/web/view.html`.

Files: `config.py` (who), `drawing.py` (the style's code as numbers), `refs.py`, `headfit.py`, `hair3d.py`, `shapes.py`,
`blob.py`, `build.py`, `bases.py`, `compare.py`, `make_pics.py`, `make_live.py`, `look.py`, `mesh.py`, `pack.py`,
`web/` (viewer: `char.js`, `face.js`, `ui.js`, `view.html`). Pack format `r1/character` as Р1's, plus `ob` (outline
moved back), `face.shadow`, `face.params`, `face.expr`, `stand`, `headFwd`.

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`).
- Kimodo motions: `engine/motions`.
- The drawing and its code: this repository (`styles/s7-ghibli`). three.js: MIT. scikit-image (marching cubes): BSD.

## Honest state, what is weak

- Clothes and hair are skinned shells, not cloth: the jacket does not swing, in a deep bow its back stretches; sitting
  on the ground the jacket's hem goes into the thighs.
- The drawing's front view hides the shoes behind the trousers (it paints the trousers over them); in 3D the toes are
  seen in front of the trouser legs, as they would be.
- The drawing's collar is a round-bottomed tube painted over the chest; in 3D it is a collar round the neck, so its
  lower edge is not the drawing's arc.
- The jacket's shoulders are the drawing's (a notch where the sleeve's top was cut in the drawing) — kept, not improved.
- The skull is the drawing's "face mask" (flat at the back under the hair) — the hair covers it, as in Р9.
- The under-jaw and the neck behind the jaw are plain shade; close up the jaw's edge is still less clean than drawn.
- The hair is rigid; the loose strand does not move.
