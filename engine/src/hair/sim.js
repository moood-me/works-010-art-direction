// Hair in motion (В1's motion.js, carried onto the engine's figure): every guide is a chain of points rooted on the
// Head joint, moved by position-based dynamics, as games and film do it (TressFX; Müller et al. 2012, "Fast simulation
// of inextensible hair"). A figure's step (src/figure.js) runs it after the floor, in small steps of 1/240 s, always
// the same whatever the frame's step (the time a frame leaves over is carried to the next: so the hair moves the same at
// 20, 30, 60 or 144 frames a second); in each:
// - gravity and the air (the wind with its gusts and a turbulence of its own round every lock, less the lock's own
//   velocity, drag as the square of that speed, pushing across a lock more than along it);
// - twice the groom: every point pulled toward where the hairstyle has it, carried by the head; every segment bent back
//   toward its designed angle against the one above — stiffnesses as springs (1/s²), each pass taking k·h²/(1 + k·h²)
//   as XPBD's compliance does;
// - the solids (src/solids.js: the head's shape with its jaw — each point allowed as deep as it lies at rest —, the
//   body's skin between the frames, the floor), with friction against their own motion;
// - lengths kept exactly (follow-the-leader, with its velocity correction; ringlets give like springs);
// - the hair's own friction (its motion against where the head carries the hairstyle dies down), friction between
//   neighbouring locks (each point's velocity drawn toward its neighbours' in the other locks near it at rest — hair
//   against hair, as film does it by smoothing the hair's velocities, Petrovic et al. 2005: neighbouring locks move as a
//   mass instead of falling apart into ribbons), and zigzags along a chain damped — each a rate (1/s).
// The hairstyle was designed as it hangs, so the groom is set against the hair's weight: let hang, the groom moved up by
// how far it sagged, a few times over, until hanging is the design (an inverse of the rest shape, as film pipelines do
// it) — then let settle once on the standing body (over its shoulders, not through them), and that is its rest.
// The surfaces ride the chains: each point bound to up to three chains where it lies (src/hair/build.js bindOf), in
// the chain's frame there (carried down it without twist), blended between neighbouring frames. The free points are
// drawn where they are at the frame's own moment (carried on by their velocity over the part of a small step the frame
// leaves over), the roots where the head is.
//   new HairSim(figure, {guides, meshes: [{output, bind, normals: 'design' | 'surface'}], physics})
//   sim.wind = {speed, dir, gust, turbulence} | null      sim.step(ctx) — the figure's simulation step
import { qRot3, qSlerp } from '../math.js';
import { normalsOf } from '../mesh.js';

// WIND: how much more the wind takes the hair than the air of its own motion does (the wind felt as a flow WIND times as
// fast): with the air of its motion alone, a strong wind leaned long hair 24°; with that air made as strong (four, eight
// times), running hair stood out in wings. Film directs the wind apart from the motion's air too.
const WIND = 3;
// G: gravity; H: the small step; PIN: points of a chain carried by the head; MU: friction against a solid (the share of
// its motion along the solid taken away in a small step); AIR: how fast the air stills a point's own motion (1/s)
const G = 9.81, H = 1 / 240, PIN = 2, MU = 0.35, AIR = 0.4;
// ZIGZAG: how fast a point's velocity against its two neighbours' dies (1/s: 0.35 of it a small step); TOGETHER: how
// fast a point's velocity against its neighbouring locks' (1/s); NEAR: how near at rest a point of another lock is a
// neighbour; FLOOR: the floor's friction (a share a small step)
const ZIGZAG = 103, TOGETHER = 40, NEAR = 0.035, FLOOR = 0.6;
// LINK: how much farther apart than at rest two neighbouring locks may part (a share of their gap); LINK_RATE: how fast
// beyond it they are drawn back (1/s)
const LINK = 0.3, LINK_RATE = 120;
// LIE: how near the skin a lock lies on it (it lies on it as it lay at rest: framesOf)
const LIE = 0.03;
// TWIST: how much faster a lock's turn about itself may change from one segment to the next (framesOf)
const TWIST = 12 * Math.PI / 180;
// NEAR_SKIN: a chain this near the skin has its surfaces laid on it (onSkin): a lock's half width and more
const NEAR_SKIN = 0.04;
// SETTLE: small steps a reset lets the hair settle in its pose without speed; the groom: GROOM_FIT times let hang and
// moved up by the sag (each move at most GROOM_STEP), DRAPE: the bend while it settles on the body, SETTLED: still
// enough (m) to be the rest
const SETTLE = 60, GROOM_FIT = 5, GROOM_STEP = 0.03, DRAPE = 0.05, SETTLED = 0.004;

// the wind at a point: a steady flow (o.speed along o.dir) going through gusts — two waves travelling along the wind,
// slow and quick, the strength o.gust —, a slow swing of each lock's own (its seed), a turbulence round each lock
// (o.turbulence: its share of the speed across the wind and up), and the flow's small lift
export function windAt(o, x, y, z, t, seed, out) {
  const s = o.speed, d = o.dir, along = x * d[0] + z * d[2], g = o.gust ?? 1, tu = o.turbulence ?? 1;
  const gust = 0.62 + g * (0.3 * Math.sin(t * 1.3 - along * 1.7) * Math.sin(t * 0.47 + 1.3) + 0.22 * Math.sin(t * 3.1 - along * 4 + seed) * Math.sin(t * 0.9 + seed * 0.7));
  const k = s * gust * (0.85 + 0.3 * Math.sin(seed * 5.1 + t * 0.6));
  out[0] = d[0] * k + tu * 0.32 * s * Math.sin(t * 2.3 + y * 7 + seed * 1.7) * Math.sin(t * 0.8 + seed);
  out[1] = d[1] * k + tu * 0.22 * s * Math.sin(t * 2.9 + x * 6 + seed * 2.3) + 0.08 * s;
  out[2] = d[2] * k + tu * 0.32 * s * Math.cos(t * 2.1 + z * 7 + seed * 3.1) * Math.sin(t * 0.7 + seed * 1.3);
  return out;
}

