// Renders every docs/*.svg to a 2x PNG next to it.  Run: node docs/src/render.js  (needs playwright)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = path.join(__dirname, '..');
  const b = await chromium.launch();
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    const w = +svg.match(/width="(\d+)"/)[1], h = +svg.match(/height="(\d+)"/)[1];
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 2 });
    await p.goto('file://' + path.join(dir, f));
    await p.screenshot({ path: path.join(dir, f.replace('.svg', '.png')) });
    await p.close();
  }
  await b.close();
})();
