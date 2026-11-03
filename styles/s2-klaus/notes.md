# С2 — Klaus: рисованное как объём

## What was done

1. **Samples.** Searched for character art of "Klaus" (SPA Studios, 2019): the Cartoon Brew gallery from
   "Klaus: The Art of the Movie", articles about the film's lighting (Before & Afters, 3DVF, a UAL student blog that
   reposts Netflix production stills), Netflix production stills. Looked at all of them, kept ten in `refs/`
   (≤ 800 px, jpg). The most useful: `01` (Jesper: line → flat colour → lit — the whole trick of the style),
   `02` (Klaus flat vs lit), `03` (the book's page on volumetric eyes). The four Klaus frames already in
   `docs/pictures/references/` were used as well.
2. **Rules** — written into `entry.json` (block «Правила стиля»), each one from what is seen in the samples.
3. **Drawing.** Every picture is SVG written by Python scripts in `tools/` (hand-written paths, no tracing, no image
   models):
   - `kit.py` — the light model. A *form* is one flat shape; on top of it, inside its clip: the shadow colour masked
     by the shape moved toward the light and blurred (gives the core shadow with a soft edge on the far side), then
     hand-drawn tone shapes (cast shadows of hair and nose, eye sockets, blush), then optionally a thin rim light
     (the shape minus the shape moved toward the light). Colours: lit = base mixed toward a warm key, shadow = base
     mixed toward a cool purple. `grain()` adds fine grain, a broad mottled texture (soft-light) and a vignette.
     `Doc.flat = True` draws only the flat colours (used for the rules picture).
   - `parts.py` — the Klaus eye (white, big iris, heavy lid with its shadow, thick lash line with a wing past the
     outer corner, crease, lower lid), tapered brows.
   - `anya.py`, `savely.py`, `tim.py`, `vera.py` — each character: `head34(d, out, expr)` (three-quarter head in a
     500×600 frame, chin anchors in `common.py`), `bust`, `figure`; Аня and Тим also `head_front`, `head_side`,
     `bust_front`, `bust_side`; expressions in `EXPR`.
   - `build.py` — composes and renders all pictures.
4. **By eye.** Rendered, looked, redrew many times: the first versions had a light halo round every shape (rim on
   inner edges; rim is now off by default), faces too flat (the shadow plane was hidden under the hair — moved the
   terminator into the face), necks like pillars (shoulders raised), hair like a helmet (split into a front lock and
   two curtains), Tim's fringe dirty (explicit shadow on the back of the hair instead of the moved-shape shadow),
   Anya's joy looked sly (lids up, lower lids pushed up by the cheeks).

## How to repeat

```
cd styles/s2-klaus
python3 tools/build.py            # all pictures → svg/ and pics/ (headless google-chrome, ~45 s)
python3 tools/build.py portrait   # only names that contain "portrait"
```

Rendering is `google-chrome --headless=new --screenshot` of a tiny HTML page holding the SVG (SVG filters, masks
and blend modes render as in a browser).

## Honest state

Close in light and mood; weaker in drawing than SPA: faces milder than their caricature, poses stiffer, no living
line, no painterly brush. Turnarounds are heads with shoulders, not full figures. Hands are simple.

## Sources (third-party pictures, kept only as references)

- `refs/01-jesper-line-flat-lit.jpg` — Before & Afters, "Here's what made the 2D animation in Klaus look 3D",
  https://beforesandafters.com/2019/11/14/heres-what-made-the-2d-animation-in-klaus-look-3d/ (image
  `klaus_feature.jpg`; also reposted at https://ctrlz.myblog.arts.ac.uk/?p=34)
- `refs/02-klaus-flat-vs-lit.jpg` — https://ctrlz.myblog.arts.ac.uk/?p=34 (`klaus.jpg`, comparison from a Klaus test)
- `refs/03-eyes-volumetric.jpg`, `refs/06-krum-women-designs.jpg`, `refs/07-ellingboe-sheet.jpg` — "Klaus: The Art
  of the Movie", Cartoon Brew gallery,
  https://www.cartoonbrew.com/books/book-preview-klaus-the-art-of-the-movie-exclusive-gallery-182718.html
  (Klaus_ArtoftheMovie_13, _81, _51)
- `refs/04-alva-jesper-arch.jpg`, `refs/05-klaus-jesper-sleigh.jpg`, `refs/08-jesper-margu.jpg` — Netflix production
  stills via Before & Afters (`Klaus-Production-Stills-022`, `-014`, `-023`)
- `refs/09-townsfolk.jpg` — 3DVF, https://3dvf.com/redaction/klaus-les-coulisses-dun-film-danimation-hors-du-commun/2/
- `refs/10-klaus-lighting-tool.jpg` — 3DVF, interview with Florian Aupetit,
  https://3dvf.com/klaus-les-coulisses-de-leclairage-du-film-en-compagnie-de-florian-aupetit/

Downloads and scratch renders: `/home/user/cache/styles-s2-klaus/`.
