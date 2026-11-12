// node svg2png.mjs dir — every dir/*.svg → dir/*.png (one browser, closed at the end)
import { createRequire } from 'node:module';
import { readdirSync, readFileSync } from 'node:fs';
const require = createRequire('/opt/node-tools/node_modules/');
const { chromium } = require('playwright');
const dir = process.argv[2], b = await chromium.launch(), page = await b.newPage();
for (const f of readdirSync(dir).filter(f => f.endsWith('.svg'))) {
  const svg = readFileSync(`${dir}/${f}`, 'utf8'), m = svg.match(/width="(\d+)" height="(\d+)"/);
  await page.setViewportSize({ width: +m[1], height: +m[2] });
  await page.setContent(`<body style="margin:0">${svg}</body>`);
  await page.screenshot({ path: `${dir}/${f.slice(0, -4)}.png` });
}
await b.close();
