// A character: plain data (characters/<id>.json) that names a body and says how it is changed, skinned, moved and
// looked at. Checked against its schema: an unknown key or value is refused, not ignored. The body is pinned by its
// content hash (`moood-woman@3f2a…`): if the body's data changes, the character is refused until someone looks at the
// difference and pins it anew (tools/characters.mjs pin). The format has a version; when it changes, `upgrade` turns a
// description of an earlier version into the current one (tools/characters.mjs upgrade). Whether an engine change
// alters a character is what the checks see (check/numbers.mjs, check/pictures.mjs).
//
//   {format: "engine/character", version: 3, id, label: {ru, en},
//    base?: "<character id>@<hash>"   another character this one starts from (a full-body preset): its body, rest, pose,
//                        skinning, motion and look, with this one's over them — its body if it names one, its rest
//                        changes and pose layers after the base's, its skinning, motion and look keys over the base's
//    body: "<body id>@<hash>"   (required without a base),
//    rest: [change…]     changes of the body's rest, in order (src/changes.js):
//                        {kind: "turn", joint, axis: [x, y, z] (in the joint's own frame), degrees, frames: "keep" | "turn"}
//                        {kind: "morph", name, weight}
//                        {kind: <a deformer>, …its parameters, strength, frames} (src/deform.js, src/deformers/)
//                        {kind: "preset", id: "<preset>@<hash>", strength, frames} (presets/: its changes, each × strength)
//    pose: [layer…]      pose layers on every frame, in order (src/layers.js): {kind: "armsOff", degrees?, clear?},
//                        {kind: "armsOutOfHead", margin?}, {kind: "amplifyLimbs", factor?, parts?},
//                        {kind: "dampHeadSpine", spine?, head?}, {kind: "clavicleShare", share?},
//                        {kind: "turn", joint, axis, degrees}, {kind: "morph", name, weight},
//                        {kind: <a deformer>, …, strength} (src/deform.js: a change of the pose — the line, contrapposto,
//                        with space?: "pelvis" | "upright" — or a change of the form, its rest change weighed in; the
//                        sign is a change of the rest only), {kind: "preset", id, strength, space?}
//    skinning: {method: "cor" | "dqs" | "lbs", sigma (the centres' likeness, cor), seam: null | {iterations, rings}},
//    motion: {floor: "lowest" | "pelvis"},
//    look: {skin: "#rrggbb", roughness},
//    head?: {preset?: "<head preset>@<hash>",  the head this one starts from (a part: presets/ of group "head")
//            size?          how big the head is drawn against Anny's own (head units, src/head/frame.js)
//            form?: [change…]   changes of the rest made after the character's own (deformers: the wrap onto a designed
//                           form, the face deformers, Anny's own face, a head of another age; or presets of them)
//            features?: [feature…]   painted or as volume (src/head/features.js), or {kind: "preset"} of features;
//                           {kind: "off", id} takes one of the base's away
//            expressions?: [expression…]   by the mesh (src/head/expressions.js), or {kind: "preset"} of them
//            pieces?: [piece…]   meshes on the rig beside the skin (src/head/pieces.js)
//            light?: {toon, soft, outline, outlineColor, design, faceShadows} or {kind: "preset", id}
//            skin?: the face picture's skin colour (else look.skin)
//            ref?: {image, points, view, crop} — the picture it was drawn after (tools/overlay.mjs)}
//    — this one's head over its base's and its preset's: its size, skin and light keys over theirs, its form after
//    theirs, its features, expressions and pieces replacing theirs of the same id (name) and added after them
// motion.floor: "lowest" — after everything is drawn, the figure's lowest point as high as SOMA's skin's lowest then
// (scaled): standing on its feet, lying on its back, nothing in the floor; "pelvis" — only the pelvis's height scaled.
import { validate, num, color, pin } from './schema.js';
import { pinned } from './hash.js';
import { DEFORMERS, layerOf } from './deform.js';
import './deformers/index.js';
import { FEATURE_SCHEMA } from './head/features.js';
import { EXPRESSION_SCHEMA } from './head/expressions.js';
import { PIECE_SCHEMA } from './head/pieces.js';
import { LIGHT_SCHEMA } from './head/head.js';

export const FORMAT = 'engine/character', VERSION = 5;

