# Status — where the work stands (2026-11-10, branch `claude/gallant-knuth-5qo916`)

Everything below is in this branch, which starts from `ccr-a7af59de-aubv8d` (itself not merged into main; main has
gone 66 commits on since they parted and conflicts with it in `index.html` and `gallery/index.html`). Nothing here
is merged anywhere. Update or remove this file when the work moves on.

## Done

- **The drawn styles (`styles/`):** six characters in sixteen styles. History:
  [history/2026-11-09-styles-six-and-sixteen.md](history/2026-11-09-styles-six-and-sixteen.md); findings: "Drawing
  styles, round three" in [findings.md](findings.md); brief: [briefs/styles-more.md](briefs/styles-more.md).
- **Drawings to 3D (`to3d/`):** two more characters in each of the sixteen styles, Р13–Р44, all finished, looked at
  by the orchestrator and shown to Pavel. History:
  [history/2026-11-10-to3d-round-three.md](history/2026-11-10-to3d-round-three.md) (the table of who is where);
  findings: "Drawings to 3D, round three"; brief: "Third round" in [briefs/to3d.md](briefs/to3d.md).
- Both sites open and every page loads its pictures and films (`python3 -m http.server`, `/styles/`, `/to3d/`).
  The browser viewers («3D» tabs) were opened by the agents in headless Chromium, not by the orchestrator.

## Known weak, not redone

- Drawings: Кира in С12 (the weakest Кира) and in С8 (reads older than fifteen); Вера in С16 (reads younger than
  forty); bodies of straight pieces in С15; Марат's hair brown and not curly in С15; Аня dark-haired in С13 (red
  elsewhere); no ladle for Марат in С1; samples that didn't download for the new styles (each `notes.md` lists them).
- 3D: Р19 and Р20 (Arcane) and Р14 (Pixar's Кира) are middling — a hard adult face from the realistic base; Р40
  (paper Кира) loses her face in profile under the fringe; Р16 and Р30 (Марат in Klaus and mid-century) have rough
  bodies and aprons. Everywhere: clothes and hair are shells, the drawings' poses and props are mostly not made.
- Р4's viewer (С5, an earlier round) probably stretches the figure when its control panel is open; fixed in Р21 and
  Р22 only.

## Not decided

Nothing is waiting to run. Not asked for and not done: merging this branch or `ccr-a7af59de-aubv8d` into main; the
other four characters of each style in 3D; redoing the weak ones above.

## To go on in a new container

Blender 4.5 LTS into `/home/user/cache/blender/` (`download.blender.org/release/Blender4.5/`), the Human Base Meshes
bundle v1.4.1 into `/home/user/cache/n5-heads/hbm/` (`download.blender.org/demo/asset-bundles/human-base-meshes/`),
from pip `libigl`, `shapely`, `scipy`, `scikit-image`. Each character's working files are rebuilt by its `tools/`
into `/home/user/cache/to3d-<folder>/`. The cloud environment `moood-works` lets through package registries, the
sample sites of the new styles and Blender's download sites. Four or five 3D agents at a time; heavy runs through
the shared locks.
