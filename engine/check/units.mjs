// The engine's contracts, checked in node: what is refused, what a pose and a step promise, several meshes off one
// pose and one floor, meshes beyond 65,536 vertices, morphs, rest changes and their frames, the collision shape.
//   node engine/check/units.mjs
import { createEngine } from '../src/engine.js';
import { read } from './node-read.mjs';
import { resolve, upgrade } from '../src/character.js';
import { makeMesh } from '../src/mesh.js';
import { qRot3 } from '../src/math.js';
import { Pose } from '../src/pose.js';
import { withRest } from '../src/changes.js';
import { DEFORMERS, complete } from '../src/deform.js';
import { regionsOf } from '../src/regions.js';
import { headShares } from '../src/head/frame.js';
import { wrapKey, wrapHead } from '../src/head/wrap.js';
import { buildStyle, styleKey, BUILD_SOURCES } from '../src/hair/hair.js';
import { hashOf } from '../src/hash.js';

const E = await createEngine({ read });
let failed = 0, passed = 0;
const test = async (name, fn) => { try { await fn(); passed++; } catch (e) { failed++; console.log(`✗ ${name}: ${e.message}`); } };
const ok = (c, m) => { if (!c) throw new Error(m); };
const refuses = async (fn, re) => { try { await fn(); } catch (e) { ok(re.test(e.message), `refused, but with "${e.message}"`); return; } throw new Error('not refused'); };
const woman = await E.description('woman');
const desc = o => ({ ...structuredClone(woman), ...o });
const maxApart = (a, b, idx) => { let m = 0; for (const i of idx) m = Math.max(m, Math.hypot(a[i * 3] - b[i * 3], a[i * 3 + 1] - b[i * 3 + 1], a[i * 3 + 2] - b[i * 3 + 2])); return m; };
const all = n => Array.from({ length: n }, (_, i) => i);
// the head's deformers, each with what it needs (src/head/)
const { kind: _wrap, ...wrapCase } = (await E.preset('form-red')).changes[0];
const HEAD_CASES = { wrap: wrapCase, face: { changes: { 'nose-scale-vert-incr': 1 } }, headOf: { body: `moood-child@${(await E.body('moood-child')).hash.slice(0, 16)}` },
  points: { moves: { noseTip: [0, 0, 0.2] } }, cage: { moves: [{ at: [1, 2, 2], by: [0, 0.2, 0] }] }, warps: { warps: [{ kind: 'push', at: [0, -0.6, 0.9], r: 0.3, by: [0, 0, 0.2] }] } };

