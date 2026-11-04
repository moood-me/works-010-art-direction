// The engine's quality contracts, checked in node: not whether something changed (numbers.mjs, pictures.mjs) but
// whether it is still sound — each a measure with a limit.
//   skin       no triangle turned over by a change of the rest, against the base body (every preset, on five bodies);
//              no edge stretched more than its limit at the rest against the base body, and in motion no more than the
//              plain body's own skinning stretches it (both against the base body; every full-body preset)
//   bones      pose layers keep every bone's length: turns exactly; a change of the rest as a layer as its rest change
//              makes them, in every frame
//   feet       pose layers keep the feet: a foot planted in the plain walk slides no more with the layer than without
//              it; the lowest point of a standing figure is on the floor
//   order      layers run in the order they are listed (two orders give two figures; a code layer before a change of
//              the rest sets its weight); a change of the rest as a layer at weight 1 is the same change on the rest
//   heads      every character with a head (src/head/): no triangle of the head turned (against its designed form where
//              it is wrapped on one, else against the body it was made from); no vertex standing out of its neighbours
//              (a spike, a crumple); no edge of the head and neck stretched past its limit at the rest, and in motion (seven
//              motions, every skinning method, a body's change on the rest and as a layer, a smile in a motion) no more
//              than the plain body's skinning stretches it, in expressions no more than 2.5×; no crease where the head
//              meets the neck, under the jaw or at the nape; the face's picture not smeared where it shows; the drawn eyes
//              on the skin's eyes and the drawn mouth's parting where the lips part (mm); reliefs not stretched; pieces on
//              the skin in motion and when a layer grows the head
//   hair       every character whose hair moves: at rest it keeps the rest its groom found (sagging from its design no
//              more than 2 cm, leaving it no more than 12 mm in 8 s, no jitter past 1 mm a frame), its roots as deep under
//              the scalp as designed (3 mm); in every motion and chain the engine has, whole, and in a strong wind: no point
//              not a number, every lock's length kept (1 %; ringlets give 35 %), no point faster than 10 m/s, no shimmer
//              more than the head's that carries it and 1 mm (the 99.9th), the hair no deeper in the body than at rest (its
//              surfaces' 1 % deepest: 30 mm; more than 1 cm in: 2.5 % — inside the hair's own mass, looked at), no lock
//              torn (edges past 2×: 2 %), the inner layer hidden where locks part (a
//              quarter at most); walking at 20, 60, 144 frames a second as at 30 (5 mm on the whole, 3 cm at most); long
//              locks leaning in the wind as the presets say (light 12–30°, strong 45–75°) — each limit says why
//   node engine/check/quality.mjs [--only skin,bones,feet,order,heads,hair] [--print]   (--print: every measure, not only failures)
import { createEngine } from '../src/engine.js';
import { read } from './node-read.mjs';
import { resolve } from '../src/character.js';
import { turnedOver } from '../src/regions.js';
import { headShares } from '../src/head/frame.js';
import { formOnBody } from '../src/head/wrap.js';
import { gradOf, projectOn } from '../src/head/shapes.js';
import { cross, clamp } from '../src/math.js';
import { neighboursOf, normalsOf } from '../src/mesh.js';
import { surfaceDistance } from '../src/solids.js';
import { PARTED } from '../src/hair/shade.js';
import { landmarksOf } from '../src/head/face.js';
import { SPAN, CY, mouthLines, grinLines, along } from '../src/head/paint.js';

const E = await createEngine({ read }), sk = E.skeleton;
const argv = process.argv.slice(2), only = argv.includes('--only') ? argv[argv.indexOf('--only') + 1].split(',') : null, PRINT = argv.includes('--print');
const presets = (await E.presets()).presets, chars = (await E.characters()).characters;
const HEADS = [];
for (const c of chars) if ((await E.description(c.id)).head) HEADS.push(c.id);
const FULL = chars.filter(c => !['woman', 'man', 'girl', 'boy', 'child', 'oldwoman', 'oldman', 'hero', 'elf', 'princess-toddler-head'].includes(c.id) && !HEADS.includes(c.id)).map(c => c.id);
const BODIES = ['moood-woman', 'moood-child', 'moood-oldman', 'anny-m-heavy', 'anny-T-chibi-baby17'];
const MOMENTS = [['walk', 30], ['run', 20], ['sit', 100], ['jump', 45], ['dance', 60]];
let failed = 0, passed = 0;
// expressions have no counterpart on the plain body: an edge of the face no more than 2.5× its rest's (a smile draws the
// mouth's corners out and up)
const EXPR_LIMIT = 2.5;
// a head's headwear (src/head/pieces.js)
const WEAR = ['hood', 'hat', 'earDevice'];
const check = (name, value, limit, unit = '') => {
  const ok = value <= limit;
  if (!ok) failed++; else passed++;
  if (!ok || PRINT) console.log(`${ok ? '  ' : '✗ '}${name}: ${value.toFixed(3)}${unit} (limit ${limit}${unit})`);
};
// a measure between two limits
const within = (name, value, lo, hi, unit = '') => {
  const ok = value >= lo && value <= hi;
  if (!ok) failed++; else passed++;
  if (!ok || PRINT) console.log(`${ok ? '  ' : '✗ '}${name}: ${value.toFixed(3)}${unit} (limits ${lo}–${hi}${unit})`);
};
const woman = await E.description('woman');
const on = async (body, o) => E.figure(await E.expand(resolve({ ...structuredClone(woman), body, ...o }, sk)));
const pinOf = id => presets.find(p => p.id === id).pin;
const bodyPin = async id => `${id}@${(await E.body(id)).hash.slice(0, 16)}`;

// the most any edge is stretched: its length in `to` against its length in `from` — or in `also` (another state),
// whichever is longer (a change of the rest that shortened an edge doesn't make its length in motion a tear); only:
// which edges count (by their two vertices)
function stretch(mesh, from, to, also = null, only = null) {
  const T = mesh.triangles, L = (P, a, b) => Math.hypot(P[a] - P[b], P[a + 1] - P[b + 1], P[a + 2] - P[b + 2]); let worst = 0;
  for (let t = 0; t < T.length; t += 3) for (let e = 0; e < 3; e++) {
    if (only && !only(T[t + e], T[t + (e + 1) % 3])) continue;
    const a = T[t + e] * 3, b = T[t + (e + 1) % 3] * 3, l0 = Math.max(L(from, a, b), also ? L(also, a, b) : 0); if (l0 < 1e-5) continue;
    const r = L(to, a, b) / l0; if (r > worst) worst = r;
  }
  return worst;
}

