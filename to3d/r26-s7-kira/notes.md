# Р26 — Кира, Гибли (style С7) in 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, third round; brief: `docs/briefs/to3d.md`, "Third round";
asked for by Pavel through the orchestrator): Кира of style С7 (`styles/s7-ghibli`) built in 3D by the same tools as
Р25 (Вера, `to3d/r25-s7-vera` — its `notes.md` tells what the tools do and what is new against Р9, Аня); only
`tools/config.py` differs (who, the cache, her motions, the hair locks' mesh size, the arms' offset).

## Why this way

As Р9 and Р25: С7's drawing is built from simple 3D forms, the 3D takes those very numbers, every view matches by
construction. Кира has a turnaround and an expression sheet on the style's page; `tools/refs.py` renders them from
the style's SVG.

## What is hers

- **The slouch is in the rest shape.** The drawing's 'stand' pose leans the upper body forward (4.5 cm at the
  shoulders), pushes the head forward, raises the shoulders a little and bows the head 6°. The torso's rings, the
  trunk's joints, the neck and the head are built that way, so she slouches standing — and in every Kimodo motion,
  since a motion turns the joints from this rest. The head's bow is given to the viewer (`headFwd`), which needs the
  face's direction for the nose's side.
- **Body**: thin (shoulders 11.8 cm from the middle, arm radius 2.9 → 1.8 cm). Anny `moood-woman` gives the hands
  (made thinner with the arm), the SOMA skeleton and the weights; nothing else of it is seen. No child or teen body
  was needed: the figure is the drawing's forms.
- **Face**: a longer face, eyes smaller than Аня's with one lash and a tilt, low thick brows, a lilac-grey iris;
  her own expressions from her module (`kira.CALM`, `kira.EXPR`): the look from under the brows and aside, joy as a
  crooked half-smile with a blush (never an open smile), anger without a tongue.
- **Hair**: the shell, the long fringe's four pointed locks across the forehead over her left eye (in 3D they really
  cover the eye — from her right the eye is seen behind them), the short side bits, the jagged back, the tuft on the
  crown, two rows of tufts with a swirl.
- **Clothes**: the hoodie (torso loft + 3.4 cm; under the hood it comes in to the neck — the drawing paints the hood
  and the headphones over the chest, in 3D they must lie outside it; the hem goes round the thighs), the kangaroo
  pocket and the hem band as lines on its surface, sleeves with cuffs; the hood as a soft roll round the neck, high
  at the back, open at the throat (`blob.py`: tubes joined softly), two drawstrings; the headphones — a band behind
  the neck, pads, acid-yellow cups with a ring on each; narrow trousers (pelvis and legs as one piece); heavy boots
  (foot and shaft as one piece, a separate thick sole, four acid laces).
- **Motion**: walk, sneak, sit on the page (and the idle close-up); all of the engine's motions in the viewer.

Neural models were not used.

## Repeat

```
cd to3d/r26-s7-kira/tools
C=/home/user/cache/to3d-r26-s7-kira
(cd $C && npm install three@0.160.0)
L="flock /home/user/cache/heavy.$((RANDOM % 3)).lock"        # heavy runs take turns (the brief)
$L /home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
   --python hbm_export.py -- $C/hbm_head.npz                 # (here the file was copied from Р25's cache: the same export)
python3 refs.py                                              # the drawing's turnaround and expression sheet → $C/refs
python3 build.py                                             # the pack $C/out/kira.json/.bin
python3 bases.py
$L python3 compare.py /cache/to3d-r26-s7-kira/out/kira.json $C/cmp
$L python3 make_pics.py stills turn
cp $C/out/kira.* ../data/
$L python3 make_live.py
```

The viewer by hand: serve the repository root with `python3 -m http.server` and open
`to3d/r26-s7-kira/tools/web/view.html`; `node check_view.mjs out.png` opens it as a person does and saves a picture.
Files: as Р25's (`tools/` is the same but `config.py` and the viewer's title and pack in `web/view.html`).

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`).
- Kimodo motions: `engine/motions`.
- The drawing and its code: this repository (`styles/s7-ghibli`). three.js: MIT. scikit-image (marching cubes): BSD.

## Honest state, what is weak

- The hoodie is a skinned shell, not cloth: it is oversized in the drawing but does not hang or fold; sitting, its hem
  goes into the thighs. The hood and the headphones go with the chest and do not move by themselves.
- The neck: the head is pushed forward and bowed, so a long piece of neck in plain shade shows between the hair and
  the hood from the side and behind; the jaw's edge close up is less clean than drawn.
- The hoodie's neckline between the cups is a straight edge; the drawing has the hood's two ends meeting there.
- The boots' toes are narrower and more pointed from the front than drawn (the drawing's foot tube seen in 3D).
- The hair is rigid; the fringe does not swing.
- Kimodo's motions are an adult's; her slouch stays, but an awkward teenager's own way of moving is not there.
