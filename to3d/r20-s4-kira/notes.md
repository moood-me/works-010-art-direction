# Р20 — Кира, Arcane (style С4) in 3D

What was done, why, how to repeat, the bases' licences. Brief: `docs/briefs/to3d.md`, its part "Third round". Made
right after Р19 Савелий Петрович by the same agent and with the same tools; the starting point of both is Р7 Вера
(`to3d/r7-s4-vera`). The orchestrator commits.

## The idea

As Р7 and Р19: the С4 drawing is built as 3D by its own code (`styles/s4-arcane/tools`, Кира in `cast2.py`), so the
bases are fitted to its numbers and checked in its cameras; where the drawing is a mannequin (a stick body on stilts)
the style's rules lead — near-real anatomy, one graphic shadow with a clear edge, a warm band, a rim (hers is the
acid lime of her accent), painterly grain. Units as the cast's: K = 0.97 mm per drawing unit; she is 1.55 m.

The tools are Р19's (see its `notes.md`, "What is new against Р7"): `drawing.py` names the character and its
config, `parts.py` holds the shared builders (hair shell cut by the drawing's mask, locks as flattened tubes, shoes),
`web/figure.js`, `life.js`, `ui.js`, `faces.py`, `compare.py`, `steps.py` are the same files; hers alone are
`build.py`, `web/char.js`, and small changes in `fit_head.py` and `web/face.js` (below).

## What Кира needed

- **A thin, long-legged teenager.** Anny `moood-girl` (1.51 m), trunk 0.84–0.86 and limbs 0.8 of their thickness,
  scaled by the shoulders (the drawn head is big for the body), legs 7 % longer, narrow shoulders, each leg turned in
  5°. Joint frames are not touched: Kimodo retargets as for any engine body.
- **The slouch** is a standing pose, not a body: hips a little back, the spine bent forward step by step (4°, 5°,
  7°), the neck forward, the head brought back up to look from under the brows, tilted and turned a little as the
  drawing's `head_pose` says. In Kimodo's motions the body moves as the motion says (her `sneak` is the hunched one).
- **Hands in the hoodie's pocket**, not arms crossed as drawn. Crossed arms by a two-bone reach were tried once: the
  hands stuck out past the elbows. The pocket hides Anny's realistic hands, suits «не трогайте меня», and holds.
  It is a departure from the drawing.
- **The oversized hoodie**: the trunk and the arms pushed 16–24 mm off the body; below the chest every section of the
  trunk is pushed out to at least an ellipse that widens toward the hem, so the waist does not show; a pouch on the
  belly for the hands; the hem's ribbing, the pocket's outline and two drawstrings of uneven length with acid tips
  are painted by place in the shader. The hood is a soft lump on the upper back; Anny's lower neck in the hoodie's
  cloth is the neckband, loose round the fitted neck.
- **Headphones round the neck**: two lime cups on dark pads on the collarbones (placed on the hoodie's own surface),
  a band behind the neck. With the laces and the drawstrings' tips they are the one acid accent.
- **Narrow trousers** are the legs with 3 mm of cloth, charcoal by place below the hoodie's hem; their front under
  the hem, between the legs, is smoothed flat (the body's own form there read as a dark lump hanging under the
  hoodie). **Heavy boots** are built in `build.py` (`boots()`): a loft by height — a thick sole with a heel and an
  arch under it, a welt, a high rounded toe box, the instep rising into a shaft that narrows at the ankle and goes
  with the shin; the sole's tread, the toe cap's seam and the zigzag laces are painted in the shader. (The first
  try, the shared shoe made tall, was a wedge with a straight shaft.)
- **Hair**: the shell over the skull above the drawing's hairline (a choppy lower edge), thick on the crown, and all
  58 locks of the drawing as flattened tubes with pointed tips — the choppy layers, the pieces pushed off the right
  side of the face, the long fringe from the parting down over her left eye. A lock whose root lies below the
  hairline (in the drawing other locks cover it; in 3D it was a dark bar stuck on the forehead) is grown up into the
  hair first (`rooted`). The lock's light is violet (`char.js`).
- **Face**: fifteen, not an adult. The first fit kept the base's adult forms — a heavy brow ridge and nose, a long
  jaw, a grim mouth: she read as a hard grown-up, almost a man. Now the fit follows the drawing's smooth head closer
  (stiffness down to 3), the nose is let go to the drawing's small one (`nose_keep`, `nose_min`), and what is left
  of the bony forms is smoothed everywhere but the eyes, lips, nostrils and ears (`smooth`: 14 steps). Eye region
  1.27× the head's scale and 1.1× wider (Arcane's almond eyes, smaller than Аня's), the base's wide mouth drawn in
  to 0.74. The resting mouth's corners are lifted a little (the base's turn down), one more than the other. `fit_head.py` differs from Р19's in two places: the mouth's narrowing leaves the
  nose's base alone (her mouth sits close under a short nose — the nostrils were pinched), and the mouth's inside is
  kept behind the skin in front of it (it came out through the upper lip). No teeth band: behind her thin lips it
  showed through as a grey upper lip; she never opens her mouth in a smile anyway.
  The painted layer: dark brow blocks, the heaviest lash line of the cast with a wing, freckles over the nose.
- **Expressions** from her own sheet (`cast2.py`): calm = heavy lids, low knit brows, a look aside and from under the
  brows, the mouth pressed with one corner up; joy = a crooked half-smile — `face.js` got `smirk` (her right corner
  up, the other a little down) for it. Surprise, sadness, anger as the sheet.
- **Light**: cast shadows are faded over the eyes and the upper cheeks (`eyeShade` in `char.js`: the fringe's
  shadow under an eye read as a bruise), and the face's front takes little of the lime rim (`faceRim`: a coloured
  rim on lips and lids read as dirt). Shade planes of the face are smoothed twice as far as Вера's and followed
  almost fully (0.96), and the shadow's edge is brushed three times less (`edgeN`): few clean shadow shapes.

