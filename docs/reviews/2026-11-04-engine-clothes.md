# Review of the engine, stage 4 — clothes (2026-11-04)

An independent review, by eye and by code; nothing changed by it. Most important first. Pictures and probes in the
scratchpad `rv4/` (`o-side-rv.png`, `jeans-roll*.png`, `d1–d9.png`, `probe/`).

**Run by the reviewer:** units 35/35; quality clothes on 4 characters 397/401 (all 4 standing still: heavy man 26.4 mm
a frame, creeping 24.3 mm; dress 2.6; jeans 2.4); hair 51/1315 broken, all on the four with hair over clothes (g3-red
16.4 mm a frame standing, g1-alva 10.8); heads 890/890; numbers clothes-* 71/71; pictures 24/24. The stored outputs
agree with the code, but what they show is mostly not caught by any check.

1. **Bodies come out through the clothes in ordinary motions — worse than О3 with the same garments.** Roll: knees
   punch through trouser fronts (52–64), a leg comes out of the hole (68–72) — jeans, heavy man, hood, old, semi,
   tails. Sitting: shins through jeans and tails. Roll: knees through the bell and Disney's dress; running: the thigh
   out of granny's skirt and Disney's dress; the wind dress ends at the hips sitting and rolling. О3's own page with
   the same jeans (roll 52, 64, 85) and its sweater outfit (72) keeps them on; in the engine both legs come off the
   sweater outfit. Causes: (a) point-against-skin only — a triangle's middle asked only when a corner is within 4 mm;
   once a knee is past, points on its far side read "outside"; (b) О3's pinch rule (`experiments/cloth/cloth.js`
   collide: keep the previous surface when the nearest flips) not carried; (c) `solids.js kept()` asks the nearest
   limb only, hip-band trouser points have home 0 (`clothes.js homeOf`) — the thigh never asked in deep flexion; (d) the
   form's pull (`sim.js pull`) drags a bell's hem into a rising knee (ON_SKIN stops only the normal part within 5 mm).
   Fix: body-against-cloth (skin vertices or knee/elbow capsules against cloth triangles); О3's pinch memory per
   point; the own limb for every point of a tube incl. the hip band; weaken the pull where the body is near.
2. **The checks can't see it**: `inBody` (`quality.mjs`) uses `S.skin` — Infinity past 3 cm from skin unless in a
   capsule, planes mixed between touching parts; 24–26 % of points more than 3 cm inside read outside (`probe/caps.mjs`);
   jeans in the roll "0.000 mm in the body" with the legs out. Only simulated points checked: not the body through
   triangles, cloth through cloth, a limb leaving its tube, riding up. Loop limit 3× the next frame's move (tails 275 mm
   passes, limit 839); speed limit 15 m/s measures the 12 m/s cap; jitter (rest only), depth 35 mm, tear 7 %, frame
   rate 15 cm fitted to measures. Fix: topological checks (each tube's ring round its bone; covered skin stays covered;
   a garment on its side of the one under), a true inside test, loop limit in mm, speed before the cap.
