// A head's pieces: meshes on the rig beside its skin — where the skin won't stretch (a long nose, a ball of a nose:
// Г3's, experiments/heads-wrap), and what a head preset wears so it looks as it was drawn (Г1's and Г3's hair, hoods,
// hats, an ear device: experiments/heads-anime). Each piece is one or more meshes rigid on the Head joint, made in
// head units at the rest (src/head/frame.js). Garments (Г1's turtleneck, the outfits) are the clothes' stage. Hair
// here is Г1's designed hair carried as it was (rigid volumes and ribbons on the head); the hair that moves is a
// later stage — it takes the head's shape to collide with (src/head/head.js, src/figure.js headShape).
//   piecesOf(list, {form, frame, sk, skin, cranium}) → [mesh fields for makeMesh]
import { smin, clamp, lerp, add, sub, scale, normalize, len, cross, dot } from '../math.js';
import { smax, sdEll, sdCapsule, sdSphere, meshOf } from './shapes.js';
import { headShares } from './frame.js';
import { washes, washedAt } from './paint.js';
import { followOf } from '../mesh.js';
import { num, flag, color } from '../schema.js';
import { STYLE_PIECE, PHYSICS, styleMeshes } from '../hair/hair.js';
import { guideOf } from '../hair/build.js';

const part = { type: 'array', min: 2, max: 2, items: { anyOf: [{ type: 'string', pattern: /^[a-zA-Z]+$/ }, { type: 'map', values: { anyOf: [num(-100, 100), color, { type: 'array', items: { type: 'array', items: num(-20, 20) } }, flag] } }] } };
export const PIECE_SCHEMA = { type: 'union', key: 'kind', cases: {
  nose: { type: 'object', props: { kind: { const: 'nose' }, id: { type: 'string' }, ink: num(0, 0.01), inkColor: color, rosy: num(0, 1), shine: num(0, 1) }, required: ['kind'] },
  hair: { type: 'object', props: { kind: { const: 'hair' }, id: { type: 'string' }, color, ink: color, parts: { type: 'array', min: 1, items: part }, moves: flag, physics: PHYSICS }, required: ['kind', 'color', 'parts'] },
  style: STYLE_PIECE,
  hood: { type: 'object', props: { kind: { const: 'hood' }, id: { type: 'string' }, color, inner: color, ink: color, wide: num(0.5, 2) }, required: ['kind', 'color'] },
  hat: { type: 'object', props: { kind: { const: 'hat' }, id: { type: 'string' }, color, ink: color }, required: ['kind', 'color'] },
  earDevice: { type: 'object', props: { kind: { const: 'earDevice' }, id: { type: 'string' }, color, dark: color, ink: color }, required: ['kind', 'color'] },
} };
export const HAIR_PARTS = ['cap', 'bangsBlunt', 'bangsSide', 'bangsSpiky', 'sides', 'back', 'sidePart', 'centerPart', 'sideSweep', 'spiky', 'mass', 'messyShort', 'chunky', 'sweptBack', 'topBun', 'twoTails', 'bowl', 'messy', 'fringeTufts', 'strays'];

export function piecesOf(list, ctx) {
  const out = [];
  for (const p of list) {
    if (p.kind === 'nose') out.push(...nose(p, ctx));
    else if (p.kind === 'hair') out.push(...hair(p, ctx));
    else if (p.kind === 'style') out.push(...styleMeshes(p, ctx).map(({ name, positions, triangles, ...o }) => onHead(ctx, name, { positions, triangles }, o)));
    else out.push(extra(p, ctx));
  }
  return out;
}
// a piece on the head: carried by the Head joint (skinned to it alone: every skinning method moves it the same, so the
// cheapest, linear, does), and following the head's skin — bound to the skin of the head nearest it, so whatever changes
// the head's rest in a frame (an expression's morph, a change of the form as a pose layer: a bigger head) moves it too
// (positions in metres, on the body's rest)
function onHead(ctx, name, m, o) {
  const P = m.positions, n = P.length / 3, { omega } = headShares(ctx.body.mesh, ctx.sk);
  return { kind: 'skinned', id: name, positions: P, triangles: m.triangles, floor: false, piece: true, skinning: { method: 'lbs' },
    skin: { K: 1, joints: new Uint8Array(n).fill(ctx.sk.index.Head), weights: new Float32Array(n).fill(1) },
    follow: followOf('body', ctx.body.mesh, ctx.body.mesh.positions, P, Uint8Array.from(omega, w => w > 0.5 ? 1 : 0)), ...o };
}
const toWorld = (P, F) => { const out = new Float32Array(P.length); for (let i = 0; i < P.length; i += 3) { const w = F.toW(P[i], P[i + 1], P[i + 2]); out[i] = w[0]; out[i + 1] = w[1]; out[i + 2] = w[2]; } return out; };

