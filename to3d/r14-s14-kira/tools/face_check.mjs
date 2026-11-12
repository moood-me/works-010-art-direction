// node face_check.mjs out.png — a picture of web/face-check.html (the face's pieces alone, five expressions)
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const { chromium } = createRequire(import.meta.url)('playwright');
const srv = await serve('/home/user/');
const b = await chromium.launch(); const page = await b.newPage({ viewport: { width: 2560, height: 512 } });
page.on('console', m => console.log(m.text())); page.on('pageerror', e => console.log(e.message));
await page.goto(srv.url + 'works-010-art-direction/to3d/r14-s14-kira/tools/web/face-check.html');
await page.waitForFunction(() => window.done);
await page.screenshot({ path: process.argv[2] });
await b.close(); srv.close();
