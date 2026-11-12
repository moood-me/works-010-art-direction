// The other person's shoulder as a place to touch: B (an engine character in its own Kimodo motion, placed in the
// scene) is played on its body exactly as the page plays it, a point of its skin on the top of the left shoulder is
// chosen, and where that point is every frame is written out (plans/shoulder-other.json). tools/plan.py gives those
// places to Kimodo for A's hand; the page puts A's palm on the same skin point.
//   node tools/other.mjs <character> <motion id> <x> <z> <heading> [share 0.15] [out shoulder-other]
import { readFile, writeFile } from 'node:fs/promises';
import { createEngine } from '../../../engine/src/engine.js';
import { loadMotion, clipOf } from '../../../engine/src/motion.js';
import { ContactFigure } from '../contact-figure.js';

const here = new URL('../', import.meta.url);
const read = async u => { const b = await readFile(new URL(u)); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength); };
const E = await createEngine({ root: new URL('../../../engine/', import.meta.url), read });
const [who, mid, x, z, heading, share = '0.15', outName = 'shoulder-other'] = process.argv.slice(2);
const spec = await E.character(who), body = await E.body(spec.body), sk = body.skeleton;
const fig = new ContactFigure(body, spec, { position: [+x, 0, +z], heading: +heading });
const clip = clipOf([await loadMotion(new URL(`motions/${mid}.json`, here), E.skeleton, read)]);

// the point: at frame 0, the highest skin of the left collarbone and upper arm within 2 cm (over the floor) of the
// place (by default) 15% of the way from the shoulder joint (the arm's head) to the collarbone's inner end — the top of the
// shoulder. (A third of the way, tried first, is nearly at the neck: the hand lay on the trapezius by the neck.)
fig.frame(clip, 0);
const P = fig.pose.P, a = sk.index.LeftArm * 3, s = sk.index.LeftShoulder * 3;
const c = [P[a] + (P[s] - P[a]) * +share, P[a + 2] + (P[s + 2] - P[a + 2]) * +share];
console.log('arm joint', [P[a], P[a + 1], P[a + 2]].map(x => +x.toFixed(3)), 'collarbone joint', [P[s], P[s + 1], P[s + 2]].map(x => +x.toFixed(3)));
let v = -1, top = -Infinity;
const shoulder = body.part('Lclavicle'), arm = body.part('LupperArm');
for (let i = 0; i < body.N; i++) {
  if (shoulder[i] + arm[i] < 0.5) continue;
  const px = fig.positions[i * 3], py = fig.positions[i * 3 + 1], pz = fig.positions[i * 3 + 2];
  if (Math.hypot(px - c[0], pz - c[1]) < 0.02 && py > top) { top = py; v = i; }
}
const at = [];
for (let t = 0; t < clip.frames; t++) { fig.frame(clip, t); at.push([0, 1, 2].map(k => +fig.positions[v * 3 + k].toFixed(4))); }
await writeFile(new URL(`plans/${outName}.json`, here), JSON.stringify({ who, motion: mid, place: { position: [+x, 0, +z], heading: +heading }, vertex: v, at }));
console.log('vertex', v, 'at frame 0', at[0], 'frames', at.length);
