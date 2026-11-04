// Hair in motion (В1's motion.js, carried onto the engine's figure): every guide is a chain of points rooted on the
// Head joint, moved by position-based dynamics, as games and film do it (TressFX; Müller et al. 2012, "Fast simulation
// of inextensible hair"). A figure's step (src/figure.js) runs it after the floor, from the previous pose to this one in
// small steps of at most 1/240 s; in each:
// - gravity and the air (the wind with its gusts and a turbulence of its own round every lock, less the lock's own
//   velocity, drag as the square of that speed, pushing across a lock more than along it);
// - twice the groom: every point pulled toward where the hairstyle has it, carried by the head; every segment bent back
//   toward its designed angle against the one above — stiffnesses as springs (1/s²), each pass taking k·h²/(1 + k·h²)
//   as XPBD's compliance does;
// - the solids (src/solids.js: the head's shape with its jaw — each point allowed as deep as it lies at rest —, the
//   body's skin as the frame drew it, the floor), with friction against their own motion;
// - lengths kept exactly (follow-the-leader, with its velocity correction; ringlets give like springs);
// - the hair's own friction (its motion against where the head carries the hairstyle dies down) and zigzags along a
//   chain damped.
// The hairstyle was designed as it hangs, so the groom is set against the hair's weight: let hang, the groom moved up by
// how far it sagged, a few times over, until hanging is the design (an inverse of the rest shape, as film pipelines do
// it) — then let settle once on the standing body (over its shoulders, not through them), and that is its rest.
// The surfaces ride the chains: each point bound to up to three chains where it lies (src/hair/build.js bindOf), in
// the chain's frame there (carried down it without twist), blended between neighbouring frames.
//   new HairSim(figure, {guides, meshes: [{output, bind, normals: 'design' | 'surface'}], physics})
//   sim.wind = {speed, dir, gust, turbulence} | null      sim.step(ctx) — the figure's simulation step
import { qRot3, qMul, qBetween, qSlerp, qNorm } from '../math.js';
import { normalsOf } from '../mesh.js';

const G = 9.81, MAX_H = 1 / 240, PIN = 2, MU = 0.35, SETTLE = 60;