3. **Standing tremble — causes found by switching parts off** (`probe/still.mjs`): trousers 26 mm → 0.0 with `S.among`
   off (it merges the corners' kept points from both legs at the crotch — the mix `kept()` avoids); oversized top:
   capsules fitted at the 10th percentile minus 5 mm (`capsules.js`, SHARE 0.1) stand out of the skin (Spine1 on the
   heavy man ~6 cm, the man's trunk 2.7–3.4 cm; end caps not counted) — cloth past 3 cm falls into a capsule, pushed,
   "unseen", falls back: a limit cycle, and cloth standing 3 cm off the back; `bend()` bends toward flat, not the rest
   angle, pressing tubes outward. Fix: one limb in `among()`; capsules inside the skin (minimum, or a distance field),
   no hard 3 cm switch; bend toward the rest angle.
4. **Hair over clothes shimmers by the cover's own field** (`probe/hairover.mjs`): 16.4 mm as is, 16.4 with the cloth
   frozen, 0.4 with `S.over` off; 13 of 21 shimmering points within 3 cm of the dress's open edge. The cover
   (`solids.js cover`) is a planes field over all garments with no open-edge handling (cloth has RIM, the cover none),
   mixes inner and outer garments, `allowCover` all or nothing per point at rest. Fix: fade past open edges, outermost
   garment only, a per-point offset.
5. **Formed dresses lying, rolling, bowing**: a strength-1 bell, the pleated and full skirts stand as a rigid dome or
   spiky crown over a lying body; lying, the bell over the hips with bare legs; bowing, the hem flips up in stiff
   panels; sitting, the bell a wall behind where О1 drapes over the knees; the tulip at walk 60 a straight tube. Cause:
   the form carried rigidly by the pelvis at 2000/s² whatever gravity or the floor. Fix: release the pull as the
   garment's axis leaves vertical and where it presses floor or body, or a form that hangs under gravity.
6. **By eye, more**: V hero's toes through the boots at rest; T-shirts ride up to the chest rolling and lying, and in
   idle in strong wind (a bare strip of back); the heavy man's trouser legs ride up in a bow; the scarf a stiff strip
   (О3's lies on the chest); the clothes-hair skirt flat off the hips in strong wind; granny's pleats star spikes
   jumping; torn-through cloth shows its dark inside at the shins sitting. Good: the jacket outfit in every motion;
   walking, running, dancing clean on most; the bell's swing; the dress in wind.
7. **Solver**: `stretch()` 3× per substep without accumulated λ — not XPBD, stiffness grows with passes; `held()`,
   `pull()`, `tethers()` positional blends, HELD_MASS changes inertia; the 12 m/s SPEED cap, the PRESSED floor rule
   and `quality.mjs` skipping points within 2.5 cm of the floor are workarounds. Good: deterministic; fixed substeps
   with the leftover carried; frame-rate 1 % farthest 30–53 mm; a reset the same however reached, but 126 substeps
   (0.3–1.6 s per scrub).
8. **Performance** (jeans walk ~92 ms a frame): `collide` ~70 % (`S.kept` 43 ms, `S.among` 38); `S.skinAt`
   re-interpolates the whole skin every substep (~9 ms); hair and cloth build their own moments and hashes of the same
   skin; "the step allocates nothing" false (`garments.slice`, `[a,b,c]` per triangle, `subarray` per push); Д11 three
   figures ~6 fps. Fix: each skin moment built once per figure and shared; drop the mixed-limb `among`; batch; GPU later.
9. **Hard-coded and presets**: ~20 constants in `sim.js` (HOLD_TIME, TETHER, SHAPE_K, ON_SKIN, AGAINST, RIM, TOUCH,
   CURVE, SELF, PRESSED, SPEED…), SMOOTH and HANG in `clothes.js`, HOLDS — none per garment or fabric; trousers can't
   take a hem or belt hold; tight fit only per pattern; silhouette strength schema 0–2 vs README 0–1; `quality.mjs`
   repeats `shapeK >= 2000`; the skin sunk 4 mm (`view3d.js sunk`) decided at rest stays sunk where cloth has left.
10. **Layering and folds**: cloth against cloth one-way, masked by where garments lay together at rest; points 2–3 cm
    apart, butterfly only interpolates; "folds as drawing" only as hem flutes — consider wrinkles from compression.
11. **Duplication**: three spatial hashes (`sim.js` Grid, `solids.js` cellHash, `patterns.js nearestOn`'s Map); hair
    and cloth each their own step loop, contact with friction, floor; one cover per figure (`solids.cover` throws on a
    second); several characters ruled out on the CPU by the cost.
12. **Docs** understate it: not "one leg of the loose trousers" — knees through trousers and dresses rolling, shins
    sitting, thighs through skirts running, and О3 does better with the same garments.

**Not checked:** clothes quality on the other 20 dressed characters; pictures for all but 4; viewer `?clothes` and
Д11–Д13 in a browser; browser frame rate; every motion for every character; stomp, sneak, wave, lying; the hood looking
round; light wind; toon on clothes; `shape.js`, `patterns.js` line by line; long-session memory.