export class HairSim {
  constructor(figure, { guides, meshes, physics = {}, grows = null }) {
    this.figure = figure; this.solids = figure.solids(); this.wind = null; this.meshes = meshes; this.outputs = meshes.map(m => m.output);
    const k = this.k = { hold: 1, bend: 1, drag: 1, wind: 1, friction: 1, damping: 1, together: 1, ...physics };
    const chains = this.chains = [], f = s => s * H * H / (1 + s * H * H);
    let N = 0;
    for (const [gi, g] of guides.entries()) {
      const n = g.points.length, c = { n, at: N, head: !!g.head, seed: gi * 1.618, gain: 0.8 + 0.4 * ((gi * 0.618) % 1) };
      // (each stiffness's share of a pass in a small step)
      if (!g.head) Object.assign(c, { rooted: g.rooted, depth: g.depth ?? null, rad: g.rad, hold: g.hold.map(v => f(v * k.hold)), bend: g.bend.map(v => f(v * k.bend)), drag: g.drag * k.drag, inner: g.inner * k.damping, stretch: g.stretch });
      chains.push(c); N += n;
    }
    this.N = N;
    const F = () => new Float64Array(N * 3);
    this.x = F(); this.xp = F(); this.v = F(); this.corr = F(); this.cn = F(); this.ct = new Uint8Array(N);
    // X0: the guides at rest (the body's rest space); T0: where the groom pulls (moved against the weight); R0: where
    // the hair hangs at rest; NX, NR: each node's place and frame now (for the surfaces); D: the points as drawn
    this.X0 = F(); guides.forEach((g, gi) => g.points.forEach((p, k) => this.X0.set(p, (chains[gi].at + k) * 3)));
    this.T0 = Float64Array.from(this.X0); this.R0 = null;
    this.NX = F(); this.NR = new Float64Array(N * 9); this.D = F(); this.under = new Float64Array(N).fill(Infinity); this.underN = F(); this.underM = F();
    for (const c of chains) {
      if (c.head) continue;
      c.L = []; c.d0 = [];
      for (let k = 0; k < c.n - 1; k++) { const i = (c.at + k) * 3, d = [0, 1, 2].map(j => this.X0[i + 3 + j] - this.X0[i + j]), l = Math.hypot(...d); c.L.push(l); c.d0.push(d.map(q => q / l)); }
      c.t0 = c.d0.map(d => d.slice());
    }
    // what a small step works with, made once: the solids now and a small step ago, a point's answers, scratch
    const S = this.solids;
    this.m = { now: S.moment(1), was: S.moment(1), end: S.moment(1), rest: S.rest.moment(0) };
    this.q = { o: [0, 0, 0], w: [0, 0, 0], r: [0, 0, 0], pp: [0, 0, 0], l: [0, 0, 0], lp: [0, 0, 0], n: [0, 0, 0], p: [0, 0, 0], Q: [0, 0, 0, 1], B: [0, 0, 0, 1], at: { n: [0, 0, 0], v: [0, 0, 0] } };
    this.Qs = new Float64Array(N * 4);
    // how deep each point lies in the head's shape at rest, and in the skin (where a head without a designed form is
    // its skin): it may stay that deep (the hairstyle lies as designed)
    const head = S.head, l = [0, 0, 0], mr = this.m.rest, at = this.q.at;
    for (const c of chains) if (!c.head) {
      c.allow = Array.from({ length: c.n }, (_, k) => { if (!head) return 0; for (let j = 0; j < 3; j++) l[j] = this.X0[(c.at + k) * 3 + j]; return Math.min(c.rad[k], head.distance(l) - 0.001); });
      // (in the head's skin — a head without a designed form — as deep as it lay at rest, roots under the scalp; out of
      // the body's by its own half-thickness, however the design lay on the neutral head's small shoulders)
      c.allowSkin = Array.from({ length: c.n }, (_, k) => { const i = (c.at + k) * 3, d = S.skin(mr, this.X0[i], this.X0[i + 1], this.X0[i + 2], at); return at.head > 0.5 ? Math.min(c.rad[k], d - 0.001) : c.rad[k]; });
    }
    // the inner layers: their edges, and how far each point's are stretched now (output.parted: src/hair/shade.js hides
    // the inner layer where it is stretched past PARTED — where locks part it does not stretch into a web between them)
    for (const M of meshes) if (M.output.mesh.hair?.layer === 'inner') { M.edges = edgesOf(M.output.mesh.triangles); M.output.parted = new Float32Array(M.output.mesh.N); }
    this.drape = 1; this.headRest = Float64Array.from(S.headRest);
    this.groom();
    this.neighbours();
    // where each lock lies on the body at rest (the skin's normal at each segment, how near: src/hair/sim.js framesOf)
    for (const c of chains) if (!c.head) c.lay = c.d0.map((_, k) => { const i = (c.at + k) * 3, R = this.R0, d = S.skin(mr, (R[i] + R[i + 3]) / 2, (R[i + 1] + R[i + 4]) / 2, (R[i + 2] + R[i + 5]) / 2, at), w = 1 - Math.min(1, Math.max(0, d) / LIE); return w > 0 && Number.isFinite(d) ? { n: at.n.slice(), w } : null; });
    // the changes of the rest as pose layers (a bigger head): each moves the guides' rest as it moves the hairstyle
    // fitted onto the changed body (grows(from, to): per guide its points' deltas); their weights this frame
    this.growth = grows ? figure.restLayers.map(l => { const D = new Float64Array(N * 3); grows(l.bodies.from, l.bodies.to).forEach((d, gi) => { if (d) for (let k = 0; k < d.indices.length; k++) for (let c = 0; c < 3; c++) D[(chains[gi].at + d.indices[k]) * 3 + c] = d.deltas[k * 3 + c]; }); return D; }) : [];
    this.base = this.growth.length ? { X0: Float64Array.from(this.X0), T0: Float64Array.from(this.T0), R0: Float64Array.from(this.R0) } : null;
    this.weights = new Float64Array(this.growth.length);
    this.time = 0; this.left = 0; this.started = false;
  }

  // ———— the head carrying the hairstyle: x' = R (x − J) + P, at a moment of the solids (J: the Head joint's rest place
  // this frame) ————
  carry(m, x, y, z, o) { const t = this.solids.carrier(m), r = this.headRest; qRot3(t.q, x - r[0], y - r[1], z - r[2], o); o[0] += t.p[0]; o[1] += t.p[1]; o[2] += t.p[2]; return o; }

