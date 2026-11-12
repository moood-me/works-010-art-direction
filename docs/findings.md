# Findings: other people's tools, drawn styles, drawings to 3D

What three rounds of work found (2026-11-03/04), for the agents who come next. Details, numbers and how to repeat are
in each page's `notes.md`; the briefs the agents worked from are in [briefs/](briefs/).

## The main finding

**Draw first, then build the 3D from good ready bases fitted to the drawing.** An agent draws a character in a
style taken from real works (rules written from samples, the drawing in SVG by code), and the 3D is assembled from
artist-made bases — Anny's body on SOMA, a head from Blender's Human Base Meshes — fitted to the drawing's front and
profile, with the face and colour from the drawing's own code, judged by overlaying on the drawing. Four of five
characters made this way came out close to their drawings and attractive (`to3d/` Р1–Р4), better than anything built
from parameters before. Decisions about beauty are made where an agent makes them well — on the drawing — and the 3D
follows.

## Drawing styles (`styles/`)

- Taking a style from real works and writing its rules from samples gives far more attractive characters than
  inventing a look. The same cast in twelve styles makes the styles comparable.
- SVG drawn by code is native for flat and graphic styles: graphic flat (С3), mid-century gouache (С9), 1930s rubber
  hose (С11), pen and watercolour (С12), ligne claire (С10), Klaus-like light (С2) came out best.
- Styles drawn by projecting a 3D proxy (Pixar С1, Arcane С4) looked like dolls and mannequins: the life of drawing
  is lost. A proxy is good for consistent turnarounds; the look needs drawn decisions on top.
- Weak everywhere: hands (hidden, mittens, tubes), stiff standing poses without a line of action, an even line
  without pressure. Women's faces are harder than old men and children — caricature carries those.
- A style's drawing code is reusable: shared parts (head, face, line, colour) apart from per-character modules; each
  style's `notes.md` says how to add a character.

## Drawing styles, round three (six characters, sixteen styles)

- **Adding a character by a style's own code works.** Twelve agents who had not written the styles drew two new
  characters into them from `tools/` and `notes.md` alone, and in every style the new two stand beside the four as
  their own. The shared code only had to be extended (a beard, curls, a laughing mouth, a hand with fingers, a line
  of action for the whole figure), never rewritten.
- **A caricature carries; a subtle young face doesn't.** Марат (a big bearded laughing man) came out warm in all
  sixteen styles at the first try. Кира (a sullen girl of fifteen) had to be redrawn in three styles and stays the
  weakest in several: she reads older, gaunt, or as a boy. A fringe over one eye is a trap in three-quarter view —
  what remains of the far side of the face (a nose tip, one eye) reads as something else; show both eyes, or keep the
  nose inside the face shape.
- **A described pose gives a line of action.** "Laughs with the whole body, a ladle up, a fist on the hip" and
  "slouches, looks from under the brow" gave the liveliest figures in several styles, livelier than the four, who
  were described by character only.
- **New styles that suit SVG by code:** layered cut paper (С14: every form a piece with its own edge, a light rim and
  a shadow on the layer below — filters do the material), the woodblock print (С13: a line with pressure, a flat
  pattern laid over cloth without following folds, hairline strokes at the hairline), pixel art (С16: sprites typed
  as character maps, portraits on a larger grid), noir (С15: the black shape does the drawing; faces strong, bodies
  of straight pieces still wooden).
- **Still weak everywhere:** hands (one of Кира's is in a pocket in almost every style), profiles (simpler than the
  three-quarter view), bodies in the styles built from a 3D-like proxy (С1, С4, С7, С8).
- A full rebuild of some styles (С5, С7) doesn't reproduce the committed pictures of the four exactly — build only
  the new sheets there (each `notes.md` says how).

## Drawings to 3D (`to3d/`)

- **Bases.** Anny's body (engine packs, SOMA, Kimodo through the engine) for human proportions; Anny's child bodies
  for children; for 2–3 heads tall, our indie constructor (`experiments/indie`) — a human body can't be bent into it.
  Heads from Human Base Meshes (CC0): the "animation" head for ligne claire, the stylised one fitted by points
  elsewhere; fitting by points of the silhouette works, fitting by height slices gives folds.
- **Faces.** In drawn styles keep the face as a drawn layer: the style's own SVG functions projected from the front,
  redrawn each frame from a few numbers — expressions match the sheet line for line. A modelled eye with lids (Р2)
  suits a style whose eyes are dots in lids. Close eye sockets and lips of the base with a smooth patch when the
  features are drawn.
- **Where the drawing lies.** Drawn front and profile often don't make one head (the eye deeper in profile than the
  front allows; three-quarters drawn at different angles for eyes, ear, nose). Follow the front and say so.
- **Looks.** Flat colour + one shadow step + outline works in the browser; ligne claire via Blender Freestyle, an
  even pixel outline in the browser; Klaus light (warm key, lilac shadow, rim, cast shadows) works on the head but
  blotches appear where face normals aren't smoothed. Running the render through the drawing's own SVG filter keeps
  paper and gouache (Р3).
