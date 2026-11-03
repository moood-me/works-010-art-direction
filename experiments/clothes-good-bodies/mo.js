// items: {name, motion, mode:'tailor'|'ride'|'phys', from, to, shots:[...], camera...} → q-<name>-<frame>.png
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8776/index.html');
  await p.waitForFunction(() => window.__sh, null, { timeout: 300000 });
  for (const s of JSON.parse(require('fs').readFileSync(process.argv[2]))) {
    const t0 = Date.now();
    for (let f = s.from ?? 0; f <= (s.to ?? 0); f++) {
      await p.evaluate(async ([s, f]) => { window.__phys = s.mode === 'phys'; window.__ride = s.mode === 'ride'; if (f === (s.from ?? 0)) { window.__physReset = true; window.__physState = {}; window.__designRest = {}; }
        await window.__setMotion(s.motion, f); if (s.lookDef) window.__sh.LOOKS[s.look] = s.lookDef; const S = window.__sh.state; S.mode = 'one'; S.who = s.who || 'woman'; S.gw = s.gw || {}; S.cw = s.cw || {}; S.over = s.over || {}; S.look = s.look; window.__sh.mark(); await window.__sh.refresh(); const c = window.__sh.cam; c.yaw = s.yaw ?? 0.5; if (s.dist) c.dist = s.dist; if (s.ty) c.target.y = s.ty; if (s.pitch != null) c.pitch = s.pitch; }, [s, f]);
      if (s.shots.includes(f)) { await p.waitForTimeout(300); await (await p.$('#stage')).screenshot({ path: `q-${s.name}-${String(f).padStart(3, '0')}.png`, timeout: 180000 }); }
    }
    console.log(s.name, ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  console.log(errs.join('\n') || 'no errors'); await b.close();
})();
