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
