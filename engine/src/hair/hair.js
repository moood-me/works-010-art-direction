// Hair as a head's piece (src/head/pieces.js), and hair that moves.
// A hairstyle of В1 is a piece {kind: "style", style, …} (its builders and styles: src/hair/build.js, styles.js):
//   style        which hairstyle (STYLES)
//   off, only    groups of it taken away, or the only ones kept (`fringe`, `back`, `under`…: each style names its own)
//   color        its colour (its own parts' — a hat's fabric keeps its own)
//   shading      how its strands take the light (HAIR_SHADING: the highlights, how dark the hair is inside, the strands)
//   moves        whether it moves (true by default; false: it rides the head as it was designed)
//   physics      how it moves, each a share of the hairstyle's own (1): hold (how firmly it keeps its designed shape),
//                bend (how stiff each lock is), drag (how much the air holds it), wind (how much the wind takes it)
// Г1's hair (kind "hair", drawn as it was) takes `moves` and `physics` too: its locks and its masses' clumps then hang
// on chains of the same simulation, its cap rides the head (src/head/pieces.js).
// A hairstyle takes 4–15 s to build: it is built once in its design space and stored by the key of what it is built
// from (data/hair/, tools/characters.mjs hair) — then fitted onto each head (src/hair/fit.js) when the head is made.
import { STYLES } from './styles.js';
import { buildHair, bindOf, headSDF } from './build.js';
import { fitOn } from './fit.js';
import { HairSim } from './sim.js';
import { hashOf } from '../hash.js';
import { num, flag, color } from '../schema.js';
import { HEAD_BUILD } from '../head/version.js';

export const HAIR_SHADING = { spec: num(0, 4), spec2: num(0, 4), shift: num(-0.5, 0.5), inner: num(0, 1), strands: num(0, 2), ink: num(0, 0.005) };
export const PHYSICS = { type: 'object', props: { hold: num(0, 4), bend: num(0, 4), drag: num(0, 4), wind: num(0, 4) } };
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
export const styleKey = p => hashOf(['engine/hair', HEAD_BUILD.hair, p.style, [...(p.off || [])].sort(), p.only ? [...p.only].sort() : null]).slice(0, 16);

// a hairstyle built in its design space: its surfaces (each with what its shading needs and how it is bound to the
// guides) and its guides — the header and arrays of a pack, as data/hair/ stores it: directions and shares in bytes,
// places along a lock in 1/32767ths, a binding's place in 1/2048ths of a node (what a picture can tell apart stays)
export function buildStyle(p) {
  const S = styleOf(p), built = buildHair(S, headSDF(S.head || {}).sdf), { guides, binds } = bindOf(built);
  const arrays = {}, meshes = built.map((e, k) => {
    const m = e.mesh, nv = m.pos.length / 3, a = (name, array, w) => { arrays[`m${k}.${name}`] = { array, shape: [array.length / w, w] }; };
    const unit = v => Uint8Array.from(v, x => Math.round((Math.max(-1, Math.min(1, x)) * 0.5 + 0.5) * 255)), share = (v, top = 1) => Uint8Array.from(v, x => Math.round(Math.max(0, Math.min(1, x / top)) * 255));
    a('positions', m.pos, 3); a('normals', unit(m.nor), 3); a('triangles', nv > 65536 ? Uint32Array.from(m.idx) : Uint16Array.from(m.idx), 3);
    if (!e.plain) { a('tangents', unit(m.tan), 3); a('uv', Int16Array.from(m.uv, (x, i) => Math.round(i % 2 ? x * 32767 : Math.max(-1, Math.min(1, x / UV_ACROSS)) * 32767)), 2); a('seed', share(m.seed), 1); a('ao', share(m.ao), 1); a('colors', m.ci, 1); a('width', share(m.wd ?? new Float32Array(nv).fill(0.006), WIDTH_TOP), 1); }
    a('bindC', binds[k].c, 3); a('bindU', Uint16Array.from(binds[k].u, u => Math.round(u * 2048)), 3); a('bindW', share(binds[k].w), 3);
    return { kind: e.plain ? 'fabric' : e.lockLayer ? 'locks' : 'inner', palette: e.palette.map(hexOf), rough: e.rough ?? null, ink: e.ink ?? null };
  });
  return { header: { format: 'engine/hair', version: 1, key: styleKey(p), style: p.style, off: p.off ?? [], only: p.only ?? null, meshes, guides }, arrays };
}
const hexOf = c => '#' + c.toString(16).padStart(6, '0'), UV_ACROSS = 0.1, WIDTH_TOP = 0.012;
// a stored hairstyle's arrays as numbers again
function unpacked(A) {
  const out = {}, unit = v => { const o = Float32Array.from(v, q => q / 255 * 2 - 1); for (let i = 0; i < o.length; i += 3) { const l = Math.hypot(o[i], o[i + 1], o[i + 2]) || 1; o[i] /= l; o[i + 1] /= l; o[i + 2] /= l; } return o; };
  for (const [key, v] of Object.entries(A)) {
    const name = key.split('.')[1];
    out[key] = name === 'normals' || name === 'tangents' ? unit(v) : name === 'uv' ? Float32Array.from(v, (q, i) => i % 2 ? q / 32767 : q / 32767 * UV_ACROSS)
      : name === 'seed' || name === 'ao' || name === 'bindW' ? Float32Array.from(v, q => q / 255) : name === 'width' ? Float32Array.from(v, q => q / 255 * WIDTH_TOP)
      : name === 'bindU' ? Float32Array.from(v, q => q / 2048) : v;
  }
  return out;
}