  // the hair's rest this frame: the guides' rest, where the groom pulls and where it hangs, each moved by the changes of
  // the rest as they are weighed in this frame; the Head joint's rest place
  grown() {
    const ctx = this.figure.ctx, H = this.figure.rig.skeleton.index.Head;
    for (let k = 0; k < 3; k++) this.headRest[k] = ctx.rest[H * 3 + k];
    if (!this.base) return;
    const w = ctx.applied; let same = true; for (let l = 0; l < w.length; l++) if (w[l] !== this.weights[l]) same = false; if (same) return;
    this.weights.set(w);
    for (const [name, A] of Object.entries(this.base)) { const X = this[name]; X.set(A); this.growth.forEach((D, l) => { if (w[l]) for (let i = 0; i < X.length; i++) X[i] += w[l] * D[i]; }); }
  }
  // the figure's step: {pose, previous, dt, reset, jump, t}
  step({ dt, reset, jump, t }) {
    const S = this.solids, m = this.m;
    this.grown();
    // (a reset — the first step, a new clip, a scrub — finds the hair as it hangs on the body in this pose: from where
    // it hangs at rest, carried by the head, let settle without speed, so a body unlike the rest's doesn't fling it)
    if (reset || !this.started) {
      S.moment(1, m.now); S.moment(1, m.was); this.place(m.now);
      for (let k = 0; k < SETTLE; k++) this.substep(m.was, m.now, null, true);
      this.v.fill(0); this.started = true; this.left = 0; this.time = t / (this.figure.state?.clip?.fps ?? 30); this.write(); return;
    }
    // (a jump — the clip begun again — carries the hair as it is with the head: it goes on from where it was on it)
    if (jump) this.jumped();
    if (!(dt > 0)) { this.write(); return; }   // (the same moment again: nothing moves)
    // small steps from where the last frame left the hair (this.left behind it) up to this frame, the solids at each
    // small step's moment within the frame (the first from the last one's: the head where the hair last saw it)
    const lag = this.left, n = Math.floor((lag + dt) / H + 1e-9);
    for (let s = 1; s <= n; s++) { [m.was, m.now] = [m.now, m.was]; S.moment(Math.max(0, Math.min(1, (s * H - lag) / dt)), m.now); this.substep(m.was, m.now, this.wind, false); this.time += H; }
    this.left = lag + dt - n * H;
    this.write();
  }
  // everything carried by the head's jump (from where it was before it to where it is now); the velocities as they
  // were against the head's own motion there (the moments of the last small step before the jump), turned with it — on
  // the head, standing still through the jump's frame, the hair swings on as it swung on the head
  jumped() {
    const S = this.solids, { T0, v } = this, a = S.jumped, o = this.q.o, pp = this.q.pp, mw = this.m.was, mn = this.m.now;
    for (let i = 0; i < v.length; i += 3) { this.carry(mn, T0[i], T0[i + 1], T0[i + 2], o); this.carry(mw, T0[i], T0[i + 1], T0[i + 2], pp); for (let d = 0; d < 3; d++) v[i + d] -= (o[d] - pp[d]) / H; }
    const b = S.carrier(S.moment(0, mn)), qi = [-a.q[0], -a.q[1], -a.q[2], a.q[3]];
    const T = [b.q[3] * qi[0] + b.q[0] * qi[3] + b.q[1] * qi[2] - b.q[2] * qi[1], b.q[3] * qi[1] - b.q[0] * qi[2] + b.q[1] * qi[3] + b.q[2] * qi[0], b.q[3] * qi[2] + b.q[0] * qi[1] - b.q[1] * qi[0] + b.q[2] * qi[3], b.q[3] * qi[3] - b.q[0] * qi[0] - b.q[1] * qi[1] - b.q[2] * qi[2]];
    for (const A of [this.x, this.xp]) for (let i = 0; i < A.length; i += 3) { qRot3(T, A[i] - a.p[0], A[i + 1] - a.p[1], A[i + 2] - a.p[2], o); A[i] = o[0] + b.p[0]; A[i + 1] = o[1] + b.p[1]; A[i + 2] = o[2] + b.p[2]; }
    for (let i = 0; i < v.length; i += 3) { qRot3(T, v[i], v[i + 1], v[i + 2], o); v[i] = o[0]; v[i + 1] = o[1]; v[i + 2] = o[2]; }
    S.moment(0, mw);
  }
  // everything where the hairstyle hangs (once found, R0; else the groom), on the head at moment m
  place(m) {
    const R = this.R0 || this.T0, o = this.q.o;
    for (let i = 0; i < this.x.length; i += 3) { this.carry(m, R[i], R[i + 1], R[i + 2], o); this.x[i] = this.xp[i] = o[0]; this.x[i + 1] = this.xp[i + 1] = o[1]; this.x[i + 2] = this.xp[i + 2] = o[2]; }
    this.v.fill(0);
  }

