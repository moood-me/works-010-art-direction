# С20 «Советская мультипликация 60–70-х» — notes

Round three of "Стили персонажей" (brief: `docs/briefs/styles-more.md`, part B). A new style: the people of
Soyuzmultfilm's 1960s–70s films as Fyodor Khitruk, Vladimir Zuykov, Eduard Nazarov and Vyacheslav Kotyonochkin drew
them. All six of the cast are drawn: Аня, Савелий Петрович, Тим, Вера, Марат, Кира.

## What was done

1. **Samples** (`refs/`, twelve small copies, sources below). Wikipedia and Wikimedia Commons answered "429 Too many
   requests" to this session (the API and upload.wikimedia.org, also for thumbnails), so the stills on the Wikipedia
   pages of «Винни-Пух», «Жил-был Козявин», «Ну, погоди!» were **not downloaded**; nothing was traced from memory or
   faked. What was downloaded: the Film Museum / Animation Foundation gallery of sketches and stills on Russia Beyond,
   Animation Obsessive's stills of «Человек в рамке» and «История одного преступления», Lambiek's Kotyonochkin page,
   stills in articles on mel.fm, snob.ru, vokrugsveta.ru, sport24.ru. Khrzhanovsky could not be found as pictures in
   what the network gave; the rules do not lean on him. Bing image search was refused by the session's permissions.
2. **Rules** — written from those samples (in `entry.json`, block «Правила стиля»). The core: a bold caricature form
   for body and head, the face left as paper, the nose over the contour, small eyes by the nose with a lid that cuts
   them, a pen line with pressure, paint off register with gouache streaks, crayon for blush, stripes and shadow,
   one bright field behind with dry-brush clouds and a crayon meadow.
3. **Drawing code** (`tools/`, Python → SVG, no dependencies). Chosen to stay far from С9 (gouache without line,
   painted skin): here everything has an ink line, faces are unpainted, forms are blunt caricature.
4. **Sheets**: portrait and figure for all six; turnarounds for Аня, Тим, Марат, Кира; expression sheets for all six;
   the four together (`cast`, the cover), all six together (`cast6`); two rule pictures.
5. Looked at every render and redrew: the first brush texture was a sponge of speckles → broad soft streaks only;
   heads had sharp box corners → crown and chin points; Аня's head and hands were too small, legs too long → bigger
   head, shorter legs, bigger hands everywhere (×1.25); profiles were a circle with a nose → a face line built from the
   features (`prof`), and the hair now lies over the back of the skull in profile; Марат first read as an apron with a
   head → a barrel jacket wider than the apron, arms out from under the shoulders, a cooler white for the jacket so
   the bare forearms read; Вера's finger at her nose read as picking it → a raised finger beside her head; Кира's hand
   at her chin → arms crossed; Савелий's moustache read as a frown even in joy → two lobes whose tips go up when he
   laughs, the mouth moved below it; a big loupe read as a cap → small.

## How it is built

- `tools/kit.py` — the hand and the paper. `ink(points, lw, closed, taper, weight, gap, press)` — a line as a filled
  outline through Catmull-Rom points: wobble along the normal, thinner at open ends, heavier where the contour faces
  down-right, a gap may be left. `paint(points, colour, tex)` — paint shifted off register (`OFF()`), textures
  `brush` / `crayon` / `flat`; `form()` = paint + line; `hatch()` — pencil hatching clipped to a shape; `blush()` —
  rubbed crayon; `Doc` writes the SVG with the filters it used and a paper grain over everything. `scaled(s)` tells
  the kit the scale the drawing will be placed at, so line width, shift and grain stay the same on screen.
- `tools/face.py` — `Head(rows, …)`: the skull as half-widths at a few heights; eyes (`ring`, `dot`, `happy`, `wide`,
  a lid as a line), bushy or stroke brows, noses (`button`, `potato`, `long`, `wedge`), mouths (`line`, `smirk`, `o`,
  `open` with teeth and tongue, `teeth`), ears, cheeks; views `front`, `three`, `side`; `EXPR` holds the expressions,
  a character overrides them in `expr=`. `draw(view, expr, hair_back, hair_front, beard, stache, after)`.
- `tools/body.py` — `pick(front, side, view)`: a silhouette written for front and side with the same number of points;
  three-quarters is their blend. `tube/limb/leg`, `hand(kind = open, rest, fist, hold, point)`, `shoe`.
