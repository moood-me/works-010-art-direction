// Measures a scene frame by frame: where each contact's palm is against its point (Kimodo alone, and with the
// correction on top), and whether one body goes into the other (each vertex of one against the other's nearest skin
// and its normal).  node tools/measure.mjs <scene id> [step]   → prints a summary and writes pics/<scene>-measure.json
import { writeFileSync } from 'node:fs';
import { createEngine } from '../../../../engine/src/engine.js';
import { read } from '../../../../engine/check/node-read.mjs';
import { loadScene, jointAt, palmRest } from '../../scene.js';
import { SCENES } from '../../touch-scenes.js';

const [id, stepArg] = process.argv.slice(2), step = +(stepArg || 1);
const def = SCENES.find(s => s.id === id);
const E = await createEngine({ read });
const S = await loadScene(E, new URL('../../', import.meta.url), def, read);

// the skin of `o` in a grid, to find the nearest vertex fast
function grid(pos, cell = 0.06) {
  const m = new Map(), key = (x, y, z) => `${Math.floor(x / cell)},${Math.floor(y / cell)},${Math.floor(z / cell)}`;
  for (let i = 0; i < pos.length / 3; i++) { const k = key(pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]); (m.get(k) || m.set(k, []).get(k)).push(i); }
  return { near(x, y, z) {
    let best = -1, bd = Infinity; const cx = Math.floor(x / cell), cy = Math.floor(y / cell), cz = Math.floor(z / cell);
    for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) for (const i of m.get(`${cx + a},${cy + b},${cz + c}`) || []) {
      const d = (pos[i * 3] - x) ** 2 + (pos[i * 3 + 1] - y) ** 2 + (pos[i * 3 + 2] - z) ** 2; if (d < bd) { bd = d; best = i; }
    }
    return [best, Math.sqrt(bd)];
  } };
}
// how deep the vertices of p go into q: the most, and how many vertices are more than 5 mm in
function inside(p, q, used) {
  const g = grid(q.fig.positions), P = p.fig.positions, Q = q.fig.positions, N = q.fig.normals;
  let deepest = 0, count = 0;
  for (let i = 0; i < P.length / 3; i += 2) {
    if (!used[i]) continue;
    const [j, d] = g.near(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]); if (j < 0 || d > 0.06) continue;
    const s = (P[i * 3] - Q[j * 3]) * N[j * 3] + (P[i * 3 + 1] - Q[j * 3 + 1]) * N[j * 3 + 1] + (P[i * 3 + 2] - Q[j * 3 + 2]) * N[j * 3 + 2];
    if (s < -0.005) { count++; deepest = Math.max(deepest, -s); }
  }
  return { deepest, count };
}
const usedOf = b => { const u = new Uint8Array(b.N); for (const i of b.triangles) u[i] = 1; return u; };
const used = Object.fromEntries(S.people.map(p => [p.id, usedOf(p.body)]));

const rows = [];
for (let T = 0; T < S.frames; T += step) {
  const row = { T };
  for (const corr of [false, true]) {
    S.corrections = corr; S.misses = {}; S.at(T);
    for (const [ci, c] of (def.contacts || []).entries()) {
      const P = S.by[c.who], O = S.by[c.on];
      if (T < c.from || T > c.to) continue;
      const target = jointAt(O.fig.pose, O.body, O.body.skeleton.index[c.joint], c.point);
      const palm = jointAt(P.fig.pose, P.body, P.body.skeleton.index[c.side + 'Hand'], palmRest(P.body, c.side).point);
      row[(corr ? 'with' : 'kimodo') + ':' + c.who + c.side + ci] = +(Math.hypot(...palm.map((v, i) => v - target[i])) * 100).toFixed(2);
    }
    if (corr) {
      const [a, b] = S.people;
      const ab = inside(a, b, used[a.id]), ba = inside(b, a, used[b.id]);
      row.inside = +(Math.max(ab.deepest, ba.deepest) * 100).toFixed(2); row.insideCount = ab.count + ba.count;
    }
  }
  rows.push(row);
}
writeFileSync(new URL(`../../pics/${id}-measure.json`, import.meta.url), JSON.stringify(rows));
const pick = k => rows.filter(r => r[k] != null).map(r => r[k]);
for (const [ci, c] of (def.contacts || []).entries()) {
  const k = pick('kimodo:' + c.who + c.side + ci), w = pick('with:' + c.who + c.side + ci);
  const stat = a => a.length ? `mean ${(a.reduce((x, y) => x + y, 0) / a.length).toFixed(1)} cm, max ${Math.max(...a).toFixed(1)} cm` : '—';
  console.log(`${c.who}'s ${c.side.toLowerCase()} palm on ${c.on}'s ${c.joint}, frames ${c.from}–${c.to}: Kimodo alone ${stat(k)}; with the correction ${stat(w)}`);
}
const ins = rows.filter(r => r.insideCount > 0);
console.log(`one body in the other (> 5 mm): ${ins.length} of ${rows.length} frames; deepest ${Math.max(0, ...rows.map(r => r.inside)).toFixed(1)} cm`, ins.slice(0, 12).map(r => `${r.T}:${r.inside}cm/${r.insideCount}`).join(' '));