  // a small step from the solids at moment mw to mn
  substep(mw, mn, wind, settle) {
    const { x, xp, v, T0, corr } = this, h = H, q = this.q, o = q.o, w = q.w, r = q.r, pp = q.pp, Q = q.Q, B = q.B, damp = Math.exp(-AIR * h), kw = this.k.wind;
    const zig = 1 - Math.exp(-ZIGZAG * this.k.damping * h);
    for (const ch of this.chains) {
      if (ch.head) continue;
      const a0 = ch.at;
      // the pinned root
      for (let k = 0; k < PIN; k++) { const i = (a0 + k) * 3; xp[i] = x[i]; xp[i + 1] = x[i + 1]; xp[i + 2] = x[i + 2]; this.carry(mn, T0[i], T0[i + 1], T0[i + 2], o); x[i] = o[0]; x[i + 1] = o[1]; x[i + 2] = o[2]; }
      // forces: gravity, the air
      for (let k = PIN; k < ch.n; k++) {
        const i = (a0 + k) * 3;
        if (wind && !settle) windAt(wind, x[i], x[i + 1], x[i + 2], this.time, ch.seed, w); else w[0] = w[1] = w[2] = 0;
        const gain = wind ? ch.gain * kw * WIND : 1;
        let rx = w[0] * gain - v[i], ry = w[1] * gain - v[i + 1], rz = w[2] * gain - v[i + 2];
        const j = i - 3, dx = x[i] - x[j], dy = x[i + 1] - x[j + 1], dz = x[i + 2] - x[j + 2], dl = Math.hypot(dx, dy, dz) || 1, ra = (rx * dx + ry * dy + rz * dz) / dl * 0.7;
        rx -= ra * dx / dl; ry -= ra * dy / dl; rz -= ra * dz / dl;
        const cd = ch.drag * Math.hypot(rx, ry, rz) + 0.5;
        v[i] = (v[i] + cd * rx * h) * damp; v[i + 1] = (v[i + 1] + (cd * ry - G) * h) * damp; v[i + 2] = (v[i + 2] + cd * rz * h) * damp;
        xp[i] = x[i]; xp[i + 1] = x[i + 1]; xp[i + 2] = x[i + 2];
        x[i] += v[i] * h; x[i + 1] += v[i + 1] * h; x[i + 2] += v[i + 2] * h;
      }
      // the groom: toward where the hairstyle has each point, and each segment's bend against the one above
      for (let it = 0; it < 2; it++) {
        for (let k = PIN; k < ch.n; k++) {
          const i = (a0 + k) * 3, g = ch.hold[k]; this.carry(mn, T0[i], T0[i + 1], T0[i + 2], o);
          x[i] += (o[0] - x[i]) * g; x[i + 1] += (o[1] - x[i + 1]) * g; x[i + 2] += (o[2] - x[i + 2]) * g;
        }
        const hq = this.solids.carrier(mn).q; for (let c = 0; c < 4; c++) Q[c] = hq[c];
        for (let k = 0; k < ch.n - 1; k++) {
          const i = (a0 + k) * 3, j = i + 3, t0 = ch.t0[k];
          qRot3(Q, t0[0], t0[1], t0[2], r);
          if (k + 1 >= PIN) {
            const L = ch.L[k], kl = ch.bend[k + 1] * this.drape;
            const ex = (x[i] + r[0] * L - x[j]) * kl, ey = (x[i + 1] + r[1] * L - x[j + 1]) * kl, ez = (x[i + 2] + r[2] * L - x[j + 2]) * kl;
            if (k < PIN) { x[j] += ex; x[j + 1] += ey; x[j + 2] += ez; }
            else { x[j] += ex * 0.5; x[j + 1] += ey * 0.5; x[j + 2] += ez * 0.5; x[i] -= ex * 0.5; x[i + 1] -= ey * 0.5; x[i + 2] -= ez * 0.5; }
          }
          const dx = x[j] - x[i], dy = x[j + 1] - x[i + 1], dz = x[j + 2] - x[i + 2], dl = Math.hypot(dx, dy, dz) || 1;
          turnOn(Q, r, dx / dl, dy / dl, dz / dl, B);
        }
      }
    }
    // the locks held together where they lie together (each pair of neighbouring points no farther apart than LINK
    // past their rest's gap): hair is a mass, its locks part a little, not into ribbons
    if (this.links) this.link();
    for (const ch of this.chains) {
      if (ch.head) continue;
      const a0 = ch.at;
      this.ct.fill(0, a0, a0 + ch.n);
      this.collide(ch, mw, mn, true);
      // lengths: follow the leader, from the root out; the solids again; the lengths again, last (exact, so a lock never
      // stretches; what the solids push out a second time is left to the next small step)
      corr.fill(0, a0 * 3, (a0 + ch.n) * 3);
      this.lengths(ch);
      this.collide(ch, mw, mn, false);
      this.lengths(ch);
      // velocities, with follow-the-leader's correction (the next point's shift taken back), and the hair's own
      // friction: its motion against where the head carries the hairstyle dies down
      const fr = 1 - Math.exp(-ch.inner * h);
      for (let k = PIN; k < ch.n; k++) {
        const i = (a0 + k) * 3, nx = k + 1 < ch.n ? i + 3 : -1;
        this.carry(mn, T0[i], T0[i + 1], T0[i + 2], o); this.carry(mw, T0[i], T0[i + 1], T0[i + 2], pp);
        for (let d = 0; d < 3; d++) { const vv = (x[i + d] - xp[i + d]) / h - (nx >= 0 ? 0.9 * corr[nx + d] / h : 0), vt = (o[d] - pp[d]) / h; v[i + d] = vv - (vv - vt) * fr; }
        // a point a solid pushed out leaves it without the push's speed (no bounce: hair lies on what it meets)
        if (this.ct[a0 + k]) { const c = this.cn, j = (a0 + k) * 3, vn = (v[i] - (o[0] - pp[0]) / h) * c[j] + (v[i + 1] - (o[1] - pp[1]) / h) * c[j + 1] + (v[i + 2] - (o[2] - pp[2]) / h) * c[j + 2]; if (vn > 0) for (let d = 0; d < 3; d++) v[i + d] -= c[j + d] * vn; }
      }
      // a zigzag along the chain (one point against its neighbours) dies at once: real hair bends in curves
      for (let k = PIN; k < ch.n - 1; k++) { const i = (a0 + k) * 3; for (let d = 0; d < 3; d++) v[i + d] += ((v[i - 3 + d] + v[i + 3 + d]) * 0.5 - v[i + d]) * zig; }
      if (settle) v.fill(0, a0 * 3, (a0 + ch.n) * 3);
    }
    if (!settle) this.together(h);
  }
  // neighbouring points of two locks kept within LINK of their gap at rest (beyond it, each pulled half the way back)
  link() {
    const { x, links: K } = this, a = K.a, b = K.b, d0 = K.d0, k = 1 - Math.exp(-LINK_RATE * this.k.together * H);
    for (let e = 0; e < a.length; e++) {
      const i = a[e] * 3, j = b[e] * 3, dx = x[j] - x[i], dy = x[j + 1] - x[i + 1], dz = x[j + 2] - x[i + 2], d = Math.hypot(dx, dy, dz), far = d0[e] * (1 + LINK);
      if (d <= far) continue;
      const f = (d - far) / d * 0.5 * k; x[i] += dx * f; x[i + 1] += dy * f; x[i + 2] += dz * f; x[j] -= dx * f; x[j + 1] -= dy * f; x[j + 2] -= dz * f;
    }
  }
  // hair against hair: each point's velocity drawn toward its neighbours' in the other locks (their weighed mean)
  together(h) {
    const nb = this.nb; if (!nb) return;
    const v = this.v, V = this.vs, f = 1 - Math.exp(-TOGETHER * this.k.together * h);
    V.set(v);
    for (let p = 0; p < nb.of.length; p++) {
      const i = nb.of[p] * 3; let sx = 0, sy = 0, sz = 0, sw = 0;
      for (let e = nb.start[p]; e < nb.start[p + 1]; e++) { const j = nb.with[e] * 3, wt = nb.w[e]; sx += V[j] * wt; sy += V[j + 1] * wt; sz += V[j + 2] * wt; sw += wt; }
      v[i] += (sx / sw - V[i]) * f; v[i + 1] += (sy / sw - V[i + 1]) * f; v[i + 2] += (sz / sw - V[i + 2]) * f;
    }
  }
  // the neighbours of each free point in the other locks: within NEAR at rest, weighed by nearness
  neighbours() {
    const R = this.R0, free = [], of = [], start = [0], wi = [], ww = [];
    for (const [ci, c] of this.chains.entries()) if (!c.head) for (let k = PIN; k < c.n; k++) free.push([c.at + k, ci]);
    for (const [p, ci] of free) {
      for (const [q, cj] of free) {
        if (cj === ci) continue;
        const d = Math.hypot(R[p * 3] - R[q * 3], R[p * 3 + 1] - R[q * 3 + 1], R[p * 3 + 2] - R[q * 3 + 2]);
        if (d < NEAR) { wi.push(q); ww.push(1 - d / NEAR); }
      }
      if (wi.length > start[start.length - 1]) { of.push(p); start.push(wi.length); }
    }
    this.nb = of.length ? { of: Int32Array.from(of), start: Int32Array.from(start), with: Int32Array.from(wi), w: Float64Array.from(ww) } : null;
    // (each pair once, for the links)
    const la = [], lb = [], ld = [];
    for (let p = 0; p < of.length; p++) for (let e = start[p]; e < start[p + 1]; e++) if (wi[e] > of[p]) { la.push(of[p]); lb.push(wi[e]); ld.push(Math.hypot(R[of[p] * 3] - R[wi[e] * 3], R[of[p] * 3 + 1] - R[wi[e] * 3 + 1], R[of[p] * 3 + 2] - R[wi[e] * 3 + 2])); }
    this.links = la.length ? { a: Int32Array.from(la), b: Int32Array.from(lb), d0: Float64Array.from(ld) } : null;
    this.vs = new Float64Array(this.v.length);
  }
  // the head (in its rest space, each point allowed as deep as it lay at rest), the body's skin, the floor; with
  // friction against the solid's own motion (mw → mn: the solids a small step ago and now)
  collide(ch, mw, mn, friction) {
    const { x, xp, solids: S } = this, head = S.head, q = this.q, l = q.l, lp = q.lp, n = q.n, o = q.o, p = q.p, at = q.at, mu = MU * this.k.friction;
    for (let k = PIN; k < ch.n; k++) {
      const i = (ch.at + k) * 3, rad = ch.rad[k];
      if (head) {
        p[0] = x[i]; p[1] = x[i + 1]; p[2] = x[i + 2]; head.local(mn, p, l);
        const d = head.distance(l), limit = ch.allow[k];
        if (d < limit) {
          head.normal(l, n);
          for (let j = 0; j < 3; j++) l[j] += n[j] * (limit - d);
          if (friction) { p[0] = xp[i]; p[1] = xp[i + 1]; p[2] = xp[i + 2]; head.local(mw, p, lp); const dx = l[0] - lp[0], dy = l[1] - lp[1], dz = l[2] - lp[2], dn = dx * n[0] + dy * n[1] + dz * n[2]; l[0] -= (dx - dn * n[0]) * mu; l[1] -= (dy - dn * n[1]) * mu; l[2] -= (dz - dn * n[2]) * mu; }
          head.world(mn, l, o); x[i] = o[0]; x[i + 1] = o[1]; x[i + 2] = o[2];
          this.contact(ch.at + k, head.turn(mn, n, p));
        }
      }
      // the skin between the frames; friction against its own motion in a small step
      if (!this.noBody) {
        const d = S.skin(mn, x[i], x[i + 1], x[i + 2], at) - ch.allowSkin[k];
        if (d < 0) {
          const N = at.n; x[i] -= N[0] * d; x[i + 1] -= N[1] * d; x[i + 2] -= N[2] * d;
          this.contact(ch.at + k, N);
          if (friction) {
            const ux = x[i] - xp[i] - at.v[0] * H, uy = x[i + 1] - xp[i + 1] - at.v[1] * H, uz = x[i + 2] - xp[i + 2] - at.v[2] * H, un = ux * N[0] + uy * N[1] + uz * N[2];
            x[i] -= (ux - un * N[0]) * mu; x[i + 1] -= (uy - un * N[1]) * mu; x[i + 2] -= (uz - un * N[2]) * mu;
          }
        }
      }
      if (x[i + 1] < rad) { x[i + 1] = rad; if (friction) { x[i] -= (x[i] - xp[i]) * FLOOR; x[i + 2] -= (x[i + 2] - xp[i + 2]) * FLOOR; } }
    }
  }
  // follow the leader along a chain (ringlets give like a spring, within limits); each point's shift kept (corr) for
  // the velocity's correction
  lengths(ch) {
    const { x, corr } = this;
    for (let k = PIN; k < ch.n; k++) {
      const i = (ch.at + k) * 3, j = i - 3, L = ch.L[k - 1];
      const dx = x[i] - x[j], dy = x[i + 1] - x[j + 1], dz = x[i + 2] - x[j + 2], dl = Math.hypot(dx, dy, dz) || 1e-9;
      const want = ch.stretch ? Math.min(L * 1.35, Math.max(L * 0.8, dl + (L - dl) * ch.stretch)) : L;
      const nx = x[j] + dx / dl * want, ny = x[j + 1] + dy / dl * want, nz = x[j + 2] + dz / dl * want;
      corr[i] += nx - x[i]; corr[i + 1] += ny - x[i + 1]; corr[i + 2] += nz - x[i + 2];
      x[i] = nx; x[i + 1] = ny; x[i + 2] = nz;
    }
  }
  // a point in contact this small step, and the solid's normal there (world)
  contact(p, n) { this.ct[p] = 1; this.cn[p * 3] = n[0]; this.cn[p * 3 + 1] = n[1]; this.cn[p * 3 + 2] = n[2]; }

