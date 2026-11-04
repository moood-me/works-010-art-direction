// A head on a body: what a character's `head` makes of its body after the head's form is made (the form is changes of
// the rest — Anny's own face, a head of another age, the face deformers, a wrap onto a designed form: they run with the
// character's other changes of the rest, src/engine.js). Here, on that rest:
//   features   painted (the skin's place in the face's picture and how much of it shows, src/head/features.js: faceUV)
//              and as volume (reliefs)
//   expressions  morphs of the skin (src/head/expressions.js), each played by a pose layer {kind: "expression"}
//   pieces     meshes beside the skin (src/head/pieces.js): rigid on the Head joint or skinned with the body
//   light      how the face is lit (an option): toon with an outline; shading from the designed form (the form's own
//              normals, turned with the skin each frame: src/figure.js); no cast shadows on the face
//   shape      the head to collide with (hair later): the designed form's distance (or a ball fitted to the head), in
//              head units — headShape(pose) in src/figure.js moves it with the Head joint
// buildHead({pre, laid, drawn, post}, head) → {body (post with uv, paint, morphs, shading, head), meshes: [mesh fields]}
//   pre: the body before the head's form; laid: before its wrap (the form is laid on it as the wrap laid it); drawn:
//   right after the wrap (the face is drawn on that head: src/head/features.js picturePlaces), or pre without one;
//   post: after the whole form
import { headFrame, headShares, HEAD_SIZE } from './frame.js';
import { formOnBody } from './wrap.js';
import { picturePlaces, faceUV, reliefsOf } from './features.js';
import { expressionMorph } from './expressions.js';
import { piecesOf } from './pieces.js';
import { gradOf } from './shapes.js';
import { num, flag, color } from '../schema.js';

export const LIGHT_SCHEMA = { type: 'object', props: {
  toon: flag, soft: num(0, 8), shade: num(0, 1), outline: num(0, 0.01), outlineColor: color,
  design: num(0, 1), faceShadows: flag } };
// (shade: the toon's darkest tone — the side away from the key light and what it shadows; Г3's ramp had 0.59 but drew
// cast shadows darker by multiplying them in: 0.45 keeps that weight with the shadows taken through the tones)
export const LIGHT_DEFAULTS = { toon: false, soft: 3, shade: 0.45, outline: 0, outlineColor: '#2a1e24', design: 0, faceShadows: true };

// how near the designed form (head units) the skin counts as lying on it, for its shading
const ON_FORM = 0.03;

