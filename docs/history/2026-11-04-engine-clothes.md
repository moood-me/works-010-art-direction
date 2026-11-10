# 2026-11-04 — the engine, stage 4: clothes

**What called for it.** The engine's plan (docs/directions.md, "The engine view", agreed with Pavel 2026-11-03): one
clothing system with О3 (real cloth: garments, fabrics with their properties, collisions, wind, every motion) as the
base; from О1 the designed silhouette of a garment as a shape the cloth is pulled towards, with a strength from "a stiff
petticoat holds the bell" to "the cloth hangs freely", and folds as drawing; О1's silhouettes as presets, О1's own physics
replaced by О3's with a rest shape; from О2 MakeHuman's garments as source meshes; collision with the body shared by
clothes and hair. Pavel on О3: «классно»; on О1: «Мне очень нравится… на мужчинах, детях; будут ли они двигаться?». The
requirement (docs/requirements.md): clothes are cloth, not a mask on the body — they don't go through the body, they
crumple, bend, take the wind, and behave logically when a person walks, runs, lies down, tumbles, rolls; ordinary clothes
of today in fabrics of different kinds. The task was set by the lead agent (what to build, on every body and motion, the
checks, the gallery, the pictures); the ways below were decided by me.

**What was done** (engine/README.md has how it works: Clothes, formats, checks, adding things, not done yet).
- *Source meshes*: MakeHuman's 15 garments (CC0) as the engine's data, `data/garments/mh-*` (`tools/garments.mjs` from
  the bytes moood bakes, experiments/data — the same О2 and О3 took).
- *Patterns* (`src/cloth/patterns.js`): MakeHuman's garments laid on any body of Anny's mesh; О3's made on the body
  (blouse, cardigan, jacket, swimsuit, flared skirt, scarf); Г1's turtleneck; the heads' hood as cloth. Each with what
  holds it on, its layer, its limbs. О3's `wardrobe.js` carried as code (its copy stays for its page).
- *Silhouettes* (`src/cloth/shape.js`): О1's `tailor` carried as code — the designed form drawn on rings round the trunk,
  arms and legs; the cloth cut to it and pulled toward it with the garment's strength (0 hangs freely, 1 a stiff
  petticoat), not pulled where the body stands in it (Pavel's "a weaker pull to the form when sitting", О1's notes).
  22 silhouettes as presets (`shape-*`: О1's eight dresses and its outfits' skirts, sleeves and legs).
- *Fabrics*: О3's 16 as presets (`fabric-*`: weight, stretch, compress, Kawabata's bending, damping, friction,
  thickness, air, sheen, roughness, opacity).
- *The cloth* (`src/cloth/sim.js`): О3's XPBD cloth on the figure's step — all of a figure's garments in one simulation,
  innermost first in each small step; fixed small steps of 1/240 s (any frame rate), a reset going into the pose from
  the rest with the cloth along it, a loop carrying it with the skin; the body met through the figure's solids, the one
  collision hair uses (src/solids.js got what cloth needs: a limb's own skin, the skin points a reader keeps nearest,
  the way into a pose from the rest, a cover — the clothes — that hair lies over).
- *Clothes as a character's parts* (format 7, presets 6): `clothes: [garment…]`, outfits as presets, over a base's by id
  (`src/parts.js`, shared with the head's parts); 10 dressed characters `clothes-*` (woman, man, child, old woman, girl,
  a heavy man, Disney's princess, the V hero, hair over a blouse, a cardigan and scarf in the wind); the ready heads
  (Г1, Г3) in the outfits they were drawn in (`outfit-*`, by `tools/heads.mjs`) — their hoods and the turtleneck are
  cloth now, not rigid shells (the piece kind `hood`, `wear-hood`, `wear-old` gone).
- *Drawing* (`src/view3d.js`): cloth with its fabric's sheen and roughness, inside darker, toon light and outline on a
  toon character's clothes; the skin under close clothes drawn sunk 4 mm (О3's way, drawn only).
- *The viewer*: `?clothes` — garments, fabric, silhouette, strength, taken off, put on; the wind; any character.
- *Checks*: `units.mjs` (6 for clothes), `quality.mjs --only clothes`, cases for clothes (numbers and pictures),
  `tools/sheets/clothes.json`, `tools/clothes-o.mjs` (О1 and О3 on their own pages beside the engine).

**How it went, and what was tried** (each in the code where it matters).
- Simulating MakeHuman's garments subdivided, as О3 did (points a centimetre apart), needs small steps of 1/960 s to keep
  their lengths — four times the cost; they are simulated as cut (2–3 cm) and drawn finer. Loop's subdivision for the
  drawing pulled the surface between points into a knee pressing the cloth: the butterfly scheme goes through them.
