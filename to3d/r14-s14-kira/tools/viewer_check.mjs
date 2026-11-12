// node viewer_check.mjs out.png — opens web/view.html as the site serves it (with its controls), lets it play, takes a picture
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const { chromium } = createRequire(import.meta.url)('playwright');
const srv = await serve('/home/user/works-010-art-direction/');
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 1100, height: 760 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: '/home/user/cache/n3-cloth/node_modules/three/build/three.module.js', contentType: 'text/javascript' }));
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto(srv.url + 'to3d/r14-s14-kira/tools/web/view.html');
await page.waitForFunction(() => window.__ready, null, { timeout: 120000 });
await page.waitForTimeout(6000);
await page.selectOption('#motion', 'walk'); await page.click('#talk'); await page.click('#exprs button:nth-child(2)');
await page.waitForTimeout(6000);
await page.screenshot({ path: process.argv[2] });
await page.click('#close'); await page.waitForTimeout(5000);
await page.screenshot({ path: process.argv[2].replace('.png', '-close.png') });
console.log(errs.length ? 'errors:\n' + errs.join('\n') : 'no errors');
await b.close(); srv.close();
