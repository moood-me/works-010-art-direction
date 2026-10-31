const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('http://localhost:8775/index.html');
  await p.waitForFunction(() => window.__sh, null, { timeout: 180000 }).catch(e => errs.push('timeout'));
  console.log(errs.join('\n') || 'ok'); await b.close();
})();
