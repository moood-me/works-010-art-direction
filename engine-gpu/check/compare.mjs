// A page as it was against its fast variant, in real Chrome on this machine's video card, at 1920×1080.
//   node engine-gpu/check/compare.mjs <jobs.json> <outdir>
// jobs: { old: "to3d/…/view.html?pack=…", new: "to3d/…/fast.html?pack=…", shots: [{ name, set: {…window.A.set options} }],
//         speed: { set: {…}, frames: 300, step: 0.5 } }
// Both pages must give window.__ready and window.A with set(o) and render() (the Р pages do).
// For each shot: <name>-old.png, <name>-new.png, <name>-diff.png (where they differ, white) and how many pixels differ
// by more than 24 of 255 in a channel. For speed: milliseconds a frame of A.set (the processor's work) and of
// A.render with the video card's work waited for, over the motion.
// Needs playwright (npm i playwright, or NODE_PATH to one) and Chrome.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import http from 'node:http';
import { join, extname, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire(process.env.PLAYWRIGHT_FROM || import.meta.url);
const { chromium } = require('playwright');

const REPO = fileURLToPath(new URL('../../', import.meta.url));
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.bin': 'application/octet-stream' };
const server = http.createServer(async (req, res) => {
  const path = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
  try { const b = await readFile(join(REPO, path)); res.writeHead(200, { 'content-type': TYPES[extname(path)] || 'application/octet-stream', 'cache-control': 'no-store' }); res.end(b); }
  catch { res.writeHead(404); res.end(); }
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}/`;

const jobs = JSON.parse(await readFile(process.argv[2], 'utf8')), out = process.argv[3];
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ channel: 'chrome', headless: false, args: ['--window-size=1940,1200', '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows'] });
const open = async url => {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => console.error('page error:', url, e.message));
  page.on('console', m => { if (m.type() === 'error' && !/404/.test(m.text())) console.error('page:', url, m.text().slice(0, 300)); });
  await page.goto(base + url); await page.waitForFunction(() => window.__ready, null, { timeout: 120000 });
  return page;
};
const pages = { old: await open(jobs.old), new: await open(jobs.new) };
const report = { gpu: await pages.new.evaluate(() => { const gl = document.createElement('canvas').getContext('webgl2'), e = gl.getExtension('WEBGL_debug_renderer_info'); return e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : '?'; }), shots: [], speed: null };

for (const s of jobs.shots || []) {
  const url = {};
  for (const k of ['old', 'new']) {
    await pages[k].bringToFront();
    url[k] = await pages[k].evaluate(async o => { await window.A.set(o); window.A.render(); return document.querySelector('canvas').toDataURL('image/png'); }, s.set || {});
    await writeFile(`${out}/${s.name}-${k}.png`, Buffer.from(url[k].split(',')[1], 'base64'));
  }
  const d = await pages.new.evaluate(async ({ a, b }) => {
    const img = u => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = u; });
    const [A, B] = [await img(a), await img(b)], w = A.width, h = A.height;
    const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(A, 0, 0); const pa = g.getImageData(0, 0, w, h); g.drawImage(B, 0, 0); const pb = g.getImageData(0, 0, w, h);
    let n = 0; const o = g.createImageData(w, h);
    for (let i = 0; i < pa.data.length; i += 4) {
      const m = Math.max(Math.abs(pa.data[i] - pb.data[i]), Math.abs(pa.data[i + 1] - pb.data[i + 1]), Math.abs(pa.data[i + 2] - pb.data[i + 2]));
      const v = m > 24 ? 255 : 0; if (v) n++; o.data[i] = o.data[i + 1] = o.data[i + 2] = v; o.data[i + 3] = 255;
    }
    g.putImageData(o, 0, 0);
    return { differ: n, of: w * h, png: c.toDataURL('image/png') };
  }, { a: url.old, b: url.new });
  await writeFile(`${out}/${s.name}-diff.png`, Buffer.from(d.png.split(',')[1], 'base64'));
  report.shots.push({ name: s.name, differ: d.differ, share: +(d.differ / d.of * 100).toFixed(3) + '%' });
  console.log(s.name, d.differ);
}

if (jobs.speed) {
  report.speed = {};
  for (const k of ['old', 'new']) {
    await pages[k].bringToFront();
    report.speed[k] = await pages[k].evaluate(async ({ set, frames, step }) => {
      const A = window.A, cv = document.querySelector('canvas'), gl = cv.getContext('webgl2'), px = new Uint8Array(4);
      await A.set(set); const n = A.frames() || 1, cpu = [], draw = [];
      for (let i = 0; i < frames + 20; i++) {
        const a = performance.now(); await A.set({ t: (i * step) % Math.max(1, n - 1), time: i / 60 });
        const b = performance.now(); A.render(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
        const c = performance.now(); if (i >= 20) { cpu.push(b - a); draw.push(c - b); }
      }
      const st = v => { const s = [...v].sort((x, y) => x - y); return { mean: +(s.reduce((x, y) => x + y, 0) / s.length).toFixed(2), p95: +s[Math.floor(s.length * 0.95)].toFixed(2), worst: +s[s.length - 1].toFixed(2) }; };
      return { processorMs: st(cpu), drawMs: st(draw) };
    }, { frames: 300, step: 0.5, ...jobs.speed });
  }
}
await writeFile(`${out}/report.json`, JSON.stringify(report, null, 1));
console.log(JSON.stringify(report, null, 1));
await browser.close(); server.close();
