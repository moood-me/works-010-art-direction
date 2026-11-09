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
- `anya.py`, `savely.py`, `tim.py`, `vera.py`, `marat.py`, `kira.py` — a person each. Head units: crown about y = −125, chin y ≈ 100,
  eyes at y ≈ 0, the face looking to the viewer's left (mirror with `d.push(..., flip=True)`). Each has
  `head34(d, expr)`, `bust(d)` (600 × 720), `figure(d, expr)` (600 × 1000, feet at y ≈ 880); Аня, Тим, Марат and Кира also
  `head_front`, `head_side`, `bust_view(d, view)` (500 × 620).
- `build.py` — composes the pictures (`JOBS`).

To add a person: copy the closest of the four (a young woman → `anya.py`, a man → `savely.py`), keep the same head
units, and change what makes the character: the profile line (forehead, nose, lips, chin) in `head34`, eye size and
lids, brows, hair (a wash mass + a few lines, or `tufts`), colours at the top of the file; then the clothes in
`bust` and the pose in `figure` (a body is washes + `tube()` limbs + `hand()`; lean it with `d.turn`). Expressions come
from `parts.EXPR` through `eye/brow/mouth/extra`. Add the jobs in `build.py`. Look at it next to `refs/` and redraw.

## Round three: Марат and Кира

Asked for by the brief `docs/briefs/styles-more.md` (part A): two more characters in this style, the four untouched.

- **Added to the shared code** (new functions and new `EXPR` keys only; the four's SVGs were regenerated and
  compared byte for byte — unchanged): `kit.paper()` (paper left white in any shape — teeth), `kit.gouache()` and
  `kit.gouache_line()` (a light opaque accent over a dark wash: the paper is cleared in that shape and the colour
  laid on it — the layers are washes → whites → ink, so a light colour can't otherwise sit on a dark one);
  `parts.curls()` (a curly hair edge: a row of round bumps), `parts.curl()` (one hook of a curl inside the mass),
  `parts.chop()` (chopped hair ends: base, tip, base… — each lock two strokes meeting in a point);
  `EXPR['merry']` (Марат at rest), `EXPR['sulk']` (Кира at rest).
- **`marat.py`.** A wide head; hair and beard are dark washes in two layers with `curls()` round the edge and
  `curl()` hooks inside; the beard is a polygon that leaves a gap for the mouth and drops with the jaw. His own mouth
  `grin()`: teeth are `paper()` under the upper lip, the dark of the mouth below, a tongue when he laughs. The white
  jacket is bare paper with a warm grey shade. `figure`: the upper body turned back 8° from the knees, the belly
  line leading, the head thrown back (a negative turn of the head throws it back, a positive one bows it).
  By eye: the first curls were a lace edge with bubbles (fewer, bigger bumps; hooks, not loops), the hair sat like a
  hat (hairline lowered, no bumps along it), the eyes were dots (bigger), the nose a beak (shortened), the figure a
  rectangle with a small head (head 0.62 → 0.72, belly line, longer legs).
- **`kira.py`.** A longer face than a child's, a small pointed chin, a light jaw; both eyes in the open, with a
  heavy upper lid and the pupil high under it (`her_eye`), a low straight brow over the near one; the fringe hides
  only the far brow, one long lock hangs down the far side of the face. `lips()` — her own small mouths, all inside
  the face: pressed shut, the half-smirk, a round of surprise, corners down, teeth set in anger; `her()` turns "joy" into that smirk, a little
  warmer. Hair: dark washes with a jagged outline and `chop()`. Headphones and laces: `gouache`. `figure`: the body
  turned back 9°, the head forward and bowed 13°. By eye: the first hair was a helmet with a frill (`tufts` → `chop`,
  a jagged wash, fewer strands in the fringe), the figure a child in a coat (hoodie shortened to the hips, legs
  longer, sleeves thinner). The first head had the fringe over the whole far half of the face and one eye left — it
  read as an odd boy (the coordinator's remark): redrawn with both eyes open, the fringe lifted to the brow, a
  lighter jaw, a touch of colour on the lips and cheeks, no grey under the eye; open mouths from `parts.mouth` stuck
  out of her profile, so she got her own.
- **Pictures:** `portrait-`, `figure-`, `turn-`, `expr-` for `marat` and `kira`; `cast-six` (all six, 2520 × 880, the
  same scale as `cast`). Repeat: `python3 tools/build.py marat`, `… kira`, `… six`.
- **Weak:** Марат's hair from the front (like a fur hat); Кира's figure (the hoodie is a sack, both hands mostly
  hidden) and her head in profile (the fringe is one wedge over the forehead).

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
