// Pictures of the page: node shot.js jobs.json out/ — each job bakes an outfit through a motion and shoots the frames
// asked for from the views asked for (out/<name>-<view>-<frame>.png; a view may ask for frames of its own). The page is served from the repository's root on
// PORT (8790 by default: python3 -m http.server 8790).
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [jobsPath, out] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: Number(process.env.W || 900), height: Number(process.env.H || 900) } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(`http://localhost:${process.env.PORT || 8790}/experiments/cloth/index.html?shots`);
  await p.waitForFunction(() => window.__cloth, null, { timeout: 120000 });
  await p.addStyleTag({ content: 'header, .controls, .notes, .hint { display: none !important } main { padding: 0 !important; max-width: none !important } .stage { aspect-ratio: auto !important; height: 100vh !important; border-radius: 0 !important }' });
  for (const job of JSON.parse(fs.readFileSync(jobsPath))) {
    const t0 = Date.now();
    const n = await p.evaluate(o => window.__cloth.bake(o), job);
    for (const v of job.views) for (const f of v.frames || job.frames) {
      await p.evaluate(([f, v]) => window.__cloth.view(Math.min(f, 100000), v), [f, v]);
      await (await p.$('#cv')).screenshot({ path: `${out}/${job.name}-${v.name}-${String(f).padStart(3, '0')}.png` });
    }
    console.log(job.name, n, 'frames', ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  console.log(errs.join('\n') || 'no errors'); await b.close();
})();
