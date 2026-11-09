# С13 — Японская гравюра: укиё-э и син-ханга

## What was done

1. **Samples.** This session's network let through only a few hosts, so the samples come from the Met's open-access
   collection (its API `collectionapi.metmuseum.org/public/collection/v1.1/search` and `/v1/objects/<id>`, images
   from `images.metmuseum.org`) and Wikimedia Commons (thumbnails from `upload.wikimedia.org`; its API answered
   "too many requests" most of the time, so files were taken by direct thumbnail path, slowly). Twelve kept in
   `refs/` (≤ 800 px, jpg). Not downloaded (rate limit): Sharaku's Ōtani Oniji from Commons (the Met's impression is
   used instead), Utamaro's «Three Beauties of the Present Day» and «Fukaku shinobu koi», Kotondo's «Rain».
   Itō Shinsui: not looked for on these hosts (his prints are not in the public domain); the shin-hanga rules rest
   on Goyō and Kotondo.
2. **Rules** — in `entry.json`, block «Правила стиля»; each is something seen in the samples.
3. **Drawing.** Every picture is SVG written by the Python scripts in `tools/` (points placed by hand, nothing
   traced, no image models), rendered to JPEG with headless Chromium through Playwright (`tools/render.js`).
4. **By eye.** Rendered, looked, redrew. What changed on the way: the wood grain was strong stripes over everything
   (made faint, a light streak only where the colour is dark); skin was darker than the ground (it is now almost bare
   paper); the first faces were round dolls with round eyes (the face made longer, the eye lower and longer, the nose
   smaller, the blush weaker); hair was combed with even white stripes (now a few thin lines); busts were small in the
   middle of the sheet (now the head fills it and the sheet's edge cuts the shoulders, as in an okubi-e); the first
   fingers were thin rakes (shorter, fuller, tapering); Савелий stood tall and thin (now heavy-headed and stooped);
   Тим's hair was a paper crown (softer lumps); Марат's curls were a cog wheel (the bumps were on the wrong side);
   Тим's raised finger with a beetle looked rude (the beetle now sits on his shoulder).

## Sources of the samples

| file | work | link |
|---|---|---|
| 01 | Tōshūsai Sharaku, Ichikawa Ebizō, 1794 | https://www.metmuseum.org/art/collection/search/37368 |
| 02 | Sharaku, Ōtani Oniji III as Yakko Edobei, 1794 | https://www.metmuseum.org/art/collection/search/37358 |
| 03 | Kitagawa Utamaro, Young lady blowing on a poppin, c. 1790 | https://commons.wikimedia.org/wiki/File:Flickr_-_…trialsanderrors_-_Utamaro,_Young_lady_blowing_on_a_poppin,_1790.jpg |
| 04 | Utamaro, Woman Relaxing after Her Bath | https://www.metmuseum.org/art/collection/search/36623 |
| 05 | Utamaro, Hairdresser, from «Twelve Types of Women's Handicraft» | https://commons.wikimedia.org/wiki/File:Kitagawa_Utamaro_-_Hairdresser_(Kamiyui)_-_from_the_series_'Twelve_types_of_women's_handicraft_(Fujin_tewaza_juniko)'_-_Google_Art_Project.jpg |
| 06 | Katsushika Hokusai, Manga, vols 1–11 (the dancers) | https://www.metmuseum.org/art/collection/search/57804 |
| 07 | a sheet of hands, on Commons as «Manga Hokusai.jpg» | https://commons.wikimedia.org/wiki/File:Manga_Hokusai.jpg |
| 08 | Utagawa Kuniyoshi, Portrait of Yato Yomoshichi Norikane | https://www.metmuseum.org/art/collection/search/44999 |
| 09 | Kuniyoshi, «At first glance he looks very fierce, but he's really a nice person» | https://commons.wikimedia.org/wiki/File:At_first_glance_he_looks_very_fiarce,_but_he_s_really_a_nice_person.jpg |
| 10 | Hashiguchi Goyō, Woman Applying Makeup, 1918 | https://www.metmuseum.org/art/collection/search/908751 |
| 11 | Torii Kotondo, Combing Her Hair, 1929 (Walters Art Museum) | https://commons.wikimedia.org/wiki/File:Torii_Kotondo_-_Kamisuki_(Combing_Her_Hair)_-_Walters_95889.jpg |
| 12 | Suzuki Harunobu, Lovers Walking in the Snow | https://www.metmuseum.org/art/collection/search/45085 |

## How to repeat

```
cd styles/s13-ukiyo-e
python3 tools/build.py            # every picture → svg/ and pics/ (one headless Chromium, ~6 s)
python3 tools/build.py portrait   # only names containing "portrait"; also figure, turn, expr, cast, rule
```

Playwright must be reachable by `require('playwright')`.

## The code (`tools/`)

- `kit.py` — the print's means; knows no person. `Doc`: the sheet (`ground` — tone and bokashi bands, the border;
  `cartouche` — the name slip and the seal; paper, wood grain and age are filters laid over the whole sheet in
  `svg()`), groups (`with d.g(x, y, scale, rot, flip)`), `fill` / `shape` (flat colour, a pattern printed over it,
  the outline), `line` (one brush stroke; profiles `taper`, `tail`, `swell`, `press`, `even`), `contour` (a closed
  outline whose weight follows direction), `bokashi`, `strands` (fine lines between two guide curves), `fringe`
  (separate hairs out of an edge), the patterns (`stripes`, `checks`, `dots`, `asanoha`, `seigaiha`, `blossoms`,
  `kasuri`). Points are `(x, y)`; `(x, y, 'c')` is a corner.
