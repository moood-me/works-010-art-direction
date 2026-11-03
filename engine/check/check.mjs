// The picture check: every character preset rendered in a few fixed moments and compared with its stored pictures
// (check/pictures/<character>-<shot>.png), so improving the engine never silently changes a character.
//   node engine/check/check.mjs            compare; differences go to a folder it names, with the stored, new and diff
//   node engine/check/check.mjs --update   store the new pictures (after looking at them: a change meant)
//   node engine/check/check.mjs --only woman,man
// A picture differs when more than 0.05% of its pixels differ by more than 16 of 255 in a channel (software WebGL
// draws the same picture the same way; the tolerance covers antialiasing, not a change of form).
import { readFile, writeFile, mkdir, copyFile, mkdtemp } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { shoot } from './shots.mjs';
import { browser } from './browser.mjs';

const HERE = fileURLToPath(new URL('./', import.meta.url)), STORE = join(HERE, 'pictures');
const SHOTS = JSON.parse(await readFile(join(HERE, 'shots.json'), 'utf8'));
const args = process.argv.slice(2), update = args.includes('--update');
const only = args.includes('--only') ? args[args.indexOf('--only') + 1].split(',') : null;
const chars = JSON.parse(await readFile(join(HERE, '../characters/index.json'), 'utf8')).characters.map(c => c.id).filter(c => !only || only.includes(c));

const out = await mkdtemp(join(tmpdir(), 'engine-check-'));
const jobs = chars.flatMap(c => SHOTS.map(s => ({ ...s, char: c, name: `${c}-${s.name}` })));
await shoot(jobs, out, () => {});
if (update) {
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
  if (r.size || r.share > 0.0005) {
    bad++;
    if (r.diff) await writeFile(join(out, j.name + '-diff.png'), Buffer.from(r.diff, 'base64'));
    await copyFile(stored, join(out, j.name + '-stored.png'));
    console.log(`${j.name}: differs (${r.size ? 'another size' : (r.share * 100).toFixed(2) + '% of pixels'})`);
  }
}
await b.close();
console.log(bad ? `${bad} of ${jobs.length} pictures differ — see ${out}` : `all ${jobs.length} pictures as stored`);
process.exit(bad ? 1 : 0);