- **Alive.** Blinks at uneven intervals (close ~70–80 ms, open ~140–170 ms, also on big gaze shifts), saccades with
  holds of 0.2–1.6 s, the gaze leading a head turn by ~0.25 s, speech as syllable mouth shapes with pauses, expressions
  blended — schedules from a seeded random stream, no sines; the same moment always looks the same (scrubbing works).
- **Motion.** Kimodo's motions retarget well onto these bodies. Weak: `idle`/`stand` stoop or bow the head; short
  arms make waves tiny and hands reach the ears; sitting puts them on the floor. Clothes and hair are skinned shells,
  not cloth — skirts in a wide step stretch like trousers.
- **Not good yet:** realistic Anny hands against drawn mittens (replace them), shells for clothes and hair, the
  hardest face (a young woman in a painterly style, Р5).
- Engine note: centres-of-rotation skinning takes ~15 s to prepare on a 48k-vertex dressed mesh — too slow for the
  browser; viewers used dual quaternions. Worth an issue.

## Drawings to 3D, round two (all twelve styles)

One character from each remaining style, same brief, the five done as examples (`to3d/` Р6–Р12; the menu shows each
one's style and name, e.g. «Р1 (С3 Аня)»; folders keep the Р numbers). Out of twelve, ten came out good and alive.
- **Bases follow the style, not one recipe.** When a style's drawing code already builds a volume (С4, С6, С7, С8,
  С10), fit the bases to those numbers — all views agree at once. Proportions far from human take our constructors:
  indie (П1) for 3 heads tall, the expressive one (П2: arcs through the joints, ball head) for 1930s rubber hose —
  still on SOMA, still Kimodo through the engine.
- **The look can be drawn each frame from the 3D.** Pen and watercolour (Р12): silhouette and crease lines taken from
  the 3D each frame and drawn with the style's own pen code, washes as offset masks under its own filter — reads as the
  drawing, not a shader. Symbolic (Р8): no face, mood by pose and breath, the rim light moving with a real lamp.
  Stop-motion (Р10): Cycles materials (resin skin, glass eyes, ribbed knit), 12 frames a second, replaceable mouths
  and brows like Laika's. 1930s (Р11): head squash and stretch on a spring, a wobbling ink line, black-and-white film.
- **Following the style's rules over a weak drawing** (Arcane Р7) gave a face better than the drawing but a figure of
  real proportions that no longer matches it.
- **Weak spots repeat:** open mouths without a tongue or teeth read as holes (Р6); big modelled eyes can look staring;
  realistic Anny hands; skirts and coats as shells; a big head makes Kimodo's wave cover the face.
- Viewers load slowly in software WebGL (centres-of-rotation skinning on ~70k vertices takes about a minute).

## Drawings to 3D, round three (two more characters in each of sixteen styles)

Thirty-two characters (`to3d/` Р13–Р44). By the orchestrator's eye: strongest where the 3D is built from the
drawing's own forms and drawn by its own code; weakest where a realistic base carries a stylised look.
- **A second and third character in a style cost much less than the first, and come out better.** Every agent
  started from the style's first character and turned its code into "shared part + one file per character"; several
  fixed the first one's named weaknesses on the way (fingers lying as drawn in С7, a mouth with a tongue in С1, a
  drawn mouth in place of modelled lips in С10, a viewer that opens in a second instead of ninety in С7).
- **Build from the drawing's own numbers where the style allows.** Best matches: indie (Р21, Р22 — hard to tell from
  the drawing), rubber hose (Р33, Р34), symbolic (Р23, Р24), ligne claire (Р31, Р32), stop-motion (Р27, Р28 — the
  3D is better than the drawing). No Anny body and no base head at all in С6, С14, С15, С16: inside the shape there
  is nothing in those styles, only its edge from every side.
- **A realistic base under a stylised look is the weak way.** Arcane (Р19, Р20) and Pixar's Кира (Р14): the base's
  brow, nose and jaw give a hard adult face; shadow edges on a real head break into blotches; real proportions are
  wider than the drawn figure; real hands on thin drawn arms. Sending С4 back fixed defects (a lump of body showing
  under the hoodie, wedge boots, shard-like hair) but not the face.
- **How each new style lives in 3D** (first tries, all four worked):
  - woodblock print (Р37, Р38): the 3D is never shown; every frame is printed again by the drawing's code — flat
    colour, the pattern laid flat and not following the body, a brush line found on the 3D, the sheet's paper, frame
    and seal standing still;
  - cut paper (Р39, Р40): a paper puppet in space — every thing a piece of one colour on the skeleton, the paper
    (edge, short and long shadow on what is farther, light rim, grain) made in one pass over the picture, light
    fixed to the picture, 12 frames a second;
  - noir (Р41, Р42): a few flat faces by the drawing's numbers; a face turned to the light is flat colour, turned
    away or covered is solid black, so the black stays clean straight-edged shapes and moves as the figure turns;
  - pixel art (Р43, Р44): each body part typed as character maps from the front and the side, a voxel per pixel,
    seen through the sprite's grid; parts move by whole pixels and turn in steps, so pixels don't crawl; the front
    view is the drawing pixel for pixel (89–96 %), the portrait stays a drawing.
