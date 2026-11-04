// Characters' and chains' pins and versions, written back into their files.
//   node engine/tools/characters.mjs upgrade [ids…]   characters of an earlier format version → the current one
//                                                      (the body pinned as it is now; look at them after)
//   node engine/tools/characters.mjs pin [ids…]       pin each character's body anew, as it is now — after its data
//                                                      changed and the checks were looked at
//   node engine/tools/characters.mjs chains           pin the motions of motions/index.json's chains as they are now
//   node engine/tools/characters.mjs presets          upgrade every preset (presets/*.json) of an earlier version,
//                                                      check it, pin the presets it takes, write presets/index.json
//                                                      (by group, each pinned)
//   node engine/tools/characters.mjs bodies           write data/bodies/index.json (every body, its group, pinned)
//   node engine/tools/characters.mjs cases            pin anew the presets and bodies check/cases.json takes
//   node engine/tools/characters.mjs wraps            store every wrapped head the characters and the cases make
//                                                      (data/wraps/: by the key of what each is made from), drop the
//                                                      ones nothing makes now
//   node engine/tools/characters.mjs hair             store every hairstyle the presets, characters and cases take
//                                                      (data/hair/: built in its design space, by the key of what it is
//                                                      built from), drop the ones nothing takes now
// `pin` also pins the presets a character takes, and the character it starts from (`base`), as they are now.
// No ids: every character of characters/index.json.
import { readFile, writeFile, readdir, rm } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { createEngine } from '../src/engine.js';
import { upgrade, VERSION, checkPreset, upgradePreset, PRESET_VERSION } from '../src/character.js';
import { hashOf, pinned, pinOf } from '../src/hash.js';
import { read } from '../check/node-read.mjs';
import { jobsOf } from '../check/cases.mjs';
import { complete } from '../src/deform.js';
import { wrapKey, wrapHead } from '../src/head/wrap.js';
import { packOf } from '../src/pack.js';
import { buildStyle, styleKey, BUILD_SOURCES } from '../src/hair/hair.js';

const ROOT = new URL('../', import.meta.url), E = await createEngine({ root: ROOT, read });
const [what, ...ids] = process.argv.slice(2);
const file = id => fileURLToPath(new URL(`characters/${id}.json`, ROOT));
const all = async () => ids.length ? ids : (await E.characters()).characters.map(c => c.id);
const save = (path, d) => writeFile(path, JSON.stringify(d, null, 1) + '\n');
// the presets a list of changes takes, pinned as they are now
// (and the bodies a change takes: a head of another age)
const repin = list => Promise.all(list.map(async c => c.kind === 'preset' ? { ...c, id: pinOf(pinned(c.id).id, (await E.preset(pinned(c.id).id)).hash) }
  : typeof c.body === 'string' ? { ...c, body: pinOf(pinned(c.body).id, (await E.body(pinned(c.body).id)).hash) } : c));
const pinRef = async ref => pinOf(pinned(ref).id, (await E.preset(pinned(ref).id)).hash);
// a head's presets (the head it starts from, its form's, its features', expressions' and light's), pinned as they are now
async function repinHead(h) {
  if (!h) return h;
  const o = { ...h };
  if (o.preset) o.preset = await pinRef(o.preset);
  for (const k of ['form', 'features', 'expressions', 'pieces']) if (o[k]) o[k] = await repin(o[k]);
  if (o.light?.kind === 'preset') o.light = { ...o.light, id: await pinRef(o.light.id) };
  return o;
}

// clothes (a character's, an outfit's): its outfits, each garment's fabric and shape, pinned as they are now
const repinClothes = list => Promise.all(list.map(async g => g.kind === 'preset' ? { ...g, id: await pinRef(g.id) }
  : { ...g, ...(typeof g.fabric === 'string' ? { fabric: await pinRef(g.fabric) } : {}), ...(typeof g.shape === 'string' ? { shape: await pinRef(g.shape) } : {}) }));

