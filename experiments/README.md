# Experiments

Each folder is a page that opens in a browser (serve the folder, e.g. `python3 -m http.server`, and open
`index.html`). three.js is loaded from jsDelivr.

- **[midshot/](midshot/)** — two dialogue scenes at mid-shot, drawn in 2D canvas, not on moood's engine: a kitchen at
  2 a.m. (mother and grown daughter), a bus stop in the first snow (grandfather and grandson). How people could be
  drawn in a mid-shot. Bodies and motion were the weak part. `frames/` holds stills.
- **[body/](body/)** — one body sculpted by code (signed distance fields), skinned, with a cloth skirt (Verlet) and a
  braid; stand, walk, sit, wave, spin; soft, toon and silhouette views. Rated 4/10 by its maker: proportions and cloth
  alive, but shoulders, arms, torso and legs not human. Led to taking Anny.
- **[anny/](anny/)** — Anny's bodies and garments as moood bakes them (`engines/1/bodies/`, converted to base64 JS
  modules in `data/`), with the 77 joints.
- **[form/](form/)** — body styles and simplification on Anny: genres, characters, shape language, proportions, masses,
  gesture, caricature, the silhouette as one form, the sign. Test tools: `one.js` and `rr.js` render states to
  pictures with Playwright (they expect the page on port 8768), `err.js` measures the neutral design against Anny,
  `sheet.py` tiles pictures. The `window.__stage`, `__R`, `__K` hooks in the page exist for these tools.
- **[cloth/](cloth/)** — clothes as cloth of their own fabric (XPBD) on Anny's bodies through Kimodo motions: walking,
  running, jumping, dancing, sitting on the floor, lying down, a forward roll, rolling over, with wind; dress, skirt,
  T-shirt, sweater, trousers, shorts, blouse, cardigan, jacket, swimsuit, scarf in sixteen fabrics, on a woman, a man and
  a child. The page computes a motion, then plays it; `shot.js` makes pictures.
