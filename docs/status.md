# Status — where the work stands (2026-11-12, `main`)

`main` is the catalogue ([history/2026-11-10-catalogue.md](history/2026-11-10-catalogue.md)), published as it is at
`lab.moood.me/works-010-art-direction/` (GitHub Pages serves `main`; a push to `main` is a publication).

## Done, in `main`

- **The drawn styles (`styles/`):** six characters in sixteen styles, С1–С16. History:
  [history/2026-11-09-styles-six-and-sixteen.md](history/2026-11-09-styles-six-and-sixteen.md); findings: "Drawing
  styles, round three" in [findings.md](findings.md); brief: [briefs/styles-more.md](briefs/styles-more.md).
- **Drawings to 3D (`to3d/`):** Р1–Р44 — the twelve of the first rounds and the thirty-two of the third round, two
  more characters in each of the sixteen styles. History:
  [history/2026-11-10-to3d-round-three.md](history/2026-11-10-to3d-round-three.md) (the table of who is where, and
  how the round came into `main`); findings: "Drawings to 3D, round three"; brief: "Third round" in
  [briefs/to3d.md](briefs/to3d.md).

## Known weak, not redone

- Drawings: Кира in С12 (the weakest Кира) and in С8 (reads older than fifteen); Вера in С16 (reads younger than
  forty); bodies of straight pieces in С15; Марат's hair brown and not curly in С15; Аня dark-haired in С13 (red
  elsewhere); no ladle for Марат in С1; samples that didn't download for the new styles (each `notes.md` lists them).
- 3D: Р19 and Р20 (Arcane) and Р14 (Pixar's Кира) are middling — a hard adult face from the realistic base; Р40
  (paper Кира) loses her face in profile under the fringe; Р16 and Р30 (Марат in Klaus and mid-century) have rough
  bodies and aprons. Everywhere: clothes and hair are shells, the drawings' poses and props are mostly not made.
- Р4's viewer (С5, an earlier round) probably stretches the figure when its control panel is open; fixed in Р21 and
  Р22 only.

## Not in `main` yet

The branch `ccr-a7af59de-aubv8d` holds another session's work: four more styles (`styles/s17-bilibin`, `s18-manga`,
`s19-lowpoly`, `s20-soviet`) and their characters in 3D. Its 3D folders are numbered `r13…r20`, the codes Р13–Р20
that the third round holds here: they take the next free codes, from Р45, when they come
(`to3d/items.json`; the folders' names carry the number too).

## Room

The files of `main` are about 735 MB; GitHub Pages publishes a site of up to 1 GB. What comes next has about 265 MB.

## To go on in a new container

Blender 4.5 LTS into `/home/user/cache/blender/` (`download.blender.org/release/Blender4.5/`), the Human Base Meshes
bundle v1.4.1 into `/home/user/cache/n5-heads/hbm/` (`download.blender.org/demo/asset-bundles/human-base-meshes/`),
from pip `libigl`, `shapely`, `scipy`, `scikit-image`. Each character's working files are rebuilt by its `tools/`
into `/home/user/cache/to3d-<folder>/`. The cloud environment `moood-works` lets through package registries, the
sample sites of the new styles and Blender's download sites. Four or five 3D agents at a time; heavy runs through
the shared locks (the end of [briefs/to3d.md](briefs/to3d.md)).
