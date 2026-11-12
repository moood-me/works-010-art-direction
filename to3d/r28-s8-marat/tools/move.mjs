// Марат moved by Kimodo's motions through the engine (engine/src as it is: createEngine → figure → clip; retargeting,
// skinning by centres of rotation, the floor), with the live face (web/face.mjs, web/life.mjs) laid on after
// skinning. The engine's file reading is pointed at our body: data/{bodies,topology}/marat8.* come from CACHE.
// usage: node move.mjs JOB.json      JOB: {out: path.bin, motion: id | [ids] | null (rest), frames: [t…]
//        or range: [a, b, step], life: {expr, talk, seed, still}, face: {e, v, sp, blink, gaze} (a fixed face), head: {yaw, pitch}
//        (a turn of the head on top, for stills), place: {position, heading}}
// out: float32 frames × N × 3 (metres, the engine's axes); out.json: {frames, N, times, hips, head, fps}
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const ENGINE = path.resolve(here, '../../../engine/');
const CACHE = '/home/user/cache/to3d-r28-s8-marat';
const job = JSON.parse(await readFile(process.argv[2], 'utf8'));
const read = async url => {
  let p = fileURLToPath(url);
  const rel = path.relative(path.join(ENGINE, 'data'), p);
  if (rel.startsWith('bodies/marat8') || rel.startsWith('topology/marat8')) p = path.join(CACHE, 'engine/data', rel);
  const b = await readFile(p);
  return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
};
const E_ = p => import(pathToFileURL(path.join(ENGINE, 'src', p)).href);
const { createEngine } = await E_('engine.js');
const { resolve } = await E_('character.js');
const { qRot, qMul } = await E_('math.js');
const { newSample } = await E_('motion.js');
const { turnUnder, build } = await E_('retarget.js');
const { loadPack } = await E_('pack.js');
const { Face } = await import('./web/face.mjs');
const { lifeTrack, headFacing } = await import('./web/life.mjs');

const E = await createEngine({ root: pathToFileURL(ENGINE + '/'), read });
const spec = resolve({ format: 'engine/character', version: 1, id: 'marat8', label: { ru: 'Марат' }, body: 'marat8',
  skinning: { method: 'cor', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: { armsOutOfHead: { margin: 0.03 } } } });
const fig = await E.figure(spec, job.place || { position: [0, 0, 0], heading: 0 });
const sk = fig.body.skeleton, HI = sk.index.Head;
const face = new Face(await loadPack(pathToFileURL(path.join(CACHE, 'engine/face.json')), read));
const rest = fig.body.positions, disp = new Float32Array(rest.length);

const ids = job.motion == null ? null : [].concat(job.motion);
const clip = ids ? await E.clip(ids) : null;
const fps = clip?.fps ?? 30;
let times = job.frames || [0];                  // frame times, or a range: {range: [a, b, step]}
if (clip && job.range) { times = []; for (let t = job.range[0]; t <= Math.min(job.range[1], clip.frames - 1); t += job.range[2]) times.push(t); }
let life = null;
if (job.life) {
  const smp = newSample(sk.J);
  const head = s => clip ? headFacing(fig.retarget.pose(clip.sample(Math.min(clip.frames - 1, s * fps), smp)), HI, qRot) : { yaw: 0, pitch: 0 };
  const secs = Math.max(clip ? clip.frames / fps : 1, job.clockFps ? times.length / job.clockFps : 0);
  life = lifeTrack(head, { seconds: secs, ...job.life });
}
const N = fig.body.N, chunks = [], hips = [], heads = [], params = [];
for (const [k, t] of times.entries()) {
  fig.frame(clip, t);
  if (job.head || job.turns) {   // a turn of the head on top (stills): yaw about the world's up, pitch, roll about an axis given;
    // level: first the head's own pitch in the pose taken out (the drawing's heads look straight ahead);
    // turns: [{joint, axis (world), deg}] — a limb turned on top of the pose, for a still that shows the drawing's pose
    const P = fig.pose;
    for (const t of job.turns || []) {
      const h = t.deg * Math.PI / 360, n = Math.hypot(...t.axis), s = Math.sin(h) / n;
      turnUnder(P, sk, sk.index[t.joint], [t.axis[0] * s, t.axis[1] * s, t.axis[2] * s, Math.cos(h)]);
    }
    job.head = job.head || {};
    let a = (job.head.yaw || 0) * Math.PI / 180, b = (job.head.pitch || 0) * Math.PI / 180;
    if (job.head.level) { const f = headFacing(P, HI, qRot); b -= f.pitch * Math.PI / 180 * (job.head.levelPitch ?? 1); if (job.head.level !== 'pitch') a -= f.yaw * Math.PI / 180; }
    const r = (job.head.roll || 0) * Math.PI / 180, ra = job.head.rollAxis || [0, 0, 1];
    const share = [['Neck1', 0.3], ['Neck2', 0.3], ['Head', 0.4]];
    for (const [nm, h] of share) {
      const j = sk.index[nm];
      let qq = qMul([0, Math.sin(a * h / 2), 0, Math.cos(a * h / 2)], [Math.sin(b * h / 2), 0, 0, Math.cos(b * h / 2)]);
      const sr = Math.sin(r * h / 2);
      qq = qMul([ra[0] * sr, ra[1] * sr, ra[2] * sr, Math.cos(r * h / 2)], qq);
      turnUnder(P, sk, j, qq);
    }
    build(P, fig.body, [P.P[0], P.P[1], P.P[2]]);
    fig.skinner.skin(P, fig.positions);
    if (fig.spec.motion.floor === 'lowest' && clip) {
      let lo = Infinity; for (let i = 1; i < fig.positions.length; i += 3) lo = Math.min(lo, fig.positions[i]);
      const sh = P.floor - lo; for (let i = 1; i < fig.positions.length; i += 3) fig.positions[i] += sh;
    }
  }
  // the face's clock: the clip's time, or (a still pose filmed, clockFps) the k-th picture's
  const st = job.face || (life ? life.at(job.clockFps ? k / job.clockFps : t / fps) : { e: { calm: 1 } });
  params.push(st);
  face.apply(st, rest, disp);
  face.onto(fig.positions, rest, disp, fig.skinner.matrix(fig.pose, HI));
  chunks.push(Buffer.from(new Float32Array(fig.positions).buffer));
  const P = fig.pose.P;
  hips.push([P[0], P[1], P[2]]);
  heads.push([P[HI * 3], P[HI * 3 + 1], P[HI * 3 + 2]]);
}
await writeFile(job.out, Buffer.concat(chunks));
await writeFile(job.out.replace(/\.bin$/, '.json'), JSON.stringify({ frames: times.length, N, times, hips, head: heads, fps, params }));
console.log('frames', times.length, 'N', N);
