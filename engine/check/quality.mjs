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
//   node engine/check/quality.mjs [--only skin,bones,feet,order] [--print]   (--print: every measure, not only failures)
import { createEngine } from '../src/engine.js';
import { read } from './node-read.mjs';
import { resolve } from '../src/character.js';
import { turnedOver } from '../src/regions.js';

const E = await createEngine({ read }), sk = E.skeleton;
const argv = process.argv.slice(2), only = argv.includes('--only') ? argv[argv.indexOf('--only') + 1].split(',') : null, PRINT = argv.includes('--print');
const presets = (await E.presets()).presets, chars = (await E.characters()).characters;
const FULL = chars.filter(c => !['woman', 'man', 'girl', 'boy', 'child', 'oldwoman', 'oldman', 'hero', 'elf', 'princess-toddler-head'].includes(c.id)).map(c => c.id);
const BODIES = ['moood-woman', 'moood-child', 'moood-oldman', 'anny-m-heavy', 'anny-T-chibi-baby17'];
const MOMENTS = [['walk', 30], ['run', 20], ['sit', 100], ['jump', 45], ['dance', 60]];
let failed = 0, passed = 0;
const check = (name, value, limit, unit = '') => {
  const ok = value <= limit;
  if (!ok) failed++; else passed++;
  if (!ok || PRINT) console.log(`${ok ? '  ' : '✗ '}${name}: ${value.toFixed(3)}${unit} (limit ${limit}${unit})`);
};
const woman = await E.description('woman');
const on = async (body, o) => E.figure(await E.expand(resolve({ ...structuredClone(woman), body, ...o }, sk)));
const pinOf = id => presets.find(p => p.id === id).pin;
const bodyPin = async id => `${id}@${(await E.body(id)).hash.slice(0, 16)}`;

// the most any edge is stretched: its length in `to` against its length in `from` — or in `also` (another state),
// whichever is longer (a change of the rest that shortened an edge doesn't make its length in motion a tear)
function stretch(mesh, from, to, also = null) {
  const T = mesh.triangles, L = (P, a, b) => Math.hypot(P[a] - P[b], P[a + 1] - P[b + 1], P[a + 2] - P[b + 2]); let worst = 0;
  for (let t = 0; t < T.length; t += 3) for (let e = 0; e < 3; e++) {
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

console.log(failed ? `${failed} of ${passed + failed} contracts broken` : `all ${passed} contracts hold`);
process.exit(failed || !passed ? 1 : 0);
