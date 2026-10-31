const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 900 }, deviceScaleFactor: 1 });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error' || m.type()==='warning') errs.push(m.text()); });
  const t0 = Date.now();
  await p.goto('file://' + process.cwd() + '/index.html');
  await p.waitForFunction(() => window.__body, null, { timeout: 120000 });
  console.log('built in', Date.now() - t0, 'ms');
  for (const s of process.argv.slice(2)) {
    const [m, t, yaw, dist, bones, view, wind] = s.split(':');
    await p.evaluate(([m, t, yaw, dist, bones, view, wind]) => {
      const B = window.__body; B.seek(m, +t); B.cam.yaw = +yaw; if (dist) B.cam.dist = +dist;
      const bb = document.getElementById('bones'); if ((bb.getAttribute('aria-pressed') === 'true') !== (bones === '1')) bb.click();
      document.querySelector(`[data-v="${view || 'soft'}"]`).click();
      const w = document.getElementById('wind'); if ((w.getAttribute('aria-pressed') === 'true') !== (wind === '1')) w.click();
    }, [m, t, yaw, dist, bones, view, wind]);
    await p.waitForTimeout(2500);
    await (await p.$('#stage')).screenshot({ path: `o-${s.replace(/[:.]/g, '_')}.png` });
  }
  console.log(errs.slice(0, 8).join('\n') || 'no errors');
  await b.close();
})();
