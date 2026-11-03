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
import { pinned, checkPin, canonical, hashOf } from './hash.js';
import { resolve, checkPreset } from './character.js';
import { turnAtRest, morphAtRest } from './changes.js';
import { DEFORMERS, deformAtRest, layerOf, turnLayer, restLayer } from './deform.js';
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
    character: async id => E.expand(await E.resolve(await E.description(id))),
    // a description resolved (src/character.js), with the character it starts from (`base`) resolved first
    resolve: async d => d.base ? resolve(d, skeleton, await E.resolve(await E.base(d.base))) : resolve(d, skeleton),
    // a character's description pinned by its content (what a `base` names): refused if it changed under the pin
    base: ref => pinnedLoad('character ', ref, id => async () => { const d = await E.description(id); return { ...d, hash: hashOf([d]) }; }).then(d => { const o = { ...d }; delete o.hash; return o; }),
    bodies: () => once('bi', () => readJSON(new URL('data/bodies/index.json', root), read)),
    // presets (presets/<id>.json, presets/index.json): checked, pinned like bodies
    presets: () => once('pi', () => readJSON(new URL('presets/index.json', root), read)),
    preset: ref => pinnedLoad('preset ', ref, id => async () => { const p = checkPreset(await readJSON(new URL(`presets/${id}.json`, root), read)); return { ...p, hash: hashOf([p]) }; }),
    // a resolved character with its presets taken apart into their changes (src/character.js: presets)
    async expand(spec) {
      const open = async (list, mode, depth = 0) => {
        const out = [];
        for (const c of list) {
          if (c.kind !== 'preset') { out.push(c); continue; }
          if (depth > 8) throw new Error(`preset ${c.id}: presets nested deeper than 8 (a cycle?)`);
          const p = await E.preset(c.id), k = c.strength ?? 1;
          const inner = p.changes.map(x => ({ ...x, strength: (x.strength ?? 1) * k, ...(mode === 'rest' ? { frames: c.frames } : c.space && (x.kind === 'preset' || layerOf(x.kind) === 'turns') ? { space: c.space } : {}) }));
          if (mode === 'pose') for (const x of inner) if (x.kind !== 'preset' && !layerOf(x.kind)) throw new Error(`preset ${c.id}: ${x.kind} gives its own skin weights — a change of the rest only, not a pose layer`);
          out.push(...await open(inner, mode, depth + 1));
        }
        return out;
      };
      return { ...spec, rest: await open(spec.rest, 'rest'), pose: await open(spec.pose, 'pose') };
    },
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
        for (const c of spec.rest) b = c.kind === 'turn' ? turnAtRest(b, c) : c.kind === 'morph' ? morphAtRest(b, c) : DEFORMERS[c.kind] ? await deformAtRest(b, c, E) : (() => { throw new Error(`no rest change "${c.kind}"`); })();
        return b;
      });
    },
    // a character (by id, or a resolved description) as a figure. layers: the character's code, after its own pose
    // layers ({kind: 'code', apply(pose, ctx)}); meshes: more meshes off its pose ([{mesh, name?, skinning?}])
    // Pose layers run in the order listed (src/figure.js). A deformer as a layer is a change of the pose (its turns:
    // src/deform.js turnLayer) or its rest change weighed in each frame (restLayer: named "<its place in the list>:<kind>"
    // for ctx.weights), made on the body with the changes of the rest before it in the list.
    async figure(c, { place, layers = [], meshes = [] } = {}) {
      const spec = typeof c === 'string' ? await E.character(c) : c.pose.some(l => l.kind === 'preset') || c.rest.some(l => l.kind === 'preset') ? await E.expand(c) : c;
      const body = await E.restBody(spec), list = [];
      let from = body, chain = [];
      for (const [k, l] of spec.pose.entries()) {
        if (!DEFORMERS[l.kind]) { list.push(l); continue; }
        const how = layerOf(l.kind);
        if (how === 'turns') { list.push(turnLayer(l, body)); continue; }
        if (!how) throw new Error(`${l.kind} gives its own skin weights: it is a change of the rest only (rest: [{kind: "${l.kind}", …, frames}])`);
        chain = [...chain, l];
        const to = await E.layerBody(spec, chain);
        list.push(restLayer(`${k}:${l.kind}`, l, from, to, spec.skinning.sigma));
        from = to;
      }
      return new Figure({
        rig: body.rig, body, place, floor: spec.motion.floor, layers: [...list, ...layers],
        meshes: [{ mesh: body.mesh, name: 'body', skinning: spec.skinning }, ...meshes],
      });
    },
    // the character's rest with the changes of the rest among its pose layers made, up to the last of `chain` (kept)
    layerBody(spec, chain) {
      return once('lb:' + spec.body + canonical(spec.rest) + canonical(chain), async () => {
        const from = chain.length > 1 ? await E.layerBody(spec, chain.slice(0, -1)) : await E.restBody(spec);
        return deformAtRest(from, { ...chain[chain.length - 1], frames: 'keep' }, E);
      });
    },
  };
  return E;
}
