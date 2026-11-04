// A figure: a rig moving through a clip, with every mesh it carries — the whole way from Kimodo's data to the skins.
// Each frame, in this order:
//   1. the pose: the clip's moment retargeted onto the rig (src/retarget.js), or the rig at rest
//   2. pose layers, in the order they are listed, each seeing what the ones before it did:
//        turns (src/layers.js, a deformer's turns, the character's code: {kind: 'code', apply(pose, ctx)}) — the
//          places rebuilt after each;
//        changes of the rest ({kind: 'rest'}: a deformer's rest change weighed in, src/deform.js: restLayer) — the
//          joints' rest places this frame (ctx.rest) moved by its weight (ctx.weights[name], 1 if no code layer before
//          it set one), the places rebuilt down the bones as they now are;
//        morphs ({kind: 'morph'}) — weights of a mesh's morphs this frame
//      then, if the rest changed, the pelvis set on Kimodo's path again by the hip height of this frame's rest
//   3. placed where the figure stands ({position, heading})
//   4. every mesh off that one pose (src/mesh.js): skinned — its rest with this frame's morphs and changes of the rest
//      weighed in, about this frame's joints and centres of rotation; rigid; rebuilt (sweeps)
//   5. the floor (motion.floor 'lowest'): the lowest of all meshes that count for it, over the vertices their triangles
//      use, set as high as the pose says — everything (meshes and pose) moved up by that one shift (pose.shift)
//   6. normals; where a mesh shades by a designed form (mesh.shading: a head's light, src/head/head.js; hair), its
//      normals are that form's, turned as the skin's joints turned it, weighed in by its weights (and its directions
//      along the surface, mesh.shading.tangents: hair's strands, turned the same, into output.tangents)
//   7. attached meshes laid on their host (a feature as volume on the skin), and their normals
// `frame(clip, t, pose?)` does that for a moment, into the pose it is given (or a new one) and into the meshes'
// buffers (figure.outputs) — it keeps nothing between calls. `step(clip, t, {loop})` is the stateful frame for
// simulations (hair, cloth): it keeps the current and the previous pose (figure.pose, figure.previous: valid until the
// next step; clone() to keep one) and the time step; it resets on the first step, a new clip, a jump back (a scrub) or
// a jump ahead of more than `maxGap` frames; `loop` says this step goes on across the clip's end, the clip begun again
// (t is its new moment: the time goes on, the body jumps to the clip's start and the simulations carry on from where
// they were on it). Then the body's solids (src/solids.js: what simulations meet, made when one asks for them) are
// updated once, and each simulation runs with {figure, pose, previous, dt, reset, jump, t, solids}; simulations run
// after the floor and don't count for it.
import { makeRetarget, place } from './retarget.js';
import { Skinner } from './skin.js';
import { morphed, normalsOf } from './mesh.js';
import { Pose, build, hipOf } from './pose.js';
import { LAYERS, NO_REBUILD } from './layers.js';
import { makeSolids } from './solids.js';
import { newSample } from './motion.js';
import { qRot3 } from './math.js';

