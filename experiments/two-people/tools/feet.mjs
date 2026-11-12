// how high a person's lowest point is above the floor, frame by frame (one carried: off the floor while held; set
// down, it should be 0)   node tools/feet.mjs <scene> <who> <from> <to> <step>
import { createEngine } from '../../../engine/src/engine.js';
import { read } from '../../../engine/check/node-read.mjs';
import { loadScene } from '../scene.js';
import { SCENES } from '../scenes.js';
const [id, who, a, b, st] = process.argv.slice(2);
const E = await createEngine({ read });
const S = await loadScene(E, new URL('../', import.meta.url), SCENES.find(s => s.id === id), read);
const out = [];
for (let T = +a; T <= +b; T += +st) { S.at(T); const P = S.by[who].fig.positions; let lo = Infinity; for (let i = 1; i < P.length; i += 3) lo = Math.min(lo, P[i]); out.push(`${T}:${(lo * 100).toFixed(1)}`); }
console.log(who, 'lowest point, cm:', out.join(' '));
