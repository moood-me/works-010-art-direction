// Hair as a head's piece (src/head/pieces.js), and hair that moves.
// A hairstyle of В1 is a piece {kind: "style", style, …} (its builders and styles: src/hair/build.js, styles.js):
//   style        which hairstyle (STYLES)
//   off, only    groups of it taken away, or the only ones kept (`fringe`, `back`, `under`…: each style names its own)
//   color        its colour (each part's own; what has a colour of its own — a streak, a band, a hat's fabric — keeps it)
//   shading      how its strands take the light (HAIR_SHADING: the highlights, how dark the hair is inside, the strands)
//   moves        whether it moves (true by default; false: it rides the head as it was designed)
//   physics      how it moves, each a share of the hairstyle's own (1): hold (how firmly it keeps its designed shape),
//                bend (how stiff each lock is), drag (how much the air holds it), wind (how much the wind takes it),
//                friction (against the body), damping (how fast its own motion against the head and its zigzags die),
//                together (how much neighbouring locks move as one)
// Г1's hair (kind "hair", drawn as it was) takes `moves` and `physics` too: its locks and its masses' clumps then hang
// on chains of the same simulation, its cap rides the head (src/head/pieces.js).
// What of a hairstyle is slow to build (src/hair/build.js: its inner layers and occlusion, 5–20 s) is built once in its
// design space and stored by the key of what it is built from (data/hair/, tools/characters.mjs hair); its locks and
// guides are made beside it when it is used, and it is fitted onto each head (src/hair/fit.js) when the head is made.
import { STYLES } from './styles.js';
import { partsOf, guidesOf, innerOf, locksOf, occlusionOf, headSDF } from './build.js';
import { fitOn } from './fit.js';
import { HairSim } from './sim.js';
import { hashOf } from '../hash.js';
import { num, flag, color } from '../schema.js';
import { HEAD_BUILD } from '../head/version.js';

export const HAIR_SHADING = { spec: num(0, 4), spec2: num(0, 4), shift: num(-0.5, 0.5), inner: num(0, 1), strands: num(0, 2), ink: num(0, 0.005) };
export const PHYSICS = { type: 'object', props: { hold: num(0, 4), bend: num(0, 4), drag: num(0, 4), wind: num(0, 4), friction: num(0, 2.5), damping: num(0, 4), together: num(0, 4) } };
const groupsOf = id => [...new Set(STYLES[id].parts.flatMap(p => Object.keys(p.items)))];
export const STYLE_PIECE = { type: 'object', props: {
  kind: { const: 'style' }, id: { type: 'string' }, style: { type: 'string', enum: Object.keys(STYLES) },
  off: { type: 'array', items: { type: 'string', pattern: /^[a-zA-Z]+$/ } }, only: { type: 'array', items: { type: 'string', pattern: /^[a-zA-Z]+$/ } },
  color, shading: { type: 'object', props: HAIR_SHADING }, moves: flag, physics: PHYSICS }, required: ['kind', 'style'] };

// the hairstyle a piece asks for: its style with the groups it keeps
function styleOf(p) {
  const S = STYLES[p.style], all = groupsOf(p.style);
  for (const g of [...(p.off || []), ...(p.only || [])]) if (!all.includes(g)) throw new Error(`hair "${p.style}" has no group "${g}" (it has ${all.join(', ')})`);
  const keep = g => (!p.only || p.only.includes(g)) && !(p.off || []).includes(g);
  const parts = S.parts.map(part => ({ ...part, items: Object.fromEntries(Object.entries(part.items).filter(([g]) => keep(g))) })).filter(part => Object.keys(part.items).length);
  if (!parts.length) throw new Error(`hair "${p.style}": every group taken away`);
  return { ...S, parts };
}
// the files a stored hairstyle is built by (from engine/): their content's hash is kept beside the store
// (data/hair/index.json source), so a change of the code under it is seen even where the version was not raised
export const BUILD_SOURCES = ['src/hair/build.js', 'src/hair/styles.js', 'src/hair/hair.js', 'src/decimate.js'];
export const styleKey = p => hashOf(['engine/hair', HEAD_BUILD.hair, p.style, [...(p.off || [])].sort(), p.only ? [...p.only].sort() : null]).slice(0, 16);

