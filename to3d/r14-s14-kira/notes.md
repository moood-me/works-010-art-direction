# Р14 — Кира, вырезанная бумага: from the drawing to 3D

What was done (Claude, one agent of the «Рисунок в 3D» run, third round; brief: `docs/briefs/to3d.md`): Кира of style
С14 (`styles/s14-paper`: figure-kira, turn-kira, portrait-kira, expr-kira; the code that draws them: `tools/kira.py`,
`face.py`, `kit.py`, `body.py`) made a 3D character that moves by Kimodo through the engine. It is the first 3D for
this style, so the question was how cut paper lives in 3D.

## What was decided, and why

- **The figure is made of paper pieces, each a thin shell with a cut edge.** The drawing's rule is "everything seen is
  a piece of paper: an outline, a colour, a height, a kind of paper; no line". In 3D a piece is a sheet lying on the
  form under it: the hair is three sheets (the back piece, the side lock, the fringe glued at the crown and standing
  off the forehead), the hoodie one big sheet with a pocket, a hem band, strings and a heaped hood glued on, the
  headphones thick pads of card, the nose a piece folded down its ridge, the ears two ovals standing out of the head,
  the hands Anny's hands pressed flat (a hand cut from card with the fingers as snips).
- **The look is the drawing's four marks of paper, done by light instead of an SVG filter**: one flat colour per piece;
  brush streaks inside the painted papers (hair, hoodie), fixed to the piece and running down it — also down the
  sleeves; the sheet's light core along every cut edge (a rim 2.4 mm wide on the face of the piece, and the edge's own
  band); soft plum shadows that pieces throw on what lies under them — a real shadow map, the light always from the
  picture's top left wherever the picture is taken from, as the drawing's rule says. No outline, no gloss, almost no
  shading of the form (paper is matt); the clothes are lit as a few flat faces with creases, as folded card.
- **The face's small pieces are drawn, not modelled**: eyes with the lid piece and the lash sliver, brows, cheeks of
  tissue, the mouth — `face.py`'s functions carried to JavaScript line for line, with `kit.py`'s cast shadow, contact
  shadow and light rim for every piece, drawn each frame into a picture the head takes from the front. So the
  expressions are the sheet's own numbers and they blend; the lid piece comes down for a blink.
- **Proportions from the drawing**: 1 figure unit = 2.8 mm (she stands 1.52 m with the slouch); the head is big
  (0.34 m with the hair, 4.5 heads), the hoodie very oversized (0.36 m wide), stick legs, long arms, heavy boots.
- **The slouch is in the rest, not in a formula on top of the motion**: the spine's joints are turned (hips a little
  back, the back rounded, the neck forward, the head hung) together with the surface they carry, and the shoulders
  rolled forward and up; the joints' frames are not touched. The engine's retargeting measures Kimodo's turns against
  the frames, so every Kimodo motion carries her slouch along (engine/README: "a design in the rest rides along").
- **Where the drawing contradicts itself the front view wins.** In the front view the fringe hangs over her right eye
  and down to the cheek at the head's side; in the profile the same hair ends above the eye and leaves the temple and
  the ear bare. One head can't have both; the 3D follows the front, so its profile shows less face than the drawn
  profile. The profile's nose starts between the eyes, the front's below them — the 3D nose is the front's, its tip
  where the profile has it. The three-quarter drawing is drawn at no single angle; the 3D is shown at 24°.

## Steps and what each base gave

1. **Body — Anny's girl** (`engine/data/bodies/moood-girl`, SOMA skeleton). `tools/fitbody.py` (Р3's deformer): an
   affine map per joint (along the bone and across it), joints rebuilt down the chain, vertices moved by their skin
   weights' blend. Gave: joints, skin weights for everything cut from it, and the hands. Almost all of it is under
   the clothes.
