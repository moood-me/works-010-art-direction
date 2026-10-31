const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1600, height: 1100 } }); const errs = []; p.on('pageerror', e => errs.push(e.message)); 
  await p.goto('http://localhost:8777/index.html', { timeout: 120000 });
  await p.waitForFunction(() => window.__ih, null, { timeout: 400000 });
  for (const s of JSON.parse(process.argv[2])) {
    await p.evaluate(s => { const I = window.__ih; Object.assign(I.state, s.state); I.layout(); if (s.cam) { I.camera.position.set(...s.cam.pos); I.camera.lookAt(...s.cam.at); if (s.cam.fov) { I.camera.fov = s.cam.fov; I.camera.updateProjectionMatrix(); } } }, s);
    await p.evaluate(() => window.__ih.render()); const bb = await (await p.$('#stage')).boundingBox();
    await p.screenshot({ path: `i-${s.name}.png`, clip: bb, timeout: 120000 });
  }
  console.log(errs.join('\n') || 'ok'); await b.close();
})();
