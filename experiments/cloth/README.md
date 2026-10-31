# Clothes of fabric

A body (Anny, as moood bakes it) in everyday clothes, each garment simulated as cloth of its own fabric, through
Kimodo motions: standing, walking, running, jumping, dancing, sitting down on the floor, lying down, a forward roll,
lying down and rolling over — with or without wind. Open `index.html` (served from the repository's root); the motion
is computed first (the bar under the picture), then plays in a loop. Pictures: [docs/pictures/cloth](../../docs/pictures/cloth/).

**The cloth** (`cloth.js`, XPBD with small steps — 16 a frame, one pass each):
- points with the fabric's mass (kg/m²); edges hold against stretching (N/m) and give way more easily to being pushed
  together, so the cloth folds; lengths are solved before and after bending, or bending would stretch the cloth;
- hinges between triangles hold against bending toward flat with the fabric's bending rigidity B (N·m, Kawabata's;
  per hinge k = 3·B·e/(h₁+h₂)) — chiffon's bending length is about a centimetre, denim's three, tweed's four;
- the air pushes on each triangle as it faces the flow (the wind, gusting, minus the cloth's own velocity) — light
  fabrics fly, heavy ones barely move;
- the body and the garments under are solid: every point stays its fabric's thickness outside the nearest surface
  point (along that point's normal), with friction against the surface's own motion; the floor too; the cloth's own
  points keep apart (skirt, dress, trousers, scarf);
- a garment meets one under it only where they lie together as dressed (a blouse's hem over a skirt's waistband, not
  its sleeve and the skirt — the one under doesn't feel it), and not past that one's edge;
- a sleeve or trouser leg belongs to its limb: where another part of the body is nearer (legs pressed together, an arm
  to the side), it also keeps outside its own limb, which has the last word; a point pinched between two surfaces facing
  each other (a folded knee, skin into skin) is left where it is, not pushed through to the far side;
- the hand is a mitten for the cloth (5 mm proud: fingers are thinner than the cloth's reach);
- what holds a garment on: its waistband or neckline (and a long sleeve's cuff, lightly; a swimsuit's edges) pulled to
  where the skin carries it, like an elastic; every point no farther from the nearest held point than the cloth between
  them is long (tethers);
- the nearest surface point is looked up afresh every other step and followed over the surface in between; points
  surely far from every surface are not looked at.

**The garments** (`wardrobe.js`): MakeHuman's dress, T-shirt, sweater, trousers and shorts (CC0), each triangle in four
(Loop), each turned as a whole so its outside faces out; the skirt as a tube from the waist that clears the hips and legs and flares to the hem; blouse, cardigan, jacket
and swimsuit made on the body — the skin's region offset by the garment's ease and smoothed so the cloth bridges the
hollows, the cut points moved onto the cut lines so hem, cuffs, neckline and the open front are clean; the scarf a flat
strip laid round the back of the neck, its ends down the front (its lengths those of the flat strip). Sixteen fabrics
with their weight, stretch, bending, damping, friction and thickness.

**The motion** (`people.js`, `sim.js`): the Kimodo turns as in `gallery/player-core.js`, the pelvis along the floor as
SOMA's (scaled by leg length), the body set so its lowest point is as high as SOMA's whole skin's lowest point (never
under the floor; lying, a little above it so the cloth under has room); the arms 7° off the body (SOMA's arms swing
close by its hips; on these wider bodies the hands would go into the hips and press the clothes into them). Each frame the skin goes evenly from one frame
to the next over the small steps. Standing half a second while the clothes settle, then into the motion; walking,
running and dancing go round (the last frames mixed into the first, the body carried on).

**Motions.** `motions/*.json` by `conv.py` (indie's conversion plus SOMA's lowest point per frame): walk, run, jump,
dance, sit, idle from the earlier studio motions; three new — "A person kneels down and then lies down on the floor
on their back." (after a second standing: `lie`), "A person does a forward roll on the floor." (`roll`), and, going on
from the lying one, "A person lying on their back on the floor rolls over sideways onto their stomach, and keeps
rolling onto their back again." — joined to it by `chain.py` (`rollover`).

**Pictures.** `shot.js` bakes outfits through motions in headless Chromium and shoots frames from the views asked for
(`PORT=8841 node shot.js jobs.json out/` with the repository served on that port); the page's `?shots` mode draws only
those frames.

**Speed.** About 0.1–0.4 s of computing per frame (5–23 thousand cloth points), so a motion is computed first and then
played; in headless Chromium with software WebGL a whole motion takes 15–100 s.

**Not solved.** Where the skinned body folds into itself (a deep knee bend, kneeling) the cloth pinched in it can poke
through on the knee for a few frames; trousers ride up the shins when kneeling and stay there, as a T-shirt stays ridden
up after a roll (friction holds them; nobody tugs them back). Lengths are solved twice per small step, not to convergence,
so heavy fabrics stretch a few per cent under their weight. The blouse keeps a soft crease under the bust from its
smoothed shell.
