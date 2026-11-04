// The checks' cases (cases.json) as jobs, and a job's figure at its moment — the same in node (numbers.mjs) and in a
// page (render.html, for pictures.mjs).
import { HEAD_BUILD } from '../src/head/version.js';
import { paintFace } from '../src/head/paint.js';
import { paintState } from '../src/head/expressions.js';
import { hashOf } from '../src/hash.js';

export function jobsOf(cases, characters, only) {
  const ids = characters.map(c => c.id);
  const jobs = [...ids.flatMap(char => cases.each.map(c => ({ ...c, char, name: `${char}-${c.name}` }))),
    ...cases.cases.map(c => ({ ...c, name: `${c.char}-${c.name}` }))];
  for (const j of jobs) if (!ids.includes(j.char)) throw new Error(`case ${j.name}: no character ${j.char}`);
  if (!only) return jobs;
  // --only: characters or case names; each must name something
  const picked = jobs.filter(j => only.includes(j.char) || only.includes(j.name));
  const unknown = only.filter(o => !jobs.some(j => j.char === o || j.name === o));
  if (unknown.length) throw new Error(`--only: no character or case ${unknown.join(', ')} (characters: ${ids.join(', ')})`);
  return picked;
}

// the job's character: its description with the case's keys replaced, checked like any — at its moment: a figure with
// simulations (hair that moves) stepped there frame by frame from the start (the wind a preset's: job.wind), else
// that moment's frame
export async function figureOf(E, job) {
  const d = structuredClone(await E.description(job.char));
  for (const [k, v] of Object.entries(job.over || {})) d[k] = v;
  const spec = await E.resolve(d);
  const fig = await E.figure(spec, { place: job.place });
  const clip = job.clip ? await E.clip(job.clip) : null;
  if (fig.simulations.length) {
    const wind = job.wind ? (await E.preset(job.wind)).wind : null;
    for (const s of fig.simulations) s.wind = wind;
    for (let k = 0; k < job.t; k++) fig.step(clip, k);
    fig.step(clip, job.t);
  } else fig.frame(clip, job.t, fig.pose);
  return { fig, clip, spec, description: d };
}

// what the job's numbers depend on: the body, the motions (their hashes); for a head, how heads are built (their
// versions: src/head/version.js) and its face's picture as drawn at that moment (the hash of the drawing's every stroke)
export async function sourcesOf(E, job, spec, clip, fig) {
  const body = await E.body(spec.body), out = { body: `${spec.bodyId}@${body.hash.slice(0, 16)}` };
  if (clip) out.motions = await Promise.all(clip.motions.map(async id => `${id}@${(await E.motion(id)).hash.slice(0, 16)}`));
  if (fig.body.head) { out.heads = HEAD_BUILD; out.picture = pictureHash(fig.body.head, fig.ctx.expressions); }
  return out;
}

// the face's picture as a hash of what drawing it does (src/head/paint.js on a context that keeps every call and every
// setting, its numbers rounded to a millionth): in node, with no canvas, the drawing itself is what is compared
export function pictureHash(head, expressions) {
  const strokes = [], value = v => typeof v === 'number' ? Math.round(v * 1e6) / 1e6 : v;
  const g = new Proxy({ canvas: { width: 1024, height: 1024 } }, {
    get: (t, k) => k === 'canvas' ? t.canvas : (...a) => { strokes.push([k, ...a.map(value)]); if (/^create.*Gradient$/.test(k)) return { addColorStop: (...s) => strokes.push(['stop', ...s.map(value)]) }; },
    set: (t, k, v) => { strokes.push(['=', k, typeof v === 'object' ? 'gradient' : value(v)]); return true; },
  });
  paintFace(g, 1024, head.features, head.skin, paintState(head, expressions));
  return hashOf([strokes]).slice(0, 16);
}

export const parseArgs = argv => {
  const a = argv.slice(2), at = k => a.includes(k) ? a[a.indexOf(k) + 1] : null;
  if (a.includes('--only') && !at('--only')) throw new Error('--only needs names');
  return { update: a.includes('--update'), only: at('--only') ? at('--only').split(',') : null, rest: a };
};