if (!only || only.includes('skin')) {
  // every preset on the rest, on five bodies: nothing turned over (the sign gathers the hands' and feet's skin onto
  // balls and folds it there by its nature — measured by its stretch in motion instead)
  // Some changes pushed past what a body has room for press its skin into itself — a reed's, a V's or a slim torso's
  // narrow hips into a heavy body's or a baby's thighs, thicker limbs into a heavy body, a baby's difference from
  // grown-ups drawn out: there a few triangles turn over where two surfaces meet; their limits say how many
  const PUSHED = { 'silhouette-reed': 10, 'silhouette-v': 6, 'proportions-slim-torso': 10, 'proportions-thick-limbs': 6, 'proportions-short-neck': 15, average: 10, caricature: 40 };
  for (const id of BODIES) {
    const base = await E.body(id), pin = await bodyPin(id), roomy = id.startsWith('moood-');
    for (const p of presets) {
      if (p.group === 'pictogram') continue;
      // (the head's parts are no changes of a body; a wrap is measured against its own form: below, heads)
      const content = await E.preset(p.pin); if (!content.changes || content.changes.some(c => c.kind === 'wrap')) continue;
      const r = await E.restBody(await E.expand(resolve({ ...structuredClone(woman), body: pin, rest: [{ kind: 'preset', id: p.pin, frames: 'keep' }] }, sk)));
      check(`${p.id} on ${id}: triangles turned over`, turnedOver(base.mesh.triangles, base.mesh.positions, r.mesh.positions, base.mesh.isUsed).n, roomy ? 0 : PUSHED[p.id] ?? 0);
    }
  }
  // full-body presets: at the rest, and in motion no more than the plain body (the same base, no changes) stretches in
  // the same moment, with room for a fifth more — every edge against the base body's (or its own rest's, if longer)
  for (const c of FULL) {
    const spec = await E.character(c), base = await E.body(spec.body), rest = await E.restBody(spec);
    const sign = spec.rest.some(r => r.kind === 'sign');
    check(`${c} at rest: edge stretch against its base body`, stretch(base.mesh, base.mesh.positions, rest.mesh.positions), sign ? 10 : 3, '×');   // (a sign gathers a hand onto a ball and draws a foot's sole out: its rest is far from the body's
    const fig = await E.figure(c), plain = await E.figure(resolve({ ...structuredClone(woman), body: spec.body }, sk));
    for (const [m, t] of MOMENTS) {
      const clip = await E.clip(m); fig.frame(clip, t, fig.pose); plain.frame(clip, t, plain.pose);
      const own = stretch(base.mesh, base.mesh.positions, fig.positions, rest.mesh.positions), ref = stretch(base.mesh, base.mesh.positions, plain.positions);
      check(`${c} ${m}${t}: edge stretch in motion against the plain body's`, own / ref, 1.2, '×');
    }
  }
}

// a piece's nearest points to the skin of the head at the rest (within 4 mm; `only`: which of the skin's vertices are
// the head's): how much farther from the skin they are now (mm), against the same at the rest
function pieceGap(piece, skin, body, only) {
  const R = piece.mesh.positions, S = body.mesh.positions, near = [];
  for (const i of piece.mesh.used) { let b = -1, d = Infinity; for (let j = 0; j < body.mesh.N; j += 1) { if (!body.mesh.isUsed[j] || !only(j)) continue; const e = Math.hypot(R[i * 3] - S[j * 3], R[i * 3 + 1] - S[j * 3 + 1], R[i * 3 + 2] - S[j * 3 + 2]); if (e < d) { d = e; b = j; } } if (d < 0.004) near.push([i, b, d]); if (near.length > 40) break; }
  let worst = 0; for (const [i, j, d0] of near) { const p = piece.positions, q = skin.positions; worst = Math.max(worst, Math.hypot(p[i * 3] - q[j * 3], p[i * 3 + 1] - q[j * 3 + 1], p[i * 3 + 2] - q[j * 3 + 2]) - d0); }
  return worst * 1000;
}
// how much farther from (or nearer to) the skin's surface than at rest (mm) a piece's points lie that lie within 4 mm of
// it at rest (plain: the figure at rest; the skin: the head's, `only`)
function surfaceGap(piece, skin, plain, only) {
  const of = (o, P) => { const N = normalsOf(P, o.mesh.triangles, undefined, o.mesh.used), a = [], b = []; for (const i of o.mesh.used) if (only(i)) { a.push(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]); b.push(N[i * 3], N[i * 3 + 1], N[i * 3 + 2]); } return surfaceDistance(Float32Array.from(a), Float32Array.from(b)); };
  const rest = plain.outputs.find(o => o.name === piece.name).positions, s0 = of(plain.outputs[0], plain.outputs[0].positions), s1 = of(skin, skin.positions);
  let worst = 0;
  for (const v of piece.mesh.used) { const a = s0(rest[v * 3], rest[v * 3 + 1], rest[v * 3 + 2]); if (!(Math.abs(a) < 0.004)) continue; const b = s1(piece.positions[v * 3], piece.positions[v * 3 + 1], piece.positions[v * 3 + 2]); worst = Math.max(worst, Number.isFinite(b) ? Math.abs(b - a) : Infinity); }
  return worst * 1000;
}
// the sharpest angle (degrees) between two triangles that share an edge, among triangles `inside(t)`
function sharpest(mesh, P, inside) {
  const T = mesh.triangles, byEdge = new Map(), nrm = t => { const a = T[t] * 3, b = T[t + 1] * 3, c = T[t + 2] * 3, n = cross([P[b] - P[a], P[b + 1] - P[a + 1], P[b + 2] - P[a + 2]], [P[c] - P[a], P[c + 1] - P[a + 1], P[c + 2] - P[a + 2]]), l = Math.hypot(...n) || 1; return n.map(v => v / l); };
  let worst = 0;
  for (let t = 0; t < T.length; t += 3) { if (!inside(t)) continue; for (let e = 0; e < 3; e++) { const a = T[t + e], b = T[t + (e + 1) % 3], k = Math.min(a, b) + ',' + Math.max(a, b); if (byEdge.has(k)) { const n1 = nrm(byEdge.get(k)), n2 = nrm(t); worst = Math.max(worst, Math.acos(Math.max(-1, Math.min(1, n1[0] * n2[0] + n1[1] * n2[1] + n1[2] * n2[2]))) * 180 / Math.PI); } else byEdge.set(k, t); } }
  return worst;
}
// how far (mm) a vertex stands out of its neighbours or sinks into them — along its normal, the umbrella's reach — more
// than the same vertex on `base` does (a spike, a crumple; a designed form's own curves are smooth): the most, over `only`
function bumps(mesh, P, base, only) {
  const nb = neighboursOf(mesh), NA = normalsOf(P, mesh.triangles, undefined, mesh.used), NB = normalsOf(base, mesh.triangles, undefined, mesh.used);
  const reach = (Q, N, i) => { let x = 0, y = 0, z = 0; const a = nb.start[i], b = nb.start[i + 1]; for (let q = a; q < b; q++) { const j = nb.list[q]; x += Q[j * 3]; y += Q[j * 3 + 1]; z += Q[j * 3 + 2]; } const n = b - a; return Math.abs((Q[i * 3] - x / n) * N[i * 3] + (Q[i * 3 + 1] - y / n) * N[i * 3 + 1] + (Q[i * 3 + 2] - z / n) * N[i * 3 + 2]); };
  let worst = 0; for (const i of mesh.used) if (only(i) && nb.start[i + 1] > nb.start[i]) worst = Math.max(worst, reach(P, NA, i) - reach(base, NB, i));
  return worst * 1000;
}
// an attached mesh's (a relief's) edges in a moment against its own at the rest
function reliefStretch(o, rest) { const T = o.mesh.triangles, P = o.positions; let worst = 0; for (let t = 0; t < T.length; t += 3) for (let e = 0; e < 3; e++) { const a = T[t + e] * 3, b = T[t + (e + 1) % 3] * 3, l0 = Math.hypot(rest[a] - rest[b], rest[a + 1] - rest[b + 1], rest[a + 2] - rest[b + 2]); if (l0 > 1e-6) worst = Math.max(worst, Math.hypot(P[a] - P[b], P[a + 1] - P[b + 1], P[a + 2] - P[b + 2]) / l0); } return worst; }

