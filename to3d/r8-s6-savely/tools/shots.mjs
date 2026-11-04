// Pictures and films of the 3D Савелий: node shots.mjs jobs.json outdir
// a picture: {name, size: [w, h], set: {...A.set}, warm: seconds of life lived first (breath, springs)}
// a film: {name, size, set: {...}, frames: n | [{...A.frame}], dt} — set once, then each frame saved as outdir/name/f0000.png
import { readFile, mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const require = createRequire('/opt/node-tools/node_modules/');
const { chromium } = require('playwright');

const jobs = JSON.parse(await readFile(process.argv[2], 'utf8')), out = process.argv[3];
await mkdir(out, { recursive: true });
const srv = await serve();
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 800, height: 800 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: '/home/user/cache/n3-cloth/node_modules/three/build/three.module.js', contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.text()); else console.log('page:', m.text()); });
const t0 = Date.now();
await page.goto(srv.url + 'to3d/r8-s6-savely/tools/web/view.html?shots');
try { await page.waitForFunction(() => window.__ready, null, { timeout: 600000 }); }
catch (e) { console.error(errs.join('\n')); throw e; }
console.log('ready in', ((Date.now() - t0) / 1000).toFixed(1), 's');
for (const j of jobs) {
  await page.setViewportSize({ width: j.size[0], height: j.size[1] });
  await page.evaluate(o => { window.A.set(o); }, { size: j.size, ...j.set });
  if (j.warm) await page.evaluate(([s, dt]) => { for (let t = 0; t < s; t += dt) window.A.frame({ dt, skip: true }); }, [j.warm, 1 / 30]);
  const clip = { x: 0, y: 0, width: j.size[0], height: j.size[1] };
  if (j.frames) {
    await mkdir(`${out}/${j.name}`, { recursive: true });
    const frames = typeof j.frames === 'number' ? Array.from({ length: j.frames }, () => ({})) : j.frames;
    for (let k = 0; k < frames.length; k++) {
      await page.evaluate(o => window.A.frame(o), { dt: j.dt ?? 1 / 30, ...frames[k] });
      await page.screenshot({ path: `${out}/${j.name}/f${String(k).padStart(4, '0')}.png`, clip });
    }
  } else {
    await page.evaluate(() => window.A.render());
    await page.screenshot({ path: `${out}/${j.name}.png`, clip });
  }
  console.log(j.name, ((Date.now() - t0) / 1000).toFixed(1), 's');
}
await b.close(); srv.close();
if (errs.length) console.error('page messages:\n' + errs.join('\n'));
