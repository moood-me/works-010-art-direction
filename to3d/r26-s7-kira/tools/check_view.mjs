// The viewer as a person opens it (no ?pack: the panel, the mouse): loads, plays a motion, saves a picture.
//   node check_view.mjs out.png
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const { chromium } = createRequire(import.meta.url)('playwright');
const FOLDER = new URL('..', import.meta.url).pathname.split('/').filter(Boolean).pop();
const srv = await serve('/home/user/');
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 1000, height: 760 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: `/home/user/cache/to3d-${FOLDER}/node_modules/three/build/three.module.js`, contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
const t0 = Date.now();
await page.goto(srv.url + `works-010-art-direction/to3d/${FOLDER}/tools/web/view.html`);
await page.waitForFunction(() => window.__ready, null, { timeout: 120000 });
console.log('ready in', Date.now() - t0, 'ms');
await page.selectOption('#mv', 'walk'); await page.click('[data-e="joy"]'); await page.click('#talk');
await page.waitForTimeout(2500);
await page.screenshot({ path: process.argv[2] });
await b.close(); srv.close();
if (errs.length) { console.error('page errors:\n' + errs.join('\n')); process.exit(1); }
