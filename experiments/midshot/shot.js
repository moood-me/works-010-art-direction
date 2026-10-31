const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + process.cwd() + '/index.html');
  await p.waitForTimeout(800);
  const shots = process.argv.slice(2);
  for (const s of shots) {
    const [sc, t] = s.split(':');
    await p.evaluate(([sc, t]) => window.__midshot[sc].seek(+t), [sc, t]);
    await p.waitForTimeout(150);
    const el = await p.$('#' + sc);
    await el.screenshot({ path: `out-${sc}-${t}.png` });
  }
  console.log(errs.join('\n') || 'no errors');
  await b.close();
})();
