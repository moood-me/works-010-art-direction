// The picture check: the cases of cases.json marked `picture` drawn by render.html (headless Chromium, software
// WebGL, the repository's own three.js) — framed by the figure's bounds — and compared with the stored ones (pictures/).
// What the numbers can't say — is it still beautiful — is for eyes: look at the pictures it leaves.
//   node engine-full/check/pictures.mjs             compare; differences go to a folder it names (stored, new, diff)
//   node engine-full/check/pictures.mjs --update    store the new pictures (after looking at them)
//   node engine-full/check/pictures.mjs --only woman,man-dqs-sit100
//   node engine-full/check/pictures.mjs --jobs jobs.json outdir    pictures of any cases ([{name, char, clip, t, view, over?,
//                                                            place?, w?, h?, focus? (a joint), size? (m)}]) for looking at,
//                                                            nothing compared
// A picture differs when more than 0.02% of its pixels differ by more than 16 of 255 in a channel (software WebGL
// draws the same picture the same way; the tolerance covers antialiasing, not a change of form).
import { readFile, writeFile, mkdir, copyFile, mkdtemp } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { serve } from './serve.mjs';
import { browser } from './browser.mjs';
import { jobsOf, parseArgs } from './cases.mjs';

const HERE = fileURLToPath(new URL('./', import.meta.url)), STORE = join(HERE, 'pictures'), W = 400, H = 400, SHARE = 0.0002;

export async function shoot(jobs, outdir, log = () => {}) {
  await mkdir(outdir, { recursive: true });
  const srv = await serve(), b = await browser(), page = await b.newPage({ viewport: { width: W, height: H } });
  const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto(srv.url + 'engine-full/check/render.html');
  await page.waitForFunction(() => window.ready, null, { timeout: 120000 });
  for (const j of jobs) {
    const w = j.w || W, h = j.h || H;
    await page.setViewportSize({ width: w, height: h });
    await page.evaluate(([j, w, h]) => window.render(j, w, h), [j, w, h]);
    await (await page.$('#cv')).screenshot({ path: join(outdir, j.name + '.png') });
    log(j.name);
  }
  await b.close(); srv.close();
  if (errs.length) throw new Error('page errors: ' + errs.join(' | '));
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const args = parseArgs(process.argv);
  if (args.rest.includes('--jobs')) {
    const i = args.rest.indexOf('--jobs'), jobs = JSON.parse(await readFile(args.rest[i + 1], 'utf8'));
    if (!jobs.length) { console.log('no jobs'); process.exit(1); }
    await shoot(jobs, args.rest[i + 2], console.log);
    process.exit(0);
  }
  const cases = JSON.parse(await readFile(join(HERE, 'cases.json'), 'utf8'));
  const chars = JSON.parse(await readFile(join(HERE, '../characters/index.json'), 'utf8')).characters;
  const jobs = jobsOf(cases, chars, args.only).filter(j => j.picture);
  if (!jobs.length) { console.log('no pictures to check'); process.exit(1); }
  const out = await mkdtemp(join(tmpdir(), 'engine-pictures-'));
  await shoot(jobs, out);
  if (args.update) {
    await mkdir(STORE, { recursive: true });
    for (const j of jobs) await copyFile(join(out, j.name + '.png'), join(STORE, j.name + '.png'));
    console.log(`stored ${jobs.length} pictures in ${STORE}`);
    process.exit(0);
  }
  // compared in a page (no image library needed in node)
  const b = await browser(), page = await b.newPage();
  await page.setContent('<!doctype html><title>compare</title>');
  let bad = 0;
  for (const j of jobs) {
    const stored = join(STORE, j.name + '.png');
    if (!existsSync(stored)) { console.log(`${j.name}: no stored picture (run with --update after looking at it)`); bad++; continue; }
    const [a, n] = await Promise.all([readFile(stored), readFile(join(out, j.name + '.png'))]);
    const r = await page.evaluate(async ([a, n]) => {
      const img = async b64 => { const i = new Image(); i.src = 'data:image/png;base64,' + b64; await i.decode(); return i; };
      const [A, B] = await Promise.all([img(a), img(n)]);
      if (A.width !== B.width || A.height !== B.height) return { size: true };
      const c = document.createElement('canvas'); c.width = A.width; c.height = A.height; const g = c.getContext('2d');
      g.drawImage(A, 0, 0); const da = g.getImageData(0, 0, c.width, c.height).data;
      g.drawImage(B, 0, 0); const db = g.getImageData(0, 0, c.width, c.height).data;
      const diff = g.createImageData(c.width, c.height); let n2 = 0;
      for (let i = 0; i < da.length; i += 4) {
        const d = Math.max(Math.abs(da[i] - db[i]), Math.abs(da[i + 1] - db[i + 1]), Math.abs(da[i + 2] - db[i + 2]));
        const off = d > 16; if (off) n2++;
        diff.data[i] = off ? 255 : da[i] * 0.3; diff.data[i + 1] = off ? 0 : da[i + 1] * 0.3; diff.data[i + 2] = off ? 0 : da[i + 2] * 0.3; diff.data[i + 3] = 255;
      }
      g.putImageData(diff, 0, 0);
      return { share: n2 / (da.length / 4), diff: c.toDataURL('image/png').split(',')[1] };
    }, [a.toString('base64'), n.toString('base64')]);
    if (r.size || r.share > SHARE) {
      bad++;
      if (r.diff) await writeFile(join(out, j.name + '-diff.png'), Buffer.from(r.diff, 'base64'));
      await copyFile(stored, join(out, j.name + '-stored.png'));
      console.log(`${j.name}: differs (${r.size ? 'another size' : (r.share * 100).toFixed(2) + '% of pixels'})`);
    }
  }
  await b.close();
  console.log(bad ? `${bad} of ${jobs.length} pictures differ — see ${out}` : `all ${jobs.length} pictures as stored`);
  process.exit(bad ? 1 : 0);
}
