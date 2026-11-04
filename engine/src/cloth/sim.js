// Clothes in motion (О3's cloth, experiments/cloth/cloth.js and sim.js, carried onto the engine's figure; this is the
// source now): every garment a sheet of its fabric, moved by position-based dynamics with compliance (XPBD, Macklin et
// al. 2016: each constraint's multiplier λ gathered over the passes of a small step, so a fabric is as stiff as it is
// however many passes) in the figure's small steps (src/figure.js), all the garments of a figure in one simulation,
// the innermost first in each small step, so each meets the ones under it as they are then. In each small step, for
// each garment:
// - gravity, the fabric's own damping, and the air (the wind — the hair's presets, src/wind.js — less the cloth's own
//   velocity, pressing on each point as its surface faces the flow: light fabrics fly, heavy ones barely move);
// - lengths: each edge holds against stretching with the fabric's stretch (N/m) and gives way more easily when pushed
//   together (its compress share), so the cloth folds rather than shrinks — three passes, the edges in the order of their
//   distance from where the garment hangs;
// - bending: the angle at each inner edge held toward its angle as the garment was put on (a sleeve is a tube, not a
//   sheet pressed flat round the arm) with the fabric's bending rigidity B (N·m, Kawabata's; per hinge k = 3·B·e/(h₁+h₂))
//   — chiffon's bending length is about a centimetre, denim's three, tweed's four;
// - what holds it on: its waistband, neckline or shoulders (and a long sleeve's cuff, lightly) drawn to where the skin
//   carries them, as an elastic; every point no farther from its nearest held point than the cloth between them is long, as a strip of the cloth
//   one edge wide would hold it (tethers, Kim et al. 2012);
// - its designed silhouette (src/cloth/shape.js), when it has one: every point pulled toward the designed form as the
//   body carries it (fitted parts by the skin, what hangs below the hips by the pelvis), as firmly as the garment's
//   strength says — 1 a stiff petticoat holding the bell, 0 cloth hanging freely as it was cut; what hangs lets go of it
//   as the hips leave upright (lying, rolling, bowing a petticoat does not hold a bell up against gravity), and where the
//   cloth lies on the body or the floor (it drapes over the knees sitting, О1's);
// - its own points kept apart where it can fold onto itself (a skirt, a dress, trousers);
// - the body, both ways: each point out of the figure's solids (src/solids.js — its skin between the frames at that
//   small step's moment, at any depth; the head's designed form) by the fabric's thickness, with friction against the
//   skin's own motion, and left where it is where it is pinched in a fold of the body (skin folded onto skin: О3's);
//   and each point of the skin the garment covers kept under its triangles (a knee between the cloth's points pushes the
//   triangle it meets, not through it) — but where the skin has gone out past an open edge (a hem slid up over the
//   knees), which it may come back under; the body has the last word. Then the garments under it, where they lie
//   together as dressed (a blouse's hem over a skirt's waistband, not its sleeve and the skirt), not past their edge;
//   last the floor.
// The rest it hangs in: put on the body at rest (out of the skin and the garments under it), then let settle there;
// a reset (the first step, a new clip, a scrub back) places it where it hangs at rest carried by the skin into the pose,
// and lets it settle without speed; a loop carries it on across the clip's end, each point moved with the skin under it.
// What lies over the clothes (hair) meets them through the figure's solids (S.over): the outermost garment's surface
// where it is, out to its thickness, not past its open edges.
//   new ClothSim(figure, garments)    garments: [{output, cut, fabric, strength, form?, sim, drawn, pattern, home}] (src/cloth/clothes.js)
//   sim.wind = {speed, dir, gust, turbulence} | null        sim.begin(ctx), sim.substep(was, now), sim.end(left) — the
//                                                            figure's step; sim.sink: how deep each skin point is drawn
//                                                            sunk under the cloth now (src/view3d.js)
import { normalsOf } from '../mesh.js';
import { windAt } from '../wind.js';
import { stenciled } from './patterns.js';
import { sst, clamp } from '../math.js';
import { cellHash } from '../cells.js';
import { SMALL } from '../figure.js';

// H: the small step; G: gravity; RHO: the air's density; DRAG: pressure on a surface facing the flow; SKIN_DRAG: the air
// along it
const H = SMALL, G = 9.81, RHO = 1.2, DRAG = 1.2, SKIN_DRAG = 0.03;
// HOLD_K: how firmly a held point is drawn where the skin carries it (1/s²: a centimetre off, thirty times as hard as
// gravity pulls it — an elastic band, a third of the way back in a small step); TETHER: how much longer than the cloth between them a point may be from its
// held point before the cloth's own stretch along the way holds it; SHAPE_K: the designed form's pull at strength 1
// (1/s²: at 2000 the cloth sags 5 mm under its own weight from the form, a stiff petticoat; at 0.1 it sags 5 cm)
const HOLD_K = 30000, TETHER = 1.04, SHAPE_K = 2000;
// UPRIGHT, LYING: the hips' tilt from upright (degrees) up to which a garment's designed form holds what hangs of it
// wholly, and from which it holds none of it (a bell standing and walking; bowing it begins to fall, lying it hangs);
// LIES: how long a point that lay on the body or the floor keeps lying on it, released from its form (s)
const UPRIGHT = 20, LYING = 70, LIES = 0.15;
// SETTLE: small steps a reset lets the cloth settle in its pose without speed; ENTER: how long (s) the body goes into it
// from the rest on a reset; REST_TIME: how long it hangs on the body at rest to find the rest (s); PREPARE: rounds of
// putting it on (out of the skin and the garments under it)
const SETTLE = 30, REST_TIME = 2, PREPARE = 6, ENTER = 0.4;
// FLOOR_MU: the floor's friction; REACH: how far past its thickness a point is looked at by the skin (farther: surely
// clear until the skin or the point has moved that far); HEAD_REACH: how near the Head joint the head's form is asked
const FLOOR_MU = 0.8, REACH = 0.01, HEAD_REACH = 0.3;
// SELF: how far apart a garment's points keep where it folds onto itself (m), at least twice its thickness
const SELF = 0.008;
// AGAINST: the share of its depth in a garment under it a point is pushed out of it in a small step (all of it at once,
// a hem lying on a waistband was thrown off it and fell back, a shimmer)
const AGAINST = 0.5;
// RIM: how far past a garment's edge one over it (or hair) stops meeting it (m)
const RIM = 0.015;
// CURVE: the radius of the body's tightest curve cloth wraps (m)
const CURVE = 0.04;
// TOUCH: how near the skin a corner of a triangle is, for its middle to be asked too (m)
const TOUCH = 0.004;
// SINK, SINK_NEAR, SINK_FAR: the skin under cloth drawn this much sunk (m), all of it where the cloth is within SINK_NEAR,
// none past SINK_FAR (src/view3d.js: between the cloth's points the skin's own finer bulges would show)
const SINK = 0.004, SINK_NEAR = 0.012, SINK_FAR = 0.027;

