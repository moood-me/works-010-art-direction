// The checks' cases (cases.json) as jobs, and a job's figure at its moment — the same in node (numbers.mjs) and in a
// page (render.html, for pictures.mjs).

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

// the job's character: its description with the case's keys replaced, checked like any
export async function figureOf(E, job) {
  const d = structuredClone(await E.description(job.char));
  for (const [k, v] of Object.entries(job.over || {})) d[k] = v;
  const spec = await E.resolve(d);
  const fig = await E.figure(spec, { place: job.place });
  const clip = job.clip ? await E.clip(job.clip) : null;
  fig.frame(clip, job.t, fig.pose);
  return { fig, clip, spec, description: d };
}

// what the job's numbers depend on: the body, the motions, the description (their hashes)
export async function sourcesOf(E, job, spec, clip) {
  const body = await E.body(spec.body), out = { body: `${spec.bodyId}@${body.hash.slice(0, 16)}` };
  if (clip) out.motions = await Promise.all(clip.motions.map(async id => `${id}@${(await E.motion(id)).hash.slice(0, 16)}`));
  return out;
}

export const parseArgs = argv => {
  const a = argv.slice(2), at = k => a.includes(k) ? a[a.indexOf(k) + 1] : null;
  if (a.includes('--only') && !at('--only')) throw new Error('--only needs names');
  return { update: a.includes('--update'), only: at('--only') ? at('--only').split(',') : null, rest: a };
};
