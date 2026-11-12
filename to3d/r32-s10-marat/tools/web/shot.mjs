// Pictures of the viewer in headless Chromium (engine/check's browser and server), to look at it.
// usage: node shot.mjs OUT_PREFIX [motion] [seconds…]
import { browser } from '../../../../engine/check/browser.mjs';
import { serve } from '../../../../engine/check/serve.mjs';

const [out, motion = 'walk', ...secs] = process.argv.slice(2);
const srv = await serve();
const b = await browser();
const page = await b.newPage({ viewport: { width: 640, height: 560 } });
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('console:', m.text()); });
page.on('pageerror', e => console.log('pageerror:', e.message));
// three.js comes from jsDelivr in the page; where the network doesn't let it through, a local copy stands in:
// THREE_DIR=…/node_modules/three (npm install three@0.160.0)
if (process.env.THREE_DIR) {
  const { readFile } = await import('node:fs/promises');
  await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', async route => {
    const rel = new URL(route.request().url()).pathname.replace('/npm/three@0.160.0/', '');
    route.fulfill({ body: await readFile(process.env.THREE_DIR + '/' + rel), contentType: 'text/javascript' });
  });
}
await page.goto(srv.url + 'to3d/r32-s10-marat/tools/web/view.html');
await page.waitForSelector('#msg', { state: 'detached', timeout: 120000 });
await page.selectOption('#motion', motion);
await page.click('#play');
for (const s of (secs.length ? secs : ['0.5'])) {
  await page.evaluate(v => { const el = document.getElementById('time'); el.value = v; el.dispatchEvent(new Event('input')); }, String(s));
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${out}-${s}.png`, timeout: 120000 });
}
await b.close(); srv.close();
