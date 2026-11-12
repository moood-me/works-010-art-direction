# С18 — Чёрно-белая манга: штрих и тон

## What was done

1. **Samples.** This session's network let through review sites but not image search (Bing was refused, Wikipedia's
   API was rate-limited). Ten pages and spreads were found in reviews and articles: Taniguchi (The Walking Man, The
   Solitary Gourmet), Urasawa (20th Century Boys, Monster), Asano (A Girl on the Shore). Kept in `refs/` (≤ 800 px,
   jpg). Not reached: pages of Pluto, A Distant Neighborhood, Solanin, Goodnight Punpun — the rules for those are not
   written from pictures looked at here.
2. **Rules** — in `entry.json` («Правила стиля»), from the samples.
3. **Drawing.** SVG written by Python in `tools/` (no tracing, no image models).
   - The head is 3D: horizontal cross-sections (`head.ADULT`, changed per character by zones in
     `features.sections`), features as 3D curves on the surface, the silhouette found per level — so front,
     three-quarter and profile come from the same numbers. The pen draws: tapered strokes with pressure, the contour
     heavier away from the light, face shadow as flat tone where the surface turns from the light.
   - Hair: locks as tapered ribbons on a shell round the head (`hair.Hair`), split into the layer behind the head and
     the layer in front by which way the shell faces; black with white streaks, or tone with pen lines.
   - Bodies are 3D too (`body3d`): a posed skeleton, the torso as superellipse sections along a bent spine, limbs as
     tapered capsules, clothes as shells grown over them. Each group (the torso's garment with the arms at its sides,
     a leg, a sleeve) is one shape: a black copy moved to the lower right under a white one gives the outline heavier
     on the shadow side; the cast shadow is the shape in a darker tone, uncovered where the lit copy moved away.
   - Hands: a small 3D hand (palm plate, three-joint fingers, thumb) posed by curls and a twist, depth-sorted.
4. **By eye.** First bodies were drawn in 2D and looked like pasted pieces; rebuilt in 3D. Long horse jaws on the
   young faces (a `ramus` to shorten the jaw), a square chin (more chin sections), the hairline cut like a wig (the
   scalp covered by shell quads, a fringe of locks), the beard first as hair locks (spikes), then as a region of the
   face plus the grown lower outline. Tone fills vanished once — `<use>` of a group inside `<clipPath>` is not allowed;
   clip with the paths themselves. Backgrounds were made lighter (they fought the hair).

## What is weak

Faces are harder and simpler than in the samples; the young women's jaws still long; Аня's light hair reads as a
cap; bodies wooden, clothes without living folds; small doll-like hands; the slouch of Кира and the laugh of Марат
are milder than described. Dot tone by code is cheaper than real hand-cut screentone (no gradients on faces, no pen
hatching on clothes beyond knit).

## Files

- `tools/pen.py` — the kit: `stroke` (pen with pressure), `outline` (weight by the light), `tone`/`gtone`
  (screentone flat / graded), `hatch`, `blush`, `clip`, `svg`.
- `tools/head.py` — the 3D head, `View`, eye/brow/nose/mouth/ear, neck, `draw_head`, `EXPR`.
- `tools/hair.py` — `Hair` (locks on a shell; modes `black`, `tone`, `light`; a bun; extra locks).
- `tools/features.py` — face shapes by zones (`sections`), glasses, wrinkles, freckles, blush, plaster, beard,
  moustache.
- `tools/body.py` — the 3D hand (`hand`) and older 2D helpers; `tools/body3d.py` — skeleton, torso, limbs, `group`,
  shoes, `head3d`; `tools/figure.py` — a figure from a description (`figure`, `neutralize` for sheets).
- `tools/chars/<name>.py` — one module per character: `HEAD`, `HAIR`, `EXTRAS`, `HEIGHT`, `skeleton()`, `FIGURE()`.
- `tools/build.py` — every picture → `svg/*.svgz` (gzipped: the drawings are big text) and `pics/` (grey PNG, JPG
  for the two group pictures); `tools/render.js` (Playwright, one Chromium).

## How to repeat

```
cd styles/s18-manga/tools
python3 build.py            # everything (~40 s)
python3 build.py portrait   # only names containing "portrait"
```
Plain `.svg` copies for rendering go to `/home/user/cache/styles-s18-manga/svg` (env `TMPDIR_S18` to change).

## How to add a character

1. Copy the nearest module in `tools/chars/` (a man: `sav.py`/`marat.py`, a woman: `anya.py`/`vera.py`, a teenager:
   `kira.py`, a child: `tim.py`).
2. The head: `sections(...)` sets the shape by zones (cranium, cheek, jaw, chin, face length, hollow cheeks,
   `ramus` for a short young jaw). `nose.profile` is (y, projection, half-width) down the nose; `eye`, `brow`
   (`style='bushy'` for white old brows), `mouth`, `rest` (the resting expression as numbers of `EXPR`). Hair:
   `Hair(mode=..., hl=hairline by azimuth, end=length by azimuth, part, spike, wave, locks=[extra locks])`.
   `EXTRAS` draw over the face (glasses, wrinkles); `HEAD['under']` under the features (a beard).
   `EXPR_FIX` changes an expression for this character.
3. The body: `skeleton()` starts from `stand(HEIGHT, sw, hw)` and moves joints for the pose; `Body(joints,
   scale_sections(MALE|FEMALE, width, depth, belly, chest), spine, twist)`. `FIGURE()` describes arms (radii, sleeve,
   hands with pose/twist and held items), legs (trousers or bare, shoes), skirts, torso layers (with `extra`
   functions for plackets, buttons, collars), and items drawn at stages (`back`, `legs`, `mid`, `neck`, `torso`,
   `front`).
4. `chars/__init__.py`: add to `CAST`, `NAMES`, the order lists; `build.py`: `HEAD` (relative head size) and `YAW`.

## Sources

- https://madinkbeard.com/archives/walking-man-review — taniguchi-walking-man-p17
- https://theslingsandarrows.com/the-walking-man/ — taniguchi-walking-man-p8
- https://craigmod.com/ridgeline/158/ — taniguchi-walking-man-spread (crop of a photo of the book)
- https://sabukaru.online/articles/the-solitary-gourmet-the-ultimate-ode-to-food — taniguchi-gourmet-train,
  taniguchi-gourmet-shop
- https://animeuknews.net/2025/09/the-solitary-gourmet-manga-review — taniguchi-gourmet-ramen
- https://ifanboy.com/articles/march-manganess-20th-century-boys/ — urasawa-20th-century-boys
- https://www.galaxus.ch/en/page/monster-is-a-slowly-unfolding-masterpiece-29877 — urasawa-monster
- https://goodokbad.com/reviews/girl_on_the_shore_review.php — asano-girl-on-the-shore-tears, -stairs