export class ClothSim {
  constructor(figure, garments) {
    this.figure = figure; this.solids = figure.solids(); this.wind = null;
    this.garments = garments.slice().sort((a, b) => a.pattern.layer - b.pattern.layer).map((g, k) => new Garment(g, k, this.solids));
    this.outputs = this.garments.map(g => g.output);
    const S = this.solids;
    this.m = { now: S.moment(1), was: S.moment(1), rest: S.rest.moment(0) };
    this.at = { n: [0, 0, 0], v: [0, 0, 0] }; this.at2 = { n: [0, 0, 0], v: [0, 0, 0] }; this.hl = [0, 0, 0]; this.hn = [0, 0, 0]; this.hv = [0, 0, 0]; this.hp = [0, 0, 0]; this.ho = [0, 0, 0]; this.w = [0, 0, 0]; this.down = [0, 0, 0];
    this.time = 0; this.started = false; this.keep = 1; this.bodyMove = 0; this.stepMove = 0; this.bodyWas = null;
    this.sink = new Float32Array(figure.outputs[0].mesh.N);
    this.rest();
    S.lieOn(this);
  }

  // ———— the rest it hangs in ————
  rest() {
    const mr = this.m.rest, gs = this.garments;
    for (const g of gs) { g.T0.set(g.cut); g.T1.set(g.cut); if (g.shape0) { g.S0.set(g.shape0); g.S1.set(g.shape0); } }
    // put on, innermost first: out of the skin and the garments under it before its lengths are its own (the masks: where
    // it lies together with each one under it)
    for (let k = 0; k < gs.length; k++) {
      const g = gs[k];
      g.masks = gs.slice(0, k).map(u => g.over(u));
      for (let it = 0; it < PREPARE; it++) { g.p.set(g.x); this.collide(g, k, mr, mr, false); }
      g.fitted(); g.normals(); g.publish();
      // (the head's designed form is met only where the cloth lies outside it as it is put on — a hood round it; a
      // form reaching down the neck stands in the collar of a dress, which is the skin's to meet)
      if (this.solids.head) { const H = this.solids.head, l = this.hl, q = this.hp; g.onForm = Uint8Array.from({ length: g.n }, (_, i) => { q[0] = g.x[i * 3]; q[1] = g.x[i * 3 + 1]; q[2] = g.x[i * 3 + 2]; return H.distance(H.local(mr, q, l)) > g.thick ? 1 : 0; }); }
      // (and the skin it covers as it is put on)
    }
    // let hang on the body at rest
    const n = Math.round(REST_TIME / H);
    for (let s = 0; s < n; s++) this.small(mr, mr, null);
    // (and that is where it is held: where it hangs, not as it was cut — held as cut, a point the skin pushed out was
    // drawn back into it for ever, a standing tug at a strap that shimmered)
    // (and its points that lie together as it hangs may: its folds at rest are not pushed apart for ever)
    for (const g of gs) { g.R0 = Float64Array.from(g.x); g.base.set(g.x); g.cut.set(g.x); g.v.fill(0); g.normals(); g.publish(); }
  }