// a figure's bones in a moment
const bones = P => { const out = []; for (let j = 0; j < sk.J; j++) { const p = sk.parent[j]; if (p >= 0) out.push(Math.hypot(P[j * 3] - P[p * 3], P[j * 3 + 1] - P[p * 3 + 1], P[j * 3 + 2] - P[p * 3 + 2])); } return out; };
const LAYERS = [['line-front-s', 'pelvis'], ['line-side-c-forward', 'upright'], ['contrapposto', 'upright'], ['squash', null], ['stretch', null], ['silhouette-hourglass', null], ['silhouette-v', null], ['limbs-taper', null], ['limbs-arcs', null]];
const layer = (id, space) => ({ kind: 'preset', id: pinOf(id), strength: 1, ...(space ? { space } : {}) });

if (!only || only.includes('bones')) {
  const w = await E.body(woman.body);
  for (const [id, space] of LAYERS) {
    const fig = await on(woman.body, { pose: [layer(id, space)] }), ref = await on(woman.body, { rest: [{ kind: 'preset', id: pinOf(id), strength: 1, frames: 'keep' }] });
    const turns = presets.find(p => p.id === id).group.match(/line|contrapposto/);
    const want = bones(turns ? w.rig.joints : ref.rig.joints);
    let worst = 0;
    for (const [m, t] of MOMENTS) { fig.frame(await E.clip(m), t, fig.pose); bones(fig.pose.P).forEach((l, k) => { worst = Math.max(worst, Math.abs(l - want[k])); }); }
    check(`${id} as a layer: a bone's length off ${turns ? 'the body\'s' : 'its rest change\'s'}`, worst * 1000, 0.01, ' mm');
  }
}

if (!only || only.includes('feet')) {
  // the toes' base of each foot in the plain walk: frames where it stays (moves < 4 mm and is low) are its planted ones
  const clip = await E.clip('walk'), toes = ['LeftToeBase', 'RightToeBase'].map(n => sk.index[n]);
  const track = async o => { const f = await on(woman.body, o), out = []; for (let t = 0; t < clip.frames; t++) { f.frame(clip, t, f.pose); out.push(toes.map(j => [f.pose.P[j * 3], f.pose.P[j * 3 + 1], f.pose.P[j * 3 + 2]])); } return out; };
  const base = await track({}), planted = base.map((p, t) => toes.map((_, s) => t > 0 && Math.hypot(p[s][0] - base[t - 1][s][0], p[s][2] - base[t - 1][s][2]) < 0.004 && p[s][1] < 0.06));
  const slide = tr => { let s = 0; for (let t = 1; t < tr.length; t++) for (let k = 0; k < 2; k++) if (planted[t][k]) s += Math.hypot(tr[t][k][0] - tr[t - 1][k][0], tr[t][k][2] - tr[t - 1][k][2]); return s * 1000; };
  const s0 = slide(base);
  for (const [id, space] of LAYERS) {
    const turns = presets.find(p => p.id === id).group.match(/line|contrapposto/);
    // turns keep the feet where they were; a change of the form keeps them as its rest change does (no more than it)
    const ref = turns ? s0 : slide(await track({ rest: [{ kind: 'preset', id: pinOf(id), strength: 1, frames: 'keep' }] }));
    check(`${id} as a layer: planted feet slide in the walk, beyond ${turns ? 'the plain body\'s' : 'its rest change\'s'}`, Math.max(0, slide(await track({ pose: [layer(id, space)] })) - ref), turns ? 1 : 2, ' mm');
  }
  // standing on the floor: the lowest point of every full-body preset in the walk's double support is on the floor
  for (const c of FULL) {
    const f = await E.figure(c); f.frame(clip, 0, f.pose);
    let lo = Infinity; for (const i of f.outputs[0].mesh.used) lo = Math.min(lo, f.positions[i * 3 + 1]);
    check(`${c}: the lowest point standing, off the floor`, Math.abs(lo - f.pose.floor) * 1000, 0.5, ' mm');
  }
}

