// node render.js name [name…] — svg/<name>.svg → pics/<name>.png (then tools/webp.py makes .webp). One browser, closed at the end.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const root = path.join(__dirname, '..');
  let names = process.argv.slice(2);
  if (!names.length) names = fs.readdirSync(path.join(root, 'svg')).filter(f => f.endsWith('.svg')).map(f => f.slice(0, -4));
  const out = process.env.OUT || path.join(root, 'pics');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const n of names) {
    const svg = fs.readFileSync(path.join(root, 'svg', n + '.svg'), 'utf8');
    const m = svg.match(/width="(\d+)" height="(\d+)"/);
    await page.setViewportSize({ width: +m[1], height: +m[2] });
    await page.setContent(`<body style="margin:0">${svg}</body>`);
    await page.screenshot({ path: path.join(out, n + '.png') });
    console.log('png', n);
  }
  await browser.close();
})();
