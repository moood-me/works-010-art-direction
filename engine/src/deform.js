// Deformers: changes of a body's form, each with a strength, composed in the order an author lists them, usable on
// the rest or as a pose layer, on any body, anywhere, at any heading. The deformers themselves are in
// src/deformers/*.js; this is how they are run.
//
// Two kinds, by what they act on at the rest:
//   'figure'  the whole figure in its own space — a field that moves every point (and every joint) by where it is and
//             which limb it belongs to: the line of action, squash and stretch, contrapposto, the silhouette by
//             height, the limbs' arcs, taper, straight against curved
//   'skin'    the surface itself — its contours, its masses, its small forms, its proportions, the sign
// On the rest either moves the body and its joints once (src/changes.js: frames kept or turned), and never turns a
// triangle over (where it would fold the skin, it goes only as far as it can). As a pose layer:
//   a change of the pose (a deformer with `turns`: the line of action, contrapposto) — turns of the joints each
//             frame, so every bone keeps its length; the pelvis stays where Kimodo put it and the feet too (a layer
//             that turns the pelvis puts the legs back on their feet, src/pose.js: keepFeet); `space` says in which
//             frame it bends: 'pelvis' (its turn now: a lying figure bends along its length) or 'upright' (its
//             heading only, the vertical kept)
//   a change of the form (every other) — its rest change, weighed in every frame (src/figure.js): the vertices, the
//             centres of rotation and the joints' rest places moved as the same change on the rest moves them, then
//             skinned and posed as the rest is — a rest change carried through skinning, never a field over the posed
//             figure, so bones stay as long as the change makes them and the feet stand where the motion puts them.
//             Its weight is 1 unless a code layer before it sets ctx.weights[name]; at weight 1 the figure is the
//             one the same change on the rest (frames kept) gives. A change that gives its own skin weights (the sign)
//             is a change of the rest only.
//
// A deformer (src/deformers/*.js) is registered as
//   {kind, of: 'figure' | 'skin', params: {key: schema}, defaults: {…},
//    field(p, R) → move(x, y, z, limbShares, isJoint, out)     ('figure': R the regions of the body at its rest)
//    rest(p, R, ctx) → {positions, joints?, skin?}             ('skin': on the rest; ctx.data from prepare; skin:
//                                                               {joints, weights} — its own skin weights)
//    prepare?(p, E, body) → data                               (what it needs loaded: other bodies)
//    turns?(p, R) → apply(pose, ctx)                           (as a pose layer: turns of the joints)
//    restOnly?: true                                           (refused as a pose layer)
//    ownFolds?: true                                           (its folds are its own to ease: src/head/wrap.js)}
// p — the change's parameters, complete (defaults filled in), with `strength`.
import { regionsOf, limbsOfMesh, unfold } from './regions.js';
import { withRest } from './changes.js';
import { keepUnused } from './mesh.js';
import { centresOf } from './skin.js';

export const DEFORMERS = {};
export function register(d) {
  if (DEFORMERS[d.kind]) throw new Error(`deformer ${d.kind} registered twice`);
  if (!['figure', 'skin'].includes(d.of)) throw new Error(`deformer ${d.kind}: of 'figure' or 'skin'`);
  if ((d.of === 'figure') !== (typeof d.field === 'function') || (d.of === 'skin') !== (typeof d.rest === 'function')) throw new Error(`deformer ${d.kind}: a field ('figure') or a rest ('skin')`);
  DEFORMERS[d.kind] = d;
}
export const isDeformer = kind => kind in DEFORMERS;
export const complete = c => ({ ...DEFORMERS[c.kind].defaults, strength: 1, ...c });
// how a deformer goes as a pose layer: 'turns', 'rest' (its rest change weighed in), or null (a change of the rest only)
export const layerOf = kind => { const d = DEFORMERS[kind]; return d.restOnly ? null : d.turns ? 'turns' : 'rest'; };

// —— on the rest ——
export async function deformAtRest(body, change, E) {
  const d = DEFORMERS[change.kind], p = complete(change), rig = body.rig;
  let positions, joints, skin;
  const R = regionsOf(body.mesh, rig);
  if (d.of === 'figure') {
    positions = Float32Array.from(body.mesh.positions); joints = Float64Array.from(rig.joints);
    moveAll(d.field(p, R), positions, body.mesh, R.limb, joints, R.jlimb);
  } else {
    const data = d.prepare ? await d.prepare(p, E, body) : null;
    ({ positions, joints, skin } = d.rest(p, R, { data, body }));
    positions = keepUnused(body.mesh, positions);
  }
  // no triangle turned over: where a change would fold the skin it goes only as far as it can (src/regions.js: unfold).
  // The sign is the exception: it gathers a hand's skin onto a ball, folded there by its nature
  // (a wrap onto a designed form sees its own folds against the form, not against the body it starts from: ownFolds)
  if (!d.restOnly && !d.ownFolds) positions = unfold(R, body.mesh.positions, positions);
  return withRest(body, { positions, joints: joints ?? rig.joints, skin, frames: change.frames });
}

