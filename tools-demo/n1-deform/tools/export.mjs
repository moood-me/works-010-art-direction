// Exports Anny meshes from our own experiment pages (form-tools: cage, face, smoothing; lines: arcs, line of action)
// so libigl works on exactly the same bodies and our results are rendered the same way.
// node export.mjs <outdir>   (run from anywhere; serves the repository itself)
import { createRequire } from 'node:module';
import { writeFile, mkdir } from 'node:fs/promises';
import { serve } from '../../../engine/check/serve.mjs';
const require = createRequire('/opt/node-tools/node_modules/');
const { chromium } = require('playwright');
const out = process.argv[2]; await mkdir(out, { recursive: true });
const srv = await serve();
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage({ viewport: { width: 900, height: 600 } });
const errs = []; p.on('pageerror', e => errs.push(e.message));
const save = async (name, arr, kind = 'f4') => { const buf = kind === 'f4' ? Buffer.from(new Float32Array(arr).buffer) : Buffer.from(new Int32Array(arr).buffer); await writeFile(`${out}/${name}.${kind}`, buf); };

// ——— form-tools, the body at rest (the page's own __restPose hook) ———
await p.addInitScript(() => { window.__restPose = true; });
await p.goto(srv.url + 'experiments/form-tools/index.html');
await p.waitForFunction(() => window.__sh && window.__vp, null, { timeout: 300000 });
const base = await p.evaluate(() => { const B = window.__vp.BASE; return { N: B.N, tris: Array.from(B.tris), joint: Array.from(B.joint), weight: Array.from(B.weight), JN: window.__vp.JN }; });
await save('tris', base.tris, 'i4'); await save('joint', base.joint, 'i4'); await save('weight', base.weight, 'i4');
await writeFile(`${out}/joints.json`, JSON.stringify(base.JN));
const grab = async (gw, cw, over) => p.evaluate(async ([gw, cw, over]) => {
  const S = window.__sh.state; S.mode = 'one'; S.who = 'woman'; S.gw = gw; S.cw = cw; S.over = over; await window.__sh.refresh();
  const m = window.__vp.group.children[0].children[0]; return { pos: Array.from(m.geometry.attributes.position.array), J: window.__restJ.flatMap(v => [v.x, v.y, v.z]) };
}, [gw, cw, over]);
const DIS = [{ disney: 1 }, { princess: 0.6 }];
const jobs = { disney: {}, cage_hourglass: { cageType: 'hourglass', cageAmt: 0.8 }, cage_pear: { cageType: 'pear', cageAmt: 1 }, cage_egg: { cageType: 'egg', cageAmt: 1 }, cage_wedge: { cageType: 'wedge', cageAmt: 1 },
  face_elf: { faceType: 'elf', faceAmt: 1 }, face_anime: { faceType: 'anime', faceAmt: 1.3 }, face_burton: { faceType: 'burton', faceAmt: 1.2 }, face_pixar: { faceType: 'pixar', faceAmt: 1.3 }, face_hero: { faceType: 'hero', faceAmt: 1.3 } };
for (const [name, over] of Object.entries(jobs)) { const r = await grab(...DIS, over); await save('ft_' + name, r.pos); await save('ft_' + name + '_J', r.J); console.log(name); }
// the raw Anny woman (no style) and our two smoothings of her: the old uniform (Taubin) and the current cotangent one
const raw = await grab({}, {}, { deg: -0.75 }); await save('raw_woman', raw.pos); await save('raw_woman_J', raw.J);
for (const R of [0.02, 0.04]) {
  const sm = await p.evaluate(R => { const pos = Float32Array.from(window.__vp.group.children[0].children[0].geometry.attributes.position.array); return Array.from(window.__sh.dbg.curvSmooth(pos, R, () => 1)); }, R);
  await save('ours_cot_' + Math.round(R * 100), sm);
}
const tb = await p.evaluate(() => { const pos = Float32Array.from(window.__vp.group.children[0].children[0].geometry.attributes.position.array); return Array.from(window.__sh.dbg.taubin(pos, () => 1, 40)); });
await save('ours_taubin', tb);

// ——— lines: the posed body, deformed by our deform(). The page keeps its group to itself; for this export only, the
// served copy gets one line that hands it out (the file in the repository is not touched) ———
const p2 = await b.newPage({ viewport: { width: 900, height: 600 } }); p2.on('pageerror', e => errs.push(e.message));
await p2.route('**/experiments/lines/index.html', async r => { const res = await r.fetch(); const t = (await res.text()).replace('window.__sh = {', 'window.__group = group; window.__sh = {'); await r.fulfill({ response: res, body: t }); });
await p2.goto(srv.url + 'experiments/lines/index.html');
await p2.waitForFunction(() => window.__sh && window.__group, null, { timeout: 300000 });
const lines = { base: {}, arc1: { arc: 1 }, arc05: { arc: 0.5 }, lineC: { front: { type: 'C', a: 0.08 } }, squash: { stretch: -0.35 } };
for (const [name, D] of Object.entries(lines)) {
  const pos = await p2.evaluate(async D => { window.__items = [{ tag: '', ...D }]; const S = window.__sh.state; S.mode = 'items'; S.who = 'woman'; await window.__sh.refresh(); return Array.from(window.__group.children[0].children[0].geometry.attributes.position.array); }, D);
  await save('ln_' + name, pos); console.log('lines', name, pos.length / 3);
}
console.log(errs.join('\n') || 'no errors'); await b.close(); srv.close();
