// A look at the viewer as a person opens it (not ?shots): node view_check.mjs out.png [button text to press]
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
import { fileURLToPath } from 'node:url';
import { basename, dirname } from 'node:path';
const FOLDER = basename(dirname(dirname(fileURLToPath(import.meta.url))));
const THREE_PATH = process.env.THREE || `/home/user/cache/to3d-${FOLDER}/node_modules/three/build/three.module.js`;
const require = createRequire('/opt/node-tools/node_modules/');
const { chromium } = require('playwright');
const srv = await serve();
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 900, height: 640 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: THREE_PATH, contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto(srv.url + `to3d/${FOLDER}/tools/web/view.html?slow`);
await page.waitForFunction(() => window.__ready, null, { timeout: 120000 });
for (const t of process.argv.slice(3)) { await page.getByRole('button', { name: t, exact: true }).click(); await page.waitForTimeout(2500); }
await page.waitForTimeout(2500);
await page.screenshot({ path: process.argv[2] });
await b.close(); srv.close();
console.log(errs.length ? 'page errors:\n' + errs.join('\n') : 'no page errors');
