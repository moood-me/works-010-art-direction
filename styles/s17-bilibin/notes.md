# С17 — Билибин и модерн: сказочный орнамент

## What was done

1. **Samples.** Wikimedia Commons answered with "too many requests" (429) to every image download in this session
   (the search API worked), so the pictures were taken from WikiArt (`www.wikiart.org` lists an artist's works as
   JSON at `/en/App/Painting/PaintingsByArtist?artistUrl=<artist>&json=2`, images on `uploads*.wikiart.org`).
   About forty were downloaded into `/home/user/cache/styles-s17-bilibin/dl2/`, looked at, and twelve kept in
   `refs/` (≤ 800 px). Edmund Dulac was looked at (three plates) but not kept: his painterly watercolour does not share
   the ornamental line.
2. **Rules** — in `entry.json`, block «Правила стиля»; each is something seen in the samples.
3. **Drawing.** Every picture is SVG written by the Python scripts in `tools/` (points placed by hand, nothing
   traced, no image models), rendered to JPEG with headless Chromium through Playwright (`tools/render.js`).
4. **Clothes.** The cast stay today's people. The style's logic of patterned clothes is carried by ornament on
   modern things: Аня's blouse with an embroidered yoke and a print skirt with an ornament hem, Савелий's knitted
   waistcoat, Вера's printed rose shawl (Pavlovo Posad — worn today as then), Марат's cook's jacket with an
   embroidered stand collar and placket and a rushnik towel, Кира's hoodie with a printed ornament band, Тим's striped
   top and knitted knee socks. No sarafans or kokoshniks.
5. **By eye.** What changed on the way: the head's outline was lumpy (cosine easing between table keys → a monotone
   cubic); the face was a narrow snout in three-quarter view (the face depth now follows the profile mask, the
   silhouette is found by sampling each cross-section); the chin was flat (its point was lost when thinning the
   outline); hair was a helmet with a straight edge (the cap is now closed along a 3D hairline, locks are ribbons
   that start tapered inside the mass); Тим's curls stuck out like antennae (the cap's edge is now broken into lobes);
   the first hands were paddles of tubes (now one silhouette per pose with finger lobes); arms ended in square cuts at
   the shoulder (a round cap), elbows broke at sharp bends (two tubes and a round joint); Вера's knot sat in front of
   her cheek (it is now behind the head); Кира read as a boy (softer jaw, fuller lips, lashes, shorter neck); the plain
   landscape looked like flat vector (Bilibin's firs in tiers, a birch, a flower frieze along the near edge, a double
   ornament border).
6. **Not done / weak:** Марат's profile (the beard folds badly), so his turnaround is not shown; Кира's expression
   sheet was made and dropped — the four faces differed too little; the figures' torsos stay stiff.

## Sources of the samples

| file | work | link |
|---|---|---|
| 01 | Bilibin, «Vasilisa the Beautiful», 1900 (Vasilisa with the skull lantern) | https://uploads3.wikiart.org/images/ivan-bilibin/illustration-for-the-fairy-tale-vasilisa-the-beautiful-1900-3(1).jpg |
| 02 | Bilibin, «Vasilisa the Beautiful», 1900 | https://uploads3.wikiart.org/images/ivan-bilibin/illustration-for-the-fairy-tale-vasilisa-the-beautiful-1900-1(1).jpg |
| 03 | Bilibin, «The Frog Princess», 1899 | https://uploads5.wikiart.org/images/ivan-bilibin/illustration-for-the-russian-fairy-story-the-frog-princess-1899(1).jpg |
| 04 | Bilibin, «Tale of Tsar Saltan», Merchants, 1905 | https://uploads1.wikiart.org/images/ivan-bilibin/merchants-illustration-for-alexander-pushkin-s-fairytale-of-the-tsar-saltan-1905.jpg |
| 05 | Bilibin, «Tale of Tsar Saltan», 1905 | https://uploads5.wikiart.org/images/ivan-bilibin/illustration-for-alexander-pushkin-s-fairytale-of-the-tsar-saltan-1905-4(1).jpg |
| 06 | Bilibin, «Feather of Finist the Falcon», 1900 | https://uploads0.wikiart.org/images/ivan-bilibin/illustration-for-the-russian-fairy-story-feather-of-finist-falcon-2(1).jpg |
| 07 | Bilibin, «Vasilisa the Beautiful», first page, 1900 | https://uploads1.wikiart.org/images/ivan-bilibin/illustration-for-the-fairy-tale-vasilisa-the-beautiful-1900(1).jpg |
| 08 | Bilibin, «Red Rider», 1899 | https://uploads8.wikiart.org/images/ivan-bilibin/red-rider-illustration-for-the-fairy-tale-vasilisa-the-beautiful-1899.jpg |
| 09 | Alphonse Mucha, «Job», 1896 | https://uploads3.wikiart.org/images/alphonse-mucha/job-1896.jpg |
| 10 | Mucha, «Zodiac», 1896 | https://uploads5.wikiart.org/00380/images/alphonse-mucha/mucha-zodiac-portfolio-arts-group.jpg |
| 11 | Mucha, «Byzantine Head. The Blonde», 1897 | https://uploads7.wikiart.org/images/alphonse-mucha/byzantine-head-the-blonde-1897.jpg |
| 12 | Kay Nielsen, «East of the Sun and West of the Moon», 1914 | https://uploads8.wikiart.org/images/kay-nielsen/east-of-the-sun-and-west-of-the-moon-1914-1.jpg |

