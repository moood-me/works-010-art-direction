const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs=[]; p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8775/index.html');
  await p.waitForFunction(() => window.__sh, null, { timeout: 180000 });
  for (const s of JSON.parse(process.argv[2])) {
    await p.evaluate(async s => { window.__K = s.K; window.__R = s.R; window.__stage = s.stage; const S = window.__sh.state; S.mode = 'one'; S.who = s.who || 'woman'; S.gw = s.gw; S.cw = s.cw || {}; S.over = s.over || {}; window.__sh.mark(); await window.__sh.refresh(); const c = window.__sh.cam; c.yaw = s.yaw ?? 0.3; c.dist = s.dist ?? 1.4; c.target.y = s.ty ?? 1.0; }, s);
    await p.waitForTimeout(900);
    await (await p.$('#stage')).screenshot({ path: `q-${s.name}.png` });
  }
  console.log(errs.join('\n') || 'ok'); await b.close();
})();