// the wind at a point: a steady flow, gusts going through it, and a turbulence of its own round every lock
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
  constructor(figure, { guides, meshes, physics = {} }) {
    this.figure = figure; this.solids = figure.solids(); this.wind = null; this.meshes = meshes; this.outputs = meshes.map(m => m.output);
    const k = { hold: 1, bend: 1, drag: 1, wind: 1, ...physics };
    this.k = k;
    const chains = this.chains = [];
    let N = 0;
    for (const [gi, g] of guides.entries()) {
      const n = g.points.length, c = { n, at: N, head: !!g.head, seed: gi * 1.618, gain: 0.8 + 0.4 * ((gi * 0.618) % 1) };
      if (!g.head) Object.assign(c, { rooted: g.rooted, rad: g.rad, hold: g.hold.map(v => v * k.hold), bend: g.bend.map(v => v * k.bend), drag: g.drag * k.drag, inner: g.inner, stretch: g.stretch });
      chains.push(c); N += n;
    }
    this.N = N;
    this.x = new Float64Array(N * 3); this.cn = new Float64Array(N * 3); this.ct = new Uint8Array(N); this.xp = new Float64Array(N * 3); this.v = new Float64Array(N * 3); this.corr = new Float64Array(N * 3);
    // X0: the guides at rest (the body's rest space); T0: where the groom pulls (moved against the weight); R0: where
    // the hair hangs at rest; NX, NR: each node's place and frame now (for the surfaces)
    this.X0 = new Float64Array(N * 3); guides.forEach((g, gi) => g.points.forEach((p, k) => this.X0.set(p, (chains[gi].at + k) * 3)));
    this.T0 = Float64Array.from(this.X0); this.R0 = null;
    this.NX = new Float64Array(N * 3); this.NR = new Float64Array(N * 9);
    for (const c of chains) {
      if (c.head) continue;
      c.L = []; c.d0 = [];
      for (let k = 0; k < c.n - 1; k++) { const i = (c.at + k) * 3, d = [0, 1, 2].map(j => this.X0[i + 3 + j] - this.X0[i + j]), l = Math.hypot(...d); c.L.push(l); c.d0.push(d.map(q => q / l)); }
      c.t0 = c.d0.map(d => d.slice());
    }
    // how deep each point lies in the head's shape at rest: it may stay that deep (the hairstyle lies as designed)
    const head = this.solids.head, l = [0, 0, 0];   // (at rest a point is in the head's rest space as it is)
    // (and in the skin, where a head without a designed form is its skin)
    this.solids.rest(); const at = { n: [0, 0, 0], v: [0, 0, 0] };
    for (const c of chains) if (!c.head) {
      c.allow = Array.from({ length: c.n }, (_, k) => { if (!head) return 0; for (let j = 0; j < 3; j++) l[j] = this.X0[(c.at + k) * 3 + j]; return Math.min(c.rad[k], head.distance(l) - 0.001); });
      c.allowSkin = Array.from({ length: c.n }, (_, k) => { const i = (c.at + k) * 3; return Math.min(c.rad[k], this.solids.skin(this.X0[i], this.X0[i + 1], this.X0[i + 2], at) - 0.001); });
    }
    this.per = new Map(); this.drape = 1;
    // (the skin's answer at a point; how much of a frame's motion of the skin a small step takes)
    this.skinAt = { n: [0, 0, 0], v: [0, 0, 0] }; this.share = 0;
    this.groom();
    this.time = 0; this.started = false;
  }

  // ———— the head carrying the hairstyle: x' = R (x − J) + P, now or a step ago ————
  carry(t, x, y, z, o) { const r = this.solids.carrier.rest; qRot3(t.q, x - r[0], y - r[1], z - r[2], o); o[0] += t.p[0]; o[1] += t.p[1]; o[2] += t.p[2]; return o; }
  // a stiffness's share of each pass at step h
  shares(h) {
    if (this.per.has(h)) return this.per.get(h);
    const f = k => k * h * h / (1 + k * h * h), out = this.chains.map(c => c.head ? null : { hold: c.hold.map(f), bend: c.bend.map(f) });
    this.per.set(h, out); return out;
  }

  // the figure's step: {pose, previous, dt, reset, t}
  step({ pose, previous, dt, reset, t }) {
    const S = this.solids;
    // (a reset — the first step, a loop, a scrub — finds the hair as it hangs on the body in this pose: from where it
    // hangs at rest, carried by the head, let settle without speed, so a body unlike the rest's doesn't fling it)
    if (reset || !this.started) { S.set(pose, pose, true); this.place(S.carrier.now); for (let k = 0; k < SETTLE; k++) this.substep(1 / 240, null, true); this.v.fill(0); this.started = true; this.time = t / (this.figure.state?.clip?.fps ?? 30); this.write(); return; }
    if (!(dt > 0)) { this.write(); return; }   // (the same moment again: nothing moves)
    const n = Math.max(1, Math.ceil(dt / MAX_H - 1e-6)), h = dt / n;
    S.set(previous, pose); this.share = h / dt;
    for (let s = 1; s <= n; s++) { S.at(s / n); this.substep(h, this.wind, false); this.time += h; }
    this.write();
  }
  // everything where the hairstyle hangs (once found, R0; else the groom), on the head as it is now
  place(H) {
    const R = this.R0 || this.T0, o = [0, 0, 0];
    for (let i = 0; i < this.x.length; i += 3) { this.carry(H, R[i], R[i + 1], R[i + 2], o); this.x[i] = this.xp[i] = o[0]; this.x[i + 1] = this.xp[i + 1] = o[1]; this.x[i + 2] = this.xp[i + 2] = o[2]; }
    this.v.fill(0); this.framesOf();
  }

  substep(h, wind, settle) {
    const { x, xp, v, T0, corr, solids: S } = this, H = S.carrier.now, Hw = S.carrier.was, per = this.shares(h);
    const o = [0, 0, 0], w = [0, 0, 0], r = [0, 0, 0], pp = [0, 0, 0], damp = Math.exp(-0.4 * h), kw = this.k.wind;
    for (const [ci, ch] of this.chains.entries()) {
      if (ch.head) continue;
      const a0 = ch.at, sh = per[ci];
      // the pinned root
      for (let k = 0; k < PIN; k++) { const i = (a0 + k) * 3; xp[i] = x[i]; xp[i + 1] = x[i + 1]; xp[i + 2] = x[i + 2]; this.carry(H, T0[i], T0[i + 1], T0[i + 2], o); x[i] = o[0]; x[i + 1] = o[1]; x[i + 2] = o[2]; }
      // forces: gravity, the air
      for (let k = PIN; k < ch.n; k++) {
        const i = (a0 + k) * 3;
        if (wind && !settle) windAt(wind, x[i], x[i + 1], x[i + 2], this.time, ch.seed, w); else w[0] = w[1] = w[2] = 0;
        const gain = wind ? ch.gain * kw : 1;
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
          const i = (a0 + k) * 3, g = sh.hold[k]; this.carry(H, T0[i], T0[i + 1], T0[i + 2], o);
          x[i] += (o[0] - x[i]) * g; x[i + 1] += (o[1] - x[i + 1]) * g; x[i + 2] += (o[2] - x[i + 2]) * g;
        }
        let Q = H.q;
        for (let k = 0; k < ch.n - 1; k++) {
          const i = (a0 + k) * 3, j = i + 3, t0 = ch.t0[k];
          qRot3(Q, t0[0], t0[1], t0[2], r);
          if (k + 1 >= PIN) {
            const L = ch.L[k], kl = sh.bend[k + 1] * this.drape;
            const ex = (x[i] + r[0] * L - x[j]) * kl, ey = (x[i + 1] + r[1] * L - x[j + 1]) * kl, ez = (x[i + 2] + r[2] * L - x[j + 2]) * kl;
            if (k < PIN) { x[j] += ex; x[j + 1] += ey; x[j + 2] += ez; }
            else { x[j] += ex * 0.5; x[j + 1] += ey * 0.5; x[j + 2] += ez * 0.5; x[i] -= ex * 0.5; x[i + 1] -= ey * 0.5; x[i + 2] -= ez * 0.5; }
          }
          const dx = x[j] - x[i], dy = x[j + 1] - x[i + 1], dz = x[j + 2] - x[i + 2], dl = Math.hypot(dx, dy, dz) || 1;
          Q = qMul(qBetween(r, [dx / dl, dy / dl, dz / dl]), Q);
        }
      }
      this.ct.fill(0, a0, a0 + ch.n);
      this.collide(ch, true);
      // lengths: follow the leader, from the root out; the solids again; the lengths again, last (exact, so a lock never
      // stretches; what the solids push out a second time is left to the next small step)
      corr.fill(0, a0 * 3, (a0 + ch.n) * 3);
      this.lengths(ch);
      this.collide(ch, false);
      this.lengths(ch);
      // velocities, with follow-the-leader's correction (the next point's shift taken back), and the hair's own
      // friction: its motion against where the head carries the hairstyle dies down
      const fr = 1 - Math.exp(-ch.inner * h);
      for (let k = PIN; k < ch.n; k++) {
        const i = (a0 + k) * 3, nx = k + 1 < ch.n ? i + 3 : -1;
        this.carry(H, T0[i], T0[i + 1], T0[i + 2], o); this.carry(Hw, T0[i], T0[i + 1], T0[i + 2], pp);
        const vt3 = [(o[0] - pp[0]) / h, (o[1] - pp[1]) / h, (o[2] - pp[2]) / h];
        for (let d = 0; d < 3; d++) { const vv = (x[i + d] - xp[i + d]) / h - (nx >= 0 ? 0.9 * corr[nx + d] / h : 0), vt = (o[d] - pp[d]) / h; v[i + d] = vv - (vv - vt) * fr; }
        // a point a solid pushed out leaves it without the push's speed (no bounce: hair lies on what it meets)
        if (this.ct[a0 + k]) { const c = this.cn, j = (a0 + k) * 3, vn = (v[i] - vt3[0]) * c[j] + (v[i + 1] - vt3[1]) * c[j + 1] + (v[i + 2] - vt3[2]) * c[j + 2]; if (vn > 0) for (let d = 0; d < 3; d++) v[i + d] -= c[j + d] * vn; }
      }
      // a zigzag along the chain (one point against its neighbours) dies at once: real hair bends in curves
      for (let k = PIN; k < ch.n - 1; k++) { const i = (a0 + k) * 3; for (let d = 0; d < 3; d++) v[i + d] += ((v[i - 3 + d] + v[i + 3 + d]) * 0.5 - v[i + d]) * 0.35; }
      if (settle) v.fill(0, a0 * 3, (a0 + ch.n) * 3);
    }
  }
  // the head (in its rest space, each point allowed as deep as it lay at rest), the body's skin, the floor; with
  // friction against the solid's own motion
  collide(ch, friction) {
    const { x, xp, solids: S } = this, head = S.head, l = [0, 0, 0], lp = [0, 0, 0], n = [0, 0, 0], o = [0, 0, 0], q = [0, 0, 0], at = this.skinAt, share = this.share;
    for (let k = PIN; k < ch.n; k++) {
      const i = (ch.at + k) * 3, rad = ch.rad[k];
      // the head, in its own rest (each point as deep as it lay in it at rest)
      if (head) {
        q[0] = x[i]; q[1] = x[i + 1]; q[2] = x[i + 2]; head.local(q, l);
        const d = head.distance(l), limit = ch.allow[k];
        if (d < limit) {
          head.normal(l, n);
          for (let j = 0; j < 3; j++) l[j] += n[j] * (limit - d);
          if (friction) { q[0] = xp[i]; q[1] = xp[i + 1]; q[2] = xp[i + 2]; head.was(q, lp); const dx = l[0] - lp[0], dy = l[1] - lp[1], dz = l[2] - lp[2], dn = dx * n[0] + dy * n[1] + dz * n[2]; l[0] -= (dx - dn * n[0]) * MU; l[1] -= (dy - dn * n[1]) * MU; l[2] -= (dz - dn * n[2]) * MU; }
          head.world(l, o); x[i] = o[0]; x[i + 1] = o[1]; x[i + 2] = o[2];
          this.contact(ch.at + k, head.turn(n, q));
        }
      }
      // the skin as this frame drew it; friction against its own motion in a small step
      if (!this.noBody) {
        const d = S.skin(x[i], x[i + 1], x[i + 2], at) - ch.allowSkin[k];
        if (d < 0) {
          const N = at.n; x[i] -= N[0] * d; x[i + 1] -= N[1] * d; x[i + 2] -= N[2] * d;
          this.contact(ch.at + k, N);
          if (friction) {
            const ux = x[i] - xp[i] - at.v[0] * share, uy = x[i + 1] - xp[i + 1] - at.v[1] * share, uz = x[i + 2] - xp[i + 2] - at.v[2] * share, un = ux * N[0] + uy * N[1] + uz * N[2];
            x[i] -= (ux - un * N[0]) * MU; x[i + 1] -= (uy - un * N[1]) * MU; x[i + 2] -= (uz - un * N[2]) * MU;
          }
        }
      }
      if (x[i + 1] < rad) { x[i + 1] = rad; if (friction) { x[i] -= (x[i] - xp[i]) * 0.6; x[i + 2] -= (x[i + 2] - xp[i + 2]) * 0.6; } }
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
  // where the chains are, in the head's rest space (the solids at rest: that is the body's rest space)
  settled(frames, from = true) {
    if (from) this.place(this.solids.carrier.now);
    for (let f = 0; f < frames; f++) for (let s = 0; s < 8; s++) this.substep(MAX_H, null, !this.noSettle);
    this.v.fill(0);
    return Float64Array.from(this.x);
  }
  dirs() {
    for (const c of this.chains) if (!c.head) for (let k = 0; k < c.n - 1; k++) { const i = (c.at + k) * 3, d = [0, 1, 2].map(j => this.T0[i + 3 + j] - this.T0[i + j]), l = Math.hypot(...d) || 1; c.t0[k] = d.map(q => q / l); }
  }
  groom() {
    const S = this.solids, D = Float64Array.from(this.T0), free = [];
    S.rest();
    for (const c of this.chains) if (!c.head) for (let k = PIN; k < c.n; k++) free.push((c.at + k) * 3);
    this.noBody = true; this.R0 = null;
    let X;
    for (let it = 0; it < 5; it++) {
      X = this.settled(30);
      for (const i of free) for (let d = 0; d < 3; d++) this.T0[i + d] += Math.max(-0.03, Math.min(0.03, D[i + d] - X[i + d]));
      this.dirs();
    }
    X = this.settled(30);
    this.noBody = false;
    // on the body: first draped over it (the locks' bend eased, so they lie over the shoulders rather than stand off
    // them), then let settle as they are, stiff again — where that leaves them is the rest. The pull toward the design
    // takes the body's settling in; the bend keeps the shape it hangs in free (a lock draped round a shoulder at rest
    // does not keep that curve once the shoulder has moved from under it)
    this.drape = 0.05; const Y0 = this.settled(90); this.drape = 1;
    for (const i of free) for (let d = 0; d < 3; d++) this.T0[i + d] += Y0[i + d] - X[i + d];
    // (stiff, it lets settle as it would stand: moving, not crept step by step — friction holds a creeping lock where
    // a moving one slides on)
    // (again from standing still, until it stays: a lock held on a sloping arm by its own motion slides off when it
    // starts from rest, as every reset starts it)
    this.noSettle = true; let Y = this.settled(150, false);
    for (let k = 0; k < 6; k++) { const Z = this.settled(60, false); let m = 0; for (const i of free) m = Math.max(m, Math.hypot(Z[i] - Y[i], Z[i + 1] - Y[i + 1], Z[i + 2] - Y[i + 2])); Y = Z; if (m < 0.004) break; }
    this.noSettle = false;
    // (and what it settled to is the rest as it is: the pull's aim moved by it again would pull it on further)
    this.v.fill(0); this.R0 = Y;
    // how far the hanging hair stays from its design, and how far the body moved it (for the checks)
    let sag = 0, body = 0; for (const i of free) { sag = Math.max(sag, Math.hypot(X[i] - D[i], X[i + 1] - D[i + 1], X[i + 2] - D[i + 2])); body = Math.max(body, Math.hypot(Y[i] - X[i], Y[i + 1] - X[i + 1], Y[i + 2] - X[i + 2])); }
    this.rested = { sag, body };
  }

  // ———— the surfaces ————
  // each node's place and frame now (turned from the rest by the chain's bending, carried down it without twist)
  framesOf() {
    const { x, NX, NR } = this, H = this.solids.carrier.now, r = [0, 0, 0], hm = matOf(H.q, []);
    for (const c of this.chains) {
      // (the head's chain: the Head joint's place and turn; a surface on it is offset from the joint's rest place)
      if (c.head) { for (let k = 0; k < c.n; k++) { const i = (c.at + k) * 3; NX[i] = H.p[0]; NX[i + 1] = H.p[1]; NX[i + 2] = H.p[2]; NR.set(hm, (c.at + k) * 9); } continue; }
      let Q = H.q; const Qs = [];
      for (let k = 0; k < c.n - 1; k++) {
        const i = (c.at + k) * 3, d0 = c.d0[k]; qRot3(Q, d0[0], d0[1], d0[2], r);
        const dx = x[i + 3] - x[i], dy = x[i + 4] - x[i + 1], dz = x[i + 5] - x[i + 2], dl = Math.hypot(dx, dy, dz) || 1;
        Q = qMul(qBetween(r, [dx / dl, dy / dl, dz / dl]), Q); Qs.push(Q);
      }
      for (let k = 0; k < c.n; k++) {
        const q = k === 0 ? Qs[0] : k === c.n - 1 ? Qs[k - 1] : qNorm(qSlerp(Qs[k - 1], Qs[k], 0.5)), i = (c.at + k) * 3;
        NR.set(matOf(q, []), (c.at + k) * 9); NX[i] = x[i]; NX[i + 1] = x[i + 1]; NX[i + 2] = x[i + 2];
      }
    }
  }
  // every surface where the chains carry it now: positions, normals (the design's turned with the frames, or the
  // surface's own), strand directions
  write() {
    this.framesOf();
    const { NX, NR, X0, chains } = this;
    for (const M of this.meshes) {
      const o = M.output, m = o.mesh, { c: bc, u: bu, w: bw } = M.bind, P0 = m.positions, N0 = M.normals === 'design' ? m.shading.normals : null, T0 = m.shading?.tangents ?? null;
      const pos = o.positions, nor = o.normals, tan = o.tangents;
      for (const v of m.used) {
        let X = 0, Y = 0, Z = 0, nx = 0, ny = 0, nz = 0, tx = 0, ty = 0, tz = 0;
        const px = P0[v * 3], py = P0[v * 3 + 1], pz = P0[v * 3 + 2];
        for (let k = 0; k < 3; k++) {
          const w = bw[v * 3 + k]; if (!w) continue;
          const c = chains[bc[v * 3 + k]], u = c.head ? 0 : bu[v * 3 + k], i0 = Math.min(c.n - 2, Math.floor(u)), f = Math.min(1, u - i0), g = 1 - f;
          const A = c.at + i0, a3 = A * 3, b3 = a3 + 3, a9 = A * 9, b9 = a9 + 9;
          // the offset from the chain's rest there (the head's chain: from the Head joint's rest place)
          const rx = c.head ? this.solids.carrier.rest[0] : X0[a3] * g + X0[b3] * f, ry = c.head ? this.solids.carrier.rest[1] : X0[a3 + 1] * g + X0[b3 + 1] * f, rz = c.head ? this.solids.carrier.rest[2] : X0[a3 + 2] * g + X0[b3 + 2] * f;
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
      if (!N0) normalsOf(pos, m.triangles, nor, m.used);
    }
  }
}
// a quaternion's rotation as a matrix, column-major (column k: where axis k goes)
function matOf(q, m) {
  const [x, y, z, w] = q;
  m[0] = 1 - 2 * (y * y + z * z); m[1] = 2 * (x * y + z * w); m[2] = 2 * (x * z - y * w);
  m[3] = 2 * (x * y - z * w); m[4] = 1 - 2 * (x * x + z * z); m[5] = 2 * (y * z + x * w);
  m[6] = 2 * (x * z + y * w); m[7] = 2 * (y * z - x * w); m[8] = 1 - 2 * (x * x + y * y);
  return m;
}
