// Pictures of the engine's viewer: node engine/check/shots.mjs jobs.json outdir
// jobs: [{name, char, clip ("" — rest), t (frame), view: "front" | "side" | "back" | {yaw, pitch, dist}, w, h,
//         method?, clav?, seam?, corr?: {name: true}, joints?: bool, dist?: number, pitch?: number, focus?: joint name}]
// The camera looks at the figure at that moment (front/side: from where it faces then).
import { readFile, mkdir } from 'node:fs/promises';
import { serve } from './serve.mjs';
import { browser } from './browser.mjs';

export async function shoot(jobs, outdir, log = console.log) {
  await mkdir(outdir, { recursive: true });
  const srv = await serve(), b = await browser();
  const page = await b.newPage({ viewport: { width: 900, height: 900 } });
  const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto(srv.url + 'engine/viewer/index.html?paused&follow=1');
  await page.waitForFunction(() => window.__viewer, null, { timeout: 120000 });
  for (const j of jobs) {
    await page.setViewportSize({ width: j.w || 600, height: j.h || 800 });
    await page.evaluate(async j => {
      const V = window.__viewer, o = {};
      if (V.S.char !== j.char) o.char = j.char;
      for (const k of ['method', 'clav', 'seam']) if (j[k] !== undefined && V.S[k] !== j[k]) o[k] = j[k];
      const corr = j.corr || {}; if (JSON.stringify(corr) !== JSON.stringify(V.S.corr)) o.corr = corr;
      o.clip = j.clip ?? 'walk'; o.t = j.t || 0; o.playing = false; o.joints = !!j.joints;
      await V.set(o);
      const v = j.view || 'front', f = V.facing();
      const h = V.fig.body.measures.height;
      if (typeof v === 'string') { V.cam.yaw = f + { front: 0, side: Math.PI / 2, back: Math.PI, three: 0.6 }[v]; V.cam.pitch = j.pitch ?? 0.06; V.cam.dist = j.dist ?? Math.max(2.2, h * 2.9); }
      else Object.assign(V.cam, v);
      if (j.target) V.cam.target = j.target;
      if (j.focus) { const k = V.fig.body.skeleton.index[j.focus], P = V.fig.pose.P; V.cam.target = [P[k * 3], P[k * 3 + 1], P[k * 3 + 2]]; }
      V.render();
    }, j);
    const panel = j.panel ? null : await page.$('#vpPanel');
    if (panel) await panel.evaluate(p => p.style.visibility = 'hidden');
    await page.screenshot({ path: `${outdir}/${j.name}.png` });
    if (panel) await panel.evaluate(p => p.style.visibility = '');
    log(j.name);
  }
  await b.close(); srv.close();
  if (errs.length) throw new Error('page errors: ' + errs.join(' | '));
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const jobs = JSON.parse(await readFile(process.argv[2], 'utf8'));
  await shoot(jobs, process.argv[3]);
}
