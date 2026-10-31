// node shot.js '[{"name":"marco","mode":"head","yaw":0,"shape":{},"out":"x.png"}]'
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('http://localhost:8781/index.html');
  await p.waitForFunction(() => window.__ready, null, { timeout: 180000 }).catch(e => { console.log(errs.join('\n')); throw e; });
  for (const s of JSON.parse(process.argv[2])) {
    await p.evaluate(async s => { await window.__show(s.name, s.mode, s.yaw ?? 0, s.shape || {}, s.pitch ?? 0.04); }, s);
    await p.waitForTimeout(150);
    await (await p.$('#stage')).screenshot({ path: s.out });
  }
  console.log(errs.join('\n') || 'ok'); await b.close();
})();
