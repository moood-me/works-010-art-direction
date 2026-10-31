// Hair in motion, as games and film do it: every lock's guide curve becomes a chain of points rooted on the Head joint,
// moved by position-based dynamics (after TressFX and "Fast simulation of inextensible hair", Müller et al. 2012):
// - each small step: gravity, the air (the wind with its gusts and a turbulence of its own round every lock, less the
//   lock's own velocity — so the air also damps it), then
// - the groom: every point pulled toward where the hairstyle has it, carried by the head (strong where the lock lies on
//   the skull, fading down the free part), and every segment bent back toward its designed angle against the one
//   above it (stiff at the root, softer toward the tip; stiff all along for short hair);
// - the head, the face, the neck, shoulders, trunk, arms and hands are solid (ellipsoids and capsules from the posed
//   skeleton, with friction), so is the floor;
// - lengths kept exactly (follow-the-leader with its velocity correction), except ringlets, which give like springs;
// - the hairstyle was designed as it hangs: the groom is set against the hair's weight so that hanging it is the
//   design (found by letting it hang and moving the groom up by the sag, a few times over) — nothing sags at rest,
//   and the weight is real: hair hangs down when the head tilts, swings like a pendulum, leans against the wind.
// The lock's surface is carried by its chain: each point of it bound to the chain where it lies, in the frame of the
// chain there (frames carried down the chain without twist), blended between neighbouring frames. Clumps' smaller
// locks ride their clump's chain, a braid is one chain with its strands and tail on it, combed hair, buns and bands
// ride the head. The inner layer between the locks is bound to the locks it lies under, blended by nearness.
import { frames, CRANIUM } from './hair.js';
import { warp } from './fit.js';

export const SUB = 8, FPS = 30;
const G = 9.81;
const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
// quaternions as [x, y, z, w]
const qmul = (a, b) => [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1], a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0], a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3], a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]];
function qrot(q, x, y, z, o = [0, 0, 0]) {
  const tx = 2 * (q[1] * z - q[2] * y), ty = 2 * (q[2] * x - q[0] * z), tz = 2 * (q[0] * y - q[1] * x);
  o[0] = x + q[3] * tx + q[1] * tz - q[2] * ty; o[1] = y + q[3] * ty + q[2] * tx - q[0] * tz; o[2] = z + q[3] * tz + q[0] * ty - q[1] * tx; return o;
}
// the shortest turn taking unit a to unit b
function qbetween(a, b) {
  const d = a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  if (d < -0.9999) { const ax = Math.abs(a[0]) < 0.9 ? [0, -a[2], a[1]] : [-a[1], a[0], 0], l = Math.hypot(...ax); return [ax[0] / l, ax[1] / l, ax[2] / l, 0]; }
  const q = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0], 1 + d], l = Math.hypot(...q);
  return q.map(v => v / l);
}
const qnorm = q => { const l = Math.hypot(...q); return q.map(v => v / l); };
const qslerp = (a, b, t) => {
  let d = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3], s = 1; if (d < 0) { d = -d; s = -1; }
  if (d > 0.9995) return qnorm(a.map((v, i) => v + (s * b[i] - v) * t));
  const th = Math.acos(d), k0 = Math.sin((1 - t) * th) / Math.sin(th), k1 = s * Math.sin(t * th) / Math.sin(th);
  return a.map((v, i) => v * k0 + b[i] * k1);
};
const qmat = (q, m, o) => { // into m at o: column-major 3x3
  const [x, y, z, w] = q;
  m[o] = 1 - 2 * (y * y + z * z); m[o + 1] = 2 * (x * y + z * w); m[o + 2] = 2 * (x * z - y * w);
  m[o + 3] = 2 * (x * y - z * w); m[o + 4] = 1 - 2 * (x * x + z * z); m[o + 5] = 2 * (y * z + x * w);
  m[o + 6] = 2 * (x * z + y * w); m[o + 7] = 2 * (y * z - x * w); m[o + 8] = 1 - 2 * (x * x + y * y);
};
// a rotation matrix (column-major 4x4, as THREE's elements) as a quaternion
function mquat(e) {
  const m00 = e[0], m10 = e[1], m20 = e[2], m01 = e[4], m11 = e[5], m21 = e[6], m02 = e[8], m12 = e[9], m22 = e[10], tr = m00 + m11 + m22;
  let q;
  if (tr > 0) { const s = 0.5 / Math.sqrt(tr + 1); q = [(m21 - m12) * s, (m02 - m20) * s, (m10 - m01) * s, 0.25 / s]; }
  else if (m00 > m11 && m00 > m22) { const s = 2 * Math.sqrt(1 + m00 - m11 - m22); q = [0.25 * s, (m01 + m10) / s, (m02 + m20) / s, (m21 - m12) / s]; }
  else if (m11 > m22) { const s = 2 * Math.sqrt(1 + m11 - m00 - m22); q = [(m01 + m10) / s, 0.25 * s, (m12 + m21) / s, (m02 - m20) / s]; }
  else { const s = 2 * Math.sqrt(1 + m22 - m00 - m11); q = [(m02 + m20) / s, (m12 + m21) / s, 0.25 * s, (m10 - m01) / s]; }
  return qnorm(q);
}
// an ellipsoid's distance (approximate, good near it) and its outward direction at p
function ellDist(p, c, r, n) {
  const qx = (p[0] - c[0]) / r[0], qy = (p[1] - c[1]) / r[1], qz = (p[2] - c[2]) / r[2];
  const k0 = Math.hypot(qx, qy, qz) || 1e-6, gx = qx / r[0], gy = qy / r[1], gz = qz / r[2], k1 = Math.hypot(gx, gy, gz) || 1e-6;
  n[0] = gx / k1; n[1] = gy / k1; n[2] = gz / k1;
  return k0 * (k0 - 1) / k1;
}

