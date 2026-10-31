const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8775/index.html');
  await p.waitForFunction(() => window.__sh, null, { timeout: 180000 });
  for (const s of JSON.parse(require('fs').readFileSync(process.argv[2]))) {
    const t0 = Date.now();
    await p.evaluate(async s => { const S = window.__sh.state; S.mode = s.mode || 'one'; S.who = s.who || 'woman'; S.gw = s.gw || {}; S.cw = s.cw || {}; S.over = s.over || {}; S.subdiv = !!s.subdiv; window.__sh.mark(); await window.__sh.refresh(); const c = window.__sh.cam; c.yaw = s.yaw ?? 0.4; if (s.dist) c.dist = s.dist; if (s.ty) c.target.y = s.ty; if (s.tx != null) c.target.x = s.tx; if (s.pitch != null) c.pitch = s.pitch; }, s);
    await p.waitForTimeout(700);
    await (await p.$('#stage')).screenshot({ path: `q-${s.name}.png` });
    console.log(s.name, Date.now() - t0, 'ms');
  }
  console.log(errs.join('\n') || 'no errors'); await b.close();
})();
