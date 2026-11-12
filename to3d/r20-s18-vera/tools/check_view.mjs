// The viewer as a person opens it (no ?pack): loads, a motion and an expression chosen, a picture saved.  node check_view.mjs out.png
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const { chromium } = createRequire(import.meta.url)('playwright');
const srv = await serve('/home/user/');
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 1000, height: 700 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: '/home/user/cache/n3-cloth/node_modules/three/build/three.module.js', contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto(srv.url + 'works-010-art-direction/to3d/r20-s18-vera/tools/web/view.html');
await page.waitForFunction(() => window.__ready && document.querySelector('#ui'), null, { timeout: 120000 });
await page.selectOption('#mv', 'walk'); await page.click('[data-e="joy"]'); await page.click('#talk');
await page.waitForTimeout(4000);
await page.screenshot({ path: process.argv[2] });
await b.close(); srv.close();
console.log(errs.length ? 'errors:\n' + errs.join('\n') : 'viewer ok');
