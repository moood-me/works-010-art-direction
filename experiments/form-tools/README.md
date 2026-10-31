# Deformation tools

The form page with four tools added (uses the same `data/` as [../form](../form/)):
- **smoothing in centimetres** — cotangent Laplacian, one solve for the whole body, plus a solve along the normal that
  gives back limb girth; nipples, navel and toes go, limbs don't thin;
- **cage** — a 6×14×5 lattice around the body, presets reshape the whole silhouette (pear, wedge, hourglass, egg,
  column, bean, mass on legs, reed); joints move with it, arms ride with their shoulder;
- **face by points** — about 20 landmarks on Anny's head moved by presets (baby, hero, elf, anime, Pixar, Burton, clay,
  old), the head follows by RBF, fading down the neck;
- **subdivision** — Loop subdivision at display time, after posing; harmless but little gain on Anny's mesh. Remeshing
  would break garment binding and the engine's fixed body mesh, so it wasn't done.
Pictures: [docs/pictures/tools](../../docs/pictures/tools/).
