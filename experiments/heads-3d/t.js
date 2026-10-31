const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  await p.goto('http://localhost:8781/index.html'); await p.waitForFunction(() => window.__ready, null, { timeout: 180000 });
  for (const [k, v] of [['a', false], ['b', true]]) { await p.evaluate(async v => { window.__noLo = v; await window.__show('gwen', 'head', 0); }, v); await (await p.$('#stage')).screenshot({ path: 'tl-' + k + '.png' }); }
  await b.close();
})();
