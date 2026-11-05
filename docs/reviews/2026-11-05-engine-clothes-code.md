# Code review of the engine, stage 4 — clothes after the fixes (2026-11-05)

Independent; e591e55..HEAD; nothing changed by it. Probes in the scratchpad `rv5/probe/`.

**Run:** units 35/35; quality skin/bones/feet/order 508/508, heads 890/890, hair 44/1315 broken (all four with hair
over clothes; Г3's lock 90 mm off its rest standing); clothes-jeans 13/208 broken (body through cloth in sit, lie,
roll-side, lie-rollover; legs off their tubes in lie-rollover, 30 % of rings at the end; a flick 12.4 m/s; the walk
loop). Nothing outside clothes broken by the fixes.

1. **A loop pops the cloth — a bug, not a strict limit**: jeans across the walk's wrap 162 mm against the skin (25 mm
   the frame before), 985 points over 3 cm. `Garment.jump()` (`cloth/sim.js`) moves points by their target's change
   only (`x += T1 − T0`), not turning offsets and velocities with the limb; tethers then pull 62 mm, collision pushes
   104 mm. Fix: carry x, p, v by each point's whole skinning transform (as hair does with the head); a fixed loop limit
   in mm. Medium (~30 lines), low risk.
2. **Tethers move points 1.5–3 cm in one substep** (184–689 of ~2000 passes per motion over 1 cm; 4–7 m/s into the
   velocity) — likely feeding the flicks and the pop (not confirmed). Fix: gathered λ, or a limited, velocity-level
   correction. Small, needs a look.
3. **The triangle-middle test searches needlessly** (~18 % of a frame): `middles()` calls `S.skin` filtered by limb
   though the corners' kept points are already on that limb. Fix: `among` in both branches. One line.
4. **Limits' О3 figures not reproducible**: `quality.mjs` cites О3's 2–3 % knees through and 25–32 % bare skin, but
   nothing runs `through.mjs` on О3; "most moments" = every 10th frame at the 90th percentile can miss 10–15 frames
   (allowed by Pavel's О3 level, but say so); the loop limit still relative. Fix: measure О3 with `through.mjs` or call
   the figures "by eye"; loop in mm.
5. **The history contradicts itself and the picture**: "knee through at roll 52–64 as О3's" vs "worse than О3";
   `o3-side.png` shows no knee through in О3. The sheet shows more: trousers off the buttocks under the sweater already
   at roll 40; sitting (100) the skirt falls behind with bare thighs where О3 drapes it over the knees.
6. **Stale comments and dead code**: `sim.js` header (26–30), 111, 194 describe a dropped approach; `solids.js`
   `S.surface`/`surfaceOf`/`m.V`, `S.NEAR` unused. No capsule leftovers (`capsules.js` only for `armsOff`).
7. **"At any depth" only for the nearest-limb search**: own-limb and middles' tests use `S.skin`'s 3 cm reach. Fix:
   `S.FAR`, or say so.
8. **Workarounds**: HELD_MASS (written down). Not written down: `AGAINST 0.5` (relaxation against shimmer, older); the
   triangle middle only on sleeves, trouser legs, hanging garments (added against a tremble — trunk garments have
   point-only contact, an elbow can pass between points); the form release by hip tilt and contact (a heuristic, in
   line with Pavel's "weaker pull sitting"). The speed cap and floor rule are really gone.
9. **Duplication**: the planes distance ×3 (`solids.planes`, `Garment.surface`, `Garment.against`); contact with
   friction ×4; three neighbour searches. ~60 lines, low risk.
10. **Cost**: jeans 77–82 ms a frame; a scrub ~1 s; no arrays in the step (GC ~1.4 %).

**Correct:** bending gradients, stretch XPBD λ and units, held points and form pull as XPBD, shared substeps with hair,
determinism and reset, substeps independent of frame rate, `through.mjs`'s inside test (the body mesh closed and
oriented), rings, `cells.js`.

**Not checked:** clothes quality on the other 23 dressed; numbers and pictures; the viewer and Д11–Д13 in a browser;
browser frame rate; eye beyond `o3-side.png`; tethers as the flicks' cause; `shape.js`, `patterns.js` line by line.
