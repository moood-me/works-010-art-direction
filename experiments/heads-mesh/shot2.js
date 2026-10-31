// node shot2.js name… → s-<name>.png: the reference, the head at the picture's angle, front, three-quarter, side
const { chromium } = require('playwright'); const { execSync } = require('child_process');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 560, height: 640 } }); p.on('pageerror', e => console.log(e.message)); p.on('console', m => console.log(m.text()));
  await p.goto('http://localhost:8786/view.html'); await p.waitForFunction(() => window.__ready, null, { timeout: 180000 });
  const wire = process.env.WIRE === '1';
  for (const n of process.argv.slice(2)) {
    const D = JSON.parse(require('fs').readFileSync(`out/${n}.json`)); const v = D.view;
    const Z = +(process.env.ZOOM || 1); const roll = D.roll || 0; const shots = [['r', v[0], v[1], roll], ['f', 0, 0.05], ['q', 0.65, 0.05], ['s', 1.5708, 0.05], ['b', -0.9, 0.3]];
    for (const [k, y, pi, ro] of shots) { await p.evaluate(async ([n, y, pi, w, z, ro]) => window.__show(n, y, pi, z, w, ro || 0), [n, y, pi, wire, Z, ro]); await (await p.$('#cv')).screenshot({ path: `o/${n}-${k}.png` }); }
    execSync(`python3 py/sheet.py ${n} ${D.ref} '${JSON.stringify(D.crop || 0)}' rfqsb s-${n}.png`);
  }
  await b.close();
})();
