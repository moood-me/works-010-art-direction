// SVG files -> PNG with a transparent background: node svg2png.mjs in1.svg out1.png [in2.svg out2.png ...]
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const b = await chromium.launch();
const page = await b.newPage();
const a = process.argv.slice(2);
for (let i = 0; i < a.length; i += 2) {
  const s = await readFile(a[i], 'utf8');
  const w = +s.match(/width="(\d+)"/)[1], h = +s.match(/height="(\d+)"/)[1];
  await page.setViewportSize({ width: w, height: h });
  await page.setContent(`<html><body style="margin:0;background:transparent">${s}</body></html>`);
  await page.screenshot({ path: a[i + 1], omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
  console.log(a[i + 1]);
}
await b.close();
