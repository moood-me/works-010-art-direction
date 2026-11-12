// Pictures and films of the page (headless Chromium, software WebGL), and its numbers over every frame.
//   node tools/shots.cjs jobs.json        jobs: [{out, scene, t | frames: [a, b, step], view | cam, w, h, raw}]
//   a job with `frames` writes out-%03d.png (then ffmpeg makes the film); `measure: "<file>"` writes the numbers.
// The repository is served on a port of its own; one browser, closed at the end.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const REPO = path.resolve(__dirname, '../../../..');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.bin': 'application/octet-stream', '.png': 'image/png' };

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const server = http.createServer((req, res) => {
    const p = path.join(REPO, decodeURIComponent(new URL(req.url, 'http://x').pathname));
    fs.readFile(p, (e, b) => { if (e) { res.writeHead(404); res.end(); } else { res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(b); } });
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}/experiments/other-bodies/table.html`;
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  page.on('pageerror', e => console.error('page:', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
  let open = null;
  for (const j of jobs) {
    const w = j.w || 900, h = j.h || 700;
    await page.setViewportSize({ width: w, height: h });
    if (open !== j.scene) {
      await page.goto(`${base}?s=${j.scene}&paused`);
      await page.waitForFunction(() => window.__contacts, null, { timeout: 120000 });
      open = j.scene;
    }
    await page.evaluate(() => { document.getElementById('panel').style.display = 'none'; window.dispatchEvent(new Event('resize')); });
    await page.evaluate(([raw]) => window.__contacts.set({ correct: !raw, playing: false, marks: false }), [!!j.raw]);
    if (j.eval) { const r = await page.evaluate(j.eval); console.log(JSON.stringify(r)); continue; }
    if (j.measure) {
      const m = await page.evaluate(() => window.__contacts.measureAll(1));
      fs.writeFileSync(path.resolve(j.measure), JSON.stringify(m));
      console.log('measured', j.measure); continue;
    }
    const ts = j.frames ? Array.from({ length: Math.floor((j.frames[1] - j.frames[0]) / j.frames[2]) + 1 }, (_, k) => j.frames[0] + k * j.frames[2]) : [j.t];
    let k = 0;
    for (const t of ts) {
      await page.evaluate(([t, v, c]) => { const C = window.__contacts; C.S.t = t; C.render(); if (v) C.view(v); if (c) Object.assign(C.cam, c); C.render(); }, [t, j.view || null, j.cam || null]);
      const out = j.frames ? j.out.replace('%03d', String(k++).padStart(3, '0')) : j.out;
      await page.locator('#cv').screenshot({ path: out });
    }
    console.log('wrote', j.out, ts.length);
  }
  await browser.close(); server.close();
})().catch(e => { console.error(e); process.exit(1); });
