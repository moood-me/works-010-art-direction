# Anny's own shape space

Anny's model run locally (Python, from github.com/naver/anny) to see what her phenotype sliders and ~1250 local targets
made by people can sculpt by themselves.

- `gen.py` — bodies from descriptions (sliders, targets, a head of another age);
- `fit.py` — fits Anny's sliders to moood's woman (surface error 2.7 mm mean, 7 mm p95);
- `tomoood2.py` — carries a form onto moood's mesh as a change: moood's woman + (new Anny − fitted Anny), smoothed;
- `index.html`, `shot.js` — the viewer and its shots. Generated meshes (`out/`, `*.npy`, `map.npz`) are not kept.

Found: proportions made by people hold to about ±1.5…2; a child's or toddler's head, scaled 1.2–1.4, on an adult body
gives cartoon, doll-like proportions with a whole head and no neck seam. Not given: a simplified or cartoon surface, a
cute face; beyond ±2 it breaks. In Anny `gender = 1` is female. Exact transfer of targets to moood's mesh needs the
baking (`bake.py` in people-tools). Pictures: [docs/pictures/anny-space](../../docs/pictures/anny-space/).
