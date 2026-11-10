// Т7's designed contours (experiments/designed-form) as a deformer of any body's own contours.
//
// A body's contours are read off it the way Т7's `construct()` reads them: along each part's bone (torso, neck, the
// collarbones, upper and lower arms, thighs, shins, feet) its section's radius in eight directions round the bone, at
// 24 places along it — the 70th percentile of the skin that is surely that part's, smoothed along the bone. A drawn
// form is the same thing drawn: Т7's style curves — four contours of each limb (outer, inner, front, back) along the
// whole limb, the torso's side, front and back along the spine — in the body's own units (a thigh's radius, an upper
// arm's, the hips' half-width). So the strength is a blend of radii: each point keeps its place against its own
// section and moves as the section's radius moves from the body's own (strength 0) to the drawn one (strength 1) —
// from a touch-up to the drawn form; the small forms of the body ride on it as they are. Edits multiply the radii on
// top: {part, dir, keys}. The hands, feet and the head stay the body's own; the change is smoothed over the surface
// where parts meet.
//
//   form    {units: {leg, arm} (the drawing's units against the body's own: ×), n: {leg, arm, torso} (the sections'
//           roundness: 2 an ellipse, more a squarer one), leg | arm: {outer, inner, front, back}, torso: {side, front,
//           back}: each [[at, radius in units], …] — at along the whole limb (0 its root joint, 1 its end) or along
//           the torso (0 the hips' joint, 1 the neck's)}
//   edits   [{part: torso | neck | clav | arm | fore | thigh | shin | foot | arms | legs, dir: all | outer | inner |
//           front | back | side, keys: [[at, factor], …]}] — at along the bone (0..1), or along the whole limb for
//           arms | legs
//   own     how much of the body's own small forms ride on the new sections: 1 all of them (the default), 0 none —
//           every point on the drawn radius, the drawn form itself
import { register } from '../deform.js';
import { local, smoothField } from '../regions.js';
import { clamp, lerp } from '../math.js';
import { curve } from './curves.js';
import { num } from '../schema.js';

const keys = { type: 'array', min: 1, items: { type: 'array', min: 2, max: 2, items: num(-1, 10) } };
const four = { type: 'object', props: { outer: keys, inner: keys, front: keys, back: keys }, required: ['outer', 'inner', 'front', 'back'] };
const FORM = { type: 'object', props: {
  units: { type: 'object', props: { leg: num(0.1, 5), arm: num(0.1, 5) } }, n: { type: 'object', props: { leg: num(1, 8), arm: num(1, 8), torso: num(1, 8) } },
  leg: four, arm: four, torso: { type: 'object', props: { side: keys, front: keys, back: keys }, required: ['side', 'front', 'back'] } } };
const PARTS = ['torso', 'neck', 'clav', 'arm', 'fore', 'thigh', 'shin', 'foot', 'arms', 'legs'];
const EDIT = { type: 'object', props: { part: { type: 'string', enum: PARTS }, dir: { type: 'string', enum: ['all', 'outer', 'inner', 'front', 'back', 'side'] }, keys }, required: ['part', 'keys'] };
const SWEEPS = new Set(['torso', 'neck', 'clav', 'arm', 'fore', 'thigh', 'shin', 'foot']);
const TB = 24;

