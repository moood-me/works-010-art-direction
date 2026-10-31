const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 900 }, deviceScaleFactor: 1 });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + process.cwd() + '/index.html');
  await p.waitForFunction(() => window.__body, null, { timeout: 120000 });
  await p.evaluate(() => { window.__hold = true; });
  for (const [btn, sec, yaw, name] of JSON.parse(process.argv[2])) {
    if (btn) await p.click(btn);
    await p.evaluate(([sec, yaw]) => { if (yaw != null) window.__body.cam.yaw = yaw; window.__body.advance(sec); }, [sec, yaw]);
    if (name) await (await p.$('#stage')).screenshot({ path: `a-${name}.png` });
  }
  console.log(errs.join('\n') || 'no errors');
  await b.close();
})();
