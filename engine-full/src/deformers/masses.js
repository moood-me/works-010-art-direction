// Т7's soft separate masses (experiments/designed-form: the bust, the buttocks, the shoulder's cap and its slope from
// the neck) as local bumps on any body: each a simple solid set against the body's own joints, in the body's own
// units, melted into the surface (a smooth union, Т7's smin, of `blend` width) — the skin goes out along its normal to
// where the union's surface is, so the mass grows out of the body without a seam. The strength scales how far.
//
//   items   [{shape: "ellipsoid", radii: [x, y, z]} | {shape: "capsule", r: [r1, r2], to: place},
//            at: place, blend, unit: "torso" | "arm" | "leg", mirror: true (the same on the right, x mirrored)]
//   place   {from: joint, to?: joint, t?: a share of the way from → to, along?: units along it, offset?: [x, y, z]
//            in units} — the units: the hips' half-width (torso), the upper arm's or the thigh's radius
import { register } from '../deform.js';
import { smoothField } from '../regions.js';
import { normalsOf } from '../mesh.js';
import { smin } from '../math.js';
import { ownContours } from './contour.js';
import { num, flag, vec } from '../schema.js';

const v3 = vec(3, -10, 10);
const PLACE = { type: 'object', props: { from: { type: 'string', pattern: /^[A-Za-z0-9]+$/ }, to: { type: 'string', pattern: /^[A-Za-z0-9]+$/ }, t: num(-2, 3), along: num(-10, 10), offset: v3 }, required: ['from'] };
const ITEM = { type: 'object', props: {
  shape: { type: 'string', enum: ['ellipsoid', 'capsule'] }, at: PLACE, to: PLACE, radii: v3, r: { type: 'array', min: 2, max: 2, items: num(0, 10) },
  blend: num(0, 10), unit: { type: 'string', enum: ['torso', 'arm', 'leg'] }, mirror: flag }, required: ['shape', 'at'] };

register({
  kind: 'masses', of: 'skin',
  params: { items: { type: 'array', min: 1, items: ITEM } },
  defaults: {},
  rest(p, R) {
    const own = ownContours(R), I = R.index, tor = own[I.torso];
    const units = { torso: (tor.at(tor.lo, 0) + tor.at(tor.lo, Math.PI)) / 2, arm: own[I.armLeft].mean, leg: own[I.thighLeft].mean };
    const sk = R.skeleton, J = R.rig.joints;
    const joint = n => { const j = sk.index[n]; if (j == null) throw new Error(`masses: no joint ${n}`); return [J[j * 3], J[j * 3 + 1], J[j * 3 + 2]]; };
    const place = (pl, U, mx) => {
      const name = s => mx ? s.replace(/^Left/, 'Right') : s, a = joint(name(pl.from));
      let q = a.slice();
      if (pl.to) {
        const b = joint(name(pl.to)), d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], L = Math.hypot(...d);
        const k = (pl.t ?? 0) + (pl.along ?? 0) * U / L; q = [a[0] + d[0] * k, a[1] + d[1] * k, a[2] + d[2] * k];
      }
      const o = pl.offset || [0, 0, 0]; return [q[0] + (mx ? -1 : 1) * o[0] * U, q[1] + o[1] * U, q[2] + o[2] * U];
    };
    const solids = [];
    for (const it of p.items) for (const mx of it.mirror ? [false, true] : [false]) {
      const U = units[it.unit ?? 'torso'], c = place(it.at, U, mx), k = (it.blend ?? 0.15) * U;
      if (it.shape === 'ellipsoid') {
        const r = it.radii.map(v => v * U), m = Math.min(...r);
        solids.push({ k, f: (x, y, z) => { const qx = (x - c[0]) / r[0], qy = (y - c[1]) / r[1], qz = (z - c[2]) / r[2], q = Math.sqrt(qx * qx + qy * qy + qz * qz); return (q - 1) * m; }, c, reach: Math.max(...r) + 2 * k });
      } else {
        if (!it.to || !it.r) throw new Error('masses: a capsule has `to` and `r`');
        const e = place(it.to, U, mx);
        solids.push({ k, f: cone(c, e, it.r[0] * U, it.r[1] * U), c: c.map((v, i) => (v + e[i]) / 2), reach: Math.hypot(e[0] - c[0], e[1] - c[1], e[2] - c[2]) / 2 + Math.max(...it.r) * U + 2 * k });
      }
    }
    const P = R.mesh.positions, n = normalsOf(P, R.mesh.triangles), N = R.mesh.N, disp = new Float32Array(N * 3), s = p.strength;
    const reach = Math.max(...solids.map(m => m.reach));
    for (const i of R.mesh.used) {
      const x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2], nx = n[i * 3], ny = n[i * 3 + 1], nz = n[i * 3 + 2];
      const near = solids.filter(m => Math.hypot(x - m.c[0], y - m.c[1], z - m.c[2]) < m.reach); if (!near.length) continue;
      // the union along the normal: the body is h away at p + h·n; find where smin(h, solid) crosses zero
      const F = h => { let d = h; for (const m of near) d = smin(d, m.f(x + nx * h, y + ny * h, z + nz * h), m.k); return d; };
      if (F(0) >= 0) continue;
      // out along the normal until outside the union (no farther than the largest mass reaches), then halved to it
      let a = 0, b = 0.01 * R.height; while (F(b) < 0 && b < reach) b *= 2;
      for (let it = 0; it < 30; it++) { const c = (a + b) / 2; if (F(c) < 0) a = c; else b = c; }
      const h = (a + b) / 2 * s * (1 - R.head[i]);
      disp[i * 3] = nx * h; disp[i * 3 + 1] = ny * h; disp[i * 3 + 2] = nz * h;
    }
    smoothField(disp, 3, R.nb, 3);
    return { positions: Float32Array.from(P, (v, i) => v + disp[i]) };
  },
});

// the distance to a cone between two balls (Т7's `cone`, after Inigo Quilez)
export function cone(a, b, r1, r2) {
  const bax = b[0] - a[0], bay = b[1] - a[1], baz = b[2] - a[2];
  const l2 = bax * bax + bay * bay + baz * baz, rr = r1 - r2, a2 = l2 - rr * rr, il2 = 1 / l2;
  return (x, y, z) => {
    const pax = x - a[0], pay = y - a[1], paz = z - a[2];
    const yy = pax * bax + pay * bay + paz * baz, zz = yy - l2;
    const xx = pax * l2 - bax * yy, xy = pay * l2 - bay * yy, xz = paz * l2 - baz * yy;
    const x2 = xx * xx + xy * xy + xz * xz, y2 = yy * yy * l2, z2 = zz * zz * l2;
    const k = Math.sign(rr) * rr * rr * x2;
    if (Math.sign(zz) * a2 * z2 > k) return Math.sqrt(x2 + z2) * il2 - r2;
    if (Math.sign(yy) * a2 * y2 < k) return Math.sqrt(x2 + y2) * il2 - r1;
    return (Math.sqrt(x2 * a2 * il2) + yy * rr) * il2 - r1;
  };
}
