// node render.js [name…] — svg/<name>.svg → pics/<name>.png (then webp.py makes .webp). One browser, closed at the end.
// SVG=dir OUT=dir override the folders (scratch renders).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const root = path.join(__dirname, '..');
  const src = process.env.SVG || path.join(root, 'svg');
  const out = process.env.OUT || path.join(root, 'pics');
  let names = process.argv.slice(2);
  if (!names.length) names = fs.readdirSync(src).filter(f => f.endsWith('.svg')).map(f => f.slice(0, -4));
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