if (!only || only.includes('order')) {
  // two layers that don't commute, in both orders: the turn amplified, or not; the silhouette of the squashed body, or
  // the squashed silhouette
  const clip = await E.clip('walk'), H = sk.index.LeftHand;
  const pairs = [[{ kind: 'turn', joint: 'LeftForeArm', axis: [0, 0, 1], degrees: 30 }, { kind: 'amplifyLimbs', factor: 1.5, parts: ['foreArm'] }],
    [{ kind: 'preset', id: pinOf('squash'), strength: 1 }, { kind: 'preset', id: pinOf('silhouette-v'), strength: 1 }]];
  for (const [x, y] of pairs) {
    const f1 = await on(woman.body, { pose: [x, y] }), f2 = await on(woman.body, { pose: [y, x] });
    f1.frame(clip, 30, f1.pose); f2.frame(clip, 30, f2.pose);
    let d = 0; for (const i of f1.outputs[0].mesh.used) d = Math.max(d, Math.hypot(...[0, 1, 2].map(c => f1.positions[i * 3 + c] - f2.positions[i * 3 + c])));
    check(`${x.kind} and ${y.kind} in both orders: the same figure (the order lost) — closer than 1 mm counts as one`, d * 1000 < 1 ? 1 : 0, 0);
  }
  // a change of the rest as a layer at weight 1 is the same change on the rest (frames kept); its weight a code layer sets
  for (const id of ['squash', 'silhouette-v', 'smooth-4cm', 'proportions-big-head']) {
    const lay = await on(woman.body, { pose: [{ kind: 'preset', id: pinOf(id), strength: 1 }] }), rest = await on(woman.body, { rest: [{ kind: 'preset', id: pinOf(id), strength: 1, frames: 'keep' }] });
    lay.frame(clip, 30, lay.pose); rest.frame(clip, 30, rest.pose);
    let w = 0; for (const i of lay.outputs[0].mesh.used) w = Math.max(w, Math.hypot(...[0, 1, 2].map(c => lay.positions[i * 3 + c] - rest.positions[i * 3 + c])));
    check(`${id}: as a layer against the same on the rest`, w * 1000, 0.5, ' mm');
  }
  const spec = await E.expand(resolve({ ...structuredClone(woman), pose: [{ kind: 'preset', id: pinOf('squash'), strength: 1 }] }, sk));
  const zero = await E.figure(spec, { layers: [] }), plain = await E.figure('woman');
  zero.layers.unshift({ kind: 'code', apply: (pose, ctx) => { ctx.weights[zero.restLayers[0].name] = 0; } });
  zero.frame(clip, 30, zero.pose); plain.frame(clip, 30, plain.pose);
  let w = 0; for (const i of plain.outputs[0].mesh.used) w = Math.max(w, Math.hypot(...[0, 1, 2].map(c => zero.positions[i * 3 + c] - plain.positions[i * 3 + c])));
  check('a change of the rest as a layer weighed 0 by a code layer before it: off the plain body', w * 1000, 0.5, ' mm');
}

