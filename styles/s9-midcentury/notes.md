# С9 — Середина века: гуашь и формы

## What was done

1. **Samples.** Searched for character art of mid-century illustration and animation design: Mary Blair (Golden Book
   "I Can Fly", concept art for Peter Pan and "It's a Small World"), Alice and Martin Provensen, Miroslav Šašek ("This
   is London"), Jim Flora, the "101 Dalmatians" model sheets, sketches of the three fairies of "Sleeping Beauty".
   Looked at about 60 downloads, kept twelve in `refs/` (≤ 800 px, jpg). Most useful for faces: `01`–`04` (Blair:
   features low and tiny, round blush, closed-lash eyes, red mouths), `06` (Provensen children), `07`–`09` (Šašek
   adults: long heads, big noses, ink line on part of a contour). Eyvind Earle's Sleeping Beauty work is backgrounds;
   for its characters only line sketches (`12`) were found.
2. **Rules** — in `entry.json` (block «Правила стиля»), each one from what is seen in the samples.
3. **Drawing.** Every picture is SVG written by the Python scripts in `tools/` (hand-placed points, no tracing, no image
   models). Rendered with headless Chrome; the page shows WebP (q 90) because the paper grain makes PNGs 1–2 MB each.
4. **By eye**, rendered and redrawn many times. What changed on the way: the first gouache filter was far too strong
   (white streaks over everything, dark speckle like sand) — the mottle became a soft-light blend and the speckle was
   thinned; the backdrop got its own milder texture (`board`) because big fields looked like water; Anya's eyes grew
   (tiny features read as empty faces), she got a white-almond "upward look" and painted lips; necks were too long
   (the bust moved up per character, `BUST_DY`); the head's own neck is now off in full figures (`neck=False`) because
   it lay over the shirt; Savely's figure went from a block on long legs to a bean with a round back bent over the
   watch; Tim's arms were redrawn so the near arm swings back instead of crossing his chest; anger looked sly until
   the `glare` eye (lid slanting down to the nose); a partial ink line on the jaw (`edge`) gave the faces Šašek's line.

## How to repeat

```
cd styles/s9-midcentury
python3 tools/build.py            # all pictures → svg/*.svg and pics/*.webp (headless google-chrome, ~35 s)
python3 tools/build.py portrait   # only names that contain "portrait"
```

Scratch PNGs go to `/home/user/cache/styles-s9-midcentury/render/` (or `$S9_SCRATCH`). Needs Python 3 with Pillow.

## The code (`tools/`)

- `kit.py` — the medium, shared by everyone. `shape(pts, fill)` a flat gouache shape (Catmull-Rom through points;
  a point `(x, y, 'c')` is a sharp corner); `brush(pts, w, color)` a tapered brush line; `limb(pts, widths, fill)` a
  tube with a width at each point (arms, legs); `edge(pts, i0, i1)` part of a contour in ink, offset like a misprint;
  `blush`, `dryb` (dry-brush strokes inside a mass), `pattern_dots`, `stripes`; `g(items, transform, filter)`.
  Filters: `gouache` (displaced edge, soft-light mottle, sparse dark specks), `board` (milder, for big fields),
  `paper` (grain over the whole picture). `Doc(w, h)` collects the SVG; `render()` runs Chrome.
- `face.py` — features in the style: `eye(kind=open|look|dot|closed|happy|wide|sad|lid|glare|cross)`, `brow`,
  `mouth(kind=lips|soft|smile|smirk|flat|frown|o|grin|sad|shout)`, and `EXPR` — the four expressions and calm.
- `scenery.py` — backdrops (`BACK`: field colour, ground, motif per character), motifs (daisy, clock, sun, leaf),
  `town()` — a Provensen street.
- `anya.py`, `savely.py`, `tim.py`, `vera.py` — one module per character, all with the same interface:
  colours at the top; `OWN` — the character's overrides of `EXPR`; `head(view, expr, neck=True)` (head around (0, 0),
  crown near y=−120, chin near y=95; Anya and Tim have `front`, `34`, `side`, the others `34`); `bust(view)` (drawn
  over the head, shifted by `BUST_DY`); `figure(expr)` (feet at (0, 0), draws the head itself, scaled 0.5–0.6);
  `FIG_SCALE` — how much larger the figure is drawn on its own page.
