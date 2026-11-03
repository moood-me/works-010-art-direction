# 2026-11-03 — the engine, stage 1: bodies

**What called for it.** The plan's stage 1 (bodies), as agreed with Pavel ([directions.md](../directions.md), "The engine
view"; [requirements.md](../requirements.md)): the base body is Anny with her own settings (Т8); deformers on top, each
with a strength, on the rest or as a pose layer, composed in the author's order, on any body, anywhere, any heading —
from Т5 (lines and shapes), Т6 (the cage, which the review found to be nearly the same as Т5's body-as-one-shape: merge,
don't duplicate), Т1 (proportions, caricature, anatomy, smoothing in centimetres, the pictogram as a preset), Т7 (a
contour deformer whose strength is a blend of the same section radii as `construct()`'s, the style contours as examples,
the soft masses); presets of parts and full-body presets as plain data agents browse, copy and modify (Pavel: presets
matter, presets of parts too). The review of Т5 had found a hard corner at the hip on the rectangle and the hourglass at
full strength and a shelf at the shoulders on the inverted trapezoid and the V. During the work Pavel added to the
requirements that he never wanted people's limbs bent ("limbs as arcs" was where a theme came from, not a rule): the
arc deformer stays as a tool, no full preset uses it, the gallery says so.

**What was done** (all in [engine/](../../engine/README.md); its README has the architecture, the formats, how to add):
- *A deformer framework* (`src/deform.js`, `src/regions.js`): deformers registered with their parameters (the character
  schema and the preset schema take them from there). Two kinds by what they act on: of the figure — a field moving
  every point by where it is and which limb it belongs to, and every joint; on the rest once (frames kept or turned), as
  a pose layer every frame after skinning in the figure's own space (`pelvis` or `upright`), every mesh following by its
  own limb shares, then the floor step (a new stage in `src/figure.js`: mesh layers); of the surface — computed on the
  rest, as a pose layer carried as a morph weighed by strength; those that move joints are refused as layers. Sizes are
  shares of the body's own height at its rest. `regions.js`: the parts along their bones (Т1's segments), each vertex's
  two strongest parts and its share of the five limbs smoothed over the surface, landmarks by height (the waist found as
  the narrowest torso), the mesh tools (smoothing a field, Taubin, normals); neighbours moved into `src/mesh.js`, shared
  with the skinning (nothing moved: the 90 stored cases held).
- *Deformers* (`src/deformers/`): line, squash, contrapposto (Т5); taper, straight, arc (Т5's chains); silhouette (Т5's
  shapes and Т6's cage as one profile of width, depth and forward by height, keys at landmarks, a monotone curve smoothed
  over a share of the height, the arms riding with their root and turning out as far as the new torso needs — the corner
  and the shelf are gone; a "slope" mode that widened the shoulder as a likeness about the neck was tried, creased the
  chest at the armpit and was taken out); proportions and caricature (Т1's `placeIn`, its displacement smoothed a little
  after a pinch was seen at the armpit with longer collarbones; the average of moood's seven scaled to the body's
  height); anatomy (Т1), smooth (Т9's cotangent smoothing); contour (Т7: the body's own sections read as `construct()`
  reads them, Т7's drawn curves in the body's units, strength blends the radii, `own` how much of the small forms ride
  on, edits by part and direction); masses (ellipsoids and capsules at joints in body units, melted in by a smooth union
  along each point's normal: the bust, the buttocks, the shoulder's cap and its slope from the neck); sign (Т4: first
  ported as Т1 carried points onto its distance — the armpit skin tore between the trunk and the arm, as on Т4's own
  picture; per-limb surfaces as in Т1 changed nothing; now the trunk's skin settles onto the sign while each limb's skin
  goes round its own axis onto its stick, blended by the limb shares — no tear at rest).
- *Presets* (`presets/`, 64, each with its label and about in Russian and English, pinned in `presets/index.json`):
  14 silhouettes (Т5's ten re-set at real landmarks — Т5's own keys sat lower than their names: its "waist" was the hip
  bone — and Т6's wedge, column, mass on legs, reed), 6 lines, squash, stretch, contrapposto, 5 limbs, 15 proportions,
  caricature and its reverse, anatomy both ways, smoothing 2/4/8 cm, Т7's three contours, their busts and buttocks and
  the shoulder, 4 pictograms.
- *New bodies from Anny* (`tools/bodies_new.py`, `data/anny/specs.json`): 28 — ages from a toddler to old, women and
  men; thin, heavy, muscular, tall, short; her three origin sliders. Made as Т8's were in one step (Anny run, a head of
  another age blended over the neck when asked, carried onto moood's mesh as a smoothed change from moood's woman, joints
  by Anny's regression); checked first to give Т8's own d-C-hero.bin again within 1e-7 m (6 smoothing steps — the number
  Т8 used was not written anywhere; found by that comparison). Tall and short were first 2.2–2.4 m and 1.2–1.3 m and
  were set back; heavy was too mild at weight 1.2 and is 1.7. `data/bodies/index.json` lists all 59 bodies by group.
- *Full-body presets* (characters): Disney princess (Т8's princess, smoothing, Disney contour, bust, shoulders, small
  hands and feet, taper), Pixar mother, anime girl, Burton-thin (first overdone — the S line zig-zagged a stick figure —
  and set back), pear old woman (with arms off the body as a pose layer: the hands went into the hips walking), V hero
  (longer collarbones made the shoulder boxy and were dropped; contrapposto as an upright pose layer), egg baby, two
  pictograms.
- *The viewer* (`?bodies`): the base body and the deformers of the chosen figure (strength, rest or layer, frames, add,
  remove), URL `&b=…&d=…`; Д1 without `?bodies` is as it was. *The gallery*: Д2 bases, Д3 deformers, Д4 full bodies, each
  with its 3D.
- *Checks*: 157 numeric cases (the new characters in every moment; squash, straight and arcs, caricature, frames turned,
  a silhouette running, lines as layers walking and lying in both spaces, placed and turned, squash as a layer jumping,
  smoothing as a layer, a contour half-strength sitting, a new body walking), 118 pictures, 18 contracts (refusals,
  strength 0 leaves every deformer's body as it is on the rest and as a layer, a figure layer the same at any place and
  heading and carrying every mesh and the joints, a surface layer equal to its rest change, every preset makes a body,
  landmarks in order on five bodies).

**How, to repeat it.** Bodies: `python3 engine/tools/bodies_new.py [ids]` (Anny from github.com/naver/anny, torch),
`node engine/tools/characters.mjs bodies`. Presets: write `presets/<id>.json`, `node engine/tools/characters.mjs
presets`; characters pinned with `characters.mjs pin <ids>`. Pictures: `node engine/tools/sheets.mjs
engine/tools/sheets/bodies.json [names]` → [pictures/engine/bodies](../pictures/engine/bodies/). Looked at front, side
and three-quarter, at rest and in walk, run, sit and lie, close-ups at the hips and the shoulders. Checks: `node
engine/check/units.mjs`, `numbers.mjs`, `pictures.mjs` (then `--update` after looking).

**Seen and left.** The pictogram opens at its thin shoulder when an arm swings far (running, sitting with the arms
forward): the skin gathered at the stick's root spreads under Anny's weights; Т7's seam fix doesn't help — not solved.
Anny's "heavy" stays mild. A contour keeps the body's small forms unless `own` < 1 (Т7's look also came from its
smoothing and proportions; the full presets combine them). The silhouette's "clear" turns the arms out at rest; in
motion the arms are Kimodo's again (`armsOff` is for wide hips).
