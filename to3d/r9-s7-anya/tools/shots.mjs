// Pictures of the 3D Аня: node shots.mjs jobs.json outdir
// jobs: {pack, w, h, shots: [{name, set: {...A.set options}}]} — each shot sets the page and saves a png.
// For a film: {name, film: {from, to, step}, set} saves name/f0000.png … (t from…to).
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
await page.goto(srv.url + 'works-010-art-direction/to3d/r9-s7-anya/tools/web/view.html?pack=' + encodeURIComponent(jobs.pack) + (jobs.query || ''));
try { await page.waitForFunction(() => window.__ready, null, { timeout: 300000 }); }
catch (e) { console.error(errs.join('\n')); throw e; }
for (const s of jobs.shots) {
  if (s.w) await page.setViewportSize({ width: s.w, height: s.h });
  if (s.film) {
    await mkdir(`${out}/${s.name}`, { recursive: true });
    let k = 0;
    for (let t = s.film.from; t <= s.film.to + 1e-9; t += s.film.step) {
      const set = { ...s.set, t };
      if (s.film.yaw) set.cam = { ...(s.set.cam || {}), yaw: s.film.yaw[0] + (s.film.yaw[1] - s.film.yaw[0]) * (t - s.film.from) / (s.film.to - s.film.from) };
      await page.evaluate(async o => { await window.A.set(o); window.A.render(); }, set);
      await page.screenshot({ path: `${out}/${s.name}/f${String(k++).padStart(4, '0')}.png` });
    }
  } else {
    await page.evaluate(async o => { await window.A.set(o); window.A.render(); }, s.set || {});
    await page.screenshot({ path: `${out}/${s.name}.png` });
  }
  console.log(s.name);
}
await b.close(); srv.close();
if (errs.length) { console.error('page errors:\n' + errs.join('\n')); process.exit(1); }
