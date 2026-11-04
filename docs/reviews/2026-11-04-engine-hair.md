# Review of the engine, stage 3 — hair (2026-11-04)

An independent review, by eye and by code; nothing changed by it. Most important first. Pictures and scripts in the
scratchpad `rv3/`, `rvs/`.

**Run by the reviewer:** units 29/29; quality hair 712/712 (worst: depth 18.4/20 mm, share 2.36/3 %, root 14.7/16 mm,
rest 9.1/12, jitter 0.61/1, speed 14.3/20 m/s — the three loosened limits were set from what hair measures); heads
1/890 broken (`hair-gwen` on a grown head, 5.77 > 5 mm); numbers 333/333; pictures 268/268 (incl. the 48 hair ones —
the history's count is wrong).

1. **Hair surfaces stretch a lot, no check sees it**: chains keep lengths, surfaces bound to up to three chains
   (`sim.js write()`) don't — inner layer in alva's run: 4 % of edges over 1.5×, worst 1 % 5×, max 229×; locks 1.3 %;
   Gwen's bob 2 % in a walk. Dark wedges and webs between locks, spiky heaps in a roll. The length contract measures
   `lengths()` (exact by construction). Fix: measure drawn edges' stretch; bind the inner layer to one chain or to
   neighbours of the same lock; let it hide where locks part.
2. **Collision blind past 3 cm, skin not interpolated in substeps**: `solids.js skinOf().at` gives Infinity beyond 3 cm,
   uncounted by the depth check (0.4–0.9 % of alva's samples deeper than 3 cm); `set()` takes the end-of-frame skin
   for all 8 substeps while the head is interpolated — a hand at 5 m/s jumps 17 cm ("arms through long hair" is this).
   Fix: interpolate the previous skin per substep; a coarse inside test for deep points (capsules or a coarse distance
   per bone); a depth check robust past 3 cm.
3. **The body's collision not ready to share with clothes**: `set()` mutates shared state per HairSim (a second user
   gets skin velocity 0, friction breaks); no thickness or offset; three APIs (capsules `figure.collider`/`neckShape`,
   `headShape` repeating `solids.headOf`'s jaw, `solids`). Dropping capsules: right as the contact surface, wrong as
   the only inside test. Fix: update once in `figure.step` before simulations; a side-and-depth answer deep inside;
   fold or drop `headShape`/`neckShape`.
4. **Every loop pops**: reset on `t < s.t`, the viewer wraps to 0 — alva walk jumps 14–16 cm (mean 1.5–2), g1-alva
   10–17; 60 settle substeps in one frame (~155 ms spike); a unit test enshrines it. Fix: continue across a cyclic
   wrap carrying hair relative to the head; reset only on scrub or a new clip; spread the settle or reuse the stored
   rest.
5. **Checks measure less than they say**: only the first 240 frames (turn-back of walk-stop-look-back, most of
   rollover unchecked); jitter only at rest (in motion the fastest per-frame move in the head's frame 8–23 cm); root
   `|d + 6 mm| ≤ 16` accepts −22…+10 mm; speed limit loose; no frame-rate, loop, surface stretch or wind checks;
   `units` compares only nimona's stored build. Fix: whole clips, the missing measures, root offset per style from
   the design, every stored style (or a source hash).
6. **Wind does far less than its presets say**: long locks' lean 16° / 17.5° / 36.5° (none/light/strong, alva), kpony
   9/13/30, against ~20° and ~60° promised. Fix: tune against the groom's pull, check the lean.
7. **By eye**: light better (strands, bundles, broken highlight). Forms the same slabs (Gwen's bob a hard crease
   across the back, doll's back pillows). Worse than В1: thinner locks leave gaps and dark cracks at the crown (Ariel,
   Gwen); Ariel narrower, shredded, a lock cut square; dark specks on Gwen's and Jack's locks; kpony's hairline ragged.
   In motion: Г3's moving hair falls apart into thin ribbons with skin between (its rigid design reads as one mass);
   Г1's side locks curl like worms in the run; alva crumples into spiky heaps in roll and run; kpony's tail stays on
   her back in a bow (as В1). At rest stable, nothing through the face, no explosions.
8. **Cost, and several characters not prepared for**: 17–19 ms a frame (Gwen, g1-alva), 37.6 ms red-ariel in node,
   33.6 ms alva in the browser — half `write()` (JS blend of 40–90k vertices), the rest skin queries; the groom ~4.5 s
   per figure on every load; the skin hash rebuilt from new arrays every frame; per-segment allocations; a browser
   leak (`this.per` cached by the float substep, one entry per frame). Fix: shares without the map; surfaces on the GPU
   (skinning with 3 influences, chain nodes as bones); store the found rest; keep buffers; reentrant solids.
9. **Frame-rate dependence moderate**: deterministic; alva's sway 27/21/20/30 mm at 30/60/144/20 fps. Causes: the
   end-of-frame skin, a zigzag damping 0.35 per substep not per second, two fixed groom passes. Fix: as 2; damping as a
   rate.
10. **Fitting**: the heads contract fails — the hairstyle carried by one affine change of the skin fitted on the rest
    head. Fix: fit as a rest layer grows the head. `fit.js`: ±3 cm clamp, 1–5 cm fade, ellipsoid at x = 0 — not in head
    units.
11. **Stored builds 45 MB (+ ~47 MB in git history over 4 build versions)**: float32, up to 140k vertices per style
    (mostly the hidden inner layer), a full copy per rebuild; 3–7 MB per style in the browser. Fix: 16-bit positions in
    the head box, a decimated inner layer, builds out of git or rare bumps.
12. **Presets**: fine by id, `off`/`only`, `color`, `physics`, `moves`; missing friction (`MU`) and damping; every
    preset restates a no-op `physics: {1,1,1,1}`; `color` replaces only each surface's first colour.
13. **Hard-coded and dead**: `sim.js` constants (PIN, MU, SETTLE, dampings, drags, zigzag, floor friction, ±3 cm,
    drape, settle tolerance), `windAt`'s unnamed; dead `SKIN_PARTS`, `irr / 3.14159 * 3.14159` in `shade.js`, stale
    comment in `figure.js`, unused `neckShape` and `collider` for hair. `build.js`/`styles.js` copied from В1 — say in
    each which is the source now.
14. **Viewer**: at 390 px width (`hair-g3-red` running, 8 s) the figure off screen, only its path.

**Not checked:** every style in every motion; dance, sneak, stomp for most; man and child in motion; wind on Г1/Г3;
toon light; gallery Д8–Д10; `build.js` and clump binding line by line; GPU frame rate; long-session memory; В1 frame
for frame.
