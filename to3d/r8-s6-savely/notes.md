# Р8 — Савелий Петрович, символический (С6 → 3D)

What was done, why, how to repeat. Brief: `/home/user/cache/BRIEF-to3d.md` (both rounds). Done by one agent in one
session; the orchestrator commits.

## The idea

In С6 the person is almost a sign: one dark form with nothing inside, a thin rim of light on one side, one warm sign,
fog in layers, grain. The face is not drawn; what he feels is his posture. And the С6 drawing is itself 3D: `sil.py`
builds the figure from lofts of elliptic rings and tubes of spheres on a small skeleton, projects it at a yaw and
merges the 2D convex hulls of neighbouring rings / spheres into one shape. So the 3D here is **the drawing's own
solids**, built by the drawing's own code (`cast.savely`, unchanged), only on a skeleton that is SOMA's, so Kimodo can
move it.

Brief points 1–2 (Anny's body, an artist's head) are not used, and why: nothing inside the silhouette exists in this
style — anatomy, a face, eyes, lids would never be seen; the silhouette is everything, and the drawing's solids already
give exactly the drawing's silhouette in every view (see the overlay: it matches to a pixel or two). Anny's skeleton
SOMA and Kimodo's motions are used as the brief asks. Points 3–6 become: colour = one ink; "look" = the rim cut from
the figure's mask on the lamp's side, the signs, the world's light. Same choice as Р4 (Вера, indie) made for its style.

## Steps (tools/)

1. `build.py` — 
   - runs `cast.savely()` with its skeleton function swapped for ours (a straight stand, arms laid along SOMA's rest
     arms), so the very lofts and tubes of the drawing come out in a rest pose;
   - every pair of neighbouring rings and every pair of neighbouring spheres (sampled, 160–520 points each) → its 3D
     convex hull (scipy). The drawing merges the 2D hulls of exactly these pairs, and the projection of a 3D hull is the
     2D hull of the projected points, so in any view the union of these hulls is the drawing's shape. 14 262 vertices,
     28 128 triangles; the hulls overlap, and that is fine: one ink, the union happens in the picture;
   - weights: limb hulls rigid on their bone (a sphere sits on each joint, so a bent knee or elbow stays round);
     torso blended Hips → Spine1 → Spine2 → Chest → Neck1 by height, its top over the shoulders 55 % on the collarbones;
     the coat's skirt from the pelvis down to the hem goes up to 78 % with the thighs (split left/right by a soft step
     across the middle); neck Neck1 → Neck2 → Head; head, cap, brim, moustache, loupe rigid on Head; the chin's front
     on Jaw (for speech);
   - SOMA's 77 joints placed on the drawing's skeleton (pelvis, chest, neck, head pivot, shoulders, elbows, wrists,
     hips, knees, ankles, balls of the feet; fingers etc. carried along). Frames: `turn(SOMA bone → our bone) ·
     SOMA's frame`, so the retarget (`Q = q·frameᵀ`, engine/src/retarget.js) makes our bones follow Kimodo's bones
     with our lengths; Hips and Head keep SOMA's frames (their orientation matters, not a bone direction);
   - poses from the drawing's pose numbers (`lean, hunch, neck, nod, slump, shrug, arm*, leg*, foot*`): every joint's
     turn = the turn of its rest bone to the drawn bone, twisted with the drawing's trunk frames. The drawn stand, and
     six moods (`MOODS`) — the drawn one (looking at the watch) and five more written in the style's rule «выражения —
     позой всего тела»: grumbling (hands behind the back), sad, glad (chin up, hands on the chest), surprised (draws
     back, hands fly up), angry (head pushed out, a fist shaken). For layering on motion each mood is kept as local
     turns: the trunk's (the lean moved from the pelvis to Spine1, so the legs stay Kimodo's) and the arms'.
   - writes `web/data/savely.{json,bin}` (an engine body + topology pack: positions, triangles, skin, joints, frames)
     and `web/data/poses.json` (the static poses, moods, where the signs sit).
