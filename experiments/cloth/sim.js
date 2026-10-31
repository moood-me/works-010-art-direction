// A person in their clothes through a motion: the body played frame by frame (Kimodo's 30 a second), each frame cut
// into small steps where the skin goes evenly from one frame to the next, and every garment, from the innermost out,
// moved as cloth against the body and the garments under it.
import { Pose, skinInto } from './people.js';
import { Cloth, Grid, nearestPerSource, nearestIn, adjacency } from './cloth.js';
import { FABRICS, cut } from './wardrobe.js';

export const STEPS = 16;
// each skin point's limb: 1, 2 the left and right arm (with the hand), 3, 4 the left and right leg, 0 the trunk and head
function limbs(body) {
  const of = body.names.map(n => /^Left(Arm|ForeArm|Hand)/.test(n) ? 1 : /^Right(Arm|ForeArm|Hand)/.test(n) ? 2 : /^Left(Leg|Shin|Foot|Toe)/.test(n) ? 3 : /^Right(Leg|Shin|Foot|Toe)/.test(n) ? 4 : 0);
  const out = new Uint8Array(body.N), acc = new Float32Array(5);
  for (let i = 0; i < body.N; i++) { acc.fill(0); for (let k = 0; k < 4; k++) acc[of[body.joint[i * 4 + k]]] += body.weight[i * 4 + k]; let m = 0; for (let l = 1; l < 5; l++) if (acc[l] > acc[m]) m = l; out[i] = m; }
  return out;
}
// the hand as the cloth meets it: a mitten — its surface 5 mm proud, so the fingers are one solid the cloth can't slip
// between (they are thinner than the cloth's reach)
function mitten(body) {
  const hand = body.names.map(n => /Hand/.test(n)), offs = new Float32Array(body.N);
  for (let i = 0; i < body.N; i++) { let w = 0; for (let k = 0; k < 4; k++) if (hand[body.joint[i * 4 + k]]) w += body.weight[i * 4 + k] / 255; offs[i] = 0.005 * Math.min(1, w * 1.5); }
  return offs;
}              // small steps a frame
const FPS = 30;

// the wind: a steady flow with gusts going through it
export function windField(o) {
  if (!o || !o.speed) return null;
  const dir = [Math.cos(o.dir ?? 0), 0, Math.sin(o.dir ?? 0)], out = [0, 0, 0];
  return (x, y, z, t) => {
    const along = x * dir[0] + z * dir[2];
    const g = 0.7 + 0.3 * Math.sin(t * 1.7 - along * 2.1) * Math.sin(t * 0.63 + y * 1.3) + 0.18 * Math.sin(t * 5.3 - along * 6 + y * 4);
    const s = o.speed * g;
    out[0] = dir[0] * s + 0.25 * o.speed * Math.sin(t * 2.9 + y * 5); out[1] = 0.12 * o.speed * Math.sin(t * 3.7 + along * 3); out[2] = dir[2] * s + 0.25 * o.speed * Math.cos(t * 2.3 + y * 4);
    return out;
  };
}

// the timeline: standing at rest while the clothes settle, then into the motion; motions that go round go on with the
// body carried along (the last frames mixed into the first)
const SETTLE = 0.5, INTO = 0.9, MIX = 10;
export function moment(pose, M, t, cyclic) {
  if (!M || t < SETTLE) return pose.at(null);
  if (t < SETTLE + INTO) { const s = (t - SETTLE) / INTO; return pose.at(M, 0, s * s * (3 - 2 * s)); }
  const g = (t - SETTLE - INTO) * FPS;
  if (!cyclic) return pose.at(M, Math.min(g, M.n - 1));
  const C = M.n - MIX, c = Math.floor(g / C), f = g - c * C;
  const D = [M.hips[C * 3] - M.hips[0], M.hips[C * 3 + 2] - M.hips[2]];
  const now = pose.at(M, f, 1, [D[0] * c, D[1] * c]);
  if (c === 0 || f >= MIX) return now;
  const was = pose.at(M, f + C, 1, [D[0] * (c - 1), D[1] * (c - 1)]), u = f / MIX, s = u * u * (3 - 2 * u);
  return { W: was.W.map((q, j) => q.clone().slerp(now.W[j], s)), hips: was.hips.clone().lerp(now.hips, s), low: was.low + (now.low - was.low) * s };
}