if (what === 'upgrade' || what === 'pin') {
  for (const id of await all()) {
    let d = JSON.parse(await readFile(file(id), 'utf8'));
    const bodyId = !d.body ? null : d.version === 1 ? d.body : pinned(d.body).id, pin = bodyId && pinOf(bodyId, (await E.body(bodyId)).hash);
    if (what === 'upgrade') { if (d.version === VERSION) { console.log(`${id}: already version ${VERSION}`); continue; } d = upgrade(d, { bodyPin: pin }); }
    else {
      if (pin) d.body = pin;
      if (d.base) { const b = pinned(d.base).id; d.base = pinOf(b, hashOf([JSON.parse(await readFile(file(b), 'utf8'))])); }
      for (const k of ['rest', 'pose']) d[k] = await repin(d[k] || []);
      if (d.head) d.head = await repinHead(d.head);
      if (d.clothes) d.clothes = await repinClothes(d.clothes);
    }
    await E.resolve(d);
    await save(file(id), d);
    console.log(`${id}: ${what === 'upgrade' ? `version ${d.version}, ` : ''}${pin ? 'body ' + pin : 'base ' + d.base}`);
  }
} else if (what === 'cases') {
  // the checks' cases (check/cases.json) take presets and bodies in their `over`: pinned as they are now
  const path = fileURLToPath(new URL('check/cases.json', ROOT)), text = await readFile(path, 'utf8'), index = await E.presets(), bodies = await E.bodies();
  const pins = Object.fromEntries([...index.presets, ...bodies.bodies].map(p => [p.id, p.pin]));
  let n = 0; const out = text.replace(/"([A-Za-z0-9][A-Za-z0-9_.-]*)@([0-9a-f]{12,64})"/g, (m, id) => pins[id] && `"${pins[id]}"` !== m ? (n++, `"${pins[id]}"`) : m);
  await writeFile(path, out); console.log(`${n} pins in check/cases.json made anew`);
} else if (what === 'wraps') {
  const dir = fileURLToPath(new URL('data/wraps/', ROOT)), index = JSON.parse(await readFile(dir + 'index.json', 'utf8'));
  const cases = JSON.parse(await readFile(fileURLToPath(new URL('check/cases.json', ROOT)), 'utf8'));
  const descs = [...await Promise.all((await E.characters()).characters.map(c => E.description(c.id))),
    ...await Promise.all(jobsOf(cases, (await E.characters()).characters, null).filter(j => j.over).map(async j => ({ ...structuredClone(await E.description(j.char)), ...j.over })))];
  const keys = new Set();
  for (const d of descs) {
    const spec = await E.expand(await E.resolve(d));
    for (const [k, c] of spec.rest.entries()) {
      if (c.kind !== 'wrap') continue;
      const body = await E.restBody({ ...spec, rest: spec.rest.slice(0, k) }), p = complete(c), key = wrapKey(p, body);
      if (keys.has(key)) continue; keys.add(key);
      if (index.keys.includes(key)) continue;
      const t = Date.now(), { json, bin } = packOf({ format: 'engine/wrap', version: 1, key, about: `${d.id}: its head wrapped (src/head/wrap.js), by wrapKey` }, { positions: { array: wrapHead(body, p.form, p.marks, p.neckSlim, p.onto), shape: [body.mesh.N, 3] } }, key + '.bin');
      await writeFile(dir + key + '.json', json); await writeFile(dir + key + '.bin', bin);
      console.log(`${d.id}: wrapped and stored as ${key} (${((Date.now() - t) / 1000).toFixed(1)} s)`);
    }
  }
  for (const key of index.keys) if (!keys.has(key)) { await rm(dir + key + '.json'); await rm(dir + key + '.bin'); console.log(`${key}: nothing makes it now — dropped`); }
  await save(dir + 'index.json', { ...index, keys: [...keys].sort() });
  console.log(`${keys.size} wraps stored`);
} else if (what === 'hair') {
  const dir = fileURLToPath(new URL('data/hair/', ROOT)), index = JSON.parse(await readFile(dir + 'index.json', 'utf8'));
  const cases = JSON.parse(await readFile(fileURLToPath(new URL('check/cases.json', ROOT)), 'utf8')), chars = (await E.characters()).characters;
  const descs = [...await Promise.all(chars.map(c => E.description(c.id))), ...await Promise.all(jobsOf(cases, chars, null).filter(j => j.over).map(async j => ({ ...structuredClone(await E.description(j.char)), ...j.over })))];
  // every hair piece: the presets' own, and each head's (its pieces over its presets')
  const pieces = (await E.presets()).presets.filter(p => p.group === 'hair').map(p => p.id);
  const list = [...(await Promise.all(pieces.map(async id => (await E.preset(id)).pieces))).flat()];
  for (const d of descs) { const spec = await E.expand(await E.resolve(d)); if (spec.head) list.push(...spec.head.pieces); }
  // (the code that builds them changed since they were stored: each stored one built again — one that comes out
  // otherwise means what it builds changed, and its version must go up)
  const source = hashOf(await Promise.all(BUILD_SOURCES.map(f => readFile(fileURLToPath(new URL(f, ROOT)), 'utf8')))).slice(0, 16), again = index.source !== source;
  const same = (a, b) => a.length === b.length && a.every((v, i) => v === b[i]);
  const keys = new Set();
  for (const p of list.filter(p => p.kind === 'style')) {
    const key = styleKey(p); if (keys.has(key)) continue; keys.add(key);
    if (index.keys.includes(key) && again) {
      const stored = await E.stored('hair', key), made = buildStyle(p).arrays;
      for (const [k, v] of Object.entries(made)) if (!stored.arrays[k] || !same(stored.arrays[k], v.array)) throw new Error(`${p.style}: built now it is not what is stored (${k}) — what hair builds changed: raise HEAD_BUILD.hair (src/head/version.js)`);
      console.log(`${p.style}: built again, as stored`);
    }
    if (index.keys.includes(key)) continue;
    const t = Date.now(), { header, arrays } = buildStyle(p), { json, bin } = packOf({ ...header, about: `${p.style}: built in its design space (src/hair/hair.js), by styleKey` }, arrays, key + '.bin');
    await writeFile(dir + key + '.json', json); await writeFile(dir + key + '.bin', bin);
    console.log(`${p.style}${p.off?.length ? ' without ' + p.off.join(', ') : ''}${p.only ? ' only ' + p.only.join(', ') : ''}: built and stored as ${key} (${((Date.now() - t) / 1000).toFixed(1)} s)`);
  }
  for (const key of index.keys) if (!keys.has(key)) { await rm(dir + key + '.json'); await rm(dir + key + '.bin'); console.log(`${key}: nothing takes it now — dropped`); }
  await save(dir + 'index.json', { ...index, source, keys: [...keys].sort() });
  console.log(`${keys.size} hairstyles stored`);
} else if (what === 'chains') {
  const path = fileURLToPath(new URL('motions/index.json', ROOT)), index = JSON.parse(await readFile(path, 'utf8'));
  for (const c of index.chains) {
    c.motions = await Promise.all(c.motions.map(async r => { const id = pinned(r).id; return pinOf(id, (await E.motion(id)).hash); }));
    await E.clip({ motions: c.motions, joins: c.joins });   // refused here if they don't join
    console.log(`${c.id}: ${c.motions.join(' → ')}`);
  }
  await writeFile(path, JSON.stringify(index, null, 1) + '\n');
} else if (what === 'presets') {
  const dir = fileURLToPath(new URL('presets/', ROOT)), files = (await readdir(dir)).filter(f => f.endsWith('.json') && f !== 'index.json');
  // presets that take presets: those first pinned anew (in the order they depend)
  const list = [];
  for (const f of files) { const p = JSON.parse(await readFile(dir + f, 'utf8')); if (p.version < PRESET_VERSION) await save(dir + f, upgradePreset(p)); }
  // in the order they take each other: a preset is pinned anew after the presets it takes
  const content = {}; for (const f of files) content[f.slice(0, -5)] = JSON.parse(await readFile(dir + f, 'utf8'));
  const takes = p => JSON.stringify(p).match(/"(?:id|preset|fabric|shape)":\s*"([a-z0-9][a-z0-9-]*)@[0-9a-f]+"/g)?.map(m => m.match(/"([a-z0-9][a-z0-9-]*)@/)[1]).filter(x => x !== p.id) ?? [];
  const done = new Set(), order = [], visit = (id, path = []) => { if (done.has(id)) return; if (path.includes(id)) throw new Error(`presets take each other: ${[...path, id].join(' → ')}`); for (const t of takes(content[id])) if (content[t]) visit(t, [...path, id]); done.add(id); order.push(id); };
  for (const id of Object.keys(content)) visit(id);
  for (const id of order) {
    const p = content[id];
    if (p.changes) p.changes = await repin(p.changes);
    if (p.head) p.head = await repinHead(p.head);
    if (p.clothes) p.clothes = await repinClothes(p.clothes);
    checkPreset(p); await save(dir + id + '.json', p);
  }
  for (const f of files) { const id = f.slice(0, -5), p = await E.preset(id); list.push({ id, pin: pinOf(id, p.hash), group: p.group, label: p.label, about: p.about }); }
  const ORDER = ['silhouette', 'line', 'squash', 'contrapposto', 'limbs', 'proportions', 'caricature', 'surface', 'contour', 'masses', 'pictogram', 'head', 'head-form', 'features', 'hair', 'headwear', 'expressions', 'face-light', 'wind', 'fabric', 'garment-shape', 'outfit'];
  const rank = g => ORDER.includes(g) ? ORDER.indexOf(g) : ORDER.length;
  list.sort((a, b) => rank(a.group) - rank(b.group) || a.id.localeCompare(b.id));
  await save(dir + 'index.json', { format: 'engine/presets', version: 1, about: 'Presets of parts (each presets/<id>.json): changes a character takes into its rest or pose by {kind: "preset", id: "<pin>", strength, frames | space}; heads a character or another head takes by head.preset; a head\'s features, expressions and light; winds; fabrics, garments\' shapes and outfits a character\'s clothes take. Written by engine/tools/characters.mjs presets.', groups: ORDER, presets: list });
  console.log(`${list.length} presets`);
} else if (what === 'bodies') {
  const dir = fileURLToPath(new URL('data/bodies/', ROOT)), ids = (await readdir(dir)).filter(f => f.endsWith('.json') && f !== 'index.json').map(f => f.slice(0, -5));
  const specs = JSON.parse(await readFile(fileURLToPath(new URL('data/anny/specs.json', ROOT)), 'utf8')).bodies;
  const groupOf = id => id.startsWith('moood-') ? 'moood' : specs.find(s => s.id === id)?.group ?? (id.startsWith('anny-T-') ? 't8-head' : 't8');
  const ORDER = ['moood', 't8', 't8-head', 'age', 'build', 'origin'];
  const list = [];
  for (const id of ids) { const b = await E.body(id); list.push({ id, pin: pinOf(id, b.hash), group: groupOf(id), label: b.label, height: +b.measures.height.toFixed(3) }); }
  list.sort((a, b) => ORDER.indexOf(a.group) - ORDER.indexOf(b.group) || ids.indexOf(a.id) - ids.indexOf(b.id));
  const GROUPS = { moood: { ru: 'тела moood', en: "moood's bodies" }, t8: { ru: 'Т8: Anny своими настройками', en: "Т8: Anny's own settings" }, 't8-head': { ru: 'Т8: голова другого возраста', en: 'Т8: a head of another age' },
    age: { ru: 'Anny: возраст', en: 'Anny: age' }, build: { ru: 'Anny: сложение', en: 'Anny: build' }, origin: { ru: 'Anny: происхождение', en: 'Anny: origin' } };
  await save(fileURLToPath(new URL('data/bodies/index.json', ROOT)), { format: 'engine/bodies', version: 1, about: 'Every body (data/bodies/<id>.json), by group, pinned. Written by engine/tools/characters.mjs bodies.', groups: ORDER.map(g => ({ id: g, label: GROUPS[g] })), bodies: list });
  console.log(`${list.length} bodies`);
} else {
  console.log('node engine/tools/characters.mjs upgrade|pin [ids…] | chains | presets | bodies | cases | wraps | hair');
  process.exit(1);
}