2. `web/savely.js` — the engine as it is (`makeSkeleton`, `makeBody`, `loadMotion`, `makeRetarget`, `build`,
   `Skinner` with linear blending — the parts are rigid, nothing to blend but the coat), and on top of Kimodo's turns:
   - the mood: the trunk's mood turns multiplied onto the motion's, the arms slerped to the mood's where it holds them;
     moods mixed and followed by critically damped springs (ω 5: an old man changes his posture slowly);
   - breathing by hand (allowed as small life): breaths of 3.4–5 s, uneven depth, in-breath ~40 % eased, out-breath
     slower, a short rest; the chest straightens 1–1.6°, collarbones lift 2°, the neck and head compensate;
   - talking: Russian phrases read letter by letter (vowels open the jaw by their openness, м/б/п close it, commas
     and stops are pauses) followed by a fast spring; the jaw turns ≤ 9°, only the chin's edge shows it in profile; a
     small nod on a phrase's first stress;
   - the look: pass 1 — the world and the ink figure; pass 2 — the figure's mask and depth; composite — the rim is the
     drawing's own rule (the shape minus itself shifted toward the light), the shift pointing at the lamp's screen
     position per pixel (so the rim moves round him as the lamp or the camera moves; in the drawing's views a fixed
     direction (1, .3) as the SVG), its width the drawing's 0.55 cm at his distance, its strength by how much the lamp
     is behind him; glows as the SVG's radial gradient (lamp behind the figure, watch and loupe glint in front unless
     the body hides them — tested against the mask's depth); vignette and grain; everything drawn 2× and averaged down
     (the rim is cut from a mask: it is smooth only so);
   - the world: a dusk sky (the drawing's EMBER palette), three rings of hills, each farther one paler, with a band
     of fog over each; the ground fogging to the horizon; a 2.6 m street lamp with a pool of warm light; his shadow
     from the lamp flattened onto the ground (stencil, so it is one shadow); the watch, the chain (a sagging curve of
     fixed length from the waistcoat pocket to the hand), the loupe's glint.
3. `web/app.js`, `web/view.html` — the page and the viewer (`window.A` for pictures and films; `?shots` without
   controls, `?slow` a frame every 0.5 s — for looking at it headless, where software WebGL is too slow for a live loop).
4. `shots.mjs` — headless Chromium (swiftshader) over the page; `make.py` — all pictures and films;
   `drawing.py` + `svg2png.mjs` — the drawing's own silhouettes from the style's code for the overlays.

Repeat:
```
cd to3d/r8-s6-savely/tools
python3 build.py
python3 make.py compare steps moods      # ≈ 1 min
python3 make.py films                    # turn, walk, life, bow, wave, stomp, sit (≈ 1–2 s a frame)
```

## Motions

From `engine/motions` (copied into `tools/web/data/motions`, nothing new ordered): walk (loops travel on, never on the
spot), idle, bow, wave, stomp, sit. On all of them the mood «просто стоит» (his stoop: hunch 22°, neck 12°, without
the arms) is layered on, so Kimodo's young person walks as this old man. The standing films use the rest stand with the
mood and breath (no Kimodo motion holds a watch at the chest; Kimodo's idle looks round and drops the arms).

## Bases and licences

| What | Where | Licence |
|---|---|---|
| The drawing and its code (sil.py, cast.py, draw.py) | `styles/s6-symbolic` | ours |
| SOMA skeleton | `engine/data/skeleton.json` (NVIDIA, Apache-2.0, see `engine/data/soma/NOTICE`) | Apache-2.0 |
| Kimodo motions | `engine/motions` (moood studio) | as the engine's motions |
| three.js 0.160 | jsDelivr | MIT |

No neural images, no StdGEN, no third-party meshes.

## What is weak

- Moods other than the drawn one are mine (С6 has an expression sheet only for Тим); glad, surprised and angry were
  redone three times; angry still reads more as reaching than shaking a fist.
- The head is the drawing's head made of rings: right as a silhouette at figure size, coarse up close (the style's
  own portraits were drawn by hand for that reason). No close-up portrait was made.
- The coat's skirt is skinned, not cloth: on wide steps its front wedges with the forward thigh. The hand is one
  drop; Kimodo's fingers are ignored.
- His stoop is added to every motion as it is: in the bow it adds to Kimodo's bow, which comes out too deep (the
  head below the hips); in the wave the raised hand goes forward with the stooped trunk.
- The lamp is a point for the rim and the shadow only; nothing else is lit (on purpose: the style has no inner shade).
