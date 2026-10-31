// node shot.js style [views...] -> v-<style>-<view>.png  (the repository root served on :8799)
const { chromium } = require('playwright');
(async () => {
  const [style, ...vs] = process.argv.slice(2); const views = vs.length ? vs : ['front', 'tq', 'side', 'back'];
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 520, height: 620 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(`http://localhost:8799/experiments/hair/index.html?s=${style}${process.env.Q || ""}`, { waitUntil: "commit", timeout: 0 });
  await p.waitForFunction(() => window.__ready || window.__err, null, { timeout: 300000 });
  const ms = await p.evaluate(() => window.__ms);
  for (const v of views) { await p.evaluate(v => window.view(v), v); await p.screenshot({ path: `v-${style}-${v}.png` }); }
  console.log(style, Math.round(ms) + 'ms', errs.join(' | ') || 'ok'); await b.close();
})();
