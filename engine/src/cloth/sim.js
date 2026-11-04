// Clothes in motion (О3's cloth, experiments/cloth/cloth.js and sim.js, carried onto the engine's figure; this is the
// source now): every garment a sheet of its fabric, moved by position-based dynamics with compliance (XPBD, Macklin et
// al. 2016) in small steps — many small steps of one pass each, as Macklin et al. 2019 found best. A figure's step
// (src/figure.js) runs it after the floor, in small steps of 1/H s, always the same whatever the frame's step (what a
// frame leaves over is carried to the next: the cloth moves the same at 20, 30, 60 or 144 frames a second); all the
// garments of a figure in one simulation, the innermost first in each small step, so each meets the ones under it as
// they are then. In each small step, for each garment:
// - gravity, the fabric's own damping, and the air (the wind — the hair's presets, src/wind.js — less the cloth's own
//   velocity, pressing on each point as its surface faces the flow: light fabrics fly, heavy ones barely move);
// - lengths: each edge holds against stretching with the fabric's stretch (N/m) and gives way more easily when pushed
//   together (its compress share), so the cloth folds rather than shrinks; solved before and after bending, or bending
//   would stretch it;
// - bending: the angle at each inner edge held toward flat with the fabric's bending rigidity B (N·m, Kawabata's; per
//   hinge k = 3·B·e/(h₁+h₂)) — chiffon's bending length is about a centimetre, denim's three, tweed's four;
// - what holds it on: its waistband or neckline (and a long sleeve's cuff, lightly) pulled to where the skin carries it,
//   as an elastic; every point no farther from its nearest held point than the cloth between them is long (tethers);
// - its designed silhouette (src/cloth/shape.js), when it has one: every point pulled toward the designed form as the
//   body carries it (fitted parts by the skin, what hangs below the hips by the pelvis), as firmly as the garment's
//   strength says — 1 a stiff petticoat holding the bell, 0 cloth hanging freely as it was cut;
// - its own points kept apart where it can fold onto itself (a skirt, a dress, trousers);
// - the body: the figure's solids (src/solids.js) — its skin between the frames at that small step's moment, its inside
//   deep in, the head's designed form — with the fabric's thickness and friction against the skin's own motion; a
//   sleeve or a trouser leg belongs to its limb: where another part of the body is nearer (an arm by the side, legs
//   together) it also keeps outside its own limb, which has the last word; the garments under it, where they lie
//   together as dressed (a blouse's hem over a skirt's waistband, not its sleeve and the skirt), not past their edge;
//   the floor.
// The rest it hangs in: put on the body at rest (out of the skin and the garments under it), then let settle there;
// a reset (the first step, a new clip, a scrub back) places it where it hangs at rest carried by the skin into the pose,
// and lets it settle without speed; a loop (step(clip, t, {loop: true})) carries it on across the clip's end, each
// point moved with the skin under it.
//   new ClothSim(figure, garments)    garments: [{output, cut, fabric, strength, form?, carrier?, pattern}] (src/cloth/clothes.js)
//   sim.wind = {speed, dir, gust, turbulence} | null        sim.step(ctx) — the figure's simulation step
import { normalsOf } from '../mesh.js';
import { windAt } from '../wind.js';
import { stenciled } from './patterns.js';

// H: the small step; G: gravity; SPEED: no point of cloth faster than this (m/s — the fastest a hand moves is some 10;
// a point flung faster by a contact is a contact's error, not motion); RHO: the air's density; DRAG: pressure on a
// surface facing the flow; SKIN_DRAG: the air along it
const H = 1 / (+(globalThis.process?.env?.CLOTH_HZ) || 240), G = 9.81, SPEED = 12, RHO = 1.2, DRAG = 1.2, SKIN_DRAG = 0.03;
// HOLD_TIME: how fast a held point goes where the skin carries it (seconds to close the gap, at hold 1); TETHER: how much
// longer than the cloth between them a point may be from its held point; SHAPE_K: the designed form's pull at strength
// 1 (1/s²: a point a centimetre off it pulled as hard as gravity pulls it at 2000 × 0.005… — at 2000 the cloth sags 5 mm
// under its own weight from the form, a stiff petticoat; at 0.1 it sags 5 cm)
const HOLD_TIME = 0.012, HELD_MASS = 0.95, TETHER = 1.04, SHAPE_K = 2000;
// SETTLE: small steps a reset lets the cloth settle in its pose without speed; REST_FRAMES: how long it hangs on the body
// at rest to find the rest (s); PREPARE: rounds of putting it on (out of the skin and the garments under it)
const SETTLE = 60, REST_TIME = 1.2, PREPARE = 6;
// FLOOR_MU: the floor's friction; REACH: how far past its thickness a point is looked at by the skin (farther: surely
// clear until the skin or the point has moved that far); HEAD_REACH: how near the Head joint the head's form is asked
// (a share of nothing: metres)
const FLOOR_MU = 0.8, REACH = 0.01, HEAD_REACH = 0.3;
// CURVE: the radius of the body's tightest curve cloth wraps (m)
const CURVE = 0.04;

export class ClothSim {
  constructor(figure, garments) {
    this.figure = figure; this.solids = figure.solids(); this.wind = null;
    this.garments = garments.slice().sort((a, b) => a.pattern.layer - b.pattern.layer).map((g, k) => new Garment(g, k, this.solids.KN));
    this.outputs = this.garments.map(g => g.output);
    const S = this.solids;
    this.m = { now: S.moment(1), was: S.moment(1), rest: S.rest.moment(0) };
    this.at = { n: [0, 0, 0], v: [0, 0, 0] }; this.at2 = { n: [0, 0, 0], v: [0, 0, 0] }; this.hl = [0, 0, 0]; this.hn = [0, 0, 0]; this.hp = [0, 0, 0]; this.ho = [0, 0, 0]; this.w = [0, 0, 0];
    this.time = 0; this.left = 0; this.started = false; this.bodyMove = 0; this.stepMove = 0; this.bodyWas = null;
    this.rest();
  }

