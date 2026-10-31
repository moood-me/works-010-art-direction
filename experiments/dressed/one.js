const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8772/index.html');
  await p.waitForFunction(() => window.__sh, null, { timeout: 180000 });
  for (const s of JSON.parse(process.argv[2])) {
    await p.evaluate(async s => { if (s.lookDef) window.__sh.LOOKS[s.look] = s.lookDef; const S = window.__sh.state; S.mode = s.mode || 'one'; S.who = s.who || 'woman'; S.gw = s.gw || {}; S.cw = s.cw || {}; S.over = s.over || {}; S.look = s.look; S.face = s.face; S.hair = s.hair; window.__faceIt = s.faceIt; window.__sh.mark(); await window.__sh.refresh(); window.__sh.cam.yaw = s.yaw ?? 0.5; if (s.dist) window.__sh.cam.dist = s.dist; if (s.ty) window.__sh.cam.target.y = s.ty; if (s.head) { let my = -9; window.__sh.cam.target.y = window.__eyeY - window.__minY + s.head * window.__spread / 0.065; window.__sh.cam.dist = s.dist * window.__spread / 0.065; window.__faceIt = s.faceIt; } if (s.tx != null) window.__sh.cam.target.x = s.tx; if (s.pitch != null) window.__sh.cam.pitch = s.pitch; }, s);
    await p.waitForTimeout(1200);
    await (await p.$('#stage')).screenshot({ path: `q-${s.name}.png` });
  }
  console.log(errs.join('\n') || 'no errors'); await b.close();
})();
