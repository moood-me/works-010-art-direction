# С6 «Символический: почти знак» — notes

## What was done
- Samples: Steam store screenshots (full size) of the games below, cropped to the people and reduced to ≤ 800 px in
  `refs/`; two crops of our own hope scenes (`docs/pictures/hope/`). Third-party pictures are kept only as references.
- Rules: written from what was seen in them (entry.json, block «Правила стиля»).
- Figures: `tools/sil.py` builds a person in 3D from a few solids — lofts of elliptic rings (torso, coat, head, hair)
  and tubes of spheres (limbs, hands, shoes) — on a small skeleton with pose angles; turns it by a yaw angle,
  projects it and merges everything into ONE flat shape (shapely union, slight closing and Chaikin smoothing).
  The shape is drawn in one ink; the rim of light is the shape minus itself shifted 1–2 px (an SVG mask); accents
  (lantern, watch, loupe glint, scarf, glasses) are separate small shapes, put in front of or behind the body by depth.
  `tools/cast.py` — the four (body sizes, head profile curves, clothes, signs, default poses);
  `tools/draw.py` — figure → SVG; `tools/scenes.py` — the scenes, turnarounds, expressions, together, lineup,
  light steps; `tools/portraits.py` — the profiles, hand-written cubic paths (the 3D heads were too coarse up close).
- Iterated by eye: shoulders (pads → sloped), hands (shorter), Аня's hair (plank → fall along the back), Тим's head
  (bigger, tufts that read as cat ears/horns → a fringe and two thin strands), Савелий's arms, poses for the
  expressions (anger tried three times), portraits redrawn with bolder noses and lips.

## How to repeat
    cd styles/s6-symbolic/tools
    python3 scenes.py full turn expr together lineup steps
    python3 portraits.py
Needs python3 with numpy and shapely, google-chrome (headless, used by render.sh) and ImageMagick `convert`.
SVGs go to `svg/`, pictures (JPEG) to `pics/`.

## Sources
- Kentucky Route Zero — https://store.steampowered.com/app/231200/ (krz-pier, krz-band, krz-studio)
- Limbo — https://store.steampowered.com/app/48000/ (limbo-boys)
- Inside — https://store.steampowered.com/app/304430/ (inside-boy)
- Journey — https://store.steampowered.com/app/638230/ (journey-traveler)
- Sky: Children of the Light — https://store.steampowered.com/app/2325290/ (sky-elder, sky-cape)
- Gris — https://store.steampowered.com/app/683320/ (gris-hand)
- Monument Valley 2 — https://store.steampowered.com/app/1927740/ (mv-tower)
- hope scenes (Claude Design) — docs/pictures/hope/lake.webp, forest.webp (hope-lake, hope-forest)
- Alto's Adventure was looked at (https://store.steampowered.com/app/2837600/) but its people are too small in the
  store shots to be useful; not kept.
