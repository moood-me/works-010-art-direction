// SVG → PNG with a transparent background (headless Chromium): node svg2png.mjs outdir a.svg b.svg …
import { readFileSync } from 'node:fs';
import { basename, join } from 'node:path';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const [out, ...files] = process.argv.slice(2);
const b = await chromium.launch(); const page = await b.newPage();
for (const f of files) {
  const s = readFileSync(f, 'utf8'); const [, , w, h] = s.match(/viewBox="([\d.\s-]+)"/)[1].trim().split(/\s+/).map(Number);
  await page.setViewportSize({ width: w, height: h });
  await page.setContent(`<html><body style="margin:0;background:transparent">${s}</body></html>`);
  await page.screenshot({ path: join(out, basename(f).replace(/\.svg$/, '.png')), omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
}
await b.close();
