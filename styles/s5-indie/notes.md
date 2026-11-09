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

## Adding a character

A character is a function `name(yaw, ex, pose) -> [(layer, svg), …]` in its own module (see `tools/marat.py`,
`tools/kira.py`), registered in `tools/build.py` (`cast.CAST['name'] = …`, `NAMES`, `HEAD` — the head's centre and the
portrait's background; `WIDE` if the character doesn't fit the common sheet). Inside: head rings → `vol`; the face with
`fs` + `eye`/`brow`/`mouth` (the character's resting face is set by overriding `E` for `ex == 'neutral'`); hair with
`hair_cap` over hairline keys; the head parts wrapped with a translate and a tilt; then the body volumes, limbs, a
ground shadow. Layers: ~5 behind the head, 9 legs, 10 body, 16 arms in front, 20–23 the head.

## Round three: Марат and Кира (the cast is six)

Brief: `docs/briefs/styles-more.md`, part A. No web was used. The four's code and pictures were not changed.

- `tools/extra.py` — shared parts the kit lacked: `limb` (a limb whose width changes: thick forearm → wrist, a sleeve
  that widens to the cuff — the answer to "arms are tubes of one width"), `mitt` (the hand-ball plus a thumb),
  `mass_below` (a beard: a volume kept below a line of keys on the head — `hair_cap` upside down), `scallop` (a bumpy
  outline for curls), `front_patch` (a patch on the front of a volume: an apron, a pocket; in profile it becomes a
  strip), `band` (a strap round a volume, only its visible part), `lean` (a screen rotation of the upper body: degrees
  sideways seen from the front, forward/back seen in profile — a cheap line of action), `lay` (front or back layer by depth).
- `tools/face.py` — new mouth signs: `beam` and `laugh` (a wide open smile: a band of upper teeth and a tongue),
  `tight` (pressed shut), `half` (a crooked half-smirk with a dimple).
- `tools/marat.py` — Марат. The head is drawn 1.1 times larger (the style's "the head is the biggest thing"; the line
  keeps its weight); the barrel torso is wider than anyone's; the beard is one dark mass, the mouth lives on it by its
  teeth and tongue (a dark line on a dark beard is not seen), a closed mouth is a lower lip under the moustache, and the
  moustache lifts and droops with the mood. The resting face is a wide smile; the eyes are pushed up from below by the
  cheeks (a skin-coloured arc over the eye's lower part). In joy the head is thrown back and the ladle goes up.
  `pose='calm'` (arms down) is for the expression sheet.
- `tools/kira.py` — Кира. Smaller head and eyes than Аня's, a longer face; the look from under the brows (inner lid
  low, flat low brows, the highlights shifted sideways); the fringe is hairline keys that come down over her left eye;
  spikes under the back of the hair and on the crown; the slouch is `lean` forward plus the head pushed forward in
  profile; hips shifted, one knee out. She never smiles openly: `joy` is the half-smirk; `sad` has no tear.
- `tools/build.py` — the two registered; `WIDE` gives Марат wider sheets at the same scale (figure 525×765, turnaround
  1485×802, expressions 1750 px wide with each cell clipped) and a portrait that steps back 1.22×; `together6()` →
  `cast6`. `tools/render.py` — `<meta charset="utf-8">` (labels of the new sheets came out as mojibake without it).
- Tried and changed by eye: the ladle in the near hand covered the face in profile → moved to the far hand; a pointed
  beard with "straps" → the beard line laid on the beard's own volume, a rounder beard; brows lost in the curls →
  higher hairline, smaller brow rise; Кира's headphones hidden under the chin → lowered onto the chest and made larger;
  side spikes that read as pigtails → fewer, shorter.

Repeat: `python3 tools/build.py marat kira cast6`.

**Mind:** a full `python3 tools/build.py` re-renders the four too, and the code as committed before this round
already gives pictures of Тим and Вера (and `cast.png`) that differ slightly from the committed PNGs (checked with the
untouched code from git: the same difference, so it is not from this round). The committed pictures of the four were
kept; build only the new names if they must stay byte-for-byte.

Weak in the new two: Марат's body is an even barrel and in profile a box, his laugh is carried by the head and the
ladle more than by the body; his hands are still balls. Кира's hair is one dark blot without drawn locks; one hand is
in the pocket. In `cast6` at a negative yaw Марат's towel is hidden by his arm.

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
