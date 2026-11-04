// Clothes as a character's parts: what it wears, each garment of a pattern (src/cloth/patterns.js) in a fabric, with
// its colour and, if it has one, its designed silhouette (src/cloth/shape.js) and how firmly the cloth holds it.
//   a character's `clothes: [garment…]`, a garment:
//     {kind: "garment", id?, pattern, fabric, color, shape?, strength?, moves?, wide?}
//       id        what it is called among the character's clothes (else its pattern's id): what a character that starts
//                 from this one changes it by
//       pattern   how it is cut (PATTERNS: MakeHuman's `mh-*`, those made on the body, the hood)
//       fabric    a preset of group fabric ("fabric-denim@…") or a fabric's own keys (FABRIC)
//       shape     a preset of group garment-shape or a design's own keys (src/cloth/shape.js SHAPE): the silhouette the
//                 cloth is cut to and pulled toward
//       strength  how firmly it holds the shape (1: a stiff petticoat holds the bell; 0: the cloth hangs freely as it
//                 was cut; 1 with a shape, else 0). With no shape the garment is cut as its pattern is, and a strength
//                 holds it to that (a stiff hood keeps its shell)
//       moves     cloth (true, by default) or carried by the skin as it is cut (false: shoes are; anything can be)
//       wide      a hood's width (its shell's, against the head's: 1)
//     {kind: "preset", id}    an outfit: a preset of group outfit holding garments (`clothes`), taken in
//     {kind: "off", id}       one of those it starts from (its base's, an outfit's) taken away
//     {id, …keys}             one of those changed: only the keys that change (then checked whole)
// A character's clothes go over its base's by id: the same as a head's pieces (src/parts.js).
// Each garment is a skinned mesh of the figure (its skin each point's nearest skin vertex's, so a change of the rest
// as a pose layer moves it as the body), driven by one simulation for all its cloth (src/cloth/sim.js); what does not
// move is skinned as the body.
import { num, flag, color, pin } from '../schema.js';
import { makeMesh } from '../mesh.js';
import { Skinner } from '../skin.js';
import { headFrame } from '../head/frame.js';
import { PATTERNS, cutFor, onBody, stenciled, nearestOn } from './patterns.js';
import { designedForm, SHAPE } from './shape.js';
import { ClothSim } from './sim.js';
import { sst, clamp } from '../math.js';

// density kg/m²; stretch N/m (how hard it holds against pulling); compress: its share when pushed together (low: it
// folds); bend: bending rigidity N·m (Kawabata's B, per metre of width); damping 1/s; friction on skin and cloth; thick:
// half its thickness and a little air, m; air: how much the air takes it (1: an ordinary weave); sheen, rough, opacity:
// how it takes the light
export const FABRIC = { type: 'object', required: ['density', 'stretch', 'bend'], props: {
  density: num(0.005, 3), stretch: num(1, 100000), compress: num(0.01, 1), bend: num(1e-8, 0.01), damping: num(0, 20), friction: num(0, 2),
  thick: num(0.0005, 0.02), air: num(0, 3), sheen: num(0, 1), rough: num(0, 1), opacity: num(0.1, 1) } };
export const FABRIC_DEFAULTS = { compress: 0.25, damping: 0.4, friction: 0.5, thick: 0.0025, air: 1, sheen: 0.2, rough: 0.85, opacity: 1 };
export const SHAPE_SCHEMA = { type: 'object', props: SHAPE };
export const GARMENT_SCHEMA = { type: 'union', key: 'kind', cases: {
  garment: { type: 'object', required: ['kind', 'pattern', 'fabric', 'color'], props: {
    kind: { const: 'garment' }, id: { type: 'string', pattern: /^[a-z][a-z0-9-]*$/ }, pattern: { type: 'string', enum: Object.keys(PATTERNS) },
    fabric: { anyOf: [pin, FABRIC] }, color, shape: { anyOf: [pin, SHAPE_SCHEMA] }, strength: num(0, 2), moves: flag, wide: num(0.5, 2) } },
} };
export const garmentId = g => g.id ?? g.pattern;

