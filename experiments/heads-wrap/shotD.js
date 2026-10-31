// node shot.js '[["anime","tq",""],...]'  →  s-<c>-<view>[-expr].png
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const list = JSON.parse(process.argv[2]);
  for (const [c, view, expr] of list) {
    const p = await b.newPage({ viewport: { width: 800, height: 800 } }); const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto(`http://localhost:8783/index.html?c=${c}&view=${view}&expr=${expr || ""}${process.env.Q || ""}`);
    try { await p.waitForFunction(() => window.__ready, null, { timeout: 120000 }); } catch (e) { console.log(c, view, 'timeout', errs.join(' | ')); await p.close(); continue; }
    await p.waitForTimeout(300);
    await p.screenshot({ path: `designed/s-${c}-${view}${expr ? '-' + expr : ''}.png` });
    if (errs.length) console.log(c, view, errs.join(' | '));
    await p.close();
  }
  await b.close();
})();
