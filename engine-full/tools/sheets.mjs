// Sheets of pictures for the docs and the gallery: each a set of moments (a character, its description's keys
// replaced — a body, rest changes, pose layers — a motion and a frame, a view), drawn by the picture check's own page
// (check/render.html) and tiled with their labels (tools/sheet.py).
//   node engine-full/tools/sheets.mjs engine-full/tools/sheets/bodies.json [sheet names…]
// A sheet: {name, out (from the repository's root), title, cols, w, h, items: [{label, char, body?, rest?, pose?, head?,
// skin? (a skinning method), clothes?, clip?, t?, view?, w?, h?, place?, focus?, size?, wind? (a wind preset: hair and
// clothes that move are stepped to their moment in it)}]} — rest, pose, head and clothes as in a character, with
// presets named by id alone (pinned here as they are now) and bodies by id.
import { readFile, writeFile, mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { shoot } from '../check/pictures.mjs';

const ROOT = fileURLToPath(new URL('../../', import.meta.url)), ENG = join(ROOT, 'engine-full');
const [specPath, ...only] = process.argv.slice(2);
const spec = JSON.parse(await readFile(specPath, 'utf8'));
const presets = JSON.parse(await readFile(join(ENG, 'presets/index.json'), 'utf8')).presets, bodies = JSON.parse(await readFile(join(ENG, 'data/bodies/index.json'), 'utf8')).bodies;
const pin = (list, id, what) => { const x = list.find(p => p.id === id.split('@')[0]); if (!x) throw new Error(`no ${what} ${id}`); return x.pin; };
const changes = list => list.map(c => c.kind === 'preset' ? { ...c, id: pin(presets, c.id, 'preset') } : c);
// a head (as a character's): its presets by id alone, pinned here
const headOf = h => ({ ...h, ...(h.preset ? { preset: pin(presets, h.preset, 'preset') } : {}), ...(h.form ? { form: changes(h.form) } : {}), ...(h.features ? { features: changes(h.features) } : {}),
  ...(h.expressions ? { expressions: changes(h.expressions) } : {}), ...(h.pieces ? { pieces: changes(h.pieces) } : {}), ...(h.light?.kind === 'preset' ? { light: { ...h.light, id: pin(presets, h.light.id, 'preset') } } : {}) });
for (const s of spec.sheets) {
  if (only.length && !only.includes(s.name)) continue;
  const dir = await mkdtemp(join(tmpdir(), 'sheet-'));
  const jobs = s.items.map((it, k) => {
    const over = {};
    if (it.body) over.body = pin(bodies, it.body, 'body');
    if (it.rest) over.rest = changes(it.rest);
    if (it.pose) over.pose = changes(it.pose);
    if (it.head) over.head = headOf(it.head);
    if (it.skin) over.skinning = { method: it.skin };
    if (it.clothes) over.clothes = it.clothes.map(g => g.kind === 'preset' ? { ...g, id: pin(presets, g.id, 'preset') } : g.kind === 'off' || !g.kind ? g
      : { ...g, ...(typeof g.fabric === 'string' ? { fabric: pin(presets, g.fabric, 'preset') } : {}), ...(typeof g.shape === 'string' ? { shape: pin(presets, g.shape, 'preset') } : {}) });
    return { name: 'p' + k, char: it.char || 'woman', clip: it.clip ?? null, t: it.t ?? 0, view: it.view || 'front', over, wind: it.wind ? pin(presets, it.wind, 'preset') : undefined, place: it.place, focus: it.focus, size: it.size, w: it.w || s.w || 300, h: it.h || s.h || 440 };
  });
  await shoot(jobs, dir);
  const tile = join(dir, 'sheet.json');
  await writeFile(tile, JSON.stringify({ out: join(ROOT, s.out), title: s.title, cols: s.cols, items: s.items.map((it, k) => [it.label, join(dir, `p${k}.png`)]) }));
  execFileSync('python3', [join(ENG, 'tools/sheet.py'), tile]);
  console.log(s.out);
}
