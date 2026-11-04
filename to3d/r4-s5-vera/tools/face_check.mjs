// The canvas face (web/face.js) against the drawing's own face (tex/face-*.png from face_tex.py), per expression:
// node face_check.mjs outdir → outdir/check-<expr>.png (canvas, drawing, and the two overlaid)
import { mkdir, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { serve } from '../../../engine/check/serve.mjs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const out = process.argv[2]; await mkdir(out, { recursive: true });
const srv = await serve(), b = await chromium.launch(), page = await b.newPage();
await page.goto(srv.url + 'to3d/r4-s5-vera/tools/web/view.html?blank');
for (const ex of ['neutral', 'joy', 'surprise', 'sad', 'anger']) {
  const url = await page.evaluate(async ex => {
    const F = await import('./face.js');
    const px = 4, W = F.FW * px, H = F.FH * px;
    const c = document.createElement('canvas'); c.width = W * 3; c.height = H;
    const g = c.getContext('2d');
    const a = document.createElement('canvas'); a.width = W; a.height = H;
    F.drawFace(a.getContext('2d'), { e: F.vecExpr(F.exprVec(F.EXPR[ex])) }, px);
    const img = new Image(); img.src = `../tex/face-${ex}.png`; await img.decode();
    g.fillStyle = '#f7d7bf'; g.fillRect(0, 0, W * 3, H);
    g.drawImage(a, 0, 0); g.drawImage(img, W, 0, W, H);
    g.globalAlpha = 0.5; g.drawImage(img, 2 * W, 0, W, H); g.drawImage(a, 2 * W, 0); g.globalAlpha = 1;
    return c.toDataURL('image/png');
  }, ex);
  await writeFile(`${out}/check-${ex}.png`, Buffer.from(url.split(',')[1], 'base64'));
}
await b.close(); srv.close();
