const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const jobs = JSON.parse(process.argv[2]);
  for (const j of jobs) {
    const p = await b.newPage({ viewport: { width: j.w || 1600, height: (j.h || 700) + 28 } });
    p.on('pageerror', e => console.log('ERR', e.message));
    const q = new URLSearchParams({ set: j.set.join(','), labels: (j.labels || j.set).join('|'), yaw: j.yaw ?? 0.35, focus: j.focus || 'full', gap: j.gap || '', w: j.w || 1600, h: j.h || 700 });
    await p.goto('http://localhost:8774/index.html?' + q);
    await p.waitForFunction(() => window.__done, null, { timeout: 120000 });
    await p.screenshot({ path: j.out });
    await p.close();
  }
  await b.close();
})();
