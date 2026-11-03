// Deformers: changes of a body's form, each with a strength, composed in the order an author lists them, usable on
// the rest or as a pose layer, on any body, anywhere, at any heading. The deformers themselves are in
// src/deformers/*.js; this is how they are run.
//
// Two kinds, by what they act on:
//   'figure'  the whole figure in its own space — a field that moves every point (and every joint) by where it is and
//             which limb it belongs to: the line of action, squash and stretch, contrapposto, the silhouette by
//             height, the limbs' arcs, taper, straight against curved. On the rest they move the body and its joints
//             once; as a pose layer they move the posed figure every frame, after skinning, in the figure's own space
//             (`space`: 'pelvis' — the pelvis's turn and place now, so a lying figure is bent along its length;
//             'upright' — the pelvis's place and heading, the vertical kept). Every mesh of the figure follows
//             (each by its own limb shares) and the joints too; then the floor step.
//   'skin'    the surface itself — its contours, its masses, its small forms, its proportions: computed on the rest.
//             As a pose layer, what it does at the rest is carried as a morph and weighed in every frame by its
//             strength (so a code layer can animate it); one that moves joints (proportions, caricature) is a rest
//             change only.
//
// A deformer (src/deformers/*.js) is registered as
//   {kind, of: 'figure' | 'skin', joints: true if it moves joints (skin kinds), params: {key: schema}, defaults: {…},
//    field(p, R, S) → move(x, y, z, limbShares, isJoint, out)     ('figure': R the regions of the body at its rest,
//                     S {J: the joints now, in the figure's space; turn(j): joint j's turn from rest there})
//    rest(p, R, ctx) → {positions, joints?}                       ('skin': on the rest; ctx.data from prepare)
//    prepare?(p, E) → data                                        (what it needs loaded: other bodies)}
// p — the change's parameters, complete (defaults filled in), with `strength`.
import { regionsOf, limbsOfMesh } from './regions.js';
import { withRest } from './changes.js';
import { qMul, qConj, qRot, getQ } from './math.js';

export const DEFORMERS = {};
export function register(d) {
  if (DEFORMERS[d.kind]) throw new Error(`deformer ${d.kind} registered twice`);
  if (!['figure', 'skin'].includes(d.of)) throw new Error(`deformer ${d.kind}: of 'figure' or 'skin'`);
  DEFORMERS[d.kind] = d;
}
export const isDeformer = kind => kind in DEFORMERS;
const complete = c => ({ ...DEFORMERS[c.kind].defaults, strength: 1, ...c });

// —— on the rest ——
export async function deformAtRest(body, change, E) {
  const d = DEFORMERS[change.kind], p = complete(change);
  const R = regionsOf(body.mesh, body.rig), rig = body.rig;
  let positions, joints;
  if (d.of === 'figure') {
    positions = Float32Array.from(body.mesh.positions); joints = Float64Array.from(rig.joints);
    const S = { J: Float64Array.from(rig.joints), turn: () => [0, 0, 0, 1] };
    moveAll(d.field(p, R, S), positions, body.mesh, R.limb, joints, R.jlimb);
  } else {
    const data = d.prepare ? await d.prepare(p, E, body) : null;
    ({ positions, joints } = d.rest(p, R, { data, body }));
    positions = keepUnused(body.mesh, positions);
  }
  return withRest(body, { positions, joints: joints ?? rig.joints, frames: change.frames });
}

