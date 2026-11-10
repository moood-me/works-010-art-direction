// В1 and the engine side by side: each moment (a hairstyle, a motion and its frame, a view) drawn by В1's own page
// (experiments/hair/index.html?live — its hairstyle on Anny's woman in a T-shirt, its own simulation) and by the engine
// (the same hairstyle as a head's piece on Anny's woman, src/hair/), tiled in pairs with their labels (tools/sheet.py).
//   node engine/tools/hair-b1.mjs engine/tools/sheets/hair-b1.json
// The spec: {out (from the repository's root), title, w, h, items: [{label, style, clip?, t?, view, yaw, pitch}]} — yaw and
// pitch В1's camera (radians: 0 from the front), view the engine's (check/render.html), focus on the head.
import { readFile, writeFile, mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { shoot } from '../check/pictures.mjs';
import { serve } from '../check/serve.mjs';
import { browser } from '../check/browser.mjs';

const ROOT = fileURLToPath(new URL('../../', import.meta.url)), ENG = join(ROOT, 'engine');
const spec = JSON.parse(await readFile(process.argv[2], 'utf8')), w = spec.w || 360, h = spec.h || 360;
const presets = JSON.parse(await readFile(join(ENG, 'presets/index.json'), 'utf8')).presets, pin = id => presets.find(p => p.id === id).pin;
const dir = await mkdtemp(join(tmpdir(), 'hair-b1-'));
// В1: its page, its own buttons hidden; each moment its motion started afresh and run to the frame (В1 stands 0.5 s and
// goes into the motion over 0.9 s first — experiments/cloth/sim.js moment: the motion's frame t is its frame t + 42)
const LEAD = Math.round((0.5 + 0.9) * 30);
const srv = await serve(), b = await browser(), page = await b.newPage({ viewport: { width: w, height: h } });
await page.goto(`${srv.url}experiments/hair/index.html?live&w=${w}&h=${h}`);
await page.waitForFunction(() => window.__ready, null, { timeout: 300000 });
await page.addStyleTag({ content: '.row, #msg { display: none !important; } div:has(> .row) { display: none !important; }' });
let style = null;
for (const [k, it] of spec.items.entries()) {
  if (it.style !== style) { await page.evaluate(async s => { await window.__hair.load({ style: s }); }, it.style); style = it.style; }
  await page.evaluate(async m => { await window.__hair.start({ motion: m ?? 'idle' }); }, it.clip ?? null);
  await page.evaluate(n => window.__hair.run(n), it.clip ? it.t + LEAD : 1);
  await page.evaluate(([y, p]) => window.__hair.look({ yaw: y, pitch: p, view: 'head' }), [it.yaw, it.pitch ?? 0.06]);
  await page.screenshot({ path: join(dir, `b${k}.png`) });
}
await b.close(); srv.close();
// the engine: the same moments
await shoot(spec.items.map((it, k) => ({ name: `e${k}`, char: 'woman', clip: it.clip ?? null, t: it.t ?? 0, view: it.view, over: { head: { pieces: [{ kind: 'preset', id: pin('hair-v1-' + it.style) }] } }, focus: 'Head', size: 0.5, w, h })), dir);
const tile = join(dir, 'sheet.json');
await writeFile(tile, JSON.stringify({ out: join(ROOT, spec.out), title: spec.title, cols: 4, items: spec.items.flatMap((it, k) => [[`В1 · ${it.label}`, join(dir, `b${k}.png`)], [`движок · ${it.label}`, join(dir, `e${k}.png`)]]) }));
execFileSync('python3', [join(ENG, 'tools/sheet.py'), tile]);
console.log(spec.out);
