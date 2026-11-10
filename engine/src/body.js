// A body — the one description clothes, hair, deformers, skinning and the player all take:
//   positions   Float32Array N×3, the vertices at rest (metres, y up, facing +z, the person's left +x)
//   triangles   Uint16Array T×3
//   skin        {joints: Uint8Array N×4, weights: Float32Array N×4} — each vertex's four SOMA joints, weights summing to 1
//   parts       {names, weights: Uint8Array N×P (/255)} — each vertex's share of each body part (from the skin weights)
//   joints      Float64Array 77×3 — each joint's place at rest, as the body is (a deformer that moves the body moves these)
//   frames      Float64Array 77×4 — each joint's frame at rest (quaternions): what a motion's rotations are carried by
//               (src/retarget.js). They are the retargeting reference: a deformer changes the places, never the frames,
//               so whatever it designed into the rest pose rides along in every motion.
//   measures    sizes read off the body (body.measure() again after changing it)
//   eyes, face, facePlain — what moood's bodies have for drawn faces (optional)
// Stored as packs (src/pack.js): data/bodies/<id>.json (positions, joints, frames…) on a shared topology
// (data/topology/<id>.json: triangles, skin, parts, face).
import { loadPack } from './pack.js';

const topologies = new Map();

export async function loadBody(url, skeleton, read) {
  const { header: h, arrays: a } = await loadPack(url, read);
  if (h.format !== 'engine/body' || h.version !== 1) throw new Error(`${url}: not a body of version 1`);
  if (h.skeleton !== skeleton.id) throw new Error(`${url}: on skeleton ${h.skeleton}, not ${skeleton.id}`);
  const tu = new URL(`../topology/${h.topology}.json`, url).href;
  if (!topologies.has(tu)) topologies.set(tu, loadPack(tu, read));
  const { header: th, arrays: t } = await topologies.get(tu);
  if (th.vertices * 3 !== a.positions.length) throw new Error(`${url}: ${a.positions.length / 3} vertices, its topology has ${th.vertices}`);
  return makeBody({
    id: h.id, label: h.label, source: h.source, topology: h.topology, skeleton,
    positions: a.positions, triangles: t.triangles, skin: { joints: t.skinJoints, weights: t.skinWeights },
    parts: { names: th.parts, weights: t.parts }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
    eyes: h.eyes, face: t.face, facePlain: a.facePlain,
  });
}

export function makeBody(o) {
  const b = { ...o, N: o.positions.length / 3 };
  b.measure = () => (b.measures = measure(b));
  // the same body with another rest (a deformer's result): new places for the vertices and the joints, the same frames
  b.withRest = (positions, joints) => makeBody({ ...o, positions, joints: joints ?? o.joints });
  b.part = name => { const p = b.parts.names.indexOf(name); if (p < 0) throw new Error(`no part ${name}`); const P = b.parts.names.length; return Float32Array.from({ length: b.N }, (_, i) => b.parts.weights[i * P + p] / 255); };
  b.measure();
  return b;
}

// sizes read off a body at rest (metres)
export function measure(b) {
  const sk = b.skeleton, J = n => { const j = sk.index[n]; return [b.joints[j * 3], b.joints[j * 3 + 1], b.joints[j * 3 + 2]]; };
  const d = (p, q) => Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]);
  let lo = Infinity, hi = -Infinity;
  const used = new Uint8Array(b.N); for (const i of b.triangles) used[i] = 1;
  for (let i = 0; i < b.N; i++) if (used[i]) { const y = b.positions[i * 3 + 1]; if (y < lo) lo = y; if (y > hi) hi = y; }
  const leg = s => d(J(s + 'Leg'), J(s + 'Shin')) + d(J(s + 'Shin'), J(s + 'Foot')) + (J(s + 'Foot')[1] - lo);
  const arm = s => d(J(s + 'Arm'), J(s + 'ForeArm')) + d(J(s + 'ForeArm'), J(s + 'Hand'));
  return {
    floor: lo, height: hi - lo,
    hipHeight: J('Hips')[1] - lo,
    legLength: (leg('Left') + leg('Right')) / 2,
    armLength: (arm('Left') + arm('Right')) / 2,
    shoulderWidth: d(J('LeftArm'), J('RightArm')),
    headHeight: hi - J('Neck2')[1],
    headCenter: [(J('Head')[0] + J('HeadEnd')[0]) / 2, (J('Head')[1] + hi) / 2, (J('Head')[2] + J('HeadEnd')[2]) / 2],
  };
}
