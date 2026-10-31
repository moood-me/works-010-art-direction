const { chromium } = require('playwright');
// node shot.js '[{"name":"x","q":"c=host&view=full"}]' [w h]
(async () => {
  const W = +(process.argv[3] || 600), H = +(process.argv[4] || 800);
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: W, height: H } }); const errs = []; p.on('pageerror', e => { errs.push(e.stack); }); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  for (const s of JSON.parse(process.argv[2])) {
    await p.goto('http://localhost:8779/index.html?' + s.q);
    await p.waitForFunction(() => window.__ready, null, { timeout: s.t || 100000 }).catch(e => errs.push(s.name + ': ' + e.message));
    await p.waitForTimeout(300);
    await p.screenshot({ path: `s-${s.name}.png` });
  }
  console.log(errs.join('\n') || 'ok'); await b.close();
})();
