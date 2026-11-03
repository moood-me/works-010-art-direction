// node tools-demo/n6-toon/tools/vrmshot.mjs <folder with the .vrm files> outdir
// Pictures of the sample avatars with three-vrm (their own MToon, without outline, a plain material), and a turn.
import { mkdir } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { serve } from '../../../engine/check/serve.mjs';
import { browser } from '../../../engine/check/browser.mjs';

const [models, out] = process.argv.slice(2);
await mkdir(out + '/turn', { recursive: true });
// the models from their own folder, open to the page's origin
const fsrv = http.createServer(async (q, r) => { try { const d = await readFile(models + '/' + decodeURIComponent(q.url.slice(1))); r.writeHead(200, { 'access-control-allow-origin': '*' }); r.end(d); } catch { r.writeHead(404); r.end(); } });
await new Promise(r => fsrv.listen(0, '127.0.0.1', r));
const files = { url: `http://127.0.0.1:${fsrv.address().port}/`, close: () => fsrv.close() };
const srv = await serve(), b = await browser();
const only = process.argv[4]; let shots = [
  ['seed', 'Seed-san.vrm', 'full', ['mtoon', 'nooutline', 'plain'], 0.45],
  ['seed', 'Seed-san.vrm', 'bust', ['mtoon', 'nooutline', 'plain'], 0.45],
  ['twist', 'VRM1_Constraint_Twist_Sample.vrm', 'full', ['mtoon', 'nooutline', 'plain'], 0.45],
  ['twist', 'VRM1_Constraint_Twist_Sample.vrm', 'bust', ['mtoon', 'nooutline', 'plain'], 0.45],
];
if (only) shots = shots.filter(s => s[0] + '-' + s[2] === only);
for (const [name, file, view, mats, yaw] of shots) for (const mat of mats) {
  const w = 600, h = view === 'full' ? 800 : 600;
  const p = await b.newPage({ viewport: { width: w, height: h } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(`${srv.url}tools-demo/n6-toon/tools/vrm.html?vrm=${encodeURIComponent(files.url + file)}&mat=${mat}&view=${view}&yaw=${yaw}`);
  await p.waitForFunction(() => window.__ready, null, { timeout: 300000 });
  await p.screenshot({ path: `${out}/v-${name}-${view}-${mat}.png` }); console.log(name, view, mat, errs.join(' | '));
  if (name === 'twist' && view === 'bust' && mat === 'mtoon') {
    // a turn: 72 frames, 3 s at 24 fps
    for (let i = 0; i < 72; i++) { await p.evaluate(y => window.__frame(y), 0.45 + i / 72 * Math.PI * 2); await p.screenshot({ path: `${out}/turn/${String(i).padStart(3, '0')}.png` }); }
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', '24', '-i', `${out}/turn/%03d.png`, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '26', `${out}/v-twist-turn.mp4`]);
  }
  await p.close();
}
await b.close(); srv.close(); files.close();
