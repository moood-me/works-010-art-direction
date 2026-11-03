# Review of the engine, stage 1 — bodies (2026-11-03)

An independent review, by eye and by code; nothing changed by it. Most important first.

1. **The pictogram (`sign`) is broken at rest and in every motion**: a hard step where the arm stick leaves the trunk;
   flat cut feet with ragged rims; a pitted head ball; in run, jump and dance the upper arm thins to a ribbon and
   tears; shoulder tops open in sitting and jumping; hand balls sink into thighs in walk. Edges stretch 9–11× (the
   plain man 3–4×). Cause: the surface is replaced while Anny's skin weights stay; each arm one straight stick ignoring
   the elbow (`src/deformers/sign.js:205,239`); feet are cut stick ends (`:208`). Fix: a rest change carries skin
   weights too (`withRest`), `sign` gives weights from its own parts; one stick per bone with balls at elbow and knee;
   rounded feet.
2. **Figure deformers as pose layers change limb lengths and make planted feet slide**: forearm 0.63× in run with an S
   line, thigh 0.78–1.13× with squash; planted toe slides 74 mm on the base body, 371 mm with squash, 595 mm with the V
   silhouette. Cause: `src/deform.js:83-110` applies a rest-space field to the posed figure in pelvis space. Fix:
   evaluate the field at each vertex's and joint's rest place and carry it through skinning (a rest change applied
   each frame), or express line and contrapposto as turns of the spine chain; add checks for bone lengths and foot
   slide.
3. **Smoothing folds the toes, `anatomy` folds the fingers**: 163/420/858 triangles turn over at 2/4/8 cm; 231 with
   `anatomy-defined`. Cause: `surface.js:33` keeps head and fingers, not toes; anatomy ×1.6 on the finest parts. Fix:
   keep toes; limit anatomy by local mesh size; a check counting turned-over triangles.
4. **Silhouettes and limbs show corners, lumps, kinks**: the egg has a step at body–thighs (legs treated as torso —
   let legs ride with their root like arms); taper makes pin-thin wrists and a shoulder lump (`limbs.js:118`);
   straight-against-curved kinks elbows (`limbs.js:128-133`); `onChain` splits by projection on the shoulder–wrist line
   (`limbs.js:95`), so at a bent joint a layer jumps between bones; broad shoulders square with an armpit notch; long
   neck stalk-thin.
5. **Shoulders boxy with arms raised (jump) in every preset** (from skinning, inherited); hands brush the thighs in
   walk even with `armsOff`.
6. **Rest and pose layer anchor differently**: a rest line keeps the pelvis on Kimodo's path, a layer keeps the feet
   and moves the pelvis 155 mm off. The engine should say which it promises.
7. **Order and composition**: pose layers don't run in the written order (the pose's own first, figure deformers after
   skinning, `engine.js:86-91`); mesh layers move joint places (`pose.P`) not turns (`pose.Q`); `caricature` scales the
   average body about the origin, not the hips (`proportions.js:195-196`).
8. **Performance**: each figure layer 2–3 ms per frame per figure; per-vertex allocations (`deform.js:88-89`,
   `limbs.js:95-106`); fields rebuilt every frame (`silhouette.js:37`); `layerMorph` caches by strength though computed
   at 1 (`engine.js:99`).
9. **Hard-coded**: the sign's trunk at x = 0 (`sign.js:199`); absolute metres in the sign (`:216-219`), masses search
   (`masses.js:144`), contour fallback (`contour.js:110`); the neck always along +y (`proportions.js:153`); silhouette
   turns arms only in the front plane (`silhouette.js:56-74`).
10. **Duplication**: `keepUnused`/`copyUnused`; `smin` twice (one without the k ≤ 0 guard); `normalsAt`/`normalsOf`;
    vector helpers re-declared instead of `math.js`.
11. **Checks see change, not quality**: nothing measures torn or stretched skin, turned-over triangles, bone lengths,
    foot slide, feet above the floor, order dependence, deformers on bodies other than the woman. Fix: quality
    contracts with limits.
12. **Presets and viewer**: presets plain and easy to copy; silhouette keys are positional tuples; full presets can't
    be taken as a part ("princess plus my changes" = copy the file); with three figures the panel runs past 850 px and
    the add-deformer control is cut off; "Тело" and "Основа" read as the same.
13. New bodies plausible; the three origins barely differ; "heavy" mild.

**Not checked:** gallery pages Д2–Д4; Python tools; all 64 presets (25 on rest, 6 as layers); DQS/LBS with deformers;
chains; browser frame rate; hands closely; lying from more than one view. Pictures in the scratchpad `rv1/`.
