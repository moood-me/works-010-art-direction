# 2026-11-04 — the engine's heads after review 2

**What called for it.** The independent review of stage 2 ([reviews/2026-11-04-engine-heads.md](../reviews/2026-11-04-engine-heads.md),
15 findings). The lead agent passed it on with Pavel's notes: the old man's hood stays as it looks (part of the
character) but cheap, its going through the body left to the clothes stage, and the same for any garment a head
carries; the old man's grin tearing when the mouth opens is a visible bug; the checks must measure quality, not be
fitted to what the heads measure — the plain body's limits back where the fix allows, and plainly said where not;
hair, pieces and features as presets of their own, features merged by id, `off` and a strength for a base's form;
wraps stored pinned by hash; how heads are built versioned. Rules as always: the right ways, no workarounds, no dead
code, nothing of the experiments or the gallery broken, existing characters unchanged unless meant.

**What was done, finding by finding** (the engine's README has how it works now).
1. *Anny's face crumpled.* Two causes, both in how `tools/face_targets.py` carried her changes onto moood's mesh
   through Т8's closest-point map: moood's lips and lids found their closest point on Anny's teeth, tongue and eyeballs
   (her mesh's other pieces), and where the two faces lie a few millimetres apart on the other lid or lip. Now the head
   is mapped anew: Anny's skin alone (her mesh's largest piece) is laid onto moood's head by a smooth fit (non-rigid ICP,
   stiffness eased round by round: moood's head from Anny's 0.4 mm apart on average against Т8's 3.1), and each moood
   vertex takes its place on it (vertices moving 2 mm off their neighbours' mean, summed over every change and sign:
   69, against 643 before); what still moves unlike its neighbours (moood's eyes are closed slits, Anny's open) is let
   go and filled in harmonically. `engine/face-targets` 2. A
   contract measures the result, not the data's own formula: no vertex of a head standing out of its neighbours beyond
   its base (1.5 mm; Anny's face measured 2.6 before). Limits: at rest 5× for Anny's own changes (was 9×; the plain
   body's is 3×, but her eye changes open moood's closed eye slit, whose edges are under a millimetre — said in the
   check); the head with Anny's face now measures 4.5× (was 8.0×).
2. *Painted features didn't follow the form.* The picture is laid on the head the face is drawn on — right after the
   wrap, or Anny's own head before its form — so later changes carry it (the red-haired girl's long face now opens her
   mouth in the painted mouth). The features presets for Anny's own head (dot eyes, volume) are drawn on her eyes and
   lips, not 3 cm under them. The grin: the wrap lays the lips' parting in the grin's dark, midway below the teeth, and
   holds it there through the easing of folds; the teeth end above where the skin parts — the old man's teeth stay whole
   when he opens his mouth. A drawn mouth is set on where its lips part (0–1.5 mm on most heads, 5.4 on the long-nosed
   man; holding a drawn mouth's parting left pleats round its corners). Expressions are placed by where the features are
   drawn. Contracts in mm: the drawn eyes on the skin's eyes, the mouth's parting on the lips' (3 mm).
3. *Rigid pieces didn't take form changes.* Pieces are skinned to the Head joint and follow the skin under them: each
   carried as one by the affine change that best carries its skin's vertices in that frame (a nose with an expression, a
   head grown by a layer — hair now grows with it). First tried: each piece vertex by its nearest skin vertices — the ball
   nose cracked in a smile; then a similarity — a squashed head left the nose 4 mm off; the affine one holds.
4. *The hood.* Kept as it looks, made coarse (meshes of headwear at 0.07 head units: the old man's hood 23,396 vertices
   from 71,794; his frame 6.3 ms from 10.3); its going through the body and following a bigger head roughly are left to
   the clothes stage, where hoods become garments (README, Not done yet).
5. *The head–neck join.* Looked at in plain light, the "stepped folds" under the jaw were mostly the toon light: the
   key light's cast shadow multiplied in (three.js) made grey, stepped edges, and the designed form's shading switched
   off over two rings where the head's share falls. Now the toon's cast shadows go through its own tones (`shade`, the
   darkest; 0.45 keeps the weight Г3's multiplied shadows had) and the form's shading fades as the skin leaves the form.
   Two geometric tries (a wider join band filled bilaplacian-smooth) did not help and were taken back. The check measures
   under the jaw and at the nape too, the same 25° for every head (the old man's own 60° is gone), against the skin laid
   on its form on a wrapped head — the old man's nape ledge and jowls are his Г3 form's own and stay (said in README).
6. *Checks that couldn't fail.* The picture's mask is checked by whether it smears the picture (5×; it found the
   picture's edge row smeared over every wrapped head's crown and the sides: the mask now follows the surface's facing
   and the picture's extent); reliefs by their stretch against the plain body's (a drawn mouth's lips are now two reliefs,
   one on each side of the parting). Added: seven motions with jump and bow, every skinning method, a body's change on
   the rest and as a layer, a smile in a motion, pieces on a head grown by a layer. Pieces through the body are not a
   contract: hair and headwear do go through the shoulders (stages 3 and 4).
7. *The overlay measured the mesh.* Its points are now the drawn eyes' and mouth's places on the skin, the nose piece's
   tip, the chin; the outline is the face's without hair and headwear. The red-haired girl: 4.8 px rms at the picture's
   angle, 4.0 fitted. The changed red-haired girl still scores a little better (4.3) — her longer face is nearer the
   picture, not a flaw of the measure.
8. *Presets.* Each of our heads is now a preset of part presets — `form-*`, `features-*`, `hair-*`, `wear-*` (groups
   head-form, features, hair, headwear) — written by `tools/heads.mjs`; a head's parts go over its base's by id or name:
   `{kind: "off"}` takes one away, one without a kind changes only the keys it gives (`{id: "eyes", as: "volume"}`), a
   whole one takes its place; `head.strength` weighs the form it starts from. Character format 5, preset format 4 (only
   versions changed in the files). The viewer shows the preset's ways too (strength, ✕) and chooses a features preset.
9. *Light.* The ball nose's shine is drawn by the key light (toon); a nose piece takes the face's washes (Jesper's pink
   tint, the blush across a nose; one list of washes for the picture and the piece); closed pieces cast their shadows
   from their back faces (no acne on hair in plain light); a nose takes no cast shadows when the face doesn't. Soft light
   by the form looks like plain on the red-haired girl because her skin lies exactly on her form: said in README.
10. *Build time.* Wraps are stored by the key of what they are made from (`data/wraps/`, `characters.mjs wraps`); a
    head loads in 1–3 s (was 11–13 s).
11. *Duplication.* Landmarks found once (`landmarksOf`, which the wrap now uses — the wrapped heads moved by up to 12 mm
    at the back of the head, looked at and kept); the head's scale and size, `num`, colours, flags and pins in one place
    each; `biharmonic`/`solve` in math.js; one pack writer.
12. *Hard-coded.* The wrap's metres scaled by the head; pieces' and the grin's colours are parameters with defaults;
    the expressions' sizes are an effect's `size` with named defaults.
13. *Hooks.* `figure.headShape(pose)` takes the pose it is in, its jaw part moves with the Jaw joint, gives a normal;
    `figure.neckShape(pose)` for collars.
14. *Versioning.* `src/head/version.js` (wrap, picture, expressions, pieces): stored wraps are keyed by it and a unit
    check sees a stored wrap that is not what the wrap makes now; the numbers check keeps each head's picture places,
    mask, a hash of its drawing and the versions, and names what changed.
15. *Minor.* Relief ids by side (l/r); an expression twice sums its morph as it sums its asks; `heads.mjs` runs the
    pages' data lines in `node:vm` (nothing of node reachable); the viewer frames the face by the head's own frame, its
    panel above the face at phone width with the heads' part first. Giulia's solid stays a way of the form as before
    (it was kept on purpose, rough, as an example; not changed without asking).

**Decided by whom.** The findings by the reviewer; the hood, the grin, the checks' spirit, presets and versioning by
Pavel through the lead agent; the rest (the face map, picture on the drawn head, affine pieces, toon shadows, `shade`
0.45, the checks' forms) by me, said here.

**How, to repeat it.** `python3 engine/tools/face_targets.py`; `node engine/tools/heads.mjs`; `node
engine/tools/characters.mjs upgrade && … presets && … pin && … cases && … wraps`. Looked at: every head front, three
quarters, side, at rest, in seven motions, with each expression (`/tmp` sheets from `check/pictures.mjs` jobs), plain and
toon light, the neck join in plain light, the old man's grin opening; the viewer at desktop and phone width. Pictures:
`node engine/tools/sheets.mjs engine/tools/sheets/heads.json` (a new sheet `fixes`), `node engine/tools/overlay.mjs`.
Checks: `units.mjs`, `quality.mjs`, `numbers.mjs`, `pictures.mjs` — stored numbers and pictures refreshed for the head
characters only (every `head-*` case), after looking; bodies and every other character unchanged.