- `tools/anya.py … kira.py` — one module per character: `NAME`, `HEIGHT`, colours, `HEAD`, hair, `head(view, expr)`,
  `figure(view, expr, pose)` (feet at y = 0; pose `stand` for turnarounds and portraits, `act` for the gesture).
- `tools/build.py` — the sheets and the scenery (clouds, meadow with crayon flowers); `tools/render.js` — SVG → PNG
  (Playwright, one browser); `tools/webp.py` — PNG → WebP.

## Repeat

```
cd styles/s20-soviet
python3 tools/build.py              # all sheets → svg/   (or names: python3 tools/build.py cast figure-kira)
node tools/render.js                # → pics/*.png        (or names)
python3 tools/webp.py               # → pics/*.webp, removes the png
```

## How to add a character

1. Copy the nearest module (`kira.py` thin and slouched, `marat.py` big and bearded, `vera.py` tall with glasses,
   `tim.py` a child, `savely.py` old) to `tools/<name>.py`.
2. Pick the caricature first: one shape for the body, one for the head. `HEAD = F.Head(rows=…)` — half-widths of the
   head from crown to chin; eyes (`eye_y, eye_gap, eye_r`), nose kind and size, mouth, brows; `prof` for the profile
   line; `expr` for the character's own calm and corrections.
3. Hair as one or two dark masses in head units (centre (0, 0), crown near −60); in `side` put the mass over the face
   (return it as the front layer) so it covers the back of the skull.
4. `figure()`: write each big shape for the front and for the side with the same number of points and let `B.pick`
   make the three-quarters; draw in order legs, far arm, body, head (`place_head`), near arm. The `act` pose gets one
   clear gesture.
5. Two or three colours of the palette plus at most one sharp accent; hatching on the shaded side.
6. Add the module to `WHO` and `BG` in `build.py` (and `TURN` for a turnaround), build, render, look, redraw.

## What is weak

Bodies are simple silhouettes with tube arms; turnarounds stand stiffly; hands are small mittens with finger lines or
fists; textures come from SVG filters and are more even than real gouache and crayon; profiles reuse the front
skull; Савелий Петрович's face is crowded by white brows and moustache; Аня is the simplest of the six.

## Sources

- Russia Beyond, "What did Soviet cartoon characters look like before their release?" (Animation Foundation / Film
  Museum) — https://www.gw2ru.com/arts/198704-soviet-cartoon-characters-before-release — refs 01, 02, 05, 07
  («Фильм, фильм, фильм», «Каникулы Бонифация», «Винни-Пух»).
- Animation Obsessive — https://animationobsessive.substack.com/p/how-the-man-in-the-frame-pushed-back (ref 03,
  «Человек в рамке»), https://animationobsessive.substack.com/p/we-did-not-know-what-was-against (ref 04,
  «История одного преступления»).
- mel.fm, "8 мультфильмов Фёдора Хитрука" — https://mel.fm/zhizn/razvlecheniya/3052761-khitruk_animation (ref 06).
- sport24.ru on «Бременские музыканты» —
  https://sport24.ru/-/article-okazyvayetsya-u-printsessy-iz-bremenskikh-muzykantov-byl-realnyy-prototip-s-kogo-srisovali-vozlyublennuyu-trubadura
  (ref 08); on «Жил-был пёс» —
  https://sport24.ru/lifestyle/article-skolko-poluchil-sozdatel-legendarnogo-multfilma-iz-sssr-zhil-byl-pes-eduard-nazarov-sud-s-soyuzmultfilmom-premiya-rezhissera
  (ref 12).
- vokrugsveta.ru, мультфильмы 1969 года — https://www.vokrugsveta.ru/article/320243/ (refs 09, 11).
- Lambiek Comiclopedia, Kotyonochkin — https://www.lambiek.net/artists/k/kotenochkin.htm (ref 10).
- Not downloaded (Wikimedia 429): https://en.wikipedia.org/wiki/Winnie-the-Pooh_(1969_film),
  https://en.wikipedia.org/wiki/There_Lived_Kozyavin, https://en.wikipedia.org/wiki/Well,_Just_You_Wait!

Downloads and scratch renders: `/home/user/cache/styles-s20-soviet/`.
