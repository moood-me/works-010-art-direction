// Pictures of the 3D Вера: node shots.mjs jobs.json outdir
// jobs: [{name, size: [w, h], set: {...A.set}}] — each sets the page and saves outdir/name.png;
// a film: {name, size, set: {...A.set}, frames: [{t, dt, expr, talk}, ...]} sets once, then saves each moment
// (A.frame) as outdir/name/f0000.png … — the face lives on from frame to frame
import { readFile, mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const jobs = JSON.parse(await readFile(process.argv[2], 'utf8')), out = process.argv[3];
await mkdir(out, { recursive: true });
const srv = await serve();
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 800, height: 800 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: '/home/user/cache/n3-cloth/node_modules/three/build/three.module.js', contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.text()); });
const t0 = Date.now();
await page.goto(srv.url + 'to3d/r4-s5-vera/tools/web/view.html?shots');
try { await page.waitForFunction(() => window.__ready, null, { timeout: 600000 }); }
catch (e) { console.error(errs.join('\n')); throw e; }
console.log('built in', ((Date.now() - t0) / 1000).toFixed(1), 's');
const shot = async (size, set, path) => {
  await page.setViewportSize({ width: size[0], height: size[1] });
  await page.evaluate(async o => { await window.A.set(o); window.A.render(); }, { size, ...set });
  await page.screenshot({ path, clip: { x: 0, y: 0, width: size[0], height: size[1] } });
};
for (const j of jobs) {
  if (j.frames) {
    await mkdir(`${out}/${j.name}`, { recursive: true });
    await page.setViewportSize({ width: j.size[0], height: j.size[1] });
    await page.evaluate(async o => { await window.A.set(o); }, { size: j.size, ...j.set });
    for (let k = 0; k < j.frames.length; k++) {
      await page.evaluate(o => { window.A.frame(o); window.A.render(); }, j.frames[k]);
      await page.screenshot({ path: `${out}/${j.name}/f${String(k).padStart(4, '0')}.png`, clip: { x: 0, y: 0, width: j.size[0], height: j.size[1] } });
    }
  } else await shot(j.size, j.set, `${out}/${j.name}.png`);
  console.log(j.name);
}
await b.close(); srv.close();
if (errs.length) { console.error('page messages:\n' + errs.join('\n')); }