## How to repeat

```
cd styles/s17-bilibin
python3 tools/build.py            # every picture → svg/ and pics/ (one headless Chromium, ~1 min)
python3 tools/build.py portrait   # only names containing "portrait"; also figure, turn, expr, cast, rule
```

Playwright must be reachable by `require('playwright')`.

## The code (`tools/`)

- `kit.py` — the means of the style; knows no person. `Doc`: groups (`with d.g(x, y, scale, rot, flip)`),
  `fill` / `ink` (the even line, `LINE`) / `thin` (inner line, `THIN`) / `shape` (colour + contour) / `lock`,
  `clipped`, `band` (an ornament band along any curve: rhomb, cross, teeth, wave, dots, flower, stripe), cloth
  patterns `p_sprig`, `p_rhombs`, `p_herring`, `p_stripes`, `p_dots`, `p_checks`, `p_scales`; the page: `frame`
  (double ornament border), `halo` (Mucha's disc), `landscape` (sky, clouds, a row of firs, fields), `fir`,
  `birch`, `tuft`, `meadow`; paper texture in `svg()`.
- `parts.py` — how the style draws a person. `P(...)` — a head's numbers (cross-section widths, the profile:
  forehead, brow, nose, lips, chin; eye, brow, nose kind, mouth, lips, skin, freckles); `View(p, yaw)` turns and
  projects it (0 front, 35 three-quarter, 90 profile, the face turning to the sheet's left); `head(d, p, yaw, e,
  back, under, front, extra)` draws outline, ears, features; `EXPR` / `expr(name, ...)` — expressions as numbers
  (brow, tilt, open, smile, mouth, wide, smirk, round, teeth, cheeks, look); hair helpers `shell` (a cap closed
  along a 3D `hairline`), `side_hair` (a fringe round a bald head), `lobes` (curls, tufts, choppy locks on an
  edge), `ribbon` (a lock with a curl), `strands`; `Torso` (shoulders for a bust, turned like the head), `neck`,
  `limb`, `hand` (`HANDS`: rest, open, fist, point).
- `fig.py` — pieces of a full figure in head units: `arm` (shoulder cap, two tubes, round elbow, optional rolled
  sleeve and cuff, the hand), `leg`, `shoe` (also a boot), `skirt` (with an ornament hem), `flowers`.
- `anya.py`, `savely.py`, `tim.py`, `vera.py`, `marat.py`, `kira.py` — one module per character.
- `pages.py` — the sheets: `portrait`, `figure`, `row` (turnarounds and expression sheets in arched niches),
  `group` (the cast on one field); `rules.py` — the diagram sheets; `build.py` — the list of pictures;
  `render.js` — SVG → JPEG.

## How to add a character

1. Copy the nearest module (`vera.py` or `kira.py` for a flipped three-quarter character, `tim.py` for a child,
   `marat.py` for a big man with a beard).
2. Set `NAME`, `HEIGHT` (head units: a head is ~200; Тим 1050 … Марат 1540), colours, `HALO` (ring, field, ink of the
   portrait's disc) and `p = parts.P(...)`: the face first (`cheek`, `jaw`, `jaw_y`, `chin`, `chin_w`, the profile
   `forehead`, `brow_z`, `nose_z`, `lip_z`, `chin_z`), then the eye (`eye_w`, `eye_h`, `iris`, `lashes`, `under`),
   the brow (`arc`, `straight`, `thick`, `bushy`), the nose (`straight`, `snub`, `big`, `hooked`), the mouth and
   lips. `e_(name)` gives this person's resting face and overrides of joy / surprise / sadness / anger.
3. Hair: a function `hair(d, v)` — `parts.shell(v, grow, y_side, hairline)` for the cap (make the edge curly or
   choppy with `parts.lobes`), `parts.ribbon` for locks, `parts.strands` inside, clipped to the cap; a beard goes
   into `under`, glasses or a moustache into `extra`, hair behind the head into `back`. Check it with
   `bust(yaw=0/35/90)` — every view comes from the same numbers.
4. `bust(d, yaw, e)`: `parts.neck` → clothes on `parts.Torso(...)` (`shape` with a pattern, `band` along collars and
   plackets) → `parts.head`.
5. `figure(d, e)`: place the joints by hand with a line of action; draw back arm, legs and shoes, clothes, head (tilt
   it with nested `d.g`), front arm with `fig.arm` (hand pose and angle).
6. Add the module to `CAST` and to the sheets you want in `build.py`; build; look at it beside the others.