  // ———— the rest it hangs in ————
  rest() {
    const mr = this.m.rest, gs = this.garments;
    for (const g of gs) { g.T0.set(g.cut); g.T1.set(g.cut); if (g.form) { g.S0.set(g.form); g.S1.set(g.form); } }
    // put on, innermost first: out of the skin and the garments under it before its lengths are its own (the masks: where
    // it lies together with each one under it)
    for (const [k, g] of gs.entries()) {
      g.masks = gs.slice(0, k).map(u => g.over(u));
      for (let it = 0; it < PREPARE; it++) { g.p.set(g.x); this.collide(g, k, mr, mr, false); }
      g.fitted(); g.normals(); g.publish();
    }
    // let hang on the body at rest
    const n = Math.round(REST_TIME / H);
    for (let s = 0; s < n; s++) this.substep(mr, mr, 1, null);
    for (const g of gs) { g.R0 = Float64Array.from(g.x); g.v.fill(0); g.normals(); }
    // the clothes as what lies over them meets them (hair: src/solids.js cover), at rest
    this.coverP = new Float32Array(gs.reduce((s, g) => s + g.n * 3, 0)); this.coverN = new Float32Array(this.coverP.length);
    this.cover = this.solids.cover(this.coverP.length / 3); this.covered(); this.cover.rest(this.coverP, this.coverN);
  }
  // every garment's points and normals as one surface (out to its own thickness: what lies on it lies on its outside)
  covered() {
    let at = 0;
    for (const g of this.garments) { for (let i = 0; i < g.x.length; i++) { this.coverP[at + i] = g.x[i] + g.nrm[i] * g.F.thick; this.coverN[at + i] = g.nrm[i]; } at += g.x.length; }
  }

  // the figure's step: {dt, reset, jump, t}
  step({ dt, reset, jump, t }) {
    const S = this.solids, m = this.m, F = this.figure, gs = this.garments;
    // where the skin carries each garment now, and its designed form (the frame's end)
    for (const g of gs) { g.T0.set(g.T1); if (g.form) g.S0.set(g.S1); g.carry(F); }
    this.bodyMoved(reset || jump);
    if (reset || !this.started) {
      S.moment(1, m.now); S.moment(1, m.was);
      for (const g of gs) { g.settled(); g.place(F); }
      for (let k = 0; k < SETTLE; k++) { this.substep(m.was, m.now, 1, null); for (const g of gs) g.v.fill(0); }
      this.started = true; this.left = 0; this.time = t / (F.state?.clip?.fps ?? 30); this.write('reset', 0); return;
    }
    // (a jump — the clip begun again — carries every point with the skin under it, as it was on it)
    if (jump) for (const g of gs) { g.jump(); g.settled(); }
    if (!(dt > 0)) { this.write(jump ? 'jump' : 'reset', 0); return; }
    const lag = this.left, n = Math.floor((lag + dt) / H + 1e-9);
    this.stepMove = this.bodyMove * H / dt;
    for (let s = 1; s <= n; s++) {
      const u = Math.max(0, Math.min(1, (s * H - lag) / dt));
      [m.was, m.now] = [m.now, m.was]; S.moment(u, m.now);
      this.substep(m.was, m.now, u, this.wind); this.time += H;
    }
    this.left = lag + dt - n * H;
    this.write(jump ? 'jump' : 'go', dt);
  }
  // how far the body's skin went this frame (the most any point went): a point clear of it by more than that a small
  // step is not looked at
  bodyMoved(still) {
    const P = this.figure.outputs[0].positions, u = this.figure.outputs[0].mesh.used;
    if (!this.bodyWas) this.bodyWas = Float32Array.from(P);
    let mv = 0;
    if (!still) for (let k = 0; k < u.length; k++) { const i = u[k] * 3, d = (P[i] - this.bodyWas[i]) ** 2 + (P[i + 1] - this.bodyWas[i + 1]) ** 2 + (P[i + 2] - this.bodyWas[i + 2]) ** 2; if (d > mv) mv = d; }
    this.bodyWas.set(P);
    this.bodyMove = Math.sqrt(mv);
  }

  // one small step for every garment, innermost first; u: the small step's share of the frame (targets there)
  substep(mw, mn, u, wind) {
    for (const [k, g] of this.garments.entries()) {
      g.u = u;
      g.integrate(wind, this.time, this.w);
      for (let it = 0; it < (+(globalThis.process?.env?.CLOTH_IT) || 1); it++) g.stretch(); g.bend(); g.stretch(); g.held(); g.pull(); g.tethers();
      if (g.self && (g.tick & 1)) g.apart();
      this.collide(g, k, mw, mn, true);
      // (its normals for the air every other small step, and as the surface the garments over it meet)
      g.velocities(); if ((g.tick & 1) === 0 || k < this.garments.length - 1) g.normals(); if (k < this.garments.length - 1) g.publish();
    }
  }