// ———— the wind: a steady flow, gusts going through it, and a turbulence of its own round every lock ————
export function windAt(o, x, y, z, t, seed, out) {
  const s = o.speed, d = o.dir, along = x * d[0] + z * d[2];
  const gust = 0.62 + 0.3 * Math.sin(t * 1.3 - along * 1.7) * Math.sin(t * 0.47 + 1.3) + 0.22 * Math.sin(t * 3.1 - along * 4 + seed) * Math.sin(t * 0.9 + seed * 0.7);
  const k = s * gust * (0.85 + 0.3 * Math.sin(seed * 5.1 + t * 0.6));
  out[0] = d[0] * k + 0.32 * s * Math.sin(t * 2.3 + y * 7 + seed * 1.7) * Math.sin(t * 0.8 + seed);
  out[1] = 0.22 * s * Math.sin(t * 2.9 + x * 6 + seed * 2.3) + 0.08 * s;
  out[2] = d[2] * k + 0.32 * s * Math.cos(t * 2.1 + z * 7 + seed * 3.1) * Math.sin(t * 0.7 + seed * 1.3);
  return out;
}

// ———— the rig ————
// built: buildHair's output; fit: fitHead's; joints: {Head, …} indices and rest positions; caps: bodyCapsules
export class HairRig {
  constructor(built, fit, body, caps, o = {}) {
    this.fit = fit; this.body = body; this.caps = caps; this.floor = body.floor;
    const W = warp(fit), wp = p => W(p[0], p[1], p[2], [0, 0, 0]);
    this.headJ = body.names.indexOf('Head');
    const chains = this.chains = [];
    // the head as a chain of two points that never move off it
    chains.push({ head: true, n: 2, pts: [[0, 0, 0], [0, 0, 0]] });
    const groups = new Map(), own = new Map();
    const C = CRANIUM;
    const skullDist = p => { const n = [0, 0, 0]; return ellDist(p, C.c, C.r, n); };
    // a chain along a curve given by its points (in the hair's space) at parameters s
    const makeChain = (curve, dyn, coil) => {
      // resample by length: a point every 2 cm or so
      const acc = [0]; for (let i = 1; i < curve.length; i++) acc.push(acc[i - 1] + Math.hypot(...curve[i].p.map((v, j) => v - curve[i - 1].p[j])));
      const Lt = acc[acc.length - 1], nseg = Math.max(2, Math.min(24, Math.round(Lt / 0.02)));
      const pts = [], ss = [], rad = [];
      for (let k = 0, i = 0; k <= nseg; k++) {
        const a = Lt * k / nseg; while (i < acc.length - 2 && acc[i + 1] < a) i++;
        const f = Math.min(1, Math.max(0, (a - acc[i]) / Math.max(1e-9, acc[i + 1] - acc[i]))), A = curve[i], B = curve[i + 1];
        pts.push(A.p.map((v, j) => v + (B.p[j] - v) * f)); ss.push(A.s + (B.s - A.s) * f); rad.push((A.t + (B.t - A.t) * f));
      }
      // how stiff: short hair holds its shape all along, long hair swings from the root down; heavy (tails, braids)
      // swings slower, the air holds it less
      const L = Lt, heavy = dyn.heavy ? 1 : 0;
      // stiffness as a spring's (acceleration per metre away, 1/s²): what the groom pulls back with, what bends a segment
      // back; each pass of a small step takes its share k·h²/(1 + k·h²), as XPBD's compliance would
      // (short hair barely gives; long hair swings; between, by the length)
      const lg = (a, b) => Math.exp(Math.log(a) + (Math.log(b) - Math.log(a)) * smooth(0.1, 0.3, L));
      const lTip = dyn.lTip ?? (coil ? 600 : heavy ? 600 : lg(6000, 250));
      const gTip = dyn.gTip ?? (heavy ? 8 : lg(3000, 6));
      // where the lock lies on the skull (from the root while it stays near it): held there firmly
      let leave = 0; while (leave < nseg && skullDist(pts[leave + 1]) < 0.03) leave++;
      const kg = [], kl = [], hh = (1 / FPS / SUB) ** 2, per = k => k * hh / (1 + k * hh);
      for (let k = 0; k <= nseg; k++) {
        const a = L * k / nseg, aL = L * leave / nseg, u = smooth(0, 1, (a - aL * 0.5) / Math.max(0.02, L - aL * 0.5));
        kg.push(per(k <= leave ? 20000 : gTip * Math.pow(4000 / gTip, Math.exp(-(a - aL) / (heavy ? 0.03 : 0.06)))));
        kl.push(per(20000 * Math.pow(lTip / 20000, u)));
      }
      const ch = { n: nseg + 1, pts: pts.map(wp), s: ss, rad: rad.map(t => Math.min(0.012, 0.55 * t + 0.002)), kg, kl,
        drag: dyn.drag ?? (heavy ? 0.1 : 0.21), inner: heavy ? 2.5 : 3, stretch: coil ? 0.18 : 0, pin: 2, seed: chains.length * 1.618, L, gain: 0.8 + 0.4 * ((chains.length * 0.618) % 1) };
      chains.push(ch); return chains.length - 1;
    };
    const lockChain = L => {
      if (L.rig === 'head') return 0;
      if (L.rig) return groupChain(L.rig);
      if (L.parent) return lockChain(L.parent);
      if (own.has(L)) return own.get(L);
      const F = frames({ ...L.o, coil: undefined }, 64), dyn = L.o.dyn || {};
      const id = makeChain(F.map(e => ({ p: e.p, s: e.s, t: e.t })), dyn, !!L.o.coil);
      own.set(L, id); return id;
    };
    const groupChain = g => {
      if (groups.has(g)) return groups.get(g);
      const F = frames({ pts: g.guide, w: 0.03, t: 0.012 }, 64);
      const id = makeChain(F.map(e => ({ p: e.p, s: e.s, t: 0.016 })), g.dyn || {}, false);
      groups.set(g, id); return id;
    };
    // (chains are made as the surfaces are bound to them, below; their points are counted after)
    this.meshes = [];
    for (const e of built) {
      const m = e.mesh, nv = m.pos.length / 3, P0 = new Float32Array(nv * 3), N0 = Float32Array.from(m.nor), T0 = m.tan ? Float32Array.from(m.tan) : null;
      const bc = new Int32Array(nv * 3), bu = new Float32Array(nv * 3), bw = new Float32Array(nv * 3), tmp = [0, 0, 0];
      for (let v = 0; v < nv; v++) { W(m.pos[v * 3], m.pos[v * 3 + 1], m.pos[v * 3 + 2], tmp); P0.set(tmp, v * 3); }
      const set = (v, k, c, u, w) => { bc[v * 3 + k] = c; bu[v * 3 + k] = u; bw[v * 3 + k] = w; };
      if (e.lockLayer) {
        for (let v = 0; v < nv; v++) {
          const L = e.locks[m.lockOf[v]], c = lockChain(L);
          if (c === 0) { set(v, 0, 0, 0, 1); continue; }
          const ch = chains[c];
          if (own.get(L) === c) set(v, 0, c, this.paramOfS(ch, m.uv[v * 2 + 1]), 1);
          else set(v, 0, c, this.project(ch, P0, v), 1);
        }
      } else if (!e.locks || !e.locks.length) {
        for (let v = 0; v < nv; v++) set(v, 0, 0, 0, 1);
      } else {
        // the inner layer: bound to what it lies under, the nearest few blended by nearness
        const items = e.items, info = {}, cand = [];
        for (let v = 0; v < nv; v++) {
          const x = m.pos[v * 3], y = m.pos[v * 3 + 1], z = m.pos[v * 3 + 2];
          cand.length = 0; let dmin = 1e9;
          for (const it of items) {
            const ox = Math.max(it.bb[0][0] - x, 0, x - it.bb[1][0]), oy = Math.max(it.bb[0][1] - y, 0, y - it.bb[1][1]), oz = Math.max(it.bb[0][2] - z, 0, z - it.bb[1][2]);
            if (ox + oy + oz > Math.min(dmin + 0.01, 0.04)) continue;
            const d = it.isLock ? it.sdf(x, y, z, info) : it.sdf(x, y, z);
            if (d > dmin + 0.01) continue;
            dmin = Math.min(dmin, d); cand.push({ it, d, s: it.isLock ? info.s : 0 });
          }
          const acc = new Map();
          for (const q of cand) {
            // (sharply: where locks part, the layer parts with them rather than stretching into a web between them)
            if (q.d > dmin + 0.003) continue;
            const w = Math.exp(-(q.d - dmin) / 0.0007);
            let c = 0, u = 0;
            if (q.it.isLock) { c = lockChain(q.it); if (c) u = own.get(q.it) === c ? this.paramOfS(chains[c], q.s) : this.project(chains[c], P0, v); }
            else if (q.it.rig && q.it.rig !== 'head') { c = groupChain(q.it.rig); u = this.project(chains[c], P0, v); }
            const a = acc.get(c) || { w: 0, u: 0 }; a.w += w; a.u += u * w; acc.set(c, a);
          }
          const best = [...acc.entries()].sort((a, b) => b[1].w - a[1].w).slice(0, 3), ws = best.reduce((s, b) => s + b[1].w, 0) || 1;
          if (!best.length) set(v, 0, 0, 0, 1);
          best.forEach(([c, a], k) => set(v, k, c, a.u / a.w, a.w / ws));
        }
      }
      this.meshes.push({ e, nv, P0, N0, T0, bc, bu, bw });
    }
    // the points, all chains together
    let N = 0; for (const c of chains) { c.at = N; N += c.n; }
    this.N = N;
    // the state
    this.x = new Float64Array(N * 3); this.xp = new Float64Array(N * 3); this.v = new Float64Array(N * 3);
    this.X0 = new Float64Array(N * 3); this.T0 = new Float64Array(N * 3); this.corr = new Float64Array(N * 3);
    this.NX = new Float32Array(N * 3); this.NR = new Float32Array(N * 9); this.N0 = new Float32Array(N * 3);
    for (const c of chains) for (let k = 0; k < c.n; k++) { this.X0.set(c.pts[k], (c.at + k) * 3); }
    this.T0.set(this.X0); this.N0.set(this.X0);
    for (const c of chains) {
      if (c.head) continue;
      c.Ld = []; c.d0 = [];
      for (let k = 0; k < c.n - 1; k++) { const a = c.pts[k], b = c.pts[k + 1], d = b.map((q, j) => q - a[j]), l = Math.hypot(...d); c.Ld.push(l); c.d0.push(d.map(q => q / l)); }
      c.Lt = c.Ld.slice(); c.t0 = c.d0.map(d => d.slice());
    }
    this.restDepth();
    this.reset();
  }
  // the chain's parameter (node index + fraction) where its lock's parameter s lies
  paramOfS(ch, s) {
    const S = ch.s; let i = 0; while (i < S.length - 2 && S[i + 1] < s) i++;
    const f = Math.min(1, Math.max(0, (s - S[i]) / Math.max(1e-9, S[i + 1] - S[i])));
    return i + f;
  }
  // the nearest place on a chain (at rest) to point v of P
  project(ch, P, v) {
    const x = P[v * 3], y = P[v * 3 + 1], z = P[v * 3 + 2]; let best = 1e9, u = 0;
    for (let i = 0; i < ch.n - 1; i++) {
      const a = ch.pts[i], b = ch.pts[i + 1], bx = b[0] - a[0], by = b[1] - a[1], bz = b[2] - a[2], L2 = bx * bx + by * by + bz * bz || 1e-9;
      const t = Math.max(0, Math.min(1, ((x - a[0]) * bx + (y - a[1]) * by + (z - a[2]) * bz) / L2));
      const d = (x - a[0] - bx * t) ** 2 + (y - a[1] - by * t) ** 2 + (z - a[2] - bz * t) ** 2;
      if (d < best) { best = d; u = i + t; }
    }
    return u;
  }
  // how deep each point lies in the head's solids at rest: it may stay that deep (the hairstyle lies as designed)
  restDepth() {
    const n = [0, 0, 0];
    for (const c of this.chains) {
      if (c.head) continue;
      c.allowS = []; c.allowF = [];
      for (let k = 0; k < c.n; k++) {
        const p = c.pts[k];
        c.allowS.push(Math.min(c.rad[k], ellDist(p, this.fit.skull.c, this.fit.skull.r, n) - 0.001));
        c.allowF.push(Math.min(c.rad[k], ellDist(p, this.fit.face.c, this.fit.face.r, n) - 0.001));
      }
    }
  }
  reset() { this.started = false; this.t = 0; this.v.fill(0); }

