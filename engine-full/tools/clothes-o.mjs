// О1, О3 and the engine side by side: each moment (an outfit, a motion and its frame) drawn by О3's own page
// (experiments/cloth: its outfit on moood's body, its own cloth) or О1's (experiments/clothes-good-bodies: a dress of its
// own silhouette on its designed body, its cloth physics with the drawn form as rest), and by the engine (the same
// garments — or the same silhouette — as a character's clothes on Anny's body of the same age and sex), tiled in pairs
// with their labels (tools/sheet.py). The pages take three.js from a CDN; here they are given the repository's own copy
// (engine/vendor/three, the same version) — nothing of them is changed.
//   node engine-full/tools/clothes-o.mjs engine-full/tools/sheets/clothes-o.json [sheet names…]
// The spec: {sheets: [{name, out, title, w, h, cols, items: [{label, o3?: {outfit, motion, t, yaw, pitch, dist}, o1?: {look,
// motion, t, yaw, dist}, engine: {char, clothes?, clip, t, view}}]}]} — t the motion's frame (О3 stands 0.5 s and goes
// into its motion over 0.9 s first: its frame is the motion's + 42; О1 is stepped through the motion's frames to t), the
// engine's view as check/render.html has them, its clothes with presets by id (as tools/sheets.mjs).
import { readFile, writeFile, mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { shoot } from '../check/pictures.mjs';
import { serve } from '../check/serve.mjs';
import { browser } from '../check/browser.mjs';

const ROOT = fileURLToPath(new URL('../../', import.meta.url)), ENG = join(ROOT, 'engine-full');
const [specPath, ...only] = process.argv.slice(2), spec = JSON.parse(await readFile(specPath, 'utf8'));
const presets = JSON.parse(await readFile(join(ENG, 'presets/index.json'), 'utf8')).presets, pin = id => { const p = presets.find(p => p.id === id); if (!p) throw new Error(`no preset ${id}`); return p.pin; };
const LEAD = Math.round((0.5 + 0.9) * 30);
// О1's dresses as its viewer has them (experiments/clothes/viewer.json: each its body, its look)
const O1 = Object.fromEntries(JSON.parse(await readFile(join(ROOT, 'experiments/clothes/viewer.json'), 'utf8')).map(v => [v.id, v.state]));
// a page of an experiment, its three.js the repository's own
async function open(b, path, w, h) {
  const page = await b.newPage({ viewport: { width: w, height: h } });
  await page.route(u => u.href.includes('cdn.jsdelivr.net/npm/three@0.160.0/'), r => r.fulfill({ path: join(ENG, 'vendor/three/three.module.js'), contentType: 'text/javascript' }));
  await page.route(u => /fonts\.(googleapis|gstatic)\.com/.test(u.href), r => r.abort());
  // (О1's latest page was kept without the data folder it ran beside — the moood bodies and garments every page here
  // takes, experiments/data: given that)
  await page.route(u => u.pathname.startsWith('/experiments/clothes-good-bodies/data/'), r => r.fulfill({ path: join(ROOT, 'experiments/data', new URL(r.request().url()).pathname.split('/data/')[1]) }));
  await page.goto(path);
  return page;
}
const srv = await serve(), b = await browser();
for (const s of spec.sheets) {
  if (only.length && !only.includes(s.name)) continue;
  const dir = await mkdtemp(join(tmpdir(), 'clothes-o-')), w = s.w || 360, h = s.h || 460;
  for (const [k, it] of s.items.entries()) {
    if (it.o3) {
      const page = await open(b, `${srv.url}experiments/cloth/index.html?shots`, w, h);
      await page.waitForFunction(() => window.__cloth, null, { timeout: 120000 });
      await page.addStyleTag({ content: 'header, .controls, .notes, .hint { display: none !important } main { padding: 0 !important; max-width: none !important } .stage { aspect-ratio: auto !important; height: 100vh !important; border-radius: 0 !important }' });
      const o = it.o3; await page.evaluate(([o, lead]) => window.__cloth.bake({ outfit: o.outfit, motion: o.motion, upto: o.t + lead + 1, wind: o.wind || 0 }), [o, LEAD]);
      await page.evaluate(([f, v]) => window.__cloth.view(f, v), [o.t + LEAD, { yaw: o.yaw ?? 0.6, pitch: o.pitch ?? 0.1, dist: o.dist ?? 4.2 }]);
      await (await page.$('#cv')).screenshot({ path: join(dir, `o${k}.png`) }); await page.close();
    } else {
      // (its page lays its stage out under its panel: a large window, the stage taken, its middle cut to the picture's shape)
      const o = it.o1, st = O1[o.look], page = await open(b, `${srv.url}experiments/clothes-good-bodies/index.html`, 1100, 1000);
      await page.waitForFunction(() => window.__sh, null, { timeout: 300000 });
      for (let f = 0; f <= o.t; f++) await page.evaluate(async ([o, st, f]) => {
        window.__phys = true; window.__ride = false; if (f === 0) { window.__physReset = true; window.__physState = {}; window.__designRest = {}; }
        await window.__setMotion(o.motion, f); window.__sh.LOOKS[st.look] = st.lookDef; const S = window.__sh.state; S.mode = 'one'; S.who = st.who; S.gw = st.gw; S.cw = st.cw; S.over = st.over || {}; S.look = st.look;
        window.__sh.mark(); await window.__sh.refresh(); const c = window.__sh.cam; c.yaw = o.yaw ?? 0.5; if (o.dist) c.dist = o.dist;
      }, [o, st, f]);
      await page.waitForTimeout(300);
      const el = await page.$('#stage'); await el.scrollIntoViewIfNeeded(); const box = await el.boundingBox();
      await page.screenshot({ path: join(dir, `o${k}.png`), clip: box, timeout: 180000 }); await page.close();
      execFileSync('python3', ['-c', 'import sys; from PIL import Image; i = Image.open(sys.argv[1]); w, h = int(sys.argv[2]), int(sys.argv[3]); cw = min(i.width, round(i.height * w / h)); ch = round(cw * h / w); x = (i.width - cw) // 2; y = (i.height - ch) // 2; i.crop((x, y, x + cw, y + ch)).resize((w, h)).save(sys.argv[1])', join(dir, `o${k}.png`), String(w), String(h)]);
    }
  }
  const jobs = s.items.map((it, k) => ({ name: `e${k}`, char: it.engine.char, clip: it.engine.clip ?? null, t: it.engine.t ?? 0, view: it.engine.view ?? 'three', w, h,
    over: it.engine.clothes ? { clothes: it.engine.clothes.map(g => ({ ...g, fabric: pin(g.fabric), ...(g.shape ? { shape: pin(g.shape) } : {}) })) } : {}, ...(it.engine.wind ? { wind: pin(it.engine.wind) } : {}) }));
  await shoot(jobs, dir);
  const tile = join(dir, 'sheet.json');
  await writeFile(tile, JSON.stringify({ out: join(ROOT, s.out), title: s.title, cols: s.cols || 4, items: s.items.flatMap((it, k) => [[`${it.o3 ? 'О3' : 'О1'} · ${it.label}`, join(dir, `o${k}.png`)], [`движок · ${it.label}`, join(dir, `e${k}.png`)]]) }));
  execFileSync('python3', [join(ENG, 'tools/sheet.py'), tile]);
  console.log(s.out);
}
await b.close(); srv.close();
