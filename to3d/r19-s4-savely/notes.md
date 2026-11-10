# Р19 — Савелий Петрович, Arcane (style С4) in 3D

What was done, why, how to repeat, the bases' licences. Brief: `docs/briefs/to3d.md`, its part "Third round": two
more characters in each style, starting from the style's character already in 3D — here Р7 Вера
(`to3d/r7-s4-vera`). Done by one agent (it made Р20 Кира next, with the same tools); the orchestrator commits.

## The idea (from Р7, kept)

The С4 drawing is itself built as 3D (`styles/s4-arcane/tools/arc.py`: the head a loft of sections with bumps, a nose
surface, a neck loft; features drawn in the face's flat coordinates and wrapped onto the head), so the bases are fitted
to its numbers and the result is checked in the drawing's own cameras. The drawing is weak as a drawing (a mannequin:
a stick body on stilts, an angular face), so the head's shape, the features' places, the colours and the light rules
are taken from it, and the rest from the style's rules (`styles/s4-arcane/entry.json`): near-real anatomy, one graphic
shadow shape with a clear edge, a warm band at the shadow's edge, a cool rim, painterly grain.

Units: world = (x·K, (FEET − y)·K, z·K + ZOFF), K = 0.97 mm per drawing unit (the same as Вера: the cast keeps its
sizes); he is 1.58 m, his head 225 mm.

## What is new against Р7 (and why)

Р7's page named its weak spots; these were done differently here:

