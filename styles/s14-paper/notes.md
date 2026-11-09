# С14 «Вырезанная бумага» — notes

Round three of "Стили персонажей" (brief: `docs/briefs/styles-more.md`, part B). A new style: characters of cut and
torn paper laid in layers. All six of the cast are drawn: Аня, Савелий Петрович, Тим, Вера, Марат, Кира.

## What was done

1. **Samples.** This session's network lets through only a few hosts, so the samples are what could be downloaded
   from Wikipedia/Wikimedia and Steam (list below); twelve small copies are in `refs/`. **Not downloaded** (the proxy
   refuses the hosts; nothing was traced from memory or faked): Eiko Ojala (https://ploom.tv), Elsa Mora
   (https://www.elsamora.net), the paper and origami sequences of Kubo and the Two Strings
   (https://www.laika.com/our-films/kubo-and-the-two-strings), more of Tearaway (https://tearaway.mediamolecule.com,
   https://tearaway.fandom.com), Eric Carle's originals (https://www.carlemuseum.org), Norstein's stills beyond the
   two on Wikipedia. The Tearaway cover and the Carle, Keats, Matisse and «Сказка сказок» pictures are small
   (under 400 px) — only those sizes are on Wikipedia.
2. **Rules** — written from those samples (in `entry.json`, block «Правила стиля»).
3. **Drawing code** (`tools/`, Python → SVG, no dependencies): every visible thing is a *piece of paper* — a closed
   outline, a colour, a height, a kind of paper. No strokes at all.
4. **Sheets**: portrait and figure for all six; turnarounds for Аня, Тим, Марат, Кира; expression sheets for all six;
   the four together (`cast`, the cover), all six together (`cast6`); four rule diagrams.
5. Looked at every render and redrew: the first street behind the cast (houses, sun, lawn) looked like С9's cover —
   replaced by a paper theatre (torn hills in layers with tissue haze, clouds and sun on threads); Кира was redrawn
   twice (dark lids read as a bruise → lashes as eyeliner; a vertical figure → one S-curve slouch; the fringe now
   falls over one eye); lower lids looked like bags under the eyes → lighter and only where the cheek pushes up.

## How it is built

- `tools/kit.py` — the paper. `card / paint / torn / flat / tissue / shade / light` make pieces; `ell, strip, arc,
  crescent` make outlines; `move, scale, rot, mirror` move trees of pieces (nested lists; later = on top);
  `Doc` writes the SVG. The SVG filters live here: for each height 1–3 a cast shadow (offset blur) + a crisp contact
  shadow + a light rim on the lit edge; `paint` adds brush streaks (stretched fractal noise, four directions);
  `torn` displaces the edge and shows a white core; one grain filter over the whole sheet (paper fibre).
  Each piece carries an invisible padded box so its filter region is exact. Mirror with `mirror()` (numbers), never
  with an SVG transform — the shadows must keep falling down-right.
- `tools/face.py` — the head from a `spec` (dict of numbers and colours; `DEFAULT` lists them): `outline` (face
  piece for front / three-quarter / profile), `eye` (white, iris, pupil, speck, the lid piece, lashes, lower lid),
  `brow`, `nose`, `mouth` (sliver, or an open piece with teeth and tongue), `ear`, `neck`; `face()` returns the layers,
  `stack()` glues them with the character's hair between; `turn()` turns front-view hair pieces into three-quarter.
  `EXPR` holds the expressions; a character's `rest` is its own calm, `on` its own corrections (Кира's joy is a smirk).
- `tools/body.py` — `limb` (strips pinned with brads), `hand` (cut with finger snips), `fist`, `shoe`, `boot`,
  `folds`, `curl`, `ground_shadow`.
- `tools/scenery.py` — torn mat, the paper theatre (`street`), bunting.
- `tools/anya.py … kira.py` — one module per character: `SPEC`, hair, `head(yaw, expr, collar)`, `shoulders(yaw)`,
  `bust(yaw, expr)`, `figure(expr, yaw)` (feet at y = 0).
- `tools/build.py` — the sheets; `tools/render.js` — SVG → PNG (Playwright, one browser); `tools/webp.py` — PNG → WebP.

## Repeat

```
cd styles/s14-paper/tools
python3 build.py            # all sheets → ../svg   (or: python3 build.py cast figure-kira)
node render.js              # → ../pics/*.png       (or names)
python3 webp.py             # → ../pics/*.webp, removes the png
```

## How to add a character

1. Copy the module nearest in type (`kira.py` for a thin teenager, `marat.py` for a big bearded man, `anya.py` for
   long hair) to `tools/<name>.py`.
2. `SPEC`: skin, face size (`rx, ry, jaw, chin`), eyes (`eye_y, eye_gap, eye_w, eye_h, iris, lid, lash`), brows, nose
   kind (`button / wedge / long / broad`), mouth, cheeks; `rest` — the resting expression; `on` — corrections per
   expression.
3. Hair: two or three big pieces in head space (face centre (0, 0), about ±80 × ±100): behind the head, over the
   forehead; `paint` for hair, `torn` for grey or fluffy, `B.curl` for curls and lock ends. Write the front view and
   get the three-quarter with `F.turn()`, or write each view by hand; the profile is always by hand.
4. `shoulders(yaw)` and what lies over the neck (`collar`); `figure()`: legs, far arm, body, head, near arm — in that
   order, with a pose that has one line through it. Two or three papers of the character's own colours.
5. Add the module to `WHO`, `BG`, `NAMES`, `HEIGHT` in `build.py`, build, render, look, redraw.

## Sources

- Tearaway (Media Molecule, 2013), cover — https://en.wikipedia.org/wiki/Tearaway_(video_game)
- Tengami (Nyamyam, 2014), screenshots — https://store.steampowered.com/app/299680/Tengami/
- Lumino City (State of Play, 2014), screenshot — https://store.steampowered.com/app/205020/Lumino_City/
- Yuri Norstein, «Ёжик в тумане» (USSR stamp, 1988) — https://commons.wikimedia.org/wiki/File:The_Soviet_Union_1988_CPA_5919_stamp_(Hedgehog_in_the_Fog).jpg
- Yuri Norstein, «Сказка сказок», still — https://en.wikipedia.org/wiki/Tale_of_Tales_(1979_film)
- Eric Carle, The Very Hungry Caterpillar, cover — https://en.wikipedia.org/wiki/The_Very_Hungry_Caterpillar
- Ezra Jack Keats, The Snowy Day, cover — https://en.wikipedia.org/wiki/The_Snowy_Day
- Henri Matisse, Blue Nude II; The Sorrows of the King — https://en.wikipedia.org/wiki/Blue_Nudes , https://en.wikipedia.org/wiki/The_Sorrows_of_the_King
- Lotte Reiniger, Die Abenteuer des Prinzen Achmed, title card — https://en.wikipedia.org/wiki/The_Adventures_of_Prince_Achmed
- Mary Delany, paper mosaic — https://en.wikipedia.org/wiki/Mary_Delany

Downloads and scratch renders: `/home/user/cache/styles-s14-paper/`.