## Steps (tools/, in order)

1. `export_hbm.py` — as Р7 (the same `hbm_head.npz` as Р19's).
2. `drawing.py` → the drawing's head, nose, neck as points; 3. `fit_head.py`; 4. `build.py`; 5. `faces.py`;
6. `web/` — `figure.js` + `char.js` (the look and what is hers), `face.js`, `life.js`, `view.html` + `ui.js` (the 3D
   tab: stand, walk, sneak, idle; expressions and a mix; speech; face close; play/pause; scrub);
7. `shots.mjs`, `compare.py`, `steps.py` — pictures.

## Repeat

```
cd to3d/r20-s4-kira/tools;  C=/home/user/cache/to3d-r20-s4-kira;  (cd $C && npm install three@0.160.0)
flock /home/user/cache/heavy.0.lock blender -b …/human_base_meshes_bundle.blend -P export_hbm.py -- $C/hbm_head.npz
python3 drawing.py $C && python3 fit_head.py $C && python3 build.py $C && python3 faces.py $C
cp $C/out/{kira.json,kira.bin,face.json,face.png} web/data/
flock /home/user/cache/heavy.0.lock node shots.mjs jobs/jstill.json $C/st
flock /home/user/cache/heavy.0.lock node shots.mjs jobs/jfilm.json $C/fm
python3 compare.py turn $C/st $C/cmp/turn;  python3 steps.py $C steps.jpg
ffmpeg -framerate 20 -i $C/fm/turn/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 26 ../pics/turn.mp4   (motions: 30 fps)
```

## What is weak (seen by eye)

- Hands in the pocket, not arms crossed as drawn; in Kimodo's motions they come out and Anny's realistic hands show.
- The figure is of near-real proportions, wider than the drawing's stick; the hoodie is a shell, not cloth: no folds.
- In the profile the shadow on the cheek and jaw is one band now, but its edge under the jaw is still uneven.
- An open mouth has no teeth; small dark ticks of the painted mouth line show at the corners.
- The eye regions are carried from the base as a whole: a faint ridge under the eyes is still in the form (the
  shade does not show it).

## Licences

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body (`moood-girl`), SOMA skeleton and weights: as in `engine/data` (`engine/data/soma/NOTICE`).
- Kimodo motions: `engine/motions` (moood studio).
- The drawing and its code: ours (`styles/s4-arcane`). three.js 0.160 (MIT). No neural images.
