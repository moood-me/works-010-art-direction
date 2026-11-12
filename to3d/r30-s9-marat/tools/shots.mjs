// Pictures of Tim's model: node shots.mjs jobs.json outdir
// jobs: {w, h, shots: [{name, set: {...A.set}, compose?: backdrop-svg-url | true, film?: {from, to, step, yaw?: [a, b]}}]}
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
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: '/home/user/cache/to3d-r30-s9-marat/node_modules/three/build/three.module.js', contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); else console.log('page:', m.text()); });
await page.goto(srv.url + 'works-010-art-direction/to3d/r30-s9-marat/tools/web/marat.html?shots=1');
try { await page.waitForFunction(() => window.__ready, null, { timeout: 100000 }); }
catch (e) { console.error(errs.join("\n")); await b.close(); srv.close(); throw e; }
const shoot = async (set, path, compose) => {
  await page.evaluate(async ([o, c]) => { await window.A.set(o); window.A.render(); if (c) await window.A.compose(c === true ? null : c); }, [set, compose]);
  const w = set.w || jobs.w || 800, h = set.h || jobs.h || 800;
  if (set.w) await page.setViewportSize({ width: w, height: h });
  await page.screenshot({ path, omitBackground: !compose, clip: { x: 0, y: 0, width: w, height: h } });
  if (compose) await page.evaluate(() => window.A.uncompose());
};
for (const s of jobs.shots) {
  const set = { w: jobs.w || 800, h: jobs.h || 800, ...(jobs.set || {}), ...s.set };
  if (s.film) {
    await mkdir(`${out}/${s.name}`, { recursive: true });
    let k = 0;
    for (let t = s.film.from; t <= s.film.to + 1e-9; t += s.film.step) {
      const o = { ...set, t };
      if (s.film.yaw) { o.cam = { ...set.cam, yaw: s.film.yaw[0] + (s.film.yaw[1] - s.film.yaw[0]) * (t - s.film.from) / (s.film.to - s.film.from) }; if (!s.film.motion) delete o.t; }
      await shoot(o, `${out}/${s.name}/f${String(k++).padStart(4, '0')}.png`, s.compose);
    }
  } else await shoot(set, `${out}/${s.name}.png`, s.compose);
  console.log(s.name);
}
await b.close(); srv.close();
if (errs.length) { console.error('page errors:\n' + errs.join('\n')); process.exit(1); }
