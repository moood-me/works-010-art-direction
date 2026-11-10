# 2026-11-10 — the branches put together as a catalogue (branch `catalog`)

**What called for it.** The work had gone four ways that never met: `main` (the broad search: bodies, heads, hair,
clothes, indie and rubber-hose characters), `engine` (those gathered into one engine; Pavel rolled main back from it),
`ccr-a7af59de-aubv8d` (other people's tools, drawn styles, drawings to 3D) and `claude/gallant-knuth-5qo916` (its
continuation: six characters, sixteen styles, a third 3D round stopped half-way). Pavel wants agents who write games
to find here ready ways of making characters — to take and change freely, without reinventing them and without
changing games already made — and to be able to look at all of it himself on the site and talk about it by code
names. His words are in [requirements.md](../requirements.md), "The catalogue". He asked for it head-on: a catalogue,
names, navigation, a place for new variants; no generalising, no library, copied code is fine; nothing new rendered.

**Decided with Pavel.** A new branch from `claude/gallant-knuth-5qo916`; main untouched until he has looked. The
existing codes kept (he left names to me: hundreds of references stand on them, and each has its name beside it).
Smoke tests in a headless browser allowed, without going into bug fixing; what was already broken is not mended.
Of the third 3D round nothing unfinished: its agents were all stopped at work and the orchestrator had written "no
character is finished", so none of its sixteen folders is here — they come when their agents finish
([status.md](../status.md) says how). moood and the engine in real games: not now.

**Decided by me (Claude).**
- Folders stay where they lay (`styles/`, `to3d/`, `tools-demo/`, `experiments/`, `gallery/`): the catalogue is a
  layer over them, so what the third round finishes comes over by a checkout of its folder.
- The engine branch came in by a merge (two conflicts, both menus). Its engine is `engine-full/`; `engine/` stays the
  early engine the twelve Р pages stand on (and the third round's agents still work on). So there are two engines side
  by side, on purpose: nothing was cut out of the late one — taking parts out of it would be the refactoring Pavel
  wants to avoid. Its own paths were repointed (`engine/tools/…` → `engine-full/tools/…` in its code and README).
- Not carried from the engine branch: `engine/check/numbers` — 40 MB of stored numbers its regression check compares
  against; `node engine-full/check/numbers.mjs --update` makes them again. Its stored pictures (16 MB) are kept.
- No pins: an item carries its own code and data; what is shared (`engine/`, `engine-full/`, `experiments/data/`) is
  not changed in place — a new version is a new folder beside.
- One list a section, read by both its site and the catalogue: the gallery's `groups` and `VIEW3D` moved out of
  `gallery/index.html` into `gallery/paths.js`; `ITEMS` of `styles/`, `to3d/`, `tools-demo/` moved into `items.json`
  (`to3d`'s with what its menu adds in brackets, which was `LABEL`).
- Every gallery path says where its code is (`code`), shown on its page with a link to the page itself; the pages the
  gallery had no 3D view of open by that link (`PAGE`: Т2–Т5, О3, Г2, Г4). Two early pages that were in no list are
  listed: И2 (the 2D mid-shot dialogue), И3 (the body sculpted by code). The pages of styles, 3D characters and tools
  say their folder too.
- Nothing of the experiments or the gallery was removed, the dead ends neither (requirements: "keep everything we
  made"); each shows its status. Intermediate versions that the pages and docs already keep (first and second
  versions, sub-variants) stay; I did not go through the history commit by commit looking for lost good states.

**What was done.**
- `index.html` — the catalogue: sections С, Р, П, Т, Г, В, О, Д, Н, И, a card an item (cover, code, name, status,
  code folder), a search, what is shared and where the docs are.
- `README.md` — what is where, the codes, how to take something for a game, how to put something here, what is
  shared; `CLAUDE.md` — the same as rules for agents.
- `docs/requirements.md` — Pavel's words on the catalogue; `docs/reviews/2026-11-09-engine-what-went-wrong.md` — the
  engine agent's account Pavel passed on; `docs/status.md` — what is not here yet and how it comes.

**Checked.** Every page the catalogue links to was opened in a headless browser (Chromium, software WebGL) and
watched for errors and failed requests for a few seconds: the catalogue, the four sites, 25 pages of the gallery's 3D
views (the late engine's thirteen among them), the pages opened by link, the twelve 3D characters' viewers, the early
engine's viewer — 49 in all, none with an error. One heavy view of the late engine was left for 50 s and came up. The
viewers were not played through, and nothing was compared by eye with how it looked before beyond the pages opening.

**How, to repeat it.** `git checkout -b catalog origin/claude/gallant-knuth-5qo916`; `git merge origin/engine`
(the root page ours, the gallery's menu both); `git mv engine engine-full`, `git checkout <gallant> -- engine`; then
the lists and the pages as above. To look: `python3 -m http.server` at the repository's root.
