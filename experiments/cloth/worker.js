// The simulation, away from the page: given who, what they wear, the motion and the wind, it runs the frames and
// sends each one back (every garment's points, and the joints' matrices to carry the body, shoes and hair).
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { person } from './people.js';
import { Scene } from './sim.js';

const cache = {};
const bytes = name => (cache[name] ??= import('../data/' + name + '.js').then(m => Uint8Array.from(atob(m.default), c => c.charCodeAt(0)).buffer));
let meta = null, job = 0;

onmessage = async e => {
  const o = e.data, my = ++job;
  meta ??= await (await fetch('../data/meta.json')).json();
  if (my !== job) return;
  const body = await person(THREE, bytes, meta, o.who);
  const M = o.motion ? await (await fetch('motions/' + o.motion + '.json')).json() : null;
  const data = {};
  for (const w of o.wear) if (['dress', 'tshirt', 'sweater', 'pants', 'shorts'].includes(w.g)) data[w.g] = await bytes(w.g);   // (MakeHuman's)
  const S = new Scene(THREE, body, M, o.wear, data, { cyclic: o.cyclic, wind: o.wind });
  postMessage({ type: 'cut', id: o.id, garments: S.cloths.map(c => ({ name: c.name, fabric: c.fabric.key, tris: c.tris, n: c.n, rest: c.restSkin })), frames: o.frames });
  for (let f = 0; f < o.frames; f++) {
    if (my !== job) return;
    S.frame();
    const pos = S.cloths.map(c => Float32Array.from(c.x));
    postMessage({ type: 'frame', id: o.id, f, E: S.E.map(e => Float32Array.from(e)), pos }, pos.map(p => p.buffer));
    if (f % 4 === 3) await new Promise(r => setTimeout(r, 0));   // (a new job can come in)
  }
  postMessage({ type: 'done', id: o.id });
};
