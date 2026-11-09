// SVG -> PNG, one browser for all: node render.js a.svg a.png [b.svg b.png ...]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const a = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage();
  for (let i = 0; i < a.length; i += 2) {
    const s = fs.readFileSync(a[i], 'utf8');
    const [, w, h] = s.match(/width="(\d+)" height="(\d+)"/);
    await p.setViewportSize({ width: +w, height: +h });
    await p.setContent(`<html><body style="margin:0">${s}</body></html>`);
    await p.screenshot({ path: a[i + 1] });
  }
  await b.close();
})();
