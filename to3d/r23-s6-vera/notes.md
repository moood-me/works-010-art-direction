# Р23 — Вера, символический (С6 → 3D)

What was done, why, how to repeat. Brief: `docs/briefs/to3d.md`, its part "Third round". Done by one agent in one
session together with Р24 (Кира, `to3d/r24-s6-kira`); the orchestrator commits.

## The idea — Р8's, carried on

In С6 the person is almost a sign: one dark form with nothing inside, a thin rim of light on one side, one sign, fog in
layers, grain; no face — what she feels is her posture. The С6 drawing is itself 3D (`styles/s6-symbolic/tools/sil.py`:
lofts of rings and tubes of spheres on a small skeleton, projected and merged into one shape). Р8 (Савелий Петрович,
`to3d/r8-s6-savely`) showed the way: take the drawing's own solids, built by the drawing's own code, put them on a
skeleton that is SOMA's — and the silhouette is the drawing's from every side, and Kimodo moves it. Anny's body and an
artist's head (the brief's points 1–2) are not used for the same reason as there: nothing inside the silhouette exists
in this style.

Р8's code was written for one character (which tube is a leg was written by its number). Here it is made to take any
character of the style: the shared part is the same in Р23 and Р24, and what is the character's own sits in two small
files.

| File | What |
|---|---|
| `tools/build.py` | the style's function for the character → hulls on SOMA, weights by each solid's role, SOMA joints and frames, poses from the drawing's pose numbers (the whole body) |
| `tools/character.py` | **her own**: which function draws her, which solid is what, her moods, the drawing's sheets to compare with, the settings of pictures and films |
| `tools/web/figure.js` | the figure in the page: life (moods, breath, glances, speech), the poser, the look (ink, rim from the mask, signs), the world |
| `tools/web/character.js` | **her own**: palette, world's light, motions, phrases, how she breathes and looks about |
| `tools/web/app.js`, `view.html` | the page and the viewer; `window.A` for pictures and films (`?shots`), `?slow` |
| `tools/make.py`, `shots.mjs`, `drawing.py`, `svg2png.mjs` | pictures and films through the page; the drawing's silhouettes for the overlays |
| `tools/poses_preview.py` | a quick look at moods by the style's 2D code, without a browser |

## What is new against Р8

- **Any character**: `character.py` names the solids' roles in the order the style's function makes them
  (`leg:L`, `foot:L`, `neck`, `arm:L`, `hand:L`, `on:Head:hair`, lofts `torso` with its ring heights, `skirt`, `head`,
  `on:Chest:folder`); `build.py` checks the count and weights each by its role.
- **Moods are the whole body.** Standing, a mood is every joint's turn and the pelvis's place (legs too — a step back,
  the weight on one leg), mixed by springs; in Р8 only the trunk and arms were. On a motion a mood is still the trunk
  and the arms it holds, each arm on its own: Вера's right arm keeps the folder at the chest while the left is the
  motion's (`arms=(0, 1)`).
- **She looks about**: now and then the head turns aside for a second or two and comes back (a seeded schedule; the
  turn goes quickly, the return more slowly). Without a face the profile of the nose turning is the look.
- **Signs in the mask.** The figure's mask now has a channel for signs lying over the form (the lenses; Кира's
  headphones), so the rim is not drawn over them or along their edge.
- **The light is the character's**: a street lamp (Р8), a lit window standing alone in the dusk (Вера: her sheet has
  it), a far town (Кира). The rim comes from where the light is on the screen, the shadow from it on the ground.
- **The lenses** keep the drawing's rule: seen at an angle, a small ellipse; facing us they would read as eyes, so they
  thin to the bright edge of the frame.
- The sheets' own colours for the comparison (`pal`), the ink without air in the drawing's views, less grain there.
- Heavy runs (a browser drawing frames) go through the shared locks (`make.py: heavy`): a free one if there is one.

## Steps

1. `python3 build.py` — `cast.vera()` run unchanged on a skeleton standing straight with arms along SOMA's rest arms;
   each pair of neighbouring rings / spheres → a 3D convex hull (13 354 vertices, 26 308 triangles); weights: limbs
   rigid on their bones, the coat's torso along the spine and 55 % on the collarbones over the shoulders, the coat's
   column from the pelvis to the hem up to 62 % with the thighs (split left/right by a soft step: in a stride it opens
   into a tent), collar and neck Neck1 → Neck2 → Head, head / hair / bun on Head, the chin's front on Jaw, the folder
   rigid on Chest. SOMA's 77 joints on the drawing's skeleton, frames turned from SOMA's. Poses: the drawn stand, the
   straight rest, the moods. Writes `web/data/figure.{json,bin}`, `web/data/poses.json`.
2. `python3 make.py compare steps moods` — the drawing's views side by side and overlaid (prints how much the
   silhouettes differ), the steps, the mood sheet. `python3 make.py films` — turn, walk, life, bow, run.
   `python3 make.py strip:<motion>:<mood>` — eight moments of a motion in a row into the cache, to look before filming.

three.js 0.160 for the headless run: `npm i three@0.160.0` in `/home/user/cache/to3d-r23-s6-vera` (the page itself
takes it from jsDelivr).

## Moods

С6 has no expression sheet for Вера. The first mood is the drawn stand; the other six are written by the style's rule
«выражения — позой всего тела» with the drawing's pose numbers over the drawn stand (looked at first with
`poses_preview.py`, then in 3D; the hand to the forehead and the hand at the chin took three tries). Her right arm
always holds the folder: only the free arm, the back, the head and the legs speak.

## Motions

From `engine/motions`, copied into `tools/web/data/motions`: walk, run, bow. On each lies the mood «идёт с папкой»
(her carriage and the folder arm). Tried and left out: `idle` (Kimodo's stoops low — not her), `stomp` (reads as a
bow), `wave` (Kimodo waves with the right hand — hers holds the folder).

## Bases and licences

| What | Where | Licence |
|---|---|---|
| The drawing and its code (sil.py, cast.py, draw.py) | `styles/s6-symbolic` | ours |
| The way and the first code | `to3d/r8-s6-savely` | ours |
| SOMA skeleton | `engine/data/skeleton.json` (NVIDIA, Apache-2.0, see `engine/data/soma/NOTICE`) | Apache-2.0 |
| Kimodo motions | `engine/motions` (moood studio) | as the engine's motions |
| three.js 0.160 | jsDelivr | MIT |

No neural images, no third-party meshes.

## What is weak

- The rim is thin and nearly goes out from the front when the window is not behind her.
- Moods other than the drawn one are mine; «думает» and «довольна» differ little from the stand.
- The lenses at three-quarters are two bright dots and from afar read as eyes (so they do in the drawing).
- Kimodo's bow is to the waist — too deep for her; in the run the coat blows out like a wide skirt (it is skinned to
  the thighs, not cloth). The folder is fixed to the chest; the hand is one drop.
- No close-up portrait: the head of rings is right as a silhouette at figure size, not as a face (the style's own
  portraits are drawn by hand).
- The window always faces us (a flat light); in a turn around it leaves the frame.
