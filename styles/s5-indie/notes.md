# С5 — Инди-герои: просто и мило

## What was done

1. **Samples.** Character art downloaded from the games' fandom wikis through the MediaWiki API
   (`https://<wiki>.fandom.com/api.php?action=query&titles=<page>&prop=pageimages&piprop=original&format=json`), looked at
   side by side, 12 kept in `refs/` (flattened on a light background, ≤ 800 px, jpg). Third-party, kept only as references.
   Downloads and scratch are in `/home/user/cache/styles-s5-indie/`.
2. **Rules** written from what the samples show (see `entry.json`, block «Правила стиля»).
3. **Cast** built by our own scripts — no tracing, no image models:
   - `tools/geo.py` — a tiny 2.5D kit: a volume is a stack of elliptic rings `(y, w, d, cx, cz)`; at a yaw its
     silhouette is projected and drawn as one smooth flat shape with one cel shade (a darker copy, the base colour on top
     shifted up-left, clipped) and a warm outline. Limbs are stroked tubes; features sit on the surface of the head
     (`surf`) so they turn with it.
   - `tools/face.py` — the face signs: eye (dark oval, highlights, a lid that cuts it), brow, mouth; expressions.
   - `tools/cast.py` — the four characters. Hair is the head volume, a bit larger, above a hairline given as keys
     `(phi, y)`; a second mass behind the head. Face features (and the hairline, ears) turn ~0.38·sin(yaw) further than
     the skull, as cartoon turnarounds cheat, so the face doesn't sink into the edge in profile.
   - `tools/build.py` — writes `svg/*.svg` and renders `pics/*.png`; `tools/render.py` — headless Chrome screenshot.
4. **Iterated by eye**: eyes with and without sclera (sclera went anime — dropped), hairline locks (zigzag → swept
   locks), the side view (ears and side locks covered the face → the turn cheat, a bob over the ears), the old man
   (bald crown over a white horseshoe, pear body, shorter legs, hands behind), Вера (no grey streak — it read as a hair
   clip; a side-swept hairline), line weight (3.2 dark → 2.4 warm), brows of anger had the wrong tilt.
   `pics/compare.jpg` puts the samples above our cast.

## How to repeat

```
cd styles/s5-indie
python3 tools/build.py            # everything; or: build.py anya | portrait | turn | expr | cast | rules
```
Needs `google-chrome` (headless) and Python 3. `compare.jpg` is a montage (ImageMagick):
`montage refs/nitw-mae.jpg refs/nitw-bea.jpg refs/sf-stella.jpg refs/hk-elderbug.jpg refs/celeste-granny.jpg refs/ahit-hatkid.jpg -tile 6x -geometry 200x260+6+6 -background '#ece5d9' r.png; convert r.png -resize 1260x pics/cast.png -append pics/compare.jpg`

## What is weak (honestly)

- Closer to tidy chibi clip-art (A Hat in Time, Kirby) than to the bold graphic shapes of Night in the Woods or Hollow
  Knight: pleasant, but ordinary.
- Arms are tubes of one width, hands are balls; poses stand, with little line of action.
- Fringes are made from a hairline on a sphere: zigzag edges, no separate locks.

## Sources (refs/)

| file | work | link |
|---|---|---|
| nitw-mae.jpg | Night in the Woods — Mae | https://static.wikia.nocookie.net/nightinthewoods/images/2/2e/Mae_Borowski_Sprite_Idle.png |
| nitw-bea.jpg | Night in the Woods — Bea | https://static.wikia.nocookie.net/nightinthewoods/images/8/85/Bea_placeholder.png |
| nitw-candy.jpg | Night in the Woods — Candy Borowski | https://static.wikia.nocookie.net/nightinthewoods/images/e/e5/Mom_Table_bod_00000.png |
| sf-stella.jpg | Spiritfarer — Stella | https://static.wikia.nocookie.net/spiritfarer/images/d/de/Stella_Artwork.png |
| sf-atul.jpg | Spiritfarer — Atul | https://static.wikia.nocookie.net/spiritfarer/images/e/ea/Atul_Full.png |
| hk-elderbug.jpg | Hollow Knight — Elderbug | https://static.wikia.nocookie.net/hollowknight/images/5/54/Elderbug-2.png |
| hk-hornet.jpg | Hollow Knight — Hornet | https://static.wikia.nocookie.net/hollowknight/images/1/16/Hornet_Idle.png |
| celeste-granny.jpg | Celeste — Granny | https://static.wikia.nocookie.net/celestegame/images/d/d9/Granny.png |
| ahit-hatkid.jpg | A Hat in Time — Hat Kid | https://static.wikia.nocookie.net/a-hat-in-time/images/0/03/HatKidUpdatedRender.webp |
| kirby-adeleine.jpg | Kirby Star Allies — Adeleine | https://static.wikia.nocookie.net/kirby/images/2/29/KSA_Adeleine.png |
| ori-naru.jpg | Ori and the Blind Forest — Naru | https://static.wikia.nocookie.net/oriandtheblindforest/images/a/a4/Naru.png |
| alba.jpg | Alba: A Wildlife Adventure — Alba | https://static.wikia.nocookie.net/alba-a-wildlife-adventure/images/d/d7/Alba_AWA.png |
