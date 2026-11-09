# Brief for every agent of "Стили персонажей", round three: two more characters, four more styles

Read first: the repository's `CLAUDE.md`, `docs/requirements.md`, [styles.md](styles.md) (the brief of the first
rounds — everything in it holds: why, the approach, the rules of work), the "Drawing styles" part of
`docs/findings.md`, `styles/README.md`. Then your task below: **A** if your style exists (С1–С12), **B** if it is new
(С13–С16).

## The cast is now six

The four as before (`styles.md`): Аня, Савелий Петрович, Тим, Вера. Two new ones, made to differ sharply from the
four in age, build, character and mood:

- **Марат**, about 35, a cook — huge, loud, merry, generous. The biggest in the cast: the tallest and by far the
  widest, a barrel chest, heavy shoulders, thick forearms, big hands, a short neck. Short dark curly hair, a thick
  black beard, thick brows, a broad nose, dark eyes that narrow when he laughs — and he laughs with the whole face and
  body. A white cook's jacket with the sleeves rolled up, a long apron, a towel over the shoulder; a ladle if a prop
  helps. His colours: warm white and terracotta-orange. Mood: open joy, appetite for life. He is the only one in the
  cast whose resting state is a wide smile. (An open mouth needs teeth and a tongue, or it reads as a hole.)
- **Кира**, about 15 — prickly, closed, defiant; vulnerable underneath, and she hides it. Thin and angular, all
  elbows and knees: long thin arms and legs, narrow shoulders, a slouch, the head a little down and the look from
  under the brows, sideways. Short choppy dark hair, a long fringe falling over one eye. A mouth pressed shut or a
  crooked half-smirk; she never smiles openly. An oversized dark hoodie, headphones round the neck, narrow trousers,
  heavy boots. Her colours: dark plum and charcoal with one sharp acid accent (lime-yellow) — the headphones or the
  laces. Mood: «не трогайте меня». A teenager — neither the child Тим nor the young woman Аня: a longer face than a
  child's, the eyes smaller than Аня's, awkward proportions that haven't settled.

Height order, low to high: Тим, Савелий Петрович, Кира (about Аня's height or a little under, but she slouches), Аня,
Вера, Марат. Their descriptions say who they are; how each feature is drawn is decided by your style's rules.

## A. An existing style (С1–С12): add Марат and Кира

Your folder `styles/<folder>/` already has the style's samples (`refs/`), its rules (`entry.json`), the four drawn by
code (`tools/`, `svg/`, `pics/`) and `notes.md` with "how to add a character". No web is needed.

1. Read `entry.json` (the rules and the verdict — it names the style's weak spots), `notes.md`, the code in `tools/`.
   Look at the samples in `refs/` and at every existing picture in `pics/` with your own eyes.
2. Draw Марат and Кира **by this style's rules and with its code**: a module per character beside the four, built on
   the style's shared parts — so that they stand next to the four as their own (the same line, colour, shading, eye,
   proportions logic, paper, format and size of the sheets). For each of the two: a head-and-shoulders portrait and
   the full figure; a turnaround (front, three-quarter, side) and an expression sheet (joy, surprise, sadness, anger)
   for at least one of them each — for both if the style's code gives them without much cost. Plus one new picture of
   **all six together** (a new file; the picture of the four stays).
3. Iterate by eye: render, put each new picture next to the four and next to the samples, look as a person would. Do
   they belong to this cast and this style? Is Марат attractive and warm, not a lump? Is Кира a living teenager, not a
   small Вера or a sad Аня? Redraw what is weak; try several variants of a face and keep the best.
4. **Don't change the four.** Their pictures stay as they are (if you had to touch shared code, re-render and check
   that their pictures didn't change). If the style's code can't do what the new two need, extend it in the style's
   own way.
5. The page (`entry.json`): add the new pictures to the blocks where the four's are (portraits, figures, turnarounds,
   expressions, together) with captions in Russian; `cover` stays. Add to `verdict` two or three honest sentences
   about how the new two came out. `notes.md`: a section on what was done and how to repeat.

## B. A new style (С13–С16): the style and all six

Do the whole job of `styles.md` for your style — samples, the style's rules, the cast drawn in SVG by your code,
the page — in a new folder `styles/<folder>/` (named in your task). Order: first the four (portrait and figure for
each, turnarounds for at least two, an expression sheet for at least one, the four together — the `cover`), then
Марат and Кира the same way (portrait and figure for each; a turnaround and an expression sheet for at least one of
them each) and a picture of all six together. Keep the drawing code in `tools/` reusable (shared parts apart from a
module per character) and say in `notes.md` how to add a character.

Your style must stay unlike the twelve existing ones and the other three new ones (your task names them): look at the
existing styles' covers (`styles/*/pics/cast.*`, С6: `together.jpg`) before you start, and lean on what makes your
style its own.

Samples: search the web and download as `styles.md` says. If this session's network doesn't let you download a
picture, don't trace it from memory and don't fake a sample: say so in `notes.md` and in your report, give the links,
and write the rules from what you could actually look at.

## Rules of work (as in `styles.md`)

- Work ONLY in `styles/<folder>/` and `/home/user/cache/styles-<folder>/` (downloads, scratch). Don't touch anything
  else in the repository — not `styles/index.html`, not `docs/`; no git commit/push/checkout/stash — the orchestrator
  commits. Fifteen other agents work in parallel in the neighbouring folders.
- 4 CPU cores shared by all: keep renders light, one browser at a time, close it when done.
- SVG is written by you or generated by your own scripts — no tracing of the samples, no image-generating models.
- Weak spots known from the first rounds — do better where you can: hands (hidden, mittens, tubes), stiff standing
  poses without a line of action, an even line without pressure. Марат's laugh and big gestures and Кира's slouch are
  a chance for a pose with a line of action.
- Don't show what you yourself find ugly or off-style; if something stays weak after honest tries, show it and say so.

## Final report (your last message)

Short, in Russian, plain words: what was drawn, how it came out (honestly — which pictures are good, which weak),
what didn't work, the files made. Name the two or three best pictures and the weakest one.
