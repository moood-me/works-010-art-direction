// Animated pictures of the viewer for the docs and the gallery: the viewer (engine/viewer) opened with a query, its
// panel hidden, stepped frame by frame through a motion as it plays (its simulations go on from frame to frame) and
// drawn each `every` frames into a GIF.
//   node engine-full/tools/gif.mjs engine-full/tools/sheets/gifs.json [names…]
// The spec: {gifs: [{name, out (from the repository's root), query (the viewer's: ?clothes&c=…&m=…&w=…), from?, to, every?,
// w?, h?, yaw?, pitch?}]}
import { readFile, mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { serve } from '../check/serve.mjs';
import { browser } from '../check/browser.mjs';

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const [specPath, ...only] = process.argv.slice(2), spec = JSON.parse(await readFile(specPath, 'utf8'));
const srv = await serve(), b = await browser();
for (const g of spec.gifs) {
  if (only.length && !only.includes(g.name)) continue;
  const dir = await mkdtemp(join(tmpdir(), 'gif-')), w = g.w || 420, h = g.h || 520, page = await b.newPage({ viewport: { width: w, height: h } });
  await page.goto(`${srv.url}engine-full/viewer/index.html${g.query}&paused`);
  await page.waitForFunction(() => window.__viewer, null, { timeout: 300000 });
  await page.addStyleTag({ content: '#vpPanel { display: none !important }' });
  await page.evaluate(() => window.dispatchEvent(new Event('resize')));
  const frames = [];
  for (let t = g.from ?? 0; t <= g.to; t++) {
    await page.evaluate(async ([t, g]) => { const V = window.__viewer; if (g.yaw != null) V.cam.yaw = g.yaw; if (g.pitch != null) V.cam.pitch = g.pitch; await V.set({ t }); V.render(); }, [t, g]);
    if ((t - (g.from ?? 0)) % (g.every ?? 2)) continue;
    const f = join(dir, `f${String(t).padStart(4, '0')}.png`); await page.screenshot({ path: f }); frames.push(f);
  }
  await page.close();
  execFileSync('python3', ['-c', 'import sys; from PIL import Image; fs = sys.argv[3:]; ims = [Image.open(f).convert("P", palette=Image.ADAPTIVE) for f in fs]; ims[0].save(sys.argv[1], save_all=True, append_images=ims[1:], duration=int(sys.argv[2]), loop=0)', join(ROOT, g.out), String(Math.round(1000 / 30 * (g.every ?? 2))), ...frames]);
  console.log(g.out);
}
await b.close(); srv.close();
