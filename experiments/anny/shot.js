const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('http://localhost:8765/index.html');
  await p.waitForFunction(() => window.__anny, null, { timeout: 60000 });
  for (const s of JSON.parse(process.argv[2])) {
    for (const c of s.click || []) { await p.click(c); await p.waitForTimeout(600); }
    if (s.yaw != null) await p.evaluate(y => window.__anny.cam.yaw = y, s.yaw);
    await p.waitForTimeout(1500);
    await (await p.$('#stage')).screenshot({ path: `s-${s.name}.png` });
  }
  console.log(errs.join('\n') || 'no errors'); await b.close();
})();
