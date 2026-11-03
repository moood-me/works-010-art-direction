// A character: plain data (characters/<id>.json) that names a body and says how it is changed, skinned, moved and
// looked at. Checked against its schema: an unknown key or value is refused, not ignored. The body is pinned by its
// content hash (`moood-woman@3f2a…`): if the body's data changes, the character is refused until someone looks at the
// difference and pins it anew (tools/characters.mjs pin). The format has a version; when it changes, `upgrade` turns a
// description of an earlier version into the current one (tools/characters.mjs upgrade). Whether an engine change
// alters a character is what the checks see (check/numbers.mjs, check/pictures.mjs).
//
//   {format: "engine/character", version: 2, id, label: {ru, en},
//    body: "<body id>@<hash>",
//    rest: [change…]     changes of the body's rest, in order (src/changes.js):
//                        {kind: "turn", joint, axis: [x, y, z] (in the joint's own frame), degrees, frames: "keep" | "turn"}
//                        {kind: "morph", name, weight}
//                        {kind: <a deformer>, …its parameters, strength, frames} (src/deform.js, src/deformers/)
//                        {kind: "preset", id: "<preset>@<hash>", strength, frames} (presets/: its changes, each × strength)
//    pose: [layer…]      pose layers on every frame, in order (src/layers.js): {kind: "armsOff", degrees?},
//                        {kind: "armsOutOfHead", margin?}, {kind: "amplifyLimbs", factor?, parts?},
//                        {kind: "dampHeadSpine", spine?, head?}, {kind: "clavicleShare", share?},
//                        {kind: "turn", joint, axis, degrees}, {kind: "morph", name, weight},
//                        {kind: <a deformer that moves no joints>, …, strength, space?: "pelvis" | "upright"},
//                        {kind: "preset", id, strength, space?}
//    skinning: {method: "cor" | "dqs" | "lbs", sigma (the centres' likeness, cor), seam: null | {iterations, rings}},
//    motion: {floor: "lowest" | "pelvis"},
//    look: {skin: "#rrggbb", roughness}}
// motion.floor: "lowest" — after everything is drawn, the figure's lowest point as high as SOMA's skin's lowest then
// (scaled): standing on its feet, lying on its back, nothing in the floor; "pelvis" — only the pelvis's height scaled.
import { validate } from './schema.js';
import { pinned } from './hash.js';
import { DEFORMERS } from './deform.js';
import './deformers/index.js';

export const FORMAT = 'engine/character', VERSION = 2;

const PARTS = ['pelvis', 'spine', 'neck', 'head', 'eye', 'clavicle', 'upperArm', 'foreArm', 'hand', 'finger', 'thigh', 'shin', 'foot', 'toe'];
// the defaults, the one place they are kept: a missing key takes these
export const DEFAULTS = {
  skinning: { method: 'cor', sigma: 0.1, seam: null },
  seam: { iterations: 10, rings: 3 },
  motion: { floor: 'lowest' },
  look: { skin: '#d9b49a', roughness: 0.65 },
  layers: {
    armsOff: { degrees: 7 }, armsOutOfHead: { margin: 0.02 }, amplifyLimbs: { factor: 1.3, parts: ['upperArm', 'foreArm', 'thigh', 'shin'] },
    dampHeadSpine: { spine: 0.7, head: 0.7 }, clavicleShare: { share: 1 / 3 },
  },
};