export class Figure {
  // rig; meshes: [{mesh, name?, skinning?: {method, sigma, seam}}] (the first is the body's, named 'body'); layers: resolved pose layers;
  // body (for layers that need a body: armsOutOfHead); floor: 'lowest' | 'pelvis'; place: {position, heading}
  constructor({ rig, meshes, layers = [], body = null, floor = 'lowest', place: where = {} }) {
    if (!['lowest', 'pelvis'].includes(floor)) throw new Error(`motion.floor "${floor}"`);
    for (const l of layers) {
      if (l.kind === 'code' && typeof l.apply !== 'function') throw new Error('a code layer applies itself: {kind: "code", apply(pose, ctx)}');
      if (l.kind === 'rest' && !(l.joints && l.body && l.forMesh)) throw new Error('a change of the rest as a layer is made by src/deform.js: restLayer');
      if (l.kind !== 'code' && l.kind !== 'rest' && !LAYERS[l.kind]) throw new Error(`no pose layer "${l.kind}"`);
    }
    Object.assign(this, { rig, body, layers, floorMode: floor, maxGap: 3, simulations: [], driven: new Set() });
    this.restLayers = layers.filter(l => l.kind === 'rest');
    this.place = { position: [0, 0, 0], heading: 0, ...where };
    this.retarget = makeRetarget(rig);
    this.sample = newSample(rig.J);
    this.outputs = [];
    for (const m of meshes) this.addMesh(m.mesh, m);
    this.pose = new Pose(rig.J); this.previous = new Pose(rig.J); this.state = null;
    // rest: the joints' rest places this frame; weights: of the changes of the rest (by name; a code layer may set
    // them); applied: the weight each change of the rest was taken at this frame (in this.restLayers' order)
    this.ctx = { rig, body, t: 0, morphs: {}, weights: {}, expressions: {}, rest: Float64Array.from(rig.joints), applied: new Float64Array(this.restLayers.length),
      hip: [0, 0, 0], pose: null, build: () => build(this.ctx.pose, rig, this.ctx.hip, this.ctx.rest) };
  }
  // another mesh off the same pose (a head, a piece, a garment, a sweep); name: what morph layers call it ('body' for
  // the body's own)
  addMesh(mesh, { skinning = {}, name = mesh.id } = {}) {
    if (this.outputs.some(o => o.name === name)) throw new Error(`a figure with two meshes named "${name}"`);
    const o = { name, mesh, positions: new Float32Array(mesh.N * 3), normals: new Float32Array(mesh.N * 3) };
    // (a mesh shaded by a designed form that carries directions along it too — hair's strands — has them turned the same)
    if (mesh.shading?.tangents) o.tangents = new Float32Array(mesh.N * 3);
    if (mesh.kind === 'skinned') {
      o.skinner = new Skinner(mesh, this.rig, skinning);
      // what each change of the rest does to this mesh: the body's own as the change made it, another's by its field
      const sk = this.rig.skeleton, rest = Float32Array.from(mesh.positions), cor = o.skinner.cor ? Float32Array.from(o.skinner.cor) : null;
      // (a mesh that follows its host's rest takes the changes of the rest as the host's vertices it is bound to do)
      o.changes = mesh.follow ? [] : this.restLayers.map(l => {
        const m = name === 'body' ? l.body : l.forMesh(mesh, rest, cor, sk);
        if (m) for (let k = 0; k < m.indices.length; k++) for (let c = 0; c < 3; c++) rest[m.indices[k] * 3 + c] += m.deltas[k * 3 + c];
        if (m?.centres && cor) for (let i = 0; i < cor.length; i++) cor[i] += m.centres[i];
        return m;
      });
      if (Object.keys(mesh.morphs).length || o.changes.some(Boolean) || mesh.follow) o.rest = new Float32Array(mesh.positions.length);
      if (mesh.follow) { o.host = this.outputs.find(h => h.name === mesh.follow.host); if (!o.host) throw new Error(`${mesh.id}: follows "${mesh.follow.host}", added after it`); }
      if (o.skinner.cor && o.changes.some(m => m?.centres)) o.cor = new Float64Array(o.skinner.cor.length);
    }
    this.outputs.push(o);
    return o;
  }
  removeMesh(mesh) { this.outputs = this.outputs.filter(o => o.mesh !== mesh); }
  get positions() { return this.outputs[0].positions; }
  get normals() { return this.outputs[0].normals; }
  // a simulation, and the meshes it writes on each step (sim.outputs: what the step's frame leaves to it)
  addSimulation(sim) { this.simulations.push(sim); for (const o of sim.outputs || []) this.driven.add(o); return sim; }
  // the body as hair and clothes meet it: the head's shape, the skin between two frames, its inside (src/solids.js)
  solids() { return (this._solids ??= makeSolids(this)); }

  // the pose at moment t (frames) of a clip (null: at rest), before the meshes: steps 1–3
  poseAt(clip, t, pose = new Pose(this.rig.J)) {
    const sk = this.rig.skeleton, ctx = this.ctx, rest = ctx.rest;
    if (clip) this.retarget.pose(clip.sample(t, this.sample), pose); else Pose.rest(this.rig, pose);
    rest.set(this.rig.joints); ctx.applied.fill(0);
    ctx.pose = pose; ctx.t = t; ctx.morphs = {}; ctx.weights = {}; ctx.expressions = {}; ctx.hip = hipOf(pose, sk);
    let changed = false, r = 0;
    for (const l of this.layers) {
      if (l.kind === 'rest') {
        const w = ctx.weights[l.name] ?? 1; ctx.applied[r++] = w;
        if (w) { const d = l.joints; for (let i = 0; i < rest.length; i++) rest[i] += w * d[i]; changed = true; ctx.build(); }
        continue;
      }
      if (l.kind === 'code') l.apply(pose, ctx); else LAYERS[l.kind](pose, ctx, l);
      if (!NO_REBUILD.has(l.kind)) ctx.build();
    }
    if (changed) {
      if (clip) { const h = this.retarget.root(this.sample, pose, rest); ctx.hip[0] = h[0]; ctx.hip[1] = h[1]; ctx.hip[2] = h[2]; }
      else { const H = sk.index.Hips; ctx.hip[0] = rest[H * 3]; ctx.hip[1] = rest[H * 3 + 1]; ctx.hip[2] = rest[H * 3 + 2]; ctx.build(); }
    }
    return place(pose, this.rig, this.place);
  }

