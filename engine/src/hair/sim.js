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
//   skin of the neck, trunk, shoulders and upper arms, the body's other capsules, the floor), with friction against
//   their own motion;
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

const G = 9.81, MAX_H = 1 / 240, PIN = 2, MU = 0.35;

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
      if (!g.head) Object.assign(c, { rad: g.rad, hold: g.hold.map(v => v * k.hold), bend: g.bend.map(v => v * k.bend), drag: g.drag * k.drag, inner: g.inner, stretch: g.stretch });
      chains.push(c); N += n;
    }
    this.N = N;
    this.x = new Float64Array(N * 3); this.xp = new Float64Array(N * 3); this.v = new Float64Array(N * 3); this.corr = new Float64Array(N * 3);
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
    for (const c of chains) if (!c.head) c.allow = Array.from({ length: c.n }, (_, k) => { if (!head) return 0; for (let j = 0; j < 3; j++) l[j] = this.X0[(c.at + k) * 3 + j]; return Math.min(c.rad[k], head.distance(l) - 0.001); });
    this.per = new Map(); this.drape = 1;
    // how far from the Head joint the hair can reach (the capsules beyond it are not looked at)
    const hr = this.solids.carrier.rest; this.reach = 0.15;
    for (let i = 0; i < this.X0.length; i += 3) this.reach = Math.max(this.reach, Math.hypot(this.X0[i] - hr[0], this.X0[i + 1] - hr[1], this.X0[i + 2] - hr[2]) + 0.08);
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
    if (reset || !this.started) { S.set(pose, pose); this.nearCaps(); this.place(S.carrier.now); this.started = true; this.time = t / (this.figure.state?.clip?.fps ?? 30); this.write(); return; }
    const n = Math.max(1, Math.ceil(dt / MAX_H - 1e-6)), h = dt / n;
    S.set(previous, pose); this.nearCaps();
    for (let s = 1; s <= n; s++) { S.at(s / n); this.substep(h, this.wind, false); this.time += h; }
    this.write();
  }
  // the capsules the hair can reach this frame (both ends of it)
  nearCaps() {
    const H = this.solids.carrier.now.p, R = this.reach + 0.3, d = (a, b) => { let best = Infinity; for (let t = 0; t <= 1; t += 0.25) best = Math.min(best, Math.hypot(a[0] + (b[0] - a[0]) * t - H[0], a[1] + (b[1] - a[1]) * t - H[1], a[2] + (b[2] - a[2]) * t - H[2])); return best; };
    this.near = this.solids.caps.filter(c => d(c.a, c.b) - Math.max(c.ra, c.rb) < R);
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
      this.collide(ch, true);
      // lengths: follow the leader, from the root out (ringlets give like a spring, within limits)
      for (let k = PIN; k < ch.n; k++) {
        const i = (a0 + k) * 3, j = i - 3, L = ch.L[k - 1];
        const dx = x[i] - x[j], dy = x[i + 1] - x[j + 1], dz = x[i + 2] - x[j + 2], dl = Math.hypot(dx, dy, dz) || 1e-9;
        const want = ch.stretch ? Math.min(L * 1.35, Math.max(L * 0.8, dl + (L - dl) * ch.stretch)) : L;
        const nx = x[j] + dx / dl * want, ny = x[j + 1] + dy / dl * want, nz = x[j + 2] + dz / dl * want;
        corr[i] = nx - x[i]; corr[i + 1] = ny - x[i + 1]; corr[i + 2] = nz - x[i + 2];
        x[i] = nx; x[i + 1] = ny; x[i + 2] = nz;
      }
      this.collide(ch, false);
      // velocities, with follow-the-leader's correction (the next point's shift taken back), and the hair's own
      // friction: its motion against where the head carries the hairstyle dies down
      const fr = 1 - Math.exp(-ch.inner * h);
      for (let k = PIN; k < ch.n; k++) {
        const i = (a0 + k) * 3, nx = k + 1 < ch.n ? i + 3 : -1;
        this.carry(H, T0[i], T0[i + 1], T0[i + 2], o); this.carry(Hw, T0[i], T0[i + 1], T0[i + 2], pp);
        for (let d = 0; d < 3; d++) { const vv = (x[i + d] - xp[i + d]) / h - (nx >= 0 ? 0.9 * corr[nx + d] / h : 0), vt = (o[d] - pp[d]) / h; v[i + d] = vv - (vv - vt) * fr; }
      }
      // a zigzag along the chain (one point against its neighbours) dies at once: real hair bends in curves
      for (let k = PIN; k < ch.n - 1; k++) { const i = (a0 + k) * 3; for (let d = 0; d < 3; d++) v[i + d] += ((v[i - 3 + d] + v[i + 3 + d]) * 0.5 - v[i + d]) * 0.35; }
      if (settle) v.fill(0, a0 * 3, (a0 + ch.n) * 3);
    }
  }
  // the head (in its rest space, each point allowed as deep as it lay at rest), the body's capsules, the floor; with
  // friction against the solid's own motion
  collide(ch, friction) {
    const { x, xp, solids: S } = this, l = [0, 0, 0], lp = [0, 0, 0], n = [0, 0, 0], o = [0, 0, 0], q = [0, 0, 0];
    for (let k = PIN; k < ch.n; k++) {
      const i = (ch.at + k) * 3, rad = ch.rad[k];
      // the head (each point as deep as it lay in it at rest) and the skin's parts, each in its own rest
      for (const part of S.parts) {
        if (this.noBody && !part.head) continue;
        if ((x[i] - part.c[0]) ** 2 + (x[i + 1] - part.c[1]) ** 2 + (x[i + 2] - part.c[2]) ** 2 > (part.r + rad) ** 2) continue;
        q[0] = x[i]; q[1] = x[i + 1]; q[2] = x[i + 2]; part.local(q, l);
        const d = part.distance(l), limit = part.head ? ch.allow[k] : rad;
        if (d >= limit) continue;
        part.normal(l, n);
        for (let j = 0; j < 3; j++) l[j] += n[j] * (limit - d);
        if (friction) { q[0] = xp[i]; q[1] = xp[i + 1]; q[2] = xp[i + 2]; part.was(q, lp); const dx = l[0] - lp[0], dy = l[1] - lp[1], dz = l[2] - lp[2], dn = dx * n[0] + dy * n[1] + dz * n[2]; l[0] -= (dx - dn * n[0]) * MU; l[1] -= (dy - dn * n[1]) * MU; l[2] -= (dz - dn * n[2]) * MU; }
        part.world(l, o); x[i] = o[0]; x[i + 1] = o[1]; x[i + 2] = o[2];
      }
      if (!this.noBody) for (const c of this.near) {
        if ((x[i] - c.m[0]) ** 2 + (x[i + 1] - c.m[1]) ** 2 + (x[i + 2] - c.m[2]) ** 2 > (c.reach + rad) ** 2) continue;
        const d = S.capsule(c, x[i], x[i + 1], x[i + 2], n) - rad; if (d >= 0) continue;
        x[i] -= n[0] * d; x[i + 1] -= n[1] * d; x[i + 2] -= n[2] * d;
        if (friction) {
          const t = n.t, mx = c.a[0] + (c.b[0] - c.a[0]) * t - (c.a0[0] + (c.b0[0] - c.a0[0]) * t), my = c.a[1] + (c.b[1] - c.a[1]) * t - (c.a0[1] + (c.b0[1] - c.a0[1]) * t), mz = c.a[2] + (c.b[2] - c.a[2]) * t - (c.a0[2] + (c.b0[2] - c.a0[2]) * t);
          const ux = x[i] - xp[i] - mx, uy = x[i + 1] - xp[i + 1] - my, uz = x[i + 2] - xp[i + 2] - mz, un = ux * n[0] + uy * n[1] + uz * n[2];
          x[i] -= (ux - un * n[0]) * MU; x[i + 1] -= (uy - un * n[1]) * MU; x[i + 2] -= (uz - un * n[2]) * MU;
        }
      }
      if (x[i + 1] < rad) { x[i + 1] = rad; if (friction) { x[i] -= (x[i] - xp[i]) * 0.6; x[i + 2] -= (x[i + 2] - xp[i + 2]) * 0.6; } }
    }
  }

  // ———— the rest it hangs in ————
  // where the chains are, in the head's rest space (the solids at rest: that is the body's rest space)
  settled(frames) {
    this.place(this.solids.carrier.now);
    for (let f = 0; f < frames; f++) for (let s = 0; s < 4; s++) this.substep(1 / 120, null, true);
    return Float64Array.from(this.x);
  }
  dirs() {
    for (const c of this.chains) if (!c.head) for (let k = 0; k < c.n - 1; k++) { const i = (c.at + k) * 3, d = [0, 1, 2].map(j => this.T0[i + 3 + j] - this.T0[i + j]), l = Math.hypot(...d) || 1; c.t0[k] = d.map(q => q / l); }
  }
  groom() {
    const S = this.solids, D = Float64Array.from(this.T0), free = [];
    S.rest(); this.nearCaps();
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
    this.drape = 0.05; const Y = this.settled(90); this.drape = 1;
    for (const i of free) for (let d = 0; d < 3; d++) this.T0[i + d] += Y[i + d] - X[i + d];
    this.dirs(); this.v.fill(0); this.R0 = Y;
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
