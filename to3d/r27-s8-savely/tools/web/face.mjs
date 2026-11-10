// Савелий Петрович's face, a stop-motion puppet's: replacement pieces (the mouth — lips, the dark inside, teeth, the
// moustache over it: header.mouth lists them — and the brows)
// whose shapes are mixed, lids that turn over the glass eyes about each eye's horizontal axis, and the eyes that
// turn in their sockets. The shapes and weights come from tools/build.py (the face pack); the shapes themselves are
// the drawing's own mouth and brows (tools/face.py).
//
// A state: {e: {calm, joy, …} weights, v: {A, O, …} speech mouth weights, sp: 0…1 how much the mouth speaks,
//           blink: 0…1, gaze: [yaw, pitch] degrees in the head (+yaw toward his left, +pitch up), brow: lift 0…1}
// apply(state, rest, out): for every vertex the face moves, out gets its displaced rest position (metres);
// returns the list of moved vertex indices. After skinning, each of them is moved by the head's turn of
// (displaced − rest) — the head is rigid on its joint, so this is exact.

const rot = (v, ax, a) => {           // Rodrigues: v turned about the unit axis ax by a radians
  const c = Math.cos(a), s = Math.sin(a), d = v[0] * ax[0] + v[1] * ax[1] + v[2] * ax[2];
  return [v[0] * c + (ax[1] * v[2] - ax[2] * v[1]) * s + ax[0] * d * (1 - c),
          v[1] * c + (ax[2] * v[0] - ax[0] * v[2]) * s + ax[1] * d * (1 - c),
          v[2] * c + (ax[0] * v[1] - ax[1] * v[0]) * s + ax[2] * d * (1 - c)];
};

export class Face {
  constructor({ header: h, arrays: a }) {
    this.h = h; this.a = a;
    this.faces = h.faces; this.visemes = h.visemes;
    this.moved = [];
    const add = (s, n) => { for (let i = s; i < s + n; i++) this.moved.push(i); };
    for (const p of [...h.mouth, 'brows', 'lashes', 'eyeL', 'eyeR']) add(...h.pieces[p]);
    for (const k of ['L', 'R']) for (const i of a[`lid${k}.idx`]) this.moved.push(i);
    this.moved = [...new Set(this.moved)];
  }

  // the lids' turn (radians; + closes) from the expression mix and the blink
  lids(st) {
    let up = 0, lo = 0;
    for (const [k, w] of Object.entries(st.e || {})) { const x = this.h.expr[k]; if (x) { up += w * Math.max(-0.5, x.up); lo += w * x.lo; } }
    const { eU0, eL0 } = this.h;
    const eU = eU0 - up, eL = eL0 + lo;                  // the margins' elevations now
    const meet = eL + 0.3 * (eU - eL);                   // a blink: the upper lid comes down most of the way
    const b = st.blink || 0;
    return { up: up + b * (eU - meet), lo: lo + b * (meet - eL) };
  }

  apply(st, rest, out) {
    const { h, a } = this;
    const mix = (piece, weights) => {
      const [s, n] = h.pieces[piece];
      const base = a[`${piece}.calm`];
      for (let i = 0; i < n * 3; i++) out[s * 3 + i] = base[i];
      for (const [k, w] of weights) {
        if (!w) continue;
        const S = a[`${piece}.${k}`]; if (!S) continue;
        for (let i = 0; i < n * 3; i++) out[s * 3 + i] += w * (S[i] - base[i]);
      }
    };
    const sp = st.sp || 0;
    const mw = [];
    for (const [k, w] of Object.entries(st.e || {})) mw.push([k, w * (1 - sp)]);
    let cw = 0; for (const [, w] of mw) cw += w;
    for (const [k, w] of Object.entries(st.v || {})) mw.push(['v' + k, w * sp]);
    let tot = cw; for (const [k, w] of Object.entries(st.v || {})) tot += w * sp;
    // weights relative to calm: the calm shape is the base, the rest are differences
    const rel = mw.filter(([k]) => k !== 'calm').map(([k, w]) => [k, w / Math.max(tot, 1e-6)]);
    for (const p of h.mouth) mix(p, rel);
    const bw = Object.entries(st.e || {}).filter(([k]) => k !== 'calm');
    mix('brows', bw);
    if (st.brow) {                                       // a lift of the brows (speech: phrase starts)
      const [s, n] = h.pieces.brows;
      for (let i = s; i < s + n; i++) out[i * 3 + 1] += st.brow * 0.004;
    }
    // lids: the head's own skin round each eye turns about the eye's horizontal axis
    const L = this.lids(st);
    for (const k of ['L', 'R']) {
      const e = h.lids[k], idx = a[`lid${k}.idx`], wU = a[`lid${k}.wU`], wL = a[`lid${k}.wL`];
      for (let j = 0; j < idx.length; j++) {
        const i = idx[j];
        const v = [rest[i * 3] - e.c[0], rest[i * 3 + 1] - e.c[1], rest[i * 3 + 2] - e.c[2]];
        const ang = wU[j] * L.up - wL[j] * L.lo;
        const r = rot(v, e.ax, ang);
        out[i * 3] = e.c[0] + r[0]; out[i * 3 + 1] = e.c[1] + r[1]; out[i * 3 + 2] = e.c[2] + r[2];
      }
    }
    // the lash line goes with the upper lid of its eye (the nearer eye)
    {
      const [s, n] = h.pieces.lashes, lw = a['lash.w'];
      for (let i = s; i < s + n; i++) {
        const k = rest[i * 3] >= 0 ? 'L' : 'R', e = h.lids[k];
        const v = [rest[i * 3] - e.c[0], rest[i * 3 + 1] - e.c[1], rest[i * 3 + 2] - e.c[2]];
        const r = rot(v, e.ax, L.up * lw[i - s]);
        out[i * 3] = e.c[0] + r[0]; out[i * 3 + 1] = e.c[1] + r[1]; out[i * 3 + 2] = e.c[2] + r[2];
      }
    }
    // the eyes turn: yaw about the head's up, pitch about the eye's horizontal axis
    const [gy, gp] = st.gaze || [0, 0];
    for (const k of ['L', 'R']) {
      const [s, n] = h.pieces['eye' + k], c = h.eyes[k], e = h.lids[k];
      for (let i = s; i < s + n; i++) {
        let v = [rest[i * 3] - c[0], rest[i * 3 + 1] - c[1], rest[i * 3 + 2] - c[2]];
        v = rot(v, e.ax, -gp * Math.PI / 180);
        v = rot(v, [0, 1, 0], gy * Math.PI / 180);
        out[i * 3] = c[0] + v[0]; out[i * 3 + 1] = c[1] + v[1]; out[i * 3 + 2] = c[2] + v[2];
      }
    }
    return this.moved;
  }

  // after skinning: positions[i] += R_head · (displaced − rest); M: the head joint's transform, 3×4 rows
  // (the engine's skinner.matrix(pose, Head))
  onto(positions, rest, out, M) {
    for (const i of this.moved) {
      const dx = out[i * 3] - rest[i * 3], dy = out[i * 3 + 1] - rest[i * 3 + 1], dz = out[i * 3 + 2] - rest[i * 3 + 2];
      positions[i * 3] += M[0] * dx + M[1] * dy + M[2] * dz;
      positions[i * 3 + 1] += M[4] * dx + M[5] * dy + M[6] * dz;
      positions[i * 3 + 2] += M[8] * dx + M[9] * dy + M[10] * dz;
    }
  }
}