  // ———— the rest it hangs in ————
  // where the chains are after some frames on the body at its rest (the solids' rest: that is the body's rest space)
  settled(frames, from = true) {
    const mr = this.m.rest;
    if (from) this.place(mr);
    for (let f = 0; f < frames; f++) for (let s = 0; s < 8; s++) this.substep(mr, mr, null, !this.noSettle);
    this.v.fill(0);
    return Float64Array.from(this.x);
  }
  dirs() {
    for (const c of this.chains) if (!c.head) for (let k = 0; k < c.n - 1; k++) { const i = (c.at + k) * 3, d = [0, 1, 2].map(j => this.T0[i + 3 + j] - this.T0[i + j]), l = Math.hypot(...d) || 1; c.t0[k] = d.map(q => q / l); }
  }
  groom() {
    const D = Float64Array.from(this.T0), free = [];
    for (const c of this.chains) if (!c.head) for (let k = PIN; k < c.n; k++) free.push((c.at + k) * 3);
    this.noBody = true; this.R0 = null;
    let X;
    for (let it = 0; it < GROOM_FIT; it++) {
      X = this.settled(30);
      for (const i of free) for (let d = 0; d < 3; d++) this.T0[i + d] += Math.max(-GROOM_STEP, Math.min(GROOM_STEP, D[i + d] - X[i + d]));
      this.dirs();
    }
    X = this.settled(30);
    this.noBody = false;
    // on the body: first draped over it (the locks' bend eased, so they lie over the shoulders rather than stand off
    // them), then let settle as they are, stiff again — where that leaves them is the rest. The pull toward the design
    // takes the body's settling in; the bend keeps the shape it hangs in free (a lock draped round a shoulder at rest
    // does not keep that curve once the shoulder has moved from under it)
    this.drape = DRAPE; const Y0 = this.settled(90); this.drape = 1;
    for (const i of free) for (let d = 0; d < 3; d++) this.T0[i + d] += Y0[i + d] - X[i + d];
    // (stiff, it lets settle as it would stand: moving, not crept step by step — friction holds a creeping lock where
    // a moving one slides on; again from standing still, until it stays: a lock held on a sloping arm by its own
    // motion slides off when it starts from rest, as every reset starts it)
    this.noSettle = true; let Y = this.settled(150, false);
    for (let k = 0; k < 6; k++) { const Z = this.settled(60, false); let m = 0; for (const i of free) m = Math.max(m, Math.hypot(Z[i] - Y[i], Z[i + 1] - Y[i + 1], Z[i + 2] - Y[i + 2])); Y = Z; if (m < SETTLED) break; }
    this.noSettle = false;
    // (and what it settled to is the rest as it is: the pull's aim moved by it again would pull it on further)
    this.v.fill(0); this.R0 = Y;
    // how far the hanging hair stays from its design, and how far the body moved it (for the checks)
    let sag = 0, body = 0; for (const i of free) { sag = Math.max(sag, Math.hypot(X[i] - D[i], X[i + 1] - D[i + 1], X[i + 2] - D[i + 2])); body = Math.max(body, Math.hypot(Y[i] - X[i], Y[i + 1] - X[i + 1], Y[i + 2] - X[i + 2])); }
    this.rested = { sag, body };
  }