// a field over every used vertex (by its limb shares) and every joint (by its limb), in place
export function moveAll(move, P, mesh, limb, J, jlimb) {
  const out = [0, 0, 0], w = new Float32Array(5), u = mesh.used;
  for (let k = 0; k < u.length; k++) {
    const i = u[k];
    for (let c = 0; c < 5; c++) w[c] = limb[i * 5 + c];
    move(P[i * 3], P[i * 3 + 1], P[i * 3 + 2], w, false, out);
    P[i * 3] = out[0]; P[i * 3 + 1] = out[1]; P[i * 3 + 2] = out[2];
  }
  if (!J) return;
  for (let j = 0; j < jlimb.length; j++) {
    w.fill(0); w[jlimb[j]] = 1;
    move(J[j * 3], J[j * 3 + 1], J[j * 3 + 2], w, true, out);
    J[j * 3] = out[0]; J[j * 3 + 1] = out[1]; J[j * 3 + 2] = out[2];
  }
}

// —— as a pose layer ——
// a change of the pose: {kind: 'code', name, apply(pose, ctx)} (src/figure.js runs it in its place among the layers)
export function turnLayer(change, body) {
  const d = DEFORMERS[change.kind], p = complete(change);
  if (!d.turns) throw new Error(`${change.kind} is a change of the form: as a pose layer it is its rest change weighed in (restLayer)`);
  return { kind: 'code', name: change.kind, apply: d.turns(p, regionsOf(body.mesh, body.rig)) };
}
// a change of the form: what it does to the rest `from` (the body with the layers before it made at their weight 1),
// giving `to` — {kind: 'rest', name, joints (J×3 deltas), body: {indices, deltas, centres}, forMesh(mesh, rest, cor,
// skeleton) → the same for another mesh or null}. The body's own
// mesh moves as `to` has it, its centres of rotation as `to`'s are; another skinned mesh (clothes) by the same
// field, if the deformer is one of the figure (a change of the surface is the body's own).
export function restLayer(name, change, from, to, sigma) {
  const d = DEFORMERS[change.kind];
  if (!layerOf(change.kind)) throw new Error(`${change.kind} gives its own skin weights: it is a change of the rest only (rest: [{kind: "${change.kind}", …, frames}])`);
  const dJ = Float64Array.from(to.rig.joints, (v, i) => v - from.rig.joints[i]);
  const R = d.of === 'figure' ? regionsOf(from.mesh, from.rig) : null, move = R ? d.field(complete(change), R) : null;
  // the body's mesh: the vertices and centres as the changed rest has them
  const c0 = centresOf(from.mesh, sigma), c1 = centresOf(to.mesh, sigma);
  const body = { ...sparse(from.mesh, from.mesh.positions, to.mesh.positions), centres: Float64Array.from(c1.cor, (v, i) => v - c0.cor[i]) };
  const layer = { kind: 'rest', name, deformer: change.kind, joints: dJ, body, meshes: new WeakMap() };
  // another mesh: moved by the field at its rest (the vertices, and its centres where it has them)
  layer.forMesh = (mesh, rest, cor, sk) => {
    if (layer.meshes.has(mesh)) return layer.meshes.get(mesh);
    let m = null;
    if (move) {
      const P = Float32Array.from(rest), limb = limbsOfMesh(mesh, sk);
      moveAll(move, P, mesh, limb, null, null);
      m = sparse(mesh, rest, P);
      if (cor) { const C = Float32Array.from(cor), CP = Float32Array.from(C); moveAll(move, CP, mesh, limb, null, null); m.centres = Float64Array.from(CP, (v, i) => v - C[i]); }
    }
    layer.meshes.set(mesh, m);
    return m;
  };
  return layer;
}
// the vertices that moved, and by how much
function sparse(mesh, a, b) {
  const idx = [], del = [];
  for (const i of mesh.used) {
    const dx = b[i * 3] - a[i * 3], dy = b[i * 3 + 1] - a[i * 3 + 1], dz = b[i * 3 + 2] - a[i * 3 + 2];
    if (Math.abs(dx) + Math.abs(dy) + Math.abs(dz) > 1e-7) { idx.push(i); del.push(dx, dy, dz); }
  }
  return { indices: Uint32Array.from(idx), deltas: Float32Array.from(del) };
}