// a hairstyle built in its design space: what is slow to make, as data/hair/ stores it — each part's inner layer (or a
// fabric's surface) and its locks' occlusion; positions in 1/65535ths of the surface's box, directions and shares in
// bytes, places along a lock in 1/32767ths, a binding's place in 1/2048ths of a node (what a picture can tell apart
// stays). The locks themselves, the guides and how the locks ride them are quick and made where it is used (assembled).
export function buildStyle(p) {
  const S = styleOf(p), parts = partsOf(S), G = guidesOf(parts), head = headSDF(S.head || {}).sdf, arrays = {}, meshes = [];
  const unit = v => Uint8Array.from(v, x => Math.round((Math.max(-1, Math.min(1, x)) * 0.5 + 0.5) * 255)), share = v => Uint8Array.from(v, x => Math.round(Math.max(0, Math.min(1, x)) * 255));
  for (const P of parts) {
    const k = meshes.length, a = (name, array, w) => { arrays[`m${k}.${name}`] = { array, shape: [array.length / w, w] }; };
    const m = innerOf(P, parts, head, G), nv = m.pos.length / 3, lo = [0, 1, 2].map(c => Math.min(...m.pos.filter((_, i) => i % 3 === c))), hi = [0, 1, 2].map(c => Math.max(...m.pos.filter((_, i) => i % 3 === c)));
    a('positions', Uint16Array.from(m.pos, (x, i) => Math.round((x - lo[i % 3]) / Math.max(1e-9, hi[i % 3] - lo[i % 3]) * 65535)), 3); a('normals', unit(m.nor), 3); a('triangles', nv > 65536 ? Uint32Array.from(m.idx) : Uint16Array.from(m.idx), 3);
    if (P.palette.length > 1) a('colors', m.ci, 1);
    if (!P.plain) { a('tangents', unit(m.tan), 3); a('uv', Int16Array.from(m.uv, (x, i) => Math.round(i % 2 ? x * 32767 : Math.max(-1, Math.min(1, x / UV_ACROSS)) * 32767)), 2); a('seed', share(m.seed), 1); a('ao', share(m.ao), 1); a('bindC', m.bind.c, 3); a('bindU', Uint16Array.from(m.bind.u, u => Math.round(u * 2048)), 3); a('bindW', share(m.bind.w), 3); }
    meshes.push({ kind: P.plain ? 'fabric' : 'inner', palette: P.palette.map(hexOf), rough: P.part.rough ?? null, ink: P.part.ink ?? null, box: [lo, hi] });
    if (P.plain || !P.locks.length) continue;
    const L = locksOf(P, G);
    arrays[`m${meshes.length}.ao`] = { array: share(occlusionOf(parts, head, L)), shape: [L.pos.length / 3, 1] };
    meshes.push({ kind: 'locks', palette: P.palette.map(hexOf), rough: P.part.rough ?? null, ink: P.part.ink ?? null });
  }
  return { header: { format: 'engine/hair', version: 2, key: styleKey(p), style: p.style, off: p.off ?? [], only: p.only ?? null, meshes }, arrays };
}
const hexOf = c => '#' + c.toString(16).padStart(6, '0'), UV_ACROSS = 0.1, WIDTH_TOP = 0.012;
// a stored hairstyle as its surfaces and guides: the stored arrays as numbers again, the locks made anew beside them
function assembled(p, { header: h, arrays: A }) {
  const S = styleOf(p), parts = partsOf(S), G = guidesOf(parts), out = {}, unit = v => { const o = Float32Array.from(v, q => q / 255 * 2 - 1); for (let i = 0; i < o.length; i += 3) { const l = Math.hypot(o[i], o[i + 1], o[i + 2]) || 1; o[i] /= l; o[i + 1] /= l; o[i + 2] /= l; } return o; };
  let k = 0;
  for (const P of parts) {
    const get = n => A[`m${k}.${n}`], [lo, hi] = h.meshes[k].box, Q = get('positions'), nv = Q.length / 3;
    const o = { positions: Float32Array.from(Q, (q, i) => lo[i % 3] + q / 65535 * (hi[i % 3] - lo[i % 3])), normals: unit(get('normals')), triangles: get('triangles'), colors: get('colors') ?? null };
    if (!P.plain) Object.assign(o, { tangents: unit(get('tangents')), uv: Float32Array.from(get('uv'), (q, i) => i % 2 ? q / 32767 : q / 32767 * UV_ACROSS), seed: Float32Array.from(get('seed'), q => q / 255), ao: Float32Array.from(get('ao'), q => q / 255),
      width: new Float32Array(nv).fill(0.006), bind: { c: get('bindC'), u: Float32Array.from(get('bindU'), q => q / 2048), w: Float32Array.from(get('bindW'), q => q / 255) } });
    else o.bind = { c: new Uint16Array(nv * 3), u: new Float32Array(nv * 3), w: Float32Array.from({ length: nv * 3 }, (_, i) => i % 3 ? 0 : 1) };
    out[k++] = o;
    if (P.plain || !P.locks.length) continue;
    const L = locksOf(P, G);
    out[k] = { positions: L.pos, normals: L.nor, triangles: L.idx, colors: L.ci, tangents: L.tan, uv: L.uv, seed: L.seed, width: Float32Array.from(L.wd, w => Math.min(w, WIDTH_TOP)), ao: Float32Array.from(A[`m${k}.ao`], q => q / 255), bind: L.bind };
    k++;
  }
  return { header: h, guides: G.guides, meshes: out };
}