  // ———— the surfaces ————
  // the points as drawn: the roots where the head is now, the free points carried on by their velocity over the part of
  // a small step the frame leaves over (this.left)
  drawn() {
    const { x, v, D, T0, left } = this, o = this.q.o; D.set(x);
    if (!left) return D;
    const end = this.m.end;
    for (const c of this.chains) if (!c.head) for (let k = 0; k < c.n; k++) {
      const i = (c.at + k) * 3;
      if (k < PIN) { this.carry(end, T0[i], T0[i + 1], T0[i + 2], o); D[i] = o[0]; D[i + 1] = o[1]; D[i + 2] = o[2]; }
      else { D[i] += v[i] * left; D[i + 1] += v[i + 1] * left; D[i + 2] += v[i + 2] * left; }
    }
    return D;
  }
  // each node's place and frame now (turned from the rest by the chain's bending, carried down it without twist)
  framesOf(x) {
    const { NX, NR, Qs } = this, end = this.m.end, hq = this.solids.carrier(end).q, hp = this.solids.carrier(end).p, r = this.q.r, Q = this.q.Q, B = this.q.B, M = this.q.M ??= [0, 0, 0, 0, 0, 0, 0, 0, 0], T = [0, 0, 0, 1];
    matOf(hq, M);
    for (const c of this.chains) {
      // (the head's chain: the Head joint's place and turn; a surface on it is offset from the joint's rest place)
      if (c.head) { for (let k = 0; k < c.n; k++) { const i = (c.at + k) * 3; NX[i] = hp[0]; NX[i + 1] = hp[1]; NX[i + 2] = hp[2]; NR.set(M, (c.at + k) * 9); } continue; }
      // each segment's frame carried down the chain without twist; the skin under it (its plane, for the surfaces:
      // onSkin); and where the lock lies on the body as it lay on it at rest, how far it would turn about itself to lie
      // on the skin as it lay then (flat on the back stays flat on it, not edge-on), as much as it lies on it now and lay
      // on it then
      const tw = this.q.tw ??= new Float64Array(64); tw.fill(0, 0, c.n);
      for (let j = 0; j < 4; j++) Q[j] = hq[j];
      for (let k = 0; k < c.n - 1; k++) {
        const i = (c.at + k) * 3, d0 = c.d0[k]; qRot3(Q, d0[0], d0[1], d0[2], r);
        const dx = x[i + 3] - x[i], dy = x[i + 4] - x[i + 1], dz = x[i + 5] - x[i + 2], dl = Math.hypot(dx, dy, dz) || 1;
        turnOn(Q, r, dx / dl, dy / dl, dz / dl, B); Qs.set(Q, (c.at + k) * 4);
        const lay = c.lay[k], mx = (x[i] + x[i + 3]) / 2, my = (x[i + 1] + x[i + 4]) / 2, mz = (x[i + 2] + x[i + 5]) / 2, at = this.q.at, d = this.solids.skin(end, mx, my, mz, at), s3 = (c.at + k) * 3;
        this.under[c.at + k] = d; this.underN[s3] = at.n[0]; this.underN[s3 + 1] = at.n[1]; this.underN[s3 + 2] = at.n[2]; this.underM[s3] = mx; this.underM[s3 + 1] = my; this.underM[s3 + 2] = mz;
        const w = lay ? Math.min(lay.w, 1 - Math.min(1, Math.max(0, d) / LIE)) : 0;
        if (w > 0) {
          const tx = dx / dl, ty = dy / dl, tz = dz / dl, n = lay.n; qRot3(Q, n[0], n[1], n[2], r);
          const pa = r[0] * tx + r[1] * ty + r[2] * tz, ax = r[0] - pa * tx, ay = r[1] - pa * ty, az = r[2] - pa * tz;
          const pb = at.n[0] * tx + at.n[1] * ty + at.n[2] * tz, bx = at.n[0] - pb * tx, by = at.n[1] - pb * ty, bz = at.n[2] - pb * tz;
          tw[k] = Math.atan2((ay * bz - az * by) * tx + (az * bx - ax * bz) * ty + (ax * by - ay * bx) * tz, ax * bx + ay * by + az * bz) * w;
        }
      }
      // (the turn changing no faster than TWIST a segment, from the root on — a sudden turn tears the surface between)
      tw[0] = 0; for (let k = 1; k < c.n - 1; k++) tw[k] = Math.max(tw[k - 1] - TWIST, Math.min(tw[k - 1] + TWIST, tw[k]));
      for (let k = c.n - 3; k >= 0; k--) tw[k] = Math.max(tw[k + 1] - TWIST, Math.min(tw[k + 1] + TWIST, tw[k]));
      for (let k = 0; k < c.n - 1; k++) {
        if (!tw[k]) continue;
        const i = (c.at + k) * 3, q = (c.at + k) * 4, dx = x[i + 3] - x[i], dy = x[i + 4] - x[i + 1], dz = x[i + 5] - x[i + 2], dl = Math.hypot(dx, dy, dz) || 1, sn = Math.sin(tw[k] / 2);
        B[0] = dx / dl * sn; B[1] = dy / dl * sn; B[2] = dz / dl * sn; B[3] = Math.cos(tw[k] / 2);
        const q0 = Qs[q], q1 = Qs[q + 1], q2 = Qs[q + 2], q3 = Qs[q + 3];
        Qs[q] = B[3] * q0 + B[0] * q3 + B[1] * q2 - B[2] * q1; Qs[q + 1] = B[3] * q1 - B[0] * q2 + B[1] * q3 + B[2] * q0; Qs[q + 2] = B[3] * q2 + B[0] * q1 - B[1] * q0 + B[2] * q3; Qs[q + 3] = B[3] * q3 - B[0] * q0 - B[1] * q1 - B[2] * q2;
      }
      for (let k = 0; k < c.n; k++) {
        const i = (c.at + k) * 3, a = (c.at + Math.min(k, c.n - 2)) * 4, b = (c.at + Math.max(0, k - 1)) * 4;
        if (k === 0 || k === c.n - 1) for (let j = 0; j < 4; j++) T[j] = Qs[(k === 0 ? a : b) + j];
        else { const A = [Qs[b], Qs[b + 1], Qs[b + 2], Qs[b + 3]], C = [Qs[a], Qs[a + 1], Qs[a + 2], Qs[a + 3]]; qSlerp(A, C, 0.5, T); }
        matOf(T, M); NR.set(M, (c.at + k) * 9); NX[i] = x[i]; NX[i + 1] = x[i + 1]; NX[i + 2] = x[i + 2];
      }
    }
  }
  // every surface where the chains carry it now: positions, normals (the design's turned with the frames, or the
  // surface's own), strand directions
  write() {
    this.solids.moment(1, this.m.end);
    this.framesOf(this.drawn());
    const { NX, NR, X0, chains } = this, hr = this.headRest;
    for (const M of this.meshes) {
      const o = M.output, m = o.mesh, { c: bc, u: bu, w: bw } = M.bind, P0 = o.rest && o.moved ? o.rest : m.positions, N0 = M.normals === 'design' ? m.shading.normals : null, T0 = m.shading?.tangents ?? null;
      const pos = o.positions, nor = o.normals, tan = o.tangents;
      for (const v of m.used) {
        let X = 0, Y = 0, Z = 0, nx = 0, ny = 0, nz = 0, tx = 0, ty = 0, tz = 0;
        const px = P0[v * 3], py = P0[v * 3 + 1], pz = P0[v * 3 + 2];
        for (let k = 0; k < 3; k++) {
          const w = bw[v * 3 + k]; if (!w) continue;
          const c = chains[bc[v * 3 + k]], u = c.head ? 0 : bu[v * 3 + k], i0 = Math.min(c.n - 2, Math.floor(u)), f = Math.min(1, u - i0), g = 1 - f;
          const A = c.at + i0, a3 = A * 3, b3 = a3 + 3, a9 = A * 9, b9 = a9 + 9;
          // the offset from the chain's rest there (the head's chain: from the Head joint's rest place)
          const rx = c.head ? hr[0] : X0[a3] * g + X0[b3] * f, ry = c.head ? hr[1] : X0[a3 + 1] * g + X0[b3 + 1] * f, rz = c.head ? hr[2] : X0[a3 + 2] * g + X0[b3 + 2] * f;
          const ox = px - rx, oy = py - ry, oz = pz - rz;
          const m0 = NR[a9] * g + NR[b9] * f, m1 = NR[a9 + 1] * g + NR[b9 + 1] * f, m2 = NR[a9 + 2] * g + NR[b9 + 2] * f, m3 = NR[a9 + 3] * g + NR[b9 + 3] * f, m4 = NR[a9 + 4] * g + NR[b9 + 4] * f, m5 = NR[a9 + 5] * g + NR[b9 + 5] * f, m6 = NR[a9 + 6] * g + NR[b9 + 6] * f, m7 = NR[a9 + 7] * g + NR[b9 + 7] * f, m8 = NR[a9 + 8] * g + NR[b9 + 8] * f;
          X += w * (NX[a3] * g + NX[b3] * f + m0 * ox + m3 * oy + m6 * oz); Y += w * (NX[a3 + 1] * g + NX[b3 + 1] * f + m1 * ox + m4 * oy + m7 * oz); Z += w * (NX[a3 + 2] * g + NX[b3 + 2] * f + m2 * ox + m5 * oy + m8 * oz);
          if (N0) { const ax = N0[v * 3], ay = N0[v * 3 + 1], az = N0[v * 3 + 2]; nx += w * (m0 * ax + m3 * ay + m6 * az); ny += w * (m1 * ax + m4 * ay + m7 * az); nz += w * (m2 * ax + m5 * ay + m8 * az); }
          if (T0) { const ax = T0[v * 3], ay = T0[v * 3 + 1], az = T0[v * 3 + 2]; tx += w * (m0 * ax + m3 * ay + m6 * az); ty += w * (m1 * ax + m4 * ay + m7 * az); tz += w * (m2 * ax + m5 * ay + m8 * az); }
        }
        pos[v * 3] = X; pos[v * 3 + 1] = Y; pos[v * 3 + 2] = Z;
        if (N0) { const l = Math.hypot(nx, ny, nz) || 1; nor[v * 3] = nx / l; nor[v * 3 + 1] = ny / l; nor[v * 3 + 2] = nz / l; }
        if (T0) { const l = Math.hypot(tx, ty, tz) || 1; tan[v * 3] = tx / l; tan[v * 3 + 1] = ty / l; tan[v * 3 + 2] = tz / l; }
      }
      this.onSkin(M, pos, bc, bu, bw);
      if (!N0) normalsOf(pos, m.triangles, nor, m.used);
      if (M.edges) partedOf(M, P0, pos, o.parted);
    }
  }
  // the surface lies on the skin, not in it: where a chain lies near the skin, what of its surface went under the skin
  // there (its plane under the segment, the nearer the better) deeper than it lay under it at rest is laid on it — a
  // lock's width over a round shoulder, its side tilted into an arm (the chains themselves are kept out by the solids;
  // these are their surfaces beside them). At rest it may lie as deep in the head's skin as designed, in the body's not.
  onSkin(M, pos, bc, bu, bw) {
    if (this.noBody) return;
    const { chains, under, underN: UN, underM: UM } = this, u = M.output.mesh.used;
    // (each point's segment, and how far under that segment's skin it lies at rest — 0 where the skin is the body's)
    const seg = M.seg ??= Int32Array.from({ length: M.output.mesh.N }, (_, v) => { const c = chains[bc[v * 3]]; return c.head || !bw[v * 3] ? -1 : c.at + Math.min(c.n - 2, Math.floor(bu[v * 3])); });
    const rest = M.restDepth ??= this.restDepth(M, seg);
    for (const v of u) {
      const g = seg[v]; if (g < 0 || !(under[g] < NEAR_SKIN)) continue;
      // (the skin's plane holds only near where it was found: no farther from its foot than NEAR_SKIN)
      const g3 = g * 3, ex = pos[v * 3] - UM[g3], ey = pos[v * 3 + 1] - UM[g3 + 1], ez = pos[v * 3 + 2] - UM[g3 + 2], h = ex * UN[g3] + ey * UN[g3 + 1] + ez * UN[g3 + 2], d = h + under[g] - rest[v];
      if (d < 0 && ex * ex + ey * ey + ez * ez - h * h < NEAR_SKIN * NEAR_SKIN) { pos[v * 3] -= UN[g3] * d; pos[v * 3 + 1] -= UN[g3 + 1] * d; pos[v * 3 + 2] -= UN[g3 + 2] * d; }
    }
  }
  // how far each point of a surface lies under the skin at rest (0 where it is out, or where the skin is the body's)
  restDepth(M, seg) {
    const S = this.solids, mr = this.m.rest, at = this.q.at, P = M.output.mesh.positions, D = new Float32Array(M.output.mesh.N);
    for (const v of M.output.mesh.used) if (seg[v] >= 0) { const d = S.skin(mr, P[v * 3], P[v * 3 + 1], P[v * 3 + 2], at); if (d < 0 && at.head > 0.5) D[v] = d; }
    return D;
  }
}
// a surface's edges, each once (pairs of vertices)
function edgesOf(T) {
  const seen = new Set(), out = [];
  for (let t = 0; t < T.length; t += 3) for (let e = 0; e < 3; e++) { const a = T[t + e], b = T[t + (e + 1) % 3], k = a < b ? a * 4194304 + b : b * 4194304 + a; if (!seen.has(k)) { seen.add(k); out.push(a, b); } }
  return Uint32Array.from(out);
}
// how stretched each point's edges are now against their rest (the most of them; the rest's lengths kept while the rest
// is the same)
function partedOf(M, R, P, out) {
  const E = M.edges;
  if (M.restOf !== R || R !== M.output.mesh.positions) { M.restOf = R; M.l0 = Float32Array.from({ length: E.length / 2 }, (_, k) => { const a = E[k * 2] * 3, b = E[k * 2 + 1] * 3; return Math.hypot(R[a] - R[b], R[a + 1] - R[b + 1], R[a + 2] - R[b + 2]); }); }
  const L0 = M.l0; out.fill(1);
  for (let e = 0; e < E.length; e += 2) {
    const a = E[e] * 3, b = E[e + 1] * 3, l0 = L0[e >> 1]; if (l0 < 1e-6) continue;
    const r = Math.hypot(P[a] - P[b], P[a + 1] - P[b + 1], P[a + 2] - P[b + 2]) / l0;
    if (r > out[E[e]]) out[E[e]] = r; if (r > out[E[e + 1]]) out[E[e + 1]] = r;
  }
}
// Q turned on by the smallest turn taking r to the unit direction (dx, dy, dz): Q ← between(r, d) · Q (B: scratch)
function turnOn(Q, r, dx, dy, dz, B) {
  const d = r[0] * dx + r[1] * dy + r[2] * dz;
  if (d < -0.999999) { const ax = Math.abs(r[0]) < 0.9 ? [0, r[2], -r[1]] : [-r[2], 0, r[0]], l = Math.hypot(...ax); B[0] = ax[0] / l; B[1] = ax[1] / l; B[2] = ax[2] / l; B[3] = 0; }
  else { const cx = r[1] * dz - r[2] * dy, cy = r[2] * dx - r[0] * dz, cz = r[0] * dy - r[1] * dx, w = 1 + d, l = Math.hypot(cx, cy, cz, w); B[0] = cx / l; B[1] = cy / l; B[2] = cz / l; B[3] = w / l; }
  const ax = B[0], ay = B[1], az = B[2], aw = B[3], bx = Q[0], by = Q[1], bz = Q[2], bw = Q[3];
  Q[0] = aw * bx + ax * bw + ay * bz - az * by; Q[1] = aw * by - ax * bz + ay * bw + az * bx; Q[2] = aw * bz + ax * by - ay * bx + az * bw; Q[3] = aw * bw - ax * bx - ay * by - az * bz;
}
// a quaternion's rotation as a matrix, column-major (column k: where axis k goes)
function matOf(q, m) {
  const [x, y, z, w] = q;
  m[0] = 1 - 2 * (y * y + z * z); m[1] = 2 * (x * y + z * w); m[2] = 2 * (x * z - y * w);
  m[3] = 2 * (x * y - z * w); m[4] = 1 - 2 * (x * x + z * z); m[5] = 2 * (y * z + x * w);
  m[6] = 2 * (x * z + y * w); m[7] = 2 * (y * z - x * w); m[8] = 1 - 2 * (x * x + y * y);
  return m;
}