await test('a description: unknown keys and values refused', async () => {
  await refuses(() => resolve(desc({ colour: 'red' }), E.skeleton), /unknown key "colour"/);
  await refuses(() => resolve(desc({ skinning: { method: 'quaternions' } }), E.skeleton), /"quaternions" is not one of/);
  await refuses(() => resolve(desc({ skinning: { metod: 'cor' } }), E.skeleton), /unknown key "metod"/);
  await refuses(() => resolve(desc({ pose: [{ kind: 'armsOf' }] }), E.skeleton), /kind "armsOf" is not one of/);
  await refuses(() => resolve(desc({ pose: [{ kind: 'armsOff', degres: 5 }] }), E.skeleton), /unknown key "degres"/);
  await refuses(() => resolve(desc({ rest: [{ kind: 'turn', joint: 'Spine9', axis: [1, 0, 0], degrees: 5, frames: 'keep' }] }), E.skeleton), /"Spine9" is not one of/);
  await refuses(() => resolve(desc({ rest: [{ kind: 'turn', joint: 'Spine1', axis: [1, 0, 0], degrees: 5 }] }), E.skeleton), /"frames" is missing/);
  await refuses(() => resolve(desc({ look: { skin: '#e9bb9c', roughness: 3 } }), E.skeleton), /3 is above 1/);
  await refuses(() => resolve(desc({ body: 'moood-woman' }), E.skeleton), /is not of the form/);
});
await test('a description of an earlier version: refused with the way to upgrade; the upgrade gives the stored preset', async () => {
  const v1 = { format: 'engine/character', version: 1, id: 'woman', label: woman.label, body: 'moood-woman',
    skinning: { method: 'cor', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} }, look: woman.look };
  await refuses(() => resolve(v1, E.skeleton), /upgrade it to 6/);
  const up = upgrade(v1, { bodyPin: woman.body });
  ok(JSON.stringify(resolve(up, E.skeleton)) === JSON.stringify(resolve(woman, E.skeleton)), 'the upgraded woman is not the preset');
  const v1c = { ...v1, skinning: { method: 'dqs', clavicleShare: 1 / 3 }, motion: { corrections: { armsOff: { degrees: 5 }, dampHeadSpine: { on: false } } } };
  const u = upgrade(v1c, { bodyPin: woman.body });
  ok(JSON.stringify(u.pose) === JSON.stringify([{ kind: 'armsOff', degrees: 5 }, { kind: 'clavicleShare', share: 1 / 3 }]), 'corrections and the share as layers: ' + JSON.stringify(u.pose));
});
await test('a pinned body whose data changed is refused', async () => {
  await refuses(() => E.figure(resolve(desc({ body: 'moood-woman@0123456789abcdef' }), E.skeleton)), /changed under what pinned it/);
  await refuses(() => E.motion('walk@0123456789abcdef'), /changed under what pinned it/);
});
await test('a chain: motions not made after each other, or without their joins said, are refused', async () => {
  await refuses(() => E.clip({ motions: ['walk', 'rollover'], joins: [{ blend: 'cut' }] }), /was not made to go on from walk/);
  await refuses(() => E.clip({ motions: ['lie', 'rollover'], joins: [] }), /says how each of its 1 joins/);
  await refuses(() => E.clip({ motions: ['lie', 'rollover'], joins: [{ blend: 'smooth' }] }), /a join is treated by/);
});
await test('a chain: where the next starts is measured from the shared frames, and agrees with the studio', async () => {
  const c = await E.clip({ motions: ['lie', 'rollover'], joins: [{ blend: 'cut' }] }), lie = await E.motion('lie'), ro = await E.motion('rollover'), J = lie.J;
  const s = { q: new Float64Array(J * 4), p: new Float64Array(J * 3) };
  c.sample(lie.frames - 1, s); const a = s.p.slice(); c.sample(lie.frames, s);
  ok(Math.hypot(s.p[0] - a[0], s.p[2] - a[2]) < 0.02, 'the pelvis jumps at the join');
  ok(Math.abs(ro.p[0] + ro.kimodo.startsAt.x - s.p[0]) < 0.004, 'not at startsAt');
});
await test('the pose belongs to whoever gives it', async () => {
  const fig = await E.figure('woman'), clip = await E.clip('walk'), p1 = new Pose(fig.rig.J), p2 = new Pose(fig.rig.J);
  fig.frame(clip, 10, p1); const keep = p1.P.slice(); fig.frame(clip, 50, p2);
  ok(p1.P.every((v, i) => v === keep[i]), 'an earlier pose was overwritten');
  ok(maxApart(p1.P, p2.P, all(77)) > 0.05, 'the two poses are the same');
});
await test('the step: time step, previous pose, resets on a new clip, a loop and a scrub', async () => {
  const fig = await E.figure('woman'), clip = await E.clip('walk'), log = [];
  fig.addSimulation({ step: c => log.push({ dt: c.dt, reset: c.reset, same: c.previous === c.pose, prevHip: c.previous.P[2], hip: c.pose.P[2] }) });
  for (const t of [0, 1, 2, 2.5, 119, 0, 1, 40]) fig.step(clip, t);
  fig.step(await E.clip('run'), 1);
  const r = log.map(l => l.reset);
  ok(JSON.stringify(r) === JSON.stringify([true, false, false, false, true, true, false, true, true]), 'resets ' + JSON.stringify(r));
  ok(Math.abs(log[1].dt - 1 / 30) < 1e-12 && Math.abs(log[3].dt - 0.5 / 30) < 1e-12 && log[0].dt === 0, 'dt ' + log.map(l => l.dt));
  ok(log.every(l => !l.same), 'previous and current are one object');
  ok(log[2].prevHip !== log[2].hip && log[0].prevHip === log[0].hip, 'previous is not the frame before (or not the frame itself at a reset)');
});
await test('several meshes off one pose and one floor; a mesh that counts for the floor lifts everything', async () => {
  const fig = await E.figure('woman'), clip = await E.clip('walk'), sk = E.skeleton, H = sk.index.Head, F = sk.index.LeftFoot;
  fig.frame(clip, 30, fig.pose); const alone = fig.pose.shift, headNow = fig.pose.P.slice(H * 3, H * 3 + 3);
  const box = (c, s) => { const p = []; for (const x of [-1, 1]) for (const y of [-1, 1]) for (const z of [-1, 1]) p.push(c[0] + x * s, c[1] + y * s, c[2] + z * s); return Float32Array.from(p); };
  const T = [0, 1, 3, 0, 3, 2, 4, 6, 7, 4, 7, 5, 0, 4, 5, 0, 5, 1, 2, 3, 7, 2, 7, 6, 0, 2, 6, 0, 6, 4, 1, 5, 7, 1, 7, 3];
  const r = fig.rig.joints, hat = makeMesh({ id: 'hat', kind: 'rigid', joint: H, positions: box([r[H * 3], r[H * 3 + 1] + 0.25, r[H * 3 + 2]], 0.05), triangles: T, floor: false });
  // a sole 3 cm under the foot's lowest rest point, carried by the foot
  let lo = Infinity; for (const i of fig.outputs[0].mesh.used) lo = Math.min(lo, fig.outputs[0].mesh.positions[i * 3 + 1]);
  const sole = makeMesh({ id: 'sole', kind: 'rigid', joint: F, positions: box([r[F * 3], lo - 0.03, r[F * 3 + 2] + 0.05], 0.02), triangles: T });
  // a sweep rebuilt each frame: a thin strip from the left shoulder to the hand
  const strip = makeMesh({ id: 'strip', kind: 'procedural', N: 4, triangles: [0, 1, 2, 1, 3, 2], floor: false, build(pose, rig, out) {
    for (const [n, name] of [[0, 'LeftArm'], [2, 'LeftHand']]) { const j = rig.skeleton.index[name]; for (const d of [0, 1]) { out[(n + d) * 3] = pose.P[j * 3]; out[(n + d) * 3 + 1] = pose.P[j * 3 + 1] + d * 0.01; out[(n + d) * 3 + 2] = pose.P[j * 3 + 2]; } }
  } });
  for (const m of [hat, strip]) fig.addMesh(m);
  fig.frame(clip, 30, fig.pose);
  ok(Math.abs(fig.pose.shift - alone) < 1e-9, 'a mesh not counted for the floor moved it');
  const hatNow = fig.outputs[1].positions, dHead = Math.hypot(hatNow[0] - fig.pose.P[H * 3], hatNow[1] - fig.pose.P[H * 3 + 1], hatNow[2] - fig.pose.P[H * 3 + 2]);
  ok(Math.abs(dHead - Math.hypot(0.05, 0.2, 0.05)) < 1e-4, 'the hat does not ride on the head');
  ok(Math.abs(fig.outputs[2].positions[6] - fig.pose.P[sk.index.LeftHand * 3]) < 1e-6, 'the strip is not at the hand');
  fig.addMesh(sole); fig.frame(clip, 30, fig.pose);
  ok(fig.pose.shift - alone > 0.005, `a sole under the foot did not lift the figure (${fig.pose.shift - alone})`);
  ok(Math.abs(fig.pose.P[H * 3 + 1] - headNow[1] - (fig.pose.shift - alone)) < 1e-6, 'the pose did not move with the meshes');
});
await test('a mesh beyond 65,536 vertices', async () => {
  const fig = await E.figure('woman'), n = 70000, P = new Float32Array(n * 3), JS = new Uint8Array(n * 4), WS = new Float32Array(n * 4), tris = [];
  const L = E.skeleton.index.LeftShin;
  for (let i = 0; i < n; i++) { P[i * 3] = 0.1 + (i % 100) * 1e-4; P[i * 3 + 1] = 0.3 + Math.floor(i / 100) * 1e-4; P[i * 3 + 2] = 0; JS[i * 4] = L; WS[i * 4] = 1; }
  for (let i = 0; i + 101 < n; i += 2) tris.push(i, i + 1, i + 100);
  const m = makeMesh({ id: 'big', positions: P, triangles: tris, skin: { joints: JS, weights: WS, K: 4 }, floor: false });
  ok(m.triangles instanceof Uint32Array, 'not 32-bit triangles');
  fig.addMesh(m); fig.frame(await E.clip('walk'), 30, fig.pose);
  const o = fig.outputs[1]; ok(o.positions[(n - 101) * 3 + 1] !== 0 && Number.isFinite(o.normals[0]), 'not skinned');
});
await test('morphs: weighed in each frame as a pose layer, or baked into the rest', async () => {
  const clip = await E.clip('wave'), girl = await E.description('girl');
  const a = await E.figure(resolve({ ...girl, pose: [{ kind: 'morph', name: 'plainFace', weight: 1 }] }, E.skeleton));
  const b = await E.figure(resolve({ ...girl, rest: [{ kind: 'morph', name: 'plainFace', weight: 1 }] }, E.skeleton));
  const c = await E.figure('girl');
  a.frame(clip, 40, a.pose); b.frame(clip, 40, b.pose); c.frame(clip, 40, c.pose);
  const face = (await E.body(girl.body)).face;
  ok(maxApart(a.positions, b.positions, face) < 0.002, 'the layer and the baked morph disagree ' + maxApart(a.positions, b.positions, face));
  ok(maxApart(a.positions, c.positions, face) > 0.001, 'the morph did nothing');
  await refuses(() => E.figure(resolve({ ...girl, pose: [{ kind: 'morph', name: 'smile', weight: 1 }] }, E.skeleton)).then(f => f.frame(clip, 1)), /no morph "smile"/);
});
await test('a rest change: frames kept ride along in motion; frames turned are anatomy (motion as before)', async () => {
  const clip = await E.clip('walk'), turn = { kind: 'turn', joint: 'Spine1', axis: [1, 0, 0], degrees: 12 };
  const plain = await E.figure('woman'), keep = await E.figure(resolve(desc({ rest: [{ ...turn, frames: 'keep' }] }), E.skeleton));
  const anat = await E.figure(resolve(desc({ rest: [{ ...turn, frames: 'turn' }] }), E.skeleton));
  for (const f of [plain, keep, anat]) f.frame(clip, 30, f.pose);
  ok(maxApart(plain.pose.P, anat.pose.P, all(77)) < 0.004, 'anatomy changed the motion ' + maxApart(plain.pose.P, anat.pose.P, all(77)));
  ok(maxApart(plain.pose.P, keep.pose.P, all(77)) > 0.05, 'the design did not ride along');
  const b = await E.body(woman.body), same = withRest(b, { positions: b.mesh.positions, joints: b.rig.joints, frames: 'turn' });
  let d = 0; for (let i = 0; i < b.rig.frames.length; i++) d = Math.max(d, Math.abs(Math.abs(same.rig.frames[i]) - Math.abs(b.rig.frames[i])));
  ok(d < 1e-4, 'frames turned for an unchanged body moved ' + d);
});
await test('the body\'s solids: the skin between two frames, its inside deep in, updated once a step and read by many', async () => {
  const fig = await E.figure('man'), clip = await E.clip('walk'), S = fig.solids(), sk = E.skeleton, out = { n: [0, 0, 0], v: [0, 0, 0] };
  for (let t = 0; t <= 30; t++) fig.step(clip, t);
  const P = fig.pose.P, at = (j, dx = 0) => [P[j * 3] + dx, P[j * 3 + 1], P[j * 3 + 2]], m = S.moment(1);
  ok(S.capsules(m).length >= 15, `only ${S.capsules(m).length} capsules`);
  // deep in the trunk (farther than the skin's points reach): inside, and which way is out
  const sp = at(sk.index.Spine2), d = S.skin(m, ...sp, out);
  ok(d < -0.05 && Math.abs(Math.hypot(...out.n) - 1) < 1e-6, `the spine is not deep inside the body (${d})`);
  ok(S.skin(m, ...at(sk.index.Hips, 2), out) === Infinity, 'a point 2 m aside is not out of reach');
  // just outside the hand, the skin's velocity is the hand's
  const hand = sk.index.RightHand, h1 = at(hand); fig.step(clip, 31); const h2 = [0, 1, 2].map(k => fig.pose.P[hand * 3 + k]), v = h2.map((x, k) => (x - h1[k]) * clip.fps);
  const top = fig.outputs[0].positions, near = Array.from(fig.outputs[0].mesh.used).reduce((b, i) => { const dd = Math.hypot(top[i * 3] - h2[0], top[i * 3 + 1] - h2[1], top[i * 3 + 2] - h2[2]); return dd < b[0] ? [dd, i] : b; }, [Infinity, -1])[1];
  S.skin(S.moment(1), top[near * 3], top[near * 3 + 1], top[near * 3 + 2], out);
  ok(Math.hypot(out.v[0] - v[0], out.v[1] - v[1], out.v[2] - v[2]) < 0.35 * Math.hypot(...v) + 0.05, `the skin's velocity at the hand ${out.v.map(x => x.toFixed(2))} against the hand's ${v.map(x => x.toFixed(2))}`);
  // between the frames the skin is where it was in between (a point on the hand halfway is on the skin at u = 0.5)
  const mid = [0, 1, 2].map(k => (fig.previous.P[hand * 3 + k] + fig.pose.P[hand * 3 + k]) / 2), dm = S.skin(S.moment(0.5), ...mid, out), d1 = S.skin(S.moment(1), ...mid, out);
  ok(dm < 0 && (d1 > dm || d1 === Infinity), `halfway the hand is not where it was halfway (${dm} at 0.5, ${d1} at 1)`);
  // two readers at once: asking at one moment changes nothing another sees
  const a = S.moment(0.25), b = S.moment(0.75), x = mid, da = S.skin(a, ...x, out); S.skin(b, ...x, out); ok(S.skin(a, ...x, out) === da, 'one reader changed what another sees');
});

