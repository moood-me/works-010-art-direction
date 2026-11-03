// Characters' and chains' pins and versions, written back into their files.
//   node engine/tools/characters.mjs upgrade [ids…]   characters of an earlier format version → the current one
//                                                      (the body pinned as it is now; look at them after)
//   node engine/tools/characters.mjs pin [ids…]       pin each character's body anew, as it is now — after its data
//                                                      changed and the checks were looked at
//   node engine/tools/characters.mjs chains           pin the motions of motions/index.json's chains as they are now
// No ids: every character of characters/index.json.
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { createEngine } from '../src/engine.js';
import { upgrade, resolve, VERSION } from '../src/character.js';
import { pinned, pinOf } from '../src/hash.js';
import { read } from '../check/node-read.mjs';

const ROOT = new URL('../', import.meta.url), E = await createEngine({ root: ROOT, read });
const [what, ...ids] = process.argv.slice(2);
const file = id => fileURLToPath(new URL(`characters/${id}.json`, ROOT));
const all = async () => ids.length ? ids : (await E.characters()).characters.map(c => c.id);
const save = (path, d) => writeFile(path, JSON.stringify(d, null, 1) + '\n');

if (what === 'upgrade' || what === 'pin') {
  for (const id of await all()) {
    let d = JSON.parse(await readFile(file(id), 'utf8'));
    const bodyId = d.version === 1 ? d.body : pinned(d.body).id, body = await E.body(bodyId), pin = pinOf(bodyId, body.hash);
    if (what === 'upgrade') { if (d.version === VERSION) { console.log(`${id}: already version ${VERSION}`); continue; } d = upgrade(d, { bodyPin: pin }); }
    else d.body = pin;
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
} else {
  console.log('node engine/tools/characters.mjs upgrade|pin [ids…] | chains');
  process.exit(1);
}