  // the figure at moment t: the pose (into `pose`), every mesh, the floor, normals — but those in `skip` (the step's
  // simulations write theirs after it)
  frame(clip, t, pose = new Pose(this.rig.J), skip = null) {
    this.poseAt(clip, t, pose);
    const { morphs, rest, applied } = this.ctx;
    for (const o of this.outputs) {
      const m = o.mesh; if (skip?.has(o)) continue;
      if (m.kind === 'skinned') o.skinner.skin(pose, o.positions, m.follow ? followed(o) : o.rest ? restOf(o, morphs[o.name] || {}, applied) : m.positions, rest, o.cor ? centresOf(o, applied) : o.skinner.cor);
      else if (m.kind === 'rigid') rigid(o, pose, this.rig);
      else if (m.build) m.build(pose, this.rig, o.positions);
    }
    pose.shift = 0;
    if (this.floorMode === 'lowest') {
      let lo = Infinity;
      for (const o of this.outputs) if (o.mesh.floor && o.mesh.kind !== 'attached') { const u = o.mesh.used, p = o.positions; for (let k = 0; k < u.length; k++) { const y = p[u[k] * 3 + 1]; if (y < lo) lo = y; } }
      if (lo < Infinity) {
        const shift = pose.floor - lo;
        for (const o of this.outputs) { if (o.mesh.kind === 'attached' || skip?.has(o)) continue; const u = o.mesh.used, p = o.positions; for (let k = 0; k < u.length; k++) p[u[k] * 3 + 1] += shift; }
        for (let j = 0; j < this.rig.J; j++) pose.P[j * 3 + 1] += shift;
        pose.shift = shift;
      }
    }
    // (a mesh shaded wholly by its design takes no normals of its own)
    for (const o of this.outputs) if (o.mesh.kind !== 'attached' && !skip?.has(o)) { if (!o.mesh.shading?.whole) normalsOf(o.positions, o.mesh.triangles, o.normals, o.mesh.used); if (o.mesh.shading) shadeByForm(o, pose); }
    for (const o of this.outputs) if (o.mesh.kind === 'attached') { attach(o, this.outputs.find(h => h.name === o.mesh.host)); normalsOf(o.positions, o.mesh.triangles, o.normals, o.mesh.used); }
    return pose;
  }

  // the stateful frame (see the top)
  step(clip, t, { loop = false } = {}) {
    const s = this.state, fps = clip ? clip.fps : 30, on = loop && s && s.clip === clip && clip;
    const reset = !s || s.clip !== clip || (!on && (t < s.t || t - s.t > this.maxGap));
    const dt = reset ? 0 : on ? (clip.frames - 1 - s.t + t) / fps : (t - s.t) / fps;
    [this.pose, this.previous] = [this.previous, this.pose];
    this.frame(clip, t, this.pose, this.driven);
    if (reset || on) this.previous.copy(this.pose);
    this.state = { clip, t };
    const solids = this._solids ?? null, jump = !reset && !!on;
    if (solids) solids.update(this.previous, this.pose, reset ? 'reset' : jump ? 'jump' : 'go', dt);
    for (const sim of this.simulations) sim.step({ figure: this, pose: this.pose, previous: this.previous, dt, reset, jump, t, solids });
    return this.pose;
  }
  reset() { this.state = null; }

