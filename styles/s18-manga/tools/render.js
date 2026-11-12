// node render.js a.svg b.svg ... -> ../pics/<name>.png ; OUT=dir to change; JPG=1 for jpeg
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage();
  for (const f of process.argv.slice(2)) {
    const s = fs.readFileSync(f, 'utf8'); const m = s.match(/viewBox="0 0 (\d+) (\d+)"/);
    await pg.setViewportSize({ width: +m[1], height: +m[2] });
    await pg.setContent(`<body style="margin:0">${s}</body>`);
    const out = process.env.OUT || path.join(path.dirname(f), '..', 'pics');
    const name = path.basename(f, '.svg');
    await pg.screenshot(process.env.JPG ? { path: path.join(out, name + '.jpg'), type: 'jpeg', quality: 88 } : { path: path.join(out, name + '.png') });
  }
  await b.close();
})();
