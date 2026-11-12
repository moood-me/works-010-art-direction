// The viewer as a person opens it (with its controls): node viewer_check.mjs out.png [motion]
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const here = path.dirname(fileURLToPath(import.meta.url)), folder = path.basename(path.dirname(here));
const srv = await serve('/home/user/');
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 900, height: 700 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: `/home/user/cache/to3d-${folder}/node_modules/three/build/three.module.js`, contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto(srv.url + `works-010-art-direction/to3d/${folder}/tools/web/view.html`);
await page.waitForFunction(() => window.__ready, null, { timeout: 300000 });
if (process.argv[3]) { await page.selectOption('#mv', process.argv[3]); }
await page.waitForTimeout(6000);
await page.screenshot({ path: process.argv[2] });
await b.close(); srv.close();
if (errs.length) { console.error('page errors:\n' + errs.join('\n')); process.exit(1); }
console.log('viewer ok');
