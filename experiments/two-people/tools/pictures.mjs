// Pictures of the page (headless Chromium, software WebGL): sheets of moments from several sides, close-ups, films.
//   node tools/pictures.mjs <jobs.json>
// a job: {out: "pics/<name>.png|.mp4", scene, corr?: true, kind: "sheet"|"still"|"film",
//         frames: [..] (sheet, still: one) | {from, to, step} (film), views: [{yaw, pitch, dist, target: [x,y,z] | "contact", label}],
//         size: [w, h] (a cell; a film's frame), labels?: true}
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { serve } from '../../../engine/check/serve.mjs';
import { browser } from '../../../engine/check/browser.mjs';

const jobs = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const HERE = new URL('../', import.meta.url).pathname;
const srv = await serve(), br = await browser();
const tmp = mkdtempSync(join(tmpdir(), 'two-'));
try {
  for (const job of jobs) {
    const [w, h] = job.size || [480, 560];
    const page = await br.newPage({ viewport: { width: w, height: h } });
    page.on('pageerror', e => console.error('page:', e.message));
    await page.goto(`${srv.url}experiments/two-people/index.html?bare&paused&s=${job.scene}`);
    await page.waitForFunction(() => window.__page?.S, null, { timeout: 120000 });
    const shot = async (t, v, file) => {
      await page.evaluate(([t, v, corr, mark]) => {
        const p = window.__page; p.P.playing = false; p.P.t = t; p.P.corr = corr; p.P.mark = !!mark;
        p.render();
        const S = p.S, c = S.def.contacts?.[0];
        let target = v.target;
        if (target === 'contact' && c) { const O = S.by[c.on], j = O.body.skeleton.index[c.joint]; const Q = O.fig.pose.Q, P = O.fig.pose.P, r = O.body.joints;
          // the contact point now (the page's own jointAt, inlined to keep the page's API small)
          const q = [Q[j * 4], Q[j * 4 + 1], Q[j * 4 + 2], Q[j * 4 + 3]], x = [c.point[0] - r[j * 3], c.point[1] - r[j * 3 + 1], c.point[2] - r[j * 3 + 2]];
          const [qx, qy, qz, qw] = q, tx = 2 * (qy * x[2] - qz * x[1]), ty = 2 * (qz * x[0] - qx * x[2]), tz = 2 * (qx * x[1] - qy * x[0]);
          target = [x[0] + qw * tx + qy * tz - qz * ty + P[j * 3], x[1] + qw * ty + qz * tx - qx * tz + P[j * 3 + 1], x[2] + qw * tz + qx * ty - qy * tx + P[j * 3 + 2]]; }
        if (target === 'mid') { const a = S.people[0].fig.pose.P, b = S.people[1].fig.pose.P; target = [(a[0] + b[0]) / 2, v.y ?? 0.95, (a[2] + b[2]) / 2]; }
        Object.assign(p.cam, { yaw: v.yaw, pitch: v.pitch, dist: v.dist, target });
        p.stage.look(p.cam.target, p.cam); p.stage.render();
      }, [t, v, job.corr !== false, job.mark]);
      await page.locator('#cv').screenshot({ path: file });
    };
    if (job.kind === 'film') {
      const { from, to, step } = job.frames; let n = 0;
      for (let t = from; t <= to; t += step) await shot(t, job.views[0], join(tmp, `f${String(n++).padStart(4, '0')}.png`));
      execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(30 / step), '-i', join(tmp, 'f%04d.png'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '30', '-preset', 'slow', '-movflags', '+faststart', join(HERE, job.out)]);
      execFileSync('sh', ['-c', `rm -f ${tmp}/f*.png`]);
    } else {
      const rows = [];
      for (const [vi, v] of job.views.entries()) {
        const cells = [];
        for (const [fi, t] of job.frames.entries()) {
          const f = join(tmp, `c${vi}_${fi}.png`); await shot(t, v, f);
          if (job.labels !== false) execFileSync('convert', [f, '-gravity', 'NorthWest', '-fill', '#26231f', '-pointsize', '15', '-annotate', '+8+6', `${(t / 30).toFixed(1)} с${v.label ? ' · ' + v.label : ''}`, f]);
          cells.push(f);
        }
        const row = join(tmp, `r${vi}.png`); execFileSync('convert', [...cells, '+append', row]); rows.push(row);
      }
      execFileSync('convert', [...rows, '-append', '-strip', join(HERE, job.out)]);
    }
    console.log('made', job.out);
    await page.close();
  }
} finally { await br.close(); srv.close(); rmSync(tmp, { recursive: true, force: true }); }
