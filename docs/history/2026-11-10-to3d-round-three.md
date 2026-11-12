# 2026-11-10 — drawings to 3D, round three: two more characters in every style (branch `claude/gallant-knuth-5qo916`)

**What called for it.** After the six characters were drawn in sixteen styles
([2026-11-09](2026-11-09-styles-six-and-sixteen.md)), Pavel asked for two more characters in 3D in each style whose
six were ready: one of the three old characters not yet in 3D there and one of the new two — and, when asked, the
same for the four new styles, which had no character in 3D at all.

**What was done.** Thirty-two characters, `to3d/` Р13–Р44, two per style, each with its page (the drawing and the 3D
side by side and overlaid, steps, a turn, Kimodo motions through the engine, a live face, a browser viewer as the
«3D» tab), `notes.md` and `tools/`; the site's list names each by style and character.

| Style | Was in 3D | Added |
|---|---|---|
| С1 Pixar | Тим | Р13 Вера, Р14 Кира |
| С2 Klaus | Аня | Р15 Савелий, Р16 Марат |
| С3 graphic flat | Аня | Р17 Тим, Р18 Кира |
| С4 Arcane | Вера | Р19 Савелий, Р20 Кира |
| С5 indie | Вера | Р21 Тим, Р22 Кира |
| С6 symbolic | Савелий | Р23 Вера, Р24 Кира |
| С7 Ghibli | Аня | Р25 Вера, Р26 Кира |
| С8 stop-motion | Тим | Р27 Савелий, Р28 Марат |
| С9 mid-century | Тим | Р29 Аня, Р30 Марат |
| С10 ligne claire | Савелий | Р31 Вера, Р32 Марат |
| С11 rubber hose | Савелий | Р33 Аня, Р34 Марат |
| С12 pen and watercolour | Аня | Р35 Тим, Р36 Марат |
| С13 woodblock print | — | Р37 Аня, Р38 Марат |
| С14 cut paper | — | Р39 Вера, Р40 Кира |
| С15 noir | — | Р41 Савелий, Р42 Тим |
| С16 pixel art | — | Р43 Тим, Р44 Аня |

**Who decided what.** In С1–С12 the orchestrator (Claude) chose who is made: the old characters spread evenly, the
new one being whoever came out better in that style's drawings. In the four new styles the first character was the
orchestrator's choice, one different old character per style; the second was drawn by lot from the six at Pavel's
word — first freely (it gave Аня three times), then again, at his word, without repeats and without the style's
first: Марат, Кира, Тим, Аня. Statuses on the pages are the agents' own except Р19 and Р20, set to «mid» by the
orchestrator after looking (the agent had «good»).

**How, to repeat it.** The brief is the "Third round" part of `docs/briefs/to3d.md`: one agent per style makes both
characters one after the other, starting from the character of that style already in 3D (its `notes.md` and code);
in a new style, from the characters whose way of making the look is nearest. Each works only in its two folders and
caches. The orchestrator looked at the comparison pictures and at frames of films of every character, showed Pavel
two pictures and two films per style, committed per style, and sent С4 back once.
- Outside the repository: Blender 4.5 LTS and the Human Base Meshes bundle from `download.blender.org` into
  `/home/user/cache/` (Blender's sites were added to the environment `moood-works`); `libigl`, `shapely`, `scipy`,
  `scikit-image` from pip. Several agents installed three.js from npm into their cache for headless shots; some
  viewers still load three.js from a CDN, as the earlier ones do.
- Eight 3D agents at once overloaded the 4 cores (load 20) and the container restarted; after that heavy runs
  (Blender, films) went through three shared file locks (`flock /home/user/cache/heavy.N.lock …`) and four or five
  agents ran at a time. One agent noticed a run queued on a busy lock while another was free — choose a free lock
  first.
- The work was cut several times (container restarts, the account's usage limits, a pause at Pavel's word). Files
  survived every time because work in progress was committed often; agents were resumed by message and went on from
  their files. One agent could not be resumed and a new one finished its two characters from the folder alone.

**Seen.** In `docs/findings.md`, "Drawings to 3D, round three".

**Into main (2026-11-12).** `main` had become the catalogue on 2026-11-10, put together from this branch as it stood
on the evening of 2026-11-09: the drawn styles came, the third round's folders did not, because none was finished
then. Pavel asked for the finished round to be put into `main` rightly and at once, without showing him first.
- Not a merge of the branches: tried dry (`git merge-tree`), it gives 113 conflicts — the half-made folders were
  taken out of `main` and finished here. Done the way `docs/status.md` in `main` said: a branch from `main`;
  `git checkout claude/gallant-knuth-5qo916 -- to3d/r13-… … to3d/r44-…` (thirty-two folders as they are), this note
  and `docs/findings.md` the same way (neither had changed in `main`); thirty-two lines in `to3d/items.json`
  (the code, the folder, what the menu adds in brackets); `docs/status.md` written anew. Then `main` fast-forwarded.
- Nothing else in `main` was touched; the folders stand on the early `engine/`, which `main` keeps for the Р pages.
- Checked before the push, served from a folder above the repository so that paths are as on
  `lab.moood.me/works-010-art-direction/`: the catalogue (shows Р13–Р44), the 3D site, each of the thirty-two pages
  and each of their thirty-two viewers opened in headless Chromium — no failed request and no error on the pages;
  every viewer came up with its character (a screenshot of each was looked at). The viewers load three.js from
  jsDelivr, as the twelve earlier ones do; this container's network doesn't let that host through, so for the check
  the same version (0.160.0, from npm) was served in its place. On the published site they were not opened.
- Codes: another session's work in `ccr-a7af59de-aubv8d` (styles С17–С20 and their 3D) had numbered its 3D folders
  `r13…r20` meanwhile. Pavel decided: the third round keeps Р13–Р44; those take the next codes when they come.
- Size: `main`'s files grew from 546 MB to about 735 MB (GitHub Pages publishes up to 1 GB).
