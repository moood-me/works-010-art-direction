// The viewer as a person opens it: node view_check.mjs out.png — loads tools/web/view.html, waits, clicks a motion and
// an expression, saves a picture; prints page errors
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { serve } from '../../../engine/check/serve.mjs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const here = path.dirname(fileURLToPath(import.meta.url)), folder = path.basename(path.dirname(here));
const THREE = `/home/user/cache/to3d-${folder}/node_modules/three/build/three.module.js`;
const srv = await serve();
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 1100, height: 760 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: THREE, contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto(srv.url + `to3d/${folder}/tools/web/view.html`);
await page.waitForSelector('#ui.on', { timeout: 120000 });
await page.waitForTimeout(1500);
await page.screenshot({ path: process.argv[2].replace('.png', '-1.png') });
await page.click('#clips button:nth-child(2)'); await page.click('#exprs button:nth-child(2)'); await page.click('#talk');
await page.mouse.move(500, 300); await page.mouse.down(); await page.mouse.move(380, 290, { steps: 5 }); await page.mouse.up();
await page.waitForTimeout(2500);
await page.screenshot({ path: process.argv[2] });
console.log(errs.length ? 'errors:\n' + errs.join('\n') : 'no errors');
await b.close(); srv.close();
