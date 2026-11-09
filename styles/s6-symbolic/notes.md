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

## Round three: Марат and Кира (brief `docs/briefs/styles-more.md`, part A)
What was asked: the two new characters drawn by this style's rules and code, beside the four, without changing the four.

- `tools/cast_more.py` — the two bodies, on the same shared parts as the four (`sil.py` solids and skeleton,
  `cast.py` limbs and head curves); `cast.py` registers them in `CAST` (its last lines).
  - **Марат**: the tallest and widest body (shoulders 24.5 against Вера's 15), a barrel torso with a belly, a short
    thick neck, rolled sleeves (a thick roll above the elbow, heavy forearms, big hands), the apron as a front panel
    (the legs stay seen behind it in profile), curls as small spheres over a hair cap (a scalloped edge from any side),
    a spade beard and a moustache over a mouth notch in the profile curve. Default pose: leaning back, head thrown
    back, one fist on the hip (the gap between arm and body is what tells him apart), the ladle held out.
    Signs: the warm white towel over the shoulder; a terracotta ember and a thread of steam in the ladle.
  - **Кира**: long thin legs in heavy boots (a thick shaft and sole), a boxy hoodie wider than her shoulders, the hood
    as a bump on the back, hands in the pocket with the elbows out, a slouch (pelvis forward, back round, head
    forward), short hair with sharp ends at the nape and a fringe that hangs past the brow. Sign: lime headphones
    round the neck (each half of the band with its cup, so the far half goes behind the body); `phones='on'` puts
    them on the head.
- `tools/scenes_more.py` — their full figures (two more lights of the same world: `HEARTH`, `PLUM`), turnarounds,
  expressions by pose for both, `together-six`, `lineup-six`. The worlds, fog, rim and finish are those of `scenes.py`.
  Own small helpers where the four's did not fit: `fig2` (the shadow under the feet only — with an arm flung wide the
  four's shadow grew as wide as the arm), `expr_sheet` (a place for each figure), `turn_more` (a pose for the turn).
- `tools/portraits_more.py` — the two cameos, hand-written paths like the four; the whole bust is leaned by `lean()`
  (he back, she forward). `portraits.py` got two general kinds of sign: `('path', d, colour)` and
  `('line', d, colour, width)`.
- The four were not re-rendered: their files in `pics/` and `svg/` are byte for byte as before (checked by md5), and
  `portraits.py` after the change still writes the same SVG for each of them (checked against `svg/`).
- Iterated by eye: Марат's towel (a horseshoe that read as a horse collar → a strip down the chest), the ladle (a ball
  that read as a mace → a bowl flat on top, with the ember and steam), the ladle arm (in front of the face → out to
  the side), the apron (a slab → shorter and narrower than the hips), his anger (an arm glued to the head → pointing
  out with the ladle); Кира's head (bowed so far the face was lost → less), her fringe (a slab over the whole face,
  then a cap's peak → a mass over the forehead ending in a point at the eye), the headphones (two dots that read as
  eyes → cup and band), her joy (a raised hand → dancing alone with the headphones on), her sadness (arms like a
  dive → a ball hugging the knees); Марат's portrait was redrawn three times (wig-like curls, a ball of a beard).
- Weak, left as it is and said in the verdict: Марат's cameo (the laugh is only a notch under the moustache), the
  towel's shape in the silhouette, Кира's surprise, the front views.

To repeat (python3 with numpy and shapely — here `pip install shapely`, 2.2.0):

    cd styles/s6-symbolic/tools
    python3 scenes_more.py            # or: full turn expr together lineup
    python3 portraits_more.py

## How to add a character
1. A function in `tools/cast_more.py` (or a module like it): body sizes `*_B`, a profile curve `*_PROF`, the default
   pose, the solids (legs, torso, clothes, head, hair) and one or two signs in `acc`; add it to `MORE` and `MORE_NAMES`.
   Look at it first in black from several sides beside the others (as `lineup_six` does): it must be told apart by
   mass, head and pose alone.
2. Its scenes in `tools/scenes_more.py`: a line in `full_more` (a light, a side, one far warm thing), a turnaround,
   a table of four poses for `expr_sheet`.
3. Its cameo in `tools/portraits_more.py`: one closed path facing right in a 420×500 frame, a disc, two rims, signs.
4. The pictures into `entry.json`, into the blocks where the others' are.