await test('deformers in a description: unknown parameters refused; a deformer that moves joints is a rest change only', async () => {
  await refuses(() => resolve(desc({ rest: [{ kind: 'line', bend: 0.1 }] }), E.skeleton), /"frames" is missing/);
  await refuses(() => resolve(desc({ rest: [{ kind: 'line', bnd: 0.1, frames: 'keep' }] }), E.skeleton), /unknown key "bnd"/);
  await refuses(() => resolve(desc({ rest: [{ kind: 'silhouette', keys: [{ at: 'belly', width: 1 }], frames: 'keep' }] }), E.skeleton), /none of the allowed forms/);
  await refuses(() => resolve(desc({ rest: [{ kind: 'silhouette', keys: [['waist', 1, 1, 0]], frames: 'keep' }] }), E.skeleton), /must be an object/);
  await refuses(() => resolve(desc({ pose: [{ kind: 'sign' }] }), E.skeleton), /kind "sign" is not one of/);
  await refuses(() => resolve(desc({ pose: [{ kind: 'smooth', cm: 4, space: 'pelvis' }] }), E.skeleton), /unknown key "space"/);
  await refuses(() => resolve(desc({ pose: [{ kind: 'squash', space: 'upright' }] }), E.skeleton), /unknown key "space"/);
  const sign = (await E.presets()).presets.find(p => p.id === 'pictogram-rectangle');
  await refuses(() => E.figure(resolve(desc({ pose: [{ kind: 'preset', id: sign.pin }] }), E.skeleton)), /a change of the rest only/);
  await refuses(() => E.figure(resolve(desc({ rest: [{ kind: 'preset', id: 'silhouette-pear@0123456789abcdef', frames: 'keep' }] }), E.skeleton)), /changed under what pinned it/);
});
await test('every deformer at strength 0 leaves the body as it is (at rest, and as a pose layer)', async () => {
  const b = await E.body(woman.body), clip = await E.clip('walk'), plain = await E.figure('woman'); plain.frame(clip, 30, plain.pose);
  const P = { line: {}, squash: {}, contrapposto: {}, taper: {}, straight: {}, arc: {}, silhouette: { keys: [{ at: 'waist', width: 0.7, depth: 0.8, forward: 0.02 }] }, proportions: { parts: { head: { size: 1.4 }, thigh: { length: 1.3 } } },
    caricature: {}, anatomy: {}, smooth: {}, contour: { edits: [{ part: 'legs', dir: 'outer', keys: [[0, 1.5], [1, 1]] }] }, masses: { items: [{ shape: 'ellipsoid', at: { from: 'Hips' }, radii: [1, 1, 1] }] }, sign: {}, ...HEAD_CASES };
  for (const kind of Object.keys(DEFORMERS)) {
    ok(kind in P, `no case for the deformer ${kind}`);
    const spec = resolve(desc({ rest: [{ kind, ...P[kind], strength: 0, frames: 'keep' }] }), E.skeleton), r = await E.restBody(spec);
    const d = maxApart(r.mesh.positions, b.mesh.positions, b.mesh.used), dj = maxApart(r.rig.joints, b.rig.joints, all(77));
    ok(d < 2e-5 && dj < 2e-5, `${kind} at strength 0 moved the rest ${d} m, joints ${dj} m`);
    if (kind === 'sign') continue;
    const f = await E.figure(resolve(desc({ pose: [{ kind, ...P[kind], strength: 0 }] }), E.skeleton)); f.frame(clip, 30, f.pose);
    ok(maxApart(f.positions, plain.positions, b.mesh.used) < 2e-5, `${kind} at strength 0 as a pose layer moved the figure`);
  }
});
await test('a deformer of the figure as a pose layer: the same in the figure\'s own space wherever it stands and faces; every mesh and the joints go with it', async () => {
  const clip = await E.clip('walk'), layer = { kind: 'line', view: 'side', curve: 'C', bend: 0.1 };
  const a = await E.figure(resolve(desc({ pose: [layer] }), E.skeleton)), b = await E.figure(resolve(desc({ pose: [layer] }), E.skeleton), { place: { position: [3, 0, -2], heading: 2.2 } });
  const p0 = await E.figure('woman');
  for (const f of [a, b, p0]) f.frame(clip, 30, f.pose);
  // b's figure brought back to a's place and heading
  const c = Math.cos(-2.2), s = Math.sin(-2.2), back = (P, i) => { const x = P[i * 3] - 3, z = P[i * 3 + 2] + 2; return [c * x + s * z, P[i * 3 + 1], -s * x + c * z]; };
  let d = 0; for (const i of a.outputs[0].mesh.used) { const q = back(b.positions, i); d = Math.max(d, Math.hypot(q[0] - a.positions[i * 3], q[1] - a.positions[i * 3 + 1], q[2] - a.positions[i * 3 + 2])); }
  ok(d < 1e-4, `placed and turned, the layer differs by ${d} m`);
  ok(maxApart(a.positions, p0.positions, a.outputs[0].mesh.used) > 0.05, 'the layer did nothing');
  const H = E.skeleton.index.Head; ok(Math.hypot(a.pose.P[H * 3 + 2] - p0.pose.P[H * 3 + 2], a.pose.P[H * 3] - p0.pose.P[H * 3]) > 0.03, 'the joints did not go with it');
  // a rigid mesh on the head moves with the layer too
  const r = a.rig.joints, hat = makeMesh({ id: 'hat', kind: 'rigid', joint: H, positions: Float32Array.from([r[H * 3], r[H * 3 + 1] + 0.3, r[H * 3 + 2], r[H * 3] + 0.01, r[H * 3 + 1] + 0.3, r[H * 3 + 2], r[H * 3], r[H * 3 + 1] + 0.31, r[H * 3 + 2]]), triangles: [0, 1, 2], floor: false });
  const a2 = await E.figure(resolve(desc({ pose: [layer] }), E.skeleton)); a2.addMesh(hat); a2.frame(clip, 30, a2.pose);
  const p2 = await E.figure('woman'); p2.addMesh(hat); p2.frame(clip, 30, p2.pose);
  ok(maxApart(a2.outputs[1].positions, p2.outputs[1].positions, [0, 1, 2]) > 0.01, 'a rigid mesh did not follow the layer');
});
await test('a deformer of the surface as a pose layer is its rest change carried as a morph', async () => {
  const clip = await E.clip('idle'), sm = { kind: 'smooth', cm: 5 };
  const lay = await E.figure(resolve(desc({ pose: [sm] }), E.skeleton)), rest = await E.figure(resolve(desc({ rest: [{ ...sm, frames: 'keep' }] }), E.skeleton));
  lay.frame(clip, 60, lay.pose); rest.frame(clip, 60, rest.pose);
  const d = maxApart(lay.positions, rest.positions, lay.outputs[0].mesh.used);
  ok(d < 0.004, `the morph and the rest change differ by ${d} m (only the centres of rotation may)`);
});
await test('every preset makes a body, and its index and every character pin it as it is', async () => {
  const index = await E.presets(), b = await E.body(woman.body);
  for (const p of index.presets) {
    const now = await E.preset(p.pin);
    ok(now.label.ru && now.label.en && now.about?.ru && now.about?.en, `preset ${p.id} has no label or about in both languages`);
    if (!now.changes) continue;   // the head's parts: their own contracts (heads.mjs)
    const spec = await E.expand(resolve(desc({ rest: [{ kind: 'preset', id: p.pin, frames: 'keep' }] }), E.skeleton)), r = await E.restBody(spec);
    let bad = 0; for (const i of r.mesh.used) for (let c = 0; c < 3; c++) if (!Number.isFinite(r.mesh.positions[i * 3 + c])) bad++;
    // (a mass smaller than the body's own form there adds nothing: a mass is a union)
    ok(!bad && (p.group === 'masses' || maxApart(r.mesh.positions, b.mesh.positions, b.mesh.used) > 1e-4), `preset ${p.id}: ${bad ? bad + ' non-numbers' : 'changed nothing'}`);
  }
  for (const c of (await E.characters()).characters) await E.character(c.id);
});
await test('a character that starts from another (a full-body preset as a part): its body, rest and pose, then its own; a base whose content changed is refused', async () => {
  const princess = await E.description('disney-princess'), base = await E.base(`disney-princess@${(await import('../src/hash.js')).hashOf([princess]).slice(0, 16)}`);
  ok(base.id === 'disney-princess', 'the base was not read');
  const pin = `disney-princess@${(await import('../src/hash.js')).hashOf([princess]).slice(0, 16)}`;
  const mine = { format: 'engine/character', version: 6, id: 'my-princess', label: { ru: 'моя', en: 'mine' }, base: pin,
    rest: [{ kind: 'squash', stretch: 0.1, frames: 'keep' }], pose: [{ kind: 'armsOff', degrees: 5 }], look: { skin: '#aa8877' } };
  const spec = await E.resolve(mine), p = await E.resolve(princess);
  ok(spec.body === p.body && spec.rest.length === p.rest.length + 1 && spec.rest.at(-1).kind === 'squash' && spec.pose.at(-1).kind === 'armsOff', 'not the base and then its own');
  ok(spec.look.skin === '#aa8877' && spec.skinning.method === p.skinning.method, 'look or skinning not over the base');
  const f = await E.figure(spec); f.frame(await E.clip('walk'), 30, f.pose);
  await refuses(() => E.resolve({ ...mine, base: 'disney-princess@0123456789abcdef' }), /changed under what pinned it/);
  const { base: _b, ...alone } = mine;
  await refuses(() => resolve(alone, E.skeleton), /"body" is missing/);
});
await test('regions: landmarks in order on every body; parts and limbs of every vertex', async () => {
  for (const id of ['moood-woman', 'moood-child', 'anny-f-toddler', 'anny-m-tall', 'anny-T-chibi-baby17']) {
    const b = await E.body(id), R = regionsOf(b.mesh, b.rig), L = ['floor', 'ankle', 'knee', 'crotch', 'hips', 'waist', 'chest', 'armpit', 'shoulders', 'neck', 'head', 'top'];
    for (let k = 1; k < L.length; k++) ok(R.levels[L[k]] > R.levels[L[k - 1]], `${id}: ${L[k]} (${R.levels[L[k]].toFixed(3)}) not above ${L[k - 1]} (${R.levels[L[k - 1]].toFixed(3)})`);
    let worst = 0; for (const i of b.mesh.used) { let s = 0; for (let c = 0; c < 5; c++) s += R.limb[i * 5 + c]; worst = Math.max(worst, Math.abs(s - 1)); }
    ok(worst < 1e-3, `${id}: limb shares sum to 1 within ${worst}`);
  }
});

