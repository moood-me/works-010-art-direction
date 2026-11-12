// The viewer as the site serves it (with its controls): opens, plays a motion, changes the face. node viewer_check.mjs out.png
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const { chromium } = createRequire(import.meta.url)('playwright');
const srv = await serve();
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 1100, height: 760 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: '/home/user/cache/n3-cloth/node_modules/three/build/three.module.js', contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto(srv.url + 'to3d/r50-s19-marat/tools/web/view.html');
await page.waitForSelector('#ui.on', { timeout: 60000 });
await page.click('button[data-clip="wave"]'); await page.click('button[data-expr="joy"]'); await page.click('#talk');
await page.waitForTimeout(1500);
await page.screenshot({ path: process.argv[2] });
await b.close(); srv.close();
console.log(errs.length ? 'errors:\n' + errs.join('\n') : 'ok');