- The skin asked once a point every small step was three quarters of the cost: each point keeps the skin points
  nearest it and looks for them afresh every other step. Its clearance once never came back from "far" (a point beyond
  the skin's reach was left unasked for ever — legs through skirts).
- Weights from the nearest skin vertex, point by point, tore cloth apart in a pose (an armpit's collarbone beside a
  chest's; a bell's hem between the thighs, or carried by a hand beside it): weights smoothed over the cloth, what hangs
  carried by the pelvis, never by a hand.
- A reset placing the cloth straight in a pose left a skirt's hem round a leg that should be inside it; it now goes
  into the pose along the solids' entry.
- Hard tethers fought the body where cloth goes round it (60–90 m/s points); soft now. Points pushed between body and
  floor bounced; pressed cloth now lies on the floor, and no point leaves the skin with its push's speed. The capsules'
  ends stand out of a bent knee: cloth is pushed only to their surface, not past it. A hem over a waistband shimmered as
  its one nearest point changed along the edge: the planes of the nearest points, met less past the edge. Held as cut,
  a strap tugged into the skin for ever: held where it hangs settled.
- Each triangle's middle is kept out of the skin too (a knee went between points), over its corners' skin points.

**Checks.** `units.mjs`: all 35 hold (the bell's wider hem measured on its designed form: hanging at strength 0 the extra cloth falls in folds). `quality.mjs` skin, bones, feet, order: hold (the feet check now takes the lowest
point of every mesh standing on the floor — shoes lift a dressed figure by their soles). `quality.mjs --only clothes`
(24 dressed characters, every motion and chain whole, two winds): 2384 of 2401 hold — the cloth through the body, its
speed, the loop, a scrub back, other frame rates hold everywhere; broken: standing still, cloth moving more than 2 mm a
frame on 15 characters (2–4.5 mm on eight; 7–9 mm on six — trouser hems over rigid boots, oversized sweaters, the
princess's dress; the heavy man 26 mm and creeping 24 mm in 8 s — his thighs touch, and on his back the cloth stands at
the skin's reach), the blouse in a strong wind drawn out past 1.5× at 9 % (7). `quality.mjs --only heads`: all 890 hold. `quality.mjs --only hair` (run with the planes' fade dropped below; without it hair without clothes is exactly as stored before this stage): all hair without clothes holds; 47 of 1315 broken, all on the four with hair
over clothes (Г3's girl, Г1's Alva, Ariel over a dress; the blouse of clothes-hair): a shimmer of 1–8 mm in motion, 13
mm standing, a few locks torn — hair lying over the cloth is not right yet. Seen in the pictures, not by the checks: in
a forward roll MakeHuman's loose trousers come off one leg (clothes-jeans, head-tails, head-semi; the other trousers
keep on) — not solved. Tried for it and dropped: the hair meeting
the cloth as drawn (finer), not as simulated; a point beside the cloth's edge not over it; hair as near the cloth as at
rest — none changed it. Cost of a frame of a dressed figure's whole step in node: 24–126 ms. Stored numbers and
pictures changed only for the characters with clothes, heads and hair (`clothes-*`, `head-*`, `hair-*` cases): the
heads and the hair characters on them are dressed now (their outfits as cloth). Nothing else moved. Tried and dropped:
the skin's planes fading to nothing at their reach (an oversized sweater's flicker 9 → 3 mm), as it moved hair fitted on
a grown head off the skin (Alva, 8 mm against 5).

**Pictures** (docs/pictures/engine/clothes/): bodies.png (garments on eight bodies, front/¾/side), motion.png (Kimodo's
motions and chains), fabrics.png (one dress in eight fabrics, walking and in a strong wind), strengths.png (the
silhouette's strength 0 … 1, and eight silhouettes at 1), hair.png (hair and clothes on one figure, hoods and the
collar as cloth), heads.png (the ready heads in their outfits), o3-side.png and o1-side.png (О3's and О1's pages beside
the engine at the same moments), viewer-clothes.png (the viewer's panel), and GIFs.

**How, to repeat it.** `node engine/tools/garments.mjs` (once), `node engine/tools/heads.mjs`, `node
engine/tools/characters.mjs presets && … pin && … cases`; checks as above; pictures: `node engine/tools/sheets.mjs
engine/tools/sheets/clothes.json`, `node engine/tools/clothes-o.mjs engine/tools/sheets/clothes-o.json`.
