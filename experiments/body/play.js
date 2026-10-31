const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 900 }, deviceScaleFactor: 1 });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + process.cwd() + '/index.html');
  await p.waitForFunction(() => window.__body, null, { timeout: 120000 });
  // a script: [button, seconds to wait, yaw, shot name]
  const steps = JSON.parse(process.argv[2]);
  for (const [btn, wait, yaw, name] of steps) {
    if (btn) await p.click(btn);
    if (yaw != null) await p.evaluate(y => { window.__body.cam.yaw = y; }, yaw);
    await p.waitForTimeout(wait * 1000);
    if (name) await (await p.$('#stage')).screenshot({ path: `p-${name}.png` });
  }
  const fps = await p.evaluate(() => new Promise(r => { let n = 0; const t0 = performance.now(); const f = () => { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(f); else r(n / 2); }; requestAnimationFrame(f); }));
  console.log('fps (software GL):', fps, errs.join('\n') || 'no errors');
  await b.close();
})();
