const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8768/index.html');
  await p.waitForFunction(() => window.__sh, null, { timeout: 180000 });
  console.log(JSON.stringify(await p.evaluate(() => window.__prof("woman","torso")).catch(e => e.message)));
  console.log(errs.join('\n')); await b.close();
})();