if (!only || only.includes('heads')) {
  // the plain body's own limits where a head has a counterpart: in motion no more stretched than the plain body (×1.2,
  // as the full-body presets), at the rest no more than 3× (as they); what has no counterpart says why its limit is what
  // it is, beside it
  const HM = [['walk', 30], ['run', 20], ['look-around', 60], ['dance', 60], ['sit', 100], ['jump', 45], ['bow', 45]], EXPR = ['blink', 'open', 'smile', 'browsUp'];
  for (const c of HEADS) {
    const spec = await E.character(c), base = await E.body(spec.body), { body } = await E.headBody(spec), mesh = body.mesh, P = mesh.positions, T = mesh.triangles;
    const { omega, jaw } = headShares(mesh, sk), F = body.head.frame, wrap = spec.head.wrap;
    const G = wrap ? formOnBody(wrap.form, await E.restBody({ ...spec, rest: spec.rest.slice(0, spec.head.wrapAt) }), wrap.neckSlim) : null;
    const at = i => F.toL(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]), ofHead = i => omega[i] > 0.5;
    // the mouth's inside: where the skin is drawn as the mouth (between a drawn mouth's lips, in a grin's crescent) — there
    // the lips' parting is held where the mouth is drawn, and what folds round it is the mouth's opening, drawn dark
    const pic = i => [(mesh.uv[i * 2] - 0.5) * 2 * SPAN, (mesh.uv[i * 2 + 1] - 0.5) * 2 * SPAN + CY], drawnMouth = body.head.features.find(f => f.kind === 'mouth' && f.type !== 'none');
    const lips = drawnMouth && (drawnMouth.type === 'grin' ? (({ top, bot }) => [top, bot])(grinLines(drawnMouth)) : (({ upper, lower }) => [upper, lower])(mouthLines(drawnMouth)));
    const inMouth = i => { if (!lips) return false; const [x, y] = pic(i); const m = 0.02; return x > lips[0][0][0] - m && x < lips[0][lips[0].length - 1][0] + m && y < along(lips[0], x) + m && y > along(lips[1], x) - m; };   // (and its outline's width round it)
    // (under a nose set on as its own piece the skin is hidden: what it does there inside the piece doesn't count)
    const hidden = i => G?.piece && G.nose(...at(i)) < 0.05;
    const inHead = t => Math.min(omega[T[t]], omega[T[t + 1]], omega[T[t + 2]]) > 0.9;
    // turned triangles: on a wrapped head, against its designed form right after the wrap, and against that head for
    // whatever changes it after; on Anny's own, against the body it came from
    const drawn = G ? (await E.restBody({ ...spec, rest: spec.rest.slice(0, spec.head.wrapAt + 1) })).mesh.positions : null;
    let turned = 0;
    if (G) {
      const g = [0, 0, 0], D = drawn;
      for (let t = 0; t < T.length; t += 3) {
        if (!inHead(t)) continue; const a = T[t] * 3, b = T[t + 1] * 3, d = T[t + 2] * 3;
        const n = cross([D[b] - D[a], D[b + 1] - D[a + 1], D[b + 2] - D[a + 2]], [D[d] - D[a], D[d + 1] - D[a + 1], D[d + 2] - D[a + 2]]), l = F.toL((D[a] + D[b] + D[d]) / 3, (D[a + 1] + D[b + 1] + D[d + 1]) / 3, (D[a + 2] + D[b + 2] + D[d + 2]) / 3);
        gradOf(G.sdf, ...l, 0.004, g);
        if (n[0] * g[0] + n[1] * g[1] + n[2] * g[2] < 0 && !hidden(T[t]) && !(inMouth(T[t]) && inMouth(T[t + 1]) && inMouth(T[t + 2]))) turned++;
      }
      turned += turnedOver(T, drawn, P, mesh.isUsed).n;
    } else turned = turnedOver(T, base.mesh.positions, P, mesh.isUsed).n;
    check(`${c}: head triangles turned${G ? ' against its designed form' : ''}`, turned, 0);
    // at the rest: no vertex standing out of its neighbours (a spike, a crumple) — the face, the jaw and under it, the
    // join; against the body it came from, or on a wrapped head against the skin laid exactly on its form (the form's
    // own creases — a jowl over the neck — are the design)
    const smooth = G ? Float32Array.from(P) : base.mesh.positions;
    if (G) for (const i of mesh.used) if (omega[i] > 0.9) smooth.set(F.toW(...projectOn(G.sdf, at(i), 4)), i * 3);
    check(`${c}: a vertex of the head standing out of its neighbours or sunk into them, beyond ${G ? 'its form' : 'its base body'}`, bumps(mesh, P, smooth, i => omega[i] > 0.05 && !hidden(i) && !inMouth(i)), 1.5, ' mm');
    const headMesh = { triangles: Uint32Array.from([...Array(T.length / 3).keys()].filter(k => Math.max(omega[T[k * 3]], omega[T[k * 3 + 1]], omega[T[k * 3 + 2]]) > 0.05).flatMap(k => [T[k * 3], T[k * 3 + 1], T[k * 3 + 2]])) };
    // (a wrap draws Anny's head out onto another form — a long nose, a big cranium, an eye's place: its edges at the rest
    // are the design, not wear; Anny's own changes open moood's closed eye's sub-millimetre edges: see the README)
    check(`${c} at rest: head edge stretch against its base body`, stretch(headMesh, base.mesh.positions, P), G ? 8 : 5, '×');
    // in motion, with every skinning method, as a body's change of the form goes on the rest and as a layer, an expression
    // in a motion: no more stretched than the plain body is there (against the base, or the head's own rest if longer)
    const plainOf = o => E.figure(resolve({ ...structuredClone(woman), body: spec.body, ...o }, sk));
    const moments = [...HM.map(([m, t]) => [m, t, {}, {}]), ['look-around', 60, { skinning: { method: 'dqs' } }, { skinning: { method: 'dqs' } }], ['look-around', 60, { skinning: { method: 'lbs' } }, { skinning: { method: 'lbs' } }],
      ['walk', 30, { pose: [layer('squash', null)] }, { pose: [layer('squash', null)] }], ['walk', 30, { rest: [{ kind: 'preset', id: pinOf('silhouette-hourglass'), strength: 1, frames: 'keep' }] }, { rest: [{ kind: 'preset', id: pinOf('silhouette-hourglass'), strength: 1, frames: 'keep' }] }],
      ['look-around', 60, { pose: [{ kind: 'expression', name: 'smile', weight: 1 }] }, {}]];
    for (const [m, t, own, plainO] of moments) {
      // (a head with no expressions — Anny's own, wearing only hair — has no smile to try)
      if (own.pose?.[0].kind === 'expression' && !spec.head.expressions.some(x => x.name === own.pose[0].name)) continue;
      const figSpec = await E.expand(await E.resolve({ ...structuredClone(await E.description(c)), ...own, ...(own.pose && spec.pose.length ? { pose: [...spec.pose, ...own.pose] } : {}) }));
      const fig = await E.figure(figSpec), plain = await plainOf(plainO), clip = await E.clip(m);
      fig.frame(clip, t, fig.pose); plain.frame(clip, t, plain.pose);
      // (each against the base body or its own rest, if longer: a change of the rest that shortened an edge doesn't
      // make its length in motion a tear)
      const figRest = (await E.headBody(figSpec)).body.mesh.positions, plainRest = plain.body.mesh.positions;
      const what = `${m}${t}${own.skinning ? ' ' + own.skinning.method : ''}${own.rest ? ' on an hourglass' : ''}${own.pose ? ' with ' + (own.pose[0].kind === 'expression' ? 'a smile' : 'squash as a layer') : ''}`;
      const lim = own.pose?.[0].kind === 'expression' ? EXPR_LIMIT : 1.2;
      check(`${c} ${what}: head edge stretch in motion against the plain body's`, stretch(headMesh, base.mesh.positions, fig.positions, figRest) / stretch(headMesh, base.mesh.positions, plain.positions, plainRest), lim, '×');
      const nose = fig.outputs.find(o => o.name === 'nose');
      if (nose) check(`${c} ${what}: the nose piece off the skin, beyond its rest`, pieceGap(nose, fig.outputs[0], body, ofHead), 2, ' mm');
      // a relief no more stretched than the plain body is there (a smile's against its limit)
      for (const o of fig.outputs.filter(o => o.mesh.kind === 'attached')) { const r = await E.figure(own.rest ? figSpec : spec); r.frame(null, 0, r.pose); check(`${c} ${what}: the relief ${o.name} stretched against its rest, against the plain body's`, reliefStretch(o, r.outputs.find(x => x.name === o.name).positions) / stretch(headMesh, base.mesh.positions, plain.positions, plainRest), lim, '×'); }
    }
    // pieces follow the head's form as a pose layer (a bigger head: the hair grows with it)
    if (body.head && spec.head.pieces.length) {
      const big = await E.figure(await E.expand(await E.resolve({ ...structuredClone(await E.description(c)), pose: [layer('proportions-big-head', null)] }))); big.frame(null, 0, big.pose);
      // (headwear is left to the clothes stage, where it becomes a garment)
      // (carried as one by the change of the skin under it, a piece can't follow the head's own unevenness: a bigger head
      // grows its cranium more than its face; a hairstyle is fitted onto the grown head — it grows with the cranium and
      // slides over the skin as it grows, so it is measured off the skin's surface, not off the skin's points under it)
      const plain = await E.figure(c); plain.frame(null, 0, plain.pose);
      for (const o of big.outputs.filter(o => o.mesh.piece && !WEAR.includes(o.name))) check(`${c}: its ${o.name} on the head grown by a layer, off the skin beyond its rest`, o.mesh.grows ? surfaceGap(o, big.outputs[0], plain, ofHead) : pieceGap(o, big.outputs[0], body, ofHead), 5, ' mm');
    }
    // in the expressions: no edge stretched more than 2.5× (an open jaw: the lips between what the jaw carries and what it
    // doesn't — Anny's mouth is closed skin, there it opens)
    const firm = (a, b) => (jaw[a] < 0.05 && jaw[b] < 0.05) || (jaw[a] > 0.95 && jaw[b] > 0.95);
    for (const x of EXPR.filter(x => body.head.expressions[x])) {
      const f = await E.figure({ ...spec, pose: [{ kind: 'expression', name: x, weight: 1 }] }); f.frame(null, 0, f.pose);
      const jawed = !!body.head.expressions[x].jaw;
      check(`${c} ${x}: head edge stretch in the expression${jawed ? ' (but the lips that open)' : ''}`, stretch(headMesh, P, f.positions, null, jawed ? firm : null), EXPR_LIMIT, '×');
      // (a relief of the lips in an open mouth: as the lips' skin, it opens)
      if (!jawed) for (const o of f.outputs.filter(o => o.mesh.kind === 'attached')) { const r = await E.figure(spec); r.frame(null, 0, r.pose); check(`${c} ${x}: the relief ${o.name} stretched against its rest`, reliefStretch(o, r.outputs.find(y => y.name === o.name).positions), EXPR_LIMIT, '×'); }
    }
    // no crease where the head meets the neck, under the jaw and at the nape: the sharpest angle between neighbouring
    // triangles of the head's lower part and its join, beyond the body it came from's — or, on a wrapped head, beyond
    // the skin laid exactly on its form (a fold of the form itself, a jowl over the neck, is the design)
    const low = t => { const w = [omega[T[t]], omega[T[t + 1]], omega[T[t + 2]]]; return Math.max(...w) > 0.05 && (Math.min(...w) < 0.97 || at(T[t])[1] < (G?.chin ?? -1.1) + 0.35) && !hidden(T[t]) && !inMouth(T[t]); };
    check(`${c}: the sharpest fold where the head meets the neck, under the jaw and at the nape, beyond ${G ? 'its form' : 'its base body'}'s`, Math.max(0, sharpest(mesh, P, low) - sharpest(mesh, smooth, low)), 25, '°');
    // the face's picture: shown only where it isn't smeared — a triangle showing it (at least half) is no more than 5×
    // longer on the skin than in the picture (round the sides of the head a front projection would smear it along the
    // skin; Anny's eye changes open moood's closed eye slit, its sub-millimetre edges ~4.5×: 5)
    let smear = 0;
    for (let t = 0; t < T.length; t += 3) {
      const v = [T[t], T[t + 1], T[t + 2]]; if (Math.min(...v.map(i => mesh.paintMask[i])) < 0.5 || v.some(hidden)) continue;
      for (let e = 0; e < 3; e++) { const a = v[e], b = v[(e + 1) % 3], w = Math.hypot(...[0, 1, 2].map(k => P[a * 3 + k] - P[b * 3 + k])) / F.R, u = Math.hypot(mesh.uv[a * 2] - mesh.uv[b * 2], mesh.uv[a * 2 + 1] - mesh.uv[b * 2 + 1]) * 2 * SPAN; if (w > 1e-4) smear = Math.max(smear, w / Math.max(u, 1e-9)); }
    }
    check(`${c}: the face's picture smeared over the skin where it shows`, smear, 5, '×');
    // the drawing on the mesh's own features: the eyes' middles where Anny's eyes are (where the wrap put them), the mouth's
    // parting where the lips part (mm, in the picture)
    const L = landmarksOf(body), mm = d => d * F.R * 1000;
    const eye = body.head.features.find(f => f.kind === 'eye');
    if (eye) for (const [s, n] of [[1, 'eyeL'], [-1, 'eyeR']]) { const p = pic(L[n]); check(`${c}: the drawn ${n === 'eyeL' ? 'left' : 'right'} eye's middle off the skin's eye`, mm(Math.hypot(p[0] - s * eye.x, p[1] - eye.y)), 3, ' mm'); }
    const mouth = body.head.features.find(f => f.kind === 'mouth' && f.type !== 'none');
    if (mouth) {
      const line = mouth.type === 'grin' ? null : mouthLines(mouth).line, g = mouth.type === 'grin' ? grinLines(mouth) : null; let off = 0;
      for (let t = 0; t < T.length; t += 3) {
        const v = [T[t], T[t + 1], T[t + 2]]; if (Math.max(...v.map(i => jaw[i])) - Math.min(...v.map(i => jaw[i])) < 0.5 || v.some(i => omega[i] < 0.9)) continue;
        for (const i of v) {
          if (jaw[i] >= 0.5) continue; const [x, y] = pic(i), half = mouth.type === 'grin' ? mouth.w : mouth.w / 2; if (Math.abs(x) > 0.8 * half || Math.abs(y - mouth.y) > half) continue;
          // a drawn mouth: its parting line; a grin: anywhere inside its crescent
          off = Math.max(off, line ? Math.abs(y - along(line, x)) : Math.max(0, y - along(g.top, x), along(g.bot, x) - y));
        }
      }
      check(`${c}: the lips' parting off the drawn mouth's`, mm(off), 3, ' mm');
    }
  }
}