const PARTS = ['pelvis', 'spine', 'neck', 'head', 'eye', 'clavicle', 'upperArm', 'foreArm', 'hand', 'finger', 'thigh', 'shin', 'foot', 'toe'];
// the defaults, the one place they are kept: a missing key takes these
export const DEFAULTS = {
  skinning: { method: 'cor', sigma: 0.1, seam: null },
  seam: { iterations: 10, rings: 3 },
  motion: { floor: 'lowest' },
  look: { skin: '#d9b49a', roughness: 0.65 },
  layers: {
    armsOff: { degrees: 7, clear: 0 }, armsOutOfHead: { margin: 0.02 }, amplifyLimbs: { factor: 1.3, parts: ['upperArm', 'foreArm', 'thigh', 'shin'] },
    dampHeadSpine: { spine: 0.7, head: 0.7 }, clavicleShare: { share: 1 / 3 },
  },
};

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
  const preset = { type: 'object', props: { kind: { const: 'preset' }, id: pin, strength: num(-3, 3) }, required: ['kind', 'id'] };
  // a change of a head's form: a deformer or a preset of them (made on the rest with its frames kept)
  const formChange = { type: 'union', key: 'kind', cases: { preset, ...Object.fromEntries(Object.values(DEFORMERS).map(d => [d.kind, deformer(d, {}, [])])) } };
  return {
    type: 'object', required: ['format', 'version', 'id', 'label'],
    props: {
      format: { const: FORMAT }, version: { const: VERSION },
      id: { type: 'string', pattern: /^[a-z0-9][a-z0-9-]*$/ },
      label: { type: 'object', props: { ru: { type: 'string' }, en: { type: 'string' } }, required: ['ru', 'en'] },
      base: pin,
      body: { type: 'string', pattern: /^[A-Za-z0-9_.-]+@[0-9a-f]{12,64}$/ },
      rest: { type: 'array', items: { type: 'union', key: 'kind', cases: {
        turn: { ...turn, props: { ...turn.props, frames }, required: [...turn.required, 'frames'] },
        morph, preset: { ...preset, props: { ...preset.props, frames }, required: [...preset.required, 'frames'] },
        ...Object.fromEntries(Object.values(DEFORMERS).map(d => [d.kind, deformer(d, { frames }, ['frames'])])) } } },
      pose: { type: 'array', items: { type: 'union', key: 'kind', cases: {
        armsOff: layer('armsOff', { degrees: num(-45, 45), clear: num(0, 0.1) }),
        armsOutOfHead: layer('armsOutOfHead', { margin: num(0, 0.2) }),
        amplifyLimbs: layer('amplifyLimbs', { factor: num(0, 3), parts: { type: 'array', items: { type: 'string', enum: PARTS }, min: 1 } }),
        dampHeadSpine: layer('dampHeadSpine', { spine: num(0, 2), head: num(0, 2) }),
        clavicleShare: layer('clavicleShare', { share: num(0, 1) }),
        turn, morph, preset: { ...preset, props: { ...preset.props, space } },
        expression: layer('expression', { name: { type: 'string', pattern: /^[a-z][a-zA-Z0-9]*$/ }, weight: num(-1, 2) }),
        ...Object.fromEntries(Object.values(DEFORMERS).filter(d => layerOf(d.kind)).map(d => [d.kind, deformer(d, layerOf(d.kind) === 'turns' ? { space } : {}, [])])) } } },
      skinning: { type: 'object', props: {
        method: { type: 'string', enum: ['cor', 'dqs', 'lbs'] }, sigma: num(0.01, 1),
        seam: { anyOf: [{ type: 'null' }, { type: 'object', props: { iterations: { type: 'integer', min: 1, max: 200 }, rings: { type: 'integer', min: 0, max: 20 } } }] } } },
      motion: { type: 'object', props: { floor: { type: 'string', enum: ['lowest', 'pelvis'] } } },
      look: { type: 'object', props: { skin: color, roughness: num(0, 1) } },
      head: headSchema(formChange),
    },
  };
}
// a head (a character's, or a head preset's): see the top. A list of the head's parts takes, besides whole parts: a
// preset of them ({kind: "preset", id}), one of what it starts from taken away ({kind: "off", id | name}), and one of
// those changed — only the keys that change, under its id (name): merged over it, then checked whole
const REF = { type: 'object', props: { kind: { const: 'preset' }, id: pin }, required: ['kind', 'id'] };
const OFF = { type: 'object', props: { kind: { const: 'off' }, id: { type: 'string' } }, required: ['kind', 'id'] };
const OFF_NAMED = { type: 'object', props: { kind: { const: 'off' }, name: { type: 'string' } }, required: ['kind', 'name'] };
// every key any case of a union has (but its kind), none required but `key`: a part changed by its id or name
const partial = (cases, key) => ({ type: 'object', required: [key], props: Object.assign({}, ...Object.values(cases).map(s => s.props), { kind: undefined, [key]: { type: 'string' } }) });
const own = props => Object.fromEntries(Object.entries(props).filter(([, v]) => v));
export function headSchema(change) {
  const named = { type: 'union', key: 'kind', cases: { ...Object.fromEntries(Object.entries(change.cases).map(([k, s]) => [k, { ...s, props: { ...s.props, name: { type: 'string' } } }])), off: OFF_NAMED } };
  const formPartial = { type: 'object', required: ['name'], props: { name: { type: 'string' }, strength: num(-3, 3) } };
  const feat = partial(FEATURE_SCHEMA.cases, 'id'), piece = partial(PIECE_SCHEMA.cases, 'id');
  return { type: 'object', props: {
    preset: pin, size: num(0.3, 3), skin: color,
    // the form it starts from (its base's, its preset's) weighed by this
    strength: num(0, 3),
    form: { type: 'array', items: { anyOf: [named, formPartial] } },
    features: { type: 'array', items: { anyOf: [{ type: 'union', key: 'kind', cases: { ...FEATURE_SCHEMA.cases, preset: REF, off: OFF } }, { ...feat, props: own(feat.props) }] } },
    expressions: { type: 'array', items: { anyOf: [REF, OFF_NAMED, EXPRESSION_SCHEMA] } },
    pieces: { type: 'array', items: { anyOf: [{ type: 'union', key: 'kind', cases: { ...PIECE_SCHEMA.cases, preset: REF, off: OFF } }, { ...piece, props: own(piece.props) }] } },
    light: { anyOf: [REF, LIGHT_SCHEMA] },
    // the picture it was drawn after, for the overlay check (tools/overlay.mjs): the image (docs/pictures/references/),
    // its landmarks in the picture's pixels, the angle it is seen at
    ref: { type: 'object', required: ['image'], props: { image: { type: 'string', pattern: /^[a-z0-9][a-z0-9._-]*\.(png|jpg|webp)$/ },
      points: { type: 'map', keys: ['eL', 'eR', 'tip', 'mouth', 'mL', 'mR', 'chin'], values: { type: 'array', min: 2, max: 2, items: num(-10000, 10000) } },
      view: { type: 'object', props: { yaw: num(-4, 4), pitch: num(-2, 2) } }, crop: { type: 'array', min: 4, max: 4, items: num(0, 100000) } } },
  } };
}

