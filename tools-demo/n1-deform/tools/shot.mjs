// node shot.mjs jobs.json — renders each job's meshes with shot.html (the scene of experiments/form-tools) to job.out
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const require = createRequire('/opt/node-tools/node_modules/');
const { chromium } = require('playwright');
const jobs = JSON.parse(await readFile(process.argv[2], 'utf8'));
const srv = await serve('/home/user/');
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage({ viewport: { width: 1600, height: 1000 } });
const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
await p.goto(srv.url + 'works-010-art-direction/tools-demo/n1-deform/tools/shot.html');
await p.waitForFunction(() => window.ready, null, { timeout: 60000 });
const U = s => srv.url + s.replace(/^\/home\/user\//, '');
for (const j of jobs) {
  await p.setViewportSize({ width: j.w, height: j.h });
  await p.evaluate(j => window.shot(j), { ...j, tris: U(j.tris), meshes: j.meshes.map(U), colors: j.colors && j.colors.map(c => c && U(c)) });
  await (await p.$('#st')).screenshot({ path: j.out, type: j.out.endsWith('.jpg') ? 'jpeg' : 'png', ...(j.out.endsWith('.jpg') ? { quality: 88 } : {}) });
  console.log(j.out);
}
console.log(errs.join('\n') || 'no errors'); await b.close(); srv.close();
