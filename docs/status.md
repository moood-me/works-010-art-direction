# Status — where the work stands (2026-11-10, branch `catalog`)

`catalog` is the catalogue put together from `claude/gallant-knuth-5qo916` and `engine`
([history/2026-11-10-catalogue.md](history/2026-11-10-catalogue.md)). The drawn styles below are all in it. The third
round of drawings to 3D is not: its agents were stopped half-way and go on in `claude/gallant-knuth-5qo916`, where
this file's tables were written on 2026-11-09 (kept below as the list of what is still to come).

## A finished character of the third round comes here so

When its agent has finished it and the orchestrator has looked at it, in `catalog`:

```
git fetch origin claude/gallant-knuth-5qo916
git checkout origin/claude/gallant-knuth-5qo916 -- to3d/<folder>
```

and a line `["Р<number>", "<folder>", "С<style> <name>"]` in `to3d/items.json`; a look at its page (`/to3d/#Р<number>`);
a note in the history. Nothing else has to change: the folders lie where they lay there.

## Done: the drawn styles (`styles/`)

Six characters in sixteen styles; the site opens without errors (`python3 -m http.server`, `/styles/`). History:
[history/2026-11-09-styles-six-and-sixteen.md](history/2026-11-09-styles-six-and-sixteen.md); findings: "Drawing
styles, round three" in [findings.md](findings.md); the brief: [briefs/styles-more.md](briefs/styles-more.md).
- Марат and Кира added to С1–С12; four new styles С13 woodblock print, С14 cut paper, С15 noir, С16 pixel art with
  all six.
- Known weak, not redone: Кира in С12 (the weakest Кира) and in С8 (reads older than fifteen); Вера in С16 (reads
  younger than forty); bodies of straight pieces in С15; Марат's hair brown and not curly in С15; Аня dark-haired in
  С13 (red elsewhere); no ladle for Марат in С1; samples that didn't download for the new styles (each `notes.md`
  lists them).

## Paused, in `claude/gallant-knuth-5qo916`: two more characters in 3D in each style (`to3d/`)

Asked by Pavel: in every style whose six are drawn — one of the three old characters not yet in 3D there and one of
the new two; later he confirmed the same for the four new styles (two each). Brief: "Third round" at the end of
[briefs/to3d.md](briefs/to3d.md). Who is made where was chosen by the orchestrator: the old characters spread
evenly, the new one being whoever came out better in that style's drawings. The site's list (`to3d/index.html`)
already names Р13–Р44; folders that don't exist yet show as missing there.

One agent per style makes both characters, one after the other. Eight styles were started; the container was
restarted twice (the second time with eight 3D agents at load 20 on 4 cores), then Pavel asked to stop them all.
**No character is finished, and the orchestrator has not looked at any of these pictures yet** — the statuses in the
`entry.json` files are the agents' own, unchecked.

| Style | Р | Character | Folder | Stage when stopped |
|---|---|---|---|---|
| С1 | Р13 | Вера | `r13-s1-vera` | begun: code and viewer, 4 comparison pictures; no page, no notes |
| С1 | Р14 | Кира | `r14-s1-kira` | not started |
| С2 | Р15 | Савелий | `r15-s2-savely` | page, notes, 14 pictures, 4 films, viewer — near done |
| С2 | Р16 | Марат | `r16-s2-marat` | not started |
| С3 | Р17 | Тим | `r17-s3-tim` | page, notes, 14 pictures, 9 films, viewer — near done |
| С3 | Р18 | Кира | `r18-s3-kira` | page, notes, 14 pictures, viewer; 8 films named on the page are not rendered (hair was being reworked) |
| С5 | Р21 | Тим | `r21-s5-tim` | page, notes, 17 pictures, viewer; 3 of 6 films not rendered |
| С5 | Р22 | Кира | `r22-s5-kira` | just begun: notes and code, no pictures |
| С9 | Р29 | Аня | `r29-s9-anya` | page, notes, 7 pictures; 4 of 7 films not rendered; no browser viewer |
| С9 | Р30 | Марат | `r30-s9-marat` | begun: code and model, 2 pictures; no page |
| С10 | Р31 | Вера | `r31-s10-vera` | begun: code and viewer; no pictures, no page |
| С10 | Р32 | Марат | `r32-s10-marat` | not started |
| С11 | Р33 | Аня | `r33-s11-anya` | notes, 6 pictures, 8 films, viewer; no page yet |
| С11 | Р34 | Марат | `r34-s11-marat` | notes, 6 pictures, 5 films, viewer; no page yet |
| С12 | Р35 | Тим | `r35-s12-tim` | page, notes, 8 pictures, 4 films, viewer; 1 film not rendered |
| С12 | Р36 | Марат | `r36-s12-marat` | begun: code and viewer; no pictures, no page |

Not started at all (planned, waiting for Pavel's word):

| Style | Characters |
|---|---|
| С4 Arcane | Р19 Савелий, Р20 Кира |
| С6 symbolic | Р23 Вера, Р24 Кира |
| С7 Ghibli | Р25 Вера, Р26 Кира |
| С8 stop-motion | Р27 Савелий, Р28 Марат |
| С13 woodblock print | Р37 Аня, Р38 Марат |
| С14 cut paper | Р39 Вера, Р40 Марат |
| С15 noir | Р41 Савелий, Р42 Кира |
| С16 pixel art | Р43 Тим, Р44 Кира |

## To go on

- An agent's memory doesn't outlive its session: a new agent continues a folder from its files — the folder's
  `notes.md` and `tools/`, the brief, and the row above. In the session that started them the seven agents (all but
  С5's) can be resumed by message.
- Outside the repository, needed again in a new container: Blender 4.5 LTS in `/home/user/cache/blender/`
  (`download.blender.org/release/Blender4.5/`), the Human Base Meshes bundle v1.4.1 in
  `/home/user/cache/n5-heads/hbm/` (`download.blender.org/demo/asset-bundles/human-base-meshes/`), from pip:
  `libigl`, `shapely`, `scipy`, `scikit-image`. Each character's working files are in
  `/home/user/cache/to3d-<folder>/` and are rebuilt by its `tools/`.
- The cloud environment `moood-works` lets through package registries, the sample sites of the new styles and
  Blender's download sites; nothing else.
- Fewer agents at once: eight 3D agents overloaded 4 cores. The brief now makes heavy runs (Blender, films) take
  turns through three shared locks; three or four 3D agents at a time is a safer number.
- When a character is finished: the orchestrator looks at every picture and film, sends the weak back once, shows
  Pavel the cover and a couple of sheets, commits. Then a history note for the 3D round and what it found in
  `findings.md`.
