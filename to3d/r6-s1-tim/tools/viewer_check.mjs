// Opens the viewer as the site serves it (the repository's root) and takes a picture after it has run a while.
//   node viewer_check.mjs out.png
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const require = createRequire('/opt/node-tools/node_modules/');
const { chromium } = require('playwright');
const srv = await serve();
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 900, height: 700 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: '/home/user/cache/n3-cloth/node_modules/three/build/three.module.js', contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto(srv.url + 'to3d/r6-s1-tim/tools/web/view.html');
await page.waitForFunction(() => window.__ready, null, { timeout: 300000 });
await page.selectOption('#motion', 'walk');
await page.click('#exprs button:nth-child(3)');
await page.waitForTimeout(20000);
await page.click('#play');
await page.waitForTimeout(5000);
await page.screenshot({ path: process.argv[2] });
await b.close(); srv.close();
console.log(errs.length ? 'errors:\n' + errs.join('\n') : 'no errors');
