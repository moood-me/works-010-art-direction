// The skeleton every body and motion here stands on: SOMA's 77 joints, as Kimodo moves them (data/skeleton.json,
// made by tools/soma.py from Kimodo's SOMA skin). Its rest is the T-pose a motion's rotations are measured against.
import { readJSON } from './pack.js';

export async function loadSkeleton(url, read) {
  const s = await readJSON(url, read);
  if (s.format !== 'engine/skeleton' || s.version !== 1) throw new Error(`${url}: not a skeleton of version 1`);
  return makeSkeleton(s);
}

export function makeSkeleton(s) {
  const J = s.joints.length, names = s.joints.map(j => j.name);
  const sk = {
    id: s.id, J, names, floor: s.floor,
    index: Object.fromEntries(names.map((n, i) => [n, i])),
    parent: Int16Array.from(s.joints, j => j.parent),
    side: s.joints.map(j => j.side), part: s.joints.map(j => j.part),
    rest: Float64Array.from(s.joints.flatMap(j => j.rest)),
    frames: Float64Array.from(s.joints.flatMap(j => j.frame)),
  };
  // parents always come before their children (the order a pose is built in)
  for (let j = 0; j < J; j++) if (sk.parent[j] >= j) throw new Error(`skeleton ${s.id}: ${names[j]}'s parent comes after it`);
  sk.children = names.map((_, j) => names.map((__, k) => k).filter(k => sk.parent[k] === j));
  // the joints under j (j too)
  const under = names.map((_, j) => { const out = [j]; for (let k = j + 1; k < J; k++) if (out.includes(sk.parent[k])) out.push(k); return out; });
  sk.under = j => under[j];
  return sk;
}
