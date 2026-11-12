# Р40 — Кира, вырезанная бумага (С14 → 3D)

What was done, why, how to repeat. Brief: `docs/briefs/to3d.md`, "Third round". The second character of С14 in 3D,
made by the same agent (Claude) right after Р39 (Вера, `to3d/r39-s14-vera`) — read its `notes.md` first: the idea
(a cut-out puppet standing in space; the paper look made in one pass over the picture), the files and the decisions
are there. Who the second character is was decided by Pavel through the orchestrator (first Марат, then Аня, finally
Кира).

## What is shared and what is hers

Shared with Р39, the same files in both folders (`tools/web/paper.js, look.js, face.js, body.js, figure.js, app.js`,
`tools/make.py, drawing.py, shots.mjs, svg2png.mjs, heavy.sh, view_check.mjs`). Hers: `tools/web/kira.js`
(`kira.py`'s numbers carried into space), `tools/web/char.js` (points at it), `tools/character.py`, the page's colours.

What Кира added to the shared code (Вера's pictures were made again with it):
- `shoe()` makes boots (a tall shaft, a thick sole, laces as three strips);
- `headShape.shell(…, puff)` — hair wider than the skull toward the crown (her hair is a wide flat cap; an egg's top
  is too narrow for it); the shell is pushed out evenly (before, only its top ring was lifted — a bump on the crown);
- expressions carry their own `look` (her rest is a sideways glance), glances go over it; the mouth «pout»;
- `straight` — the stand without the character's own carriage (to lay the busts over the drawn ones);
- `fig.motionId` for `onMotion`; `cheek_x` in the spec.

## How she is built

- **Skeleton**: SOMA by her sizes (`proportion`): legs 0.75 m of 1.66, shoulders 0.24 m wide, arms 0.26 + 0.255 m.
  Built standing straight. **The slouch is a pose**: pelvis −9°, spine +4 +8 +9°, shoulders up 10°, neck +15 +8°,
  head −26° (so the face looks ahead from under the brows); on a motion the same turns at 0.8 over Kimodo's (0.25 on
  `sneak`, which crouches by itself). Her left arm (elbow out, the hand in the pocket — the sleeve's end goes into
  the hoodie, no hand is made) is held on every motion.
- **Hoodie**: one shell (shoulders → under the hips) with the neck cut out by `clip`, a darker band at the hem (its
  own ring), pocket and strings glued on; the hood is a heap behind the neck on Chest. Sleeves: a strip per bone, the
  forearm 9 units longer than the arm, the hand moved down into it.
- **Headphones**: two lime slabs with dark centres on the chest, a band behind the neck.
- **Hair**: `hairBack` (a jagged hem by a zigzag of the angle round the head), `hairSide` (the lock at her left
  temple), `fringe` — a shell 8 units off the skull kept where the drawing's own fringe outline (front view) covers
  it; from the side it is cut shorter by `sideLine`.
- **Where the drawing lies**: the front view's fringe covers her right eye down to the cheek; the drawn profile (from
  the same side) shows the eye under a shorter fringe. The front is followed (`docs/findings.md` says so): from the
  fringe's side the face is hidden, from the other it is open.

## Repeat

```
(cd /home/user/cache/to3d-r40-s14-kira && npm install three@0.160.0)
cd to3d/r40-s14-kira/tools
./heavy.sh python3 drawing.py
python3 make.py compare steps expr hero
python3 make.py films                   # turn, walk, life, sneak
./heavy.sh node view_check.mjs /tmp/v.png
```

## Bases and licences

As Р39: the drawing and its code (`styles/s14-paper`, ours), SOMA skeleton (Apache-2.0, `engine/data/soma/NOTICE`),
Kimodo motions walk and sneak (`engine/motions`), three.js 0.160 (MIT). No neural images, no third-party meshes.

## What is weak

- The figure does not lie on the drawn one: the drawing is a flat S of pieces seen three-quarters with feet apart and
  boots pointing both ways; here the legs and boots are real and point forward.
- From the fringe's side the face is hidden; a seam of hair pieces shows on the crown.
- Boots are dark lumps with small laces; the drawing's are bigger and crisper.
- `sneak`: the right arm goes to the chest (Kimodo's), the crouch plus her slouch is deep.
- No torn edges except the ground; no fold shades on the hoodie.
