// The numeric check: every case of cases.json (every character preset in a few moments, and moments that exercise
// each option) computed in node — the figure's vertices (every 4th the triangles use, of every mesh) and joints at that
// moment — and compared with the stored numbers (numbers/), in millimetres. So any change of the engine that moves a
// character is seen, and how much, and where.
//   node engine/check/numbers.mjs              compare (fails when anything moved more than the tolerance)
//   node engine/check/numbers.mjs --update     store them (after looking at what changed and at its pictures)
//   node engine/check/numbers.mjs --only woman,man-dqs-sit100     characters or cases
// The stored numbers keep the hashes of the body and the motions they were made from: a difference whose data
// changed says so.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { createEngine } from '../src/engine.js';
import { loadPack } from '../src/pack.js';
import { read } from './node-read.mjs';
import { jobsOf, figureOf, sourcesOf, parseArgs } from './cases.mjs';

const TOLERANCE_MM = 0.05, STRIDE = 4;
const HERE = new URL('./', import.meta.url), STORE = new URL('numbers/numbers.json', HERE);
const args = parseArgs(process.argv);
const E = await createEngine({ read });
const cases = JSON.parse(await readFile(new URL('cases.json', HERE), 'utf8'));
const jobs = jobsOf(cases, (await E.characters()).characters, args.only);
if (!jobs.length) { console.log('no cases to check'); process.exit(1); }

// a job's numbers: the joints, then every STRIDE-th used vertex of each mesh
async function numbersOf(job) {
  const { fig, spec, clip } = await figureOf(E, job);
  const parts = [Float32Array.from(fig.pose.P)];
  for (const o of fig.outputs) { const u = o.mesh.used, a = new Float32Array(Math.ceil(u.length / STRIDE) * 3); for (let k = 0, n = 0; k < u.length; k += STRIDE, n++) for (let c = 0; c < 3; c++) a[n * 3 + c] = o.positions[u[k] * 3 + c]; parts.push(a); }
  const all = new Float32Array(parts.reduce((s, p) => s + p.length, 0)); let at = 0; for (const p of parts) { all.set(p, at); at += p.length; }
  return { values: all, joints: fig.rig.J, sources: await sourcesOf(E, job, spec, clip) };
}

const stored = existsSync(fileURLToPath(STORE)) ? await loadPack(STORE, read) : null;
const now = {};
for (const j of jobs) now[j.name] = await numbersOf(j);

if (args.update) {
  // the stored ones kept for the jobs not run now (--only)
  const keep = {};
  if (stored) for (const [name, m] of Object.entries(stored.header.jobs)) if (!now[name]) keep[name] = { values: stored.arrays[name], joints: m.joints, sources: m.sources };
  const all = { ...keep, ...now }, names = Object.keys(all).sort();
  const header = { format: 'engine/check-numbers', version: 1, about: 'check/numbers.mjs: each case\'s joints and every 4th used vertex, metres', stride: STRIDE,
    jobs: Object.fromEntries(names.map(n => [n, { joints: all[n].joints, sources: all[n].sources }])), bin: 'numbers.bin', arrays: {} };
  const chunks = []; let off = 0;
  for (const n of names) { header.arrays[n] = { dtype: 'float32', shape: [all[n].values.length / 3, 3], offset: off }; chunks.push(Buffer.from(all[n].values.buffer, all[n].values.byteOffset, all[n].values.byteLength)); off += all[n].values.byteLength; }
  await mkdir(new URL('numbers/', HERE), { recursive: true });
  await writeFile(STORE, JSON.stringify(header, null, 1) + '\n');
  await writeFile(new URL('numbers/numbers.bin', HERE), Buffer.concat(chunks));
  console.log(`stored the numbers of ${jobs.length} cases (${names.length} in all)`);
  process.exit(0);
}

if (!stored) { console.log('no stored numbers (run with --update after looking at the pictures)'); process.exit(1); }
let bad = 0;
for (const j of jobs) {
  const m = stored.header.jobs[j.name], a = stored.arrays[j.name], b = now[j.name];
  if (!m) { console.log(`${j.name}: not stored`); bad++; continue; }
  const changed = ['body', 'motions'].filter(k => JSON.stringify(m.sources[k]) !== JSON.stringify(b.sources[k]));
  if (a.length !== b.values.length) { console.log(`${j.name}: another number of vertices (${a.length / 3} stored, ${b.values.length / 3} now)${changed.length ? ' — its ' + changed.join(', ') + ' changed' : ''}`); bad++; continue; }
  let worst = 0, at = 0;
  for (let i = 0; i < a.length; i += 3) { const e = Math.hypot(a[i] - b.values[i], a[i + 1] - b.values[i + 1], a[i + 2] - b.values[i + 2]); if (e > worst) { worst = e; at = i / 3; } }
  if (worst * 1000 > TOLERANCE_MM) {
    bad++;
    const where = at < m.joints ? `joint ${E.skeleton.names[at]}` : `vertex ${(at - m.joints) * STRIDE}th used`;
    console.log(`${j.name}: moved ${(worst * 1000).toFixed(2)} mm (most at ${where})${changed.length ? ' — its ' + changed.map(k => `${k}: ${JSON.stringify(m.sources[k])} → ${JSON.stringify(b.sources[k])}`).join('; ') : ''}`);
  }
}
console.log(bad ? `${bad} of ${jobs.length} cases differ (more than ${TOLERANCE_MM} mm)` : `all ${jobs.length} cases as stored (within ${TOLERANCE_MM} mm)`);
process.exit(bad ? 1 : 0);
