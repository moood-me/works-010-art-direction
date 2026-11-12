# Р47 — Аня, нуар: рисунок в 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, third round; brief: `docs/briefs/to3d.md`): Аня of style
С15 (`styles/s15-noir`: Bruce Timm, Mignola, Cooke — the black shape draws the form) made a 3D character on the SOMA
skeleton that moves by Kimodo through the engine. It is the first try of this style in 3D; the question was how the
black shapes live there. Started from Р1 (`to3d/r1-s3-anya`: the same girl, a flat graphic style) — its build, its
live face's timing and its viewer are reused; the head's face, the hair, the clothes, the shoes and the whole look are
new.

## The look: how the black lives in 3D

Flat colour or black, nothing between; one hard key from the picture's left (it turns with the camera, so every view
is lit as the drawings are). A dark shader alone gives a soft terminator crawling over every bump; the drawing's black
is a designed shape with straight edges. So (`tools/web/anya.js`, the `LIGHT` shader part):

- **Head and hair — the drawn edges.** `head.py`'s edge of the side shadow in the front view (`side_f` for ANYA: from
  the temple by the cheekbone to the chin) and the hair's shadow zigzag (`cast.py anya_hair`) are polylines in the
  head's own frame (each vertex carries its place there, `hp`, head units). The light is tested not on the mesh's
  normals but on a designed form: flat towards the front inside the edge, the side plane beyond it. So the terminator
  stands on the drawn line while the light or the head moves, and crosses the face only when the light goes far round
  (the face also gets a bias: it is the light's island and goes black last). With the light on the other side the
  shape mirrors. The head's mesh has the same plane break (below), so the silhouette agrees with the black shape.
- **More drawn shapes:** the jaw's cast shadow on the neck (`neck_f`'s shape: a band under the chin running down the
  side away from the light), the black wedge at the parting and the fringe's underside (distance to the drawn lines),
  the hair behind the neck black from the middle on; away from the drawn edge the hair's terminator is cut in straight
  teeth.
- **Body — straight terminators and real cast shadows.** Clothes and limbs are smooth shells, so their terminator is
  a straight edge down the form, as drawn. Cast shadows are real: a 2048² shadow map from the key, compared hard — the
  head on the shoulders, the arm on the jacket, the skirt on the legs, the figure on the floor.
- **No outline on the lit side; a rim where black meets black.** The inverted hull is drawn only where the form is
  turned from the light, in the drawing's cool rim colour (`noir.RIM`).
- **The face is drawn**: the eyes, brows, the nose's black plane and the lips are `head.py`'s own shapes (`eye`,
  `brow`, `mouth`; `noir.d` — the path with hard and soft corners — and `wedge`) ported to canvas in
  `tools/web/face.js`, drawn every frame from a few numbers, projected from the front. In the black the whites of the
  eyes stay, the lips go dark.
- **The stage:** night, a lighter window (or a disc) always behind the figure for the camera — the black side of the
  silhouette reads against it —, the floor ending at a wall, the window's light on the floor with the figure's black
  shadow in it.

## How the form is built (what each base gave)

- **Body and skeleton — Anny `moood-woman`** from `engine/data` (SOMA joints and weights), through Р1's `build.py`:
  joints moved to the drawing (neck, head, narrower hips, arms 8 % shorter), legs slimmed; only the legs below the
  skirt and the wrists are kept; hands are Р1's mittens (the drawing's hand is a wedge of closed fingers).
- **Head — Blender Human Base Meshes stylised head** (CC0; `hbm_export.py` → `hbm_head.npz`). `headfit.py`: heights by
  landmarks (neck end, chin, eye line, crown), each height's width to the front outline and depth to the profile
  (`head.front_outline`, `side_outline` of the style, `drawing.py`). Then the face is cut out along one loop inside the
  outline (sockets, lids, nose, lips, the mouth's bag — all drawn in this style; what hung on them inside is dropped)
  and closed by a clean patch laid on `surf`: the planes the drawing designs — the front plane to the drawn shadow
  edge, the side plane from it to the outline, the profile's line (nose wedge, lips, chin) down the middle. The base
  gives the skull, the jaw's underside, the neck, the ears.
- **Proportions.** The drawing's head is 1/5.6 of the figure (Р1: 1/6.4): `drawing.py` keeps Р1's units for the body
  and makes a head unit 1.37 of them. Heights of shoulders, waist, hems are the figure drawing's; the shoulders' width
  is the turn sheet's bust.
- **Clothes — shells** (Р1's lofts with new rows): a blue top and skirt as one shell (skin above the top's neckline),
  the mustard jacket over it with a V from the neck, narrow sleeves. Weights from the fitted Anny, a skirt rule below
  the hips; in a step the skirt is pushed off the legs' capsules (Р1's `pushSkirt`).