function moveAll(move, P, mesh, limb, J, jlimb) {
  const out = [0, 0, 0], w = new Float32Array(5);
  for (const i of mesh.used) {
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
// vertices no triangle uses keep their rest
function keepUnused(mesh, P) { for (let i = 0; i < mesh.N; i++) if (!mesh.isUsed[i]) for (let c = 0; c < 3; c++) P[i * 3 + c] = mesh.positions[i * 3 + c]; return P; }

// —— as a pose layer ——
// a 'figure' deformer on every frame: {stage: 'mesh', apply(figure, pose)} — src/figure.js runs these after skinning
export function meshLayer(change, body) {
  const d = DEFORMERS[change.kind], p = complete(change);
  if (d.of !== 'figure') throw new Error(`${change.kind} is a change of the surface: as a pose layer it is a morph (deformAsMorph)`);
  const R = regionsOf(body.mesh, body.rig), rig = body.rig, sk = rig.skeleton, H = sk.index.Hips, J = rig.J;
  const S = { J: new Float64Array(J * 3), Q: new Float64Array(J * 4), turn: j => getQ(S.Q, j) };
  const limbs = new WeakMap(), a = [0, 0, 0], b = [0, 0, 0];
  const space = p.space ?? 'pelvis';
  return {
    stage: 'mesh', kind: change.kind,
    apply(fig, pose) {
      // the figure's space: rest-like coordinates around the pelvis — x_local = Rᵀ (x − pelvis now) + pelvis at rest
      let r = getQ(pose.Q, H);
      if (space === 'upright') { const f = qRot(r, [0, 0, 1]), yaw = Math.atan2(f[0], f[2]); r = [0, Math.sin(yaw / 2), 0, Math.cos(yaw / 2)]; }
      const ri = qConj(r), o = [pose.P[H * 3], pose.P[H * 3 + 1], pose.P[H * 3 + 2]], h = [rig.joints[H * 3], rig.joints[H * 3 + 1], rig.joints[H * 3 + 2]];
      const toLocal = (x, y, z, out) => { qRot(ri, [x - o[0], y - o[1], z - o[2]], out); out[0] += h[0]; out[1] += h[1]; out[2] += h[2]; return out; };
      const toWorld = (x, y, z, out) => { qRot(r, [x - h[0], y - h[1], z - h[2]], out); out[0] += o[0]; out[1] += o[1]; out[2] += o[2]; return out; };
      for (let j = 0; j < J; j++) {
        toLocal(pose.P[j * 3], pose.P[j * 3 + 1], pose.P[j * 3 + 2], a); S.J[j * 3] = a[0]; S.J[j * 3 + 1] = a[1]; S.J[j * 3 + 2] = a[2];
        const q = qMul(ri, getQ(pose.Q, j)); for (let c = 0; c < 4; c++) S.Q[j * 4 + c] = q[c];
      }
      const move = d.field(p, R, S), w = new Float32Array(5);
      for (const o2 of fig.outputs) {
        let L = limbs.get(o2.mesh); if (!L) limbs.set(o2.mesh, L = o2.mesh === body.mesh ? R.limb : limbsOfMesh(o2.mesh, sk));
        const P = o2.positions, u = o2.mesh.used;
        for (let k = 0; k < u.length; k++) {
          const i = u[k];
          for (let c = 0; c < 5; c++) w[c] = L[i * 5 + c];
          toLocal(P[i * 3], P[i * 3 + 1], P[i * 3 + 2], a); move(a[0], a[1], a[2], w, false, b); toWorld(b[0], b[1], b[2], a);
          P[i * 3] = a[0]; P[i * 3 + 1] = a[1]; P[i * 3 + 2] = a[2];
        }
      }
      for (let j = 0; j < J; j++) {
        w.fill(0); w[R.jlimb[j]] = 1;
        move(S.J[j * 3], S.J[j * 3 + 1], S.J[j * 3 + 2], w, true, b); toWorld(b[0], b[1], b[2], a);
        pose.P[j * 3] = a[0]; pose.P[j * 3 + 1] = a[1]; pose.P[j * 3 + 2] = a[2];
      }
    },
  };
}
// a 'skin' deformer as a pose layer: what it does to the rest, as a morph of the body's mesh (weighed by strength)
export async function deformAsMorph(body, change, E) {
  const d = DEFORMERS[change.kind];
  if (d.of !== 'skin') throw new Error(`${change.kind} moves the figure: as a pose layer it is a mesh layer (meshLayer)`);
  if (d.joints) throw new Error(`${change.kind} moves joints: it is a change of the rest only (rest: [{kind: "${change.kind}", …, frames}])`);
  const p = { ...complete(change), strength: 1 }, R = regionsOf(body.mesh, body.rig);
  const data = d.prepare ? await d.prepare(p, E, body) : null;
  const { positions } = d.rest(p, R, { data, body }), P0 = body.mesh.positions, idx = [], del = [];
  for (const i of body.mesh.used) {
    const dx = positions[i * 3] - P0[i * 3], dy = positions[i * 3 + 1] - P0[i * 3 + 1], dz = positions[i * 3 + 2] - P0[i * 3 + 2];
    if (Math.abs(dx) + Math.abs(dy) + Math.abs(dz) > 1e-7) { idx.push(i); del.push(dx, dy, dz); }
  }
  return { indices: Uint32Array.from(idx), deltas: Float32Array.from(del) };
}