const num = (min, max) => ({ type: 'number', min, max });
const axis = { type: 'array', items: num(-1, 1), min: 3, max: 3 };
export function schemaOf(skeleton) {
  const joint = { type: 'string', enum: skeleton.names };
  const turn = { type: 'object', props: { kind: { const: 'turn' }, joint, axis, degrees: num(-180, 180) }, required: ['kind', 'joint', 'axis', 'degrees'] };
  const morph = { type: 'object', props: { kind: { const: 'morph' }, name: { type: 'string', pattern: /^[A-Za-z][A-Za-z0-9]*$/ }, weight: num(-2, 2) }, required: ['kind', 'name', 'weight'] };
  const layer = (kind, props) => ({ type: 'object', props: { kind: { const: kind }, ...props }, required: ['kind'] });
  const frames = { type: 'string', enum: ['keep', 'turn'] }, space = { type: 'string', enum: ['pelvis', 'upright'] };
  // a deformer (src/deform.js): its own parameters, its strength, and how it goes on the rest (frames) or as a layer (space)
  const deformer = (d, more, required) => ({ type: 'object', props: { kind: { const: d.kind }, ...d.params, strength: num(-3, 3), ...more }, required: ['kind', ...required] });
  // a preset (presets/<id>.json): its changes, each one's strength times this one
  const preset = { type: 'object', props: { kind: { const: 'preset' }, id: { type: 'string', pattern: /^[a-z0-9][a-z0-9-]*@[0-9a-f]{12,64}$/ }, strength: num(-3, 3) }, required: ['kind', 'id'] };
  return {
    type: 'object', required: ['format', 'version', 'id', 'label', 'body'],
    props: {
      format: { const: FORMAT }, version: { const: VERSION },
      id: { type: 'string', pattern: /^[a-z0-9][a-z0-9-]*$/ },
      label: { type: 'object', props: { ru: { type: 'string' }, en: { type: 'string' } }, required: ['ru', 'en'] },
      body: { type: 'string', pattern: /^[A-Za-z0-9_.-]+@[0-9a-f]{12,64}$/ },
      rest: { type: 'array', items: { type: 'union', key: 'kind', cases: {
        turn: { ...turn, props: { ...turn.props, frames }, required: [...turn.required, 'frames'] },
        morph, preset: { ...preset, props: { ...preset.props, frames }, required: [...preset.required, 'frames'] },
        ...Object.fromEntries(Object.values(DEFORMERS).map(d => [d.kind, deformer(d, { frames }, ['frames'])])) } } },
      pose: { type: 'array', items: { type: 'union', key: 'kind', cases: {
        armsOff: layer('armsOff', { degrees: num(-45, 45) }),
        armsOutOfHead: layer('armsOutOfHead', { margin: num(0, 0.2) }),
        amplifyLimbs: layer('amplifyLimbs', { factor: num(0, 3), parts: { type: 'array', items: { type: 'string', enum: PARTS }, min: 1 } }),
        dampHeadSpine: layer('dampHeadSpine', { spine: num(0, 2), head: num(0, 2) }),
        clavicleShare: layer('clavicleShare', { share: num(0, 1) }),
        turn, morph, preset: { ...preset, props: { ...preset.props, space } },
        ...Object.fromEntries(Object.values(DEFORMERS).filter(d => !d.joints).map(d => [d.kind, deformer(d, d.of === 'figure' ? { space } : {}, [])])) } } },
      skinning: { type: 'object', props: {
        method: { type: 'string', enum: ['cor', 'dqs', 'lbs'] }, sigma: num(0.01, 1),
        seam: { anyOf: [{ type: 'null' }, { type: 'object', props: { iterations: { type: 'integer', min: 1, max: 200 }, rings: { type: 'integer', min: 0, max: 20 } } }] } } },
      motion: { type: 'object', props: { floor: { type: 'string', enum: ['lowest', 'pelvis'] } } },
      look: { type: 'object', props: { skin: { type: 'string', pattern: /^#[0-9a-f]{6}$/i }, roughness: num(0, 1) } },
    },
  };
}

// A preset (presets/<id>.json): a named list of changes — deformers with their parameters and strengths, or other
// presets — that a character takes into its rest or its pose layers ({kind: "preset", id: "<id>@<hash>", strength,
// frames | space}); each of its changes' strength is multiplied by the reference's, the reference says how they go on
// the rest (frames) or as a layer (space). Plain data an author can read, copy and change.
//   {format: "engine/preset", version: 1, id, label: {ru, en}, group, about: {ru, en}, changes: [change…]}
export const PRESET_FORMAT = 'engine/preset', PRESET_VERSION = 1;
export function presetSchemaOf() {
  const num = (min, max) => ({ type: 'number', min, max });
  const ref = { type: 'object', props: { kind: { const: 'preset' }, id: { type: 'string', pattern: /^[a-z0-9][a-z0-9-]*@[0-9a-f]{12,64}$/ }, strength: num(-3, 3) }, required: ['kind', 'id'] };
  return {
    type: 'object', required: ['format', 'version', 'id', 'label', 'group', 'changes'],
    props: {
      format: { const: PRESET_FORMAT }, version: { const: PRESET_VERSION }, id: { type: 'string', pattern: /^[a-z0-9][a-z0-9-]*$/ },
      label: { type: 'object', props: { ru: { type: 'string' }, en: { type: 'string' } }, required: ['ru', 'en'] },
      group: { type: 'string', pattern: /^[a-z][a-z-]*$/ },
      about: { type: 'object', props: { ru: { type: 'string' }, en: { type: 'string' } }, required: ['ru', 'en'] },
      changes: { type: 'array', min: 1, items: { type: 'union', key: 'kind', cases: {
        preset: ref,
        ...Object.fromEntries(Object.values(DEFORMERS).map(d => [d.kind, { type: 'object', props: { kind: { const: d.kind }, ...d.params, strength: num(-3, 3) }, required: ['kind'] }])) } } },
    },
  };
}
export function checkPreset(p) {
  if (p?.format !== PRESET_FORMAT || p.version !== PRESET_VERSION) throw new Error(`${p?.id ?? '?'}: not a preset of version ${PRESET_VERSION}`);
  validate(p, presetSchemaOf(), 'preset ' + p.id);
  return p;
}

// a description checked and completed by the defaults: what the engine builds a figure from
export function resolve(desc, skeleton) {
  if (desc?.format !== FORMAT) throw new Error(`${desc?.id ?? '?'}: not a character`);
  if (desc.version !== VERSION) {
    if (desc.version < VERSION) throw new Error(`${desc.id}: a character of version ${desc.version} — upgrade it to ${VERSION} (node engine/tools/characters.mjs upgrade ${desc.id})`);
    throw new Error(`${desc.id}: character version ${desc.version} is newer than this engine knows (${VERSION})`);
  }
  validate(desc, schemaOf(skeleton), desc.id);
  const sk = { ...DEFAULTS.skinning, ...(desc.skinning || {}) };
  if (sk.seam) sk.seam = { ...DEFAULTS.seam, ...sk.seam };
  return {
    id: desc.id, label: desc.label, version: desc.version, body: desc.body, bodyId: pinned(desc.body).id,
    rest: (desc.rest || []).map(c => ({ ...c })),
    pose: (desc.pose || []).map(l => ({ ...(DEFAULTS.layers[l.kind] || {}), ...l })),
    skinning: sk,
    motion: { ...DEFAULTS.motion, ...(desc.motion || {}) },
    look: { ...DEFAULTS.look, ...(desc.look || {}) },
  };
}

// a description of an earlier version as the current one. bodyPin: the body's id@hash now (version 1 named a body by
// id alone; upgrading pins the body as it is — look at the character after upgrading).
export function upgrade(desc, { bodyPin }) {
  let d = structuredClone(desc);
  if (d.format !== FORMAT) throw new Error(`${d.id ?? '?'}: not a character`);
  if (d.version === 1) {
    // version 1: {body: id, skinning: {method, clavicleShare, seam}, motion: {floor, corrections: {name: params}}, look}
    // → 2: the body pinned; the collarbone's share and the corrections are pose layers, in the order they were applied
    // (corrections first, in their order, then the collarbone's share)
    if (pinned(bodyPin).id !== d.body) throw new Error(`${d.id}: upgrading names body ${d.body}, not ${bodyPin}`);
    const pose = [];
    for (const [kind, prm] of Object.entries(d.motion?.corrections || {})) {
      if (prm && prm.on === false) continue;
      pose.push({ kind, ...Object.fromEntries(Object.entries(prm || {}).filter(([k]) => k !== 'on')) });
    }
    const share = d.skinning?.clavicleShare ?? 0;
    if (share > 0) pose.push({ kind: 'clavicleShare', share });
    const skinning = { ...(d.skinning || {}) }; delete skinning.clavicleShare;
    const motion = { ...(d.motion || {}) }; delete motion.corrections;
    d = { format: FORMAT, version: 2, id: d.id, label: d.label, body: bodyPin, rest: [], pose, skinning, motion, look: d.look };
    for (const k of ['skinning', 'motion', 'look']) if (d[k] === undefined) delete d[k];
  }
  if (d.version !== VERSION) throw new Error(`${d.id}: no way from version ${d.version} to ${VERSION}`);
  return d;
}