// A preset (presets/<id>.json): a named list of changes — deformers with their parameters and strengths, or other
// presets — that a character takes into its rest or its pose layers ({kind: "preset", id: "<id>@<hash>", strength,
// frames | space}); each of its changes' strength is multiplied by the reference's, the reference says how they go on
// the rest (frames) or as a layer (space). Plain data an author can read, copy and change.
//   {format: "engine/preset", version: 3, id, label: {ru, en}, group, about: {ru, en}, and one of
//    changes: [change…]          deformers (of a body, or of a head's form)
//    head: {…}                   a whole head, as a character's `head` (its form, features, expressions, pieces, light),
//                                that a character or another head takes by head.preset and changes
//    features: [feature…]        a head's features (src/head/features.js)
//    expressions: [expression…]  a head's expressions (src/head/expressions.js)
//    light: {…}                  a head's light (src/head/head.js)}
// (version 3: the head's parts; version 2: a silhouette's keys are {at, width, depth, forward}; version 1 had
// [at, width, depth, forward] — upgradePreset, run by tools/characters.mjs presets)
export const PRESET_FORMAT = 'engine/preset', PRESET_VERSION = 4;
export const PRESET_CONTENT = ['changes', 'head', 'features', 'expressions', 'pieces', 'light'];
export function presetSchemaOf() {
  const ref = { type: 'object', props: { kind: { const: 'preset' }, id: pin, strength: num(-3, 3) }, required: ['kind', 'id'] };
  const change = { type: 'union', key: 'kind', cases: { preset: ref,
    ...Object.fromEntries(Object.values(DEFORMERS).map(d => [d.kind, { type: 'object', props: { kind: { const: d.kind }, ...d.params, strength: num(-3, 3) }, required: ['kind'] }])) } };
  return {
    type: 'object', required: ['format', 'version', 'id', 'label', 'group'],
    props: {
      format: { const: PRESET_FORMAT }, version: { const: PRESET_VERSION }, id: { type: 'string', pattern: /^[a-z0-9][a-z0-9-]*$/ },
      label: { type: 'object', props: { ru: { type: 'string' }, en: { type: 'string' } }, required: ['ru', 'en'] },
      group: { type: 'string', pattern: /^[a-z][a-z-]*$/ },
      about: { type: 'object', props: { ru: { type: 'string' }, en: { type: 'string' } }, required: ['ru', 'en'] },
      changes: { type: 'array', min: 1, items: change },
      head: headSchema(change),
      features: { type: 'array', min: 1, items: FEATURE_SCHEMA },
      expressions: { type: 'array', min: 1, items: EXPRESSION_SCHEMA },
      pieces: { type: 'array', min: 1, items: PIECE_SCHEMA },
      light: LIGHT_SCHEMA,
    },
  };
}
export function checkPreset(p) {
  if (p?.format === PRESET_FORMAT && p.version < PRESET_VERSION) throw new Error(`${p.id}: a preset of version ${p.version} — upgrade it to ${PRESET_VERSION} (node engine/tools/characters.mjs presets)`);
  if (p?.format !== PRESET_FORMAT || p.version !== PRESET_VERSION) throw new Error(`${p?.id ?? '?'}: not a preset of version ${PRESET_VERSION}`);
  validate(p, presetSchemaOf(), 'preset ' + p.id);
  const has = PRESET_CONTENT.filter(k => k in p);
  if (has.length !== 1) throw new Error(`preset ${p.id}: one of ${PRESET_CONTENT.join(', ')}, not ${has.length ? has.join(' and ') : 'none'}`);
  return p;
}

