// A head's pieces: meshes on the rig beside its skin — where the skin won't stretch (a long nose, a ball of a nose:
// Г3's, experiments/heads-wrap), and what a head preset wears so it looks as it was drawn (Г1's and Г3's hair, hoods,
// hats, an ear device: experiments/heads-anime). Each piece is one or more meshes rigid on the Head joint, made in
// head units at the rest (src/head/frame.js). Garments (Г1's turtleneck, the outfits) are the clothes' stage. Hair
// here is Г1's designed hair carried as it was (rigid volumes and ribbons on the head); the hair that moves is a
// later stage — it takes the head's shape to collide with (src/head/head.js, src/figure.js headShape).
//   piecesOf(list, {form, frame, sk, skin, cranium}) → [mesh fields for makeMesh]
import { smin, clamp, lerp, sst, add, sub, scale, normalize, len, cross, dot } from '../math.js';
import { smax, sdEll, sdCapsule, sdSphere, meshOf } from './shapes.js';

const num = (min, max) => ({ type: 'number', min, max }), color = { type: 'string', pattern: /^#[0-9a-f]{6}$/i };
const part = { type: 'array', min: 2, max: 2, items: { anyOf: [{ type: 'string', pattern: /^[a-zA-Z]+$/ }, { type: 'map', values: { anyOf: [num(-100, 100), { type: 'string', pattern: /^#[0-9a-f]{6}$/i }, { type: 'array', items: { type: 'array', items: num(-20, 20) } }, { type: 'boolean' }] } }] } };
export const PIECE_SCHEMA = { type: 'union', key: 'kind', cases: {
  nose: { type: 'object', props: { kind: { const: 'nose' }, id: { type: 'string' }, ink: num(0, 0.01) }, required: ['kind'] },
  hair: { type: 'object', props: { kind: { const: 'hair' }, id: { type: 'string' }, color, ink: color, parts: { type: 'array', min: 1, items: part } }, required: ['kind', 'color', 'parts'] },
  hood: { type: 'object', props: { kind: { const: 'hood' }, id: { type: 'string' }, color, inner: color, wide: num(0.5, 2) }, required: ['kind', 'color'] },
  hat: { type: 'object', props: { kind: { const: 'hat' }, id: { type: 'string' }, color }, required: ['kind', 'color'] },
  earDevice: { type: 'object', props: { kind: { const: 'earDevice' }, id: { type: 'string' }, color, dark: color }, required: ['kind', 'color'] },
} };
export const HAIR_PARTS = ['cap', 'bangsBlunt', 'bangsSide', 'bangsSpiky', 'sides', 'back', 'sidePart', 'centerPart', 'sideSweep', 'spiky', 'mass', 'messyShort', 'chunky', 'sweptBack', 'topBun', 'twoTails', 'bowl', 'messy', 'fringeTufts', 'strays'];

export function piecesOf(list, ctx) {
  const out = [];
  for (const p of list) {
    if (p.kind === 'nose') out.push(...nose(p, ctx));
    else if (p.kind === 'hair') out.push(...hair(p, ctx));
    else out.push(extra(p, ctx));
  }
  return out;
}
const rigidOn = (ctx, name, m, o) => ({ kind: 'rigid', id: name, joint: ctx.sk.index.Head, positions: toWorld(m.positions, ctx.frame), triangles: m.triangles, floor: false, ...o });
const toWorld = (P, F) => { const out = new Float32Array(P.length); for (let i = 0; i < P.length; i += 3) { const w = F.toW(P[i], P[i + 1], P[i + 2]); out[i] = w[0]; out[i + 1] = w[1]; out[i + 2] = w[2]; } return out; };

// the drawn nose set on the wrapped face where the skin couldn't take it: a long one — what of the drawn head stands
// out of the face the skin was laid on, closed a little under the skin (its outline only inked); a ball — round, a
// little rosier than the face, with a shine where the light falls
function nose(p, ctx) {
  const G = ctx.form, N = G?.piece; if (!N) throw new Error('a nose piece needs a designed form whose nose is its own piece (form.face.nose.piece)');
  const skin = ctx.skin, hsdf = G.sdf;
  if (N.ball && N.root) {   // a ball on a capsule nose: the ball round; on a nose drawn by its side curve, what stands out as below
    const b = N.ball, ns = (x, y, z) => smin(sdCapsule(x, y, z, N.root, N.tip, N.radius), sdSphere(x - b.at[0], y - b.at[1], z - b.at[2], b.r), b.k ?? 0.05);
    const m = meshOf(ns, [b.at[0] - b.r - 0.1, b.at[1] - b.r - 0.1, 0.5], [b.at[0] + b.r + 0.1, N.root[1] + 0.1, b.at[2] + b.r + 0.1], 0.012);
    const keep = []; for (let t = 0; t < m.triangles.length; t += 3) { let inside = 0; for (let k = 0; k < 3; k++) { const v = m.triangles[t + k]; if (hsdf(m.positions[v * 3], m.positions[v * 3 + 1], m.positions[v * 3 + 2]) < -0.01) inside++; } if (inside < 3) keep.push(m.triangles[t], m.triangles[t + 1], m.triangles[t + 2]); }
    const base = mix(hex(skin), hex('#f0a088'), 0.25), hi = hex('#fff4ea'), L = normalize([-0.45, 0.6, 0.65]), cl = new Float32Array(m.positions.length);
    for (let v = 0; v < m.positions.length / 3; v++) { const sp = sst(clamp((dot([m.normals[v * 3], m.normals[v * 3 + 1], m.normals[v * 3 + 2]], L) - 0.86) / 0.06, 0, 1)), c = mix(base, hi, sp * 0.85); cl.set(c, v * 3); }
    return [rigidOn(ctx, 'nose', { positions: m.positions, triangles: keep }, { color: skin, colors: cl, ink: { width: 0.0014, color: '#7a4a2a' }, toon: true })];
  }
  const ridge = G.nose, ns = (x, y, z) => Math.max(G.full(x, y, z), -(hsdf(x, y, z) + 0.03), ridge(x, y, z) - 0.05);
  const m = meshOf(ns, [-0.32, -1.12, 0.4], [0.32, 0.0, 1.72], 0.008);
  return [rigidOn(ctx, 'nose', m, { color: skin, ink: { width: p.ink ?? 0.0008, color: '#a07882' }, toon: true, shadows: false })];
}

// hoods, hats, an ear device: shells by distance, two-sided
function extra(p, ctx) {
  const W = p.wide ?? 1;
  const sdf = {
    hood: (x, y, z) => { const s0 = smin(sdEll(x, y - 0.12, z + 0.1, 1.24 * W, 1.32, 1.32), sdCapsule(x, y, z, [0, -0.7, -0.3], [0, -2.2, -0.4], [1.15 * W, 1.4 * W]), 0.5); const d = Math.abs(s0) - 0.075, ell = (Math.hypot(x / (0.92 * W), (y + 0.42) / 1.18) - 1) * 0.92, open = smax(ell, -(z - 0.05), 0.1); return smax(d, -open, 0.12); },
    hat: (x, y, z) => { const crown = sdEll(x, y - 1.05, z + 0.05, 1.32, 0.78, 1.28), band = Math.max(Math.abs(y - 0.55) - 0.16, Math.hypot(x / 1.12, (z + 0.04) / 1.14) - 1); return smin(crown, band - 0.03, 0.12); },
    earDevice: (x, y, z) => Math.max(sdCapsule(x, y, z, [-1.0, -0.28, -0.05], [-1.16, -0.28, -0.05], 0.26), 0),
  }[p.kind];
  const m = meshOf(sdf, [-2.4, -3.2, -2.2], [2.4, 2.2, 2.2], 0.04);
  return rigidOn(ctx, p.id ?? p.kind, m, { color: p.color, double: true, ink: { width: 0.0018, color: '#2a1e24' }, toon: true });
}

// —— Г1's hair: a cap and locks (ribbons flattened against the head), masses with clumps melted into their edge ——
function hair(p, ctx) {
  const H = ctx.cranium, out = [];
  const C0 = [0, 0.02, -0.04];
  const cr = dir => { const d = normalize(dir), k = 1 / Math.hypot(d[0] / H.w, d[1] / H.h, d[2] / H.d); return add(scale(d, k), C0); };
  const S = (az, el, o = 1.06) => scale(cr([Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el)]), o);
  const V = (x, y, z) => [x, y, z];
  // a lock wraps the head from root to tip, lifted off it by `lift`, then hangs
  const wrapLock = (pts, lift = 0.08) => pts.map((q, i) => { const t = i / (pts.length - 1), L = sub(q, C0), need = len(cr(L)) * (1.04 + lift * Math.sin(Math.PI * Math.min(1, t * 1.2))); return len(L) < need && q[1] > -1.0 ? add(scale(normalize(L), need), C0) : q.slice(); });
  const locks = [], solids = [];
  const lock = (ctrl, w, o = {}) => locks.push({ pts: wrapLock(bezier(ctrl, 26), o.lift ?? 0.06), w, flat: o.flat ?? 0.32, tipPow: o.tipPow ?? 1.5, color: o.color });
  const capOf = (front, back, sc = [1.06, 1.07, 1.06], dy = 0.03, dz = 0.05) => (x, y, z) => smax(sdEll(x, y - dy, z + dz, H.w * sc[0], H.h * sc[1], H.d * sc[2]), lerp(back, front, clamp((z / H.d + 1) / 2, 0, 1) ** 1.3) - y, 0.22);
  for (const [kind, o] of p.parts) {
    if (!HAIR_PARTS.includes(kind)) throw new Error(`no hair part "${kind}" (${HAIR_PARTS.join(', ')})`);
    if (kind === 'cap') solids.push({ sdf: capOf(o.front ?? 0.3, o.back ?? -0.75) });
    if (kind === 'bangsBlunt') for (let k = 0; k < o.n; k++) { const t = k / (o.n - 1) * 2 - 1, az = t * o.spread * 0.9, tip = S(az * 1.05, -0.05, 1.04); tip[1] = o.y - 0.12 * Math.abs(t) ** 2 + (k % 3 === 1 ? -0.06 : 0); lock([S(az * 0.4, 1.0), S(az * 0.8, 0.6, 1.12), S(az, 0.15, 1.1), tip], o.w * (1 - 0.3 * Math.abs(t)), { lift: 0.05 }); }
    if (kind === 'bangsSide') for (let k = 0; k < o.n; k++) { const t = k / Math.max(1, o.n - 1), az = lerp(-0.7, 0.5, t); lock([S(0.6, 1.05), S(az * 0.4 + 0.2, 0.75, 1.14), S(az, 0.25, 1.12), S(az - 0.1, o.long ? -0.45 : -0.05, 1.05)], 0.2, { lift: 0.05 }); }
    if (kind === 'bangsSpiky') for (let k = 0; k < o.n; k++) { const az = lerp(-0.55, 0.55, k / (o.n - 1)); lock([S(az * 0.5, 0.9), S(az, 0.55, 1.2), add(S(az * 1.2, 0.3, 1.25), [0, 0, 0.1])], 0.22, { lift: 0.12 }); }
    if (kind === 'sides') for (const s of [-1, 1]) for (let k = 0; k < o.n; k++) { const az = s * (0.9 + k * 0.18); lock([S(s * 0.5, 0.9), S(az, 0.3, 1.1), S(az * 1.05, -0.4, 1.06), V(s * (0.95 + k * 0.06), -o.len, (o.z ?? 0.2) - k * 0.15)], o.w, { lift: 0.04 }); }
    if (kind === 'back') for (let k = 0; k < o.n; k++) { const t = k / (o.n - 1) * 2 - 1, az = Math.PI + t * 1.25, wave = o.wave || 0, base = S(az, -0.5, 1.06); lock([S(az * 0.6 + Math.PI * 0.4, 0.95), S(az, 0.3, 1.12 + (o.lift || 0)), scale(base, 1 + (o.lift || 0)), V(base[0] * 1.15 + wave * Math.sin(k * 1.7), -o.len * 0.6, -1.25 + 0.2 * Math.cos(t)), V(base[0] * 1.05, -o.len, -1.35 + 0.25 * Math.cos(t))], o.w, { lift: 0.05 }); }
    if (kind === 'sidePart') {
      for (let k = 0; k < 9; k++) { const t = k / 8, az = lerp(-0.35, -1.45, t); lock([S(0.38, 1.1), S(lerp(0.15, -0.6, t), lerp(1.05, 0.95, t), 1.3), S(az, lerp(0.62, 0.42, t), 1.32), S(az - 0.25, -0.3, 1.24), V(-1.25 - 0.2 * t, -2.6 - t, 0.1 - t * 0.7)], 0.38, { lift: 0.12 }); }
      for (let k = 0; k < 6; k++) { const t = k / 5, az = lerp(0.9, 1.6, t); lock([S(0.38, 1.1), S(lerp(0.7, 1.1, t), 0.85, 1.24), S(az, 0.25, 1.2), V(1.2 + 0.15 * t, -2.4 - t * 0.8, 0.1 - t * 0.6)], 0.36, { lift: 0.12 }); }
    }
    if (kind === 'centerPart') for (const sd of [-1, 1]) for (let k = 0; k < (o.n || 7); k++) { const t = k / ((o.n || 7) - 1), az = sd * lerp(0.95, 2.0, t); lock([S(sd * 0.05, 1.3, 1.0), S(sd * lerp(0.5, 1.1, t), lerp(0.95, 0.75, t), 1.18), S(az, lerp(0.4, 0.1, t), 1.2), S(az * 1.03, -0.45, 1.14), V(sd * (1.05 + 0.2 * t), -2.4 - 0.4 * t, 0.0 - 0.9 * t), V(sd * (1.3 + 0.3 * t), -3.1 - 0.3 * t, -0.1 - 1.0 * t)], o.w || 0.42, { lift: 0.08, tipPow: 1.3 }); }
    if (kind === 'sideSweep') for (let k = 0; k < 6; k++) { const t = k / 5; lock([S(-0.45, 1.15), S(lerp(-0.2, 0.3, t), 0.85, 1.3), S(lerp(0.3, 0.85, t), lerp(0.25, 0.1, t), 1.32), S(lerp(0.5, 1.0, t), lerp(-0.45, -0.3, t), 1.22)], 0.36, { lift: 0.14, tipPow: 1.2 }); }
    if (kind === 'spiky') for (let k = 0; k < o.n; k++) { const az = (k / o.n) * Math.PI * 2, el = 0.2 + 0.9 * ((k * 0.618) % 1), root = S(az, el, 1.0), dir = normalize(root), tip = add(add(root, scale(dir, o.len * (0.6 + 0.6 * ((k * 0.37) % 1)))), [0, -0.15, -0.25]); lock([root, add(lerp3(root, tip, 0.5), scale(dir, 0.1)), tip], o.w, { lift: 0.0, tipPow: 1.0 }); }
    if (kind === 'mass') {
      const cl = [], n = o.n || 18, sc = o.scale || 1.16;
      for (let k = 0; k < n; k++) {
        const az = (k / n) * Math.PI * 2 - Math.PI + (o.twist || 0), j = (k * 0.618) % 1, front = Math.cos(az), el = front > 0.35 ? (o.bangEl ?? 0.45) : lerp(0.15, -0.25, (1 - front) / 2);
        const root = S(az, el + 0.25, sc), outv = normalize(sub(root, C0)), L = (front > 0.35 ? (o.bang ?? 0.45) : (o.len ?? 0.6)) * (0.75 + 0.5 * j);
        const tip = add(add(root, scale(outv, (o.flick ?? 0.15) + (o.spread ?? 0) * j)), [Math.sin(az) * (o.side ?? 0.05), -L, front > 0.35 ? 0.12 : 0]);
        if (o.up && front < 0.35 && j > 0.5) tip[1] += L * 1.2;
        cl.push([root, tip, (o.r ?? 0.24) * (0.8 + 0.4 * j)]);
      }
      for (const t of o.tufts || []) { const root = S(t[0], t[1], sc), outv = normalize(root); cl.push([root, add(add(root, scale(outv, t[2])), [0, t[3] || 0, t[4] || 0]), t[5] || 0.22]); }
      const front = o.front ?? 0.4, back = o.back ?? -0.7;
      solids.push({ sdf: (x, y, z) => { let d = smax(sdEll(x, y - 0.06, z + 0.06, H.w * sc, H.h * sc * 1.02, H.d * sc), lerp(back, front, clamp((z / H.d + 1) / 2, 0, 1) ** 1.3) - y, 0.2); for (const [a, b, r] of cl) d = smin(d, sdCapsule(x, y, z, a, b, [r, 0.015]), 0.12); return d; } });
    }
    if (kind === 'messyShort') for (let k = 0; k < o.n; k++) { const az = (k / o.n) * Math.PI * 2 - Math.PI, j = (k * 0.618) % 1, front = Math.cos(az), root = S(az * 0.25, 1.35, 1.0), mid = S(az, lerp(0.85, 0.6, Math.max(0, front)), (o.mid || 1.28) + 0.06 * j), tip = add(S(az * (1.06 + 0.1 * j), front > 0.4 ? lerp(0.1, 0.3, j) : lerp(-0.2, 0.3, j), (o.out || 1.42) + 0.12 * j), [Math.sin(az) * (o.side || 0.15), front > 0.4 ? 0.05 : 0.15 * j, front > 0.4 ? 0.1 : -0.05]); lock([root, mid, tip], (o.w || 0.42) - 0.1 * j, { lift: 0.0, tipPow: 1.0, flat: 0.45 }); }
    if (kind === 'chunky') for (let k = 0; k < o.n; k++) { const az = (k / o.n) * Math.PI * 2, j = (k * 0.618) % 1, el = 0.35 + 0.7 * j, root = S(az * 0.5, 1.2, 1.0), mid = S(az, el, 1.22), dir = normalize(mid), tip = add(add(mid, scale(dir, 0.35 + 0.3 * ((k * 0.37) % 1))), [0, 0.1 - 0.4 * (1 - el), 0.15]); lock([root, mid, tip], 0.34, { lift: 0.0, tipPow: 1.0, flat: 0.4 }); }
    if (kind === 'sweptBack') for (let k = 0; k < o.n; k++) { const az = lerp(-1.2, 1.2, k / (o.n - 1)); lock([S(az * 0.6, 0.6, 1.0), S(az * 0.4, 1.2, 1.12), S(Math.PI + az * 0.5, 0.5, 1.1), S(Math.PI + az * 0.6, -0.2, 1.05)], o.w, { lift: 0.04 }); }
    if (kind === 'topBun') {
      solids.push({ sdf: (x, y, z) => sdEll(x, y - 1.18, z + 0.35, 0.42, 0.36, 0.4) });
      for (let k = 0; k < 3; k++) solids.push({ sdf: (x, y, z) => sdEll(x - (-0.3 + k * 0.3), y - 1.0 - (k === 1 ? 0.12 : 0), z + 0.05, 0.05, 0.12, 0.04), color: o.color2 });
      for (let k = 0; k < 4; k++) { const az = Math.PI + lerp(-0.6, 0.6, k / 3); lock([V(0, 1.3, -0.4), V(Math.sin(az) * 0.5, 1.55, -0.6), V(Math.sin(az) * 0.9, 0.9, -1.0)], 0.18, { lift: 0 }); }
    }
    if (kind === 'twoTails') for (const s of [-1, 1]) { const root = V(s * 0.75, 0.55, -0.7); solids.push({ sdf: (x, y, z) => sdEll(x - root[0], y - root[1], z - root[2], 0.12, 0.12, 0.12), color: o.tie ?? '#2a1612' }); for (let k = 0; k < 4; k++) lock([root, add(root, [s * 0.4, 0.15 + k * 0.08, -0.15]), add(root, [s * (1.0 + k * 0.08), 0.1 + k * 0.15 - 0.15, -0.35 - k * 0.05])], 0.2, { lift: 0, tipPow: 1.2 }); }
    if (kind === 'bowl') for (let k = 0; k < o.n; k++) { const az = (k / o.n) * Math.PI * 2, front = Math.cos(az), tip = S(az, -0.05, 1.08); tip[1] = front > 0.3 ? lerp(-0.05, -0.35, (Math.sin(az) + 1) / 2) : lerp(-0.25, -0.75, 1 - front); lock([S(0, 1.4, 1.0), S(az, 0.75, 1.16), S(az, 0.15, 1.18), tip], 0.3, { lift: 0.08 }); }
    if (kind === 'messy') for (let k = 0; k < o.n; k++) { const az = Math.PI + lerp(-1.9, 1.9, k / (o.n - 1)), j = (k * 0.61) % 1, base = S(az, -0.3, 1.06); lock([S(az * 0.5 + Math.PI * 0.5, 1.0), S(az, 0.4, 1.15), base, add(base, [Math.sin(az) * (0.4 + j * 0.5), -0.6 - j * 0.9, -0.2])], 0.2 + 0.06 * j, { lift: 0.06 }); }
    if (kind === 'fringeTufts') for (const s of [-1, 1]) for (let k = 0; k < 4; k++) { const az = s * (0.7 + k * 0.25); lock([S(az * 0.6, 0.6, 1.0), S(az, 0.35, 1.2), add(S(az * 1.1, -0.05, 1.2), [s * 0.1, 0, 0])], 0.26, { lift: 0.12, tipPow: 1.2 }); }
    if (kind === 'strays') for (let k = 0; k < o.n; k++) { const s = k % 2 ? 1 : -1, az = s * (0.3 + 0.15 * k); lock([S(az * 0.3, 1.0), S(az, 0.5, 1.16), add(S(az * 1.3, -0.1, 1.12), [s * 0.1, -0.2 - 0.1 * k, 0.05])], 0.06, { lift: 0.1, tipPow: 1.0 }); }
  }
  const ink = { width: 0.0016, color: p.ink ?? '#2a1e24' };
  solids.forEach((s, k) => { const m = meshOf(s.sdf, [-1.7, -1.2, -1.7], [1.7, 1.8, 1.7], 0.035); out.push(rigidOn(ctx, `${p.id ?? 'hair'}-${k}`, m, { color: s.color || p.color, ink, toon: true })); });
  if (locks.length) {
    // the locks as one mesh (each a ribbon of its own)
    const P = [], T = [];
    for (const L of locks) { const g = lockGeometry(L), o = P.length / 3; P.push(...g.positions); for (const i of g.triangles) T.push(i + o); }
    out.push(rigidOn(ctx, `${p.id ?? 'hair'}-locks`, { positions: Float32Array.from(P), triangles: T }, { color: p.color, ink: { width: 0.0012, color: p.ink ?? '#2a1e24' }, toon: true }));
  }
  return out;
}
const lerp3 = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
function bezier(ps, n = 30) { const out = []; for (let k = 0; k <= n; k++) { let q = ps; const t = k / n; while (q.length > 1) q = q.slice(1).map((p, i) => lerp3(q[i], p, t)); out.push(q[0]); } return out; }
// a lock: a ribbon swept along its points, flattened against the head, tapering to its tip
function lockGeometry(L, R = 10) {
  const pts = L.pts, n = pts.length, pos = [], idx = [], C0 = [0, 0.02, -0.04];
  for (let i = 0; i < n; i++) {
    const T = normalize(sub(pts[Math.min(n - 1, i + 1)], pts[Math.max(0, i - 1)])), radial = normalize(sub(pts[i], C0)), Nn = normalize(sub(radial, scale(T, dot(radial, T)))), B = cross(T, Nn);
    const t = i / (n - 1), w = L.w * (t < 0.12 ? lerp(0.55, 1, t / 0.12) : Math.max(0, 1 - ((t - 0.12) / 0.88) ** L.tipPow)) + 0.004;
    for (let a = 0; a < R; a++) { const ang = a / R * Math.PI * 2, x = Math.cos(ang) * w * L.flat, y = Math.sin(ang) * w; pos.push(pts[i][0] + Nn[0] * x + B[0] * y, pts[i][1] + Nn[1] * x + B[1] * y, pts[i][2] + Nn[2] * x + B[2] * y); }
  }
  for (let j = 0; j + 1 < n; j++) for (let a = 0; a < R; a++) { const a1 = (a + 1) % R; idx.push(j * R + a, j * R + a1, (j + 1) * R + a, j * R + a1, (j + 1) * R + a1, (j + 1) * R + a); }
  const cap = (ring, tip, flip) => { const v = pos.length / 3; pos.push(...tip); for (let a = 0; a < R; a++) { const a1 = (a + 1) % R; flip ? idx.push(v, ring * R + a, ring * R + a1) : idx.push(v, ring * R + a1, ring * R + a); } };
  cap(0, pts[0], false); cap(n - 1, pts[n - 1], true);
  return { positions: pos, triangles: idx };
}
const hex = c => [parseInt(c.slice(1, 3), 16) / 255, parseInt(c.slice(3, 5), 16) / 255, parseInt(c.slice(5, 7), 16) / 255].map(v => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
const mix = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
