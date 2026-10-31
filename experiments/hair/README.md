# Hair

A hairstyle is a set of parts. Each lock lies along its own guide curve (so it can later hang on a chain of joints
from the Head bone) and is drawn twice:

- **as its own swept surface** — a lens section (thin side edges, the inner face flatter), thinning to a true point at
  the tip with an eased start, a hooked tip that bends sideways, and smaller locks breaking off a clump's end
  (`clump`, each kid with its own guide). Normals lean out along the lock, so it shades as a sheet, not a tube;
- **merged with the part's other pieces into one surface** (scalp mass cut by a drawn hairline, buns, a quiff's body),
  drawn a little inside the locks: the darker inner layer that fills the gaps and that light falls into between clumps.
  Under locks the scalp mass sinks below them (`under`), never into the skull.

Hair shading (`index.html`): strand direction from each lock (the inner layer takes it from the lock above it), fine
and coarse strand lines that gather towards the tip and fade where finer than a pixel, darker roots, an occlusion term
from the hair's own distance field (grooves and inner layers dark), and a two-lobe anisotropic highlight band along
the strands (Kajiya-Kay), the second lobe tinted and broken by the strands.

Helpers in `styles.js`: `fall` (locks from the crown round the head, with a rhythm of big and small clumps, varied
lengths and hooks), `fringe`, `under` (the under-layer of long hair), `sweep` (sleek hair combed from the hairline to a
band or bun), `tail`, `braid` (three locks crossing), `bun` (locks wound round a centre), `ringlet` (a lock wound in a
spiral round its guide). `styles.js` holds 14 hairstyles after Pavel's references. `?dbg=inner` shows the inner layer
in magenta (to find where locks don't cover), `?only=i` builds one item, `?strands=0`, `?ink=…`.
Pictures: [docs/pictures/hair](../../docs/pictures/hair/).

## In motion

`index.html` with no hairstyle asked for (or `?live`) is the hairstyles on a body in motion: Anny's woman, man or
child as moood bakes them (in a T-shirt and trousers, drawn rigid on the skin), the Kimodo motions (stand,
walk, run, wave, jump, dance, bow, sneak, stomp, sit down on the floor, lie down, forward roll, roll over), wind
(none, light, strong) and head turns laid over the motion (looking round, quick turns to the sides). `?s=…` alone is
still the one hairstyle at rest, as before, and `?viewer` the gallery's 3D view of it.

- **Onto the body** (`fit.js`): the body's skull is fitted with an ellipsoid (its points above the brows) and the
  hairstyle is carried over from the designed head: what lies on the designed skull lands on the body's skull, what
  lies off it keeps its distance and direction from it. The body as the hair meets it: the fitted skull and an
  ellipsoid face ride the Head joint; the neck, the trunk (pairs of capsules side by side in slices), shoulders, arms
  and hands are capsules fitted to the skin, each end carried by a joint.
- **The simulation** (`motion.js`), as games and film do it (TressFX; Müller et al., *Fast simulation of inextensible
  hair*): each lock's guide curve is a chain of points every 2 cm rooted on the head (the first two pinned); 8 small
  steps a frame, each: gravity and the air (wind with gusts and its own turbulence round each lock, less the lock's
  velocity, drag as the square of that speed, pushing across a lock more than along it; light wind leans long hair
  some 20°, strong some 60°), then twice the groom — each point pulled toward where the
  hairstyle has it, carried by the head (firm where the lock lies on the skull, fading down the free part), each
  segment bent back toward its designed angle against the one above (stiff at the root, softer toward the tip) —
  stiffnesses as springs (1/s²), each pass taking k·h²/(1+k·h²) as XPBD's compliance does; then the solids (skull and
  face as deep as each point lies at rest, capsules, the floor) with friction against their own motion; lengths kept
  exactly (follow-the-leader with its velocity correction; ringlets give like springs); the hair's own friction (its
  motion against where the head carries the hairstyle dies down) and a damping of zigzags along a chain. Short hair is
  stiff all along, long hair swings, tails and braids (`dyn: { heavy }`) are heavy and slow, ringlets bounce. The
  hairstyle was designed as it hangs, so the groom is set against the hair's weight: on loading the hair is let hang,
  the groom moved up by how far it sagged, a few times over, until hanging it is the design (the inverse rest shape
  film pipelines use) — nothing sags at rest and the weight is real (hair hangs as the head tilts, swings like a
  pendulum, leans against the wind). Then it settles once on the standing body (over its shoulders, not through
  them), and that is its rest.
- **The surfaces ride the chains**: each lock's points are bound to its chain where they lie, in the chain's frame
  there (carried down the chain from the head without twist), blended between neighbouring frames; a clump's smaller
  locks ride their clump's chain; a braid is one chain (`rig` in `braid`) with its three strands, the tail below and
  the band on it; combed hair (`sweep`), buns and bands ride the head (`rig: 'head'`). The inner layer is bound sharply to the
  lock it lies under (blended only within a millimetre or so), so where locks part it parts with them rather than
  stretching into a web. The occlusion baked at rest is lightened, and the inner layer's outline faded, where the hair
  has moved off where it lay (what hid it no longer does; the outline would show through folds). `dyn` on a lock (or a
  braid) sets its own stiffness: `lTip`, `gTip` (1/s²), `heavy` — the ginger boy's quiff is set hard. `?dbg=caps`
  draws the solids the hair meets.
- `motionshot.js` makes pictures: `PORT=8799 node motionshot.js jobs.json out/` (jobs: hairstyle, body, motion, wind,
  head turns, frames, views); the page's `?shots` mode draws only what it is asked. Pictures:
  [docs/pictures/hair/motion](../../docs/pictures/hair/motion/).