register({
  kind: 'contour', of: 'skin',
  params: { form: FORM, edits: { type: 'array', items: EDIT }, own: num(0, 1) },
  defaults: { edits: [], own: 1 },
  rest(p, R) {
    const own = ownContours(R), s = p.strength, P = R.mesh.positions, N = R.mesh.N, F = R.frames;
    const drawn = p.form ? drawnForm(p.form, R, own) : null;
    const edits = p.edits.map(e => ({ ...e, f: curve(e.keys) }));
    const disp = new Float32Array(N * 3), tmp = [0, 0, 0];
    for (const i of R.mesh.used) {
      const keep = (1 - R.ends[i]) * (1 - R.head[i]); if (keep < 1e-3) continue;
      for (let h = 0; h < 2; h++) {
        const si = R.seg[i * 2 + h], w = R.sw[i * 2 + h], g = R.segs[si]; if (w < 1e-4 || !SWEEPS.has(g.kind)) continue;
        const f = F[si], o = own[si], [t, x, z] = local(f, P[i * 3], P[i * 3 + 1], P[i * 3 + 2]), rho = Math.hypot(x, z); if (rho < 1e-5) continue;
        const ph = Math.atan2(z, x), r0 = o.at(t, ph);
        const dir = dirOf(f, ph, g.side), L = o.chain(t);
        let r = drawn && drawn[si] ? lerp(r0, drawn[si](t, L, dir), s) : r0;
        for (const e of edits) if (matches(e.part, g.kind)) r *= 1 + (e.f(e.part === 'arms' || e.part === 'legs' ? L : t) - 1) * share(e.dir ?? 'all', dir) * s;
        // own: how much of the point's own place against its section rides on the new one (0: on the drawn radius)
        const ow = 1 - (1 - p.own) * s, want = ow >= 1 ? rho * r / r0 : r * Math.pow(rho / r0, ow), k = (want / rho - 1) * w * keep;
        // the point moved off the bone's line by the change of its section's radius
        tmp[0] = (x * f.u[0] + z * f.w[0]) * k; tmp[1] = (x * f.u[1] + z * f.w[1]) * k; tmp[2] = (x * f.u[2] + z * f.w[2]) * k;
        disp[i * 3] += tmp[0]; disp[i * 3 + 1] += tmp[1]; disp[i * 3 + 2] += tmp[2];
      }
    }
    smoothField(disp, 3, R.nb, 8);
    const out = Float32Array.from(P);
    for (const i of R.mesh.used) for (let c = 0; c < 3; c++) out[i * 3 + c] += disp[i * 3 + c];
    return { positions: out };
  },
});
const matches = (part, kind) => part === kind || (part === 'arms' && (kind === 'arm' || kind === 'fore')) || (part === 'legs' && (kind === 'thigh' || kind === 'shin'));
// a direction round a bone as its shares: a (+ outwards, to the part's side), b (+ forwards)
function dirOf(f, ph, side) {
  const c = Math.cos(ph), s = Math.sin(ph), d = [f.u[0] * c + f.w[0] * s, f.u[1] * c + f.w[1] * s, f.u[2] * c + f.w[2] * s];
  const flat = v => { const k = v[0] * f.e[0] + v[1] * f.e[1] + v[2] * f.e[2], q = [v[0] - k * f.e[0], v[1] - k * f.e[1], v[2] - k * f.e[2]], l = Math.hypot(...q) || 1; return [q[0] / l, q[1] / l, q[2] / l]; };
  const out = flat([side || 1, 0, 0]), fw = flat([0, 0, 1]);
  return { a: d[0] * out[0] + d[1] * out[1] + d[2] * out[2], b: d[0] * fw[0] + d[1] * fw[1] + d[2] * fw[2] };
}
function share(dir, { a, b }) {
  const A = a * a, B = b * b, n = A + B || 1;
  switch (dir) {
    case 'all': return 1;
    case 'outer': return a > 0 ? A / n : 0; case 'inner': return a < 0 ? A / n : 0;
    case 'front': return b > 0 ? B / n : 0; case 'back': return b < 0 ? B / n : 0;
    case 'side': return A / n;
  }
  throw new Error(`contour: no direction ${dir}`);
}

