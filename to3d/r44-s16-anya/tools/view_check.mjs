// the viewer opened as a person opens it, pressed, and photographed:  node view_check.mjs out.png
import { createRequire } from 'node:module';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const { chromium } = createRequire(import.meta.url)('playwright');
const HERE = path.dirname(fileURLToPath(import.meta.url)), TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const srv = http.createServer((q, s) => { const f = path.join(HERE, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); } else { s.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' }); s.end(d); } }); }).listen(0);
const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1100, height: 760 } });
const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
await p.goto(`http://localhost:${srv.address().port}/web/view.html`); await p.waitForFunction(() => window.A, null, { timeout: 20000 });
await p.waitForTimeout(600); await p.screenshot({ path: process.argv[2] });
await p.click('text=идёт'); await p.click('text=радость'); await p.click('#talk'); await p.waitForTimeout(900);
const box = await p.locator('canvas').boundingBox(); await p.mouse.move(box.x + 200, box.y + 200); await p.mouse.down(); await p.mouse.move(box.x + 120, box.y + 200); await p.mouse.up();
await p.waitForTimeout(300); await p.screenshot({ path: process.argv[2].replace('.png', '-2.png') });
const fps = await p.evaluate(() => new Promise(r => { let n = 0; const t0 = performance.now(); const f = () => { n++; performance.now() - t0 < 1000 ? requestAnimationFrame(f) : r(n); }; requestAnimationFrame(f); }));
console.log('errors:', errs, 'frames a second:', fps);
await b.close(); srv.close();