- **Shoes** — the drawing's small pointed flats modelled in place of Anny's feet (a loft, flat under, on the foot and
  toe joints).
- **Hair — one shell** (`hair.py`, rewritten): width from the front drawing, depth from the profile; the window's two
  edges are the drawn hairline (a side parting on the picture's right, the fringe swept to the left), each laid on the
  face; from the temples the edges go behind the ears and in to the neck's sides, and the hair hangs behind the neck
  as a mass with a flat front; pointed ends. Rigid: Head, the ends on the chest.

Neural models were not used.

## Alive

- **Face** (`tools/web/face.js`): Р1's timing — blinks at log-normal intervals (close 70 ms, hold 30, open 150),
  saccades, the gaze leading the head's turns by 0.25 s with a blink on big ones, speech as syllables of mouth shapes
  through a damped spring, expressions mixed and changing as damped springs (brows ahead) — driving С15's numbers:
  the brows' lift and tilt, how open the eye is, the mouth (corners, width, open, between the round «о» and the grin,
  teeth). The sheet's expressions are `head.EXPR`'s numbers; «calm» is Аня's rest (`smile`).
- **Motions**: Kimodo's from `engine/motions` (walk, wave, idle, sneak, sit) through the engine's retargeting and
  skinning, as Р1.
- **Viewer** `tools/web/view.html` (`ui.js`): drag to turn (the light turns with the camera), wheel nearer, motion,
  play/pause, scrub, the expressions and their mix, talk, the face close.

## Repeat

```
cd to3d/r47-s15-anya/tools
B=/home/user/cache/blender/blender; C=/home/user/cache/to3d-r47-s15-anya
$B -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
   --python hbm_export.py -- $C/hbm_head.npz        # (here it was copied from Р1's cache — the same file)
python3 build.py                # → $C/out/anya.json/.bin (2 s)
python3 bases.py $C/out         # the bases as they come, for the steps
cp $C/out/anya.* ../data/
python3 compare.py              # $C/cmp: the drawing and the 3D in the drawing's views
python3 make_pics.py            # ../pics: stills and the turn
python3 make_live.py            # ../pics: walk, wave, face-live, idle-face, sneak, sit (24 pictures a second)
```
`shots.mjs` serves `/home/user/` and drives `web/view.html?pack=…` with Playwright (software WebGL; three.js routed
to `/home/user/cache/n3-cloth/node_modules`); about 0.7 s a frame. By hand: serve the repository root, open
`to3d/r47-s15-anya/tools/web/view.html`.

Files: `drawing.py` (the drawing's shapes in the pack's units), `headfit.py`, `hair.py`, `build.py`, `mesh.py`,
`pack.py`, `bases.py`, `compare.py`, `make_pics.py`, `make_live.py`, `shots.mjs`, `web/` (`anya.js` — the look and the
stage, `face.js`, `ui.js`, `view.html`). The pack is Р1's format plus `hp` (place in the head's frame, head units) and
`kind` (0 body, 1 head skin, 2 hair).

## Licences of the bases

- Human Base Meshes bundle v1.4.1 (Blender Foundation): CC0.
- Anny body and the SOMA skeleton: as in `engine/` (`engine/data/soma/NOTICE`; Kimodo's SOMA skin Apache-2.0).
- Kimodo motions: `engine/motions`.
- Р1's code and the С15 drawing and its code: this repository.

## Honest state: what the style keeps in 3D and what it can't

Keeps: black or colour and nothing between; the side of the head, the neck, the far half of the body in black; the
drawn edge of the face's shadow; the rim; the eyes, brows and lips line for line in front and three-quarter; one red
accent on the dark; a readable silhouette in motion.

Weak:
- **The profile.** The face layer is projected from the front, so in a pure profile the eye is a thin black wedge and
  the lips a sliver; the drawing's profile has its own eye. The head's planes hold, the features don't.
- **The hair is smoother than the drawing**: the drawing cuts the hair's black in big zigzags and its ends in sharp
  points; here the mass is a smooth shell, the teeth are in the shadow's edge only, the ends are soft points. In
  three-quarter the near side is one black mass where the drawing leaves red wedges. Rigid, no inertia.
- **The figure stands straighter and stiffer than the drawing** (it has no pose of its own: the flower, the tilted
  head, the weight on one leg are not there), and its limbs are Anny's rounded forms, not the drawing's angular beams.
- **Eyes are soft and round for this language** — as in the drawing (its notes say so too).
- Hands are mittens; the skirt and jacket are shells (the skirt is pushed off the legs, it does not swing).
- The cast shadows are a shadow map: at the edges of thin parts (fingers, the hem in a wide step) they can break into
  small black bits for a frame.
- The light is tied to the camera; a lamp standing in the scene (the group picture's street lamp) was not tried.