  // a garment's points against the body (the solids at moment mn, mw a small step before), the head's form, the
  // garments under it, the floor
  collide(g, k, mw, mn, moving) {
    const S = this.solids, head = S.head, at = this.at, at2 = this.at2, { x, p, n, thick, mu } = g, under = this.garments.slice(0, k);
    const move = moving ? this.stepMove : 0, hp = head ? S.carrier(mn).p : null;
    for (let i = 0; i < n; i++) {
      const i3 = i * 3;
      // the skin (and deep in, its inside): unless surely clear of it
      g.clear[i] -= move + Math.sqrt((x[i3] - p[i3]) ** 2 + (x[i3 + 1] - p[i3 + 1]) ** 2 + (x[i3 + 2] - p[i3 + 2]) ** 2);
      if (g.clear[i] <= REACH) {
        const d = S.kept(mn, x[i3], x[i3 + 1], x[i3 + 2], at, g.near, i * S.KN, !moving || ((i + g.tick) & 1) === 0);
        // (beyond the skin's reach it is at least that far from it)
        g.clear[i] = (d === Infinity ? S.FAR : d) - thick;
        if (d < thick) this.contact(g, i3, at, thick - d, mu);
        // a sleeve or a trouser leg: outside its own limb too, which has the last word
        const home = g.home[i];
        if (home && d !== Infinity && at.limb !== home) { const e = S.skin(mn, x[i3], x[i3 + 1], x[i3 + 2], at2, home); if (e < thick) this.contact(g, i3, at2, thick - e, mu); }
      }
      // the head's designed form (in its rest space, carried by the head and the jaw)
      if (head && (x[i3] - hp[0]) ** 2 + (x[i3 + 1] - hp[1]) ** 2 + (x[i3 + 2] - hp[2]) ** 2 < HEAD_REACH * HEAD_REACH) this.onHead(g, i3, mw, mn, moving);
      // the floor
      if (x[i3 + 1] < thick) {
        const pen = thick - x[i3 + 1]; x[i3 + 1] = thick;
        const tx = x[i3] - p[i3], tz = x[i3 + 2] - p[i3 + 2], tl = Math.hypot(tx, tz);
        if (tl > 1e-12) { const f = tl < FLOOR_MU * pen ? 1 : FLOOR_MU * pen / tl; x[i3] -= tx * f; x[i3 + 2] -= tz * f; }
      }
    }
    for (const [j, u] of under.entries()) if (g.masks?.[j]) g.against(u, g.masks[j]);
  }
  // one point pushed out of the skin by pen along its normal; its slide over the skin held back by friction (against the
  // skin's own motion in the small step)
  contact(g, i3, at, pen, mu) {
    const { x, p } = g, N = at.n, V = at.v;
    x[i3] += N[0] * pen; x[i3 + 1] += N[1] * pen; x[i3 + 2] += N[2] * pen;
    let tx = x[i3] - p[i3] - V[0] * H, ty = x[i3 + 1] - p[i3 + 1] - V[1] * H, tz = x[i3 + 2] - p[i3 + 2] - V[2] * H;
    const dn = tx * N[0] + ty * N[1] + tz * N[2]; tx -= dn * N[0]; ty -= dn * N[1]; tz -= dn * N[2];
    const tl = Math.sqrt(tx * tx + ty * ty + tz * tz);
    if (tl > 1e-12) { const f = tl < mu * pen ? 1 : mu * pen / tl; x[i3] -= tx * f; x[i3 + 1] -= ty * f; x[i3 + 2] -= tz * f; }
  }
  onHead(g, i3, mw, mn, moving) {
    const head = this.solids.head, { x, p, thick, mu } = g, l = this.hl, nn = this.hn, q = this.hp, o = this.ho;
    q[0] = x[i3]; q[1] = x[i3 + 1]; q[2] = x[i3 + 2]; head.local(mn, q, l);
    const d = head.distance(l); if (d >= thick) return;
    head.normal(l, nn); for (let j = 0; j < 3; j++) l[j] += nn[j] * (thick - d);
    if (moving) { q[0] = p[i3]; q[1] = p[i3 + 1]; q[2] = p[i3 + 2]; head.local(mw, q, o); const dx = l[0] - o[0], dy = l[1] - o[1], dz = l[2] - o[2], dn = dx * nn[0] + dy * nn[1] + dz * nn[2]; l[0] -= (dx - dn * nn[0]) * mu; l[1] -= (dy - dn * nn[1]) * mu; l[2] -= (dz - dn * nn[2]) * mu; }
    head.world(mn, l, o); x[i3] = o[0]; x[i3 + 1] = o[1]; x[i3 + 2] = o[2];
  }

  // every garment drawn where it is at the frame's own moment (carried on by its velocity over the part of a small step
  // the frame leaves over), its normals; the cover over the body as the clothes are now (how: as the solids' update)
  write(how, dt) {
    for (const g of this.garments) g.normals();
    this.covered(); this.cover.update(this.coverP, this.coverN, how, dt);
    for (const g of this.garments) {
      const o = g.output, x = g.x, v = g.v, L = this.left, X = g.drawn ? (g.at ??= new Float32Array(x.length)) : o.positions;
      for (let i = 0; i < x.length; i++) X[i] = x[i] + v[i] * L;
      if (g.drawn) stenciled(g.drawn, X, o.positions);
      normalsOf(o.positions, o.mesh.triangles, o.normals, o.mesh.used);
    }
  }
}

