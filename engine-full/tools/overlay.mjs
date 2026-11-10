// The overlay check, for authors: a head laid over the picture it was drawn after (its head.ref: the image in
// docs/pictures/references/, its landmarks marked in the picture's pixels, the angle it is seen at) — seen at that
// angle (or at the angle that fits best, --fit), its landmarks (the eyes, the nose's tip, the mouth and its corners,
// the chin: found on the head's own skin) carried onto the picture's by the best similarity, and the error in the
// picture's pixels per landmark. Writes <outdir>/<character>-overlay.png: the picture, the head's outline over it,
// both sets of points joined. From Г2's fit.py (experiments/heads-mesh/py), on the engine's own heads.
//   node engine-full/tools/overlay.mjs outdir character… [--fit]
import { writeFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { serve } from '../check/serve.mjs';
import { browser } from '../check/browser.mjs';

const args = process.argv.slice(2), fit = args.includes('--fit'), [out, ...chars] = args.filter(a => a !== '--fit');
if (!out || !chars.length) { console.log('node engine-full/tools/overlay.mjs outdir character… [--fit]'); process.exit(1); }
await mkdir(out, { recursive: true });
const srv = await serve(), b = await browser(), page = await b.newPage({ viewport: { width: 512, height: 512 } }), errs = [];
page.on('pageerror', e => errs.push(e.message));
await page.goto(srv.url + 'engine-full/tools/overlay.html'); await page.waitForFunction(() => window.ready, null, { timeout: 120000 });
for (const c of chars) {
  const r = await page.evaluate(([c, fit]) => window.overlay(c, fit), [c, fit]);
  await writeFile(join(out, `${c}-overlay.png`), Buffer.from(r.png, 'base64'));
  console.log(`${c}: seen at yaw ${r.yaw.toFixed(2)}, pitch ${r.pitch.toFixed(2)} — landmarks off the picture's by ${r.rms.toFixed(1)} px (rms), at most ${r.worst.toFixed(1)} px: ${JSON.stringify(r.errors)}`);
}
await b.close(); srv.close();
if (errs.length) { console.log('page errors: ' + errs.join(' | ')); process.exit(1); }
