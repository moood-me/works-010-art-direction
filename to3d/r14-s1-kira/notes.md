# Р14 — Кира, Pixar (С1): from the drawing to 3D

What was done, why, and how to repeat it. Brief: `docs/briefs/to3d.md`, its part "Third round". The drawing:
`styles/s1-pixar` (kira-portrait, kira-figure, kira-turnaround, kira-expressions; its code `tools/kira.py` — `kira`,
`kira_hair`, `kira_person`, `SLOUCH` —, `pix.py`, `face.py`, `person.py`). Made right after Р13 Вера, from its
`tools/` (which came from Р6 Тим's): read `to3d/r13-s1-vera/notes.md` first — the head fit, the mouth split by rings,
the tongue, the drawing's own stance for the stills, the camera counted from the body or the head, the cloth layer
are the same here. Done by one agent; the orchestrator commits.

## What is hers

- **`char.py`**: the drawing's person (`kira.kira_person`), body `moood-girl`, the eye's ball 10.8, the stills, the
  films.
- **Body** (`fitbody.py`): Anny's girl made thin and angular: trunk ×1.31 long, ×0.58 wide; arms ×1.08 / ×1.15 long
  and half as thick; legs under half as thick, 3.4 cm off the middle. K = 2.8 mm per unit: 1.66 m to the crown.
- **The slouch** (`build.py slouch_dz`): the drawing's line of action `kira.SLOUCH` (the figure shifted forward and
  back by a spline over the height: head +20 units, chest −6, hips +3, knees +6) is put into the rest model itself —
  every vertex and joint moved along z by the spline at its height, the head as one piece — after everything was
  built upright. The frames (the retargeting reference) stay, so every Kimodo motion is carried by a body that
  slouches. This is the body "found" for her: no engine body slouches, and a pose would be lost in motion.
- **Hair** (`hair.py`, Р6's): the drawing's own locks made 3D — the choppy strips round the sides and back (points on
  the shell, then on a cylinder round the head for the hanging part), the fringe from the side parting with the
  long lock over her left eye — over a cap (the scalp above `hl_kira` lifted 2.2 units).
- **Hoodie**: the body's surface cut at the hem (y 302), the neckline and the wrists, moved out to the drawing's
  sections (the last layer of `kira_person`: up to 46 units wide — much wider than she is), the sleeves to the drawn
  radius; hem and cuffs turned in. The ribbed hem is a band in the shader; the pocket, the cords and the folds are
  the drawing's `hoodie_deco`, painted into the cloth layer. The hood on her back: a closed body lofted on the
  drawing's «rib» layer (from y 68, under the jaw). All skinned by the body's own weights (the hood rides the chest).
- **Headphones** (`kira.py` phones_back, cup): the band behind the neck, two cups on the chest with lime discs —
  the drawing's places and sizes, riding the chest.
- Narrow trousers (the legs' surface a little out); **boots**: a heavy shoe lofted along the foot on a thick sole,
  a shaft up the shin (the drawing's «sock»), three lime chevrons of lacing on the shaft's front (the drawing has
  them a little lower, where here the shoe's body is).
- **Faces** (`web/face.js`): after the style's sheet of her — calm (from under the brows), look (the portrait:
  sideways, a brow down), smirk (her joy), surprise, sad, anger. She never smiles openly.
- The stills' stance also takes the head's own turn (`stance.head`: down and to the shoulder, as the style's portrait
  and figure hold it) and straightens the wrist (Anny's rest wrist is bent; with hanging arms the hands turned in).

## How to repeat

Heavy commands go through a shared lock: `L="flock /home/user/cache/heavy.$((RANDOM % 3)).lock"`.
```
cd to3d/r14-s1-kira/tools
# hbm.npz: as Р13 (hbm_export.py in Blender), or copied from its cache; three.js: npm install three@0.160.0 in the cache
python3 head.py                 # → cache/head_fit.npz
python3 paint.py                # → web/data/paint.json
python3 build.py                # → web/data/kira.json/.bin
$L python3 compare.py turn figure expr portrait
$L python3 films.py turn walk sneak idle face
python3 steps.py
$L node viewer_check.mjs /tmp/v.png
```
The viewer runs from the repository's root: `/to3d/r14-s1-kira/tools/web/view.html`.

## Licences of the bases

| What | Licence |
|---|---|
| Human Base Meshes bundle v1.4.1: `GEO-head_stylized` (+ its eyes) | CC0 (Blender Foundation) |
| Anny girl body (`moood-girl`, in the engine), SOMA skeleton and weights | Anny (NAVER, Apache-2.0), MakeHuman (CC0), SOMA (NVIDIA, Apache-2.0) — `engine/data/soma/NOTICE` |
| Kimodo motions (walk, sneak, idle …) | `engine/motions` (moood studio) |
| The drawing and its code; Р6's and Р13's code | ours |
| three.js 0.160 | MIT |

No neural images.

## What is weak / not done

- The face is harder and older than drawn: the base's brow ridge and nose show, the drawing's face is soft and almost
  without relief; the brows are heavier. The cast shadow on skin was made light (`web/look.js`): the fringe's dark
  shadow cut the face in two.
- Hands are Anny's, large on the thin arms; the hand in the pocket (the figure sheet) and the sheet's sideways line
  of action are not made.
- The drawn arms hang inside the drawn hoodie; here the sleeves partly enter its side (the same colour, it does not
  show much). The hoodie is a shell: no folds of cloth, the hem open underneath. The hood and the headphones ride
  the chest rigidly. Hair is rigid.
- The laces stand a little higher than drawn.
- Kimodo's `idle` stoops on top of her own slouch; it suits her, but the head hangs low.
