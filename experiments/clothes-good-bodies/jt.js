const { chromium } = require('playwright');
(async () => { const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage(); await p.goto('http://localhost:8776/index.html'); await p.waitForFunction(() => window.__sh, null, { timeout: 300000 });
  const r = await p.evaluate(async () => { const A = await window.__sh.dbg.analyse('woman'); return A.J.map(v => [v.x, v.y, v.z]); });
  require('fs').writeFileSync('mot/restJ-woman.json', JSON.stringify(r)); await b.close(); })();