- `build.py` — composes the pages: `portrait`, `figure`, `turnaround`, `expressions`, `cast`, the three rule pictures.

## How to add a new character

1. Copy the shortest module (`vera.py` or `savely.py`) to `tools/<name>.py`; set its colours (two or three bold
   paints plus skin), `OWN`, `BUST_DY`, `FIG_SCALE`.
2. Draw `head('34')` in this order: hair behind the head, neck (`if neck:`), face shape (then `edge` along the jaw),
   ear, blush, eyes and brows from `face.py` (near eye larger, far eye `squash≈0.65`), nose, mouth, front hair. Keep
   features small and below the middle of the face; put one telling prop on the head or in the hands.
3. `bust()` — shoulders as one big shape, one pattern or one contrasting collar. `figure()` — legs with `limb`, the
   body as one or two shapes, arms with `limb`, then the head with `neck=False`.
4. Add a backdrop entry in `scenery.BACK` and the module to `CAST` in `build.py`; run `python3 tools/build.py <name>`
   and look at the pictures next to the samples in `refs/`.

## Round three: Марат and Кира

Asked for by `docs/briefs/styles-more.md` (part A): two more characters in this style, drawn with its code, the four
untouched.

**What was done.** Two modules beside the four, same interface: `tools/marat.py`, `tools/kira.py` (each has `front`,
`34`, `side` heads, so both got a turnaround and an expression sheet). New pictures: `portrait-`, `figure-`, `turn-`,
`expr-` for `marat` and `kira`, and `cast-six` (all six on the street of `cast`; the picture of the four stays the
cover). Each got a backdrop in `scenery.BACK` (Марат — olive with lemons, Кира — lilac with four-point "atomic" stars).

**How each is built.**
- Марат: the beard is one dark shape from ear to ear with the mouth drawn on top of it and the moustache on top of the
  mouth; curls are round dabs along a line (`_curls`), on the crown, the forehead and the bottom of the beard; thick
  block brows; a broad nose a little ruddier than the skin. His calm face is already a smile (`beam`: a white crescent
  of teeth), joy is `laugh` (open mouth, upper teeth, tongue). Figure: a white barrel on short legs, the apron wraps
  the belly, shoulders lean back, the ladle is raised, the other fist on the hip. `FIG_SCALE` is 0.88 — at 1.0 the
  ladle leaves the sheet; his real size shows in `cast-six`.
- Кира: a narrower, longer face than Tim's with a small chin; the eye is the `look` almond at a small size, heavy lid,
  no lash flick, the iris slid sideways (`gaze`); brows thick, low, inner end down; a muted mouth colour. The fringe
  is one shape with ragged points over the far eye; in `34` the nose tip is drawn after the fringe. `head('34')` and
  `head('side')` are already tipped 6° down. She never smiles openly: her `joy` is `smirk` with softer lids. Figure:
  a dark bean of a hoodie (round back, hips forward), thin legs with knees, heavy boots with lime laces, one hand in
  the pocket, the other out of a sleeve that is too long.

