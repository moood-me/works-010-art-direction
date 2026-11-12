# Status — where the work stands (2026-11-12, `main`)

`main` is the catalogue ([history/2026-11-10-catalogue.md](history/2026-11-10-catalogue.md)), published as it is at
`lab.moood.me/works-010-art-direction/` (GitHub Pages serves `main`; a push to `main` is a publication).

## Done, in `main`

- **The drawn styles (`styles/`):** six characters in twenty styles, С1–С20 (С17–С20: Bilibin and Art Nouveau,
  black-and-white manga, low-poly, Soviet animation — [history/2026-11-12-styles-17-20-and-3d-45-50.md](history/2026-11-12-styles-17-20-and-3d-45-50.md)). History:
  [history/2026-11-09-styles-six-and-sixteen.md](history/2026-11-09-styles-six-and-sixteen.md); findings: "Drawing
  styles, round three" in [findings.md](findings.md); brief: [briefs/styles-more.md](briefs/styles-more.md).
- **Drawings to 3D (`to3d/`):** Р1–Р50 — the twelve of the first rounds, the thirty-two of the third round (two
  more characters in each of the sixteen styles) and Р45–Р50, one character of each of С15–С20
  ([history/2026-11-12-styles-17-20-and-3d-45-50.md](history/2026-11-12-styles-17-20-and-3d-45-50.md)). History:
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
- С17–С20: С18 manga is the weakest style (wooden bodies, simple faces); stiff standing poses and plain hands in all
  four. 3D Р45–Р50: profiles where the drawings' front and side disagree (Р45, Р50), the skirt as a shell in a wide
  step (Р47), the body wider than the drawing (Р47, Р48), Kimodo's wave bringing a short arm to a big head (Р49).
- Р4's viewer (С5, an earlier round) probably stretches the figure when its control panel is open; fixed in Р21 and
  Р22 only.

## Room

The files of `main` are about 810 MB; GitHub Pages publishes a site of up to 1 GB. What comes next has about 190 MB.

## To go on in a new container

Blender 4.5 LTS into `/home/user/cache/blender/` (`download.blender.org/release/Blender4.5/`), the Human Base Meshes
bundle v1.4.1 into `/home/user/cache/n5-heads/hbm/` (`download.blender.org/demo/asset-bundles/human-base-meshes/`),
from pip `libigl`, `shapely`, `scipy`, `scikit-image`. Each character's working files are rebuilt by its `tools/`
into `/home/user/cache/to3d-<folder>/`. The cloud environment `moood-works` lets through package registries, the
sample sites of the new styles and Blender's download sites. Four or five 3D agents at a time; heavy runs through
the shared locks (the end of [briefs/to3d.md](briefs/to3d.md)).
