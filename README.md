# works-010-art-direction

Art direction for moood games — form, character, style.

moood's engine 3 can draw beautiful scenes (works-009-hope ports Claude Design's scenes almost one to one), yet the
games made on it so far look assembled rather than designed. This repository is where we work out how to make them
beautiful: scenes first, then people.

- [gallery/](gallery/index.html) — every path's final pictures on one page: serve the repository (`python3 -m http.server`)
  and open `/gallery/`.
- [docs/](docs/README.md) — the problem, thoughts on scenes, thoughts on people, history.
- [engine/](engine/README.md) — the character engine's foundation: one body description, one skinning, Kimodo motions
  and their retargeting, characters as checked data and the checks; bodies (stage 1): Anny's bodies, deformers, presets
  of parts and full-body presets; its viewer is in the gallery (Д1; bodies Д2–Д4).
- [experiments/](experiments/README.md) — pages we built to try ideas: a mid-shot dialogue in 2D, a code-sculpted
  body with cloth, Anny's bodies from moood, and the page of body styles and simplification.