  // ———— the body's pose for a frame: the joints the hair needs, as turns and places ————
  // E: the joint matrices (column-major, rest → posed), from Pose.skin
  jointsOf(E) {
    const need = this.need ??= [this.headJ, ...new Set(this.caps.flatMap(c => [c.ja, c.jb]))];
    const out = {};
    for (const j of need) {
      const e = E[j], J = this.body.J[j];
      out[j] = { q: mquat(e), p: [e[0] * J.x + e[4] * J.y + e[8] * J.z + e[12], e[1] * J.x + e[5] * J.y + e[9] * J.z + e[13], e[2] * J.x + e[6] * J.y + e[10] * J.z + e[14]] };
    }
    return out;
  }
  // the joints between two frames
  between(A, B, u) {
    const out = {};
    for (const j in A) out[j] = { q: qslerp(A[j].q, B[j].q, u), p: A[j].p.map((v, k) => v + (B[j].p[k] - v) * u) };
    return out;
  }
  // a rest point carried by joint j
  carry(Js, j, a, o) { const J = this.body.J[j], s = Js[j]; qrot(s.q, a[0] - J.x, a[1] - J.y, a[2] - J.z, o); o[0] += s.p[0]; o[1] += s.p[1]; o[2] += s.p[2]; return o; }

  // ———— one frame forward: from the joints at its start to those at its end ————
  step(JA, JB, wind, settle = false) {
    if (!this.started) { this.place(JA); this.started = true; this.prevCaps = null; }
    const h = 1 / FPS / SUB;
    for (let s = 1; s <= SUB; s++) this.substep(this.between(JA, JB, s / SUB), h, wind, settle);
    this.t += 1 / FPS;
    this.framesOf(JB);
  }
  // everything where the hairstyle hangs (once found, R0; else the groom), on a head at Js
  place(Js) {
    const o = [0, 0, 0], R = this.R0 || this.T0;
    for (const c of this.chains) for (let k = 0; k < c.n; k++) {
      const i = (c.at + k) * 3; this.carry(Js, this.headJ, [R[i], R[i + 1], R[i + 2]], o);
      this.x[i] = this.xp[i] = o[0]; this.x[i + 1] = this.xp[i + 1] = o[1]; this.x[i + 2] = this.xp[i + 2] = o[2];
    }
    this.v.fill(0); this.framesOf(Js);
  }
  substep(Js, h, wind, settle) {
    const { x, xp, v, T0, corr } = this, hs = Js[this.headJ], qH = hs.q, J = this.body.J[this.headJ];
    // the head: x' = R (x - J) + P
    const head = (a, o) => { qrot(qH, a[0] - J.x, a[1] - J.y, a[2] - J.z, o); o[0] += hs.p[0]; o[1] += hs.p[1]; o[2] += hs.p[2]; return o; };
    const qHi = [-qH[0], -qH[1], -qH[2], qH[3]];
    const toHead = (a, o) => { qrot(qHi, a[0] - hs.p[0], a[1] - hs.p[1], a[2] - hs.p[2], o); o[0] += J.x; o[1] += J.y; o[2] += J.z; return o; };
    const prevHead = this.prevHead || hs, qPi = [-prevHead.q[0], -prevHead.q[1], -prevHead.q[2], prevHead.q[3]];
    const prevCarry = (a, o) => { const J2 = J; qrot(prevHead.q, a[0] - J2.x, a[1] - J2.y, a[2] - J2.z, o); o[0] += prevHead.p[0]; o[1] += prevHead.p[1]; o[2] += prevHead.p[2]; return o; };
    const toPrevHead = (a, o) => { qrot(qPi, a[0] - prevHead.p[0], a[1] - prevHead.p[1], a[2] - prevHead.p[2], o); o[0] += J.x; o[1] += J.y; o[2] += J.z; return o; };
    const gx = 0, gy = -G, gz = 0;
    // the capsules now and a step ago
    const caps = this.caps.map(cp => ({ a: this.carry(Js, cp.ja, cp.a, [0, 0, 0]), b: this.carry(Js, cp.jb, cp.b, [0, 0, 0]), r: cp.r }));
    const prevCaps = this.prevCaps || caps;
    const o = [0, 0, 0], w = [0, 0, 0], n = [0, 0, 0], q = [0, 0, 0], r = [0, 0, 0];
    const damp = Math.exp(-0.4 * h);
    for (const ch of this.chains) {
      const a0 = ch.at;
      if (ch.head) continue;
      if (this.rigid) { const X0 = this.X0; for (let k = 0; k < ch.n; k++) { const i = (a0 + k) * 3; head([X0[i], X0[i + 1], X0[i + 2]], o); x[i] = o[0]; x[i + 1] = o[1]; x[i + 2] = o[2]; } continue; }
      // the pinned root
      for (let k = 0; k < ch.pin; k++) { const i = (a0 + k) * 3; xp[i] = x[i]; xp[i + 1] = x[i + 1]; xp[i + 2] = x[i + 2]; head([T0[i], T0[i + 1], T0[i + 2]], o); x[i] = o[0]; x[i + 1] = o[1]; x[i + 2] = o[2]; }
      // forces: gravity, the air
      for (let k = ch.pin; k < ch.n; k++) {
        const i = (a0 + k) * 3;
        let ax = gx, ay = gy, az = gz;
        if (wind && !settle) windAt(wind, x[i], x[i + 1], x[i + 2], this.t, ch.seed, w); else w[0] = w[1] = w[2] = 0;
        const gain = wind ? ch.gain : 1;
        let rx = w[0] * gain - v[i], ry = w[1] * gain - v[i + 1], rz = w[2] * gain - v[i + 2];
        // the air pushes across a lock more than along it
        const j = i - 3, dx = x[i] - x[j], dy = x[i + 1] - x[j + 1], dz = x[i + 2] - x[j + 2], dl = Math.hypot(dx, dy, dz) || 1, ra = (rx * dx + ry * dy + rz * dz) / dl * 0.7;
        rx -= ra * dx / dl; ry -= ra * dy / dl; rz -= ra * dz / dl;
        // drag as the square of the speed through the air (light wind leans long hair some 20°, strong wind 60°),
        // and a little that goes as the speed itself
        const rl = Math.hypot(rx, ry, rz), cd = ch.drag * rl + 0.5;
        ax += cd * rx; ay += cd * ry; az += cd * rz;
        v[i] = (v[i] + ax * h) * damp; v[i + 1] = (v[i + 1] + ay * h) * damp; v[i + 2] = (v[i + 2] + az * h) * damp;
        xp[i] = x[i]; xp[i + 1] = x[i + 1]; xp[i + 2] = x[i + 2];
        x[i] += v[i] * h; x[i + 1] += v[i + 1] * h; x[i + 2] += v[i + 2] * h;
      }
      // the groom: toward where the hairstyle has each point, and each segment's bend against the one above
      for (let it = 0; it < 2; it++) {
        for (let k = ch.pin; k < ch.n; k++) {
          const i = (a0 + k) * 3; head([T0[i], T0[i + 1], T0[i + 2]], o); const g = ch.kg[k];
          x[i] += (o[0] - x[i]) * g; x[i + 1] += (o[1] - x[i + 1]) * g; x[i + 2] += (o[2] - x[i + 2]) * g;
        }
        let Q = qH;
        for (let k = 0; k < ch.n - 1; k++) {
          const i = (a0 + k) * 3, j = i + 3, t0 = ch.t0[k];
          qrot(Q, t0[0], t0[1], t0[2], r);
          if (k + 1 >= ch.pin) {
            const L = ch.Lt[k], kl = ch.kl[k + 1];
            const ex = (x[i] + r[0] * L - x[j]) * kl, ey = (x[i + 1] + r[1] * L - x[j + 1]) * kl, ez = (x[i + 2] + r[2] * L - x[j + 2]) * kl;
            if (k < ch.pin) { x[j] += ex; x[j + 1] += ey; x[j + 2] += ez; }
            else { x[j] += ex * 0.5; x[j + 1] += ey * 0.5; x[j + 2] += ez * 0.5; x[i] -= ex * 0.5; x[i + 1] -= ey * 0.5; x[i + 2] -= ez * 0.5; }
          }
          const dx = x[j] - x[i], dy = x[j + 1] - x[i + 1], dz = x[j + 2] - x[i + 2], dl = Math.hypot(dx, dy, dz) || 1;
          Q = qmul(qbetween(r, [dx / dl, dy / dl, dz / dl]), Q);
        }
      }
      // solids
      this.collide(ch, caps, prevCaps, toHead, toPrevHead, head, true);
      // lengths: follow the leader, from the root out (ringlets give like a spring, within limits)
      for (let k = ch.pin; k < ch.n; k++) {
        const i = (a0 + k) * 3, j = i - 3, L = ch.Lt[k - 1];
        const dx = x[i] - x[j], dy = x[i + 1] - x[j + 1], dz = x[i + 2] - x[j + 2], dl = Math.hypot(dx, dy, dz) || 1e-9;
        let want = L;
        if (ch.stretch) want = Math.min(L * 1.35, Math.max(L * 0.8, dl + (L - dl) * ch.stretch));
        const nx = x[j] + dx / dl * want, ny = x[j + 1] + dy / dl * want, nz = x[j + 2] + dz / dl * want;
        corr[i] = nx - x[i]; corr[i + 1] = ny - x[i + 1]; corr[i + 2] = nz - x[i + 2];
        x[i] = nx; x[i + 1] = ny; x[i + 2] = nz;
      }
      this.collide(ch, caps, prevCaps, toHead, toPrevHead, head, false);
      // velocities, with follow-the-leader's correction (the next point's shift taken back), and the hair's own
      // friction: its motion against where the head carries the hairstyle dies down (a swing ends, the head's motion
      // is not slowed)
      const fr = 1 - Math.exp(-ch.inner * h), pp = [0, 0, 0];
      for (let k = ch.pin; k < ch.n; k++) {
        const i = (a0 + k) * 3, nx = k + 1 < ch.n ? i + 3 : -1, sd = 0.9;
        head([T0[i], T0[i + 1], T0[i + 2]], o); prevCarry([T0[i], T0[i + 1], T0[i + 2]], pp);
        for (let d = 0; d < 3; d++) { const vv = (x[i + d] - xp[i + d]) / h - (nx >= 0 ? sd * corr[nx + d] / h : 0), vt = (o[d] - pp[d]) / h; v[i + d] = vv - (vv - vt) * fr; }
      }
      // a zigzag along the chain (one point against its neighbours) dies at once: real hair bends in curves
      for (let k = ch.pin; k < ch.n - 1; k++) {
        const i = (a0 + k) * 3;
        for (let d = 0; d < 3; d++) v[i + d] += ((v[i - 3 + d] + v[i + 3 + d]) * 0.5 - v[i + d]) * 0.35;
      }
      if (settle) v.fill(0, a0 * 3, (a0 + ch.n) * 3);   // (settling: straight to where it rests)
    }
    this.prevCaps = caps; this.prevHead = hs;
  }
  // the head (in its own rest space: skull and face, each point allowed as deep as it lies at rest), the body's
  // capsules and the floor; friction against the solid's own motion
  collide(ch, caps, prevCaps, toHead, toPrevHead, head, friction) {
    const { x, xp } = this, a0 = ch.at, sk = this.fit.skull, fc = this.fit.face, n = [0, 0, 0], p = [0, 0, 0], pp = [0, 0, 0], o = [0, 0, 0];
    const mu = 0.35;
    for (let k = ch.pin; k < ch.n; k++) {
      const i = (a0 + k) * 3, rad = ch.rad[k];
      // the head
      toHead([x[i], x[i + 1], x[i + 2]], p); let hit = false;
      for (const [E, allow] of [[sk, ch.allowS[k]], [fc, ch.allowF[k]]]) {
        const d = ellDist(p, E.c, E.r, n);
        if (d < allow) { p[0] += n[0] * (allow - d); p[1] += n[1] * (allow - d); p[2] += n[2] * (allow - d); hit = true; }
      }
      if (hit) {
        if (friction) { toPrevHead([xp[i], xp[i + 1], xp[i + 2]], pp); const dx = p[0] - pp[0], dy = p[1] - pp[1], dz = p[2] - pp[2], dn = dx * n[0] + dy * n[1] + dz * n[2]; p[0] -= (dx - dn * n[0]) * mu; p[1] -= (dy - dn * n[1]) * mu; p[2] -= (dz - dn * n[2]) * mu; }
        head(p, o); x[i] = o[0]; x[i + 1] = o[1]; x[i + 2] = o[2];
      }
      // the body
      for (let c = 0; c < (this.noBody ? 0 : caps.length); c++) {
        const C = caps[c], A = C.a, B = C.b, bx = B[0] - A[0], by = B[1] - A[1], bz = B[2] - A[2], L2 = bx * bx + by * by + bz * bz || 1e-9;
        const qx = x[i] - A[0], qy = x[i + 1] - A[1], qz = x[i + 2] - A[2], t = Math.max(0, Math.min(1, (qx * bx + qy * by + qz * bz) / L2));
        const dx = qx - bx * t, dy = qy - by * t, dz = qz - bz * t, dl = Math.hypot(dx, dy, dz), R = C.r + rad;
        if (dl >= R || dl < 1e-9) continue;
        const nx = dx / dl, ny = dy / dl, nz = dz / dl, push = R - dl;
        x[i] += nx * push; x[i + 1] += ny * push; x[i + 2] += nz * push;
        if (friction) {
          const P = prevCaps[c], mx = (A[0] + bx * t) - (P.a[0] + (P.b[0] - P.a[0]) * t), my = (A[1] + by * t) - (P.a[1] + (P.b[1] - P.a[1]) * t), mz = (A[2] + bz * t) - (P.a[2] + (P.b[2] - P.a[2]) * t);
          const ux = x[i] - xp[i] - mx, uy = x[i + 1] - xp[i + 1] - my, uz = x[i + 2] - xp[i + 2] - mz, un = ux * nx + uy * ny + uz * nz;
          x[i] -= (ux - un * nx) * mu; x[i + 1] -= (uy - un * ny) * mu; x[i + 2] -= (uz - un * nz) * mu;
        }
      }
      // the floor
      const fl = this.floor + rad;
      if (x[i + 1] < fl) { x[i + 1] = fl; if (friction) { x[i] -= (x[i] - xp[i]) * 0.6; x[i + 2] -= (x[i + 2] - xp[i + 2]) * 0.6; } }
    }
  }
  // where the chains are now, in the head's rest space
  headSpace(Js) {
    const o = [0, 0, 0], hs = Js[this.headJ], J = this.body.J[this.headJ], qi = [-hs.q[0], -hs.q[1], -hs.q[2], hs.q[3]], out = new Float64Array(this.x.length);
    for (let i = 0; i < this.x.length; i += 3) { qrot(qi, this.x[i] - hs.p[0], this.x[i + 1] - hs.p[1], this.x[i + 2] - hs.p[2], o); out[i] = o[0] + J.x; out[i + 1] = o[1] + J.y; out[i + 2] = o[2] + J.z; }
    return out;
  }
  settleAt(Js, frames) { this.R0 = null; this.place(Js); for (let f = 0; f < frames; f++) this.step(Js, Js, null, true); return this.headSpace(Js); }
  // each segment's direction in the groom from its points
  dirs() {
    for (const c of this.chains) {
      if (c.head) continue;
      for (let k = 0; k < c.n - 1; k++) { const i = (c.at + k) * 3, d = [0, 1, 2].map(j => this.T0[i + 3 + j] - this.T0[i + j]), l = Math.hypot(...d) || 1; c.t0[k] = d.map(q => q / l); }
    }
  }
  // The hairstyle is designed as it hangs, under its own weight. So the groom the simulation pulls toward is set a
  // little against the weight — found by letting it hang, seeing how far it sagged from the design and moving the
  // groom up by as much, a few times over — so that hanging, it is the design (an inverse of the rest shape, as film
  // pipelines do it). Then, standing on this body, the hair settles over its shoulders and back, not through them,
  // and the groom takes on that change too.
  groom(Js) {
    const D = Float64Array.from(this.T0), free = [];
    for (const c of this.chains) if (!c.head) for (let k = c.pin; k < c.n; k++) free.push((c.at + k) * 3);
    this.noBody = true;
    let X;
    for (let it = 0; it < 5; it++) {
      X = this.settleAt(Js, 30);
      for (const i of free) for (let d = 0; d < 3; d++) this.T0[i + d] += Math.max(-0.03, Math.min(0.03, D[i + d] - X[i + d]));
      this.dirs();
    }
    X = this.settleAt(Js, 30);
    this.noBody = false;
    const Y = this.settleAt(Js, 45);
    for (const i of free) for (let d = 0; d < 3; d++) this.T0[i + d] += Y[i + d] - X[i + d];
    this.dirs(); this.v.fill(0); this.R0 = Y;
    // how far the hanging hair stays from its design (for checking)
    let worst = 0; for (const i of free) worst = Math.max(worst, Math.hypot(X[i] - D[i], X[i + 1] - D[i + 1], X[i + 2] - D[i + 2]));
    return worst;
  }
  // each node's place and frame (turned from the design by the chain's bending, carried down it without twist)
  framesOf(Js) {
    const { x, NX, NR } = this, hs = Js[this.headJ], qH = hs.q, J = this.body.J[this.headJ], r = [0, 0, 0];
    for (const c of this.chains) {
      if (c.head) {
        const t = qrot(qH, -J.x, -J.y, -J.z); for (let k = 0; k < 2; k++) { NX.set([t[0] + hs.p[0], t[1] + hs.p[1], t[2] + hs.p[2]], (c.at + k) * 3); qmat(qH, NR, (c.at + k) * 9); }
        this.N0.fill(0, c.at * 3, c.at * 3 + 6);
        continue;
      }
      let Q = qH; const Qs = [];
      for (let k = 0; k < c.n - 1; k++) {
        const i = (c.at + k) * 3, d0 = c.d0[k]; qrot(Q, d0[0], d0[1], d0[2], r);
        const dx = x[i + 3] - x[i], dy = x[i + 4] - x[i + 1], dz = x[i + 5] - x[i + 2], dl = Math.hypot(dx, dy, dz) || 1;
        Q = qmul(qbetween(r, [dx / dl, dy / dl, dz / dl]), Q); Qs.push(Q);
      }
      for (let k = 0; k < c.n; k++) {
        const q = k === 0 ? Qs[0] : k === c.n - 1 ? Qs[k - 1] : qnorm(qslerp(Qs[k - 1], Qs[k], 0.5));
        qmat(q, NR, (c.at + k) * 9); const i = (c.at + k) * 3; NX[i] = x[i]; NX[i + 1] = x[i + 1]; NX[i + 2] = x[i + 2];
      }
    }
  }
  // the surfaces where the chains have them now: into pos, nor, tan (Float32Arrays of the mesh's size); and the
  // occlusion (baked at rest, ao0 → ao): where the hair has left where it lay, what hid it no longer does
  skin(mi, pos, nor, tan, ao0, ao, moved) {
    const M = this.meshes[mi], { NX, NR, N0 } = this, { P0, N0: Nr, T0, bc, bu, bw } = M;
    const ch = this.chains;
    for (let v = 0; v < M.nv; v++) {
      let X = 0, Y = 0, Z = 0, nx = 0, ny = 0, nz = 0, tx = 0, ty = 0, tz = 0;
      const px = P0[v * 3], py = P0[v * 3 + 1], pz = P0[v * 3 + 2], ax = Nr[v * 3], ay = Nr[v * 3 + 1], az = Nr[v * 3 + 2];
      const sx = T0 ? T0[v * 3] : 0, sy = T0 ? T0[v * 3 + 1] : 0, sz = T0 ? T0[v * 3 + 2] : 0;
      for (let k = 0; k < 3; k++) {
        const w = bw[v * 3 + k]; if (!w) continue;
        const c = ch[bc[v * 3 + k]], u = bu[v * 3 + k], i0 = Math.min(c.n - 2, Math.floor(u)), f = Math.min(1, u - i0), g = 1 - f;
        const A = c.at + i0, B = A + 1, a3 = A * 3, b3 = B * 3, a9 = A * 9, b9 = B * 9;
        const ox = px - (N0[a3] * g + N0[b3] * f), oy = py - (N0[a3 + 1] * g + N0[b3 + 1] * f), oz = pz - (N0[a3 + 2] * g + N0[b3 + 2] * f);
        const m0 = NR[a9] * g + NR[b9] * f, m1 = NR[a9 + 1] * g + NR[b9 + 1] * f, m2 = NR[a9 + 2] * g + NR[b9 + 2] * f;
        const m3 = NR[a9 + 3] * g + NR[b9 + 3] * f, m4 = NR[a9 + 4] * g + NR[b9 + 4] * f, m5 = NR[a9 + 5] * g + NR[b9 + 5] * f;
        const m6 = NR[a9 + 6] * g + NR[b9 + 6] * f, m7 = NR[a9 + 7] * g + NR[b9 + 7] * f, m8 = NR[a9 + 8] * g + NR[b9 + 8] * f;
        X += w * (NX[a3] * g + NX[b3] * f + m0 * ox + m3 * oy + m6 * oz);
        Y += w * (NX[a3 + 1] * g + NX[b3 + 1] * f + m1 * ox + m4 * oy + m7 * oz);
        Z += w * (NX[a3 + 2] * g + NX[b3 + 2] * f + m2 * ox + m5 * oy + m8 * oz);
        nx += w * (m0 * ax + m3 * ay + m6 * az); ny += w * (m1 * ax + m4 * ay + m7 * az); nz += w * (m2 * ax + m5 * ay + m8 * az);
        if (T0) { tx += w * (m0 * sx + m3 * sy + m6 * sz); ty += w * (m1 * sx + m4 * sy + m7 * sz); tz += w * (m2 * sx + m5 * sy + m8 * sz); }
      }
      pos[v * 3] = X; pos[v * 3 + 1] = Y; pos[v * 3 + 2] = Z;
      if (ao) {
        const hx = NX[0] + NR[0] * px + NR[3] * py + NR[6] * pz - X, hy = NX[1] + NR[1] * px + NR[4] * py + NR[7] * pz - Y, hz = NX[2] + NR[2] * px + NR[5] * py + NR[8] * pz - Z;
        const t = Math.min(1, Math.max(0, (Math.hypot(hx, hy, hz) - 0.01) / 0.05)), a = ao0[v];
        const e = t * t * (3 - 2 * t);
        ao[v] = a + (Math.max(a, 0.8) - a) * e;
        if (moved) moved[v] = e;
      }
      const nl = Math.hypot(nx, ny, nz) || 1; nor[v * 3] = nx / nl; nor[v * 3 + 1] = ny / nl; nor[v * 3 + 2] = nz / nl;
      if (T0 && tan) { const tl = Math.hypot(tx, ty, tz) || 1; tan[v * 3] = tx / tl; tan[v * 3 + 1] = ty / tl; tan[v * 3 + 2] = tz / tl; }
    }
  }
}
