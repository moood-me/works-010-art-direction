// A look at the interactive viewer as the site serves it (from the repository's root): node viewer_check.mjs out.png
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const { chromium } = createRequire(import.meta.url)('playwright');
const srv = await serve();
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 900, height: 640 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: '/home/user/cache/to3d-r29-s9-anya/node_modules/three/build/three.module.js', contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto(srv.url + 'to3d/r29-s9-anya/tools/web/anya.html');
await page.waitForFunction(() => window.__ready, null, { timeout: 120000 });
await page.waitForTimeout(4000);
await page.click('#talk'); await page.click('text=радость');
await page.mouse.move(450, 320); await page.mouse.down(); await page.mouse.move(380, 300, { steps: 5 }); await page.mouse.up();
await page.waitForTimeout(3000);
await page.screenshot({ path: process.argv[2], timeout: 120000 });
await b.close(); srv.close();
if (errs.length) { console.error(errs.join('\n')); process.exit(1); }