2. **Head — Human Base Meshes, stylised head** (Blender, CC0). `tools/hbm_export.py`, `hbm.py`, `head.py` (Р3's way):
   the face cut out and closed by a smooth patch (libigl, biharmonic), a thin-plate warp from the base's silhouettes
   to the drawing's front and side outlines (`drawing.py` reads them from `face.py: outline`). In `build.py`: the
   base's ears smoothed away, what lies outside the front view's egg drawn in under the jaw to a thin neck (a darker
   piece, as drawn), the nose and ears added as paper.
3. **Hair** — `build.py: sheet()`: the head's surface cut along the drawing's outlines (signed distance to the front
   view's fringe and side lock in front, sharp teeth round the sides and back), lifted off the head, and below the
   head's widest hung straight down instead of following the skull in (`bell`).
4. **Hoodie** — the body's surface from the hips to the neck and wrists, moved onto an oval tube round the trunk and
   wide tubes round the arms, the hem and the too-long cuffs drawn on as extra rings (the hem takes a share of the
   thighs' weights, the cuffs of the hands'); the pocket and strings are patches laid on its front by ray casts; the
   hood a lofted lump behind the neck.
5. **Trousers, boots, headphones** — trousers: the legs' surface a little off; boots lofted along each foot with a
   thick sole and three lime laces; headphone pads and band lofted, on the chest joint.
6. **Thickness and rims** — `thick()`: along every open edge a band turned in (its own vertices, marked as the cut
   edge), and for every point of the piece its distance to the cut edge (`rim`), which the shader turns into the
   light line.
7. **The slouch** — `slouch()` in `build.py` (above).
8. **Look and motion** — `tools/web/kira.js`: the pack becomes an engine body (`makeBody`), the engine's `Figure`
   retargets Kimodo's motions and skins it (dual quaternions: fast to prepare in the browser); corrections of the
   engine used: `dampHeadSpine` (spine 0.6, head 0.5 — Kimodo's standing motions bow, and she already slouches),
   `armsOutOfHead`. Nothing of the engine was changed.

## Alive

`tools/web/face.js` (Р3's timeline with С14's pieces): blinks at uneven intervals (most 2–6 s, 12 % doubles; closing
~70 ms, held 30 ms, opening ~150 ms) and on fast head turns; saccades (fixations 0.3–2.4 s, a jump of ~40 ms with a
little overshoot; now and then a glance across) round her sideways resting look; the gaze leads a head turn by 0.25 s
(the head's yaw is read off the clip); speech as syllables of mouth shapes with pauses — small ones, she mutters;
expressions (calm, joy = a smirk, surprise, sad, angry) blend number by number over 0.35 s, the brows a little ahead.
All from a seeded random stream: a moment always looks the same.

Viewer: `tools/web/view.html` (`ui.js`) — drag to turn, wheel nearer, motion, play/pause, scrub, expressions, talk,
the face nearer. It reads `data/kira.json/.bin` and the engine (`engine/src`, `engine/motions`), three.js 0.160 from
jsDelivr; served from the repository's root. `tools/web/face-check.html` shows the face's pieces alone.

## Repeat

```
cd to3d/r14-s14-kira/tools
# once: the base head as arrays (Blender; the same file as Р3's)
/home/user/cache/blender/blender -b /home/user/cache/n5-heads/hbm/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend \
    --python hbm_export.py -- /home/user/cache/to3d-r14-s14-kira/hbm_head.npz
PY=/home/user/cache/n1-deform/venv/bin/python      # numpy, scipy, libigl
$PY head.py                     # the fitted head → cache/head_steps.npz
$PY build.py steps              # → ../data/kira.json/.bin; cache: kira-up (upright, for the sheets), the steps' packs
python3 backdrop.py             # the drawing's sheets without the figure (cache)
python3 compare.py turn expr figure     # ../pics: the drawing and the 3D side by side and overlaid
python3 steps.py                # ../pics: the steps
python3 films.py turn walk sneak idle wave sit face     # ../pics: mp4
python3 look.py name '{"views":"fqsb"}'  ·  python3 sheet.py walk 0 120 12      # quick looks while building (cache/look)
```
`shots.mjs jobs.json outdir` drives `web/view.html?shots=1` with Playwright (software WebGL; three.js routed to
`/home/user/cache/n3-cloth/node_modules`). Heavy runs go through `common.heavy()` — one of the three shared locks.
In this session `hbm_head.npz` was copied from Р3's cache (the same export).

## Licences of the bases

| What | Licence |
|---|---|
| Anny body (moood-girl, in the engine), SOMA skeleton | Anny (NAVER, Apache-2.0), MakeHuman (CC0), SOMA rig (NVIDIA, Apache-2.0) — `engine/data/soma/NOTICE` |
| Human Base Meshes bundle v1.4.1, `GEO-head_stylized` | CC0 (Blender Foundation) |
| Kimodo motions | `engine/motions` (made in the moood studio) |
| The drawing and its code; Р3's build code reused (`meshcut.py`, `hbm.py`, `head.py`, the face timeline) | this repository |

Neural models were not used.

## Honest state

- Recognisable and alive; front and three-quarter lie close on the drawing; the sheet's expressions are the same pieces.
- What of the paper is kept: one colour a piece, brush streaks inside painted paper, the light cut edge, layers with
  shadows between them, the light from the top left. What is not: the forms are round and smooth (papier-mâché rather
  than a folded sheet; only the nose is folded), no torn edge, no tissue; the "few flat faces" lighting of the clothes
  is barely seen because the paper's shade is weak on dark colours.
- The profile shows less face than the drawn profile (the front view's fringe wins, see above).
- Under the chin the neck piece has blotchy shade and a crease along the face's edge (the two pieces don't share
  normals there, on purpose; the patch's fan under the mouth still shows a little).
- The hoodie is a skinned shell: it doesn't crumple; faint ripples from smoothing run over it; in a wide step the hem
  follows the thighs like a skirt. Hair is rigid.
- Hands: Anny's hands pressed flat; under the long cuffs only the fingers show. The drawing's hand in the pocket is
  not made (no such motion in `engine/motions`).
- On a bowed head the fringe shades more of the face than the drawing's short shadow; on the skin the shadow is made
  lighter (0.20 against 0.36) so the face stays readable.
- The floor's shadow is cut where the shadow map ends (it fades there).
- Not tried: real folds (a low-polygon folded build of the head and clothes, as Tearaway does), cloth, the engine's
  centres-of-rotation skinning in the viewer (dual quaternions are used: fast to prepare).
