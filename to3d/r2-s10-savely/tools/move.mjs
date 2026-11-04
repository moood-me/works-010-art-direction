// Савелий Петрович moved by a Kimodo motion through the engine (engine/src): the engine's own retargeting and
// skinning, on his body pack (pack_engine.py). The engine is used as it is; only its file reading is pointed at our
// body: data/bodies/savely.* and data/topology/savely.* are read from CACHE/engine/data.
// usage: node move.mjs CACHE MOTION[,MOTION…] OUT.bin [step] [frames a:b]
//   OUT.bin: float32, frames × N × 3 (metres, the engine's axes); OUT.json: {frames, N, times, hips: [[x, y, z]…]}
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const ENGINE = path.resolve(here, '../../../engine/');
const [cache, motions, out, stepArg, rangeArg] = process.argv.slice(2);
const step = Number(stepArg || 1);
const ours = path.resolve(cache, 'engine/data');

const read = async url => {
  let p = fileURLToPath(url);
  const rel = path.relative(path.join(ENGINE, 'data'), p);
  if (rel.startsWith('bodies/savely') || rel.startsWith('topology/savely')) p = path.join(ours, rel);
  const b = await readFile(p);
  return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
};

const { createEngine } = await import(pathToFileURL(path.join(ENGINE, 'src/engine.js')).href);
const { resolve } = await import(pathToFileURL(path.join(ENGINE, 'src/character.js')).href);
const E = await createEngine({ root: pathToFileURL(ENGINE + '/'), read });
const spec = resolve({ format: 'engine/character', version: 1, id: 'savely', label: { ru: 'Савелий Петрович' },
  body: 'savely', skinning: { method: 'cor', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} } });
const fig = await E.figure(spec, { position: [0, 0, 0], heading: 0 });
const clip = await E.clip(motions.split(','));
let [a, b] = rangeArg ? rangeArg.split(':').map(Number) : [0, clip.frames - 1];
const N = fig.body.N, times = [], hips = [], head = [];
const H = fig.body.skeleton.index.Hips, HD = fig.body.skeleton.index.Head;
const chunks = [];
for (let t = a; t <= b; t += step) {
  fig.frame(clip, t);
  chunks.push(Buffer.from(new Float32Array(fig.positions).buffer));
  times.push(t);
  hips.push([fig.pose.P[H * 3], fig.pose.P[H * 3 + 1], fig.pose.P[H * 3 + 2]]);
}
await writeFile(out, Buffer.concat(chunks));
await writeFile(out.replace(/\.bin$/, '.json'), JSON.stringify({ frames: times.length, N, times, hips, fps: clip.fps ?? 30 }));
console.log('frames', times.length, 'N', N);
