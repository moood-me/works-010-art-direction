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
import { readJSON, defaultRead, loadPack } from './pack.js';
import { pinned, checkPin, canonical, hashOf } from './hash.js';
import { resolve, checkPreset } from './character.js';
import { turnAtRest, morphAtRest } from './changes.js';
import { DEFORMERS, deformAtRest, layerOf, turnLayer, restLayer, complete } from './deform.js';
import { Figure } from './figure.js';
import { buildHead, LIGHT_DEFAULTS } from './head/head.js';
import { featureId, FEATURE_SCHEMA } from './head/features.js';
import { EXPRESSION_SCHEMA } from './head/expressions.js';
import { PIECE_SCHEMA } from './head/pieces.js';
import { makeMesh } from './mesh.js';
import { stylesOf, hairSims } from './hair/hair.js';
import { overParts } from './parts.js';
import { clothesOn, clothSim, GARMENT_SCHEMA, garmentId } from './cloth/clothes.js';

// a way of a head's form by its name: its own, or a preset's id, or a deformer's kind
const wayName = c => c.name ?? (c.kind === 'preset' ? pinned(c.id).id : c.kind);

export async function createEngine({ root = new URL('../', import.meta.url), read = defaultRead } = {}) {
  root = new URL(root);
  const skeleton = await loadSkeleton(new URL('data/skeleton.json', root), read);
  const cache = new Map(), once = (key, make) => { if (!cache.has(key)) cache.set(key, make()); return cache.get(key); };
  const pinnedLoad = (kind, ref, load) => { const { id } = pinned(ref); return once(kind + id, load(id)).then(x => { checkPin(ref, kind, x.hash); return x; }); };
  const E = {
    root, skeleton, read,
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
    // Anny's own changes of the face (data/anny/face.json, tools/face_targets.py): {unit, changes: {name: {i, p, n}}}
    faceTargets: () => once('face', async () => {
      const { header: h, arrays: a } = await loadPack(new URL('data/anny/face.json', root).href, read);
      return { unit: h.unit, topology: h.topology, changes: Object.fromEntries(h.changes.map(c => [c.name, { i: a['i' + c.key], p: a['p' + c.key], n: a['n' + c.key] }])) };
    }),
    // what is slow to make, stored by the key of all it is made from (data/<kind>/index.json lists the keys stored, each
    // a pack data/<kind>/<key>.json): the pack ({header, arrays}), or null when it is not stored (then it is made where
    // it is needed)
    stored: async (kind, key) => {
      const index = await once('stored:' + kind, () => readJSON(new URL(`data/${kind}/index.json`, root), read));
      return index.keys.includes(key) ? loadPack(new URL(`data/${kind}/${key}.json`, root).href, read) : null;
    },
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
      const head = spec.head ? await E.headOf(spec.head, spec.look) : null, clothes = spec.clothes ? await E.clothesOf(spec.clothes) : [];
      const rest = await open(spec.rest, 'rest');
      if (!head) return { ...spec, rest, pose: await open(spec.pose, 'pose'), head: null, clothes, expanded: true };
      // the head's form: changes of the rest after the character's own, frames kept (a design rides along in motion)
      const form = await open(head.form.map(c => ({ ...c, frames: 'keep' })), 'rest');
      // the last wrap onto a designed form: where in the rest it is made (the face is drawn on the head it leaves)
      const w = form.findLastIndex(c => c.kind === 'wrap'), wrap = w < 0 ? null : complete(form[w]);
      return { ...spec, rest: [...rest, ...form], pose: await open(spec.pose, 'pose'), head: { ...head, formAt: rest.length, wrapAt: w < 0 ? null : rest.length + w, wrap }, clothes, expanded: true };
    },
    // a head with what it starts from (its base's head, its preset, the preset's own) merged under it, its presets of
    // features, expressions, pieces and light taken in: {size, skin, form, features, expressions, pieces, light}. Its
    // own parts go over theirs by id (features, pieces) or name (expressions, the form's ways: a preset's id, or a
    // deformer's kind, unless it names itself): {kind: "off"} takes one away, one with no kind changes the keys it gives
    // (then checked whole; an expression, which has no kind, is new when there is none of its name), a whole one takes
    // the place of theirs, a new one comes after; `strength` weighs the form it starts from
    async headOf(h, look = {}, depth = 0) {
      if (depth > 8) throw new Error('heads nested deeper than 8 (a cycle?)');
      const under = h.under ? await E.headOf(h.under, look, depth + 1) : h.preset ? await E.headOf(await E.headPreset(h.preset), look, depth + 1) : { form: [], features: [], expressions: [], pieces: [], light: { ...LIGHT_DEFAULTS } };
      const inline = async (list, key) => (await Promise.all((list || []).map(async x => x.kind === 'preset' ? (await E.preset(x.id))[key] ?? (() => { throw new Error(`preset ${x.id} has no ${key}`); })() : [x]))).flat();
      const light = h.light?.kind === 'preset' ? (await E.preset(h.light.id)).light : h.light, k = h.strength ?? 1;
      return {
        size: h.size ?? under.size, skin: h.skin ?? under.skin ?? look.skin, ref: h.ref ?? under.ref ?? null,
        form: overParts(under.form.map(c => k === 1 ? c : { ...c, strength: (c.strength ?? 1) * k }), (h.form || []).map(c => ({ ...c, name: wayName(c) })), c => c.name, null, 'a way of the form'),
        features: overParts(under.features, await inline(h.features, 'features'), featureId, FEATURE_SCHEMA, 'feature'),
        expressions: overParts(under.expressions, await inline(h.expressions, 'expressions'), x => x.name, EXPRESSION_SCHEMA, 'expression', true),
        pieces: overParts(under.pieces, await inline(h.pieces, 'pieces'), p => p.id ?? p.kind, PIECE_SCHEMA, 'piece'),
        light: { ...under.light, ...(light || {}) },
      };
    },
    // a character's clothes with what they start from (its base's) under them, its outfits taken in (src/parts.js), each
    // garment's fabric and shape as their keys (a preset's, or its own): [garment…] (src/cloth/clothes.js)
    async clothesOf(c, depth = 0) {
      if (depth > 8) throw new Error('clothes nested deeper than 8 (a cycle?)');
      const under = c.under ? await E.clothesOf(c.under, depth + 1) : [];
      const own = (await Promise.all(c.list.map(async g => g.kind === 'preset' ? (await E.preset(g.id)).clothes ?? (() => { throw new Error(`preset ${g.id} holds no clothes`); })() : [g]))).flat();
      const content = async (ref, key) => typeof ref === 'string' ? (await E.preset(ref))[key] ?? (() => { throw new Error(`preset ${ref} is not a ${key}`); })() : ref;
      return Promise.all(overParts(under, own, garmentId, GARMENT_SCHEMA, 'garment').map(async g => ({ ...g, id: garmentId(g), fabric: await content(g.fabric, 'fabric'), shape: g.shape ? await content(g.shape, 'shape') : null })));
    },
    // a head preset's head (presets/ of group "head"), pinned
    headPreset: async ref => { const p = await E.preset(ref); if (!p.head) throw new Error(`preset ${ref} is not a head`); return p.head; },
    // the character's body with its head made on it (src/head/head.js), and the meshes beside its skin (kept)
    headBody(spec) {
      if (!spec.head) return E.restBody(spec).then(body => ({ body, meshes: [] }));
      return once('head:' + spec.body + canonical(spec.rest) + canonical(spec.head), async () => {
        const upTo = n => E.restBody({ ...spec, rest: spec.rest.slice(0, n) }), { formAt, wrapAt } = spec.head, pre = await upTo(formAt);
        const styles = await stylesOf(spec.head.pieces, E);
        const { body, meshes } = buildHead({ pre, laid: wrapAt == null ? null : await upTo(wrapAt), drawn: wrapAt == null ? pre : await upTo(wrapAt + 1), post: await E.restBody(spec) }, { ...spec.head, styles });
        return { body, meshes: meshes.map(m => makeMesh(m)) };
      });
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
      const spec = typeof c === 'string' ? await E.character(c) : c.expanded ? c : await E.expand(c);
      const { body, meshes: head } = await E.headBody(spec), list = [], laid = await clothesOn(body, spec.clothes, E);
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
      const figure = new Figure({
        rig: body.rig, body, place, floor: spec.motion.floor, layers: [...list, ...layers],
        meshes: [{ mesh: body.mesh, name: 'body', skinning: spec.skinning }, ...head.map(mesh => ({ mesh, name: mesh.id, skinning: mesh.skinning ?? spec.skinning })),
          ...laid.map(l => ({ mesh: l.mesh, name: l.mesh.id, skinning: l.mesh.skinning })), ...meshes],
      });
      // clothes that move: one simulation for all of them (src/cloth/sim.js), before the hair (which lies over them)
      const cloth = clothSim(figure, laid); if (cloth) figure.addSimulation(cloth);
      // hair that moves: a simulation of its own on the figure's step (src/hair/sim.js)
      for (const sim of hairSims(figure)) figure.addSimulation(sim);
      return figure;
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