// the body's own sections (kept per rest): per part, lo/hi along the bone, the radii in 8 directions at 24 places
const OWN = new WeakMap();
export function ownContours(R) {
  if (OWN.has(R)) return OWN.get(R);
  const P = R.mesh.positions, segs = R.segs;
  const out = segs.map((g, si) => {
    const f = R.frames[si], pts = [];
    for (const min of [0.85, 0.4]) {
      for (const i of R.mesh.used) if (R.seg[i * 2] === si && R.sw[i * 2] >= min) pts.push(local(f, P[i * 3], P[i * 3 + 1], P[i * 3 + 2]));
      if (pts.length >= 40) break;
    }
    if (pts.length < 8) return null;
    const ts = pts.map(q => q[0]).sort((a, b) => a - b), lo = ts[Math.floor(ts.length * 0.03)], hi = ts[Math.floor(ts.length * 0.97)];
    // a direction no point of the part lies in takes the part's own median radius
    const fallback = (() => { const r = pts.map(([, x, z]) => Math.hypot(x, z)).sort((a, b) => a - b); return r[r.length >> 1]; })();
    const bins = Array.from({ length: TB * 8 }, () => []);
    for (const [t, x, z] of pts) {
      const b = Math.round((t - lo) / (hi - lo) * (TB - 1)); if (b < 0 || b >= TB) continue;
      const q = ((Math.round(Math.atan2(z, x) / (Math.PI / 4)) % 8) + 8) % 8;
      bins[q * TB + b].push(Math.hypot(x, z));
    }
    const raw = Float64Array.from(bins, v => { v.sort((a, c) => a - c); return v.length ? v[Math.floor(v.length * 0.7)] : NaN; });
    for (let q = 0; q < 8; q++) for (let i = 0; i < TB; i++) if (Number.isNaN(raw[q * TB + i])) {
      let v = NaN; for (let j = 1; j < TB && Number.isNaN(v); j++) { if (i - j >= 0 && !Number.isNaN(raw[q * TB + i - j])) v = raw[q * TB + i - j]; else if (i + j < TB && !Number.isNaN(raw[q * TB + i + j])) v = raw[q * TB + i + j]; }
      raw[q * TB + i] = Number.isNaN(v) ? fallback : v;
    }
    // smoothed along the bone (as Т7's construct reads its seven keys off the bins)
    const sm = new Float64Array(TB * 8);
    for (let q = 0; q < 8; q++) for (let i = 0; i < TB; i++) { let s = 0, ws = 0; for (let j = 0; j < TB; j++) { const w = Math.exp(-(((j - i) / 1.6) ** 2)); s += raw[q * TB + j] * w; ws += w; } sm[q * TB + i] = s / ws; }
    const at = (t, ph) => {
      const u = clamp((t - lo) / (hi - lo), 0, 1) * (TB - 1), i = Math.min(TB - 2, Math.floor(u)), fr = u - i;
      const xk = ((ph / (Math.PI / 4)) % 8 + 8) % 8, k0 = Math.floor(xk), tk = xk - k0;
      const g = j => { const q = (k0 + j + 8) % 8; return sm[q * TB + i] * (1 - fr) + sm[q * TB + i + 1] * fr; };
      const p0 = g(-1), p1 = g(0), p2 = g(1), p3 = g(2);
      return Math.max(0.002, 0.5 * ((2 * p1) + (-p0 + p2) * tk + (2 * p0 - 5 * p1 + 4 * p2 - p3) * tk * tk + (-p0 + 3 * p1 - 3 * p2 + p3) * tk * tk * tk));
    };
    const mean = sm.reduce((a, b) => a + b, 0) / sm.length;
    return { lo, hi, at, mean, sm, chain: t => t };
  });
  // along the whole limb: thigh + shin, upper arm + forearm (0 the root joint, 1 the end)
  for (const [a, b] of [['thighLeft', 'shinLeft'], ['thighRight', 'shinRight'], ['armLeft', 'foreLeft'], ['armRight', 'foreRight']]) {
    const ia = R.index[a], ib = R.index[b], la = R.frames[ia].L, lb = R.frames[ib].L, T = la + lb;
    out[ia].chain = t => t * la / T; out[ib].chain = t => (la + t * lb) / T;
  }
  OWN.set(R, out);
  return out;
}

// a drawn form, as a radius for a part's point (its t along the bone, L along the limb, direction)
function drawnForm(form, R, own) {
  const I = R.index, kL = form.units?.leg ?? 1, kA = form.units?.arm ?? 1;
  const Rleg = own[I.thighLeft].mean * kL, Rarm = own[I.armLeft].mean * kA;
  const tor = own[I.torso], Rtor = (tor.at(tor.lo, 0) + tor.at(tor.lo, Math.PI)) / 2;
  const sup = (a, b, rA, rB, n) => Math.pow(Math.abs(a / rA) ** n + Math.abs(b / rB) ** n, -1 / n);
  const C = o => o && Object.fromEntries(Object.entries(o).map(([k, v]) => [k, curve(v)]));
  const leg = C(form.leg), arm = C(form.arm), torso = C(form.torso), n = { leg: 2, arm: 2, torso: 2, ...form.n };
  const limb = (d, unit, nn) => (t, L, { a, b }) => sup(a, b, (a >= 0 ? d.outer : d.inner)(L) * unit, (b >= 0 ? d.front : d.back)(L) * unit, nn);
  const out = [];
  R.segs.forEach((g, si) => {
    if (leg && (g.kind === 'thigh' || g.kind === 'shin')) out[si] = limb(leg, Rleg, n.leg);
    else if (arm && (g.kind === 'arm' || g.kind === 'fore')) out[si] = limb(arm, Rarm, n.arm);
    else if (torso && g.kind === 'torso') out[si] = (t, L, { a, b }) => sup(Math.sqrt(Math.max(0, 1 - b * b)), b, torso.side(t) * Rtor, (b >= 0 ? torso.front : torso.back)(t) * Rtor, n.torso);
  });
  return out;
}