- **Where the drawing lies, again.** Front, three-quarter and profile of a drawing are often not one head or one
  figure (a fringe that is a different piece in front and in profile, shoulders wider on one sheet than another,
  feet drawn sideways under a body seen from the front). Agents followed the front or the figure sheet and said so.
  Where a style had no turnaround or expression sheet for the character (Вера in С1, С7, С10; Тим in С3; Савелий in
  С8), the agent drew them with the style's code into its own folder; the style's page was not touched.
- **Poses of the drawings are mostly lost.** The ladle, the fist on the hip, the bunch of flowers, crossed arms:
  there is no such motion in `engine/motions`, so the 3D stands plainly. Where an agent set the drawing's pose by
  hand as a rest pose (Кира's slouch built into the body in С3, С5, С7; Марат's laugh in С12, С13) it holds through
  every Kimodo motion and is what makes the character.
- **Kimodo on unusual bodies:** `idle` stoops and drops the head on almost everyone and was left out or replaced by
  the first frame of another motion; `bow` is too deep; `wave` ends at the cheek on short arms and suits a big man
  (Марат) best; a stoop built into the body adds to `sneak` and bends too low; sitting pushes legs through skirts
  and aprons.
- **Still weak everywhere:** clothes and hair are shells, not cloth; hands; open mouths on modelled faces; profiles.
- A slip to know: the earlier viewers of С5 (Р4) stretch the figure when the control panel is open — fixed in Р21
  and Р22, Р4 itself not touched.

## Drawing styles С17–С20 and drawings to 3D Р45–Р50

Four more styles unlike the sixteen (Bilibin and Art Nouveau, black-and-white seinen manga, low-poly facets, Soviet
animation of the 1960s–70s), all six characters each, by part B of `briefs/styles-more.md`; then one character of
each of С15–С20 into 3D by `briefs/to3d.md` (Р45 Аня noir, Р46 Савелий pixel art, Р47 Вера Bilibin, Р48 Вера manga,
Р49 Марат low-poly, Р50 Кира Soviet).
- **Styles.** Soviet animation (С20) and low-poly (С19) came out best: a bold caricature with the face as bare
  paper; a line of faceted figurines whose turns are honest because the drawing code builds real 3D. Bilibin (С17)
  works as a fairy-tale page by moving the ornament onto today's clothes (shawl, knit, embroidery). Manga (С18) is the
  weakest: wooden bodies, simple faces — an exact adult face is what that style lives by, and it is the hardest.
- **3D.** The strongest ways: rig the style's own 3D model on SOMA when its drawing code already builds one (Р49
  matches its drawing point for point); for pixel art, render small and let the style's pixel rules decide every
  pixel, the 3D only answering material, light and depth (Р46); draw each frame with the style's own pen, tone or
  print from the 3D (Р48, Р50 — the Р12 way); in noir, keep the black as designed shapes whose edges stay on the
  drawn lines while the light moves (Р45).
- **Duplicates.** Two more were made in this round — Марат in С13 and Кира in С14 — the same characters as Р38 and
  Р40 of round three. Side by side, Марат came out about equal (a livelier figure, a weaker profile) and Кира worse
  (softer, papier-mâché rather than paper); Pavel decided to keep main's and not bring these two in.

## Other people's tools (`tools-demo/`)

- **Better than ours:** Blender Studio's character heads (Rain, Snow…, CC-BY) — eyeballs under thick lids, lips with
  a rim, mouth corners into cheeks, loops around eyes and mouth, expressions as skin motion. Use as a model and as
  parts (eyes, teeth), not whole characters. Human Base Meshes (CC0) are the bases used in `to3d/`.
- **Partly better:** GarmentCode — garments as sewing patterns sewn and draped on Anny, honest fit and folds; realism
  only, rest only, 4–17 min per garment on CPU (its simulator's licence is non-commercial). MToon — a cleaner shade
  and outline, but beauty comes from the artist's textures, not the shader.
- **Not better:** libigl (our deformers stand on the same maths; ARAP keeps limb thickness — worth as a layer over our
  arc), Blender cloth and HOOD against our О3, Blender hair (a realistic wig, not cartoon locks), Monster Mash (soft
  joins, flat depth). HairDeck looks right for stylised hair with springs, but its main path needs a GPU and two gated
  models (SAM 3, DINOv3).
- **StdGEN (picture → 3D body, clothes, hair).** Guesses the shape from all sides in ~3 min on an A100; surfaces are a
  cheap-toy draft (blotches, holes, smeared faces). Cleanest on flat simple styles; breaks on strong caricature, on
  silhouettes, on painterly and watercolour. Its copy `completelyreal/StdGEN` on Hugging Face needs Python 3.10 and
  pydantic 2.10.6 pinned; it doesn't fit 24 GB. Useful at most as a hint for unseen sides.

## Working

- One agent per page with a common brief, working only in its folder and a cache outside the repository; the
  orchestrator looks at every result and commits. Asking every page for "what the tool does in its own cases" made
  the tool pages understandable.
- The studio's Kimodo GPU can take longer than 25 minutes to wake; an order may fail with `wake` and succeed later.