- `parts.py` — how the print draws a head and a hand. `P(...)` — a character's numbers (length of the face, cheek,
  jaw, chin, eye, brow, nose kind, mouth, blush); `head(d, p, view, expr, under, extra, front)` — views `q`
  (three-quarter, turned left), `f`, `s`; `EXPR` — expressions as numbers; `neck`, `shoulders`, `hand` (poses
  `rest`, `pinch`, `open`, `point`, `grip`), `glasses`, `tube` (a limb), `scallop` (a curly edge), `oval`, `flower`.
  A head is 200 units high, eye line at y = 0.
- `anya.py`, `savely.py`, `tim.py`, `vera.py`, `marat.py`, `kira.py` — one module per character.
- `build.py` — the sheets (portraits, figures, turnarounds, expressions, the two groups, the rule pictures);
  `render.js` — SVG → JPEG.

## How to add a character

1. Copy the nearest module (`kira.py` for a three-quarter-only character, `marat.py` for one with all three views).
2. Set `NAME`, `HEIGHT` (figure units; a head is about 100, Тим 500 … Марат 800), the colours, and `p = parts.P(...)`:
   start from the face (long / cheek / jaw / chin), then the eye (`w`, `h`, `iris`, `lid`), the brow kind (`arc`,
   `thick`, `bushy`), the nose kind (`soft`, `snub`, `long`, `big`, `broad`), the mouth. `CALM` is the resting
   expression; `EXPR` overrides what joy, surprise, sadness and anger mean for this person.
3. Hair: a function drawing in head units — a flat mass (`d.fill`), a few `d.strands`, `d.fringe` along the hairline;
   one branch per view you need. A beard goes into `under`, a moustache, wrinkles, glasses into `extra`.
4. `bust(d, view, expr, hand)`: neck → clothes on `parts.shoulders(...)` (choose a pattern) → head. `hand=True`
   adds the hand and the prop of the portrait.
5. `figure(d)`: feet at y = 0, the body turned left; back to front: far arm, legs, body, near arm, neck, head
   (`with d.g(hx, hy, 0.46…0.52, rot)`). Decide the arc of the pose first.
6. In `build.py`: add the module to `WHO` and a ground to `GROUND`; list the key in `_each('turn', …)` /
   `_each('expr', …)` if it has them; place it in a group with `stand(...)`.
7. Render, look next to the others and next to `refs/`, redraw.

## Round three: Марат and Кира

Drawn with the same parts as the four. Марат: `brow kind='thick'`, `nose kind='broad'`, the resting expression is
`grin` (eyes closed into arcs, the open mouth with teeth and tongue), the beard is a black mass under the features
with `fringe` at its edge, curls by `scallop`; three views. Кира: a long narrow face, a low straight brow, the gaze
turned aside (`look=(5, …)`), the fringe drawn over the far eye, `joy` is a smirk; three-quarter view only.
`pics/cast6.jpg` is all six; `pics/cast.jpg` (the cover) is the four.
