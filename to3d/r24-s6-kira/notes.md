# Р24 — Кира, символический (С6 → 3D)

What was done, why, how to repeat. Brief: `docs/briefs/to3d.md`, its part "Third round". Done by one agent in one
session right after Р23 (Вера, `to3d/r23-s6-vera`); the orchestrator commits.

## The idea

The way of Р8 (Савелий Петрович, `to3d/r8-s6-savely`): in С6 the figure is one dark form with a rim of light and one
sign, and the drawing is itself built in 3D by the style's code (`styles/s6-symbolic/tools/sil.py`, `cast_more.kira`)
— so the 3D is **the drawing's own solids** on SOMA's skeleton, moved by Kimodo through the engine. Why not Anny's body
and an artist's head: nothing inside the silhouette exists in this style. The brief asks to find a body for a thin
slouching girl: here it is the drawing's own body (`KIRA_B`: thin long legs, narrow shoulders), and the slouch is the
drawing's pose numbers laid on every motion.

The shared code is the same as in Р23 (its `notes.md` has the table of files and what is new against Р8): `build.py`,
`make.py`, `drawing.py`, `shots.mjs`, `web/figure.js`, `web/app.js` are identical in both folders; what is Кира's own
is `tools/character.py` and `tools/web/character.js` (and `view.html`'s colours).

## What Кира needed beyond Вера

- **Her expression sheet is in the style** (`scenes_more.EXPR_KIRA`: joy, surprise, sadness, anger — whole-body poses:
  a sway with the headphones on, a step back, a squat with the head on the knees, a kick). The same pose numbers are
  her moods here; `make.py expr` puts the style's sheet and the 3D in the same layout and overlays the silhouettes.
- **Signs that are solids in their own colour**: the lime headphones are the drawing's accent tubes turned into hulls
  like the rest, kept as their own part and drawn in their colour (`SIGN_SETS`). Two sets: round the neck (on Chest)
  and on the head (on Head, hidden); a mood says which is seen (`show` / `hide`), so in joy and in the dance the
  headphones are on the head.
- **The hands' pocket**: the drawing joins the two hands in the hoodie's pocket with one more solid. It exists only
  where the drawn pose puts the hands, so it is taken from the drawn pose and carried back to rest, each half rigid on
  its hand; moods that take the hands out hide it.
- **The boots' shafts** (`shin:L`), the hood on the back and the hair's sharp ends and fringe (`on:Chest`, `on:Head`).
- **Her light** is the far town with its lit windows and a violet glow over the roofs (her sheet: «the light she has
  turned her back on»): the rim comes from its side, her shadow falls toward us.

## Steps

```
cd to3d/r24-s6-kira/tools
python3 build.py                                  # 23 449 vertices, 46 342 triangles
python3 make.py compare steps moods expr          # prints how much the silhouettes differ from the drawing's
python3 make.py films                             # turn, walk, life, sneak, dance
python3 make.py strip:<motion>:<mood>             # eight moments of a motion into the cache, to look before filming
python3 poses_preview.py out.png                  # the moods by the style's 2D code, without a browser
```
three.js 0.160 for the headless run: `npm i three@0.160.0` in `/home/user/cache/to3d-r24-s6-kira`. Every browser run
goes through one of the shared locks (`make.py: heavy`).

## Motions

From `engine/motions`, copied into `tools/web/data/motions`: walk (the mood «руки в карманах»: her slouch and both
hands in the pocket — Kimodo moves only the legs and the trunk's sway), sneak (her slouch, the arms Kimodo's), dance
(the headphones on, the back straighter). Tried and left out: sit — Kimodo's clip is already on the ground from its
first frame, and a dark lump on dark ground says nothing (her own squat of the sheet says it better). Not taken: stomp and idle — on Вера they stooped low and read as a bow; they were not tried on Кира.

## Bases and licences

| What | Where | Licence |
|---|---|---|
| The drawing and its code (sil.py, cast.py, cast_more.py, draw.py) | `styles/s6-symbolic` | ours |
| The way and the first code | `to3d/r8-s6-savely` | ours |
| SOMA skeleton | `engine/data/skeleton.json` (NVIDIA, Apache-2.0, see `engine/data/soma/NOTICE`) | Apache-2.0 |
| Kimodo motions | `engine/motions` (moood studio) | as the engine's motions |
| three.js 0.160 | jsDelivr | MIT |

No neural images, no third-party meshes.

## What is weak

- Headphones round the neck are honest solids behind the hood and the neck; the drawing lays them flat over the
  figure, so in three-quarter views the 3D shows less of the lime than the drawing.
- Against the town's dark blocks her dark body is held only by the thin rim: where a block is behind her the
  silhouette is weaker than against the sky.
- In the sneak her slouch adds to Kimodo's crouch: she is bent very low.
- Parts that moods show and hide (the headphones on the head, the hands' pocket) appear at once, not gradually.
- The joy pose sits 3–4 px off the drawing's (the drawing stands it on the sole, the 3D on its lowest point).
- The hand is one drop in a sleeve; no close-up portrait (the head of rings is a silhouette, not a face).
