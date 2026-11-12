// Pictures of the 3D Савелий: node shots.mjs jobs.json outdir
// jobs: [{name, set: {...A.set}}] — each sets the page, draws, and saves outdir/name.json (the grid of colour keys;
// for mode 'solid'/'clay' a PNG of the canvas instead);
// a film: {name, set, frames: [{t, expr, talk, yaw}, ...]} saves outdir/name.json with every frame's grid.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const jobs = JSON.parse(await readFile(process.argv[2], 'utf8')), out = process.argv[3];
await mkdir(out, { recursive: true });
const srv = await serve();
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 1000, height: 800 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: '/home/user/cache/n3-cloth/node_modules/three/build/three.module.js', contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.text()); });
const t0 = Date.now();
await page.goto(srv.url + 'to3d/r46-s16-savely/tools/web/view.html?shots');
try { await page.waitForFunction(() => window.__ready, null, { timeout: 600000 }); }
catch (e) { console.error(errs.join('\n')); throw e; }
console.log('built in', ((Date.now() - t0) / 1000).toFixed(1), 's');
for (const j of jobs) {
  if (j.frames) {
    const grids = await page.evaluate(async ({ set, frames }) => {
      await window.A.set(set); const out = [];
      for (const f of frames) { if (f.yaw !== undefined) window.A.V.yaw = f.yaw; window.A.frame(f); window.A.render(); out.push(window.A.grid().map(r => r.join(','))); }
      return out;
    }, j);
    await writeFile(`${out}/${j.name}.json`, JSON.stringify(grids));
  } else {
    const g = await page.evaluate(async set => { await window.A.set(set); window.A.render(); return /solid|clay/.test(window.A.V.mode) ? null : window.A.grid(); }, j.set);
    if (g) await writeFile(`${out}/${j.name}.json`, JSON.stringify(g));
    else await (await page.$('#cv')).screenshot({ path: `${out}/${j.name}.png` });
  }
  console.log(j.name);
}
await b.close(); srv.close();
if (errs.length) { console.error('page messages:\n' + errs.join('\n')); }
