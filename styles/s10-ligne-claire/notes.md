# С10 — Чистая линия: франко-бельгийский комикс

## What was done

1. **Samples.** Searched Wikimedia Commons (the Brussels comic-book route murals are photographed there), Lambiek
   Comiclopedia (artist pages with panels) and 2dgalleries (original pages). Looked at ~70 pictures, kept twelve in
   `refs/` (≤ 800 px, jpg): Hergé (Stockel metro mural, Quick & Flupke), Chaland (the "Le jeune Albert" mural,
   Freddy Lombard, Spirou), Floc'h (an Albany & Sturgess original page, Blitz), Jacobs (La Marque jaune), Ted Benoit
   (Histoires vraies, Ray Banana), Swarte (Jazzroute Haarlem portrait). Clerc and Moebius were looked at but not
   kept (Clerc's pages found were small; Moebius is not quite clear line). Brecht Evens was left out on purpose.
2. **Rules** — in `entry.json` (block «Правила стиля»), each one from the samples.
3. **Drawing.** Everything is SVG written by our own Python in `tools/` (no tracing, no image models). The method
   is the style's own logic turned into a program: a character is a simple 3D body; a tiny renderer splits the
   picture into flat colour regions and draws one even line exactly where a form is in front of something else
   (the background, another colour, or the same colour farther back — the nose over the far cheek, the jaw over the
   neck, a sleeve over the body). Then the few marks of the face are drawn on the surface. That gives turnarounds,
   expressions and the group picture from one model per character.
4. **By eye.** Rendered, compared with the samples, redrew. What changed on the way: hair was a helmet (now an
   edge with lock points, a few long lines inside, Аня's tucked behind one ear), necks were thin tubes (now real
   width, head set lower), hands as 3D mittens looked like sausages (replaced by drawn 2D hand shapes pinned to the
   wrist), the lower face was too long (shortened per character), mouths in expressions were too small (bigger),
   Savely's hair was a slab (now a wavy horseshoe), Vera's grey streak looked like a hairband (now light strands).

## Files

- `tools/lc.py` — SVG kit: Catmull-Rom paths through points, shapes, lines, colours, rendering with headless
  Chrome (`google-chrome --headless=new --screenshot`).
- `tools/r3.py` — the renderer: `View` (yaw, pitch, roll, scale), `Part` (dense surface samples with a material),
  `Render` (z-buffer → `fills(colours)`, `lines(width)`, `visible()` for marks, `clip_path()`).
- `tools/head.py` — `Head`: skull and face from horizontal slices (`slices` rows: y, half width, z of the widest
  point, front z, back z, front exponent), nose/lips/chin/brow as bumps, ears, neck; `Shell` (same slices, for hair
  and clothes; `shell.curve([(deg from front, y)])` gives 3D curves on it); `lock_part` (a ribbon of hair: tufts,
  moustache); `Mark` (3D polyline or shape drawn on top, clipped to its material) and `Glyph` (a 2D drawing pinned
  to a 3D point — hands, the pocket watch, the slingshot).
- `tools/features.py` — eyes, brows, mouth, nose tip, glasses; `EXPR` holds the expressions as numbers.
- `tools/hands.py` — the hand shapes (hang, grip, fist, open).
- `tools/body.py` — tubes (limbs, sleeves, trouser legs), blobs, boxes, ring and line marks, buttons.
- `tools/scene.py` — renders one or many characters together (placement: x, y, z, yaw, scale, expr).
- `tools/cast.py` — the four heads: shape, hair, face marks, colours.
- `tools/figures.py` — the four bodies and clothes, poses, head tilt on the neck (`Figure`).
- `tools/build.py` — composes every picture (panels, the street) → `svg/`, `pics/`.
- Round three (below): `tools/marat.py`, `tools/kira.py`, `tools/extra.py`, `tools/build6.py`.

## How to repeat

```
cd styles/s10-ligne-claire
python3 tools/build.py              # all pictures (~4 min, one Chrome at a time)
python3 tools/build.py portrait     # only names containing "portrait"
```

## How to add a new character

1. In `cast.py` write `def name():` returning `(Head(...), colours)`. Start from the nearest of the four:
   - head shape: copy a `slices` table; `squash(rows, K)` shortens (K < 1, younger, cuter) or lengthens the face
     below the eyes; widths at y 40–90 make the jaw and chin; `nose`, `lips`, `chin` rows are (y, height, half
     width) — the nose is the caricature, make it differ;
   - hair: a `Shell` a few units outside the skull, and a `keep(X, Y, Z, a)` that says which part of it is hair —
     `hairline_keep(hairline, side_z)` covers most cuts (hairline: degrees from the front → y; a row of points
     gives lock tips); tufts and moustaches with `lock_part`; lines inside the hair as `Mark(shell.curve(...),
     on='hair')`;
   - face: `face_marks(eye=..., brow=..., mouth=..., nose=...)` with the character's sizes; extras (glasses,
     freckles, wrinkles) as more marks.
