// Runs our О3 cloth (experiments/cloth, unchanged) in Node for one outfit and motion, and writes what the other
// simulators need: the body's skin each frame, the joints' matrices each frame, every garment as dressed (its rest
// shape, triangles, hold, skin weights) and our own cloth's points each frame (the "now" side).
// node export.mjs <outfit id> <motion id> <out dir> [frames]
import * as THREE from '/home/user/cache/n3-cloth/node_modules/three/build/three.module.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const here = path.dirname(fileURLToPath(import.meta.url)), exp = path.resolve(here, '../../../experiments');
const { person } = await import(exp + '/cloth/people.js');
const { Scene } = await import(exp + '/cloth/sim.js');

const [outfit, motion, out, upto] = process.argv.slice(2);
// the page's outfits and motions (experiments/cloth/index.html), read from it so they are the same
const page = fs.readFileSync(exp + '/cloth/index.html', 'utf8');
const OUTFITS = eval(page.match(/const OUTFITS = (\[[\s\S]*?\n\]);/)[1]), MOTIONS = eval(page.match(/const MOTIONS = (\[[\s\S]*?\n\]);/)[1]);
const O = OUTFITS.find(o => o.id === outfit), Mo = MOTIONS.find(m => m.id === motion);
const bytes = async name => { const m = await import(exp + '/data/' + name + '.js'); return Uint8Array.from(Buffer.from(m.default, 'base64')).buffer; };
const meta = JSON.parse(fs.readFileSync(exp + '/data/meta.json'));
const body = await person(THREE, bytes, meta, O.who);
const M = JSON.parse(fs.readFileSync(exp + '/cloth/motions/' + Mo.file + '.json'));
const data = {}; for (const [g] of O.wear) if (['dress', 'tshirt', 'sweater', 'pants', 'shorts'].includes(g)) data[g] = await bytes(g);
const wind = 0;
const S = new Scene(THREE, body, M, O.wear.map(([g, fabric]) => ({ g, fabric })), data, { cyclic: !!Mo.cyclic, wind: null });
const F = +(upto || Mo.frames);
fs.mkdirSync(out, { recursive: true });
const w = (name, arr) => fs.writeFileSync(path.join(out, name), Buffer.from(arr.buffer, arr.byteOffset, arr.byteLength));
// frame 0 is the rest pose the garments were put on in
const bodyF = new Float32Array((F + 1) * body.N * 3), EF = new Float32Array((F + 1) * 77 * 16);
bodyF.set(S.bodyB.pos, 0); S.E.forEach((e, j) => EF.set(e, j * 16));
const ours = S.cloths.map(c => { const a = new Float32Array((F + 1) * c.n * 3); a.set(c.x, 0); return a; });
const t0 = Date.now();
for (let f = 1; f <= F; f++) {
  S.frame();
  bodyF.set(S.bodyB.pos, f * body.N * 3); S.E.forEach((e, j) => EF.set(e, (f * 77 + j) * 16));
  S.cloths.forEach((c, k) => ours[k].set(c.x, f * c.n * 3));
}
const secs = (Date.now() - t0) / 1000;
w('body.f32', bodyF); w('E.f32', EF); w('bodytris.u32', Uint32Array.from(body.tris));
const garments = S.cloths.map((c, k) => {
  w(`ours-${c.name}.f32`, ours[k]); w(`${c.name}-tris.u32`, Uint32Array.from(c.tris)); w(`${c.name}-rest.f32`, Float32Array.from(c.restSkin));
  w(`${c.name}-hold.f32`, Float32Array.from(c.hold)); w(`${c.name}-skinJ.u8`, Uint8Array.from(c.skinJ)); w(`${c.name}-skinW.u8`, Uint8Array.from(c.skinW));
  return { name: c.name, n: c.n, fabric: c.fabric.key, F: { ...c.fabric } };
});
const info = { outfit: O, motion: Mo, frames: F + 1, N: body.N, garments, oursSeconds: secs, joints: meta.joints };
fs.writeFileSync(path.join(out, 'run.json'), JSON.stringify(info, null, 1));
console.log(outfit, motion, F, 'frames', secs.toFixed(0) + 's', garments.map(g => g.name + ':' + g.n).join(' '));
