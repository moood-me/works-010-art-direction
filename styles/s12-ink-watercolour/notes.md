# С12 — Перо и акварель: книжная иллюстрация

## What was done

1. **Samples.** Looked for character art by picture-book pen-and-watercolour illustrators: Quentin Blake (his own
   site and the Quentin Blake Centre), Edward Ardizzone (Chris Beetles Gallery), Ronald Searle (Sotheby's), Sempé
   (auction listings), Tomi Ungerer (The Drawing Center), Lisbeth Zwerger (The Marginalian). Oliver Jeffers: nothing
   usable found (only a pencil sketch), so he is not among the samples. Kept twelve in `refs/` (≤ 800 px, jpg).
   The most useful: `01` (Blake's self-portrait — nose, two marks for eyes, a cheek of pink), `02` (old man and girl —
   white-paper eyes, gesture, washes that don't reach the line), `03` (a crowd — every person a different nose and
   silhouette), `05` (Blake's pens).
2. **Rules** — in `entry.json`, block «Правила стиля», each from what is seen in the samples.
3. **Drawing.** Every picture is SVG written by Python scripts in `tools/` (points placed by hand, no tracing, no
   image models). Rendered with headless Chrome (filters and blend modes as in a browser), kept as JPEG (the grain
   makes PNGs ~1 MB each).
4. **By eye.** Rendered, looked, redrew: the first line was a smooth vector line (made thicker, with stronger
   pressure, a fine tremor and a second pass of the pen); the first washes were soft clouds like an airbrush (the
   pigment noise was made streaky, along a random brush direction, with a darker dried rim and less blur); faces were
   blank (eyes made bigger, rounds of white paper); Tim's hair went from a zigzag crown to radial spikes like a
   hedgehog to tufts leaning one way; Вера's hair came out grey (dark colours need two layers); necks were too long
   everywhere (shortened); Савелий stood straight (now bent from the hips and looking at his watch); Вера's folded
   arms were a tangle (now one arm holds the folder); expressions were too quiet (brows and mouths bigger, the head
   tilts with the feeling, a tear / start-lines / a flush beside the face); open mouths stuck out of the profile like a
   beak (their near corner is kept inside the contour).

## How to repeat

```
cd styles/s12-ink-watercolour
python3 tools/build.py            # all pictures → svg/ and pics/ (headless google-chrome, ~25 s)
python3 tools/build.py portrait   # only names that contain "portrait"; also figure, turn, expr, cast, rule
```

## The code (`tools/`) and how to add a character

- `kit.py` — the medium, knows no person. `Doc` (picture, transform stack `push/pop`, `turn` to lean a body,
  layers: paper → washes → whites → ink; `fade` for the book-page vignette). `ink()` — a pen stroke through points:
  pressure, taper (`start`/`end`), wobble (`jit`), second pass (`retrace`), dry nib (`skip`). `wash()` — a watercolour
  patch (SVG filter: displaced edge, streaky pigment along `angle`, dark rim, grain); `dx/dy` move it off the line.
  `dot()`, `white()` (paper left white: eyes), `blot()` (cheeks), `hatch()`. `render()`.
- `parts.py` — things drawn the same for everyone: colours, `EXPR` (expressions as numbers), `eye()`, `brow()`,
  `mouth()`, `extra()` (tear / start / flush), `hand()`, `tufts()` (tufty hair edge), `tube()` (sleeve, leg: two pen
  lines and a wash), `shoe()`.
- `anya.py`, `savely.py`, `tim.py`, `vera.py` — a person each. Head units: crown about y = −125, chin y ≈ 100,
  eyes at y ≈ 0, the face looking to the viewer's left (mirror with `d.push(..., flip=True)`). Each has
  `head34(d, expr)`, `bust(d)` (600 × 720), `figure(d, expr)` (600 × 1000, feet at y ≈ 880); Аня and Тим also
  `head_front`, `head_side`, `bust_view(d, view)` (500 × 620).
- `build.py` — composes the pictures (`JOBS`).

To add a person: copy the closest of the four (a young woman → `anya.py`, a man → `savely.py`), keep the same head
units, and change what makes the character: the profile line (forehead, nose, lips, chin) in `head34`, eye size and
lids, brows, hair (a wash mass + a few lines, or `tufts`), colours at the top of the file; then the clothes in
`bust` and the pose in `figure` (a body is washes + `tube()` limbs + `hand()`; lean it with `d.turn`). Expressions come
from `parts.EXPR` through `eye/brow/mouth/extra`. Add the jobs in `build.py`. Look at it next to `refs/` and redraw.

## Honest state

Reads as a pen-and-watercolour picture book, with likeable characters, but cleaner than Blake: the line is not
scratchy enough, the washes are sometimes too soft (no blooms or wet edges), poses are simpler, hands are schematic,
turnarounds are heads with shoulders only.

## Sources (third-party pictures, kept only as references)

- `refs/01-blake-selfportrait.jpg` — quentinblake.com, https://quentinblake.com/storage/5464/SP31_018.jpg
- `refs/02-blake-join-the-movement.jpg` — quentinblake.com, Refugee Week 2026 news,
  https://quentinblake.com/news/refugee-week-2026-simple-acts-campaign-uses-quentins-illustrations
- `refs/03-blake-crowd-door.jpg` — quentinblake.com (home page gallery), https://quentinblake.com
- `refs/04-blake-courage.jpg` — quentinblake.com, same Refugee Week news page as `02`
- `refs/05-blake-pens.jpg` — Quentin Blake Centre for Illustration, https://www.qbcentre.org.uk/quentin-blake
- `refs/06-ardizzone-old-man-boy.jpg` — Chris Beetles Gallery, «Jim and Derry»,
  https://chrisbeetles.com/artwork/50252/jim-and-derry
- `refs/07-ardizzone-tim-cover.jpg` — Chris Beetles Gallery, «Tim to the Rescue I»,
  https://chrisbeetles.com/artwork/47620/tim-to-the-rescue-i
- `refs/08-searle-heredity.jpg` — Sotheby's, Ronald Searle, «…Unaccountable thing heredity…», 1954,
  https://www.sothebys.com/en/buy/auction/2021/books-and-manuscripts-19th-and-20th-century-2/ronald-searle-unaccountable-thing-heredity-1954
- `refs/09-sempe-lunch.jpg` — Very Important Lot, Sempé,
  https://veryimportantlot.com/en/lot/view/semp201-jean-jacques-1932-2022-1079613
- `refs/10-ungerer-ink-wash.jpg` — The Drawing Center, «Tomi Ungerer: All in One»,
  https://drawingcenter.org/exhibitions/tomi-ungerer-all-in-one
- `refs/11-zwerger-alice.jpg`, `refs/12-zwerger-alice-cover.jpg` — The Marginalian, Lisbeth Zwerger's «Alice in
  Wonderland», https://www.themarginalian.org/2014/04/30/lisbeth-zwergers-alice-in-wonderland/

Downloads and scratch are in `/home/user/cache/styles-s12-ink-watercolour/`.
