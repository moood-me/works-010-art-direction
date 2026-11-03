// Т1's proportions (experiments/form: `proportions`, `placeIn`) and its caricature (`averageBody`), on the rest only
// (they move joints: the skeleton itself gets other bones).
//   proportions  each part's length and width: {parts: {torso, neck, head, clav, arm, fore, hand, thigh, shin, foot:
//                {length, width}}} (head: `size`, both at once). Each part is laid along its bone in its own frame;
//                a longer bone carries everything below it along (its children start where it now ends), a wider part
//                is wider about its bone; a point between two parts goes by its share of each — so the joints move
//                with the skin. The neck grows along the torso's own line (up the body),
//                so a longer neck lifts the head rather than pushing it forwards. The strength scales each factor (1 + (k − 1)·strength).
//   caricature   the body's own difference from an average body, drawn out (strength > 0) or taken back (< 0): every
//                point and joint moved by strength × (it − the average), the average made of `of` (moood's seven by
//                default) each scaled to this body's height about its own pelvis's line and its floor, set on this
//                one's. On bodies of one topology only.
import { register } from '../deform.js';
import { local, smoothField } from '../regions.js';

const num = (min, max) => ({ type: 'number', min, max });
const KINDS = ['torso', 'neck', 'head', 'clav', 'arm', 'fore', 'hand', 'thigh', 'shin', 'foot'];
const part = { type: 'object', props: { length: num(0.2, 4), width: num(0.2, 4), size: num(0.2, 4) } };

register({
  kind: 'proportions', of: 'skin',
  params: { parts: { type: 'object', props: Object.fromEntries(KINDS.map(k => [k, part])) } },
  defaults: { parts: {} },
  rest(p, R) {
    const s = p.strength, k = v => 1 + ((v ?? 1) - 1) * s;
    const PR = R.segs.map(g => {
      const q = p.parts[g.kind] || {};
      return g.kind === 'head' ? { len: k(q.size ?? q.length), wid: k(q.size ?? q.width) } : { len: k(q.length), wid: k(q.width) };
    });
    const J = R.rig.joints, at = j => [J[j * 3], J[j * 3 + 1], J[j * 3 + 2]], F = R.frames, newA = [], up = F[R.index.torso].e;
    const placeIn = (si, x, y, z, out) => {
      const f = F[si], [t, u, w] = local(f, x, y, z), pr = PR[si], o = newA[si];
      const L = t * f.L, neck = R.segs[si].kind === 'neck';
      for (let c = 0; c < 3; c++) out[c] = o[c] + (neck ? f.e[c] * L + up[c] * L * (pr.len - 1) : f.e[c] * L * pr.len) + f.u[c] * u * pr.wid + f.w[c] * w * pr.wid;
      return out;
    };
    R.segs.forEach((g, i) => { const a = at(g.a); newA[i] = g.parentIndex >= 0 ? placeIn(g.parentIndex, a[0], a[1], a[2], [0, 0, 0]) : a; });
    const joints = new Float64Array(J.length), tmp = [0, 0, 0];
    for (let j = 0; j < R.rig.J; j++) {
      const si = R.jseg[j], g = R.segs[si], q = j === g.a ? newA[si] : placeIn(si, J[j * 3], J[j * 3 + 1], J[j * 3 + 2], tmp);
      joints[j * 3] = q[0]; joints[j * 3 + 1] = q[1]; joints[j * 3 + 2] = q[2];
    }
    const P = R.mesh.positions, out = Float32Array.from(P);
    for (const i of R.mesh.used) {
      let x = 0, y = 0, z = 0;
      for (let h = 0; h < 2; h++) {
        const si = R.seg[i * 2 + h], w = R.sw[i * 2 + h]; if (w < 1e-4) continue;
        placeIn(si, P[i * 3], P[i * 3 + 1], P[i * 3 + 2], tmp); x += w * tmp[0]; y += w * tmp[1]; z += w * tmp[2];
      }
      out[i * 3] = x; out[i * 3 + 1] = y; out[i * 3 + 2] = z;
    }
    // where two parts meet (an armpit between the trunk and a longer collarbone) their placements differ: the move,
    // smoothed a little over the surface, so no pinch is left there
    // (only there: inside a part the move is its part's own similarity, which smoothing over a fine mesh — a finger, a
    // toe — would only spoil)
    const disp = Float32Array.from(out, (v, i) => v - P[i]), seam = new Uint8Array(R.mesh.N);
    for (const i of R.mesh.used) if (R.seg[i * 2] !== R.seg[i * 2 + 1] && R.sw[i * 2 + 1] > 0.02) seam[i] = 1;
    smoothField(disp, 3, R.nb, 6, grow(seam, R.nb, 4));
    for (const i of R.mesh.used) for (let c = 0; c < 3; c++) out[i * 3 + c] = P[i * 3 + c] + disp[i * 3 + c];
    return { positions: out, joints };
  },
});

const MOOOD = ['moood-woman', 'moood-man', 'moood-girl', 'moood-boy', 'moood-child', 'moood-oldwoman', 'moood-oldman'];
register({
  kind: 'caricature', of: 'skin',
  params: { of: { type: 'array', min: 1, items: { type: 'string', pattern: /^[A-Za-z0-9_.-]+(@[0-9a-f]{12,64})?$/ } } },
  defaults: { of: MOOOD },
  async prepare(p, E, body) {
    const bodies = await Promise.all(p.of.map(E.body));
    for (const b of bodies) if (b.topology !== body.topology) throw new Error(`caricature: ${b.id} is on topology ${b.topology}, not ${body.topology}`);
    return bodies;
  },
  rest(p, R, { data }) {
    const N = R.mesh.N, P = R.mesh.positions, J = R.rig.joints, H = R.height, y0 = R.levels.floor, h = R.skeleton.index.Hips;
    const avgP = new Float64Array(N * 3), avgJ = new Float64Array(J.length), o = [J[h * 3], y0, J[h * 3 + 2]];
    // each body scaled to this one's height about its own pelvis's line and floor, set on this one's
    for (const b of data) {
      const m = b.measures, k = H / m.height, bp = b.mesh.positions, bj = b.rig.joints, bo = [bj[h * 3], m.floor, bj[h * 3 + 2]];
      for (let i = 0; i < N * 3; i++) avgP[i] += (o[i % 3] + (bp[i] - bo[i % 3]) * k) / data.length;
      for (let i = 0; i < J.length; i++) avgJ[i] += (o[i % 3] + (bj[i] - bo[i % 3]) * k) / data.length;
    }
    const s = p.strength, out = Float32Array.from(P, (v, i) => v + s * (v - avgP[i]));
    return { positions: out, joints: Float64Array.from(J, (v, i) => v + s * (v - avgJ[i])) };
  },
});

// a mask grown over the surface by some rings
function grow(m, nb, rings) {
  for (let r = 0; r < rings; r++) { const g = Uint8Array.from(m); for (let i = 0; i < m.length; i++) if (m[i]) for (let q = nb.start[i]; q < nb.start[i + 1]; q++) g[nb.list[q]] = 1; m = g; }
  return m;
}
