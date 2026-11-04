// A still pose for the comparison pictures: the rest with the arms let down along the body (the rest is Anny's A pose),
// skinned by the engine's own Skinner. Not a motion — only the stand the drawing shows; moving is Kimodo's (move.mjs).
// usage: node stand.mjs CACHE OUT.bin   (writes OUT.bin/json in move.mjs's format, one frame)
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const ENGINE = path.resolve(here, '../../../engine/');
const [cache, out] = process.argv.slice(2);
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
const { qAxisAngle, qMul, qRot } = await import(pathToFileURL(path.join(ENGINE, 'src/math.js')).href);
const E = await createEngine({ root: pathToFileURL(ENGINE + '/'), read });
const spec = resolve({ format: 'engine/character', version: 1, id: 'savely', body: 'savely' });
const fig = await E.figure(spec, { position: [0, 0, 0], heading: 0 });
const body = fig.body, sk = body.skeleton, J = sk.J;
const pose = { Q: new Float64Array(J * 4), P: Float64Array.from(body.joints) };
for (let j = 0; j < J; j++) pose.Q[j * 4 + 3] = 1;
const parent = sk.parent;
const under = (root) => { const s = new Set([root]); for (let j = 0; j < J; j++) if (s.has(parent[j])) s.add(j); return s; };
// turn a joint and everything under it by q about the joint's place now
function turn(name, axis, deg) {
  const r = sk.index[name], q = qAxisAngle(axis, deg * Math.PI / 180), c = [0, 1, 2].map(k => pose.P[r * 3 + k]);
  for (const j of under(r)) {
    const qq = qMul(q, [...pose.Q.slice(j * 4, j * 4 + 4)]);
    pose.Q.set(qq, j * 4);
    const v = qRot(q, [0, 1, 2].map(k => pose.P[j * 3 + k] - c[k]));
    for (let k = 0; k < 3; k++) pose.P[j * 3 + k] = c[k] + v[k];
  }
}
const A = JSON.parse(process.env.STAND || '{"arm": 38, "fore": 12, "back": 6}');
turn('LeftArm', [0, 0, 1], -A.arm); turn('RightArm', [0, 0, 1], A.arm);          // arms down to the sides
turn('LeftArm', [1, 0, 0], A.back); turn('RightArm', [1, 0, 0], A.back);         // a little back
turn('LeftForeArm', [1, 0, 0], -A.fore); turn('RightForeArm', [1, 0, 0], -A.fore); // elbows a little bent
const P = new Float32Array(body.N * 3);
fig.skinner.skin(pose, P);
await writeFile(out, Buffer.from(P.buffer));
const H = sk.index.Hips;
await writeFile(out.replace(/\.bin$/, '.json'), JSON.stringify({ frames: 1, N: body.N, times: [0], hips: [[0, pose.P[H * 3 + 1], 0]] }));
console.log('stand', body.N);