2. In `figures.py` write `def name_figure(bust=False, head_rot=(pitch, yaw, roll))`: torso rows as a `Shell`
   (inner garments with `inset(rows, d)`, openings with `open_front` / `vneck`), arms and legs with `B.tube`, shoes
   with `B.blob`, details as marks, hands as `hand(anchor, toward, kind, skin, length)`. Units: the head is ~200
   from crown to chin; an adult is 6–7 heads, a child ~5.
3. Add the name to `NAMES`, `RU`, `PANEL` in `build.py`, run it, and look at the pictures beside `refs/`.

## Honest state

The language is right (even line, flat colour, line only on edges, faces from few signs, careful clothes) and it is
closest to Hergé and Chaland. Savely and Tim came out best. Аня is the weakest: pleasant, but plainer than
Floc'h's and Chaland's women. Poses are stiff, legs are plain tubes, feet are ovals. Hands are 2D drawings, so they
don't turn with the figure. The line is mechanical: it never swells or thins the way a hand-drawn line does, and
small details (hair ends, collar) can get a little jagged. Turnarounds are heads with shoulders.

## Round three: Марат and Кира (the cast is six)

Brief: `docs/briefs/styles-more.md`, part A. No new samples; the style's rules are as they were.

What was done:

- `tools/marat.py`, `tools/kira.py` — a module per character: `head()` and `figure(bust, head_rot)`, plus the
  panel colour (`PANEL`) and, where needed, the character's own settings for the sheets (`PORTRAIT`, `TURN`, `EXPR`).