  // the box around everything drawn (the used vertices of every mesh)
  bounds() {
    const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
    for (const o of this.outputs) { const u = o.mesh.used, p = o.positions; for (let k = 0; k < u.length; k++) for (let c = 0; c < 3; c++) { const v = p[u[k] * 3 + c]; if (v < lo[c]) lo[c] = v; if (v > hi[c]) hi[c] = v; } }
    return { min: lo, max: hi, center: lo.map((v, c) => (v + hi[c]) / 2), size: lo.map((v, c) => hi[c] - v) };
  }
  // where the pelvis goes over a clip, on this figure (for drawing the path)
  path(clip, step = 1) {
    const out = [], pose = new Pose(this.rig.J);
    for (let t = 0; t < clip.frames; t += step) { this.poseAt(clip, t, pose); out.push([pose.P[0], pose.P[2]]); }
    return out;
  }
}

// a skinned mesh's rest this frame: its morphs and the changes of the rest weighed in (into o.rest); o.moved: whether
// anything moved it
function restOf(o, weights, applied) {
  const P = morphed(o.mesh, weights, o.rest);
  o.moved = Object.values(weights).some(Boolean);
  for (let n = 0; n < o.changes.length; n++) {
    const m = o.changes[n], w = applied[n]; if (!m || !w) continue;
    o.moved = true;
    const I = m.indices, D = m.deltas;
    for (let k = 0; k < I.length; k++) { const i = I[k] * 3; P[i] += w * D[k * 3]; P[i + 1] += w * D[k * 3 + 1]; P[i + 2] += w * D[k * 3 + 2]; }
  }
  return P;
}
// a mesh that follows its host's rest: its rest carried by the affine change that best carries the host's vertices it
// is bound to (weighed) from their rest to this frame's — their middle's move, and how they grew, narrowed or leaned
// (a bigger head, a squashed one, an expression's morph under a nose) — so it stays whole and on them (into o.rest)
function followed(o) {
  const m = o.mesh, { idx, w } = m.follow, P = m.positions;
  if (!o.host.moved) return P;   // (the host's rest is its own this frame)
  const H = o.host.rest, H0 = o.host.mesh.positions, f = o.fit ??= fitOf(idx, w, H0), c1 = [0, 0, 0], C = new Float64Array(9);
  for (let k = 0; k < idx.length; k++) { const j = idx[k] * 3; for (let c = 0; c < 3; c++) c1[c] += w[k] * H[j + c] / f.s; }
  for (let k = 0; k < idx.length; k++) { const j = idx[k] * 3; for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) C[r * 3 + c] += w[k] * (H[j + r] - c1[r]) * (H0[j + c] - f.c0[c]); }
  const A = new Float64Array(9); for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) for (let k = 0; k < 3; k++) A[r * 3 + c] += C[r * 3 + k] * f.inv[k * 3 + c];
  const R = o.rest;
  for (const i of m.used) { const x = P[i * 3] - f.c0[0], y = P[i * 3 + 1] - f.c0[1], z = P[i * 3 + 2] - f.c0[2]; for (let r = 0; r < 3; r++) R[i * 3 + r] = c1[r] + A[r * 3] * x + A[r * 3 + 1] * y + A[r * 3 + 2] * z; }
  return R;
}
// what of the bound vertices' rest the fit needs: their weighed middle, the weights' sum, the inverse of their spread
function fitOf(idx, w, H0) {
  const c0 = [0, 0, 0]; let s = 0; for (let k = 0; k < idx.length; k++) { s += w[k]; for (let c = 0; c < 3; c++) c0[c] += w[k] * H0[idx[k] * 3 + c]; } for (let c = 0; c < 3; c++) c0[c] /= s;
  const M = new Float64Array(9); for (let k = 0; k < idx.length; k++) { const j = idx[k] * 3; for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) M[r * 3 + c] += w[k] * (H0[j + r] - c0[r]) * (H0[j + c] - c0[c]); }
  const [a, b, c, d, e, g, h, i, l] = M, det = a * (e * l - g * i) - b * (d * l - g * h) + c * (d * i - e * h);
  const inv = Float64Array.from([e * l - g * i, c * i - b * l, b * g - c * e, g * h - d * l, a * l - c * h, c * d - a * g, d * i - e * h, b * h - a * i, a * e - b * d], v => v / det);
  return { c0, s, inv };
}
// its centres of rotation this frame (into o.cor)
function centresOf(o, applied) {
  const C = o.cor; C.set(o.skinner.cor);
  for (let n = 0; n < o.changes.length; n++) {
    const m = o.changes[n], w = applied[n]; if (!m?.centres || !w) continue;
    const D = m.centres; for (let i = 0; i < C.length; i++) C[i] += w * D[i];
  }
  return C;
}
// a rigid mesh: its joint's transform from the rig's rest to now, on its rest vertices — it keeps its place against
// its joint as it was made, whatever a change of the rest does to where that joint is
function rigid(o, pose, rig) {
  const m = o.mesh, j = m.joint, q = [pose.Q[j * 4], pose.Q[j * 4 + 1], pose.Q[j * 4 + 2], pose.Q[j * 4 + 3]], [x, y, z, w] = q;
  const R = [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)];
  const r = [rig.joints[j * 3], rig.joints[j * 3 + 1], rig.joints[j * 3 + 2]], P = m.positions, out = o.positions;
  for (const i of m.used) {
    const a = P[i * 3] - r[0], b = P[i * 3 + 1] - r[1], c = P[i * 3 + 2] - r[2];
    out[i * 3] = R[0] * a + R[1] * b + R[2] * c + pose.P[j * 3];
    out[i * 3 + 1] = R[3] * a + R[4] * b + R[5] * c + pose.P[j * 3 + 1];
    out[i * 3 + 2] = R[6] * a + R[7] * b + R[8] * c + pose.P[j * 3 + 2];
  }
}

