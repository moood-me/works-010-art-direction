// Characters' and chains' pins and versions, written back into their files.
//   node engine/tools/characters.mjs upgrade [ids…]   characters of an earlier format version → the current one
//                                                      (the body pinned as it is now; look at them after)
//   node engine/tools/characters.mjs pin [ids…]       pin each character's body anew, as it is now — after its data
//                                                      changed and the checks were looked at
//   node engine/tools/characters.mjs chains           pin the motions of motions/index.json's chains as they are now
//   node engine/tools/characters.mjs presets          check every preset (presets/*.json), pin the presets they take,
//                                                      write presets/index.json (by group, each pinned)
//   node engine/tools/characters.mjs bodies           write data/bodies/index.json (every body, its group, pinned)
// `pin` also pins the presets a character takes as they are now.
// No ids: every character of characters/index.json.
import { readFile, writeFile, readdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { createEngine } from '../src/engine.js';
import { upgrade, resolve, VERSION, checkPreset } from '../src/character.js';
import { pinned, pinOf } from '../src/hash.js';
import { read } from '../check/node-read.mjs';

const ROOT = new URL('../', import.meta.url), E = await createEngine({ root: ROOT, read });
const [what, ...ids] = process.argv.slice(2);
const file = id => fileURLToPath(new URL(`characters/${id}.json`, ROOT));
const all = async () => ids.length ? ids : (await E.characters()).characters.map(c => c.id);
const save = (path, d) => writeFile(path, JSON.stringify(d, null, 1) + '\n');
// the presets a list of changes takes, pinned as they are now
const repin = list => Promise.all(list.map(async c => c.kind === 'preset' ? { ...c, id: pinOf(pinned(c.id).id, (await E.preset(pinned(c.id).id)).hash) } : c));

if (what === 'upgrade' || what === 'pin') {
  for (const id of await all()) {
    let d = JSON.parse(await readFile(file(id), 'utf8'));
    const bodyId = d.version === 1 ? d.body : pinned(d.body).id, body = await E.body(bodyId), pin = pinOf(bodyId, body.hash);
    if (what === 'upgrade') { if (d.version === VERSION) { console.log(`${id}: already version ${VERSION}`); continue; } d = upgrade(d, { bodyPin: pin }); }
    else { d.body = pin; for (const k of ['rest', 'pose']) d[k] = await repin(d[k] || []); }
    resolve(d, E.skeleton);
    await save(file(id), d);
    console.log(`${id}: ${what === 'upgrade' ? `version ${d.version}, ` : ''}body ${pin}`);
  }
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
  for (const f of files) { const p = JSON.parse(await readFile(dir + f, 'utf8')); p.changes = await repin(p.changes); checkPreset(p); await save(dir + f, p); }
  for (const f of files) { const id = f.slice(0, -5), p = await E.preset(id); list.push({ id, pin: pinOf(id, p.hash), group: p.group, label: p.label, about: p.about }); }
  const ORDER = ['silhouette', 'line', 'squash', 'contrapposto', 'limbs', 'proportions', 'caricature', 'surface', 'contour', 'masses', 'pictogram'];
  const rank = g => ORDER.includes(g) ? ORDER.indexOf(g) : ORDER.length;
  list.sort((a, b) => rank(a.group) - rank(b.group) || a.id.localeCompare(b.id));
  await save(dir + 'index.json', { format: 'engine/presets', version: 1, about: 'Presets of parts (each presets/<id>.json): changes a character takes into its rest or pose by {kind: "preset", id: "<pin>", strength, frames | space}. Written by engine/tools/characters.mjs presets.', groups: ORDER, presets: list });
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
  console.log('node engine/tools/characters.mjs upgrade|pin [ids…] | chains | presets | bodies');
  process.exit(1);
}