  // ———— the figure's step (src/figure.js) ————
  // as the frame begins: where the skin carries each garment at its end, and its designed form; a reset, a jump
  begin({ dt, reset, jump, t }) {
    const S = this.solids, m = this.m, F = this.figure, gs = this.garments;
    for (const g of gs) { g.settled(); g.carry(F); }
    this.bodyMoved(reset || jump);
    this.upright(F.pose);
    if (reset || !this.started) {
      // (from where it hangs at rest, carried whole by the pelvis to where the body is now, the body going into its pose
      // over ENTER — the cloth going along it, as a person dressed standing goes into a stride — then let settle there
      // without speed)
      const entry = S.entry(F.pose); this.bodyWas = null; this.bodyMoved(true); this.stepMove = this.bodyMove;
      for (const g of gs) g.enter(entry.pose);
      const n = Math.round(ENTER / H);
      for (let k = 1; k <= n; k++) { const u = sst(k / n), w = m.was; m.was = m.now; m.now = w; entry.moment(u, m.now); if (k === 1) entry.moment(0, m.was); this.small(m.was, m.now, null, u); }
      S.moment(1, m.now); S.moment(1, m.was); this.stepMove = 0;
      for (const g of gs) g.settled();
      for (let k = 0; k < SETTLE; k++) { this.small(m.was, m.now, null); for (const g of gs) g.v.fill(0); }
      this.started = true; this.time = t / (F.state?.clip?.fps ?? 30); this.how = 'reset'; this.dt = 0; return;
    }
    // (a jump — the clip begun again — carries every point with the skin under it, as it was on it)
    if (jump) for (const g of gs) { g.jump(); g.settled(); }
    this.stepMove = dt > 0 ? this.bodyMove * H / dt : 0; this.dt = dt; this.how = jump ? 'jump' : 'go';
  }
  // a small step of the frame (the targets at its share u of the frame: the moment's own)
  substep(mw, mn) { this.small(mw, mn, this.wind, this.dt > 0 ? mn.u : 1); this.time += H; }
  // as the frame ends: every garment drawn where it is at the frame's own moment (carried on by its velocity over the
  // part of a small step the frame leaves over), its normals; how deep the skin under it is drawn sunk
  end(left) {
    for (const g of this.garments) {
      const o = g.output, x = g.x, v = g.v, X = g.drawn ? g.at : o.positions;
      for (let i = 0; i < x.length; i++) X[i] = x[i] + v[i] * left;
      if (g.drawn) stenciled(g.drawn, X, o.positions);
      normalsOf(o.positions, o.mesh.triangles, o.normals, o.mesh.used);
    }
    this.sunk();
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
  // how much of its designed form what hangs keeps this frame: as upright as the hips are (their own down against the
  // world's)
  upright(pose) {
    const q = pose.Q, h = this.figure.rig.skeleton.index.Hips * 4, x = q[h], z = q[h + 2];
    // (the hips' up turned into the world: its height is the cosine of their tilt)
    const up = 1 - 2 * (x * x + z * z), tilt = Math.acos(clamp(up, -1, 1)) * 180 / Math.PI;
    this.keep = 1 - sst(clamp((tilt - UPRIGHT) / (LYING - UPRIGHT), 0, 1));
  }

  // one small step for every garment, innermost first; u: the small step's share of the frame (targets there)
  small(mw, mn, wind, u = 1) {
    const gs = this.garments;
    for (let k = 0; k < gs.length; k++) {
      const g = gs[k];
      g.u = u;
      g.integrate(wind, this.time, this.w);
      g.lambdas();
      g.stretch(); g.stretch(); g.bend(); g.stretch(); g.held(); g.tethers(); g.pull(this.keep);
      if (g.self && (g.tick & 1)) g.apart();
      this.collide(g, k, mw, mn, true);
      g.velocities(); g.normals(); g.publish();
    }
  }

  // a garment's points against the body (the solids at moment mn, mw a small step before), the head's form, the skin it
  // covers against its triangles, the garments under it, the floor
  collide(g, k, mw, mn, moving) {
    const S = this.solids, head = S.head, at = this.at, at2 = this.at2, { x, p, n, thick, mu } = g;
    const move = moving ? this.stepMove : 0, hp = head ? S.carrier(mn).p : null, KN = S.KN;
    g.touched.fill(0);
    for (let i = 0; i < n; i++) {
      const i3 = i * 3;
      // the skin (at any depth): unless surely clear of it
      g.clear[i] -= move + Math.sqrt((x[i3] - p[i3]) ** 2 + (x[i3 + 1] - p[i3 + 1]) ** 2 + (x[i3 + 2] - p[i3 + 2]) ** 2);
      if (g.clear[i] <= REACH) {
        const fresh = !moving || ((i + g.tick) & 1) === 0, d = S.kept(mn, x[i3], x[i3 + 1], x[i3 + 2], at, g.near, i * KN, fresh, thick);
        // (beyond the skin's reach it is at least that far from it)
        g.clear[i] = (d === Infinity ? S.FAR : d) - thick;
        // (pinched in a fold of the body: left where it is until the skin is looked for anew)
        if (fresh) g.pinched[i] = at.pinched ? 1 : 0;
        // (a sleeve or a trouser leg where another part of the body is nearest — an arm by the side, legs together —: its
        // own limb has the last word, О3's; near it, it lies outside its own limb and goes into the other, hidden between
        // them, rather than be pushed from one to the other)
        const home = g.home[i], e = home && d !== Infinity && at.limb !== home ? S.skin(mn, x[i3], x[i3 + 1], x[i3 + 2], at2, home) : Infinity;
        if (!g.pinched[i]) { if (d < thick) this.contact(g, i3, at, thick - d, mu); if (e < thick) this.contact(g, i3, at2, thick - e, mu); }
      }
      // the head's designed form (in its rest space, carried by the head and the jaw)
      if (head && g.onForm?.[i] && (x[i3] - hp[0]) ** 2 + (x[i3 + 1] - hp[1]) ** 2 + (x[i3 + 2] - hp[2]) ** 2 < HEAD_REACH * HEAD_REACH) this.onHead(g, i3, mw, mn, moving);
    }
    this.middles(g, mn);
    const masks = g.masks; for (let j = 0; j < k; j++) if (masks[j]) g.against(this.garments[j], masks[j]);
    // the floor
    for (let i = 0; i < n; i++) {
      const i3 = i * 3; if (x[i3 + 1] >= thick) continue;
      const pen = thick - x[i3 + 1]; x[i3 + 1] = thick; g.lies[i] = 1;
      const tx = x[i3] - p[i3], tz = x[i3 + 2] - p[i3 + 2], tl = Math.hypot(tx, tz);
      if (tl > 1e-12) { const f = tl < FLOOR_MU * pen ? 1 : FLOOR_MU * pen / tl; x[i3] -= tx * f; x[i3 + 2] -= tz * f; }
    }
  }
  // each triangle's middle out of the skin too, its three points moved together (a knee pressed into a skirt or a trouser
  // leg goes between points two or three centimetres apart, and through, though every point keeps out) — over the skin
  // points its corners keep; only on a sleeve, a trouser leg or what hangs (a skirt), where a corner is in touch (a body
  // part between points lies on them) and all three lie on one limb, their own (where the trunk meets an arm its nearest
  // skin goes from one to the other, and its middle was pushed one way and the other, a tremble; a triangle across two — between a heavy body's thighs, touching — has no one inside to keep
  // out of: pushed from one to the other it trembled); each point moved as far as the deepest of its triangles asks
  middles(g, mn) {
    const S = this.solids, at = this.at, x = g.x, T = g.tris, C = g.clear, Q = g.pinched, LB = S.limbs, H = g.home, near = g.near, KN = S.KN, thick = g.thick, PL = g.pushL, PN = g.pushN, PV = g.pushV; PL.fill(0);
    for (let t = 0; t < T.length; t += 3) {
      const a = T[t], b = T[t + 1], c = T[t + 2]; if ((C[a] > TOUCH && C[b] > TOUCH && C[c] > TOUCH) || Q[a] || Q[b] || Q[c]) continue;
      const na = near[a * KN], nb = near[b * KN], nc = near[c * KN]; if (na < 0 || nb < 0 || nc < 0) continue;
      const l = LB[na]; if (LB[nb] !== l || LB[nc] !== l || H[a] !== H[b] || H[a] !== H[c] || (H[a] ? H[a] !== l : !g.hangs)) continue;
      const a3 = a * 3, b3 = b * 3, c3 = c * 3, mx = (x[a3] + x[b3] + x[c3]) / 3, my = (x[a3 + 1] + x[b3 + 1] + x[c3 + 1]) / 3, mz = (x[a3 + 2] + x[b3 + 2] + x[c3 + 2]) / 3;
      const d = S.among(mn, mx, my, mz, at, near, a * KN, b * KN, c * KN); if (!(d < thick)) continue;
      const pen = thick - d, N = at.n;
      for (let s = 0; s < 3; s++) { const v = T[t + s]; if (pen > PL[v]) { PL[v] = pen; for (let q = 0; q < 3; q++) { PN[v * 3 + q] = N[q]; PV[v * 3 + q] = at.v[q]; } } }
    }
    const n3 = this.hn, v3 = this.hv;
    for (let v = 0; v < g.n; v++) { const pen = PL[v]; if (!pen) continue; const i3 = v * 3; for (let q = 0; q < 3; q++) { x[i3 + q] += PN[i3 + q] * pen; n3[q] = PN[i3 + q]; v3[q] = PV[i3 + q]; } g.touch(i3, n3, v3); }
  }
  // one point pushed out of the skin by pen along its normal; its slide over the skin held back by friction (against the
  // skin's own motion in the small step)
  contact(g, i3, at, pen, mu) {
    const { x, p } = g, N = at.n, V = at.v;
    g.touch(i3, N, V);
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
    head.world(mn, l, o); x[i3] = o[0]; x[i3 + 1] = o[1]; x[i3 + 2] = o[2]; g.lies[i3 / 3] = 1;
  }

  // what lies over the clothes (hair: S.over) meets the outermost garment where it is: the distance from its surface,
  // out to its thickness (the planes of its nearest points), past its open edges as far as from the edge; out.v how fast
  // the cloth there moves
  distance(x, y, z, out) {
    let best = Infinity;
    for (let k = this.garments.length - 1; k >= 0; k--) { const d = this.garments[k].surface(x, y, z, this.at); if (d < best) { best = d; for (let c = 0; c < 3; c++) { out.n[c] = this.at.n[c]; out.v[c] = this.at.v[c]; } } }
    return best;
  }
  // the skin under the cloth drawn sunk: as near as the cloth covering it is now
  // (the skin points each point of cloth keeps nearest, as near as it is to them)
  sunk() {
    const K = this.sink, idx = this.solids.points, KN = this.solids.KN; K.fill(0);
    for (const g of this.garments) for (let i = 0; i < g.n; i++) {
      const d = g.clear[i] + g.thick; if (!(d < SINK_FAR)) continue;
      const s = SINK * (1 - clamp((d - SINK_NEAR) / (SINK_FAR - SINK_NEAR), 0, 1));
      for (let q = 0; q < KN; q++) { const k = g.near[i * KN + q]; if (k < 0) break; const v = idx[k]; if (s > K[v]) K[v] = s; }
    }
  }
}

// ———— one garment ————
class Garment {
  constructor({ output, cut, fabric: F, strength = 0, form = null, sim, drawn, pattern, home }, index, S) {
    const T = cut.triangles, R = form ?? cut.positions, n = R.length / 3, kn = S.KN;
    Object.assign(this, { output, pattern, index, n, tris: T, F, mu: F.friction, self: !!pattern.self, tick: 0, strength, hangs: !!pattern.hangs, home });
    // base: where its points are held at rest (as cut, then as it hangs settled); shape0: its designed form at rest
    // (what it is pulled toward), if it has one
    this.skinner = sim; this.drawn = drawn; this.base = Float32Array.from(R); this.shape0 = form ? Float32Array.from(form) : null;
    if (form) { this.S0 = new Float64Array(n * 3); this.S1 = new Float64Array(n * 3); }
    this.cut = Float64Array.from(R); this.form = form ? Float64Array.from(form) : null;
    this.x = Float64Array.from(R); this.p = Float64Array.from(R); this.v = new Float64Array(n * 3);
    this.T0 = new Float64Array(n * 3); this.T1 = new Float64Array(n * 3); this.u = 1; this.buf = new Float32Array(n * 3); this.at = drawn ? new Float32Array(R.length) : null;
    // the skin points nearest each point (src/solids.js kept: looked for afresh every other small step, half the points
    // each time)
    this.nrm = new Float64Array(n * 3); this.clear = new Float64Array(n); this.near = new Int32Array(n * kn).fill(-1);
    this.touched = new Uint8Array(n); this.pinched = new Uint8Array(n); this.tn = new Float64Array(n * 3); this.tv = new Float64Array(n * 3); this.lies = new Float64Array(n);
    this.uv = [0, 0, 0]; this.nn = [0, 0, 0]; this.kid = new Int32Array(4); this.kd = new Float64Array(4);
    this.pushL = new Float64Array(n); this.pushN = new Float64Array(n * 3); this.pushV = new Float64Array(n * 3);
    this.hold = Float64Array.from(cut.hold);
    this.shapeK = strength * SHAPE_K;
    // masses from the fabric's weight per square metre (the smallest triangles' points given at least a share of a usual
    // point's mass: the cloth weighs the same within a few per cent, and slivers don't fly off); each point's share of
    // the surface (the air on it)
    const m = new Float64Array(n), area = new Float64Array(n);
    for (let t = 0; t < T.length; t += 3) { const A = triArea(R, T[t], T[t + 1], T[t + 2]); for (let k = 0; k < 3; k++) { m[T[t + k]] += A / 3 * F.density; area[T[t + k]] += A / 3; } }
    const med = Float64Array.from(m).sort()[n >> 1];
    for (let i = 0; i < n; i++) m[i] = Math.max(m[i], med * 0.4);
    this.mass = m; this.area = area; this.w = Float64Array.from(m, v => 1 / Math.max(v, 1e-9));
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
    this.bulge = this.edge * this.edge / (8 * CURVE); this.thick = F.thick + this.bulge;
    this.H = Uint32Array.from(Hg); this.HC = new Float64Array(Hg.length / 4); this.HA = new Float64Array(Hg.length / 4);
    for (let k = 0; k < this.HC.length; k++) {
      const a = Hg[k * 4], b = Hg[k * 4 + 1], c = Hg[k * 4 + 2], d = Hg[k * 4 + 3], e = dist(R, a, b) || 1e-4, h1 = 2 * triArea(R, a, b, c) / e, h2 = 2 * triArea(R, a, b, d) / e;
      // (a hinge of slivers says nothing about the cloth's curvature: left out)
      this.HC[k] = Math.min(h1, h2) < this.edge * 0.25 ? -1 : (h1 + h2) / (3 * F.bend * e);
    }
    const h2 = 1 / (H * H); this.aT = h2 / F.stretch; this.aC = h2 / (F.stretch * F.compress); this.damp = Math.exp(-F.damping * H);
    this.shapeF = this.shapeK * H * H / (1 + this.shapeK * H * H);
    // (each constraint's λ, gathered over a small step's passes)
    this.lE = new Float64Array(this.EL.length); this.lB = new Float64Array(this.HC.length);
    this.tether();
    // (its points kept SELF apart — О3's half an edge was half a centimetre on its finer cloth; here an edge is 2–3 cm)
    this.selfGrid = cellHash(Math.max(F.thick * 2, SELF)); this.grid = cellHash(0.025);
    this.normals();
  }
  // tethers: each point no farther from its nearest held point than the cloth between them is long (by TETHER), as stiff
  // as a strip of its cloth one edge wide along the way
  tether() {
    const n = this.n, d = new Float64Array(n).fill(Infinity), from = new Int32Array(n).fill(-1), adj = Array.from({ length: n }, () => []);
    for (let k = 0; k < this.EL.length; k++) { const a = this.E[k * 2], b = this.E[k * 2 + 1]; adj[a].push(b, this.EL[k]); adj[b].push(a, this.EL[k]); }
    const heap = [], push = (i, v) => { heap.push([v, i]); let c = heap.length - 1; while (c > 0) { const q = (c - 1) >> 1; if (heap[q][0] <= heap[c][0]) break; [heap[q], heap[c]] = [heap[c], heap[q]]; c = q; } };
    const pop = () => { const top = heap[0], last = heap.pop(); if (heap.length) { heap[0] = last; let c = 0; for (;;) { const l = c * 2 + 1, r = l + 1; let m = c; if (l < heap.length && heap[l][0] < heap[m][0]) m = l; if (r < heap.length && heap[r][0] < heap[m][0]) m = r; if (m === c) break; [heap[m], heap[c]] = [heap[c], heap[m]]; c = m; } } return top; };
    for (let i = 0; i < n; i++) if (this.hold[i] > 0.5) { d[i] = 0; from[i] = i; push(i, 0); }
    while (heap.length) { const [v, i] = pop(); if (v > d[i]) continue; const a = adj[i]; for (let k = 0; k < a.length; k += 2) { const j = a[k], nv = v + a[k + 1]; if (nv < d[j]) { d[j] = nv; from[j] = from[i]; push(j, nv); } } }
    this.anchor = from; this.reach = Float64Array.from(d, v => Number.isFinite(v) ? v * TETHER : 0);
    this.aR = Float64Array.from(d, v => Number.isFinite(v) && v > 0 ? v / (this.F.stretch * this.edge) / (H * H) : 0);
    // the edges in the order of their distance from the held points, nearest first: one pass of the lengths then carries
    // the weight down from where the garment hangs, as a chain is solved from its top (in any other order a pass moves a
    // hanging garment's weight a few edges, and it stretches far under it)
    const order = Array.from({ length: this.EL.length }, (_, k) => k), far = k => Math.min(d[this.E[k * 2]], d[this.E[k * 2 + 1]]);
    order.sort((a, b) => far(a) - far(b));
    this.E = Uint32Array.from(order.flatMap(k => [this.E[k * 2], this.E[k * 2 + 1]])); this.EL = Float64Array.from(order, k => this.EL[k]);
  }
  // where the skin carries it at this frame's end (T1), and its designed form (S1): its rest (with this frame's changes of
  // the rest) skinned by its own skin
  carry(F) {
    const b = this.buf; this.skinner.skin(F.pose, b, this.moved(this.base, 'bm'), F.ctx.rest); for (let i = 0; i < b.length; i++) this.T1[i] = b[i];
    if (this.shape0) { this.skinner.skin(F.pose, b, this.moved(this.shape0, 'sm'), F.ctx.rest); for (let i = 0; i < b.length; i++) this.S1[i] = b[i]; }
  }
  // a rest of it this frame, moved by what moved the drawn mesh's rest (a change of the rest as a pose layer: the drawn
  // mesh's first points are the cut's own, src/cloth/patterns.js drawnStencil)
  moved(R, key) {
    const o = this.output; if (!(o.rest && o.moved)) return R;
    const r = this[key] ??= new Float32Array(R.length); for (let i = 0; i < r.length; i++) r[i] = R[i] + o.rest[i] - o.mesh.positions[i];
    return r;
  }
  // placed where it hangs at rest, carried whole by the pelvis as the entry pose has it (a reset), its targets from
  // there (to this frame's, T1)
  enter(pose) {
    const b = this.buf; this.skinner.skin(pose, b, this.base); for (let i = 0; i < b.length; i++) this.x[i] = this.p[i] = b[i];
    this.T0.set(this.x); if (this.shape0) { this.skinner.skin(pose, b, this.shape0); for (let i = 0; i < b.length; i++) this.S0[i] = b[i]; }
    // (nothing of before kept: a reset is the same however it is come to)
    this.v.fill(0); this.clear.fill(0); this.near.fill(-1); this.touched.fill(0); this.pinched.fill(0); this.lies.fill(0); this.tick = 0;
  }
  // the clip begun again: each point moved as the skin under it jumped (T0: before, T1: after)
  jump() { const { x, p, T0, T1 } = this; for (let i = 0; i < x.length; i++) { const d = T1[i] - T0[i]; x[i] += d; p[i] += d; } this.clear.fill(0); }
  // put on: its lengths are as it lies now, out of the body and the garments under it (a garment cut a little tight
  // would otherwise stand stretched where it was pushed out) — but a garment laid on as cut flat (a scarf) keeps its
  // flat lengths; its bends as they are now; where it is cut to and kept apart from itself is here too
  fitted() {
    if (!this.flat) for (let k = 0; k < this.EL.length; k++) this.EL[k] = dist(this.x, this.E[k * 2], this.E[k * 2 + 1]) * this.tight;
    for (let k = 0; k < this.HA.length; k++) this.HA[k] = this.flat ? Math.PI : this.angle(k);
    // (where the skin carries it is where it lies now)
    this.cut.set(this.x); this.p.set(this.x); this.T0.set(this.x); this.T1.set(this.x); this.base.set(this.x);
    if (this.shape0) { this.S0.set(this.shape0); this.S1.set(this.shape0); }
    this.tether();
  }
  // the dihedral angle at hinge k now (π: flat)
  angle(k) {
    const x = this.x, Hg = this.H, i1 = Hg[k * 4] * 3, i2 = Hg[k * 4 + 1] * 3, i3 = Hg[k * 4 + 2] * 3, i4 = Hg[k * 4 + 3] * 3;
    const p2 = [x[i2] - x[i1], x[i2 + 1] - x[i1 + 1], x[i2 + 2] - x[i1 + 2]], p3 = [x[i3] - x[i1], x[i3 + 1] - x[i1 + 1], x[i3 + 2] - x[i1 + 2]], p4 = [x[i4] - x[i1], x[i4 + 1] - x[i1 + 1], x[i4 + 2] - x[i1 + 2]];
    const n1 = cross(p2, p3), n2 = cross(p2, p4), l = Math.hypot(...n1) * Math.hypot(...n2);
    return l < 1e-24 ? Math.PI : Math.acos(clamp((n1[0] * n2[0] + n1[1] * n2[1] + n1[2] * n2[2]) / l, -1, 1));
  }
  // the targets as they are at the frame's end, from its start too (nothing to go between)
  settled() { this.T0.set(this.T1); if (this.shape0) this.S0.set(this.S1); }
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
    const fade = Math.exp(-H / LIES), L = this.lies;
    for (let i = 0; i < n; i++) {
      const i3 = i * 3;
      v[i3] *= damp; v[i3 + 1] = (v[i3 + 1] - G * H) * damp; v[i3 + 2] *= damp;
      p[i3] = x[i3]; p[i3 + 1] = x[i3 + 1]; p[i3 + 2] = x[i3 + 2];
      x[i3] += v[i3] * H; x[i3 + 1] += v[i3 + 1] * H; x[i3 + 2] += v[i3 + 2] * H;
      L[i] *= fade;
    }
  }
  // a small step's λ from nothing
  lambdas() { this.lE.fill(0); this.lB.fill(0); }
  // the lengths (XPBD: Δλ = (−C − α̃λ) / (Σw|∇C|² + α̃), its stiffness against stretching or, softer, pushing together)
  stretch() {
    const { x, w, E, EL, aT, aC, lE } = this;
    for (let k = 0; k < EL.length; k++) {
      const a = E[k * 2], b = E[k * 2 + 1], a3 = a * 3, b3 = b * 3, wa = w[a], wb = w[b];
      const dx = x[b3] - x[a3], dy = x[b3 + 1] - x[a3 + 1], dz = x[b3 + 2] - x[a3 + 2], l = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (l < 1e-9) continue;
      const C = l - EL[k], al = C > 0 ? aT : aC, dl = (-C - al * lE[k]) / (wa + wb + al); lE[k] += dl;
      const s = -dl / l;
      x[a3] += wa * s * dx; x[a3 + 1] += wa * s * dy; x[a3 + 2] += wa * s * dz;
      x[b3] -= wb * s * dx; x[b3 + 1] -= wb * s * dy; x[b3 + 2] -= wb * s * dz;
    }
  }
  // the dihedral angle at each inner edge, toward its angle as put on (Müller et al. 2007; with these normals the q
  // below are −∂d/∂p)
  bend() {
    const { x, w, H: Hg, HC, HA, lB } = this, h2 = 1 / (H * H);
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
      const C = Math.acos(d) - HA[k];
      const s = Math.sqrt(1 - d * d); if (s < 1e-6) continue;
      const q3x = ((p2y * n2z - p2z * n2y) + (n1y * p2z - n1z * p2y) * d) / l1, q3y = ((p2z * n2x - p2x * n2z) + (n1z * p2x - n1x * p2z) * d) / l1, q3z = ((p2x * n2y - p2y * n2x) + (n1x * p2y - n1y * p2x) * d) / l1;
      const q4x = ((p2y * n1z - p2z * n1y) + (n2y * p2z - n2z * p2y) * d) / l2, q4y = ((p2z * n1x - p2x * n1z) + (n2z * p2x - n2x * p2z) * d) / l2, q4z = ((p2x * n1y - p2y * n1x) + (n2x * p2y - n2y * p2x) * d) / l2;
      const q2x = -((p3y * n2z - p3z * n2y) + (n1y * p3z - n1z * p3y) * d) / l1 - ((p4y * n1z - p4z * n1y) + (n2y * p4z - n2z * p4y) * d) / l2;
      const q2y = -((p3z * n2x - p3x * n2z) + (n1z * p3x - n1x * p3z) * d) / l1 - ((p4z * n1x - p4x * n1z) + (n2z * p4x - n2x * p4z) * d) / l2;
      const q2z = -((p3x * n2y - p3y * n2x) + (n1x * p3y - n1y * p3x) * d) / l1 - ((p4x * n1y - p4y * n1x) + (n2x * p4y - n2y * p4x) * d) / l2;
      const q1x = -q2x - q3x - q4x, q1y = -q2y - q3y - q4y, q1z = -q2z - q3z - q4z;
      const w1 = w[i1], w2 = w[i2], w3 = w[i3], w4 = w[i4], al = HC[k] * h2;
      const sum = (w1 * (q1x * q1x + q1y * q1y + q1z * q1z) + w2 * (q2x * q2x + q2y * q2y + q2z * q2z) + w3 * (q3x * q3x + q3y * q3y + q3z * q3z) + w4 * (q4x * q4x + q4y * q4y + q4z * q4z)) / (s * s);
      const dl = (-C - al * lB[k]) / (sum + al); lB[k] += dl;
      const f = dl / s;
      x[i1 * 3] += w1 * q1x * f; x[i1 * 3 + 1] += w1 * q1y * f; x[i1 * 3 + 2] += w1 * q1z * f;
      x[i2 * 3] += w2 * q2x * f; x[i2 * 3 + 1] += w2 * q2y * f; x[i2 * 3 + 2] += w2 * q2z * f;
      x[i3 * 3] += w3 * q3x * f; x[i3 * 3 + 1] += w3 * q3y * f; x[i3 * 3 + 2] += w3 * q3z * f;
      x[i4 * 3] += w4 * q4x * f; x[i4 * 3 + 1] += w4 * q4y * f; x[i4 * 3 + 2] += w4 * q4z * f;
    }
  }
  // held points toward where the skin carries them, as firmly as they are held (a spring of no length per unit of mass,
  // HOLD_K at hold 1: XPBD's share k·h²/(1 + k·h²) of the way in its one pass, as the form's)
  held() {
    const { x, hold, T0, T1, n, u } = this, kh = HOLD_K * H * H;
    for (let i = 0; i < n; i++) {
      const s = hold[i]; if (s <= 0) continue; const f = s * kh / (1 + s * kh);
      for (let c = i * 3; c < i * 3 + 3; c++) x[c] += (T0[c] + (T1[c] - T0[c]) * u - x[c]) * f;
    }
  }
  // toward the designed form, as firmly as the garment's strength says (a spring of no length per unit of mass, XPBD's
  // share k·h²/(1 + k·h²) of the way in a pass); what hangs as firmly as the hips keep upright (keep), and not where it
  // lies on the body or the floor (a stiff hood's shell keeps it where it touches the head: let go there, it fell onto
  // the head and was drawn off it again, a tremble)
  pull(keep) {
    if (!this.shapeF) return;
    const { x, S0, S1, u, lies: L, hold } = this, f = this.shapeF;
    for (let i = 0; i < this.n; i++) {
      const i3 = i * 3, g = this.hangs && hold[i] < 0.5 ? f * keep * (1 - L[i]) : f;
      x[i3] += (S0[i3] + (S1[i3] - S0[i3]) * u - x[i3]) * g; x[i3 + 1] += (S0[i3 + 1] + (S1[i3 + 1] - S0[i3 + 1]) * u - x[i3 + 1]) * g; x[i3 + 2] += (S0[i3 + 2] + (S1[i3 + 2] - S0[i3 + 2]) * u - x[i3 + 2]) * g;
    }
  }
  // the tethers (XPBD, one way: only farther than its reach)
  tethers() {
    const { x, w, anchor, reach, aR, n } = this;
    for (let i = 0; i < n; i++) {
      const a = anchor[i]; if (a < 0 || a === i) continue;
      const dx = x[i * 3] - x[a * 3], dy = x[i * 3 + 1] - x[a * 3 + 1], dz = x[i * 3 + 2] - x[a * 3 + 2], l = Math.sqrt(dx * dx + dy * dy + dz * dz), C = l - reach[i];
      if (C <= 0) continue;
      const wi = w[i], wa = w[a], dl = -C / (wi + wa + aR[i]), s = dl / l;
      x[i * 3] += wi * s * dx; x[i * 3 + 1] += wi * s * dy; x[i * 3 + 2] += wi * s * dz;
      x[a * 3] -= wa * s * dx; x[a * 3 + 1] -= wa * s * dy; x[a * 3 + 2] -= wa * s * dz;
    }
  }
  // its own points kept apart, unless they were near as cut (neighbours along the cloth)
  apart() {
    const { x, cut: R, n, w, selfGrid: G } = this, r = G.cell, r2 = r * r, inv = 1 / r;
    G.build(x, n);
    for (let i = 0; i < n; i++) {
      const cx = Math.floor(x[i * 3] * inv), cy = Math.floor(x[i * 3 + 1] * inv), cz = Math.floor(x[i * 3 + 2] * inv);
      for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
        const hh = G.bucket(cx + dx, cy + dy, cz + dz), e = G.start[hh + 1];
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
  // the velocities the small step leaves; a point the body pushed out leaves it without the push's speed (no bounce:
  // cloth lies on what it meets, and is carried off it only as fast as the skin moves there)
  velocities() {
    const { x, p, v, touched: T, tn, tv } = this, ih = 1 / H;
    for (let i = 0; i < x.length; i++) v[i] = (x[i] - p[i]) * ih;
    for (let i = 0; i < this.n; i++) {
      if (!T[i]) continue; const i3 = i * 3, vn = (v[i3] - tv[i3]) * tn[i3] + (v[i3 + 1] - tv[i3 + 1]) * tn[i3 + 1] + (v[i3 + 2] - tv[i3 + 2]) * tn[i3 + 2];
      if (vn > 0) { v[i3] -= tn[i3] * vn; v[i3 + 1] -= tn[i3 + 1] * vn; v[i3 + 2] -= tn[i3 + 2] * vn; }
    }
  }
  // a point the body pushed out this small step: which way, and how fast the skin there moves
  touch(i3, N, V) { const i = i3 / 3; this.touched[i] = 1; this.lies[i] = 1; for (let c = 0; c < 3; c++) { this.tn[i3 + c] = N[c]; this.tv[i3 + c] = V[c]; } }
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
  // as a surface what lies over it meets: its points in a hash, which way is off its open edges
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
    for (let i = 0; i < this.n; i++) m[i] = u.grid.nearest(u.x, this.x[i * 3], this.x[i * 3 + 1], this.x[i * 3 + 2], reach) >= 0 ? 1 : 0;
    return m;
  }
  // the NEAR nearest points of this garment within r of (x, y, z) into ids/ds (squared distances, nearest first; −1 past
  // the last), how many
  nearestK(x, y, z, r, ids, ds) {
    const g = this.grid, inv = 1 / g.cell, cx = Math.floor(x * inv), cy = Math.floor(y * inv), cz = Math.floor(z * inv), P = this.x, K = ids.length;
    ids.fill(-1); ds.fill(r * r); let n = 0;
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
      const h = g.bucket(cx + dx, cy + dy, cz + dz), e = g.start[h + 1];
      for (let k = g.start[h]; k < e; k++) {
        const i = g.items[k], d = (P[i * 3] - x) ** 2 + (P[i * 3 + 1] - y) ** 2 + (P[i * 3 + 2] - z) ** 2; if (d >= ds[K - 1]) continue;
        let q = K - 1; while (q > 0 && ds[q - 1] > d) { ds[q] = ds[q - 1]; ids[q] = ids[q - 1]; q--; } ds[q] = d; ids[q] = i; if (n < K) n++;
      }
    }
    return n;
  }
  // its surface as what lies over it meets it (x, y, z within reach): the planes of its nearest points, weighed by
  // nearness, out to its thickness; past its open edge, as far as from the edge (Infinity beyond reach). out: {n, v}
  surface(x, y, z, out) {
    const P = this.x, N = this.nrm, Q = this.p, R = this.rim, ids = this.kid, ds = this.kd, m = this.nearestK(x, y, z, this.grid.cell * 1.5, ids, ds);
    if (!m) return Infinity;
    const h2 = Math.max(ds[0], 1e-6) * 4 + 1e-5; let sw = 0, sd = 0; out.n[0] = out.n[1] = out.n[2] = 0; out.v[0] = out.v[1] = out.v[2] = 0;
    for (let q = 0; q < m; q++) { const b = ids[q] * 3, w = Math.exp(-ds[q] / h2); sw += w; sd += w * ((x - P[b]) * N[b] + (y - P[b + 1]) * N[b + 1] + (z - P[b + 2]) * N[b + 2]); for (let c = 0; c < 3; c++) { out.n[c] += w * N[b + c]; out.v[c] += w * (P[b + c] - Q[b + c]) / H; } }
    const l = Math.hypot(out.n[0], out.n[1], out.n[2]) || 1; for (let c = 0; c < 3; c++) { out.n[c] /= l; out.v[c] /= sw; }
    const d = sd / sw - this.F.thick, b0 = ids[0] * 3, rl = Math.hypot(R[b0], R[b0 + 1], R[b0 + 2]);
    const past = rl ? ((x - P[b0]) * R[b0] + (y - P[b0 + 1]) * R[b0 + 1] + (z - P[b0 + 2]) * R[b0 + 2]) / rl : 0;
    return past > 0 ? Math.hypot(d, past) : d;
  }
  // its points against garment u under it, where they lie together: out to both thicknesses from u's surface there (the
  // planes of its nearest points, weighed by nearness: one nearest point's plane jumps where it changes, and the cloth
  // over it shimmered), not past u's edge, the slide over it held back by friction, no bounce
  against(u, mask) {
    const { x, p, n, mu } = this, P = u.x, N = u.nrm, Q = u.p, R = u.rim, want = this.F.thick + u.F.thick, reach = Math.min(u.grid.cell * 1.5, want + 0.02), ids = this.kid, ds = this.kd, nn = this.nn, uv = this.uv;
    for (let i = 0; i < n; i++) {
      if (!mask[i]) continue;
      const k = i * 3, m = u.nearestK(x[k], x[k + 1], x[k + 2], reach, ids, ds); if (!m) continue;
      const b0 = ids[0] * 3;
      // (past its edge what lies beyond is not under it: met less the farther past it, gone RIM past — met or not as
      // its nearest point changes along the edge, a hem lying over a waistband shimmered)
      const rl = Math.hypot(R[b0], R[b0 + 1], R[b0 + 2]), past = rl ? ((x[k] - P[b0]) * R[b0] + (x[k + 1] - P[b0 + 1]) * R[b0 + 1] + (x[k + 2] - P[b0 + 2]) * R[b0 + 2]) / rl : 0, keep = past > 0 ? 1 - past / RIM : 1;
      if (keep <= 0) continue;
      const h2 = Math.max(ds[0], 1e-6) * 4 + 1e-5; let sw = 0, sd = 0; nn[0] = nn[1] = nn[2] = 0; uv[0] = uv[1] = uv[2] = 0;
      for (let q = 0; q < m; q++) { const b = ids[q] * 3, w = Math.exp(-ds[q] / h2); sw += w; sd += w * ((x[k] - P[b]) * N[b] + (x[k + 1] - P[b + 1]) * N[b + 1] + (x[k + 2] - P[b + 2]) * N[b + 2]); for (let c = 0; c < 3; c++) { nn[c] += w * N[b + c]; uv[c] += w * (P[b + c] - Q[b + c]); } }
      const d = sd / sw, l = Math.hypot(nn[0], nn[1], nn[2]) || 1; for (let c = 0; c < 3; c++) { nn[c] /= l; uv[c] /= sw; }
      // (far under it — tucked in under a waistband — it stays there)
      if (d >= want || d < -want) continue;
      const pen = (want - d) * keep * AGAINST;
      x[k] += nn[0] * pen; x[k + 1] += nn[1] * pen; x[k + 2] += nn[2] * pen;
      let tx = (x[k] - p[k]) - uv[0], ty = (x[k + 1] - p[k + 1]) - uv[1], tz = (x[k + 2] - p[k + 2]) - uv[2];
      const dn = tx * nn[0] + ty * nn[1] + tz * nn[2]; tx -= dn * nn[0]; ty -= dn * nn[1]; tz -= dn * nn[2];
      const tl = Math.sqrt(tx * tx + ty * ty + tz * tz);
      if (tl > 1e-12) { const f = tl < mu * pen ? 1 : mu * pen / tl; x[k] -= tx * f; x[k + 1] -= ty * f; x[k + 2] -= tz * f; }
      for (let c = 0; c < 3; c++) uv[c] /= H;
      this.touch(k, nn, uv);
    }
  }

}

const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
function dist(x, a, b) { return Math.hypot(x[a * 3] - x[b * 3], x[a * 3 + 1] - x[b * 3 + 1], x[a * 3 + 2] - x[b * 3 + 2]); }
function triArea(x, a, b, c) {
  const ux = x[b * 3] - x[a * 3], uy = x[b * 3 + 1] - x[a * 3 + 1], uz = x[b * 3 + 2] - x[a * 3 + 2], vx = x[c * 3] - x[a * 3], vy = x[c * 3 + 1] - x[a * 3 + 1], vz = x[c * 3 + 2] - x[a * 3 + 2];
  return Math.hypot(uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx) / 2;
}
