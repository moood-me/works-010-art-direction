// node tools-demo/n6-toon/tools/shot.mjs jobs.json outdir
// jobs: [{ name, src: "experiments/…/index.html", q: "the page's own parameters", looks: ["ours", "hard", …], w, h }]
//       or { name, engine: { char, clip, t, view, dist, pitch, focus }, looks, w, h } — the engine's viewer
// → outdir/<name>-<look>.png
import { readFile, mkdir } from 'node:fs/promises';
import { serve } from '../../../engine/check/serve.mjs';
import { browser } from '../../../engine/check/browser.mjs';

const jobs = JSON.parse(await readFile(process.argv[2], 'utf8')), out = process.argv[3];
await mkdir(out, { recursive: true });
const srv = await serve(), b = await browser();
for (const j of jobs) {
  const page = await b.newPage({ viewport: { width: j.w || 600, height: j.h || 800 } });
  const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  if (j.engine) {
    await page.goto(srv.url + 'engine/viewer/index.html?paused&follow=1');
    await page.waitForFunction(() => window.__viewer, null, { timeout: 180000 });
    await page.evaluate(async j => {
      const V = window.__viewer, e = j.engine;
      await V.set({ char: e.char, clip: e.clip ?? '', t: e.t || 0, playing: false, joints: false });
      const f = V.facing(), h = V.fig.body.measures.height;
      V.cam.yaw = f + ({ front: 0, side: Math.PI / 2, three: 0.6 }[e.view || 'front']); V.cam.pitch = e.pitch ?? 0.06; V.cam.dist = e.dist ?? Math.max(2.2, h * 2.9);
      if (e.focus) { const k = V.fig.body.skeleton.index[e.focus], P = V.fig.pose.P; V.cam.target = [P[k * 3], P[k * 3 + 1], P[k * 3 + 2]]; }
      V.render();
      const { look } = await import('/tools-demo/n6-toon/tools/mtoon.js');
      window.__look = (name, over) => { look(V.stage.scene, name, over); V.render(); };
      document.getElementById('vpPanel').style.visibility = 'hidden';
    }, j);
  } else {
    await page.goto(srv.url + 'tools-demo/n6-toon/tools/run.html?src=' + j.src + '&look=ours&' + (j.q || ''));
    await page.waitForFunction(() => window.__ready, null, { timeout: 240000 });
  }
  for (const l of j.looks) {
    await page.evaluate(([l, over]) => window.__look(l, over), [l, j.over || {}]);
    await page.waitForTimeout(200);
    await page.screenshot({ path: `${out}/${j.name}-${l}.png` });
    console.log(j.name, l);
  }
  if (errs.length) console.log('ERRORS', j.name, errs.join(' | '));
  await page.close();
}
await b.close(); srv.close();
