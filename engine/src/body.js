// A body: a rig (src/rig.js: its skeleton, joint places and frames at rest, floor, hip height) and its skin, a mesh
// (src/mesh.js) — the one description clothes, hair, deformers, skinning and the player take.
//   body.rig        joints (77×3, the designed rest), frames (77×4, the retargeting reference), floor, hipHeight
//   body.mesh       positions (N×3, metres, y up, facing +z, the person's left +x), triangles, skin {joints, weights, K: 4},
//                   used (the vertices triangles use), morphs (plainFace: moood's face without features, where it has one)
//   body.parts      {names, weights: Uint8Array N×P (/255)} — each vertex's share of each body part (from the weights)
//   body.measures   sizes read off the body (floor, height, hipHeight, legLength, armLength, shoulderWidth, headHeight, headCenter)
//   body.hash       its content (the body's pack and its topology's): what a character pins
//   eyes, face, facePlain — what moood's bodies have for drawn faces (optional)
// Stored as packs (src/pack.js): data/bodies/<id>.json (positions, joints, frames…) on a shared topology
// (data/topology/<id>.json: triangles, skin, parts, face).
// Places are the designed rest; frames are the retargeting reference. A change of the rest (src/changes.js) says
// what its frames do: kept (a design rides along in motion) or turned with their bones (anatomy).
import { loadPack } from './pack.js';
import { hashOf } from './hash.js';
import { makeRig } from './rig.js';
import { makeMesh } from './mesh.js';

const topologies = new Map();

export async function loadBody(url, skeleton, read) {
  const { header: h, arrays: a, hash } = await loadPack(url, read);
  if (h.format !== 'engine/body' || h.version !== 1) throw new Error(`${url}: not a body of version 1`);
  if (h.skeleton !== skeleton.id) throw new Error(`${url}: on skeleton ${h.skeleton}, not ${skeleton.id}`);
  const tu = new URL(`../topology/${h.topology}.json`, url).href;
  if (!topologies.has(tu)) topologies.set(tu, loadPack(tu, read));
  const { header: th, arrays: t, hash: th_hash } = await topologies.get(tu);
  if (th.vertices * 3 !== a.positions.length) throw new Error(`${url}: ${a.positions.length / 3} vertices, its topology has ${th.vertices}`);
  const morphs = {};
  if (a.facePlain) {
    const I = Uint32Array.from(t.face), D = new Float32Array(I.length * 3);
    for (let k = 0; k < I.length; k++) for (let c = 0; c < 3; c++) D[k * 3 + c] = a.facePlain[k * 3 + c] - a.positions[I[k] * 3 + c];
    morphs.plainFace = { indices: I, deltas: D };
  }
  const mesh = makeMesh({ id: h.id, kind: 'skinned', positions: a.positions, triangles: t.triangles, skin: { joints: t.skinJoints, weights: t.skinWeights, K: 4 }, morphs });
  return makeBody({
    id: h.id, label: h.label, source: h.source, topology: h.topology, skeleton, hash: hashOf([hash, th_hash]),
    mesh, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
    parts: { names: th.parts, weights: t.parts }, eyes: h.eyes, face: t.face, facePlain: a.facePlain,
  });
}

// a body from a mesh and its joints at rest (its rig's floor is the mesh's lowest used vertex)
export function makeBody(o) {
  const { mesh, skeleton } = o;
  let lo = Infinity; for (const i of mesh.used) lo = Math.min(lo, mesh.positions[i * 3 + 1]);
  const rig = makeRig({ skeleton, joints: o.joints, frames: o.frames, floor: lo });
  const b = { ...o, rig, N: mesh.N };
  delete b.joints; delete b.frames;
  b.measures = measure(rig, mesh);
  b.part = name => {
    const p = b.parts.names.indexOf(name); if (p < 0) throw new Error(`no part ${name}`);
    const P = b.parts.names.length; return Float32Array.from({ length: b.N }, (_, i) => b.parts.weights[i * P + p] / 255);
  };
  // the same body with another rest: new vertices and joints; frames as given (src/changes.js makes them)
  b.withRest = ({ positions, joints, frames, label }) => makeBody({
    ...o, label: label ?? o.label, hash: null,   // a changed body is not the stored one: it has no pin of its own
    mesh: makeMesh({ ...mesh, positions: positions ?? mesh.positions }),
    joints: joints ?? rig.joints, frames: frames ?? rig.frames,
  });
  return b;
}

// sizes read off a body at rest (metres), over the vertices its triangles use
export function measure(rig, mesh) {
  const sk = rig.skeleton, J = n => { const j = sk.index[n]; return [rig.joints[j * 3], rig.joints[j * 3 + 1], rig.joints[j * 3 + 2]]; };
  const d = (p, q) => Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]);
  let lo = Infinity, hi = -Infinity;
  for (const i of mesh.used) { const y = mesh.positions[i * 3 + 1]; if (y < lo) lo = y; if (y > hi) hi = y; }
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
