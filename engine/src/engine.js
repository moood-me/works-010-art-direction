// The engine's entry: where its data is, and what reads it. Nothing here knows a character, a port or a size:
// the data's root is found from this file's own place (or given), everything is named by id — or by id@hash, which
// refuses data that changed under the pin (src/hash.js).
//   const E = await createEngine();                          // engine/ beside src/
//   const body = await E.body('moood-woman'), m = await E.motion('walk');
//   const clip = await E.clip('lie-rollover');                // a motion, a chain of motions/index.json, or
//                                                             // {motions: [ids], joins: [{blend…}]}
//   const fig = await E.figure('woman', {place: {position: [0, 0, 0], heading: 0}});  fig.frame(clip, 12.5)
import { loadSkeleton } from './skeleton.js';
import { loadBody } from './body.js';
import { loadMotion, clipOf } from './motion.js';
import { loadSoma } from './soma.js';
import { readJSON, defaultRead } from './pack.js';
import { pinned, checkPin, canonical } from './hash.js';
import { resolve } from './character.js';
import { turnAtRest, morphAtRest } from './changes.js';
import { Figure } from './figure.js';

export async function createEngine({ root = new URL('../', import.meta.url), read = defaultRead } = {}) {
  root = new URL(root);
  const skeleton = await loadSkeleton(new URL('data/skeleton.json', root), read);
  const cache = new Map(), once = (key, make) => { if (!cache.has(key)) cache.set(key, make()); return cache.get(key); };
  const pinnedLoad = (kind, ref, load) => { const { id } = pinned(ref); return once(kind + id, load(id)).then(x => { checkPin(ref, kind, x.hash); return x; }); };
  const E = {
    root, skeleton,
    body: ref => pinnedLoad('body ', ref, id => () => loadBody(new URL(`data/bodies/${id}.json`, root).href, skeleton, read)),
    motion: ref => pinnedLoad('motion ', ref, id => () => loadMotion(new URL(`motions/${id}.json`, root), skeleton, read)),
    motions: () => once('mi', () => readJSON(new URL('motions/index.json', root), read)),
    soma: () => once('soma', () => loadSoma(new URL('data/soma/soma.bin', root), read)),
    characters: () => once('ci', () => readJSON(new URL('characters/index.json', root), read)),
    description: id => once('d:' + id, () => readJSON(new URL(`characters/${id}.json`, root), read)),
    character: async id => resolve(await E.description(id), skeleton),
    // what plays: a motion id, a chain's id (motions/index.json), or {motions: [refs], joins}
    async clip(what) {
      let spec = what;
      if (typeof what === 'string') {
        const index = await E.motions(), chain = index.chains.find(c => c.id === what);
        spec = chain ?? { motions: [what], joins: [] };
      }
      const key = canonical(spec);
      return once('clip:' + key, async () => {
        const motions = await Promise.all(spec.motions.map(E.motion));
        const soma = spec.joins.some(j => j.blend === 'dead') ? await E.soma() : null;
        return clipOf(motions, { joins: spec.joins, soma });
      });
    },
    // the character's body with its rest changes made (src/changes.js), kept for every figure of it
    restBody(spec) {
      return once('rest:' + spec.body + canonical(spec.rest), async () => {
        let b = await E.body(spec.body);
        for (const c of spec.rest) b = c.kind === 'turn' ? turnAtRest(b, c) : c.kind === 'morph' ? morphAtRest(b, c) : (() => { throw new Error(`no rest change "${c.kind}"`); })();
        return b;
      });
    },
    // a character (by id, or a resolved description) as a figure. layers: the character's code, after its own pose
    // layers ({kind: 'code', apply(pose, ctx)}); meshes: more meshes off its pose ([{mesh, name?, skinning?}])
    async figure(c, { place, layers = [], meshes = [] } = {}) {
      const spec = typeof c === 'string' ? await E.character(c) : c;
      const body = await E.restBody(spec);
      return new Figure({
        rig: body.rig, body, place, floor: spec.motion.floor, layers: [...spec.pose, ...layers],
        meshes: [{ mesh: body.mesh, name: 'body', skinning: spec.skinning }, ...meshes],
      });
    },
  };
  return E;
}