// ———— one garment ————
class Garment {
  constructor({ output, cut, fabric: F, strength = 0, form = null, carrier = null, sim, drawn, pattern, home }, index, kn) {
    const T = cut.triangles, R = form ?? cut.positions, n = R.length / 3;
    Object.assign(this, { output, pattern, index, n, tris: T, F, mu: F.friction, self: !!pattern.self, home, tick: 0 });
    this.formRest = form; this.carrier = carrier; this.skinner = sim; this.drawn = drawn; this.base = Float32Array.from(R);
    this.cut = Float64Array.from(R); this.form = form ? Float64Array.from(form) : null;
    this.x = Float64Array.from(R); this.p = Float64Array.from(R); this.v = new Float64Array(n * 3);
    this.T0 = new Float64Array(n * 3); this.T1 = new Float64Array(n * 3); this.u = 1; this.buf = new Float32Array(n * 3);
    if (form) { this.S0 = new Float64Array(n * 3); this.S1 = new Float64Array(n * 3); }
    // the skin points nearest each point (src/solids.js kept: looked for afresh every other small step, half the points
    // each time)
    this.nrm = new Float64Array(n * 3); this.clear = new Float64Array(n); this.near = new Int32Array(n * kn).fill(-2);
    this.hold = Float64Array.from(cut.hold); this.shapeK = strength * SHAPE_K;
    // masses from the fabric's weight per square metre (the smallest triangles' points given at least a share of a usual
    // point's mass: the cloth weighs the same within a few per cent, and slivers don't fly off); each point's share of
    // the surface (the air on it)
    const m = new Float64Array(n), area = new Float64Array(n);
    for (let t = 0; t < T.length; t += 3) { const A = triArea(R, T[t], T[t + 1], T[t + 2]); for (let k = 0; k < 3; k++) { m[T[t + k]] += A / 3 * F.density; area[T[t + k]] += A / 3; } }
    const med = Float64Array.from(m).sort()[n >> 1];
    for (let i = 0; i < n; i++) m[i] = Math.max(m[i], med * 0.4);
    // (a held point is as good as carried: its inverse mass taken down as it is held, so the cloth's weight hangs from
    // it rather than pulling it down — a waistband of a hundred points carries a pair of trousers of five thousand)
    this.mass = m; this.area = area; this.w = Float64Array.from(m, (v, i) => (1 - HELD_MASS * this.hold[i]) / Math.max(v, 1e-9));
    // edges and hinges: rest lengths as cut (a scarf's as it lies flat), the swimsuit's a share shorter
    const em = new Map();
    for (let t = 0; t < T.length; t += 3) for (let k = 0; k < 3; k++) {
      const a = T[t + k], b = T[t + (k + 1) % 3], c = T[t + (k + 2) % 3], key = a < b ? a * n + b : b * n + a, e = em.get(key);
      if (e) e.push(c); else em.set(key, [Math.min(a, b), Math.max(a, b), c]);
    }
    const E = [], Hg = [], BE = [], L0 = cut.flat ?? R, tight = this.tight = pattern.tight ?? 1; this.flat = !!cut.flat;
    for (const e of em.values()) { E.push(e[0], e[1]); if (e.length === 4) Hg.push(e[0], e[1], e[2], e[3]); else if (e.length === 3) BE.push(e[0], e[1], e[2]); }
    this.E = Uint32Array.from(E); this.EL = Float64Array.from({ length: E.length / 2 }, (_, k) => dist(L0, E[k * 2], E[k * 2 + 1]) * tight);
    this.BE = Uint32Array.from(BE); this.rim = new Float64Array(n * 3);
    this.edge = this.EL.reduce((s, l) => s + l, 0) / this.EL.length;
    // how far its points keep off the body: its fabric's thickness, and as far as the cloth between two points sags in
    // from them over the body's tightest curve (a knee, an elbow: CURVE) — else the skin shows between them
    this.thick = F.thick + this.edge * this.edge / (8 * CURVE);
    this.H = Uint32Array.from(Hg); this.HC = new Float64Array(Hg.length / 4);
    for (let k = 0; k < this.HC.length; k++) {
      const a = Hg[k * 4], b = Hg[k * 4 + 1], c = Hg[k * 4 + 2], d = Hg[k * 4 + 3], e = dist(R, a, b) || 1e-4, h1 = 2 * triArea(R, a, b, c) / e, h2 = 2 * triArea(R, a, b, d) / e;
      // (a hinge of slivers says nothing about the cloth's curvature: left out)
      this.HC[k] = Math.min(h1, h2) < this.edge * 0.25 ? -1 : (h1 + h2) / (3 * F.bend * e);
    }
    const h2 = 1 / (H * H); this.aT = h2 / F.stretch; this.aC = h2 / (F.stretch * F.compress); this.damp = Math.exp(-F.damping * H);
    this.shapeF = this.shapeK * H * H / (1 + this.shapeK * H * H);
    this.tether();
    this.selfGrid = new Grid(Math.max(this.thick * 2, this.edge * 0.55), n); this.grid = new Grid(0.025, n);
    this.normals();
  }
  // tethers: each point no farther from its nearest held point than the cloth between them is long (by TETHER)
  tether() {
    const n = this.n, d = new Float64Array(n).fill(Infinity), from = new Int32Array(n).fill(-1), adj = Array.from({ length: n }, () => []);
    for (let k = 0; k < this.EL.length; k++) { const a = this.E[k * 2], b = this.E[k * 2 + 1]; adj[a].push(b, this.EL[k]); adj[b].push(a, this.EL[k]); }
    const heap = [], push = (i, v) => { heap.push([v, i]); let c = heap.length - 1; while (c > 0) { const q = (c - 1) >> 1; if (heap[q][0] <= heap[c][0]) break; [heap[q], heap[c]] = [heap[c], heap[q]]; c = q; } };
    const pop = () => { const top = heap[0], last = heap.pop(); if (heap.length) { heap[0] = last; let c = 0; for (;;) { const l = c * 2 + 1, r = l + 1; let m = c; if (l < heap.length && heap[l][0] < heap[m][0]) m = l; if (r < heap.length && heap[r][0] < heap[m][0]) m = r; if (m === c) break; [heap[m], heap[c]] = [heap[c], heap[m]]; c = m; } } return top; };
    for (let i = 0; i < n; i++) if (this.hold[i] > 0.5) { d[i] = 0; from[i] = i; push(i, 0); }
    while (heap.length) { const [v, i] = pop(); if (v > d[i]) continue; const a = adj[i]; for (let k = 0; k < a.length; k += 2) { const j = a[k], nv = v + a[k + 1]; if (nv < d[j]) { d[j] = nv; from[j] = from[i]; push(j, nv); } } }
    this.anchor = from; this.reach = Float64Array.from(d, v => Number.isFinite(v) ? v * TETHER : 0);
    // the edges in the order of their distance from the held points, nearest first: one pass of the lengths then carries
    // the weight down from where the garment hangs, as a chain is solved from its top (in any other order a pass moves a
    // hanging garment's weight a few edges, and it stretches far under it)
    const order = Array.from({ length: this.EL.length }, (_, k) => k), far = k => Math.min(d[this.E[k * 2]], d[this.E[k * 2 + 1]]);
    order.sort((a, b) => far(a) - far(b));
    this.E = Uint32Array.from(order.flatMap(k => [this.E[k * 2], this.E[k * 2 + 1]])); this.EL = Float64Array.from(order, k => this.EL[k]);
  }
  // where the skin carries it at this frame's end (T1), and its designed form (S1): its rest (with this frame's changes of
  // the rest) skinned by its own skin and by the form's carrier
  carry(F) {
    const b = this.buf, J = F.ctx.rest, r = this.restNow(F);
    this.skinner.skin(F.pose, b, r, J); for (let i = 0; i < b.length; i++) this.T1[i] = b[i];
    if (this.form) {
      // (the form moved by what moved the garment's rest this frame)
      const fr = this.formNow ??= new Float32Array(b.length);
      for (let i = 0; i < fr.length; i++) fr[i] = this.formRest[i] + r[i] - this.base[i];
      this.carrier.skin(F.pose, b, fr, J); for (let i = 0; i < b.length; i++) this.S1[i] = b[i];
    }
  }
  // its rest this frame: as cut, moved by what moved the drawn mesh's rest (a change of the rest as a pose layer: the
  // drawn mesh's first points are the cut's own, src/cloth/patterns.js loopStencil)
  restNow(F) {
    const o = this.output, r = this.rest ??= Float32Array.from(this.base);
    if (!(o.rest && o.moved)) return this.base;
    for (let i = 0; i < r.length; i++) r[i] = this.base[i] + o.rest[i] - o.mesh.positions[i];
    return r;
  }
  // placed where it hangs at rest, carried by the skin into this pose (a reset)
  place(F) {
    const b = this.buf, R = this.R0, base = this.base, rest = this.restNow(F), r = this.placeRest ??= new Float32Array(b.length);
    for (let i = 0; i < r.length; i++) r[i] = R[i] + rest[i] - base[i];
    this.skinner.skin(F.pose, b, r, F.ctx.rest);
    for (let i = 0; i < b.length; i++) this.x[i] = this.p[i] = b[i];
    this.v.fill(0); this.clear.fill(0);
  }
  // the clip begun again: each point moved as the skin under it jumped (T0: before, T1: after)
  jump() { const { x, p, T0, T1 } = this; for (let i = 0; i < x.length; i++) { const d = T1[i] - T0[i]; x[i] += d; p[i] += d; } this.clear.fill(0); }
  // put on: its lengths are as it lies now, out of the body and the garments under it (a garment cut a little tight
  // would otherwise stand stretched where it was pushed out) — but a garment laid on as cut flat (a scarf) keeps its
  // flat lengths; where it is cut to and kept apart from itself is here too
  fitted() {
    if (!this.flat) for (let k = 0; k < this.EL.length; k++) this.EL[k] = dist(this.x, this.E[k * 2], this.E[k * 2 + 1]) * this.tight;
    this.cut.set(this.x); this.p.set(this.x);
    this.tether();
  }
  // the targets as they are at the frame's end, from its start too (nothing to go between)
  settled() { this.T0.set(this.T1); if (this.form) this.S0.set(this.S1); }
  // gravity, damping, the air; then each point carried on by its velocity
  integrate(wind, t, W) {
    const { n, x, v, p, nrm, area, mass, F } = this, damp = this.damp, odd = (++this.tick) & 1, air = F.air;
    // (the air every other small step, for two)
    if (air > 0 && odd) for (let i = 0; i < n; i++) {
      const i3 = i * 3;
      if (wind) windAt(wind, x[i3], x[i3 + 1], x[i3 + 2], t, this.index * 1.618, W); else W[0] = W[1] = W[2] = 0;
      const rx = v[i3] - W[0], ry = v[i3 + 1] - W[1], rz = v[i3 + 2] - W[2], nx = nrm[i3], ny = nrm[i3 + 1], nz = nrm[i3 + 2];
      const vn = rx * nx + ry * ny + rz * nz, k = 0.5 * RHO * area[i] * 2 * H / mass[i] * air;
      // (pressure on the surface facing the flow, a little along it: never more than to stop it in the flow)
      let dvn = k * DRAG * vn * Math.abs(vn); if (Math.abs(dvn) > Math.abs(vn)) dvn = vn;
      const tx = rx - vn * nx, ty = ry - vn * ny, tz = rz - vn * nz; let ft = k * SKIN_DRAG * Math.hypot(tx, ty, tz); if (ft > 1) ft = 1;
      v[i3] -= dvn * nx + ft * tx; v[i3 + 1] -= dvn * ny + ft * ty; v[i3 + 2] -= dvn * nz + ft * tz;
    }
    for (let i3 = 0; i3 < n * 3; i3 += 3) {
      v[i3] *= damp; v[i3 + 1] = (v[i3 + 1] - G * H) * damp; v[i3 + 2] *= damp;
      const sp = v[i3] * v[i3] + v[i3 + 1] * v[i3 + 1] + v[i3 + 2] * v[i3 + 2]; if (sp > SPEED * SPEED) { const s = SPEED / Math.sqrt(sp); v[i3] *= s; v[i3 + 1] *= s; v[i3 + 2] *= s; }
      p[i3] = x[i3]; p[i3 + 1] = x[i3 + 1]; p[i3 + 2] = x[i3 + 2];
      x[i3] += v[i3] * H; x[i3 + 1] += v[i3 + 1] * H; x[i3 + 2] += v[i3 + 2] * H;
    }
  }
  stretch() {
    const { x, w, E, EL, aT, aC } = this;
    for (let k = 0; k < EL.length; k++) {
      const a = E[k * 2], b = E[k * 2 + 1], a3 = a * 3, b3 = b * 3, wa = w[a], wb = w[b];
      const dx = x[b3] - x[a3], dy = x[b3 + 1] - x[a3 + 1], dz = x[b3 + 2] - x[a3 + 2], l = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (l < 1e-9) continue;
      const C = l - EL[k], s = C / ((wa + wb + (C > 0 ? aT : aC)) * l);
      x[a3] += wa * s * dx; x[a3 + 1] += wa * s * dy; x[a3 + 2] += wa * s * dz;
      x[b3] -= wb * s * dx; x[b3 + 1] -= wb * s * dy; x[b3 + 2] -= wb * s * dz;
    }
  }
  // the dihedral angle at each inner edge, toward flat (Müller et al. 2007; with these normals the q below are −∂d/∂p)
  bend() {
    const { x, w, H: Hg, HC } = this, h2 = 1 / (H * H);
    for (let k = 0; k < HC.length; k++) {
      if (HC[k] < 0) continue;
      const i1 = Hg[k * 4], i2 = Hg[k * 4 + 1], i3 = Hg[k * 4 + 2], i4 = Hg[k * 4 + 3];
      const ox = x[i1 * 3], oy = x[i1 * 3 + 1], oz = x[i1 * 3 + 2];
      const p2x = x[i2 * 3] - ox, p2y = x[i2 * 3 + 1] - oy, p2z = x[i2 * 3 + 2] - oz;
      const p3x = x[i3 * 3] - ox, p3y = x[i3 * 3 + 1] - oy, p3z = x[i3 * 3 + 2] - oz;
      const p4x = x[i4 * 3] - ox, p4y = x[i4 * 3 + 1] - oy, p4z = x[i4 * 3 + 2] - oz;
      let n1x = p2y * p3z - p2z * p3y, n1y = p2z * p3x - p2x * p3z, n1z = p2x * p3y - p2y * p3x;
      let n2x = p2y * p4z - p2z * p4y, n2y = p2z * p4x - p2x * p4z, n2z = p2x * p4y - p2y * p4x;
      const l1 = Math.sqrt(n1x * n1x + n1y * n1y + n1z * n1z), l2 = Math.sqrt(n2x * n2x + n2y * n2y + n2z * n2z);
      if (l1 < 1e-12 || l2 < 1e-12) continue;
      n1x /= l1; n1y /= l1; n1z /= l1; n2x /= l2; n2y /= l2; n2z /= l2;
      let d = n1x * n2x + n1y * n2y + n1z * n2z; d = d > 1 ? 1 : d < -1 ? -1 : d;
      const C = Math.acos(d) - Math.PI; if (C > -1e-3) continue;
      const q3x = ((p2y * n2z - p2z * n2y) + (n1y * p2z - n1z * p2y) * d) / l1, q3y = ((p2z * n2x - p2x * n2z) + (n1z * p2x - n1x * p2z) * d) / l1, q3z = ((p2x * n2y - p2y * n2x) + (n1x * p2y - n1y * p2x) * d) / l1;
      const q4x = ((p2y * n1z - p2z * n1y) + (n2y * p2z - n2z * p2y) * d) / l2, q4y = ((p2z * n1x - p2x * n1z) + (n2z * p2x - n2x * p2z) * d) / l2, q4z = ((p2x * n1y - p2y * n1x) + (n2x * p2y - n2y * p2x) * d) / l2;
      const q2x = -((p3y * n2z - p3z * n2y) + (n1y * p3z - n1z * p3y) * d) / l1 - ((p4y * n1z - p4z * n1y) + (n2y * p4z - n2z * p4y) * d) / l2;
      const q2y = -((p3z * n2x - p3x * n2z) + (n1z * p3x - n1x * p3z) * d) / l1 - ((p4z * n1x - p4x * n1z) + (n2z * p4x - n2x * p4z) * d) / l2;
      const q2z = -((p3x * n2y - p3y * n2x) + (n1x * p3y - n1y * p3x) * d) / l1 - ((p4x * n1y - p4y * n1x) + (n2x * p4y - n2y * p4x) * d) / l2;
      const q1x = -q2x - q3x - q4x, q1y = -q2y - q3y - q4y, q1z = -q2z - q3z - q4z;
      const s = Math.sqrt(1 - d * d); if (s < 1e-6) continue;
      const w1 = w[i1], w2 = w[i2], w3 = w[i3], w4 = w[i4];
      const sum = (w1 * (q1x * q1x + q1y * q1y + q1z * q1z) + w2 * (q2x * q2x + q2y * q2y + q2z * q2z) + w3 * (q3x * q3x + q3y * q3y + q3z * q3z) + w4 * (q4x * q4x + q4y * q4y + q4z * q4z)) / (s * s);
      const f = -C / (sum + HC[k] * h2) / s;
      x[i1 * 3] += w1 * q1x * f; x[i1 * 3 + 1] += w1 * q1y * f; x[i1 * 3 + 2] += w1 * q1z * f;
      x[i2 * 3] += w2 * q2x * f; x[i2 * 3 + 1] += w2 * q2y * f; x[i2 * 3 + 2] += w2 * q2z * f;
      x[i3 * 3] += w3 * q3x * f; x[i3 * 3 + 1] += w3 * q3y * f; x[i3 * 3 + 2] += w3 * q3z * f;
      x[i4 * 3] += w4 * q4x * f; x[i4 * 3 + 1] += w4 * q4y * f; x[i4 * 3 + 2] += w4 * q4z * f;
    }
  }
  // held points go where the skin carries them, as firmly as they are held (an elastic: a share of the way each step)
  held() {
    const { x, hold, T0, T1, n, u } = this, rate = H / HOLD_TIME;
    for (let i = 0; i < n; i++) {
      const s = hold[i]; if (s <= 0) continue; const f = Math.min(1, s * rate);
      for (let c = i * 3; c < i * 3 + 3; c++) x[c] += (T0[c] + (T1[c] - T0[c]) * u - x[c]) * f;
    }
  }
  // toward the designed form, as firmly as the garment's strength says
  pull() {
    if (!this.form || !this.shapeF) return;
    const { x, S0, S1, u } = this, f = this.shapeF; for (let i = 0; i < x.length; i++) x[i] += (S0[i] + (S1[i] - S0[i]) * u - x[i]) * f;
  }
  tethers() {
    const { x, anchor, reach, n } = this;
    for (let i = 0; i < n; i++) {
      const a = anchor[i]; if (a < 0 || a === i) continue;
      const dx = x[i * 3] - x[a * 3], dy = x[i * 3 + 1] - x[a * 3 + 1], dz = x[i * 3 + 2] - x[a * 3 + 2], l = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (l > reach[i]) { const s = reach[i] / l; x[i * 3] = x[a * 3] + dx * s; x[i * 3 + 1] = x[a * 3 + 1] + dy * s; x[i * 3 + 2] = x[a * 3 + 2] + dz * s; }
    }
  }
  // its own points kept apart, unless they were near as cut (neighbours along the cloth)
  apart() {
    const { x, cut: R, n, w, selfGrid: G } = this, r = G.cell, r2 = r * r, inv = 1 / r;
    G.build(x, n);
    for (let i = 0; i < n; i++) {
      const cx = Math.floor(x[i * 3] * inv), cy = Math.floor(x[i * 3 + 1] * inv), cz = Math.floor(x[i * 3 + 2] * inv);
      for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
        const hh = G.key(cx + dx, cy + dy, cz + dz), e = G.start[hh + 1];
        for (let k = G.start[hh]; k < e; k++) {
          const j = G.items[k]; if (j <= i) continue;
          const ax = x[j * 3] - x[i * 3], ay = x[j * 3 + 1] - x[i * 3 + 1], az = x[j * 3 + 2] - x[i * 3 + 2], d2 = ax * ax + ay * ay + az * az;
          if (d2 >= r2 || d2 < 1e-14) continue;
          const rx = R[j * 3] - R[i * 3], ry = R[j * 3 + 1] - R[i * 3 + 1], rz = R[j * 3 + 2] - R[i * 3 + 2];
          if (rx * rx + ry * ry + rz * rz < r2 * 2.6) continue;
          const d = Math.sqrt(d2), c = (r - d) / d / (w[i] + w[j]);
          x[i * 3] -= ax * c * w[i]; x[i * 3 + 1] -= ay * c * w[i]; x[i * 3 + 2] -= az * c * w[i];
          x[j * 3] += ax * c * w[j]; x[j * 3 + 1] += ay * c * w[j]; x[j * 3 + 2] += az * c * w[j];
        }
      }
    }
  }
  velocities() { const { x, p, v } = this, ih = 1 / H; for (let i = 0; i < x.length; i++) v[i] = (x[i] - p[i]) * ih; }
  normals() {
    const { x, tris: T, nrm } = this; nrm.fill(0);
    for (let t = 0; t < T.length; t += 3) {
      const a = T[t] * 3, b = T[t + 1] * 3, c = T[t + 2] * 3;
      const ux = x[b] - x[a], uy = x[b + 1] - x[a + 1], uz = x[b + 2] - x[a + 2], vx = x[c] - x[a], vy = x[c + 1] - x[a + 1], vz = x[c + 2] - x[a + 2];
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      nrm[a] += nx; nrm[a + 1] += ny; nrm[a + 2] += nz; nrm[b] += nx; nrm[b + 1] += ny; nrm[b + 2] += nz; nrm[c] += nx; nrm[c + 1] += ny; nrm[c + 2] += nz;
    }
    for (let i = 0; i < nrm.length; i += 3) { const l = Math.hypot(nrm[i], nrm[i + 1], nrm[i + 2]) || 1; nrm[i] /= l; nrm[i + 1] /= l; nrm[i + 2] /= l; }
  }
  // as a surface the garments over it meet: its points in a hash, which way is off its open edges
  publish() {
    this.grid.build(this.x, this.n);
    const { x, BE, rim } = this; rim.fill(0);
    for (let k = 0; k < BE.length; k += 3) {
      const a = BE[k] * 3, b = BE[k + 1] * 3, c = BE[k + 2] * 3;
      let ex = x[b] - x[a], ey = x[b + 1] - x[a + 1], ez = x[b + 2] - x[a + 2]; const el = Math.hypot(ex, ey, ez) || 1; ex /= el; ey /= el; ez /= el;
      let ox = (x[a] + x[b]) / 2 - x[c], oy = (x[a + 1] + x[b + 1]) / 2 - x[c + 1], oz = (x[a + 2] + x[b + 2]) / 2 - x[c + 2];
      const d = ox * ex + oy * ey + oz * ez; ox -= d * ex; oy -= d * ey; oz -= d * ez;
      rim[a] += ox; rim[a + 1] += oy; rim[a + 2] += oz; rim[b] += ox; rim[b + 1] += oy; rim[b + 2] += oz;
    }
  }
  // where it lies together with garment u (under it) as dressed: its points within reach of u's (the mask it meets u by)
  over(u) {
    u.publish();
    const m = new Uint8Array(this.n), reach = u.thick + this.thick + 0.02;
    for (let i = 0; i < this.n; i++) m[i] = u.nearest(this.x[i * 3], this.x[i * 3 + 1], this.x[i * 3 + 2], reach) >= 0 ? 1 : 0;
    return m;
  }
  // the nearest point of this garment within r of (x, y, z), or −1
  nearest(x, y, z, r) {
    const g = this.grid, inv = 1 / g.cell, cx = Math.floor(x * inv), cy = Math.floor(y * inv), cz = Math.floor(z * inv), P = this.x;
    let best = -1, bd = r * r;
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
      const h = g.key(cx + dx, cy + dy, cz + dz), e = g.start[h + 1];
      for (let k = g.start[h]; k < e; k++) { const i = g.items[k], d = (P[i * 3] - x) ** 2 + (P[i * 3 + 1] - y) ** 2 + (P[i * 3 + 2] - z) ** 2; if (d < bd) { bd = d; best = i; } }
    }
    return best;
  }
  // its points against garment u under it, where they lie together: out to both thicknesses along u's normal there, not
  // past u's edge, the slide over it held back by friction
  against(u, mask) {
    const { x, p, n, mu } = this, P = u.x, N = u.nrm, Q = u.p, R = u.rim, want = this.thick + u.thick, reach = Math.min(u.grid.cell * 1.5, want + 0.02);
    for (let i = 0; i < n; i++) {
      if (!mask[i]) continue;
      const k = i * 3, b = u.nearest(x[k], x[k + 1], x[k + 2], reach); if (b < 0) continue;
      const bk = b * 3, ex = x[k] - P[bk], ey = x[k + 1] - P[bk + 1], ez = x[k + 2] - P[bk + 2];
      if ((R[bk] || R[bk + 1] || R[bk + 2]) && ex * R[bk] + ey * R[bk + 1] + ez * R[bk + 2] > 0) continue;
      const d = ex * N[bk] + ey * N[bk + 1] + ez * N[bk + 2]; if (d >= want) continue;
      const pen = want - d;
      x[k] += N[bk] * pen; x[k + 1] += N[bk + 1] * pen; x[k + 2] += N[bk + 2] * pen;
      let tx = (x[k] - p[k]) - (P[bk] - Q[bk]), ty = (x[k + 1] - p[k + 1]) - (P[bk + 1] - Q[bk + 1]), tz = (x[k + 2] - p[k + 2]) - (P[bk + 2] - Q[bk + 2]);
      const dn = tx * N[bk] + ty * N[bk + 1] + tz * N[bk + 2]; tx -= dn * N[bk]; ty -= dn * N[bk + 1]; tz -= dn * N[bk + 2];
      const tl = Math.sqrt(tx * tx + ty * ty + tz * tz);
      if (tl > 1e-12) { const f = tl < mu * pen ? 1 : mu * pen / tl; x[k] -= tx * f; x[k + 1] -= ty * f; x[k + 2] -= tz * f; }
    }
  }
}