// the drawn nose set on the wrapped face where the skin couldn't take it: a long one — what of the drawn head stands
// out of the face the skin was laid on, closed a little under the skin (its outline only inked); a ball — round, a
// little rosier than the face (`rosy`), with a shine where the key light falls (drawn by the light: src/view3d.js). Each
// takes the face's washes of colour where it stands over them (a nose's tint, the blush across it: src/head/paint.js)
function nose(p, ctx) {
  const G = ctx.form, N = G?.piece; if (!N) throw new Error('a nose piece needs a designed form whose nose is its own piece (form.face.nose.piece)');
  const hsdf = G.sdf, ball = N.ball && N.root;
  let m;
  if (ball) {   // a ball on a capsule nose: the ball round; on a nose drawn by its side curve, what stands out as below
    const b = N.ball, ns = (x, y, z) => smin(sdCapsule(x, y, z, N.root, N.tip, N.radius), sdSphere(x - b.at[0], y - b.at[1], z - b.at[2], b.r), b.k ?? 0.05);
    m = meshOf(ns, [b.at[0] - b.r - 0.1, b.at[1] - b.r - 0.1, 0.5], [b.at[0] + b.r + 0.1, N.root[1] + 0.1, b.at[2] + b.r + 0.1], 0.012);
    const keep = []; for (let t = 0; t < m.triangles.length; t += 3) { let inside = 0; for (let k = 0; k < 3; k++) { const v = m.triangles[t + k]; if (hsdf(m.positions[v * 3], m.positions[v * 3 + 1], m.positions[v * 3 + 2]) < -0.01) inside++; } if (inside < 3) keep.push(m.triangles[t], m.triangles[t + 1], m.triangles[t + 2]); }
    m = { positions: m.positions, triangles: keep };
  } else {
    const ridge = G.nose, ns = (x, y, z) => Math.max(G.full(x, y, z), -(hsdf(x, y, z) + 0.03), ridge(x, y, z) - 0.05);
    m = meshOf(ns, [-0.32, -1.12, 0.4], [0.32, 0.0, 1.72], 0.008);
  }
  const rosy = p.rosy ?? (ball ? 0.25 : 0), base = mixed(rgb(ctx.skin), rgb(ROSY), rosy), w = washes(ctx.features), cl = new Float32Array(m.positions.length);
  for (let v = 0; v < m.positions.length / 3; v++) cl.set(washedAt(w, base, m.positions[v * 3], m.positions[v * 3 + 1]).map(linear), v * 3);
  return [onHead(ctx, 'nose', { positions: toWorld(m.positions, ctx.frame), triangles: m.triangles }, { onFace: true, color: ctx.skin, colors: cl, ink: { width: p.ink ?? (ball ? 0.0014 : 0.0008), color: p.inkColor ?? (ball ? '#7a4a2a' : '#a07882') }, toon: true, ...(ball ? { shine: p.shine ?? 0.85 } : { shadows: false }) })];
}
const ROSY = '#f0a088';