// a mesh shaded by a designed form: each vertex's normal there is the form's normal at its rest, turned as its joints
// turned (their turns blended by its skin's weights), weighed in by its weight; its directions along it the same
function shadeByForm(o, pose) {
  const m = o.mesh, { normals: D, weight: W, tangents: TD } = m.shading, K = m.skin.K, SJ = m.skin.joints, SW = m.skin.weights, Q = pose.Q, n = o.normals, T = o.tangents, r = [0, 0, 0];
  const qs = o.qs ??= Array.from({ length: Q.length / 4 }, () => [0, 0, 0, 1]);
  for (let j = 0; j < qs.length; j++) for (let k = 0; k < 4; k++) qs[j][k] = Q[j * 4 + k];
  for (const i of m.used) {
    const w = W[i];
    for (let pass = TD ? 0 : 1; pass < 2; pass++) {
      if (pass && !w) continue;
      const V = pass ? D : TD; let x = 0, y = 0, z = 0;
      for (let k = 0; k < K; k++) { const a = SW[i * K + k]; if (!a) continue; qRot3(qs[SJ[i * K + k]], V[i * 3], V[i * 3 + 1], V[i * 3 + 2], r); x += a * r[0]; y += a * r[1]; z += a * r[2]; }
      const l = Math.hypot(x, y, z) || 1;
      if (!pass) { T[i * 3] = x / l; T[i * 3 + 1] = y / l; T[i * 3 + 2] = z / l; continue; }
      x = n[i * 3] + (x / l - n[i * 3]) * w; y = n[i * 3 + 1] + (y / l - n[i * 3 + 1]) * w; z = n[i * 3 + 2] + (z / l - n[i * 3 + 2]) * w;
      const L = Math.hypot(x, y, z) || 1; n[i * 3] = x / L; n[i * 3 + 1] = y / L; n[i * 3 + 2] = z / L;
    }
  }
}
// an attached mesh on its host this frame: each vertex at its place in its host triangle, lifted along the normal there
function attach(o, host) {
  if (!host) throw new Error(`${o.mesh.id}: no mesh "${o.mesh.host}" to lay it on`);
  const m = o.mesh, T = host.mesh.triangles, P = host.positions, N = host.normals, out = o.positions;
  for (let v = 0; v < m.N; v++) {
    const t = m.tri[v] * 3, a = T[t] * 3, b = T[t + 1] * 3, c = T[t + 2] * 3, u = m.bary[v * 3], w = m.bary[v * 3 + 1], s = m.bary[v * 3 + 2];
    let nx = u * N[a] + w * N[b] + s * N[c], ny = u * N[a + 1] + w * N[b + 1] + s * N[c + 1], nz = u * N[a + 2] + w * N[b + 2] + s * N[c + 2];
    const l = Math.hypot(nx, ny, nz) || 1, h = m.lift[v] / l;
    out[v * 3] = u * P[a] + w * P[b] + s * P[c] + nx * h; out[v * 3 + 1] = u * P[a + 1] + w * P[b + 1] + s * P[c + 1] + ny * h; out[v * 3 + 2] = u * P[a + 2] + w * P[b + 2] + s * P[c + 2] + nz * h;
  }
}