// a spatial hash: points into cells (counting sort into flat arrays, kept and refilled)
class Grid {
  constructor(cell, max) {
    this.cell = cell; this.size = 1; while (this.size < max * 2) this.size <<= 1;
    this.start = new Int32Array(this.size + 1); this.items = new Int32Array(max); this.keys = new Int32Array(max);
  }
  key(ix, iy, iz) { return (Math.imul(ix, 92837111) ^ Math.imul(iy, 689287499) ^ Math.imul(iz, 283923481)) & (this.size - 1); }
  build(pos, n) {
    const { start, items, keys, cell } = this, inv = 1 / cell; start.fill(0);
    for (let i = 0; i < n; i++) { const h = this.key(Math.floor(pos[i * 3] * inv), Math.floor(pos[i * 3 + 1] * inv), Math.floor(pos[i * 3 + 2] * inv)); keys[i] = h; start[h]++; }
    let s = 0; for (let h = 0; h < this.size; h++) { s += start[h]; start[h] = s; } start[this.size] = s;
    for (let i = 0; i < n; i++) items[--start[keys[i]]] = i;
  }
}
function dist(x, a, b) { return Math.hypot(x[a * 3] - x[b * 3], x[a * 3 + 1] - x[b * 3 + 1], x[a * 3 + 2] - x[b * 3 + 2]); }
function triArea(x, a, b, c) {
  const ux = x[b * 3] - x[a * 3], uy = x[b * 3 + 1] - x[a * 3 + 1], uz = x[b * 3 + 2] - x[a * 3 + 2], vx = x[c * 3] - x[a * 3], vy = x[c * 3 + 1] - x[a * 3 + 1], vz = x[c * 3 + 2] - x[a * 3 + 2];
  return Math.hypot(uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx) / 2;
}
