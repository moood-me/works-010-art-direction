// Render SVG files to PNG with headless Chrome (Playwright).
// Usage: NODE_PATH=/opt/node-tools/node_modules node render.js out_dir scale file1.svg file2.svg ...
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [outDir, scale, ...files] = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const page = await browser.newPage({ deviceScaleFactor: parseFloat(scale) });
  for (const f of files) {
    const svg = fs.readFileSync(f, 'utf8');
    const m = svg.match(/viewBox="([\d.\s-]+)"/);
    const [, , w, h] = m[1].trim().split(/\s+/).map(Number);
    await page.setViewportSize({ width: Math.round(w), height: Math.round(h) });
    await page.setContent(`<html><body style="margin:0">${svg.replace(/<svg /, `<svg width="${w}" height="${h}" `)}</body></html>`);
    const out = path.join(outDir, path.basename(f).replace(/\.svg$/, '.png'));
    await page.screenshot({ path: out, clip: { x: 0, y: 0, width: w, height: h } });
    console.log(out);
  }
  await browser.close();
})();
