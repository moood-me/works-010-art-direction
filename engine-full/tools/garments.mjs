// MakeHuman's garments (CC0) as the engine's source meshes: each read from the bytes moood bakes (experiments/data, the
// same as О2's and О3's pages take) and written as a pack, data/garments/mh-<name>.json + .bin (`engine/garment` 1) —
// every point on three vertices of Anny's mesh as moood has it (topology anny-moood) with its place among them
// (barycentric) and an offset scaled by the body's own measures, and the triangles. src/cloth/patterns.js lays them on
// any body of that mesh. data/garments/index.json lists them.
//   node engine-full/tools/garments.mjs
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { packOf } from '../src/pack.js';

const ROOT = new URL('../../', import.meta.url), OUT = new URL('../data/garments/', import.meta.url);
// what each is (MakeHuman's kind as moood keeps it: experiments/data/meta.json), its names
const GARMENTS = {
  dress: ['top', 'платье', 'dress'], tshirt: ['top', 'футболка', 'T-shirt'], sweater: ['top', 'свитер', 'sweater'], polo: ['top', 'поло', 'polo shirt'],
  oversized: ['top', 'оверсайз', 'oversized top'], tunic: ['top', 'туника', 'tunic'], robe: ['top', 'халат', 'robe'], hood: ['top', 'худи с капюшоном', 'hooded top'],
  pants: ['bottom', 'брюки', 'trousers'], shorts: ['bottom', 'шорты', 'shorts'], skirt: ['bottom', 'юбка', 'skirt'], vikingpants: ['bottom', 'широкие штаны', 'wide trousers'],
  apron: ['apron', 'фартук', 'apron'], boots: ['shoes', 'ботинки', 'boots'], flats: ['shoes', 'туфли', 'flats'],
};
// moood's bytes: [V, T, …] then each point's three vertices, its place among them, its offset (1/10000 m), the six
// vertices and three spans its offset is measured by, joints, weights, and what О2 read off it, then the triangles
function parse(buf) {
  let at = 0; const take = (Kind, n) => { const a = new Kind(buf.slice(at, at + n * Kind.BYTES_PER_ELEMENT)); at += n * Kind.BYTES_PER_ELEMENT; return a; };
  const [V, T] = take(Uint32Array, 4);
  const refs = take(Uint16Array, V * 3), bary = take(Float32Array, V * 3), offset = take(Int16Array, V * 3), measure = take(Uint16Array, 6), span = take(Float32Array, 3);
  take(Uint8Array, V * 4); take(Uint8Array, V * 4); take(Uint8Array, V); take(Uint16Array, V); take(Uint16Array, V); take(Uint16Array, V);
  return { V, refs, bary, offset, measure, span, triangles: take(Uint16Array, T * 3) };
}
const keys = [];
for (const [name, [kind, ru, en]] of Object.entries(GARMENTS)) {
  const text = await readFile(fileURLToPath(new URL(`experiments/data/${name}.js`, ROOT)), 'utf8'), b = Buffer.from(text.match(/"([A-Za-z0-9+/=]+)"/)[1], 'base64');
  const g = parse(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength)), id = `mh-${name}`;
  const header = { format: 'engine/garment', version: 1, id, kind, label: { ru, en }, topology: 'anny-moood', unit: 1e-4,
    source: `MakeHuman (CC0), as moood bakes it onto Anny's mesh (experiments/data/${name}.js)` };
  const { json, bin } = packOf(header, { refs: { array: g.refs, shape: [g.V, 3] }, bary: { array: g.bary, shape: [g.V, 3] }, offset: { array: g.offset, shape: [g.V, 3] },
    measure: { array: g.measure, shape: [3, 2] }, span: { array: g.span }, triangles: { array: g.triangles, shape: [g.triangles.length / 3, 3] } }, `${id}.bin`);
  await writeFile(new URL(`${id}.json`, OUT), json); await writeFile(new URL(`${id}.bin`, OUT), bin);
  keys.push({ id, kind, label: { ru, en }, points: g.V, triangles: g.triangles.length / 3 });
}
await writeFile(new URL('index.json', OUT), JSON.stringify({ format: 'engine/garments', version: 1, about: "MakeHuman's garments as source meshes on Anny's mesh (tools/garments.mjs)", garments: keys }, null, 1) + '\n');
console.log(keys.map(k => `${k.id} ${k.points}`).join('\n'));
