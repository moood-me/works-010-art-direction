// The bench page measured in real Chrome on this machine's video card, 1920×1080: for each number of characters and
// each way, the page's own frames over some seconds.
//   node engine-gpu/check/bench.mjs [counts=1,2,4,6,9,12,16] [seconds=5] [pack=to3d/r45-s15-anya/data/anya.json]
// Prints a table: frames a second, the longest gap between frames, the processor's milliseconds a frame.
// Needs playwright (PLAYWRIGHT_FROM: a folder that has it) and Chrome.
import { readFile } from 'node:fs/promises';
import http from 'node:http';
import { join, extname, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire(process.env.PLAYWRIGHT_FROM || import.meta.url);
const { chromium } = require('playwright');

const REPO = fileURLToPath(new URL('../../', import.meta.url));
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json', '.bin': 'application/octet-stream' };
const server = http.createServer(async (req, res) => {
  const path = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
  try { const b = await readFile(join(REPO, path)); res.writeHead(200, { 'content-type': TYPES[extname(path)] || 'application/octet-stream', 'cache-control': 'no-store' }); res.end(b); }
  catch { res.writeHead(404); res.end(); }
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}/engine-gpu/bench/index.html`;
const counts = (process.argv[2] || '1,2,4,6,9,12,16').split(',').map(Number), seconds = Number(process.argv[3] || 5), pack = process.argv[4];

const browser = await chromium.launch({ channel: 'chrome', headless: false, args: ['--window-size=1940,1200', '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', e => console.error('page error:', e.message));
const rows = [];
for (const n of counts) for (const way of ['cpu', 'gpu']) {
  await page.goto(`${base}?n=${n}&way=${way}${pack ? '&pack=' + encodeURIComponent(pack) : ''}`);
  await page.waitForFunction(() => window.__ready, null, { timeout: 180000 });
  await page.waitForTimeout(1500);
  const r = await page.evaluate(s => window.B.measure(s), seconds);
  rows.push(r); console.log(JSON.stringify(r));
}
await browser.close(); server.close();