// hoods, hats, an ear device: shells by distance, two-sided — what a head preset wears so it looks as it was drawn, made
// coarse (a garment's form is the clothes' stage: there a hood becomes cloth that doesn't go through the body)
const WEAR_STEP = 0.07, INK = '#2a1e24';
function extra(p, ctx) {
  const W = p.wide ?? 1;
  const sdf = {
    hood: (x, y, z) => { const s0 = smin(sdEll(x, y - 0.12, z + 0.1, 1.24 * W, 1.32, 1.32), sdCapsule(x, y, z, [0, -0.7, -0.3], [0, -2.2, -0.4], [1.15 * W, 1.4 * W]), 0.5); const d = Math.abs(s0) - 0.075, ell = (Math.hypot(x / (0.92 * W), (y + 0.42) / 1.18) - 1) * 0.92, open = smax(ell, -(z - 0.05), 0.1); return smax(d, -open, 0.12); },
    hat: (x, y, z) => { const crown = sdEll(x, y - 1.05, z + 0.05, 1.32, 0.78, 1.28), band = Math.max(Math.abs(y - 0.55) - 0.16, Math.hypot(x / 1.12, (z + 0.04) / 1.14) - 1); return smin(crown, band - 0.03, 0.12); },
    earDevice: (x, y, z) => Math.max(sdCapsule(x, y, z, [-1.0, -0.28, -0.05], [-1.16, -0.28, -0.05], 0.26), 0),
  }[p.kind];
  const m = meshOf(sdf, [-2.4, -3.2, -2.2], [2.4, 2.2, 2.2], WEAR_STEP);
  return onHead(ctx, p.id ?? p.kind, { positions: toWorld(m.positions, ctx.frame), triangles: m.triangles }, { color: p.color, double: true, ink: { width: 0.0018, color: p.ink ?? INK }, toon: true });
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
      const front = o.front ?? 0.4, back = o.back ?? -0.7, core = (x, y, z) => smax(sdEll(x, y - 0.06, z + 0.06, H.w * sc, H.h * sc * 1.02, H.d * sc), lerp(back, front, clamp((z / H.d + 1) / 2, 0, 1) ** 1.3) - y, 0.2);
      solids.push({ sdf: (x, y, z) => { let d = core(x, y, z); for (const [a, b, r] of cl) d = smin(d, sdCapsule(x, y, z, a, b, [r, 0.015]), 0.12); return d; }, core, clumps: cl });
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
  const ink = { width: 0.0016, color: p.ink ?? INK }, F = ctx.frame, id = p.id ?? 'hair';
  // moving (`moves`): every lock and every clump of a mass a guide (src/hair/build.js guideOf) on the head's skull as
  // the hair was drawn on it; the cap, buns and ties ride the head (guide 0)
  const guides = p.moves ? [{ head: true, points: [[0, 0, 0], [0, 0, 0]] }] : null;
  const onSkull = q => { const l = F.toL(...q), d = sub(l, C0); return (len(d) - len(cr(d)) * 1.04) * F.R < 0.03; };
  const guide = (pts, t) => { guides.push(guideOf(pts.map((q, i) => ({ p: F.toW(...q), s: i / (pts.length - 1), t: t * F.R })), {}, false, onSkull)); return guides.length - 1; };
  // a place along a guide (node index and fraction) where its curve's parameter s lies
  const at = (c, s) => { const G = guides[c]; let i = 0; while (i < G.s.length - 2 && G.s[i + 1] < s) i++; return i + clamp((s - G.s[i]) / (G.s[i + 1] - G.s[i]), 0, 1); };
  const sim = bind => guides ? { sim: { piece: id, guides, physics: p.physics ?? {}, bind, normals: 'surface' } } : {};
  solids.forEach((s, k) => {
    const m = meshOf(s.sdf, [-1.7, -1.2, -1.7], [1.7, 1.8, 1.7], 0.035);
    out.push(onHead(ctx, `${id}-${k}`, { positions: toWorld(m.positions, F), triangles: m.triangles }, { color: s.color || p.color, ink, toon: true, ...sim(guides && boundToClumps(m.positions, s, s.clumps ? s.clumps.map(([a, b, r]) => guide(lerpLine(a, b, 6), r * 0.5)) : [], at)) }));
  });
  if (locks.length) {
    // the locks as one mesh (each a ribbon of its own; moving, each on its own guide, ring by ring)
    const P = [], T = [], bc = [], bu = [];
    for (const L of locks) {
      const g = lockGeometry(L), o = P.length / 3, c = guides ? guide(L.pts, L.w * L.flat) : 0, n = L.pts.length, R = (g.positions.length / 3 - 2) / n;
      P.push(...g.positions); for (const i of g.triangles) T.push(i + o);
      if (guides) for (let v = 0; v < g.positions.length / 3; v++) { const ring = v < n * R ? Math.floor(v / R) : v === n * R ? 0 : n - 1; bc.push(c); bu.push(at(c, ring / (n - 1))); }
    }
    const nv = P.length / 3, bind = guides && { c: new Uint16Array(nv * 3), u: new Float32Array(nv * 3), w: new Float32Array(nv * 3) };
    if (bind) for (let v = 0; v < nv; v++) { bind.c[v * 3] = bc[v]; bind.u[v * 3] = bu[v]; bind.w[v * 3] = 1; }
    out.push(onHead(ctx, `${id}-locks`, { positions: toWorld(Float32Array.from(P), F), triangles: T }, { color: p.color, ink: { width: 0.0012, color: p.ink ?? INK }, toon: true, ...sim(bind) }));
  }
  return out;
}
// points along a line from a to b
const lerpLine = (a, b, n) => Array.from({ length: n }, (_, k) => lerp3(a, b, k / (n - 1)));
// a solid of the hair bound to its clumps' guides (each vertex to the nearest few, sharply by how near, the head where
// the solid's core is nearer): {c, u, w} as src/hair/build.js bindOf gives
function boundToClumps(P, s, ids, at) {
  const n = P.length / 3, c = new Uint16Array(n * 3), u = new Float32Array(n * 3), w = new Float32Array(n * 3), cl = s.clumps || [];
  for (let v = 0; v < n; v++) {
    const x = P[v * 3], y = P[v * 3 + 1], z = P[v * 3 + 2], cand = [[0, s.core ? s.core(x, y, z) : -1, 0]];
    cl.forEach(([a, b, r], k) => { const ab = sub(b, a), t = clamp(dot(sub([x, y, z], a), ab) / dot(ab, ab), 0, 1); cand.push([ids[k], sdCapsule(x, y, z, a, b, [r, 0.015]), at(ids[k], t)]); });
    cand.sort((p, q) => p[1] - q[1]);
    const best = cand.slice(0, 3), d0 = best[0][1], ws = best.map(q => Math.exp(-(q[1] - d0) / 0.04)), sw = ws.reduce((a, b) => a + b, 0);
    best.forEach((q, k) => { c[v * 3 + k] = q[0]; u[v * 3 + k] = q[2]; w[v * 3 + k] = ws[k] / sw; });
  }
  return { c, u, w };
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
// a colour: '#rrggbb' → [r, g, b] 0..255; two mixed; one 0..255 sRGB channel as linear 0..1 (vertex colours are linear)
const rgb = c => [1, 3, 5].map(k => parseInt(c.slice(k, k + 2), 16));
const mixed = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
const linear = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