export function buildHead({ pre, laid, drawn, post }, head) {
  const sk = post.rig.skeleton, wrap = head.wrap, size = head.size ?? wrap?.form.size ?? HEAD_SIZE;
  const frame = headFrame(post.rig, size), { omega } = headShares(post.mesh, sk), P = post.mesh.positions, N = post.mesh.N;
  const G = wrap ? formOnBody(wrap.form, laid, wrap.neckSlim) : null;
  const light = { ...LIGHT_DEFAULTS, ...head.light };
  // the face's picture: every vertex's place in it (on the head the face is drawn on), how much of it shows
  const drawnFrame = headFrame(drawn.rig, size), pic = picturePlaces(drawn, drawnFrame);
  const { uv, mask: paintMask } = faceUV(pic, P, frame, omega);
  // a grin's teeth end where the skin parts (src/head/paint.js): an open jaw opens below them, into the dark
  const features = head.features.map(f => f.kind === 'mouth' && f.type === 'grin' ? { ...f, parting: partingOf(post.mesh, sk, pic, omega, f) } : f);
  // expressions: morphs of the skin as it is now, placed by where the features are drawn on it
  const eye = features.find(f => f.kind === 'eye') ?? wrap?.marks.eye, mouthF = features.find(f => f.kind === 'mouth' && f.type !== 'none');
  const mouth = mouthF ? { y: mouthF.y, w: mouthF.w, wide: mouthF.type === 'grin' } : wrap?.marks.mouth, brow = features.find(f => f.kind === 'brow');
  const morphs = { ...post.mesh.morphs };
  for (const x of head.expressions) if (x.mesh?.length) morphs[x.name] = expressionMorph(x, { pic, P, mesh: post.mesh, frame, omega, eye, mouth, brow });
  // shading from the designed form: its normals at each vertex's rest place, weighed in as far as the skin lies on the
  // form (fading as it leaves it, down the join with the neck: no seam where the head's share falls)
  let shading = null;
  if (light.design > 0 && G) {
    const normals = new Float32Array(N * 3), weight = new Float32Array(N), g = [0, 0, 0], k = wrap.strength ?? 1;
    for (const i of post.mesh.used) {
      if (omega[i] < 0.005) continue;
      const l3 = frame.toL(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]), d = G.sdf(...l3) / ON_FORM;
      gradOf(G.sdf, ...l3, 0.004, g); const l = Math.hypot(g[0], g[1], g[2]) || 1;
      normals[i * 3] = g[0] / l; normals[i * 3 + 1] = g[1] / l; normals[i * 3 + 2] = g[2] / l;
      weight[i] = light.design * k * Math.exp(-d * d);
    }
    shading = { normals, weight };
  }
  // the face's own shadows: which vertices are face (no cast shadows there, as an option) — as far as it shows the picture
  const face = light.faceShadows ? null : paintMask;
  const shape = G ? { sdf: G.full, frame } : ballOf(P, post.mesh, frame, omega);
  const info = { frame, light, features, expressions: Object.fromEntries(head.expressions.map(x => [x.name, x])), skin: head.skin, shape };
  const body = post.withRest({ mesh: { morphs, uv, paintMask, paint: { features, skin: head.skin }, shading, noShadow: face } });
  body.head = info;
  const cranium = wrap?.form.kind === 'curves' ? { w: 1, h: 1, d: 1.05, ...wrap.form.cranium } : { w: 1, h: 1, d: 1.05 };
  const meshes = [...piecesOf(head.pieces, { form: G, frame, body, sk, skin: head.skin, features, cranium }), ...reliefsOf(features, { drawn, frame: drawnFrame, pic, omega })];
  return { body, meshes };
}

// where the lips part, as it is in the picture under a grin (head units): the lowest of the upper lip's points where the
// jaw's weight changes across a triangle, by its place along the grin — [x, y] from corner to corner
function partingOf(mesh, sk, pic, omega, M) {
  const { jaw } = headShares(mesh, sk), T = mesh.triangles, n = 24, low = new Float64Array(n + 1).fill(Infinity), bin = x => Math.round((x / M.w + 1) / 2 * n);
  for (let t = 0; t < T.length; t += 3) {
    const v = [T[t], T[t + 1], T[t + 2]]; if (Math.max(...v.map(i => jaw[i])) - Math.min(...v.map(i => jaw[i])) < 0.5 || v.some(i => omega[i] < 0.9)) continue;
    for (const i of v) { const x = pic[i * 2], y = pic[i * 2 + 1], k = bin(x); if (jaw[i] >= 0.5 || k < 0 || k > n || Math.abs(y - M.y) > M.w) continue; low[k] = Math.min(low[k], y); }
  }
  const out = []; for (let k = 0; k <= n; k++) if (low[k] < Infinity) out.push([(2 * k / n - 1) * M.w, low[k]]);
  if (out.length < 2) throw new Error('a grin over a head whose lips part nowhere under it');
  return out;
}

// a head without a designed form: a ball fitted to its skin (its centre and mean reach), in head units
function ballOf(P, mesh, frame, omega) {
  let c = [0, 0, 0], n = 0;
  for (const i of mesh.used) if (omega[i] > 0.9) { const l = frame.toL(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]); c[0] += l[0]; c[1] += l[1]; c[2] += l[2]; n++; }
  c = c.map(v => v / n); let r = 0;
  for (const i of mesh.used) if (omega[i] > 0.9) { const l = frame.toL(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]); r += Math.hypot(l[0] - c[0], l[1] - c[1], l[2] - c[2]); }
  r /= n;
  return { sdf: (x, y, z) => Math.hypot(x - c[0], y - c[1], z - c[2]) - r, frame };
}
