// The face layer as pictures: node face_png.mjs outdir [expr …] → face-<expr>.png (transparent), drawn by web/face.js
// in headless Chromium — the same code that draws the 3D head's face every frame.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const { chromium } = createRequire(import.meta.url)('playwright');
const [out, ...names] = process.argv.slice(2); mkdirSync(out, { recursive: true });
const src = readFileSync(fileURLToPath(new URL('./web/face.js', import.meta.url)), 'utf8').replace(/export /g, '');
const b = await chromium.launch(); const page = await b.newPage();
await page.setContent('<canvas id="c"></canvas>');
const res = await page.evaluate(({ src, names }) => {
  const f = new Function(src + '; return { LiveFace, draw, EXPR_NAMES, X0, X1, Y0, Y1, PX };')();
  const c = document.getElementById('c'); c.width = (f.X1 - f.X0) * f.PX; c.height = (f.Y1 - f.Y0) * f.PX;
  const g = c.getContext('2d'), o = {};
  for (const n of (names.length ? names : f.EXPR_NAMES)) {
    const face = new f.LiveFace(7); face.still = true; face.exprKeys = [{ t: -10, w: { [n]: 1 } }];
    f.draw(g, face.at(2)); o[n] = c.toDataURL('image/png');
  }
  return o;
}, { src, names });
for (const [n, d] of Object.entries(res)) writeFileSync(`${out}/face-${n}.png`, Buffer.from(d.split(',')[1], 'base64'));
await b.close();
