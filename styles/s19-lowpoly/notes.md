# С19 «Низкополигональный: грани» — notes

Round three of "Стили персонажей" (brief: `docs/briefs/styles-more.md`, part B). A new style: stylised characters
built from a few large flat facets, each lit as a plane — the look of Virginia (Variable State) and the GO games
(Square Enix Montréal). All six of the cast: Аня, Савелий Петрович, Тим, Вера, Марат, Кира.

## What was done

1. **Samples.** Steam's store API and CDN were reachable: screenshots and capsule art of Virginia, Lara Croft GO,
   Hitman GO, Kentucky Route Zero were downloaded to `/home/user/cache/styles-s19-lowpoly/dl/`, looked at, and twelve
   small copies (≤ 800 px) kept in `refs/` (list below). ArtStation pages are refused by the proxy (403), so no
   low-poly character art by individual artists is among the samples; nothing was traced or faked. Thirty Flights of
   Loving was looked at and left out (blocky and textured, not faceted). Superhot was not used (only as a contrast).
2. **Rules** — from the samples, in `entry.json` («Правила стиля»), with two diagrams (`rule-planes`, `rule-heights`).
3. **Drawing code** (`tools/`, Python → SVG; numpy, scipy, shapely): the characters are real 3D models. Every form is
   a convex piece — the hull of a few hand-placed points — and the points are the drawing: where they sit decides
   where the planes go. A camera turns the model and projects it; every face is filled with one flat colour from its
   normal; hidden parts are cut away exactly (see below). Features of the face, stripes, buttons, laces are decals
   pressed onto the facets.
4. **Sheets**: portrait and figure for all six; turnarounds for all six; expression sheets for all six; the four
   together (`cast`, the cover); all six (`cast6`); two rule diagrams.
5. Iterated by eye against the samples. What changed on the way: a generic eye (dark almond) looked asleep → white,
   octagon iris, lid band, speck; the hair cap wrapped round the head was drawn over the face by a piece-order
   painter → replaced by exact hidden-surface removal per face; knees showed a cap seam → limbs as chains with a hull
   at each bent joint; square box shoulders → a `shoulder` piece from neck to arm; heads were too small for the style
   → head scale 1.12–1.3; Савелий's loupe on the forehead read as a black plug → in his eye in the figure only;
   Кира's choppy ends on top read as cat ears → only downward ends; her figure turned so the face shows past the
   fringe; Вера's legs poked through the coat → narrower stance, deeper hem; Марат made taller and much wider.

## How it is built

- `tools/poly.py` — the engine. `hull(points, colour, mat)` makes a `Piece` (coplanar triangles of the hull merged
  into one face); `segment`, `chain` (limbs through joints, a hull at each bent joint), `ring`, `mirror_x`;
  `press(piece, polygon, colour, …)` lays a flat decal onto the facets (straight in along `dir`, or out from a
  `centre`); `Light` (warm key upper left, cool shadow, faint fill; per material: skin, cloth, hair, metal);
  `Camera(yaw, pitch, f, scale, ox, oy, target)` with a weak perspective that keeps planes planar; `render()` →
  SVG paths. **Hidden surfaces are exact**: each face turned to the viewer is cut down to the part where no face of
  another piece is nearer (on an overlap both are planes, so "nearer" is a half-plane; Sutherland–Hodgman + shapely);
  decals are cut the same way and drawn over their piece. So pieces may wrap round or pass through each other.
  `render(…, edges=colour, decals=False, flat=colour)` draws the diagrams.
- `tools/face.py` — the head from a `spec` (numbers move the points; `DEFAULT` lists them): one hull for skull and
  face, a nose wedge, ears; decals: `eye` (`_eye2d` draws it flat: almond, iris cut by it, pupil, lid band, lash
  flick, speck, crease), `brow`, `mouth` (line / smile / smirk / down / tight, or open with teeth, tongue, lower lip).
  `EXPR` holds the expressions; a character's module may give its own `EXPR` (Марат's rest is a laugh, Кира's joy is
  a smirk). `eye_rest`, `look`, `lash`, `iris`, `lid_th`, `laugh_lines`, `lips` tune a face.
