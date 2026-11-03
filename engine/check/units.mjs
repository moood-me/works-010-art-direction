// The engine's contracts, checked in node: what is refused, what a pose and a step promise, several meshes off one
// pose and one floor, meshes beyond 65,536 vertices, morphs, rest changes and their frames, the collision shape.
//   node engine/check/units.mjs
import { createEngine } from '../src/engine.js';
import { read } from './node-read.mjs';
import { resolve, upgrade } from '../src/character.js';
import { makeMesh } from '../src/mesh.js';
import { Pose } from '../src/pose.js';
import { withRest } from '../src/changes.js';
import { DEFORMERS } from '../src/deform.js';
import { regionsOf } from '../src/regions.js';

const E = await createEngine({ read });
let failed = 0, passed = 0;
const test = async (name, fn) => { try { await fn(); passed++; } catch (e) { failed++; console.log(`✗ ${name}: ${e.message}`); } };
const ok = (c, m) => { if (!c) throw new Error(m); };
const refuses = async (fn, re) => { try { await fn(); } catch (e) { ok(re.test(e.message), `refused, but with "${e.message}"`); return; } throw new Error('not refused'); };
const woman = await E.description('woman');
const desc = o => ({ ...structuredClone(woman), ...o });
const maxApart = (a, b, idx) => { let m = 0; for (const i of idx) m = Math.max(m, Math.hypot(a[i * 3] - b[i * 3], a[i * 3 + 1] - b[i * 3 + 1], a[i * 3 + 2] - b[i * 3 + 2])); return m; };
const all = n => Array.from({ length: n }, (_, i) => i);

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
  await refuses(() => resolve(v1, E.skeleton), /upgrade it to 2/);
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
await test('the collision shape: capsules on the body, moving with the pose', async () => {
  const fig = await E.figure('man'), clip = await E.clip('walk'); fig.frame(clip, 30, fig.pose);
  const C = fig.collider().update(fig.pose), sk = E.skeleton, P = fig.pose.P, H = sk.index.Hips, out = {};
  ok(C.capsules.length >= 15, `only ${C.capsules.length} capsules`);
  const sp = sk.index.Spine2, inside = C.distance([P[sp * 3], P[sp * 3 + 1], P[sp * 3 + 2]], out);
  ok(inside < -0.05, `the spine is not inside the body (${inside})`);
  const far = C.distance([P[H * 3] + 2, P[H * 3 + 1], P[H * 3 + 2]], out);
  ok(far > 1.5 && far < 2, `a point 2 m aside is ${far} m away`);
  ok(Math.abs(Math.hypot(...out.normal) - 1) < 1e-9, 'no normal');
});

await test('deformers in a description: unknown parameters refused; a deformer that moves joints is a rest change only', async () => {
  await refuses(() => resolve(desc({ rest: [{ kind: 'line', bend: 0.1 }] }), E.skeleton), /"frames" is missing/);
  await refuses(() => resolve(desc({ rest: [{ kind: 'line', bnd: 0.1, frames: 'keep' }] }), E.skeleton), /unknown key "bnd"/);
  await refuses(() => resolve(desc({ rest: [{ kind: 'silhouette', keys: [['belly', 1, 1, 0]], frames: 'keep' }] }), E.skeleton), /none of the allowed forms/);
  await refuses(() => resolve(desc({ pose: [{ kind: 'proportions', parts: { head: { size: 1.2 } } }] }), E.skeleton), /kind "proportions" is not one of/);
  await refuses(() => resolve(desc({ pose: [{ kind: 'smooth', cm: 4, space: 'pelvis' }] }), E.skeleton), /unknown key "space"/);
  const big = (await E.presets()).presets.find(p => p.id === 'proportions-big-head');
  await refuses(() => E.figure(resolve(desc({ pose: [{ kind: 'preset', id: big.pin }] }), E.skeleton)), /a change of the rest only/);
  await refuses(() => E.figure(resolve(desc({ rest: [{ kind: 'preset', id: 'silhouette-pear@0123456789abcdef', frames: 'keep' }] }), E.skeleton)), /changed under what pinned it/);
});
await test('every deformer at strength 0 leaves the body as it is (at rest, and as a pose layer)', async () => {
  const b = await E.body(woman.body), clip = await E.clip('walk'), plain = await E.figure('woman'); plain.frame(clip, 30, plain.pose);
  const P = { line: {}, squash: {}, contrapposto: {}, taper: {}, straight: {}, arc: {}, silhouette: { keys: [['waist', 0.7, 0.8, 0.02]] }, proportions: { parts: { head: { size: 1.4 }, thigh: { length: 1.3 } } },
    caricature: {}, anatomy: {}, smooth: {}, contour: { edits: [{ part: 'legs', dir: 'outer', keys: [[0, 1.5], [1, 1]] }] }, masses: { items: [{ shape: 'ellipsoid', at: { from: 'Hips' }, radii: [1, 1, 1] }] }, sign: {} };
  for (const kind of Object.keys(DEFORMERS)) {
    ok(kind in P, `no case for the deformer ${kind}`);
    const spec = resolve(desc({ rest: [{ kind, ...P[kind], strength: 0, frames: 'keep' }] }), E.skeleton), r = await E.restBody(spec);
    const d = maxApart(r.mesh.positions, b.mesh.positions, b.mesh.used), dj = maxApart(r.rig.joints, b.rig.joints, all(77));
    ok(d < 2e-5 && dj < 2e-5, `${kind} at strength 0 moved the rest ${d} m, joints ${dj} m`);
    if (kind === 'proportions' || kind === 'caricature') continue;
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
    const spec = await E.expand(resolve(desc({ rest: [{ kind: 'preset', id: p.pin, frames: 'keep' }] }), E.skeleton)), r = await E.restBody(spec);
    let bad = 0; for (const i of r.mesh.used) for (let c = 0; c < 3; c++) if (!Number.isFinite(r.mesh.positions[i * 3 + c])) bad++;
    // (a mass smaller than the body's own form there adds nothing: a mass is a union)
    ok(!bad && (p.group === 'masses' || maxApart(r.mesh.positions, b.mesh.positions, b.mesh.used) > 1e-4), `preset ${p.id}: ${bad ? bad + ' non-numbers' : 'changed nothing'}`);
  }
  for (const c of (await E.characters()).characters) await E.character(c.id);
});
await test('regions: landmarks in order on every body; parts and limbs of every vertex', async () => {
  for (const id of ['moood-woman', 'moood-child', 'anny-f-toddler', 'anny-m-tall', 'anny-T-chibi-baby17']) {
    const b = await E.body(id), R = regionsOf(b.mesh, b.rig), L = ['floor', 'ankle', 'knee', 'crotch', 'hips', 'waist', 'chest', 'armpit', 'shoulders', 'neck', 'head', 'top'];
    for (let k = 1; k < L.length; k++) ok(R.levels[L[k]] > R.levels[L[k - 1]], `${id}: ${L[k]} (${R.levels[L[k]].toFixed(3)}) not above ${L[k - 1]} (${R.levels[L[k - 1]].toFixed(3)})`);
    let worst = 0; for (const i of b.mesh.used) { let s = 0; for (let c = 0; c < 5; c++) s += R.limb[i * 5 + c]; worst = Math.max(worst, Math.abs(s - 1)); }
    ok(worst < 1e-3, `${id}: limb shares sum to 1 within ${worst}`);
  }
});

console.log(failed ? `${failed} of ${passed + failed} failed` : `all ${passed} hold`);
process.exit(failed ? 1 : 0);