// ———— hair (src/hair/): every character whose hair moves, in every motion the engine has (whole), and in the wind ————
// The limits say what looks right, not what the hair measures now (each says why).
if (!only || only.includes('hair')) {
  const HAIR = [];
  for (const c of chars) { const f = await E.figure(c.id); if (f.simulations.length) HAIR.push(c.id); }
  const index = await E.motions(), CLIPS = [...index.motions.filter(m => !m.after).map(m => m.id), ...index.chains.map(c => c.id)];
  const wind = async id => (await E.preset(pinOf(id))).wind, strong = await wind('wind-strong'), light = await wind('wind-light');
  const at = { n: [0, 0, 0], v: [0, 0, 0] }, l = [0, 0, 0];
  // how deep a point lies in the body's solids at a moment (0 outside): the head's shape, the skin (deep inside too)
  const depth = (S, m, x, y, z) => { let d = S.skin(m, x, y, z, at); if (S.head) d = Math.min(d, S.head.distance(S.head.local(m, [x, y, z], l))); return Math.max(0, -d); };
  // the hair's surfaces (every 7th vertex), how much deeper in the body than at rest — the most over a share of them
  const surfaces = sim => sim.outputs.flatMap(o => Array.from(o.mesh.used).filter((_, k) => k % 7 === 0).map(v => [o, v]));
  // (hair the body lies on — within PRESSED of the floor — has no room between them, and isn't seen: not counted)
  const PRESSED = 0.025;
  const deepest = (sim, pts, rest) => { const S = sim.solids, m = S.moment(1), out = []; pts.forEach(([o, v], k) => { if (o.positions[v * 3 + 1] > PRESSED) out.push(depth(S, m, o.positions[v * 3], o.positions[v * 3 + 1], o.positions[v * 3 + 2]) - rest[k]); }); out.sort((a, b) => b - a); return out; };
  // each lock's drawn edges stretched past 2× (a share of them): a lock torn into a wedge
  const torn = sim => { let n = 0, bad = 0; for (const o of sim.outputs) { if (o.mesh.hair?.layer !== 'locks') continue; const T = o.mesh.triangles, P = o.positions, R = o.mesh.positions; for (let t = 0; t < T.length; t += 9) for (let e = 0; e < 3; e++) { const a = T[t + e] * 3, b = T[t + (e + 1) % 3] * 3, l0 = Math.hypot(R[a] - R[b], R[a + 1] - R[b + 1], R[a + 2] - R[b + 2]); if (l0 < 5e-4 || (P[a + 1] < PRESSED && P[b + 1] < PRESSED)) continue; n++; if (Math.hypot(P[a] - P[b], P[a + 1] - P[b + 1], P[a + 2] - P[b + 2]) > 2 * l0) bad++; } } return n ? bad / n : 0; };
  // the inner layer hidden where it parts (src/hair/shade.js PARTED): a share of its points
  const parted = sim => { let n = 0, hid = 0; for (const o of sim.outputs) if (o.parted) for (const v of o.mesh.used) { n++; if (o.parted[v] > PARTED) hid++; } return n ? hid / n : 0; };
  // the free points as drawn, and where the head carries their rest (what the head itself does there)
  const drawn = (sim, out, carried) => { const o = [0, 0, 0], m = sim.solids.moment(1); out.set(sim.D); for (const c of sim.chains) if (!c.head) for (let k = 2; k < c.n; k++) { const i = (c.at + k) * 3; sim.carry(m, sim.R0[i], sim.R0[i + 1], sim.R0[i + 2], o); carried[i] = o[0]; carried[i + 1] = o[1]; carried[i + 2] = o[2]; } };
  // a shimmer at a point: its motion turning back and forth two frames running (its second differences, three in a row,
  // each against the last), as much as the least of them — a quarter of it (a point shimmering by ε a frame gives ε; a
  // swing, an impact, a turn, nothing)
  const shimmer = (A, i) => { const a = [0, 1, 2], d = (s, c) => A[s][i + c] - 2 * A[s + 1][i + c] + A[s + 2][i + c], u = a.map(c => d(0, c)), v = a.map(c => d(1, c)), w = a.map(c => d(2, c)), dot = (p, q) => p[0] * q[0] + p[1] * q[1] + p[2] * q[2]; return dot(u, v) < 0 && dot(v, w) < 0 ? Math.min(Math.hypot(...u), Math.hypot(...v), Math.hypot(...w)) / 4 : 0; };
  for (const id of HAIR) {
    const fig = await E.figure(id), sim = fig.simulations[0], S = sim.solids;
    const free = sim.chains.filter(c => !c.head).flatMap(c => Array.from({ length: c.n - 2 }, (_, k) => (c.at + k + 2) * 3));
    // at rest: the rest kept (it hangs where its groom found it, and stays), no jitter
    fig.step(null, 0); const R = Float64Array.from(sim.x), pts = surfaces(sim), m0 = S.moment(1), rest = pts.map(([o, v]) => depth(S, m0, o.positions[v * 3], o.positions[v * 3 + 1], o.positions[v * 3 + 2]));
    let prev = null, jitter = 0;
    for (let t = 1; t <= 240; t++) { fig.step(null, t); if (t > 120) { for (let i = 0; i < sim.x.length; i += 3) jitter = Math.max(jitter, Math.hypot(sim.x[i] - prev[i], sim.x[i + 1] - prev[i + 1], sim.x[i + 2] - prev[i + 2])); } prev = Float64Array.from(sim.x); }
    let kept = 0; for (let i = 0; i < R.length; i += 3) kept = Math.max(kept, Math.hypot(sim.x[i] - R[i], sim.x[i + 1] - R[i + 1], sim.x[i + 2] - R[i + 2]));
    // (2 cm: a hairstyle that hangs lower than drawn is another hairstyle; 12 mm in 8 s and 1 mm a frame: hair standing
    // still that creeps or shimmers is seen at once)
    check(`${id}: hanging at rest, it sags from its design`, sim.rested.sag * 1000, 20, ' mm');
    check(`${id}: standing still 8 s, it leaves its rest`, kept * 1000, 12, ' mm');
    check(`${id}: standing still, it moves in a frame (jitter)`, jitter * 1000, 1, ' mm');
    // roots: each root as deep under the head's surface (its form, else its skin) as its design has it under the designed
    // head, grown with the head (3 mm: under the scalp mass, thicker than that, it doesn't show)
    let root = 0, roots = 0; const mr = S.rest.moment(0);
    for (const c of sim.chains) if (c.rooted && c.depth !== null) { const i = c.at * 3, d = S.head ? S.head.distance(S.head.local(mr, [sim.X0[i], sim.X0[i + 1], sim.X0[i + 2]], l)) : S.skin(mr, sim.X0[i], sim.X0[i + 1], sim.X0[i + 2], at); root = Math.max(root, Math.abs(d - c.depth)); roots++; }
    if (roots) check(`${id}: a root off its designed depth under the scalp`, root * 1000, 3, ' mm');
    for (const [clip, w] of [...CLIPS.map(c => [c, null]), ['idle', strong]]) {
      const C = await E.clip(clip); sim.wind = w; fig.reset();
      let len = 0, speed = 0, bad = 0, deep = 0, share = 0, tear = 0, hide = 0, flick = [], shook = [];
      const h = [0, 1, 2, 3, 4].map(() => new Float64Array(sim.x.length)), g = [0, 1, 2, 3, 4].map(() => new Float64Array(sim.x.length));
      for (let t = 0; t < C.frames; t++) {
        fig.step(C, t);
        for (const c of sim.chains) if (!c.head) for (let k = 0; k < c.n - 1; k++) { const i = (c.at + k) * 3, d = Math.hypot(sim.x[i + 3] - sim.x[i], sim.x[i + 4] - sim.x[i + 1], sim.x[i + 5] - sim.x[i + 2]); len = Math.max(len, Math.abs(d / c.L[k] - 1) - (c.stretch ? 0.35 : 0)); }
        for (let i = 0; i < sim.v.length; i++) { if (!Number.isFinite(sim.x[i])) bad++; }
        for (let i = 0; i < sim.v.length; i += 3) speed = Math.max(speed, Math.hypot(sim.v[i], sim.v[i + 1], sim.v[i + 2]));
        // the hair's shimmer, and its head's: where the head carries the hair's rest (Kimodo's run shakes the head so,
        // 7 mm at the hair's tips)
        h.push(h.shift()); g.push(g.shift()); drawn(sim, h[4], g[4]);
        if (t >= 4) for (const i of free) if (h.every(A => A[i + 1] > PRESSED)) { flick.push(shimmer(h, i)); shook.push(shimmer(g, i)); }
        if (t % 6 === 0) { const d = deepest(sim, pts, rest); deep = Math.max(deep, d[Math.floor(d.length * 0.01)]); share = Math.max(share, d.filter(x => x > 0.01).length / d.length); tear = Math.max(tear, torn(sim)); hide = Math.max(hide, parted(sim)); }
      }
      flick.sort((a, b) => a - b); shook.sort((a, b) => a - b);
      const what = `${id} in ${clip}${w ? ' in a strong wind' : ''}`;
      check(`${what}: points not numbers`, bad, 0);
      check(`${what}: a lock's segment longer or shorter (share)`, len, 0.01);
      // (10 m/s: hair is whipped by a head that turns and a body that runs at most so fast; faster, it has flown off)
      check(`${what}: the fastest point (m/s)`, speed, 10);
      // (the hair shimmers no more than the head that carries it does there, and a millimetre — a pixel at the size a
      // figure is shown — more; the 99.9th of every point in every frame)
      // (in a strong wind the tips flutter: that is the wind's)
      if (!w) check(`${what}: the hair shimmers beyond its head (the 99.9th's, against the head's)`, (flick[Math.floor(flick.length * 0.999)] - shook[Math.floor(shook.length * 0.999)]) * 1000, 1, ' mm');
      // (looked at where it is worst — Ariel face down at the end of lying → rolling over, 29 mm and 2.1 %; Г3 rolling
      // sideways, 2.1 %; Ariel waving, 1.1 %; Alva sneaking, 0.7 % — what of the hair's surfaces is in the body there lies
      // inside the hair's own mass: the far side of a wide mass hanging over an arm, hair pressed under a face on the floor;
      // nothing is seen through the skin. Past these it is not known to stay hidden)
      check(`${what}: the hair through the body, deeper than at rest (the 1% deepest)`, deep * 1000, 30, ' mm');
      check(`${what}: the share of the hair more than 1 cm in the body`, share * 100, 2.5, ' %');
      // (a lock's edge drawn out past twice its length: looked at where it is most — Alva rolling sideways, 1.5 %; Ariel's
      // forward roll, 1.4 %: crumpled locks, folds, no wedge torn out of a lock; Alva bowing, 0.7 %: nothing seen)
      check(`${what}: a lock torn (its edges past 2×, share)`, tear * 100, 2, ' %');
      // (the inner layer hidden where locks part: where most of it is hidden the hair has fallen apart — a quarter at most)
      check(`${what}: the inner layer hidden where locks part (share)`, hide * 100, 25, ' %');
    }
    sim.wind = null;
    // the same at any frame rate: walking 2 s at 20, 60 and 144 frames a second against 30 (5 mm on the whole and 3 cm
    // at most: a lock's swing a little earlier or later, not another motion)
    const walk = await E.clip('walk'), at30 = (fps => { fig.reset(); const st = 30 / fps, n = Math.round(60 / st); for (let k = 0; k <= n; k++) fig.step(walk, k * st); return Float64Array.from(sim.D); });
    const ref = at30(30);
    for (const fps of [20, 60, 144]) {
      const x = at30(fps); let most = 0, sum = 0; for (const i of free) { const d = Math.hypot(x[i] - ref[i], x[i + 1] - ref[i + 1], x[i + 2] - ref[i + 2]); most = Math.max(most, d); sum += d; }
      check(`${id}: walking 2 s at ${fps} frames a second against 30, the hair apart (mean)`, sum / free.length * 1000, 5, ' mm');
      check(`${id}: walking 2 s at ${fps} frames a second against 30, the hair apart (most)`, most * 1000, 30, ' mm');
    }
    // the wind: long locks (root to tip more than 30 cm: a bob's are stiff, short hair holds its shape) lean from where
    // they hang still as the presets say — some 20° in a light wind, some 60° in a strong one (12–30°, 45–75°)
    const long = sim.chains.filter(c => !c.head && c.L.reduce((a, b) => a + b, 0) > 0.3);
    if (long.length >= 3) {
      const dirs = () => long.map(c => { const r = c.at * 3, t = (c.at + c.n - 1) * 3, v = [0, 1, 2].map(k => sim.x[t + k] - sim.x[r + k]), q = Math.hypot(...v); return v.map(x => x / q); });
      const leanIn = w => { sim.wind = w; fig.reset(); for (let t = 0; t < 150; t++) fig.step(null, t); const out = []; for (let t = 150; t < 180; t++) { fig.step(null, t); out.push(dirs()); } return out; };
      const still = leanIn(null)[0], lean = w => { const D = leanIn(w); let s = 0, n = 0; for (const f of D) f.forEach((v, k) => { s += Math.acos(clamp(v[0] * still[k][0] + v[1] * still[k][1] + v[2] * still[k][2], -1, 1)) * 180 / Math.PI; n++; }); return s / n; };
      const a = lean(light), b = lean(strong); sim.wind = null;
      within(`${id}: a light wind leans its long locks`, a, 12, 30, '°'); within(`${id}: a strong wind leans its long locks`, b, 45, 75, '°');
    }
  }
}

console.log(failed ? `${failed} of ${passed + failed} contracts broken` : `all ${passed} contracts hold`);
process.exit(failed || !passed ? 1 : 0);
