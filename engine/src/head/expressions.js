// Expressions by the mesh: each a morph of the head's skin (made once on the head as it is, in head units: src/head/
// frame.js) and, if it asks, a turn of the jaw (the Jaw joint, so Anny's own jaw weights open the mouth), with what it
// asks of the painted features (src/head/paint.js: close, happy, smile, open, up, down). Played by a pose layer
// {kind: "expression", name, weight} (src/layers.js) — the painted features follow the skin they are drawn on, and
// redraw as the expression asks. From Г3's blink, open jaw and smile (experiments/heads-wrap) and Г1's brows.
//   mesh effects: lids (the skin over each eye swells, as a lid over a ball), corners (the mouth's corners up, out and
//   back, its middle still), cheeks (they rise and round), brows (the skin over the brows lifts) — each with an amount
import { clamp } from '../math.js';

const num = (min, max) => ({ type: 'number', min, max });
const EFFECT = { type: 'object', required: ['kind'], props: { kind: { type: 'string', enum: ['lids', 'corners', 'cheeks', 'brows'] }, amount: num(-3, 3) } };
export const EXPRESSION_SCHEMA = { type: 'object', required: ['name'], props: {
  name: { type: 'string', pattern: /^[a-z][a-zA-Z0-9]*$/ }, label: { type: 'object', props: { ru: { type: 'string' }, en: { type: 'string' } }, required: ['ru', 'en'] },
  jaw: num(-30, 30), mesh: { type: 'array', items: EFFECT },
  paint: { type: 'object', props: { close: num(0, 1), happy: num(0, 1), smile: num(0, 1), open: num(0, 1), up: num(0, 1), down: num(0, 1) } } } };

// the morph of one expression: {indices, deltas} (metres), on positions P of the head; eye, mouth: where they are
// drawn (head units: the eye's {x, y, w, h, tilt}, the mouth's {y, w, wide})
export function expressionMorph(x, { P, mesh, frame, omega, eye, mouth, brow }) {
  const idx = [], del = [], R = frame.R;
  const hw = mouth ? (mouth.wide ? mouth.w : mouth.w / 2) : 0.1, my = mouth?.y ?? -0.8;
  for (const i of mesh.used) {
    if (omega[i] < 0.5) continue;
    const [lx, ly, lz] = frame.toL(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]); if (lz < 0) continue;
    let dx = 0, dy = 0, dz = 0;
    for (const e of x.mesh || []) {
      const a = e.amount ?? 1;
      if (e.kind === 'lids' && eye && omega[i] > 0.9) for (const s of [-1, 1]) {
        const cx = s * eye.x, u = (lx - cx) / (eye.w / 2), v = ly - eye.y - (eye.tilt || 0) * s * (lx - cx), r = Math.hypot(u, v / eye.h * 2.2);
        dz += a * 0.035 * Math.exp(-r * r * 1.6);
      }
      if (e.kind === 'corners') {
        const up = clamp(0.6 * hw, 0.035, 0.08), ry = Math.max(0.1, hw * 0.5), u = Math.abs(lx) / hw, gx = u < 1 ? u * u : Math.exp(-(((u - 1) * hw / 0.1) ** 2)), f = gx * Math.exp(-(((ly - my) / ry) ** 2));
        dx += a * Math.sign(lx) * 0.18 * hw * f; dy += a * up * f; dz -= a * 0.02 * f;
      }
      if (e.kind === 'cheeks') for (const s of [-1, 1]) { const rk = Math.hypot(lx - s * 0.42, ly - (my + 0.24)) / 0.24, fk = Math.exp(-rk * rk); dy += a * 0.035 * fk; dz += a * 0.025 * fk; }
      if (e.kind === 'brows' && brow) for (const s of [-1, 1]) { const rb = Math.hypot(lx - s * (brow.x0 + brow.x1) / 2, ly - (brow.y0 + brow.y1) / 2 - 0.02) / 0.28; dy += a * 0.05 * Math.exp(-rb * rb); }
    }
    const w = omega[i];
    if (Math.abs(dx) + Math.abs(dy) + Math.abs(dz) < 1e-6) continue;
    idx.push(i); del.push(dx * w * R, dy * w * R, dz * w * R);
  }
  return { indices: Uint32Array.from(idx), deltas: Float32Array.from(del) };
}

// what the expressions playing now (their weights by name) ask of the painted features: each ask the weights' sum,
// rounded to a hundredth (so the picture is drawn again only when it changes)
export function paintState(head, weights) {
  const st = {};
  for (const [name, w] of Object.entries(weights || {})) for (const [k, v] of Object.entries(head.expressions[name]?.paint || {})) st[k] = (st[k] ?? 0) + v * w;
  for (const k of Object.keys(st)) st[k] = Math.round(Math.min(1, Math.max(0, st[k])) * 100) / 100;
  return st;
}
