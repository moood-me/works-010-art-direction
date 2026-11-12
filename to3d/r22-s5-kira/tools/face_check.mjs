// The canvas face (web/face.js with the character's numbers) against the drawing's own face (face_tex.py), per
// expression: node face_check.mjs → <cache>/tex/check.png (rows: canvas, drawing, the two overlaid)
import { readFile, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { serve } from '../../../engine/check/serve.mjs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const here = path.dirname(fileURLToPath(import.meta.url)), folder = path.basename(path.dirname(here)), tex = `/home/user/cache/to3d-${folder}/tex`;
const EX = ['neutral', 'joy', 'surprise', 'sad', 'anger'];
const imgs = {}; for (const e of EX) imgs[e] = 'data:image/png;base64,' + (await readFile(`${tex}/face-${e}.png`)).toString('base64');
const srv = await serve(), b = await chromium.launch(), page = await b.newPage();
await page.route('**/three.module.js', r => r.fulfill({ body: 'export const x = 0;', contentType: 'text/javascript' }));
await page.goto(srv.url + `to3d/${folder}/tools/web/face_check.html`);
const url = await page.evaluate(async ({ EX, imgs }) => {
  const F = (await import('./face_def.js')).face;
  const px = 3, [, , FW, FH] = F.rect, W = FW * px, H = FH * px;
  const c = document.createElement('canvas'); c.width = W * EX.length; c.height = H * 3;
  const g = c.getContext('2d'); g.fillStyle = '#f7d7bf'; g.fillRect(0, 0, c.width, c.height);
  for (const [i, ex] of EX.entries()) {
    const a = document.createElement('canvas'); a.width = W; a.height = H;
    F.drawFace(a.getContext('2d'), { e: F.vecExpr(F.exprVec(F.EXPR[ex])) }, px);
    const img = new Image(); img.src = imgs[ex]; await img.decode();
    g.drawImage(a, i * W, 0); g.drawImage(img, i * W, H, W, H);
    g.globalAlpha = 0.5; g.drawImage(img, i * W, 2 * H, W, H); g.drawImage(a, i * W, 2 * H); g.globalAlpha = 1;
  }
  return c.toDataURL('image/png');
}, { EX, imgs });
await writeFile(`${tex}/check.png`, Buffer.from(url.split(',')[1], 'base64'));
await b.close(); srv.close();
