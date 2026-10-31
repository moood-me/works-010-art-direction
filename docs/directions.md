# Directions

Where the work on people goes now, and why.

## The approach

Pavel wants breadth now: to look at a wide spread of forms and styles, find the principles of beauty, and learn,
instrumentally, to do everything needed to make the characters he wants. Not inventing two characters and polishing
them. Motion, poses and scenes are not the focus now — the form is.

## Two directions found by looking

- **The designed form is primary.** Going from the real body and removing things gives a blurred real person. Per
  style, the contours are drawn as deliberate curves, and Anny's mesh is pulled onto that form (she keeps proportions,
  joints and topology, so motion still sits). First result: Disney and anime bodies below the neck clean and whole,
  but with little rhythm in the contours yet.
- **Judge on a dressed person with a face.** The player sees head, hands, silhouette and how clothes sit. First
  result: clothes sit; modelled eyes, brows and mouth give the cartoon quality — Pavel: where it puts in cartoon
  elements it looks good, the cartoon quality comes exactly from that; it needs work on aesthetics and forms so it
  isn't ugly. Cartoon eyes on Anny's realistic lower face clash; MakeHuman hair reads as a helmet.
- **Together:** the dressed person with the face and body drawn as a form, hair as designed volumes, and the face
  built as in [references.md](references.md) (around the eyes, the eye as skin, drawn features on the form, coupled
  proportions, expressions).

## What we didn't do, technically

Asked "what, in implementation, are we not doing", the answer was seven things; Pavel asked to do them all.

1. **A cage deformer** — a coarse shell around the body that it follows smoothly and whole (harmonic or mean-value
   coordinates, a lattice): the silhouette changed in one gesture, not part by part.
2. **Landmark deformation** — points (eye corners, nose tip, chin, shoulder, knee) told where to stand, the rest
   follows smoothly (RBF). Above all for the face: put cartoon face proportions directly by points.
3. **Anny's own shape space** — her phenotype sliders and ~1250 local targets made by people. We bent seven frozen
   bodies from outside; Anny herself (open source) can give forms by her own means. "Take Anny's sources and see what
   can be sculpted from her."
4. **A mesh that adapts to the form** — remeshing or subdivision where strong stylisation stretches Anny's mesh; only
   if it doesn't spoil skin weights, joints, motion, garments.
5. **The right smoothing operator** — cotangent Laplacian / mean-curvature flow, so smoothness follows the real
   geometry; the uniform one left nipples, navel and toes because Anny's mesh is twenty times finer there.
6. **Face and hair as parts with their own builders** — the eye with its socket and lid; hair from locks along guide
   curves.
7. **Clothes with their own form** that simplify with the body — a skirt's bell, a coat's block, stiffness, folds as
   design — down to the garment as a sign.

## For other kinds of characters

From the indie and expressive references ([references.md](references.md)): a constructor of characters from simple
forms with its own skeleton; limbs bending along a curve; a graphic face that changes a lot; things as part of the
silhouette; non-human heroes.

## Results so far

- **Anny's own space** ([experiments/anny-space](../experiments/anny-space/README.md),
  [pictures](pictures/anny-space/)): proportions made by people hold to about twice the slider range; a head of another
  age on an adult body gives doll-like cartoon proportions with a whole head. The surface stays realistic and there is
  no cute face — so Anny goes first (proportions, childlikeness by her own means), our designed form, simplification
  and face on top.
- **Deformation tools** ([experiments/form-tools](../experiments/form-tools/README.md), [pictures](pictures/tools/)):
  smoothing in centimetres cleans small forms without thinning limbs; the cage changes the whole silhouette smoothly
  and gives the clearest new range of forms; face by points reads but twenty points are too few for strong changes;
  subdivision is harmless and brings little, remeshing is not the path. The tools change shapes cleanly but don't
  supply taste — the presets are rough guesses.
- **Expressive faces and bends** ([experiments/toon](../experiments/toon/README.md), [pictures](pictures/toon/)): about
  5 of 11 appealing (imp, grin cat, jester, rabbit, TV robot) — each holds one shape language, a big head with the face
  filling it, and one strong feature. The drawn face carries the character while its features are big; one arc per
  limb makes the rubber-hose look. Weak: torsos as lumpy tubes without designed sides, legs tapering too little, small
  faces on stick bodies.
- **Indie heroes** ([experiments/indie](../experiments/indie/README.md), [pictures](pictures/indie/)): about 12 of 18
  pleasant as toy characters — the first result nice to look at. Beauty holds on the silhouette and one main thing, not
  anatomy; a head of half the height and tiny legs make a hero cute almost without effort; two or three colours; eyes
  as two dark dots set low and wide. Limits: glossy plastic without colour zones or outline; hard heroes (stone,
  robot) need separate pieces, not one smooth form; short arms hide behind the head, so motion must be exaggerated
  and spread; held things need their own orientation.
  Second version: about 17 of 24 alive and charming. Expressiveness comes from a face of two or three graphic signs
  that change shape (lid, brow, mouth) together with the tilt of the whole figure; pose and feeling must agree; held
  things need their own orientation. Pavel: "развей их, делай ещё и стильнее" — one direction among the others.