- **The tools are shared, the character is a config.** Р7's scripts had Вера written into them. Here `drawing.py`
  names the character (`WHO`, `BODY`, `FIT`, `FACE`), `web/figure.js` (Р7's `vera.js`) is the same for every
  character of the style, and what is one character's own — the clothes painted by place, the standing pose, colours,
  expressions, motions — is in `web/char.js`. `parts.py` holds the shared builders. Р20 uses the same files.
- **Hair as locks, not one shell** (Р7: "one shell with painted strands"). `parts.hair_cap` makes a shell over the
  fitted skull and carries the drawing's own hair mask as an attribute — the shader cuts it, so the edge is clean and
  can be ragged; `parts.lock_mesh` turns every lock of the drawing's list (`P.hair_locks`) into a flattened tapered
  tube. Савелий's white tufts are the drawing's 70 plus as many again by the same recipe.
- **Brows and moustache are thin shells of hair** on the face (`parts.face_shell`: the head's own triangles inside the
  drawing's brow and moustache shapes, pushed off the skin) — they stand off the face in profile and move with the
  skin in expressions (they are skin pieces for `face.js`).
- **Clothes cut by place in the shader, not by vertex**: the waistcoat over the shirt, its V, the tie, buttons, the
  watch chain, pocket welts, the trousers below its hem and their crease are decided per pixel from the rest position
  (crisp edges); the mesh only gives thickness (the waistcoat stands 8 mm off the shirt). The trousers are each
  leg pushed out to a straight tube from hip to shoe, so the knee and the calf do not show as in tights.
- **The body is scaled by the shoulders, not the height.** Anny's head is smaller for the body than the drawn one and
  her shoulders rise high beside the neck; a scale by the whole height left no neck. The scale puts Anny's shoulder
  tops where the drawing's are.
- **The mouth's inside** is found by what is hardly seen from outside (the rays of `export_hbm.py`) and is dark and
  free of the painted layer; a band of upper teeth sits behind the lips. The base's mouth is wide for this face and
  is drawn in before the fit (`FIT['mouth_narrow']`).
- **Cast shadows are weak round the eyes** (a deep socket under a brow read as a bruise).
- The vertex shader took more than 16 attributes with the new ones: the scalars go four to an attribute.

## Steps (tools/, in order) and what each base gave

1. `export_hbm.py` (Blender 4.5, background) — Human Base Meshes «head for animation» (realistic) with its sculpted
   level, scleras and irises, and how much of each vertex's hemisphere is seen from outside. As Р7.
2. `drawing.py` — the drawing's head, nose and neck surfaces (`cast.savely()`) as points; the character's config.
3. `fit_head.py` — as Р7 (placement by the eyes and by heights of chin, mouth, nose base, nose tip, eyes, crown; the
   nose's protrusion scaled to the drawn nose; eye regions carried whole; non-rigid ICP), with his numbers: eye region
   1.1× the head's scale (an old man's small eyes), the mouth drawn in to 0.78, the drawn neck 1.3× wider.
   Gave: a real skull, lids, lips, a big nose with nostrils, big ears.
4. `build.py` — the pack (engine body format + look attributes):
   - Anny `moood-man` made lean (trunk 0.84–0.9, limbs 0.8–0.86), scaled by the shoulders, legs 3 % longer and each
     turned in 7° about its hip (he stands feet together), narrow sloping shoulders. Joint frames are not touched.
   - Anny's head and upper neck removed; her lower neck in the shirt's cloth is the collar, drawn in round the fitted
     neck (by how much a point belongs to the neck — smooth weights, no hard mask: a mask left a ragged edge), the
     cut's edge put on a level ring. The fitted head weighted Head → Neck2 → Neck1 → Chest down the neck.
   - Hair, brows, moustache as above. Round glasses from `P.glasses` (wire 0.75 units, brass: thinner gold did not
     read), low on the nose as drawn. Lofted shoes; Anny's feet removed, the trousers' hems level over the shoes.
5. `faces.py` — the painted layer as Р7 (lid lines on the fitted lids' real edges, lips on the fitted mouth, blush,
   nostrils, the drawing's own wrinkles `P.lines`), plus his age spots (`P.freckles`); brows are not painted (shells).
6. `web/figure.js` + `web/char.js` — the look (Р7's shader) and what is his own. Stand pose: hands clasped behind the
   back as drawn (each wrist put behind the pelvis by a two-bone reach, fingers curled).
7. `web/face.js`, `web/life.js` — Р7's (the face moved by a few numbers; blinks, saccades, the gaze leading the head,
   speech, blended expressions), the expressions from `char.js`. Joy and anger keep the mouth nearly shut: an open
   mouth under a moustache reads badly (see below).
8. `web/view.html` + `ui.js` — the 3D tab: turn, come closer, motion (stand, walk, bow, wave, idle), expressions and
   a mix, speech, face close, play/pause, scrub. Data in `web/data/`.
9. `shots.mjs`, `compare.py`, `steps.py` — pictures.

## Repeat

```
cd to3d/r19-s4-savely/tools;  C=/home/user/cache/to3d-r19-s4-savely;  (cd $C && npm install three@0.160.0)
flock /home/user/cache/heavy.0.lock blender -b …/human_base_meshes_bundle.blend -P export_hbm.py -- $C/hbm_head.npz
python3 drawing.py $C && python3 fit_head.py $C && python3 build.py $C && python3 faces.py $C
cp $C/out/{savely.json,savely.bin,face.json,face.png} web/data/
flock /home/user/cache/heavy.0.lock node shots.mjs jobs/jstill.json $C/st      # stills in the drawing's frames
flock /home/user/cache/heavy.0.lock node shots.mjs jobs/jfilm.json $C/fm       # film frames
python3 compare.py turn $C/st $C/cmp/turn;  python3 steps.py $C steps.jpg
ffmpeg -framerate 20 -i $C/fm/turn/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 26 ../pics/turn.mp4   (motions: 30 fps)
```
`shots.mjs` takes three.js from `$THREE` or the cache's `node_modules`; the page itself takes it from the CDN.

## What is weak (seen by eye)

- The figure is of near-real proportions and much wider than the drawing's stick on stilts (overlay); the drawing's
  own page calls its legs too long. Chosen as in Р7: the style's rules ask for real anatomy.
- Clothes are skinned shells, not cloth: no folds from motion; in the deep bow (Kimodo's `bow`) the waistcoat
  stretches with the back. The collar is a plain band with a painted notch and fold line, not a sewn collar.
- An open mouth: no lower teeth or tongue, the painted lips stretch — so joy is a closed smile, and speech opens the
  jaw only a little. Under the moustache it passes; a laugh would not.
- His brows are smaller and quieter than the drawn bushy ones; the face came out kinder than the stern drawing.
- Hands are Anny's (realistic), clasped behind the back by eye — fingers overlap rather than interlock.
- Kimodo's `idle` stoops and drops the head (the motion's own).
- The trousers' crease is a thin painted line and breaks into dashes at a distance.

## Licences

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body (`moood-man`), SOMA skeleton and weights: as in `engine/data` (`engine/data/soma/NOTICE`).
- Kimodo motions: `engine/motions` (moood studio).
- The drawing and its code: ours (`styles/s4-arcane`). three.js 0.160 (MIT). No neural images.
