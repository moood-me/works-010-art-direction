// node render.js [name…] — svg/<name>.svg → $OUT/<name>.png (default ../pics). One browser, closed at the end.
// tools/webp.py then turns the PNGs into WebP and removes them.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const root = path.join(__dirname, '..');
  const src = process.env.SRC || path.join(root, 'svg');
  let names = process.argv.slice(2);
  if (!names.length) names = fs.readdirSync(src).filter(f => f.endsWith('.svg')).map(f => f.slice(0, -4));
  const out = process.env.OUT || path.join(root, 'pics');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const n of names) {
    const svg = fs.readFileSync(path.join(src, n + '.svg'), 'utf8');
    const m = svg.match(/width="(\d+)" height="(\d+)"/);
    await page.setViewportSize({ width: +m[1], height: +m[2] });
    await page.setContent(`<body style="margin:0">${svg}</body>`);
    await page.screenshot({ path: path.join(out, n + '.png') });
    console.log('png', n);
  }
  await browser.close();
})();