// every built hairstyle a head's pieces ask for: stored, or built here (an author's new choice of groups)
export async function stylesOf(pieces, E) {
  const out = new Map();
  for (const p of pieces) if (p.kind === 'style' && !out.has(styleKey(p))) {
    const s = await E.stored('hair', styleKey(p)) ?? (b => ({ header: b.header, arrays: Object.fromEntries(Object.entries(b.arrays).map(([k, v]) => [k, v.array])) }))(buildStyle(p));
    out.set(styleKey(p), { header: s.header, arrays: unpacked(s.arrays) });
  }
  return out;
}

// a hairstyle's surfaces on a head: fitted onto it (its designed form where it has one, else its skin), each a mesh's
// fields (src/head/pieces.js lays them on the head) with its hair shading and, when it moves, what binds it to the guides
//   ctx: {frame, form, body, sk, styles (stylesOf)}
export function styleMeshes(p, ctx) {
  const built = ctx.styles.get(styleKey(p)), { header: h, arrays: A } = built, fit = fitOn(ctx), sc = fit.scale;
  const id = p.id ?? 'hair', moves = p.moves ?? true;
  const guides = h.guides.map(g => g.head ? g : { ...g, points: g.points.map(q => fit.map(...q)), rad: g.rad.map(r => r * sc) });
  const sim = moves ? { piece: id, guides, physics: p.physics ?? {} } : null;
  return h.meshes.map((m, k) => {
    const get = n => A[`m${k}.${n}`], P = get('positions'), n = P.length / 3, Q = new Float32Array(n * 3), o = [0, 0, 0];
    for (let v = 0; v < n; v++) { fit.map(P[v * 3], P[v * 3 + 1], P[v * 3 + 2], o); Q[v * 3] = o[0]; Q[v * 3 + 1] = o[1]; Q[v * 3 + 2] = o[2]; }
    const palette = m.palette.map((c, i) => i === 0 && m.kind !== 'fabric' && p.color ? p.color : c), ci = get('colors');
    const colors = new Float32Array(n * 3); for (let v = 0; v < n; v++) colors.set(linear(palette[ci ? ci[v] : 0]), v * 3);
    const fields = { name: `${id}-${k}`, positions: Q, triangles: get('triangles'), colors, color: palette[0],
      shading: { whole: true, normals: Float32Array.from(get('normals')), weight: new Float32Array(n).fill(1), ...(get('tangents') ? { tangents: Float32Array.from(get('tangents')) } : {}) },
      sim: sim && { ...sim, bind: { c: get('bindC'), u: get('bindU'), w: get('bindW') }, normals: 'design' } };
    if (m.kind === 'fabric') return { ...fields, rough: m.rough ?? 0.85, ink: { width: 0.0012, color: INK } };
    const width = Float32Array.from(get('width'), w => Math.min(1, Math.max(0.1, w * sc / 0.006)));
    return { ...fields, hair: { layer: m.kind, uv: get('uv'), seed: get('seed'), ao: get('ao'), width, shading: { ...SHADING, ...(STYLES[p.style].shading || {}), ...(p.shading || {}) } } };
  });
}
export const SHADING = { spec: 1, spec2: 0.6, shift: 0.12, inner: 0.8, strands: 1, ink: 0.0007 };
const INK = '#24161a';
const linear = c => [1, 3, 5].map(k => { const v = parseInt(c.slice(k, k + 2), 16) / 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; });

// the simulations a figure's meshes ask for: one per hair piece that moves, its surfaces bound to its guides
export function hairSims(figure) {
  const pieces = new Map();
  for (const o of figure.outputs) { const s = o.mesh.sim; if (!s) continue; if (!pieces.has(s.piece)) pieces.set(s.piece, { guides: s.guides, physics: s.physics, meshes: [] }); pieces.get(s.piece).meshes.push({ output: o, bind: s.bind, normals: s.normals }); }
  return [...pieces.values()].map(p => new HairSim(figure, p));
}
