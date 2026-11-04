# Review of the engine, stage 2 — heads (2026-11-04)

An independent review, by eye and by code; nothing changed by it. Most important first. Pictures in the scratchpad
`rv2/`.

**Holds:** units (23) and `quality --only heads` (303) pass; old characters didn't move; Г3's and Г1's heads look like
their experiments and hold in look-round, walk, run, dance, jump, sit, bow with CoR, DQS, LBS; volume eyes sit well.

1. **Anny's own face settings crumple the face** (head-anny-face; the toddler's lids): `data/anny/face.json` has
   one-vertex spikes (3–10 mm off the neighbours' mean; 87 in chin-height) at lips, nostrils, lids, jaw —
   `tools/face_targets.py` samples Anny through `map.npz` unchecked. The check was fitted to it (`quality.mjs:206`, 9×).
   Fix: map leaving lids, inner mouth, eyeballs out, or drop vertices moving unlike their neighbours; a spike contract
   per change; the limit back near the plain body's.
2. **Painted features don't follow the form nor sit on the mesh's features**: the picture projected after all form
   changes (`head.js:72`), features in fixed head units. A change after the wrap moves the lip seam, not the painted
   mouth — opening shows dark stretched skin like a tongue; on unwrapped heads dot eyes land under Anny's sockets;
   head-old's grin tears open (seam at `wrap.js:99` through the painted teeth). Fix: picture coordinates on the body
   right after the wrap (or Anny's own surface); features against `landmarksOf`; a grin's seam between teeth and
   inside; a contract in mm for mouth line vs lip seam and eye centre vs eye landmark.
3. **Rigid pieces don't take form changes**: big head as a pose layer leaves hair small (bald, hair inside the head);
   any head-form layer under a nose or hair; the nose piece ignores expression morphs (`figure.js` applies rest layers
   to skinned meshes only). Fix: pieces as skinned meshes on the Head joint through `forMesh`, or refuse.
4. **The hood is a garment as a rigid shell**: through the shoulders and arms in look-round, run, dance, jump;
   71,794 vertices; head-old 10.3 ms a frame against 2 ms. Fix: to the clothes stage, or a coarser step
   (`pieces.js` `extra`).
5. **The head–neck join worse than in the experiments** (hidden there under a turtleneck): tails — a jaw and ear
   bulge under the jaw with a stepped fold; blond — a chin shelf; old — a nape shelf. The check misses it (`sharpest()`
   only where the head share is 0.05–0.7; head-old's own 60° limit by name, `quality.mjs:226`). Fix: measure under the
   jaw too, no per-character limit.
6. **Some checks can't fail**: the face mask re-tested by its own formula (`features.js:201` vs `quality.mjs:228`);
   `reliefGap` re-measures `attach` (always 0). Missing: DQS/LBS, a body deformer, jump, bow, pieces through the body,
   expressions in motion.
7. **The overlay check measures the mesh, not the drawing**: mouth corners are the lip seam the wrap widens; the
   outline is the silhouette with hair; head-red-mine scores better than head-red. Fix: points from the painted
   features or the form's marks; the face contour without pieces.
8. **Presets hard to combine and change**: a head preset bundles form, features, hair, hood inline (250–340 lines);
   hair and pieces have no `{kind: "preset"}`; a feature replaced by id, not merged (18 fields restated to switch
   `as`); a base's form can't be taken away or weakened (no `off`, no strength on `head.preset`) — short of "ways
   combinable with a strength"; the viewer has no features preset choice.
9. **Light**: the ball nose's highlight baked from a fixed direction (`pieces.js`); nose tint and blush lost under a
   nose piece (Jesper's pink nose); shadow acne on hair in plain light; soft-form looks like plain on Red; in toon the
   hair's cast shadows as grey blotches on the body.
10. **Build time**: 11–13 s per wrapped head in node on every load (200 rounds of fold easing, a dense biharmonic
    solve); Д7 about 90 s. Fix: store the wrapped rest pinned by the form's hash, or cheaper rounds.
11. **Duplication**: landmarks twice (`face.js` `landmarksOf`, `wrap.js:105-113`); head-size ratio ×4; default head
    size 1.1 ×4; `num` in 6 files.
12. **Hard-coded**: metres in `wrap.js` (`:40`, `:54`, `:67`); colours in pieces and the grin, the hood's ink; fixed
    lifts in expressions.
13. **Hooks**: `figure.headShape()` reads a pose only `step()` sets (stale after `frame()`); no jaw or expressions,
    no gradient; no neck shape for collars.
14. **Versioning**: how heads are built (wrap rounds, paint, the face mask) is unversioned code; the painted picture
    is not in the numbers.
15. **Minor**: relief ids swapped by side (`features.js:262`); the expression layer overwrites a morph of the same
    name but sums paint asks (`layers.js`); `heads.mjs` runs slices of experiment pages through `new Function`;
    Giulia's solid shipped as a preset though rough; the viewer's face close-up off-centre, the heads panel below the
    fold at phone width.

**Not checked:** `face_targets.py`; the full numbers and pictures checks; every combination of the 11 form presets;
cage, warps, headOf on other bodies; volume brows and mouth; hands near the face; browser frame rate; the gallery
beyond loading; heads lying or rolling.
