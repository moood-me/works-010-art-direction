// node svg2png.mjs dir size name… — dir/name.svg → dir/name.png on a transparent background (headless Chromium)
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const [dir, size, ...names] = process.argv.slice(2), [W, H] = size.includes('x') ? size.split('x').map(Number) : [+size, +size];
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: H } });
for (const n of names) {
  await p.setContent(`<html><body style="margin:0;background:transparent">${await readFile(`${dir}/${n}.svg`, 'utf8')}</body></html>`);
  await p.screenshot({ path: `${dir}/${n}.png`, omitBackground: true, clip: { x: 0, y: 0, width: W, height: H } });
}
await b.close();