**What the shared code got** (the four don't use any of it, their SVG is byte-for-byte the same — checked):
- `kit.hand(x, y, s, rot, fill, line, kind=open|fist|curl, side)` — a hand of a palm, a thumb and fingers or knuckle
  lines, instead of the oval mitten.
- `kit.limb(..., cap='round')` — ends rounded outward. The old `cap=True` cuts a half-circle *into* each end (unseen
  on the four: their limb ends sit under hands and sleeves); it is left as it was so their pictures don't change.
  Sharp bends in a wide `limb` fold the inner edge over itself and leave holes: draw a thick arm as two straight
  limbs (upper arm, forearm).
- `face.mouth(kind='beam'|'laugh')`.
- `scenery`: motifs `lemon`, `star`.
- `build.py`: `cast_six()`; the two are in `CAST`.

**How to repeat.** `python3 tools/build.py marat`, `python3 tools/build.py kira`, `python3 tools/build.py cast-six`
(the filter is a part of the file name; running these doesn't rewrite the four's files). To check the four after
touching shared code: build each of their pages in Python and compare `Doc.svg()` with the file in `svg/`.

**Tried and changed by eye.** Марат's nose first sat over the far eye and was clown-pink — moved lower, paler; the
jacket covered his mouth — the bust went down (`BUST_DY = 14`) so the beard lies on the collar; the apron was a slab
to the ankles — shortened to the knees and narrowed down. Кира's far arm first reached up to the headphones and read
as a wing — now it hangs; the fringe hid the nose — the tip comes out under it.

**Honest state.** Good: Марат's portrait and laugh, `cast-six`, Кира's silhouette and her expression sheet. Weak:
Кира's nose tip in three-quarter (reads uncertainly next to the fringe), her legs are straight like stilts; Марат's
profile (the neck shows behind the beard, the head is simpler than the other views); busts are still domes.

## Honest state

In mood and medium close (board, flat gouache, blush, tiny features, one bold palette each). Weaker than the samples
in drawing: poses are upright and still, shapes are cleaner and more even than real gouache, no living ink line or
dry brush with paper showing through, little of the pattern and small graphics of Provensen and Šašek. Anya's side
view and the side bust are simpler than the other views. Hands are mittens.

## Sources (third-party pictures, kept only as references)

- `refs/01-blair-icanfly-swing.jpg`, `02-blair-icanfly-cow.jpg`, `03-blair-icanfly-cats.jpg` — Mary Blair, "I Can
  Fly" (Ruth Krauss, Little Golden Book), via The Marginalian,
  https://www.themarginalian.org/2014/04/17/i-can-fly-ruth-krauss-mary-blair/ (`icanfly_kraussblair1/5/3.jpg`)
- `refs/04-blair-mermaids.jpg` — Mary Blair, concept art for Peter Pan, Illustration History,
  https://illustrationhistory.org/artists/mary-blair (`Mary3.jpg`)
- `refs/05-blair-smallworld-arctic.jpg` — Mary Blair, "It's a Small World" concept (Heritage Auctions image), via
  Bleeding Cool, https://bleedingcool.com/comics/its-a-small-world-with-these-mary-blair-concept-paintings (`sw1.jpeg`)
- `refs/06-provensen-children.jpg` — Alice and Martin Provensen, collage on Fishink,
  https://fishinkblog.com/2010/10/25/alice-and-martin-provensen-vintage-childrens-illustration
- `refs/07-sasek-pub.jpg`, `08-sasek-tube.jpg`, `09-sasek-queue.jpg` — Miroslav Šašek, "This is London" (1959), via
  Age of Uncertainty, https://ageofuncertainty.blogspot.com/2013/01/saseks-london.html (`sasek-london-06/09/03.jpg`)
- `refs/10-flora-smoked.jpg` — Jim Flora, via Flashbak, https://flashbak.com/jim-flora-mesmeric-album-covers-282607/
  (`James-Flora-smokers.jpg`)
- `refs/11-dalmatians-anita-sheet.jpg` — "101 Dalmatians" (1961), stat model sheet of Anita, Choice Fine Art,
  https://choicecollect.com/collections/disney-model-sheets/products/101-dalmatians-original-stat-model-sheet-anita
- `refs/12-sleeping-beauty-fairies.jpg` — "Sleeping Beauty" (1959), sketches for the three good fairies, Andreas Deja's
  blog, https://andreasdeja.blogspot.com/2018/01/designs-for-three-good-fairies.html

Downloads and scratch renders: `/home/user/cache/styles-s9-midcentury/`.
