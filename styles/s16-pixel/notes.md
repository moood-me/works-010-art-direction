# С16. Пиксель-арт — notes

Round three of "Стили персонажей" (brief: `docs/briefs/styles-more.md`, part B): a new style and all six characters.

## What was done

- **Samples** (`refs/`, 12 pictures): crops of official screenshots, kept at the screenshot's own size so the pixels
  show. Third-party, kept only as references.
- **Rules** — in `entry.json` («Правила стиля»), with four small pictures (`pics/rule-*.png`).
- **The cast**, drawn by code in `tools/`: for each of the six a portrait (56×56 in a dialogue box) and a sprite of
  the figure; turnarounds (front, three-quarter, side) for Тим, Савелий Петрович and Кира; expression sheets for Аня,
  Тим, Савелий Петрович and Марат; the four together (`cast`, the cover) and all six (`six`) in a street at dusk.
- Expression sheets for Вера and Кира were drawn and not kept: Кира's one visible eye did not carry joy and sadness,
  Вера's were plain. Their `portrait(expr)` functions still take the four expressions.

## What could not be downloaded

`www.spriters-resource.com` and `www.mobygames.com` answered 403 to this session (sprite sheets and the pixel
portraits of Fire Emblem GBA, Final Fantasy VI, Chrono Trigger were to come from there); The Last Night's Steam
screenshots did not come either. So the samples are in-game screenshots only, and **no pixel portrait of a game is
among them**: the rules of the small sprite are written from what is in `refs/`; the portrait is the same rules
carried to a larger grid, not rules read off samples. Nothing was traced or redrawn from memory.

## Sources

Steam store pages (screenshots from `shared.akamai.steamstatic.com`):
- Eastward — https://store.steampowered.com/app/977880/Eastward/ (`eastward-market`, `eastward-city`)
- Owlboy — https://store.steampowered.com/app/115800/Owlboy/ (`owlboy-snow`, `owlboy-pirates`)
- Celeste — https://store.steampowered.com/app/504230/Celeste/ (`celeste-hotel`, `celeste-cabin`)
- Hyper Light Drifter — https://store.steampowered.com/app/257850/Hyper_Light_Drifter/ (`hyper-light-drifter-fire`)
- Octopath Traveler — https://store.steampowered.com/app/921570/OCTOPATH_TRAVELER/ (`octopath-battle`)
- Chrono Trigger — https://store.steampowered.com/app/613830/CHRONO_TRIGGER/ (`chrono-trigger-fair`)
- Final Fantasy VI — https://store.steampowered.com/app/1173820/FINAL_FANTASY_VI/ (`ff6-airship`)

Wikipedia (enlarged ×3 and ×2, nearest neighbour):
- Fire Emblem: The Blazing Blade — https://en.wikipedia.org/wiki/Fire_Emblem:_The_Blazing_Blade
  (`fire-emblem-gba`, file `FE_Rekka_English_gameplay.png`)
- Superbrothers: Sword & Sworcery EP — https://en.wikipedia.org/wiki/Superbrothers:_Sword_%26_Sworcery_EP
  (`sword-sworcery`, file `Sword_and_Sworcery_-_Gameplay.png`)

## How to repeat

```
python3 tools/build.py            # all pictures: svg/<name>.svg and pics/<name>.png
python3 tools/build.py six cast   # only some
```
Needs Python 3 and Node with Playwright (one Chromium for all pictures). Pictures are small PNGs (the folder is ~2.5 MB).

## The code (`tools/`)

- `pal.py` — the palette: ramps of five steps, a key is a ramp letter and a step (`s3`, `a1`). Step 0 is the ramp's
  outline colour.
- `px.py` — the pixel canvas: `px`, `rect`, `hline`/`vline`/`line`, `spans` (a silhouette typed row by row), `sym`
  (rows of half-widths), `stamp` (an ASCII map), the passes `rim` (a band of shade along chosen edges) and `outline`
  (the coloured selective outline), `svg(scale)` (crisp rects, `shape-rendering="crispEdges"`).
- `sprite.py` — a sprite from an ASCII map (or from a function that draws a canvas), with the outline.
- `portrait.py` — shared parts of portraits: `skin`, `cast` (hair's shadow on skin), `jaw`, `eyes`, `both`, `blob`,
  `framed` (the dialogue box).
- `chars/<name>.py` — one module a character: `LEG` (the legend of its ASCII maps), `VIEWS` (`front`, and `q`, `side`
  where drawn), `portrait(expr)` with `rest`, `joy`, `surprise`, `sadness`, `anger`.
- `sheets.py` — the pictures (`PICS`): portrait, figure, turnaround, expressions, the street, the rule pictures.
- `build.py`, `render.js` — SVG, then PNG.

## How to add a character

1. `tools/chars/<name>.py`. Choose its ramps in `pal.py` (add a ramp only if none fits: five steps, shadows cooler,
   lights warmer).
2. The sprite: type `FRONT` as rows of characters, one a pixel, `.` empty; `LEG` maps your letters to colour keys
   (`s t u h` skin, `k` ink, `i` white, `p` blush come from `sprite.BASE`; override `s t u h` for another skin, as
   Марат does). Don't draw the outline — `sprite.make` adds it. Head 13–17 wide; height by the cast's order (Тим 32
   … Марат 50). Give the figure a pose and one thing of its own; check the silhouette. A big figure may be a function
   that draws with `spans` (see `marat.front`). `VIEWS = {'front': FRONT}`; add `q` and `side` for a turnaround.
3. The portrait: `portrait(expr='rest')` returns a 56×56 canvas built in layers (back hair, body, head, features,
   front hair) and stacked with `P.stack`; type the head as half-widths (`sym`), shade it with `P.skin`, stamp the
   eyes with `P.eyes`, put brows and mouth per expression, then `P.cast` and `P.jaw`. Start from the module of the
   nearest character.
4. Add the name to `SIX` (or the lists of turnarounds and expressions) in `sheets.py`, build, and look at the picture
   beside the others: at the sprite's true size too, not only enlarged.

## What is weak

- Вера's portrait (younger and plainer than she should be); Кира's hoodie rounds her in the front sprite.
- Hands are blobs of 2–4 pixels, as in the samples; no fingers.
- Portrait shading is partly a rule (`rim`: a band along an edge), which in places reads as an even border rather
  than a placed cluster.
- The palette is wider than strict pixel art keeps: 16 ramps × 5; 22–35 colours a character, 79 in the cast.
