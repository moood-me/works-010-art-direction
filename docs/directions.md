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
  On other people: dresses and long garments hold on other bodies; knitwear and coats don't. In motion (walk, jump,
  sit): cloth physics with the designed form as rest shape is the first that looks like a dress moving — bell and
  A-line keep their silhouette, the knee pushes the cloth softly; sitting still breaks (the skirt sinks under the
  thighs — it needs collision with the top of the legs and the floor, and a weaker pull to the form when sitting).

**Decided with Pavel (later):** clothes go onto the good bodies (A's designed forms, cage silhouettes, moderate
stylisation); dresses in motion keep going with cloth physics ("Чудесно"); the wrapped heads are to be made
beautiful by looking and trying, bugs first; the 3D-heads agent may change its tool to one face mesh moved by
landmarks and curves, independently, and must not come back with a mediocre result; a dedicated hair tool is started
(big locks along guide curves merged into a hairstyle with its own silhouette). Assembling a whole character from the
best parts and converging the head paths into one — "пока рано".

**Pavel on Anny's own space:** "так хорошие же тела! почему мы их не используем?" — Anny's native settings give real
bodies; the cage (path 9) can be laid on top a little for artfulness; clearly better than the drawn bodies of path 7.
Agreed: Anny first, our form on top.

**Head paths fixed for now (Pavel will look at home).** What each head path brought that the others lack:
- Г2 (face mesh on a drawn form): an overlay check against the picture in its angle, error in pixels; lids and lips
  cut along Anny's mesh edges so they can move; the face form drawn straight under the mesh.
- Г1 (anime heads): drawn features on the skin (eyes, brows, lips) and toon light with an outline — what makes the
  faces cartoon and alive; noses and mouths from their own curves; a dome skull instead of an egg.
- Г3 (wrap): the profile laid point by point along the drawing's line; folds found and eased; a long nose as its own
  piece over the mesh.
- Т5 (deformations): changing the form with the joints moving along.

**Pavel at home, on the gallery:** О3 (cloth) — "более-менее классно. на самом деле классно"; Т5 — "примерно понятно",
Т5-з (body as one shape) — "нравится, теперь понятно к чему она"; В1 (hair) — "все пластилиновые! улучшай"; Г3 —
"неплохо". He asked for the 3D view to be large and comfortable, without its own scroll, and for the controls to stay.

## The engine view (talk with Pavel, 2026-11-03)

We make an engine: few assumptions, much allowed; examples of preset bodies and of recommended deformations; the agents
who write concrete characters have their own vision, choose the tools and are responsible for moderation themselves —
the engine doesn't guard them from mistakes. A deformer that can apply both to the rest shape and as a pose layer should
offer both. Where it ends up (baking or the engine) is not thought about now — later, from this repository.

Bodies: Т8 (Anny's own settings) as the base and Т5's deformers on top (with the cage Т6) — agreed as the direction,
not combined yet. From Т7 to take into it: the two posing fixes (the clavicle takes a third of the arm drop; skin
offsets smoothed over the surface) into the common skinning; a contour deformer that edits a body's own contour curves,
with a strength from "touch up" to "replace with a drawn form entirely"; the style contour presets (Disney, Pixar,
anime) as examples; the soft separate masses (bust, buttocks, the shoulder cap and slope from the neck). The clothes О1
then move from Т7's bodies to the new ones. With these taken, nothing of value stays in today's Т7 but its pictures.

Heads (same talk): the base is always Anny's head mesh (alive, no seam, moves with the skeleton). Its form by a set of
ways that combine with a strength: Anny's own face settings and a head of another age; deformers on top (face by
points, a cage on the head, smooth warps); a designed form the mesh is wrapped onto (as Г3), made from a drawing's
curves (as Г1) or as a solid fitted to a picture (as Г2); separate pieces where the mesh won't stretch (a long nose, a
ball nose). Features as a separate layer, per feature: painted on the skin or as volume, mixable. Expressions by the
mesh with painted features following. Face light as an option (toon with outline, shading from the designed form, no
cast shadows on the face). For authors: an overlay check against the picture; our heads as preset examples. Dropped:
the old sculpting by balls (Г2's first way), the rays of Г4, and a standalone head without Anny. Not doing now:
blending expressions, mouth shapes for speech, a gaze that follows.

Characters not from Anny (same talk): П1 and П2 differ in one thing — how a body part is built and bends: merged
simple forms skinned to bones (П1) or sweeps along curves through the joints rebuilt every frame, bending in an arc
(П2). One constructor for them: a shared SOMA skeleton with the character's own bone lengths; per part a choice of
"form" or "sweep" (mixable); shared things on joints keeping their orientation; one face library (a drawn layer on the
head, eyes, brows, mouths, marks, expressions from both); one look (tones, outline, plastic or clay); one Kimodo
retargeting with options (amplify limbs, push arms out of a big head, damp head and spine bends); all our characters
rewritten in one description as presets.
