// The engine's entry: where its data is, and what reads it. Nothing here knows a character, a port or a size:
// the data's root is found from this file's own place (or given), everything is named by id.
//   const E = await createEngine();                         // engine/ beside src/
//   const body = await E.body('moood-woman'), m = await E.motion('walk');
//   const clip = await E.clip(['lie', 'rollover']);          // a chain
//   const fig = await E.figure('woman', {position: [0, 0, 0], heading: 0});  fig.frame(clip, 12.5).positions
import { loadSkeleton } from './skeleton.js';
import { loadBody } from './body.js';
import { loadMotion, clipOf } from './motion.js';
import { readJSON } from './pack.js';
import { resolve } from './character.js';
import { Figure } from './figure.js';

export async function createEngine({ root = new URL('../', import.meta.url), read } = {}) {
  root = new URL(root);
  const skeleton = await loadSkeleton(new URL('data/skeleton.json', root), read);
  const cache = new Map(), once = (key, make) => { if (!cache.has(key)) cache.set(key, make()); return cache.get(key); };
  const E = {
    root, skeleton,
    body: id => once('b:' + id, () => loadBody(new URL(`data/bodies/${id}.json`, root).href, skeleton, read)),
    motion: id => once('m:' + id, () => loadMotion(new URL(`motions/${id}.json`, root), skeleton, read)),
    motions: () => once('mi', () => readJSON(new URL('motions/index.json', root), read)),
    characters: () => once('ci', () => readJSON(new URL('characters/index.json', root), read)),
    character: id => once('c:' + id, async () => resolve(await readJSON(new URL(`characters/${id}.json`, root), read))),
    clip: async ids => clipOf(await Promise.all(ids.map(E.motion))),
    // a character (by id, or a description already resolved) as a figure placed where asked
    async figure(c, place) {
      const spec = typeof c === 'string' ? await E.character(c) : c;
      return new Figure(await E.body(spec.body), spec, place);
    },
  };
  return E;
}