- **Dressed, with a face** ([experiments/dressed](../experiments/dressed/README.md), [pictures](pictures/dressed/)):
  of 72 generated characters about 12 pleasant, 4–5 close to beautiful, none beautiful in the film sense. What beauty
  seemed to depend on: hair that frames the face (bob, shoulder length); an open upper lid; a soft drawn face with a
  small nose; moderate stylisation and girl or child proportions; two or three clear colour blocks with hair
  contrasting skin and clothes; a mouth contrasting the skin; big eyes only with a round, childlike face. Holding it
  back now: realistic crease-heavy garments bunching on stylised bodies, the dead A-pose, ragged hair edges, faces
  still long below the eyes, thin long necks.
- **Heads from anime and drawn references** ([experiments/heads-anime](../experiments/heads-anime/README.md),
  [pictures](pictures/heads-anime/)): 3 of 9 fair, TV-cartoon level; a drawn face on a designed head reads better than
  modelled eyeballs. What stops them: the profile — a drawn face on a smooth egg has no nose–lip–chin line in side view;
  hair as ribbons reads as plastic panels, as a mass as a helmet — missing the rhythm of a few big designed clumps;
  brows hidden under bangs; no edge loops around eyes and mouth.
  Second version, after Pavel's note: chins, noses and mouths now differ (pointed, square, round, jowly, long; tiny,
  button, straight, upturned, ball, long wedge; line, pout, smirk, crooked grin, lips) — four heads close to their
  picture at its angle. Still: hair approximate (panels and helmets), features painted by front projection, the
  angular teen boys came out round and babyish.
- **Clothes with their own form** ([experiments/clothes](../experiments/clothes/README.md),
  [pictures](pictures/clothes/)): dresses are the best — six of eight silhouettes clean and readable as a designed
  garment; the dress's ladder from cloth to sign works on all four steps, the cone-sign reads. Weak: knitwear and coats
  (sleeves turn into boxes or ridged frills, a tight sweater reads as skin with muscles), MakeHuman's front slit with a
  ragged hem.
- **Heads from 3D-cartoon references** ([experiments/heads-3d](../experiments/heads-3d/README.md),
  [pictures](pictures/heads-3d/)): none beautiful, three recognisable by type (Gwen, Go Go, Marco). One template moved
  weakly gives one face to all; hair as cap plus ribbons reads as a helmet; eye and skin joined with a dark hollow
  under the eyes. Sent back with Pavel's notes on the anime heads (per-reference proportions, lines and curves, neck).
- **A and B combined** ([experiments/combined](../experiments/combined/README.md), [pictures](pictures/combined/)):
  none beautiful, and uglier than the drawn-face heads — Anny's head laid onto a drawn form leaves lumps: a hollow bowl
  around each eye, the lower face bulging like a muzzle, an undefined join to the neck; MakeHuman hair as helmets. The
  eye itself close up became good. Of the head approaches, the drawn face on a head lofted from its own curves
  (heads-anime) goes furthest.

**Decided with Pavel:** the dressed characters (B) are kept as the base "body plus clothes" and as a set of findings;
their faces and MakeHuman hair are dropped. The head will come from the work on heads (a drawn face on a designed
head, wrapped with Anny's mesh) and be joined to B's bodies and clothes later.
- **Kimodo on indie heroes** ([pictures](pictures/indie/motion/)): most motions sit — walk, run, jump, dance, sit,
  stomp, idle: real weight and shift, cute on short heroes. Wave works only with the arm pushed out of the head; the
  bow breaks (a human 90° bend with a half-height head puts the face on the floor) — big heads need head and spine
  bends damped and limbs amplified; a ghost needs its own motion; feet slide; real motion lacks cartoon clarity
  (strong poses, holds).

**Pavel on the expressive faces and rubber-hose characters:** "супер охуенно и супер ценно… я люблю тут всех
персонажей… практически готовый вариант персонажей; если Kimodo может ими управлять, это отлично подойдёт для некоторых
игр."
  Pavel on the second versions of the expressive characters: "новая стала лучше, да, отлично" (first versions kept).
- **Wrap of Anny's head onto designed heads** ([experiments/heads-wrap](../experiments/heads-wrap/README.md),
  [pictures](pictures/heads-wrap/)): technically works — the designed look held, no lumps, no seam at the neck, blink
  and an opening jaw as real mesh. Attractiveness no better than the designed heads, in places worse (faint shading
  marks where Anny's features were; the mouth opens as a ragged "o" — lips need their own rim laid on drawn curves).
