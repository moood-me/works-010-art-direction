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
