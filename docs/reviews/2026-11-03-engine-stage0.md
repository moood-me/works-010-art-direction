# Review of the engine, stage 0 (2026-11-03)

An independent code review after stage 0 was built; nothing was changed by it. Findings, most important first.

**Holds (checked by running):** the picture check is deterministic on one machine; the retargeting rule rebuilds
Kimodo's own joint places within 1.5 mm; bones lie in their joint frames within 4.7° of SOMA's; characters travel along
Kimodo's path scaled by hip height; single-joint vertices identical in all three skinning methods.

1. **The only chain (lie → rollover) isn't seamless and rests on a reconstruction** (`tools/motions.py:143-159`,
   `src/motion.js:36-46`): vertex jumps of 46–84 mm at frames 180–182, the toe turns 14.3° in a frame; rollover's first
   five frames were copied from lie's last five. The studio still has rollover's own data (key 7a4c19b1…, 150 frames).
   `clipOf` assumes the next motion keeps the previous heading; the ask's heading, transition_frames, seed and
   constraints aren't kept. Fix: re-fetch rollover's own data, measure the join; keep the whole ask; turn by heading
   or refuse.
2. **Versioning protects only top-level defaults** (`src/character.js:14-33`): correction defaults, seam iterations,
   CoR sigma, floor algorithm, retarget and `clipOf` live in code unversioned; bodies and motions referred to by id
   without a version or hash; `resolve` accepts unknown keys and values; no `upgrade`. Fix: the version selects
   behaviour (a versioned pipeline with its defaults inside); pin a content hash of each body and motion; validate
   descriptions against a schema, refusing unknown keys and values.
3. **The floor step counts invisible vertices** (`src/figure.js:34`): 1561 vertices used by no triangle; the visible body
   floats up to 12.8 mm. Fix: keep the used vertices in the topology; make the floor its own step after everything
   drawn (shoes, clothes, head pieces), with the shift exposed.
4. **The picture check is coarse and has gaps**: 240×360 pictures, 0.05 % threshold; doubling CoR sigma missed in 29 of
   40 shots; no shot exercises DQS, LBS, the clavicle share, the seam, a correction, placement, or the join; the lying
   shot cuts off the legs (camera at floor + 0.52 × height); renders through the viewer, so UI or camera changes count
   as character changes; three.js from the network; a wrong `--only` passes with 0 jobs. Fix: a numeric check in node
   (skinned positions at fixed moments, tolerance in mm); frame pictures by the figure's bounds, larger; presets and
   moments for each option and the join; three.js in the repository; fail with no jobs.
5. **What later stages need that the foundation lacks:**
   - bodies: no way to apply something as a pose layer (`Figure.frame` runs a fixed sequence; corrections are a
     registry inside the engine, `corrections.js:13`); frame turning only in Python (`bodies_anny.py:218-237`) — the
     engine needs both, with an explicit choice per change (anatomy: turn the frame; design: keep it);
   - hair and clothes: `frame(clip, t)` holds no state (time step, previous pose, reset on loop or scrub); `fig.pose` is
     an internal buffer that gets overwritten (`figure.js:56`, `retarget.js:32`); no collision shape for the body
     (capsules per bone or an SDF);
   - heads: `Skinner.skin` skins only `body.positions`; mesh expressions need a per-frame rest change (morphs) before
     skinning;
   - characters not from Anny: `makeRetarget` needs mesh measures and `Figure` assumes one mesh with 4 weights per
     vertex — split the rig (skeleton, frames, hip height, floor) from the meshes, so several meshes and sweeps run off
     one pose and one floor shift;
   - triangles as uint16 limit meshes to 65,535 vertices.
6. **Performance** (`src/skin.js:126-183`): CoR 2.2 ms a frame per figure in node (DQS 3.7, LBS 1.2); inner loops
   allocate per vertex; unused vertices skinned; building a CoR Skinner 236 ms, redone per Figure and on every toggle;
   one shadow box and a light following one figure (`view3d.js:247,265`). Fix: cache centres and neighbours per body;
   skip unused vertices; loops without allocation or skinning on the GPU.
7. **Hard-coded:** camera target at floor + 0.52 × height (`viewer.js:97`), the fixed shadow box. Nothing by body name,
   port or data root.
8. **Minor:** `tools/motions.py:72` refers to a missing `src/chain.js`; dead `rbf[0] = rbf[1]` (`bodies_anny.py:175`);
   rest hips at the origin while Kimodo's frame 0 is about 7 cm back on z, so switching rest → motion jumps.

**Not checked:** the Python tools (Anny, torch not run); Kimodo's real rollover frames; the viewer by hand; hands and
fingers; the picture check on another machine.
