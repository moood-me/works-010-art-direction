# С3 — Графичный: плоские формы

What was done (Claude, one agent of the "Стили персонажей" run; the brief is `/home/user/cache/BRIEF-styles.md`): found
samples of the flat graphic style (Nimona, Cartoon Saloon, Hilda, Spider-Verse concepts, UPA), wrote the style's rules
from them, and drew the same cast — Аня, Савелий Петрович, Тим, Вера — in hand-written SVG by those rules: four
portraits, four full figures, turnarounds for Аня and Савелий Петрович, expression sheets for all four, the four
together, and two rule diagrams (main shapes, eye construction).

## How it was drawn

- Every shape is a hand-written cubic path in Python (`tools/*.py`), one module per character, written into SVG by
  `tools/build.py`. No tracing, no image models.
- `tools/lib.py`: `F` (a flat shape with a coloured outline), `L` (a line), `clip`/`shaded` (a cel shadow: a second
  shape clipped inside the form), `mx` (mirror a path for front views).
- `tools/face.py`: the shared eye (white oval, iris, lid that cuts the top and casts a shade, filled lash shape with
  an optional wing, lower lid for smiles), closed eye, tapered brow, the angry mouth.
- Each character module has `head_q(expr)` (three-quarter head with expressions), `figure_q()`; Аня and Савелий also
  `figure_f()` (front) and `figure_s()` (profile).
- Iteration was by eye: render, compare with the samples, redraw. What changed on the way: Аня's eyes made bigger and
  the fringe raised so the brows show; her hair rebuilt as two curtains from a middle part (the first hair was a
  helmet); her back hair moved behind the body; a filled lash shape instead of a stroked lid line (the stroked one
  looked like a worm); no lash wing for the men and the boy; Савелий's horn-like tufts removed, his head sunk into the
  collar; the angry mouth redrawn as a box with clenched teeth (the first was a thin strip); dresses and the coat made
  longer, so legs are not long sticks.

## Repeat

```
cd styles/s3-graphic/tools
python3 build.py                                                    # writes ../svg/*.svg
NODE_PATH=/opt/node-tools/node_modules node render.js ../pics 1 ../svg/*.svg   # headless Chrome → ../pics/*.png
```

`render.js` uses Playwright with `/usr/bin/google-chrome`.

## Sources of the samples (`refs/`, third-party, kept only as references)

- `01-nimona-key-art.jpg` — Nimona (2023) key art, via animatedviews.com:
  https://animatedviews.com/2023/nimonas-production-designer-aidan-sugano-creating-a-future-medieval-world/
- `02-nimona-ambrosius.jpg` — Nimona still, from `docs/pictures/references/nimona-ambrosius.png` (sent by Pavel).
- `03-nimona-concept-sugano.jpg` — Aidan Sugano, Nimona hair concept, The heART of Nimona exhibition, Gallery Nucleus:
  https://www.gallerynucleus.com/events/1024
- `04-song-of-the-sea-cast.jpg` — Song of the Sea character cards (Conor, Granny, Bronagh, Saoirse), cropped and put
  side by side: https://screenanarchy.com/2012/08/meet-the-characters-in-tomm-moores-song-of-the-sea.html
- `05-song-of-the-sea-still.jpg` — same page, birthday scene.
- `06-wolfwalkers-still.jpg`, `07-wolfwalkers-model-sheet.jpg` — Animation Obsessive, "Inside the look of Wolfwalkers
  with Sandra Andersen": https://animationobsessive.substack.com/p/inside-the-look-of-wolfwalkers-with
- `08-hilda-turnaround-mother.jpg`, `09-hilda-turnaround-boy.jpg` — Hilda model sheets:
  https://floobynooby.blogspot.com/2018/09/hilda-animated-series.html
- `10-spiderverse-aunt-may.jpg` — Into the Spider-Verse concept art:
  https://www.slashfilm.com/563128/spider-man-into-the-spider-verse-concept-art
- `11-upa-gerald-model-sheet.jpg` — UPA, Gerald McBoing-Boing model sheet:
  https://cartoonresearch.com/index.php/sounds-like-a-classic-the-75th-anniversary-of-gerald-mcboing-boing/

Downloads and scratch renders are in `/home/user/cache/styles-s3-graphic/`.

## Honest state

Close to Song of the Sea / Hilda, not to Nimona: no soft sculpted shading, no tapered brush line. Weak: uniform line
width, thin legs, hands avoided (pockets, behind the back, holding things), calm poses without a line of action,
front and profile views simpler than the three-quarter. Strongest: Тим and Савелий Петрович.