- `tools/extra.py` — shared parts the two needed; the four don't use them:
  - `Posed` — a `Figure` whose whole body follows a line of action: `spine` rows (y, dx, dz, tilt, twist) shift,
    tilt and turn the body by height (Марат leans back laughing; Кира's head is forward, the hips pushed out);
  - `OnShell` — draws `features.py` marks on a shell instead of the face (Марат's mouth is on his beard);
  - `bumps` — pushes a shell into curls, so the silhouette is scalloped; `curl` — a small "c" stroke;
  - `strip` — a band of cloth along a 3D path (the towel over the shoulder);
  - `grin_marks` (an open laughing mouth: teeth along the top, the tongue below), `smirk_marks` (a shut mouth
    with one corner up).
- `tools/build6.py` — builds the new pictures with `build.py`'s own sheets (same format, size, line, paper):
  `portrait-`, `figure-`, `turn-`, `expr-` for `marat` and `kira`, and `cast-six` (all six in the same street).
- One change in shared code: `build.turnaround` got `side` (which way the character turns; default as before)
  and passes extra keywords to the figure. Кира's turnaround is turned to our right, where the fringe doesn't hide
  her face; Марат's is drawn with the arms down (the ladle stood in front of his profile).
- The four were not touched: after the work their `svg/` and `pics/` files have the same checksums as before, and
  `turn-anya`, `turn-savely` re-rendered with the changed `build.py` came out byte for byte the same.

How it went by eye: Марат's beard first hid the ears and squeezed the face into a hole — the cheek line was lowered,
the sideburns narrowed, the mouth made wide. Кира's fringe first covered half the face as a slab; now it is three
long points, and the eye looks out between two of them. Her headphones first looked like two lime eyes on the chest;
now the cups hang edge-on at the collarbones. The towel as a `lock_part` ribbon tore on the shoulder — `strip` was
written for it.

Honest state of the two: Марат is good (portrait, expressions, the figure with the ladle); his fists are the same
flat signs as everyone's hands. Кира's portrait and turnaround are alive; her full figure is the weakest new picture
(the hoodie is a smooth sack, the slouch reads more as a lean, no sharp elbows and knees under the clothes); on her
expression sheet a lock cuts the near eye in places.

How to repeat:

```
cd styles/s10-ligne-claire
python3 tools/build6.py             # the nine new pictures (~3 min); run one name at a time if memory is short
python3 tools/build6.py kira        # only names containing "kira"
```

Needs `numpy`, `scipy`, `scikit-image` and `google-chrome`. In this session scipy and scikit-image were not
installed: they were put into `/home/user/cache/styles-s10-ligne-claire/pylib` (`pip install --target`) and used
through `PYTHONPATH`.

A new character now: a module like `marat.py` (the nearest example for a big man, a beard, curls, a pose) or
`kira.py` (a girl, a fringe, a hood), registered in `NEW` in `build6.py`. The steps of "How to add a new character"
above hold; `Posed` with a `spine` gives the pose a line of action.

## Sources (third-party pictures, kept only as references)

- `refs/01-herge-stockel-cast-left.jpg`, `refs/02-herge-stockel-cast-right.jpg` — Hergé's mural at Stockel metro
  station, photo on Wikimedia Commons: https://commons.wikimedia.org/wiki/File:Stockel-TinTin-1.jpg (crops)
- `refs/03-herge-quick-flupke.jpg` — Hergé, Quick & Flupke, via Lambiek: https://www.lambiek.net/artists/h/herge.htm
  (`herge_quick1.jpg`)
- `refs/04-chaland-jeune-albert-mural.jpg` — Yves Chaland's mural, Brussels, Wikimedia Commons:
  https://commons.wikimedia.org/wiki/File:Comic_mural_Le_jeune_Albert,_Yves_Chaland,_Brussels.jpg (crop)
- `refs/05-chaland-freddy-lombard.jpg`, `refs/06-chaland-spirou.jpg` — Lambiek:
  https://www.lambiek.net/artists/c/chaland.htm (`chaland_freddylombard3.jpg`, `chaland_spirou2.jpg`)
- `refs/07-floch-albany-sturgess-page.jpg` — Floc'h, original page, 2dgalleries:
  https://www.2dgalleries.com/art/floc-h-albany-sturgess-a-la-recherche-de-sir-malcom-248954
- `refs/08-floch-blitz.jpg` — Lambiek: https://www.lambiek.net/artists/f/floch.htm (`floch_blitz.jpg`)
- `refs/09-jacobs-marque-jaune.jpg` — Lambiek: https://www.lambiek.net/artists/j/jacobs.htm (`jacobs_marquejaune.jpg`)
- `refs/10-benoit-histoires-vraies.jpg`, `refs/11-benoit-ray-banana.jpg` — Lambiek:
  https://www.lambiek.net/artists/b/benoit.htm (`benoit_ted_histvraies.jpg`, `benoit_ted_raybanana.jpg`)
- `refs/12-swarte-meijer-wery.jpg` — Joost Swarte, Jazzroute Haarlem, Wikimedia Commons:
  https://commons.wikimedia.org/wiki/File:Jazzroute-Meijer_Wery_by_Joost_Swarte.jpg (crop)

Downloads and scratch renders: `/home/user/cache/styles-s10-ligne-claire/`.
