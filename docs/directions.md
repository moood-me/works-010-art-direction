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
