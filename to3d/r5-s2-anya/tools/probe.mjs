// Where the pelvis is over a clip: node probe.mjs pack clip
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [pack, clip] = process.argv.slice(2);
const srv = await serve('/home/user/');
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 200, height: 200 } });
await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', r => r.fulfill({ path: '/home/user/cache/n3-cloth/node_modules/three/build/three.module.js', contentType: 'text/javascript' }));
await page.goto(srv.url + 'works-010-art-direction/to3d/r5-s2-anya/tools/web/view.html?pack=' + encodeURIComponent(pack));
await page.waitForFunction(() => window.__ready, null, { timeout: 300000 });
const r = await page.evaluate(async c => { await window.A.set({ clip: c, t: 0 }); const n = window.A.frames(); const out = [];
  for (let t = 0; t < n; t += 10) { await window.A.set({ t }); out.push([t, ...window.A.hips().map(x => +x.toFixed(3))]); } return out; }, clip);
console.log(JSON.stringify(r)); await b.close(); srv.close();