// every built hairstyle a head's pieces ask for: stored, or built here (an author's new choice of groups)
export async function stylesOf(pieces, E) {
  const out = new Map();
  for (const p of pieces) if (p.kind === 'style' && !out.has(styleKey(p))) {
    const s = await E.stored('hair', styleKey(p)) ?? (b => ({ header: b.header, arrays: Object.fromEntries(Object.entries(b.arrays).map(([k, v]) => [k, v.array])) }))(buildStyle(p));
    out.set(styleKey(p), assembled(p, s));
  }
  return out;
}

// a hairstyle's surfaces on a head: fitted onto it (its designed form where it has one, else its skin), each a mesh's
// fields (src/head/pieces.js lays them on the head) with its hair shading and, when it moves, what binds it to the guides
//   ctx: {frame, form, body, sk, styles (stylesOf)}
export function styleMeshes(p, ctx) {
  const built = ctx.styles.get(styleKey(p)), { header: h } = built, design = headSDF(STYLES[p.style].head || {}).sdf, fit = fitOn(ctx, design), sc = fit.scale;
  const id = p.id ?? 'hair', moves = p.moves ?? true;
  // (a root's place: as deep under the head's surface as the design has it under the designed head's, grown with the head)
  const guides = built.guides.map(g => g.head ? g : { ...g, points: g.points.map(q => fit.map(...q)), rad: g.rad.map(r => r * sc), ...(g.rooted ? { depth: design(...g.points[0]) * sc } : {}) });
  // a change of the rest as a pose layer (a bigger head) moves the hair as it moves the hairstyle fitted onto the skin:
  // fitted onto the changed body, against fitted onto the body before it (src/deform.js restLayer: bodies), per surface
  // and for the guides — made once per change
  const growth = new WeakMap(), grownBy = (from, to) => {
    const byTo = growth.get(from) ?? growth.set(from, new WeakMap()).get(from);
    if (byTo.has(to)) return byTo.get(to);
    const a = fitOn({ ...ctx, form: null, body: from }, design), b = fitOn({ ...ctx, form: null, body: to }, design), pa = [0, 0, 0], pb = [0, 0, 0];
    const delta = P => { const idx = [], del = []; for (let v = 0; v < P.length / 3; v++) { a.map(P[v * 3], P[v * 3 + 1], P[v * 3 + 2], pa); b.map(P[v * 3], P[v * 3 + 1], P[v * 3 + 2], pb); if (Math.abs(pb[0] - pa[0]) + Math.abs(pb[1] - pa[1]) + Math.abs(pb[2] - pa[2]) > 1e-7) { idx.push(v); del.push(pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]); } } return { indices: Uint32Array.from(idx), deltas: Float32Array.from(del) }; };
    const out = { meshes: built.meshes && Object.values(built.meshes).map(B => delta(B.positions)), guides: built.guides.map(g => g.head ? null : delta(Float32Array.from(g.points.flat()))) };
    byTo.set(to, out); return out;
  };
  const sim = moves ? { piece: id, guides, physics: p.physics ?? {}, grows: (from, to) => grownBy(from, to).guides } : null;
  return h.meshes.map((m, k) => {
    const B = built.meshes[k], P = B.positions, n = P.length / 3, Q = new Float32Array(n * 3), o = [0, 0, 0];
    for (let v = 0; v < n; v++) { fit.map(P[v * 3], P[v * 3 + 1], P[v * 3 + 2], o); Q[v * 3] = o[0]; Q[v * 3 + 1] = o[1]; Q[v * 3 + 2] = o[2]; }
    // (the colour asked for is the hair's own — each part's first; what has a colour of its own, a streak, a band, a
    // hat's fabric, keeps it)
    const palette = m.palette.map((c, i) => i === 0 && m.kind !== 'fabric' && p.color ? p.color : c), ci = B.colors;
    const colors = new Float32Array(n * 3); for (let v = 0; v < n; v++) colors.set(linear(palette[ci ? ci[v] : 0]), v * 3);
    const fields = { name: `${id}-${k}`, positions: Q, triangles: B.triangles, colors, color: palette[0], grows: (from, to) => grownBy(from, to).meshes[k],
      shading: { whole: true, normals: B.normals, weight: new Float32Array(n).fill(1), ...(B.tangents ? { tangents: B.tangents } : {}) },
      sim: sim && { ...sim, bind: B.bind, normals: 'design' } };
    if (m.kind === 'fabric') return { ...fields, rough: m.rough ?? 0.85, ink: { width: 0.0012, color: INK } };
    const width = Float32Array.from(B.width, w => Math.min(1, Math.max(0.1, w * sc / 0.006)));
    return { ...fields, hair: { layer: m.kind, uv: B.uv, seed: B.seed, ao: B.ao, width, shading: { ...SHADING, ...(STYLES[p.style].shading || {}), ...(p.shading || {}) } } };
  });
}
export const SHADING = { spec: 1, spec2: 0.6, shift: 0.12, inner: 0.8, strands: 1, ink: 0.0007 };
const INK = '#24161a';
const linear = c => [1, 3, 5].map(k => { const v = parseInt(c.slice(k, k + 2), 16) / 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; });

// the simulations a figure's meshes ask for: one per hair piece that moves, its surfaces bound to its guides
export function hairSims(figure) {
  const pieces = new Map();
  for (const o of figure.outputs) { const s = o.mesh.sim; if (!s) continue; if (!pieces.has(s.piece)) pieces.set(s.piece, { guides: s.guides, physics: s.physics, grows: s.grows, meshes: [] }); pieces.get(s.piece).meshes.push({ output: o, bind: s.bind, normals: s.normals }); }
  return [...pieces.values()].map(p => new HairSim(figure, p));
}