await test('heads: every head preset makes a head on its body; a head is refused where it is wrong; a head from a preset with its own changes', async () => {
  const index = await E.presets();
  for (const p of index.presets.filter(p => p.group === 'head')) {
    const ch = (await E.characters()).characters.find(c => c.id === p.id); if (!ch) continue;
    const f = await E.figure(ch.id); f.frame(null, 0, f.pose);
    let bad = 0; for (const o of f.outputs) for (let i = 0; i < o.positions.length; i++) if (!Number.isFinite(o.positions[i])) bad++;
    ok(!bad && f.body.head && f.outputs[0].mesh.uv, `${p.id}: ${bad} non-numbers, or no head`);
  }
  const red = await E.description('head-red'), dr = o => ({ ...structuredClone(red), ...o });
  await refuses(() => resolve(dr({ head: { ...red.head, features: [{ kind: 'eye', x: 0.4 }] } }), E.skeleton), /"y" is missing/);
  await refuses(() => resolve(dr({ head: { ...red.head, light: { toon: 'yes' } } }), E.skeleton), /none of the allowed forms/);
  await refuses(async () => { const f = await E.figure(resolve(dr({ pose: [{ kind: 'expression', name: 'wink', weight: 1 }] }), E.skeleton)); f.frame(null, 0, f.pose); }, /expression "wink": the head has/);
  await refuses(async () => { const f = await E.figure(resolve({ ...structuredClone(woman), pose: [{ kind: 'expression', name: 'blink', weight: 1 }] }, E.skeleton)); f.frame(null, 0, f.pose); }, /has no head/);
  // its own: an eye as volume replaces the preset's eyes (by id), the blush taken off, a deformer of the form after the wrap
  const mine = await E.character('head-red-mine'), base = await E.character('head-red');
  ok(mine.head.features.find(f => f.id === 'eyes').as === 'volume' && base.head.features.find(f => f.id === 'eyes').as === 'paint', 'its own eyes did not replace the preset\'s');
  ok(mine.rest.length === base.rest.length + 1 && mine.rest.at(-1).kind === 'points' && mine.rest.at(-2).kind === 'wrap', 'its own form not after the preset\'s');
  const off = await E.expand(await E.resolve(dr({ head: { ...red.head, features: [{ kind: 'off', id: 'blush' }] } })));
  ok(!off.head.features.some(f => f.id === 'blush') && off.head.features.length === base.head.features.length - 1, 'a feature taken off stayed');
});
await test('heads: an expression at weight 0 leaves the figure as it is; at weight 1 it moves the face only (and what the jaw carries)', async () => {
  const red = await E.description('head-red'), clip = await E.clip('walk');
  const plain = await E.figure('head-red'); plain.frame(clip, 30, plain.pose);
  for (const name of ['blink', 'open', 'smile']) {
    const zero = await E.figure(await E.resolve({ ...structuredClone(red), pose: [{ kind: 'expression', name, weight: 0 }] })); zero.frame(clip, 30, zero.pose);
    ok(maxApart(zero.positions, plain.positions, plain.outputs[0].mesh.used) < 1e-6, `${name} at weight 0 moved the figure`);
    const one = await E.figure(await E.resolve({ ...structuredClone(red), pose: [{ kind: 'expression', name, weight: 1 }] })); one.frame(clip, 30, one.pose);
    // (the face: the head's skin, and what Anny's jaw weights carry down the throat)
    const { omega, jaw } = headShares(one.body.mesh, E.skeleton); let face = 0, body = 0;
    for (const i of one.outputs[0].mesh.used) { const d = Math.hypot(...[0, 1, 2].map(c => one.positions[i * 3 + c] - plain.positions[i * 3 + c])); if (omega[i] > 0.05 || jaw[i] > 0) face = Math.max(face, d); else body = Math.max(body, d); }
    ok(face > 5e-4 && body < 1e-6, `${name}: the face moved ${face} m, the body ${body} m`);
    ok(Object.keys(one.ctx.expressions).includes(name), `${name}: what it asks of the drawing is not said`);
  }
});
await test('heads: a face deformer on the rest and as a pose layer is the same; Anny\'s face changes are on her mesh only', async () => {
  const clip = await E.clip('idle'), c = { kind: 'warps', warps: [{ kind: 'push', at: [0, -0.6, 0.9], r: 0.3, by: [0, 0, 0.2] }] };
  const lay = await E.figure(resolve(desc({ pose: [c] }), E.skeleton)), rest = await E.figure(resolve(desc({ rest: [{ ...c, frames: 'keep' }] }), E.skeleton));
  lay.frame(clip, 60, lay.pose); rest.frame(clip, 60, rest.pose);
  ok(maxApart(lay.positions, rest.positions, lay.outputs[0].mesh.used) < 0.004, 'the layer and the rest change differ');
  await refuses(() => E.restBody(resolve(desc({ rest: [{ kind: 'face', changes: { 'nose-long-incr': 1 }, frames: 'keep' }] }), E.skeleton)), /Anny has no face change "nose-long-incr"/);
});
await test('heads: the head\'s solid is where the head is, its jaw with the Jaw joint', async () => {
  const f = await E.figure('head-red'), clip = await E.clip('look-around'), H = E.skeleton.index.Head, S = f.solids(), l = [0, 0, 0], n = [0, 0, 0];
  for (let t = 0; t <= 60; t++) f.step(clip, t);
  const p = f.pose, m = S.moment(1), inHead = [p.P[H * 3], p.P[H * 3 + 1] + 0.08, p.P[H * 3 + 2]];
  const d = S.head.distance(S.head.local(m, inHead, l)); ok(d < 0, `a point in the head is outside its shape (${d})`);
  S.head.turn(m, S.head.normal(S.head.local(m, [inHead[0], inHead[1] + 0.2, inHead[2]], l), n), n); ok(n[1] > 0.7, `the shape's normal above the head points ${n}`);
  // an open mouth: a point just under the chin at rest is inside the shape once the jaw opens
  const shut = await E.figure('head-red'), open = await E.figure({ ...await E.character('head-red'), pose: [{ kind: 'expression', name: 'open', weight: 2 }] });
  const F = shut.body.head.frame, chin = F.toW(0, -1.12, 0.45), under = g => { g.step(null, 0); const s = g.solids(); return s.head.distance(s.head.local(s.moment(1), chin, l)); }, d0 = under(shut), d1 = under(open);
  ok(Math.abs(d1 - d0) > 0.002, `the jaw's part of the shape did not move with the jaw (${d0} → ${d1})`);
});
await test('heads: a wrapped head is stored for every character, and what is stored is what the wrap makes now', async () => {
  for (const c of (await E.characters()).characters) {
    const spec = await E.character(c.id); if (spec.head?.wrapAt == null) continue;
    const body = await E.restBody({ ...spec, rest: spec.rest.slice(0, spec.head.wrapAt) });
    ok(await E.stored('wraps', wrapKey(complete(spec.head.wrap), body)), `${c.id}: its wrap is not stored (node engine/tools/characters.mjs wraps)`);
  }
  const spec = await E.character('head-mask'), w = complete(spec.head.wrap), body = await E.restBody({ ...spec, rest: spec.rest.slice(0, spec.head.wrapAt) });
  const stored = (await E.stored('wraps', wrapKey(w, body))).arrays.positions, made = wrapHead(body, w.form, w.marks, w.neckSlim, w.onto);
  ok(maxApart(stored, made, body.mesh.used) < 1e-6, 'the stored wrap is not what the wrap makes now — its version (src/head/version.js) was not raised');
});
await test('heads: a head taken as a part — its form weakened, a way taken away, a feature changed by its id, features from a preset', async () => {
  const red = await E.preset('head-red'), index = (await E.presets()).presets, pinOf = id => index.find(p => p.id === id).pin, redPin = pinOf('head-red');
  const h = await E.headOf({ preset: redPin, strength: 0.5, features: [{ id: 'eyes', as: 'volume' }, { kind: 'off', id: 'brows' }], pieces: [{ kind: 'off', id: 'hair' }] });
  ok(h.form[0].strength === 0.5 && h.form[0].name === 'form-red', `the form: ${JSON.stringify(h.form.map(c => [c.name, c.strength]))}`);
  const eyes = h.features.find(f => f.id === 'eyes'), base = (await E.headOf(red.head)).features.find(f => f.id === 'eyes');
  ok(eyes.as === 'volume' && eyes.iris.join() === base.iris.join(), 'the eyes not changed by their id alone');
  ok(!h.features.some(f => f.id === 'brows') && !h.pieces.some(p => p.id === 'hair'), 'what was taken away is there');
  const off = await E.headOf({ preset: redPin, form: [{ kind: 'off', name: 'form-red' }] });
  ok(!off.form.length, 'the way was not taken away');
  await refuses(() => E.headOf({ preset: redPin, features: [{ id: 'eyes', w: 7 }] }), /7 is above/);
  await refuses(() => E.headOf({ features: [{ id: 'eyes', as: 'volume' }] }), /to change: there is none/);
  const dots = await E.headOf({ preset: redPin, features: [{ kind: 'preset', id: pinOf('features-dots') }] });
  ok(dots.features.find(f => f.id === 'eyes').irisScale === 2.2, 'a features preset did not take the place of the head\'s');
});
// ———— hair (stage 3) ————
const apart = (a, b) => { let m = 0; for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i])); return a.length === b.length ? m : Infinity; };
const hairOn = async (head, base = 'woman') => E.figure(await E.expand(await E.resolve({ ...structuredClone(await E.description(base)), id: 'h', head })));
const hairPin = async id => (await E.presets()).presets.find(p => p.id === id).pin;
await test('hair: every hairstyle preset makes hair on a head; what is stored is what is built now', async () => {
  for (const p of (await E.presets()).presets.filter(p => p.group === 'hair')) {
    const pre = await E.preset(p.pin);
    for (const piece of pre.pieces) if (piece.kind === 'style') ok(await E.stored('hair', styleKey(piece)), `${p.id}: its hairstyle is not stored (node engine/tools/characters.mjs hair)`);
  }
  // (one built again here; every one is built again by the tool whenever the code they are built by changed — its hash
  // is kept beside them)
  const piece = { kind: 'style', style: 'nimona' }, stored = (await E.stored('hair', styleKey(piece))).arrays, made = buildStyle(piece).arrays;
  for (const [k, v] of Object.entries(made)) ok(apart(stored[k], v.array) === 0, `${k}: the stored hairstyle is not what is built now — its version (src/head/version.js: hair) was not raised`);
  const { readFile } = await import('node:fs/promises'), source = hashOf(await Promise.all(BUILD_SOURCES.map(f => readFile(new URL('../' + f, import.meta.url), 'utf8')))).slice(0, 16);
  ok(JSON.parse(await readFile(new URL('../data/hair/index.json', import.meta.url), 'utf8')).source === source, 'the code the hairstyles are built by changed since they were stored: node engine/tools/characters.mjs hair (it builds them again and says whether their version must go up)');
});
await test('hair: a hairstyle changed by its groups, colour and physics; refused where it has no such group', async () => {
  const gwen = await hairPin('hair-v1-gwen');
  const f = await hairOn({ pieces: [{ kind: 'preset', id: gwen }, { id: 'hair', off: ['fringe'], color: '#3a2a20', physics: { hold: 2 } }] });
  ok(f.simulations.length === 1 && f.simulations[0].k.hold === 2, 'the physics not taken');
  ok(f.outputs.some(o => o.mesh.color === '#3a2a20'), 'the colour not taken');
  const whole = await hairOn({ pieces: [{ kind: 'preset', id: gwen }] });
  ok(f.simulations[0].chains.length < whole.simulations[0].chains.length, 'the fringe not taken away');
  await refuses(() => hairOn({ pieces: [{ kind: 'style', style: 'gwen', off: ['tail'] }] }), /has no group "tail"/);
  const still = await hairOn({ pieces: [{ kind: 'preset', id: gwen }, { id: 'hair', moves: false }] });
  ok(!still.simulations.length, 'hair that does not move still simulated');
});
await test('hair: the step — a scrub back is a fresh start; a loop goes on from where the hair was on the head; the same moment again moves nothing; frame keeps nothing', async () => {
  const f = await hairOn({ pieces: [{ kind: 'preset', id: await hairPin('hair-v1-alva') }] }), clip = await E.clip('walk'), sim = f.simulations[0];
  for (let t = 0; t <= 20; t++) f.step(clip, t);
  const at20 = Float64Array.from(sim.x); f.step(clip, 20); ok(apart(at20, sim.x) === 0, 'the same moment again moved the hair');
  f.step(clip, 0); const back = Float64Array.from(sim.x);
  const g = await hairOn({ pieces: [{ kind: 'preset', id: await hairPin('hair-v1-alva') }] }); g.step(clip, 0);
  ok(apart(back, g.simulations[0].x) < 1e-9, 'a scrub back to the start is not a fresh start');
  for (let t = 1; t <= 20; t++) f.step(clip, t);
  ok(apart(at20, sim.x) < 1e-9, 'played again, the hair is not where it was');
  // a loop: across the clip's end the hair goes on as it was on the head (carried by the head's jump, swinging on as it
  // swung on it) — on the head it moves, on the whole, a tenth of what starting afresh would, and no more than twice a
  // frame of the motion (a wave: across its end the body itself jumps 4 cm against the head, and pushes it a little)
  const wave = await E.clip('wave'), H = E.skeleton.index.Head, free = sim.chains.filter(c => !c.head).flatMap(c => Array.from({ length: c.n }, (_, k) => (c.at + k) * 3));
  const inHead = fig => { const Q = fig.pose.Q, P = fig.pose.P, q = [-Q[H * 4], -Q[H * 4 + 1], -Q[H * 4 + 2], Q[H * 4 + 3]], o = [0, 0, 0], x = fig.simulations[0].x, out = new Float64Array(x.length); for (const i of free) { qRot3(q, x[i] - P[H * 3], x[i + 1] - P[H * 3 + 1], x[i + 2] - P[H * 3 + 2], o); out.set(o, i); } return out; };
  const mean = (a, b) => free.reduce((s, i) => s + Math.hypot(a[i] - b[i], a[i + 1] - b[i + 1], a[i + 2] - b[i + 2]), 0) / free.length;
  let frame = 0, prev = null;
  for (let t = 0; t < wave.frames; t++) { f.step(wave, t); const now = inHead(f); if (t > 10) frame = Math.max(frame, mean(prev, now)); prev = now; }
  f.step(wave, 1, { loop: true }); const pop = mean(prev, inHead(f)); f.step(wave, 0); const fresh = mean(prev, inHead(f));
  ok(pop <= 2 * frame && pop < fresh / 10, `across the loop the hair moved ${(pop * 1000).toFixed(1)} mm on the head (the mean); in a frame of the wave at most ${(frame * 1000).toFixed(1)}, set anew ${(fresh * 1000).toFixed(1)}`);
  const o = f.outputs.find(o => o.mesh.sim), before2 = Float32Array.from(o.positions); f.frame(clip, 5); ok(apart(before2, o.positions) > 0, 'frame did not draw the hair (at rest on the head)');
});
await test('hair: a ready head\'s hair as it was (rigid) unless it moves; moving, at rest it keeps its look', async () => {
  const rigid = await E.figure('head-red'), moving = await E.figure('hair-g3-red');
  ok(!rigid.simulations.length && moving.simulations.length === 1, 'which moves');
  const pose = rigid.frame(null, 0); moving.step(null, 0);
  const a = rigid.outputs.find(o => o.name === 'hair-locks'), b = moving.outputs.find(o => o.name === 'hair-locks');
  // (on the head itself — the part of each lock above the shoulders — the moving hair lies as the rigid one)
  let worst = 0; const H = pose.P[E.skeleton.index.Neck1 * 3 + 1];
  for (const v of a.mesh.used) if (a.positions[v * 3 + 1] > H + 0.06) worst = Math.max(worst, Math.hypot(a.positions[v * 3] - b.positions[v * 3], a.positions[v * 3 + 1] - b.positions[v * 3 + 1], a.positions[v * 3 + 2] - b.positions[v * 3 + 2]));
  ok(worst < 0.01, `on the head the moving hair lies ${(worst * 1000).toFixed(1)} mm from its design`);
});
console.log(failed ? `${failed} of ${passed + failed} failed` : `all ${passed} hold`);
process.exit(failed ? 1 : 0);
