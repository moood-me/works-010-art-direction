// Pictures of the viewer as the site shows it (served from the repository's root; three.js routed to the local copy):
// node viewshot.mjs OUTDIR '[{"name": "a", "set": {"motion": "walk", "t": 1.2, "expr": "joy"}}]' [w h]
import { mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const [out, list, w = 900, h = 700] = process.argv.slice(2);
await mkdir(out, { recursive: true });
const srv = await serve();
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: +w, height: +h } });
const T = '/home/user/cache/to3d-r27-s8-savely/node_modules/three/';
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', r => {
  const p = r.request().url().replace('https://cdn.jsdelivr.net/npm/three@0.160.0/', T);
  r.fulfill({ path: p, contentType: 'text/javascript' });
});
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto(srv.url + 'to3d/r27-s8-savely/tools/web/view.html' + (JSON.parse(list).length ? '?shots=1' : ''));
try { await page.waitForFunction(() => window.__ready, null, { timeout: 600000 }); }
catch (e) { console.error(errs.join('\n')); throw e; }
await page.waitForTimeout(2500);          // the paints (textures) load after the page is ready
for (const s of JSON.parse(list)) {
  await page.evaluate(async o => { await window.A.set(o); }, s.set);
  await page.waitForTimeout(300);
  await page.screenshot({ path: `${out}/${s.name}.png` });
  console.log(s.name);
}
await b.close(); srv.close();
if (errs.length) { console.error('page errors:\n' + errs.join('\n')); process.exit(1); }
