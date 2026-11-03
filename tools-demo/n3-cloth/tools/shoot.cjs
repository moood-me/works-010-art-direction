// node shoot.cjs <run url> <src> <tag> <out dir> <yaw> <pitch> <dist> [from] [to] [step] — frames of a run as PNGs.
// No server: the page's requests to http://local/repo/… are answered from the repository on disk and
// http://local/cache/… from /home/user/cache; three.js comes from jsDelivr as on the page.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [run, src, tag, out, yaw, pitch, dist, from = 0, to = 1e9, step = 1] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: +(process.env.W || 480), height: +(process.env.H || 540) } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  const roots = { repo: path.resolve(__dirname, '../../..'), cache: '/home/user/cache' };
  const types = { html: 'text/html', js: 'text/javascript', json: 'application/json' };
  await p.route('http://local/**', r => {
    const [, root, ...rest] = new URL(r.request().url()).pathname.split('/'), f = roots[root] + '/' + rest.join('/');
    return fs.existsSync(f) ? r.fulfill({ path: f, contentType: types[f.split('.').pop()] || 'application/octet-stream' }) : r.fulfill({ status: 404 });
  });
  await p.goto('http://local/repo/tools-demo/n3-cloth/tools/view.html');
  await p.waitForFunction(() => window.__ready, null, { timeout: 120000 });
  const n = await p.evaluate(([r, s, t]) => window.__v.load(r, s, t), [run, src, tag]);
  const v = { yaw: +yaw, pitch: +pitch, dist: +dist };
  // the camera eases from frame 0 on, as on the page, so every frame is drawn (only those asked for are kept)
  for (let f = 0; f < Math.min(n, +to + 1); f++) {
    await p.evaluate(([f, v]) => window.__v.show(f, v), [f, f === 0 ? { ...v, snap: true } : v]);
    if (f >= +from && (f - from) % step === 0) await p.screenshot({ path: `${out}/${String(f).padStart(4, '0')}.png` });
  }
  console.log(n, 'frames', errs.join('\n') || 'no errors'); await b.close();
})();