export class Scene {
  // body: people.person(); M: a motion (or null); wear: [{g, fabric}]; data: {garment name → bytes} for MakeHuman's
  constructor(THREE, body, M, wear, data, o = {}) {
    this.THREE = THREE; this.body = body; this.M = M; this.cyclic = !!o.cyclic; this.wind = windField(o.wind);
    this.pose = new Pose(THREE, body); this.t = 0;
    const N = body.N;
    this.bodyA = { pos: new Float32Array(N * 3), nrm: new Float32Array(N * 3) }; this.bodyB = { pos: new Float32Array(N * 3), nrm: new Float32Array(N * 3) };
    this.bodyNow = { pos: new Float32Array(N * 3), nrm: new Float32Array(N * 3), prev: new Float32Array(N * 3), n: N, off: 0, grid: new Grid(0.025, N), adj: adjacency(N, body.tris), move: 0, offs: mitten(body), limb: limbs(body) };
    this.E = this.pose.skin(this.pose.at(null), this.bodyB.pos, this.bodyB.nrm).E;
    this.bodyA.pos.set(this.bodyB.pos); this.bodyA.nrm.set(this.bodyB.nrm);
    // the garments, innermost first
    this.items = wear.map(({ g, fabric }) => ({ c: cut(body, g, data[g]), fabric: { ...FABRICS[fabric], key: fabric } })).sort((a, b) => a.c.layer - b.c.layer);
    this.cloths = this.items.map(({ c, fabric }) => {
      const cl = new Cloth({ name: c.name, pos: c.pos, tris: c.tris, fabric: { ...fabric, self: c.self }, hold: c.hold, skinJ: c.skinJ, skinW: c.skinW });
      cl.sgn = c.sgn; cl.tight = c.tight; cl.flat = c.flat;
      // a garment's sleeves and legs: each point's own limb (where the skin under it was, dressed)
      if (c.tubes) { const L = this.bodyNow.limb; cl.home = Uint8Array.from(c.near, b => L[b]); cl.homeNear = Int32Array.from(c.near); }
      return cl;
    });
    this.targetsA = this.cloths.map(c => Float32Array.from(c.rest)); this.targetsB = this.cloths.map(c => Float32Array.from(c.rest));
    this.prepare();
  }
  // each garment put on: out of the body and of the garments under it before its lengths are taken as its own
  prepare() {
    const B = this.bodyNow; B.pos.set(this.bodyB.pos); B.nrm.set(this.bodyB.nrm); B.prev.set(B.pos); B.grid.build(B.pos, B.n);
    for (let k = 0; k < this.cloths.length; k++) {
      const c = this.cloths[k], src = this.sourcesFor(k);
      // a garment meets one under it where they lie together as dressed (a blouse's hem over a skirt's waistband), not
      // where they only pass each other (its sleeve and the skirt): the one under doesn't feel it, so there it would
      // only be shoved
      c.masks = src.map((S, s) => {
        if (s === 0) return null;
        const m = new Uint8Array(c.n), g = new Grid(0.05, S.n); g.build(S.pos, S.n);
        for (let i = 0; i < c.n; i++) m[i] = nearestIn({ grid: g, pos: S.pos }, c.x[i * 3], c.x[i * 3 + 1], c.x[i * 3 + 2]) >= 0 ? 1 : 0;
        return m;
      });
      for (let it = 0; it < 6; it++) { c.p.set(c.x); c.collide(src, 1 / 480); }
      c.rest.set(c.flat || c.x); c.p.set(c.x); c.v.fill(0);
      const R = c.flat || c.x;
      for (let e = 0; e < c.EL.length; e++) { const a = c.E[e * 2], b = c.E[e * 2 + 1]; c.EL[e] = Math.hypot(R[a * 3] - R[b * 3], R[a * 3 + 1] - R[b * 3 + 1], R[a * 3 + 2] - R[b * 3 + 2]) * c.tight; }
      c.restSkin = Float32Array.from(c.x);
      c.tether(1.04);
      c.normals(); this.publish(c);
    }
  }
  publish(c) { // a garment as a surface others collide with
    c.src ??= { pos: c.x, nrm: c.nrm, rim: c.rim, prev: c.p, n: c.n, off: c.fabric.thick, grid: new Grid(0.025, c.n), adj: adjacency(c.n, c.tris), move: 0 };
    c.rims(); c.src.grid.build(c.x, c.n); c.src.move = c.moved || 0;
  }
  sourcesFor(k) { return [this.bodyNow, ...this.cloths.slice(0, k).map(c => c.src).filter(Boolean)]; }
  // one frame (1/30 s) forward
  frame() {
    const { THREE, pose } = this, h = 1 / FPS / STEPS;
    this.bodyA.pos.set(this.bodyB.pos); this.bodyA.nrm.set(this.bodyB.nrm);
    for (let k = 0; k < this.cloths.length; k++) this.targetsA[k].set(this.targetsB[k]);
    this.t += 1 / FPS;
    const st = moment(pose, this.M, this.t, this.cyclic);
    this.E = pose.skin(st, this.bodyB.pos, this.bodyB.nrm).E;
    this.cloths.forEach((c, k) => skinInto(c.restSkin, null, c.skinJ, c.skinW, 255, this.E, this.targetsB[k], null));
    const B = this.bodyNow, A = this.bodyA, Bb = this.bodyB, n3 = B.n * 3;
    let mv = 0; for (let i = 0; i < n3; i += 3) { const m = (Bb.pos[i] - A.pos[i]) ** 2 + (Bb.pos[i + 1] - A.pos[i + 1]) ** 2 + (Bb.pos[i + 2] - A.pos[i + 2]) ** 2; if (m > mv) mv = m; }
    B.move = Math.sqrt(mv) / STEPS;
    for (let s = 1; s <= STEPS; s++) {
      const u = s / STEPS, t = this.t - 1 / FPS + u / FPS;
      B.prev.set(B.pos);
      for (let i = 0; i < n3; i++) { B.pos[i] = A.pos[i] + (Bb.pos[i] - A.pos[i]) * u; B.nrm[i] = A.nrm[i] + (Bb.nrm[i] - A.nrm[i]) * u; }
      B.grid.build(B.pos, B.n);
      for (let k = 0; k < this.cloths.length; k++) {
        const c = this.cloths[k], ta = this.targetsA[k], tb = this.targetsB[k], T = c.target;
        for (let i = 0; i < T.length; i++) T[i] = ta[i] + (tb[i] - ta[i]) * u;
        c.step(h, this.sourcesFor(k), this.wind, t);
        if (k < this.cloths.length - 1) { c.normals(); this.publish(c); }
      }
    }
    for (const c of this.cloths) c.normals();
  }
  // how much of each garment is inside the body now (points deeper than 2 mm under the skin)
  inside() {
    const B = this.bodyNow, ids = new Int32Array(1);
    return this.cloths.map(c => {
      let bad = 0, worst = 0;
      for (let i = 0; i < c.n; i++) {
        const k = i * 3; nearestBody(B, c.x[k], c.x[k + 1], c.x[k + 2], ids); const b = ids[0]; if (b < 0) continue;
        const d = (c.x[k] - B.pos[b * 3]) * B.nrm[b * 3] + (c.x[k + 1] - B.pos[b * 3 + 1]) * B.nrm[b * 3 + 1] + (c.x[k + 2] - B.pos[b * 3 + 2]) * B.nrm[b * 3 + 2];
        if (d < -0.002) { bad++; worst = Math.min(worst, d); }
      }
      return { name: c.name, bad, worst };
    });
  }
}
function nearestBody(B, x, y, z, out) { nearestPerSource([B], x, y, z, out); }
