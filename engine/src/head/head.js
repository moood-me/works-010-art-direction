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
// buildHead(pre, post, head) → {body (post with uv, paint, morphs, shading, head), meshes: [mesh fields]}
//   pre: the body before the head's form (the wrap's form is laid on it as the wrap laid it), post: after it
import { headFrame, headShares } from './frame.js';
import { formOnBody } from './wrap.js';
import { faceUV, reliefsOf } from './features.js';
import { expressionMorph } from './expressions.js';
import { piecesOf } from './pieces.js';
import { gradOf } from './shapes.js';
import { clamp, sst } from '../math.js';

const num = (min, max) => ({ type: 'number', min, max });
export const LIGHT_SCHEMA = { type: 'object', props: {
  toon: { type: 'boolean' }, soft: num(0, 8), outline: num(0, 0.01), outlineColor: { type: 'string', pattern: /^#[0-9a-f]{6}$/i },
  design: num(0, 1), faceShadows: { type: 'boolean' } } };
export const LIGHT_DEFAULTS = { toon: false, soft: 3, outline: 0, outlineColor: '#2a1e24', design: 0, faceShadows: true };

export function buildHead(pre, post, head) {
  const sk = post.rig.skeleton, wrap = head.wrap, size = head.size ?? wrap?.form.size ?? 1.1;
  const frame = headFrame(post.rig, size), { omega } = headShares(post.mesh, sk), P = post.mesh.positions, N = post.mesh.N;
  const G = wrap ? formOnBody(wrap.form, pre, wrap.neckSlim ?? 0.78) : null;
  const light = { ...LIGHT_DEFAULTS, ...head.light };
  const eye = head.features.find(f => f.kind === 'eye') ?? wrap?.marks.eye, mouthF = head.features.find(f => f.kind === 'mouth' && f.type !== 'none');
  const mouth = mouthF ? { y: mouthF.y, w: mouthF.w, wide: mouthF.type === 'grin' } : wrap?.marks.mouth, brow = head.features.find(f => f.kind === 'brow');
  // the face's picture: every vertex's place in it
  const { uv, mask: paintMask } = faceUV(P, post.mesh, frame, omega);
  // expressions: morphs of the skin as it is now
  const morphs = { ...post.mesh.morphs };
  for (const x of head.expressions) if (x.mesh?.length) morphs[x.name] = expressionMorph(x, { P, mesh: post.mesh, frame, omega, eye, mouth, brow });
  // shading from the designed form: its normals at each vertex's rest place, weighed in where the skin is the form's
  let shading = null;
  if (light.design > 0 && G) {
    const normals = new Float32Array(N * 3), weight = new Float32Array(N), g = [0, 0, 0], k = wrap.strength ?? 1;
    for (const i of post.mesh.used) {
      if (omega[i] < 0.05) continue;
      gradOf(G.sdf, ...frame.toL(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]), 0.004, g); const l = Math.hypot(g[0], g[1], g[2]) || 1;
      normals[i * 3] = g[0] / l; normals[i * 3 + 1] = g[1] / l; normals[i * 3 + 2] = g[2] / l;
      weight[i] = light.design * k * sst(clamp((omega[i] - 0.3) / 0.6, 0, 1));
    }
    shading = { normals, weight };
  }
  // the face's own shadows: which vertices are face (no cast shadows there, as an option)
  const face = light.faceShadows ? null : Float32Array.from(omega, (w, i) => sst(clamp((w - 0.3) / 0.5, 0, 1)) * (frame.toL(P[i * 3], P[i * 3 + 1], P[i * 3 + 2])[2] > -0.2 ? 1 : 0));
  const shape = G ? { sdf: G.full, frame } : ballOf(P, post.mesh, frame, omega);
  const info = { frame, light, features: head.features, expressions: Object.fromEntries(head.expressions.map(x => [x.name, x])), skin: head.skin, shape };
  const body = post.withRest({ mesh: { morphs, uv, paintMask, paint: { features: head.features, skin: head.skin }, shading, noShadow: face } });
  body.head = info;
  const cranium = wrap?.form.kind === 'curves' ? { w: 1, h: 1, d: 1.05, ...wrap.form.cranium } : { w: 1, h: 1, d: 1.05 };
  const meshes = [...piecesOf(head.pieces, { form: G, frame, body, sk, skin: head.skin, cranium }), ...reliefsOf(head.features, { body, frame, omega })];
  return { body, meshes };
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