- `tools/body.py` — `Skel(prop, pose)`: forward kinematics (pelvis, spine, neck, head; arms: abduction, forward,
  twist, elbow bend, wrist; legs likewise; feet set on the ground). Parts: `leg`, `arm` (chains; a 4th radius gives a
  calf), `shoulder`, `torso_hull` (rings in the pelvis or chest frame; `side` keeps half — an open jacket's panel),
  `hand` (relax / fist / open / point: palm, finger block, thumb), `shoe` (shoe or boot, sole), `band` (a stripe
  round a piece).
- `tools/scenery.py` — the graded faceted backdrop, the plinth under a figure, the diorama for the cast.
- `tools/anya.py … kira.py` — one module per character: `COL`, `SPEC`, maybe `EXPR`, `PROP`, `POSES`
  (`stand` for the figure and the cast, `turn` for turnarounds and expressions, `portrait`), `hair(e)`, props,
  `figure(pose, expr) → (pieces, skeleton)`; sheet settings: `PORTRAIT_CAM = (yaw, up, scale)`, `FIGURE_YAW`, `PLINTH`.
- `tools/build.py` — the sheets; `tools/render.js` — SVG → PNG (Playwright, one browser); `tools/webp.py` — → WebP.

## Repeat

```
cd styles/s19-lowpoly/tools
python3 build.py                     # all sheets → ../svg (about 40 s)   (or: python3 build.py cast figure-kira)
NODE_PATH=/opt/node-tools/node_modules node render.js     # → ../pics/*.png   (or names)
python3 webp.py                      # → ../pics/*.webp, removes the png
```
`SVG=dir python3 build.py …` and `SVG=dir OUT=dir node render.js …` build and render into a scratch folder.

## How to add a character

1. Copy the nearest module (`kira.py` thin teenager, `marat.py` big bearded man, `anya.py` long hair, `savely.py`
   old man with pieces for brows and moustache, `vera.py` glasses and a long coat, `tim.py` child).
2. `SPEC`: skin, the head's points (`crown, skull_w, face_z, cheek_*, zyg_w, low_*, jaw_*, chin_*`), the nose
   (`nose_tip_y/z, nose_w`), eyes (`eye_x, eye_y, eye_w, eye_h, iris, lash, eye_rest, look`), brows, mouth. Look at
   the head with `render(…, edges=…)` (as `rule_planes` does) and move points until the planes sit where you want.
3. Hair: a cap hull a little outside the skull (its front edge is the hairline), then masses: locks, a bun, tufts,
   curls, a fringe — each its own hull in head space (origin between the ears at eye level, z forward).
4. `PROP` (lengths in cm) and `POSES`; give `stand` one line of action (pelvis tilt against the chest, the weight
   on one leg, the head turned). Print joints with `Skel(PROP, pose).j` to place hands.
5. `figure()`: legs and shoes, torso and clothes (`torso_hull`, `band`, `press`), neck, `shoulder` + `arm`, hands,
   props, `sk.place_head(head pieces)`.
6. Add the name to `WHO`, `NAMES`, `TURNS` and `scenery.BG`, build, render, look, redraw.

## Weak spots

Women's faces are correct but plain and hard (Вера in front view reads long and almost male); Кира reads more
androgynous than a girl; Савелий's face in the figure is half hidden (looking down, loupe in the eye); bodies are
straight with long stiff legs; hands are 3–4-facet mittens; no cast shadows and no atmospheric light as in Virginia.

## Sources

- Virginia (Variable State, 2016) — https://store.steampowered.com/app/374030/Virginia/ — refs 01–06
  (screenshots 01, 02, 08, 11, 04 and the library capsule)
- Lara Croft GO (Square Enix Montréal, 2015) — https://store.steampowered.com/app/540840/Lara_Croft_GO/ — refs 07, 08
- Hitman GO: Definitive Edition (Square Enix Montréal) — https://store.steampowered.com/app/427820/ — refs 09, 10
- Kentucky Route Zero (Cardboard Computer) — https://store.steampowered.com/app/231200/ — refs 11, 12
- Not downloadable here: ArtStation (https://www.artstation.com, proxy 403).

Downloads and scratch renders: `/home/user/cache/styles-s19-lowpoly/`.
