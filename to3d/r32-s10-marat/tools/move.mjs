// Марат moved by a Kimodo motion through the engine (engine/src): the engine's own retargeting and
// skinning, on his body pack (pack_engine.py). The engine is used as it is; only its file reading is pointed at our
// body: data/bodies/marat.* and data/topology/marat.* are read from CACHE/engine/data.
// usage: node move.mjs CACHE MOTION[,MOTION…] OUT.bin [step] [frames a:b]
//   OUT.bin: float32, frames × N × 3 (metres, the engine's axes); OUT.json: {frames, N, times, hips: [[x, y, z]…]}
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const ENGINE = path.resolve(here, '../../../engine/');
const ID = 'marat', RU = 'Марат';
const [cache, motions, out, stepArg, rangeArg] = process.argv.slice(2);
const step = Number(stepArg || 1);
const ours = path.resolve(cache, 'engine/data');

const read = async url => {
  let p = fileURLToPath(url);
  const rel = path.relative(path.join(ENGINE, 'data'), p);
  if (rel.startsWith('bodies/' + ID + '.') || rel.startsWith('topology/' + ID + '.')) p = path.join(ours, rel);
  const b = await readFile(p);
  return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
};

const { createEngine } = await import(pathToFileURL(path.join(ENGINE, 'src/engine.js')).href);
const { resolve } = await import(pathToFileURL(path.join(ENGINE, 'src/character.js')).href);
const E = await createEngine({ root: pathToFileURL(ENGINE + '/'), read });
const spec = resolve({ format: 'engine/character', version: 1, id: ID, label: { ru: RU },
  body: ID, skinning: { method: 'cor', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} } });
const fig = await E.figure(spec, { position: [0, 0, 0], heading: 0 });
const clip = await E.clip(motions.split(','));
let [a, b] = rangeArg ? rangeArg.split(':').map(Number) : [0, clip.frames - 1];
// the live face (web/face.mjs, web/life.mjs): LIFE='{"talk": true, "expr": [[0, {"calm": 1}], [2, {"joy": 1}]], "seed": 3}'
const { Face } = await import('./web/face.mjs');
const { lifeTrack, headFacing } = await import('./web/life.mjs');
const { qRot } = await import(pathToFileURL(path.join(ENGINE, 'src/math.js')).href);
const LIFE = process.env.LIFE ? JSON.parse(process.env.LIFE) : null;
const fps = clip.fps ?? 30;
let face = null, life = null;
if (LIFE) {
  face = new Face(fig.body, JSON.parse(await readFile(path.resolve(cache, 'engine/face.json'), 'utf8')));
  const HI = fig.body.skeleton.index.Head, smp = (await import(pathToFileURL(path.join(ENGINE, 'src/motion.js')).href)).newSample(fig.body.skeleton.J);
  const head = s => headFacing(fig.retarget.pose(clip.sample(Math.min(clip.frames - 1, s * fps), smp)), HI, qRot);
  life = lifeTrack(head, { seconds: clip.frames / fps, ...LIFE });
}
const N = fig.body.N, times = [], hips = [], head = [], params = [];
const H = fig.body.skeleton.index.Hips, HD = fig.body.skeleton.index.Head;
const chunks = [];
for (let t = a; t <= b; t += step) {
  fig.frame(clip, t);
  if (face) {
    const q = life.at(t / fps); params.push(q);
    face.update(q);
    face.apply(fig.positions, fig.skinner.matrix(fig.pose, fig.body.skeleton.index.Head));
  }
  chunks.push(Buffer.from(new Float32Array(fig.positions).buffer));
  times.push(t);
  hips.push([fig.pose.P[H * 3], fig.pose.P[H * 3 + 1], fig.pose.P[H * 3 + 2]]);
  head.push([fig.pose.P[HD * 3], fig.pose.P[HD * 3 + 1], fig.pose.P[HD * 3 + 2]]);
}
await writeFile(out, Buffer.concat(chunks));
await writeFile(out.replace(/\.bin$/, '.json'), JSON.stringify({ frames: times.length, N, times, hips, head, fps, params, blinks: life?.blinks }));
console.log('frames', times.length, 'N', N);