// a preset of an earlier version as the current one
export function upgradePreset(p) {
  const d = structuredClone(p);
  if (d.format !== PRESET_FORMAT) throw new Error(`${d.id ?? '?'}: not a preset`);
  if (d.version === 1) { d.changes = d.changes.map(namedKeys); d.version = 2; }
  if (d.version === 2) d.version = 3;   // 2 → 3 added the head's parts: a preset of changes is as it was
  if (d.version === 3) d.version = 4;   // 3 → 4 added pieces as a preset's content, and a head's parts changed by their id or name: as it was
  if (d.version !== PRESET_VERSION) throw new Error(`${d.id}: no way from preset version ${d.version} to ${PRESET_VERSION}`);
  return d;
}
const namedKeys = c => c.kind === 'silhouette' && c.keys.some(Array.isArray) ? { ...c, keys: c.keys.map(([at, width, depth, forward]) => ({ at, width, depth, forward })) } : c;

// a description checked and completed by the defaults: what the engine builds a figure from. base: the resolved
// character it starts from (when it names one: engine.js reads it)
export function resolve(desc, skeleton, base = null) {
  if (desc?.format !== FORMAT) throw new Error(`${desc?.id ?? '?'}: not a character`);
  if (desc.version !== VERSION) {
    if (desc.version < VERSION) throw new Error(`${desc.id}: a character of version ${desc.version} — upgrade it to ${VERSION} (node engine/tools/characters.mjs upgrade ${desc.id})`);
    throw new Error(`${desc.id}: character version ${desc.version} is newer than this engine knows (${VERSION})`);
  }
  validate(desc, schemaOf(skeleton), desc.id);
  if (desc.base && !base) throw new Error(`${desc.id}: starts from ${desc.base} — resolved by the engine (E.character, E.resolve)`);
  if (!desc.base && base) throw new Error(`${desc.id}: names no base`);
  if (!desc.body && !base) throw new Error(`${desc.id}: "body" is missing (a character names its body, or a base it starts from)`);
  const b = base ?? { rest: [], pose: [], skinning: DEFAULTS.skinning, motion: DEFAULTS.motion, look: DEFAULTS.look };
  const sk = { ...b.skinning, ...(desc.skinning || {}) };
  if (sk.seam) sk.seam = { ...DEFAULTS.seam, ...sk.seam };
  const body = desc.body ?? base.body;
  return {
    id: desc.id, label: desc.label, version: desc.version, base: desc.base ?? null, body, bodyId: pinned(body).id,
    rest: [...b.rest, ...(desc.rest || []).map(c => ({ ...c }))],
    pose: [...b.pose, ...(desc.pose || []).map(l => ({ ...(DEFAULTS.layers[l.kind] || {}), ...l }))],
    skinning: sk,
    motion: { ...b.motion, ...(desc.motion || {}) },
    look: { ...b.look, ...(desc.look || {}) },
    // the head: this one's over its base's (engine.js expand merges them, with their presets)
    head: desc.head ? { ...desc.head, under: b.head ?? null } : b.head ?? null,
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
  if (d.version === 2) {
    // version 2 → 3: a silhouette's keys named ({at, width, depth, forward}); `space` only on the layers that are turns
    // (the line, contrapposto, presets) — a change of the form as a layer is its rest change, in no space
    d.rest = (d.rest || []).map(namedKeys);
    d.pose = (d.pose || []).map(l => { l = namedKeys(l); if (l.space && DEFORMERS[l.kind] && layerOf(l.kind) !== 'turns') { l = { ...l }; delete l.space; } return l; });
    d.version = 3;
  }
  if (d.version === 3) d.version = 4;   // 3 → 4 added the head: a character without one is as it was
  if (d.version === 4) d.version = 5;   // 4 → 5: a head's parts changed by their id or name, its form's strength: as it was
  if (d.version !== VERSION) throw new Error(`${d.id}: no way from version ${d.version} to ${VERSION}`);
  return d;
}
