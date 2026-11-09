// node render.js a.svg a.jpg [scale] ... — SVG files to JPG pictures with headless Chromium
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const args = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (let i = 0; i + 1 < args.length; i += 3) {
    const svg = fs.readFileSync(args[i], 'utf8');
    const m = svg.match(/viewBox="0 0 (\d+) (\d+)"/);
    const k = parseFloat(args[i + 2] || '1');
    const w = Math.round(m[1] * k), h = Math.round(m[2] * k);
    await page.setViewportSize({ width: w, height: h });
    await page.setContent('<body style="margin:0;background:#fff">' +
      svg.replace(/width="\d+" height="\d+">/, `width="${w}" height="${h}">`) + '</body>');
    await page.screenshot({ path: args[i + 1], type: 'jpeg', quality: 88 });
  }
  await browser.close();
})();
