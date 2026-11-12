// Pictures of Кира's model: node shots.mjs jobs.json outdir
// jobs: {w, h, query?, set?: {...A.set for all}, shots: [{name, set: {...A.set}}]} — each a transparent PNG.
import { readFile, mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const jobs = JSON.parse(await readFile(process.argv[2], 'utf8')), out = process.argv[3];
await mkdir(out, { recursive: true });
const srv = await serve('/home/user/');
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: jobs.w || 800, height: jobs.h || 800 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: '/home/user/cache/n3-cloth/node_modules/three/build/three.module.js', contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); else console.log('page:', m.text()); });
await page.goto(srv.url + 'works-010-art-direction/to3d/r46-s14-kira/tools/web/view.html?shots=1' + (jobs.query || ''));
try { await page.waitForFunction(() => window.__ready, null, { timeout: 300000 }); }
catch (e) { console.error(errs.join('\n')); await b.close(); srv.close(); process.exit(1); }
for (const s of jobs.shots) {
  const set = { w: jobs.w || 800, h: jobs.h || 800, ...(jobs.set || {}), ...s.set };
  await page.evaluate(async o => { await window.A.set(o); window.A.render(); }, set);
  await page.screenshot({ path: `${out}/${s.name}.png`, omitBackground: true, clip: { x: 0, y: 0, width: set.w, height: set.h } });
}
await b.close(); srv.close();
if (errs.length) { console.error('page errors:\n' + errs.join('\n')); process.exit(1); }
