// Shoots our current characters (П1 indie page, П2 toon page) in front, three-quarter and side views.
// node shoot_ours.cjs <outdir>   (the repository served at http://localhost:8791)
const { chromium } = require('playwright');
const out = process.argv[2];
const VIEWS = { front: 0, q34: 0.75, side: Math.PI / 2 };
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const errs = [];
  // П1: one hero standing, the other poses of the 'one' row hidden; the figure turned as by dragging on the page
  {
    const p = await b.newPage({ viewport: { width: 900, height: 1000 } }); p.on('pageerror', e => errs.push(e.message));
    await p.goto('http://localhost:8791/experiments/indie/index.html', { timeout: 120000 });
    await p.waitForFunction(() => window.__ih, null, { timeout: 400000 });
    for (const hero of (process.argv[3] || 'bear').split(',')) for (const [v, yaw] of Object.entries(VIEWS)) {
      await p.evaluate(([hero, yaw]) => {
        const I = window.__ih; I.state.mode = 'one'; I.state.hero = hero; I.state.view = 'style'; I.layout();
        const pl = I.placed(); pl.forEach((x, i) => { x.root.visible = i === 0; if (x.tagEl) x.tagEl.style.display = 'none'; });
        pl[0].root.position.set(0, 0, 0); pl[0].root.rotation.y = yaw;
        I.camera.position.set(0, 0.45, 3.6); I.camera.lookAt(0, 0.33, 0); I.camera.fov = 18; I.camera.aspect = 1; I.camera.updateProjectionMatrix(); I.render();
      }, [hero, yaw]);
      await p.waitForTimeout(200);
      const bb = await (await p.$('#stage')).boundingBox();
      const s = Math.min(bb.width, bb.height);
      await p.screenshot({ path: `${out}/our-${hero}-${v}.png`, clip: { x: bb.x + (bb.width - s) / 2, y: bb.y + (bb.height - s) / 2, width: s, height: s } });
    }
    await p.close();
  }
  // П2: toon page v2, pose 'stand', yaw by the page's own parameter
  {
    const p = await b.newPage({ viewport: { width: 700, height: 800 } }); p.on('pageerror', e => errs.push(e.message));
    for (const c of (process.argv[4] || 'cat').split(',')) for (const [v, yaw] of Object.entries(VIEWS)) {
      await p.goto(`http://localhost:8791/experiments/toon/index.html?c=${c}&v=2&pose=stand&yaw=${yaw}`);
      await p.waitForFunction(() => window.__ready, null, { timeout: 200000 }).catch(e => errs.push(c + ': ' + e.message));
      await p.waitForTimeout(300);
      await p.screenshot({ path: `${out}/our-${c}-${v}.png` });
    }
  }
  console.log(errs.join('\n') || 'ok'); await b.close();
})();