// the garments laid on a body (the character's rest, its head made): each its mesh and what its simulation needs.
// list: the character's clothes as expanded (each fabric and shape a design's keys); head: the body's head (its frame)
export async function clothesOn(body, list, E) {
  const B = onBody(body), frame = body.head?.frame ?? headFrame(body.rig), out = [];
  for (const g of list) {
    const P = PATTERNS[g.pattern], cut = await cutFor(body, g.pattern, E, { frame, wide: g.wide }), moves = !P.rides && g.moves !== false;
    // (the form it is pulled toward: its design, or — given a strength and no design — the cut itself: a stiff hood)
    const form = !moves ? null : g.shape ? designedForm(cut, B, g.shape, P) : g.strength ? Float32Array.from(cut.positions) : null, rest = form ?? cut.positions, F = { ...FABRIC_DEFAULTS, ...g.fabric };
    // simulated as cut (its points each skinned as the skin nearest it is: where the skin carries it), drawn as the
    // figure's mesh — subdivided where the cut is coarse, its points skinned the same way (what does not move)
    const sim = skinnedOn(body, `cloth-${garmentId(g)}-cut`, rest, cut.triangles, cut.near), D = cut.drawn;
    const drawnAt = D ? stenciled(D, rest) : Float32Array.from(rest);
    const mesh = skinnedOn(body, `cloth-${garmentId(g)}`, drawnAt, D ? D.triangles : cut.triangles, D ? nearestOn(body.mesh.positions, drawnAt, body.mesh.used) : cut.near,
      { floor: !moves, cloth: { color: g.color, fabric: F, pattern: g.pattern }, skinning: { method: 'lbs' } });
    out.push({ mesh, garment: g, cut, form, moves, fabric: F, pattern: P, sim: moves ? new Skinner(sim, body.rig, { method: 'lbs' }) : null, drawn: D,
      carrier: form ? carrierOf(body, sim, form, P) : null, home: Uint8Array.from(cut.near, b => P.tubes ? B.limb[b] : 0) });
  }
  return out;
}
// a mesh skinned as the body's skin nearest each of its points is (near: those vertices)
function skinnedOn(body, id, positions, triangles, near, more = {}) {
  const n = positions.length / 3, K = body.mesh.skin.K, joints = new Uint8Array(n * K), weights = new Float32Array(n * K);
  for (let i = 0; i < n; i++) for (let k = 0; k < K; k++) { joints[i * K + k] = body.mesh.skin.joints[near[i] * K + k]; weights[i * K + k] = body.mesh.skin.weights[near[i] * K + k]; }
  return makeMesh({ kind: 'skinned', id, positions: Float32Array.from(positions), triangles, skin: { joints, weights, K }, ...more });
}
// what carries the designed form: the skin where the garment is fitted, the pelvis where it hangs below the hips (a skirt's
// bell swings with the hips, not with each thigh: О1's)
function carrierOf(body, mesh, form, P) {
  const sk = body.rig.skeleton, K = mesh.skin.K, n = mesh.N, hipY = body.rig.joints[sk.index.Hips * 3 + 1], H = sk.index.Hips;
  const joints = new Uint8Array(n * K), weights = new Float32Array(n * K);
  for (let i = 0; i < n; i++) {
    // the skin's weights given up to the pelvis by how far below the hips the point hangs; the K strongest kept
    const wt = P.hangs ? sst(clamp((hipY - form[i * 3 + 1]) / 0.3, 0, 1)) : 0, w = new Map([[H, wt]]);
    for (let k = 0; k < K; k++) { const j = mesh.skin.joints[i * K + k], v = mesh.skin.weights[i * K + k] * (1 - wt); if (v) w.set(j, (w.get(j) ?? 0) + v); }
    const top = [...w].sort((a, b) => b[1] - a[1]).slice(0, K), s = top.reduce((a, [, v]) => a + v, 0);
    top.forEach(([j, v], k) => { joints[i * K + k] = j; weights[i * K + k] = v / s; });
  }
  return new Skinner(makeMesh({ kind: 'skinned', id: mesh.id + '-form', positions: form, triangles: mesh.triangles, skin: { joints, weights, K } }), body.rig, { method: 'lbs' });
}
// the simulation of a figure's cloth (one for all of it), its garments' outputs found by their meshes
export function clothSim(figure, laid) {
  const moving = laid.filter(l => l.moves);
  if (!moving.length) return null;
  return new ClothSim(figure, moving.map(l => ({ ...l, output: figure.outputs.find(o => o.mesh === l.mesh), strength: l.form ? l.garment.strength ?? 1 : 0 })));
}
