// Renders Monster Mash meshes with view.html in our pages' look, in the same views as shoot_ours.cjs.
// node shoot_mm.cjs '<json list of {name, dir, preset, w, h, k, u0, vFloor, frames?}>' <outdir>
// (the work folder, with view.html in it, served at http://localhost:8792)
const { chromium } = require('playwright');
const VIEWS = { front: 0, q34: 0.75, side: Math.PI / 2 };
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const errs = [], out = process.argv[3];
  for (const s of JSON.parse(process.argv[2])) {
    const p = await b.newPage({ viewport: { width: s.w, height: s.h } }); p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto(`http://localhost:8792/view.html?preset=${s.preset}&w=${s.w}&h=${s.h}`);
    await p.waitForFunction(() => window.__ready);
    await p.evaluate(s => window.show({ dir: s.dir, k: s.k, u0: s.u0, vFloor: s.vFloor, yaw: 0 }), s);
    if (s.frames) {
      for (let f = 0; f < s.frames; f++) {
        await p.evaluate(([f, yaw]) => { window.__yaw = yaw; return window.frame('f' + String(f).padStart(4, '0') + '.obj').then(() => window.setYaw(yaw)); }, [f, s.yaw ?? 0]);
        await p.screenshot({ path: `${out}/${s.name}-${String(f).padStart(4, '0')}.png` });
      }
    } else for (const [v, yaw] of Object.entries(s.views ? Object.fromEntries(Object.entries(VIEWS).filter(([k]) => s.views.includes(k))) : VIEWS)) {
      await p.evaluate(y => window.setYaw(y), yaw);
      await p.screenshot({ path: `${out}/${s.name}-${v}.png` });
    }
    await p.close();
  }
  console.log(errs.join('\n') || 'ok'); await b.close();
})();
