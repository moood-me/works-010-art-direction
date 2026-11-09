# С15 — Нуар: чёрное пятно

## What was done

1. **Samples.** This session's network let through only a few hosts. Looked at ~700 pictures: the "Art of Batman: The
   Animated Series" and "Art of Samurai Jack" pages of Character Design References (model sheets, Bruce Timm's
   drawings, backgrounds) and the fair-use covers and panels in English Wikipedia articles (Mignola's Hellboy and
   Lobster Johnson, a Slam Bradley cover (artist not checked), Cooke's New Frontier covers, Miller's Sin City, Bernet's Torpedo, Mask of the Phantasm).
   Twelve are kept in `refs/` (≤ 800 px, jpg). Not reached: pages of Alex Toth, Cooke's Parker, the Fandom wikis'
   stills (their page hosts are closed, only the image host is open — no way to list images), so the rules for Toth
   and Parker are not written from pictures looked at here. The Wikipedia API was rate-limited; article pages were
   read instead.
2. **Rules** — in `entry.json` («Правила стиля»), from the samples.
3. **Drawing.** SVG written by Python in `tools/` (no tracing, no image models). The style's logic is in one
   function, `noir.form`: a form is drawn black, and its lit copy — the same path in colour, moved a few units towards
   the light and cut by the form — is laid over; what the copy doesn't cover is the black shadow following the form's
   own edge. More black shapes (the planes turned from the light, cast shadows) go on top, cut by the form; a thin
   cool rim parts black from black. Everything faces the viewer's left and is lit from the left; a figure is mirrored
   (`flip=True`) when the light is on its other side (the lamp in the group pictures).
4. **By eye.** Rendered, compared, redrew: heads were too small on the bodies (now ~6.5 heads); the side shadow ate
   the women's faces (moved back); Марат's beard merged with the shadow into a mask (the beard is now a lit brown form,
   the shadow moved behind the cheek); Аня's first torso was a post with stripes (redrawn with a waist); Кира's face
   disappeared when the head was tilted too far; a rim of back light was added so that black sides don't dissolve in
   the night; Вера's nose was witch-long.

## Files

- `tools/noir.py` — the kit: `d` (path with hard and soft corners), `form` (the lit form), `limb`, `wedge` (a stroke
  with pressure), `clip`, `g`, `svg`.
- `tools/head.py` — the head in three views (`head_q` three-quarter, `head_f` front, `head_s` side), `eye`, `brow`,
  `mouth`, necks; `DEFAULT` (a character's values), `EXPR` (expressions as numbers).
- `tools/cast.py` — the six heads: shape, features, colours, hair, glasses, moustache, beard.
- `tools/figures.py` — the six bodies in a pose, `hand`, `shoe`, `figure(k, expr, x, y, s, flip)`.
- `tools/build.py` — every picture → `svg/`; `tools/render.js` → `pics/` (Playwright, one Chromium).

## How to repeat

```
cd styles/s15-noir/tools
python3 build.py            # everything (~10 s)
python3 build.py portrait   # only names containing "portrait"
```

## How to add a character

1. `cast.py`: `NAME = P(DEFAULT, ...)`. Start from the nearest of the six. `q={...}` moves points of the
   three-quarter outline (jaw, chinr, chinl, cheek, brow…; a third value `'s'` makes a point smooth) — the front and
   side outlines are derived from it (`f_over`, `s_over` correct them). `eye`, `brow`, `nose` (`kind`: `wedge` — the
   black side plane, `line`, `under`), `mouth` (`lips` > 0 — drawn lips), `side` (the edge of the side shadow), `skin`,
   `lip`, `iris`. Hair is a function `hair(view, layer, p, e)` returning forms for `'back'` and `'front'`; `extras`
   (glasses, moustache), `beard`, `folds` (black wrinkles) are functions of the view too. `expr_fix` changes an
   expression for this character (Кира never grins). Add to `CAST`, `NAMES`, `REST`.
2. `figures.py`: a function returning `dict(body, over, neck, rot, hs)` — limbs and garments as `limb`/`form` with
   their black shapes, far side first; `neck` is where the head sits, `rot` its tilt, `hs` its scale. Add to `BODY`.
3. `build.py`: a colour pair in `BACK`, a row in `bust` (shoulders for the sheets), the name in the lists of pictures.

## Марат and Кира

Drawn the same way as the four, in the same round. Марат: the widest body, a lit brown beard with the grin cut into
it (teeth and tongue), eyes as arcs when he laughs, arms thrown wide (an open hand, a ladle). Кира: an S-slouch, hands
in the hoodie's pocket, the fringe over the far eye (`hide_far_eye`), lime headphones as the accent; her "joy" is a
smirk.

## Sources

- https://characterdesignreferences.com/art-of-animation-4/art-of-batman-the-animated-series — timm-batman-face,
  timm-batman-red, timm-two-face, timm-catwoman, btas-bruce-turn
- https://characterdesignreferences.com/art-of-animation-8/art-of-samurai-jack — samurai-jack-rain
- https://en.wikipedia.org/wiki/Hellboy — mignola-hellboy (Hellboy: The Wolves of Saint August)
- https://en.wikipedia.org/wiki/Lobster_Johnson — mignola-lobster
- https://en.wikipedia.org/wiki/Slam_Bradley — slam-bradley (the artist of this cover was not checked)
- https://en.wikipedia.org/wiki/Marv_(Sin_City) — miller-marv
- https://en.wikipedia.org/wiki/Torpedo_(comics) — bernet-torpedo
- https://en.wikipedia.org/wiki/Andrea_Beaumont — btas-andrea
