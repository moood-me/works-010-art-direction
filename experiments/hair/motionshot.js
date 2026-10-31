// Pictures of hair in motion: node motionshot.js jobs.json outdir/   (the repository root served on $PORT, 8799 by default)
// jobs: [{ style, who?, motion, wind?, turns?, frames: [f…] or every: k with upto: n, views: { name: {yaw, pitch, dist?, view} } }]
// Each job: the hairstyle loaded on the body, the motion run, and at each frame asked a picture from each view:
// <outdir>/<style>-<motion>[-w<wind>][-<turns>]-<view>-<frame>.png
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [jobsFile, out] = process.argv.slice(2), jobs = JSON.parse(fs.readFileSync(jobsFile, 'utf8')), port = process.env.PORT || 8799;
  const W = +(process.env.W || 560), H = +(process.env.H || 640);
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: W, height: H } }); const errs = [];
  p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(`http://localhost:${port}/experiments/hair/index.html?live&shots&w=${W}&h=${H}`, { waitUntil: 'commit', timeout: 0 });
  await p.waitForFunction(() => window.__ready || window.__err, null, { timeout: 600000 });
  for (const j of jobs) {
    const t0 = Date.now();
    await p.evaluate(j => window.__hair.load(j), { style: j.style, who: j.who });
    await p.evaluate(j => window.__hair.start(j), j);
    if (j.noink) await p.evaluate(w => window.__hair.ink(false, w === true ? undefined : w), j.noink);
    const frames = j.frames || Array.from({ length: Math.floor(j.upto / j.every) + 1 }, (_, i) => i * j.every);
    let at = 0, worst = { vmax: 0, bad: 0 };
    const tag = `${j.style}-${j.motion}${j.wind ? '-w' + j.wind : ''}${j.turns && j.turns !== 'none' ? '-' + j.turns : ''}${j.who ? '-' + j.who : ''}${j.rigid ? '-rigid' : ''}`;
    for (const f of frames) {
      await p.evaluate(n => window.__hair.run(n), f - at); at = f;
      const s = await p.evaluate(() => window.__hair.stats()); worst = { vmax: Math.max(worst.vmax, s.vmax), bad: worst.bad + s.bad };
      for (const [name, v] of Object.entries(j.views)) {
        await p.evaluate(v => window.__hair.look(v), v);
        await p.screenshot({ path: `${out}/${tag}-${name}-${String(f).padStart(3, '0')}.png` });
      }
    }
    console.log(tag, ((Date.now() - t0) / 1000).toFixed(1) + 's', 'vmax', worst.vmax.toFixed(2), 'bad', worst.bad, errs.splice(0).join(' | ') || 'ok');
  }
  await b.close();
})();
