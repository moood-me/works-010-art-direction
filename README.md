# works-010-art-direction

Beautiful characters for moood's games: every way of making one that was tried here — drawn or in 3D — and the parts
for it (bodies, heads, hair, clothes), kept as a catalogue. An agent making a game looks through it, takes a way that
suits the game, and makes its own characters by it.

## Looking at it

Serve the repository and open its root:

```
python3 -m http.server
```

The root page is the catalogue: every item by its code, with its picture, how it came out, and the folder its code is
in; a search over all of it. An item opens on its own page, with its pictures and, where it has one, its 3D view.

## Codes

Every item has a code to talk by — a section's letter and a number (`Т5`, `С9`, `Р3`); a picture on its page is the
code, a hyphen and a letter (`Т5-б`). The letters are Russian.

| Letter | What | Where it lives | Its list |
|---|---|---|---|
| С | a drawn style: samples, its rules, the cast drawn by them in SVG | `styles/<folder>/` | `styles/items.json` |
| Р | a drawn character built in 3D, moving and with a live face | `to3d/<folder>/` | `to3d/items.json` |
| П | characters not from Anny: indie heroes, rubber-hose | `experiments/indie`, `experiments/toon` | `gallery/paths.js` |
| Т | bodies: Anny's own settings, deformations on top | `experiments/…` | `gallery/paths.js` |
| Г | heads | `experiments/…` | `gallery/paths.js` |
| В | hair | `experiments/hair` | `gallery/paths.js` |
| О | clothes: a designed form, real cloth | `experiments/…` | `gallery/paths.js` |
| Д | the late engine: bodies, heads, hair and clothes in one viewer | `engine-full/` | `gallery/paths.js` |
| Н | other people's open tools beside ours | `tools-demo/<folder>/` | `tools-demo/items.json` |
| И | where it began, and the earliest tries | `docs/pictures/hope`, `experiments/…` | `gallery/paths.js` |

An item's page says which folder its code is in. That folder has what is needed to run it and, in its `notes.md` or
`README.md`, what was done, how to repeat it, and what is weak.

## Taking something for a game

- **Take the way, not the character.** The characters on the pages are examples of what a way gives. A game makes its
  own by that way; if it starts from one of these, it changes at least how the character looks.
- **Copy, don't link.** Copy the folder (and what it uses of the shared ones, below) into the game's own repository
  and change it there freely. Nothing here changes under a game that took a copy, and nothing a game does changes what
  is here.
- Parts are not made to fit each other. Where someone did fit several together, that is an item of its own (the Р
  pages are such: a body, a head, a drawn face, clothes, a look, motion).

## Putting something here

What turned out well in a game or an experiment comes here as a new item, so the next agents find it.

1. **A new folder beside the others**, never over one: `styles/s17-…`, `to3d/r45-…`, `tools-demo/n9-…`,
   `experiments/<name>/`. A better version of something that is here is a new folder too — copy the old one and change
   the copy; copied code is fine.
2. **The next free code** of its letter, and **one line in that section's list** (the table above). The catalogue and
   the section's site read the list; nothing else has to be told.
3. **In the folder**: the page's `entry.json` (styles, to3d, tools-demo: the format is in `styles/README.md` and
   `tools-demo/README.md`) or its entry in `gallery/paths.js`; its pictures; its code; `notes.md` — what was done and
   why, how to repeat it, how to make one's own by it, what is weak, said honestly; what it grew from, by code.
4. **It runs from the repository's root** served as above, by paths relative to its own folder.
5. **Only what is finished** comes here: what is still being made stays in its author's branch. A result that was
   good and then grew into something worse is kept beside what it grew into.
6. A note in `docs/history/` (CLAUDE.md).

## What is shared

Some folders serve several items. They are not changed in place — a page that stands on one would change with it; a
new version is a new folder beside the old (as `engine-full/` is beside `engine/`).

- `engine/` — the early engine: a body, the SOMA skeleton, Kimodo's motions carried onto a body, skinning. The Р pages
  stand on it. `engine/motions/` — Kimodo's motions in its format.
- `engine-full/` — the late engine, whole (Д1–Д13): its own bodies, presets, motions and chains of motions. Its cloth is
  weaker than О3's; what went wrong with it as an engine is in `docs/reviews/`.
- `experiments/data/` — Anny's bodies and garments as moood bakes them; `experiments/motions-raw/` — Kimodo's motions
  for the cloth and indie pages.

## Docs

[docs/](docs/README.md): the problem, what Pavel said matters (`requirements.md`), what the rounds found
(`findings.md`), the briefs the page agents worked from (`briefs/`), reviews of the engine, the history.

## Branches

`main` is this catalogue (made in the branch `catalog`, merged on 2026-11-10). It was put together from `claude/gallant-knuth-5qo916` (styles, drawings to 3D, tools;
it contains `main` and `ccr-a7af59de-aubv8d`) and `engine` (the late engine); those stay as they were. The third round
of drawings to 3D is still being made in `claude/gallant-knuth-5qo916` — `docs/status.md` says how its finished
characters come here.
